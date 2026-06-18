# sources/distributed-fs/ceph-client/drivers/media/tuners/mxl301rf.c

Purpose: implements an incomplete MaxLinear MxL301RF OFDM tuner I2C driver. It provides basic wake/sleep, tuning, and RF-strength reporting, but explicitly relies on parent device firmware/card code to perform undisclosed chip initialization before this driver's `init()`.

Important APIs/types: `struct mxl301rf_state` embeds public config and `i2c_client`. I2C helpers are `raw_write()`, `reg_write()`, and `reg_read()`; `reg_read()` uses a `0xfb, reg` address-selection write before receiving one byte. DVB callbacks are `mxl301rf_init()`, `mxl301rf_sleep()`, `mxl301rf_set_params()`, and `mxl301rf_get_rf_strength()`. The Linux `i2c_driver` probe/remove functions attach state to the DVB frontend.

Control flow: probe allocates state, copies platform config, stores frontend private data, copies tuner ops, and stores a clientdata pointer to embedded config. Init only writes register `0x01=0x01` to wake the tuner. Tuning writes an abort/config sequence, optionally modifies spur-shift placeholder registers from `shf_tab` if requested frequency is near a listed center, converts frequency to a 10.6 fixed-point MHz value for RF registers `0x11/0x12`, starts tuning, waits 31 ms, writes `0x1a=0x0d`, and writes an IDAC sequence. Sleep writes standby register pairs. RF strength triggers measurement, reads RF input/offset registers, calculates dBm in millidecibels for the DVB stats cache, and returns a percentage approximation through the legacy `u16 *out`.

State and persistence: only frontend/client pointers and copied config are stored. The driver does not cache frequency, bandwidth, or full register state. The parent is responsible for persistent or firmware-provided initialization.

Dependencies and integration: uses Linux I2C client model, DVB frontend stats/property cache, platform data `struct mxl301rf_config`, and is noted as currently dependent on PT3-style parent initialization.

Risks: no null check for `client->dev.platform_data` before `memcpy()`. The packed register arrays are cast to `u8 *`, relying on `struct reg_val` being exactly two packed bytes. Tuning supports only fixed bandwidth register value and no IF-frequency callback. Initialization is intentionally incomplete, so this driver is not standalone. RF-strength percentage math can produce values outside common expectations if raw readings exceed assumed range.

Test signals: probe with missing/valid platform data, parent-init sequencing, raw I2C short write/read handling, spur-shift table matches at threshold edges, fixed-point frequency conversion rounding, RF strength stats scale/value, and remove clearing `fe->tuner_priv`.

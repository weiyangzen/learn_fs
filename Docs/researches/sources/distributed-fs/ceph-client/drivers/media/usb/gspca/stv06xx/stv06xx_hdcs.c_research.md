# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_hdcs.c

Purpose: implements HDCS-1000/1100 and HDCS-1020 sensor backends for STV06xx bridges, including probe, mode selection, power state transitions, window programming, exposure/gain controls, and register dumps.

Important APIs and functions: sensor operations are `hdcs_probe_1x00`, `hdcs_probe_1020`, `hdcs_init`, `hdcs_start`, `hdcs_stop`, `hdcs_init_controls`, and `hdcs_dump`. Internal helpers include `hdcs_reg_write_seq`, `hdcs_set_state`, `hdcs_reset`, `hdcs_set_exposure`, `hdcs_set_gains`, `hdcs_set_gain`, and `hdcs_set_size`.

Control flow: probe reads `HDCS_IDENT`, selects mode table and sensor-private geometry/timing parameters, and stores `struct hdcs` in `sensor_priv`. Init optionally enables STV0600 emulation on STV602, writes bridge init registers, resets the sensor, writes common sensor init registers, enables continuous capture config, programs ADC/PGA timing, and centers the default window. Start transitions the sensor to RUN; stop transitions to SLEEP. Exposure control converts user exposure into row and sub-row exposure using sensor timing constants, stops streaming, writes exposure registers, clears error flags, and restarts streaming.

State and persistence: `struct hdcs` tracks power state, active width/height, visible array geometry, exposure timing constants, and sample period. This private state is volatile and freed by the STV06xx core cleanup paths.

Dependencies and integration points: depends on STV06xx shared I2C helpers, `stv06xx_hdcs.h` register constants and descriptor objects, V4L2 exposure/gain controls, and bridge-specific quirks.

Risks: comments note no locking around private state. Exposure math is integer-heavy and sensor-specific; invalid timing assumptions can produce bad sub-row values. Probe allocates private state only after ID match; cleanup must free it. Packet-size values in the descriptors are fixed with FIXME comments about bandwidth testing.

Test signals: probe both HDCS ID values, stream HDCS1x00 and HDCS1020 hardware, vary exposure/gain while streaming, verify centered crop and dimensions, test STV602 emulation, and enable `dump_sensor` for register-read diagnostics.

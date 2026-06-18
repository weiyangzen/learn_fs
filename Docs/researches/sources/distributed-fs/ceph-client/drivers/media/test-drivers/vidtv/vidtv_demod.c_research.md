# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_demod.c

Purpose: virtual DVB demodulator I2C driver. It exposes a `dvb_frontend` supporting DVB-T/T2/C/S/S2, delegates tuning to the virtual tuner, simulates lock and signal statistics, and provides frontend callbacks used by the bridge.

Important APIs/types/functions: CNR threshold tables map delivery system/modulation/FEC to "ok" and "good" values. Core functions include `vidtv_match_cnr_s()`, `vidtv_clean_stats()`, `vidtv_demod_update_stats()`, `vidtv_demod_read_status()`, `vidtv_demod_set_frontend()`, `vidtv_demod_release()`, `vidtv_demod_i2c_probe()`, and `vidtv_demod_i2c_remove()`. `vidtv_demod_ops` defines supported delivery systems, frontend caps, and callback table.

Control flow: probe allocates `vidtv_demod_state`, copies frontend ops and bridge-provided config, stores the frontend in I2C client data, and initializes stats. Tuning calls tuner `set_params()`, reads RF strength/CNR, sets full lock if CNR is nonzero, updates stats, and closes the I2C gate if present. Status reads may randomly drop lock when CNR is below threshold or recover lock when signal improves, based on module-provided probabilities. Stats report strength/CNR with slight random variation and expose BER/block counters only when locked.

State and persistence: `vidtv_demod_state` holds frontend, config, current `enum fe_status`, and latest tuner CNR. State is per I2C client and freed on frontend release/remove.

Dependencies and integration points: integrates with I2C driver core, DVB frontend ops, tuner ops supplied by virtual tuner, random number helpers, and bridge platform data. Bridge retrieves the frontend pointer from I2C client data.

Risks: `vidtv_demod_i2c_probe()` names platform data as `struct vidtv_tuner_config *` even though it copies into `vidtv_demod_config`; this works only if the pointer actually points to compatible demod config from the bridge, and the type is misleading. Random lock-loss behavior can make tests flaky unless probabilities are controlled. `read_signal_strength()` returns `uvalue` while strength is filled via `svalue`, which may be semantically odd for signed dBm-like values.

Test signals: tune to valid/invalid virtual frequencies via tuner, frontend status transitions with probabilities set to 0/100, stats scale changes with lock, delivery-system threshold matching, module probe/remove, and DVB scan behavior through the bridge.

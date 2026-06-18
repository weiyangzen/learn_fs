# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_c.c

Purpose: DVB-C Annex A support routines for the CXD2820R demodulator, called by `cxd2820r_core.c` based on `delivery_system`.

Important APIs and functions: exports `cxd2820r_set_frontend_c()`, `cxd2820r_get_frontend_c()`, `cxd2820r_read_status_c()`, `cxd2820r_init_c()`, `cxd2820r_sleep_c()`, and `cxd2820r_get_tune_settings_c()` to the core through `cxd2820r_priv.h`.

Control flow: `set_frontend_c()` programs the tuner through `fe->ops.tuner_ops.set_params`, writes the DVB-C mode table when switching systems, stores `SYS_DVBC_ANNEX_A`, clears `ber_running`, requires tuner `get_if_frequency`, calculates IF register value from `CXD2820R_CLK`, writes it to secondary regmap bank `0x0042`, then starts acquisition with registers `0x00ff` and `0x00fe`. `get_frontend_c()` reads symbol rate, modulation, and inversion from bank 1. `read_status_c()` reads sync and TS-lock indicators, maps them to DVB status bits, updates signal strength, CNR, and post-bit-error counters.

State and persistence: updates `priv->delivery_system`, `priv->ber_running`, and cumulative `priv->post_bit_error`; writes DVBv5 stat cache fields in `dtv_frontend_properties`. No persistent storage exists.

Dependencies and integration: depends on regmap bank 1 for DVB-C demod registers, common table writer in core, tuner ops for IF frequency, `intlog2()`, and shared private state.

Risks and test signals: tuning fails if the tuner lacks `get_if_frequency`. BER counting uses a start/read/restart sequence and only accumulates valid windows, so polling cadence matters. CNR formula depends on constellation bits and logarithm constants. Test 6/7/8 MHz cable paths through core, missing IF callback, lock/no-lock stat scales, BER start/read transitions, and sleep clearing system state.

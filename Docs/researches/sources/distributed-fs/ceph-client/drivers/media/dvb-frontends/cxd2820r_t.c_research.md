# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_t.c

Purpose: DVB-T support routines for the CXD2820R demodulator.

Important APIs and functions: exports `cxd2820r_set_frontend_t()`, `cxd2820r_get_frontend_t()`, `cxd2820r_read_status_t()`, `cxd2820r_init_t()`, `cxd2820r_sleep_t()`, and `cxd2820r_get_tune_settings_t()`.

Control flow: `set_frontend_t()` validates bandwidth 6/7/8 MHz, programs the tuner, writes the DVB-T initialization table when switching into T mode, stores `SYS_DVBT`, clears BER running, requires tuner IF frequency, writes IF registers, timing-recovery bandwidth tables, bandwidth selector, latency values, and start registers. `get_frontend_t()` decodes modulation, transmission mode, guard interval, hierarchy, HP/LP code rates, and inversion from demod registers. `read_status_t()` reads sync and TS-lock, maps status bits, then updates relative strength, dB CNR, and post-bit-error counters. `sleep_t()` clears active mode registers and marks the system undefined.

State and persistence: updates shared `priv->delivery_system`, `priv->ber_running`, cumulative `post_bit_error`, and DVBv5 statistic fields. No durable state.

Dependencies and integration: uses regmap bank 0, common register table writer, tuner `set_params`/`get_if_frequency`, and `intlog10()` for CNR.

Risks and test signals: unsupported bandwidth returns `-EINVAL`. IF callback absence breaks tuning. BER counters are restart-driven and require polling under sync. Test all bandwidths, invalid bandwidth, lock partial states, CNR edge cases around zero/large register values, and core search switching between T and T2.

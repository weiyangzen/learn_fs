# sources/distributed-fs/ceph-client/drivers/media/tuners/tda827x.c

Purpose: implements attach-style support for Philips/NXP TDA8275/TDA8275A tuner variants for digital and analog use.

Important APIs and functions: exported entry is `tda827x_attach`. Initial ops assume older TDA827X until `tda827x_probe_version` reads a byte and either finalizes old ops or replaces them with TDA827XA ops. Key tuning functions are `tda827xo_set_params`, `tda827xo_set_analog_params`, `tda827xa_set_params`, `tda827xa_set_analog_params`, sleep/init/getters, and LNA/AGC helpers.

Control flow: attach allocates private state, records address/adapter/config, installs initial old-tuner ops, and defers variant detection to first init/sleep. Digital tuning selects IF by bandwidth, chooses a frequency table row, computes divider `N`, writes register sequences, waits, adjusts charge pump, and caches frequency/bandwidth. The A variant adds DVB-C-specific tables, AGC reads, LNA gain switching, CP correction, and AGC freeze. Analog tuning maps V4L2 standard/radio mode to sound IF and low-pass selection, then writes variant-specific tuning sequences.

State and persistence: `struct tda827x_priv` stores I2C address/adapter, config pointer, analog IF and LP selection, and cached frequency/bandwidth. Variant selection mutates `fe->ops.tuner_ops` and may populate `cfg->agcf`.

Dependencies and integration points: depends on DVB frontend I2C gate callbacks, V4L2 analog parameters, `tda8290_lna` config from `tda8290.h`, and optional board callbacks in `struct tda827x_config`. Often attached by `tda8290.c` behind an analog IF demod bridge.

Risks: many analog write sequences ignore transfer return values. Initial variant probing is lazy, so failures can surface on first init/sleep rather than attach. LNA behavior depends on board callback and switch address correctness. Several waits are long fixed sleeps, making tune latency high.

Test signals: attach plus first init detecting 8275 vs 8275A, digital DVB-T/DVB-C tuning across frequency tables, analog standards and radio, LNA high/low switching paths, I2C-gate open/close traces, and error injection for tuner reads/writes.

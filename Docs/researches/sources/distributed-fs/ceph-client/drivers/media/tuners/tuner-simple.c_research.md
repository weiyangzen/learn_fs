# sources/distributed-fs/ceph-client/drivers/media/tuners/tuner-simple.c

Purpose: generic simple four-byte PLL tuner driver for many analog, radio, and hybrid TV tuner modules.

APIs/functions: exports `simple_tuner_attach()`. Ops include init, sleep, analog params, DVB params, calc-regs, release, frequency/bandwidth/status/RF-strength getters. Key helpers choose params, ranges, standard-specific bytes, RF inputs, radio band-switch bytes, TDA9887 config, DVB byte calculation, and post-tune actions.

Control flow/state: attach validates tuner ID, optionally probes I2C, obtains shared state, and installs ops/name. Analog TV picks PAL/SECAM/NTSC params, computes IF offset and divider, applies model-specific standard/RF/TDA9887 tweaks, writes four bytes, and optionally post-tunes. Radio adds configured radio IF and writes a 50 kHz-step payload. Digital computes bytes from frontend cache, opens I2C gate, puts analog demod in standby, writes tuner bytes, and caches frequency/bandwidth.

Dependencies/integration: `tuner-types.c` table, `tuner-i2c.h`, V4L2/DVB frontend APIs, I2C gates, analog demod standby, and TDA9887 private config commands.

Risks/tests: table values, IF math, and shared lifetime are high risk. Test representative PAL/NTSC/SECAM/radio/DTV tuners, boundary frequencies, RF-input module params, TDA9887 commands, no-adapter `calc_regs`, and attach/release reference counts.

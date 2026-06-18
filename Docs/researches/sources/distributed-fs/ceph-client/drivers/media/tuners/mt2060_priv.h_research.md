# sources/distributed-fs/ceph-client/drivers/media/tuners/mt2060_priv.h

Purpose: private MT2060 register map and state definition shared by the C implementation. It documents the inferred register layout from a Comtech SDVBT-3K6M tuner datasheet and centralizes constants used by the tuning and calibration code.

Important APIs/types: defines register offsets `REG_PART_REV` through `REG_LOTO`, chip ID `PART_REV 0x63`, default I2C address `0x60`, optional compile-time `MT2060_SPURCHECK`, and `struct mt2060_priv`. The private state contains the active config pointer, I2C adapter/client, embedded config for I2C-model devices, `i2c_max_regs`, cached tuned `frequency`, `if1_freq`, calibration `fmfreq`, and `sleep` feature flag.

Control flow integration: `mt2060.c` uses these register names for all raw reads/writes, PLL setup, calibration loops, and power management. The embedded `config` lets the I2C-driver path build a config from platform data while still using the same helper code as legacy attach.

State and persistence: describes in-memory state only. The `sleep` comment is important operational context: using `REG_MISC_CTRL` for sleep can reduce power materially, but is disabled by default for legacy attach because bit meanings are not fully known.

Dependencies: requires `mt2060_config`, `i2c_adapter`, `i2c_client`, fixed-width integer types, and `bool` from included kernel headers through the C file.

Risks: the register map has unknown/reserved fields and comments with uncertainty; any behavior changes around `REG_MISC_CTRL`, calibration, or reserved bytes need hardware validation. `PART_REV` hard-codes support to part 6/rev 3. Since private state stores raw pointers to board-supplied config, legacy callers must keep config memory alive as long as the frontend exists.

Test signals: verify register constants against transfer traces, cover ID mismatch, confirm `sleep` false on legacy attach and true on I2C probe, and test `i2c_max_regs` chunk behavior because it is private state but externally controlled via platform data.

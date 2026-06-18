# sources/distributed-fs/ceph-client/drivers/mfd/aat2870-core.c

Purpose: MFD core for the AnalogicTech AAT2870 backlight/regulator chip. It supplies raw I2C register access with a software cache, enable GPIO control, optional debugfs register access, child registration for backlight and LDO regulators, and suspend/resume register restore.

Important APIs, types, and functions: `aat2870_i2c_probe()` initializes `aat2870_data` and registers children. `__aat2870_read()`, `__aat2870_write()`, and `aat2870_update()` implement cached register access under `io_lock`. `aat2870_enable()`/`aat2870_disable()` drive the optional enable GPIO. Debugfs uses `aat2870_reg_read_file()` and `aat2870_reg_write_file()`. `aat2870_pm_ops` restores cached writeable registers on resume.

Control flow: probe requires platform data, copies pointers/callbacks, requests the enable GPIO, powers the chip, maps platform subdevice data onto static `aat2870_devs[]`, registers all cells, and creates debugfs when enabled. Suspend disables the chip; resume enables it and writes every cached writeable register.

State and persistence: `aat2870_data` stores client, callbacks, enable state, GPIO, mutex, and a pointer to static `aat2870_regs`. The register cache is static global storage, so values can persist across devices and probes. Hardware register state is restored from cache after resume.

Dependencies and integration: depends on I2C, legacy GPIO APIs, MFD core, regulator platform data, optional debugfs, and child drivers named `aat2870-backlight` and `aat2870-regulator`.

Risks: probe dereferences `pdata` without checking NULL; static register cache and static child descriptors are not per-device; debugfs write parsing attempts to parse the value from the same string position as the address, so writes may not behave as intended; no remove path disables hardware or removes MFD children except device core cleanup; legacy GPIO requirement limits portability.

Test signals: build with `CONFIG_MFD_AAT2870_CORE`, probe with complete platform data, verify child data mapping, register read/write/update locking, debugfs dump/write behavior, suspend/resume cache restore, enable GPIO polarity, and multiple-device behavior.

# sources/distributed-fs/ceph-client/drivers/mfd/ntxec.c

Purpose: I2C MFD core for Netronix embedded controllers used in e-book readers. It initializes big-endian 16-bit register access, detects firmware version, registers RTC/PWM children depending on firmware, and optionally provides system poweroff/restart handlers.

Important APIs, types, and functions: `ntxec_poweroff()` writes `NTXEC_REG_POWEROFF` and sleeps long enough for power loss. `ntxec_restart()` writes the reset register through a restart notifier. `regmap_config` defines normal I2C regmap access; `regmap_config_noack` stacks a wrapper regmap for firmware that does not ACK writes. `ntxec_probe()` reads `NTXEC_REG_VERSION`, selects child cells, enables `POWERKEEP` for system-power-controller nodes, assigns global poweroff/restart client state, and calls `devm_mfd_add_devices()`. `ntxec_remove()` unregisters global power handlers for the owning client.

Control flow: probe initializes regmap first, rejects unknown firmware versions, optionally wraps regmap for Tolino Shine 2, handles system power controller duties, stores clientdata, and registers children. Poweroff/restart callbacks bypass regmap and issue raw I2C transfers because they may run late in shutdown.

State and persistence: `struct ntxec` stores device and regmap. Global `poweroff_restart_client`, `pm_power_off`, and `ntxec_restart_handler` are process-wide state. `POWERKEEP` changes controller behavior to keep the host running.

Dependencies and integration points: depends on I2C, regmap, MFD core, reboot/poweroff infrastructure, OF `system-power-controller`, and public `<linux/mfd/ntxec.h>`. Children are `ntxec-rtc` and/or `ntxec-pwm`.

Risks: global poweroff handler assignment is only logged if already occupied; probe continues. `ntxec_remove()` sets `pm_power_off = NULL` without verifying that it still points to `ntxec_poweroff`. The no-ACK wrapper ignores write errors by design, which may hide hardware failures. Test signals include firmware-version matrix, no-ACK write wrapper, poweroff/restart raw I2C lengths, system-power-controller conflict behavior, and child selection.

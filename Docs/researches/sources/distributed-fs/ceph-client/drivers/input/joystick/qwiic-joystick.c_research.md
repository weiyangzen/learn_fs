# sources/distributed-fs/ceph-client/drivers/input/joystick/qwiic-joystick.c

Purpose: I2C polling driver for SparkFun Qwiic Joystick, reporting two 10-bit axes and a thumb button.

Important APIs/types/functions: `struct qwiic_jsk` stores phys string, input device, and I2C client. `struct qwiic_ver` and `struct qwiic_data` model firmware version and data registers. `qwiic_probe()` reads firmware version, allocates state/input, configures ABS/button capabilities, sets input polling intervals, and registers. `qwiic_poll()` reads the data block and reports X/Y/thumb.

Control flow: Probe first reads version register 1 and rejects short reads. It then creates input with BUS_I2C, ABS_X/ABS_Y ranges 0..1023, `BTN_THUMBL`, and a 16 ms polling interval with 8..32 ms bounds. Poll reads register 3 as a block; only exact-size reads produce events.

State and persistence: Per-client state is devm-managed. No persistent storage. Firmware version is logged only at debug level.

Dependencies and integration points: I2C SMBus block reads, input polling, OF compatible `sparkfun,qwiic-joystick`, I2C ID table using `KBUILD_MODNAME`.

Risks: No interrupt mode; missed fast changes are possible at polling interval. Axis values are big-endian and shifted right by 6, so firmware layout changes would break scaling. Short reads are silently ignored during polling.

Test signals: Version read success/failure; data block endian/scaling; thumb active-low behavior; poll interval sysfs adjustments within bounds; OF and I2C ID binding.

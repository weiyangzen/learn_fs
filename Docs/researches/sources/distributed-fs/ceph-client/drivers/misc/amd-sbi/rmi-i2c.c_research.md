# sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/rmi-i2c.c

Purpose: provides the AMD SB-RMI transport probe/remove layer for I2C and I3C devices, creates regmaps, enables alerts, caches maximum power, and registers hwmon/misc interfaces.

Important APIs and functions: `sbrmi_common_probe` initializes shared state for both buses. `sbrmi_i2c_probe/remove` bind the I2C driver. `sbrmi_i3c_probe/remove` bind the I3C driver. `sbrmi_enable_alert` clears the control bit that masks software alerts, and `sbrmi_get_max_pwr_limit` initializes `pwr_limit_max`.

Control flow: I2C probe creates an 8-bit register regmap, reads `SBRMI_REV`, and switches to a 16-bit little-endian register-address regmap for revision 0x21 or newer to avoid bus corruption. I3C probe first filters devices by instance id, performs the same revision/regmap selection, and passes the dynamic address into common probe. Common probe allocates `sbrmi_data`, initializes the mutex, enables alerts, reads max power, stores drvdata, registers hwmon if enabled, then registers the misc device. Remove deregisters the misc device.

State and persistence: per-device state is devm-allocated and lasts until device removal. Regmap selection persists for the lifetime of the device. Firmware power-limit and alert state live in the managed AMD device.

Dependencies and integration points: depends on I2C, I3C, regmap, OF matching, the APML core in `rmi-core.c`, and optional hwmon creation.

Risks: common probe enables alerts and performs a mailbox command before misc registration, so probe fails if firmware is slow or unavailable. I2C remove nulls fields after deregistration but I3C remove does not. Address-width switching depends solely on revision read success.

Test signals: I2C and I3C probe/remove, revision 0x20 versus 0x21+ regmap behavior, I3C instance-id filtering, alert-enable register writes, max-power mailbox read, and devnode creation.

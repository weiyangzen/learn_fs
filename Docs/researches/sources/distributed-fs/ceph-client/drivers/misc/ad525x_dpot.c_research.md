# sources/distributed-fs/ceph-client/drivers/misc/ad525x_dpot.c

Purpose: implements the shared Analog Devices AD525x/AD52xx digital potentiometer core used by bus-specific I2C and SPI frontends. It translates device capability encodings from `ad525x_dpot.h` into per-RDAC sysfs files, handles RDAC/EEPROM/OTP/tolerance access, and exports `ad_dpot_probe` and `ad_dpot_remove`.

Important APIs and functions: `struct dpot_data` stores copied bus ops, feature bits, wiper mask, RDAC mask, OTP enable bits, and write-only RDAC cache. Bus wrappers call `struct ad_dpot_bus_ops`. `dpot_read_spi`, `dpot_read_i2c`, `dpot_write_spi`, and `dpot_write_i2c` contain device-family protocol differences. Sysfs helpers are `sysfs_show_reg`, `sysfs_set_reg`, and `sysfs_do_cmd`; generated attributes cover `rdacN`, `eepromN`, `toleranceN`, `otpN`, `otpNen`, and increment/decrement commands.

Control flow: bus drivers call `ad_dpot_probe` with a device id encoding. Probe allocates state, derives max position and masks, creates sysfs files for each enabled wiper, initializes write-only caches to midscale, and optionally creates command attributes. Sysfs writes parse decimal values, clamp to the RDAC range, require explicit `otpNen` before OTP writes, serialize on `update_lock`, and sleep after EEPROM or OTP programming. Remove deletes per-wiper files and frees state.

State and persistence: software state is per device and held in drvdata. Hardware RDAC state is volatile unless written to EEPROM or OTP through exposed sysfs paths. OTP enable state is a software guard only and is not persistent. Write-only SPI parts rely on `rdac_cache` for reads.

Dependencies and integration points: depends on kernel device/sysfs APIs, mutexes, sleep delays, and bus ops supplied by sibling I2C/SPI drivers. The ABI is the misc-device sysfs interface documented externally by the driver family.

Risks: the file contains malformed-looking source in this snapshot around the SPI appdata path, including a dangling `else`/`BUG()` structure, which is a build risk if not caused by snapshot corruption. `ad_dpot_remove` does not remove the command attribute group created for `F_CMD_INC`. Sysfs writes ignore `dpot_write` return values and still return `count`, so programming failures can be hidden. OTP writes are destructive and exposed through sysfs after a simple enable flag. The wiper attribute table starts with duplicate `rdac0`, which is intentional for index alignment but brittle.

Test signals: build with AD525x I2C/SPI frontends, probe every encoded family class, verify sysfs file creation for one through six wipers, exercise read/write paths on EEPROM, OTP, tolerance, and write-only parts, and use bus-error injection to confirm user-visible failures.

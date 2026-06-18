# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/hac300s.c

Purpose: PMBus driver for Hi-Tron HAC300S PSUs. It fakes `VOUT_MODE` and strips linear11 exponents because the device does not follow PMBus VOUT linear16 expectations.

Important APIs/types/functions: `struct hac300s_data` embeds a per-device PMBus info copy and the detected VOUT exponent. `hac300s_probe()` reads `PMBUS_READ_VOUT` to derive the exponent, sets `PMBUS_NO_CAPABILITY`, and calls PMBus core. `hac300s_read_byte_data()` returns the stored exponent for `PMBUS_VOUT_MODE`. `hac300s_read_word_data()` reads VOUT-related commands and returns only the linear11 mantissa.

Control flow: probe checks SMBus byte/word support, reads VOUT once, extracts exponent bits, copies static info, installs platform data, and registers PMBus. PMBus core later calls hooks for VOUT mode and VOUT reads while other commands fall through to core/default behavior or `-ENODATA`.

State and persistence: the detected exponent is stored per device. Hardware state is not modified by the driver.

Dependencies and integration: depends on PMBus core, I2C, OF/I2C matching, bitfield helpers, and PMBus linear conversion.

Risks: the exponent is inferred at probe and assumed stable. Clearing exponent bits for all VOUT limit and read commands assumes the same encoding across those registers. `PMBUS_NO_CAPABILITY` bypasses device capability reporting, so the static descriptor must be accurate.

Test signals: VOUT scaling against known values, VOUT limit reads, probe error when initial VOUT read fails, absence of capability reads, and hwmon files for declared sensors/statuses.

# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/dps920ab.c

Purpose: PMBus driver for Delta DPS920AB power supplies. It verifies manufacturer/model strings, masks unsupported commands, exposes supported telemetry, allows fan command writes, and creates debugfs files for manufacturer ID/model.

Important APIs/types/functions: `struct dps920ab_data` stores duplicated manufacturer strings for debugfs. `dps920ab_read_word_data()` whitelists supported PMBus reads and returns `-ENXIO` for unsupported commands. `dps920ab_write_word_data()` allows only `PMBUS_FAN_COMMAND_1`. `dps920ab_info` declares one linear-format page. `dps920ab_init_debugfs()` creates `mfr_id` and `mfr_model` files.

Control flow: probe allocates private data, reads and validates `PMBUS_MFR_ID == "DELTA"` and model prefix `DPS-920AB`, stores strings, calls `pmbus_do_probe()`, then initializes debugfs under the PMBus root. PMBus core calls read/write hooks to prevent unsupported register access.

State and persistence: private state is only debugfs string storage. Hardware fan command writes persist in the PSU until changed. Unsupported commands are not cached.

Dependencies and integration: depends on PMBus core, I2C SMBus block/word operations, OF/I2C matching, and debugfs seq-file helpers.

Risks: whitelisting is conservative and may hide valid commands added by newer firmware. Manufacturer/model length checks are strict. Debugfs creation is optional after PMBus probe; missing debugfs does not affect hwmon.

Test signals: manufacturer/model rejection, visible hwmon files for declared capabilities, unsupported read suppression, fan command write success and other writes rejected, debugfs string files, and probe cleanup through devm allocations.

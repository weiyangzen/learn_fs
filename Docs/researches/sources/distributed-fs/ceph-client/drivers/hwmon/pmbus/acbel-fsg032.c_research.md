# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/acbel-fsg032.c

Purpose: PMBus driver for AcBel FSG032 power supplies. It verifies manufacturer/model strings, declares supported PMBus telemetry, and exposes firmware revision through debugfs.

Important APIs/types/functions: `acbel_fsg032_info` declares one PMBus page with voltage, current, power, temperature, fan, and status capabilities. `acbel_fsg032_probe()` reads `PMBUS_MFR_ID` and `PMBUS_MFR_MODEL` and then calls `pmbus_do_probe()`. `acbel_fsg032_debugfs_read()` reads manufacturer command `ACBEL_MFR_FW_REVISION` and formats up to three bytes; `acbel_fsg032_init_debugfs()` creates `fw_version`.

Control flow: I2C/OF matching binds the driver, probe rejects non-ACBEL/non-FSG032 devices, PMBus core creates hwmon files from `acbel_fsg032_info`, then debugfs is attached under the PMBus debugfs directory if available.

State and persistence: no private long-lived state beyond PMBus core state. Debugfs reads query hardware each time.

Dependencies and integration: depends on I2C SMBus block reads, PMBus core, debugfs, OF matching, and hwmon PMBus status mapping.

Risks: block data is treated as a C string only after setting `buf[rc]`, so model/manufacturer validation depends on returned lengths being within the SMBus block buffer. Debugfs output is intentionally short and may truncate longer firmware revisions. Probe does not explicitly check adapter functionality before block reads.

Test signals: model/manufacturer rejection, hwmon files for declared capabilities, debugfs `fw_version`, and failure injection for SMBus block reads.

# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/bpa-rs600.c

Purpose: PMBus driver for BluTek BPA-RS600/BPD-RS600 power supplies. It handles several firmware/spec deviations while exposing voltage, current, power, temperature, and fan telemetry.

Important APIs/types/functions: `bpa_rs600_read_byte_data()` masks out non-existent fan2 bits from `PMBUS_FAN_CONFIG_12`. `bpa_rs600_read_vin()` rewrites unsigned mantissa VIN encodings into a representation the PMBus core can decode. `bpa_rs600_read_pin_max()` corrects a known bad 1640 W `MFR_PIN_MAX` value to 700 W. `bpa_rs600_read_word_data()` rejects invalid undocumented limits and routes special reads. `bpa_rs600_probe()` checks SMBus capability and validates model block data against supported IDs.

Control flow: probe verifies adapter support, reads `PMBUS_MFR_MODEL`, matches against the ID table, and calls PMBus core. During hwmon reads, the PMBus core delegates selected byte/word commands to driver hooks for correction or rejection.

State and persistence: no private state. Corrected values are computed on demand from hardware reads.

Dependencies and integration: depends on PMBus core, I2C SMBus byte/word/block operations, OF/I2C matching, and PMBus linear encoding semantics.

Risks: corrections are firmware-specific; future firmware could use different encodings. The fan2 mask assumes only one physical fan despite PMBus config reporting two. Invalid command filtering removes limits and virtual attributes to avoid bad data, so users may see fewer files than generic PMBus probing would expose.

Test signals: model validation for both IDs, fan config masking, VIN correction on high mantissa bit, `MFR_PIN_MAX` bad-value correction, invalid limit suppression, and hwmon readings for declared capabilities.

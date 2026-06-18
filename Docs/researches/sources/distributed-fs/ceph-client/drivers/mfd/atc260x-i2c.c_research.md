<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atc260x-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/atc260x-i2c.c

Purpose: provides the I2C transport binding for Actions ATC260x PMICs. It allocates the shared core state, obtains variant configuration from OF match data, initializes an I2C regmap, and delegates to `atc260x_device_probe`.

Important APIs and functions: `atc260x_i2c_probe` is the only runtime entry point. It calls `atc260x_match_device` and `devm_regmap_init_i2c`, then stores client data and invokes the core.

Control flow: probe allocates `struct atc260x`, sets device and IRQ from the I2C client, fills a local `struct regmap_config` through the core matcher, stores the state as client data, creates the regmap, and finishes through `atc260x_device_probe`.

State and persistence: this transport owns no state beyond the devm-allocated shared `struct atc260x` and bus regmap lifetime. All variant, IRQ, and child state is controlled by `atc260x-core.c`.

Dependencies and integration points: depends on I2C, OF matching for `"actions,atc2603c"` and `"actions,atc2609a"`, regmap, and the exported ATC260x core functions.

Risks: there is no ACPI or I2C ID fallback; match data must come from OF. No remove callback is needed because devm and MFD core handle resources, but behavior depends on the core's devm usage. Missing IRQ will cause the core probe to fail.

Test signals: I2C probe for both OF compatibles, regmap initialization errors, handoff to core with IRQ present/absent, child registration, and module load/unload coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atc260x-i2c.c -->

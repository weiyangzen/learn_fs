<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/axp20x-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/axp20x-i2c.c

Purpose: provides the I2C transport binding for X-Powers AXP PMICs supported by the AXP20x MFD core. It allocates shared state, matches the PMIC variant, initializes an I2C regmap, and delegates device setup/removal to the core.

Important APIs and functions: `axp20x_i2c_probe` and `axp20x_i2c_remove` are the lifecycle functions. Match tables cover many OF compatibles from AXP152 through AXP15060 and ACPI ID `INT33F4` for AXP288.

Control flow: probe allocates `struct axp20x_dev`, sets device and IRQ, stores driver data, calls `axp20x_match_device` to fill variant-specific regmap/cell/IRQ-chip pointers, initializes I2C regmap using the chosen config, and calls `axp20x_device_probe`. Remove calls `axp20x_device_remove`.

State and persistence: transport state is only the devm-allocated `struct axp20x_dev` and I2C regmap. Variant, IRQ, child, and power-off state are owned by `axp20x.c`.

Dependencies and integration points: depends on I2C, OF and ACPI match data, regmap, and exported AXP20x core functions. It is the path for non-RSB PMIC variants and x86 AXP288 ACPI systems.

Risks: the I2C ID table entries do not carry driver data, so non-OF/non-ACPI I2C instantiation may not provide a variant through `device_get_match_data`. Remove always calls core removal, which deletes IRQ chip state only if it was created. Correct no-IRQ behavior depends on the core's fallback cell selection.

Test signals: OF probe for each listed compatible, ACPI `INT33F4` AXP288 probe, no-IRQ fallback behavior, regmap init failure handling, child creation per variant, and remove/unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/axp20x-i2c.c -->

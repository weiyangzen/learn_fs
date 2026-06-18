# sources/distributed-fs/ceph-client/drivers/regulator/max8925-regulator.c

Purpose: MFD child driver registering one MAX8925 regulator per platform device/resource. It supports SDV1-3 and LDO1-20, including SDV suspend/DVM voltage controls.

Important APIs/types/functions: `struct max8925_regulator_info` embeds a descriptor plus voltage and enable register addresses. `max8925_set_voltage_sel()`/`get_voltage_sel()` use parent `max8925_set_bits()` and register reads. `max8925_enable()`, `max8925_disable()`, and `max8925_is_enabled()` manage I2C sequencing bits. SDV ops add suspend voltage/enable/disable callbacks.

Control flow: platform probe obtains the parent chip, finds the regulator descriptor whose `vol_reg` matches the platform `IORESOURCE_REG`, fills the parent I2C pointer, applies optional init data, registers one regulator, and stores the rdev as platform data.

State and persistence: descriptor table entries are static and get their `i2c` pointer filled at probe. Hardware registers store enable, sequencing, and voltage settings.

Dependencies and integration: depends on MAX8925 MFD APIs, platform resources created by the parent, and regulator core.

Risks and test signals: static descriptor entries are mutated with the parent I2C pointer, so multiple PMIC instances could conflict. Floating-point-looking macro arguments are multiplied by 1000 in C constants but deserve compile/test scrutiny. Test resource-to-regulator matching, I2C sequencing detection, SDV DVM suspend range, LDO enable semantics, and missing resource failure.

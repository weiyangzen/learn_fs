# sources/distributed-fs/ceph-client/drivers/regulator/pv88080-regulator.c

Purpose: implements the PV88080 regulator driver for AA/BA register-layout variants. It registers three buck regulators and one HVBUCK, supports dynamic voltage range calculation, buck current limits, buck modes, and global fault IRQ notifications.

Important APIs/types/functions: `struct pv88080_compatible_regmap` describes variant-specific register addresses and masks for AA and BA silicon. `struct pv88080_regulator` wraps descriptors with mode and range config registers. `pv88080_buck_get_mode()` and `pv88080_buck_set_mode()` map mode bits to regulator modes. Descriptor macros define generic buck and HVBUCK descriptors, which are completed at probe from variant regmap data.

Control flow: probe initializes regmap, selects match data, sets up optional IRQ masking and unmasking, then iterates buck1-3. For each buck it fills descriptor register fields from variant data, reads `conf2` and `conf5`, derives min/step/count from voltage range and gain bits, and registers the regulator. HVBUCK register fields are then filled and registered separately.

State and persistence: `pv88080_regulator_info` is a static mutable descriptor array. Probe writes variant-specific register fields and voltage ranges into it, which is simple for one instance but risky for multiple instances. Hardware config registers determine runtime voltage range.

Dependencies and integration: depends on I2C, regmap, OF/I2C match data, interrupts, and regulator framework. Compatible strings include `pvs,pv88080`, `pvs,pv88080-aa`, and `pvs,pv88080-ba`.

Risks and test signals: static descriptor mutation can leak between devices or variants. Global IRQs are broadcast to all regulators. Test AA and BA variants, dynamic voltage range derivation, HVBUCK registration, current-limit tables, buck mode transitions, IRQ handling, no-IRQ operation, and multiple-instance behavior.

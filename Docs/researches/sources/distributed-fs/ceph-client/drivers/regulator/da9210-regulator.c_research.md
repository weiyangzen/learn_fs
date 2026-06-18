# sources/distributed-fs/ceph-client/drivers/regulator/da9210-regulator.c

Purpose: Implements a compact I2C regulator driver for the single DA9210 buck regulator. It exposes voltage selection, enable/disable, current-limit programming, and fault notifications through the regulator framework.

Important APIs, types, and functions: `struct da9210` stores the single `regulator_dev` and regmap. `da9210_buck_ops` uses standard regulator regmap helpers for enable, voltage selector, and current limit. `da9210_reg` defines the rail's linear 300 mV to 1570 mV range, current-limit table, `VBUCK_A` selector register, `BUCK_CONT` enable bit, and `BUCK_ILIM` current selector. `da9210_irq_handler()` maps `EVENT_B` bits to overcurrent, undervoltage, overtemperature, and regulation-out notifications.

Control flow: Probe allocates state, creates an 8-bit regmap, resolves init data from platform data or OF regulator constraints, masks all interrupt sources to deassert the IRQ line, registers the regulator, then requests a shared threaded IRQ when `i2c->irq` is present. After requesting the IRQ it unmasks selected fault bits in `MASK_B`.

State and persistence: The driver relies on PMIC registers for enabled state, voltage selector, and current limit. The only in-memory state is the rdev/regmap pair. Interrupt mask state is programmed at probe; handled events are cleared by writing their bits back to `EVENT_B`.

Dependencies and integration points: It depends on I2C, regmap, OF regulator data, optional legacy platform data from `struct da9210_pdata`, and the private register header. Compatible string `dlg,da9210` and I2C ID `da9210` bind the driver.

Risks and test signals: Test no-IRQ operation, IRQ event clearing, mask register writes, OF/platform init-data selection, current-limit selector values, and voltage boundaries. Because the regmap config does not model paged ranges from the header, accesses used by this driver must stay within the simple 8-bit register window it actually touches.

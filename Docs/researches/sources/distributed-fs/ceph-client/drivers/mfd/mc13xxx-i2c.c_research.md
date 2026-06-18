# sources/distributed-fs/ceph-client/drivers/mfd/mc13xxx-i2c.c

Purpose: I2C transport driver for MC13892 and MC34708 PMIC variants. It creates an 8-bit register, 24-bit value regmap and delegates all PMIC behavior to `mc13xxx_common_init()`.

Important APIs, types, and functions: `mc13xxx_i2c_device_id[]` and `mc13xxx_dt_ids[]` bind variants to `struct mc13xxx_variant`. `mc13xxx_regmap_i2c_config` defines regmap width and disables caching. `mc13xxx_i2c_probe()` allocates `struct mc13xxx`, sets `irq`, initializes regmap with `devm_regmap_init_i2c()`, stores the variant from match data, and calls the common core. `mc13xxx_i2c_remove()` calls `mc13xxx_common_exit()`.

Control flow: registered at `subsys_initcall()`, the driver probes early, sets driver data before common initialization, and relies on devm for memory/regmap cleanup while the common exit handles children and irqchip removal.

State and persistence: no transport-specific persistent state beyond the common `struct mc13xxx`. Hardware access is direct through regmap with no cache.

Dependencies and integration points: depends on the common local header `mc13xxx.h`, public `<linux/mfd/mc13xxx.h>`, I2C match tables, and MFD children registered by the common core. It does not support MC13783 over I2C in its match table.

Risks: lack of explicit `MODULE_DEVICE_TABLE(i2c/of)` coverage would be a risk, but both are present. Variant match data must exist for every ID, or common init dereferences a NULL variant. Test signals include I2C regmap read/write width, IRQ propagation from `client->irq`, OF and legacy ID matching, and remove path cleanup.

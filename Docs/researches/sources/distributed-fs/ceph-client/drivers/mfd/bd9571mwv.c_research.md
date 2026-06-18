<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/bd9571mwv.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/bd9571mwv.c

Purpose: implements the ROHM BD9571MWV-M and BD9574MWF-M PMIC MFD core. It identifies the product, selects variant-specific regmap access tables and child cells, registers a regmap IRQ chip, and exposes regulator and GPIO children.

Important APIs and functions: `bd9571mwv_probe` is the lifecycle entry point; `bd957x_identify` validates vendor/product/revision registers after regmap creation. Static tables define BD9571MWV and BD9574MWF readable/writable/volatile ranges, regmap configs, shared IRQ bits, variant IRQ chips, and child cell arrays.

Control flow: probe reads product code with raw SMBus before regmap setup, selects the BD9571 or BD9574 configuration, initializes I2C regmap, validates vendor and revision registers, registers a one-register regmap IRQ chip with `IRQF_ONESHOT`, and adds variant-specific regulator/GPIO children with the IRQ domain.

State and persistence: the core does not allocate a private state structure; devm owns the regmap and IRQ data. Hardware state includes PMIC voltage, GPIO, DVFS, backup mode, and interrupt registers, with volatile status ranges excluded from cache.

Dependencies and integration points: depends on I2C, regmap and regmap IRQ, MFD core, ROHM generic headers, and child regulator/GPIO drivers. IRQ resources are provided through the regmap IRQ domain.

Risks: if `client->irq` is zero, `devm_regmap_add_irq_chip` will likely fail and prevent even regulator-only use. Product selection happens before regmap access filtering, so I2C read failures abort early. `bd957x_identify` reads product and revision but only validates vendor code. The driver name and I2C ID table only name BD9571MWV despite OF supporting BD9574MWF.

Test signals: probe BD9571 and BD9574 products, vendor mismatch handling, IRQ chip delivery for PMIC interrupt bits, regulator/GPIO child binding, no-IRQ board behavior, and regmap table coverage for DVFS/GPIO/interrupt registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/bd9571mwv.c -->

# sources/distributed-fs/ceph-client/drivers/mfd/da9062-core.c

## Purpose
`da9062-core.c` is a combined I2C, MFD, regmap, and IRQ driver for Dialog DA9061 and DA9062 PMICs. It selects chip-specific access tables and child devices, validates hardware identity, configures IRQ polarity, and registers the PMIC children.

## Important APIs, Types, and Functions
`da9061_irqs[]` and `da9062_irqs[]` describe event bits for each chip family. `da9061_irq_chip` and `da9062_irq_chip` expose three event/mask registers. `da9061_devs_irq/noirq` and `da9062_devs_irq/noirq` describe child devices with and without IRQ resources. `da9062_clear_fault_log()`, `da9062_get_device_type()`, and `da9062_configure_irq_type()` perform setup checks. The many `regmap_range` and `regmap_access_table` definitions encode DA9061/DA9062 readable, writeable, and volatile register windows.

## Control Flow
Probe allocates `struct da9062`, gets the chip type from OF/I2C match data, chooses the no-IRQ child list and regmap config, creates the I2C regmap, switches to I2C mode when full I2C functionality is available, clears the fault log, validates the device and variant ID, then conditionally reselects IRQ-capable child cells and the proper regmap IRQ chip if `i2c->irq` exists. IRQ setup programs `CONFIG_A` according to the parent IRQ trigger type, adds a shared oneshot regmap IRQ chip, and passes the assigned IRQ base to `mfd_add_devices()`.

## State and Persistence
`struct da9062` holds device, regmap, type, and regmap IRQ data. The driver updates persistent hardware registers such as `CONFIG_J` bus mode, `CONFIG_A` IRQ type, and clears fault-log/event registers. Regmap uses `REGCACHE_MAPLE`, but no explicit suspend persistence is implemented here.

## Dependencies and Integration Points
It depends on I2C, OF matching, regmap ranges, regmap-irq, MFD core, and DA9062 regulator/watchdog/thermal/RTC/onkey/GPIO children. Parent IRQ trigger type is read from the IRQ descriptor and mirrored into PMIC configuration.

## Risks and Edge Cases
`da9062_i2c_remove()` always calls `regmap_del_irq_chip(i2c->irq, chip->regmap_irq)` even though probe supports no-IRQ mode; a no-IRQ probed instance could expose an invalid cleanup path. Unsupported parent IRQ types abort probe. `da9062_get_device_type()` logs the variant but only rejects too-old MRC; it does not require the VRC to match the selected compatible. Event clearing can discard pre-boot events.

## Test Signals
Test DA9061 and DA9062 compatibles, no-IRQ and IRQ-equipped systems, low/high parent IRQ configuration, invalid edge IRQ rejection, register access-table coverage, child resources, fault-log clearing, and remove behavior in no-IRQ configurations.

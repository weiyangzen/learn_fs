# sources/distributed-fs/ceph-client/drivers/mfd/da9055-core.c

## Purpose
`da9055-core.c` is the common MFD core for the Dialog DA9055 PMIC. It defines regmap access policy, the PMIC interrupt chip, child MFD devices, and the init/exit routines used by the I2C transport.

## Important APIs, Types, and Functions
`da9055_register_readable()`, `da9055_register_writeable()`, and `da9055_register_volatile()` define the exported `da9055_regmap_config`. `da9055_irqs[]` maps onkey, alarm, tick, hwmon, and regulator current-limit events. `da9055_regmap_irq_chip` exposes the three event/mask registers. `da9055_devs[]` lists GPIO, regulators, onkey, RTC, hwmon, and watchdog children. `da9055_device_init()` and `da9055_device_exit()` are exported to the bus driver.

## Control Flow
Initialization runs optional platform init, selects either a platform-provided IRQ base or dynamic base, clears all event registers with a three-byte group write, installs the regmap IRQ chip on `chip_irq`, records the assigned IRQ base, and registers all child devices with that IRQ base. Failure after IRQ setup removes the regmap IRQ chip. Exit deletes the IRQ chip and removes children.

## State and Persistence
State is held in `struct da9055`: regmap, device pointer, chip IRQ, IRQ base, and regmap IRQ data. Hardware state consists of PMIC event/mask/control/regulator/RTC registers. There is no persistence beyond PMIC hardware retention.

## Dependencies and Integration Points
This core depends on regmap, regmap-irq, MFD core, DA9055 register definitions, and optional platform data. Child drivers receive compatible strings and named IRQ resources.

## Risks and Edge Cases
`DA9055_IRQ_ADC_MASK` and `DA9055_IRQ_BUCK_ILIM_MASK` both use bit `0x08` but in different event-register offsets; offset correctness is essential. `da9055_device_exit()` deletes the IRQ chip before removing children, which can matter if child remove paths expect live IRQ mappings. Event clearing at init can discard events that occurred before Linux handled them.

## Test Signals
Check regmap access filters, event clear writes to A/B/C, IRQ base assignment, child resources for RTC/hwmon/regulator/onkey, dynamic and fixed IRQ base operation, and cleanup after `mfd_add_devices()` failure.

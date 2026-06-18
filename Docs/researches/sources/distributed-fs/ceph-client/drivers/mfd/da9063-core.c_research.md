# sources/distributed-fs/ceph-client/drivers/mfd/da9063-core.c

## Purpose
`da9063-core.c` is the common MFD core for Dialog DA9063 and DA9063L PMICs. It clears fault logs, initializes the interrupt subsystem, and registers common and DA9063-only child devices.

## Important APIs, Types, and Functions
Resource arrays describe regulator, RTC, onkey, and hwmon IRQs. `da9063_common_devs[]` registers regulators, LEDs, watchdog, hwmon, onkey, and vibration children. `da9063_devs[]` registers the RTC child only for full DA9063, not DA9063L. `da9063_clear_fault_log()` reports and clears PMIC fault bits. `da9063_device_init()` is the core init entry called by the I2C driver.

## Control Flow
`da9063_device_init()` clears the fault log, initializes flags and IRQ fields, calls `da9063_irq_init()`, records the regmap IRQ base, registers common children via `devm_mfd_add_devices()`, and conditionally registers DA9063-only RTC support when `da9063->type == PMIC_TYPE_DA9063`.

## State and Persistence
State is stored in `struct da9063`: type, variant, flags, chip IRQ, IRQ base, regmap, and regmap IRQ data. Hardware fault-log state is cleared by writing back the read fault bits. Child devices are devm-managed.

## Dependencies and Integration Points
The file depends on regmap, MFD core, DA9063 register definitions, and `da9063_irq_init()` from the IRQ file. Child drivers consume DA9063 driver-name constants and named IRQ resources.

## Risks and Edge Cases
Fault-log clearing writes the read value even when zero, so bus errors must be distinguished from harmless empty logs. The core requires IRQ initialization to succeed; platforms without a configured PMIC IRQ cannot register children. The file includes unused proc/kthread/uaccess headers, suggesting historical baggage but no runtime effect.

## Test Signals
Verify DA9063 versus DA9063L child differences, fault-log bit reporting and clearing, regmap IRQ base propagation, child IRQ resource mapping, and probe failure when the parent IRQ is missing.

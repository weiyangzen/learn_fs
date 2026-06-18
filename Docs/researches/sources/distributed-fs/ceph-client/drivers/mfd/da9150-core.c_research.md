# sources/distributed-fs/ceph-client/drivers/mfd/da9150-core.c

## Purpose
`da9150-core.c` is the MFD core and I2C driver for the Dialog DA9150 charger/fuel-gauge/GPADC device. It provides exported register/QIF helpers, regmap IRQ support, child device registration, and shutdown behavior.

## Important APIs, Types, and Functions
Raw QIF helpers `da9150_i2c_read_device()` and `da9150_i2c_write_device()` implement STOP/START read semantics. Exported APIs include `da9150_read_qif()`, `da9150_write_qif()`, `da9150_reg_read()`, `da9150_reg_write()`, `da9150_set_bits()`, `da9150_bulk_read()`, and `da9150_bulk_write()`. `da9150_volatile_reg()` and `da9150_regmap_config` define paged regmap behavior. `da9150_irqs[]` and `da9150_regmap_irq_chip` expose EVENT_E through EVENT_H. `da9150_devs[]` registers GPADC, charger, and fuel-gauge children.

## Control Flow
Probe allocates `struct da9150`, initializes the paged I2C regmap, reads the secondary QIF base address from `CORE2WIRE_CTRL_A`, creates a dummy I2C QIF client, applies optional platform fuel-gauge data, installs the regmap IRQ chip, enables wake on the parent IRQ, and adds child devices. Remove deletes the IRQ chip, removes children, and unregisters the QIF client. Shutdown enables PM wake and sets the device disabled bit.

## State and Persistence
State includes the primary I2C client, secondary QIF client, regmap, IRQ base, and regmap IRQ data. Hardware state includes paged PMIC registers, QIF address routing, event/mask bits, wake configuration, and disabled mode set during shutdown.

## Dependencies and Integration Points
The driver depends on I2C, regmap, regmap-irq, MFD core, DA9150 register definitions, optional platform data, and child drivers for GPADC, charger, and fuel gauge. QIF helpers are exported for child use.

## Risks and Edge Cases
Raw QIF write allocates a temporary buffer for each access and can fail under memory pressure. `da9150_reg_read()` returns `u8`, so callers cannot distinguish a read error from an actual register value without logs. `enable_irq_wake()` is not explicitly disabled. Shutdown deliberately changes power state, so tests must avoid triggering it unexpectedly.

## Test Signals
Verify QIF dummy address calculation, STOP/START raw read behavior, paged regmap access, regmap IRQ events for charger/GPADC/fuel gauge, platform fuel-gauge data propagation, wake enablement, and shutdown writes to `CONFIG_D` and `CONTROL_C`.

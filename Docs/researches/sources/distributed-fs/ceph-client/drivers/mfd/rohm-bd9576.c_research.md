# sources/distributed-fs/ceph-client/drivers/mfd/rohm-bd9576.c

### Purpose
`rohm-bd9576.c` is the MFD parent driver for ROHM BD9576MUF and BD9573MUF PMICs. It creates regulator and watchdog child devices and conditionally exposes BD9576 regulator IRQ resources when a usable PMIC IRQ is present.

### Important APIs, Types, And Functions
The central function is `bd957x_i2c_probe()`. Static definitions include `bd9573_mfd_cells[]`, `bd9576_mfd_cells[]`, `bd9576_regulator_irqs[]`, volatile regmap ranges, `bd957x_regmap`, `bd9576_irqs[]`, and `bd9576_irq_chip`. The enum indexes the regulator and watchdog cells so resources can be attached to the regulator cell before MFD registration.

### Control Flow
Probe reads chip type from OF match data. BD9576 uses IRQs only if `i2c->irq` is populated; BD9573 always disables usable IRQs because its fatal IRQs cannot be serviced before SoC power loss. The driver initializes an 8-bit maple-cached regmap. If IRQs are usable, it attaches named thermal/overvoltage/undervoltage resources to the regulator cell, registers a one-register regmap IRQ chip, and passes its domain to MFD children. Otherwise it masks all main interrupts in hardware and registers children without an IRQ domain.

### State, Persistence, And Dependencies
Runtime state is device-managed regmap, optional regmap IRQ data, and MFD children. Persistent hardware state includes the interrupt mask register and any IRQ masking done by regmap-irq. Volatile regmap ranges cover SMRB assert, PMIC internal status, thermal status, OVP through system status, and main interrupt status. Dependencies are I2C, OF matching, regmap, regmap-irq, MFD core, and ROHM BD957x register definitions.

### Integration Points
The regulator child names differ by chip (`bd9573-regulator` or `bd9576-regulator`) and the watchdog child name is `bd9576-wdt` for both. Regulator notification behavior depends on whether this parent provides IRQ resources; without a valid IRQ, the child can still regulate but should omit interrupt-driven notifiers.

### Risks
The driver intentionally tolerates missing BD9576 IRQs because the PMIC can hold the IRQ line asserted for the whole fault condition. That avoids interrupt storms but loses notification coverage. BD9573 fatal IRQs are never exposed. If `bd9576_mfd_cells` is shared across instances, modifying the regulator cell resources during one probe can affect later probes. Masking all IRQs on the no-IRQ path must succeed or probe fails.

### Test Signals
Test BD9576 with and without a DT IRQ: with IRQ, regulator child resources should include thermal, OVD, and UVD IRQs; without IRQ, `BD957X_REG_INT_MAIN_MASK` should have all bits masked and child creation should still succeed. BD9573 tests should confirm no IRQ domain is exposed. Fault-injection should cover regmap init failure, IRQ chip add failure, and MFD add failure.

# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sl28cpld.c

## Purpose
Provides a compact interrupt-controller driver for the Kontron SL28 CPLD. It exposes eight CPLD interrupt bits through the regmap-irq framework with status, enable, and ack registers derived from the device's `reg` property.

## Important APIs, Types, And Functions
`sl28cpld_irqs` declares eight `REGMAP_IRQ_REG_LINE()` entries. `struct sl28cpld_intc` stores the parent regmap, a mutable `regmap_irq_chip`, and returned regmap IRQ chip data. `sl28cpld_intc_probe()` wires the regmap IRQ chip into the platform IRQ.

## Control Flow
Probe requires a parent MFD device, obtains its regmap, gets the parent IRQ, reads the register base offset, populates `regmap_irq_chip` fields, and calls `devm_regmap_add_irq_chip_fwnode()` with shared oneshot flags. Runtime masking, acking, status reads, and nested interrupt dispatch are handled by regmap-irq core.

## State And Persistence
The driver has no custom runtime state beyond the allocated chip descriptor. Persistent hardware state is the CPLD enable and pending registers managed by regmap-irq. Device-managed resources remove the registration with the platform device.

## Dependencies And Integration Points
Depends on the parent SL28 CPLD MFD regmap, Linux platform-device APIs, generic interrupt flags, firmware properties, and compatible `kontron,sl28cpld-intc`.

## Risks
The `reg` property must point at the correct CPLD interrupt block because all register offsets are derived from it. Parent IRQ flags are shared/oneshot, so interrupt lines must tolerate threaded handling. Any change to CPLD register layout requires updating status/unmask/ack offsets together.

## Test Signals
Probe under the SL28 CPLD parent, verify eight child IRQs appear, and trigger each CPLD source while checking mask, unmask, and ack behavior. Regression tests should include missing parent regmap, missing parent IRQ, and incorrect `reg` property handling.

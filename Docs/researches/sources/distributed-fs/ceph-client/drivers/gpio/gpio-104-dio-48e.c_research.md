# sources/distributed-fs/ceph-client/drivers/gpio/gpio-104-dio-48e.c

## Purpose
This ISA driver supports ACCES 104-DIO-48E and 104-DIO-24E boards. It exposes two i8255 PPI blocks as 48 GPIO lines, wires the board interrupt sources into a regmap IRQ domain, and registers the on-board i8254 counter/timer through the i8254 regmap helper.

## Important APIs, types, and functions
Key module parameters are `base[]` and `irq[]`, registered with `module_param_hw_array()`. `struct dio48e_gpio` stores the shared raw spinlock, main regmap, MMIO/ioport mapping, saved IRQ flags, and current IRQ mask. Important helpers are `dio48e_regmap_lock()`, `pit_regmap_lock()`, `dio48e_handle_mask_sync()`, `dio48e_irq_init_hw()`, and `dio48e_probe()`. Integration hinges on `devm_regmap_init_mmio()`, `devm_regmap_add_irq_chip()`, `devm_i8254_regmap_register()`, and `devm_i8255_regmap_register()`.

## Control flow
`module_isa_driver_with_irq()` instantiates one device per configured base/IRQ pair. Probe reserves the I/O region, maps 16 ports, initializes a regmap with explicit readable/writable/volatile/precious ranges, initializes a second regmap view for the i8254, creates a regmap IRQ chip, disables interrupts before registration, registers the IRQ chip, registers the timer, and finally registers the i8255 GPIO block with line names and the IRQ domain.

## State and persistence behavior
State is hardware register state plus runtime driver state. The regmap uses `REGCACHE_FLAT`, the device interrupt enable state is mirrored in `irq_mask`, and the i8254 access window is enabled and disabled in the PIT regmap lock/unlock path. No filesystem state is persisted.

## Dependencies and integration points
The driver depends on ISA probing, I/O port resources, regmap, regmap-irq, raw spinlocks, the local `gpio-i8255.h` helper, and the i8254 helper namespace. It imports the `I8255` and `I8254` namespaces and publishes child GPIO IRQs only for bit 3 of Port C on each PPI.

## Risks and edge cases
The interrupt enable/disable register is accessed by writes and reads to the same offset, so precious regmap treatment matters. The shared lock also gates PIT address-window changes; a bug there could corrupt normal GPIO register accesses. Probe requires valid module base/IRQ arrays, and interrupt support is limited to rising edges on two PPI lines.

## Test signals
Test by loading with known `base=` and `irq=` values, verifying 48 named GPIO lines, toggling i8255 outputs, reading inputs, exercising the i8254 registration, and confirming the two supported GPIO IRQs enable, clear, and disable without spurious interrupts.

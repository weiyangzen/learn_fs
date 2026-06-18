# sources/distributed-fs/ceph-client/drivers/gpio/gpio-104-idio-16.c

## Purpose
This driver supports ACCES 104-IDIO-16 family ISA boards and related 8/16-channel variants. It delegates the common IDIO-16 GPIO behavior to `gpio-idio-16.h` while providing the board-specific I/O range, regmap layout, and IRQ descriptions.

## Important APIs, types, and functions
Module parameters `base[]` and `irq[]` enumerate boards. `idio_16_regmap_config` defines writable output/control ranges, readable input/status ranges, volatile reads, and precious interrupt status. `idio_16_regmap_irqs[]` describes edge-both IRQs for input GPIOs 16 through 31. `idio_16_probe()` wires these into `devm_idio_16_regmap_register()`.

## Control flow
The ISA driver claims an 8-port region, maps it, initializes the regmap, fills `struct idio_16_regmap_config` with the regmap, IRQ table, hardware IRQ, and `no_status = true`, then registers the common IDIO-16 regmap GPIO implementation.

## State and persistence behavior
State is held in the board registers and in regmap cache. The driver itself has no long-lived private structure beyond devres-managed objects. Output register values may be cached by regmap; input and status registers are volatile.

## Dependencies and integration points
Dependencies are ISA, ioport mapping, regmap, and the local `GPIO_IDIO_16` helper namespace. The helper owns most GPIO operations, while this file supplies the ACCES 104-IDIO-16 register access contract.

## Risks and edge cases
Only input lines support IRQs, so consumers must not expect interrupts for output lines. The status register is precious and can be side-effectful. Incorrect base/IRQ module parameters or conflicting I/O regions will fail probe.

## Test signals
Load with valid base/IRQ parameters, confirm the helper exposes the expected output/input split, verify writes affect output lines only, reads work for input lines, and edge-both interrupts are delivered for GPIOs 16-31.

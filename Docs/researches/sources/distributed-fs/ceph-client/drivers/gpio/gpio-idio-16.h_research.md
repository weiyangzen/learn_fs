<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-idio-16.h -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-idio-16.h

## Purpose
`gpio-idio-16.h` defines the public configuration structure for the ACCES IDIO-16 gpio-regmap helper.

## Important APIs, types, and functions
It declares `struct idio_16_regmap_config` with parent, regmap, regmap IRQ descriptors, IRQ line, no-status flag, and filter flag, plus `devm_idio_16_regmap_register()`.

## Control flow
Bus-specific drivers include this header, build the regmap and regmap IRQ table, set flags for device variant behavior, and call the devm helper in probe.

## State and persistence behavior
The header itself has no state; its fields control how the C helper initializes hardware and represents IRQ state.

## Dependencies and integration points
Only forward declarations are used, keeping the interface suitable for ISA/PCI/USB wrapper drivers. It integrates with regmap and regmap-irq.

## Risks and edge cases
Supplying a mismatched IRQ table or wrong `no_status`/`filters` flags can make child IRQs unreliable. The helper requires `regmap_irqs`, so wrappers for non-interrupt-capable variants need a different path.

## Test signals
Compile tests for users, invalid config tests, and wrapper probe tests for status/no-status and filter/non-filter devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-idio-16.h -->

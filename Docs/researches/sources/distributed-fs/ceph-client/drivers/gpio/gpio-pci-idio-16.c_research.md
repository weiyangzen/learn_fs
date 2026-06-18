<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pci-idio-16.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pci-idio-16.c

## Purpose
PCI wrapper for ACCES PCI-IDIO-16. It maps board I/O registers into regmap, defines access tables and input IRQs, and delegates GPIO behavior to the shared IDIO-16 helper.

## Important APIs, types, and functions
`idio_16_regmap_config` describes 8-bit I/O-port registers with flat cache, volatile read ranges, and a precious status register. `idio_16_regmap_irqs[]` maps GPIOs 16-31 as both-edge capable inputs. `idio_16_probe()` enables PCI, maps BAR 2, initializes regmap, fills helper config, and calls `devm_idio_16_regmap_register()`.

## Control flow
Probe is linear and delegates after regmap setup. The local file does not implement GPIO callbacks directly; the imported helper provides them.

## State and persistence behavior
Local state is limited to regmap/helper-owned state. The precious register avoids accidental interrupt-state-consuming reads.

## Dependencies and integration points
Depends on PCI ID `0x494F:0x0DC8`, regmap MMIO over I/O ports, regmap IRQs, and namespace `GPIO_IDIO_16`.

## Risks and edge cases
Correctness depends on accurate access tables and the helper. Only input lines interrupt; output IRQ requests must be rejected by the helper.

## Test signals
BAR mapping, regmap range enforcement, expected helper GPIO registration, input-only IRQ delivery on GPIOs 16-31, and filter handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pci-idio-16.c -->

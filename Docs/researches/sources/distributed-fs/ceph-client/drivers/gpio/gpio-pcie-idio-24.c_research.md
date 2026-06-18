<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pcie-idio-24.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pcie-idio-24.c

## Purpose
ACCES PCIe-IDIO-24 family driver exposing 24 FET outputs, 24 isolated inputs, and 8 TTL/CMOS configurable lines through gpio-regmap, with change-of-state IRQs through regmap_irq.

## Important APIs, types, and functions
`struct idio_24_gpio` stores board regmap, raw lock, and cached COS IRQ type bits. Important functions are `idio_24_handle_mask_sync()`, `idio_24_set_type_config()`, `idio_24_reg_mask_xlate()`, and `idio_24_probe()`. Regmap configs cover the PLX PEX8311 interrupt CSR and board I/O registers.

## Control flow
Probe maps PLX and board BARs, creates regmaps, initializes IRQ types to both edges, soft-resets the board, enables PLX interrupt forwarding, registers a regmap IRQ chip on the PCI IRQ, and registers a 56-line gpio-regmap chip. Offset mapping distinguishes FET outputs, isolated inputs, and TTL lines.

## State and persistence behavior
State is mostly hardware/regmap plus cached `irq_type`. No PM hook exists. TTL direction is controlled by a shared control bit.

## Dependencies and integration points
Uses PCI, regmap, gpio-regmap, regmap_irq, and PLX PEX8311 interrupt forwarding. Multiple ACCES PCI IDs bind to the same driver.

## Risks and edge cases
TTL direction is group-wide although exposed per GPIO operation. COS mask/type synchronization depends on custom callbacks. Failed PLX interrupt enable breaks IRQs while GPIO data may still work.

## Test signals
PCI IDs, soft reset, PLX enable bits, 56 names/layout, FET writes, isolated reads, TTL direction/data switching, IRQ domain mapping, and edge type configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pcie-idio-24.c -->

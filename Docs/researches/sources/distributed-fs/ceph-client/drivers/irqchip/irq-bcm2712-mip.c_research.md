# sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm2712-mip.c

## Purpose
Implements the Broadcom BCM2712 MIP MSI-X interrupt controller as an MSI parent domain layered over a parent interrupt domain, typically GIC.

## Important APIs, Types, and Functions
`struct mip_priv` stores MMIO, MSI message address, SPI base/range/offset, bitmap allocator, parent domain, and device. Key functions are `mip_parse_dt()`, `mip_init_domains()`, `mip_middle_domain_alloc()`, `mip_middle_domain_free()`, `mip_compose_msi_msg()`, and platform probe registration through `IRQCHIP_PLATFORM_DRIVER`.

## Control Flow
Probe allocates private data, parses `msi-ranges`, optional `brcm,msi-offset`, and a second `reg` entry as MSI write address, maps MMIO, allocates the hwirq bitmap, then creates an MSI parent domain. Allocation reserves a power-of-two bitmap region, maps it to parent SPI hwirqs, configures parent IRQs as edge rising, installs the MIP middle chip, and marks IRQs single-target/affinity-on-activate.

## State and Persistence
Persistent state includes the allocation bitmap, MMIO mask/config registers, MSI address, parent domain reference, and per-IRQ chip data pointing back to `mip_priv`. Hardware is configured host-unmasked, VPU-masked, edge-triggered.

## Dependencies and Integration Points
Uses `irq-msi-lib`, generic MSI parent ops, OF MSI range parsing, platform irqchip probing, and parent-domain allocation. It serves PCI MSI/MSI-X through `DOMAIN_BUS_GENERIC_MSI` selection.

## Risks and Test Signals
Risks include malformed `msi-ranges`, alignment assumptions in bitmap allocation, hwirq offset/base confusion, and leaked allocations if parent setup partially fails. Test signals are MSI domain creation logs, PCI MSI/MSI-X allocation success, correct composed MSI address/data, and interrupt delivery through parent GIC SPIs.

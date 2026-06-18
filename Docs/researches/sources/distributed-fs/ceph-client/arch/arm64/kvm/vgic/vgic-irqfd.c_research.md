<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-irqfd.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-irqfd.c

## Purpose
This file connects KVM irqfd/routing infrastructure to arm64 VGIC interrupt injection. It supports IRQCHIP routing for SPIs and MSI routing through a VGIC ITS, including an atomic fast path.

## Important APIs, Types, And Functions
- `kvm_set_routing_entry()` converts userspace `kvm_irq_routing_entry` records into kernel routing entries for IRQCHIP and MSI routes.
- `kvm_set_msi()` injects an MSI via VGIC ITS for irqfd and userspace MSI injection.
- `kvm_arch_set_irq_inatomic()` attempts fast in-atomic irqfd injection for MSI cached translations or SPI line injection.
- `kvm_vgic_setup_default_irq_routing()` creates default IRQCHIP routing entries for all SPIs.
- `vgic_irqfd_set_irq()` is the IRQCHIP route callback that maps a pin to an SPI INTID and calls `kvm_vgic_inject_irq()`.
- `kvm_populate_msi()` copies MSI fields from the kernel routing entry into `struct kvm_msi`.

## Control Flow
Userspace routing updates call `kvm_set_routing_entry()`, which validates IRQCHIP pins/chips or stores MSI address/data/flags/devid. IRQCHIP injection adds `VGIC_NR_PRIVATE_IRQS` to the pin to form the SPI INTID, validates it, and injects the level. MSI injection requires an ITS and ignores deasserted level calls.

The atomic path rejects deassertions with `-EWOULDBLOCK`. MSI routes use cached ITS translation when an ITS exists. IRQCHIP routes can inject SPIs in atomic context if the VGIC is initialized. Otherwise callers fall back to the non-atomic path.

## State And Persistence Behavior
Routing entries persist in KVM’s generic IRQ routing table, not in this file. Default routing allocation is temporary and freed after `kvm_set_irq_routing()`. Injection mutates VGIC IRQ pending/line state through VGIC helpers.

## Dependencies And Integration Points
The file depends on KVM IRQ routing, irqfd callbacks, VGIC IRQ injection, ITS MSI injection and cached translation, and VGIC initialization state. It is called from generic KVM irqfd/eventfd and irq routing paths.

## Risks And Edge Cases
- IRQCHIP pins are zero-based SPIs and must be translated by `VGIC_NR_PRIVATE_IRQS`.
- Invalid SPI ranges return `-EINVAL`.
- MSI injection requires an ITS and returns `-ENODEV` without one.
- Deasserted MSI or atomic deassertion is not injected.
- Atomic SPI injection is only valid after VGIC initialization.
- Default routing count follows `dist->nr_spis`; incorrect SPI sizing propagates into routing setup.

## Test Signals
Tests should cover default SPI route creation, irqfd SPI injection, userspace SPI injection, MSI injection with and without ITS, atomic irqfd fast path, invalid pins/chips, invalid SPI ranges, and deassertion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-irqfd.c -->

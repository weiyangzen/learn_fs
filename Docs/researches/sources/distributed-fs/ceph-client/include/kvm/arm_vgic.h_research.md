<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_vgic.h -->
# sources/distributed-fs/ceph-client/include/kvm/arm_vgic.h

## Purpose
`arm_vgic.h` defines ARM KVM's virtual GIC data model and APIs for GICv2, GICv3, GICv4 forwarding, and GICv5 support. It is the shared contract between KVM core, VGIC MMIO devices, ITS/LPI handling, VCPU world-switch state, and in-kernel interrupt injection.

## Important APIs, types, and functions
The header defines INTID limits and classification helpers for SGI/PPI/SPI/LPI, including GICv5 hardware IRQ encoding helpers. Key types include `vgic_global`, `irq_ops`, `vgic_irq`, `vgic_io_device`, `vgic_its`, `vgic_redist_region`, `vgic_v5_vm`, `vgic_dist`, `vgic_v2_cpu_if`, `vgic_v3_cpu_if`, `vgic_v5_cpu_if`, `vgic_v5_ppi_caps`, and `vgic_cpu`. APIs cover creation/destruction, VCPU init/destroy, resource mapping, hyp init, IRQ injection, IRQ owner/ops setup, physical IRQ mapping, load/put, hwstate sync/flush, SGI dispatch, default routing, GICv4 forwarding, GICv5 PPI finalization, nested-state checks, and CPU hotplug.

## Control flow
VM setup chooses a VGIC model, initializes distributor/redistributor/ITS state, maps MMIO iodev regions, and initializes per-VCPU private interrupts and CPU interface state. Guest MMIO and sysreg paths mutate `vgic_irq` and distributor state under locks. Before guest entry KVM loads CPU interface state; on exit it syncs or flushes hardware state and handles pending/active lists.

## State and persistence behavior
Persistent VM state includes distributor addresses, enabled/ready flags, SPI/LPI arrays, ITS tables, GICv4 VM data, GICv5 PPI masks, implementation revision, and routing properties. Per-VCPU state includes private IRQs, AP lists, redistributor mapping, pending table address, priority/id-bit caches, and CPU interface registers. Many fields are migration-visible.

## Dependencies and integration points
The header depends on KVM MMIO iodev support, xarrays, mutexes, raw spinlocks, static keys, irqchip GICv4/GICv5 definitions, and KVM userspace device attributes. It integrates with irq routing, in-kernel devices, ITS emulation, physical interrupt forwarding, nested virtualization, CPU hotplug, and timer/PMU PPIs.

## Risks and test signals
Risks include INTID classification errors across GIC versions, AP-list races, wrong LPI translation-cache invalidation, mismatched migration ABI revision, physical IRQ forwarding leaks, and GICv5 PPI mask inconsistencies. Test signals include KVM VGIC selftests, irq routing/injection tests, ITS/MSI tests, migration save/restore, nested VGIC tests, CPU hotplug, and GICv2/v3/v5 configuration builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_vgic.h -->

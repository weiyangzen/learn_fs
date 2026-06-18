# sources/distributed-fs/ceph-client/drivers/iommu/hyperv-iommu.c

## Purpose

`hyperv-iommu.c` is a stub IRQ-remapping driver for Hyper-V x86 systems. It creates an IRQ-remapping domain for the Hyper-V-emulated IO-APIC, constrains guest IO-APIC interrupt affinity when real remapping is unavailable, and provides a root-partition path that maps/unmaps IO-APIC interrupts through Hyper-V hypercalls.

## Important APIs, Types, and Functions

- `IOAPIC_REMAPPING_ENTRY`: 24 entries for the single exposed IO-APIC.
- Guest path: `hyperv_ir_set_affinity`, `hyperv_irq_remapping_alloc/free/select`, `hyperv_ir_domain_ops`.
- `hyperv_prepare_irq_remapping` and `hyperv_enable_irq_remapping`: exported via `hyperv_irq_remap_ops`.
- Root path: `struct hyperv_root_ir_data`, `hyperv_root_ir_compose_msi_msg`, `hyperv_root_ir_set_affinity`, `hyperv_root_irq_remapping_alloc/free`, `hyperv_root_ir_domain_ops`.

## Control Flow

Preparation only proceeds on Microsoft Hyper-V when extended destination IDs are unavailable. It creates a named IRQ-domain hierarchy under the architecture IRQ parent. Guests build an `ioapic_max_cpumask` of CPUs whose physical APIC IDs fit in 8 bits and enforce that mask on IO-APIC IRQ affinity. Root partitions use a different irq chip; composing an MSI message unmaps any previous Hyper-V IO-APIC interrupt, maps the new CPU/vector through `hv_map_ioapic_interrupt`, stores the returned entry, and translates its RTE into MSI message fields.

## State and Persistence Behavior

Guest state is the global `ioapic_max_cpumask` and `ioapic_ir_domain`. Root-partition state is per-IRQ `hyperv_root_ir_data`, including IO-APIC ID, trigger type, and last mapped Hyper-V interrupt entry. Freeing root IRQs unmaps any live Hyper-V mapping and releases the per-IRQ state.

## Dependencies and Integration Points

The file is compiled under `CONFIG_IRQ_REMAP` and integrates with x86 APIC/IO-APIC IRQ domains, Hyper-V detection and hypercalls, MSI message composition, vector cleanup, and the common `irq_remapping.h` operations table.

## Risks and Edge Cases

- Guest affinity is limited to CPUs with APIC IDs below 256; systems with sparse/high APIC IDs may reject requested masks.
- `hyperv_root_ir_compose_msi_msg` silently returns if `hv_map_ioapic_interrupt` fails, leaving the MSI message zeroed.
- Root compose chooses the first online CPU in the effective affinity mask; empty masks would be problematic.
- Domain creation assumes one Hyper-V IO-APIC with 24 entries.

## Test Signals

Boot Hyper-V guest and root-partition configurations with IRQ remapping enabled, exercise IO-APIC IRQ allocation/free, affinity changes across APIC-ID boundaries, xAPIC/x2APIC enable return modes, root hypercall map/unmap paths, and CPU hotplug or affinity updates.

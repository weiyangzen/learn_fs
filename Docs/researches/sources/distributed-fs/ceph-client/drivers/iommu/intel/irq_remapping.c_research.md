<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/irq_remapping.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/irq_remapping.c

Purpose: Intel VT-d interrupt-remapping support for x86 IO-APIC, HPET, PCI MSI/MSI-X, posted MSI, kdump table reuse, and DRHD hotplug. It owns IR table allocation, ACPI DMAR scope parsing, IRTE programming, MSI parent irq-domain integration, and global enable/disable of interrupt remapping.

Important APIs/types/functions: `struct ioapic_scope`, `struct hpet_scope`, `struct irq_2_iommu`, and `struct intel_ir_data` track source devices, IRTE allocation, sub-handles, and cached MSI/IRTE state. Key paths are `intel_prepare_irq_remapping()`, `intel_enable_irq_remapping()`, `intel_setup_irq_remapping()`, `modify_irte()`, `clear_entries()`, `intel_irq_remapping_alloc()`, `intel_irq_remapping_activate()`, `intel_ir_set_affinity()`, `intel_ir_set_vcpu_affinity()`, `intel_irq_remap_add_device()`, and `dmar_ir_hotplug()`.

Control flow: early boot parses DMAR IOAPIC/HPET scopes, verifies every remapping unit supports IR/EIM, allocates a 1 MiB IR table plus bitmap, creates an MSI parent irqdomain, enables queued invalidation, loads kdump IRTEs when applicable, writes IRTA, then enables IRE and blocks compatibility-format interrupts. IRQ allocation delegates vector allocation to the parent domain, allocates one or more contiguous IRTEs, fills source-ID validation according to IOAPIC/HPET/PCI aliasing, composes DMAR-format MSI messages, and writes IRTEs on activation or affinity changes. Free/deactivate paths clear IRTEs, release bitmap regions, and invalidate IEC entries.

State and persistence: persistent state is in `iommu->ir_table`, `iommu->ir_domain`, global `ir_ioapic[]`/`ir_hpet[]`, `eim_mode`, irq-domain chip data, and per-IOMMU `VTD_FLAG_IRQ_REMAP_PRE_ENABLED`. Kdump can copy a firmware/previous-kernel IR table and preserve used entries in the bitmap.

Dependencies and integration: integrates ACPI DMAR parsing, x86 APIC/vector domains, MSI parent domains, PCI DMA aliases, queued invalidation, posted interrupt descriptors, HPET/IOAPIC routing, and Intel IOMMU register locking.

Risks: IRTE updates require correct 128-bit atomic handling for posted formats and strict lock ordering. Source-ID validation is topology-sensitive, especially HPET quirks and PCI aliases. Removing a hotplugged DRHD while bitmap entries remain returns `-EBUSY`. This local source contains duplicate lines/declarations around `map_dev_to_ir()` and IOAPIC scope parsing, which is a compile/review signal for this snapshot.

Test signals: boot with xAPIC/x2APIC, DMAR x2APIC opt-out, kdump with pre-enabled IR, IOAPIC and HPET interrupt delivery, PCI MSI/MSI-X including multi-MSI, posted MSI/vCPU affinity transitions, IRQ affinity migration, DRHD hotplug add/remove, and fault-injection for IRTE allocation and queued invalidation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/irq_remapping.c -->

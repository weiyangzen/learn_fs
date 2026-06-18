# sources/distributed-fs/ceph-client/drivers/iommu/amd/amd_iommu_types.h

## Purpose

This header defines the AMD IOMMU driver's register constants, feature bits, hardware table formats, global lists, state structures, and interrupt-remapping data types. It is the low-level data contract that lets `init.c`, runtime domain code, PASID/PPR handling, debugfs, IRQ remapping, and IOMMUFD nested code agree on AMD-Vi hardware layout.

## Important Constants And Macros

The file defines MMIO register offsets for device tables, command/event/PPR/GA logs, MSI data, interrupt capability extension registers, status, and performance counters. Feature masks cover EFR/EFR2 bits such as PPR, x2APIC, guest translation, GA/GAM, PASID max, SNP, SEV-TIO, GCR3 trap mode, SNP AVIC support, HT range ignore, and 2K interrupt remap support. Command, event, PPR, GA log, DTE, interrupt-table, page-mode, protection, capability, IVINFO, and timeout constants encode the hardware ABI.

Iteration macros traverse `amd_iommu_pci_seg_list`, `amd_iommu_list`, protection-domain device lists, and IVHD DTE flag lists. SBDF conversion macros convert between PCI segment/device identifiers and the packed form used by command-line and debugfs code.

## Important Structures

`struct protection_domain` embeds generic page-table domain variants, device lists, lock, domain ID, mode, dirty tracking flag, per-IOMMU xarray, SVA notifier, PASID attachment list, and vIOMMU list. `struct amd_iommu_pci_seg` stores per-PCI-segment device table, reverse lookup table, IRQ lookup table, old kdump device table copy, alias table, and unity mappings. `struct amd_iommu` stores per-hardware-IOMMU list membership, locks, PCI device pointers, MMIO ranges, ACPI flags, EFRs, device ID, PCI segment, exclusion range, command/event/PPR/GA buffers, IRQ names, interrupt state, command completion semaphore, sysfs/core `iommu_device`, resume register snapshots, performance counter limits, debugfs offsets, and IOPF queue.

Other key types include `struct gcr3_tbl_info`, `struct pdom_dev_data`, `struct pdom_iommu_info`, `struct amd_iommu_viommu`, `struct nested_domain`, `struct iommu_dev_data`, `struct dev_table_entry`, `struct iommu_cmd`, `struct ivhd_dte_flags`, `struct unity_map_entry`, `struct irq_remap_table`, 32-bit and 128-bit IRTE unions, `struct amd_ir_data`, and `struct amd_irte_ops`.

## State And Persistence

The persistent external contract is AMD IOMMU hardware and ACPI IVRS layout. Runtime state is stored in global lists and per-IOMMU/per-segment structures initialized once at boot and reused during suspend/resume and kdump paths. Some state mirrors firmware data, such as IVHD DTE flags, unity maps, IOAPIC/HPET/ACPI HID maps, and pre-enabled translation state.

## Dependencies, Risks, And Test Signals

The header depends on kernel bitfield helpers, IOMMU APIs, MMU notifiers, MSI/PCI/list/spinlock infrastructure, IOMMUFD uapi, generic page-table code, and IRQ remapping. Risks are high because bit positions and packed table formats directly program hardware; wrong masks can corrupt device table entries, command buffers, interrupt remapping, or log processing. Structure changes affect debugfs and runtime code. Test signals include AMD hardware boot, IVRS parsing, DMA remapping, PASID/PPR/IOPF, interrupt remapping in xAPIC/x2APIC/vAPIC modes, SNP/SEV-TIO feature gating, kdump reuse, suspend/resume, and debugfs dumps of DTE/IRTE state.

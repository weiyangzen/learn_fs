# sources/distributed-fs/ceph-client/drivers/iommu/amd/init.c

## Purpose

This file performs AMD IOMMU discovery, ACPI IVRS parsing, hardware setup, PCI integration, interrupt/log setup, command-line parsing, suspend/resume handling, SNP integration, and performance-counter access. It is the boot-time state machine for AMD-Vi and also exposes several runtime helpers used by IRQ remapping, PPR/PASID, performance counters, and SNP teardown.

## Important APIs, Types, And Globals

Local packed ACPI overlays `struct ivhd_header`, `struct ivhd_entry`, and `struct ivmd_header` parse IVRS hardware and memory-definition blocks. Global exported state includes `amd_iommu_evtlog_size`, `amd_iommu_pprlog_size`, `amd_iommu_dump`, `amd_iommu_irq_remap`, `amd_iommu_pgtable`, `amd_iommu_hpt_level`, `amd_iommu_gpt_level`, `amd_iommu_guest_ir`, `amd_iommu_efr`, `amd_iommu_efr2`, `amd_iommu_hatdis`, `amd_iommu_snp_en`, `amd_iommu_np_cache`, `amd_iommu_iotlb_sup`, `amdr_ivrs_remap_support`, `amd_iommu_force_isolation`, and `amd_iommu_pgsize_bitmap`. Global lists hold PCI segments, IOMMUs, and persistent IVHD DTE flags.

External entry points include `amd_iommu_detect()`, IRQ-remapping hooks `amd_iommu_prepare()`, `amd_iommu_enable()`, `amd_iommu_disable()`, `amd_iommu_reenable()`, `amd_iommu_enable_faulting()`, feature helpers `amd_iommu_pasid_supported()`, `get_amd_iommu()`, performance-counter accessors, and SNP exports `amd_iommu_snp_disable()` and `amd_iommu_sev_tio_supported()` when SEV support is enabled.

## Control Flow

Initialization is driven by `enum iommu_init_state` and `iommu_go_to_state()`. `amd_iommu_detect()` runs from x86 IOMMU detection, checks global disable conditions and SME compatibility, moves to `IOMMU_IVRS_DETECTED`, marks `iommu_detected`, and installs `amd_iommu_init()` as the x86 IOMMU initializer. `amd_iommu_init()` advances to `IOMMU_INITIALIZED` and sets up debugfs on success.

`state_next()` implements the boot sequence: detect IVRS, parse ACPI through `early_amd_iommu_init()`, early-enable hardware, register syscore and SNP support, allocate/remap event buffers, initialize PCI/core IOMMU devices through `amd_iommu_init_pci()`, enable interrupts through `amd_iommu_enable_interrupts()`, then mark initialized. Error handling frees DMA resources and either tears hardware down or leaves interrupt-remapping state flushed when IRQ remapping has already been enabled.

ACPI parsing happens in multiple passes. `get_highest_supported_ivhd_type()` chooses the most capable IVHD type. `find_last_devid_acpi()` and `find_last_devid_from_ivhd()` size per-segment tables. `init_iommu_all()` allocates `struct amd_iommu`, calls `init_iommu_one()`, computes global EFR masks, then runs `init_iommu_one_late()` to allocate command buffers and IRQ domains. `init_iommu_from_acpi()` parses device entries, aliases, special IOAPIC/HPET devices, ACPI HID mappings, persistent DTE flags, and reverse lookup entries. `init_memory_definitions()` records IVMD unity/exclusion mappings.

Hardware programming is split across helper phases. Early enable disables stale state, applies ACPI control flags, programs device table and command buffer, exclusion/CWWB range, GT/GA/XT/IRT cache controls, 2K interrupt remapping, enables the IOMMU, and flushes caches. PCI init obtains the PCI device, reads capability/EFR data, enables GT/PPR/IOPF, handles NP cache strict mode, stores RD890 resume state, applies errata, adds sysfs, registers `iommu_device`, initializes identity domain and DTE DMA blocking, then flushes caches. Interrupt setup chooses INTCAPXT x2APIC-style domains or MSI, requests threaded IRQs, and enables event/PPR/GA logging.

## State And Persistence

Most state is boot-persistent kernel memory: IOMMU list, PCI segment tables, DTEs, alias/rlookup/IRQ lookup tables, unity maps, event/command/PPR/GA buffers, sysfs/debugfs registration, command completion semaphores, and per-IOMMU feature flags. Kdump paths can remap and reuse prior kernel command/event/CWB buffers and device tables when translation was already enabled. Firmware-derived state from IVRS is persistent across initialization and restored into DTEs on later operations. Suspend disables IOMMUs before firmware interaction; resume reapplies RD890 quirks, reloads hardware, reenables event buffers and interrupts.

## Dependencies And Integration Points

The file integrates with ACPI IVRS, x86 IOMMU detection, PCI/MSI, x86 IRQ remapping, IOAPIC/HPET mappings, generic IOMMU core/sysfs, AMD runtime `iommu_ops`, PPR/PASID/IOPF code, generic page-table infrastructure, SME/SNP memory encryption APIs, KVM SEV/SNP RMP handling, GART fallback, debugfs setup, and kernel command-line `__setup()` hooks. Hardware integration is direct MMIO and PCI config programming.

## Risks

Risk is high because this file programs DMA isolation hardware early in boot. Incorrect IVRS parsing can size tables wrongly or route devices to the wrong IOMMU. DTE flag handling must preserve firmware-required pass-through/system-management bits. Kdump reuse paths must validate old tables and SME encryption bits or DMA faults and command timeouts can follow. SNP requires V1 page-table mode, enabled IOMMU, RMP initialization, and shared-buffer handling; partial failures can leave security-sensitive state. Interrupt setup must choose compatible MSI/INTCAPXT/GA/vAPIC modes. Error unwinds are complex and differ depending on IRQ-remapping state. Command-line overrides can mask firmware bugs but also mis-map IOAPIC/HPET/ACPI HID devices.

## Test Signals

Essential signals include x86 AMD boot with IVRS present, `amd_iommu=off`, `force_enable`, `pgtbl_v1`, `pgtbl_v2`, `irtcachedis`, page-size options, and IVRS IOAPIC/HPET/ACPI HID overrides; DMA remapping in strict/lazy/passthrough modes; IRQ remapping in xAPIC, x2APIC XT, GA legacy, and vAPIC modes; PPR/PASID/IOPF device attach; IOMMUFD nested builds; SNP host boot and `amd_iommu_snp_disable()`; kdump with pre-enabled translation; suspend/resume on RD890 and modern systems; debugfs/sysfs presence; event/PPR/GA log overflow restart; and performance-counter get/set bounds checking.

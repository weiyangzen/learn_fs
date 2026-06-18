# Research Report: subset-b-005015

This grouped report covers PCI core quirk handling, Resizable BAR helpers, PCI device/bus removal, and PCI ROM mapping in the Ceph-client kernel source mirror. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/quirks.c -->
# sources/distributed-fs/ceph-client/drivers/pci/quirks.c

Purpose: Implements the generic PCI quirk registry and a large set of device, chipset, bridge, reset, DMA alias, interrupt, power-management, ACS, ATS, ASPM, DPC, and firmware workaround hooks. The file is the central non-architecture-specific location for PCI hardware errata that must be applied during enumeration, enable, suspend, resume, final device setup, or special helper queries.

Important APIs and functions: `pci_fixup_device()` is exported and dispatches `struct pci_fixup` entries for the selected `enum pci_fixup_pass`. `pci_apply_final_quirks()` runs at `fs_initcall_sync` and enables the final pass after PCI devices have been discovered while also deriving `pci_cache_line_size`. `pcie_failed_link_retrain()` handles an ASMedia/Pericom downstream-port retraining erratum. Public helper entry points include `pci_dev_specific_reset()`, `pci_dev_specific_acs_enabled()`, `pci_dev_specific_enable_acs()`, `pci_dev_specific_disable_acs_redir()`, and `pci_disable_broken_acs_cap()`. Major internal helper groups include debug timing for fixups, resource declaration helpers such as `quirk_io()` and `quirk_io_region()`, device-specific reset methods, MSI/HT MSI policy helpers, DMA alias helpers, ACS emulation/enabling tables, and device-link helpers for multifunction GPU dependencies.

Control flow: Enumeration code invokes `pci_fixup_device()` with early/header/final/enable/resume/suspend pass ids. The dispatcher selects linker-defined fixup ranges such as `__start_pci_fixups_early` and calls `pci_do_fixups()`, which matches class, vendor, and device, resolves PREL32 hook offsets when needed, logs slow calls under `initcall_debug`, and runs the hook. Most quirk functions then read or write PCI config space, mutate `struct pci_dev` or `struct pci_bus` fields, claim resources, add aliases, or establish device links. The final pass is deferred until `pci_apply_final_quirks()` sets `pci_apply_fixup_final_quirks`, then iterates all devices. Device-specific reset and ACS helpers are called later by reset/IOMMU/ACS paths, not by the normal fixup dispatcher.

State and persistence: The file mutates persistent kernel model state such as `dev->class`, `dev->cfg_size`, `dev->no_msi`, `dev->no_d1d2`, `dev->no_bw_notif`, `dev->d3hot_delay`, `dev->d3cold_delay`, `dev->dev_flags`, `dev->broken_intx_masking`, `dev->clear_retrain_link`, `dev->rom_bar_overlap`, `dev->ats_cap`, `dev->pme_support`, `dev->acs_capabilities`, `dev->dma_alias_mask` via `pci_add_dma_alias()`, subordinate `bus_flags`, and host bridge flags. It also changes hardware state by writing chipset registers, PCI capability registers, MMIO registers, ACPI methods, I/O ports, and PCIe link/ACS controls. Resume and suspend fixups exist because some state is lost across D3, reset, firmware transitions, or bridge mode changes.

Dependencies and integration points: Depends on PCI core internals from `pci.h`, Linux PCI config accessors, resource management, ACPI, DMI, IOMMU, AER, ASPM, PM runtime, switchtec NTB register definitions, NVMe register definitions, x86 IO-APIC support, and optional config blocks such as `CONFIG_PCI_MSI`, `CONFIG_PCI_ATS`, `CONFIG_PCIEASPM`, `CONFIG_PCIE_DPC`, `CONFIG_ACPI`, and `CONFIG_DMAR_TABLE`. It integrates with enumeration, resource sizing, MSI/MSI-X setup, HyperTransport MSI mapping, IOMMU grouping, VFIO/device assignment reset paths, PCIe hotplug, AER/DPC, GPU/audio/USB/UCSI power ordering, and platform firmware workarounds.

Risks: This is high-risk infrastructure because hooks run early and often on partially initialized devices. Incorrect matching can change unrelated hardware behavior; missing resume hooks can make devices fail only after suspend; wrong ACS claims can weaken or misrepresent IOMMU isolation; wrong DMA aliases can break DMA remapping or merge groups unnecessarily; config/MMIO pokes can hang defective devices; and reset quirks affect VFIO and device-assignment safety. Many fixes are constrained by firmware, DMI, revision, subsystem IDs, or build options, so adding a quirk requires hardware evidence and careful pass selection.

Test signals: Build coverage across PCI configs, boot logs containing expected `pci_info()` or `pci_warn()` messages on affected hardware, successful enumeration/resource assignment, suspend/resume on affected systems, MSI and INTx behavior, IOMMU group layout, VFIO reset testing, AER/DPC logs, ASPM capability changes, and device-specific regression reports are the main validation signals. For generic changes, test both devices that match a quirk and nearby devices that must not match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/rebar.c -->
# sources/distributed-fs/ceph-client/drivers/pci/rebar.c

Purpose: Implements PCIe Resizable BAR capability support. It converts between encoded Resizable BAR sizes and byte sizes, discovers the capability location, queries possible/current BAR sizes, writes new BAR sizes, restores BAR size state after save/restore flows, and coordinates safe resource resizing through the PCI resource allocator.

Important APIs and functions: Exports `pci_rebar_bytes_to_size()`, `pci_rebar_size_to_bytes()`, `pci_rebar_get_possible_sizes()`, `pci_rebar_size_supported()`, `pci_rebar_get_max_size()`, and `pci_resize_resource()`. Internal/core-facing helpers include `pci_rebar_init()`, `pci_rebar_find_pos()`, `pci_rebar_get_current_size()`, `pci_rebar_set_size()`, `pci_restore_rebar_state()`, `pci_resize_resource_set_size()`, and `pci_resize_is_memory_decoding_enabled()`.

Control flow: `pci_rebar_init()` caches the extended capability offset in `pdev->rebar_cap`. Queries call `pci_rebar_find_pos()`, which handles both normal BARs and SR-IOV VF BARs, reads `PCI_REBAR_CTRL_NBAR_MASK`, walks each 8-byte capability entry, and matches `PCI_REBAR_CTRL_BAR_IDX`. Size queries read `PCI_REBAR_CAP` or `PCI_REBAR_CTRL`; setters update the encoded `PCI_REBAR_CTRL_BAR_SIZE` field and notify SR-IOV helpers for VF resources. `pci_resize_resource()` rejects host bridges preserving firmware configuration, rejects active memory decoding, verifies support, then delegates the release/reassign operation to `pci_do_resource_release_and_resize()`.

State and persistence: The file mutates PCI config-space Resizable BAR control fields and kernel `struct resource` sizes. `pci_restore_rebar_state()` recomputes encoded sizes from current resource lengths and writes hardware config state during restore. For SR-IOV VF BARs, size changes are scaled by total VFs and mirrored through IOV-specific helpers. No data is stored outside `struct pci_dev`, config space, and resource descriptors.

Dependencies and integration points: Depends on PCI extended capability constants, `FIELD_GET()` and `FIELD_PREP()`, resource helpers, `roundup_pow_of_two()`, log2 helpers, SR-IOV helpers, host bridge policy, and the PCI resource allocator. It integrates with GPU/NVMe/accelerator drivers that request larger BAR apertures, PCI restore paths, and sysfs or driver paths that resize resources before enabling memory decoding.

Risks: Resizing while memory decoding is active is rejected because live MMIO windows could move under a driver. Host bridges with `preserve_config` cannot be resized safely. Encoded sizes are limited to the PCIe spec range from 1MB through 128TB; callers must pass encoded values, not raw bytes. Resource assignment can fail if bridge windows cannot be expanded, and callers may make failure more likely by excluding dependent BARs from release. A device-specific workaround maps an invalid Radeon RX 5600 XT Pulse BAR0 size mask from `0x700` to `0x3f00`.

Test signals: Unit-style checks for byte/encoded conversions, config-space traces for supported size masks and current size, successful resize with memory decoding disabled, resource tree updates after `pci_resize_resource()`, restore after suspend/resume or reset, SR-IOV VF BAR sizing, and failure paths for unsupported sizes, missing capability, active decoding, and preserved firmware resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/rebar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/remove.c -->
# sources/distributed-fs/ceph-client/drivers/pci/remove.c

Purpose: Implements PCI device and bus teardown. It separates stopping devices from destroying them, recurses through subordinate buses, removes sysfs/proc/device-tree representations, releases resources, updates global PCI bus lists, and handles root bus teardown.

Important APIs and functions: Exports `pci_remove_bus()`, `pci_stop_and_remove_bus_device()`, `pci_stop_and_remove_bus_device_locked()`, `pci_stop_root_bus()`, and `pci_remove_root_bus()`. Internal helpers are `pci_free_resources()`, `pci_stop_dev()`, `pci_destroy_dev()`, `pci_stop_bus_device()`, and `pci_remove_bus_device()`.

Control flow: Stop is a driver-facing phase: `pci_stop_dev()` disables PME activity, checks and clears the added flag, releases the bound driver, removes proc/sysfs files, and removes OF nodes. Destruction is a core-model phase: `pci_destroy_dev()` marks the device removed, tears down DOE/NPEM/TSM/IDE/ASPM state, calls `device_del()`, removes the device from `bus_list` under `pci_bus_sem`, updates bridge D3 state, frees claimed resources, and drops the final device reference. Recursive helpers stop children before parents and destroy children before removing subordinate buses. The locked wrapper takes `pci_rescan_remove_lock`; the unlocked exported path asserts that the caller already holds it.

State and persistence: Mutates `pci_dev` added/removed state, `dev->subordinate`, bus and device linked lists, resource parentage, sysfs/proc/device-tree objects, DOE/IDE/ASPM/TSM side state, bridge D3 accounting, host bridge `bus`, and generic device-model registration. Released resources leave the kernel resource tree and device references are dropped with `put_device()` or `device_unregister()`.

Dependencies and integration points: Depends on PCI core locking (`pci_rescan_remove_lock`, `pci_bus_sem`), Linux device core, driver core, OF PCI helpers, proc/sysfs PCI helpers, DOE/IDE/NPEM/TSM teardown, ASPM, bridge D3 policy, host bridge/domain-number handling, and platform `bus->ops->remove_bus`, `pcibios_remove_bus()`, and `pci_remove_legacy_files()`. It is used by hot-remove, rescan/remove sysfs operations, root bus removal, and platform host bridge teardown.

Risks: Ordering is critical. Drivers must be detached before the device disappears from the device model, children must be stopped before parents, and SR-IOV VFs must be handled without corrupting iteration over bus device lists. The code uses reverse iteration for stop because stopping a PF can remove VFs. Missing locks can race with rescan or enumeration; double removal is guarded by added/removed test-and-set bits. Resource leaks or premature `put_device()` would destabilize the PCI device model.

Test signals: PCI hotplug remove, sysfs remove/rescan, SR-IOV PF/VF removal, bridge subtree removal, root bus unregistration, OF node cleanup, DOE/IDE/ASPM teardown coverage, lockdep checks for `pci_rescan_remove_lock`, and clean sysfs/proc/resource state after repeated remove/rescan cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/remove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/rom.c -->
# sources/distributed-fs/ceph-client/drivers/pci/rom.c

Purpose: Provides PCI expansion ROM access helpers. It enables and disables ROM decoding, maps the ROM BAR into kernel virtual address space, determines the real image length inside the resource window, and unmaps/restores decode state.

Important APIs and functions: Exports `pci_enable_rom()`, `pci_disable_rom()`, `pci_map_rom()`, and `pci_unmap_rom()`. The internal `pci_get_rom_size()` parser walks one or more PCI ROM images using the `0xaa55` ROM header signature, the `PCIR` data structure signature, the image length field, and the last-image bit.

Control flow: `pci_enable_rom()` rejects devices without a ROM resource, no-ops for shadow ROM copies, converts the kernel resource to bus coordinates, preserves non-address bits from `pdev->rom_base_reg`, writes the ROM base address plus `PCI_ROM_ADDRESS_ENABLE`, and returns success. `pci_map_rom()` assigns the ROM resource if needed, reads start and length, enables decoding, `ioremap()`s the window, shrinks `*size` to the parsed image length, and unwinds on map or validation failure. `pci_unmap_rom()` unmaps the address and disables decoding unless the resource was already marked enabled by the caller or platform.

State and persistence: Mutates the ROM BAR enable bit and possibly the ROM BAR address in PCI config space. It may trigger resource assignment for `PCI_ROM_RESOURCE`. The returned mapping is temporary kernel virtual state owned by the caller until `pci_unmap_rom()`. Shadow ROM resources are treated as already accessible RAM and do not change hardware decode bits.

Dependencies and integration points: Depends on PCI resource helpers, bus/resource address translation, `pci_assign_resource()`, config-space accessors, `ioremap()`/`iounmap()`, and endian-safe MMIO reads. It is used by PCI drivers and core paths that need firmware ROM contents, option ROMs, or video BIOS data while preserving device decode behavior.

Risks: Enabling ROM decoding can disable access to other MMIO regions on devices with shared decoders, as the file comment warns. Some devices report buggy disabled ROM BAR values, so the helper rewrites the address while enabling. `pci_get_rom_size()` trusts only bounded parsing and clamps to the resource window because ROM length fields can be wrong. Callers must always pair successful maps with `pci_unmap_rom()` and must not assume the resource window length equals image length.

Test signals: ROM read tests on devices with real ROM BARs and shadow ROMs, invalid-signature handling, multi-image ROM parsing, failure unwinding when assignment or mapping fails, preservation of caller-enabled ROM state, and driver flows that copy or inspect option ROM data without losing MMIO access after unmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/rom.c -->

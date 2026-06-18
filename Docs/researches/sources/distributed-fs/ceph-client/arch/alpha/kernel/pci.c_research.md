# sources/distributed-fs/ceph-client/arch/alpha/kernel/pci.c

**Purpose:** Provides common Alpha PCI infrastructure: hose list management, PCI quirks, resource alignment, subsystem PCI initialization, optional SRM config save/restore, bus fixups, latency fixes, console resource claiming, root-bus scanning over multiple PCI controllers, allocation helpers, `pciconfig_iobase` syscall, and exported ISA bridge / `pci_iounmap()`.

**Important APIs/types/functions:** Exposes `pci_io_names`, `pci_mem_names`, `pci_hae0_name`, `hose_head`, `hose_tail`, `pci_isa_hose`, `pcibios_align_resource()`, `pcibios_fixup_bus()`, `pcibios_set_master()`, `pcibios_claim_one_bus()`, `common_init_pci()`, `alloc_pci_controller()`, `alloc_resource()`, `pciconfig_iobase()`, `pci_iounmap()`, and `isa_bridge`. Quirks include `quirk_isa_bridge()`, `quirk_cypress()`, and `pcibios_fixup_final()`.

**Control flow:** Core-logic files allocate and populate `pci_controller` hoses before `pcibios_init()` calls `alpha_mv.init_pci()`. `common_init_pci()` iterates hoses, clips memory-resource ends to avoid direct/SG DMA windows, builds host-bridge windows with offsets, sets machine-vector PCI ops/swizzle/map callbacks, scans each root bus, tracks domain info when bus numbers would overflow, claims firmware/console resources, assigns unassigned resources, and adds devices. Bus fixups optionally read bridge bases in probe-only mode and save SRM state per device. Resource alignment enforces per-hose minima and avoids sparse-memory alias octants. `pciconfig_iobase()` returns hose or sparse/dense base information by hose index or PCI bus/devfn.

**State and persistence behavior:** Maintains global hose list, `pci_isa_hose`, optional SRM saved-config linked list, `isa_bridge`, PCI resources, and host bridge/bus state. It can restore SRM PCI config during reboot when `ALPHA_RESTORE_SRM_SETUP` is enabled. No filesystem persistence.

**Dependencies and integration points:** Central integration point for all Alpha core logic files, machine vectors, Linux PCI core, memblock allocation, IOMMU arena globals, syscall table, and reboot code that may call `pci_restore_srm_config()`.

**Risks:** Multi-hose resource offsets and bus-number domain fallback are subtle. Cypress quirk modifies direct/SG DMA windows to avoid BIOS ROM aliases. `pciconfig_iobase()` assumes domain 0 for device lookup. `alloc_pci_controller()` relies on memblock zeroing/initialization assumptions after allocation; callers must fill all fields before scan.

**Test signals:** Boot representative one-hose and multi-hose Alpha systems, verify PCI enumeration/resource assignment, probe-only SRM behavior, Cypress IDE/bridge quirks, ISA bridge DMA mask, bus mastering latency timer writes, `pciconfig_iobase()` outputs, domain info when bus numbers wrap, and reboot SRM config restore.

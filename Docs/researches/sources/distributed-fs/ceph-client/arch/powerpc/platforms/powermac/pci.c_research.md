# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pci.c

Purpose: discovers and configures PowerMac PCI host bridges, supplies bridge-specific config-space accessors, applies Apple hardware fixups, and provides PowerMac PCI controller callbacks. It covers 32-bit Bandit/Chaos/Grackle/UniNorth and 64-bit U3 AGP, U3 HyperTransport, and U4 PCIe.

Important APIs/types/functions: exported or externally used symbols include `k2_skiplist`, `pmac_pci_irq_fixup`, `pmac_pci_init`, `pmac_pcibios_after_init`, and `pmac_pci_controller_ops`. Important helpers include `fixup_bus_range`, `macrisc_cfg_map_bus`, `chaos_map_bus`, `u3_ht_read_config`, `u3_ht_write_config`, `u4_pcie_cfg_map_bus`, `pmac_add_bridge`, setup functions for each bridge family, and PCI fixups for OHCI, CardBus, PCI ATA, K2 SATA, and U4 PCIe.

Control flow: `pmac_pci_init` sets global PCI flags, walks root OF children for PCI-like host bridges, creates a `pci_controller` through `pmac_add_bridge`, installs appropriate config ops, processes OF ranges, fixes bus-range properties, and performs architecture-specific post-setup. Config access paths encode type 0/type 1 cycles differently for MacRISC, U3 HT, and U4 PCIe. Device enable hooks re-enable GMAC and FireWire cells that early feature code enabled for probing and then powered down. Late fixups disable broken K2 SATA resources and repair U4 PCIe root bridge windows.

State and persistence: runtime state includes `has_uninorth`, `has_second_ohare` on 32-bit, `u3_agp` on 64-bit, global PCI flags, per-hose config address/data mappings, and `k2_skiplist` entries used to fake config reads for powered-down K2 devices. There is no persistent storage; changes are PCI config space, OF-derived resource setup, and powered-device state.

Dependencies/integration: integrates with OF PCI parsing, `pci_controller` allocation, generic PCI config helpers, PowerMac feature calls for GMAC/FireWire, IRQ mapping, DART IOMMU setup through setup code, and machine controller ops used by the generic PCI core.

Risks: many paths depend on firmware device-tree accuracy, but this file also mutates `bus-range` properties and compensates for missing or misleading nodes. U3 HT intentionally hides devices not present in OF to avoid machine checks on K2. U4 PCIe resource repair chooses the largest acceptable host memory window. 32-bit enable hooks alter command/cache-line/latency registers only for selected onboard devices; incorrect node matching can leave devices inaccessible or powered down.

Test signals: enumerate each supported bridge type; verify config reads/writes on root and subordinate buses; test U3 HT hidden/powered-down K2 devices; confirm GMAC/FireWire enable-disable lifecycle; verify second OHare IRQ fixup; CardBus and PCI ATA config rewrites; disabled firmware OHCI resource suppression; U4 PCIe bridge window programming; K2 SATA function/resource disabling.

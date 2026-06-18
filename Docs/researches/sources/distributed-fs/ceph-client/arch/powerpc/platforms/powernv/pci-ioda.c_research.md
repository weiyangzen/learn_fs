## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci-ioda.c

### Purpose
`pci-ioda.c` is the main PowerNV IODA PHB implementation. It initializes PHBs, allocates and configures partitionable endpoints (PEs), maps MMIO segments, sets up DMA/IOMMU windows and bypass, creates MSI domains, handles PE freeze/unfreeze for EEH, integrates hotplug/release, and configures IODA2/NPU OpenCAPI controller operations.

### Important APIs, Types, And Functions
Important APIs include `pnv_ioda_alloc_pe()`, `pnv_ioda_free_pe()`, `pnv_ioda_configure_pe()`, `pnv_ioda_deconfigure_pe()`, `pnv_pci_bdfn_to_pe()`, `pnv_ioda_get_pe()`, `pnv_pci_ioda2_setup_dma_pe()`, `pnv_pci_ioda2_release_pe_dma()`, `pnv_opal_pci_msi_eoi()`, `is_pnv_opal_msi()`, `pnv_pci_init_ioda2_phb()`, and `pnv_pci_init_npu2_opencapi_phb()`. Core internal paths cover M64 parsing, PE setup for devices/buses, PELTV setup, TCE invalidation, IOMMU table group ops, MSI allocation/composition, resource alignment/fixups, and PHB shutdown.

### Control Flow
PHB initialization reads OPAL PHB IDs, allocates `pci_controller`/`pnv_phb`, parses bus/MMIO resources, maps registers, derives PE counts and reserved/root PEs, parses M64 windows, allocates PE/segment arrays, installs PCI/controller hooks, initializes MSI domains, resets IODA tables, optionally resets PHBs for kdump/forced reset, configures M64, and creates dynamic PCI nodes. During device setup, buses or devices are associated with PEs, OPAL `opal_pci_set_pe()` maps RIDs, PELTV tables connect child/parent error domains, MMIO segments are mapped to PEs, and non-bridge devices trigger DMA setup. DMA setup creates a default 32-bit TCE table, maps it through OPAL, optionally enables 64-bit bypass, registers IOMMU groups, and supports VFIO ownership transfer. MSI setup allocates hwirqs from a bitmap, maps them through a parent IRQ domain, asks OPAL for MSI address/data, and performs PHB3 EOI through OPAL.

### State, Persistence, And Dependencies
`struct pnv_phb` persists PHB model/type, OPAL ID, register mapping, diagnostic buffer, MSI bitmap, PE arrays, segment maps, reverse RID map, and controller callbacks. `struct pnv_ioda_pe` persists PE ownership, device/bus/VF association, table group, bypass base/state, MVE number, DMA setup state, and compound PE links. Firmware persists IODA tables, MMIO BAR windows, TVE/TCE mappings, freeze state, and XIVE/PE assignments. Dependencies include OPAL PCI calls, generic PCI core hooks, EEH, IOMMU/VFIO APIs, MSI domains, OF resources, debugfs, memblock memory size, and TCE helpers from `pci-ioda-tce.c`.

### Integration Points
`pci.c` discovers IODA-compatible PHB nodes and calls the init entry points. `pci-sriov.c` shares PE allocation and M64 state for VF setup. `pci.h` defines the shared structures. KVM uses `pnv_opal_pci_msi_eoi()` for passthrough interrupts. EEH paths call freeze/unfreeze/get-state callbacks, and generic PCI DMA hooks call the controller ops installed here.

### Risks
This file has high coupling between Linux resource assignment, OPAL IODA state, and hardware PE segmentation. PE allocation/release must keep bitmaps, lists, reverse maps, device counts, DMA windows, and PELTV entries balanced across hotplug and EEH recovery. M64 alignment and segment ownership are easy to break. TCE invalidation differs between PHB3 MMIO register and OPAL kill calls. VFIO ownership transfer must disable bypass and remove default windows without leaving stale device table bases. Several failure comments note unresolved "what do we do here" cases after PE configuration failures.

### Test Signals
Test PHB DT parsing for IODA2/IODA3/NPU, kdump and forced PHB reset, root/reserved PE allocation, bus/device PE setup, compound PE M64 selection, PELTV parent/slave behavior, MMIO segment mapping, DMA table creation failure, bypass enable/disable and 64-bit workaround, TCE invalidation paths, MSI allocation/free/compose/EOI, hotplug release and re-add, EEH frozen-state recovery, debugfs diag/PE dumps, VFIO ownership transfer, and shutdown IODA reset.

# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/iommu.c

## Purpose
Implements pSeries PCI DMA/IOMMU setup for bare-metal and LPAR guests. It provides TCE table allocation, TCE set/clear/get operations, default DMA-window discovery, dynamic DMA window (DDW) creation/removal, SPAPR TCE IOMMU API hooks for VFIO/KVM, memory-hotplug TCE maintenance, and OF reconfiguration cleanup.

## Important APIs, Types, And Functions
Core table helpers are `iommu_pseries_alloc_table`, `iommu_pseries_alloc_group`, `iommu_pseries_free_group`, and `iommu_table_setparms_common`. Non-LPAR TCE ops are `tce_build_pSeries`, `tce_clear_pSeries`, and `tce_get_pseries`; LPAR hcall-backed ops are `tce_build_pSeriesLP`, `tce_buildmulti_pSeriesLP`, `tce_free_pSeriesLP`, `tce_freemulti_pSeriesLP`, and `tce_get_pSeriesLP`. DDW state is represented by `struct dynamic_dma_window_prop`, `struct dma_win`, `struct ddw_query_response`, and `struct ddw_create_response`. Major DDW paths are `query_ddw`, `create_ddw`, `enable_ddw`, `remove_dma_window_named`, `spapr_tce_create_table`, `spapr_tce_unset_window`, `spapr_tce_take_ownership`, and `spapr_tce_release_ownership`.

## Control Flow
`iommu_init_early_pSeries` installs pSeries PCI DMA setup callbacks and registers memory and OF reconfig notifiers. Non-LPAR boot divides PHB DMA space among slots and uses firmware-provided `linux,tce-base`/`linux,tce-size`. LPAR boot walks up device-tree nodes with `pci_dma_find`, creates a table group around an `ibm,dma-window` or 64-bit window property, initializes the table, registers the IOMMU group, and attaches devices. When a device has a DMA mask above 32 bits, `iommu_bypass_supported_pSeriesLP` attempts `enable_ddw`: query firmware, optionally remove/reset default windows or enable limited-address mode, choose an IO page size and window size, create a DDW, add an OF property, premap RAM for direct mapping, and optionally install a dynamic TCE table.

## State And Persistence
Persistent runtime state includes per-PCI-node `table_group`, TCE tables, device `dma_offset`/`bus_dma_limit`, `dma_win_list` entries for created windows, `failed_ddw_pdn_list` entries that suppress unsafe retries, and dynamic OF properties such as `linux,direct64-ddr-window-info`, `ibm,dma-window`, and `ibm,dma-window-saved`. Per-CPU `tce_page` buffers cache indirect TCE pages. Firmware owns the actual LIOBN windows and TCE mappings.

## Dependencies And Integration Points
Depends on PAPR RTAS DDW calls, PAPR hcalls for TCE put/get/stuff/indirect operations, PCI OF nodes and `pci_dn`, EEH-derived BUID/config addressing, generic DMA-IOMMU ops, Linux IOMMU group/table APIs, VFIO SPAPR TCE ownership paths, memory hotplug notifiers, and OF reconfig notifiers. It is a key integration point between pSeries PCI enumeration and DMA mapping.

## Risks And Edge Cases
High-risk areas are replacing an in-use default window, partial DDW creation cleanup, stale OF properties during kexec/kdump, direct-map TCE updates during memory hotplug, limited-address mode reset behavior, and VFIO ownership ordering. Some failure paths add a parent node to the failed-DDW list to avoid reattempting operations that could race with in-flight DMA and trigger EEH. A few allocation helper failure paths must free both property names and values. Direct mappings must not premap persistent memory outside the hotplug maximum.

## Test Signals
Useful signals include pSeries LPAR boots with and without DDW, PCI devices with 32-bit, limited, and 64-bit DMA masks, kdump boots preserving/removing DDWs, memory online/offline with direct DDWs, VFIO SPAPR TCE table create/unset/take/release flows, DLPAR PCI node detach, `disable_ddw` and `multitce=off` boot parameters, and DMA stress under devices sharing a PE.

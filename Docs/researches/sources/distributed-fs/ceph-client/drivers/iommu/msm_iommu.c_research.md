# sources/distributed-fs/ceph-client/drivers/iommu/msm_iommu.c

## Purpose
`msm_iommu.c` is the Qualcomm/APQ8064-era MSM IOMMU driver. It registers an IOMMU provider, discovers context-bank masters from device tree, allocates ARM v7s page tables, programs MSM context banks and machine-ID routing, handles TLB invalidation, and logs context faults.

## Important APIs, Types, and Functions
The main private domain state is `struct msm_priv`, containing attached IOMMU list, `iommu_domain`, `io_pgtable_cfg`, `io_pgtable_ops`, owning device, and page-table spinlock. Hardware state is `struct msm_iommu_dev` from `msm_iommu.h`, with MMIO base, clocks, IRQ, context-bank bitmap, context list, and `iommu_device`. Masters are `struct msm_iommu_ctx_dev`, holding OF node, context-bank number, and MIDs.

Core functions include `msm_iommu_probe()`, `qcom_iommu_of_xlate()`, `insert_iommu_master()`, `msm_iommu_probe_device()`, `msm_iommu_attach_dev()`, `msm_iommu_identity_attach()`, `msm_iommu_domain_config()`, `msm_iommu_map()`, `msm_iommu_unmap()`, `msm_iommu_sync_map()`, `msm_iommu_iova_to_phys()`, `msm_iommu_fault_handler()`, `msm_iommu_reset()`, `config_mids()`, and `__program_context()`.

## Control Flow and State
Probe prepares clocks, maps MMIO, reads `qcom,ncb`, resets global and context registers, performs a PAR sanity check through context 0, requests the shared fault IRQ, adds the device to the global `qcom_iommu_devices` list, and registers the IOMMU. OF xlate finds the IOMMU provider by phandle and accumulates stream/MID IDs into the first master object for the consumer.

Attach initializes page-table ops for `ARM_V7S`, finds matching IOMMU devices, enables clocks, allocates context-bank numbers, configures MID-to-context routing, programs context registers with TTBR/TCR/PRRR/NMRR and fault controls, then records the IOMMU in the domain attachment list. Map/unmap call io-pgtable under `pgtlock`. TLB flushes iterate attached IOMMUs and their masters, enable clocks, issue context or range invalidations, and disable clocks. Identity attach frees page-table ops and resets contexts.

Runtime state is held in the global device list, context bitmaps, per-domain attachment lists, io-pgtable memory, master MID arrays, clocks, and hardware registers. There is no persistent storage.

## Dependencies and Integration Points
The driver depends on the MSM register macro header, ARM v7s io-pgtable, platform device resources, clocks, device tree `of_xlate`, generic device groups, fault IRQs, and the IOMMU core. It exports `msm_iommu_fault_handler()` through the header for context interrupt hookup.

## Risks and Test Signals
Risks include global lock coverage over clocked hardware operations, limited cleanup in attach failure paths after partial context allocation, duplicate domain configuration on repeated attach, assumptions that a device maps to the first context-list entry, and fault handler returning `0` rather than `IRQ_HANDLED`. Test signals include multi-MID OF entries, duplicate stream IDs, attach/detach cycles, map/unmap with range invalidation, PAR-based `iova_to_phys()`, shared IRQ fault logging, clock enable failures, and `qcom,ncb` boundary cases.

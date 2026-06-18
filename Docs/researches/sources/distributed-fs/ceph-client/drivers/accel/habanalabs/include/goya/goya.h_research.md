## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya.h

Purpose: small Goya hardware identity and memory-layout header. It defines BAR IDs/sizes, CFG/SRAM/DRAM/host physical regions, interrupt count, queue entry size, ASID count, protection-bit offset, and engine counts for DMA, TPC, and MME.

Important API surface: `SRAM_CFG_BAR_ID`, `MSIX_BAR_ID`, `DDR_BAR_ID`; `CFG_BAR_SIZE`, `MSIX_BAR_SIZE`, `CFG_BASE`, `CFG_SIZE`; `SRAM_BASE_ADDR`, `SRAM_SIZE`; `DRAM_PHYS_BASE`; `HOST_PHYS_BASE`, `HOST_PHYS_SIZE`; `GOYA_MSIX_ENTRIES`; `QMAN_PQ_ENTRY_SIZE`; `MAX_ASID`; `PROT_BITS_OFFS`; `DMA_MAX_NUM`, `TPC_MAX_NUM`, `MME_MAX_NUM`.

Control flow and state: no runtime flow. These constants drive compile-time checks and runtime address calculations. They are not persisted, but changing them changes driver memory mapping, queue layout, security masks, and loop bounds.

Dependencies and integration: included by `goyaP.h`; `GOYA_MSIX_ENTRIES` guards interrupt count, `QMAN_PQ_ENTRY_SIZE` sizes SRAM QMAN slots, `TPC_MAX_NUM`/`DMA_MAX_NUM` bound loops, and `PROT_BITS_OFFS` is used by security code.

Risks and test signals: incorrect constants can map the wrong BAR, exceed SRAM reservations, undercount engines, or misconfigure protection bits. Test with build-time assertions, PCI BAR probing, SRAM reservation checks, DMA/TPC loop coverage, MSIX allocation, and security programming.

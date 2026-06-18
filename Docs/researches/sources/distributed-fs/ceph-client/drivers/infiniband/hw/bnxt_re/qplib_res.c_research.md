# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_res.c

## Purpose
`qplib_res.c` is the qplib resource manager. It allocates/free page-buffer-list backed hardware queues, firmware context tables, TQM rings, SGID/PD/DPI tables, stats DMA blocks, and doorbell BAR mappings used by the rest of the bnxt_re driver.

## Important APIs, types, and functions
Core allocation APIs are `bnxt_qplib_alloc_init_hwq()`, `bnxt_qplib_free_hwq()`, `bnxt_qplib_alloc_hwctx()`, `bnxt_qplib_free_hwctx()`, `bnxt_qplib_alloc_pd()`, `bnxt_qplib_dealloc_pd()`, `bnxt_qplib_alloc_dpi()`, `bnxt_qplib_dealloc_dpi()`, `bnxt_qplib_alloc_uc_dpi()`, `bnxt_qplib_free_uc_dpi()`, `bnxt_qplib_alloc_stats_ctx()`, `bnxt_qplib_free_stats_ctx()`, `bnxt_qplib_alloc_res()`, `bnxt_qplib_free_res()`, `bnxt_qplib_init_res()`, `bnxt_qplib_cleanup_res()`, `bnxt_qplib_map_db_bar()`, `bnxt_qplib_unmap_db_bar()`, and `bnxt_qplib_determine_atomics()`. Internal helpers allocate/free PBL levels, map TQM page tables, and initialize/cleanup SGID, PD, and DPI bitmaps.

## Control flow
`bnxt_qplib_alloc_init_hwq()` rounds depth/stride, determines kernel versus user memory, allocates direct or one/two-level PBL/PDE structures, fills valid/last/next-to-last PTE flags, initializes producer/consumer indices, and exposes direct page pointers for queue access. Context allocation builds QPC, MRW, SRQ, CQ, TQM, and TIM memory before RCFW firmware init consumes their addresses. Resource allocation creates the QP table, SGID table, PD bitmap, and DPI bitmap. DPI allocation reserves a page, maps UC/WC doorbell space for user or kernel use, and records the application owner. Cleanup unwinds these resources and clears SGID firmware state.

## State and persistence
State is mostly RAM and DMA memory owned by `bnxt_qplib_res`, `bnxt_qplib_hwq`, `bnxt_qplib_ctx`, SGID/PD/DPI tables, and stats contexts. Hardware-visible persistence consists of DMA page tables, context tables, stats DMA addresses, and BAR mappings while the device is active. PD and DPI allocation state is a bitmap protected by mutexes. SGID table entries mirror firmware SGID registrations and are reset on cleanup.

## Dependencies and integration points
The resource manager uses PCI DMA APIs, vmalloc, RDMA umem iteration, netdevice SGID context, qplib slow-path SGID delete helpers, RCFW constants, and PCIe atomic capability APIs. It feeds `main.c` setup, `qplib_rcfw.c` CMDQ/CREQ allocation, `qplib_fp.c` queue allocation, and `ib_verbs.c` PD/DPI/user queue flows.

## Risks
PBL allocation is complex and easy to regress around edge page counts, `nopte`, user umem, and PTE flag placement. `bnxt_qplib_alloc_pd_tbl()` and DPI bitmap sizing use `max >> 3`, which underallocates if `max` is not divisible by 8. `bnxt_qplib_dealloc_dpi()` skips `pci_iounmap()` when `dpi->dpi` is zero, which is also a valid first DPI for non-kernel allocations. `bnxt_qplib_alloc_dpi()` does not check `ioremap()` failure before returning success for WC/UC user mappings. Doorbell BAR mapping validates only UC length. Cleanup depends on `res->rcfw` being non-null when freeing QP tables.

## Test signals
Test HWQ allocation at page-count boundaries for level 0/1/2, user umem versus kernel pages, `nopte`, queue PTE last flags, context allocation failure unwind, SGID cleanup, PD/DPI bitmap exhaustion, DPI zero allocation, ioremap failure injection, DB BAR length validation, stats DMA allocation, atomic capability detection, and repeated alloc/free under KASAN and lockdep.

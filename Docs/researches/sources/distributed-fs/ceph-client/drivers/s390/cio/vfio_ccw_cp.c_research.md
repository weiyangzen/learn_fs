## sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_cp.c

Purpose: implements vfio-ccw channel-program translation. It copies guest CCW chains from VFIO DMA/IOMMU-visible guest memory, follows TIC branches, converts format-0 CCWs to format-1, pins guest data pages, builds host IDALs, and later maps host completion addresses back to guest addresses.

Important APIs/types/functions: internal `struct page_array` tracks guest IOVAs and pinned pages; `struct ccwchain` stores translated CCW arrays and per-CCW page arrays. Exported operations are `cp_init()`, `cp_free()`, `cp_prefetch()`, `cp_get_orb()`, `cp_update_scsw()`, and `cp_iova_pinned()`. Key helpers include `ccwchain_calc_length()`, `ccwchain_handle_ccw()`, `ccwchain_loop_tic()`, `ccwchain_fetch_ccw()`, `get_guest_idal()`, and `page_array_pin()/unpin()`.

Control flow: `cp_init()` initializes the list, saves the ORB, copies the first guest chain via `vfio_dma_rw()`, calculates bounded chain length, and recursively follows TICs that target unseen chain segments. `cp_prefetch()` walks every chain and translates each CCW: TICs are retargeted to host CCW storage, non-TIC data addresses become host IDALs, and data-transfer CCWs pin guest pages through VFIO. `cp_get_orb()` rewrites the ORB to point at the first host CCW and forces format-2 IDAL semantics. Interrupt completion later calls `cp_update_scsw()` to convert the SCSW CPA back into the corresponding guest CPA.

State and persistence: state is in `struct channel_program` for one active I/O. It owns the chain list, saved ORB, initialized flag, and reusable `guest_cp` scratch buffer allocated by the mdev code. Pinned pages and allocated IDAL buffers persist only until `cp_free()`.

Dependencies and integration: depends on VFIO pin/unpin and `vfio_dma_rw()`, s390 channel I/O structures, IDAL helpers, and `vfio_ccw_private` container lookup. It feeds `vfio_ccw_fsm.c` start-subchannel flow and supports `vfio_ccw_ops.c` invalidation via `cp_iova_pinned()`.

Risks and test signals: high-risk areas are chain-loop handling, 2K versus 4K IDAW math, partial pin cleanup, unaligned IDAL coalescing, and DMA32 host address assumptions. Test by issuing direct and IDAL CCWs, TIC fan-out/back-edge programs, skipped reads, zero-count commands, invalid guest addresses, DMA unmap during pending I/O, and final SCSW CPA translation.

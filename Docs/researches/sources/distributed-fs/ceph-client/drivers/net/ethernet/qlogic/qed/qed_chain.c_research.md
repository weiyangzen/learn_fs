# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_chain.c

## Purpose
This file implements allocation, initialization, and freeing of QED DMA-backed chains. Chains are ring-like queues used by QED slowpath, LL2, storage, RDMA, and other subsystems. The implementation supports single-page, next-pointer, and page-block-list (PBL) layouts.

## Important APIs and Functions
- `qed_chain_alloc()` fills default page size, computes page count, sanity-checks capacity, initializes the chain, allocates backing memory for the selected mode, resets cursors, and frees partial allocations on failure.
- `qed_chain_free()` dispatches to mode-specific free helpers and clears base virtual/physical addresses.
- `qed_chain_init()` initializes geometry, capacity, masks, and optional external PBL metadata.
- `qed_chain_alloc_next_ptr()` allocates pages and links embedded `struct qed_chain_next` entries in a ring.
- `qed_chain_alloc_single()` allocates one coherent page.
- `qed_chain_alloc_pbl()` allocates an address table, optional internal coherent PBL table, data pages, and PBL physical-address entries.
- `qed_chain_alloc_sanity_check()` rejects zero-size chains, invalid count types, and chains exceeding selected counter width.

## Control Flow
Allocation defaults `params->page_size` when unset. Single mode uses one page; other modes compute page count from requested elements, element size, page size, and mode-specific unusable elements. After sanity checks, initialization establishes geometry and the mode switch allocates memory. On failure, the top-level allocator calls `qed_chain_free()`.

Freeing reverses the selected layout. Next-pointer mode walks embedded next pointers and frees pages. Single mode frees one coherent page. PBL mode walks `pp_addr_tbl`, frees each data page, frees the internal PBL table unless external, vfree()s the address table, and nulls it.

## State and Persistence
State persists in `struct qed_chain`: geometry fields, capacity/size, base virtual and DMA address, PBL table virtual/physical/size, external-PBL flag, and per-page virtual/DMA address table. Hardware persistence is indirect: coherent DMA pages and PBL tables are intended to be consumed by firmware/hardware rings.

## Dependencies and Integration Points
The file includes `linux/qed/qed_chain.h`, DMA mapping, vmalloc, and `qed_dev_api.h`. Callers include SPQ/EQ/ConSQ, LL2, iSCSI, NVMe/TCP, and other QED modules that need DMA queue storage.

## Risks and Edge Cases
- PBL helper early returns after partial allocations must be checked for leaks through the top-level cleanup path.
- Geometry depends on element size, page size, and unusable next-pointer elements.
- External PBL mode trusts caller-provided table addresses and capacity.
- Next-pointer free relies on valid embedded next pointers.
- Rounded actual chain size can exceed selected count type limits.

## Test Signals
Tests should allocate and free all modes with small, exact-page, multi-page, and near-limit counts; inject DMA allocation failures; exercise external/internal PBL modes; run with DMA API debug, KASAN, and kmemleak; and cover real callers such as SPQ/EQ/LL2/storage queues through probe/open/teardown.

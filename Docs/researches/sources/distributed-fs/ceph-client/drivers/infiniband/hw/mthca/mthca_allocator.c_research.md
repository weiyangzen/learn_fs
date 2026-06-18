# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_allocator.c

## Purpose
`mthca_allocator.c` provides shared allocation primitives for the mthca driver: bitmap-backed numeric resource IDs, lazily allocated pointer arrays, and DMA queue buffers registered as driver memory regions.

## Important APIs, types, and functions
`mthca_alloc_init()`, `mthca_alloc()`, `mthca_free()`, and `mthca_alloc_cleanup()` manage power-of-two ID spaces with reserved low entries and wrapped top bits. `mthca_array_init/get/set/clear/cleanup()` stores pointers in on-demand pages for CQ/QP/SRQ lookup tables. `mthca_buf_alloc()` and `mthca_buf_free()` allocate direct or page-list DMA buffers, build a DMA address list, and register it through `mthca_mr_alloc_phys()`.

## Control flow
ID allocation scans from `last`, wraps at `max`, advances `top` to avoid stale handles, and marks bits under a spinlock. Pointer arrays allocate pages with `GFP_ATOMIC` because callers hold locks. Buffer allocation chooses one coherent allocation for small queues or page-by-page coherent allocations for larger queues, then registers the physical list as an HCA MR; failure unwinds through `mthca_buf_free()`.

## State and persistence
Persistent driver state includes allocation bitmaps, generation-like high bits in allocated IDs, lazy array pages and their used counts, coherent DMA buffers, DMA mappings, and MRs visible to the HCA while queues are active.

## Dependencies and integration points
The file depends on Linux bitmap/slab/DMA APIs, `mthca_dev.h`, memory-region allocation in `mthca_mr.c`, and driver PDs. CQ, QP, SRQ, UAR, PD, AV, and MCG tables use these primitives.

## Risks
`mthca_free()` trusts callers not to double-free; a double clear can corrupt allocation state. `mthca_array_clear()` decrements before validating and only logs negative refcounts. Buffer direct-mode alignment splitting must match DMA address alignment, and error unwinds pass `mr = NULL` before registration completes. Large allocation paths need complete cleanup on partial page allocation.

## Test signals
Test power-of-two validation, reserved ID handling, ID wrap/top masking, exhaustion, double-free detection under debug, lazy array set/clear races under external locking, direct versus page-list buffer allocation, MR registration failure injection, and DMA cleanup under KASAN/dma-debug.

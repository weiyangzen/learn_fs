
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_wq.c

## Purpose
`hinic3_wq.c` implements hinic3 generic work queue creation/destruction/reset and multi-WQEBB allocation. It maps logical queue entries onto one or more coherent DMA pages and, when needed, creates an indirection table for hardware chip logical addressing.

## Important APIs, Types, And Functions
- `hinic3_wq_create()` validates depth/element size, initializes geometry, allocates pages, and builds the WQ block.
- `hinic3_wq_destroy()` frees WQ pages and optional WQ block indirection table.
- `hinic3_wq_reset()` clears producer/consumer indices and zeroes each queue page.
- `hinic3_wq_get_multi_wqebbs()` reserves multiple WQ elements and returns first/second contiguous pieces when the reservation crosses a page boundary.
- `hinic3_wq_is_0_level_cla()` reports whether a queue fits in one direct-mapped page.
- `wq_init_wq_block()`, `wq_alloc_pages()`, and `wq_free_pages()` are internal allocation helpers.

## Control Flow
Creation checks `q_depth` against `[64, 65536]`, requires power-of-two depth and WQEBB size, aligns the hardware page size to `HINIC3_MIN_PAGE_SIZE`, initializes `qpages`, allocates pages, then either points `wq_block_*` at the first queue page for level-0 CLA or allocates a minimum-page-size DMA page containing big-endian page physical addresses for level-1 CLA. Multi-WQEBB reservation advances `prod_idx`, returns the current index, and splits the descriptor span only if it crosses the current DMA page.

## State And Persistence Behavior
Each `struct hinic3_wq` owns coherent DMA queue pages plus an optional coherent indirection table. Producer/consumer indices are software runtime state; hardware sees pages through context programming in `hinic3_nic_io.c`.

## Dependencies And Integration Points
This file depends on `linux/dma-mapping.h`, `hinic3_hwdev`, `hinic3_queue_common`, and `hinic3_wq.h`. It is used by SQ/RQ allocation in `hinic3_nic_io.c` and descriptor access in TX/RX paths.

## Risks And Edge Cases
- Multi-page WQs are limited by `WQ_MAX_NUM_PAGES`, derived from the minimum page size divided by 64-bit page addresses.
- The WQ block stores page addresses as big-endian 64-bit values, unlike most NIC descriptors that use little-endian fields.
- `hinic3_wq_get_multi_wqebbs()` assumes callers have already checked free space.
- Reset zeroes descriptor memory but does not notify hardware by itself.

## Test Signals
Create/destroy WQs at min/max supported depths, verify level-0 vs level-1 CLA programming, exercise TX descriptors crossing page boundaries, and run queue reset/reopen cycles with no stale descriptors.

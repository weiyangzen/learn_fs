# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/alloc.c

## Purpose
This file provides core mlx4 allocation utilities: bitmap-backed object IDs, priority zone allocation, DMA queue buffers, doorbell pages, and compound hardware queue resources.

## Important APIs and Functions
- `mlx4_bitmap_alloc*()`, `mlx4_bitmap_free*()`, `mlx4_bitmap_init()`, and `mlx4_bitmap_cleanup()` manage reusable numeric resources with reserved ranges, round-robin behavior, alignment, and skip masks.
- `mlx4_zone_allocator_create()`, `mlx4_zone_add_one()`, `mlx4_zone_alloc_entries()`, and related free/remove helpers layer priority and fallback semantics over bitmaps.
- `mlx4_buf_alloc()` and `mlx4_buf_free()` allocate coherent queue memory either as one direct block or page list.
- `mlx4_db_alloc()` and `mlx4_db_free()` allocate doorbell records from coherent pages with order-0/order-1 bitmap splitting.
- `mlx4_alloc_hwq_res()` and `mlx4_free_hwq_res()` combine doorbell, buffer, MTT allocation, and MTT programming for hardware queues.

## Control Flow
Bitmap allocation searches from `last`, wraps by advancing `top`, marks bits, and decrements availability. Zone allocation first tries the requested zone, then optional lower/equal/higher priority fallbacks based on flags. Queue resource allocation is staged with rollback labels: doorbell, direct buffer, MTT init, then MTT write.

## State and Persistence
State is in `struct mlx4_bitmap`, zone allocator lists, doorbell page directories on `priv->pgdir_list`, DMA coherent memory, and MTT entries programmed into device memory translation tables. Locks include bitmap spinlocks, zone allocator spinlock, and `priv->pgdir_mutex`.

## Dependencies and Integration Points
It depends on Linux bitmap, DMA mapping, vmalloc/slab helpers, mlx4 private structures, MTT helpers, PCI device DMA context, and exported symbols used by CQ/QP/SRQ/Ethernet code.

## Risks and Test Signals
Risks include bitmap wrap bugs, zone list priority corruption, freeing ranges with wrong offset/mask, direct DMA allocation alignment assumptions, and doorbell order coalescing mistakes. Test signals include resource exhaustion tests, repeated allocation/free cycles, multi-function resource partitioning, CQ/QP bring-up, and DMA API debug.

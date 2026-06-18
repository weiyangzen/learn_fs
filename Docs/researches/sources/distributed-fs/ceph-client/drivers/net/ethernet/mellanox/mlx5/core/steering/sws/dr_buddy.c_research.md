# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_buddy.c

Purpose: implements a bitmap buddy allocator used by the SWS ICM pool for suballocating chunks inside a larger device-memory region.

Important APIs/functions: `mlx5dr_buddy_init`, `mlx5dr_buddy_cleanup`, `mlx5dr_buddy_alloc_mem`, and `mlx5dr_buddy_free_mem`. Internal `dr_buddy_find_free_seg()` scans free bitmaps from requested order upward.

Control flow: init allocates one bitmap per order, marks the single largest block free, and tracks free counts. Allocation finds the smallest available higher/equal order, clears it, splits down to the requested order by marking sibling blocks free, and returns a segment index in entry units. Free coalesces upward while the sibling bit is free, then marks the merged segment free.

State/persistence: state is in-memory bitmaps and `num_free` arrays within `mlx5dr_icm_buddy_mem`; it models ownership of already-created ICM memory but does not itself create hardware resources.

Dependencies/integration: used by `dr_icm_pool.c`; depends on Linux bitmap helpers and list node membership managed by the pool.

Risks: caller must serialize access; the allocator itself has no lock. Incorrect order/segment pairs on free can corrupt bitmaps. `mlx5dr_buddy_cleanup()` removes `list_node`, so callers must ensure the node is linked or list deletion is valid.

Test signals: allocate/free each order, split and coalesce back to max order, exhaustion behavior, repeated randomized alloc/free under pool lock, and cleanup after partial init failure.

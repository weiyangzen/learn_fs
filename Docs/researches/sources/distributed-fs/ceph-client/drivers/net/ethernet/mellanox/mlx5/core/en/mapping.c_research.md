# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/mapping.c

Purpose: implements a generic data-to-id mapping service used by mlx5e offload paths that need compact hardware tags and reverse lookup on packet completion/receive.

Important APIs/functions: `mapping_create`, `mapping_create_for_id`, `mapping_destroy`, `mapping_add`, `mapping_remove`, and `mapping_find`. Internal state combines an xarray from id to item, a jhash hashtable from data to item, optional delayed-removal work, and a shared-context list keyed by image GUID/type.

Control flow: `mapping_add` hashes the caller data and either bumps an existing item count or allocates a new item and xarray id in `[1, max_id]`. `mapping_remove` decrements the count, removes the item from the data hash when the count reaches zero, and either frees the xarray id immediately or puts it on a delayed pending list. Delayed work frees expired items and reschedules for the nearest remaining timeout. `mapping_find` performs an RCU-protected xarray lookup and copies the stored data to the caller.

State and persistence: all state is in kernel memory. Delayed removal keeps old ids visible for `MAPPING_GRACE_PERIOD` to avoid hardware races where packets carry an id after software has reused it. Shared contexts are refcounted globally under `shared_ctx_lock`.

Dependencies and integration: uses xarray allocation, jhash, RCU freeing, delayed work, and mlx5 software image GUID constants. TC receive code uses mapping contexts to decode register metadata.

Risks: `mapping_destroy` assumes no live users remain; it flushes delayed work and destroys the xarray but does not walk active non-delayed mappings itself. Delayed removal must preserve old data long enough for hardware completion paths but not leak ids indefinitely.

Test signals: duplicate add/remove reference counts, max-id exhaustion, delayed id reuse race tests, shared-context refcounting, and RCU lookup during concurrent remove.

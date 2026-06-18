# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/fs_hws_pools.c

## Purpose
`fs_hws_pools.c` implements flow-steering HWS pools for packet reformat and modify-header action arguments. It wraps the generic `mlx5_fs_pool` bulk allocator so many FTEs can share one HWS action object while each rule gets a unique offset and per-rule data payload.

## Important APIs, types, and functions
Packet reformat pool functions are `mlx5_fs_hws_pr_pool_init()`, `mlx5_fs_hws_pr_pool_cleanup()`, `mlx5_fs_hws_pr_pool_acquire_pr()`, `mlx5_fs_hws_pr_pool_release_pr()`, and `mlx5_fs_hws_pr_get_action()`. Modify-header pool functions are `mlx5_fs_hws_mh_pool_init()`, `mlx5_fs_hws_mh_pool_cleanup()`, `mlx5_fs_hws_mh_pool_acquire_mh()`, `mlx5_fs_hws_mh_pool_release_mh()`, and `mlx5_fs_hws_mh_pool_match()`. Counter integration is provided by `mlx5_fc_get_hws_action()` and `mlx5_fc_put_hws_action()`.

Internal helpers create bulk HWS actions for decap-L3-to-L2, encap-L2-to-L3, encap-L2-to-L2, insert-header VLAN, and modify-header patterns. The default bulk length is 65,536 entries, with thresholds updated as roughly one tenth of used units capped at `BIT(18)`.

## Control flow
Pool initialization validates action type, stores a small pool context, and initializes `mlx5_fs_pool` with bulk create/destroy callbacks. When the generic pool needs capacity, the PR bulk creator allocates a flexible bulk structure, initializes a bitmap, fills per-entry backpointers and offsets, and creates one HWS reformat or insert-header action with `log_bulk_size`. The MH bulk creator performs the same shape for modify-header actions after checking the FDB root namespace is in HMFS mode.

Acquire calls obtain an index from `mlx5_fs_pool` and return the corresponding `prs_data` or `mhs_data` entry. Release reconstructs the pool index from the entry's bulk and offset and warns if the index was not acquired. Bulk destroy refuses to free if not all offsets are returned, then destroys the associated HWS action, cleans the bitmap, and frees memory. Modify-header pool matching compares stored pattern size and action words to reuse an existing pool for identical patterns.

Counter HWS actions are created lazily per counter bulk. `mlx5_fc_get_hws_action()` takes the local counter reference, calls the generic HWS action refcount helper on `fc_bulk->hws_data`, and drops the local reference if action creation fails. The put path releases the HWS action refcount and local counter reference.

## State and persistence behavior
Each pool owns a pool context and one or more bulks. A bulk owns an HWS action object and per-offset metadata. Per-rule data buffers are not stored by this file; callers in `fs_hws.c` duplicate and free them in the acquired entries. Modify-header pools persist a copied action pattern in `pool_ctx` so future allocations can detect reuse. Counter action lifetime is tied to counter bulk HWS data refcounts.

## Dependencies and integration points
This file depends on `fs_pool`, root namespace lookup, HMFS mode, HWS action creation APIs, packet reformat and modify-header PRM data, flow counters, and `mlx5_fs_get_hws_action()`. It is consumed by `fs_hws.c` when allocating packet reformat, modify-header, and counter actions for FTE rules.

## Risks and edge cases
Destroying a bulk with active offsets returns `-EBUSY`, so caller cleanup must release all PR/MH entries first. Pool matching for modify headers compares action words in a compact way; endian or action-size mistakes can accidentally merge incompatible patterns. Bulk action creation depends on FDB root namespace HWS mode, so early or wrong-namespace use returns NULL. Pool contexts must be freed after `mlx5_fs_pool_cleanup()` to avoid dangling callbacks. Very large bulk length implies allocation and bitmap pressure under many distinct patterns or reformat sizes.

## Test signals
Test packet reformat allocation/release for insert VLAN, L2-to-L2 tunnel, L2-to-L3 tunnel, and L3 tunnel decap; modify-header allocation with repeated and distinct patterns; pool cleanup with all entries released; cleanup with active entries; counter action get/put refcounting; HMFS disabled fallback; allocation failure paths; and high-churn pool threshold behavior.

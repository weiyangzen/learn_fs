# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/fs_hws_pools.h

## Purpose
`fs_hws_pools.h` declares the flow-steering HWS packet-reformat and modify-header pool types used by `fs_hws.c` and implemented in `fs_hws_pools.c`. It also defines the VLAN insert-header shape currently accepted by the HWS flow-steering adapter.

## Important APIs, types, and functions
Constants `MLX5_FS_INSERT_HDR_VLAN_ANCHOR`, `MLX5_FS_INSERT_HDR_VLAN_OFFSET`, and `MLX5_FS_INSERT_HDR_VLAN_SIZE` encode supported VLAN header insertion. The L3-tunnel decap header indexes distinguish MAC-only and MAC+VLAN headers.

`struct mlx5_fs_hws_pr`, `mlx5_fs_hws_pr_bulk`, and `mlx5_fs_hws_pr_pool_ctx` describe packet-reformat offsets, associated HWS action bulk, header index, copied data pointer, and reformat type/size. `struct mlx5_fs_hws_mh` and `mlx5_fs_hws_mh_bulk` describe modify-header offsets, copied data, pool pointer, and HWS action. The declared functions initialize, clean up, acquire, release, match, and retrieve actions for these pools, plus get/put HWS counter actions.

## Control flow
This header has no runtime control flow. Callers initialize a pool for a specific reformat type or modify-header pattern, acquire entries while building FTE actions, use the returned offset/data/action in `mlx5hws_rule_action`, and release entries during resource deallocation or rule cleanup.

## State and persistence behavior
The structs carry per-offset metadata owned by pool bulks. `data` points to per-resource copied header or modify-action data and is freed by the caller that allocated the resource. Bulk actions persist for the lifetime of the backing pool and are shared by all offsets in that bulk.

## Dependencies and integration points
The header depends on Linux VLAN definitions, `fs_pool`, `fs_core`, and HWS action types. It integrates directly with packet reformat objects, modify-header objects, flow counters, and FTE action translation in `fs_hws.c`.

## Risks and edge cases
The fixed VLAN insert-header constants mean broader insert-header use is intentionally unsupported by this adapter. Callers must pair each acquire with the matching pool release; the type system does not prevent releasing a PR/MH entry to the wrong pool. The `data` pointer ownership is external, so missing cleanup leaks per-rule buffers.

## Test signals
Build coverage plus runtime packet reformat and modify-header allocation/free tests are the direct signals. Negative tests should cover unsupported insert-header anchors, wrong sizes, release of unacquired entries, and modify-header pattern matching.

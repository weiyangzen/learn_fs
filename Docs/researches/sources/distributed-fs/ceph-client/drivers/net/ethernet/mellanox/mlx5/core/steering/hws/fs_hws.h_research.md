# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/fs_hws.h

## Purpose
`fs_hws.h` declares the flow-steering-to-HWS adapter structures embedded in generic mlx5 flow-steering objects. It is the local contract between `fs_hws.c`, pool helpers, counter bulks, packet reformat resources, modify-header resources, matchers, and FTE rule state.

## Important APIs, types, and functions
`struct mlx5_fs_hws_actions_pool` stores namespace-wide shared actions and xarray caches for packet reformat pools, modify-header pools, table destinations, vport destinations, ASO meters, and sampler destinations. `struct mlx5_fs_hws_context` wraps the HWS context and this pool. Table, matcher, and rule adapter structs hold HWS table, BWC matcher, BWC rule, and per-rule action references.

`struct mlx5_fs_hws_action` is embedded in packet reformat and modify-header resources and stores the HWS action, associated fs pool, acquired packet-reformat or modify-header data, lazy firmware reformat ID, and a mutex protecting that ID. `struct mlx5_fs_hws_data` implements lazy shared action creation with a mutex and refcount. `struct mlx5_fs_hws_create_action_ctx` carries the action type, context, object ID, and optional return register for the generic action factory.

Exported functions are `mlx5_fs_get_hws_action()`, `mlx5_fs_put_hws_action()`, and, when HWS is configured, `mlx5_fs_hws_action_get_pkt_reformat_id()`, `mlx5_fs_hws_is_supported()`, and `mlx5_fs_cmd_get_hws_cmds()`.

## Control flow
The header has no executable flow. Generic flow-steering code uses these embedded structs after selecting HWS command operations. `fs_hws.c` initializes namespace-level pools, fills table/matcher/rule fields during create operations, and unwinds them on destroy/update. Conditional stubs return unsupported behavior when `CONFIG_MLX5_HW_STEERING` is disabled.

## State and persistence behavior
The declared state persists at the same lifetime as the flow-steering objects embedding it: root namespace, flow table, group, FTE, packet reformat, modify header, and counter bulk. `fw_reformat_id` can be initialized lazily and later freed through firmware commands. Refcounted `mlx5_fs_hws_data` objects persist in xarrays until namespace cleanup, while the underlying HWS action exists only while the refcount is nonzero.

## Dependencies and integration points
This header depends on `mlx5hws.h`, `fs_hws_pools.h`, Linux xarrays, mutexes, refcounts, counters, execute-ASO objects, and generic flow-steering types. It is included by flow-steering core headers so generic objects can carry HWS-private state without exposing implementation details.

## Risks and edge cases
Struct fields encode ownership contracts that are not obvious from types alone: `hws_action` can be shared, cached, or rule-owned depending on action kind; `fs_pool` must match the allocated `pr_data` or `mh_data`; and `fw_reformat_id` must be protected by the lock. Conditional compilation stubs must stay consistent with real signatures, or non-HWS builds break.

## Test signals
Build both with and without `CONFIG_MLX5_HW_STEERING`. Runtime validation comes from HWS namespace/table/rule lifecycle, packet reformat firmware-ID lookup, lazy shared action refcounting, and cleanup after failed FTE action construction.

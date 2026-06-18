# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/debug.c

## Purpose
`debug.c` exposes an HWS debugfs dump for FDB steering state. It emits CSV-like records describing the context, attributes, capabilities, send engines, STC resources, tables, matchers, templates, definers, and action STE tables.

## Important APIs, Types, And Functions
Public functions are `mlx5hws_debug_init_dump()` and `mlx5hws_debug_uninit_dump()`. `hws_dump_show()` calls `hws_debug_dump()`, which validates inputs and serializes the dump under `ctx->ctrl_lock`. Dump helpers format matcher definers, match templates, action templates, matcher attributes, matcher table/STE IDs, flow table ICM indexes, send queue state, capabilities, context attributes, STC pools, and action STE pools.

## Control Flow And State
Initialization creates `steering/fdb` under the mlx5 debugfs device root and a per-context file named from the context pointer. Reading the file locks the context and walks the current table list, matcher lists, STC pool resources, send queues, and action STE pool lists. It issues flow table query commands to obtain ICM addresses. Uninitialization removes the steering debugfs subtree recursively.

## Dependencies And Integration Points
The file depends on Linux debugfs and seq_file APIs, HWS context/table/matcher/action/definer structures, command flow table query, action type formatting, and pool base ID helpers. Its output format is versioned by `HWS_DEBUG_FORMAT_VERSION` in `debug.h`.

## Risks And Test Signals
Risks include sleeping firmware queries while holding `ctrl_lock`, debug readers racing teardown, only dumping available action STE tables but not full-list tables, pointer-derived IDs that are not stable across runs, and format drift with user-space parsers. Test signals include reading debugfs during active rule insertion/deletion, reading after unsupported-context open, faulting flow table query, and parser compatibility against all emitted resource type IDs.

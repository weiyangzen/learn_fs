# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/en_tc_tracepoint.h

## Purpose

`en_tc_tracepoint.h` declares tracepoints for mlx5e TC flower offload configure/delete/stats and neighbor-used updates.

## Important APIs, Types, and Functions

- `DECLARE_EVENT_CLASS(mlx5e_flower_template, ...)` captures a flower rule cookie and action IDs.
- `DEFINE_EVENT(... mlx5e_configure_flower ...)` and `DEFINE_EVENT(... mlx5e_delete_flower ...)` share the template.
- `TRACE_EVENT(mlx5e_stats_flower, ...)` records cookie, bytes, packets, and last-used time.
- `TRACE_EVENT(mlx5e_tc_update_neigh_used_value, ...)` records neighbor netdev, address, and used state.
- Helper prototypes `put_ids_to_array()` and `parse_action()` are implemented in `en_tc_tracepoint.c`.

## Control Flow

TC offload paths call generated trace helpers around rule add/delete/stats operations. The flower template handles absent `f->rule` by recording zero actions and printing `NULL`.

## State and Persistence Behavior

The file defines observability only; no mlx5 runtime state is persisted or changed.

## Dependencies and Integration Points

Depends on Linux tracepoints, trace sequence, `net/flow_offload.h`, and `en_rep.h`. It integrates with mlx5e TC, representor neighbor tracking, and ftrace/perf tooling.

## Risks and Edge Cases

- `f->cookie` is printed as a pointer-shaped value although it is a cookie cast to `void *`.
- Neighbor trace assignment assumes valid `nhe->neigh_dev`.
- Tracepoint schema changes may affect external debugging scripts.

## Test Signals

Enable TC tracepoints, add/delete flower rules with and without actions, query stats, and update IPv4/IPv6 neighbors. Verify fields and action formatting in trace output.

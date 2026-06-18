# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fs_tracepoint.h

## Purpose

`fs_tracepoint.h` declares mlx5 flow-steering tracepoints for flow table, flow group, flow table entry, and flow rule add/delete operations.

## Important APIs, Types, and Functions

- `TRACE_EVENT(mlx5_fs_add_ft/del_ft)` records flow table pointer, id, level, and type.
- `TRACE_EVENT(mlx5_fs_add_fg/del_fg)` records group range, id, match criteria enable flags, and masks.
- `TRACE_EVENT(mlx5_fs_set_fte/del_fte)` records FTE index, action flags, flow tag/source, masks, values, and whether this is add vs set.
- `TRACE_EVENT(mlx5_fs_add_rule/del_rule)` records rule pointer, owning FTE, software action, destination, and counter ID.
- `ACTION_FLAGS` maps mlx5 flow context action bits to printable strings.
- `__parse_fs_hdrs()` and `__parse_fs_dst()` call helper functions implemented in `fs_tracepoint.c`.

## Control Flow

Flow steering code emits these tracepoints during object lifecycle changes. The fast-assign blocks copy masks, values, and destination structs into the trace entry so printing does not depend on later object lifetime.

## State and Persistence Behavior

No driver state is mutated. The tracepoint payload is transient tracing state.

## Dependencies and Integration Points

Depends on Linux tracepoint APIs, `../fs_core.h`, mlx5 flow steering object layouts, and helper implementations in `fs_tracepoint.c`. Tracepoints are exported by the C file for use by other modules.

## Risks and Edge Cases

- The `mlx5_fs_add_rule` trace checks `rule->dest_attr.type & MLX5_FLOW_DESTINATION_TYPE_COUNTER`; destination type is an enum, so bitwise treatment depends on mlx5 destination constants remaining compatible with this pattern.
- Pointer fields in trace output are diagnostic identifiers, not stable object handles.
- Tracepoint payload sizes include several match arrays; enabling tracing on heavy flow churn can be expensive.

## Test Signals

Run flow steering add/delete tests with tracing enabled and compare emitted object IDs, match fields, actions, and destinations to programmed rules. Build with tracepoints enabled as a module/export consumer.

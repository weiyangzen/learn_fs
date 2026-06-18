# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/diag/vhca_tracepoint.h

## Purpose

`sf/diag/vhca_tracepoint.h` defines the tracepoint emitted when an mlx5 VHCA state event is queried, rearmed, and fanned out.

## Important APIs and Control Flow

The single `TRACE_EVENT(mlx5_sf_vhca_event)` records device name, hardware function id, software SF number, and new VHCA state from `struct mlx5_vhca_state_event`. It is used by `vhca_event.c` after querying firmware state and before notifying subscribers.

## State and Dependencies

The tracepoint does not change state. It depends on Linux tracepoint infrastructure, `struct mlx5_core_dev`, and `struct mlx5_vhca_state_event`. The include footer points trace generation to `sf/diag/vhca_tracepoint`.

## Risks and Test Signals

If event fields diverge from `struct mlx5_vhca_state_event`, trace output will become misleading. Validate with ftrace/perf during SF active, in-use, teardown, and allocated transitions, and compare with devlink function opstate.

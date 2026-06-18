# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/health.c

## Purpose

`en/health.c` provides common mlx5e health reporter helpers for devlink fmsg formatting, CQ/EQ diagnostics, reporter creation/destruction, channel health updates, SQ recovery, channel recovery, EQ recovery, generic report dispatch, resource dump streaming, and queue dump formatting.

## Important APIs, Types, and Functions

- `mlx5e_health_fmsg_named_obj_nest_start/end()` wrap named devlink fmsg object nesting.
- `mlx5e_health_cq_diag_fmsg()` queries a CQ and emits CQN, hardware status, CI, and size.
- `mlx5e_health_cq_common_diag_fmsg()` emits CQ stride and size without querying hardware status.
- `mlx5e_health_eq_diag_fmsg()` emits EQ number, IRQ, vector index, consumer index, and size.
- `mlx5e_health_create_reporters()` / `destroy_reporters()` create/destroy TX and RX reporters.
- `mlx5e_health_channels_update()` marks reporters healthy after channel updates.
- `mlx5e_health_sq_to_ready()` moves an SQ from ERR to RST to RDY.
- `mlx5e_health_recover_channels()` reopens channels under RTNL, netdev lock, and `state_lock`.
- `mlx5e_health_channel_eq_recover()` polls an IRQ-disabled EQ and updates stats.
- `mlx5e_health_report()` either calls direct recovery or `devlink_health_report()`.
- `mlx5e_health_rsc_fmsg_dump()` streams resource dump pages into a devlink binary fmsg.
- `mlx5e_health_queue_dump()` dumps a full QPC for a queue index.

## Control Flow

Reporter-specific code calls the common fmsg helpers to build structured diagnoses and dumps. Recovery may transition a failed SQ through reset states, reopen all channels when the interface is open, or poll a stuck EQ while interrupts are disabled. Resource dumps create a command, loop through `mlx5_rsc_dump_next()`, chunk page data into devlink binary records, and clean up command/page state.

## State and Persistence Behavior

Persistent mutations include reporter pointers/states, SQ firmware state transitions, channel reopen side effects, `stats->eq_rearm`, and devlink health reporter state. Resource dump output is transient fmsg data; resource dump state lives in `mdev->rsc_dump`.

## Dependencies and Integration Points

Depends on `health.h`, EQ helpers, resource dump API, mlx5 CQ/SQ modification/query APIs, devlink health, RTNL/netdev locking, and TX/RX reporter implementations. It is the shared utility layer for mlx5e health reporters.

## Risks and Edge Cases

- `mlx5e_health_cq_diag_fmsg()` ignores `mlx5_core_query_cq()` errors and may report default status.
- `mlx5e_health_rsc_fmsg_dump()` starts the devlink binary nest before command creation; error paths still close the nest except for unsupported return before allocation.
- Recovery paths require correct lock ordering: RTNL, netdev lock, then `state_lock`.
- Direct recovery is used when no reporter exists, so reporter absence changes observability but not recovery attempt.

## Test Signals

Trigger TX/RX CQ errors, SQ errors, RX timeouts, and EQ recovery. Run devlink health diagnose/dump and verify CQ/EQ/resource dump fields. Fault-inject resource dump command creation and continuation failures. Validate lockdep under channel recovery.

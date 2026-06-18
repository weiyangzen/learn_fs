# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/dim.h

## Purpose

`en/dim.h` declares mlx5e Dynamic Interrupt Moderation helpers and conversion utilities between Linux DIM CQ-period modes and mlx5 hardware CQ-period modes.

## Important APIs, Types, and Functions

- `mlx5e_dim_cq_period_mode()` converts a boolean start-from-CQE setting to DIM constants.
- `mlx5e_cq_period_mode()` maps `enum dim_cq_period_mode` to `enum mlx5_cq_period_mode`, warning on invalid input and defaulting to EQE.
- Prototypes cover RX/TX DIM work handlers and enabling/disabling DIM on RQs/SQs.

## Control Flow

Coalesce/ethtool and channel code use these helpers to translate user/kernel moderation semantics to hardware CQ modification calls and to schedule DIM work.

## State and Persistence Behavior

The header has no storage. Implementations mutate per-RQ/per-SQ DIM pointers and CQ moderation state.

## Dependencies and Integration Points

Depends on Linux DIM, mlx5 IFC definitions, and forward declarations of RQ/SQ/work structures. Integrated with `channels.c`, ethtool coalesce, and CQ moderation code.

## Risks and Edge Cases

Invalid DIM CQ-period mode triggers `WARN_ON_ONCE` and falls back to EQE mode. Callers should validate external inputs earlier.

## Test Signals

Change coalesce period mode and DIM enablement via ethtool and verify hardware CQ period mode transitions. Compile with DIM-related code paths.

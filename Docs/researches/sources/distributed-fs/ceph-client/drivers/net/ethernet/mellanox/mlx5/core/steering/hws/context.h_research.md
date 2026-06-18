# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/context.h

## Purpose
`context.h` defines the central HWS context object and capability flags shared by the steering subsystem.

## Important APIs, Types, And Functions
`enum mlx5hws_context_flags` records HWS support, private PD ownership, BWC support, and native API support. `enum mlx5hws_context_shared_stc_type` indexes shared STC resources. `struct mlx5hws_context_common_res` stores default STCs, shared STCs, and default miss table. `struct mlx5hws_context_debug_info` stores debugfs dentries. `struct mlx5hws_context_vports` stores e-switch manager/uplink GVMI and vport xarray. `struct mlx5hws_context` ties together the mlx5 device, queried caps, PD number, STC pool, action STE pools, delayed cleanup work, caches, control lock, send queues, BWC queue locks, table list, debug data, peers, and vports.

Inline helpers test BWC and native support. Function declarations expose dynamic reparse capability and selected reparse mode.

## Control Flow And State
The context is process/kernel-lifetime state for HWS. Most fields are initialized in `context.c` and then referenced by table, matcher, action, BWC, definer, vport, send, and debug code. `ctrl_lock` is the broad control-plane serialization primitive for context-wide resources and some refcounts.

## Dependencies And Integration Points
The header is included throughout the HWS implementation. It integrates command caps, pools, delayed work, send engine state, debugfs, xarrays, and vport peer mapping.

## Risks And Test Signals
Risks are stale assumptions about which fields exist when `HWS_SUPPORT` is not set, insufficient locking around shared state, and teardown ordering for delayed work and debugfs readers. Tests should validate all public operations reject unsupported contexts and run under lockdep during open/close and debug dumps.

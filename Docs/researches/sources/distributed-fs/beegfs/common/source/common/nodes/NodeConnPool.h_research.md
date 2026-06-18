# sources/distributed-fs/beegfs/common/source/common/nodes/NodeConnPool.h

## Purpose
Declares the per-node connection pool and its lightweight stats/error-state helpers.

## Important APIs, Types, And Functions
`NodeConnPoolStats` counts established TCP and RDMA sockets. `NodeConnPoolErrorState` tracks last successful peer/NIC and whether the prior attempt failed on all routes to suppress repetitive logs. `NodeConnPool` exposes socket acquire/release/invalidate, interface update, peer-name lookup, local NIC capability setting, max-connection override, stats export, and source-map reload.

## Control Flow
The public API separates normal socket lifecycle from interface updates. Private helpers handle invalidation, idle flag reset, socket options, auth/directness messages, stats, and route source-map loading.

## State, Persistence, And Dependencies
All fields are volatile runtime state. The class owns a `Mutex` and `Condition`, raw `PooledSocket*` list, NIC data, app pointer, parent node reference, and accounting counters. It is non-copyable and non-movable.

## Integration Points
Included by `Node`, and through `Node` by the stores and messaging toolkit. Configuration comes from `ICommonConfig`.

## Risks
Raw socket ownership means all acquire/release/invalidate paths must be paired. Direct setters such as `setChannelDirect()` are not locked, so callers should set them before concurrent use. Stats are counters, not historical telemetry.

## Test Signals
Header-level tests should confirm API overrides in test subclasses, lock-protected getters, and error-state logging decisions after success, partial failure, and complete failure.

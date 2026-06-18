# sources/control-plane/mayastor/io-engine/src/pool_information.rs

## Purpose
This file stores lightweight in-memory pool runtime status, currently focused on pool I/O stall state and recent stall-transition timestamps.

## Important APIs, Types, And Functions
`POOL_INFO` is a global `Lazy<RwLock<HashMap<String, RwLock<PoolInfo>>>>`. `PoolInfo` has `io_stalled` and `transition_timestamps`. `PoolInfo::update_transition_timestamp` drops timestamps outside a configured window. `PoolInfo::get`, `pool_info_read`, and `pool_info_write` expose guarded access.

## Control Flow
Callers insert or update pool entries through the write guard, then read individual pool state through mapped read guards. `update_transition_timestamp` is called by consumers after state transitions to keep the rolling window bounded.

## State, Persistence, And Dependencies
All state is process-local and lost on restart. It depends only on `once_cell`, `parking_lot`, `HashMap`, `VecDeque`, and `Instant`.

## Integration Points
Pool health and stall-detection code can use this as shared runtime state without touching backend metadata. The API returns lock guards, so callers can cheaply inspect state while preserving synchronization.

## Risks
There is no automatic entry creation or eviction here; callers must manage map lifecycle. Nested `RwLock`s reduce coarse contention but can create lock-order risks if external code mixes map and entry locks carelessly. Timestamps are monotonic `Instant`s and cannot be serialized.

## Test Signals
Tests should cover insertion/read lookup, missing pool lookup, transition timestamp retention with short and long windows, and concurrent read/write access patterns.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ct_types.h

## Purpose

`xe_guc_ct_types.h` defines the persistent data structures for the GuC CT layer, including CTB descriptors, snapshots, state enum, debug dead-CT state, fast-request tracking, and the main `struct xe_guc_ct`.

## Important APIs, Types, and Functions

- `struct guc_ctb_info` caches CTB size, reserved space, head, tail, free space, and broken status.
- `struct guc_ctb` pairs a BO with descriptor and command maps plus cached info.
- `struct guc_ctb_snapshot` and `struct xe_guc_ct_snapshot` capture descriptor/info and optional raw CTB bytes for later printing.
- `enum xe_guc_ct_state` defines not-initialized, disabled, stopped, and enabled states.
- Debug-only `struct xe_dead_ct` stores dead-channel reason, snapshots, and worker.
- Debug-only `struct xe_fast_req_fence` records recent fast-request fences/actions and optional call stacks.
- `struct xe_guc_ct` owns locks, H2G/G2H CTBs, outstanding G2H count, workers, state, fence sequence/xarray, waitqueues, message buffers, and debug state.

## Control Flow

The implementation initializes this structure in stages: lock/workqueue/xarray setup first, BO allocation second, CTB descriptor setup when enabling, and state transitions throughout reset/power operations. Send and receive paths update `guc_ctb_info` under the mutex and fast spinlock.

## State and Persistence Behavior

All fields persist for the GuC/GT lifetime. `g2h_outstanding`, CTB `space/head/tail`, `state`, and `fence_lookup` are highly mutable runtime state. Snapshots are separately allocated copies and must be freed by callers.

## Dependencies and Integration Points

The type depends on interrupt/workqueue, iosys-map, spinlock, waitqueue, xarray, optional stack depot, and GuC CTB ABI structures. It is embedded in `struct xe_guc` and consumed by CT, GuC lifecycle, IRQ, debug, and devcoredump code.

## Risks and Edge Cases

The state structure mixes mutex-protected, spinlock-protected, workqueue, and debug fields; misuse of locking can corrupt credits or fence lookup. `msg` and `fast_msg` are fixed-size protocol buffers and rely on CTB max-length validation. Debug-only fields must not leak assumptions into non-debug builds.

## Test Signals

Tests should validate initial state, CTB info invariants, snapshot allocation/free, xarray fence lifetime under cancellation, debug fast-request wrap behavior, and state transitions preserving lock ordering.

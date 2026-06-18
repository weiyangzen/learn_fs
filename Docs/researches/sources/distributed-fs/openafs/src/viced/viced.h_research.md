# sources/distributed-fs/openafs/src/viced/viced.h

## Purpose

`viced.h` is the primary fileserver header for shared types, counters, statistics structures, restart constants, locks, and DAFS runtime mode state. It defines the `DirHandle` contract used by physical directory I/O and the `fs_state` contract used by DAFS startup/shutdown coordination.

## Important APIs, Types, And Functions

- `DirHandle` stores volume/device/inode/vnode/uniquifier/cache-check identity plus an `IHandle_t *`.
- Opcode/stat constants define server call counter indexes and fetch/store size buckets.
- `struct AFSCallStatistics`, `struct AFSDisk`, and `struct AFSStatistics` define legacy statistics surfaces.
- Global flags `busyonrst`, `saneacls`, and `enable_old_store_acl` are declared for cross-file policy checks.
- Restart/panic constants and thread limits define fileserver control values.
- `FS_LOCK`, `FS_UNLOCK`, `FSYNC_LOCK`, and `FSYNC_UNLOCK` wrap global pthread mutexes.
- Under `AFS_DEMAND_ATTACH_FS`, `struct fs_state` tracks server mode, helper-thread tranquility, salvage sync fatal state, state-save/restore/verify options, a condition variable, and an rwlock. `FS_STATE_*` macros initialize and lock that state.
- `viced_SuperUser(struct rx_call *call)` is declared for RX stats authorization.

## Control Flow

This header encodes shared control primitives rather than executable flow. `DirHandle` is filled by `SetDirHandle` before directory buffer I/O and compared by `FidEq`. DAFS code uses `FS_STATE_WRLOCK` to transition from normal to shutdown, helper threads use the same lock to publish tranquil flags, and shutdown waits on `worker_done_cv` while checking these flags.

## State And Persistence Behavior

The `DirHandle` fields are deliberately copied out of the underlying ihandle so cached directory pages remain tied to the original volume/vnode generation even if an ihandle is later reused. `fs_state.options` fields are immutable after multithreaded startup and determine whether `serialize_state.c` writes or reads persistent host/callback state.

## Dependencies And Integration Points

It includes system-call utility headers and `fs_stats.h`, and it exposes shared locks for `viced.c`, file procedure code, and fsync paths. It also provides `DirHandle` to `physio.c` and DAFS mode definitions to `serialize_state.c`.

## Risks And Edge Cases

- Comments warn that `DirHandle` size and field ordering matter to `dir/buffer.c`; layout changes can break cache hashing.
- Lock hierarchy notes put `fs_state.state_lock` directly above `FS_LOCK`; inversions can deadlock shutdown.
- `volatile` fields in `fs_state` are not a synchronization substitute; correct use depends on the provided locks.

## Test Signals

Static ABI/layout checks for `DirHandle`, lock-order review tests, and DAFS thread-state transition tests are important. Statistics consumers should also compile-check all counter constants against generated RPC opcode ranges.

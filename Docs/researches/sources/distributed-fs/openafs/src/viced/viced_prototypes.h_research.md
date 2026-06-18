# sources/distributed-fs/openafs/src/viced/viced_prototypes.h

## Purpose

`viced_prototypes.h` is a small cross-module declaration header for fileserver globals and functions needed by multiple `viced` components. It avoids local extern duplication for error translation, quota spare settings, callback initialization/break helpers, and DAFS state persistence entry points.

## Important APIs, Types, And Functions

- `sendBufSize` is the global fileserver send buffer size.
- `sys_error_to_et` and `init_sys_error_to_et` expose system-error to OpenAFS error-table translation.
- `BlocksSpare` and `PctSpare` expose quota/partition spare policy from `afsfileprocs.c`.
- `InitCallBack`, `BreakLaterCallBacks`, and `BreakVolumeCallBacksLater` expose callback package operations.
- Under `AFS_DEMAND_ATTACH_FS`, `fs_stateSave` and `fs_stateRestore` expose serialized state lifecycle calls.

## Control Flow

This header does not implement flow, but the declarations connect startup/shutdown and maintenance logic: `viced.c` initializes callbacks with `InitCallBack`, the fsync maintenance thread drains delayed callback breaks via `BreakLaterCallBacks`, the volume package can use `BreakVolumeCallBacksLater`, and DAFS shutdown/startup invokes `fs_stateSave`/`fs_stateRestore`.

## State And Persistence Behavior

The DAFS prototypes are the persistence bridge to `serialize_state.c`. The spare-space globals affect fileserver write/quota behavior but are not persisted here.

## Dependencies And Integration Points

The file assumes common OpenAFS typedefs such as `afs_int32` and `VolumeId` are already visible to includers. It is included by `physio.c`, `serialize_state.c`, and `viced.c`.

## Risks And Edge Cases

- Because it is a broad extern header, type drift between declarations and implementations can cause subtle ABI or compile failures.
- The conditional DAFS declarations mean non-DAFS builds must not reference state save/restore.

## Test Signals

The main signal is full matrix compilation with and without `AFS_DEMAND_ATTACH_FS`, plus link checks for callback and error translation symbols.

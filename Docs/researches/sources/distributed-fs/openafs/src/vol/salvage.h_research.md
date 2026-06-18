# sources/distributed-fs/openafs/src/vol/salvage.h

## Purpose
Defines the salvager-specific `DirHandle` used by directory repair code. This is intentionally separate from fileserver directory handles.

## Important APIs, Types, And Functions
`DirHandle` stores `dirh_volume`, `dirh_device`, `dirh_inode`, `dirh_handle`, `dirh_cacheCheck`, and a pointer to `volumeChanged`. The file includes `afs/afssyscalls.h` so `Inode` and related system-call abstractions are available.

## Control Flow
No functions are implemented here. `physio.c` initializes, copies, compares, reads, writes, and releases this structure during salvage directory processing.

## State And Persistence
The structure holds runtime identity for a directory object and a pointer to mutable caller state indicating whether the volume was repaired. It represents persistent directory storage through its inode handle but stores no data on its own.

## Dependencies And Integration Points
It is used by `physio.c`, the salvager directory routines, and code including `afs/dir.h` in salvage mode. It must match the expectations of `SetSalvageDirHandle`, `ReallyRead`, and `ReallyWrite`.

## Risks And Test Signals
Risks are layout/signature drift against directory package callbacks and missed `IH_RELEASE` when handles are copied or zapped incorrectly. Salvager build coverage and directory salvage tests are the main signals.

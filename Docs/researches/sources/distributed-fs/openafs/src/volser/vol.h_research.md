# sources/distributed-fs/openafs/src/volser/vol.h

## Purpose
Defines the `DirHandle` structure used by volser physical directory I/O helpers.

## Important APIs And Types
`DirHandle` stores a volume id, device, inode, cache-check value, and referenced `IHandle_t *`. It includes `<afs/afssyscalls.h>` to pick up `Inode`.

## Control Flow, State, And Persistence
There is no executable control flow. The structure is in-memory state that identifies a directory object; `physio.c` uses it to open inode handles and read/write AFS directory pages.

## Dependencies And Integration
Integrated with `physio.c`, `afs_dir` routines, `vol_split.c`, and salvage-style directory manipulation. Consumers must manage `dirh_handle` references using `IH_INIT`, `IH_RELEASE`, or helpers such as `SetSalvageDirHandle` and `FidZap`.

## Risks And Test Signals
Risks include stale cache-check identity, leaked inode handles, and structure layout expectations in directory helper code. Test signals include handle lifecycle tests, `FidEq`/`FidVolEq` behavior, and split-volume mountpoint directory updates.

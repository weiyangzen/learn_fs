# sources/distributed-fs/openafs/src/volser/physio.h

## Purpose
Declares the `DirHandle` setup and teardown helpers exported by `physio.c`.

## Important APIs
`SetSalvageDirHandle` initializes a `DirHandle` for a volume/device/inode and takes an inode-handle reference. `FidZap` releases the handle and clears the structure.

## Control Flow, State, And Persistence
No control flow exists in the header. The declared functions affect in-memory handle state; callers use those handles for persistent directory page I/O through `physio.c` and directory-library callbacks.

## Dependencies And Integration
It depends on `DirHandle`, `VolumeId`, and `Inode` declarations supplied by surrounding includes such as `vol.h` and AFS syscall headers. It is used by code that performs salvage or split-volume directory edits.

## Risks And Test Signals
Risks include missing prototypes for other `physio.c` functions used indirectly and include-order dependency for `DirHandle`. Test signals are warning-free builds and directory operation tests that confirm every `SetSalvageDirHandle` is paired with `FidZap`.

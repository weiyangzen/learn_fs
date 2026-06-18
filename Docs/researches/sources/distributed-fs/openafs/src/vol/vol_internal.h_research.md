# sources/distributed-fs/openafs/src/vol/vol_internal.h

## Purpose
Provides a small internal volume-module prototype boundary. In this subset it exposes the physical I/O helper needed by the salvager to initialize directory handles.

## Important APIs, Types, and Functions
The only declaration is `SetSalvageDirHandle(DirHandle *, VolumeId, Device, Inode, int *)`, implemented by `physio.c`. It binds a `DirHandle` to a volume id, device, inode, and a change flag pointer.

## Control Flow
There is no executable control flow. `vol-salvage.c` calls `SetSalvageDirHandle` before checking, copying, rebuilding, or mutating AFS directories in `CopyOnWrite`, `CopyAndSalvage`, `CreateRootDir`, `SalvageDir`, and orphan attachment.

## State and Persistence Behavior
The helper declaration is persistence-critical because the resulting `DirHandle` is the object through which directory operations read and write directory inodes. The `int *` change flag lets low-level directory handling propagate that a volume was modified.

## Dependencies and Integration Points
Requires `DirHandle`, `VolumeId`, `Device`, and `Inode` definitions from the including volume sources. It creates an intentional private dependency from salvage logic to physical directory I/O without exporting the entire `physio.c` surface.

## Risks
The narrow header means type availability depends on include order. Any signature change in `physio.c` must be kept synchronized here and across salvager call sites.

## Test Signals
Compilation validates the prototype. Directory salvage tests that repair, copy, or create directories validate the runtime behavior behind this declaration.

## Source Notes
Read as C header; 8 source lines; source-tree-aligned report generated for subset `subset-b-007819`.

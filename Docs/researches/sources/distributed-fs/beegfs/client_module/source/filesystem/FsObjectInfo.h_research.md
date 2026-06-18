# sources/distributed-fs/beegfs/client_module/source/filesystem/FsObjectInfo.h

## Purpose
Provides a small base "class" for file-private BeeGFS objects, distinguishing directory and file state and supporting virtual cleanup.

## Important APIs and Types
`FsObjectType` enumerates `DIRECTORY` and `FILE`. `FsObjectInfo` stores an `App*`, object type, and `uninit` function pointer. Inline functions initialize the base, dispatch virtual destruction, and return the app/type.

## Control Flow
Derived objects call `FsObjectInfo_init()` then assign `uninit`. Generic cleanup calls `FsObjectInfo_virtualDestruct()`, which invokes the derived uninit and frees the object.

## State and Persistence
State is per open file/directory object and is not durable. It links file-private state back to the per-mount `App`.

## Dependencies and Integration Points
Used by `FsDirInfo` and `FsFileInfo`; indirectly integrated with VFS file private data and close/release paths.

## Risks
`FsObjectInfo_virtualDestruct()` does not check whether `uninit` is null. Any partially initialized object passed to it will crash. The pattern relies on C casts from derived structs whose first member is `FsObjectInfo`.

## Test Signals
Construct/destroy file and directory private objects, allocation failure paths that avoid virtual destruction on uninitialized memory, and type dispatch in release paths.

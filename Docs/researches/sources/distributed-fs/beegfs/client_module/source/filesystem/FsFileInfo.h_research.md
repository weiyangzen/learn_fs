# sources/distributed-fs/beegfs/client_module/source/filesystem/FsFileInfo.h

## Purpose
Declares the opaque `FsFileInfo` type and the public API for managing per-open-file BeeGFS state.

## Important APIs and Types
Defines cache heuristic constants: initial hits `3`, upper threshold `5`, lower threshold `-5`, and slow-start read length `64 KiB`. Declares construction, initialization, uninitialization, cache hit adjustment, flag/offset/caching/append accessors, `FsFileInfo_getIOInfo()`, and entry-lock usage accessors.

## Control Flow
The header establishes an opaque type boundary: users manipulate state through declared functions rather than direct field access. Read/write code can call cache and offset accessors while remoting code can derive `RemotingIOInfo`.

## State and Persistence
No state is defined in the header beyond constants and forward declarations. Runtime state is implemented in `FsFileInfo.c` and is per open file.

## Dependencies and Integration Points
Includes common definitions, `FhgfsInode`, and `FsObjectInfo`. Forward declarations avoid pulling in remoting and striping definitions for all includers.

## Risks
Changing constants alters cache behavior globally. Because the struct is opaque, any new direct field usage elsewhere would require exposing layout or adding accessors.

## Test Signals
Compile all file operation users, then validate cache threshold behavior, `RemotingIOInfo` generation, and close cleanup paths that rely on entry-lock state.

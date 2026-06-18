# sources/distributed-fs/beegfs/client_module/source/filesystem/FsDirInfo.h

## Purpose
Defines per-open-directory state used to cache directory listing batches, maintain server offsets, and remember metadata-server capabilities.

## Important APIs and Types
`FsDirInfo` embeds `FsObjectInfo` and owns `StrCpyVec` entry names, `UInt8Vec` entry types, `StrCpyVec` entry IDs, `Int64CpyVec` server offsets, current server/local positions, end-of-directory state, and capability bitmasks. `META_CAP_LISTDIR_BUFSIZE_MODE` indicates support for buffer-size-aware directory listing. Inline constructors/destructors and getters/setters manage this state.

## Control Flow
`FsDirInfo_construct()` allocates and initializes vectors, offsets, end flag, capability masks, and virtual uninit pointer. Readdir/listing code appends server responses to the vectors, advances `currentContentsPos`, updates `serverOffset`, and marks `endOfDir`. Capability helpers mark a capability known and supported/unsupported.

## State and Persistence
All state is per directory handle and in memory. It persists only while the open directory file object exists. Vector contents mirror a fetched listing window and are not durable.

## Dependencies and Integration Points
Depends on BeeGFS vector containers, storage definitions, common types, and `FsObjectInfo`. It is used by directory VFS operations that need file-private directory enumeration state.

## Risks
This header contains inline function definitions, so changes affect every includer. Vector triplets must stay index-aligned; corruption yields wrong names/types/entry IDs/offsets. Capability bitmasks are single-byte and assume future capabilities fit. The virtual destructor assumes `uninit` is set through initialization.

## Test Signals
Directory listing tests should cover empty dirs, multi-batch dirs, telldir/seekdir offsets, end-of-dir transitions, vector cleanup, capability probe known/supported states, and allocation failure.

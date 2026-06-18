<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/ChunkStore.cpp -->
## sources/distributed-fs/beegfs/storage/source/storage/ChunkStore.cpp

### Purpose
Implements chunk directory cache/reference management, chunk directory creation/removal, quota-aware chunk opening, and legacy V2 permission repair.

### Important APIs, Types, And Functions
Important functions are constructor, referenceDir(), releaseDir(), cache sweep helpers, rmdirChunkDirPath(), mkdirV2ChunkDirPath(), mkdirChunkDirPath(), openAndChown(), openChunkFile(), and chmodV2ChunkDirPath().

### Control Flow
Directory references are stored in a map of AtomicObjectReferencer objects and a separate refCache that holds extra references for cache retention. Opening a chunk first checks quota-exceeded stores, tries openAndChown(), creates missing directories with V2 or V3 locking if PATHNOTEXISTS, retries open, unlocks/releases the last directory element, and logs failures. V3 mkdir holds parent/current locks to prevent racing bottom-up rmdir from removing a just-created parent.

### State, Persistence, And Dependencies
Persistent effects include creating chunk directories, creating/opening chunk files, chowning quota-owned files, removing empty chunk directories, and chmodding legacy V2 paths. Runtime state includes the directory reference map, refCache, random sweep state, and locks. Depends on Program/App config, ChunkDir, StorageTk path conventions, ExceededQuotaStore, StorageTkEx include, Random, Path, POSIX mkdirat/unlinkat/openat/fchown/fchmodat, and quota/session data.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include StorageTk::pathExists() in quota check not using targetFD and therefore checking process-relative paths, unlink(path.c_str()) in openAndChown also not targetFD-relative, manual cache reference accounting, ignored chmodV2 retry result in callers, and complex lock release paths on mkdir/open failures.

### Test Signals
Test signals include V2 and V3 path creation, racing mkdir/rmdir, quota exceeded on new versus existing chunk, NOTOWNER repair, cache sweep limits, openAndChown failure cleanup, and rmdir stopping on ENOTEMPTY/ENOENT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/ChunkStore.cpp -->

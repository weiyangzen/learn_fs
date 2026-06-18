<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/ChunkStore.h -->
## sources/distributed-fs/beegfs/storage/source/storage/ChunkStore.h

### Purpose
Declares the directory-level chunk store used by storage IO paths to manage chunk directory locks, references, cache, creation, removal, and file opening.

### Important APIs, Types, And Functions
Public APIs include referenceDir(), releaseDir(), getCacheSize(), cacheSweepAsync(), rmdirChunkDirPath(), openChunkFile(), and chmodV2ChunkDirPath(). Private helpers manage directory insertion, release, cache add/remove/sweep, mkdir variants, openAndChown(), and getUniqueDirID().

### Control Flow
The class separates directory object lifetime from filesystem paths: ChunkDir instances lock path elements, while POSIX calls operate relative to target FDs.

### State, Persistence, And Dependencies
State consists of dirs, refCacheSyncLimit, refCacheAsyncLimit, randGen, refCache, and rwlock. Persistent state is only changed by the cpp methods that create/remove dirs and files. Depends on AtomicObjectReferencer, MetadataTk, Random, Path, StorageDefinitions, StorageErrors, SessionQuotaInfo, ExceededQuotaStorePtr, and ChunkDir.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include raw pointer referencers, manual release requirements after referenceDir(), and cache limits computed at construction from global App config.

### Test Signals
Test signals include reference/release balance, getUniqueDirID depth uniqueness, cache size and sweep behavior, and openChunkFile declarations matching caller expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/ChunkStore.h -->

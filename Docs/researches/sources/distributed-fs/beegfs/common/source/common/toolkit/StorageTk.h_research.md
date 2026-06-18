<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/StorageTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/StorageTk.h

**Purpose:** Declares the `StorageTk` static utility surface and storage path/format constants used throughout BeeGFS common, metadata, and storage code.

**Important APIs/types/functions:** Defines filenames (`format.conf`, `nodeNumID`, `targetID`, `targetNumID`, `storagePoolID`, session backups), chunk-hash constants, `Mount`, `CloseDirDeleter`, and the public storage helper API. Inline helpers cover path existence, child detection, file ID generation, ID counter reset, dirent type conversion, hash split/merge, chunk path V2/V3 generation, timestamp-to-path mapping, `createFile`, and hash computations.

**Control flow:** Inline chunk path selection depends on `PathInfo::hasOrigFeature`: old format uses two-level hash directories, while newer layout uses UID, timestamp-derived year/month/day-like directories, parent ID, and entry ID. `generateFileID` combines counter, timestamp, and local node ID as hex components. `resetIDCounterToNow` refuses to move the timestamp backward.

**State and persistence behavior:** Declares static `idCounter`, with high 32 bits timestamp and low 32 bits sequence. The constants name persistent files used by `StorageTk.cpp` and daemon startup/shutdown.

**Dependencies and integration points:** Pulls in BeeGFS path, stat, striping, quota/storage pool, locking, hashing, atomics, and POSIX directory types. It is a broad common header, so changes have wide compile impact.

**Risks:** Many inline APIs take strings by value and expose raw POSIX semantics. `pathHasChildren` treats non-directories and missing paths the same as empty. Chunk path logic is compatibility-critical for on-disk layout. `createFile` treats `EEXIST` as success and only optionally tells the caller whether creation happened.

**Test signals:** Existing tests exercise related `Path`, `LockFD`, and `PreallocatedFile` behavior; additional tests should verify chunk path compatibility and hash distribution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/StorageTk.h -->

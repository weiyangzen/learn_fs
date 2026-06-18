<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/toolkit/StorageTkEx.h -->
## sources/distributed-fs/beegfs/storage/source/toolkit/StorageTkEx.h

### Purpose
Provides storage-server-specific helper routines for reading dynamic POSIX file attributes from open FDs or target-relative paths.

### Important APIs, Types, And Functions
APIs are two overloads of getDynamicFileAttribs(): one for an open file descriptor and one for dirFD plus path. It also defines storage format constants, max EntryInfo serialization size, and default chunk dir/file modes.

### Control Flow
Each overload calls fstat or fstatat and fills file size, allocated blocks, modification time, and last access time on success.

### State, Persistence, And Dependencies
No state is stored. Persistent state is not changed; these helpers observe filesystem metadata. Depends on Config, Common, FsckChunk, Path, Storagedata, StorageErrors, Mutex/SafeRWLock includes, StorageTk, and POSIX stat APIs.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include returning false without preserving errno for callers, using st_blocks units directly as allocated block count, and broad includes in a header-only utility.

### Test Signals
Test signals include fstat/fstatat success, missing path failure, symlink behavior via fstatat flags, and correct timestamp/block values for sparse files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/toolkit/StorageTkEx.h -->

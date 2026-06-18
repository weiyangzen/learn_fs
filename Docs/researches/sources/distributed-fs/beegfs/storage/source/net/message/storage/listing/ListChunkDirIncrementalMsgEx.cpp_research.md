<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/listing/ListChunkDirIncrementalMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/listing/ListChunkDirIncrementalMsgEx.cpp

### Purpose
Implements incremental listing of a target chunk directory for scanners such as resync, fsck, or maintenance tools.

### Important APIs, Types, And Functions
processIncoming() reads targetID, mirror flag, relativeDir, offset, maxOutEntries, onlyFiles, and ignore-not-exists from ListChunkDirIncrementalMsg. readChunks() fills names, entryTypes, and newOffset and returns FhgfsOpsErr.

### Control Flow
The handler opens the target-relative directory or duplicates the target root FD for an empty relativeDir, wraps it with fdopendir, seekdir()s to the supplied offset, filters entries through StorageTk::readdirFiltered(), resolves d_type or fstatat fallback, applies onlyFiles filtering, records d_off as the next offset, and sends ListChunkDirIncrementalRespMsg.

### State, Persistence, And Dependencies
The operation is read-only and intentionally has no locking, as documented by the caution comment. State is the caller-provided offset cursor and the transient directory stream. Depends on StorageTargets, target chunk/mirror FDs, POSIX openat/dup/fcntl/fdopendir/readdir/seekdir, StorageTk filtering, MetadataTk type conversion, and response list serialization.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include offset portability across directory mutations, no locking while directories can be concurrently modified, possible O_RDONLY fcntl misuse after dup, and different behavior when ignoreNotExists suppresses logging but still maps ENOENT to PATHNOTEXISTS.

### Test Signals
Test signals include listing root and nested directories, continuation offsets, onlyFiles filtering, DT_UNKNOWN stat fallback, ENOENT with and without ignore flag, and concurrent directory changes during listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/listing/ListChunkDirIncrementalMsgEx.cpp -->

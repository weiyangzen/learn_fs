<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/ChunkDir.h -->
## sources/distributed-fs/beegfs/storage/source/storage/ChunkDir.h

### Purpose
Declares the in-memory lock object representing one chunk directory path element.

### Important APIs, Types, And Functions
ChunkDir stores an ID string and an RWLock, with readLock(), writeLock(), unlock(), and getID(). ChunkStore is a friend and creates/manages instances.

### Control Flow
The object gives ChunkStore a per-directory-element lock to coordinate mkdir/rmdir races across V3 chunk directory paths.

### State, Persistence, And Dependencies
Runtime state is the RWLock and stable ID. No direct persistence exists; it represents filesystem directories on disk indirectly. Depends on string and BeeGFS RWLock.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include manual lock/unlock usage without RAII in callers and ID uniqueness relying on ChunkStore::getUniqueDirID().

### Test Signals
Test signals include concurrent mkdir/rmdir paths using the same directory ID and lock/unlock pairing under errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/ChunkDir.h -->

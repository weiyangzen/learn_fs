<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionLocalFile.h -->
## sources/distributed-fs/beegfs/storage/source/session/SessionLocalFile.h

### Purpose
Declares the per-open-chunk session object used to cache file descriptors, offsets, mirroring metadata, IO counters, and crash-dirty state.

### Important APIs, Types, And Functions
SessionLocalFile contains nested Handle with close(), serialization template, openFile(), setMirrorNodeExclusive(), releaseLastReference(), close(), getters/setters for FD, flags, offset, mirror state, counters, and serverCrashed.

### Control Flow
The class separates store ownership from underlying filesystem handle lifetime: stores hold shared_ptr<SessionLocalFile>, outsiders may hold references, and releaseLastReference returns a closeable Handle only when the removed file has no remaining references and the handle was not claimed by another caller.

### State, Persistence, And Dependencies
Runtime state includes shared Handle, targetID, fileID, openFlags, offset, mirrorNode, isMirrorSession, atomic read/write/read-ahead counters, sessionMutex, and serverCrashed. Serialized state includes IDs, flags, offset, mirror info, crash flag, and counters. Depends on NodeHandle, PathInfo, QuotaData, Mutex, FDHandle, atomic, and BeeGFS serialization helpers.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include complex lifetime protocol around shared_ptr/weak_ptr and claimed atomic, exposing FDHandle by const reference that may become invalid after close, and lock granularity mixing atomics with mutex-protected offset/FD fields.

### Test Signals
Test signals include serialization round trip, handle close after last reference removal, multiple concurrent removals claiming only once, direct IO flag detection, counter atomics, and mirror-session key separation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionLocalFile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionLocalFileStore.cpp -->
## sources/distributed-fs/beegfs/storage/source/session/SessionLocalFileStore.cpp

### Purpose
Implements a mutex-protected map of local-file session objects keyed by file handle, target, and mirror-session status.

### Important APIs, Types, And Functions
APIs include addAndReferenceSession(), referenceSession(), removeSession(), removeAllSessions(), removeAllMirrorSessions(), deleteAllSessions(), getSize(), mergeSessionLocalFiles(), serializeForTarget(), and deserializeForTarget().

### Control Flow
Add inserts a unique_ptr and returns a shared_ptr to inserted or existing session. Remove erases from the map, then calls releaseLastReference() outside the mutex to decide whether a handle can be closed by the caller. Serialization writes a fixed-up element count for sessions matching targetID. Deserialization reads keys and SessionLocalFile objects and rejects mismatched target IDs.

### State, Persistence, And Dependencies
Runtime state is the sessions map guarded by mutex. Persistence is target-filtered serialization used by SessionStore. Depends on SessionLocalFile, Program/App for logging context, serialization framework, boost::make_unique, std::map ordering, and Mutex.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include removeAllMirrorSessions erasing shared_ptrs without returning handles for close, mergeSessionLocalFiles moving from another store without locking that other store, and serializeForTarget writing total session count placeholder correctly only if Serializer mark fixup remains valid.

### Test Signals
Test signals include duplicate add returning existing session, remove with active external reference, target-filtered serialize/deserialize, mismatch target deserialization failure, duplicate merge warning, and mirror cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionLocalFileStore.cpp -->

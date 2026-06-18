<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionLocalFileStore.h -->
## sources/distributed-fs/beegfs/storage/source/session/SessionLocalFileStore.h

### Purpose
Declares the local-file session store and its compound key for file handle, concrete target ID, and mirror/non-mirror namespace.

### Important APIs, Types, And Functions
Public APIs add/reference/remove sessions, bulk remove, mirror-target cleanup, size, merge, serialize, and deserialize. Key has a serialization template and operator< based on tuple ordering.

### Control Flow
The key design lets original and mirrored sessions for the same file handle and target coexist when rotated mirrors can attach both buddies to one server.

### State, Persistence, And Dependencies
State is std::map<Key, shared_ptr<SessionLocalFile>> plus a mutable Mutex. Depends on ObjectReferencer include legacy, Mutex, Common.h, and SessionLocalFile.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include raw pointer parameter to mergeSessionLocalFiles() and direct map ownership semantics that require cpp code to manage handle closing correctly.

### Test Signals
Test signals include key ordering, mirror namespace separation, and compile-time serialization of Key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionLocalFileStore.h -->

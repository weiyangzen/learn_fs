<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionStore.h -->
## sources/distributed-fs/beegfs/storage/source/session/SessionStore.h

### Purpose
Declares the storage daemon session registry keyed by client NumNodeID.

### Important APIs, Types, And Functions
Public APIs allow referencing, adding, synchronizing, listing IDs, sizing, target-filtered serialization/deserialization, and load/save from file.

### Control Flow
The class models sessions as shared objects so in-flight operations can retain references while the map is synchronized or cleaned.

### State, Persistence, And Dependencies
State is std::map<NumNodeID, shared_ptr<Session>> guarded by mutable Mutex. Depends on Node.h, ObjectReferencer include, Mutex, Common.h, and Session.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include exposing removed sessions to caller cleanup while other references may remain and relying on callers to pass an ordered master list to syncSessions().

### Test Signals
Test signals include map lookup/add behavior, syncSessions ordering assumptions, and persistence method declarations matching cpp behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionStore.h -->

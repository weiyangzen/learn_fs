<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionStore.cpp -->
## sources/distributed-fs/beegfs/storage/source/session/SessionStore.cpp

### Purpose
Implements the top-level client Session map, synchronization with management node session lists, and binary session persistence per target.

### Important APIs, Types, And Functions
APIs include referenceSession(), referenceOrAddSession(), syncSessions(), getAllSessionIDs(), getSize(), serializeForTarget(), deserializeForTarget(), loadFromFile(), and saveToFile().

### Control Flow
The store is mutex protected. syncSessions() compares ordered local sessions with ordered master NodeHandle list and removes local sessions not present in the master list, returning removed sessions for cleanup. Serialization writes session count and each key/session payload. Deserialization merges local files into existing sessions. loadFromFile() opens, stats, reads, deserializes, and validates; saveToFile() serializes into a sized buffer and writes a truncating file.

### State, Persistence, And Dependencies
Runtime state is a map from NumNodeID to shared_ptr<Session>. Persistent state is a target-specific session file containing serialized session IDs and local file stores. Depends on Session, Mutex, serialization framework, NodeHandle, filesystem open/read/write/stat/close, boost scoped_array/make_unique, and StringTk/System logging.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include holding the store mutex during file IO, not looping on partial reads/writes, using statBuf.st_size directly for allocation, not fsyncing saved session files, and deserialization count accepting duplicate keys by merging.

### Test Signals
Test signals include session creation/reference, sync removal against sorted master lists, load corrupt/truncated files, save/load round trip, partial write simulation, and merge of duplicate sessions after restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionStore.cpp -->

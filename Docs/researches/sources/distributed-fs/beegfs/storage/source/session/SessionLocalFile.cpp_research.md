<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionLocalFile.cpp -->
## sources/distributed-fs/beegfs/storage/source/session/SessionLocalFile.cpp

### Purpose
Implements opening, closing, serialization support, and mirror-node assignment for an open chunk file within a client session.

### Important APIs, Types, And Functions
Important APIs are SessionLocalFile::Handle::close(), serializeNodeID() deserializer overload, openFile(), and setMirrorNodeExclusive(). openFile() uses target FD, PathInfo, write/read mode, SessionQuotaInfo, ChunkStore, MsgHelperIO, and ExceededQuotaStore.

### Control Flow
openFile() fast-paths already-open handles, then locks the session, constructs the chunk path, opens or creates the chunk. Write opens go through ChunkStore::openChunkFile with quota enforcement and a V2 chmod retry on NOTOWNER. Read opens call MsgHelperIO::openat and ignore ENOENT. The handle FD and offset are initialized before returning. setMirrorNodeExclusive() stores the first mirror node only.

### State, Persistence, And Dependencies
Runtime state includes FDHandle, offset, counters, mirror node, mirror session flag, and serverCrashed flag. Persistent effects are chunk file creation and ownership/permission fixes via ChunkStore. Depends on Program/App, ChunkStore, StorageTk path helpers, quota stores, MsgHelperIO, NodeStoreServers for mirror node deserialization, serialization framework, and FDHandle.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include assigning FDHandle(-1) after read-open ENOENT, logging File created even for read opens, quotaInfo assumed non-null for write opens, and deserialization failing when mirrorNode ID no longer exists.

### Test Signals
Test signals include read missing file, write create with quota, NOTOWNER chmod retry, concurrent open races, mirror node deserialization success/failure, close failure logging, and setMirrorNodeExclusive race behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionLocalFile.cpp -->

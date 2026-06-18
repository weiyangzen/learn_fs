<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/StorageResyncStartedRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/StorageResyncStartedRespMsg.h

### Purpose
`StorageResyncStartedRespMsg` is an empty acknowledgement for `StorageResyncStartedMsg`.

### Important APIs, Types, And Functions
It subclasses `SimpleMsg` with type `NETMSGTYPE_StorageResyncStartedResp`.

### Control Flow
There is no payload-specific control flow.

### State, Persistence, And Dependencies
The message has no state and depends only on simple-message handling.

### Integration Points
It completes the resync-start notification handshake.

### Risks
It carries no status; failure must be represented by missing/failed response at the communication layer. Tests should verify dispatch and timeout handling by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/StorageResyncStartedRespMsg.h -->

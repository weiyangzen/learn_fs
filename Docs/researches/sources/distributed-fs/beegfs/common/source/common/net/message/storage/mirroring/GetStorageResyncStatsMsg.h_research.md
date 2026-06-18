<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetStorageResyncStatsMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetStorageResyncStatsMsg.h

### Purpose
`GetStorageResyncStatsMsg` asks a storage node for buddy resync statistics for a specific target ID.

### Important APIs, Types, And Functions
It subclasses `SimpleUInt16Msg` with `NETMSGTYPE_GetStorageResyncStats`. `getTargetID()` returns the wrapped 16-bit target ID. The no-argument constructor is protected for factory/deserialization use.

### Control Flow
The message is a simple scalar payload. Senders construct with a target ID; receivers read it through inherited serialization.

### State, Persistence, And Dependencies
Only the target ID is held transiently. It depends on `SimpleUInt16Msg` and the storage resync handler.

### Integration Points
Management and monitoring code sends this to storage servers to inspect per-target resync progress.

### Risks
Callers must distinguish storage target IDs from buddy group IDs. Tests should cover valid target IDs, zero/unknown target handling in receivers, and pairing with the response stats message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetStorageResyncStatsMsg.h -->

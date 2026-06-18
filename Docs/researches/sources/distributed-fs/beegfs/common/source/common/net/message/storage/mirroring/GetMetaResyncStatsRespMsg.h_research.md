<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetMetaResyncStatsRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetMetaResyncStatsRespMsg.h

### Purpose
`GetMetaResyncStatsRespMsg` carries `MetaBuddyResyncJobStatistics` back to a monitoring caller.

### Important APIs, Types, And Functions
The class derives from `NetMessageSerdes<GetMetaResyncStatsRespMsg>` and uses a backed pointer to serialize/deserialize `MetaBuddyResyncJobStatistics`. Getters return a pointer or copy the parsed stats to an output reference.

### Control Flow
Senders provide a non-owned stats pointer. Receivers deserialize into the internal `jobStats` object.

### State, Persistence, And Dependencies
The state is a snapshot of resync statistics, not persistent storage. It depends on `BuddyResyncJobStatistics.h`. The default constructor currently initializes `BaseType(NETMSGTYPE_FsckSetEventLoggingResp)`, which appears inconsistent with the response type used by the send constructor.

### Integration Points
Monitoring and management tools use this after `GetMetaResyncStatsMsg` to display metadata resync status.

### Risks
The default-constructor message type mismatch is a strong test signal and may affect factory/deserialization behavior if not overridden elsewhere. Tests should instantiate deserialization objects, verify message type, and round-trip representative stats including empty, running, and completed resync states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetMetaResyncStatsRespMsg.h -->

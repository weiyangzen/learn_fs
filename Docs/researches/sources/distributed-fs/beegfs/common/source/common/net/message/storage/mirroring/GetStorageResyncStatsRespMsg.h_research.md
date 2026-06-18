<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetStorageResyncStatsRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetStorageResyncStatsRespMsg.h

### Purpose
`GetStorageResyncStatsRespMsg` returns `StorageBuddyResyncJobStatistics` for a target.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<GetStorageResyncStatsRespMsg>` with type `NETMSGTYPE_GetStorageResyncStatsResp`. Serialization uses `serdes::backedPtr(jobStatsPtr, jobStats)`. Getters return the parsed stats by pointer or copy.

### Control Flow
Senders pass a non-owned stats pointer; receivers deserialize into the internal `jobStats` object and expose it.

### State, Persistence, And Dependencies
The message is a transient stats snapshot. It depends on `BuddyResyncJobStatistics.h` and NetMessage serdes.

### Integration Points
It is consumed by monitoring tools and management paths after a storage resync stats request.

### Risks
The send-side pointer must remain valid until serialization completes. Tests should verify round-trip of all statistic fields and behavior for idle, active, failed, and completed resync states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetStorageResyncStatsRespMsg.h -->

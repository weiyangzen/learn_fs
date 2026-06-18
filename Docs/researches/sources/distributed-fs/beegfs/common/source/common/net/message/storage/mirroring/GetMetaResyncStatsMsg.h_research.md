<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetMetaResyncStatsMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetMetaResyncStatsMsg.h

### Purpose
`GetMetaResyncStatsMsg` is a payload-free request for metadata buddy resync statistics.

### Important APIs, Types, And Functions
It subclasses `SimpleMsg` and uses `NETMSGTYPE_GetMetaResyncStats`.

### Control Flow
Construction is the entire behavior; `SimpleMsg` supplies header-only serialization.

### State, Persistence, And Dependencies
There is no payload state. It depends on the NetMessage type registry and the metadata service handler that produces the paired response.

### Integration Points
Management/monitoring code sends this to metadata nodes to inspect buddy resync progress.

### Risks
The only protocol risk is routing to a node that does not implement the message type. Tests should verify request/response dispatch and empty-payload compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetMetaResyncStatsMsg.h -->

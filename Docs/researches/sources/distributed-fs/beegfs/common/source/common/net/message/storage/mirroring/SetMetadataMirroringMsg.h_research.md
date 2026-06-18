<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetMetadataMirroringMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetMetadataMirroringMsg.h

### Purpose
`SetMetadataMirroringMsg` is a payload-free request to enable metadata mirroring on the root directory.

### Important APIs, Types, And Functions
It subclasses `SimpleMsg` and uses message type `NETMSGTYPE_SetMetadataMirroring`.

### Control Flow
All behavior is inherited header-only message handling; receiver code performs the root metadata update.

### State, Persistence, And Dependencies
The message has no payload, but the handler changes persistent metadata mirroring state. It includes `EntryInfo` and `Common.h`, though the class itself only needs `SimpleMsg`.

### Integration Points
Management tooling sends this when enabling metadata mirroring for the filesystem root.

### Risks
Because the request has no body, all context and authorization must come from connection/session state. Tests should verify handler idempotence, already-enabled behavior, and response error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetMetadataMirroringMsg.h -->

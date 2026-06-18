## sources/distributed-fs/beegfs/storage/source/net/message/nodes/PublishCapacitiesMsgEx.h

### Purpose
`PublishCapacitiesMsgEx.h` declares the storage-side handler for capacity publication triggers.

### Important APIs, Types, And Functions
It derives from `PublishCapacitiesMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No additional state is stored; processing sets a flag in `InternodeSyncer`.

### Dependencies, Integration Points, Risks, And Test Signals
It is factory-created for `NETMSGTYPE_PublishCapacities`. Tests should validate dispatch and ack behavior.

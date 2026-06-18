## sources/distributed-fs/beegfs/storage/source/net/message/nodes/storagepools/RefreshStoragePoolsMsgEx.h

### Purpose
`RefreshStoragePoolsMsgEx.h` declares the storage-side storage-pool refresh trigger.

### Important APIs, Types, And Functions
The class inherits `RefreshStoragePoolsMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No additional state exists; processing sets a force-refresh flag in the internode syncer.

### Dependencies, Integration Points, Risks, And Test Signals
It is factory-created for `NETMSGTYPE_RefreshStoragePools`. Tests should validate dispatch and acknowledgement.

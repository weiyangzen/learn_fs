## sources/distributed-fs/beegfs/storage/source/net/message/nodes/StorageBenchControlMsgEx.h

### Purpose
`StorageBenchControlMsgEx.h` declares the storage-side benchmark control handler.

### Important APIs, Types, And Functions
The class derives from `StorageBenchControlMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
The header stores no state. Action fields from the base request control benchmark operator mutations.

### Dependencies, Integration Points, Risks, And Test Signals
It is created for `NETMSGTYPE_StorageBenchControlMsg`. Tests should verify factory routing and all action responses through the implementation.

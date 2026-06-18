## sources/distributed-fs/beegfs/storage/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.h

### Purpose
`SetTargetConsistencyStatesMsgEx.h` declares the storage-side consistency-state setter.

### Important APIs, Types, And Functions
The class derives from `SetTargetConsistencyStatesMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No extra state is declared. Inherited target and state lists determine the update sequence.

### Dependencies, Integration Points, Risks, And Test Signals
It is factory-created for `NETMSGTYPE_SetTargetConsistencyStates`. Tests should validate dispatch and target state mutation.

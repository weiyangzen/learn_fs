## sources/distributed-fs/beegfs/storage/source/net/message/nodes/GetTargetConsistencyStatesMsgEx.h

### Purpose
`GetTargetConsistencyStatesMsgEx.h` declares the storage-side target consistency state query handler.

### Important APIs, Types, And Functions
The class derives from `GetTargetConsistencyStatesMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No additional state is introduced; inherited `targetIDs` drive the response.

### Dependencies, Integration Points, Risks, And Test Signals
It is created by the message factory for `NETMSGTYPE_GetTargetConsistencyStates`. Tests should validate virtual dispatch and unknown-target behavior implemented in the `.cpp`.

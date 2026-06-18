## sources/distributed-fs/beegfs/storage/source/net/message/nodes/storagepools/RefreshStoragePoolsMsgEx.cpp

### Purpose
`RefreshStoragePoolsMsgEx.cpp` handles management requests to force storage pool information refresh.

### Important APIs, Types, And Functions
`processIncoming()` calls `Program::getApp()->getInternodeSyncer()->setForceStoragePoolsUpdate()` and acknowledges the request.

### Control Flow, State, And Persistence
Only internode syncer scheduling state is changed. Actual storage pool data refresh occurs asynchronously.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `InternodeSyncer` and acknowledgement behavior. The comment notes it should only arrive as an acknowledgement-capable message from management. Tests should verify force flag setting and ack path.

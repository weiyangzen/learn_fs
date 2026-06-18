## sources/distributed-fs/beegfs/storage/source/net/message/control/SetChannelDirectMsgEx.h

### Purpose
`SetChannelDirectMsgEx.h` declares the storage-side handler for `SetChannelDirectMsg`.

### Important APIs, Types, And Functions
The class inherits `SetChannelDirectMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
The header has no data members. All behavior is implemented in the `.cpp`, where the socket's direct flag is changed.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on the common control message class and is instantiated by the storage message factory. Tests should confirm factory dispatch and virtual override behavior.

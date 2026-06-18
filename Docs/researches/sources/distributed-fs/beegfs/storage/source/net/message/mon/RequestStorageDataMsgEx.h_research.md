## sources/distributed-fs/beegfs/storage/source/net/message/mon/RequestStorageDataMsgEx.h

### Purpose
`RequestStorageDataMsgEx.h` declares the storage-side monitoring data handler.

### Important APIs, Types, And Functions
`RequestStorageDataMsgEx` derives from `RequestStorageDataMsg` and overrides `processIncoming(ResponseContext&)`. The header includes app, queue, storage info, messaging, response, and program dependencies needed by the implementation.

### Control Flow, State, And Persistence
The class itself has no extra state; it uses inherited request fields such as the last stats timestamp.

### Dependencies, Integration Points, Risks, And Test Signals
It is instantiated for `NETMSGTYPE_RequestStorageData`. Tests should confirm factory routing and that the response can be built with mocked storage target and stats state.

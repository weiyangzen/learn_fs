## sources/distributed-fs/beegfs/storage/source/net/message/control/SetChannelDirectMsgEx.cpp

### Purpose
`SetChannelDirectMsgEx.cpp` processes requests that mark a socket as direct. Direct channels indicate that subsequent messages are definitely processed on this storage server rather than forwarded.

### Important APIs, Types, And Functions
`SetChannelDirectMsgEx::processIncoming()` logs the integer value, calls `ctx.getSocket()->setIsDirect(getValue())`, updates `StorageOpCounter_SETCHANNELDIRECT`, and returns true without sending a response.

### Control Flow, State, And Persistence
The message mutates per-socket state only. No persistent storage is changed and no reply is required by this control message.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on the response context socket, `Program`, and node operation stats. Risks include clients setting the flag unexpectedly and relying on socket lifetime. Tests should verify socket flag mutation, no response, and stats update.

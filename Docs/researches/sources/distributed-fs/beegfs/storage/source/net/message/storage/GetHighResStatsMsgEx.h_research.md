## sources/distributed-fs/beegfs/storage/source/net/message/storage/GetHighResStatsMsgEx.h

### Purpose
`GetHighResStatsMsgEx.h` declares the storage-side high-resolution stats query handler.

### Important APIs, Types, And Functions
The class derives from `GetHighResStatsMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No additional state is declared; the base value acts as the last-stat timestamp.

### Dependencies, Integration Points, Risks, And Test Signals
It is factory-created for `NETMSGTYPE_GetHighResStats`. Tests should validate stats response construction through the implementation.

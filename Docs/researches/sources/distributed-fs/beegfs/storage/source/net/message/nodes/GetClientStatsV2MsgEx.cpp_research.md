## sources/distributed-fs/beegfs/storage/source/net/message/nodes/GetClientStatsV2MsgEx.cpp

### Purpose
`GetClientStatsV2MsgEx.cpp` returns per-client or per-user storage operation statistics for monitoring/control clients.

### Important APIs, Types, And Functions
`processIncoming()` obtains `StorageNodeOpStats`, checks `GETCLIENTSTATSMSG_FLAG_PERUSERSTATS`, calls `mapToUInt128Vec(getCookieIP(), GETCLIENTSTATSRESP_MAX_PAYLOAD_LEN, wantPerUserStats, &opStatsVec)`, and replies with `GetClientStatsV2RespMsg`.

### Control Flow, State, And Persistence
The handler is read-only. The cookie IP selects the continuation/filtering point for stats export, and payload length caps the vector.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `StorageNodeOpStats`, `UInt128` vectors, and common response messages. Risks include payload truncation/continuation correctness and large stats maps changing while exported. Tests should cover per-user flag, cookie continuation, empty stats, max payload boundary, and response serialization.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/MapTargetsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/MapTargetsMsgEx.cpp

Purpose: Implements the MapTargetsMsgEx server-side message extension: management handler that maps storage target IDs to a storage node and storage pool.

Important APIs/types/functions: Implemented entry points: bool MapTargetsMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: mutates target mapping state.

Dependencies and integration points: Direct includes: <common/net/message/nodes/MapTargetsRespMsg.h>, <common/toolkit/MessagingTk.h>, <common/toolkit/ZipIterator.h>, <program/Program.h>, "MapTargetsMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/MapTargetsMsgEx.cpp -->

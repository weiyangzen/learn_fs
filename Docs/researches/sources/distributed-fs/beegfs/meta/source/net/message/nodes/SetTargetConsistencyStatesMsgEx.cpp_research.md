<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.cpp

Purpose: Implements the SetTargetConsistencyStatesMsgEx server-side message extension: management handler that updates target consistency states in the appropriate target state store.

Important APIs/types/functions: Implemented entry points: bool SetTargetConsistencyStatesMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: mutates target consistency/reachability state.

Dependencies and integration points: Direct includes: <common/net/message/nodes/SetTargetConsistencyStatesRespMsg.h>, <common/nodes/TargetStateStore.h>, <common/toolkit/ZipIterator.h>, <program/Program.h>, "SetTargetConsistencyStatesMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.cpp -->

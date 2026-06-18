<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/GetHighResStatsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/GetHighResStatsMsgEx.cpp

Purpose: Implements the GetHighResStatsMsgEx server-side message extension: statistics query handler for high-resolution metadata server operation counters.

Important APIs/types/functions: Implemented entry points: bool GetHighResStatsMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/GetHighResStatsRespMsg.h>, <common/toolkit/MessagingTk.h>, "GetHighResStatsMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/GetHighResStatsMsgEx.cpp -->

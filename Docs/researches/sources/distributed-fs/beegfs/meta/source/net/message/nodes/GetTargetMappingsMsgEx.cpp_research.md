<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetTargetMappingsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetTargetMappingsMsgEx.cpp

Purpose: Implements the GetTargetMappingsMsgEx server-side message extension: target-to-storage-node mapping query handler.

Important APIs/types/functions: Implemented entry points: bool GetTargetMappingsMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/GetTargetMappingsRespMsg.h>, <common/toolkit/MessagingTk.h>, <program/Program.h>, "GetTargetMappingsMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetTargetMappingsMsgEx.cpp -->

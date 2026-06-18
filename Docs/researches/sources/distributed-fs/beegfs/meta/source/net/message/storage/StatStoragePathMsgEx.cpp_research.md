<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/StatStoragePathMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/StatStoragePathMsgEx.cpp

Purpose: Implements the StatStoragePathMsgEx server-side message extension: storage-path stat handler for local metadata storage capacity and inode availability.

Important APIs/types/functions: Implemented entry points: bool StatStoragePathMsgEx::processIncoming(ResponseContext& ctx); FhgfsOpsErr StatStoragePathMsgEx::statStoragePath(int64_t* outSizeTotal, int64_t* outSizeFree, int64_t* outInodesTotal, int64_t* outInodesFree).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/StatStoragePathRespMsg.h>, <common/toolkit/MessagingTk.h>, "StatStoragePathMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/StatStoragePathMsgEx.cpp -->

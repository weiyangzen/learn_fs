<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetClientStatsV2MsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetClientStatsV2MsgEx.h

Purpose: Declares the GetClientStatsV2MsgEx server-side message extension: client operation-statistics query handler that serializes metadata op counters into the v2 client stats response.

Important APIs/types/functions: Declarations/types: class GetClientStatsV2MsgEx : public GetClientStatsV2Msg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/nodes/GetClientStatsV2Msg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetClientStatsV2MsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetNodeCapacityPoolsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetNodeCapacityPoolsMsgEx.h

Purpose: Declares the GetNodeCapacityPoolsMsgEx server-side message extension: capacity-pool query handler for meta nodes, storage targets, and buddy groups.

Important APIs/types/functions: Declarations/types: class GetNodeCapacityPoolsMsgEx : public GetNodeCapacityPoolsMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/GetNodeCapacityPoolsMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetNodeCapacityPoolsMsgEx.h -->

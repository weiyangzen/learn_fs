<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/RemoveNodeMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/RemoveNodeMsgEx.h

Purpose: Declares the RemoveNodeMsgEx server-side message extension: management handler that removes a node from the appropriate metadata-side node store.

Important APIs/types/functions: Declarations/types: class RemoveNodeMsgEx : public RemoveNodeMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/RemoveNodeMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/RemoveNodeMsgEx.h -->

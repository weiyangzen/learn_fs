<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatRequestMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatRequestMsgEx.h

Purpose: Declares the HeartbeatRequestMsgEx server-side message extension: heartbeat request responder that builds this metadata server heartbeat from local node, NIC, port, and root information.

Important APIs/types/functions: Declarations/types: class HeartbeatRequestMsgEx : public HeartbeatRequestMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/HeartbeatRequestMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatRequestMsgEx.h -->

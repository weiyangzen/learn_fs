<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatMsgEx.h

Purpose: Declares the HeartbeatMsgEx server-side message extension: heartbeat receiver that updates node stores and metadata root ownership from incoming node announcements.

Important APIs/types/functions: Declarations/types: class HeartbeatMsgEx : public HeartbeatMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/HeartbeatMsg.h>.

Risks and test signals: root-directory special cases need explicit coverage because they bypass normal parent/name lookup Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatMsgEx.h -->

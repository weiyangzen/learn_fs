<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatMsgEx.cpp

Purpose: Implements the HeartbeatMsgEx server-side message extension: heartbeat receiver that updates node stores and metadata root ownership from incoming node announcements.

Important APIs/types/functions: Implemented entry points: bool HeartbeatMsgEx::processIncoming(ResponseContext& ctx); void HeartbeatMsgEx::processIncomingRoot().

Control flow: Control flow is a metadata-server message handler path driven by processIncoming() and helper functions in this file.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/sock/NetworkInterfaceCard.h>, <program/Program.h>, "HeartbeatMsgEx.h", <boost/lexical_cast.hpp>. Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: root-directory special cases need explicit coverage because they bypass normal parent/name lookup Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatMsgEx.cpp -->

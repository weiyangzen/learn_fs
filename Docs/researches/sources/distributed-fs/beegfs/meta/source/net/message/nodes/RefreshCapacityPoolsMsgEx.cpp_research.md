<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/RefreshCapacityPoolsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/RefreshCapacityPoolsMsgEx.cpp

Purpose: Implements the RefreshCapacityPoolsMsgEx server-side message extension: control handler that asks the internode syncer to refresh capacity-pool state.

Important APIs/types/functions: Implemented entry points: bool RefreshCapacityPoolsMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is a metadata-server message handler path driven by processIncoming() and helper functions in this file.

State and persistence behavior: sets syncer force flags that affect later background refresh/publication cycles.

Dependencies and integration points: Direct includes: <common/toolkit/MessagingTk.h>, <program/Program.h>, "RefreshCapacityPoolsMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/RefreshCapacityPoolsMsgEx.cpp -->

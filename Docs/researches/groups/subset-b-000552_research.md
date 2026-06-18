# subset-b-000552 grouped research

This grouped report covers BeeGFS metadata-server message extension files under `sources/distributed-fs/beegfs/meta/source/net/message`. Each section preserves the exact source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GenericDebugMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/GenericDebugMsgEx.cpp

Purpose: Implements the GenericDebugMsgEx server-side message extension: server-side generic debug command dispatcher for metadata nodes, including live diagnostics and guarded metadata inspection/mutation commands.

Important APIs/types/functions: Implemented entry points: bool GenericDebugMsgEx::processIncoming(ResponseContext& ctx); std::string GenericDebugMsgEx::processCommand(); std::string GenericDebugMsgEx::processOpListFileAppendLocks(std::istringstream& commandStream); std::string GenericDebugMsgEx::processOpListFileEntryLocks(std::istringstream& commandStream); std::string GenericDebugMsgEx::processOpListFileRangeLocks(std::istringstream& commandStream); std::string GenericDebugMsgEx::processOpListOpenFiles(std::istringstream& commandStream); std::string GenericDebugMsgEx::processOpReferenceStatistics(std::istringstream& commandStream); std::string GenericDebugMsgEx::processOpCacheStatistics(std::istringstream& commandStream); ...

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: sets syncer force flags that affect later background refresh/publication cycles; persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates; updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/net/message/nodes/GenericDebugRespMsg.h>, <common/net/msghelpers/MsgHelperGenericDebug.h>, <common/storage/quota/Quota.h>, <common/toolkit/MessagingTk.h>, <program/Program.h>, <session/SessionStore.h>, "GenericDebugMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: referenced metadata objects must be released on every error path wire compatibility depends on sending the exact response message type expected by management clients Because some commands mutate dentries or inode fields, operational exposure and argument validation are the main risks; tests should exercise malformed command strings and release every referenced inode or directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GenericDebugMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GenericDebugMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/GenericDebugMsgEx.h

Purpose: Declares the GenericDebugMsgEx server-side message extension: server-side generic debug command dispatcher for metadata nodes, including live diagnostics and guarded metadata inspection/mutation commands.

Important APIs/types/functions: Declarations/types: class GenericDebugMsgEx : public GenericDebugMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/GenericDebugMsg.h>, <common/Common.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers.

Risks and test signals: Because some commands mutate dentries or inode fields, operational exposure and argument validation are the main risks; tests should exercise malformed command strings and release every referenced inode or directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GenericDebugMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetClientStatsV2MsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetClientStatsV2MsgEx.cpp

Purpose: Implements the GetClientStatsV2MsgEx server-side message extension: client operation-statistics query handler that serializes metadata op counters into the v2 client stats response.

Important APIs/types/functions: Implemented entry points: bool GetClientStatsV2MsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: "GetClientStatsV2MsgEx.h", <program/Program.h>, <common/net/message/storage/GetHighResStatsRespMsg.h>, <common/toolkit/MessagingTk.h>, <common/nodes/OpCounter.h>, <nodes/MetaNodeOpStats.h>, <common/net/message/nodes/GetClientStatsV2RespMsg.h>. Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetClientStatsV2MsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetClientStatsV2MsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetClientStatsV2MsgEx.h

Purpose: Declares the GetClientStatsV2MsgEx server-side message extension: client operation-statistics query handler that serializes metadata op counters into the v2 client stats response.

Important APIs/types/functions: Declarations/types: class GetClientStatsV2MsgEx : public GetClientStatsV2Msg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/nodes/GetClientStatsV2Msg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetClientStatsV2MsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetNodeCapacityPoolsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetNodeCapacityPoolsMsgEx.cpp

Purpose: Implements the GetNodeCapacityPoolsMsgEx server-side message extension: capacity-pool query handler for meta nodes, storage targets, and buddy groups.

Important APIs/types/functions: Implemented entry points: bool GetNodeCapacityPoolsMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/GetNodeCapacityPoolsRespMsg.h>, <common/storage/StoragePool.h>, <program/Program.h>, "GetNodeCapacityPoolsMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetNodeCapacityPoolsMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetNodeCapacityPoolsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetNodeCapacityPoolsMsgEx.h

Purpose: Declares the GetNodeCapacityPoolsMsgEx server-side message extension: capacity-pool query handler for meta nodes, storage targets, and buddy groups.

Important APIs/types/functions: Declarations/types: class GetNodeCapacityPoolsMsgEx : public GetNodeCapacityPoolsMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/GetNodeCapacityPoolsMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetNodeCapacityPoolsMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetNodesMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetNodesMsgEx.cpp

Purpose: Implements the GetNodesMsgEx server-side message extension: node-list query handler that returns the selected node store plus metadata root identity.

Important APIs/types/functions: Implemented entry points: bool GetNodesMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/GetNodesRespMsg.h>, <program/Program.h>, "GetNodesMsgEx.h", <boost/lexical_cast.hpp>. Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: root-directory special cases need explicit coverage because they bypass normal parent/name lookup wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetNodesMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetNodesMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetNodesMsgEx.h

Purpose: Declares the GetNodesMsgEx server-side message extension: node-list query handler that returns the selected node store plus metadata root identity.

Important APIs/types/functions: Declarations/types: class GetNodesMsgEx : public GetNodesMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/GetNodesMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetNodesMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetTargetMappingsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetTargetMappingsMsgEx.cpp

Purpose: Implements the GetTargetMappingsMsgEx server-side message extension: target-to-storage-node mapping query handler.

Important APIs/types/functions: Implemented entry points: bool GetTargetMappingsMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/GetTargetMappingsRespMsg.h>, <common/toolkit/MessagingTk.h>, <program/Program.h>, "GetTargetMappingsMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetTargetMappingsMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetTargetMappingsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetTargetMappingsMsgEx.h

Purpose: Declares the GetTargetMappingsMsgEx server-side message extension: target-to-storage-node mapping query handler.

Important APIs/types/functions: Declarations/types: class GetTargetMappingsMsgEx : public GetTargetMappingsMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/GetTargetMappingsMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetTargetMappingsMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatMsgEx.cpp

Purpose: Implements the HeartbeatMsgEx server-side message extension: heartbeat receiver that updates node stores and metadata root ownership from incoming node announcements.

Important APIs/types/functions: Implemented entry points: bool HeartbeatMsgEx::processIncoming(ResponseContext& ctx); void HeartbeatMsgEx::processIncomingRoot().

Control flow: Control flow is a metadata-server message handler path driven by processIncoming() and helper functions in this file.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/sock/NetworkInterfaceCard.h>, <program/Program.h>, "HeartbeatMsgEx.h", <boost/lexical_cast.hpp>. Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: root-directory special cases need explicit coverage because they bypass normal parent/name lookup Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatMsgEx.h

Purpose: Declares the HeartbeatMsgEx server-side message extension: heartbeat receiver that updates node stores and metadata root ownership from incoming node announcements.

Important APIs/types/functions: Declarations/types: class HeartbeatMsgEx : public HeartbeatMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/HeartbeatMsg.h>.

Risks and test signals: root-directory special cases need explicit coverage because they bypass normal parent/name lookup Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatRequestMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatRequestMsgEx.cpp

Purpose: Implements the HeartbeatRequestMsgEx server-side message extension: heartbeat request responder that builds this metadata server heartbeat from local node, NIC, port, and root information.

Important APIs/types/functions: Implemented entry points: bool HeartbeatRequestMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/HeartbeatMsg.h>, <common/toolkit/MessagingTk.h>, <program/Program.h>, "HeartbeatRequestMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: root-directory special cases need explicit coverage because they bypass normal parent/name lookup wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatRequestMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatRequestMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatRequestMsgEx.h

Purpose: Declares the HeartbeatRequestMsgEx server-side message extension: heartbeat request responder that builds this metadata server heartbeat from local node, NIC, port, and root information.

Important APIs/types/functions: Declarations/types: class HeartbeatRequestMsgEx : public HeartbeatRequestMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/HeartbeatRequestMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/HeartbeatRequestMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/MapTargetsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/MapTargetsMsgEx.cpp

Purpose: Implements the MapTargetsMsgEx server-side message extension: management handler that maps storage target IDs to a storage node and storage pool.

Important APIs/types/functions: Implemented entry points: bool MapTargetsMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: mutates target mapping state.

Dependencies and integration points: Direct includes: <common/net/message/nodes/MapTargetsRespMsg.h>, <common/toolkit/MessagingTk.h>, <common/toolkit/ZipIterator.h>, <program/Program.h>, "MapTargetsMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/MapTargetsMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/MapTargetsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/MapTargetsMsgEx.h

Purpose: Declares the MapTargetsMsgEx server-side message extension: management handler that maps storage target IDs to a storage node and storage pool.

Important APIs/types/functions: Declarations/types: class MapTargetsMsgEx : public MapTargetsMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/MapTargetsMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/MapTargetsMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/PublishCapacitiesMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/PublishCapacitiesMsgEx.cpp

Purpose: Implements the PublishCapacitiesMsgEx server-side message extension: control handler that forces an internode capacity publication cycle.

Important APIs/types/functions: Implemented entry points: bool PublishCapacitiesMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is a metadata-server message handler path driven by processIncoming() and helper functions in this file.

State and persistence behavior: sets syncer force flags that affect later background refresh/publication cycles.

Dependencies and integration points: Direct includes: <common/toolkit/MessagingTk.h>, <program/Program.h>, "PublishCapacitiesMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/PublishCapacitiesMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/PublishCapacitiesMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/PublishCapacitiesMsgEx.h

Purpose: Declares the PublishCapacitiesMsgEx server-side message extension: control handler that forces an internode capacity publication cycle.

Important APIs/types/functions: Declarations/types: class PublishCapacitiesMsgEx : public PublishCapacitiesMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/PublishCapacitiesMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/PublishCapacitiesMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/RefreshCapacityPoolsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/RefreshCapacityPoolsMsgEx.cpp

Purpose: Implements the RefreshCapacityPoolsMsgEx server-side message extension: control handler that asks the internode syncer to refresh capacity-pool state.

Important APIs/types/functions: Implemented entry points: bool RefreshCapacityPoolsMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is a metadata-server message handler path driven by processIncoming() and helper functions in this file.

State and persistence behavior: sets syncer force flags that affect later background refresh/publication cycles.

Dependencies and integration points: Direct includes: <common/toolkit/MessagingTk.h>, <program/Program.h>, "RefreshCapacityPoolsMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/RefreshCapacityPoolsMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/RefreshCapacityPoolsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/RefreshCapacityPoolsMsgEx.h

Purpose: Declares the RefreshCapacityPoolsMsgEx server-side message extension: control handler that asks the internode syncer to refresh capacity-pool state.

Important APIs/types/functions: Declarations/types: class RefreshCapacityPoolsMsgEx : public RefreshCapacityPoolsMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/RefreshCapacityPoolsMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/RefreshCapacityPoolsMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/RefreshTargetStatesMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/RefreshTargetStatesMsgEx.cpp

Purpose: Implements the RefreshTargetStatesMsgEx server-side message extension: control handler that asks the internode syncer to refresh target reachability and consistency state.

Important APIs/types/functions: Implemented entry points: bool RefreshTargetStatesMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is a metadata-server message handler path driven by processIncoming() and helper functions in this file.

State and persistence behavior: sets syncer force flags that affect later background refresh/publication cycles.

Dependencies and integration points: Direct includes: <common/toolkit/MessagingTk.h>, <program/Program.h>, "RefreshTargetStatesMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/RefreshTargetStatesMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/RefreshTargetStatesMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/RefreshTargetStatesMsgEx.h

Purpose: Declares the RefreshTargetStatesMsgEx server-side message extension: control handler that asks the internode syncer to refresh target reachability and consistency state.

Important APIs/types/functions: Declarations/types: class RefreshTargetStatesMsgEx : public RefreshTargetStatesMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/RefreshTargetStatesMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/RefreshTargetStatesMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/RemoveNodeMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/RemoveNodeMsgEx.cpp

Purpose: Implements the RemoveNodeMsgEx server-side message extension: management handler that removes a node from the appropriate metadata-side node store.

Important APIs/types/functions: Implemented entry points: bool RemoveNodeMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: mutates node-store membership.

Dependencies and integration points: Direct includes: <common/net/message/nodes/RemoveNodeRespMsg.h>, <common/toolkit/MessagingTk.h>, <program/Program.h>, "RemoveNodeMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/RemoveNodeMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/RemoveNodeMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/RemoveNodeMsgEx.h

Purpose: Declares the RemoveNodeMsgEx server-side message extension: management handler that removes a node from the appropriate metadata-side node store.

Important APIs/types/functions: Declarations/types: class RemoveNodeMsgEx : public RemoveNodeMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/RemoveNodeMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/RemoveNodeMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.cpp

Purpose: Implements the SetMirrorBuddyGroupMsgEx server-side message extension: management handler that registers or updates mirror buddy groups.

Important APIs/types/functions: Implemented entry points: bool SetMirrorBuddyGroupMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/SetMirrorBuddyGroupRespMsg.h>, <common/nodes/MirrorBuddyGroupMapper.h>, <common/toolkit/MessagingTk.h>, <program/Program.h>, "SetMirrorBuddyGroupMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.h

Purpose: Declares the SetMirrorBuddyGroupMsgEx server-side message extension: management handler that registers or updates mirror buddy groups.

Important APIs/types/functions: Declarations/types: class SetMirrorBuddyGroupMsgEx : public SetMirrorBuddyGroupMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/SetMirrorBuddyGroupMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.cpp

Purpose: Implements the SetTargetConsistencyStatesMsgEx server-side message extension: management handler that updates target consistency states in the appropriate target state store.

Important APIs/types/functions: Implemented entry points: bool SetTargetConsistencyStatesMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: mutates target consistency/reachability state.

Dependencies and integration points: Direct includes: <common/net/message/nodes/SetTargetConsistencyStatesRespMsg.h>, <common/nodes/TargetStateStore.h>, <common/toolkit/ZipIterator.h>, <program/Program.h>, "SetTargetConsistencyStatesMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.h

Purpose: Declares the SetTargetConsistencyStatesMsgEx server-side message extension: management handler that updates target consistency states in the appropriate target state store.

Important APIs/types/functions: Declarations/types: class SetTargetConsistencyStatesMsgEx : public SetTargetConsistencyStatesMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: mutates target consistency/reachability state.

Dependencies and integration points: Direct includes: <common/net/message/nodes/SetTargetConsistencyStatesMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/storagepools/RefreshStoragePoolsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/storagepools/RefreshStoragePoolsMsgEx.cpp

Purpose: Implements the RefreshStoragePoolsMsgEx server-side message extension: management handler that asks the internode syncer to refresh storage-pool definitions.

Important APIs/types/functions: Implemented entry points: bool RefreshStoragePoolsMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is a metadata-server message handler path driven by processIncoming() and helper functions in this file.

State and persistence behavior: sets syncer force flags that affect later background refresh/publication cycles.

Dependencies and integration points: Direct includes: "RefreshStoragePoolsMsgEx.h", <program/Program.h>. Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/storagepools/RefreshStoragePoolsMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/storagepools/RefreshStoragePoolsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/storagepools/RefreshStoragePoolsMsgEx.h

Purpose: Declares the RefreshStoragePoolsMsgEx server-side message extension: management handler that asks the internode syncer to refresh storage-pool definitions.

Important APIs/types/functions: Declarations/types: class RefreshStoragePoolsMsgEx : public RefreshStoragePoolsMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/storagepools/RefreshStoragePoolsMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/storagepools/RefreshStoragePoolsMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/AckNotifyMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/AckNotifyMsgEx.h

Purpose: Declares the AckNotifiyMsgEx server-side message extension: mirrored acknowledgement-notification wrapper; the spelling follows the BeeGFS message class name.

Important APIs/types/functions: Declarations/types: class AckNotifiyMsgEx : public MirroredMessage<AckNotifiyMsg, std::tuple<>>; typedef ErrorCodeResponseState< AckNotifiyRespMsg, NETMSGTYPE_AckNotify> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/net/message/session/AckNotifyMsg.h>, <common/net/message/session/AckNotifyRespMsg.h>, <net/message/MirroredMessage.h>, <session/MirrorMessageResponseState.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/AckNotifyMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/BumpFileVersionMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/BumpFileVersionMsgEx.cpp

Purpose: Implements the BumpFileVersionMsgEx server-side message extension: mirrored session handler that increments a file inode version and optionally emits file-event context.

Important APIs/types/functions: Implemented entry points: bool BumpFileVersionMsgEx::processIncoming(ResponseContext& ctx); FileIDLock BumpFileVersionMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> BumpFileVersionMsgEx::executeLocally( ResponseContext& ctx, bool isSecondary); void BumpFileVersionMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: "BumpFileVersionMsgEx.h", <components/FileEventLogger.h>, <program/Program.h>. Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/BumpFileVersionMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/BumpFileVersionMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/BumpFileVersionMsgEx.h

Purpose: Declares the BumpFileVersionMsgEx server-side message extension: mirrored session handler that increments a file inode version and optionally emits file-event context.

Important APIs/types/functions: Declarations/types: class BumpFileVersionMsgEx : public MirroredMessage<BumpFileVersionMsg, FileIDLock>; typedef ErrorCodeResponseState<BumpFileVersionRespMsg, NETMSGTYPE_BumpFileVersion> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/net/message/session/BumpFileVersionMsg.h>, <common/net/message/session/BumpFileVersionRespMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/BumpFileVersionMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/GetFileVersionMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/GetFileVersionMsgEx.cpp

Purpose: Implements the GetFileVersionMsgEx server-side message extension: mirrored read handler that returns the current version counter for a file inode.

Important APIs/types/functions: Implemented entry points: bool GetFileVersionMsgEx::processIncoming(ResponseContext& ctx); FileIDLock GetFileVersionMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> GetFileVersionMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: "GetFileVersionMsgEx.h", <program/Program.h>. Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/GetFileVersionMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/GetFileVersionMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/GetFileVersionMsgEx.h

Purpose: Declares the GetFileVersionMsgEx server-side message extension: mirrored read handler that returns the current version counter for a file inode.

Important APIs/types/functions: Declarations/types: class GetFileVersionMsgResponseState : public MirroredMessageResponseState; class GetFileVersionMsgEx : public MirroredMessage<GetFileVersionMsg, FileIDLock>; typedef GetFileVersionMsgResponseState ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/net/message/session/GetFileVersionMsg.h>, <common/net/message/session/GetFileVersionRespMsg.h>, <common/net/message/session/GetFileVersionRespMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/GetFileVersionMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockAppendMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockAppendMsgEx.cpp

Purpose: Implements the FLockAppendMsgEx server-side message extension: mirrored append-lock handler for session-scoped file append locks.

Important APIs/types/functions: Implemented entry points: bool FLockAppendMsgEx::processIncoming(ResponseContext& ctx); FileIDLock FLockAppendMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> FLockAppendMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void FLockAppendMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/net/message/session/locking/FLockAppendRespMsg.h>, <common/toolkit/MessagingTk.h>, <common/toolkit/SessionTk.h>, <net/msghelpers/MsgHelperLocking.h>, <program/Program.h>, <session/SessionStore.h>, <storage/MetaStore.h>, "FLockAppendMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockAppendMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockAppendMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockAppendMsgEx.h

Purpose: Declares the FLockAppendMsgEx server-side message extension: mirrored append-lock handler for session-scoped file append locks.

Important APIs/types/functions: Declarations/types: class FLockAppendMsgEx : public MirroredMessage<FLockAppendMsg, FileIDLock>; typedef ErrorCodeResponseState<FLockAppendRespMsg, NETMSGTYPE_FLockAppend> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/net/message/session/locking/FLockAppendMsg.h>, <common/net/message/session/locking/FLockAppendRespMsg.h>, <net/message/MirroredMessage.h>, <common/storage/StorageErrors.h>, <storage/FileInode.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockAppendMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockEntryMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockEntryMsgEx.cpp

Purpose: Implements the FLockEntryMsgEx server-side message extension: mirrored whole-entry flock handler for session-scoped file locks.

Important APIs/types/functions: Implemented entry points: bool FLockEntryMsgEx::processIncoming(ResponseContext& ctx); FileIDLock FLockEntryMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> FLockEntryMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void FLockEntryMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/net/message/session/locking/FLockEntryRespMsg.h>, <common/toolkit/MessagingTk.h>, <common/toolkit/SessionTk.h>, <net/msghelpers/MsgHelperLocking.h>, <program/Program.h>, <session/SessionStore.h>, <storage/MetaStore.h>, "FLockEntryMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockEntryMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockEntryMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockEntryMsgEx.h

Purpose: Declares the FLockEntryMsgEx server-side message extension: mirrored whole-entry flock handler for session-scoped file locks.

Important APIs/types/functions: Declarations/types: class FLockEntryMsgEx : public MirroredMessage<FLockEntryMsg, FileIDLock>; typedef ErrorCodeResponseState<FLockEntryRespMsg, NETMSGTYPE_FLockEntry> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/net/message/session/locking/FLockEntryMsg.h>, <common/net/message/session/locking/FLockEntryRespMsg.h>, <common/storage/StorageErrors.h>, <net/message/MirroredMessage.h>, <storage/FileInode.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockEntryMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockRangeMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockRangeMsgEx.cpp

Purpose: Implements the FLockRangeMsgEx server-side message extension: mirrored byte-range flock handler for session-scoped range locks.

Important APIs/types/functions: Implemented entry points: bool FLockRangeMsgEx::processIncoming(ResponseContext& ctx); FileIDLock FLockRangeMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> FLockRangeMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void FLockRangeMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/net/message/session/locking/FLockRangeRespMsg.h>, <common/toolkit/MessagingTk.h>, <common/toolkit/SessionTk.h>, <net/msghelpers/MsgHelperLocking.h>, <program/Program.h>, <session/SessionStore.h>, <storage/MetaStore.h>, "FLockRangeMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockRangeMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockRangeMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockRangeMsgEx.h

Purpose: Declares the FLockRangeMsgEx server-side message extension: mirrored byte-range flock handler for session-scoped range locks.

Important APIs/types/functions: Declarations/types: class FLockRangeMsgEx : public MirroredMessage<FLockRangeMsg, FileIDLock>; typedef ErrorCodeResponseState<FLockRangeRespMsg, NETMSGTYPE_FLockRange> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/net/message/session/locking/FLockRangeMsg.h>, <common/net/message/session/locking/FLockRangeRespMsg.h>, <common/storage/StorageErrors.h>, <net/message/MirroredMessage.h>, <storage/FileInode.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockRangeMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/opening/CloseFileMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/opening/CloseFileMsgEx.cpp

Purpose: Implements the CloseFileMsgEx server-side message extension: mirrored close-file handler that removes a session file, updates inode state, and may complete deferred unlink/disposal work.

Important APIs/types/functions: Implemented entry points: FileIDLock CloseFileMsgEx::lock(EntryLockStore& store); bool CloseFileMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> CloseFileMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); std::unique_ptr<CloseFileMsgEx::ResponseState> CloseFileMsgEx::closeFilePrimary( ResponseContext& ctx); std::unique_ptr<CloseFileMsgEx::ResponseState> CloseFileMsgEx::closeFileSecondary( ResponseContext& ctx); FhgfsOpsErr CloseFileMsgEx::closeFileAfterEarlyResponse(MetaFileHandle inode, unsigned accessFlags, bool* outUnlinkDisposalFile, unsigned& outNumHardlinks, bool& outLastWriterClosed); void CloseFileMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h>, <common/net/message/control/GenericResponseMsg.h>, <common/net/message/session/opening/CloseFileRespMsg.h>, <common/toolkit/MessagingTk.h>, <common/toolkit/SessionTk.h>, <components/FileEventLogger.h>, <net/msghelpers/MsgHelperClose.h>, <net/msghelpers/MsgHelperLocking.h>, <program/Program.h>, <session/EntryLock.h>, ... Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary The early-response close path makes ordering important: session removal, write counters, inode persistence, disposal unlink, and secondary mirroring must agree even if clients disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/opening/CloseFileMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/opening/CloseFileMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/opening/CloseFileMsgEx.h

Purpose: Declares the CloseFileMsgEx server-side message extension: mirrored close-file handler that removes a session file, updates inode state, and may complete deferred unlink/disposal work.

Important APIs/types/functions: Declarations/types: class CloseFileMsgEx : public MirroredMessage<CloseFileMsg, FileIDLock>; typedef ErrorCodeResponseState<CloseFileRespMsg, NETMSGTYPE_CloseFile> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/session/opening/CloseFileMsg.h>, <common/net/message/session/opening/CloseFileRespMsg.h>, <net/message/MirroredMessage.h>, <session/EntryLock.h>, <storage/FileInode.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary The early-response close path makes ordering important: session removal, write counters, inode persistence, disposal unlink, and secondary mirroring must agree even if clients disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/opening/CloseFileMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/opening/OpenFileMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/opening/OpenFileMsgEx.cpp

Purpose: Implements the OpenFileMsgEx server-side message extension: mirrored open-file handler that references metadata, checks access, and registers the open file in the session store.

Important APIs/types/functions: Implemented entry points: FileIDLock OpenFileMsgEx::lock(EntryLockStore& store); bool OpenFileMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> OpenFileMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void OpenFileMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/net/message/control/GenericResponseMsg.h>, <common/net/message/session/opening/OpenFileRespMsg.h>, <common/toolkit/SessionTk.h>, <common/storage/striping/Raid0Pattern.h>, <components/FileEventLogger.h>, <net/msghelpers/MsgHelperOpen.h>, <program/Program.h>, <session/EntryLock.h>, <session/SessionStore.h>, "OpenFileMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/opening/OpenFileMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/opening/OpenFileMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/opening/OpenFileMsgEx.h

Purpose: Declares the OpenFileMsgEx server-side message extension: mirrored open-file handler that references metadata, checks access, and registers the open file in the session store.

Important APIs/types/functions: Declarations/types: class OpenFileResponseState : public MirroredMessageResponseState; class OpenFileMsgEx : public MirroredMessage<OpenFileMsg, FileIDLock>; typedef OpenFileResponseState ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/session/opening/OpenFileMsg.h>, <common/net/message/session/opening/OpenFileRespMsg.h>, <storage/DirInode.h>, <storage/FileInode.h>, <net/message/MirroredMessage.h>, <session/EntryLock.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/opening/OpenFileMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/GetHighResStatsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/GetHighResStatsMsgEx.cpp

Purpose: Implements the GetHighResStatsMsgEx server-side message extension: statistics query handler for high-resolution metadata server operation counters.

Important APIs/types/functions: Implemented entry points: bool GetHighResStatsMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/GetHighResStatsRespMsg.h>, <common/toolkit/MessagingTk.h>, "GetHighResStatsMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/GetHighResStatsMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/GetHighResStatsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/GetHighResStatsMsgEx.h

Purpose: Declares the GetHighResStatsMsgEx server-side message extension: statistics query handler for high-resolution metadata server operation counters.

Important APIs/types/functions: Declarations/types: class GetHighResStatsMsgEx : public GetHighResStatsMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/GetHighResStatsMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/GetHighResStatsMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/StatStoragePathMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/StatStoragePathMsgEx.cpp

Purpose: Implements the StatStoragePathMsgEx server-side message extension: storage-path stat handler for local metadata storage capacity and inode availability.

Important APIs/types/functions: Implemented entry points: bool StatStoragePathMsgEx::processIncoming(ResponseContext& ctx); FhgfsOpsErr StatStoragePathMsgEx::statStoragePath(int64_t* outSizeTotal, int64_t* outSizeFree, int64_t* outInodesTotal, int64_t* outInodesFree).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/StatStoragePathRespMsg.h>, <common/toolkit/MessagingTk.h>, "StatStoragePathMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/StatStoragePathMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/StatStoragePathMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/StatStoragePathMsgEx.h

Purpose: Declares the StatStoragePathMsgEx server-side message extension: storage-path stat handler for local metadata storage capacity and inode availability.

Important APIs/types/functions: Declarations/types: class StatStoragePathMsgEx : public StatStoragePathMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/StatStoragePathMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/StatStoragePathMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/TruncFileMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/TruncFileMsgEx.cpp

Purpose: Implements the TruncFileMsgEx server-side message extension: mirrored truncate handler that updates metadata and delegates chunk truncation through helper logic.

Important APIs/types/functions: Implemented entry points: FileIDLock TruncFileMsgEx::lock(EntryLockStore& store); bool TruncFileMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> TruncFileMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void TruncFileMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <common/net/message/control/GenericResponseMsg.h>, <common/net/message/storage/TruncFileRespMsg.h>, <common/toolkit/MessagingTk.h>, <components/FileEventLogger.h>, <net/msghelpers/MsgHelperTrunc.h>, "TruncFileMsgEx.h", <program/Program.h>. Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/TruncFileMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/TruncFileMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/TruncFileMsgEx.h

Purpose: Declares the TruncFileMsgEx server-side message extension: mirrored truncate handler that updates metadata and delegates chunk truncation through helper logic.

Important APIs/types/functions: Declarations/types: class TruncFileMsgEx : public MirroredMessage<TruncFileMsg, FileIDLock>; typedef ErrorCodeResponseState<TruncFileRespMsg, NETMSGTYPE_TruncFile> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/storage/TruncFileMsg.h>, <common/net/message/storage/TruncFileRespMsg.h>, <net/message/MirroredMessage.h>, <storage/MetaStore.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/TruncFileMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetEntryInfoMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetEntryInfoMsgEx.cpp

Purpose: Implements the GetEntryInfoMsgEx server-side message extension: mirrored entry-info query handler returning stripe pattern, path info, remote storage target, and session counts.

Important APIs/types/functions: Implemented entry points: bool GetEntryInfoMsgEx::processIncoming(ResponseContext& ctx); FileIDLock GetEntryInfoMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> GetEntryInfoMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); FhgfsOpsErr GetEntryInfoMsgEx::getInfo(EntryInfo* entryInfo, StripePattern** outPattern, PathInfo* outPathInfo, RemoteStorageTarget* outRstInfo, uint32_t& outNumReadSessions, uint32_t& outNumWriteSessions, uint8_t& outDataState); FhgfsOpsErr GetEntryInfoMsgEx::getRootInfo(StripePattern** outPattern, RemoteStorageTarget* outRstInfo).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <common/net/message/storage/attribs/GetEntryInfoRespMsg.h>, <common/storage/striping/Raid0Pattern.h>, <common/toolkit/MessagingTk.h>, <program/Program.h>, <storage/MetaStore.h>, "GetEntryInfoMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path root-directory special cases need explicit coverage because they bypass normal parent/name lookup Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetEntryInfoMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetEntryInfoMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetEntryInfoMsgEx.h

Purpose: Declares the GetEntryInfoMsgEx server-side message extension: mirrored entry-info query handler returning stripe pattern, path info, remote storage target, and session counts.

Important APIs/types/functions: Declarations/types: class GetEntryInfoMsgResponseState : public MirroredMessageResponseState; class GetEntryInfoMsgEx : public MirroredMessage<GetEntryInfoMsg, FileIDLock>; typedef GetEntryInfoMsgResponseState ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <storage/DirInode.h>, <common/storage/StorageErrors.h>, <common/net/message/storage/attribs/GetEntryInfoMsg.h>, <common/net/message/storage/attribs/GetEntryInfoRespMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary root-directory special cases need explicit coverage because they bypass normal parent/name lookup Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetEntryInfoMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetXAttrMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetXAttrMsgEx.cpp

Purpose: Implements the GetXAttrMsgEx server-side message extension: mirrored extended-attribute read handler.

Important APIs/types/functions: Implemented entry points: bool GetXAttrMsgEx::processIncoming(ResponseContext& ctx); FileIDLock GetXAttrMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> GetXAttrMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/attribs/GetXAttrRespMsg.h>, <net/msghelpers/MsgHelperXAttr.h>, "GetXAttrMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetXAttrMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetXAttrMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetXAttrMsgEx.h

Purpose: Declares the GetXAttrMsgEx server-side message extension: mirrored extended-attribute read handler.

Important APIs/types/functions: Declarations/types: class GetXAttrMsgResponseState : public MirroredMessageResponseState; class GetXAttrMsgEx : public MirroredMessage<GetXAttrMsg, FileIDLock>; typedef GetXAttrMsgResponseState ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/storage/attribs/GetXAttrMsg.h>, <common/net/message/storage/attribs/GetXAttrRespMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetXAttrMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/ListXAttrMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/ListXAttrMsgEx.cpp

Purpose: Implements the ListXAttrMsgEx server-side message extension: mirrored extended-attribute listing handler.

Important APIs/types/functions: Implemented entry points: bool ListXAttrMsgEx::processIncoming(ResponseContext& ctx); FileIDLock ListXAttrMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> ListXAttrMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/attribs/ListXAttrRespMsg.h>, <net/msghelpers/MsgHelperXAttr.h>, "ListXAttrMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/ListXAttrMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/ListXAttrMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/ListXAttrMsgEx.h

Purpose: Declares the ListXAttrMsgEx server-side message extension: mirrored extended-attribute listing handler.

Important APIs/types/functions: Declarations/types: class ListXAttrMsgResponseState : public MirroredMessageResponseState; class ListXAttrMsgEx : public MirroredMessage<ListXAttrMsg, FileIDLock>; typedef ListXAttrMsgResponseState ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/storage/attribs/ListXAttrMsg.h>, <common/net/message/storage/attribs/ListXAttrRespMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/ListXAttrMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/RefreshEntryInfoMsg.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/RefreshEntryInfoMsg.cpp

Purpose: Implements the RefreshEntryInfoMsg server-side message extension: implementation for the BeeGFS metadata-server RefreshEntryInfoMsg network message extension.

Important APIs/types/functions: Implemented entry points: bool RefreshEntryInfoMsgEx::processIncoming(ResponseContext& ctx); std::tuple<FileIDLock, FileIDLock> RefreshEntryInfoMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> RefreshEntryInfoMsgEx::executeLocally( ResponseContext& ctx, bool isSecondary); FhgfsOpsErr RefreshEntryInfoMsgEx::refreshInfoRec(); FhgfsOpsErr RefreshEntryInfoMsgEx::refreshInfoRoot(); void RefreshEntryInfoMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/storage/attribs/RefreshEntryInfoRespMsg.h>, <common/storage/striping/Raid0Pattern.h>, <common/toolkit/MessagingTk.h>, <net/msghelpers/MsgHelperStat.h>, <common/storage/EntryInfo.h>, <program/Program.h>, <session/EntryLock.h>, <storage/MetaStore.h>, "RefreshEntryInfoMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path root-directory special cases need explicit coverage because they bypass normal parent/name lookup Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/RefreshEntryInfoMsg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/RefreshEntryInfoMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/RefreshEntryInfoMsgEx.h

Purpose: Declares the RefreshEntryInfoMsgEx server-side message extension: mirrored handler that refreshes entry information from the authoritative local inode or root metadata.

Important APIs/types/functions: Declarations/types: class RefreshEntryInfoMsgEx : public MirroredMessage<RefreshEntryInfoMsg,; typedef ErrorCodeResponseState<RefreshEntryInfoRespMsg, NETMSGTYPE_RefreshEntryInfo> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <storage/DirInode.h>, <common/storage/StorageErrors.h>, <common/net/message/storage/attribs/RefreshEntryInfoMsg.h>, <common/net/message/storage/attribs/RefreshEntryInfoRespMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary root-directory special cases need explicit coverage because they bypass normal parent/name lookup Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/RefreshEntryInfoMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/RemoveXAttrMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/RemoveXAttrMsgEx.cpp

Purpose: Implements the RemoveXAttrMsgEx server-side message extension: mirrored extended-attribute removal handler.

Important APIs/types/functions: Implemented entry points: bool RemoveXAttrMsgEx::processIncoming(ResponseContext& ctx); std::tuple<FileIDLock, FileIDLock> RemoveXAttrMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> RemoveXAttrMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void RemoveXAttrMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/attribs/RemoveXAttrRespMsg.h>, <net/msghelpers/MsgHelperXAttr.h>, <session/EntryLock.h>, "RemoveXAttrMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/RemoveXAttrMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/RemoveXAttrMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/RemoveXAttrMsgEx.h

Purpose: Declares the RemoveXAttrMsgEx server-side message extension: mirrored extended-attribute removal handler.

Important APIs/types/functions: Declarations/types: class RemoveXAttrMsgEx : public MirroredMessage<RemoveXAttrMsg, std::tuple<FileIDLock, FileIDLock>>; typedef ErrorCodeResponseState<RemoveXAttrRespMsg, NETMSGTYPE_RemoveXAttr> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/storage/attribs/RemoveXAttrMsg.h>, <common/net/message/storage/attribs/RemoveXAttrRespMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/RemoveXAttrMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetAttrMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetAttrMsgEx.cpp

Purpose: Implements the SetAttrMsgEx server-side message extension: mirrored setattr handler for metadata stat fields and optional chunk-file attribute updates.

Important APIs/types/functions: Implemented entry points: bool SetAttrMsgEx::processIncoming(ResponseContext& ctx); std::tuple<FileIDLock, FileIDLock> SetAttrMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> SetAttrMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void SetAttrMsgEx::forwardToSecondary(ResponseContext& ctx); FhgfsOpsErr SetAttrMsgEx::setAttrRoot(); FhgfsOpsErr SetAttrMsgEx::setChunkFileAttribs(FileInode& file, bool requestDynamicAttribs); FhgfsOpsErr SetAttrMsgEx::setChunkFileAttribsSequential(FileInode& inode, bool requestDynamicAttribs); FhgfsOpsErr SetAttrMsgEx::setChunkFileAttribsParallel(FileInode& inode, bool requestDynamicAttribs).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h>, <common/net/message/control/GenericResponseMsg.h>, <common/net/message/storage/attribs/SetAttrRespMsg.h>, <common/net/message/storage/attribs/SetLocalAttrMsg.h>, <common/net/message/storage/attribs/SetLocalAttrRespMsg.h>, <common/toolkit/MessagingTk.h>, <components/FileEventLogger.h>, <components/worker/SetChunkFileAttribsWork.h>, <program/Program.h>, <session/EntryLock.h>, ... Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path root-directory special cases need explicit coverage because they bypass normal parent/name lookup Chunk attribute updates can run sequentially or in parallel; dynamic-attribute refresh failures must not leave stat data inconsistent with storage targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetAttrMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetAttrMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetAttrMsgEx.h

Purpose: Declares the SetAttrMsgEx server-side message extension: mirrored setattr handler for metadata stat fields and optional chunk-file attribute updates.

Important APIs/types/functions: Declarations/types: class SetAttrMsgEx : public MirroredMessage<SetAttrMsg, std::tuple<FileIDLock, FileIDLock>>; typedef ErrorCodeResponseState<SetAttrRespMsg, NETMSGTYPE_SetAttr> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <storage/MetaStore.h>, <common/storage/StorageErrors.h>, <common/net/message/storage/attribs/SetAttrMsg.h>, <common/net/message/storage/attribs/SetAttrRespMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary root-directory special cases need explicit coverage because they bypass normal parent/name lookup Chunk attribute updates can run sequentially or in parallel; dynamic-attribute refresh failures must not leave stat data inconsistent with storage targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetAttrMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetDirPatternMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetDirPatternMsgEx.cpp

Purpose: Implements the SetDirPatternMsgEx server-side message extension: mirrored directory stripe-pattern update handler.

Important APIs/types/functions: Implemented entry points: bool SetDirPatternMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> SetDirPatternMsgEx::executeLocally( ResponseContext& ctx, bool isSecondary); void SetDirPatternMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <common/net/message/storage/attribs/SetDirPatternRespMsg.h>, <common/storage/striping/Raid0Pattern.h>, <common/toolkit/MessagingTk.h>, <program/Program.h>, <session/EntryLock.h>, <storage/DirInode.h>, <storage/MetaStore.h>, "SetDirPatternMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path root-directory special cases need explicit coverage because they bypass normal parent/name lookup Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetDirPatternMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetDirPatternMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetDirPatternMsgEx.h

Purpose: Declares the SetDirPatternMsgEx server-side message extension: mirrored directory stripe-pattern update handler.

Important APIs/types/functions: Declarations/types: class SetDirPatternMsgEx : public MirroredMessage<SetDirPatternMsg, FileIDLock>; typedef ErrorCodeResponseState<SetDirPatternRespMsg, NETMSGTYPE_SetDirPattern> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/attribs/SetDirPatternMsg.h>, <common/net/message/storage/attribs/SetDirPatternRespMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetDirPatternMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetFilePatternMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetFilePatternMsgEx.cpp

Purpose: Implements the SetFilePatternMsgEx server-side message extension: mirrored file stripe-pattern update handler.

Important APIs/types/functions: Implemented entry points: bool SetFilePatternMsgEx::processIncoming(ResponseContext& ctx); FileIDLock SetFilePatternMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> SetFilePatternMsgEx::executeLocally( ResponseContext& ctx, bool isSecondary); void SetFilePatternMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <session/EntryLock.h>, "SetFilePatternMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetFilePatternMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetFilePatternMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetFilePatternMsgEx.h

Purpose: Declares the SetFilePatternMsgEx server-side message extension: mirrored file stripe-pattern update handler.

Important APIs/types/functions: Declarations/types: class SetFilePatternMsgEx : public MirroredMessage<SetFilePatternMsg, FileIDLock>; typedef ErrorCodeResponseState<SetFilePatternRespMsg, NETMSGTYPE_SetFilePattern> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <net/message/MirroredMessage.h>, <common/net/message/storage/attribs/SetFilePatternMsg.h>, <common/net/message/storage/attribs/SetFilePatternRespMsg.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetFilePatternMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetFileStateMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetFileStateMsgEx.cpp

Purpose: Implements the SetFileStateMsgEx server-side message extension: mirrored file state update handler.

Important APIs/types/functions: Implemented entry points: bool SetFileStateMsgEx::processIncoming(ResponseContext& ctx); FileIDLock SetFileStateMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> SetFileStateMsgEx::executeLocally( ResponseContext& ctx, bool isSecondary); void SetFileStateMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <session/EntryLock.h>, "SetFileStateMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetFileStateMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetFileStateMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetFileStateMsgEx.h

Purpose: Declares the SetFileStateMsgEx server-side message extension: mirrored file state update handler.

Important APIs/types/functions: Declarations/types: class SetFileStateMsgEx : public MirroredMessage<SetFileStateMsg, FileIDLock>; typedef ErrorCodeResponseState<SetFileStateRespMsg, NETMSGTYPE_SetFileState> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <net/message/MirroredMessage.h>, <common/net/message/storage/attribs/SetFileStateMsg.h>, <common/net/message/storage/attribs/SetFileStateRespMsg.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetFileStateMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetXAttrMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetXAttrMsgEx.cpp

Purpose: Implements the SetXAttrMsgEx server-side message extension: mirrored extended-attribute write handler.

Important APIs/types/functions: Implemented entry points: std::tuple<FileIDLock, FileIDLock> SetXAttrMsgEx::lock(EntryLockStore& store); bool SetXAttrMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> SetXAttrMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void SetXAttrMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/attribs/SetXAttrRespMsg.h>, <net/msghelpers/MsgHelperXAttr.h>, <session/EntryLock.h>, "SetXAttrMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetXAttrMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetXAttrMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetXAttrMsgEx.h

Purpose: Declares the SetXAttrMsgEx server-side message extension: mirrored extended-attribute write handler.

Important APIs/types/functions: Declarations/types: class SetXAttrMsgEx : public MirroredMessage<SetXAttrMsg, std::tuple<FileIDLock, FileIDLock>>; typedef ErrorCodeResponseState<SetXAttrRespMsg, NETMSGTYPE_SetXAttr> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/storage/attribs/SetXAttrMsg.h>, <common/net/message/storage/attribs/SetXAttrRespMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetXAttrMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/StatMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/StatMsgEx.cpp

Purpose: Implements the StatMsgEx server-side message extension: mirrored stat handler for regular metadata entries and the root directory special case.

Important APIs/types/functions: Implemented entry points: bool StatMsgEx::processIncoming(ResponseContext& ctx); FileIDLock StatMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> StatMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); FhgfsOpsErr StatMsgEx::statRoot(StatData& outStatData).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/attribs/StatRespMsg.h>, <common/toolkit/MessagingTk.h>, <net/msghelpers/MsgHelperStat.h>, "StatMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary root-directory special cases need explicit coverage because they bypass normal parent/name lookup Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/StatMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/StatMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/StatMsgEx.h

Purpose: Declares the StatMsgEx server-side message extension: mirrored stat handler for regular metadata entries and the root directory special case.

Important APIs/types/functions: Declarations/types: class StatMsgResponseState : public MirroredMessageResponseState; class StatMsgEx: public MirroredMessage<StatMsg, FileIDLock>; typedef StatMsgResponseState ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <storage/DirInode.h>, <common/storage/StorageErrors.h>, <common/net/message/storage/attribs/StatMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary root-directory special cases need explicit coverage because they bypass normal parent/name lookup Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/StatMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/UpdateDirParentMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/UpdateDirParentMsgEx.cpp

Purpose: Implements the UpdateDirParentMsgEx server-side message extension: mirrored handler that updates a directory inode parent pointer.

Important APIs/types/functions: Implemented entry points: bool UpdateDirParentMsgEx::processIncoming(ResponseContext& ctx); FileIDLock UpdateDirParentMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> UpdateDirParentMsgEx::executeLocally( ResponseContext& ctx, bool isSecondary); void UpdateDirParentMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/attribs/UpdateDirParentRespMsg.h>, <common/net/message/storage/attribs/SetLocalAttrMsg.h>, <common/net/message/storage/attribs/SetLocalAttrRespMsg.h>, <common/toolkit/MessagingTk.h>, <components/worker/SetChunkFileAttribsWork.h>, <session/EntryLock.h>, "UpdateDirParentMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/UpdateDirParentMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/UpdateDirParentMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/UpdateDirParentMsgEx.h

Purpose: Declares the UpdateDirParentMsgEx server-side message extension: mirrored handler that updates a directory inode parent pointer.

Important APIs/types/functions: Declarations/types: class UpdateDirParentMsgEx : public MirroredMessage<UpdateDirParentMsg, FileIDLock>; typedef ErrorCodeResponseState<UpdateDirParentRespMsg, NETMSGTYPE_UpdateDirParent> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <storage/MetaStore.h>, <common/storage/StorageErrors.h>, <common/net/message/storage/attribs/UpdateDirParentMsg.h>, <common/net/message/storage/attribs/UpdateDirParentRespMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/UpdateDirParentMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.cpp

Purpose: Implements the GetChunkBalanceJobStatsMsgEx server-side message extension: chunk-balancer query handler returning job statistics from the metadata node job registry.

Important APIs/types/functions: Implemented entry points: bool GetChunkBalanceJobStatsMsgEx::processIncoming(ResponseContext& ctx).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: uses in-memory chunk-balancer job state and may persist resulting stripe-pattern metadata.

Dependencies and integration points: Direct includes: "GetChunkBalanceJobStatsMsgEx.h", <common/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsRespMsg.h>, <components/chunkbalancer/ChunkBalancerJob.h>, <program/Program.h>. Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics.

Risks and test signals: wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.h

Purpose: Declares the GetChunkBalanceJobStatsMsgEx server-side message extension: chunk-balancer query handler returning job statistics from the metadata node job registry.

Important APIs/types/functions: Declarations/types: class GetChunkBalanceJobStatsMsgEx : public GetChunkBalanceJobStatsMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: uses in-memory chunk-balancer job state and may persist resulting stripe-pattern metadata.

Dependencies and integration points: Direct includes: <common/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/StartChunkBalanceMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/StartChunkBalanceMsgEx.cpp

Purpose: Implements the StartChunkBalanceMsgEx server-side message extension: mirrored handler that creates or reuses a chunk-balancing job for an entry.

Important APIs/types/functions: Implemented entry points: FileIDLock StartChunkBalanceMsgEx::lock(EntryLockStore& store); bool StartChunkBalanceMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> StartChunkBalanceMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); ChunkBalancerJob* StartChunkBalanceMsgEx::addChunkBalanceJob(bool& outIsNew).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: uses in-memory chunk-balancer job state and may persist resulting stripe-pattern metadata.

Dependencies and integration points: Direct includes: <toolkit/StorageTkEx.h>, <program/Program.h>, "StartChunkBalanceMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/StartChunkBalanceMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/StartChunkBalanceMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/StartChunkBalanceMsgEx.h

Purpose: Declares the StartChunkBalanceMsgEx server-side message extension: mirrored handler that creates or reuses a chunk-balancing job for an entry.

Important APIs/types/functions: Declarations/types: class StartChunkBalanceMsgResponseState : public ErrorCodeResponseState<StartChunkBalanceRespMsg, NETMSGTYPE_StartChunkBalance>; class StartChunkBalanceMsgEx : public MirroredMessage<StartChunkBalanceMsg, FileIDLock>; typedef StartChunkBalanceMsgResponseState ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: uses in-memory chunk-balancer job state and may persist resulting stripe-pattern metadata.

Dependencies and integration points: Direct includes: <common/net/message/storage/chunkbalancing/StartChunkBalanceMsg.h>, <common/net/message/storage/chunkbalancing/StartChunkBalanceRespMsg.h>, <components/chunkbalancer/ChunkBalancerJob.h>, <net/message/MirroredMessage.h>, <session/EntryLock.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/StartChunkBalanceMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/UpdateStripePatternMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/UpdateStripePatternMsgEx.cpp

Purpose: Implements the UpdateStripePatternMsgEx server-side message extension: mirrored chunk-balancing worker handler that rewrites file stripe patterns after chunk movement checks.

Important APIs/types/functions: Implemented entry points: FileIDLock UpdateStripePatternMsgEx::lock(EntryLockStore& store); bool UpdateStripePatternMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> UpdateStripePatternMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); bool UpdateStripePatternMsgEx::setStripePattern(EntryInfo* entryInfo, FileInode& inode, std::string& relativePath, uint16_t localTargetID, uint16_t destinationID); void UpdateStripePatternMsgEx::forwardToSecondary(ResponseContext& ctx); bool UpdateStripePatternMsgEx::checkChunkOnStorageTarget(FileInode& inode, std::string& relativePath, uint16_t targetID).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates; uses in-memory chunk-balancer job state and may persist resulting stripe-pattern metadata.

Dependencies and integration points: Direct includes: <toolkit/StorageTkEx.h>, <program/Program.h>, <storage/MetaStore.h>, <components/FileEventLogger.h>, "UpdateStripePatternMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Chunk-existence checks and pattern rewrites must be atomic from the metadata perspective, or balancing can strand chunks on the wrong target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/UpdateStripePatternMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/UpdateStripePatternMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/UpdateStripePatternMsgEx.h

Purpose: Declares the UpdateStripePatternMsgEx server-side message extension: mirrored chunk-balancing worker handler that rewrites file stripe patterns after chunk movement checks.

Important APIs/types/functions: Declarations/types: class UpdateStripePatternMsgEx : public MirroredMessage<UpdateStripePatternMsg, FileIDLock>; typedef ErrorCodeResponseState<UpdateStripePatternRespMsg, NETMSGTYPE_UpdateStripePattern> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates; uses in-memory chunk-balancer job state and may persist resulting stripe-pattern metadata.

Dependencies and integration points: Direct includes: <common/net/message/storage/chunkbalancing/UpdateStripePatternMsg.h>, <common/net/message/storage/chunkbalancing/UpdateStripePatternRespMsg.h>, <components/chunkbalancer/ChunkBalancerJob.h>, <net/message/MirroredMessage.h>, <app/App.h>, <session/EntryLock.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Chunk-existence checks and pattern rewrites must be atomic from the metadata perspective, or balancing can strand chunks on the wrong target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/UpdateStripePatternMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/HardlinkMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/HardlinkMsgEx.cpp

Purpose: Implements the HardlinkMsgEx server-side message extension: mirrored hardlink creation handler coordinating source inode link counts and destination dentry insertion.

Important APIs/types/functions: Implemented entry points: std::tuple<FileIDLock, ParentNameLock, ParentNameLock, FileIDLock> HardlinkMsgEx::lock( EntryLockStore& store); bool HardlinkMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> HardlinkMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); FhgfsOpsErr HardlinkMsgEx::incDecRemoteLinkCount(NumNodeID const& ownerNodeID, bool increment); void HardlinkMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/creating/HardlinkRespMsg.h>, <common/net/message/storage/creating/MoveFileInodeMsg.h>, <common/net/message/storage/creating/MoveFileInodeRespMsg.h>, <common/net/message/storage/attribs/SetAttrMsg.h>, <common/net/message/storage/attribs/SetAttrRespMsg.h>, <common/toolkit/MessagingTk.h>, <components/FileEventLogger.h>, "HardlinkMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Link-count changes and destination dentry creation must be compensated on partial failure, especially when the source owner is remote.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/HardlinkMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/HardlinkMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/HardlinkMsgEx.h

Purpose: Declares the HardlinkMsgEx server-side message extension: mirrored hardlink creation handler coordinating source inode link counts and destination dentry insertion.

Important APIs/types/functions: Declarations/types: class HardlinkMsgEx : public MirroredMessage<HardlinkMsg,; typedef ErrorCodeResponseState<HardlinkRespMsg, NETMSGTYPE_Hardlink> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/creating/HardlinkMsg.h>, <common/net/message/storage/creating/HardlinkRespMsg.h>, <session/EntryLock.h>, <storage/DirEntry.h>, <storage/MetaStore.h>, <net/message/MirroredMessage.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Link-count changes and destination dentry creation must be compensated on partial failure, especially when the source owner is remote.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/HardlinkMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkDirMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkDirMsgEx.cpp

Purpose: Implements the MkDirMsgEx server-side message extension: mirrored mkdir handler coordinating local or remote directory-inode creation, dentry insertion, ACLs, and event logging.

Important APIs/types/functions: Implemented entry points: bool MkDirMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> MkDirMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); std::tuple<HashDirLock, FileIDLock, ParentNameLock> MkDirMsgEx::lock(EntryLockStore& store); std::unique_ptr<MkDirMsgEx::ResponseState> MkDirMsgEx::mkDirPrimary(ResponseContext& ctx); std::unique_ptr<MkDirMsgEx::ResponseState> MkDirMsgEx::mkDirSecondary(); FhgfsOpsErr MkDirMsgEx::mkDirDentry(DirInode& parentDir, const std::string& name, const EntryInfo* entryInfo, const bool isBuddyMirrored); FhgfsOpsErr MkDirMsgEx::mkRemoteDirInode(DirInode& parentDir, const std::string& name, EntryInfo* entryInfo, const CharVector& defaultACLXAttr, const CharVector& accessACLXAttr); FhgfsOpsErr MkDirMsgEx::mkRemoteDirCompensate(EntryInfo* entryInfo); ...

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h>, <common/net/message/control/GenericResponseMsg.h>, <common/net/message/storage/creating/MkLocalDirMsg.h>, <common/net/message/storage/creating/MkLocalDirRespMsg.h>, <common/net/message/storage/creating/MkDirRespMsg.h>, <common/toolkit/MessagingTk.h>, <components/FileEventLogger.h>, <components/ModificationEventFlusher.h>, <program/Program.h>, <storage/PosixACL.h>, ... Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path The remote-inode compensation path is a critical failure mode; tests should cover owner selection, remote failure, duplicate names, ACL propagation, and buddy-mirrored secondary replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkDirMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkDirMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkDirMsgEx.h

Purpose: Declares the MkDirMsgEx server-side message extension: mirrored mkdir handler coordinating local or remote directory-inode creation, dentry insertion, ACLs, and event logging.

Important APIs/types/functions: Declarations/types: class MkDirMsgEx : public MirroredMessage<MkDirMsg, std::tuple<HashDirLock, FileIDLock, ParentNameLock>>; typedef ErrorAndEntryResponseState<MkDirRespMsg, NETMSGTYPE_MkDir> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/creating/MkDirMsg.h>, <common/net/message/storage/creating/MkDirRespMsg.h>, <session/EntryLock.h>, <storage/MetaStore.h>, <net/message/MirroredMessage.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary The remote-inode compensation path is a critical failure mode; tests should cover owner selection, remote failure, duplicate names, ACL propagation, and buddy-mirrored secondary replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkDirMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileMsgEx.cpp

Purpose: Implements the MkFileMsgEx server-side message extension: mirrored regular-file creation handler using the standard BeeGFS mkfile helper path.

Important APIs/types/functions: Implemented entry points: std::tuple<FileIDLock, ParentNameLock, FileIDLock> MkFileMsgEx::lock(EntryLockStore& store); bool MkFileMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> MkFileMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); std::unique_ptr<MkFileMsgEx::ResponseState> MkFileMsgEx::executePrimary(); std::unique_ptr<MkFileMsgEx::ResponseState> MkFileMsgEx::executeSecondary(); void MkFileMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/storage/creating/MkFileRespMsg.h>, <common/net/message/control/GenericResponseMsg.h>, <common/toolkit/MessagingTk.h>, <common/storage/StatData.h>, <components/FileEventLogger.h>, <net/msghelpers/MsgHelperMkFile.h>, <program/Program.h>, "MkFileMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileMsgEx.h

Purpose: Declares the MkFileMsgEx server-side message extension: mirrored regular-file creation handler using the standard BeeGFS mkfile helper path.

Important APIs/types/functions: Declarations/types: class MkFileMsgEx : public MirroredMessage<MkFileMsg,; typedef ErrorAndEntryResponseState<MkFileRespMsg, NETMSGTYPE_MkFile> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/creating/MkFileMsg.h>, <common/net/message/storage/creating/MkFileRespMsg.h>, <session/EntryLock.h>, <storage/MetaStore.h>, <net/message/MirroredMessage.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileWithPatternMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileWithPatternMsgEx.cpp

Purpose: Implements the MkFileWithPatternMsgEx server-side message extension: mirrored file creation handler that honors an explicit caller-provided stripe pattern.

Important APIs/types/functions: Implemented entry points: std::tuple<FileIDLock, ParentNameLock, FileIDLock> MkFileWithPatternMsgEx::lock( EntryLockStore& store); bool MkFileWithPatternMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> MkFileWithPatternMsgEx::executeLocally( ResponseContext& ctx, bool isSecondary); FhgfsOpsErr MkFileWithPatternMsgEx::mkFile(const EntryInfo* parentInfo, MkFileDetails& mkDetails, EntryInfo* outEntryInfo, FileInodeStoreData& inodeDiskData); FhgfsOpsErr MkFileWithPatternMsgEx::mkMetaFile(DirInode& dir, MkFileDetails& mkDetails, EntryInfo* outEntryInfo, FileInodeStoreData& inodeDiskData); void MkFileWithPatternMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <common/net/message/storage/creating/MkFileMsg.h>, <common/net/message/storage/creating/MkFileRespMsg.h>, <program/Program.h>, <common/net/message/storage/creating/UnlinkLocalFileMsg.h>, <common/net/message/storage/creating/UnlinkLocalFileRespMsg.h>, <common/storage/striping/StripePattern.h>, <common/toolkit/MathTk.h>, <common/toolkit/MessagingTk.h>, <components/FileEventLogger.h>, <net/msghelpers/MsgHelperMkFile.h>, ... Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Explicit patterns need validation for target existence, buddy-group primary mapping, minimum targets, and power-of-two chunk size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileWithPatternMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileWithPatternMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileWithPatternMsgEx.h

Purpose: Declares the MkFileWithPatternMsgEx server-side message extension: mirrored file creation handler that honors an explicit caller-provided stripe pattern.

Important APIs/types/functions: Declarations/types: class MkFileWithPatternMsgEx : public MirroredMessage<MkFileWithPatternMsg,; typedef ErrorAndEntryResponseState<MkFileWithPatternRespMsg, NETMSGTYPE_MkFileWithPattern> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/storage/creating/MkFileRespMsg.h>, <common/net/message/storage/creating/MkFileWithPatternMsg.h>, <common/net/message/storage/creating/MkFileWithPatternRespMsg.h>, <common/storage/StorageErrors.h>, <net/message/MirroredMessage.h>, <session/EntryLock.h>, <storage/MetaStore.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Explicit patterns need validation for target existence, buddy-group primary mapping, minimum targets, and power-of-two chunk size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileWithPatternMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkLocalDirMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkLocalDirMsgEx.cpp

Purpose: Implements the MkLocalDirMsgEx server-side message extension: mirrored helper handler that creates a directory inode on the node that owns it.

Important APIs/types/functions: Implemented entry points: HashDirLock MkLocalDirMsgEx::lock(EntryLockStore& store); bool MkLocalDirMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> MkLocalDirMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void MkLocalDirMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <common/net/message/control/GenericResponseMsg.h>, <program/Program.h>, <common/net/message/storage/creating/MkLocalDirRespMsg.h>, "MkLocalDirMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkLocalDirMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkLocalDirMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkLocalDirMsgEx.h

Purpose: Declares the MkLocalDirMsgEx server-side message extension: mirrored helper handler that creates a directory inode on the node that owns it.

Important APIs/types/functions: Declarations/types: class MkLocalDirMsgEx : public MirroredMessage<MkLocalDirMsg, HashDirLock>; typedef ErrorCodeResponseState<MkLocalDirRespMsg, NETMSGTYPE_MkLocalDir> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/creating/MkLocalDirMsg.h>, <common/net/message/storage/creating/MkLocalDirRespMsg.h>, <net/message/MirroredMessage.h>, <session/EntryLock.h>, <storage/MetaStore.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkLocalDirMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MoveFileInodeMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MoveFileInodeMsgEx.cpp

Purpose: Implements the MoveFileInodeMsgEx server-side message extension: mirrored handler that verifies and moves file inode placement/mode metadata for hardlink-capable files.

Important APIs/types/functions: Implemented entry points: std::tuple<FileIDLock, ParentNameLock, FileIDLock> MoveFileInodeMsgEx::lock(EntryLockStore& store); bool MoveFileInodeMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> MoveFileInodeMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void MoveFileInodeMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/storage/creating/MoveFileInodeRespMsg.h>, "MoveFileInodeMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MoveFileInodeMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MoveFileInodeMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MoveFileInodeMsgEx.h

Purpose: Declares the MoveFileInodeMsgEx server-side message extension: mirrored handler that verifies and moves file inode placement/mode metadata for hardlink-capable files.

Important APIs/types/functions: Declarations/types: class MoveFileInodeMsgResponseState : public MirroredMessageResponseState; class MoveFileInodeMsgEx : public MirroredMessage<MoveFileInodeMsg,; typedef MoveFileInodeMsgResponseState ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/creating/MoveFileInodeMsg.h>, <common/net/message/storage/creating/MoveFileInodeRespMsg.h>, <net/message/MirroredMessage.h>, <session/EntryLock.h>, <storage/MetaStore.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MoveFileInodeMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirEntryMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirEntryMsgEx.cpp

Purpose: Implements the RmDirEntryMsgEx server-side message extension: non-mirrored administrative removal handler for removing a directory entry directly from a parent directory.

Important APIs/types/functions: Implemented entry points: bool RmDirEntryMsgEx::processIncoming(ResponseContext& ctx); FhgfsOpsErr RmDirEntryMsgEx::rmDirEntry(EntryInfo* parentInfo, std::string& entryName).

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/creating/RmDirEntryRespMsg.h>, <common/toolkit/MessagingTk.h>, "RmDirEntryMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence.

Risks and test signals: referenced metadata objects must be released on every error path wire compatibility depends on sending the exact response message type expected by management clients Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirEntryMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirEntryMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirEntryMsgEx.h

Purpose: Declares the RmDirEntryMsgEx server-side message extension: non-mirrored administrative removal handler for removing a directory entry directly from a parent directory.

Important APIs/types/functions: Declarations/types: class RmDirEntryMsgEx : public RmDirEntryMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/creating/RmDirEntryMsg.h>, <storage/MetaStore.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirEntryMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirMsgEx.cpp

Purpose: Implements the RmDirMsgEx server-side message extension: mirrored rmdir handler that removes a child directory dentry and coordinates local or remote inode deletion.

Important APIs/types/functions: Implemented entry points: bool RmDirMsgEx::processIncoming(ResponseContext& ctx); std::tuple<HashDirLock, FileIDLock, FileIDLock, ParentNameLock> RmDirMsgEx::lock(EntryLockStore& store); std::unique_ptr<RmDirMsgEx::ResponseState> RmDirMsgEx::rmDir(ResponseContext& ctx, const bool isSecondary); FhgfsOpsErr RmDirMsgEx::rmRemoteDirInode(EntryInfo* delEntryInfo); void RmDirMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h>, <common/net/message/control/GenericResponseMsg.h>, <common/net/message/storage/creating/RmDirRespMsg.h>, <common/net/message/storage/creating/RmLocalDirMsg.h>, <common/net/message/storage/creating/RmLocalDirRespMsg.h>, <common/toolkit/MessagingTk.h>, <components/FileEventLogger.h>, <components/ModificationEventFlusher.h>, <program/Program.h>, <session/EntryLock.h>, ... Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirMsgEx.h

Purpose: Declares the RmDirMsgEx server-side message extension: mirrored rmdir handler that removes a child directory dentry and coordinates local or remote inode deletion.

Important APIs/types/functions: Declarations/types: class RmDirMsgEx : public MirroredMessage<RmDirMsg,; typedef ErrorCodeResponseState<RmDirRespMsg, NETMSGTYPE_RmDir> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/creating/RmDirMsg.h>, <common/net/message/storage/creating/RmDirRespMsg.h>, <storage/MetaStore.h>, <net/message/MirroredMessage.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmLocalDirMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmLocalDirMsgEx.cpp

Purpose: Implements the RmLocalDirMsgEx server-side message extension: mirrored helper handler that removes a locally owned directory inode.

Important APIs/types/functions: Implemented entry points: std::tuple<HashDirLock, FileIDLock> RmLocalDirMsgEx::lock(EntryLockStore& store); bool RmLocalDirMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> RmLocalDirMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); std::unique_ptr<RmLocalDirMsgEx::ResponseState> RmLocalDirMsgEx::rmDir(); void RmLocalDirMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/creating/RmLocalDirRespMsg.h>, <common/toolkit/MetaStorageTk.h>, "RmLocalDirMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmLocalDirMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmLocalDirMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmLocalDirMsgEx.h

Purpose: Declares the RmLocalDirMsgEx server-side message extension: mirrored helper handler that removes a locally owned directory inode.

Important APIs/types/functions: Declarations/types: class RmLocalDirMsgEx : public MirroredMessage<RmLocalDirMsg, std::tuple<HashDirLock, FileIDLock>>; typedef ErrorCodeResponseState<RmLocalDirRespMsg, NETMSGTYPE_RmLocalDir> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/creating/RmLocalDirMsg.h>, <common/net/message/storage/creating/RmLocalDirRespMsg.h>, <session/EntryLock.h>, <storage/MetaStore.h>, <net/message/MirroredMessage.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmLocalDirMsgEx.h -->

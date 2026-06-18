# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/protocolPB/GetUserMappingsProtocolServerSideTranslatorPB.java

Purpose: this server-side translator adapts a classic `GetUserMappingsProtocol` implementation to the protobuf blocking RPC service.

Important APIs and types: it implements `GetUserMappingsProtocolPB`, stores a `GetUserMappingsProtocol` delegate, and implements protobuf `getGroupsForUser`.

Control flow: on RPC, it extracts the user from `GetGroupsForUserRequestProto`, calls the delegate, wraps any `IOException` in `ServiceException`, builds `GetGroupsForUserResponseProto`, and adds each returned group in order.

State and persistence behavior: state is only the delegate reference. No caching or persistence.

Dependencies and integration points: used by Hadoop IPC servers for HDFS/MapReduce group-mapping endpoints. Depends on generated protobuf request/response types and shaded protobuf `ServiceException`.

Risks: null delegate results or null group entries are not guarded. IOException is the only checked exception converted explicitly. Group order is preserved and may be significant to clients.

Test signals: cover user extraction, group order/count, empty groups, IOException-to-ServiceException conversion, and malformed/null delegate behavior if construction is not controlled.

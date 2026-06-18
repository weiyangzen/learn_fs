# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/GetUserMappingsProtocol.java

Purpose: `GetUserMappingsProtocol` is the RPC interface used by NameNode/JobTracker-side services to return group names for a user.

Important APIs and types: it declares `versionID = 1L` and idempotent `String[] getGroupsForUser(String user) throws IOException`.

Control flow: client tools invoke it through Hadoop RPC or the protobuf translator. Implementations map the supplied user string to group names and return them as an array.

State and persistence behavior: interface-only; no state. Implementations may consult UGI/group mapping caches but that is outside this file.

Dependencies and integration points: annotated limited-private for HDFS/MapReduce, evolving stability, and `@Idempotent` for retry semantics. Bridged by `GetUserMappingsProtocolPB` and client/server translators.

Risks: version ID and method signature are wire compatibility. The method is marked idempotent, so implementations must avoid side effects that make retries unsafe.

Test signals: verify protobuf translators preserve order/count, RPC method support metadata, retry behavior, and IOException propagation.

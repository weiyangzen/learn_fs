# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/package-info.java

Purpose: package descriptor for federation resolvers.

Important APIs: package-level private/evolving annotations and documentation identify resolvers as performance-sensitive components used in the `RouterRpcServer` request path. It names `ActiveNamenodeResolver` and `FileSubclusterResolver` as principal resolver contracts.

Control flow and state: no executable logic.

Dependencies and integration points: documentation-level integration with Router RPC, State Store, and federation path/name resolution.

Risks: typo/documentation drift only, but package privacy/evolving status guides compatibility expectations.

Test signals: none at runtime.

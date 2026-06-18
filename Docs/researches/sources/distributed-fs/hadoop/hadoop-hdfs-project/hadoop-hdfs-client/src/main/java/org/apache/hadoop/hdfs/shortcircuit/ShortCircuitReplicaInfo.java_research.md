# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ShortCircuitReplicaInfo.java

Purpose: `ShortCircuitReplicaInfo` is a small result wrapper for short-circuit replica creation/fetching. It can represent success, invalid block token, or generic no-replica failure.

Important APIs/types/functions: constructors create empty failure, replica success, or `InvalidToken` result. Getters expose `ShortCircuitReplica` and `InvalidToken`. `toString()` includes whichever payload is present.

Control flow: `ShortCircuitCache` stores instances in waitables and returns them to callers. Invalid-token results are surfaced distinctly from generic load failure.

State and persistence behavior: immutable final fields, no persistence.

Dependencies and integration points: depends on `ShortCircuitReplica` and `SecretManager.InvalidToken`. Integrates with block reader creation and cache coordination.

Risks and test signals: empty result has both fields null, so callers must distinguish it from invalid-token failure. Tests should cover all constructors and `ShortCircuitCache` behavior for invalid token versus null replica.

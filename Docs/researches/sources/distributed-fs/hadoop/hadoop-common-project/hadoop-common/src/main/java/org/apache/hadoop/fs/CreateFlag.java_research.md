## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CreateFlag.java

Purpose: `CreateFlag` defines public create and append semantics for Hadoop filesystem writes. It models POSIX-like create, overwrite, append, sync, lazy persist, new block append, locality placement hints, and replication enforcement.

Important APIs and types: enum values carry a short mode used by lower layers. Core validation methods are `validate(EnumSet<CreateFlag>)`, `validate(Object, boolean, EnumSet<CreateFlag>)`, and `validateForAppend(EnumSet<CreateFlag>)`. Public flags include `CREATE`, `OVERWRITE`, `APPEND`, `SYNC_BLOCK`, `LAZY_PERSIST`, `NEW_BLOCK`, `NO_LOCAL_WRITE`, `SHOULD_REPLICATE`, `IGNORE_CLIENT_LOCALITY`, and `NO_LOCAL_RACK`.

Control flow, state, and persistence: validation rejects null or empty flag sets and rejects `APPEND` with `OVERWRITE`. Path-aware validation enforces that existing paths require append or overwrite and non-existing paths require create. Append validation additionally requires `APPEND`. The enum itself is static process state; no persistence is implemented here.

Dependencies and integration: create builders, `FileSystem` implementations, and HDFS clients use these flags to select create or append behavior. Exceptions integrate with `HadoopIllegalArgumentException`, `FileAlreadyExistsException`, and `FileNotFoundException`.

Risks and test signals: flag combinations are a compatibility surface. The `NO_LOCAL_RACK` mode value overlaps the `IGNORE_CLIENT_LOCALITY` bit plus `NEW_BLOCK` rather than a single new bit, which tests should preserve or flag deliberately. Tests should cover all valid combinations, invalid append/overwrite combinations, path existence branches, and builder integration.

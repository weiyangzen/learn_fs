# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/MountTableManager.java

Purpose: `MountTableManager` is the management interface for router mount table CRUD and cache refresh operations.

Important APIs: methods map to protocol request/response pairs for adding, updating, removing, retrieving, listing, refreshing, and validating mount table entries. It is a resolver-side contract consumed by router admin paths and State Store-backed managers.

Control flow and state: no implementation here. Persistence is expected in State Store mount table records through implementing classes.

Dependencies and integration points: store protocol classes under `org.apache.hadoop.hdfs.server.federation.store.protocol` and admin tooling such as `RouterAdmin`.

Risks: this is an administrative API contract; response/result semantics must stay stable for CLI and service callers. Validation and refresh behavior are implementation-defined.

Test signals: implementer tests should cover each request/response operation, authorization if applied elsewhere, State Store failure propagation, and cache refresh side effects in `MountTableResolver`.

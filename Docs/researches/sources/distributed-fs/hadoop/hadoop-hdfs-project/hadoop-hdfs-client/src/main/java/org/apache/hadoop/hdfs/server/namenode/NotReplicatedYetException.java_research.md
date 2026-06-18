# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/NotReplicatedYetException.java

Purpose: `NotReplicatedYetException` is a private/evolving `IOException` used by NameNode operations when a file has not yet reached enough DataNode replicas to satisfy an operation.

Important APIs/types/functions: it contains a single `String` constructor and inherits all behavior from `IOException`.

Control flow: NameNode code throws it as a typed transient condition. Callers can catch this exact type to retry or surface a clearer client error rather than treating it as an arbitrary I/O failure.

State and persistence behavior: no custom state beyond the exception message and `serialVersionUID`.

Dependencies and integration points: depends only on Hadoop classification annotations and Java `IOException`. It integrates with file creation/close/replication checks in NameNode code.

Risks and test signals: the main risk is losing typed catch behavior if replaced with a generic exception. Tests should exercise NameNode paths that throw this when replication preconditions are not met and verify client retry/error behavior.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/SafeModeException.java

Purpose: `SafeModeException` is a private/evolving `IOException` thrown when a NameNode is in safe mode and namespace modifications cannot proceed.

Important APIs/types/functions: it has a single message constructor and a stable `serialVersionUID`.

Control flow: namespace-modifying RPC implementations throw it while safe mode is active. Client layers and admin tools use the type/message to explain why write operations are blocked.

State and persistence behavior: exception state is limited to the inherited message. It does not query safe-mode state itself.

Dependencies and integration points: depends on Hadoop classification annotations and Java `IOException`. It integrates with NameNode safe-mode checks across create, delete, rename, and similar operations.

Risks and test signals: message clarity matters for operators, and typed behavior matters for clients. Tests should cover representative write RPCs in safe mode and verify this exception is propagated or wrapped consistently.

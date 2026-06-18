# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/FSLimitException.java

Purpose: Defines filesystem limit exceptions for HDFS namespace constraints, specifically path component length and maximum directory item count. These exceptions derive from `QuotaExceededException` so callers can handle namespace limits consistently with quota failures.

Important APIs and types: `FSLimitException` is the abstract base. `PathComponentTooLongException` records the offending child name and parent path and formats a limit/length message. `MaxDirectoryItemsExceededException` records the directory path and formats a limit/items message.

Control flow: Constructors populate inherited quota/count/path fields. `getMessage()` builds user-facing explanations using the stored values.

State and persistence behavior: Exception instances carry quota, count, path, and child-name fields for the duration of error handling or RPC serialization. No persistent state is changed.

Dependencies and integration points: Depends on `QuotaExceededException` and HDFS namespace validation paths in `FSDirectory`/NameNode operations. Annotated public/evolving because clients may see these failures.

Risks: Message formatting is part of user/admin diagnostics. Protected no-arg/string constructors exist for serialization but can produce incomplete messages if used incorrectly. The child name is mutable only through construction, so accurate caller values matter.

Test signals: Tests should trigger path component length and directory item limit violations, verify exception types and messages, RPC propagation to clients, and serialization/deserialization compatibility.

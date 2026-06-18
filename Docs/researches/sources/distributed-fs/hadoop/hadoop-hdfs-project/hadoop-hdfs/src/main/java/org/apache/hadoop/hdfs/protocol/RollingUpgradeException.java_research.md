# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/RollingUpgradeException.java

Purpose: Represents rolling-upgrade-specific HDFS failures. It gives upgrade control paths a typed IOException for invalid or unsupported rolling upgrade operations.

Important APIs and types: `RollingUpgradeException` extends `IOException` and exposes a message constructor.

Control flow: No custom flow beyond exception construction.

State and persistence behavior: Exception state is the message and stack trace only.

Dependencies and integration points: Used by NameNode/DataNode rolling upgrade code and administrative APIs.

Risks: Generic catch blocks may flatten it to an ordinary IO failure, losing upgrade-specific context. Messages should identify the invalid upgrade state/action.

Test signals: Rolling upgrade tests should assert this type for invalid prepare/finalize/rollback states and verify RPC/client propagation.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionNullException.java

Purpose: checked exception indicating the router could not obtain a non-null connection.

Important API: constructor accepts a message and extends `IOException`.

Control flow and state: no mutable state. Used by higher router RPC code when connection acquisition fails.

Dependencies and integration points: complements `ConnectionManager.getConnection`, which can return null when stopped or unable to provide a usable proxy.

Risks: generic IO handling can hide the specific connection-pool failure unless the message is clear.

Test signals: router RPC client paths should throw or propagate this when connection context is null.

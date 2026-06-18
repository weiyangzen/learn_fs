# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/RouterResolveException.java

Purpose: checked exception indicating `FileSubclusterResolver` could not resolve a path.

Important API: constructor accepts an error message and extends `IOException` with a serial version UID.

Control flow and state: no mutable state. `MountTableResolver.lookupLocation` throws it when no mount matches and default namespace reads/writes are disabled.

Dependencies and integration points: propagates through Router RPC path resolution as an IO failure.

Risks: callers may treat it generically as `IOException`, so diagnostic messages are important.

Test signals: no-default-namespace path resolution should throw this specific type and message should include the unresolved path.

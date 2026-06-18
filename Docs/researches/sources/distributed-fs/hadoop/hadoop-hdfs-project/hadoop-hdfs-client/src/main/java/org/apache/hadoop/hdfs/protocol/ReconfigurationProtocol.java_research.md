# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ReconfigurationProtocol.java

## Purpose
`ReconfigurationProtocol` is an HDFS admin RPC interface for reloading and applying configuration changes on NameNode/DataNode services without restart.

## APIs and Behavior
It defines `VERSIONID = 1L` and three idempotent RPCs: `startReconfiguration()` to asynchronously reload/apply changes, `getReconfigurationStatus()` to query the current or previous task, and `listReconfigurableProperties()` to list allowed property keys.

## State, Dependencies, and Integration
The interface has no state. Implementations manage background task state and return `ReconfigurationTaskStatus`. It integrates with HDFS admin tooling and retry logic via `@Idempotent`.

## Risks and Test Signals
Although marked idempotent, starting a background reconfiguration must avoid spawning duplicate incompatible tasks under retry. Tests should cover repeated starts, status before/during/after a task, property list stability, partial failures, and RPC permission checks.

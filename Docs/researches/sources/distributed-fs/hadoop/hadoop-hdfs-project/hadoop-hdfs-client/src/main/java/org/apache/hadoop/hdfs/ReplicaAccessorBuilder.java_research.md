# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ReplicaAccessorBuilder.java

Purpose: `ReplicaAccessorBuilder` is the public stable builder API for external replica-access plugins. It lets HDFS pass all block, security, checksum, client, configuration, and visibility metadata to a plugin before the plugin decides whether it can create a `ReplicaAccessor`.

Important APIs/types/functions: setters include `setFileName`, `setBlock(long,String)`, `setGenerationStamp`, `setVerifyChecksum`, `setClientName`, `setAllowShortCircuitReads`, `setVisibleLength`, `setConfiguration`, and `setBlockAccessToken`. `build()` returns either a usable `ReplicaAccessor` or `null` when the plugin cannot handle the request.

Control flow: `BlockReaderFactory` reflectively instantiates each configured builder class, serializes the block token into bytes, invokes the setters, and calls `build()`. If `build()` returns an accessor, HDFS assumes it works and does not attempt a normal block reader for that read. If `null` is returned, the next plugin or normal reader path is tried.

State and persistence behavior: this abstract class has no state; concrete builders accumulate the setter values. `setVisibleLength` is an important consistency boundary: it tells plugins the maximum block length visible to the current file open, and later appends require reopening the file.

Dependencies and integration points: the builder consumes `Configuration` and returns `ReplicaAccessor`. It integrates with client configuration key `HdfsClientConfigKeys.REPLICA_ACCESSOR_BUILDER_CLASSES_KEY` and `BlockReaderFactory.tryToCreateExternalBlockReader()`.

Risks: plugin builders must perform permission and setup checks in `build()`; HDFS treats a non-null accessor as authoritative. Failing to honor `verifyChecksum`, block token, generation stamp, or visible length can expose stale or unauthorized data. Tests should use fake builders that return null, throw during construction, throw in build, and return accessors to validate fallback and isolation.

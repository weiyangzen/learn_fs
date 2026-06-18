# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsUtils.java

Purpose: `HdfsUtils` is a public evolving utility class. In this file it provides a health check that determines whether an HDFS URI is reachable and not in safe mode.

Important APIs/types/functions: `LOG` is an SLF4J logger. `isHealthy(URI uri)` validates the URI scheme, constructs a fresh `Configuration`, disables filesystem caching for the scheme, disables HDFS client retry policy, sets IPC max connect retries to zero, opens a `DistributedFileSystem`, queries safe mode with `SAFEMODE_GET`, and returns true only when safe mode is false.

Control flow: non-HDFS schemes throw `IllegalArgumentException`. DFS open and safe-mode query are inside try-with-resources. Any `IOException` logs at debug and returns false. Successful safe-mode query logs the result at debug and returns the negated safe-mode flag.

State and persistence behavior: no persistent changes are intended. `setSafeMode(SAFEMODE_GET)` is a query action. The method creates and closes a fresh filesystem instance with cache disabled to avoid reusing unhealthy clients.

Dependencies and integration points: integrates with `FileSystem`, `DistributedFileSystem`, `Configuration`, `CommonConfigurationKeysPublic`, `HdfsConstants`, `HdfsClientConfigKeys.Retry`, and safe-mode RPCs.

Risks: health is intentionally narrow: reachable and not in safe mode. It does not check DataNode availability, under-replication, write ability, or HA observer state. Disabling retries makes it fast but sensitive to transient connection failures. Tests should cover scheme validation, cache-disable configuration, safe-mode true/false, IOException returning false, and resource closure.

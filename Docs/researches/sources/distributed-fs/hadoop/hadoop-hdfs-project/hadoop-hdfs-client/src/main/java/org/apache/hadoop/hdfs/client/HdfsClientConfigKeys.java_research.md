# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsClientConfigKeys.java

Purpose: `HdfsClientConfigKeys` is the private central constant interface for HDFS client configuration keys and defaults. It covers core block/replication defaults, WebHDFS behavior, NameNode addresses, client socket/cache settings, short-circuit and mmap reads, retry/failover, write/pipeline behavior, erasure coding, security/data-transfer options, health probes, and deprecated compatibility keys.

Important APIs/types/functions: top-level constants include `DFS_BLOCK_SIZE_KEY/DEFAULT`, replication defaults, WebHDFS user/ACL patterns and security knobs, client socket/cache/domain-socket settings, checksum settings, data transfer protection/encryption keys, replica accessor builder classes key, dead-node detection keys, read-block-location refresh keys, and miscellaneous lease/fsck/congestion settings. Nested interfaces organize `DeprecatedKeys`, `Retry`, `Failover`, `Write` with nested `ByteArrayManager` and `ECRedundancy`, `BlockWrite` with nested `ReplaceDatanodeOnFailure`, `Read` with nested `ShortCircuit`, top-level `ShortCircuit`, `Mmap`, `HedgedRead`, `StripedRead`, and `HttpClient`.

Control flow: no executable logic beyond constant initialization. Consumers import keys and defaults to parse `Configuration` values into concrete client config objects such as `DfsClientConf`.

State and persistence behavior: all values are static constants. Configuration persistence happens outside this file in Hadoop configuration resources and runtime `Configuration` objects.

Dependencies and integration points: uses `HdfsConstants` for default data socket size and `TimeUnit` for millisecond defaults. This interface is referenced throughout HDFS client, WebHDFS, failover, read/write, short-circuit, mmap, EC, and security code.

Risks: this file is a compatibility surface; changing key names or defaults can break deployments. Some defaults strongly affect performance and failure behavior, such as socket cache capacity/expiry, striped read thread pool size, dead-node detection intervals, retry windows, and short-circuit/mmap toggles. Test signals are mostly configuration parsing tests: verify defaults, deprecated key translation, boundary values, nested prefix composition, and interactions with `DfsClientConf`. A typo-like constant `DFS_CLIENT_EC_WRITE_FAILED_BLOCKS_TOLERATED_DEFAILT` is part of the API surface and should be handled cautiously.

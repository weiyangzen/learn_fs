# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/DFSConfigKeys.java

## Purpose
`DFSConfigKeys` is the server-side HDFS configuration constant catalog. It extends `CommonConfigurationKeys`, re-exports many client keys from `HdfsClientConfigKeys`, and defines NameNode, DataNode, JournalNode, Balancer, Mover, StoragePolicySatisfier, WebHDFS, security, HA, cache, erasure coding, disk balancer, topology, and compatibility defaults used throughout HDFS.

## Important APIs and types
- Class: `@InterfaceAudience.Private public class DFSConfigKeys extends CommonConfigurationKeys`.
- Re-exported key groups: block size, replication, checksum, many DFS client retry/read/write/short-circuit/mmap/failover keys, NameNode RPC/HTTP keys, and nameservice keys from `HdfsClientConfigKeys`.
- Default class constants: `RamDiskReplicaLruTracker`, `ReservedSpaceCalculator.ReservedSpaceCalculatorAbsolute`, `BlockPlacementPolicyDefault`, `BlockPlacementPolicyRackFaultTolerant`, `DFSNetworkTopology`, and `GlobalFSNamesystemLock`.
- Enum/default references: `HdfsConstants.StoragePolicySatisfierMode.NONE`, `HdfsConstants.StoragePolicy.HOT`, `HttpConfig.Policy.HTTP_ONLY`.
- Time defaults use a mix of raw milliseconds/seconds and `TimeUnit` conversions.

## Configuration domains
- Core file layout: block size, replication, bytes/checksum, checksum type, stream buffer size, storage directory permissions, name/edits dirs, data dirs, and min/max filesystem limits.
- NameNode operations: safe mode, checkpointing, heartbeat/redundancy intervals, block reports, lease recovery, retry cache, edit log rolling/async logging, fsimage transfer/load, resource checks, access control, snapshots, xattrs, quotas, and lock metrics.
- DataNode operations: volume scanning, cache reports, bandwidth throttles, disk checks, reserved capacity, lazy persist/RAM disk, slow peer/disk reporting, socket buffers, transfer behavior, EC reconstruction, same-disk tiering, and block scanner behavior.
- HA/federation: nameservices, HA NameNode prefix/id, auto failover, ZKFC port/SSL, tail edits/log roll, stale reads, JournalNode addresses/timeouts/cache, QJM timeouts, and Router-adjacent command support through the shell.
- Admin/data movement: Balancer, Mover, SPS, DiskBalancer, NameNode getBlocks QPS, keytab/principal settings, HTTP server settings, and storage policy defaults.
- Security/web: HTTPS keystore/truststore resources, Kerberos principals/keytabs, WebHDFS auth, data transfer encryption/SASL compatibility, block tokens, XFrame protection, encryption zone and re-encryption controls.
- Compatibility: many deprecated constants alias newer nested `HdfsClientConfigKeys` locations to preserve older HDFS server code and external references.

## Control flow
The class has no methods or runtime branching. Its behavior is compile-time/static constant publication. Runtime HDFS components import these constants and use Hadoop `Configuration` getters to resolve actual values, falling back to the defaults declared here or in `HdfsClientConfigKeys`.

## State and persistence behavior
This file does not persist state, but it defines the keys by which HDFS persists and loads administrative configuration from XML files such as `hdfs-default.xml` and `hdfs-site.xml`. Several defaults have direct persistence impact, such as NameNode edits/name directories, JournalNode edit directories, DataNode data directory permissions, retry cache expiry, fsimage transfer settings, and block report intervals.

## Dependencies and integration points
The class depends on Hadoop common configuration keys, HDFS client config keys, HDFS protocol constants, block placement classes, NameNode lock manager implementations, DataNode fsdataset helpers, WebHDFS URL connection defaults, and HTTP policy enums. It is used broadly by HDFS server code, tools, tests, and configuration documentation. Shell scripts in this subset indirectly rely on constants for `dfs.hosts.exclude`, nameservice/NameNode discovery, HA automatic failover, JournalNodes, and Balancer settings via `hdfs getconf` and daemon startup.

## Risks
- Constants are a cross-module API despite `Private`; renames or default changes can break config files, tests, docs, and downstream code.
- Unit semantics are inconsistent by historical convention: some keys are seconds, some milliseconds, some duration strings, and some raw counts. Misuse can create severe timing or resource bugs.
- Deprecated aliases can obscure the canonical source of a key and complicate field/documentation comparison.
- Hidden/internal/test-only keys are intentionally skipped by `TestHdfsConfigFields`; adding a new key without documentation or skip logic can fail tests.
- Some defaults are operationally powerful, for example permissions enabled, ACLs/xattrs enabled, caching enabled, block token disabled, HTTP-only policy, and default local `/tmp` storage paths.
- Broad static catalog makes merge conflicts likely when multiple HDFS features add keys near the same domain.

## Test signals
`src/test/java/org/apache/hadoop/tools/TestHdfsConfigFields.java` compares `DFSConfigKeys`, `HdfsClientConfigKeys`, and nested client key classes against `hdfs-default.xml`, with explicit skip lists for hidden, deprecated, example, native, dynamic, and module-specific properties. Many HDFS tests import these constants directly for behavior setup, including security, HA, block placement, cache, erasure coding, balancer, and CLI tests. Compilation itself is a strong signal because default class constants must remain assignable to the expected implementation types.

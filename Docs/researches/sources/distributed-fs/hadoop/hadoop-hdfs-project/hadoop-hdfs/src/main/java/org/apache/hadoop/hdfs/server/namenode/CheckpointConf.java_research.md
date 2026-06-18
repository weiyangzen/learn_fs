# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CheckpointConf.java

## Purpose
`CheckpointConf` centralizes secondary/backup checkpoint scheduling and upload configuration derived from Hadoop `Configuration`.

## Important APIs and Types
Constructor fields include checkpoint period, edit-log check period, transaction trigger count, max merge retries, legacy OIV image directory, quiet multiplier, and parallel upload enablement. Getters expose `getPeriod`, `getCheckPeriod`, `getTxnCount`, `getMaxRetriesOnMergeError`, `getLegacyOivImageDir`, `getQuietPeriod`, and `isParallelUploadEnabled`.

## Control Flow
Construction reads current DFS config keys and warns if deprecated `fs.checkpoint.size` or `dfs.namenode.checkpoint.size` are present. `getCheckPeriod` caps the check period by the checkpoint period so polling cannot be less frequent than the maximum time-based checkpoint interval.

## State and Persistence
The class is immutable except `quietMultiplier` not declared final. It does not persist itself; checkpoint daemons consume these settings at initialization.

## Dependencies and Integration
Used by `Checkpointer` and other checkpointing components. It depends on `DFSConfigKeys`, `Configuration`, `TimeUnit`, and Guava `ImmutableList`.

## Risks and Test Signals
Misconfigured durations directly affect checkpoint latency and edit-log growth. Deprecated size keys are ignored, so tests should verify warnings and that transaction count comes only from `DFS_NAMENODE_CHECKPOINT_TXNS_KEY`. Configuration tests should cover check-period capping, quiet-period multiplication, and parallel-upload flag propagation.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/ReplaceDatanodeOnFailure.java

## Purpose
`ReplaceDatanodeOnFailure` models the client-side policy for adding a replacement DataNode to a write pipeline after one DataNode fails.

## Important APIs, Types, and Functions
Policies are `DISABLE`, `NEVER`, `DEFAULT`, and `ALWAYS`. `DISABLE` and `NEVER` never replace, `ALWAYS` always replaces when replacement is otherwise meaningful, and `DEFAULT` replaces only when replication is at least three and either existing nodes are at or below half replication or the block is appended/hflushed.

`checkEnabled` throws `UnsupportedOperationException` for `DISABLE`. `isBestEffort` tells callers whether replacement failure should be tolerated. `satisfy` rejects replacement when there are zero existing nodes or enough existing nodes, then delegates to the policy condition. `get(Configuration)` reads enable, policy, and best-effort keys. `write` writes policy settings back to a configuration.

## Control Flow
During write-pipeline recovery, callers load the policy from configuration, check whether replacement is enabled/needed, and either try to add a DataNode or continue/fail depending on `bestEffort`.

## State and Persistence Behavior
Instances are immutable and hold only policy plus best-effort. Persistent behavior is configuration-driven through `HdfsClientConfigKeys.BlockWrite.ReplaceDatanodeOnFailure`.

## Dependencies and Integration Points
It depends on Hadoop `Configuration`, `HadoopIllegalArgumentException`, `HdfsClientConfigKeys`, and `DatanodeInfo`. It integrates with DFS output stream/DataStreamer pipeline recovery and client write behavior.

## Risks and Edge Cases
Invalid policy strings throw `HadoopIllegalArgumentException`. The default condition is sensitive to integer division and append/hflush flags. `DISABLE` and `NEVER` both refuse replacement but differ in `checkEnabled` semantics and config enable state.

## Test Signals
DFS output stream and pipeline recovery tests cover integration. Unit tests should cover each policy, replication/existing-node thresholds, append/hflush overrides, best-effort config, and invalid config values.

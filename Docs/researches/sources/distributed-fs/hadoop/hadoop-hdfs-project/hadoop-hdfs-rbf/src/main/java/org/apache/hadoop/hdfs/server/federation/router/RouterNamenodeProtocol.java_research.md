<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterNamenodeProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterNamenodeProtocol.java

## Purpose
`RouterNamenodeProtocol` implements selected `NamenodeProtocol` calls through the router, mainly for operations that can be proxied to one available namespace or targeted to the namespace containing a datanode. Many checkpoint/secondary-NameNode style operations are deliberately unsupported.

## Important APIs, Types, and Functions
The constructor captures `RouterRpcServer` and `RouterRpcClient`. Implemented methods include `getBlocks`, `getBlockKeys`, `getTransactionID`, `getMostRecentCheckpointTxId`, `getMostRecentNameNodeFileTxId`, and `versionRequest`. Unsupported or no-op methods include `rollEditLog`, subordinate namenode registration, checkpoint start/end, edit-log manifest, upgrade/rolling-upgrade flags, and SPS path retrieval.

## Control Flow
`getBlocks` checks read access, asks the router for datanode storage reports across namespaces, finds the namespace whose report contains the input datanode UUID, and invokes `NamenodeProtocol.getBlocks` on that namespace. Namespace-agnostic reads build a `RemoteMethod` for `NamenodeProtocol` and call `rpcServer.invokeAtAvailableNs`. Restricted unsupported methods still call `checkOperation` with `false` for operation support before returning null/false or doing nothing.

## State and Persistence Behavior
The class is stateless beyond collaborator references. It reads datanode reports and delegates protocol calls; it does not persist or cache protocol results.

## Dependencies and Integration Points
Dependencies include `NamenodeProtocol`, `RouterRpcServer`, `RouterRpcClient`, `RemoteMethod`, `DatanodeStorageReport`, `DatanodeInfo`, `NamespaceInfo`, `ExportedBlockKeys`, and NameNode operation categories.

## Risks
`getBlocks` returns `null` if the datanode UUID is not found, so callers must handle missing routing. Datanode report retrieval can be expensive and stale. Unsupported checkpoint-related methods may not satisfy components expecting a real NameNode. Methods returning `false` for upgrade state may hide actual namespace-specific state if called unexpectedly.

## Test Signals
Tests should cover datanode-to-namespace resolution, no-match return behavior, `RemoteMethod` protocol/signature correctness, invocation at available namespace, operation-category enforcement, and explicit unsupported method behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterNamenodeProtocol.java -->

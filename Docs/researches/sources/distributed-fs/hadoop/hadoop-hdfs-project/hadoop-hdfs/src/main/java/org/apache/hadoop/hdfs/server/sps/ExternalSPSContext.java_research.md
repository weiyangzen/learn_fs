<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSContext.java

## Purpose

`ExternalSPSContext` adapts an externally running `StoragePolicySatisfier` to NameNode and DFS services. It supplies file metadata, storage policy lookup, datanode topology, SPS path polling, block-move submission, hint cleanup, and metrics registration.

## Important APIs and types

The class implements `Context`. It owns `SPSService service`, `NameNodeConnector nnc`, default `BlockStoragePolicySuite`, `ExternalSPSFilePathCollector`, `ExternalSPSBlockMoveTaskHandler`, `ExternalBlockMovementListener`, and optional `ExternalSPSBeanMetrics`. Methods include `isRunning`, `isInSafeMode`, `getNetworkTopology`, `isFileExist`, `getStoragePolicy`, `removeSPSHint`, `getNumLiveDataNodes`, `getFileInfo`, `getLiveDatanodeStorageReport`, `getNextSPSPath`, `scanAndCollectFiles`, `submitMoveTask`, `notifyMovementTriedBlocks`, and metrics helpers.

## Control flow

The external service creates this context, then SPS asks it for NameNode state as work progresses. It converts inode IDs to reserved file-ID paths, uses DFS clients through `NameNodeConnector`, builds a `NetworkTopology` from target DataNodes, delegates scans to the collector, delegates moves to the external handler, and records attempted movement blocks in an internal listener.

## State and persistence behavior

Runtime state is mostly references, a default policy suite, an in-memory list of attempted movement blocks, and JMX registration. Persistent HDFS effects occur when it removes the SPS xattr hint or when delegated block moves change placement.

## Dependencies and integration points

It bridges `StoragePolicySatisfier`, `NameNodeConnector`, DFS client APIs, `BlockStoragePolicySuite`, `NetworkTopology`, `DatanodeStorageReport`, and ExternalSPS metrics.

## Risks and test signals

Risks include `closeMetrics()` NPE if metrics were never initialized, safe-mode errors being treated as false, XAttr removal swallowing IOExceptions when the hint disappears, and unbounded attempted-block list growth. Tests should cover file-ID path conversion, missing files, safe mode failures, xattr removal races, storage reports, metrics lifecycle, and move-task delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSContext.java -->

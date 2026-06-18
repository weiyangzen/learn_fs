# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStoragePolicySatisfierWithHA.java

## Purpose

`TestStoragePolicySatisfierWithHA` validates that Storage Policy Satisfier mode cannot be dynamically changed on a standby NameNode in an HA cluster.

## Important APIs, Types, and Functions

The class builds a simple HA `MiniDFSCluster` with three DataNodes, two storages per DataNode, all-DISK storage types, configured capacities, and `DFS_STORAGE_POLICY_SATISFIER_MODE_KEY` set to `EXTERNAL`. It calls `NameNode.reconfigurePropertyImpl` and expects `ReconfigurationException`.

## Control Flow

`createCluster` configures block size, SPS mode, and a short SPS DataNode cache refresh interval, then starts HA topology and transitions NN0 active. The test transitions NN0 to standby, waits for cluster activity, tries to reconfigure SPS mode from `EXTERNAL` to `NONE`, and asserts the high-level and cause messages.

## State and Persistence Behavior

Cluster state includes HA NameNode role transitions and runtime reconfiguration state. No namespace data is written; the important persistent-style contract is that standby nodes must not start or stop SPS service through reconfiguration.

## Dependencies and Integration Points

It integrates HA state management, `MiniDFSNNTopology.simpleHATopology`, storage type/capacity cluster builder paths, and the NameNode reconfiguration subsystem for SPS configuration.

## Risks and Edge Cases

Allowing SPS mode changes on standby could desynchronize service lifecycle from HA role ownership. The test only covers disabling `EXTERNAL` on standby, not all possible SPS mode transitions.

## Test Signals

The expected signal is `ReconfigurationException` containing the attempted property change plus a cause mentioning that enabling or disabling SPS on standby is not allowed.

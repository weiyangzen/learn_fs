# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestDiskBalancer.java

## Purpose

`TestDiskBalancer` is the broad integration suite for DataNode disk balancer planning and execution. It validates NameNode topology discovery, end-to-end block movement, federated clusters, bandwidth delay computation, multi-step balancing, behavior with one empty nameservice, and resilience when a volume is removed during plan execution.

## Important APIs and types

- `DiskBalancerCluster`, `ConnectorFactory`, and `DiskBalancerDataNode` discover and model cluster topology.
- `NodePlan`, `DiskBalancerWorkStatus`, `DiskBalancerWorkItem`, and `DiskBalancer.VolumePair` represent execution plans and state.
- `DataNode.submitDiskBalancerPlan`, `queryDiskBalancerPlan`, and `getDiskBalancerStatus` exercise the DataNode RPC/JMX-facing surface.
- `DiskBalancer.DiskBalancerMover.computeDelay` enforces bandwidth throttling.
- Nested `ClusterBuilder` and `DataMover` construct imbalanced clusters, generate plans, execute them, and verify results.

## Control flow

The connectivity test starts two DataNodes, reads cluster info from the NameNode connector, matches model fields to the live DataNode ID/IP/host/volume count, then shuts down a DataNode and checks `getDiskBalancerStatus()` returns an empty string instead of throwing.

End-to-end tests create one-node clusters with multiple storage volumes and many blocks, move all blocks to one source disk, compute a plan from current cluster info, submit it, parse JMX status JSON, wait for `PLAN_DONE`, verify every volume has data, and check tolerance against planned bytes. Variants cover federated two-namespace data, one empty nameservice with expected log output for null next block, and three disks producing two plan steps.

The compute-delay test spies the dataset and uses a mocked work item with 10 MB/s bandwidth to assert 20 MB copied in 1.2 seconds yields an 800 ms delay. The disk-removal test spies mover execution, pauses after work-plan creation, reconfigures `dfs.datanode.data.dir` to remove one disk, resumes copy, waits for `PLAN_DONE`, and asserts disk errors stay within the configured maximum.

## State and persistence behavior

The suite creates real MiniDFSCluster storage, writes files, moves blocks across volumes, restarts DataNodes, submits background disk balancer plans, reads JMX-style status JSON, captures logs, and reconfigures DataNode data directories. Block movement persists to local test data directories.

## Dependencies and integration points

It integrates HDFS file creation, NameNode topology reporting, federation, DataNode volume references, disk balancer planning, DataNode plan submission, JMX status serialization, mover throttling, live reconfiguration, and block iterators.

## Risks and edge cases

- End-to-end waits are time-based and can be slow or flaky under constrained IO.
- Helpers directly move blocks before planning, which bypasses normal workload-driven imbalance creation.
- Tolerance verification uses block counts and planned bytes approximation.
- Disk-removal handling uses Mockito spies and latches, tightly coupling to mover internals.

## Test signals

Strong signals are live topology matching, real block movement to completion, parsed status consistency, final `PLAN_DONE`, all-volumes-have-data checks, federated block-pool handling, expected empty-nameservice log, multi-step plan count, exact compute-delay math, and bounded error count during volume removal.

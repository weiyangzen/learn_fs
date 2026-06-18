# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDFSZKFailoverController.java

## Purpose
`TestDFSZKFailoverController` validates DFS-specific ZooKeeper Failover Controller behavior for HA NameNodes. It covers auto failover, manual failover, bind-address selection, observer-state interaction, thread-dump capture on health changes, and startup with HDFS-backed credential-provider configuration.

## Important APIs, Types, And Functions
Key types include `DFSZKFailoverController`, `ZKFailoverController`, `ClientBaseWithFixes`, `MiniDFSCluster`, `MiniDFSNNTopology`, `ZKFCTestUtil`, `HealthMonitor`, `AlwaysSucceedFencer`, `HATestUtil`, `NamenodeProtocols`, and `TestingThread`. `startCluster()` creates a non-ephemeral-port HA topology, formats ZK, starts one ZKFC per NameNode, waits for health, and configures a failover-aware `FileSystem`.

## Control Flow
`setup()` configures a nameservice-scoped ZK quorum, fencer, auto failover, low IPC idle timeout, and explicit ZKFC ports. `startCluster()` starts nn1 and nn2, formats ZK, starts `ZKFCThread` instances, waits for nn1 to become active and both monitors to become healthy, then creates a failover filesystem. Tests shut down active NameNodes, restart nodes, call ZKFC proxies for graceful failover, invoke `DFSHAAdmin`, and poll both NameNode service state and ZKFC-local state with `GenericTestUtils.waitFor`.

## State, Persistence, And Dependencies
State spans the external test ZooKeeper from `ClientBaseWithFixes`, MiniDFSCluster NameNode process state, ZKFC election state, fencer last-target state, and actual HDFS namespace paths. Threads are managed through `TestContext` and interrupted in teardown. The static block disables edit-log fsync for speed.

## Integration Points
The test connects HDFS HA, ZooKeeper election/health monitoring, fencing, DFSHAAdmin, Web/IPC bind-address config, credential providers, and observer-state access control. It verifies that Observer NameNodes reject ZKFC-originated standby transitions and avoid active election.

## Risks
The tests depend on local port availability despite using `ServerSocketUtil.getPort`, and on timing-sensitive failover and health monitor polling. `System.in` is replaced in manual observer transition tests and must be restored on exceptional paths. ZooKeeper state and ZKFC threads require robust cleanup to avoid cross-test interference.

## Test Signals
Signals include NameNode HA state reaching ACTIVE/STANDBY/OBSERVER, successful file existence across failovers, fencer last-target addresses, expected RPC bind host, intercepted `AccessControlException`, captured ZKFC thread dump state, and election participation flags.

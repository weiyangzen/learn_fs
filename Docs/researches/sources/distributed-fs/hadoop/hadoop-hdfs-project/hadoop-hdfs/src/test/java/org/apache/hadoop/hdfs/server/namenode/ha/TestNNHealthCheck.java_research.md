# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestNNHealthCheck.java

## Purpose
`TestNNHealthCheck` verifies health-monitor RPC behavior for HA NameNodes, including use of lifeline addresses, explicitly provided target addresses, resource-unavailable failures, and optional reporting of safe mode as unhealthy.

## Important APIs, Types, And Functions
Tests are `testNNHealthCheck`, `testNNHealthCheckWithLifelineAddress`, `testNNHAServiceTargetWithProvidedAddr`, and `testNNHealthCheckWithSafemodeAsUnhealthy`. Helper `doNNHealthCheckTest` installs `MockNameNodeResourceChecker` and obtains `NNHAServiceTarget.getHealthMonitorProxy`. The test uses `DFS_NAMENODE_LIFELINE_RPC_ADDRESS_KEY`, `DFS_NAMENODE_RPC_ADDRESS_KEY`, `HA_HM_RPC_TIMEOUT_KEY`, and `DFS_HA_NN_NOT_BECOME_ACTIVE_IN_SAFEMODE`.

## Control Flow
The basic tests start a no-DataNode HA cluster, replace NN0's resource checker, build an `NNHAServiceTarget`, assert its string contains the chosen RPC or lifeline address, call `monitorHealth` successfully, then set resources unavailable and expect a `HealthCheckFailedException` either directly or wrapped in `RemoteException`. The safe-mode test enables safe-mode-unhealthy behavior, enters safe mode through the filesystem, obtains the health monitor proxy, and expects a remote exception with the configured message.

## State And Persistence
The state under test is NameNode health-monitor RPC endpoint selection, resource-checker availability, lifeline address configuration, and safe mode status. There is no important persistent namespace state.

## Dependencies And Integration Points
Dependencies include `MiniDFSCluster`, `MiniDFSNNTopology`, `NNHAServiceTarget`, `HAServiceProtocol`, `MockNameNodeResourceChecker`, `DFSUtil`, `LambdaTestUtils`, and safe mode filesystem APIs. The tests connect ZKFC-style health monitoring to NameNode resource and safe-mode status.

## Risks
Incorrect address selection can make ZKFC monitor the wrong RPC endpoint. Misreporting safe mode or resource exhaustion can cause unsafe failover decisions. Exception wrapping differs between local and remote paths, so the test accepts both direct and wrapped health failures where appropriate.

## Test Signals
Signals include target string containing the expected address, successful initial `monitorHealth`, expected message `The NameNode has no resources available` after resource failure, exact provided-address getters, and expected safe-mode-unhealthy remote exception text.

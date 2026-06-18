# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelShortCircuitLegacyRead.java

## Purpose
This subclass runs the shared parallel-read workload against the legacy short-circuit local block reader path, with TCP reads disabled so the local path is mandatory.

## Important APIs, Types, And Functions
`setupCluster` sets `DFSInputStream.tcpReadsDisabledForTesting`, clears `DFS_DOMAIN_SOCKET_PATH_KEY`, enables `DFS_CLIENT_USE_LEGACY_BLOCKREADERLOCAL`, disables domain-socket data traffic, enables short-circuit reads, keeps checksum verification enabled, sets `DFS_BLOCK_LOCAL_PATH_ACCESS_USER_KEY` to the current short username, disables domain socket bind-path validation, and delegates to the base setup with replication one.

## Control Flow
The class does only lifecycle setup/teardown. Once configured, inherited tests run copying, direct, mixed, and no-checksum workloads through the legacy local reader. `@AfterAll` shuts down the base cluster.

## State And Persistence
State is the process-global `DFSInputStream.tcpReadsDisabledForTesting` toggle plus legacy block-reader configuration. It has no persistence behavior.

## Dependencies And Integration Points
It integrates `DFSInputStream`, legacy `BlockReaderLocal`, local path access user configuration, `UserGroupInformation`, and `DomainSocket.disableBindPathValidation`.

## Risks
The static TCP-disable flag can leak between tests if teardown does not restore it elsewhere in the suite. The test depends on local filesystem access permissions and current user short name. Empty domain-socket path behavior is specific to the legacy local reader path.

## Test Signals
Signals are inherited parallel-read correctness with TCP disabled and legacy short-circuit enabled, demonstrating the workload can complete only through the intended local block-reader path.

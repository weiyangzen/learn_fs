# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestRouterHandlersFairness.java

## Purpose
`TestRouterHandlersFairness` is an integration test for router RPC fairness enforcement under real `DFSClient` calls. It verifies that configured controllers reject overloaded requests and release permits on exceptional paths.

## Important APIs, Types, and Functions
The parameterized test matrix covers `StaticRouterRpcFairnessPolicyController` and `ProportionRouterRpcFairnessPolicyController`. It uses `StateStoreDFSCluster`, `RouterConfigBuilder`, `RouterRpcClient`, `DFSClient`, `ClientProtocol`, `RemoteMethod`, `RemoteLocation`, `getAcceptedPermitForNs()`, `getRejectedPermitForNs()`, and `getRouterRpcFairnessPolicyController()`.

## Control Flow
`setupCluster()` starts a two-nameservice state-store cluster with RPC enabled, optional fairness controller class configured, a short acquire timeout, and no datanodes. `startLoadTest()` runs concurrent fan-out (`renewLease`) and sequential (`getFileInfo`) operations. When fairness is enabled, the test pre-acquires all relevant permits to force overload, checks `StandbyException` messages and rejected metrics, releases permits, then verifies later calls succeed and accepted metrics advance. `testReleasedWhenExceptionOccurs()` injects a mocked `ActiveNamenodeResolver` into `RouterRpcClient` so resolver failures occur after acquisition paths are entered, then confirms semaphore counts return to their original values.

## State and Persistence
State lives in the mini cluster, router RPC client permit counters, fairness controller semaphores, and state-store-backed resolver data. No durable files are written.

## Dependencies and Integration Points
This class exercises production routing paths across `RouterRpcServer`, `RouterRpcClient`, active namenode resolver ordering, client protocol RPCs, and metrics counters. It depends on reflection to replace a private resolver field for exception-path testing.

## Risks and Test Signals
The test uses real threads, sockets, and timeouts; failures can be timing-related. Reflection against `RouterRpcClient.namenodeResolver` is brittle under refactors. Strong signals include overload exceptions containing "is overloaded for NS", accepted/rejected metric deltas matching operation counts, and permit availability unchanged after resolver exceptions.

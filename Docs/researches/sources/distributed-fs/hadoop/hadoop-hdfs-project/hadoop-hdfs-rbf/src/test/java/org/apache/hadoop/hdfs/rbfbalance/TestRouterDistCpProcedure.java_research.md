# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/rbfbalance/TestRouterDistCpProcedure.java

This class specializes the shared `TestDistCpProcedure` for Router federation. It verifies that `RouterDistCpProcedure.disableWrite` can mark an RBF mount point read-only during a federation balance flow.

Global setup starts a `StateStoreDFSCluster` with state-store, admin, and RPC services, registers an active `ns0` namenode report, refreshes caches, and records the Router admin address in `routerConf`. The overridden `testDisableWrite()` adds `/test-write -> ns0:/test-write`, reloads the mount-table cache, creates a `DFSClient` to the Router RPC URI, builds a `FedBalanceContext`, executes `RouterDistCpProcedure.disableWrite(context)` at `Stage.FINAL_DISTCP`, and asserts that subsequent `mkdirs` under the mount fails with a read-only mount-point exception.

State is the Router state store, mount-table cache, test mount record, and procedure execution state from the superclass harness. Dependencies include `RouterDistCpProcedure`, `FedBalanceContext`, `DistCpProcedure.Stage`, `MountTableManager`, `DFSClient`, and HA state reports.

Risks include reliance on exact RemoteException text, testing only disable-write behavior rather than full DistCp copy/commit behavior here, and a single-router setup. The test signal is integration coverage between federation-balance DistCp procedure logic and Router mount-table read-only enforcement.

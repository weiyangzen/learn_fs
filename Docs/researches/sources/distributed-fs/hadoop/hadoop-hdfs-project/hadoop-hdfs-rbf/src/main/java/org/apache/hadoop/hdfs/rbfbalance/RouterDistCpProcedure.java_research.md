# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/rbfbalance/RouterDistCpProcedure.java

Purpose: Router-specific `DistCpProcedure` that freezes writes through mount-table readonly state before the final DistCp phase.

Important APIs and types: constructors mirror the parent, `disableWrite(FedBalanceContext)`, and `enableWrite()`.

Control flow: when the parent DistCp workflow asks to disable writes, this procedure reads `conf` and `mount` from `FedBalanceContext`, calls `MountTableProcedure.disableWrite`, and advances its stage to `Stage.FINAL_DISTCP`. `enableWrite()` intentionally does nothing because write re-enablement happens after the mount-table switch in `MountTableProcedure`.

State and persistence: inherits DistCp procedure state. It updates persistent Router mount-table readonly state through `MountTableProcedure`.

Dependencies and integration points: used as the first procedure in `RouterFedBalance` jobs. It depends on fedbalance `DistCpProcedure` stage semantics and Router mount-table admin RPC.

Risks: if later procedures fail, the mount can remain readonly until recovery or manual intervention. The no-op `enableWrite` is intentional but makes procedure ordering critical. Tests should verify stage transitions, readonly state changes, and recovery behavior after failures between DistCp and mount update.

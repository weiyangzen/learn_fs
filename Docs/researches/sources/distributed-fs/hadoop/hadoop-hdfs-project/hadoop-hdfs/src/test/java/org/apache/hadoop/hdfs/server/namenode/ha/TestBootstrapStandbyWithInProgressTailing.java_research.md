# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestBootstrapStandbyWithInProgressTailing.java

## Purpose

`TestBootstrapStandbyWithInProgressTailing` specializes the QJM bootstrap-standby tests to verify bootstrap works when in-progress edit tailing is enabled but RPC tailing is limited to one transaction per call.

## Important APIs, Types, and Functions

The class extends `TestBootstrapStandbyWithQJM` and overrides `createConfig`. It sets `DFS_HA_TAILEDITS_INPROGRESS_KEY=true` and `dfs.ha.tail-edits.qjm.rpc.max-txns=1`.

## Control Flow

All inherited QJM bootstrap tests run with the overridden configuration. This forces bootstrap tailing to retrieve in-progress edits through multiple small RPC calls instead of one large call.

## State and Persistence Behavior

State behavior is inherited from the QJM tests: NameNode storage, QJM journal edits, and upgrade directories are created and bootstrapped. The only local mutation is configuration.

## Dependencies and Integration Points

It specifically integrates `BootstrapStandby`, QJM in-progress edit tailing, and the per-RPC max transaction limit introduced for tailing.

## Risks and Edge Cases

If bootstrap assumes all required in-progress edits fit in one RPC, inherited tests fail under this configuration. The class has no tests of its own, so coverage depends entirely on inherited methods.

## Test Signals

Signals are inherited test success under one-transaction tailing: standbys bootstrap from active or standby QJM sources and upgrade-related bootstrap flows still pass.

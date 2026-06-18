# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestDisableRouterQuota.java

## Purpose

`TestDisableRouterQuota` verifies that the Router quota subsystem is consistently disabled when the Router is configured with `RouterConfigBuilder().quota(false).rpc()`. It is a focused guard around `Quota` behavior exposed through `RouterRpcServer`, ensuring admin-side and client-side quota paths fail with the same disabled-quota message.

## Important APIs, types, and functions

The test owns a static `Router` lifecycle in `setUp()` and `tearDown()`. `checkDisableQuota()` asserts `router.isQuotaEnabled()` is false before each test. `testSetQuota()` calls `Quota.setQuota(path, nsQuota, ssQuota, storageType, checkMountEntry)` twice, covering both `checkMountEntry=false` for `RouterAdminServer#synchronizeQuota` and `checkMountEntry=true` for `RouterClientProtocol#setQuota`. `testGetQuotaUsage()` calls `Quota.getQuotaUsage()`, and `testGetGlobalQuota()` calls `Quota.getGlobalQuota()`. `LambdaTestUtils.intercept` and `GenericTestUtils.assertExceptionContains` are the primary assertion helpers.

## Control flow

The class starts a real Router bound to an ephemeral RPC address, assigns a router id, and starts services. Each test fetches the quota module from `router.getRpcServer().getQuotaModule()` and asserts that quota APIs throw `IOException` containing `The quota system is disabled in Router.` No federated cluster or state store is involved.

## State and persistence behavior

The only persistent state is in-memory Router service state. The test does not write mount-table records or quota records. Its key state signal is the Router config bit that disables quota before RPC service startup.

## Dependencies and integration points

The file integrates `Router`, `RouterRpcServer`, `Quota`, `RouterConfigBuilder`, and `RBFConfigKeys.DFS_ROUTER_RPC_ADDRESS_KEY`. It protects the contract that all quota entry points honor the top-level Router quota switch.

## Risks and test signals

The test is sensitive to exact exception text. It is valuable for catching partial quota-disable regressions, especially if future changes bypass `Quota` checks in admin synchronization or client protocol paths. Because it uses a single Router without a state store, it does not validate disabled quota behavior through full `RouterAdmin` CLI or persisted mount-table quota metadata.

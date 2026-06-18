# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestDiskBalancerRPC.java

## Purpose

`TestDiskBalancerRPC` validates DataNode disk balancer RPC-facing methods: plan submission, validation failures, cancellation, settings lookup, status query, and direct block movement across volumes.

## Important APIs and types

- `DataNode.submitDiskBalancerPlan`, `cancelDiskBalancePlan`, `queryDiskBalancerPlan`, and `getDiskBalancerSetting` are the primary RPC-like methods.
- `DiskBalancerException.Result` distinguishes invalid hash, invalid version, invalid plan, no such plan, and unknown setting.
- `DiskBalancerWorkStatus.Result` values include `NO_PLAN`, `PLAN_UNDER_PROGRESS`, and `PLAN_DONE`.
- `RpcTestHelper` builds a `NodePlan` using `ConnectorFactory`, `DiskBalancerCluster`, `DiskBalancerDataNode`, and `GreedyPlanner`.
- `DigestUtils.sha1Hex(plan.toJson())` computes the accepted plan hash.

## Control flow

Setup enables disk balancer and starts two DataNodes. Most tests call `RpcTestHelper.invoke`, which restarts DataNode 0, reads cluster topology, selects that DataNode, balances its DISK volume set into a `NodePlan`, sets plan version one, and hashes the JSON. Submission with matching hash/version succeeds. Mutated hash, incremented version, and empty plan content each throw the expected `DiskBalancerException.Result`.

Cancellation succeeds after a valid submit; cancellation with a mutated or empty hash yields `NO_SUCH_PLAN`. Settings tests parse the volume-name JSON into a map and expect two entries, reject an unknown setting, and verify the bandwidth setting reports `10` after a submitted plan. Query tests distinguish submitted from no-plan state. The movement test creates a one-node cluster with a file, moves all blocks from one volume to another using `DiskBalancerTestUtil`, and asserts the source volume is empty.

## State and persistence behavior

The tests create real clusters and submit real DataNode disk balancer plans, though most validation is at the RPC/plan level rather than waiting for long movement. The movement test mutates on-disk block placement. `tearDown` shuts down the current cluster.

## Dependencies and integration points

This file connects DataNode RPC surface validation, plan hashing/versioning, disk balancer settings serialization, planner output, and dataset volume movement. It complements mock-mover tests by exercising DataNode wrappers.

## Risks and edge cases

- Some tests create a new cluster inside a method while setup already created one, increasing lifecycle complexity.
- Query after submit accepts either under-progress or done, reflecting asynchronous execution.
- Volume mapping assertion checks count but not path-to-UUID correctness.
- Plan generation depends on current cluster topology being imbalanced enough to create steps.

## Test signals

Strong signals are accepted valid plan submission, explicit result codes for invalid hash/version/plan/cancel/setting, volume mapping JSON parse, bandwidth setting decode, query status before and after submit, and source volume block count zero after direct movement.

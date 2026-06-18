# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestDiskBalancerWithMockMover.java

## Purpose

`TestDiskBalancerWithMockMover` tests the `DiskBalancer` coordinator with a controllable `BlockMover` implementation. It focuses on enablement checks, plan submission lifecycle, duplicate submission rejection, old and invalid plans, cancellation, invalid hashes, custom bandwidth propagation, and background execution without relying on real block copies.

## Important APIs and types

- `DiskBalancer.queryWorkStatus`, `submitPlan`, and `cancelPlan` are under test.
- `TestMover implements DiskBalancer.BlockMover` and exposes sleep, delay, runnable, exit, and run-count controls.
- `DiskBalancerWorkStatus` and `DiskBalancerWorkItem` expose result and per-step bandwidth.
- Helper builders create `DiskBalancer`, load a JSON disk balancer cluster resource, and build a `NodePlan` with live test volume paths and UUIDs.
- `DigestUtils.sha1Hex` computes plan IDs.

## Control flow

Setup starts a three-DataNode cluster with two storage volumes per DataNode and records DataNode UUID plus source/destination volume paths and storage IDs. Disabled and enabled tests build a `DiskBalancer` around `TestMover` and assert disabled query throws `DISK_BALANCER_NOT_ENABLED` while enabled query reports `NO_PLAN`.

The mock helper restarts the DataNode, creates a runnable `TestMover`, loads `/diskBalancer/data-cluster-3node-3disk.json`, generates a greedy plan for the current node ID, and rewrites plan step volume names and UUIDs to match live volumes. Submission tests verify a stuck mover causes second submit to throw `PLAN_ALREADY_IN_PROGRESS`, a normal submit eventually reaches `PLAN_DONE` and increments run count, plans older than 32 hours are rejected, version zero is rejected, null plan JSON is rejected, and a mutated hash is rejected.

The cancellation test submits a sleeping plan, cancels it, verifies `PLAN_CANCELLED`, submits again, and verifies cancelling with a wrong hash throws `NO_SUCH_PLAN`. The custom bandwidth test sets every `MoveStep` bandwidth to 100, submits the plan, and asserts the current work item carries that bandwidth.

## State and persistence behavior

Cluster storage exists but block movement is mocked. Disk balancer state is in-memory inside the `DiskBalancer` instance: current plan ID, status, background worker, and work entries. `TestMover` state is controlled by atomics/volatile fields and run count. Cluster shutdown occurs after each test.

## Dependencies and integration points

The file integrates plan JSON resources, planner output, live DataNode volume identity, `DiskBalancer` lifecycle validation, background worker status, and bandwidth propagation to work items.

## Risks and edge cases

- Mock mover does not validate actual block movement or dataset side effects.
- Sleep-based stuck-plan control must be cleared to avoid lingering background work.
- The cancellation test places cleanup calls inside a lambda after the expected exception path, so those statements are not reached when the wrong-hash cancellation throws.
- The plan resource must stay consistent with helper assumptions about disk layout.

## Test signals

Strong signals are explicit exception result codes for disabled, duplicate, old, invalid-version, null-plan, invalid-hash, and wrong-cancel cases; eventual `PLAN_DONE` with mover run count; `PLAN_CANCELLED`; and work-item bandwidth equal to custom step bandwidth.

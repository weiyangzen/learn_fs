# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockManagerFaultInjector.java

## Purpose
`BlockManagerFaultInjector` is a test-only seam for injecting faults around block manager operations. Production behavior is intentionally inert: the singleton instance methods are no-ops unless tests replace `instance` with a subclass or mock.

## Important APIs, Types, and Functions
The class exposes a visible-for-testing static `instance`, `getInstance()`, and four visible-for-testing hook methods: `incomingBlockReportRpc(DatanodeID, BlockReportContext)`, `requestBlockReportLease(DatanodeDescriptor, long)`, `removeBlockReportLease(DatanodeDescriptor, long)`, and `mockAnException()`. `incomingBlockReportRpc` can throw `IOException`; the others are void no-ops by default.

## Control Flow
Callers obtain the singleton with `BlockManagerFaultInjector.getInstance()` and invoke hooks at specific protocol points. In `BlockManager`, lease hooks are called after requesting and removing block report leases, and `mockAnException()` is invoked in heartbeat update paths. The hook object can be swapped by tests to force exceptions, delays, or observations without changing production code paths.

## State and Persistence Behavior
The only state is the mutable static singleton. There is no persistence and no synchronization around replacement. Default methods do not mutate state.

## Dependencies and Integration Points
The injector depends on HDFS block-management datanode descriptors plus protocol identifiers `DatanodeID` and `BlockReportContext`. Its integration points are narrow but important because they sit near block report lease management, incoming block report RPC processing, and heartbeat update code.

## Risks
Because `instance` is public static and mutable for tests, tests must restore it to avoid cross-test contamination. The class has no concurrency protection, so simultaneous tests in the same JVM can interfere. Production callers should not rely on side effects from the default implementation.

## Test Signals
Useful tests replace `instance` with a custom injector that throws from `incomingBlockReportRpc` or `mockAnException()`, records lease IDs from request/remove hooks, and verifies block manager behavior under injected report or heartbeat failures. Test cleanup should reset `instance` to a new default injector.

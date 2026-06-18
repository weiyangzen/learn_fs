<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/BreakableService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/BreakableService.java

## Purpose
Provides a controllably failing `AbstractService` implementation for service-lifecycle tests. It can fail during init, start, or stop and tracks how many times each lifecycle state was reached.

## Important APIs, Types, And Functions
Extends `AbstractService` and overrides `serviceInit`, `serviceStart`, and `serviceStop`. Public controls are constructors, `setFailOnInit`, `setFailOnStart`, `setFailOnStop`, `getCount`, and nested exception type `BrokenLifecycleEvent`.

## Control Flow
Each lifecycle override increments the count for the target state, optionally throws `BrokenLifecycleEvent` through `maybeFail`, and otherwise delegates to the superclass implementation. Failure happens before the superclass transition logic, matching the class comment.

## State And Persistence
State is in-memory booleans for failure injection and an integer count array indexed by `Service.STATE.ordinal()`. No external persistence exists.

## Dependencies And Integration Points
Depends on Hadoop `AbstractService`, `Service.STATE`, and `Configuration`. It is a reusable fixture for service lifecycle and listener tests.

## Risks
The count array assumes the enum ordinal range fits four entries; changes to `Service.STATE` ordering or size would break it. Failures are runtime exceptions, which may differ from checked-exception paths in production services.

## Test Signals
Downstream tests can assert state counts, expected thrown `BrokenLifecycleEvent`, and service state after failed or successful lifecycle calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/BreakableService.java -->

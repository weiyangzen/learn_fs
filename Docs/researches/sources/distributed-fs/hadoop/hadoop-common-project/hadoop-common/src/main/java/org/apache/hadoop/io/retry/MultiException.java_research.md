<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/MultiException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/MultiException.java

## Purpose
`MultiException` is an `IOException` wrapper for returning multiple keyed exceptions from a call so retry policy can evaluate all underlying failures.

## Important APIs and Types
The constructor accepts a `Map<String, Exception>`. `getExceptions` exposes that map. `toString` returns the map's `toString`.

## Control Flow
`RetryInvocationHandler.RetryInfo.newRetryInfo` detects `MultiException`, iterates its exception values, asks the retry policy about each, selects the most severe retry decision, and uses the maximum retry delay among non-fail decisions.

## State and Persistence
The instance stores a reference to the provided map without copying. It has no other state.

## Dependencies and Integration Points
It depends on `IOException` and `Map`, and is consumed by retry invocation handling.

## Risks and Edge Cases
Because the map is not defensively copied, external mutation can change exception contents after construction. Empty maps cause retry aggregation to produce no action, which would be unsafe if not prevented by callers. The class does not set a message or cause on `IOException`.

## Test Signals
Tests should cover aggregation of fail/retry/failover decisions, delay selection, map mutation behavior, empty-map handling expectations, and string output with keyed exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/MultiException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/CallReturn.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/CallReturn.java

## Purpose
`CallReturn` is the internal result envelope for one retry invocation attempt. It distinguishes returned values, thrown exceptions, retry scheduling states, and async in-progress states without throwing immediately through the retry loop.

## Important APIs and Types
The `State` enum includes `RETURNED`, `EXCEPTION`, `RETRY`, `WAIT_RETRY`, `ASYNC_CALL_IN_PROGRESS`, and `ASYNC_INVOKED`. Static singleton instances represent non-value states. Constructors wrap successful return values or throwables. `getReturnValue` rethrows stored exceptions and asserts returned state.

## Control Flow
`RetryInvocationHandler.Call.invokeOnce` and `AsyncCallHandler.AsyncCall.isDone` switch on `State` to decide whether to return to the caller, retry, wait, or keep polling.

## State and Persistence
Each instance stores at most one return value or one throwable plus a state. Preconditions reject simultaneous value and throwable. No persistent state exists.

## Dependencies and Integration Points
It depends on Hadoop `Preconditions` and is tightly coupled to `RetryInvocationHandler` and `AsyncCallHandler`.

## Risks and Edge Cases
`getReturnValue` throws if called for retry/async states, so all callers must check state first. Null is a valid return value but indistinguishable from internal null storage except by state. Exception state stores `Throwable`, not only `Exception`, preserving broader failures.

## Test Signals
Tests should cover state transitions in synchronous and asynchronous calls, exception rethrow, null successful return values, and precondition failures for invalid state/value access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/CallReturn.java -->

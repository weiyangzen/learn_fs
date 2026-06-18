<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/BreakableStateChangeListener.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/BreakableStateChangeListener.java

## Purpose
Provides a service-state-change listener fixture that records events and can deliberately fail when a service reaches a configured state.

## Important APIs, Types, And Functions
Implements `ServiceStateChangeListener.stateChanged`. Public methods expose event count, failure count, last service, last state, failing state setter, event-state list, and `toString`.

## Control Flow
On each `stateChanged` callback, the synchronized method increments event count, records the service and state, appends the state to `stateEventList`, and throws `BreakableService.BrokenLifecycleEvent` if the state equals `failingState`.

## State And Persistence
Maintains in-memory listener state: name, counts, last service/state, configured failing state, and a list of observed states. Accessors are mostly synchronized, though `getStateEventList` returns the mutable list directly.

## Dependencies And Integration Points
Depends on Hadoop `Service` and `ServiceStateChangeListener`. It pairs naturally with `BreakableService` in lifecycle tests.

## Risks
Returning the mutable event list can let callers mutate listener internals. The list itself is not synchronized when returned, so concurrent readers could race with callbacks. Failure behavior is tied to exact state equality.

## Test Signals
Tests can observe callback counts, last state/service, failure counts, ordered state events, and thrown `BrokenLifecycleEvent` when the configured failing state is reached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/BreakableStateChangeListener.java -->

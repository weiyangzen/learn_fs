<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateModel.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateModel.java

Source read size: 165 lines, 5021 bytes.

## Purpose
Small synchronized state machine that enforces legal Hadoop `Service` lifecycle transitions.

## Important APIs, Types, and Functions
Important methods are `getState()`, `isInState()`, `ensureCurrentState()`, `enterState()`, `checkStateTransition()`, `isValidStateTransition()`, and `toString()`. It stores the service name and current `Service.STATE`.

## Control Flow, State, and Persistence Behavior
Initial state is `NOTINITED`. `enterState()` validates transition unless the proposed state equals current, then updates state and returns the old state. Valid transitions include `NOTINITED -> INITED/STOPPED`, `INITED -> STARTED/STOPPED`, and `STARTED -> STOPPED`; `STOPPED` is terminal except re-entry. State is in-memory only.

## Dependencies and Integration Points
Used by `AbstractService` to implement lifecycle methods and by tests that directly validate state transition rules. Throws `ServiceStateException` for invalid states.

## Risks and Test Signals
Risks include transition-matrix drift from `Service` documentation and direct callers treating re-entry as a real transition. Test every valid/invalid transition, re-entry behavior, `ensureCurrentState()`, concurrent `enterState()` calls, and exception messages including service names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateModel.java -->

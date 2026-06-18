<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/LifecycleEvent.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/LifecycleEvent.java

Source read size: 43 lines, 1412 bytes.

## Purpose
Serializable data holder recording a service lifecycle transition time and resulting state.

## Important APIs, Types, and Functions
The class exposes public fields `time` and `state` and implements `Serializable`.

## Control Flow, State, and Persistence Behavior
There is no behavior beyond holding values. `AbstractService` creates one event after each real state transition and stores it in an in-memory history list.

## Dependencies and Integration Points
Depends on `Service.STATE`. Used by `Service.getLifecycleHistory()` for diagnostics and tests.

## Risks and Test Signals
Risks include public mutable fields and no serialVersionUID-specific compatibility guarantees beyond the declared id. Test signals are history entries after init/start/stop, timestamp ordering, state values, and defensive copying by `AbstractService.getLifecycleHistory()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/LifecycleEvent.java -->

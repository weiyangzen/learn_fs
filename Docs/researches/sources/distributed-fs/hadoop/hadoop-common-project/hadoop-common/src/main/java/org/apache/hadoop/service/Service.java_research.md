<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/Service.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/Service.java

Source read size: 225 lines, 6953 bytes.

## Purpose
Public lifecycle contract for Hadoop services. It defines legal states, lifecycle operations, configuration access, listener registration, failure diagnostics, lifecycle history, and blocker reporting.

## Important APIs, Types, and Functions
The `STATE` enum is `NOTINITED`, `INITED`, `STARTED`, and `STOPPED`. Methods include `init()`, `start()`, `stop()`, `close()`, `waitForServiceToStop()`, `getServiceState()`, `getName()`, `getConfig()`, `getStartTime()`, listener registration, `isInState()`, `getFailureCause()`, `getFailureState()`, `getLifecycleHistory()`, and `getBlockers()`.

## Control Flow, State, and Persistence Behavior
This interface defines behavior but owns no implementation. The documented lifecycle is initialize once, start once, stop once, with idempotent calls in existing states. Implementations such as `AbstractService` enforce transitions and maintain in-memory diagnostics.

## Dependencies and Integration Points
Core contract used by Hadoop daemons, composite services, launchers, shutdown hooks, and test utilities. Depends on `Configuration`, `LifecycleEvent`, and listener interfaces.

## Risks and Test Signals
Risks are implementer compliance: wrong transition handling, non-idempotent stop, blocking waits, or inconsistent failure metadata. Test any implementation against state transitions, listener callbacks, config availability, close delegating to stop, wait semantics, and immutable history/blocker snapshots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/Service.java -->

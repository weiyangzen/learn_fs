<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/AbstractService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/AbstractService.java

Source read size: 490 lines, 13995 bytes.

## Purpose
Base implementation of Hadoop's `Service` lifecycle. It provides synchronized state transitions, configuration storage, listener notifications, lifecycle history, failure recording, stop waiting, and blocker tracking.

## Important APIs, Types, and Functions
Implements `Service`. Public/final lifecycle APIs are `init()`, `start()`, `stop()`, `close()`, `waitForServiceToStop()`, state/failure/config accessors, listener registration, `isInState()`, and blocker getters. Subclass hooks are `serviceInit()`, `serviceStart()`, and `serviceStop()`.

## Control Flow, State, and Persistence Behavior
`init()` requires non-null config, enters `INITED`, sets config, invokes `serviceInit()`, and notifies listeners if still in `INITED`. `start()` enters `STARTED`, records start time, invokes `serviceStart()`, and notifies. `stop()` enters `STOPPED`, invokes `serviceStop()`, sets termination notification, wakes waiters, and notifies. Failures record first cause/state, call quiet stop for init/start failures, and convert exceptions to `ServiceStateException`. State is in `ServiceStateModel`; lifecycle events and blockers are in-memory only.

## Dependencies and Integration Points
Used throughout Hadoop services and by `CompositeService`, `ServiceLauncher`, and shutdown hooks. Depends on `Configuration`, `ServiceOperations.ServiceListeners`, `LifecycleEvent`, and `ServiceStateModel`.

## Risks and Test Signals
Risks include listener exceptions being swallowed, wait timeout semantics that return after one wait cycle, hooks that change state during callbacks, and static global listeners affecting tests. Test valid/invalid transitions, null config, hook failure cleanup, listener ordering/local/global notification, lifecycle history, wait/notify behavior, blocker map snapshots, and idempotent init/start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/AbstractService.java -->

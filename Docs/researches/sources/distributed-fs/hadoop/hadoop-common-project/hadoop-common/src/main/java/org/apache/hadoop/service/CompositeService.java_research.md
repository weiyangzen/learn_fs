<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/CompositeService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/CompositeService.java

Source read size: 190 lines, 6173 bytes.

## Purpose
Service implementation that owns a list of child services and initializes, starts, and stops them as a unit.

## Important APIs, Types, and Functions
Extends `AbstractService`. Key methods are `getServices()`, protected `addService()`, `addIfService()`, `removeService()`, `serviceInit()`, `serviceStart()`, `serviceStop()`, private `stop()`, and nested `CompositeServiceShutdownHook`.

## Control Flow, State, and Persistence Behavior
Child services are stored in a synchronized list. Initialization iterates a snapshot in insertion order and calls `init(conf)`. Start likewise starts in insertion order. Stop walks services in reverse order and, by default, stops both `STARTED` and `INITED` children. It records the first stop exception but continues stopping remaining children, then rethrows a converted exception. No persistent state is owned.

## Dependencies and Integration Points
Used by Hadoop daemons and compound subsystems. Integrates with `AbstractService` hooks, `ServiceOperations.stopQuietly()`, and JVM shutdown hooks.

## Risks and Test Signals
Risks include services added after init/start not being included in current snapshot, policy choice to stop `INITED` children, and first-exception-only reporting. Test ordering, reverse stop, partial start failure cleanup, remove behavior, addIfService with non-service objects, shutdown hook invocation, and stop continuing after child failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/CompositeService.java -->

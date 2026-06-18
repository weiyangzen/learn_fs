# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/TestCompositeService.java

Purpose: this JUnit 5 test suite validates `CompositeService` behavior around child ordering, failure rollback, stop policy, and dynamic service insertion. It is a behavioral contract for Hadoop services that aggregate child services.

Important APIs/types/functions: `CompositeService`, `Service.STATE`, `BreakableService`, `ServiceStateException`, local `ServiceManager`, `CompositeServiceImpl`, `CompositeServiceAddingAChild`, and `AddSiblingService`. `CompositeServiceImpl` records lifecycle call order and can throw on start/stop; `ServiceManager` exposes protected `addService`; `AddSiblingService` injects another service when its own state matches a trigger.

Control flow: baseline tests initialize, start, and stop five children, asserting init/start execute in registration order while stop executes in reverse order. Failure tests force a child start or stop exception and verify rollback/stop semantics. The long matrix adds children or siblings before init, during init/start/stop, and with child states `NOTINITED`, `INITED`, `STARTED`, or `STOPPED`, asserting which additions are managed, rejected, or left untouched.

State and persistence behavior: all state is in-memory service lifecycle state plus static call counters reset before each test. There is no persistence. The static `STOP_ONLY_STARTED_SERVICES` mirrors the implementation policy and changes expected stop behavior from `INITED`.

Dependencies and integration points: integrates directly with Hadoop service primitives and JUnit timeouts. It is a regression suite for `CompositeService.addService`, `addIfService`, `removeService`, parent lifecycle traversal, and exception-safe stop behavior.

Risks and test signals: the test matrix is broad but has fragile expectations tied to current stop policy and lifecycle side effects. Strong signals include explicit order counters, state assertions after every transition, reverse-stop verification, duplicate-stop no-op behavior, dynamic-add race coverage via timeouts, and exception rollback coverage.

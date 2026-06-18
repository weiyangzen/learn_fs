# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/TestServiceLifecycle.java

Purpose: validates core `AbstractService` lifecycle contracts: idempotent transitions, failure recording, listener notification, self-terminating services, and unusual transitions invoked inside lifecycle callbacks.

Important APIs/types/functions: `BreakableService`, `BreakableStateChangeListener`, `LoggingStateChangeListener`, `ServiceStateChangeListener`, `SubjectInheritingThread`, and local helper services `AsyncSelfTerminatingService`, `SelfTerminatingService`, `StartInInitService`, and `StopInInitService`.

Control flow: tests walk `NOTINITED -> INITED -> STARTED -> STOPPED`, then repeat `init/start/stop` to assert idempotence. Failure paths force exceptions in init, start, or stop and check final state, failure cause, and failure state. Listener tests register, unregister, self-unregister, and fail listeners while services transition. Async tests start a service thread that stops itself and wakes a waiting listener.

State and persistence behavior: state is the `AbstractService` in-memory lifecycle state, counters in `BreakableService`, listener event counts, failure cause/state, and short-lived thread state. No filesystem or durable state is used.

Dependencies and integration points: this is a direct integration test of Hadoop's service model and notification mechanics. It also exercises subject-inheriting thread startup for asynchronous stop behavior.

Risks and test signals: risk areas are re-entrant lifecycle calls (`start()`/`stop()` from `serviceInit` or `serviceStart`), listener mutation during callback, and failure propagation. Signals are explicit state-count assertions, event-count checks, wait/notify verification, and failure-cause validation.

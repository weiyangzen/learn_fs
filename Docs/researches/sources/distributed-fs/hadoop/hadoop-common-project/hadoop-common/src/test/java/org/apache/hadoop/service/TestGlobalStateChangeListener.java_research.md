# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/TestGlobalStateChangeListener.java

Purpose: verifies process-wide `AbstractService` global listener registration, de-registration, event dispatch ordering, and failure isolation semantics.

Important APIs/types/functions: `AbstractService.registerGlobalListener`, `AbstractService.unregisterGlobalListener`, `AbstractService.resetGlobalListeners`, `ServiceStateChangeListener`, `BreakableStateChangeListener`, `LoggingStateChangeListener`, and `BreakableService`. Helper methods wrap register/unregister and assert listener last-state/event-count fields.

Control flow: each test creates services and global listeners, drives `init/start/stop`, then checks listener observations. Double registration must collapse to one registration. Chain tests register several listeners, make one fail on `STARTED`, and verify earlier listeners see the transition while later listeners are skipped for that failing notification.

State and persistence behavior: global listener state is static process state and is reset in `@AfterEach`, which is essential to avoid cross-test contamination. Listener event counters, failure counters, and last-service references are in-memory only.

Dependencies and integration points: exercises global notification hooks in `AbstractService`, including interaction with local `BreakableService` state transitions and listener exceptions.

Risks and test signals: risks are shared static state and listener failure short-circuiting. Test signals include cleanup after every test, assertions that service state changes complete before listener failures surface, and verification that unregister order does not matter.

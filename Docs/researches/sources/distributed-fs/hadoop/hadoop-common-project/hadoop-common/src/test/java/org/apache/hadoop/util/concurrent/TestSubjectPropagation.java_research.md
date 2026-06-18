# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/concurrent/TestSubjectPropagation.java

Purpose: Tests security `Subject` propagation into Hadoop thread wrappers and ordinary Java threads. It documents why `SubjectInheritingThread` and `Daemon` preserve caller subject context even when plain thread inheritance behavior differs by Java runtime/security configuration.

Important APIs/types/functions: Tests use `SubjectUtil.callAs()`, `SubjectUtil.current()`, `SubjectInheritingThread`, `Daemon`, plain `Thread`, and `SubjectUtil.THREAD_INHERITS_SUBJECT`. `childSubject` captures what the child observes.

Control flow: Each test creates a parent `Subject`, enters it with `SubjectUtil.callAs()`, starts a child thread variant, joins up to one second, and asserts the captured subject. Wrapper tests use both override-style `work()` implementations and `Runnable` constructors. Plain `Thread` tests branch: if the runtime inherits subjects, assert equality; otherwise assert null.

State and persistence behavior: Only the instance field `childSubject` persists between parent and child execution. There is no durable state, but the tests rely on thread-local or inherited security context managed by `SubjectUtil`.

Dependencies and integration points: Depends on JAAS `Subject`, Hadoop `Daemon`, `SubjectInheritingThread`, and authentication `SubjectUtil`. These classes are central to Hadoop authorization behavior in background worker threads.

Risks: Tests call `join(1000)` without explicitly failing on timeout before subject assertion, so a stalled child produces null/equality failures rather than direct timeout diagnostics. Runtime behavior for plain threads changes across Java versions and SecurityManager settings; the branch intentionally captures that compatibility surface.

Test signals: Wrapper thread cases must always see the parent subject. Plain thread cases must match `THREAD_INHERITS_SUBJECT`, protecting both Hadoop-managed propagation and documentation of JVM-dependent behavior.

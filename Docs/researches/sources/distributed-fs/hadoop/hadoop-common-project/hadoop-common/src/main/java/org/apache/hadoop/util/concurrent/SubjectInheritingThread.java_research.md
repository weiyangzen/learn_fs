# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/SubjectInheritingThread.java

Purpose: `SubjectInheritingThread` restores JAAS `Subject` propagation for Hadoop-created threads on Java versions where plain `Thread` no longer inherits the current subject.

Important APIs/types/functions: constructors mirror common `Thread` constructors while storing the target in `hadoopTarget`. `start()` is final and captures `SubjectUtil.current()` when the runtime does not already inherit subjects. `work()` is the overridable payload method. `run()` is final and executes `work` under `SubjectUtil.doAs(startSubject, PrivilegedAction)` when needed.

Control flow: callers either pass a `Runnable` or subclass and override `work`. On start, the current subject is captured before the new thread begins. In the new thread, `run` wraps `work` with the captured subject unless `SubjectUtil.THREAD_INHERITS_SUBJECT` says the JVM already handles propagation.

State and persistence behavior: stores `startSubject` and `hadoopTarget` per thread object. No persistence beyond thread lifetime.

Dependencies and integration points: depends on JAAS `Subject`, `PrivilegedAction`, and Hadoop `SubjectUtil`. Search results show integration in configuration reconfiguration, metrics, Unix domain socket watcher/tests, HA stream pumping, IPC client/server threads, service launcher shutdown, and security tests.

Risks: subclasses must override `work`, not `run`; `run` is final to enforce subject restoration. Some constructors call a superclass constructor with a target for API compatibility but actual execution uses `hadoopTarget`, so behavior must stay aligned. Capturing subject in `start` means changes after construction but before start are honored.

Test signals: `TestSubjectPropagation` covers override and runnable modes. Broader tests should run on JVMs with and without native subject inheritance and verify nested/newly started threads observe expected subject.

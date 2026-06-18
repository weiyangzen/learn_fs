# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Daemon.java

Purpose: `Daemon` is a `Thread` subclass that is always daemonized and preserves JAAS `Subject` behavior on platforms where subjects are not inherited by threads.

Important APIs and types: constructors accept no runnable, runnable, or thread group plus runnable. `start` captures subject when needed, final `run` executes `work` under that subject, `work` runs the configured runnable, `getRunnable` exposes it, and nested `DaemonFactory` is a `ThreadFactory`.

Control flow: an instance initializer calls `setDaemon(true)`. `start` stores the current subject if thread inheritance is disabled. `run` either wraps `work` in `SubjectUtil.doAs` or invokes it directly.

State and persistence behavior: stores `startSubject` and `runnable`; no persistence.

Dependencies and integration points: used by executor factories and background Hadoop threads; integrates with `SubjectUtil` and JAAS `Subject`.

Risks: `run` and `start` are final, so subclasses must override `work` only. Runnable constructor names the thread using `runnable.toString()`, which may be unstable or verbose. Daemon threads do not keep JVM alive.

Test signals: cover daemon flag, runnable execution, work override, subject capture path, factory-created threads, thread group constructor, and name assignment.

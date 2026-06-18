# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ThreadUtil.java

Purpose: `ThreadUtil` provides thread sleep/join helpers and classpath resource loading with explicit error messages.

Important APIs/types/functions: `sleepAtLeastIgnoreInterrupts(long)` sleeps until wall-clock elapsed time reaches the requested duration while logging interruptions. `joinUninterruptibly(Thread)` repeatedly joins until the target terminates and restores interrupt status before returning. `getResourceAsStream(String)` uses the current thread context classloader; `getResourceAsStream(ClassLoader, String)` loads from an explicit classloader and throws `IOException` for null loaders or missing resources.

Control flow: sleep recomputes remaining time after every interrupt. Join loops until `Thread.join()` succeeds, tracks whether any interrupt occurred, and re-interrupts in `finally`. Resource loading validates the loader then checks for a null stream.

State and persistence behavior: stateless beyond logging. Methods may alter the current thread interrupt status on return from `joinUninterruptibly`.

Dependencies and integration points: depends on `Time.now` and SLF4J. `VersionInfo` uses the resource helpers; many daemon/test threads can use the join helper.

Risks: sleep uses wall-clock `Time.now`, so clock changes can distort elapsed sleep; monotonic time would be safer. Ignoring interrupts can delay shutdown. Resource streams are returned open and must be closed by callers.

Test signals: tests should cover interrupt restoration for joins, missing resource exceptions, null classloader exceptions, and sleep behavior under repeated interrupts.

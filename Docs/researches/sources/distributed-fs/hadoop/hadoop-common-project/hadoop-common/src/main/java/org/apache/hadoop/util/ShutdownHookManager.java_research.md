# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ShutdownHookManager.java

## Purpose
`ShutdownHookManager` provides deterministic Hadoop shutdown hook ordering by registering one JVM hook and running registered hooks sequentially from highest priority to lowest, with per-hook timeouts.

## Important APIs, Types, And Functions
Important members are singleton `MGR`, static single-thread `EXECUTOR`, `addShutdownHook` overloads, `removeShutdownHook`, `hasShutdownHook`, `isShutdownInProgress`, `clearShutdownHooks`, `executeShutdown`, `getShutdownHooksInOrder`, `getShutdownTimeout`, and nested `HookEntry`.

## Control Flow
Static initialization registers a `SubjectInheritingThread` JVM shutdown hook. During shutdown it atomically marks shutdown in progress, calls `executeShutdown`, logs timing, then shuts down the executor. `executeShutdown` sorts hooks by descending priority, submits each to the single-thread executor, waits for its configured timeout, cancels on timeout, and logs failures. Add/remove operations reject changes once shutdown begins.

## State And Persistence
Registered hooks live in a synchronized in-memory set. Shutdown progress is an `AtomicBoolean`. No persistence exists.

## Dependencies And Integration Points
It depends on Hadoop configuration keys for default shutdown timeout, `HadoopExecutors`, Guava `ThreadFactoryBuilder`, `SubjectInheritingThread`, and service/daemon cleanup code such as `RunJar` temp deletion.

## Risks
Hooks with equal priority run in nondeterministic order. `HookEntry.equals` uses runnable identity, so wrapper objects matter. Timeout cancellation requires hooks to honor interruption. Static executor lifecycle means test isolation needs care.

## Test Signals
Tests should cover priority ordering, timeout minimum enforcement, timeout cancellation count, exception logging without aborting later hooks, add/remove rejection during shutdown, duplicate hook identity, and executor termination behavior.

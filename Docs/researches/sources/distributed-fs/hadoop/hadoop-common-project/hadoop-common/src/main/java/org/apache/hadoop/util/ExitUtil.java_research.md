# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ExitUtil.java

## Purpose

`ExitUtil` centralizes JVM termination so Hadoop code can be tested or embedded without directly invoking `System.exit()` or `Runtime.halt()`. It can disable exits or halts, convert them to exceptions, remember the first attempted termination, and still perform real process termination when enabled.

## Important APIs, Types, And Functions

Important types are `ExitException` and `HaltException`, both `RuntimeException` classes implementing `ExitCodeProvider`. Control APIs include `disableSystemExit()`, `enableSystemExit()`, `disableSystemHalt()`, `enableSystemHalt()`, `resetFirstExitException()`, `resetFirstHaltException()`, `terminate(...)`, `halt(...)`, `haltOnOutOfMemory()`, and getters for the first captured exceptions.

## Control Flow, State, And Persistence

Static volatile flags gate real exit and halt calls. `terminate(ExitException)` logs nonzero status, captures logging failures as suppressed throwables, stores the first disabled-exit exception in an `AtomicReference`, and either throws it or calls `System.exit(status)`. `halt(HaltException)` mirrors this flow for `Runtime.getRuntime().halt(status)`. `haltOnOutOfMemory()` avoids normal cleanup and directly halts after best-effort stderr output. State is JVM-global and non-persistent.

## Dependencies And Integration Points

It depends on SLF4J and is annotated limited-private for HDFS, MapReduce, and YARN. Tools such as `NativeLibraryChecker` use it for testable process exit. Service launchers and tests rely on the disable flags to assert exit behavior.

## Risks And Test Signals

Global static flags can leak between tests unless reset. Logging itself can throw `Error`, and the code intentionally prioritizes errors over exit exceptions. Tests should cover real-disabled paths, first-exception capture, status propagation, suppressed exceptions, halt-vs-exit independence, and OOM halt behavior with minimal assumptions.

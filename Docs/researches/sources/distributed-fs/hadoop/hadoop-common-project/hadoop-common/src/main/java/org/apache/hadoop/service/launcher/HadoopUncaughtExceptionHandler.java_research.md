<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/HadoopUncaughtExceptionHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/HadoopUncaughtExceptionHandler.java

Source read size: 129 lines, 4390 bytes.

## Purpose
Default JVM uncaught exception handler for Hadoop service launchers. It logs uncaught failures and terminates or halts the process for serious `Error` conditions.

## Important APIs, Types, and Functions
Implements `Thread.UncaughtExceptionHandler`. Constructors optionally accept a delegate handler. The main API is `uncaughtException(Thread, Throwable)`.

## Control Flow, State, and Persistence Behavior
During JVM shutdown it only logs. Outside shutdown, `Error` triggers process termination: `OutOfMemoryError` prints to stderr and calls `ExitUtil.haltOnOutOfMemory()`, while other errors are converted to an `ExitException` through `ServiceLauncher` and terminated. Non-`Error` exceptions are logged and optionally delegated. No persistent state is owned.

## Dependencies and Integration Points
Intended for installation by launcher main methods. Integrates with `ShutdownHookManager`, `ExitUtil`, `ServiceLauncher.convertToExitException()`, and optional external exception handlers.

## Risks and Test Signals
Risks include abrupt termination bypassing cleanup, logging failures during fatal errors, and policy choice not to terminate on ordinary exceptions. Test shutdown-in-progress branch, OOM halt branch with exit utilities intercepted, generic Error conversion, simple Exception delegation, null delegate behavior, and logging resilience.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/HadoopUncaughtExceptionHandler.java -->

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SignalLogger.java

## Purpose
`SignalLogger` installs handlers for common UNIX termination signals so Hadoop logs which signal caused process exit before delegating to the previous handler.

## Important APIs, Types, And Functions
The enum singleton `INSTANCE` exposes `register(Logger)`. Internal `Handler` implements `SignalUtil.Handler`, stores the logger and previous handler, and handles `TERM`, `HUP`, and `INT`.

## Control Flow
`register` rejects repeated registration, marks registered, iterates the signal names, installs a new `Handler` through `SignalUtil.handle`, records successfully installed names, logs debug on failures, and logs the final registration list. On signal receipt, the handler logs an error with signal number/name and invokes the previous handler.

## State And Persistence
The singleton keeps a boolean `registered` flag. Installed signal handlers mutate JVM process signal state. There is no persistence.

## Dependencies And Integration Points
It depends on SLF4J, Hadoop annotations, and `SignalUtil`'s dynamic bridge to `sun.misc.Signal`.

## Risks
The registered flag is not synchronized, so concurrent registration can race. If the previous handler is null or problematic, delegating may fail. Signal APIs are non-standard and may be unavailable under some JVMs/modules/platforms.

## Test Signals
Tests should cover single-registration enforcement, successful and failed signal installations, log content on handler invocation, delegation to previous handler, and behavior when `sun.misc.Signal` bindings are unavailable.

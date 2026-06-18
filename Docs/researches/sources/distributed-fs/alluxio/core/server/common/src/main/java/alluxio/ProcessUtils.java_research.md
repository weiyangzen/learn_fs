## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/ProcessUtils.java

### Purpose
`ProcessUtils` contains daemon lifecycle helpers for running processes, fatal exits, shutdown hooks, and diagnostic dumps on exit or failover.

### Important APIs, Types, And Functions
`run(Process)` logs environment/version, starts the process, dumps diagnostics, and exits 0; on uncaught throwable it tries to stop the process, dumps diagnostics, and exits -1. `fatalError` logs or throws in test mode, dumps diagnostics, and exits. `stopProcessOnShutdown` adds a shutdown hook. `dumpInformationOnExit` and `dumpInformationOnFailover` write metrics and thread stacks. Private `dumpMetrics` and `dumpStacks` write timestamped files.

### Control Flow
Exit dumping only runs for process types in `COLLECT_ON_EXIT` (`MASTER`, `WORKER`) and when config enables it. A synchronized `sInfoDumpOnExitCheck` prevents duplicate exit dumps. Failover dump is asynchronous and returns futures, with metrics submitted before stacks to race less with shutdown.

### State And Persistence
Static state includes `COLLECT_ON_EXIT`, `sInfoDumpOnExitCheck`, and a date formatter. Persistent side effects are JSON metrics files and text stack dump files under `LOGS_DIR`.

### Dependencies And Integration Points
Depends on Alluxio configuration, metrics servlet object mapper, metrics registry, runtime constants, `CommonUtils.PROCESS_TYPE`, thread utilities, Guava `Throwables`, and Java executors. Used by server `main` methods and failover handling.

### Risks
The methods call `System.exit`, so tests must set `TEST_MODE` where fatal paths are exercised. Diagnostic dumping can fail due to log directory permissions or serialization issues. Shutdown hook and normal exit paths can race; the synchronized guard only protects exit dump, not process stop.

### Test Signals
No direct tests in this subset. Integration tests around daemon startup/shutdown and failover diagnostics are the likely coverage.

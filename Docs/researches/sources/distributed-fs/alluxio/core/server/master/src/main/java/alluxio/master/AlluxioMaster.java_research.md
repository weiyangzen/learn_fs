<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioMaster.java

## Purpose
Main entry point for the core Alluxio master process. It validates command-line usage, sets process type, constructs the configured master process, registers shutdown handling, and runs it.

## Important APIs, Types, And Functions
- `main(String[] args)` is the only operational API.
- `CommonUtils.PROCESS_TYPE` is set to `MASTER`.
- `AlluxioMasterProcess.Factory.create()` creates the concrete `MasterProcess`.
- `ProcessUtils.stopProcessOnShutdown` and `ProcessUtils.run` manage lifecycle and error handling.

## Control Flow
If arguments are present, the program logs the expected invocation and exits with `-1`. Otherwise it creates an `AlluxioMasterProcess`; construction failures are routed through `ProcessUtils.fatalError`. A shutdown hook is registered so journal resources close on termination, and `ProcessUtils.run` starts the process.

## State And Persistence Behavior
This class does not own persistent state. Its main state effect is setting global process type, which influences configuration/logging/metrics behavior, and ensuring shutdown closes journal-backed master state through the process lifecycle.

## Dependencies And Integration Points
Depends on Alluxio runtime constants, process utilities, common process-type state, SLF4J logging, and the master process factory. It is invoked by scripts or service managers launching the master JVM.

## Risks And Edge Cases
Any throwable during process creation is fatal because a partially initialized master cannot safely continue. Argument handling is intentionally strict.

## Test Signals
Coverage is typically indirect through process/factory integration tests and launch scripts. The critical signal is that a no-argument launch creates and runs a fully configured master process.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioMaster.java -->

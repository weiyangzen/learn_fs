## sources/distributed-fs/beegfs/storage/source/components/benchmarker/StorageBenchOperator.cpp

Purpose: Thin facade around `StorageBenchSlave` for storage benchmark control.

Important APIs/types/functions: Forwards `initAndStartStorageBench()`, `cleanup()`, `stopBenchmark()`, `getStatusWithResults()`, `shutdownBenchmark()`, and `waitForShutdownBenchmark()` to its `slave` member.

Control flow: No additional logic beyond delegation.

State and persistence: State resides in `StorageBenchSlave`, including benchmark files and runtime status.

Dependencies and integration: Used by `App` and storage benchmark control message handlers to avoid exposing the slave directly.

Risks and test signals: Facade has little risk; tests should focus on slave behavior and verify the operator preserves return values/status.

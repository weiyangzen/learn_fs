# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/AlluxioWorker.java

Purpose: `AlluxioWorker` is the worker process entry point.

Important API: `main(String[] args)`. Control flow rejects command-line arguments, verifies that a master host is configured, marks the process type as worker, creates a `MasterInquireClient`, loads cluster default configuration from the primary master with worker-scoped retry, creates a `WorkerProcess`, registers shutdown handling, and runs the process through `ProcessUtils`.

State and persistence include process-wide `CommonUtils.PROCESS_TYPE` and global configuration loaded from master. Dependencies include configuration utilities, retry utilities, master inquiry, server user state, and process utilities. Integration points are deployment scripts and the `WorkerProcess.Factory`, which returns `AlluxioWorkerProcess`. Risks include fatal exit on missing master/default configuration failure, startup coupling to primary master availability, and broad `Throwable` handling around process creation. No direct tests are in this subset.

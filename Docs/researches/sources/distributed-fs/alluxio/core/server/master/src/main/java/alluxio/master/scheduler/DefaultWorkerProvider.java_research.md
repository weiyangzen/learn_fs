# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/scheduler/DefaultWorkerProvider.java

Purpose: production `WorkerProvider` for scheduler jobs, sourcing worker metadata from `FileSystemMaster` and block worker clients from `FileSystemContext`.

Important APIs/types/functions: constructor stores `FileSystemMaster` and `FileSystemContext`; `getWorkerInfos` delegates to `FileSystemMaster.getWorkerInfoList`; `getWorkerClient` calls `FileSystemContext.acquireBlockWorkerClient`.

Control flow: scheduler calls `getWorkerInfos` during worker refresh, then opens clients for newly observed worker addresses. Checked `UnavailableException` becomes `UnavailableRuntimeException`; `IOException` from acquiring a block worker client becomes an `AlluxioRuntimeException`.

State and persistence: no internal mutable state and no persistence. Worker liveness and client pooling are handled by the file-system master and filesystem context.

Dependencies/integration: bridges `alluxio.scheduler.job.WorkerProvider` to master-side worker registry and block worker RPC client acquisition.

Risks: TODO notes that the provider returns all workers, not explicitly healthy-only workers. Client acquisition failures are escalated to runtime exceptions and the scheduler chooses whether to skip workers.

Test signals: verify unavailable master handling, IO-to-runtime conversion, and that returned worker list/client resources are exactly delegated.

# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMaster.java

## Purpose
`FileSystemMaster` is the central service contract for the Alluxio file-system master. It defines the namespace, metadata, mount-table, active-sync, worker-heartbeat, permission, persistence, and metadata-sync operations implemented by `DefaultFileSystemMaster` and exposed through client, worker, and job-service RPC handlers.

## Important APIs, types, and functions
The interface extends `Master`. User-facing metadata APIs include `getFileId`, `getFileInfo`, `listStatus`, streaming `listStatus`, `checkAccess`, `exists`, `checkConsistency`, `createFile`, `createDirectory`, `completeFile`, `delete`, `rename`, `free`, `setAcl`, `setAttribute`, and `scheduleAsyncPersistence`. Block/file location APIs include `getNewBlockIdForFile`, `getFileBlockInfoList`, `getInAlluxioFiles`, and `getInMemoryFiles`. Mount APIs include `mount`, `unmount`, `updateMount`, `getMountPointInfoSummary`, `getDisplayMountPointInfo`, `getUfsInfo`, `getUfsAddress`, `reverseResolve`, and `updateUfsMode`. Worker and maintenance APIs include `workerHeartbeat`, `getWorkerInfoList`, `cleanupUfs`, `validateInodeBlocks`, `getLostFiles`, `getPinIdList`, `getInodeCount`, and time-series access. Sync APIs include active sync start/stop/list, `activeSyncMetadata`, `recordActiveSyncTxid`, `needsSync`, synchronous and asynchronous `syncMetadata`, progress lookup, and cancellation.

## Control flow
This file has no implementation flow, but its method signatures define the control path for the master. RPC handlers translate protobuf requests into `AlluxioURI` and operation context objects, then call these methods. Implementations are responsible for permission checks, inode locking, journaling, block-master coordination, UFS access, and metadata loading. Several methods have internal-server semantics and TODOs for permission enforcement.

## State and persistence behavior
The contract covers persistent namespace state: inode metadata, completed-file state, ACLs, pinning, TTLs, persistence state, mount points, UFS mode, active-sync points and transaction ids, and lost-file markers. Mutating implementations must journal changes and coordinate block deletions or worker commands. Methods returning summaries or views expose snapshots rather than ownership of mutable state.

## Dependencies and integration points
The interface is consumed by `DefaultFileSystemMaster`, `FileSystemMasterFactory`, client/worker/job gRPC service handlers, scheduler/job submission, active sync, async persistence, TTL/lost-file checkers, block master, and web/UI or internal services that use `FileSystemMasterView`. It depends on Alluxio wire types, gRPC option contexts, exception hierarchy, security ACL types, UFS mode, and metadata sync response protos.

## Risks
Because this is the service boundary, signature changes ripple across generated RPC layers, tests, workers, and job services. Methods mix user-facing and internal operations, and comments note missing permission checks for some internal APIs. Sync and active-sync operations cross thread pools, UFS clients, journals, and inode locks, making cancellation and partial failure semantics important. Backward compatibility matters for exceptions and default option behavior.

## Test signals
Coverage is spread through `DefaultFileSystemMaster` tests, sync metadata tests, partial listing tests, permission tests, worker heartbeat tests, mount tests, job-service handler tests, and RPC handler tests. Contract-level signals are compile failures in handlers and mock implementations such as journal test helpers.

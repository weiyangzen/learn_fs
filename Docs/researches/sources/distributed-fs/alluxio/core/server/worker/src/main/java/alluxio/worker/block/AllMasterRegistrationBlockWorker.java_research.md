# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/AllMasterRegistrationBlockWorker.java

Purpose: `AllMasterRegistrationBlockWorker` is a `DefaultBlockWorker` variant that registers and syncs with all masters instead of only the primary.

Important APIs are constructor, `setupBlockMasterSync`, `start`, and `getBlockSyncMasterGroup`. Control flow delegates most setup to `DefaultBlockWorker`. `setupBlockMasterSync` creates an all-master `BlockSyncMasterGroup`, registers it for close, and starts it on the worker executor service. `start` calls `super.start(address)`, then waits for registration to complete on the primary master address obtained from the file-system master client; standby registration does not block worker startup.

State and persistence include the owned `BlockSyncMasterGroup` and inherited block worker state. Dependencies include `BlockMasterClientPool`, `FileSystemMasterClient`, `Sessions`, `BlockStore`, worker ID reference, and master sync group. Integration points are HA deployments with `WORKER_REGISTER_TO_ALL_MASTERS`. Risks include primary-address cast assumptions and startup waiting only on the primary, leaving standby convergence asynchronous. No direct tests are in this subset.

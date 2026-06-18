# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/AllMasterRegistrationBlockWorkerTest.java

## Purpose
`AllMasterRegistrationBlockWorkerTest` verifies startup registration behavior for `AllMasterRegistrationBlockWorker` when workers are configured to register with all masters.

## Important APIs, Types, and Functions
`before()` configures test mode, embedded journal, multi-master RPC addresses, and installs a `BlockSyncMasterGroup` factory returning the mocked block master client. `workerMasterRegistrationFailed()` makes primary registration throw and asserts startup fails with a fatal primary-master message. `workerMasterRegistration()` verifies normal startup.

## Control Flow, State, and Persistence
The test uses mocked clients and `DefaultBlockWorkerTestBase` state. It checks startup control flow rather than durable persistence.

## Dependencies and Integration Points
It integrates worker configuration, `AllMasterRegistrationBlockWorker`, `BlockSyncMasterGroup`, mocked block/file-system master clients, and worker startup.

## Risks and Test Signals
The strong signal is that primary-master registration failure is fatal. A stated gap is behavior when standby registration fails; the TODO notes a missing test for worker startup with standby failure.

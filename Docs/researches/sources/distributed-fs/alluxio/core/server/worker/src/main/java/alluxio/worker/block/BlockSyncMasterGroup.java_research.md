## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockSyncMasterGroup.java

### Purpose
`BlockSyncMasterGroup` manages per-master block synchronization when a worker registers to all masters. It creates one `SpecificMasterBlockSync` per configured master, registers each heartbeat reporter with the block store, starts heartbeat threads, and exposes registration-state checks.

### Important APIs and Types
- Constructor accepts master addresses and a `BlockWorker`.
- `start(ExecutorService)` submits heartbeat threads for each sync operator.
- `waitForPrimaryMasterRegistrationComplete(InetSocketAddress)` blocks until the primary sync is registered or fatally exits on timeout.
- `isRegisteredToAllMasters()` and `getMasterSyncOperators()` expose state.
- Nested `Factory.createAllMasterSync` obtains configured master RPC addresses.
- Nested `BlockMasterClientFactory` is test-injectable.

### Control Flow
For every master address, the constructor creates a `BlockMasterClient`, a new `BlockHeartbeatReporter`, registers that reporter as a block-store listener, and creates either `SpecificMasterBlockSync` or `TestSpecificMasterBlockSync` depending on test mode. `start` submits each sync to a `HeartbeatThread` with the worker block heartbeat interval.

### State and Persistence
State is an in-memory map of master address to sync operator and a volatile started flag. It persists nothing. Registration/heartbeat state lives in each `SpecificMasterBlockSync`.

### Dependencies and Integration Points
Used by all-master-registration worker mode. It integrates with `ConfigurationUtils`, `HeartbeatThread`, `BlockMasterClient`, `BlockWorker.getBlockStore`, and the `SpecificMasterBlockSync` implementation.

### Risks
- Master membership changes are explicitly TODO; the map is fixed at construction.
- `start` sets `mStarted` but still submits heartbeat threads on repeated calls after the first, since the submit loop is outside the guard.
- A heartbeat reporter is registered per master, so event fanout and memory grow with master count.

### Test Signals
`AllMasterRegistrationBlockWorkerTest` uses the test client factory and test syncs. `SpecificMasterBlockSyncTest` covers sync behavior below this grouping.

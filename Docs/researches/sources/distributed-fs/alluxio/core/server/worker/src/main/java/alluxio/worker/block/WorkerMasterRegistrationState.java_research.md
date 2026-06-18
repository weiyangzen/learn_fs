## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/WorkerMasterRegistrationState.java

### Purpose
`WorkerMasterRegistrationState` is the finite state enum for a worker’s registration lifecycle with a specific block master in all-master registration mode.

### Important APIs and Types
- Values: `NOT_REGISTERED`, `REGISTERING`, `REGISTERED`.

### Control Flow
`SpecificMasterBlockSync` starts at `NOT_REGISTERED`, sets `REGISTERING` during full registration, sets `REGISTERED` after successful registration, and resets to `NOT_REGISTERED` when a master requests registration or a heartbeat report is too large to retry incrementally.

### State and Persistence
The enum has no fields. Persistence is only the volatile enum field in `SpecificMasterBlockSync`.

### Dependencies and Integration Points
Used by `SpecificMasterBlockSync.isRegistered`, `heartbeat`, and registration methods.

### Risks
- The enum is intentionally minimal; any new intermediate/error states require changes to heartbeat control flow and tests.

### Test Signals
Registration state transitions are covered by `SpecificMasterBlockSyncTest` and all-master registration tests.

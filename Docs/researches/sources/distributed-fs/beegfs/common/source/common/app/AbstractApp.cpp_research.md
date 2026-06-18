<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/AbstractApp.cpp -->
## sources/distributed-fs/beegfs/common/source/common/app/AbstractApp.cpp

### Purpose
`AbstractApp.cpp` implements common application runtime services: PID-file locking/updating, component shutdown waiting, out-of-memory handling, global runtime initialization/destruction, NIC logging, NIC/route propagation, and no-default-route parsing.

### Important APIs, Types, And Functions
Key functions are `createAndLockPIDFile`, `updateLockedPIDFile`, `waitForComponentTermination`, `handleOutOfMemFromNew`, `performBasicInitialRunTimeChecks`, `basicInitializations`, `basicDestructions`, `logUsableNICs`, `updateLocalNicListAndRoutes`, and `initNoDefaultRouteList`. Static `didRunTimeInit` gates app construction through the header constructor.

### Control Flow
PID setup validates absolute paths before delegating to `StorageTk`. Component termination waits two seconds, logs if still running, then joins fully. OOM handling logs stderr and BeeGFS backtrace before throwing `std::bad_alloc`. Runtime checks validate time and condition-clock support, then initialize condition attributes. NIC updates optionally reload the routing table, replace the protected local NIC list, log capabilities, and apply the list to node stores.

### State, Persistence, And Dependencies
The only durable artifact is the PID file managed by `LockFD`. In-memory state includes static runtime initialization state, local NIC list, no-default-route filter, and routing table factory. Dependencies include `StorageTk`, `NodesTk`, `Time`, `Condition`, `NetworkInterfaceCard`, `NetFilter`, logging, and thread components.

### Integration Points
All concrete BeeGFS apps derive from `AbstractApp`. Listener code calls `PThread::getCurrentThreadApp()` to access config, message factories, routing tables, and component exception handling.

### Risks
Construction before `runTimeInitsAndChecks` throws. OOM handling itself uses logging and backtrace code that may allocate or depend on locks. `basicDestructions` runs from the base destructor, so derived classes must have stopped users of static condition state.

### Test Signals
Tests should cover PID path validation, locked PID update after daemonization, runtime init ordering, component join timeout logging, NIC update propagation to node stores, and invalid CIDR handling in `initNoDefaultRouteList`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/AbstractApp.cpp -->

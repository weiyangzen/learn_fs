<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/AbstractApp.h -->
## sources/distributed-fs/beegfs/common/source/common/app/AbstractApp.h

### Purpose
This header defines the abstract base class for BeeGFS userspace applications and the runtime services exposed to common components.

### Important APIs, Types, And Functions
Concrete apps must implement `stopComponents`, `handleComponentException`, `handleNetworkInterfaceFailure`, `getCommonConfig`, `getNetFilter`, `getTcpOnlyFilter`, and `getNetMessageFactory`. The base exposes PID helpers, component wait, NIC logging, runtime initialization through `runTimeInitsAndChecks`, routing table initialization/update/access, and optional `getStreamListenerByFD`.

### Control Flow
The protected constructor verifies static runtime initialization and installs the global `new` handler. `runTimeInitsAndChecks` performs checks, initializes shared threading condition state, then marks the process ready for app construction.

### State, Persistence, And Dependencies
State includes `localNicList`, `localNicListMutex`, optional `noDefaultRouteNets`, and a `RoutingTableFactory`. The class derives from `PThread`, making the main app itself a thread context.

### Integration Points
Common components use this as their access point for configuration, filters, routing, message factories, and failure escalation. RDMA device-removal handling and listener exception handling both reach concrete apps through this interface.

### Risks
The base destructor calls `basicDestructions`; derived shutdown order must ensure no component still needs those static resources. `getLocalNicList` returns a copy, which is safe but can become stale immediately.

### Test Signals
Compile-time tests should verify concrete app implementations satisfy pure virtual methods. Runtime tests should validate initialization ordering, local NIC list locking/copy behavior, and routing table creation with no-default-route filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/AbstractApp.h -->

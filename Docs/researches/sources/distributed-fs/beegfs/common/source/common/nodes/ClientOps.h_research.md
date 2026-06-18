<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/ClientOps.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/ClientOps.h

### Purpose
`ClientOps.h` declares storage and request helpers for per-client/per-user operation statistics.

### Important APIs, Types, And Functions
`ClientOps` defines `OpsList` and `IdOpsMap`, exposes `addOpsList()`, diff getters, absolute getters, and `clear()`. Protected helpers define sum/diff arithmetic and hold current/old maps plus a mutex. `ClientOpsRequestor` defines `IdOpsUnorderedMap` and static `request(Node&, bool perUser, bool useClientStatsV2)`.

### Control Flow
Consumers add absolute lists during collection, read absolute or diff views, then call `clear()` to advance the baseline.

### State, Persistence, And Dependencies
State is in-memory snapshots only. Dependencies include `IPAddress`, `Node`, and `Mutex`.

### Integration Points
Management statistics code combines `ClientOpsRequestor` network collection with `ClientOps` diff calculations.

### Risks
The arithmetic helpers use unsigned function signatures while lists store `int64_t`, so type conversion should be tested for large values. Tests should cover snapshot lifecycle and concurrent add/clear access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/ClientOps.h -->

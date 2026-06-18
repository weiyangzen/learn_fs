<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/RoutingTable.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/RoutingTable.h

### Purpose
`RoutingTable.h` declares immutable routing-table snapshots and the factory that loads them from the operating system.

### Important APIs, Types, And Functions
It defines `RoutingTableException`, `DestnetMap`, and `IpSourceMap`. `RoutingTable::match()` finds a source address for a destination and candidate local NIC list. `loadIpSourceMap()` computes a map for many peer NICs. `RoutingTableFactory` provides `init()`, `load()`, and `create()`.

### Control Flow
Public `RoutingTable` methods are const to support thread-safe immutable snapshots. The factory is mutable and synchronized around the current `DestnetMap`.

### State, Persistence, And Dependencies
`RoutingTable` holds shared pointers to const route data and optional default-route exclusion networks. The factory caches mutable route data in memory. Dependencies include `NetworkInterfaceCard`, `IPAddress`, mutexes, and standard maps.

### Integration Points
Networking setup code uses the factory to refresh OS routes and distribute snapshots to connection-selection code.

### Risks
Callers must call `RoutingTableFactory::init()` and `load()` before `create()`, and a default-constructed `RoutingTable` throws if used uninitialized. Tests should cover initialization ordering, thread-safe create/load behavior, and matching with empty/local NIC lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/RoutingTable.h -->

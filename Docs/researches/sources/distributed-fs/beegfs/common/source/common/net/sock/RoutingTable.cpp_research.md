<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/RoutingTable.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/RoutingTable.cpp

### Purpose
`RoutingTable.cpp` queries the OS routing table through libnl3, builds immutable destination-network-to-source-address mappings, and matches peer addresses to the best local NIC source address.

### Important APIs, Types, And Functions
`Destnet` stores an `IPNetwork` and source IP set. `RoutingTableQuery` abstracts route collection, with `Nl3RouteQuery` implementing libnl3 route/address cache access. `populateInterfaces()` maps interface indices to local IPs. `populateDestnetMap()` walks unicast routes, using preferred source addresses when present or nexthop interface addresses otherwise. `RoutingTable::match()` checks non-default routes first, then a default route unless blocked by `noDefaultRouteNets`. `loadIpSourceMap()` builds peer-to-source maps. `RoutingTableFactory::init()`, `load()`, and `create()` manage shared route snapshots.

### Control Flow
Factory `load()` creates a query, initializes libnl caches, builds a fresh `DestnetMap`, and swaps it in only when changed. Created `RoutingTable` instances hold shared immutable snapshots for thread-safe reads. Matching iterates routes, remembers a default route, and uses local NIC preference order to select a source address.

### State, Persistence, And Dependencies
Route data is cached in shared pointers and guarded by `destnetsMutex` during factory updates. No data is persisted. Dependencies include libnl3 route/address APIs, `IPAddress`, `IPNetwork`, `NetworkInterfaceCard`, logging, and BeeGFS exception macros.

### Integration Points
Connection pools and node route setup use routing tables to choose local source IPs for peer NICs.

### Risks
Route iteration order in an unordered map can affect which overlapping non-default route is considered first; longest-prefix selection is not explicit here. Some `if ((rc = call(...) != 0))` expressions assign boolean results instead of raw error codes, reducing diagnostics. Default-route filtering depends on `noDefaultRouteNets`. Tests should cover overlapping routes, preferred-source routes, nexthop-derived sources, IPv4/IPv6 separation, no-default-route filters, route reload change detection, and empty-route logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/RoutingTable.cpp -->

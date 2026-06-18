<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/NetworkInterfaceCard.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/NetworkInterfaceCard.cpp

### Purpose
`NetworkInterfaceCard.cpp` discovers usable local network interfaces, applies allow/deny preference rules, detects RDMA capability, sorts NICs, and formats NIC data.

### Important APIs, Types, And Functions
`findNicPosition()` matches preference rows against interface name, IP, protocol family, and type (`tcp`/`rdma`), with `!` rows acting as blacklists. `findAll()` discovers standard interfaces and optionally appends RDMA-capable variants. `findAllInterfaces()` wraps `getifaddrs()`, skips loopback/down/non-IP/link-local entries, honors IPv6 disablement, and applies allowed-interface filters. `filterInterfacesForRDMA()` and `checkAndAddRdmaCapability()` bind test RDMA sockets to candidate IPs. `NicAddrComp` sorts by preferences, then RDMA, IPv4, and IP order. Formatting and capability helpers expose type strings and RDMA support.

### Control Flow
Interface discovery first builds TCP candidates, then RDMA probing clones candidates as RDMA NICs when `RDMASocket` can bind. Preference matching can include wildcards and escaped literal `*`/`!` names; blacklist rows return `-1` immediately.

### State, Persistence, And Dependencies
There is no persistent state. Dependencies include `getifaddrs`, `ifaddrs`, `RDMASocket`, `LogContext`, `System`, `StringTk`, and BeeGFS NIC serialization types.

### Integration Points
Local node startup, connection-pool setup, route selection, and node serialization use discovered `NicAddressList` values.

### Risks
`findNicPosition()` assumes split rows have at least one token; empty preference rows could be unsafe depending on `StringTk::explode()` behavior. RDMA detection catches `SocketException` and silently skips interfaces, so diagnostics can be limited. Sorting prefers RDMA and IPv4 after explicit preferences, affecting connection choices. Tests should cover allow/deny rows, escaped names, IPv6 disabled mode, link-local exclusion, RDMA probing success/failure, and sorting stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/NetworkInterfaceCard.cpp -->

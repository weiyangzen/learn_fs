<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/IPAddress.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/IPAddress.h

### Purpose
`IPAddress.h` declares value types for normalized IP addresses, CIDR networks, network filters, and host/port socket addresses.

### Important APIs, Types, And Functions
`IPAddress` stores a 16-byte address, constructors accept IPv4, IPv6, sockaddr, sockaddr_storage, and uint128. It exposes family checks, loopback/link-local checks, conversions, comparisons, hashing, and string output. `IPNetwork` stores an address plus normalized prefix, with IPv4 prefixes shifted by 96 bits because IPv4 is mapped into IPv6 space. `SocketAddress` stores `IPAddress addr` and host-order `port`, with sockaddr conversion helpers.

### Control Flow
Most operations are value-object inline wrappers around implementation functions in the `.cpp`. Hash specialization allows `IPAddress` to key unordered maps.

### State, Persistence, And Dependencies
State is copied by value and not persisted. The header depends on system socket headers and BeeGFS `UInt128`.

### Integration Points
`NetworkInterfaceCard`, `RoutingTable`, `Socket`, `StandardSocket`, and `ClientOps` use these types for route matching, binding, peer naming, and client-ID conversion.

### Risks
IPv4 prefixes are internally offset by 96, so callers must use public constructors rather than directly reasoning about `getPrefix()` as a raw IPv4 prefix. `SocketAddress()` default construction is deleted, which requires immediate initialization. Tests should cover hash/equality, ordering, IPv4 prefix normalization, invalid prefixes, and string formatting with bracketed IPv6 ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/IPAddress.h -->

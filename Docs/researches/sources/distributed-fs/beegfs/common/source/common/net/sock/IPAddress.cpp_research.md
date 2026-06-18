<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/IPAddress.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/IPAddress.cpp

### Purpose
`IPAddress.cpp` implements IPv4/IPv6 address normalization, resolution, string conversion, CIDR network matching, and socket-address conversion.

### Important APIs, Types, And Functions
`IPAddress::resolve()` uses `getaddrinfo()` and prefers IPv4 over IPv6. `setAddr()` accepts `sockaddr`, IPv4, IPv6, and uint128 values. Query methods detect zero, IPv4-mapped, IPv6, loopback, and link-local addresses. Conversion methods produce uint128, IPv4 `in_addr`, string form, and `SocketAddress`. Helpers `extractPort()` and `sockAddrLen()` inspect raw sockaddr values. `IPNetwork::fromCidr()` parses CIDR strings and `containsAddress()` tests prefix membership. `SocketAddress` converts between BeeGFS address objects and `sockaddr_in`/`sockaddr_in6`.

### Control Flow
IPv4 addresses are stored as IPv4-mapped IPv6 (`::ffff:a.b.c.d`) in a 16-byte array. Network containment first rejects IPv4/IPv6 family mismatch, then compares bytes and bits up to the prefix. CIDR parsing validates prefix length separately for IPv4 and IPv6.

### State, Persistence, And Dependencies
All state is value-object memory. Dependencies include `getaddrinfo`, `inet_pton`, `inet_ntop`, socket address structs, and BeeGFS `uint128_t`.

### Integration Points
Sockets, NIC discovery, routing, client-op reporting, and serialization all use this address abstraction.

### Risks
`IPAddress::resolve()` prefers IPv4 even on IPv6-capable hosts, which affects connection selection. `isLinkLocal()` compares bytes against constants and should be tested carefully for network-byte layout. `containsAddress()` indexes `addr[bytePos]` after a full match; identical addresses return before a differing byte is found only through loop completion logic, so boundary tests matter. Tests should cover IPv4/IPv6 round-trips, CIDR parsing errors, default networks, mapped IPv4 behavior, loopback/link-local detection, and socket-address conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/IPAddress.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/Socket.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/Socket.cpp

### Purpose
`Socket.cpp` implements common socket base behavior: hostname connection resolution, wildcard binding, dummy stats setup, and global IPv6 capability detection/caching.

### Important APIs, Types, And Functions
`Socket::connect(hostname, port, ai_socktype)` resolves hostnames with `getaddrinfo()`, selects IPv4 or IPv6 based on cached IPv6 availability, formats `peername`, and delegates to `connect(SocketAddress)`. `bind(port)` binds to zero-address plus port. `checkAndCacheIPv6Availability()` probes IPv6 socket creation, loopback connect behavior, and dual-stack support; `isIPv6Available()` returns the cached value.

### Control Flow
Callers must initialize IPv6 availability before constructing code paths that call `isIPv6Available()`. Hostname connect sets canonical peer names and brackets IPv6 literal peer names. IPv6 probing honors explicit config disablement and logs fallback reasons.

### State, Persistence, And Dependencies
`dummyStats` is static fallback stats storage. `ipv6Available` is a static atomic optional cache. Dependencies include `getaddrinfo`, socket syscalls, `IPAddress`, logging, and BeeGFS config access.

### Integration Points
`StandardSocket` and RDMA/socket subclasses inherit this behavior. Startup code should call `checkAndCacheIPv6Availability()` before socket creation.

### Risks
`Socket::connect()` frees `addressList` before constructing `SocketAddress` from `addrSelected->ai_addr`, leaving `addrSelected` pointing into freed memory; this is a notable lifetime risk unless allocator behavior masks it. `isIPv6Available()` throws if the cache was not initialized. Tests should cover IPv6 disabled/unavailable/dual-stack cases, hostname IPv4/IPv6 resolution, peername formatting, and the address-list lifetime path under sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/Socket.cpp -->

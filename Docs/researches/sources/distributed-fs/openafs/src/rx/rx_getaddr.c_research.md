# Research: sources/distributed-fs/openafs/src/rx/rx_getaddr.c

## sources/distributed-fs/openafs/src/rx/rx_getaddr.c

### Purpose
`rx_getaddr.c` discovers local IPv4 interface addresses, masks, and MTUs for user-space and kernel/UKERNEL RX builds, with platform-specific paths for routing-socket/sysctl systems and ioctl-based systems.

### Important Functions
- `rxi_setaddr` and `rxi_getaddr` provide advisory address storage in kernel builds; user-space `rxi_setaddr` is a no-op.
- User-space `rxi_getaddr` returns the first address from `rx_getAllAddr`.
- `rx_getAllAddr_internal` enumerates addresses with loopback filtering.
- `rx_getAllAddr` returns non-loopback IPv4 addresses.
- `rx_getAllAddrMaskMtu` returns address, netmask, and MTU arrays, with defaults where platform APIs cannot provide them.
- Platform helpers include `rt_xaddrs`, `rxi_IsLoopbackIface`, and OpenBSD `ifm_fixversion`.

### Control Flow
On Darwin/XBSD-style systems, the code uses `sysctl` with `NET_RT_IFLIST`, parses `RTM_IFINFO` and `RTM_NEWADDR` messages, expands compact sockaddr lists, filters down/up/loopback interfaces, and records IPv4 addresses. `rx_getAllAddrMaskMtu` additionally opens a datagram socket to query interface MTU. On fallback systems, it opens an AF_INET datagram socket, calls `SIOCGIFCONF`, iterates `ifreq` entries with platform-specific sizing, filters AF_INET and loopback addresses, and optionally queries `SIOCGIFNETMASK`, `SIOCGIFMTU`, or `SIOCRIPMTU`.

### State and Persistence
No durable state. Kernel `rxi_tempAddr` is a global advisory value used for random/noise address approximation. User-space functions fill caller-provided arrays.

### Dependencies and Integration Points
Depends on `rx.h`, `rx_globals.h`, `rx_kcommon.h`, platform interface headers, `ioctl`, `sysctl`, and `rx_IsLoopbackAddr`. RX initialization and peer parameter selection use these addresses and MTUs.

### Risks and Edge Cases
- Many paths return `0` on failure, making "no interfaces" and "error" indistinguishable.
- Some error paths after opening sockets or allocating buffers may miss cleanup; for example routing-socket MTU code returns after socket failure without freeing the sysctl buffer.
- Loopback handling differs between normal and `loopbacks` modes and may skip aliased loopbacks specially.
- Fixed `NIFS` and caller `maxSize` limits truncate interface lists.
- IPv6 is not handled.

### Test Signals
Tests should run on representative platforms with multiple interfaces, loopback aliases, down interfaces, IPv4-only and no-interface scenarios, and MTU/netmask query failures. Static analysis should check cleanup paths.

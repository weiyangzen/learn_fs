# sources/distributed-fs/openafs/src/rx/rx_user.c

## Purpose
Implements user-space RX platform support: UDP socket creation, diagnostic/panic helpers, interface address/MTU discovery, local address enumeration, peer network parameter initialization, jumbo/MTU configuration, and optional Linux extended socket-error processing.

## Important APIs, Types, And Functions
Key functions are `rxi_GetHostUDPSocket`, `rxi_GetUDPSocket`, `osi_Msg`, `osi_Panic`, `osi_AssertFailU`, optional AIX `osi_Alloc`/`osi_Free`, Windows `rxi_getaddr`, `rx_getAllAddr`, `rx_getAllAddrMaskMtu`, `rx_GetIFInfo`, `rxi_InitMorePackets`, Unix `rxi_syscall`, `fudge_netmask`, `rxi_InitPeerParams`, `rx_SetNoJumbo`, `rx_SetMaxMTU`, and Linux `osi_HandleSocketError`. State includes interface arrays `rxi_NetAddrs`, `myNetMTUs`, `myNetMasks`, `myNetFlags`, `rxi_numNetAddrs`, and `Inited`, with pthread mutexes for interface initialization and data.

## Control Flow
`rxi_GetHostUDPSocket` validates reserved-port permissions, creates a UDP socket, initializes Windows transmit extensions when applicable, binds the requested host/port, sets close-on-exec, tries to enlarge send/receive buffers, configures Linux path-MTU/error-queue options, starts a listener with `rxi_Listen`, and returns the socket or closes it on error. `rx_GetIFInfo` lazily discovers interfaces: Windows delegates to `syscfg_GetIFInfo`; Unix uses `SIOCGIFCONF`, filters loopback/duplicates, reads flags, MTU, and netmask from syscalls/ioctls/fallback classful masks, updates maximum receive sizing, and preallocates continuation packet capacity for jumbo receives. `rxi_InitPeerParams` ensures interface discovery, matches peer address to local networks, sets timeout hints, computes interface/natural/max MTUs and datagram counts, optionally clamps with path MTU, and initializes slow-start fields.

## State And Persistence
State is in process memory: socket descriptors, interface caches, MTU globals, packet pool sizing, and peer transport parameters. `Inited` prevents repeated Unix interface scans; Windows can refresh addresses on each public query. No state is written to disk.

## Dependencies And Integration Points
The file depends on platform sockets/ioctls, `rx_globals.h`, `rx_stats.h`, `rx_peer.h`, `rx_packet.h`, `rx_internal.h`, packet allocation, listener startup, RX MTU helpers, and optional Linux `IP_RECVERR` handling. It is the user-mode counterpart to kernel RX network adapters.

## Risks And Test Signals
Risks include stale interface cache after address changes on Unix, incomplete bind retry behavior because the loop breaks after one bind attempt, platform-specific MTU ioctl differences, packet preallocation before RX locks are initialized, and path-MTU/error-queue portability. Test signals include binding privileged/unprivileged ports, listener startup, interface enumeration on multihomed hosts, loopback filtering, MTU clamping, jumbo disable/max MTU APIs, and Linux ICMP error processing.

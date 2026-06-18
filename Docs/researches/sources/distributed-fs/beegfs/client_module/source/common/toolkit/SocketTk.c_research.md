# sources/distributed-fs/beegfs/client_module/source/common/toolkit/SocketTk.c

## Purpose
Implements socket toolkit helpers for kernel polling, address parsing, and endpoint formatting.

## Important APIs and control flow
`SocketTk_initOnce` opens `/dev/null` as a dummy file pointer required by socket poll callbacks; `SocketTk_uninitOnce` closes it. `SocketTk_poll` multiplexes BeeGFS standard and RDMA sockets: it initializes poll wait queues, loops until events/timeout/fatal signal/error, calls RDMA or raw socket poll implementations, schedules interruptibly/killably, then runs RDMA cleanup and frees wait queues. `SocketTk_getHostByAddrStr` parses IPv4 into mapped IPv6 or native IPv6 and returns `INADDR_NONE`-mapped on failure. `SocketTk_in_aton` wraps that parser. `SocketTk_ipaddrToStr` and `SocketTk_endpointToStr` format IPv4-mapped and IPv6 addresses.

## State, dependencies, integration
Global state is `SocketTkDummyFilp`. Dependencies include `StandardSocket`, `RDMASocket`, Linux poll/scheduler APIs, `TimeTk`, and BeeGFS sockaddr helpers. Messaging and datagram code use these helpers for wait and logging paths.

## Risks and test signals
Polling depends on a successfully initialized dummy filp. The function mutates per-socket `poll.revents`, so callers should clear/add sockets through `PollState_addSocket`. Test timeout behavior, fatal-signal exit, RDMA cleanup calls, invalid address parsing, and IPv6 endpoint formatting.

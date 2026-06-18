<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/StandardSocket.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/StandardSocket.cpp

### Purpose
`StandardSocket.cpp` implements TCP/UDP/UNIX-domain socket behavior for the BeeGFS socket abstraction, including IPv4/IPv6 creation, connect with timeout, bind/listen/accept, shutdown, send/receive, epoll-based timed receive, socket options, and grouped UDP epoll handling.

### Important APIs, Types, And Functions
Constructors create AF_INET6 dual-stack sockets when available, otherwise AF_INET sockets, and optionally add the socket to an epoll set. `createSocketPair()` builds local UNIX socket pairs. `connect()` performs nonblocking connect with poll timeout. `bindToAddr()`, `listen()`, and `accept()` wrap server-side setup. `send()` requires full-length writes. `sendto()` retries `EPERM` UDP sends with cooling sleeps and suppresses repeated `ENETUNREACH`. `recv()`, `recvT()`, `recvfrom()`, and `recvfromT()` handle blocking and epoll receive. Option setters configure keepalive, reuseaddr, receive buffer, TCP_NODELAY, and TCP_CORK. `StandardSocketGroup` lets one epoll parent wait on subordinate sockets.

### Control Flow
Timed receives wait on epoll, recover from `EINTR`, and dispatch to the socket pointer stored in epoll event data. Listening sockets close their epoll FD because timed receive is not used on them. Shutdown sends `SHUT_WR` then drains until disconnect for graceful close.

### State, Persistence, And Dependencies
State is the OS file descriptor, epoll FD, socket family, peer/bind metadata, random backoff generator, and subordinate sockets. Dependencies include Linux sockets, epoll, poll, TCP options, logging, `System`, `PThread` config, and `IPAddress`.

### Integration Points
`NodeConnPool`, UDP datagram paths, local worker sockets, and the generic `Socket` interface rely on this implementation for standard networking.

### Risks
`send()` treats partial stream writes as fatal rather than looping, so callers must pass sizes appropriate for blocking sockets. `sendto()` uses a static `netUnreachLogged` flag without synchronization. `connect()` restores original flags only on success paths, so failure paths rely on destruction or later cleanup. `addToEpoll()` closes `sock` and `epollFD` on failure even when adding a subordinate, which can affect the owning group. Tests should cover IPv4 fallback, dual-stack bind, connect timeout/refusal, partial send simulation, UDP EPERM retry and ENETUNREACH suppression, epoll timeout/EINTR/HUP/ERR paths, socket option errors, socket-pair cleanup, and subordinate group lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/StandardSocket.cpp -->

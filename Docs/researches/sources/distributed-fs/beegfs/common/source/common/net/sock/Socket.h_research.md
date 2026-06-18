<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/Socket.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/Socket.h

### Purpose
`Socket.h` defines the abstract socket interface used by BeeGFS networking, covering connection setup, binding/listening/accepting, shutdown, send/receive, optional NVFS RDMA read/write, exact/min-max receive helpers, stats, and addressing metadata.

### Important APIs, Types, And Functions
Pure virtual methods define `connect()`, `bindToAddr()`, `listen()`, `accept()`, `shutdown()`, `shutdownAndRecvDisconnect()`, `send()`, `sendto()`, `recv()`, and `recvT()`. Inline helpers `recvExact()`, `recvExactT()`, `recvMinMax()`, and `recvMinMaxT()` repeatedly call receive methods until length conditions are met. Static methods manage IPv6 availability.

### Control Flow
Subclasses implement raw transport behavior while the base tracks stats pointer, socket type, peer/bind IPs, bind port, and peer name. Exact/min-max receive loops depend on subclass receive calls throwing on disconnect rather than returning negative values.

### State, Persistence, And Dependencies
State is per socket and in-memory only. It depends on `Channel`, `NetworkInterfaceCard`, `IPAddress`, `HighResolutionStats`, `Time`, and socket exception subclasses.

### Integration Points
`StandardSocket`, `RDMASocket`, `PooledSocket`, and connection pools use this as their common interface.

### Risks
Exact receive helpers can loop forever if a subclass returns zero without throwing for stream sockets. Stats pointer is mutable and not owned. Tests should cover helper loops, timeout behavior, stats incrementing in subclasses, and IPv6 initialization requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/Socket.h -->

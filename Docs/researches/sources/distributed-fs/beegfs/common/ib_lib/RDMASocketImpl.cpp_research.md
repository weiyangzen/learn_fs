<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/RDMASocketImpl.cpp -->
## sources/distributed-fs/beegfs/common/ib_lib/RDMASocketImpl.cpp

### Purpose
`RDMASocketImpl.cpp` adapts the C-style `IBVSocket` API to the BeeGFS `RDMASocket` C++ interface. It is the object used by the stream listener and connection pools when RDMA support is enabled.

### Important APIs, Types, And Functions
The file exports `beegfs_socket_impl` with callbacks for RDMA availability, `ibv_fork_init`, and socket allocation. `RDMASocketImpl` implements `connect`, `bindToAddr`, `listen`, `accept`, `shutdown`, `send`, `sendto`, `recv`, `recvT`, `checkConnection`, `nonblockingRecvCheck`, and `checkDelayedEvents`. Under `BEEGFS_NVFS` it also exposes synchronous RDMA read/write wrappers using remote buffer keys.

### Control Flow
Construction initializes default buffer count, buffer size, service level, and an underlying `IBVSocket`. Client connections resolve through `Socket::connect(host, port, SOCK_STREAM)` then `connect(SocketAddress)`, which calls `IBVSocket_connectByIP` and adopts the receive completion fd. Listening binds an RDMA CM id and switches `fd` to the connection-manager fd. Accept wraps successful `IBVSocket_accept` results in a new `RDMASocketImpl`; ignored RDMA internal events return null. Send paths require the full payload to be accepted or throw. Receive paths translate zero, timeout, and errors into BeeGFS socket exceptions.

### State, Persistence, And Dependencies
State is in the wrapped `IBVSocket*`, inherited peer/bind fields, socket stats, `fd`, and `IBVCommConfig`. There is no durable persistence. The file depends on `AbstractApp`, `System`, `PThread`, `StringTk`, `IPAddress`, `RDMASocket`, and the `IBVSocket` implementation.

### Integration Points
`beegfs_socket_impl` is the bridge used by BeeGFS RDMA socket factory code. `StreamListener` polls the fd returned here, calls `accept`, and uses `nonblockingRecvCheck` to distinguish real RDMA data from internal completion events.

### Risks
The adapter assumes `IBVSocket_send` sends all requested bytes; partial sends are fatal. `shutdownAndRecvDisconnect` does not wait for a peer disconnect despite its name. `setBuffers` and TOS only affect unconnected sockets. Statistics are updated only on successful user-visible sends/receives.

### Test Signals
Useful tests include RDMA device absence, connect/listen/accept with real or mocked RDMA CM events, partial-send failure injection, receive timeout mapping, delayed accept-event handling, and stream listener false-alarm handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/RDMASocketImpl.cpp -->

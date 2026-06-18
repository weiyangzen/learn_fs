<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/OpenTk_IBVSocket.h -->
## sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/OpenTk_IBVSocket.h

### Purpose
This header is the public C-style interface for the ibverbs socket abstraction consumed by `RDMASocketImpl`.

### Important APIs, Types, And Functions
It forward-declares `IBVSocket` and `IBVCommConfig`, defines `IBVSocket_AcceptRes`, declares construction/destruction, RDMA availability and fork initialization, connect/bind/listen/accept/shutdown, optional NVFS read/write, send/receive, connection checks, fd getters, TOS/timeouts setters, and test rejection controls. `IBVCommConfig` contains `bufNum`, `bufSize`, and `serviceLevel`.

### Control Flow
Callers construct a socket, configure buffers/timeouts/TOS before connecting or listening, then use the socket-like operations. Accept returns a tri-state result to distinguish real errors, ignored internal CM events, and successful connections.

### State, Persistence, And Dependencies
The interface hides all RDMA state behind opaque pointers. It depends only on BeeGFS `IPAddress` and system socket address declarations.

### Integration Points
This is the narrow boundary between BeeGFS common C++ sockets and the RDMA implementation library. It is included by `RDMASocketImpl.h` and compiled into `beegfs_ib`.

### Risks
The interface exposes raw pointers and C return codes, so callers must translate errors consistently and destroy sockets on every path. Buffer configuration comments are external to this header, so misuse after connection is possible.

### Test Signals
API tests should cover accept tri-state handling, fd getters before and after connection/listen, setter effects before connection, and optional NVFS builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/OpenTk_IBVSocket.h -->

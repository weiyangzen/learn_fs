<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/StandardSocket.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/StandardSocket.h

### Purpose
`StandardSocket.h` declares the concrete non-RDMA socket implementation and a grouped socket variant for epoll over multiple subordinate sockets.

### Important APIs, Types, And Functions
`StandardSocket` derives from `PooledSocket` and implements all `Socket` operations, UDP `recvfrom` variants, socket-option setters, `getFD()`, and `getFamily()`. Inline `waitForIncomingData()` wraps `poll()` for POLLIN/error checks. `StandardSocketGroup` creates subordinate sockets and uses the parent epoll FD to receive from any of them.

### Control Flow
Constructors decide whether an epoll FD exists. Methods that require epoll reject non-epoll instances. Subordinate sockets are created without their own epoll and added to the group's epoll set.

### State, Persistence, And Dependencies
State includes raw FD, datagram flag, epoll FD, address family, and random generator. Dependencies include `PooledSocket`, `RandomReentrant`, `IPAddress`, and system poll/socket types.

### Integration Points
Connection pools instantiate `StandardSocket` for TCP/UDP communication. UDP listener code can use `StandardSocketGroup` to listen across multiple local addresses.

### Risks
Inline `waitForIncomingData()` throws on `EINTR` instead of retrying, unlike epoll receive methods. `StandardSocketGroup` relies on closing epoll before subordinate destruction to avoid stale event pointers. Tests should cover poll error flags, non-epoll receive misuse, group subordinate dispatch, and destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/StandardSocket.h -->

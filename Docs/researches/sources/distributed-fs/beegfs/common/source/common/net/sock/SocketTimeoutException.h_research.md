<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketTimeoutException.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/SocketTimeoutException.h

### Purpose
`SocketTimeoutException.h` declares the socket timeout exception type.

### Important APIs, Types, And Functions
It uses `DECLARE_NAMEDSUBEXCEPTION(SocketTimeoutException, "SocketTimeoutException", SocketException)`.

### Control Flow
Timed receive methods throw this when epoll waits expire without input.

### State, Persistence, And Dependencies
Only exception message state is carried. It depends on `SocketException`.

### Integration Points
Request/response and connection-pool code catch timeouts to fail, retry, or mark peers as slow without conflating them with disconnects.

### Risks
Tests should confirm timeout exceptions are used by `recvT()`/`recvfromT()` and not by immediate nonblocking or connect timeout paths where `SocketConnectException` is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketTimeoutException.h -->

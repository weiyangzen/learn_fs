<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketDisconnectException.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/SocketDisconnectException.h

### Purpose
`SocketDisconnectException.h` declares the named exception type for established-socket disconnects and send/receive hard failures.

### Important APIs, Types, And Functions
It uses `DECLARE_NAMEDSUBEXCEPTION(SocketDisconnectException, "SocketDisconnectException", SocketException)`.

### Control Flow
`StandardSocket::recv()`, `send()`, `sendto()`, and related methods throw this when peers disconnect or syscalls fail after connection setup.

### State, Persistence, And Dependencies
Only exception text is stored. It depends on `SocketException`.

### Integration Points
Connection pools and request/response code catch disconnects to invalidate sockets and retry as appropriate.

### Risks
Tests should distinguish soft disconnect, hard disconnect, and connect-time exceptions so retry logic invalidates the correct pool entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketDisconnectException.h -->

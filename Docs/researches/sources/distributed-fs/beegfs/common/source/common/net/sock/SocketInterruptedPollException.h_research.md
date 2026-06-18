<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketInterruptedPollException.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/SocketInterruptedPollException.h

### Purpose
`SocketInterruptedPollException.h` declares the exception used when blocking poll-style waits are interrupted.

### Important APIs, Types, And Functions
It uses `DECLARE_NAMEDSUBEXCEPTION(SocketInterruptedPollException, "SocketInterruptedPollException", SocketException)`.

### Control Flow
Polling helpers can throw this on `EINTR` when they choose not to retry internally.

### State, Persistence, And Dependencies
Only exception message state is carried. It depends on `SocketException`.

### Integration Points
Callers can catch this separately when interruption should be treated differently from timeout or disconnect.

### Risks
Some epoll loops retry `EINTR` internally, so behavior differs by API. Tests should cover `waitForIncomingData()` interruption and caller retry policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketInterruptedPollException.h -->

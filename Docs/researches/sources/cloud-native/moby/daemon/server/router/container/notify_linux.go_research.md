# sources/cloud-native/moby/daemon/server/router/container/notify_linux.go

## Purpose
`notify_linux.go` provides Linux-specific connection-close notification support for hijacked container streams.

## Important APIs, Types, And Functions
`notifyClosed` accepts a `net.Conn` and callback, extracts a raw fd through `syscall.Conn`, creates an epoll fd through `unix_noeintr.EpollCreate`, registers `EPOLLHUP`, waits indefinitely, and calls `notify`.

## Control Flow
If the connection does not expose `SyscallConn`, or epoll setup/registration/wait fails, the function logs and returns. On success it blocks in `EpollWait` until hangup and then invokes the callback from inside `RawConn.Control`.

## State And Persistence
No persistent state is written. The function owns a temporary epoll fd and observes kernel state for a single connection.

## Dependencies And Integration Points
It depends on Linux epoll via `golang.org/x/sys/unix`, Moby's EINTR-safe unix wrappers, containerd logging, and callers in container attach/stream paths that need to detect a disconnected client.

## Risks
Blocking inside `RawConn.Control` is delicate because it pins raw fd access while waiting. Missing `EPOLLERR`/`EPOLLRDHUP` could miss some closure modes, and callback execution must be safe from the waiter goroutine.

## Test Signals
No direct unit tests are present; behavior is exercised indirectly by attach/exec stream disconnect integration tests on Linux.

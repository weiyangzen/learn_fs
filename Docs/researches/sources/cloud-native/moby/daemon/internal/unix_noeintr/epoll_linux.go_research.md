# sources/cloud-native/moby/daemon/internal/unix_noeintr/epoll_linux.go

## Purpose
Provides Linux epoll syscall wrappers that transparently retry on `EINTR`.

## Important APIs, Types, And Functions
`EpollCreate` calls `unix.EpollCreate1` with `EPOLL_CLOEXEC`. `EpollCtl` wraps `unix.EpollCtl`. `EpollWait` wraps `unix.EpollWait`. Each loops until the syscall returns a non-`EINTR` error or success.

## Control Flow
Every wrapper is a small `for` loop: call syscall, continue on `errors.Is(err, unix.EINTR)`, otherwise return result.

## State And Persistence
`EpollCreate` allocates a kernel file descriptor. Other wrappers mutate or wait on kernel epoll state supplied by the caller.

## Dependencies And Integration Points
Used by daemon components that need robust epoll behavior under signal interruption. Depends on `golang.org/x/sys/unix`.

## Risks And Test Signals
Infinite retry is intentional for interruptible syscalls but can mask repeated signal storms. Callers still own fd close and timeout behavior. No tests are listed in this subset.

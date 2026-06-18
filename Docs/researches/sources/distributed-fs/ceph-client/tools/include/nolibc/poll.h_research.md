# sources/distributed-fs/ceph-client/tools/include/nolibc/poll.h

## Purpose
Provides the `poll` wrapper and poll-related UAPI types for nolibc.

## APIs, Types, and Functions
Defines `_sys_poll(struct pollfd *fds, int nfds, int timeout)` and `poll(...)`, using `<linux/poll.h>` for `struct pollfd` and event constants.

## Control Flow, State, and Persistence
The wrapper issues the `poll` syscall when available or falls back to `ppoll`-style availability depending on architecture support, then translates errors with `__sysret`. State lives in the caller's `pollfd` array where the kernel writes `revents`.

## Dependencies and Integration
Depends on `arch.h`, `sys.h`, and Linux poll UAPI. It integrates with stdio/file-descriptor event loops in nolibc programs.

## Risks and Test Signals
Risks are timeout unit confusion, nfds range issues, and architecture syscall availability. Test signals are readable/writable pipe polling, timeout expiration, interrupted polls, invalid fd handling, and cross-architecture builds.

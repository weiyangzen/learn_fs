# sources/distributed-fs/ceph-client/tools/include/nolibc/signal.h

## Purpose
Provides minimal signal support for nolibc.

## APIs, Types, and Functions
Includes `<linux/signal.h>` and defines weak `raise(int signal)`, implemented by sending a signal to the current process.

## Control Flow, State, and Persistence
`raise()` obtains the process id through nolibc syscall helpers and invokes `kill(pid, signal)`. It keeps no state; signal delivery and disposition are kernel/process state.

## Dependencies and Integration
Depends on `sys.h` for `getpid` and `kill`, and Linux signal constants. It integrates with abort/error paths and small tests needing self-signalling.

## Risks and Test Signals
Risks are limited signal API coverage, process-vs-thread semantics compared with libc `raise`, and async behavior in tests. Test signals are raising ignored, handled, and default-fatal signals, plus invalid signal error paths.

# sources/distributed-fs/ceph-client/arch/um/kernel/sigio.c

## Purpose
Provides the kernel-side lock used by host SIGIO support. It exists to serialize access to host-side SIGIO/epoll state in `arch/um/os-Linux/sigio.c`.

## Important APIs, Types, and Functions
`sigio_lock()` and `sigio_unlock()` wrap a static `DEFINE_MUTEX(sigio_mutex)`. These functions are intentionally minimal and are exported through internal UML headers rather than as module symbols.

## Control Flow, State, and Persistence
The only state is the mutex. Host-side code enters this lock before adding/removing SIGIO file descriptors or starting the SIGIO workaround thread, preventing concurrent mutation of epoll data structures and helper-thread state.

## Dependencies and Integration Points
Depends on Linux mutexes and is consumed by `os-Linux/sigio.c`. It is part of the bridge between UML kernel IRQ code and host async I/O notification.

## Risks and Test Signals
Deadlocks or missing lock coverage would manifest as SIGIO workaround races, epoll control failures, or missed I/O interrupts. Test by exercising UML consoles/PTYs and async device FDs under concurrent open/close and shutdown.

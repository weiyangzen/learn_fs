# sources/distributed-fs/ceph-client/arch/um/os-Linux/sigio.c

## Purpose
Detects and works around host PTY SIGIO limitations by using an epoll helper thread to generate SIGIO for UML.

## Important APIs, Types, and Functions
`__add_sigio_fd()`/`add_sigio_fd()` and `__ignore_sigio_fd()`/`ignore_sigio_fd()` manage the workaround epoll set. `write_sigio_thread()` waits on epoll and sends SIGIO to the UML process. `sigio_broken()` and `maybe_sigio_broken()` start the workaround. `os_check_bugs()` runs the PTY SIGIO probe. `sigio_cleanup()` kills the helper at exit.

## Control Flow, State, and Persistence
Persistent state includes `write_sigio_td`, `epollfd`, `epoll_events`, `pty_output_sigio`, and probe flag `got_sigio`. The workaround starts lazily and is protected by the kernel-side sigio mutex.

## Dependencies and Integration Points
Uses `helper.c` pthread helpers, `sigio_lock()` from `kernel/sigio.c`, PTY setup, raw terminal mode, and host SIGIO handlers. It supports UML console and fd IRQ delivery.

## Risks and Test Signals
Risks include helper-thread leaks, epoll edge-trigger missed writes, wrong signal target, and probe false negatives. Test PTY output on different kernels, console I/O, add/remove fd races, and shutdown cleanup.

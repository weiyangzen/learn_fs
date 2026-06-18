# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/epoll/epoll_wakeup_test.c

## Purpose

`epoll_wakeup_test.c` is a kselftest coverage matrix for epoll readiness propagation and waiter wakeup semantics. It covers plain sockets, eventfds, nested epoll instances, poll on epoll fds, level-triggered and edge-triggered registrations, multiple waiters, `epoll_pwait`, and direct syscall coverage for `epoll_pwait2`.

## Important APIs, Types, and Functions

The shared `struct epoll_mtcontext` stores up to three epoll fds, four socket fds, a volatile wake counter, and waiter thread IDs. Helpers wrap `__NR_epoll_pwait2`, install a no-op `SIGUSR1` handler, send timeout-breaking signals, and provide waiter/emitter thread functions. Tests use `epoll_create`, `epoll_create1`, `epoll_ctl`, `epoll_wait`, `epoll_pwait`, `poll`, `socketpair`, `eventfd`, pthreads, atomic builtins, and kselftest harness assertions.

## Control Flow, State, and Persistence

Tests `epoll1` through `epoll58` form a hand-written topology matrix: a thread waits directly or with `poll`, watches sockets or nested epoll fds, and asserts whether repeated waits produce events under LT or ET rules. The multithreaded cases synchronize with delayed writers and signal-based timeout escape. `epoll59` repeatedly modifies an eventfd interest set while another thread waits, targeting a historical lost wake race. `epoll60` starts ten waiters against ten eventfds and verifies all ET waiters wake in 300 iterations. `epoll61` races a near-timeout epoll waiter with a blocking waiter and eventfd writes. `epoll62` and `epoll63` exercise `epoll_pwait2` readiness and timeout duration. `epoll64` checks two level-triggered waiters both wake for one ready socket. Persistent state is limited to kernel wait queues, eventfd counters, socket buffers, and epoll ready lists during each test.

## Dependencies, Integration Points, Risks, and Test Signals

The test depends on pthreads, Unix sockets, eventfd, signal delivery, high-resolution enough scheduling, and kernel support for `epoll_pwait2` where exercised. It integrates with `tools/testing/selftests/filesystems/epoll` and validates core fs/eventpoll behavior used by user space runtimes. Main risks are timing sensitivity, busy waits on volatile fields, signal interruption masking real races, and platform load causing long joins. Passing signals include exact wake counts, ET second wait returning zero, LT repeated readiness, `EINTR` only during stop, no lost waiters in stress loops, and `epoll_pwait2` timeout at least the configured delay.

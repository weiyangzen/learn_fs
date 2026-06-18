# sources/distributed-fs/ceph-client/tools/testing/selftests/net/stress_reuseport_listen.c

Purpose: this C helper stress-tests `listen()` scalability for many IPv6 sockets that share a port with `SO_REUSEPORT`. It creates many VIP:443 groups and measures the time to transition all sockets to listening state.

Important APIs and functions: `bind_reuseport_sock6` allocates the socket array, builds IPv6 addresses starting at `2401:dead::1`, sets `SO_REUSEPORT`, binds each socket to port 443, and increments the low 32 bits for each VIP. `main` parses `<nr_vips> <nr_socks_per_vip>`, calls `listen(fd, 0)` for every socket, measures time with `CLOCK_MONOTONIC`, prints elapsed time, closes descriptors, and frees memory.

Control flow: all sockets are created and bound before any listen call. The listen loop is the measured region, so the result focuses on kernel listen path cost under many reuseport groups rather than bind cost. Any syscall failure aborts through `error(1, errno, ...)`.

State and persistence: process state consists of global `nr_socks_per_vip`, `nr_vips`, and the allocated fd array. Kernel state is a large set of bound/listening TCP IPv6 sockets; it disappears after close or process exit. No files are written.

Dependencies and integration points: built as a selftest helper and invoked by `stress_reuseport_listen.sh` inside a network namespace with `net.ipv6.ip_nonlocal_bind=1`, allowing bind to many unassigned VIP addresses. It uses standard libc, IPv6 sockets, and Linux `SO_REUSEPORT`.

Risks: the printed microsecond field uses `(end_ns - start_ns) / NSEC_PER_USEC`, not a remainder, so display formatting is coarse. Very large inputs can exhaust file descriptors or memory. The code increments `s6_addr32[3]` in host memory order, which is acceptable for generating distinct test addresses but not a generic address arithmetic helper.

Test signals: successful execution prints a line like `listen 24000 socks took ...` and exits zero. Any socket, setsockopt, bind, listen, malloc, or address conversion failure exits nonzero with a diagnostic.

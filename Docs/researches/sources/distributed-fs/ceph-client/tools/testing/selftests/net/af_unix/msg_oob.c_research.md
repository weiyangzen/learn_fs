# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/msg_oob.c

Purpose: Documents and verifies AF_UNIX stream `MSG_OOB` urgent-data behavior by comparing it against TCP behavior across normal, peek, inline, dropped, repeated, and reset scenarios.

Important APIs/types/functions: Uses `socketpair(AF_UNIX, SOCK_STREAM|SOCK_NONBLOCK)`, a loopback TCP pair, `MSG_OOB`, `MSG_PEEK`, `SO_OOBINLINE`, `SIOCATMARK`, `EPOLLPRI`, `SIGURG` via `FIOSETOWN` and `signalfd`, and kselftest fixtures. Helpers include `create_unix_socketpair()`, `create_tcp_socketpair()`, `setup_sigurg()`, `setup_epollpri()`, `__sendpair()`, `__recvpair()`, `__epollpair()`, `__siocatmarkpair()`, and `__resetpair()`.

Control flow: Fixture creates matching AF_UNIX and TCP endpoint pairs, registers SIGURG and EPOLLPRI on receivers, then each test sends normal or urgent bytes through both protocols. The helpers assert AF_UNIX return values, errno, data ordering, epoll readiness, and at-mark state, optionally relaxing TCP comparisons via `tcp_incompliant` for known TCP differences.

State and persistence behavior: Keeps four sockets, one signal fd, two epoll fds, and a `tcp_compliant` flag in fixture state. Urgent mark state and inline mode live in kernel socket state only.

Dependencies and integration points: Requires `CONFIG_AF_UNIX_OOB`, AF_UNIX stream OOB implementation, TCP loopback, epoll, signal delivery, and kselftest harness. The Makefile/config in the same directory expose the feature.

Risks: The test is intentionally semantic and strict; small changes in urgent pointer handling, reset behavior, or `SIOCATMARK` can break many cases. It uses nonblocking sockets and immediate `epoll_wait(..., timeout 0)`, so scheduling-sensitive signal delivery would be visible. TCP is used as a reference but has explicitly different behavior in several cases.

Test signals: Passing cases confirm `EPOLLPRI`, `SIGURG`, OOB read/drop, ordinary read break-at-OOB, repeated urgent-byte replacement, `SO_OOBINLINE`, `MSG_PEEK`, and reset semantics for AF_UNIX streams.

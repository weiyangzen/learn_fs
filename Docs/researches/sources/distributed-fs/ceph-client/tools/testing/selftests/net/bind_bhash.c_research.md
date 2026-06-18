# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bind_bhash.c

Purpose: Microbenchmark for measuring bind time when a port's bind hash table already contains many sockets.

Important APIs/types/functions: Uses pthreads, `getaddrinfo()`, `socket()`, `setsockopt(SO_REUSEPORT)`, `bind()`, `listen()`, `clock()`, and large constants `MAX_THREADS=600`, `MAX_CONNECTIONS=40`.

Control flow: Main parses port, address family, and bind address. It first binds and listens on loopback with `SO_REUSEPORT`, then starts 600 threads, each binding 40 additional `SO_REUSEPORT` sockets to the same setup address/port. After population, it times a bind without reuse options to a different provided address and prints elapsed CPU time.

State and persistence behavior: Holds up to 24,000 sockets plus a listener. No files are persisted. The wrapper script runs it in a network namespace with a raised fd limit.

Dependencies and integration points: Built as `bind_bhash` by the net Makefile and invoked by `bind_bhash.sh`.

Risks: Cleanup loop has an apparent bug: inner loop condition/increment use `i` instead of `j`, so descriptor cleanup is incorrect and can loop unexpectedly or skip closes. Global `ret` is written by threads without synchronization. Resource use is intentionally heavy and depends on `ulimit -n`.

Test signals: `time spent = <seconds>` indicates benchmark completion. Failures usually come from socket/bind/listen/resource exhaustion.

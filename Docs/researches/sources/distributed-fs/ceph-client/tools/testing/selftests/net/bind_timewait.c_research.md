# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bind_timewait.c

Purpose: Verifies that binding a new TCP socket to a port still occupied by a TIME_WAIT socket fails with `EADDRINUSE`.

Important APIs/types/functions: Uses IPv4 TCP sockets, kselftest fixture variants for `INADDR_LOOPBACK` and `INADDR_ANY`, `bind()`, `listen()`, `connect()`, `accept()`, `getsockname()`, and `errno`.

Control flow: Fixture initializes an ephemeral IPv4 address. Helper `create_timewait_socket()` binds/listens, connects a client, accepts, then closes child/client/server to create TIME_WAIT state. The test then opens a new TCP socket and attempts to bind to the same address/port, expecting `-1` and `EADDRINUSE`.

State and persistence behavior: TIME_WAIT state is held by the kernel TCP stack after sockets close. No persistent files.

Dependencies and integration points: Requires IPv4 loopback TCP support and kselftest harness.

Risks: TIME_WAIT ownership can depend on close ordering and TCP state transitions, but the test intentionally closes accepted child before client/server. Ephemeral port assignment is updated through `getsockname()`.

Test signals: Passing assertions prove bind conflict accounting includes TIME_WAIT sockets for both loopback and wildcard cases.

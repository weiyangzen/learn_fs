# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/connect.c

Purpose: this is the baseline positive TCP-AO connection test. It verifies that a client and server with matching AO keys can connect, exchange data, and increment TCP-AO good-packet counters.

Important APIs and functions: `server_fn` creates a listener with `test_listen_socket`, installs a default AO key with `test_add_key`, accepts one connection, and calls `test_server_run`. `client_fn` creates a TCP socket, installs the same key, connects with `test_connect_socket`, sends and verifies 20 messages through `test_client_verify`, and checks counters with `netstat_read`, `netstat_get`, `test_get_tcp_counters`, and `test_assert_counters`.

Control flow: `test_init(2, server_fn, client_fn)` sets up the two namespace peers. Server and client synchronize after key installation and after connection establishment. The client records netstat and per-socket counters before data transfer, performs the transfer, records counters again, prints netstat diffs, and validates that `TCPAOGood` increased by at least the number of packets.

State and persistence: state is per-socket AO key material, TCP counters, and temporary netstat snapshots. `netstat_free` and `test_assert_counters` release allocated counter state. No persistent files are written.

Dependencies and integration points: depends on TCP-AO support, the shared TCP-AO selftest library, network namespace/veth setup from the harness, and IPv4/IPv6 macros selected by the Makefile.

Risks: the server calls `test_fail` after `test_server_run` returns, meaning the server side is not expected to exit normally before the client/test harness ends. Counter expectations assume at least 20 good AO packets, but retransmission or aggregation can make exact counts unsuitable, so the test uses a lower-bound check for netstat and structured assertions for socket/key counters.

Test signals: success includes a `connect TCPAOGood ... sent 20` `test_ok` line and passing counter assertions. Any connect, key install, accept, verify, or counter mismatch reports failure or exits through `test_error`.

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/connect-deny.c

Purpose: this TCP-AO selftest validates that connections are denied or accepted correctly for mismatched authentication conditions. It covers non-AO/AO asymmetry, wrong password, wrong send or receive IDs, MAC length mismatch, wrong addresses, and prefix-based matching.

Important APIs and functions: it uses `TCP_AO_ADD_KEY`, `test_prepare_key`, `test_verify_socket_key`, `test_skpair_wait_poll`, `test_skpair_connect_poll`, `test_get_tcp_counters`, `netstat_get_one`, and ftrace expectation helpers. Core functions are `test_add_key_maclen`, `try_accept`, `server_fn`, `try_connect`, and `client_fn`. The shared `sk_pair` volatile variable propagates peer-side connection failures.

Control flow: server and client iterate through the same port sequence. For each case the server prepares a listener with or without AO keys and waits for readiness or expected timeout/key rejection. The client configures the corresponding AO key state, optionally registers expected TCP-AO/hash trace events, then attempts connect with polling. Both sides synchronize before preparation, counter checks, and close.

State and persistence: all state is per-process, per-socket, and namespace-local. TCP-AO counters are sampled before and after selected cases, and netstat counters such as `TCPAOKeyNotFound`, `TCPAORequired`, `TCPAOBad`, and `TCPAOGood` are checked for increments. No files are written.

Dependencies and integration points: built for IPv4 and IPv6 via `aolib.h` macros. It integrates with optional ftrace validation, TCP-AO counter helpers, and the shared two-thread test harness from the TCP-AO library.

Risks: expected failures depend on TCP retransmission timing and counter updates; the polling helpers mitigate but cannot remove all timing sensitivity. Some cases intentionally expect no counters, such as SYNACK no-key behavior. Prefix match uses prefix length 16 for both address families through clamping helpers, so interpretation differs by family.

Test signals: each scenario emits `test_ok` on expected accept, timeout, refusal, or key rejection. Counter assertions verify per-socket/per-netns AO counters, and ftrace destructor reports missing or unexpected trace events if supported.

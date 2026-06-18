# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/bench-lookups.c

Purpose: this TCP-AO benchmark measures lookup and update costs as the number of matching key tuples grows. It times key deletion, key re-addition, asynchronous deletion, and connect-time key selection for 512 through 8192 keys.

Important APIs and functions: it uses `test_add_key`, `TCP_AO_DEL_KEY`, `ip_route_add`, `ip_addr_add`, `test_connect_socket`, `test_wait_fd`, and shared namespace synchronization. Key functions include `gen_test_ips`, `test_add_routes`, `server_apply_keys`, `measure_call`, `bench_delete`, `bench_connect_srv`, `bench_connect_client`, `client_addr_setup`, `server_fn`, and `client_fn`. `bench_stats` stores min, max, count, mean, and Welford accumulation.

Control flow: for each key count, the server allocates deterministic odd test addresses, adds routes, raises optmem sizing, installs one AO key per address on the listener, and runs two connect benchmark phases. It then times worst-case and random key deletion plus restoration, and async deletion. The client adds local addresses and routes, binds to selected source addresses, installs the corresponding AO key, synchronizes with the server, and measures connect calls.

State and persistence: benchmark state lives in `bench_results`, global `test_ips`, per-socket TCP-AO key lists, and routes/addresses added to the test namespace. `test_set_optmem` changes socket optmem limits for the process/test environment. No persistent files are produced.

Dependencies and integration points: compiled twice for IPv4/IPv6 via the Makefile and links with `-lm` for `sqrt`. It relies on the TCP-AO selftest library for topology, socket helpers, and test reporting.

Risks: the "random-search" client phase currently calls `bench_connect_client(..., false)` in the inspected source, so it reuses sequential order while printing random-search text. The standard deviation print uses `sqrt((mean/1000000)/nr)` rather than `s2`, so it is not a true variance-derived standard deviation. High key counts require sufficient optmem and memory.

Test signals: output consists of `test_ok` benchmark lines with min/max/mean fields for add, delete worst case, delete random-search, delete async, connect worst case, and connect random-search. Syscall or connection failures abort the test through `test_error`.

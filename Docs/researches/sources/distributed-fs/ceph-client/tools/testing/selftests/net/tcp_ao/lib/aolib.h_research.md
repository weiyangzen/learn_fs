# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/aolib.h

Purpose: this header is the central API contract for TCP-AO selftests. It defines logging wrappers, feature probes, address-family abstraction, namespace and netlink helpers, socket helpers, AO/MD5 key helpers, counter structures, repair helpers, and ftrace expectation APIs.

Important APIs and types: `union tcp_addr`, `enum test_fault`, `enum test_needs_kconfig`, `struct tcp_ao_counters`, `struct tcp_counters`, `struct tcp_sock_state`, and `enum trace_events` are key types. Important inline helpers include `test_init2`, `gen_tcp_addr`, `tcp_addr_to_sockaddr_in`, `test_listen_socket`, `test_connect_socket`, `test_set_md5`, `test_prepare_key`, `test_prepare_def_key`, `test_add_key_vrf`, `test_add_key`, `test_set_ao_flags`, `test_assert_counters`, `test_sock_checkpoint`, `test_sock_restore`, and trace expectation wrappers.

Control flow: tests include this header, then `test_init` or `test_init2` selects IPv4/IPv6 addresses based on `IPV6_TEST`, starts peer threads through library code, and uses helpers to build topology and sockets. AO keys are prepared as `struct tcp_ao_add`, installed through `setsockopt`, and verified through getsockopt comparison wrappers. Counter helpers compare before/after snapshots and free allocated key counter arrays.

State and persistence: the header declares thread-local `this_ip_addr` and `this_ip_dest`, global `test_family`, namespace cookies, and external helper state owned by library `.c` files. It defines constants such as `DEFAULT_TEST_PASSWORD`, `DEFAULT_TEST_ALGO`, and default prefixes. No persistent state is written by the header itself.

Dependencies and integration points: bridges Linux UAPI headers (`linux/tcp.h`, SNMP, bits), selftest library implementations (`setup.c`, `sock.c`, `utils.c`, `netlink.c`, `proc.c`, `repair.c`, `ftrace.c`), and Makefile address-family variants. It also works around missing `SOL_TCP` from libc header conflicts.

Risks: many helpers exit via `test_error`, so callers usually cannot recover from setup failures. Prefix clamping differs by family and can hide caller mistakes. Some APIs depend on optional kernel support and should be guarded with `kernel_config_has` or `should_skip_test`.

Test signals: tests using this header emit kselftest-compatible ok/fail/skip/xfail messages, structured counter assertions, and optional ftrace diagnostics for expected or unexpected TCP-AO tracepoints.

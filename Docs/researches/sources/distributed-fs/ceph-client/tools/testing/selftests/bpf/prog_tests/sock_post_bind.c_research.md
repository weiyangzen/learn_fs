<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_post_bind.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_post_bind.c

Purpose: `sock_post_bind.c` tests cgroup post-bind programs for IPv4 and IPv6 sockets. It validates attach type compatibility, allow/deny verdicts after bind, denial for specific IP/port combinations, and retry behavior on alternate ports.

Important APIs/types/functions: `struct sock_post_bind_test` holds raw BPF instructions, attach/expected attach type, socket domain/type, bind IP/port/retry port, and expected result. `load_prog()` loads inline `BPF_PROG_TYPE_CGROUP_SOCK` programs. `bind_sock()` performs the bind and optional retry. `run_test()` loads, attaches, runs bind, and detaches.

Control flow: `test_sock_post_bind()` joins `/post_bind`, creates a netns object, iterates the table as subtests, and asserts `run_test()` succeeds. Each run loads the program with expected attach type, attaches to the requested post-bind hook, handles expected attach rejection, binds a socket to the configured address/port, treats `EPERM` as BPF denial, retries on configured alternate port, and compares the resulting category with the expected result.

State and persistence: state is the cgroup FD, netns object, raw BPF program FD, one socket per subtest, and verifier log buffer. Cleanup frees the netns and closes the cgroup.

Dependencies: depends on cgroup post-bind attach types, raw BPF instruction macros, IPv4/IPv6 socket binding, `inet_pton()`, cgroup helpers, and `netns_new()`.

Integration points: exercises the post-bind cgroup hook after socket address assignment and before userspace observes bind success.

Risks: exact source-port checks use constants in network byte order and are easy to misread (`0x1002`, `0x2001`). The test treats non-`EPERM` bind failures as infrastructure errors, so occupied ports or namespace setup issues can obscure BPF behavior. Attach rejection paths still call detach best-effort on the program FD.

Test signals: expected attach rejection for mismatched attach types, expected `BIND_REJECT`, `SUCCESS`, `RETRY_SUCCESS`, or `RETRY_REJECT` for each bind scenario, and verifier log output on load failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_post_bind.c -->

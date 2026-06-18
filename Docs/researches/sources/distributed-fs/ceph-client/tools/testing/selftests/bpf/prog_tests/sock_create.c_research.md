<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_create.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_create.c

Purpose: `sock_create.c` tests `BPF_CGROUP_INET_SOCK_CREATE` programs that mutate or deny socket creation. It validates priority, mark, bound device, protocol filtering, and compatibility behavior when `expected_attach_type` is omitted.

Important APIs/types/functions: `struct sock_create_test` stores a description, raw BPF instruction array, attach/expected attach type, socket domain/type/protocol, expected socket option, and expected error category. `load_prog()` loads `BPF_PROG_TYPE_CGROUP_SOCK` instructions with verifier log options. `run_test()` attaches the program to a cgroup, creates a socket, reads expected socket options, and detaches.

Control flow: `test_sock_create()` joins `/sock_create`, iterates the table as subtests, and asserts `run_test()` succeeds. Each run loads the inline instructions, attaches to the cgroup, calls `socket()`, treats denied creates as success only for `DENY_CREATE`, checks `SO_PRIORITY`, `SO_MARK`, or `SO_BINDTOIFINDEX` when requested, then detaches and closes FDs.

State and persistence: state is a temporary cgroup FD, BPF program FD, one socket FD per subtest, verifier log buffer, and any socket options set by the BPF program. No persistent state is created.

Dependencies: depends on cgroup helpers, raw BPF instruction macros, `bpf_prog_load()`, `bpf_prog_attach()`, `BPF_PROG_TYPE_CGROUP_SOCK`, socket options `SO_PRIORITY`, `SO_MARK`, and `SO_BINDTOIFINDEX`, and root privileges for cgroup/socket mark behavior.

Integration points: exercises the cgroup socket-create hook directly with hand-written BPF instructions instead of skeletons, making it a low-level verifier and hook semantics test.

Risks: inline instruction arrays are brittle and need correct offsets into `struct bpf_sock`. The ICMPv6 denial table row uses `domain = AF_INET` with `protocol = IPPROTO_ICMPV6`, which may be intentional compatibility coverage or a table risk. Expected mark `666` assumes root UID path; non-root execution would use UID as mark.

Test signals: successful mutation of priority/mark/bound interface for IPv4 and IPv6 UDP sockets, denied ICMP/ICMPv6 creation where expected, and successful load/attach without `expected_attach_type` in compatibility mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_create.c -->

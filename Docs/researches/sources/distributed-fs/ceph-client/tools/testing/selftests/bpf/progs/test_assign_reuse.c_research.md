<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_assign_reuse.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_assign_reuse.c

Purpose: Tests `bpf_sk_assign` and reuseport socket selection interaction for TCP/UDP and tc paths.

Important APIs/types/functions: Defines `sk_map`, reuseport accept/drop programs, helpers `assign_sk`, `maybe_assign_tcp`, `maybe_assign_udp`, and `tc_main`.

Control flow: Reuseport programs accept/drop based on selected socket; tc path parses packet protocol and conditionally assigns sockets from `sk_map`.

State and persistence: Persistent state is the socket map populated by userspace.

Dependencies and integration: Depends on sk_reuseport, tc, socket map, and `bpf_sk_assign` helpers.

Risks: Protocol parsing, socket ref lifetime, and assign/reuseport ordering are risks.

Test signals: Tests send TCP/UDP packets and verify accept/drop/assignment behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_assign_reuse.c -->

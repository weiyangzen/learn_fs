<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_unsupp_cong_op.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_unsupp_cong_op.c

Purpose: Negative test for unsupported TCP congestion-control operation in BPF struct_ops.

Important APIs/types/functions: Defines a callback for an unsupported op and a `.struct_ops` map.

Control flow: Load/link should reject or skip the unsupported operation according to selftest expectations.

State and persistence: No intended persistent runtime registration if unsupported.

Dependencies and integration: Depends on TCP CA struct_ops allowlist.

Risks: Accepting unsupported hooks can expose unverified call contexts.

Test signals: Expected signal is annotated load failure or unsupported-op diagnostic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_unsupp_cong_op.c -->

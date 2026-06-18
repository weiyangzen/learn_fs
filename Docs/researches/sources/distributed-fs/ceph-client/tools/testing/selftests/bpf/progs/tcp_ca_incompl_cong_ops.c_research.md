<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_incompl_cong_ops.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_incompl_cong_ops.c

Purpose: Negative struct_ops test for incomplete TCP congestion-control ops.

Important APIs/types/functions: Defines partial `tcp_congestion_ops` callbacks in struct_ops sections and a `.struct_ops` map.

Control flow: Load/link validates required callback coverage rather than runtime congestion behavior.

State and persistence: State would be the TCP CA struct_ops registration if accepted.

Dependencies and integration: Depends on TCP congestion-control struct_ops verifier.

Risks: Missing required ops must be rejected to avoid invalid TCP CA registration.

Test signals: Expected signal is load failure or specific selftest outcome for incomplete ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_incompl_cong_ops.c -->

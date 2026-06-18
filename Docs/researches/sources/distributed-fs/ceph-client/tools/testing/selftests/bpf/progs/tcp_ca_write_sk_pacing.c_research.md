<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_write_sk_pacing.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_write_sk_pacing.c

Purpose: Tests writes to socket pacing-related fields from TCP congestion-control struct_ops callbacks.

Important APIs/types/functions: Defines helper-like calculations `tcp_left_out`, `tcp_packets_in_flight`, TCP CA callbacks, and a `.struct_ops` map.

Control flow: Callbacks inspect TCP state and write pacing fields during congestion-control events.

State and persistence: Persistent state is socket TCP state modified during test traffic and callback globals.

Dependencies and integration: Depends on TCP struct_ops verifier field-access permissions.

Risks: Verifier must allow only safe socket writes and preserve TCP invariants.

Test signals: Traffic-driven selftests validate pacing field updates and callback execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_write_sk_pacing.c -->

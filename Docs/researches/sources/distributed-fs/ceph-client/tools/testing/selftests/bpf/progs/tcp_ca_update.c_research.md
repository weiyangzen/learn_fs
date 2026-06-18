<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_update.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_update.c

Purpose: Tests updating/replacing TCP congestion-control struct_ops links.

Important APIs/types/functions: Defines several TCP CA callback variants and multiple `.struct_ops.link` maps plus a base `.struct_ops` map.

Control flow: Callbacks return distinct values so userspace can verify which linked ops instance is active after updates.

State and persistence: Persistent state is registered TCP CA links and result globals.

Dependencies and integration: Depends on struct_ops link update/detach for TCP congestion ops.

Risks: Update ordering and stale callback pointers are the risks.

Test signals: Tests attach/update links and confirm the active callback variant changes as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_update.c -->

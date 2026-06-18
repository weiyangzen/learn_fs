<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_autocreate2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_autocreate2.c

Purpose: Companion auto-create test using optional `?struct_ops/test_1` program sections and a required link map.

Important APIs/types/functions: Defines two optional test callbacks and a `.struct_ops.link` `bpf_testmod_ops` map.

Control flow: Load-time section processing determines whether optional callbacks are accepted; runtime callback flow is trivial.

State and persistence: No durable state beyond struct_ops link objects and callback return values.

Dependencies and integration: Depends on libbpf optional program sections and bpf_testmod ops BTF.

Risks: Optional callback resolution must not fail the whole object when a target is unavailable.

Test signals: Tests validate load/link behavior rather than complex runtime state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_autocreate2.c -->

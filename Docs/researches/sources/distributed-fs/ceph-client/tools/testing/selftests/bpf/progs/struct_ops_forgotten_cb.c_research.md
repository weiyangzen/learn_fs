<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_forgotten_cb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_forgotten_cb.c

Purpose: Verifies behavior when a struct_ops map omits or forgets expected callback wiring.

Important APIs/types/functions: Defines one `struct_ops/test_1` callback and a linked `bpf_testmod_ops` map.

Control flow: Load/link path checks callback discovery and map initialization; callback body itself is trivial.

State and persistence: State is the struct_ops link object only.

Dependencies and integration: Depends on bpf_testmod ops BTF and libbpf callback-to-field assignment.

Risks: Missing callback registration or wrong field assignment is the risk.

Test signals: Test signal is successful expected attach semantics or intended loader rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_forgotten_cb.c -->

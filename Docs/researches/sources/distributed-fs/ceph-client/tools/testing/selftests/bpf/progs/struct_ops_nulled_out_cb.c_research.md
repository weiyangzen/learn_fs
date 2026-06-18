<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_nulled_out_cb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_nulled_out_cb.c

Purpose: Verifies a struct_ops callback field that is nulled out behaves as intended.

Important APIs/types/functions: Defines `struct_ops/test_1` and a linked `bpf_testmod_ops` map with callback configuration under test.

Control flow: Callback execution is simple; loader/map initialization around NULL callback fields is the focus.

State and persistence: State is link-map callback table plus any result global.

Dependencies and integration: Depends on bpf_testmod ops and struct_ops link initialization.

Risks: Incorrectly accepting or invoking nulled callbacks can hide loader/kernel bugs.

Test signals: Test expects the chosen callback to be invoked or absent according to map setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_nulled_out_cb.c -->

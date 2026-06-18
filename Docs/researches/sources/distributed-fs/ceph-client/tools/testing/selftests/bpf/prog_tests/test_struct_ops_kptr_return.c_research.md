<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_kptr_return.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_kptr_return.c

Purpose: dispatches positive and negative verifier coverage for struct_ops callbacks returning kernel pointers.

Important APIs/types/functions: `RUN_TESTS()` over `struct_ops_kptr_return` plus failure skeletons for wrong type, invalid scalar, nonzero offset, and local kptr return.

Control flow: the selftest harness opens/loads/runs each generated skeleton according to its embedded expectations. This C file acts as the manifest tying those skeletons into the suite.

State and persistence: no state in the harness file; all test state is inside generated skeletons and their BPF objects.

Dependencies and integration: depends on generated skeletons and struct_ops kptr verifier support. Integrated as `test_struct_ops_kptr_return`.

Risks: because this file delegates entirely to `RUN_TESTS`, detailed semantics live in the BPF program sources. Missing or misnamed skeletons break build/runtime registration.

Test signals: pass/fail comes from the generated skeleton test macro, especially expected load rejection for invalid kptr return shapes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_kptr_return.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack_fail.c

Purpose: Negative counterpart for private-stack verifier limits in struct_ops programs.

Important APIs/types/functions: Same broad shape as the positive private-stack test, with stack usage arranged to exceed allowed limits or violate private-stack rules.

Control flow: Nested callbacks/subprograms drive the excessive stack scenario.

State and persistence: No successful runtime persistence is expected.

Dependencies and integration: Depends on private-stack verifier diagnostics and bpf_testmod ops3.

Risks: If accepted, stack-depth enforcement for struct_ops callbacks is too weak.

Test signals: Expected signal is verifier rejection rather than callback output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack_fail.c -->

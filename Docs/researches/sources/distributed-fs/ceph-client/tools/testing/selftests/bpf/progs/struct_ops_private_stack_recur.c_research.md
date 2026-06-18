<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack_recur.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack_recur.c

Purpose: Tests recursive/private-stack interaction for struct_ops callbacks and subprograms.

Important APIs/types/functions: Defines `subprog1`, `subprog2`, a struct_ops callback, and a `.struct_ops` map.

Control flow: The callback/subprogram call graph is intentionally recursive or recursion-like to exercise verifier call graph handling.

State and persistence: Only globals and the link map would persist on successful load.

Dependencies and integration: Depends on verifier recursion detection and private-stack allocation logic.

Risks: Recursive struct_ops subprograms must not bypass stack limits.

Test signals: Expected test signal is the loader outcome encoded by the selftest annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack_recur.c -->

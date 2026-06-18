<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack.c

Purpose: Positive test for private stack accounting across struct_ops callbacks and BPF subprogram calls.

Important APIs/types/functions: Defines `subprog1`, `subprog2`, callbacks `test_1`/`test_2`, globals `val_i`/`val_j`, and a `.struct_ops` map.

Control flow: `test_1` allocates a 400-byte stack array, calls `subprog1`, then invokes another testmod op; `test_2` uses a 200-byte stack path.

State and persistence: Globals persist computed values; struct_ops map stores callback pointers.

Dependencies and integration: Depends on bpf_testmod ops3 and verifier private-stack support for struct_ops programs.

Risks: Stack depth across callbacks/subprogs must be accounted without false sharing or overflow.

Test signals: Passing tests see load success and expected values after testmod invokes both callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_private_stack.c -->

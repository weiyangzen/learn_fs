<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return.c

Purpose: Positive test for returning a referenced kernel pointer from a struct_ops callback.

Important APIs/types/functions: Defines a `struct_ops/test_return_ref_kptr` callback returning a `struct task_struct *` and a linked `bpf_testmod_ops` map.

Control flow: The callback returns an accepted referenced kptr in the shape expected by the testmod op.

State and persistence: No mutable state beyond the link map.

Dependencies and integration: Depends on verifier support for struct_ops kptr return types and task kptr lifetime rules.

Risks: The verifier must enforce exact trusted referenced pointer return semantics.

Test signals: Success is load/attach without verifier complaints and correct testmod callback invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return.c -->

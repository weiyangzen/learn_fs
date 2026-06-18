<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__wrong_type.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__wrong_type.c

Purpose: Negative test for returning the wrong referenced kptr type from a struct_ops callback.

Important APIs/types/functions: Declares local kernel types such as `cgroup` and `task_struct`, then wires a failing callback into `bpf_testmod_ops`.

Control flow: Callback return value has reference semantics but not the exact expected BTF type.

State and persistence: No persistent runtime state is expected.

Dependencies and integration: Depends on BTF type identity checks for struct_ops kptr returns.

Risks: Type-compatible-looking but wrong kptrs must be rejected.

Test signals: Pass signal is expected verifier error for wrong return type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__wrong_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__invalid_scalar.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__invalid_scalar.c

Purpose: Negative verifier test returning an invalid scalar where a referenced kptr is required.

Important APIs/types/functions: Contains a `struct_ops/test_return_ref_kptr` callback annotated with expected verifier messages and a linked map.

Control flow: The callback deliberately produces the wrong return kind to force verifier rejection.

State and persistence: No runtime state should persist because load is expected to fail.

Dependencies and integration: Depends on `bpf_misc.h` failure annotations and testmod kptr-return op BTF.

Risks: If accepted, verifier kptr return validation is broken.

Test signals: Expected test signal is the annotated verifier error, not runtime execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__invalid_scalar.c -->

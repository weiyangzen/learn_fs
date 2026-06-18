<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_maybe_null_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_maybe_null_fail.c

Purpose: Negative nullable-pointer test for a struct_ops callback that dereferences maybe-NULL data unsafely.

Important APIs/types/functions: Defines a `struct_ops/test_maybe_null_struct_ptr` callback with expected failure behavior and a link map.

Control flow: The callback uses a maybe-null struct pointer without sufficient validation.

State and persistence: No successful runtime state is expected.

Dependencies and integration: Depends on verifier nullable pointer diagnostics.

Risks: If accepted, struct_ops nullable argument enforcement regressed.

Test signals: Expected test signal is verifier rejection with the annotated diagnostic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_maybe_null_fail.c -->

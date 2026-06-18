<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__local_kptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__local_kptr.c

Purpose: Negative test for returning a local kptr/object instead of an allowed referenced kernel pointer.

Important APIs/types/functions: Defines a failing struct_ops kptr-return callback and link map.

Control flow: Control flow constructs or selects a local pointer and returns it to the struct_ops ABI.

State and persistence: No successful runtime persistence is expected.

Dependencies and integration: Depends on verifier return-type tracking for local kptrs.

Risks: Accepting stack/local kptr returns would violate lifetime safety.

Test signals: Verifier rejection with the expected message is the pass condition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__local_kptr.c -->

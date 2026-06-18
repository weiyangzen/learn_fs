<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__ref_leak.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__ref_leak.c

Purpose: Negative test where a refcounted struct_ops argument is leaked.

Important APIs/types/functions: Defines a failing `test_refcounted` callback and link map.

Control flow: The callback exits without releasing the referenced task.

State and persistence: No successful runtime state is expected.

Dependencies and integration: Depends on verifier reference leak detection.

Risks: Accepting the program would leak task references from struct_ops callbacks.

Test signals: Expected verifier message reports unreleased reference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__ref_leak.c -->

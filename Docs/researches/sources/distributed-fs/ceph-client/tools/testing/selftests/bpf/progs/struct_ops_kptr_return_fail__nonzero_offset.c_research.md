<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__nonzero_offset.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__nonzero_offset.c

Purpose: Negative test for returning a referenced kptr with a nonzero offset.

Important APIs/types/functions: Defines a failing `test_return_ref_kptr` callback and linked map.

Control flow: The callback returns an offset pointer rather than the base kptr.

State and persistence: No runtime state should exist after expected load failure.

Dependencies and integration: Depends on struct_ops return verifier and BTF pointer-offset tracking.

Risks: Nonzero-offset kptr returns can corrupt object lifetime/type interpretation if accepted.

Test signals: Expected verifier rejection mentions invalid offset or pointer type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_kptr_return_fail__nonzero_offset.c -->

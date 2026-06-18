<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__global_subprog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__global_subprog.c

Purpose: Negative test for releasing a refcounted struct_ops argument through a global subprogram.

Important APIs/types/functions: Defines `subprog_release`, failure log-level annotation, callback, and link map.

Control flow: The callback hands the referenced task to a global subprogram, exercising verifier restrictions on global subprog reference ownership.

State and persistence: No runtime state should persist after expected rejection.

Dependencies and integration: Depends on refcounted struct_ops args and verifier global-function reference rules.

Risks: Global subprograms must not obscure release ownership.

Test signals: Expected verifier log indicates the reference handling violation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__global_subprog.c -->

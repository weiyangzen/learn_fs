<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__tail_call.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__tail_call.c

Purpose: Negative test for tail calls while holding a refcounted struct_ops argument.

Important APIs/types/functions: Defines `prog_array`, failing refcounted callback, and link map.

Control flow: The callback attempts or exposes a tail-call path before reference ownership is safely released.

State and persistence: No runtime persistence is expected after failed load.

Dependencies and integration: Depends on prog-array tail-call verifier and struct_ops reference tracking.

Risks: Tail calls must not bypass mandatory release of referenced args.

Test signals: Pass signal is expected verifier rejection for reference leak/tail-call hazard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_refcounted_fail__tail_call.c -->

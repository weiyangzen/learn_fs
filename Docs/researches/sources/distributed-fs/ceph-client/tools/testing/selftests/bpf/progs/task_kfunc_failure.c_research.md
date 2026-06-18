<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_failure.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_failure.c

Purpose: Negative verifier suite for task kfunc reference, trust, NULL, context, and direct-field access rules.

Important APIs/types/functions: Defines many `tp_btf/task_newtask`, kretprobe, lsm, and fentry programs annotated with expected failures; uses shared task-kfunc map helpers.

Control flow: Each program deliberately violates one rule: acquiring untrusted/NULL/frame pointers, releasing unacquired or maybe-null refs, leaking refs, calling in unsafe contexts, or accessing `comm` unsafely.

State and persistence: Expected successful runtime state is none; map mutations are setup for verifier scenarios.

Dependencies and integration: Depends on `bpf_task_acquire`, `bpf_task_release`, pid/vpid kfuncs, RCU trust annotations, and `bpf_misc.h` failure annotations.

Risks: The risk is verifier unsoundness around trusted task pointers and reference ownership.

Test signals: Pass condition is rejection with each expected verifier message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_kfunc_failure.c -->

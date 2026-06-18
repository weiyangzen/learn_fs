<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall6.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall6.c

Purpose: Tail-call test variant combining a classifier target and entry fallback in tc context.

Important APIs/types/functions: Defines `classifier_0`, `entry`, and `jmp_table`.

Control flow: Entry calls the prog-array target and falls through if the target is absent.

State and persistence: State is map population by the harness.

Dependencies and integration: Depends on tc program loading and static tail-call helper.

Risks: Verifier/JIT must preserve fallback logic and target transfer.

Test signals: Tests compare populated and unpopulated map outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall6.c -->

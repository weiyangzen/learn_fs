<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_poke.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_poke.c

Purpose: Tests tail-call poke/update behavior for fentry programs and prog-array mutation.

Important APIs/types/functions: Defines `jmp_table` and multiple optional/required `fentry/bpf_fentry_test1` programs.

Control flow: Fentry programs exercise tail-call transfer and runtime map update/poke paths.

State and persistence: Prog-array map persists target program slots.

Dependencies and integration: Depends on fentry attach, tail-call poke machinery, and libbpf optional sections.

Risks: Runtime prog-array updates must patch JIT call sites without stale targets.

Test signals: Test signals include successful attach, map update, and expected invocation/return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_poke.c -->

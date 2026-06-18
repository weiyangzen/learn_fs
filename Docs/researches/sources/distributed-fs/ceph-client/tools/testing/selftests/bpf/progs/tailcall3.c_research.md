<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall3.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall3.c

Purpose: Small static tail-call test focused on a single populated target and fallback.

Important APIs/types/functions: Defines `jmp_table`, `classifier_0`, and `entry` in tc sections.

Control flow: `entry` tail-calls index 0 and otherwise returns its fallback value.

State and persistence: Prog-array contents are the only runtime state.

Dependencies and integration: Depends on tc static tail-call support.

Risks: Risk is incorrect patching or fallback path after missing entry.

Test signals: Pass signals are target return when present and fallback when absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall3.c -->

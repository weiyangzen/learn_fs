<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_freplace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_freplace.c

Purpose: Tests tail calls inside a freplace program replacing an entry point.

Important APIs/types/functions: Defines a prog-array `jmp_table` and `entry_freplace` in `freplace` section.

Control flow: Replacement attempts a static tail call and falls back if the prog-array entry is absent.

State and persistence: Prog-array map is persistent state.

Dependencies and integration: Depends on freplace attachment plus static tail-call support.

Risks: Compatibility of replacement context and tail-call map patching is the main risk.

Test signals: Tests attach replacement and validate target/fallback return behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_freplace.c -->

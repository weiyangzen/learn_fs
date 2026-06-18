<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_kprobe_sleepable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_kprobe_sleepable.c

Purpose: Small test for attaching a sleepable kprobe-style program.

Important APIs/types/functions: Defines `handle_kprobe_sleepable` with sleepable attachment attributes.

Control flow: The handler runs on the selected kprobe and returns without complex state.

State and persistence: No persistent maps; any result is via globals if present.

Dependencies and integration: Depends on sleepable kprobe attach support.

Risks: Program type/attach flag mismatch is the key risk.

Test signals: Load/attach success and invocation are the test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_kprobe_sleepable.c -->

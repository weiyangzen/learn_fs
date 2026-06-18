<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tc_dummy.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tc_dummy.c

Purpose: Minimal dummy tc program for attach/load plumbing tests.

Important APIs/types/functions: Defines `entry` in `tc` section returning a simple code.

Control flow: No internal branching; it validates basic tc skeleton handling.

State and persistence: No persistent state.

Dependencies and integration: Depends on tc program loading and license metadata.

Risks: Main risk is section naming or attach-type mismatch.

Test signals: Test signal is successful load/attach and expected return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tc_dummy.c -->

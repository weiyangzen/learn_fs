<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-stress -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-stress

Purpose: shell stress wrapper for `sve-test`, launching many SVE register integrity loops and bombarding them with SIGUSR1.

Important APIs and functions: `cleanup`, `interrupt`, and `child_died` manage process and temp-log lifecycle; uses `nproc`, `mktemp`, `trap`, `kill`, and `wait`.

Control flow: launch `NR_CPUS * 4 + 1` `./sve-test` processes, wait 10 seconds, start infinite SIGUSR1 loop, and wait. EXIT/INT/TERM run cleanup; CHLD exits with failure.

State and persistence: temp log files are transient and printed during cleanup. Process IDs are kept in shell variables.

Dependencies and integration: depends on `sve-test` and SVE-capable runtime.

Risks: tight signal loop can dominate CPU. Simple cleanup may emit errors if children have already exited.

Test signals: child logs show startup and any mismatch; early child death returns 1, user interruption returns 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-stress -->

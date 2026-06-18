<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fpsimd-stress -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fpsimd-stress

Purpose: shell stress wrapper for `fpsimd-test`, launching many instances and repeatedly sending SIGUSR1 to stress signal-frame FPSIMD preservation.

Important APIs and functions: shell functions `cleanup`, `interrupt`, and `child_died`; uses `nproc`, `mktemp`, background jobs, `kill`, `wait`, `trap`, and `sleep`.

Control flow: start `NR_CPUS * 4 + 1` `./fpsimd-test` processes with per-child temp logs, sleep 10 seconds for startup, start an infinite signal sender, and wait. INT/TERM/EXIT clean up children and print logs; CHLD treats early death as failure.

State and persistence: temporary log files are created and removed during cleanup. Process IDs and log paths are tracked in shell variables.

Dependencies and integration: assumes `fpsimd-test` is built in the current directory. It is a simple alternative to the C stress harness for prolonged manual stress runs.

Risks: tight infinite signal loop can consume CPU. Trap cleanup uses unquoted lists and assumes simple temp paths. `kill`/`wait` failures are ignored during cleanup.

Test signals: normal operator interruption exits 0 after printing logs; premature child death exits 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fpsimd-stress -->

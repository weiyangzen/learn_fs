<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-stress -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-stress

Purpose: shell stress wrapper for `za-test`, exercising SME ZA context preservation under repeated signals and many parallel processes.

Important APIs and functions: same shell structure as SVE wrappers: `cleanup`, `interrupt`, `child_died`, `trap`, `mktemp`, `kill`, and `wait`.

Control flow: spawn `NR_CPUS * 4 + 1` `./za-test` children into temp logs, sleep 10 seconds, continuously send SIGUSR1, wait, and clean up on exit.

State and persistence: temp logs are transient; process IDs tracked in shell variables.

Dependencies and integration: requires `za-test` and SME-capable hardware/kernel.

Risks: no CHLD trap is installed despite defining `child_died`, so premature exits may be handled only by `wait`. Infinite signal loop can be CPU-heavy.

Test signals: `za-test` logs contain vector length/PID and mismatch reports; wrapper exits nonzero if wait fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-stress -->

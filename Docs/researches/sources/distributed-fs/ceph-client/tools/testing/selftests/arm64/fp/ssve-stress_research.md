<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/ssve-stress -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/ssve-stress

Purpose: shell stress wrapper for `ssve-test`, the streaming SVE variant of the SVE signal/context-switch test.

Important APIs and functions: same process/log/trap structure as `sve-stress`; launches `./ssve-test`, stores temp logs, sends SIGUSR1 continuously, and cleans up on EXIT/INT/TERM.

Control flow: spawn `NR_CPUS * 4 + 1` children, wait 10 seconds, run an infinite signal sender, and wait for termination. This script does not install the CHLD failure trap present in `fpsimd-stress`, so early child death handling differs.

State and persistence: shell PID and temp-log lists only; logs are printed then removed during cleanup.

Dependencies and integration: depends on `ssve-test` being built, typically from `sve-test.S` with `SSVE` enabled.

Risks: no CHLD trap means unexpected child death may not stop the script immediately. Tight signal loop can be aggressive.

Test signals: logs show child startup and mismatch/termination output; process exit is governed by cleanup or failed `wait`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/ssve-stress -->

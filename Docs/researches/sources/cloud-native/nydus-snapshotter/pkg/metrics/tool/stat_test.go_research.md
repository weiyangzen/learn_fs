# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/tool/stat_test.go

This test file contains `TestFindZombie`, which calls `GetProcessRunningState(1)` and asserts no error and that PID 1's state string contains either `Ss` or `S`. It is a minimal smoke test for reading and parsing `/proc/<pid>/stat`.

The test signal is limited but useful: it verifies the code can access `/proc`, split the stat fields, and extract the process state on the test host. It does not spawn or detect an actual zombie process despite the test name, and it does not exercise `GetProcessStat`, fd counting, CPU utilization, RSS calculation, or parse-error paths.

Risks include portability and environment sensitivity. PID 1 may not have state `Ss` or `S` in all containers or systems, and non-Linux environments lack `/proc`. No persistent state is used. Broader metrics correctness is covered only by runtime behavior, not this test.

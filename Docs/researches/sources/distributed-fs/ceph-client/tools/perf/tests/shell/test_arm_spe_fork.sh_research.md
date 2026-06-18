## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_spe_fork.sh

Purpose: checks that Arm SPE recording does not hang when tracing a workload with forks/threads.
Important behavior: records `perf test -w sqrtloop 10` with `arm_spe/period=65536/ -vvv`, samples perf record log line counts after two one-second intervals, then kills perf.
Control flow: if log line count is unchanged between intervals, it reports a hang failure; otherwise pass.
State and persistence: temp perf.data and log are removed.
Dependencies and integration: Arm SPE PMU and verbose perf record progress output.
Risks: log growth is a proxy for liveness and can be flaky if output quiets naturally; kill/wait behavior assumes perf responds.
Test signals: increasing verbose log line count during recording.

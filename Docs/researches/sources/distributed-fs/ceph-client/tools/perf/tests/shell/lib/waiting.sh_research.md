## sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/waiting.sh

Purpose: polling utilities for asynchronous shell tests that launch workloads or background `perf record`.
Important functions: `wait_for_threads`, `wait_for_perf_to_start`, `wait_for_process_to_exit`, and `is_running`.
Control flow: functions poll `/proc/$pid`, `/proc/$pid/task`, or a perf debug log until conditions are met or a tenths-of-a-second timeout expires.
State and persistence: no persistent state; `tenths` command computes current time with tenths precision.
Dependencies and integration: sourced by `record.sh` and `test_intel_pt.sh` to avoid races around thread creation, perf startup, and workload exit.
Risks: relies on `/proc` and a specific verbose message, `perf record has started`; slow or heavily loaded systems can hit timeout-driven false failures.
Test signals: zero return means the synchronization condition occurred; nonzero return includes a diagnostic suitable for perf test logs.

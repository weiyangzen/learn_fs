## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record.sh

Purpose: broad exclusive integration suite for `perf record` modes and parse terms.
Important functions: `test_per_thread`, `test_register_capture`, `test_system_wide`, `test_workload`, `test_branch_counter`, `test_cgroup`, `test_uid`, `test_leader_sampling`, `test_topdown_leader_sampling`, `test_precise_max`, `test_callgraph`, and `test_ratio_to_prev`.
Control flow: after symbol checks for `test_loop` and `brstack`, it raises file descriptor limits for CPU-thread mode, records workload variants, reports or scripts back evidence, and validates parse-time errors for invalid `ratio-to-prev` use.
State and persistence: temp perf.data and script output files are reused and removed; process state includes background `perf test -w thloop` during per-thread attach.
Dependencies and integration: uses `lib/waiting.sh`, `lib/perf_has_symbol.sh`, perf workloads, CPU PMU sysfs caps, cgroups, `bc`, and hardware event support.
Risks: permissions, hardware capabilities, throttling, hybrid PMUs, and architecture-specific event availability cause skips or tolerance-based checks.
Test signals: report symbols, branch counter dump/script text, CGROUP records, UID sampling output, grouped cycles consistency, and expected parser diagnostics.

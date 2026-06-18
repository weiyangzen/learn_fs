# sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/tbench.sh

Purpose: AMD P-state throughput/power benchmark using `tbench` across governors.

Important APIs/types/functions: inclusion guard `FILE_TBENCH`; governor list; CSV/cleanup helpers; `run_tbench()` starts tracer and `tbench_srv`, runs `tbench` under `perf stat`, kills server, waits for jobs; `parse_tbench()`, `gather_tbench()`, comparison helpers, `plot_png_tbench()`, and `amd_pstate_tbench()` orchestrate results.

Control flow: clears prior outputs, writes CSV headers, backs up governors, for each governor switches policy governors, loops benchmark runs, parses tracer CPU metrics, throughput, energy, and performance per watt, restores governors, plots, computes comparisons, and cleans logs.

State and persistence: starts/kills `tbench_srv`, modifies governors, writes CSV/result/PNG/log/tracer output directories, then removes many transient files.

Dependencies/integration: sourced by `run.sh`; requires tbench, perf energy events, AMD pstate tracer, `bc`, `awk`, `gnuplot`, and cpufreq sysfs.

Risks and test signals: `kill $pid` can misbehave if `pidof tbench_srv` returns empty or multiple PIDs. Plot file name has typo `tbench_perfromance.png`. Metrics depend on perf energy availability.

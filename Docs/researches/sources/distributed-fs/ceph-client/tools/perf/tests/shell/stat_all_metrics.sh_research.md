## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_all_metrics.sh

Purpose: attempts every individual metric from `perf list --raw-dump metrics`.
Important behavior: uses system-wide `sleep 0.01` when permitted, otherwise a `noploop` workload; retries failures with `perf bench internals synthesize`.
Control flow: treats missing events, not-supported/not-counted output, FP/AMX/PMM issues, and permission restrictions according to expected skip/ignore rules; hard-fails when a non-Default metric cannot be printed.
State and persistence: no files.
Dependencies and integration: metric JSON/sysfs metadata, perf stat metric evaluation, and fallback workloads.
Risks: highly platform-dependent and may be noisy across PMU generations; output match uses first 50 chars of metric name.
Test signals: metric name appears in successful output or a recognized skip/ignore reason is printed.

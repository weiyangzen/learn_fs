## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_data_symbol.sh

Purpose: validates data symbol resolution for memory profiling events.
Important behavior: records a `datasym` workload with memory load/store events, then checks `perf report` or `perf script` output for the expected data symbol.
Control flow: chooses event/recording options based on architecture/PMU support, handles AMD IBS `mem-ldst` and `--ldlat` behavior, and uses verbose record logs for diagnostics.
State and persistence: temp perf.data and error log are cleaned.
Dependencies and integration: `perf mem`, data-symbol workload, CPU-specific memory sampling PMUs, and symbol resolution.
Risks: memory event names and latency controls vary by vendor and kernel; older AMD kernels have filtering limits requiring per-CPU mode.
Test signals: expected data symbol appears in decoded memory samples without record errors.

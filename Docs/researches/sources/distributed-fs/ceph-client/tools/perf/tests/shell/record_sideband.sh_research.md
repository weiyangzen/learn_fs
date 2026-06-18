## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_sideband.sh

Purpose: validates sideband tracking events when recording CPU-wide on one CPU while the workload runs on another.
Important functions: `can_cpu_wide` and `test_system_wide_tracking`.
Control flow: probes recording on CPU 0 and CPU 1, records on CPU 0 with `taskset` binding workload to CPU 1, then checks `perf script --show-mmap-events -C 1` for MMAP events.
State and persistence: temp perf.data file is removed.
Dependencies and integration: uses CPU-wide recording, taskset, sideband MMAP synthesis, and `--no-bpf-event`.
Risks: systems with fewer than two CPUs, CPU affinity restrictions, or perf_event_paranoid can skip/fail; only MMAP count is validated.
Test signals: nonzero MMAP event count for CPU 1 while tracing CPU 0.

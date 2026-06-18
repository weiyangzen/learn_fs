## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_intel_pt.sh

Purpose: large exclusive Intel Processor Trace integration suite.
Important functions: `perf_record_no_decode`, `perf_record_no_bpf`, `can_cpu_wide`, `test_system_wide_side_band`, `can_kernel`, `test_per_thread`, `test_jitdump`, `test_packet_filter`, `test_disable_branch`, `test_time_cyc`, `test_sample`, `test_kernel_trace`, `test_virtual_lbr`, `test_power_event`, `test_no_tnt`, `test_event_trace`, `test_pipe`, `test_pause_resume`, and `count_result`.
Control flow: skips without `intel_pt//`, compiles helper workloads, validates sideband MMAP events, per-thread AUX mmap setup, JIT dump injection, packet filters, feature caps from sysfs, sample mode, virtual LBR, pipe mode, and pause/resume actions.
State and persistence: temp directory holds workloads, awk/Python scripts, perf data, stdout/stderr logs, and is path-checked before deletion.
Dependencies and integration: Intel PT PMU, compiler, libelf for JIT, sysfs caps, `waiting.sh`, taskset, perf inject/script/report.
Risks: hardware cap matrix is broad; compiled helper failures skip some paths; verbose log parsing and AWK fd validation are format-sensitive.
Test signals: accumulated ok/skip/error counters; any error fails, at least one ok passes, all skips exit `2`.

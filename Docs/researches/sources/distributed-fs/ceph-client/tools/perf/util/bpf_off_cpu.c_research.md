# sources/distributed-fs/ceph-client/tools/perf/util/bpf_off_cpu.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_off_cpu.c

Purpose: this file wires BPF off-CPU time tracking into `perf record`. It adds a `bpf-output` event, loads the off-CPU skeleton, installs record-start/end hooks, and writes aggregated BPF off-CPU records into the perf data file as synthetic samples.

Important APIs and functions: `off_cpu_config()` adds the `OFFCPU_EVENT` bpf-output event and marks it system-wide. `check_sched_switch_args()` inspects vmlinux BTF to determine whether `sched_switch` tp_btf includes `prev_state`. `off_cpu_prepare()` configures CPU/task/cgroup filters, cgroup recording, thresholding, loads and attaches BPF, and registers hooks. `off_cpu_start()` fills the BPF perf-event array and enables collection. `off_cpu_finish()` disables and destroys the skeleton. `off_cpu_write()` emits aggregated map contents as `PERF_RECORD_SAMPLE` records.

Control flow: prepare always creates the output evsel first. Target mode controls BPF filter map size and whether task keys are pid or tgid. For `target__none`, the start hook adds the workload pid into the task filter after fork. On record start, the output map is populated from the evsel fd array per CPU. On write, the code validates supported sample types, builds a sample buffer containing id/ip/tid/time/cpu/period/raw/cgroup fields as requested, reads the BPF stack map for callchains, and writes records with increasing dummy timestamps near the end of time ordering.

State and persistence: static `skel` is the active session. BPF maps store task-storage timestamps, stack ids, aggregated off-CPU durations, and optional direct output payloads. `OFF_CPU_TIMESTAMP` intentionally places synthetic samples late in sorting. No persistent filesystem state exists beyond the perf data file written by `off_cpu_write()`.

Dependencies and integration: it depends on perf hooks, evlist parsing, record options, cgroup helpers, thread/CPU maps, perf session I/O, and the `off_cpu` skeleton. It integrates with perf record by adding a bpf-output evsel and with later analysis through raw sample payload layout.

Risks: `off_cpu_write()` disables BPF but assumes the skeleton remains valid until after writing; hook ordering is important. Only sample types in `OFFCPU_SAMPLE_TYPES` are supported. Stack collection can produce zero or negative stack ids, and raw payload layout must remain synchronized with parsers. Threshold behavior splits direct perf-output samples from map-aggregated samples, so tests must cover both paths. BTF absence weakens sched_switch signature detection.

Test signals: record off-CPU with pid, tid, workload, CPU, cgroup, and record-cgroup options; test kernels before and after the `prev_state` sched_switch change; verify thresholded direct output and aggregated map output; inspect resulting perf data with report/script; and compare cgroup ids on cgroup v1/v2.

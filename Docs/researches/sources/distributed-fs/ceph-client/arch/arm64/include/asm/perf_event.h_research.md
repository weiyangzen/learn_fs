# sources/distributed-fs/ceph-client/arch/arm64/include/asm/perf_event.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/perf_event.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/perf_event.h

### Purpose
`perf_event.h` defines ARM64 perf register access helpers for BPF/perf callchain sampling.

### Important APIs, Types, And Functions
It provides `perf_arch_bpf_user_pt_regs(regs)` and `perf_arch_fetch_caller_regs(regs, __ip)` to populate `pt_regs` snapshots with caller IP and stack pointer.

### Control Flow
Perf/BPF sampling code calls these macros when preparing architecture register views for events or BPF programs.

### State, Persistence, And Dependencies
State is transient `pt_regs` sample data. It depends on stack pointer helpers and `asm/ptrace.h`.

### Integration Points
Used by perf, eBPF tracing/profiling, and observability of filesystem/network workloads.

### Risks
Incorrect register snapshots degrade profiling accuracy or BPF helper behavior. Stack pointer choice must match the sampled context.

### Test Signals
Run perf record/report, BPF perf-event tests, callchain sampling, and interrupt/NMI-like sampling paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/perf_event.h -->

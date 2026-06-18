# sources/distributed-fs/ceph-client/tools/bpf/bpftool/skeleton/profiler.bpf.c

Purpose: BPF side of `bpftool prog profile`. It attaches to a target program's fentry/fexit, reads perf event counters around each invocation, accumulates deltas per metric, and counts samples.

Important APIs, types, and functions: Defines `events` perf-event-array map, `fentry_readings`, `accum_readings`, and `counts` percpu-array maps. `num_cpu` and `num_metric` are rodata set by userspace. `fentry_XXX()` snapshots perf counters before target execution. `fexit_XXX()` reads after counters, increments sample count, and calls `fexit_update_maps()` to accumulate deltas.

Control flow: fentry looks up per-metric slots first, then reads each perf event at key `cpu + metric * num_cpu`. fexit reads all after-values before modifying maps, then updates count and accumulators if a valid before counter exists.

State and persistence: State is in BPF maps and is per-CPU. It persists only for the lifetime of the loaded profiler object and is read by `prog.c` cleanup/print logic.

Dependencies and integration points: Loaded from `profiler.skel.h` by bpftool. Depends on perf-event-array map entries populated by userspace, attach target replacement for `XXX`, and BPF helpers `bpf_perf_event_read_value()` and `bpf_get_smp_processor_id()`.

Risks: Hard limit `MAX_NUM_METRICS` is 4. Missing fentry readings suppress accumulation. Perf event read errors abort each probe invocation. Counter deltas can be affected by multiplexing, shown through enabled/running in userspace.

Test signals: Profile a BPF program with one to four selected metrics, verify counts increase, accumulators are nonzero, and offline CPU handling is managed by userspace map setup.

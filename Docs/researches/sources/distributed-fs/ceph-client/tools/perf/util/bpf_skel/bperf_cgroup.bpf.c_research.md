# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_cgroup.bpf.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_cgroup.bpf.c

Purpose: this in-kernel BPF program implements cgroup-aware bperf aggregation. It reads shared perf-event counters on cgroup switches or explicit trigger reads and accumulates deltas into per-cgroup readings.

Important maps and globals: `events` is a perf-event array holding one global event set per CPU. `cgrp_idx` maps cgroup ids to perf evlist cgroup indexes. `prev_readings` stores per-CPU previous event values, and `cgrp_readings` stores per-cgroup/event per-CPU accumulated values. Volatile rodata `num_events`, `num_cpus`, and `use_cgroup_v2` are set by user space; BSS `enabled` gates accumulation.

Control flow: `on_cgrp_switch` and `trigger_read` both call `bperf_cgroup_count()`. That helper finds matching ancestor cgroups for the current task using either cgroup v2 helper ids or cgroup v1 perf_event subsystem ancestry, reads each configured event for the current CPU, computes deltas from `prev_readings`, and adds deltas to every matching cgroup's `cgrp_readings` row only when enabled. Previous readings are always refreshed.

State and persistence: BPF per-CPU maps retain previous and aggregate readings across context switches until the skeleton is destroyed. `perf_subsys_id` is lazily initialized for cgroup v1.

Dependencies and integration: user space sizes maps and populates `events`/`cgrp_idx` in `bpf_counter_cgroup.c`. It relies on CO-RE field handling for old/new cgroup structures and on constants in `bperf_cgroup.h`.

Risks: loops are bounded by `BPERF_CGROUP__MAX_EVENTS` and `BPERF_CGROUP__MAX_LEVELS`; increasing constants may exceed verifier limits. Missing cgroup map entries skip aggregation for that ancestor. Because previous readings refresh even when disabled, enable/disable semantics intentionally avoid counting disabled time but depend on trigger cadence.

Test signals: validate cgroup v1/v2 aggregation, nested cgroup ancestry, multi-event map sizing, enable/disable boundaries, and verifier loading at maximum event constants.

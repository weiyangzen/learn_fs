# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/aperfmperf.c

## Purpose
This file samples APERF/MPERF MSRs to report current CPU frequency and support scheduler frequency/capacity invariance on x86.

## Important APIs, Types, and Functions
Per-CPU samples use `struct aperfmperf` with a seqcount, timestamps, counter deltas, and last raw values. Public functions include `arch_set_max_freq_ratio()`, `freq_invariance_set_perf_ratio()`, `arch_enable_hybrid_capacity_scale()`, `arch_set_cpu_capacity()`, `arch_scale_cpu_capacity()`, `arch_scale_freq_tick()`, `arch_freq_get_on_cpu()`, `bp_init_aperfmperf()`, and `ap_init_aperfmperf()`. Intel ratio discovery uses `slv_set_max_freq_ratio()`, `knl_set_max_freq_ratio()`, `skx_set_max_freq_ratio()`, `core_set_max_freq_ratio()`, and `intel_set_max_freq_ratio()`.

## Control Flow
Early boot initializes APERF/MPERF references on the boot CPU and, on Intel SMP x86-64, derives a max turbo/base ratio and enables the static key for scheduler frequency invariance. AP startup initializes local counter references. Each scheduler tick reads APERF/MPERF, computes deltas, publishes them under a seqcount, and updates `arch_freq_scale` if invariance is active. Frequency queries read recent deltas if fresh enough, otherwise fall back to cpufreq or `cpu_khz`. Hybrid capacity scaling allocates per-CPU capacity/frequency-ratio data and enables a separate static key.

## State and Persistence
Persistent state includes per-CPU APERF/MPERF samples, per-CPU `arch_freq_scale`, static keys for frequency and hybrid capacity scaling, global turbo/max ratios, optional per-CPU hybrid scaling data, syscore resume hooks, and a work item that disables invariance on arithmetic failure.

## Dependencies and Integration Points
The file depends on APERF/MPERF MSRs, Intel family/model matching, cpufreq, scheduler topology and capacity scaling, syscore resume, CPU hotplug init paths, static keys, seqcounts, overflow-safe math, and SMP/IPI-safe per-CPU access.

## Risks and Test Signals
Risks include stale samples on idle/NOHZ CPUs, hypervisors returning zero MSRs, bad turbo ratio heuristics, overflow in scale math, hybrid capacity misuse before enablement, and resume losing counter references. Test signals include scaling_cur_freq behavior, scheduler frequency invariance enabled logs, fallback behavior on old samples, syscore resume reinitialization, hybrid capacity tests, and warning-triggered invariance disable path.

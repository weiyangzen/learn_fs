# sources/distributed-fs/ceph-client/samples/bpf/cpustat_kern.c

Purpose: BPF tracepoint program that accumulates CPU idle-state and frequency-state residency durations.

Important APIs/types/functions: maps `my_map`, `cstate_duration`, `pstate_duration`, constants for 8 CPUs, 3 C-states, and 5 P-states, `find_cpu_pstate_idx`, tracepoint programs `bpf_prog1` for `power/cpu_idle` and `bpf_prog2` for `power/cpu_frequency`.

Control flow: tracepoint handlers look up per-CPU timestamp/state slots, compute deltas from `bpf_ktime_get_ns`, and atomically add durations to cstate or pstate duration maps. Idle entry records current pstate time; idle exit records previous cstate time. Frequency changes record previous pstate time when the CPU is not idle.

State and persistence: all state is in BPF array maps for current timestamps/state indices and accumulated durations. Maps persist while the object is loaded.

Dependencies and integration: attached and read by `cpustat_user.c`; depends on power tracepoint formats and platform-specific frequency values listed in `cpu_opps`.

Risks: constants are Hikey-specific; CPUs beyond the assumed range are ignored or risk off-by-one behavior because `ctx->cpu_id > MAX_CPU` should likely be `>=`. Atomic adds on map values are shared across event contexts. Frequency sysfs assumptions live in the user program.

Test signals: attach both tracepoints, trigger idle and frequency events, and confirm duration maps change and printed residency totals are plausible.

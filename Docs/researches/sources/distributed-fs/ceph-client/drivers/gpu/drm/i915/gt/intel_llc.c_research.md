<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc.c

Purpose: programs LLC-related IA/ring frequency tables so integrated GPUs with shared LLC can request memory-ring or CPU-reference frequencies appropriate to GT frequency.

Important APIs and functions: `intel_llc_enable()` calls `gen6_update_ring_freq()`; `intel_llc_disable()` is currently a no-op. Internal helpers include `llc_to_gt()`, `cpu_max_MHz()`, `get_ia_constants()`, `calc_ia_freq()`, and `gen6_update_ring_freq()`.

Control flow: enable reads CPU maximum frequency from cpufreq or TSC fallback, reads DCLK-derived minimum ring frequency, obtains RPS min/max raw GPU frequencies, and iterates from max to min GPU frequency. For each GPU frequency, `calc_ia_freq()` derives IA and ring ratios differently for Gen9+, Gen8, Haswell, and older shared-clock platforms, then writes the PCODE min-frequency table with `snb_pcode_write()`.

State and persistence: no software state is stored in `struct intel_llc`; the effective state is the PCU frequency table programmed into hardware. The table persists until power/reset/firmware changes require reprogramming.

Dependencies and integration points: depends on cpufreq, TSC frequency, PCODE register interface, intel RPS min/max frequency state, DCLK register, and GT uncore. It is part of GT power/frequency setup and only applies when `HAS_LLC(i915)` and not discrete graphics.

Risks: bad frequency conversion can overconstrain IA/ring frequencies or reduce memory bandwidth. `max_gpu_freq <= min_gpu_freq` is guarded to avoid an unsigned loop underflow. cpufreq absence falls back to measured TSC and relies on PCU clamping. PCODE write failures are not surfaced by `intel_llc_enable()`.

Test signals: `selftest_llc.c`, boot on Gen6-HSW/BDW/SKL class hardware, RPS min/max variation, cpufreq unavailable cases, PCODE trace/debug logging, and memory-bandwidth/power telemetry when GT frequency changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc.c -->

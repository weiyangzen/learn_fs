# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/pmu.c

Purpose: performs x86-specific PMU initialization. It marks Intel PT/BTS PMUs as AUX trace capable, attaches x86 memory event template tables, and adjusts Granite Rapids uncore CHA/IMC CPU masks for sub-NUMA clustering.

Important APIs/types/functions: `perf_pmu__arch_init()` is the exported hook. `x86__is_intel_graniterapids()` caches CPUID matching. `snc_nodes_per_l3_cache()`, `num_chas()`, `uncore_cha_snc()`, `uncore_imc_snc()`, and `uncore_cha_imc_compute_cpu_adjust()` derive SNC mapping. `gnr_uncore_cha_imc_adjust_cpumask_for_snc()` rewrites PMU cpumaps. `read_sysfs_cpu_map()` parses sysfs CPU lists.

Control flow: arch init first recognizes `intel_pt` and `intel_bts`. On AMD, it only handles `ibs_op`, selecting basic or ldlat-capable memory events after cap parsing. On non-AMD Intel, core PMUs receive Intel memory events, with `mem-loads-aux` preferred if available. For Granite Rapids uncore CHA/IMC PMUs, cpumasks are adjusted from socket-level first CPUs to SNC-node first CPUs.

State and persistence: caches CPUID result, SNC counts, CHA count, per-SNC CPU adjustments, and adjusted cpumaps in static variables. The persistent runtime effect is mutation of `struct perf_pmu` fields: `auxtrace`, `selectable`, default attr init callback, `mem_events`, and `cpus`.

Dependencies and integration: depends on PMU/sysfs APIs, internal cpumap refcounted maps, CPUID helper, x86 vendor detection, Intel PT/BTS names, memory event arrays, and sysfs topology paths for NUMA nodes and L3 cache sharing.

Risks: Granite Rapids SNC logic assumes naming/order of `uncore_cha_N` and lookup tables for IMC SNC2/SNC3 only. `snc_nodes_per_l3_cache()` divides map sizes and assumes both sysfs reads succeed. CPU adjust path has assertions and bounds assumptions. Static adjusted cpumaps are retained for process lifetime.

Test signals: perf list/record for Intel PT/BTS, `perf mem` on Intel and AMD IBS, Granite Rapids per-node uncore stat output under SNC2/SNC3, and sysfs-failure tests for missing node/cache paths.

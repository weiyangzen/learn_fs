# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cacheinfo.c

## Purpose
`cacheinfo.c` detects x86 cache topology, populates Linux cacheinfo leaves, maintains shared L2/LLC CPU masks, and coordinates cache-disable/cache-enable sequences used by MTRR and PAT programming. It supports Intel deterministic CPUID leaf 4, legacy Intel descriptor leaf 2, AMD/Hygon deterministic leaf `0x8000001d`, and legacy AMD cache leaves.

## Important APIs, Types, and Functions
Per-CPU state includes `cpu_llc_shared_map` and `cpu_l2c_shared_map`; global cache-control state includes `memory_caching_control`, `cpu_cacheinfo_mask`, `cache_aps_delayed_init`, `saved_cr4`, and `cache_disable_lock`.

Detection helpers include `_cpuid4_*` unions, `_cpuid4_info`, `legacy_amd_cpuid4()`, `amd_fill_cpuid4_info()`, `intel_fill_cpuid4_info()`, `fill_cpuid4_info()`, `find_num_cache_leaves()`, `get_cache_id()`, `calc_cache_topo_id()`, `intel_cacheinfo_0x2()`, and `intel_cacheinfo_0x4()`. Public/vendor APIs include `cacheinfo_amd_init_llc_id()`, `cacheinfo_hygon_init_llc_id()`, `init_amd_cacheinfo()`, `init_hygon_cacheinfo()`, `init_intel_cacheinfo()`, `init_cache_level()`, and `populate_cache_leaves()`.

Cache-control APIs are `cache_disable()`, `cache_enable()`, `cache_bp_init()`, `cache_bp_restore()`, `cache_aps_init()`, `set_cache_aps_delayed_init()`, and `get_cache_aps_delayed_init()`.

## Control Flow
Vendor CPU initialization calls `init_*_cacheinfo()` to set cache sizes, LLC IDs, L2 IDs, and cache leaf counts. Intel first tries CPUID leaf 4, accumulating L1/L2/L3 sizes and topology IDs, and falls back to CPUID leaf 2 descriptor parsing through `cpuid_0x2_table`. AMD/Hygon use deterministic leaf `0x8000001d` when topology extensions are available, otherwise `legacy_amd_cpuid4()` synthesizes leaf-4-like data from leaves `0x80000005` and `0x80000006`.

The generic cacheinfo framework calls `init_cache_level()` and `populate_cache_leaves()`. `populate_cache_leaves()` fills each `struct cacheinfo`, computes cache IDs, attaches AMD northbridge private data for L3 when available, and populates shared CPU maps using AMD/Hygon special cases or APIC-ID-derived sharing.

Boot cache-control starts with `cache_bp_init()`, which initializes MTRR/PAT state and programs the boot CPU when `memory_caching_control` requests it. AP handling is registered by `cache_ap_register()`. AP cache programming is either delayed until `cache_aps_init()` or run on online hotplug via `stop_machine_from_inactive_cpu()`.

## State and Persistence
Detected cache topology is stored in `cpuinfo_x86` topology fields and per-CPU `struct cpu_cacheinfo` lists. Shared CPU maps evolve with CPU online/offline state. MTRR/PAT programming persists in CPU MSRs and must be replayed on boot CPU restore, AP startup, resume, and hotplug. `cache_disable()` temporarily changes CR0.CD and CR4.PGE, disables MTRRs, flushes caches/TLBs, and serializes the sequence with a raw spinlock; `cache_enable()` reverses it.

## Dependencies and Integration Points
The file depends on `linux/cacheinfo`, CPU hotplug, stop_machine, CPUID helpers, AMD northbridge L3 support, MTRR, PAT, TLB flush accounting, APIC topology from `cpu_data`, and the Intel leaf-2 descriptor table. It feeds sysfs cacheinfo, scheduler/topology assumptions about LLC sharing, and memory type initialization.

## Risks
Cache size/topology detection is vendor-specific and CPUID-dependent; wrong sharing IDs can mislead scheduler/cacheinfo consumers. Legacy AMD fallback must handle invalid associativity encodings. Cache-disable sequences are high-risk because interrupts must already be disabled by the caller and because only the local CPU is cache-disabled while MTRRs are changed. Hotplug ordering is delicate: MTRR mutex cannot be held in early AP startup, so the code relies on stop_machine and cpuhotplug locking assumptions.

## Test Signals
Validate `/sys/devices/system/cpu/cpu*/cache/index*` size, type, ID, and shared CPU maps on Intel, AMD, Hygon, SMT, multi-die, and no-L3 systems. Exercise CPU hotplug and resume paths with MTRR/PAT enabled. Compare dmesg cache/TLB output and `lscpu -C` against expected CPUID. Run with delayed AP cache initialization both true and false.

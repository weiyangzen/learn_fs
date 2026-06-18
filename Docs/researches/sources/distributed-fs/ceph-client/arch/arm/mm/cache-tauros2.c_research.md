# sources/distributed-fs/ceph-client/arch/arm/mm/cache-tauros2.c

Purpose: initializes Marvell Tauros2 L2 cache support on PJ1/PJ4 CPUs, enabling optional prefetch and burst features and registering outer-cache callbacks for pre-v7 operation modes.

Important APIs/types/functions: important functions include `tauros2_clean_pa`, `tauros2_clean_inv_pa`, `tauros2_inv_pa`, `tauros2_inv_range`, `tauros2_clean_range`, `tauros2_flush_range`, `tauros2_disable`, `tauros2_resume`, `read_extra_features`, `write_extra_features`, `cpuid_scheme`, `read_mmfr3`, `read_actlr`, `write_actlr`, `enable_extra_feature`, `tauros2_internal_init`, and `tauros2_init`. Feature bits include `CACHE_TAUROS2_PREFETCH_ON` and `CACHE_TAUROS2_LINEFILL_BURST8`.

Control flow: public init optionally reads DT compatible `marvell,tauros2-cache` and `marvell,tauros2-cache-features`, then calls internal init. It configures prefetch/burst bits. On ARMv5-like mode it enables L2 through the extra-features register and installs `outer_cache` range/disable/resume callbacks. On ARMv7 hierarchical-cache mode it enables L2 through ACTLR and relies on v7 cache maintenance instead of registering outer callbacks.

State and persistence: no C global state beyond `outer_cache` assignments. CP15 extra-feature and ACTLR bits persist until reset/suspend handling changes them.

Dependencies and integration points: depends on Marvell Tauros2 CP15 registers, CPU ID/MMFR3 detection, device tree, and global `outer_cache`. It is selected by `CACHE_TAUROS2`.

Risks: CPU mode detection is critical: registering outer callbacks on v7 hierarchical systems would duplicate maintenance, while failing to register them on ARMv5 mode would break DMA coherency. DT feature property absence intentionally disables extra features. CP15 register writes are CPU-specific.

Test signals: boot PJ1/PJ4 systems in ARMv5 and ARMv7 personalities, verify feature bits from DT, run DMA range operations on ARMv5 mode, confirm v7 mode uses hierarchical cache ops, and exercise suspend/resume when `outer_cache.resume` is installed.

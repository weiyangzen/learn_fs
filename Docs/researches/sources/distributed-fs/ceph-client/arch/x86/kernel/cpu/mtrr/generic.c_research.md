# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/generic.c

Purpose: implements generic Intel-style MTRR state reading, writing, and lookup. It builds an effective cache-type map from fixed ranges, variable ranges, default type, and AMD TOP_MEM2, supports guest-forced read-only MTRR state, and provides the `generic_mtrr_ops` backend.

Important APIs/types/functions: key types are `fixed_range_block` and `cache_map`. Globals include `mtrr_debug`, `mtrr_tom2`, `mtrr_state`, `phys_hi_rsvd`, cache-map state, and `mtrr_state_set`. Public functions include `mtrr_build_map()`, `mtrr_copy_map()`, `guest_force_mtrr_state()`, `mtrr_type_lookup()`, `fill_mtrr_var_range()`, `mtrr_save_fixed_ranges()`, `get_mtrr_state()`, `mtrr_state_warn()`, `mtrr_wrmsr()`, `mtrr_disable()`, `mtrr_enable()`, `mtrr_generic_set_state()`, `generic_get_free_region()`, `generic_validate_add_page()`, `positive_have_wrcomb()`, and `generic_mtrr_ops`.

Control flow: boot reads `MSR_MTRRcap`, variable ranges, fixed ranges, `MSR_MTRRdefType`, and AMD TOM2, then builds an ordered cache map. Fixed entries are inserted first and marked as fixed; variable ranges are overlaid with effective type merging rules. Runtime MTRR changes rebuild variable portions of the map. `mtrr_type_lookup()` walks the map and default type to return the effective memory type and whether it is uniform. Generic writes disable caches through caller sequencing, write base/mask MSRs, and update `mtrr_state`.

State and persistence: owns the effective cache-map array, initially in `__initdata` and later copied to heap by `mtrr_copy_map()`. It stores global hardware snapshot state in `mtrr_state`; actual persistence is CPU MSR state only.

Dependencies and integration points: used by `mtrr.c` during boot and runtime changes, by PAT/memtype code through `mtrr_type_lookup()`, by virtualized platforms through `guest_force_mtrr_state()`, and by cleanup through `fill_mtrr_var_range()`. Depends on MTRR MSRs, cache disable/enable helpers, SEV-SNP/TDX/Hyper-V/Xen guest detection, and AMD SYSCFG/TOM2 handling.

Risks: effective type resolution is security- and correctness-critical for memory mappings. Cache-map exhaustion disables MTRRs. Guest-forced state clears `X86_FEATURE_MTRR` to prevent later mutation and must only be accepted for vetted virtualization cases. Reserved high bits must be masked using physical address width. Fixed MTRR precedence over variable ranges must be preserved.

Test signals: `mtrr=debug` map output, fixed and variable overlap cases, UC/WB/WT effective type combinations, AMD TOM2 handling, guest-forced MTRR state under Hyper-V/Xen/SNP/TDX, runtime add/delete rebuilding, `mtrr_type_lookup()` uniform/non-uniform ranges, and BIOS inconsistent-MTRR warnings on SMP.

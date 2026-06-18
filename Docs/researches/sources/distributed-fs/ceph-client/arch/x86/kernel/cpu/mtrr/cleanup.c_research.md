# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/cleanup.c

Purpose: sanitizes problematic BIOS MTRR layouts during early boot and trims RAM that is not covered by write-back MTRRs. With `CONFIG_MTRR_SANITIZER`, it can search for a better variable-MTRR layout that covers RAM with fewer or cleaner WB/UC ranges.

Important APIs/types/functions: key types are `var_mtrr_range_state`, `var_mtrr_state`, and `mtrr_cleanup_result`. Exported/init functions are `mtrr_cleanup()`, `amd_special_default_mtrr()`, and `mtrr_trim_uncached_memory()`. Helpers include `x86_get_mtrr_mem_range()`, `range_to_mtrr()`, `range_to_mtrr_with_hole()`, `x86_setup_var_mtrrs()`, `mtrr_need_cleanup()`, `mtrr_calc_range_state()`, `mtrr_search_optimal_index()`, `real_trim_memory()`, and early-parameter parsers for cleanup, chunk/granularity, spare registers, and trim disablement.

Control flow: cleanup snapshots current variable MTRRs, checks for a default UC setup with only WB and UC ranges, derives RAM ranges from WB entries minus UC/WP holes and AMD TOM2 removal, then either applies user-specified chunk/granularity or searches combinations from 64K up to 2G. The best zero-loss setting with enough spare registers is converted into `mtrr_state.var_ranges` via `fill_mtrr_var_range()`. Trimming separately computes covered WB ranges and reserves uncovered RAM in the E820 table.

State and persistence: uses `__initdata` arrays `range[]`, `range_state[]`, `result[]`, `min_loss_pfn[]`, and boot parameters. It mutates global `mtrr_state.var_ranges` and can update the E820 memory map by converting RAM to reserved. No filesystem state is written.

Dependencies and integration points: called from `mtrr_bp_init()` after generic MTRR state is read. Depends on common MTRR ops, `e820__range_update()`, range manipulation helpers, AMD `MSR_AMD64_SYSCFG` and `MSR_K8_TOP_MEM2`, early params, and `changed_by_mtrr_cleanup` in `mtrr.c`.

Risks: incorrect cleanup can mark usable RAM uncached or expose MMIO as write-back. The search space is bounded and may fail on complex layouts. Low-memory fixed MTRR precedence is special-cased; mistakes below 1MB can break legacy mappings. E820 trimming permanently removes RAM for this boot and warns loudly. Virtualized systems with blank MTRRs are intentionally skipped.

Test signals: BIOS layouts with UC default plus WB/UC variable entries, command-line `enable_mtrr_cleanup`, `disable_mtrr_cleanup`, `mtrr_chunk_size=`, `mtrr_gran_size=`, `mtrr_spare_reg_nr=`, `disable_mtrr_trim`, AMD TOM2 systems, virtualized blank MTRRs, E820 update logs, and debug output with `mtrr=debug`.

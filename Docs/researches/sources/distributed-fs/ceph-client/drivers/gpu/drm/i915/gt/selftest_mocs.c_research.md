# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_mocs.c Research

Purpose: this live suite checks that Memory Object Control State and L3 cache-control tables are programmed as expected for kernel contexts, new user contexts, and after engine/global reset.

Important APIs/types/functions: `struct live_mocs` bundles expected `drm_i915_mocs_table`, optional MOCS/L3CC pointers, a scratch VMA, and mapped result memory. Core helpers are `live_mocs_init()`, `read_regs()`, `read_mocs_table()`, `read_l3cc_table()`, `check_mocs_engine()`, `active_engine_reset()`, and `__live_mocs_reset()`. Entrypoint `intel_mocs_live_selftests()` runs `live_mocs_kernel`, `live_mocs_clean`, and `live_mocs_reset`.

Control flow: initialization queries `get_mocs_settings()` to discover which tables exist, creates a GGTT scratch page, and maps it WB. Per-engine checks create a request, mark scratch active for write, emit `MI_STORE_REGISTER_MEM_GEN8` commands to read the MOCS and render-only L3CC tables into scratch, wait for completion, and compare each entry with `for_each_mocs()` / `for_each_l3cc()`. Reset tests modify scheduler policy for fast reset, create a large-ring context, test clean reset, active spinner reset, and GT reset, then re-read the tables.

State and persistence: it reads live MMIO state through command streamer stores, temporarily disables normal scheduling policy, uses engine PM references, holds the global reset lock for reset checks, runs spinners, and may reset engines or the GT. Scratch VMA mappings are released by `live_mocs_fini()`.

Dependencies/integration: it depends on MOCS table generation, MOCS register addressing, L3CC register layout, engine PM, reset helpers, spinner selftests, and GuC reset semantics. MCR-ranged L3CC registers are skipped for CS readback because CPU MCR routing does not apply to command-streamer access.

Risks and test signals: failures indicate missing MOCS settings, register readback mismatch, reset not preserving programmed tables, or spinner/reset problems. The test is hardware-sensitive around global vs per-engine MOCS, render-only L3CC, MCR ranges, and GuC-submitted engines where KMD cannot manually perform the same reset.

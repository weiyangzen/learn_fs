# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_reset.c Research

Purpose: this live suite verifies base GT reset behavior independent of hangcheck-specific request replay: global reset accounting, stolen-memory preservation, wedged recovery, and atomic-context reset paths.

Important APIs/types/functions: central helper `__igt_reset_stolen()` CRCs stolen memory before and after reset. Subtests include `igt_reset_device_stolen()`, `igt_reset_engines_stolen()`, `igt_global_reset()`, `igt_wedged_reset()`, `igt_atomic_reset()`, and `igt_atomic_engine_reset()`. Entrypoint `intel_reset_live_selftests()` gates on GPU reset support.

Control flow: stolen-memory tests use the GGTT error-capture node to map each stolen page, fill unused pages with `STACK_MAGIC`, record CRCs, perform either full GT reset or per-engine reset while spinners are active, then re-map pages and compare CRCs. Global reset records `i915_reset_count()` before/after `intel_gt_reset()`. Wedged reset sets the GT wedged and expects reset to clear it. Atomic tests iterate `igt_atomic_phases`, wrap reset prepare/finish around `intel_gt_reset_all_engines()` or call `__intel_engine_reset_bh()` with tasklets disabled and bottom halves controlled.

State and persistence: it takes the global reset lock, runtime PM/GT PM references, manipulates stolen-memory scratch mappings through GGTT, runs spinners, disables tasklets during engine atomic reset, sets/clears wedged state, and forces final resets after poking reset internals. It frees CRC buffers and temporary pages on exit.

Dependencies/integration: this file integrates with stolen memory management, GGTT insert/clear operations, io-mapped WC reads, reset prepare/finish, atomic section test helpers, spinner selftests, and GuC submission gates. It skips per-engine reset tests when unsupported or GuC submission owns reset.

Risks and test signals: stolen-memory CRC differences below the reserved bias are informational, while clobbering unreserved stolen pages above `I915_GEM_STOLEN_BIAS` fails. Other pass signals are reset count increments, wedged state recovery, and successful reset under each atomic phase. Risks include platform-specific stolen memory layout, missing error-capture nodes, and strict atomic-context assumptions.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine_cs.c

Purpose: implements engine command-stream performance and structural mock selftests for batch-buffer start, large NOP execution, and engine MMIO base table ordering.

Important APIs/functions: live performance entry `intel_engine_cs_perf_selftests()` runs `perf_mi_bb_start` and `perf_mi_noop`. Mock entry `intel_engine_cs_mock_selftests()` runs `intel_mmio_bases_check`. Helpers include `perf_begin()`, `perf_end()`, `timestamp_reg()`, `write_timestamp()`, `create_empty_batch()`, `create_nop_batch()`, `trifilter()`, and `cmp_u32()`.

Control flow: performance tests force GT PM on, boost RPS by incrementing `gt->rps.num_waiters`, and iterate engines with command-stream timestamps. `perf_mi_bb_start()` times an empty batch buffer jump by storing timestamps before and after `emit_bb_start()`. `perf_mi_noop()` subtracts empty-batch overhead from execution of a 64 KiB NOP batch. Both collect five samples and use a weighted median-style filter before logging cycles. The mock MMIO-base test walks `intel_engines[]`, validates that `graphics_ver` entries decrease monotonically, stops at version 0, and rejects zero base addresses for real entries.

State and persistence behavior: temporary internal GEM objects and VMAs are created, pinned, synchronized, and released. Performance setup temporarily increases RPS waiters and holds a GT wakeref, then restores both through `perf_end()`.

Dependencies and integration points: uses i915 command emission, GGTT/user VMA pinning, timestamp registers, engine `emit_bb_start`, RPS workqueue, GT PM, and the global static engine info table. It skips unsupported engines on pre-Gen7 except RCS0.

Risks: performance numbers are informational but still require request completion; slow hardware can trip waits. Timestamp register selection differs for Gen5/G4X. Object/VMA cleanup paths must release pins after partial failures. The MMIO-base check compares table shape rather than live hardware behavior.

Test signals: `pr_info()` logs MI_BB_START and 16K MI_NOOP cycles per engine. Failures return allocation/pinning errors, EIO on request timeout/flush failure, or `-EINVAL` for malformed MMIO base metadata.

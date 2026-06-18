# Group Research: group_1450_openzfs_sources_cow_pools_openzfs_module_zfs_vdev_raidz_math_sse2_c_c5579128de71

Scope: `Docs/research_subset_a.md` includes `sources/cow-pools/openzfs`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_sse2.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_sse2.c

## Scope

x86-64 SSE2 RAID-Z math backend. This file supplies 16-byte XMM primitives and operation-specific macro bindings for the shared `vdev_raidz_math_impl.h` template, then registers the `sse2` RAID-Z generation/reconstruction implementation.

## Main Interfaces

- `vdev_raidz_sse2_impl`: `raidz_impl_ops_t` backend named `sse2`.
- `raidz_will_sse2_work()`: enables the backend only when kernel SIMD use is allowed and SSE/SSE2 are available.
- `DEFINE_GEN_METHODS(sse2)` and `DEFINE_REC_METHODS(sse2)`: instantiate RAID-Z gen/rec entry points from the shared template.
- SIMD macro API consumed by the template: `XOR_ACC`, `XOR`, `ZERO`, `COPY`, `LOAD`, `STORE`, `MUL2_SETUP`, `MUL2`, `MUL4`, `MUL`.
- Generated constant multiply helpers: `mul_x1_0..255`, `mul_x2_0..255`, plus `gf_x1_mul_fns[256]` and `gf_x2_mul_fns[256]`.

## State And Control Flow

The file is compiled only for `defined(__x86_64) && HAVE_SIMD(SSE2)`. It defines a 16-byte aligned `v_t` and maps logical vector operands to XMM register names through variadic register-selection macros.

Memory and logic operations are inline assembly over 1, 2, or 4 XMM registers depending on the template operation. Loads/stores use aligned `movdqa`, XORs use `pxor`, copies use `movdqa`, and zeroing is implemented as XOR with self. Unsupported register counts generally trip `VERIFY(0)`.

GF(2^8) multiply-by-2 is implemented with SSE2 byte arithmetic: `MUL2_SETUP()` loads the `0x1d` reduction mask into `xmm15`; `_MUL2_x1/_MUL2_x2` detect high bits with signed byte compares, double bytes with `paddb`, and XOR the reduction polynomial where required. `MUL4()` applies `MUL2()` twice.

General multiply-by-constant is implemented without SSSE3 shuffle tables. `_MUL_PARAM()` decomposes the constant into powers of two, repeatedly applies `MUL2()`, and XORs selected powers into an accumulator. The file emits 256 one-lane and 256 two-lane static helper functions, then dispatches through aligned function-pointer tables in `MUL(c, ...)`.

The lower macro section binds template operation strides and register tuples. P/PQ/PQR generation and syndrome paths use four-register strides where possible. General multiplication uses two-register stride, and PQR reconstruction is reduced to one-register stride because SSE2 lacks the more efficient SSSE3 nibble-table multiply.

## Dependencies

Depends on `sys/isa_defs.h`, `sys/simd.h`, `sys/debug.h`, `sys/vdev_raidz_impl.h`, `vdev_raidz_math_impl.h`, `kfpu_begin()/kfpu_end()`, `kfpu_allowed()`, `zfs_sse_available()`, and `zfs_sse2_available()`.

## Correctness Notes

The backend assumes aligned 16-byte buffers because it uses `movdqa`. The register tuple macros and stride declarations are part of the ABI with `vdev_raidz_math_impl.h`; a mismatch would silently corrupt parity or recovery math. SIMD context gating is required because the routines directly use XMM state in kernel context. Constant multiplication correctness depends on `_MUL_PARAM()` preserving the input/accumulator register convention used by the generated helper functions.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_sse2.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_ssse3.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_ssse3.c

## Scope

x86-64 SSSE3 RAID-Z math backend plus the shared x86 carryless/nibble multiply lookup table. The executable backend uses SSSE3 `pshufb` to accelerate GF(2^8) multiplication for RAID-Z generation and reconstruction.

## Main Interfaces

- `vdev_raidz_ssse3_impl`: `raidz_impl_ops_t` backend named `ssse3`.
- `raidz_will_ssse3_work()`: enables the backend when SIMD is allowed and SSE, SSE2, and SSSE3 are available.
- `DEFINE_GEN_METHODS(ssse3)` and `DEFINE_REC_METHODS(ssse3)`: instantiate template methods.
- Template macro API: `XOR_ACC`, `XOR`, `ZERO`, `COPY`, `LOAD`, `STORE`, `MUL2_SETUP`, `MUL2`, `MUL4`, `MUL`.
- `gf_clmul_mod_lt[4*256][16]`: 256-byte-aligned lookup table compiled for x86 when SSSE3, AVX2, or AVX512BW SIMD code may need it.

## State And Control Flow

The SSSE3 backend section is compiled only under `defined(__x86_64) && HAVE_SIMD(SSSE3)`. Like SSE2, it defines a 16-byte aligned `v_t` and uses inline XMM assembly for load/store/copy/XOR operations. Unsupported register counts call `ZFS_ASM_BUG()`.

`MUL2()` still uses byte doubling and the `0x1d` reduction mask, but general multiplication differs from SSE2. `_MULx2(c, ...)` splits each byte into high and low nibbles, loads four 16-byte rows for coefficient `c` from `gf_clmul_mod_lt`, uses `pshufb` to select nibble products/reduction terms, and XORs the upper/lower partial results back into two XMM registers. `MUL(c, ...)` handles either two or four registers by applying `_MULx2()` to register pairs.

The operation binding section gives SSSE3 wider coverage than SSE2 for general multiply: `MUL_STRIDE` is 4, and PQR reconstruction uses two-register groups for `X`, `Y`, `Z`, `XS`, and `YS`. This reflects the more efficient table-shuffle multiply path.

After method instantiation, the file defines the backend registration with no init/fini hooks. The large `gf_clmul_mod_lt` table follows outside the SSSE3-only backend guard but inside an x86 guard that also includes AVX2 and AVX512BW consumers. The table is static constant data, grouped as four 16-byte rows per coefficient.

## Dependencies

Depends on `sys/isa_defs.h`, `sys/simd.h`, `sys/vdev_raidz_impl.h`, `vdev_raidz_math_impl.h`, kernel FPU/SIMD helpers, and x86 SSSE3 `pshufb` semantics. The table is also a cross-file dependency for wider x86 RAID-Z math implementations.

## Correctness Notes

The `gf_clmul_mod_lt` layout is tightly coupled to `_MULx2()` and to other x86 SIMD backends that reuse the table. Its 256-byte alignment matters for predictable indexed loads and cache behavior. The macro layer assumes 16-byte alignment and exact XMM scratch-register usage (`xmm10..xmm15`); accidental register overlap would break multiplication. Runtime support checks must prevent use outside safe SIMD contexts.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_ssse3.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_rebuild.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_rebuild.c

## Scope

Sequential resilver/device rebuild implementation for OpenZFS top-level vdevs. This file reconstructs allocated logical address ranges in LBA/metaslab order, primarily for mirror and dRAID-style rebuilds, and persists progress in each top-level vdev ZAP.

## Main Interfaces

- `vdev_rebuild(vdev_t *vd, uint64_t txg)`: start a sequential rebuild or request a reset of an active one.
- `vdev_rebuild_load(vdev_t *vd)`: load on-disk rebuild state from `VDEV_TOP_ZAP_VDEV_REBUILD_PHYS`.
- `vdev_rebuild_restart(spa_t *spa)`: restart active rebuild threads after import/load.
- `vdev_rebuild_stop_all()` / `vdev_rebuild_stop_wait()`: stop rebuild threads while leaving active state resumable.
- `vdev_rebuild_active(vdev_t *vd)`: report whether any top-level vdev is rebuilding.
- `vdev_rebuild_txgs()`: expose the min/max TXG range covered by the rebuild.
- `vdev_rebuild_get_stats()`: return per-top-level rebuild status and progress counters.
- `vdev_rebuild_clear_sync()`: clear completed/canceled rebuild status.
- Tunables: `zfs_rebuild_max_segment`, `zfs_rebuild_vdev_limit`, `zfs_rebuild_scrub_enabled`.

## State And Control Flow

The on-disk state is `vdev_rebuild_phys_t` stored in the top-level vdev ZAP. Active rebuilds also use in-memory state in `vdev_rebuild_t`, including scan offsets per TXG, pass counters, in-flight byte accounting, current metaslab/range tree, and a rebuild thread pointer on the top-level vdev.

Starting a rebuild sets `vd->vdev_rebuilding`, increments `SPA_FEATURE_DEVICE_REBUILD`, initializes `vrp_rebuild_state = VDEV_REBUILD_ACTIVE`, records TXG bounds from `vdev_resilver_needed()`, writes the ZAP entry, logs history/events, and creates `vdev_rebuild_thread()`.

The rebuild thread cancels any scrub, creates a range tree, clears rebuild byte counters, then walks metaslabs in order. For each metaslab it disables allocations, waits for outstanding allocating ranges to sync, loads allocated ranges from the space map, overlays unflushed alloc/free trees, removes already rebuilt offsets, and issues rebuild I/O for the remaining allocated ranges. After each metaslab it waits for the last rebuild TXG to sync before re-enabling the metaslab.

`vdev_rebuild_ranges()` splits each allocated range into legal chunks using the top-level vdev op’s `vdev_op_rebuild_asize()` method. `vdev_rebuild_range()` builds a synthetic checksum-disabled block pointer for the target range, skips it if DTLs do not require resilvering, rate-limits queued bytes, schedules an update sync task for progress, and issues a raw resilver read with `ZIO_PRIORITY_REBUILD`. The I/O callback frees the ABD, records errors, releases in-flight byte accounting, wakes waiters, and exits the config lock held for the I/O.

Completion schedules one of three sync tasks: complete, cancel, or reset. Successful completion marks state complete, sets end time, reassesses DTLs, decrements the device rebuild feature, emits finish events, requests spare-detach handling, optionally starts a scrub, wakes waiters, and clears recent error-event deduplication. Cancel marks state canceled and decrements the feature. Reset clears progress and starts a fresh rebuild thread without fully canceling the feature.

## Dependencies

Depends on vdev internals, dRAID/mirror/replacing/spare rebuild hooks, metaslab space maps, range trees, DTL logic, ZIO, ABD allocation, DMU sync tasks, SPA feature accounting, ARC sizing, ZAP persistence, pool scan setup/cancel paths, and event/history reporting.

## Correctness Notes

Sequential rebuild deliberately does not verify block checksums during reconstruction; the optional post-rebuild scrub is the checksum verification phase and is strongly recommended. RAIDZ is excluded because variable stripe width prevents this simple LBA-order reconstruction model, while dRAID supplies fixed-width rebuild sizing.

Metaslabs are disabled while their allocated ranges are captured and rebuilt so new allocations cannot race the scan of that address range. Waiting for the rebuild TXG before re-enabling the metaslab prevents later allocations from interfering with reconstructed ranges. Progress is written by sync task and rolled back on certain top-level unavailability errors so import/resume can restart from a safe offset.

The stop/cancel/reset flags are intentionally separate: export/suspend leaves the on-disk state active, detach can cancel if no missing DTLs remain, and attaching another replacement device resets the active pass so the new participant receives all needed data. The in-flight byte limiter is important for latency and memory pressure; it derives from ARC size, top-level count, `zfs_rebuild_vdev_limit`, and child count.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_rebuild.c -->
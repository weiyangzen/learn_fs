# Group Research: group_531_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_5b13b26c2c6c

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/os/illumos/illumos-gate`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_impl.h

This header is the shared RAID-Z math implementation template. It is included by scalar and SIMD-specific `.c` files after they define the vector type, load/store/XOR/multiply macros, stride constants, and `raidz_math_begin/end` hooks. The same algorithmic code is therefore compiled into multiple implementations.

It computes reconstruction coefficients for Q, R, PQ, PR, QR, and PQR recovery with Galois-field helpers such as `gf_exp2`, `gf_exp4`, `gf_mul`, `gf_div`, and `gf_inv`. It also provides common ABD iteration callbacks for zeroing, copying, XOR addition, and multiplication by a constant.

Parity generation covers RAIDZ1 P, RAIDZ2 PQ, and RAIDZ3 PQR. P parity is simple XOR accumulation, while Q and R syndromes repeatedly multiply prior syndrome state by 2 or 4 in the RAID-Z GF(2^8) field before adding data. The generator functions operate over ABD-backed columns and handle shorter data columns by continuing syndrome updates through the parity column length.

Reconstruction covers one-, two-, and three-data-column loss using P/Q/R combinations. The code first builds syndromes by treating missing data as zero, adds stored parity columns, then transforms syndromes with precomputed coefficients to recover targets. For uneven RAID-Z geometry, shorter target columns may be temporarily replaced with full-size ABD buffers so vector loops can avoid per-iteration size branches, then copied back.

Key entry points emitted through this template are the `raidz_generate_*_impl()` and `raidz_reconstruct_*_impl()` routines consumed by `DEFINE_GEN_METHODS()` and `DEFINE_REC_METHODS()` in the concrete implementation files. The main dependencies are `raidz_map_t`, ABD iteration helpers, RAID-Z column constants, and the implementation-provided vector macros.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_scalar.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_scalar.c

This file provides the portable scalar RAID-Z math backend. It selects a native 32-bit or 64-bit integer lane size, wraps it in `v_t`, and defines the template macros from `vdev_raidz_math_impl.h` in terms of ordinary loads, stores, XORs, and byte-wise table multiplication.

`raidz_init_scalar()` fills `vdev_raidz_mul_lt[256][256]`, a direct GF multiplication lookup table. Reconstruction multiplication uses this table by coefficient, avoiding repeated log/exp operations during recovery. `MUL2` is optimized with word-wide bit masks for carry reduction by the RAID-Z polynomial, and `MUL4` applies `MUL2` twice.

The scalar backend defines one-lane strides for all zero/copy/add/syndrome/reconstruction operations, includes the shared template, and emits scalar generation and reconstruction method arrays with `DEFINE_GEN_METHODS(scalar)` and `DEFINE_REC_METHODS(scalar)`.

`raidz_will_scalar_work()` always returns true, making this the fallback implementation. The exported `vdev_raidz_scalar_impl` supplies `.init = raidz_init_scalar`, the generated method tables, the support predicate, and name `"scalar"`. The file also defines the public aligned `vdev_raidz_pow2` and `vdev_raidz_log2` GF tables used by broader RAID-Z math code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_scalar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_sse2.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_sse2.c

This file implements an amd64 SSE2 RAID-Z math backend. It defines a 16-byte aligned `v_t`, XMM register selection macros, and inline assembly helpers for XOR accumulation, register XOR, zeroing, copying, aligned loads, and aligned stores.

GF multiplication by 2 uses SSE2 byte comparison and mask reduction with `0x1d`. General multiplication by an arbitrary coefficient is implemented by generated per-coefficient functions: `mul_x1_*` for one XMM vector and `mul_x2_*` for two vectors. Each function expands `_MUL_PARAM`, repeatedly applying `MUL2` and XORing selected powers of two. Function pointer tables `gf_x1_mul_fns` and `gf_x2_mul_fns` dispatch by coefficient.

The backend wraps vector work in `kfpu_begin()` / `kfpu_end()`, sets wider strides than scalar for bulk operations, includes `vdev_raidz_math_impl.h`, and emits `sse2` generation and reconstruction method tables. The support predicate requires kernel FPU availability plus SSE and SSE2 CPU support.

The exported `vdev_raidz_sse2_impl` registers the implementation with name `"sse2"`. On `__i386`, the file provides only a fakekernel-oriented stub with null method tables.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_sse2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_ssse3.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_ssse3.c

This file implements an amd64 SSSE3 RAID-Z math backend. Like the SSE2 backend, it defines a 16-byte vector type and XMM inline assembly macros for load/store/copy/XOR operations, but uses SSSE3 `pshufb` table lookups for faster GF multiplication.

`MUL2` still uses SSE-style mask reduction, while arbitrary coefficient multiplication is handled by `_MULx2()`. That macro splits each byte into high and low nibbles, uses precomputed tables from `gf_clmul_mod_lt[4*256][16]`, applies `pshufb` to produce partial products and reduction terms, and XORs them into the output vectors. This supports two- and four-register multiply cases used by the shared RAID-Z reconstruction template.

The file defines stride and register assignments for all operations expected by `vdev_raidz_math_impl.h`, includes the template, and emits generated method tables for `ssse3`. The exported `vdev_raidz_ssse3_impl` is enabled only when kernel FPU, SSE, SSE2, and SSSE3 are available.

Most of the file is the aligned `gf_clmul_mod_lt` constant table, containing four 16-byte lookup vectors per coefficient. On `__i386`, the file provides only a stub implementation with null method tables and name `"sse3"`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_ssse3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_removal.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_removal.c

This file implements ZFS vdev removal. It handles auxiliary device removal for spares and L2ARC, log vdev removal by evacuation and replacement with a hole, and top-level data vdev removal by copying all allocated data elsewhere and converting the removed top-level vdev into an indirect vdev.

For top-level removal, `vdev_remove_initiate_sync()` allocates indirect mapping and birth objects, initializes `spa_removing_phys`, computes `sr_to_copy` from metaslab allocated space, activates the device-removal feature, persists removal state, dirties required MOS/config metadata, and starts `spa_vdev_remove_thread()`. `spa_remove_init()` reloads in-progress and prior indirect mappings during pool open, in newest-to-oldest order so mappings stored on newer indirect vdevs can be read safely.

The removal thread loads allocated segments from each metaslab space map into `svr_allocd_segs`, adjusts for unflushed allocs/frees and current freeing state, then repeatedly allocates replacement space and schedules copy I/O. `spa_vdev_copy_segment()` creates indirect mapping entries, accounts obsolete holes inside copied spans, allocates destination DVAs, and builds child zio trees. Mirror-to-mirror copies try to preserve corresponding child copies, reading and writing physical children under the config lock.

Sync-side progress is handled by `vdev_mapping_sync()` and `svr_sync()`. Mapping entries collected in per-txg lists are written to the indirect mapping object, birth entries are added, in-flight frees are applied, and `spa_removing_phys.sr_copied` is advanced only as txgs sync. Outstanding copy memory is throttled by `zfs_remove_max_copy_bytes`; segment size is limited by `zfs_remove_max_segment` and may shrink on ENOSPC.

Concurrent frees are handled by `free_from_removing_vdev()`. It frees from the removing vdev immediately, then distinguishes synced, in-flight, and unvisited offsets. Synced mappings are remapped and freed from the new location; in-flight mappings are recorded in per-txg `svr_frees`; unvisited ranges are removed from the copy set and counted as completed.

Completion converts the removed concrete vdev into an indirect vdev via `vdev_remove_replace_with_indirect()`, destroys obsolete spacemaps and leaf ZAPs in sync context, updates the linked list of indirect vdevs, writes remove labels, posts sysevents, and records history. Cancellation suspends the thread, frees mapped replacement space, destroys partial mapping/birth objects, decrements feature refs, restores allocation, and marks the removal canceled.

`spa_vdev_remove()` is the public dispatcher. It rejects removal while a checkpoint exists or is being discarded, removes unused spares and cache devices from auxiliary config nvlists, calls the log-vdev path for log devices, or calls the top-level removal path for ordinary vdevs. `spa_vdev_remove_top_check()` enforces major constraints: enabled feature, enough space, no removal already active, no missing/outage DTL, readable device, uniform ashift, no RAID-Z top-level vdevs, and only leaf children under mirrors. `spa_removal_get_stats()` reports removal state, progress, and indirect mapping memory.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_removal.c -->
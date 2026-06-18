# Group Research: group_1447_openzfs_sources_cow_pools_openzfs_module_zfs_vdev_raidz_c_sources_c_cbc7b029f9fb

Scope: `Docs/research_subset_a.md`, specifically the OpenZFS source tree under `sources/cow-pools/openzfs`. I read both listed source files completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz.c

## Role

This 5,558-line file is the main OpenZFS RAID-Z top-level vdev implementation. It defines RAID-Z layout mapping, parity generation fallback code, reconstruction fallback code, read/write child I/O orchestration, checksum/parity verification, self-healing, latency-outlier sit-out handling, RAID-Z expansion/reflow, vdev config serialization, and the exported `vdev_raidz_ops` vector.

The file is in subset A because it is core COW pool/block storage code: it turns a logical ZIO range into child vdev sectors and preserves redundancy for RAIDZ1/2/3, including expanded RAID-Z geometry.

## Major Dependencies

The file depends on core OpenZFS kernel abstractions: `spa_t`, `vdev_t`, `zio_t`, `blkptr_t`, `abd_t`, metaslabs, rangelocks, ZAP, uberblocks, DTLs, DSL scan, and dRAID helpers. Important headers include `sys/spa_impl.h`, `sys/vdev_impl.h`, `sys/metaslab_impl.h`, `sys/zio.h`, `sys/abd.h`, `sys/vdev_raidz.h`, `sys/vdev_raidz_impl.h`, `sys/vdev_draid.h`, `sys/uberblock_impl.h`, and `sys/dsl_scan.h`.

The parity dispatch path is coupled to `vdev_raidz_math.c` through `vdev_raidz_math_get_ops()`, `vdev_raidz_math_generate()`, and `vdev_raidz_math_reconstruct()`. dRAID support is integrated through `vdev_draid_map_verify_empty()`, `vdev_draid_map_alloc_empty()`, `vdev_draid_ops`, and `vdev_draid_config_t`.

## Key State And Tunables

The file defines internal RAID-Z parity column indexes `VDEV_RAIDZ_P`, `VDEV_RAIDZ_Q`, and `VDEV_RAIDZ_R`, plus GF(2^8) multiplication helpers for byte and packed 64-bit parity math. The top comment documents P/Q/R parity construction and the RAID-Z expansion design.

Expansion and behavior tunables include `raidz_expand_max_reflow_bytes`, `raidz_expand_pause_point`, `vdev_read_sit_out_secs`, `vdev_raidz_outlier_check_interval_ms`, `vdev_raidz_outlier_insensitivity`, `raidz_expand_max_copy_bytes`, `raidz_io_aggregate_rows`, `zfs_scrub_after_expand`, and `zfs_scrub_partial_writes`. They are exported as `ZFS_MODULE_PARAM()` entries at the end of the file.

Runtime state is mostly stored in `raidz_map_t`, `raidz_row_t`, `raidz_col_t`, and `vdev_raidz_t`. Expansion state uses `vdev_raidz_expand_t` inside `vdrz->vn_vre`, including `vre_offset`, per-txg offset/byte counters, `vre_failed_offset`, `vre_waiting_for_resilver`, `vre_rangelock`, and condition-variable protected outstanding-byte accounting.

## Layout Mapping

`vdev_raidz_map_alloc()` builds the classic single-row RAID-Z map for a logical ZIO. It computes the parent-sector start, quotient/remainder data sectors, big columns, total sectors, accessed/skipped columns, child `rc_devidx`, child `rc_offset`, and `rc_size`. It preserves the historic single-parity 1 MiB parity-swap behavior and allocates ABDs for parity/data columns.

`vdev_raidz_map_alloc_write()` prepares write ABDs, including parity padding and gang ABDs for optional skip sectors. `vdev_raidz_map_alloc_read()` allocates parity buffers and maps data columns into the caller ABD.

`vdev_raidz_map_alloc_expanded()` handles expanded RAID-Z blocks where logical width can differ from physical child count. It splits a block into rows, determines whether each row uses old location, new location, or scratch space, assigns shadow write locations when a copied-but-not-synced sector must be written twice, and can aggregate multi-row physical reads into `rm_phys_col` buffers when rows are contiguous.

## Parity Generation

The fallback parity generators are `vdev_raidz_generate_parity_p()`, `vdev_raidz_generate_parity_pq()`, and `vdev_raidz_generate_parity_pqr()`. They use ABD iteration callbacks and packed 64-bit GF helpers for P, Q, and R. Short columns are treated as zero-filled for Q/R progression.

`vdev_raidz_generate_parity_row()` first attempts the selected math implementation via `vdev_raidz_math_generate()`. If that returns `RAIDZ_ORIGINAL_IMPL`, it falls back to the local original routines. `vdev_raidz_generate_parity()` applies the row generator across all rows in a map.

## Reconstruction

Fast fallback reconstruction covers single-data-column P and Q recovery and two-data-column P+Q recovery through `vdev_raidz_reconstruct_p()`, `vdev_raidz_reconstruct_q()`, and `vdev_raidz_reconstruct_pq()`. Unsupported combinations fall back to matrix reconstruction.

The general path is split across `vdev_raidz_matrix_init()`, `vdev_raidz_matrix_invert()`, `vdev_raidz_matrix_reconstruct()`, and `vdev_raidz_reconstruct_general()`. It builds the needed Vandermonde/identity rows, performs GF(2^8) Gauss-Jordan elimination, and reconstructs only the missing data rows. Because matrix reconstruction requires linear ABDs, it temporarily linearizes non-linear data ABDs and copies results back.

`vdev_raidz_reconstruct_row()` chooses SIMD/scalar accelerated reconstruction first via `vdev_raidz_math_reconstruct()`, then tries local optimized cases, and finally uses the general matrix path. `vdev_raidz_reconstruct()` applies this to all rows.

## I/O Start Path

`vdev_raidz_io_start()` selects the correct logical width based on block birth TXG and expansion state. If the block uses expanded geometry, it may enter `vre_rangelock`, read the synced/next reflow offsets from `spa_ubsync` and in-memory expansion state, and build an expanded map. Otherwise it builds the classic map.

For writes, `vdev_raidz_io_start_write()` generates row parity and issues child writes for all nonzero columns, including shadow writes during expansion. `raidz_start_skip_writes()` issues optional NODATA writes for skip sectors in non-expanded maps to improve aggregation continuity.

For reads, `vdev_raidz_io_start_read_row()` marks unreadable, stale, and slow-sit-out columns, optionally skips a latency outlier when parity permits reconstruction, and issues child reads for data or parity as needed. `vdev_raidz_io_start_read_phys_cols()` issues aggregate reads for expanded multi-row maps. `vdev_raidz_io_start_read()` chooses row or aggregate read mode.

## I/O Completion, Verification, And Repair

`vdev_raidz_child_done()` and `vdev_raidz_shadow_child_done()` record child I/O errors. `raidz_checksum_verify()` verifies the logical checksum and has a special Direct I/O read path that prevents self-healing from mutable user buffers.

`raidz_parity_verify()` regenerates parity and compares it with read parity columns, reporting checksum errors through `vdev_raidz_checksum_error()`. `vdev_raidz_io_done_reconstruct_known_missing()` reconstructs data when known read failures are within parity limits. `vdev_raidz_read_all()` expands a failed normal read into all remaining columns so combinatorial reconstruction has maximum evidence.

`vdev_raidz_io_done_verified()` performs parity verification, repair writes, resilver/scrub writes, and shadow-location correction during expansion. It carefully avoids Direct I/O self-healing and treats rebuild cases without checksums conservatively.

`vdev_raidz_io_done()` is the main completion routine. Writes call `vdev_raidz_io_done_write_impl()`, which accepts partial writes only if both normal and shadow locations remain reconstructable. Reads handle aggregate-copyback, known-missing reconstruction, checksum verification, parity/self-heal, slow-outlier checks, retry reads, combinatorial reconstruction, and unrecoverable checksum ereports. It exits any expansion rangelock before returning.

## Combinatorial Reconstruction

`raidz_simulate_failure()` maps a logical child failure across current and previous expanded widths. This lets the recovery path test failures that could have existed before an expansion and then been reflowed diagonally across newer children.

`raidz_reconstruct()` simulates selected logical child failures row by row, reconstructs when possible, verifies the logical checksum, reports confirmed bad data, and restores original data on failure. `vdev_raidz_combrec()` enumerates combinations of up to parity-count logical failures, including all historical widths from physical width down to original width. This is the fallback for silent corruption or checksum failures after all readable columns have been fetched.

## Slow-Disk Sit-Out Handling

`vdev_sit_out_reads()` checks whether a leaf should temporarily sit out reads, with scrub protection. `vdev_child_slow_outlier()` periodically compares per-child read latency histograms with a Tukey-fence style threshold, increments outlier counters, and calls `vdev_raidz_sit_child()` when a child remains a persistent outlier. `vdev_raidz_unsit_child()` clears sit-out state. This logic is shared conceptually by RAID-Z and dRAID read paths.

## RAID-Z Expansion And Reflow

The large expansion design comment explains the on-disk format and reflow model. The implementation supports attaching a new child to an existing RAID-Z vdev, copying allocated data from old layout to new layout, using boot-area scratch space for the initial overlapping region, and preserving time-dependent geometry through `raidz_expand_txgs`.

`vdev_raidz_get_logical_width()` looks up the logical width for a block birth TXG using `vd_expand_txgs`; `vdev_raidz_psize_to_asize()` and `vdev_raidz_asize_to_psize()` use that width so older blocks keep their original parity/data ratio.

`raidz_reflow_sync()` commits reflow progress to the uberblock and top-level ZAP bytes-copied counter. `raidz_reflow_complete_sync()` records completion, adds a new expand-TXG node, dirties config, clears `ub_raidz_reflow_info`, requests initialize/trim/autotrim restarts, notifies waiters, and optionally starts a scrub.

`raidz_reflow_impl()` copies allocated ranges in bounded batches. It prevents unsafe row overlap, removes copied ranges from the work tree, records progress, holds the expansion rangelock, issues old-layout reads and new-layout writes, tracks outstanding bytes, pauses on errors, and refuses to proceed while a child is being replaced.

`raidz_reflow_scratch_sync()` handles the initial overlap region using the per-child boot area as scratch. It can resume after a paused/crashed state, reads either original or scratch data, reflows sectors in memory, persists scratch, updates `spa_ubsync` to `RRSS_SCRATCH_VALID`, overwrites the real location, flushes, then updates the uberblock to a scratch-invalid synced state. `vdev_raidz_reflow_copy_scratch()` completes scratch recovery during import after a crash with valid scratch data.

`spa_raidz_expand_thread()` is the background worker. It runs scratch reflow first, disables metaslabs one at a time, builds a range tree of allocated space, forces each metaslab's last sector into the copy set so progress advances, resumes from prior offsets, throttles outstanding copy bytes, issues reflow batches through txg-assigned work, waits for syncs when needed, and either completes the expansion or pauses waiting for resilver.

`spa_start_raidz_expansion_thread()`, `raidz_dtl_reassessed()`, `vdev_raidz_attach_check()`, and `vdev_raidz_attach_sync()` provide thread startup, paused-resume wakeups, attach validation, and attach-time on-disk state setup.

## Vdev Lifecycle And Config

`vdev_raidz_open()` validates parity count and child count, opens children, calculates usable size and ashifts, handles expanding vdev size based on old physical width, and fails if open errors exceed parity. `vdev_raidz_close()` closes children. `vdev_raidz_state_change()` sets healthy/degraded/cant-open based on degraded and faulted counts.

`vdev_raidz_need_resilver()` checks whether a block intersects dirty DTLs and always requires resilver during active expansion. `vdev_raidz_xlate()` maps logical parent ranges to child physical ranges, but returns an empty mapping during active expansion because the translation is unstable and consumers are best-effort initialize/trim operations.

`vdev_raidz_init()` parses children and parity from config, initializes expansion locks and the `vd_expand_txgs` AVL tree, recognizes `ZPOOL_CONFIG_RAIDZ_EXPANDING`, reconstructs previous expansion TXG history, and records original/physical widths. `vdev_raidz_load()` reads expansion state/timestamps/bytes-copied from top ZAP. `spa_raidz_expand_get_stats()` reports current or most recent expansion stats. `vdev_raidz_fini()` tears down expansion state and frees AVL nodes. `vdev_raidz_config_generate()` writes parity, active expanding flag, and expand TXG arrays into config nvlists.

The exported `vdev_raidz_ops` binds this implementation to OpenZFS through init/fini/open/close, size conversion, I/O start/done, state changes, resilver checks, translation, config generation, parity count, disk count, and `VDEV_TYPE_RAIDZ`.

## Important Invariants And Risks

Parity count must be 1-3 and child count must exceed parity. `raidz_row_t` column sizes and ABD ownership are tightly managed; skip sectors and zero-length phantom columns must not enter parity math incorrectly. Expanded maps require careful distinction between logical width, physical width, original width, synced offset, next offset, scratch state, and shadow writes.

The expansion path is crash-sensitive. Correctness depends on rangelock coverage, uberblock `ub_raidz_reflow_info`, flushes after scratch/real writes, per-txg progress ordering, and not marking `vre_state` finished until synced progress covers all possible writes.

Silent corruption recovery in expanded pools is intentionally broader than classic RAID-Z but can still be less durable for a silent failure during expansion when one block spans old and new formats. The file documents this limitation in the combinatorial reconstruction path.

Direct I/O reads intentionally disable normal self-healing because user buffers may be modified while I/O is in flight. Latency sit-out is also deliberately conservative: it avoids scrubs, honors parity limits, decays counters, and requires repeated outlier evidence before skipping a child.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math.c

## Role

This 663-line file is the RAID-Z math implementation selector and benchmark harness. It chooses which parity-generation and reconstruction function table should be used by `vdev_raidz.c`, supports scalar and architecture-specific SIMD implementations, exposes kernel kstats for benchmark results, and provides the tunable setter/getter for implementation selection.

## Major Dependencies

The file depends on `sys/simd.h`, `sys/zfs_context.h`, `sys/zio.h`, `sys/debug.h`, `sys/zfs_debug.h`, `sys/vdev_raidz.h`, and `sys/vdev_raidz_impl.h`. It calls back into core RAID-Z routines such as `vdev_raidz_generate_parity()`, `vdev_raidz_reconstruct()`, `vdev_raidz_map_alloc()`, and `vdev_raidz_map_free()` during benchmarking.

The implementation table references compiled-in ops from other files: original placeholder ops, scalar ops, x86 SSE2/SSSE3/AVX2/AVX512F/AVX512BW when available, AArch64 NEON/NEONx2 outside FreeBSD, and PowerPC AltiVec when available.

## Implementation Selection State

`vdev_raidz_original_impl` is an opaque entry whose methods are NULL and whose support check is `raidz_will_scalar_work`; selecting it forces callers to fall back to the original local code in `vdev_raidz.c`.

`vdev_raidz_fastest_impl` is populated at initialization with the fastest measured method for each generate/reconstruct operation. `raidz_all_maths[]` lists every compiled candidate. `raidz_supp_impl[]` and `raidz_supp_impl_cnt` hold the subset that passes initialization and `is_supported()`.

`zfs_vdev_raidz_impl` is the active selector and defaults to scalar before initialization. `user_sel_impl` holds the requested selector before init completes. Special selector values are `IMPL_FASTEST`, `IMPL_CYCLE`, `IMPL_ORIGINAL`, and `IMPL_SCALAR`; numeric values below those index supported implementations.

## Runtime Dispatch

`vdev_raidz_math_get_ops()` returns the ops table used by RAID-Z maps. If FPU/SIMD use is not allowed in the current context, it returns scalar. Otherwise it returns fastest, cycles through supported implementations, returns original/scalar, or indexes `raidz_supp_impl[]`.

`vdev_raidz_math_generate()` selects `gen_p`, `gen_pq`, or `gen_pqr` based on `raidz_parity(rm)`. If the selected function pointer is NULL, it returns `RAIDZ_ORIGINAL_IMPL` so `vdev_raidz.c` can use its original implementation.

`vdev_raidz_math_reconstruct()` chooses a reconstruction method based on RAID-Z parity level, which parity columns are valid, and how many data columns are bad. Helper selectors cover P, PQ, and PQR cases. If no accelerated function matches, it returns `RAIDZ_ORIGINAL_IMPL`.

The exported name arrays `raidz_gen_name[]` and `raidz_rec_name[]` provide stable labels for generation and reconstruction operations.

## Benchmarking And Kstats

Kernel builds maintain `raidz_impl_kstats[]` and install a raw kstat named `zfs/vdev_raidz_bench`. `raidz_math_kstat_headers()`, `raidz_math_kstat_data()`, and `raidz_math_kstat_addr()` produce a table of implementation throughput and fastest-method winners.

The benchmark uses an 8-data-column RAID-Z shape, up to triple parity, 128 KiB benchmark ZIOs, and approximately 1 ms benchmark windows per function. `benchmark_gen_impl()` runs parity generation; `benchmark_rec_impl()` runs reconstruction against fixed target sets that exercise all reconstruction variants.

`benchmark_raidz_impl()` loops over supported implementations, sets `bench_rm->rm_ops`, repeatedly invokes the benchmark function, computes per-disk throughput, stores stats, and updates `vdev_raidz_fastest_impl` per operation. This means "fastest" can be a hybrid ops table where different functions come from different implementations.

`benchmark_raidz()` initializes all implementations, filters supported ones, and in kernel builds benchmarks every generation and reconstruction function using fake ZIO/ABD maps. In user space it skips benchmarking to avoid slowing tools like `zdb`, `zhack`, `zinject`, and `ztest`, instead copying the last supported implementation into `fastest`.

## Initialization, Finalization, And Tunable API

`vdev_raidz_math_init()` runs benchmarking, creates the kstat in kernel builds, applies the user-selected implementation to `zfs_vdev_raidz_impl`, and marks math initialized.

`vdev_raidz_math_fini()` deletes the kstat and calls each implementation's `fini()` callback if present.

`vdev_raidz_impl_set()` parses a requested implementation name, accepts mandatory options `cycle`, `fastest`, `original`, and `scalar`, and after initialization also accepts names from supported implementations. It updates either the active selector or the deferred user selector. `vdev_raidz_impl_get()` lists mandatory options plus supported implementations, bracketing the active one in kernel builds.

## Important Invariants And Risks

Dispatch correctness depends on each implementation's function-table shape matching `RAIDZ_GEN_NUM` and `RAIDZ_REC_NUM`. NULL methods are valid only because callers explicitly fall back to original code.

`vdev_raidz_math_get_ops()` must avoid SIMD when `kfpu_allowed()` is false; violating that would make otherwise correct parity code unsafe in restricted kernel contexts.

The benchmark mutates `rm_ops` on fake maps and relies on fully initialized ABD buffers and parity ABDs. A broken implementation can affect benchmark selection even if scalar/original fallback exists, so `is_supported()`, init/fini hooks, and method presence must stay consistent with architecture feature detection.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math.c -->
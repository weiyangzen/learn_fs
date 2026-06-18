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

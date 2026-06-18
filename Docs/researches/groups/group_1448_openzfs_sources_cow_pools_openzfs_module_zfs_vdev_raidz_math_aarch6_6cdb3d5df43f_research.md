# Group Research: group_1448_openzfs_sources_cow_pools_openzfs_module_zfs_vdev_raidz_math_aarch6_6cdb3d5df43f

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_aarch64_neon.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_aarch64_neon.c

## Scope

This file registers the baseline AArch64 NEON RAID-Z math implementation and provides the shared precomputed GF(2^8) multiplication lookup table used by SIMD parity/reconstruction paths. It is part of subset A through `sources/cow-pools/openzfs`.

The source was read completely, lines 1-2280.

## Primary Interfaces

- `DEFINE_GEN_METHODS(aarch64_neon)` instantiates RAID-Z parity generation methods from `vdev_raidz_math_impl.h`.
- `DEFINE_REC_METHODS(aarch64_neon)` instantiates reconstruction methods from the same template.
- `raidz_will_aarch64_neon_work()` gates use on `kfpu_allowed()`.
- `vdev_raidz_aarch64_neon_impl` publishes the implementation as `"aarch64_neon"`.
- `gf_clmul_mod_lt[4*256][16]` is an aligned global lookup table consumed by the AArch64 common header and x86 AVX2/AVX512BW code.

## Architecture Configuration

The implementation is compiled only under `defined(__aarch64__)`. It includes `vdev_raidz_math_aarch64_neon_common.h`, then sets stride/register macros before including `vdev_raidz_math_impl.h`.

All regular zero/copy/add/multiply/generate/syndrome loops use 4 vector registers per step. Two-target and three-target recovery cases mostly use 2-register recovery strides, matching the common NEON helper's supported register counts and limiting temporary register pressure.

The macro groups define which NEON vector variables are live for each generated routine:
- `ZERO_*`, `COPY_*`, `ADD_*`, and `MUL_*` configure generic ABD buffer helpers.
- `GEN_P*` configure P, PQ, and PQR parity generation.
- `SYN_*` configure syndrome generation for Q, R, PQ, PR, QR, and PQR recovery.
- `REC_*` configure final recovery transforms for two- and three-column reconstruction.

## Lookup Table

After the implementation registration block, the file defines `gf_clmul_mod_lt` as a 256-byte-aligned table with `4 * 256` rows of 16 bytes. Each coefficient has four 16-byte subtables. The NEON common header's `MUL(c, ...)` macro indexes these rows to multiply vector bytes by arbitrary GF constants using nibble extraction and table lookup.

The same symbol is declared `extern` by `vdev_raidz_math_aarch64_neon_common.h`, `vdev_raidz_math_avx2.c`, and `vdev_raidz_math_avx512bw.c`, so this file is also the table provider for those lookup/shuffle implementations when linked into the OpenZFS RAID-Z math module set.

## Dependencies

- `sys/isa_defs.h` and `sys/types.h` provide platform and fixed-width type definitions.
- `vdev_raidz_math_aarch64_neon_common.h` supplies NEON vector primitives.
- `sys/vdev_raidz_impl.h` supplies RAID-Z row, column, target, and method-table contracts.
- `vdev_raidz_math_impl.h` supplies the shared algorithm template expanded under this architecture's macros.

## Filesystem Relevance

This is a CPU-specialized backend for the parity math used by ZFS RAID-Z vdevs. It accelerates P/Q/R parity generation and failed-column reconstruction on AArch64 systems with usable kernel FPU/SIMD context, while preserving the same high-level RAID-Z equations as the scalar/common implementations.

## Correctness Notes

- The implementation is not selected unless `kfpu_allowed()` is true.
- The table layout and alignment are part of the ABI expected by multiple architecture files; changing it would affect AArch64 NEON, AVX2, and AVX512BW multiplication.
- The generated routines rely on `vdev_raidz_math_impl.h` processing sizes in vector-aligned RAID-Z iteration units; this file only chooses strides and registers.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_aarch64_neon.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_aarch64_neon_common.h -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_aarch64_neon_common.h

## Scope

This header defines the AArch64 NEON vector primitive layer used by both AArch64 RAID-Z math implementations. It maps generic operations expected by `vdev_raidz_math_impl.h` onto inline assembly over 16-byte NEON vectors.

The source was read completely, lines 1-685.

## Primary Interfaces

- `v_t` is the vector element type, a 16-byte aligned byte array.
- `ELEM_SIZE` is `16`.
- `XOR_ACC`, `XOR`, `ZERO`, `COPY`, `LOAD`, and `STORE` implement vector data movement and XOR.
- `MUL2_SETUP`, `MUL2`, `MUL4`, and `MUL` implement GF(2^8) multiplication.
- `raidz_math_begin()` and `raidz_math_end()` wrap the generated math in `kfpu_begin()`/`kfpu_end()`.
- `GEN_X_DEFINE_*` declare vector variables either pinned to NEON registers in kernel builds or as compiler vector variables outside `_KERNEL`.

## Register And Assembly Model

The header uses variadic register-list macros to select the correct operand names and constraints for 2-, 4-, and 8-vector operations. `VR*`, `RVR*`, `WVR*`, and `UVR*` build inline-assembly references and input/output constraints around variables named `w0`, `w1`, and so on.

The code deliberately supplies dummy high-numbered operands for unused positions because GCC still validates constraints in macro-expanded assembly alternatives. In kernel builds, some temporary declarations alias `v31` for otherwise-unused register names, which avoids illegal duplicate constraints in active paths.

## Vector Operations

- `XOR_ACC(src, r...)` loads vectors from `src` and XORs them into existing registers.
- `XOR(r...)` XORs the first half of a register list into the second half.
- `ZERO(r...)` clears each listed vector by XORing it with itself.
- `COPY(r...)` copies the first half of a register list to the second half.
- `LOAD(src, r...)` loads contiguous 16-byte vectors from memory.
- `STORE(dst, r...)` writes contiguous 16-byte vectors to memory.

Unsupported register counts call `ZFS_ASM_BUG()`, which maps to `ASSERT(0)`.

## GF Multiplication

`MUL2_SETUP()` initializes a zero vector and a vector filled with the RAID-Z reduction polynomial byte `0x1d`. `MUL2()` performs byte-wise multiply by 2 using compare, shift, mask, and XOR reduction. `MUL4()` applies `MUL2()` twice.

Arbitrary constant multiplication uses the external `gf_clmul_mod_lt[4*256][16]` lookup table. `_MULx2(c, ...)` splits two vectors into upper and lower nibbles, uses NEON `tbl` lookups against the four subtables for coefficient `c`, and XORs the partial products. `MUL(c, ...)` applies `_MULx2()` to either one or two vector pairs.

## Dependencies

- `sys/types.h` provides fixed-width types.
- `sys/simd.h` provides kernel SIMD/FPU state helpers.
- `gf_clmul_mod_lt` is defined by `vdev_raidz_math_aarch64_neon.c`.

## Filesystem Relevance

The header is the hardware abstraction layer that lets the shared RAID-Z math template express parity and reconstruction in terms of vector primitives. It is performance critical because every RAID-Z P/Q/R operation on the AArch64 NEON backends expands through these macros.

## Correctness Notes

- The generated template assumes vector sizes and strides match `sizeof (v_t)`.
- The table multiplication path depends on the exact four-subtable layout from `gf_clmul_mod_lt`.
- The assembly uses explicit NEON registers and clobbers; edits must preserve GCC/Clang constraint validity as well as arithmetic behavior.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_aarch64_neon_common.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_aarch64_neonx2.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_aarch64_neonx2.c

## Scope

This file registers a more aggressively unrolled AArch64 NEON RAID-Z math implementation named `aarch64_neonx2`. It reuses the common AArch64 NEON primitive header and shared RAID-Z algorithm template, but chooses wider strides for several helper operations.

The source was read completely, lines 1-237.

## Primary Interfaces

- `DEFINE_GEN_METHODS(aarch64_neonx2)` instantiates generation methods.
- `DEFINE_REC_METHODS(aarch64_neonx2)` instantiates reconstruction methods.
- `raidz_will_aarch64_neonx2_work()` gates use on `kfpu_allowed()`.
- `vdev_raidz_aarch64_neonx2_impl` publishes the implementation as `"aarch64_neonx2"`.

## Architecture Configuration

The file is compiled only for `defined(__aarch64__)`. It includes `vdev_raidz_math_aarch64_neon_common.h`, defines stride/register macros, and then includes `vdev_raidz_math_impl.h`.

Compared with `aarch64_neon`, zero/copy/add use 8-vector strides and registers `0-7`, so those simple streaming operations process more data per loop body. Most syndrome and generation paths remain 4-vector stride operations. Two-column recovery for PQ, PR, and QR uses 4-vector recovery stride with separate X/Y/T register groups, while PQR recovery remains a 2-vector stride path.

## Special Build Handling

The file suppresses GCC's `-Wframe-larger-than=` diagnostic around `DEFINE_REC_METHODS(aarch64_neonx2)` for non-Clang GCC builds. The local comment explains that `-O0` debug builds may not coalesce stack frames enough, causing large-frame warnings even though the optimized build shape is intended.

## Dependencies

- `vdev_raidz_math_aarch64_neon_common.h` supplies all vector operations.
- `sys/vdev_raidz_impl.h` supplies RAID-Z structures and method-table types.
- `vdev_raidz_math_impl.h` supplies the shared generate/reconstruct implementation.

## Filesystem Relevance

This backend is an alternate AArch64 SIMD implementation for RAID-Z parity generation and reconstruction. It targets throughput improvements by increasing unrolling/register use for common buffer operations while preserving the same RAID-Z equations and selection gate as the baseline NEON backend.

## Correctness Notes

- Selection requires `kfpu_allowed()`.
- The x2 variant changes only macro configuration and generated code shape; it does not define independent parity equations.
- Larger unrolled recovery paths increase register and stack-pressure sensitivity, reflected in the explicit GCC diagnostic handling.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_aarch64_neonx2.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_avx2.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_avx2.c

## Scope

This file implements the x86_64 AVX2 RAID-Z math primitive layer, configures the shared RAID-Z math template for 32-byte vectors, and registers the `"avx2"` backend.

The source was read completely, lines 1-415.

## Primary Interfaces

- `v_t` is a 32-byte aligned vector element.
- `XOR_ACC`, `XOR`, `ZERO`, `COPY`, `LOAD`, and `STORE` map to AVX2 `ymm` instructions.
- `MUL2_SETUP`, `MUL2`, `MUL4`, and `MUL` implement GF arithmetic.
- `DEFINE_GEN_METHODS(avx2)` and `DEFINE_REC_METHODS(avx2)` instantiate the shared methods.
- `raidz_will_avx2_work()` requires `kfpu_allowed()`, `zfs_avx_available()`, and `zfs_avx2_available()`.
- `vdev_raidz_avx2_impl` registers the backend as `"avx2"`.

## Vector Operations

The implementation uses `ymm` registers and 32-byte memory slots:
- `vpxor` implements XOR and XOR-accumulate.
- `vmovdqa` implements aligned loads, stores, and copies.
- `ZERO` is implemented as `XOR(r, r)`.
- `FLUSH()` issues `vzeroupper`, and `raidz_math_end()` calls it before `kfpu_end()` to avoid AVX/SSE transition costs and stale upper-register state.

Unsupported register counts call `ZFS_ASM_BUG()`/`ASSERT(0)`.

## GF Multiplication

`MUL2_SETUP()` broadcasts `0x1d` into `ymm14` and zeros `ymm15`. `_MUL2()` uses signed byte compare, byte add, mask, and XOR reduction to multiply by 2 in GF(2^8). `MUL4()` calls `MUL2()` twice.

Arbitrary `MUL(c, ...)` uses the externally defined `gf_clmul_mod_lt` table. `_MULx2()` broadcasts the coefficient's 16-byte subtables into AVX lanes, separates upper and lower nibbles with a `0x0f` mask, performs `vpshufb` table lookups, and XORs partial products. Four-vector multiplication is handled as two two-vector operations.

## Template Configuration

All generation, syndrome, and simple buffer helpers are configured with stride 4. Two-column and three-column reconstruction use 2-vector recovery strides and register groups matching the generic `vdev_raidz_math_impl.h` recovery callbacks.

## Dependencies

- Compiled only when `defined(__x86_64) && HAVE_SIMD(AVX2)`.
- `sys/simd.h` supplies CPU feature probes and FPU-state wrappers.
- `gf_clmul_mod_lt` is provided by the AArch64 NEON table file.
- `vdev_raidz_math_impl.h` supplies shared RAID-Z algorithms.

## Filesystem Relevance

This is the AVX2 acceleration backend for ZFS RAID-Z P/Q/R parity generation and reconstruction on x86_64. It processes ABD buffers in vector chunks while the shared template handles RAID-Z row geometry, parity-column ordering, and failed-column equations.

## Correctness Notes

- The backend must not be selected unless both AVX and AVX2 are available and kernel FPU use is allowed.
- Loads/stores use aligned AVX instructions, so the surrounding ABD RAID-Z iteration must provide appropriately aligned vector spans.
- The arbitrary multiplication path depends on `gf_clmul_mod_lt` layout and on `vpshufb` operating independently per 128-bit lane.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_avx2.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_avx512bw.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_avx512bw.c

## Scope

This file implements the x86_64 AVX512BW RAID-Z math primitive layer, configures the shared RAID-Z math template for 64-byte vectors, and registers the `"avx512bw"` backend.

The source was read completely, lines 1-414.

## Primary Interfaces

- `v_t` is a 64-byte aligned vector element.
- `XOR_ACC`, `XOR`, `ZERO`, `COPY`, `LOAD`, and `STORE` use `zmm` operations.
- `MUL2_SETUP`, `MUL2`, `MUL4`, and `MUL` implement byte-wise GF arithmetic with AVX512BW support.
- `DEFINE_GEN_METHODS(avx512bw)` and `DEFINE_REC_METHODS(avx512bw)` instantiate shared generation and reconstruction methods.
- `raidz_will_avx512bw_work()` requires `kfpu_allowed()`, AVX, AVX512F, and AVX512BW feature availability.
- `vdev_raidz_avx512bw_impl` registers the backend as `"avx512bw"`.

## Vector Operations

The implementation uses 64-byte `zmm` vectors:
- `vpxorq` handles XOR and XOR-accumulate.
- `vmovdqa64` handles aligned copy/load/store.
- `ZERO` is implemented through XORing registers with themselves.
- `MUL2()` uses AVX512 mask registers from `vpcmpb` to conditionally apply the `0x1d` reduction byte after byte addition.

Unsupported register counts call `ZFS_ASM_BUG()`/`ASSERT(0)`.

## GF Multiplication

Arbitrary multiplication uses the same `gf_clmul_mod_lt[4*256][16]` table as AVX2 and AArch64 NEON. `_MULx2()` broadcasts 128-bit subtable rows with `vbroadcasti32x4`, masks/shifts nibbles, uses `vpshufb`, and XORs the lookup results. Four-vector multiplication is split into two two-vector operations.

## Template Configuration

The file explicitly notes that zero, copy, and multiply are already 2x unrolled, so AVX512 operation stride must not exceed 4 or a single step would exceed the 512-byte block size used by the template's iteration model. Generation and syndrome paths use stride 4; recovery paths use stride 2 for multi-target reconstruction.

## Dependencies

- Compiled only when `defined(__x86_64) && HAVE_SIMD(AVX512BW)`.
- `sys/param.h`, `sys/types.h`, and `sys/simd.h` supply system and SIMD helpers.
- `gf_clmul_mod_lt` is provided externally.
- `vdev_raidz_math_impl.h` supplies the shared RAID-Z algorithms.

## Filesystem Relevance

This backend accelerates RAID-Z parity generation and recovery on x86_64 CPUs with AVX512BW. It is especially relevant for byte-granular GF arithmetic because AVX512BW provides the byte operations and masking needed for efficient wide-vector multiply-by-2 and lookup-based arbitrary multiplication.

## Correctness Notes

- Feature gating includes AVX512F and AVX512BW; AVX512F alone is not sufficient for this backend.
- The stride limit comment is a correctness/performance guard around the shared template's chunking assumptions.
- The implementation's table-based multiplication must stay consistent with the global GF lookup table layout.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_avx512bw.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_avx512f.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_avx512f.c

## Scope

This file implements an x86_64 AVX512F RAID-Z math backend for systems with AVX512F but without relying on AVX512BW byte shuffle/table operations. It uses 64-byte vectors and builds arbitrary GF multiplication from generated per-coefficient functions.

The source was read completely, lines 1-495.

## Primary Interfaces

- `v_t` is a 64-byte aligned vector element.
- `XOR_ACC`, `XOR`, `ZERO`, `COPY`, `LOAD`, and `STORE` use `zmm` operations.
- `MUL2_SETUP`, `MUL2`, `MUL4`, and `MUL` implement GF multiplication without the shared lookup table.
- `MUL_x2_DEFINE(0..255)` emits 256 static multiplication functions.
- `gf_x2_mul_fns[256]` maps coefficient values to those generated functions.
- `DEFINE_GEN_METHODS(avx512f)` and `DEFINE_REC_METHODS(avx512f)` instantiate shared RAID-Z methods.
- `raidz_will_avx512f_work()` requires `kfpu_allowed()`, AVX, AVX2, and AVX512F availability.
- `vdev_raidz_avx512f_impl` registers the backend as `"avx512f"`.

## Vector Operations

The file uses `zmm` registers for primary operations and defines `VRy*` helpers for `ymm` names, though the active RAID-Z primitives are expressed with `zmm` macros. `vpxorq` performs XOR, `vmovdqa64` performs aligned movement, and `ZERO` is implemented as self-XOR.

Unlike the AVX512BW file, some switch statements omit explicit default assertions for unsupported counts in simple operations. The generated template's macro configuration supplies the supported counts used by these paths.

## GF Multiplication

`MUL2_SETUP()` broadcasts constants used by the AVX512F-only multiply-by-2 routine: reduction byte `0x1d`, high-bit mask `0x80`, and low-bit mask `0xfe`. `_MUL2()` uses qword logical shifts and `vpternlogd` to emulate byte-wise GF multiply-by-2 without AVX512BW byte compare/masked-byte operations.

Arbitrary multiplication is implemented by `_MUL_PARAM(x, in, acc)`, which conditionally accumulates powers of two for each coefficient bit. `MUL_x2_DEFINE()` expands this logic into 256 coefficient-specific functions. `MUL(c, ...)` copies two-vector pairs into fixed scratch registers, calls `gf_x2_mul_fns[c]`, and copies the accumulated result back.

## Template Configuration

Generation, syndrome, zero/copy/add, and multiply paths use stride 4. Unlike AVX2 and AVX512BW, reconstruction paths for PQ, PR, QR, and PQR are also configured with stride 4 and larger register groups. Recovery `*_DEFINE()` macros call `MUL2_SETUP()` where arbitrary multiplication may require the AVX512F constants.

## Dependencies

- Compiled only when `defined(__x86_64) && HAVE_SIMD(AVX512F)`.
- `sys/simd.h` supplies CPU feature probes and FPU state wrappers.
- `sys/debug.h` supplies `VERIFY()`.
- `vdev_raidz_math_impl.h` supplies the shared RAID-Z algorithms.
- This file does not consume `gf_clmul_mod_lt`; it uses generated multiply functions instead.

## Filesystem Relevance

This backend provides RAID-Z SIMD acceleration for AVX512F-capable systems where AVX512BW-specific byte operations may not be available. It keeps ZFS RAID-Z parity/reconstruction accelerated using only AVX512F plus AVX/AVX2 prerequisites.

## Correctness Notes

- The generated 256-function table must preserve GF(2^8) multiplication semantics for every coefficient.
- Runtime selection requires AVX2 as well as AVX512F, reflecting dependencies in the instruction strategy and SIMD environment.
- Register scratch choices such as `_mul_x2_in` and `_mul_x2_acc` are part of the macro contract used by generated multiplication functions.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_avx512f.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_impl.h -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_impl.h

## Scope

This header is the shared RAID-Z math algorithm template used by architecture-specific SIMD backends. It supplies coefficient calculation, ABD helper callbacks, P/Q/R parity generation, and reconstruction routines for one, two, and three missing data columns.

The source was read completely, lines 1-1529.

## Template Contract

Architecture files must define vector type `v_t`, vector operations (`LOAD`, `STORE`, `XOR`, `XOR_ACC`, `ZERO`, `COPY`, `MUL2`, `MUL4`, `MUL`), setup hooks, register groups, and stride macros before including this header. The header then expands those primitives into backend-specific `raidz_generate_*_impl()` and `raidz_reconstruct_*_impl()` functions via method-definition macros from `sys/vdev_raidz_impl.h`.

`raidz_math_begin()` and `raidz_math_end()` delimit SIMD/FPU state ownership around public generate/reconstruct operations.

## Coefficient Calculation

The noinline coefficient helpers compute GF constants from RAID-Z geometry and failed-column indexes:
- `raidz_rec_q_coeff()` computes the single-column Q recovery multiplier.
- `raidz_rec_r_coeff()` computes the single-column R recovery multiplier.
- `raidz_rec_pq_coeff()` solves two-column recovery using P and Q.
- `raidz_rec_pr_coeff()` solves two-column recovery using P and R.
- `raidz_rec_qr_coeff()` solves two-column recovery using Q and R.
- `raidz_rec_pqr_coeff()` solves three-column recovery using P, Q, and R.

They rely on `gf_exp2()`, `gf_exp4()`, `gf_mul()`, `gf_div()`, and `gf_inv()` supplied by the broader RAID-Z implementation.

## ABD Helper Callbacks

- `raidz_zero_abd_cb()` zeroes destination vectors and backs the `raidz_zero()` macro.
- `raidz_copy_abd_cb()` copies vectors and backs `raidz_copy()`.
- `raidz_add_abd_cb()` XORs source into destination and backs `raidz_add()`.
- `raidz_mul_abd_cb()` multiplies a buffer in place by a GF coefficient.

These callbacks are driven through `abd_iterate_func()` and `abd_iterate_func2()`, so the shared algorithm works with OpenZFS ABD storage rather than assuming one flat buffer.

## Parity Generation

`CHUNK` is fixed at 65536 bytes for L2-cache blocking.

- `raidz_generate_p_impl()` generates RAIDZ1 P parity by copying the first data column into P and XORing remaining data columns chunk by chunk.
- `raidz_generate_pq_impl()` generates RAIDZ2 P and Q parity. It initializes both parity columns from the first data column, then calls `raidz_gen_pq_add()` for each subsequent data column.
- `raidz_generate_pqr_impl()` generates RAIDZ3 P, Q, and R parity. It initializes all three parity columns from the first data column, then calls `raidz_gen_pqr_add()` for remaining data columns.

The syndrome macros encode the recurrence:
- P parity is simple XOR.
- Q parity repeatedly multiplies the existing syndrome by 2 before adding data.
- R parity repeatedly multiplies the existing syndrome by 4 before adding data.

Short data columns are handled by continuing Q/R syndrome updates after `dsize` ends, preserving RAID-Z's column-position weighting.

## Reconstruction

Reconstruction runs in two phases: calculate one or more syndromes from available data and parity, then solve for missing data using precomputed GF coefficients.

Single-column recovery:
- `raidz_reconstruct_p_impl()` reconstructs from P by XORing P with all available data columns.
- `raidz_reconstruct_q_impl()` computes Q syndrome, XORs Q parity, and multiplies by the Q coefficient.
- `raidz_reconstruct_r_impl()` computes R syndrome, XORs R parity, and multiplies by the R coefficient.

Two-column recovery:
- `raidz_reconstruct_pq_impl()` uses `raidz_syn_pq_abd()` and `raidz_rec_pq_abd()`.
- `raidz_reconstruct_pr_impl()` uses `raidz_syn_pr_abd()` and `raidz_rec_pr_abd()`.
- `raidz_reconstruct_qr_impl()` uses `raidz_syn_qr_abd()` and `raidz_rec_qr_abd()`.

Three-column recovery:
- `raidz_reconstruct_pqr_impl()` uses `raidz_syn_pqr_abd()` and `raidz_rec_pqr_abd()`.

The recovery callbacks combine parity columns with generated syndromes, save intermediate P/Q syndromes where needed, apply `MUL()` with the coefficient indexes, XOR terms together, and store reconstructed target vectors.

## RAID-Z Geometry Handling

The comments document "big" and "short" RAID-Z columns. Reconstruction uses the largest target size as the working length. If a later target column is shorter, the code allocates a temporary ABD of the larger size, computes the full syndrome/recovery there, copies only the original short length back, and frees the temporary ABD.

The implementation also handles cases where a target ABD is absent: reconstruction returns the bitmask of parity columns used without attempting writes when the primary target buffer is `NULL`.

## Dependencies

- `sys/types.h` and `sys/vdev_raidz_impl.h` supply type, ABD, RAID-Z row, code-column, target, and multiplication-index definitions.
- Architecture-specific wrappers supply all vector and SIMD-state macros.
- ABD iteration helpers provide segmented-buffer traversal and RAID-Z multi-buffer iteration.

## Filesystem Relevance

This header contains the core accelerated RAID-Z parity and reconstruction logic shared by AArch64 NEON, AVX2, AVX512BW, and AVX512F backends in this group. It is central to ZFS fault tolerance because it computes and repairs the P/Q/R erasure codes used by RAID-Z vdevs.

## Correctness Notes

- Coefficient formulas depend on `rr_cols`, `rr_firstdatacol`, and target ordering; incorrect target indexes would reconstruct incorrect bytes.
- The template assumes all vector callbacks process sizes in multiples of `sizeof (v_t)` as supplied by ABD RAID-Z iterators.
- Temporary ABD allocation is required for short targets so syndrome equations can be evaluated over the big-column range without conditional logic in vector loops.
- The returned bitmasks identify which parity columns were used for reconstruction, not a generic success/failure code.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_impl.h -->
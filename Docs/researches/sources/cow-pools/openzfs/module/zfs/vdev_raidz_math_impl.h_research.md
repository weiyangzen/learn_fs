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

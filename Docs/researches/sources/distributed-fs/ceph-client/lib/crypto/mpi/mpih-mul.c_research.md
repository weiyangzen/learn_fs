# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpih-mul.c

## Purpose
Implements low-level natural-number multiplication and squaring, including schoolbook base cases and Karatsuba recursion.

## Important APIs, Types, and Functions
- `mpihelp_mul()` is the public low-level multiply entry.
- `mul_n_basecase()` and `mul_n()` handle equal-size multiplication.
- `mpih_sqr_n_basecase()` and `mpih_sqr_n()` handle squaring.
- `mpihelp_mul_karatsuba_case()` handles unequal-size operands with recursive chunks.
- `mpihelp_release_karatsuba_ctx()` frees scratch contexts.

## Control Flow and State
For small operands, multiplication uses schoolbook loops with special cases for multiplier limb 0 or 1. Larger equal-size operands use Karatsuba splitting into high/low halves, calculating high, middle difference product, and low products, then recombining. Odd sizes are handled by recursing on size-1 and adding the top limb separately. Unequal Karatsuba multiplication processes full-size chunks and a residual tail, allocating scratch buffers in a `karatsuba_ctx` chain. The caller owns product storage and result top-limb reporting.

## Dependencies and Integration Points
Used by `mpi_mul()` and `mpi_powm()`. Relies on generic limb add/sub/mul helpers, scratch allocation, and non-overlap between product and operands.

## Risks and Test Signals
Risks include scratch leaks on error, Karatsuba recomposition carry errors, odd-size edge cases, and thresholds. Tests should cover operand sizes below, at, and above `KARATSUBA_THRESHOLD`, square-vs-multiply equivalence, unequal sizes with residual chunks, all-zero/all-one limbs, and randomized reference comparisons under allocation-failure injection.

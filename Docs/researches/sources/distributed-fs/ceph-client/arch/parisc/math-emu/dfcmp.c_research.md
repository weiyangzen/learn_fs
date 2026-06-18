# sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfcmp.c

Purpose: implements double-precision floating-point compare and writes the PA-RISC status C-bit according to the supplied condition predicate.

Important APIs/types/functions: `dbl_fcmp(dbl_floating_point *leftptr, dbl_floating_point *rightptr, unsigned int cond, unsigned int *status)`. Condition-field helpers from `float.h` extract unordered, equal, less-than, greater-than, and exception predicate bits.

Control flow: the function copies operands, handles NaN cases first, and raises invalid when a signaling NaN is present or when the condition requires an exception on unordered compare. Otherwise NaNs set C-bit from `Unordered(cond)`. Non-NaN comparisons handle opposite signs, the special equality of positive and negative zero, same-sign equality, positive magnitude ordering, and reversed negative ordering.

State and dependencies: mutates the C-bit and invalid flag in `*status`; no other persistence. Depends on `float.h` and `dbl_float.h`.

Risks: PA-RISC condition predicates are encoded in `cond`; testing only numeric compare results is insufficient. Signaling NaN detection and quiet NaN unordered behavior must match the architecture. Negative ordering is intentionally reversed and easy to break with refactors.

Test signals: compare matrices for all relation predicates, signed zeros, positive and negative finite values, infinities, quiet NaNs, signaling NaNs, invalid-trap enabled/disabled, and C-bit results for unordered conditions.

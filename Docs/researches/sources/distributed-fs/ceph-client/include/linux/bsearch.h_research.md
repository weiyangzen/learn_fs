## sources/distributed-fs/ceph-client/include/linux/bsearch.h

**Purpose:** This header provides the kernel binary-search interface for sorted arrays. It offers an inline implementation for compile-time optimization and declares the out-of-line `bsearch()` helper.

**Important APIs/types/functions:** `__inline_bsearch(const void *key, const void *base, size_t num, size_t size, cmp_func_t cmp)` walks a sorted array by repeatedly comparing the key to the middle element. `bsearch()` has the same signature and is the exported generic helper. The comparator type `cmp_func_t` comes from `linux/types.h`.

**Control flow, state, persistence:** The algorithm is stateless and read-only. It computes `pivot = base + (num >> 1) * size`, returns the pivot on comparator equality, advances `base` past the pivot on positive comparison, and halves the remaining element count until exhausted.

**Dependencies/integration:** Used by code that keeps sorted kernel arrays, including BTF ID-set lookups in `btf.h`. The caller owns ordering, comparator correctness, element lifetime, and synchronization around concurrent mutation.

**Risks and test signals:** Risks include unsorted input, comparators that overflow or violate strict ordering, zero/incorrect element sizes, and racing writers. Test signals are boundary cases for empty, one-element, first/middle/last, missing-low, missing-high, and duplicate-key arrays, plus sanitizer coverage for pointer arithmetic.

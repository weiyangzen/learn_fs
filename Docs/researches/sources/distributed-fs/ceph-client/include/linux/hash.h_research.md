<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hash.h -->
# sources/distributed-fs/ceph-client/include/linux/hash.h

Purpose: This header provides fast integer and pointer hashing helpers for kernel hash tables and subsystems.

Important APIs/types/functions: It defines `GOLDEN_RATIO_32`, `GOLDEN_RATIO_64`, word-size-dependent `GOLDEN_RATIO_PRIME`, and `hash_long()`. Generic helpers include `__hash_32_generic()`, `hash_32()`, `hash_64_generic()`, `hash_ptr()`, and `hash32_ptr()`. Architecture overrides can supply `<asm/hash.h>` and `HAVE_ARCH_*` definitions under `CONFIG_HAVE_ARCH_HASH`.

Control flow, state, and persistence: Hashing multiplies by an odd golden-ratio-derived constant and uses the high bits of the product. There is no persistent state. `hash32_ptr()` only folds a pointer to 32 bits and intentionally does not perform full hashing.

Dependencies/integration: It depends on architecture types, compiler helpers, word size, and optional arch-optimized hash functions. `hashtable.h` uses these helpers through `hash_min()`.

Risks and test signals: Passing invalid `bits` values can shift incorrectly or create poor bucket selection. Architecture overrides must match generic behavior expectations or update self-test markers. Tests should use `lib/test_hash.c`, compare arch and generic variants, exercise 32/64-bit builds, pointer folding, and distribution for typical key sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hash.h -->

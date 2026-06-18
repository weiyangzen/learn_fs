# File Research: sources/cow-pools/bcachefs-tools/include/linux/cache.h

Purpose: cacheline-size and cache-alignment shim.

Key contents:
- Defines L1 cache shift/bytes and SMP cache bytes as 64 bytes.
- Defines `L1_CACHE_ALIGN()`.
- Defines `__read_mostly` and `__ro_after_init` as empty.
- Defines cacheline alignment attributes.

Important interactions:
- Used by code that expects Linux cacheline annotation macros.
- In tools builds, most placement annotations are no-ops except explicit alignment attributes.

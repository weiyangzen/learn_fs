# sources/distributed-fs/ceph-client/arch/arm64/lib/uaccess_flushcache.c

Purpose: implements copy helpers that clean written cache lines to persistence after kernel or user-source copies.

Important APIs/types/functions: `memcpy_flushcache`, `__copy_user_flushcache`, `dcache_clean_pop`, `raw_copy_from_user`, and exported `memcpy_flushcache`.

Control flow: `memcpy_flushcache` copies from kernel source to destination, then cleans the destination range to point of persistence. `__copy_user_flushcache` performs raw copy-from-user, then cleans only the successfully copied prefix `n - rc`.

State and persistence: writes destination memory and issues cache maintenance to PoP. It does not keep software state.

Dependencies/integration: enabled by `CONFIG_ARCH_HAS_UACCESS_FLUSHCACHE`; integrates with persistent memory and uaccess paths, cacheflush assembly, and raw usercopy.

Risks: assumes destination is cacheable memory and does not require an extra barrier against the preceding memcpy. A faulting user copy must clean only bytes actually written. Persistent memory ordering semantics depend on surrounding caller barriers.

Test signals: pmem/DAX flush tests, partial usercopy faults, zero-length copies, cache line boundary ranges, and validation that only copied bytes are flushed after faults.

# sources/distributed-fs/ceph-client/arch/x86/lib/usercopy_64.c

## Purpose
This file supplies 64-bit x86 persistent-memory/cache-flush copy helpers when `CONFIG_ARCH_HAS_UACCESS_FLUSHCACHE` is enabled. It writes back cache lines with CLWB and provides non-temporal memcpy/copy-from-user variants for pmem durability paths.

## Important APIs, Types, and Functions
Key functions are `clean_cache_range()`, `arch_wb_cache_pmem()`, `copy_user_flushcache()`, and `__memcpy_flushcache()`. The implementation uses `boot_cpu_data.x86_clflush_size`, `clwb()`, `copy_to_nontemporal()`, `masked_user_access_begin()`, `user_access_end()`, `memcpy()`, `movnti`, `sfence` semantics inherited from users, and libnvdimm integration.

## Control Flow
`clean_cache_range()` rounds the start down to cache-line granularity and issues CLWB over the range. `arch_wb_cache_pmem()` is a direct exported wrapper. `copy_user_flushcache()` begins masked user access, copies from user to destination using non-temporal stores, ends access, then explicitly flushes edge regions when alignment or size forced cached copies. `__memcpy_flushcache()` copies and flushes an unaligned prefix, uses 32-byte, 8-byte, and 4-byte `movnti` loops for the aligned body, then cached-copies and flushes any tail.

## State and Persistence
There is no file-local persistent state. The observable persistence behavior is hardware cache writeback for pmem-durability users, with data written to caller-provided memory and cache lines flushed from CPU caches.

## Dependencies and Integration Points
It depends on x86 cache-line size discovery, CLWB support plumbing, non-temporal copy primitives, uaccess masking, highmem/libnvdimm headers, and pmem/DAX users that need explicit writeback. The functions are exported GPL symbols for persistence infrastructure.

## Risks and Test Signals
Risks include incorrect edge flushing for unaligned transfers, assuming CLWB availability through the Kconfig path, user-access faults during pmem copy, and durability bugs if callers omit required ordering barriers. Test signals include pmem/DAX tests, unaligned start/size cases, faulting user source copies, cacheline-size variation, and persistence validation across power-fail simulation where available.

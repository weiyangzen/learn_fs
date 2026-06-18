<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/cache.h -->
# sources/distributed-fs/ceph-client/include/vdso/cache.h

Purpose: defines cacheline alignment helpers for vDSO data structures using architecture cache-size values.

Important APIs and types: `SMP_CACHE_BYTES` defaults to `L1_CACHE_BYTES` if not already provided, and `____cacheline_aligned` applies `__attribute__((__aligned__(SMP_CACHE_BYTES)))`.

Control flow: vDSO data page structs use this attribute to keep frequently-read data cacheline aligned for userspace fast paths.

State and persistence: no state; controls compile-time object layout.

Dependencies and integration points: depends on `asm/cache.h` and is used by `vdso/datapage.h`.

Risks and test signals: risks include missing architecture cache constants or changing struct layout shared with compat vDSO readers. Test vDSO layout and alignment assertions across architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/cache.h -->

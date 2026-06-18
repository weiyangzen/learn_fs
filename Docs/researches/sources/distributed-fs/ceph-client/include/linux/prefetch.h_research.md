# sources/distributed-fs/ceph-client/include/linux/prefetch.h

Purpose: provides generic cache prefetch wrappers so common code can request read/write prefetching without depending directly on architecture intrinsics. It also exposes helper prefetches for byte ranges and page-address metadata.

Important APIs and types: `prefetch(x)` and `prefetchw(x)` default to `__builtin_prefetch()` unless an architecture supplies `ARCH_HAS_PREFETCH` or `ARCH_HAS_PREFETCHW`. `PREFETCH_STRIDE` defaults to `4 * L1_CACHE_BYTES`. `prefetch_range()` walks a buffer in stride increments when arch prefetch exists, and `prefetch_page_address()` prefetches `struct page` metadata only for page-virtual configurations.

Control flow: callers issue prefetches before touching memory on hot paths; architectures may replace the default macros with tuned instructions. The range helper is a simple loop over cacheline lookahead distance and intentionally has no effect on arches without an explicit prefetch implementation.

State and persistence: no state is stored and no data is modified. Prefetching is a transient CPU cache hint and must not be required for correctness.

Dependencies and integration points: depends on `asm/processor.h`, `asm/cache.h`, `L1_CACHE_BYTES`, and optional page virtual configuration. It integrates with list walking, networking, filesystem, and memory-management paths that want architecture-neutral prefetch hints.

Risks and test signals: risks are performance regressions from over-prefetching, relying on prefetch for ordering, and invalid arch definitions that fault on bad addresses. Test signals are build coverage across arches, microbenchmarks of streaming users, and fault-injection style calls with null/unmapped-looking addresses to confirm prefetch remains only a hint.

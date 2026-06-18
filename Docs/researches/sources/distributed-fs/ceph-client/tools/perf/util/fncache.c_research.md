# sources/distributed-fs/ceph-client/tools/perf/util/fncache.c

## Purpose

`fncache.c` caches whether file names are readable to avoid repeated `access(R_OK)` calls in paths that may query the same files many times.

## Important APIs, Types, and Functions

The public API is `file_available(const char *name)`. Static helpers initialize a global hashmap once, hash and compare string keys, look up cached booleans, and update the cache with duplicated file-name keys.

## Control Flow

`file_available` checks the cache first. On miss, it calls `access(name, R_OK)`, stores the boolean result in the hashmap with `hashmap__set`, frees any replaced key, and returns the result. `pthread_once` lazily initializes the global map.

## State and Persistence Behavior

The global `fncache` persists for the process lifetime and has no eviction. It owns duplicated key strings but stores boolean values directly as long integers through the hashmap macros. The comment notes there is no LRU and callers should only use it when the input space is bounded.

## Dependencies and Integration Points

It depends on pthread once initialization, libc allocation/string/access, Linux compiler annotations, `fncache.h`, and the generic hashmap. It is a utility for perf code that probes many possible files or debug/source paths.

## Risks and Edge Cases

The underlying hashmap is documented as non-thread-safe. `pthread_once` protects initialization only, not concurrent lookups/updates. Results can become stale if files are created, removed, or permissions change after caching. Unbounded names can grow memory for the lifetime of perf.

## Test Signals

Tests should cover cache hits/misses, permission-readable versus missing files, replaced keys, stale-result behavior after file changes, and threaded callers if the intended use ever crosses threads.

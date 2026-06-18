# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/cache.c

## Purpose
`cache.c` implements a small integer cache used by `gendwarfksyms` for repeated address/file/expansion lookups.

## Important APIs, Types, and Functions
`struct cache_item` stores an unsigned long key, int value, and hash node. `cache_set()`, `cache_get()`, `cache_init()`, and `cache_free()` manage a hashtable embedded in `struct cache`.

## Control Flow
Callers initialize a cache, insert key/value pairs, query by key with `-1` as miss, and free all entries when a processing phase ends.

## State and Persistence Behavior
Cache state is process-local and heap-backed. There is no deduplication in `cache_set()`, so repeated keys can create multiple entries; `cache_get()` returns the first matching entry in the hash chain.

## Dependencies and Integration Points
Used by DWARF processing for source-file privacy caching and expansion-cycle detection. It depends on kernel-style hashtable macros and `xmalloc()`.

## Risks and Test Signals
Using `-1` as a miss sentinel means cached values must not need negative data. Duplicate keys can waste memory or hide newer values. Test insert/get/free, miss behavior, duplicate-key semantics, and leak checks under repeated CU processing.

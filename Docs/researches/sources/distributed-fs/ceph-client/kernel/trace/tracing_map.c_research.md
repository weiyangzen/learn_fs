<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/tracing_map.c -->
# sources/distributed-fs/ceph-client/kernel/trace/tracing_map.c

Purpose: provides a preallocated, lock-free hash map used by tracing aggregation paths such as hist triggers. It associates arbitrary fixed-size keys with `tracing_map_elt` objects that carry sum fields, variables, key copies, and optional client private data.

Important APIs: map setup uses `tracing_map_create()`, `tracing_map_add_key_field()`, `tracing_map_add_sum_field()`, `tracing_map_add_var()`, and `tracing_map_init()`. Runtime operations are `tracing_map_insert()`, `tracing_map_lookup()`, `tracing_map_update_sum()`, `tracing_map_set_var()`, and read helpers. Sorting is exposed through `tracing_map_sort_entries()` and `tracing_map_destroy_sort_entries()`. Numeric and string comparison helpers drive sorting.

Control flow: creation allocates a sparse hash entry array twice the requested element count. Initialization allocates all elements before tracing starts. Insert hashes the key with jhash, probes linearly, claims empty slots with `cmpxchg()`, initializes a free element from an atomic pool, copies the full key, publishes the element with a write barrier, and increments hits. Lookup uses the same probing without insertion. Clear resets counters, map entries, and element fields. Sorting snapshots current entries into a vmalloc array and sorts by key or sum, with optional secondary sort.

State and persistence: all state is in memory and tied to the map lifetime. Keys are never deleted or resized during active use. Hits and drops are atomic counters. Sum fields are atomic64; vars include separate set flags. Client callbacks manage private per-element state.

Dependencies and integration: uses vmalloc, slab, jhash, sort, kmemleak annotations, atomics, and tracing-specific allocation helpers. It is an internal library for tracing aggregators.

Risks: the map deliberately stops inserting after the fixed pool is exhausted, so callers must handle NULL and drops. Correctness depends on no active writers during clear/destroy and on publish ordering in insert. Duplicate hash/key publication is guarded with probing and duplicate detection during sort. Test signals include concurrent insertion of equal and colliding keys, pool exhaustion, key and sum sorting, secondary sort ordering, variable read-once semantics, and client callback cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/tracing_map.c -->

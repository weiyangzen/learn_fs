# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/int-map.c

## Purpose
`int-map.c` implements an opaque map from `u64` integer keys to non-NULL pointer values using non-concurrent hopscotch hashing. It is used where VDO needs fast in-memory lookup without per-entry allocation, such as active PBN/LBN locks and bio merge tracking.

## Important APIs, Types, and Functions
The public API is `vdo_int_map_create()`, `vdo_int_map_free()`, `vdo_int_map_size()`, `vdo_int_map_get()`, `vdo_int_map_put()`, and `vdo_int_map_remove()`. `struct bucket` stores biased hop offsets plus key/value. `struct int_map` tracks size, capacity, bucket count, and bucket array. Key internals include `hash_key()`, `select_bucket()`, `search_hop_list()`, `find_empty_bucket()`, `move_empty_bucket()`, `find_or_make_vacancy()`, `resize_buckets()`, and `update_mapping()`.

## Control Flow
Creation allocates an expanded bucket array sized from the requested capacity and default load factor. Lookup hashes a key to a neighborhood and scans that neighborhood's sorted hop list. Insert first checks for an existing key, then finds or creates an empty bucket in the target neighborhood. If no vacancy can be moved within range, the map grows by roughly 50%, rehashes all entries, and retries. Remove splices the matching bucket out of its neighborhood hop list and clears the value.

## State and Persistence Behavior
All state is volatile heap memory. The map owns only the bucket array and map object, not mapped values. It never shrinks after removals. Values must be non-NULL because NULL marks an empty bucket. There is no internal locking; callers serialize access when used concurrently.

## Dependencies and Integration Points
The implementation uses VDO allocation/logging/assertion helpers, `numeric.h` for integer conventions, Linux min/max helpers, and VDO error codes. It is integrated by logical zones, physical zones, and I/O submitter merge maps.

## Risks and Edge Cases
Resize is expensive and may cause high insertion latency; capacity should be chosen for expected peak size when latency matters. Hop relocation relies on biased offsets and packed buckets, so off-by-one bugs would corrupt lookup chains. `vdo_int_map_put()` rejects NULL values with `-EINVAL`. Failed resize restores the old map, but callers must still handle insertion failure. The implementation is explicitly not thread-safe.

## Test Signals
Tests should cover create with zero and explicit capacity, insert/get/remove, duplicate insert with update false/true, old-value return, growth under high load, deletion from head/middle/tail hop lists, NULL insertion rejection, and caller-side locking in concurrent integration paths.

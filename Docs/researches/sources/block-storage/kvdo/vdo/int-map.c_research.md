# File Research: sources/block-storage/kvdo/vdo/int-map.c

Pointer-valued `uint64_t` map implemented with non-concurrent hopscotch hashing.

Key responsibilities:
- Implements `make_int_map()`, `free_int_map()`, `int_map_size()`, `int_map_get()`, `int_map_put()`, and `int_map_remove()`.
- Uses packed buckets containing `first_hop`, `next_hop`, key, and non-NULL value.
- Hashes keys with a CityHash-derived 64-bit mixer and scales 32 hash bits into the capacity without modulo division.
- Maintains sorted biased-offset hop lists per neighborhood.
- Finds or creates vacancies by probing and moving entries closer to their home neighborhood.
- Resizes by 1.5x and rehashes all entries when a suitable vacancy cannot be found.

Important behavior:
- `initial_load` defaults to 75%; values over 100 are rejected.
- Capacity is number of neighborhoods; bucket array includes `NEIGHBORHOOD - 1` extra buckets to avoid wraparound at the end.
- NULL values are invalid because NULL marks empty buckets.
- `int_map_put()` can either update existing values or preserve them while still returning the old value.
- The map grows but never shrinks.
- Deletes truly remove entries and splice hop lists, avoiding tombstones.

Dependencies:
- Uses UDS memory allocation, logging, numeric helpers, assertions, and error codes.

Notable risks:
- No internal locking; callers must serialize access.
- Resize is expensive and can cause high insertion latency.
- `NEIGHBORHOOD` is 255 to fit biased offsets in `uint8_t`; changing this affects packed encoding.
- The packed bucket layout may create unaligned key/value accesses on some architectures, relying on compiler/architecture support.

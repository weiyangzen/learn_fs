# sources/distributed-fs/ceph-client/tools/perf/util/hashmap.h

## Purpose

`hashmap.h` declares the generic hashmap API and iteration macros used by perf utility code. It originated from libbpf-style helpers and supports integer or pointer keys/values through long-sized storage.

## Important APIs, Types, and Functions

It defines `hash_bits`, `str_hash`, hash/equality callback typedefs, `struct hashmap_entry`, `struct hashmap`, `enum hashmap_insert_strategy`, lifecycle APIs, size/capacity queries, insert/set/add/update/append/delete/find wrappers, and iteration macros for all entries, safe deletion, and entries for one key. `hashmap_cast_ptr` uses `_Static_assert` to verify old-key/value pointer sizes.

## Control Flow

Callers initialize a map with callbacks, then use wrappers such as `hashmap__add`, `hashmap__set`, or `hashmap__find`. Iteration macros expand into nested bucket/chain loops. Key-specific iteration computes the bucket from the supplied key and filters by equality.

## State and Persistence Behavior

The map tracks callbacks, callback context, bucket array, capacity, capacity bits, and current size. Entry keys/values are stored as `long` or pointer unions; ownership of pointed-to data is external.

## Dependencies and Integration Points

The header depends on standard boolean/size/limits headers and is used by expression IDs, filename cache, evsel per-package masks, ftrace profile hashes, and other utility structures needing lightweight maps.

## Risks and Edge Cases

It is explicitly non-thread-safe. Pointer/integer polymorphism is convenient but can hide ownership and signedness mistakes. The comment typo `hasmap_entry` is documentation-only. `hashmap__for_each_key_entry` requires valid callbacks and handles an unallocated bucket array by starting at NULL.

## Test Signals

Compile tests should exercise integer and pointer keys/values with the static assertions. Runtime tests should cover C-string hash users, custom equality, all iteration macros, multimap append behavior, and empty-map key iteration.

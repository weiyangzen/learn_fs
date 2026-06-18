# sources/distributed-fs/ceph-client/tools/lib/bpf/hashmap.h

## Purpose
`hashmap.h` declares the generic libbpf hashmap API and provides inline hashing utilities plus macro wrappers that make the long-sized storage model usable with typed integer and pointer keys/values.

## APIs, Types, and Functions
Inline helpers are `hash_bits()` for multiplicative bucket-bit extraction and `str_hash()` for simple C-string hashing. Public types include `hashmap_hash_fn`, `hashmap_equal_fn`, `struct hashmap_entry`, `struct hashmap`, and `enum hashmap_insert_strategy`. The header declares lifecycle, query, insert, find, and delete functions, then exposes typed macros `hashmap__insert()`, `hashmap__add()`, `hashmap__set()`, `hashmap__update()`, `hashmap__append()`, `hashmap__delete()`, and `hashmap__find()`.

## Control Flow, State, and Persistence
`struct hashmap_entry` stores key and value as unions of `long` and pointer views, plus a singly linked `next` pointer. `struct hashmap` stores callback functions, callback context, bucket array, capacity, capacity bit count, and size. `hashmap_cast_ptr()` uses `_Static_assert` to verify that optional old-key/old-value output pointers point to long-sized objects or pointers. Iteration macros traverse all buckets, all buckets safely while caching `next`, all entries for one key, or one key safely.

## Dependencies and Integration
The header only requires standard boolean, size, and limit definitions. It is paired with `hashmap.c` and used by libbpf code that needs compact maps with custom hash/equality behavior. The API intentionally hides raw `long` casts behind macros for most callers while still permitting integer-key users to read `entry->key` and pointer-key users to read `entry->pkey`.

## Risks and Test Signals
Risks include ABI assumptions that pointers and chosen integer keys fit in `long`, non-thread-safe iteration and mutation, macro side effects if callers pass expressions with unexpected evaluation needs, and direct iteration over `map->buckets` requiring initialized or non-null bucket arrays. Test signals are compile-time failures for wrong output pointer sizes, LP64 and ILP32 builds, string-hash users, all iteration macro variants, append-mode multimap scans, and callers that mix integer and pointer views consistently.

# sources/distributed-fs/ceph-client/tools/lib/bpf/hashmap.c

## Purpose
`hashmap.c` implements libbpf's generic, non-thread-safe chained hashmap. It stores long-sized integer or pointer keys and values through the public macro layer in `hashmap.h`, grows buckets on demand, supports several insert semantics, and provides basic find/delete/clear/free operations.

## APIs, Types, and Functions
Implemented public functions are `hashmap__init()`, `hashmap__new()`, `hashmap__clear()`, `hashmap__free()`, `hashmap__size()`, `hashmap__capacity()`, `hashmap_insert()`, `hashmap_find()`, and `hashmap_delete()`. Internal helpers are `hashmap_add_entry()`, `hashmap_del_entry()`, `hashmap_needs_to_grow()`, `hashmap_grow()`, and `hashmap_find_entry()`. `HASHMAP_MIN_CAP_BITS` starts maps at four buckets.

## Control Flow, State, and Persistence
Initialization only stores caller-provided hash/equality callbacks and context, leaving buckets unallocated. Insert hashes the key using current capacity bits, optionally finds an existing entry for ADD/SET/UPDATE behavior, updates in place for SET/UPDATE, returns `-EEXIST` or `-ENOENT` for disallowed operations, grows the bucket table when empty or above roughly 75 percent load, allocates a new entry, and pushes it at the bucket head. Growth allocates a doubled power-of-two bucket array and rethreads existing entries using the new bit count. Clear frees entries and buckets but leaves callback configuration intact; free additionally frees the map object.

## Dependencies and Integration
The implementation depends on `hashmap.h` iteration macros, libc allocation, errno values, and `linux/err.h` for `ERR_PTR`/`IS_ERR_OR_NULL` conventions. It is used by libbpf internals such as BTF dump duplicate-name tracking and other key/value caches that need a tiny local map without pulling in a larger container library.

## Risks and Test Signals
Risks include no internal locking, caller ownership of pointed-to keys/values, append-mode duplicate keys returning the most recently inserted bucket-head entry for `hashmap_find()`, hash/equality callbacks needing to tolerate long-cast pointer keys, and iteration macros assuming bucket storage remains stable unless the safe form is used. Test signals are insert strategy coverage, growth and rehash correctness, duplicate-key append iteration, deletion from head/middle/tail chains, clear/free on empty and error-pointer maps, and pointer key/value round trips through the macro API.

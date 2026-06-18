# sources/distributed-fs/ceph-client/tools/perf/util/hashmap.c

## Purpose

`hashmap.c` implements a small generic, non-thread-safe hashmap used by perf/libbpf-derived utility code. It stores long-sized keys and values, including pointer values through wrapper macros in the header.

## Important APIs, Types, and Functions

It implements `hashmap__init`, `hashmap__new`, `hashmap__clear`, `hashmap__free`, `hashmap__size`, `hashmap__capacity`, `hashmap_insert`, `hashmap_find`, and `hashmap_delete`. Internal helpers manage chained entries, growth thresholds, rehashing, and bucket-chain search. It starts at 4 buckets and grows when the projected load exceeds roughly 75%.

## Control Flow

Insert computes a bucket using the current capacity bits, finds an existing key unless append mode is requested, performs add/set/update/append semantics, grows and rehashes as needed, then prepends a new entry. Set/update can return old key/value to callers for ownership cleanup. Find and delete compute the bucket and walk the chain. Clear frees entries and bucket storage.

## State and Persistence Behavior

The hashmap owns only entry nodes and bucket arrays. Key/value payload ownership stays with callers, which is why set/delete return old values. `hashmap__free` tolerates NULL and encoded error pointers. Bucket order changes on growth because entries are prepended into new chains.

## Dependencies and Integration Points

It depends on caller-provided hash/equality callbacks, Linux `ERR_PTR` helpers, errno values, and the iteration macros from `hashmap.h`. `#pragma GCC poison` prevents accidental use of kernel typedefs and `reallocarray`.

## Risks and Edge Cases

The implementation is not thread-safe. `hash_bits` with zero capacity bits maps all entries to bucket zero until growth; insert recalculates after growth. Pointer casting relies on long-sized pointers. Append mode creates multimaps where `find` returns the newest matching entry. Callers must free payloads before or after clear as appropriate.

## Test Signals

Tests should cover add/set/update/append semantics, old key/value return, delete, growth/rehash, iteration safe under deletion, multimap key iteration, NULL/error free, and pointer/integer macro usage.

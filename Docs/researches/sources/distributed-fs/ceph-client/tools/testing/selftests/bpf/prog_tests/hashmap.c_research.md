
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/hashmap.c

## Purpose

`hashmap.c` unit-tests libbpf's user-space `struct hashmap` implementation for integer keys, pointer/string keys, collision-heavy multimap behavior, deletion, iteration, clear, size, and empty-map semantics.

## Important APIs, Types, and Functions

The file uses `bpf/hashmap.h` APIs: `hashmap__new()`, `hashmap__free()`, `hashmap__add()`, `hashmap__set()`, `hashmap__update()`, `hashmap__append()`, `hashmap__insert()`, `hashmap__find()`, `hashmap__delete()`, `hashmap__clear()`, `hashmap__size()`, `hashmap__capacity()`, `hashmap__for_each_entry()`, and `hashmap__for_each_key_entry()`. It supplies custom hash/equality functions for integer, string, and forced-collision cases.

## Control Flow and Data Flow

Subtests create maps, insert/update/delete entries, verify returned old keys/values, iterate all buckets and per-key chains, and assert final sizes. The generic test covers normal map operations and deletion during iteration. The multimap test forces all keys into one bucket and validates per-key iteration. The empty test asserts lookups/deletes/iterations are inert. The pointer interface test uses string keys and values with custom hash/equality.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is entirely heap-allocated user-space hashmap data. Dependencies are libbpf's internal hashmap implementation and test macros; no kernel BPF state is used. Integration is with libbpf internals used by loaders and symbol maps. Risks are pointer/integer casting assumptions and collision-chain regressions. Test signals are expected size/capacity transitions, found bitmasks covering all inserted values, correct old key/value returns, no entries after deletion/clear, and no iteration from empty maps.

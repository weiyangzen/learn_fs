# sources/distributed-fs/lizardfs/src/common/flat_map.h

Purpose: implements a memory-efficient sorted-vector associative map with an interface close to `std::map`.

Important APIs/types/functions: template `flat_map<Key,T,C,Compare>` stores pairs in `flat_set<value_type, C, internal_compare>`. It exposes constructors, `operator[]`, `at`, insert/erase, iterators, `data()`, lookup, `find_nth`, bounds, comparators, relational operators, and `swap`.

Control flow: lookup delegates to `flat_set` lower-bound logic using `internal_compare`, which can compare key-to-pair and pair-to-key. `operator[]` lower-bounds by key and inserts default mapped values when absent.

State and persistence: in-memory sorted vector-like container. No persistence, no synchronization. Iterators are vector iterators and invalidate on inserts/erases as the underlying container dictates.

Dependencies and integration: depends on `flat_set.h` and standard algorithms. Used by goal label maps and other small associative data where cache locality matters.

Risks: insert is O(n); this is good for small maps but poor for large/mutation-heavy workloads. Constructor with `sorted=true` trusts caller ordering and uniqueness. `operator[](const key_type &&key)` uses a const rvalue reference, which prevents true move semantics for key input.

Test signals: `flat_map_unittest.cc` covers constructors, swap, iterators, insert/erase, `at`, count, custom compare, find/lower_bound, and nth lookup.

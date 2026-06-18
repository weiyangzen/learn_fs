# sources/distributed-fs/ceph/src/rgw/driver/posix/unordered_dense.h

## Purpose
`unordered_dense.h` is a vendored, header-only copy of `ankerl::unordered_dense` version 3.1.0. It provides fast dense-storage hash maps and hash sets for the POSIX RGW driver, using robin-hood open addressing for lookup metadata and a compact contiguous value container for iteration/storage. In this source tree it is included by `notify.h` to hold inotify watch descriptor mappings.

## Important APIs, Types, and Functions
The public aliases are `ankerl::unordered_dense::map<Key, T, Hash, KeyEqual, AllocatorOrContainer, Bucket>` and `ankerl::unordered_dense::set<Key, Hash, KeyEqual, AllocatorOrContainer, Bucket>`, both backed by `detail::table`. PMR variants are exposed under `ankerl::unordered_dense::pmr` when `<memory_resource>` or `<experimental/memory_resource>` is available.

The default `hash<T>` forwards unknown types to `std::hash`, but specializes strings, string views, pointers, smart pointers, enums, and scalar integral/character types. String-like and scalar specializations use an embedded wyhash-derived mixer and mark themselves with `is_avalanching`, which lets the table skip an extra hash-quality mixing step.

`bucket_type::standard` stores a 32-bit `m_dist_and_fingerprint` and 32-bit `m_value_idx`. `bucket_type::big` keeps the same distance/fingerprint field but uses `size_t` for `m_value_idx` and is packed for larger tables. The lower byte is a hash fingerprint; the upper bytes encode robin-hood probe distance in `dist_inc` units.

`detail::table` implements the container API: constructors, allocator access, dense iterators over `m_values`, `empty`, `size`, `max_size`, `clear`, `insert`, `emplace`, `try_emplace`, `insert_or_assign`, `erase`, `find`, `contains`, `count`, `equal_range`, `reserve`, `rehash`, `max_load_factor`, equality comparison, and nonstandard `extract`, `replace`, and `values`. Map-only APIs are SFINAE-gated on `T != void`; set instances use `T = void` and return const iterators.

The header also adds `std::erase_if` for this table type. It scans from back to front because erasing moves the last dense value into the erased slot and invalidates the old end iterator.

## Control Flow
Lookup starts with `mixed_hash(key)`, which either trusts an avalanching hasher or applies wyhash to the hasher result. The high bits select the initial bucket via `bucket_idx_from_hash(hash)`, while `dist_and_fingerprint_from_hash(hash)` initializes the probe metadata. `do_find()` probes forward, first with two unrolled checks and then a loop. It returns early when the sought probe distance becomes greater than the bucket's stored distance, because robin-hood ordering proves the key cannot appear later in that cluster.

Insertion grows the bucket array first when `is_full()` reaches the load threshold. `do_try_emplace()` and `emplace()` then probe until they find an equal key or a bucket whose stored distance is smaller than the candidate distance. New values are appended to `m_values`, and `place_and_shift_up()` swaps bucket metadata forward until an empty slot is reached. This preserves robin-hood ordering while keeping actual values dense and stable in a separate vector-like container.

Deletion uses `do_erase()`. It removes the bucket entry, backward-shifts following bucket metadata until reaching an empty slot or an entry at its home bucket, then updates `m_values`. If the erased value was not the last dense value, the last value is moved into the erased value slot and the corresponding bucket's `m_value_idx` is found and rewritten. This keeps `m_values` hole-free but means erase can move a different element and invalidate assumptions about element order.

Resizing uses `m_shifts` to represent bucket count as `2^(64 - m_shifts)`, starting at eight buckets. `reserve()` and `rehash()` compute the necessary shift from the requested capacity and max load factor, allocate a new bucket array, clear it, and rebuild bucket metadata from the dense values. `increase_size()` doubles bucket capacity by decrementing `m_shifts`.

## State and Persistence Behavior
The table's state is entirely in-memory: `m_values`, the allocated bucket metadata array, bucket count/capacity, max load factor, hasher, equality predicate, and shift count. The header has no disk, network, LMDB, or Ceph object persistence behavior.

The nonstandard `extract()` moves out the dense value container and empties the table's values without itself rebuilding buckets. `replace()` accepts a complete value container, reallocates bucket metadata if needed, rebuilds index state, and drops duplicate keys by replacing duplicates with the current back element before popping. These APIs are useful for bulk transfer or container-level persistence performed by callers, but this header does not serialize or encode anything itself.

Iteration order follows `m_values`, which is insertion order except when erase or duplicate-removal replacement moves the last value into an earlier slot. Bucket metadata is an implementation detail and should not be persisted across process, compiler, architecture, or library-version boundaries. The embedded wyhash implementation explicitly does not preserve endian-stable values.

## Dependencies and Integration Points
The header requires C++17 or newer and uses standard library facilities from `<array>`, `<cstdint>`, `<cstring>`, `<functional>`, `<initializer_list>`, `<iterator>`, `<limits>`, `<memory>`, `<stdexcept>`, `<string>`, `<string_view>`, `<tuple>`, `<type_traits>`, `<utility>`, and `<vector>`. It conditionally uses PMR memory resources and compiler intrinsics for 128-bit multiplication. If exceptions are disabled, lookup and capacity errors abort instead of throwing.

Within the POSIX RGW driver, `notify.h` includes this file and defines `Inotify::wd_callback_map_t` as `map<int, WatchRecord>` and `Inotify::wd_remove_map_t` as `map<std::string, int>`. `add_watch()` inserts both descriptor-to-record and path-to-descriptor entries, `ev_loop()` looks up watch records by inotify descriptor while holding `map_mutex`, and `remove_watch()` erases from both maps. `bucket_cache.h` owns the `Notify` instance, so these maps are part of POSIX bucket listing invalidation and notification plumbing rather than general Ceph storage state.

## Risks
Iterator and reference stability differ from `std::unordered_map`: values are dense, vector-backed by default, and insertions, rehashes, replacement, and erases can invalidate iterators/references. Erase also moves the last element into the erased slot, so code that depends on stable iteration order or stable addresses is unsafe.

The implementation assumes bucket types are trivially copyable/destructible and uses raw allocation, `memset`, and `memcpy` for bucket metadata. Any custom bucket type must preserve those properties and match the expected `m_dist_and_fingerprint`, `m_value_idx`, `dist_inc`, and `fingerprint_mask` interface.

Hash quality matters. Hashers without `is_avalanching` are mixed through wyhash, but transparent heterogeneous lookup requires both hash and equality types to expose `is_transparent`; mismatched transparent hash/equality behavior would cause missed lookups or duplicate keys.

The `std::erase_if` extension appears to return `map.size() - old_size`. Because erasing reduces size, successful removals underflow `size_t` instead of returning the number erased. This is a latent bug for any caller using the return value; no current POSIX RGW integration in this tree appears to call `std::erase_if` on `ankerl::unordered_dense`.

`replace()` duplicate detection uses `m_values[bucket.m_value_idx].first`, which is correct for map values but would be ill-formed for set values if instantiated in duplicate-detection code paths. Treat set `replace()` use as needing compile coverage before relying on it.

`notify.h` uses `insert()` rather than assignment when adding watches. If a duplicate path or descriptor is added, the map keeps the original entry and ignores the new value. That behavior comes from this container's unique-key insert semantics and is important for watch lifecycle correctness.

## Test Signals
Compile coverage should include the POSIX RGW notifier on Linux, because it instantiates `map<int, WatchRecord>` and `map<std::string, int>` with a move-only-ish `WatchRecord` shape and exercises C++17 header compatibility.

Container-level tests should cover insert/find/contains/erase, duplicate insert rejection, erase of first/middle/last dense values, reserve/rehash growth, copy/move construction and assignment, `operator[]`, `try_emplace`, `insert_or_assign`, `at()` error behavior with and without exceptions, and heterogeneous lookup when transparent hash/equality are supplied.

Notifier integration tests should add and remove watches repeatedly, verify both maps stay synchronized, and inject inotify create/delete/move and queue-overflow events. A duplicate `add_watch()` case is especially useful because the current use of `insert()` will not update an existing watch record.

Regression tests for this vendored file should check `std::erase_if`'s return value and any intended `set::replace()` use, because both are high-risk corners visible from source inspection.

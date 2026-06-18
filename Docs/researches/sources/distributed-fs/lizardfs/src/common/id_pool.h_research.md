# sources/distributed-fs/lizardfs/src/common/id_pool.h

Purpose: implements an optimized reusable ID allocator over a bounded numeric range.

Important APIs/types/functions: `detail::IdPoolBlock<ValueType,SizeType>` manages a bitset block with memory released when fully free or fully used. `IdPool<IDT>` exposes `acquire`, `release`, `markAsAcquired`, `checkIfAvailable`, `maxSize`, `size`, and static `nullId`.

Control flow: constructor reserves id `0`. `acquire` first consumes a small cache of released ids, then uses the first free block, lazily adding blocks up to max. `release` validates range, optionally stores ids in `cache_`, otherwise flips a bit in the block and updates the free-list. `markAsAcquired` forces an id unavailable, allocating blocks if needed.

State and persistence: in-memory unordered cache, vector of bit blocks, forward-list of free block indexes, used count, range limits. No persistence or synchronization.

Dependencies and integration: depends on `compact_vector` for compact bit storage. Used wherever metadata identifiers need fast allocation/recycling.

Risks: many invariants rely on block/free-list bookkeeping; corruption can throw runtime errors. Cache path stores released ids as `size_t`, so duplicate release detection checks cache and block. No thread safety. `used_count_` is adjusted for reserved id during construction and normal IDs thereafter, so callers should interpret `size()` as acquired non-null IDs.

Test signals: `id_pool_unittest.cc` covers full acquisition, release/reacquire, null handling, uniqueness, and `markAsAcquired`.

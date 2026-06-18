# Research: subset-b-008668

This grouped report covers RocksDB memtable representation, skiplist, write-buffer accounting, WBWI read-only memtable, and microbench build files. Each section preserves the source path and is intended to be split into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/alloc_tracker.cc -->
# sources/storage-engines/rocksdb/memtable/alloc_tracker.cc

## Purpose
`alloc_tracker.cc` implements `AllocTracker`, a small accounting adapter between allocator users and `WriteBufferManager`. It records bytes allocated by an arena-backed owner, reserves those bytes in the write-buffer manager, and later transitions them from active mutable memory to scheduled-for-free and finally freed memory.

## Important APIs and Functions
- `AllocTracker::AllocTracker(WriteBufferManager*)` stores the optional manager and initializes `bytes_allocated_`, `done_allocating_`, and `freed_`.
- `Allocate(size_t bytes)` is called when memory is allocated. If the manager is enabled or charging cache, it increments `bytes_allocated_` with relaxed atomics and calls `WriteBufferManager::ReserveMem`.
- `DoneAllocating()` marks the allocation owner as no longer mutable. It calls `ScheduleFreeMem(total_bytes)` exactly once, which reduces `memory_active_` in the manager while keeping total usage reserved.
- `FreeMem()` first ensures `DoneAllocating()` has happened, then calls `WriteBufferManager::FreeMem(total_bytes)` once. The destructor delegates to this method.

## Control Flow and State
The class is a lifecycle tracker. `Allocate()` may be called many times while a memtable/arena is active. `DoneAllocating()` is a one-way transition guarded by `done_allocating_`. `FreeMem()` is another one-way transition guarded by `freed_`, and it tolerates callers that forgot to call `DoneAllocating()`. `bytes_allocated_` is atomic, but the transition booleans are plain fields, so the lifecycle itself is expected to be externally serialized or owned by a single object.

## Dependencies and Integration Points
The implementation depends on `rocksdb/write_buffer_manager.h`, `memory/allocator.h`, and `memory/arena.h`. It is used by allocation-owning RocksDB components to keep global write-buffer pressure synchronized with arena memory. It directly drives `ReserveMem`, `ScheduleFreeMem`, and `FreeMem`, so its correctness affects flush pressure, stall decisions, and optional cache reservation charging.

## Risks and Test Signals
The main risk is lifecycle imbalance: missing `FreeMem()` would leak write-buffer accounting, while double free is prevented by `freed_`. If `WriteBufferManager` is disabled and not charging cache, the tracker asserts no bytes were recorded. The paired behavior is indirectly tested by write-buffer-manager tests that verify active/total memory transitions; there is no dedicated test in this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/alloc_tracker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/hash_linklist_rep.cc -->
# sources/storage-engines/rocksdb/memtable/hash_linklist_rep.cc

## Purpose
`hash_linklist_rep.cc` implements the `hash_linkedlist` memtable representation. It partitions memtable entries by a transformed user-key prefix, stores sparse buckets compactly as a single node or sorted linked list, and promotes dense buckets to per-bucket skiplists after a configurable threshold.

## Important APIs, Types, and Functions
- `BucketHeader` stores a bucket `next` pointer and relaxed `num_entries`; `next == this` marks a promoted skiplist bucket.
- `SkipListBucketHeader` embeds a `BucketHeader` plus `SkipList<const char*, KeyComparator&>`.
- `Node` stores an atomic `next_` pointer and inline `key[1]` payload.
- `HashLinkListRep` implements `Allocate`, `Insert`, `Contains`, `Get`, `GetIterator`, and `GetDynamicPrefixIterator`.
- Iterator variants are `FullListIterator` for total-order snapshots, `LinkListIterator` for a single linked bucket, `DynamicIterator` for prefix-seek-time bucket selection, and `EmptyIterator`.
- `HashLinkListRepFactory` registers options: `bucket_count`, `threshold`, `huge_page_size`, `logging_threshold`, and `log_when_flash`.

## Control Flow
`Insert()` hashes `Transform(ExtractUserKey(internal_key))` to select a bucket. Empty buckets store the node directly. A one-entry bucket is converted to a `BucketHeader` before inserting more nodes so readers never confuse a modified node with a header. Linked buckets are kept sorted by memtable key. Once `num_entries == threshold_use_skiplist_`, a new `SkipListBucketHeader` is allocated, all existing list entries plus the new node are inserted into the skiplist, and the bucket pointer is release-stored to the new header. Already-promoted buckets increment the count and insert into the skiplist.

`Get()` selects the prefix bucket, then either seeks the sorted linked list or the skiplist and calls the supplied callback until it stops. `GetIterator()` builds a new full `MemtableSkipList` containing all entries across all buckets, optionally recording bucket-size histogram logging. `GetDynamicPrefixIterator()` returns an iterator that chooses a bucket only when `Seek()` is called.

## State and Persistence Behavior
All data is in allocator-owned memory and lives for the memtable lifetime. Bucket array entries are atomics. Release/acquire stores and loads protect publication of nodes and headers, and old nodes/headers are never modified destructively during representation upgrades. There is no disk persistence; persistence happens later through memtable flush.

## Dependencies and Integration Points
The implementation depends on `db/memtable.h`, `memtable/skiplist.h`, `SliceTransform`, `GetSliceRangedNPHash`, `HistogramImpl`, and option registration. It integrates through `NewHashLinkListRepFactory`, which is selected by RocksDB options or the memtablerep benchmark. It requires a prefix extractor; without a valid transform, prefix hashing cannot work.

## Risks and Test Signals
The representation assumes single-threaded `Insert()`; `num_entries` increments are relaxed and not atomic RMW. Dynamic prefix iteration does not support total-order operations like `SeekToFirst`, `SeekToLast`, or reverse traversal for linked buckets. Full iteration is expensive because it materializes a new global skiplist. `ApproximateMemoryUsage()` returns zero because arena allocations are accounted elsewhere. Risks are indirectly covered by RocksDB memtable tests and benchmark coverage; this specific file has no listed dedicated unit test in the subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/hash_linklist_rep.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/hash_skiplist_rep.cc -->
# sources/storage-engines/rocksdb/memtable/hash_skiplist_rep.cc

## Purpose
`hash_skiplist_rep.cc` implements the `prefix_hash` memtable representation. It maps transformed user-key prefixes into hash buckets, each lazily initialized as a regular `SkipList<const char*, KeyComparator&>`.

## Important APIs, Types, and Functions
- `HashSkipListRep` implements the `MemTableRep` interface for insert, point/prefix lookup, total iteration, and dynamic prefix iteration.
- `Bucket` is an alias for `SkipList<const char*, const MemTableRep::KeyComparator&>`.
- `GetHash()` uses `MurmurHash(prefix) % bucket_size_`.
- `GetInitializedBucket()` allocates a bucket skiplist from the memtable allocator and publishes it in `buckets_`.
- `Iterator` wraps a bucket or a materialized full-list skiplist. It may own the list when used for full iteration.
- `DynamicIterator` recomputes the prefix bucket on `Seek()`.
- `HashSkipListRepFactory` registers `bucket_count`, `skiplist_height`, and `branching_factor`, with nickname `prefix_hash`.

## Control Flow
`Insert()` extracts the user key from the encoded memtable key, transforms it, lazily initializes the hashed bucket, and inserts the key into that bucket skiplist. `Contains()` performs the same bucket selection and delegates to `Bucket::Contains`. `Get()` uses the lookup key user prefix, seeks within the bucket by the full memtable key, and invokes the callback over matching entries until it returns false.

For total-order iteration, `GetIterator()` allocates a new arena and full skiplist, scans every non-null bucket from first to last, inserts all entries into the global list, and returns an owning iterator over that list. Dynamic prefix iteration avoids this cost but is only meaningful after seeking a specific prefix.

## State and Persistence Behavior
Buckets are atomic pointers stored in allocator memory. Bucket creation is published with a release store and read with acquire loads. There is no deletion of bucket skiplists during memtable lifetime. The file itself persists nothing; entries are in-memory memtable records that later flush through RocksDB.

## Dependencies and Integration Points
This file uses `memtable/skiplist.h`, `SliceTransform`, `MurmurHash`, option metadata, and `MemTableRepFactory`. It is selected through `NewHashSkipListRepFactory` or configuration strings. It integrates with `memtablerep_bench.cc`, which names it as `hashskiplist` or `prefix_hash`.

## Risks and Test Signals
`GetInitializedBucket()` is not protected by CAS, so concurrent first insertion into the same empty bucket could allocate and publish races unless higher-level insert serialization applies. `SeekForPrev()` in the bucket iterator asserts false, so reverse prefix iteration is unsupported. Full iteration has O(number of entries) rebuild cost and an extra arena. `ApproximateMemoryUsage()` returns zero because allocator-level accounting owns memory usage. Coverage is mostly through generic memtable tests and benchmark selection rather than a dedicated test file in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/hash_skiplist_rep.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/inlineskiplist.h -->
# sources/storage-engines/rocksdb/memtable/inlineskiplist.h

## Purpose
`inlineskiplist.h` defines `InlineSkipList<Comparator>`, RocksDB's memory-efficient skiplist optimized for memtable keys allocated through the skiplist itself. Compared with `SkipList<const char*>`, it stores key bytes inline with the node and places higher-level next pointers before the node object, reducing per-node pointer overhead and improving cache locality.

## Important APIs, Types, and Functions
- `AllocateKey(size_t)` allocates node plus inline key storage and returns the key payload address.
- `Insert`, `InsertConcurrently`, `InsertWithHint`, and `InsertWithHintConcurrently` link allocated keys into the list. The concurrent variants use CAS.
- `Splice` caches predecessor/successor brackets at each level for insertion hints and finger searches.
- `Node` stores `Atomic<Node*> next_[1]`; levels above zero are addressed with negative offsets before the node. `StashHeight` temporarily stores the randomly chosen height in `next_[0]` before insertion.
- `Iterator` supports forward/backward iteration, seek, seek-for-prev, random seek, and validation variants.
- `MultiGet()` performs batched sorted-key lookup using `FindGreaterOrEqualWithFinger`.
- `ApproximateNumEntries()` estimates range cardinality using higher skiplist levels.
- `TEST_Validate()` checks structural ordering across levels.

## Control Flow
Allocation chooses a random height, allocates aligned memory for extra next pointers, the node, and key bytes, and stashes the height. Insertion unstashes height, raises `max_height_` if needed, validates or recomputes the splice, then links the node level by level. Non-concurrent insertion uses release stores after no-barrier next initialization. Concurrent insertion uses CAS on predecessor next pointers and recomputes stale brackets after failed CAS.

Search starts at the current top height and descends while comparing decoded keys. Validation variants can detect out-of-order neighboring nodes and call a key validation callback. `MultiGet()` expects query keys sorted in non-decreasing comparator order; it reuses a stack-allocated `Splice` as a finger so each next search starts near the previous result.

## State and Persistence Behavior
Nodes are never removed until the allocator is destroyed. Node contents other than links are immutable after publication. `max_height_` is relaxed because stale values only affect efficiency. No persistent state exists in the file; it is an in-memory index over memtable records.

## Dependencies and Integration Points
The template depends on RocksDB `Allocator`, `Slice`, `Random`, atomic wrappers, `PREFETCH`, and sync points. `skiplistrep.cc` wraps it as the default `SkipListRep`. Tests in `inlineskiplist_test.cc` exercise basic operations, insertion hints, concurrent insertion, validation, and `MultiGet`.

## Risks and Test Signals
Correctness depends on comparator support for `DecodedType` and `decode_key`. Hint ownership matters: concurrent hint insertion requires no concurrent calls using the same hint, and heap-allocated hints returned by `AllocateSpliceOnHeap()` must be freed by the caller. `MultiGet()` requires sorted keys; unsorted batches could violate finger preconditions. The validation hooks expose corruption as `Status::Corruption`, while normal non-validation paths assert ordering in debug builds. Tests cover duplicate MultiGet key regression, concurrent MultiGet, and concurrent reads/inserts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/inlineskiplist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/inlineskiplist_test.cc -->
# sources/storage-engines/rocksdb/memtable/inlineskiplist_test.cc

## Purpose
`inlineskiplist_test.cc` is the dedicated unit and stress test suite for `InlineSkipList`. It validates empty-list behavior, ordered lookup, insertion hints, batched `MultiGet`, concurrent reads, concurrent inserts, and concurrent `MultiGet` visibility.

## Important APIs, Types, and Helpers
- `TestComparator` defines `DecodedType`, `decode_key`, and comparison overloads for encoded `uint64_t` keys.
- `InlineSkipTest` provides `Insert`, `InsertWithHint`, and `Validate` helpers that compare list contents against a `std::set` model and call `TEST_Validate`.
- `ConcurrentTest` builds composite keys `<key, generation, hash>` and validates readers never miss keys visible at iterator construction.
- `ConcurrentMultiGetState` coordinates multi-threaded insert-and-query testing with a shared ring of recently inserted keys.

## Control Flow
Basic tests build random or deterministic key sets, call `AllocateKey`, copy encoded keys into place, insert, and compare `Contains`, `Seek`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, forward iteration, and backward iteration against `std::set`.

Hint tests exercise sequential hints, many independent hints, random hint-locality patterns, and compatibility between hinted and unhinted inserts. MultiGet tests verify lower-bound behavior, exact matches, empty lists, single-key batches, randomized sorted batches, duplicate lookup keys with callbacks that walk forward, and concurrent read-after-write behavior.

Concurrency tests use `Env` background scheduling. Single-writer/read tests insert generations while a reader loops over seeks and next calls. Concurrent insert tests schedule multiple writers for distinct key groups, optionally using `InsertWithHintConcurrently`, and wait for all pending writers before advancing. The concurrent MultiGet test starts multiple threads with shuffled unique key chunks, inserts through `InsertConcurrently`, publishes keys into an atomic ring, then queries sorted/deduplicated batches.

## State and Persistence Behavior
The tests use `Arena` and `ConcurrentArena` to model allocator lifetime. State is entirely in memory. Atomic generation counters, quit flags, pending writer counters, and ring buffers coordinate test visibility and scheduling.

## Dependencies and Integration Points
The file includes `memtable/inlineskiplist.h`, `memory/concurrent_arena.h`, `rocksdb/env.h`, `test_util/testharness.h`, hashing, and random utilities. It is a strong signal for `skiplistrep.cc` because the production memtable rep delegates to `InlineSkipList`.

## Risks and Test Signals
The tests intentionally stress the tricky areas: splice hints, CAS insertion, height growth, duplicate MultiGet queries, and callback walks over multiple entries. Some randomized tests use time-derived seeds and report the seed with `SCOPED_TRACE`, which helps reproduce failures. Valgrind gating skips the heaviest concurrency tests unless full valgrind is requested.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/inlineskiplist_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/memtablerep_bench.cc -->
# sources/storage-engines/rocksdb/memtable/memtablerep_bench.cc

## Purpose
`memtablerep_bench.cc` is a gflags-driven microbenchmark for comparing RocksDB `MemTableRep` implementations under fill, point-read, scan, and mixed read/write workloads.

## Important APIs, Types, and Functions
- Flags select benchmark names, memtable representation, bucket counts, skiplist height/branching, hash linked-list thresholds, write buffer size, thread counts, operation counts, item size, prefix length, vector reserve count, and random seed.
- `RandomGenerator` provides deterministic reusable value bytes.
- `KeyGenerator` supports sequential, random, and unique-random write modes.
- `BenchmarkThread` is the base class for fill, concurrent fill, random read, sequential scan, concurrent random read, and concurrent scan workers.
- `Benchmark` runs workers, measures elapsed time with `StopWatchNano`, and prints throughput.
- `main()` creates the selected `MemTableRepFactory`, constructs an arena-backed memtable rep, and dispatches comma-separated benchmarks.

## Control Flow
When gflags is unavailable, the file builds a stub `main()` that asks the user to install gflags. Otherwise, `main()` parses flags, selects a memtable factory (`skiplist`, `vector`, `hashskiplist`/`prefix_hash`, `hashlinklist`/`hash_linkedlist`, or config-string factory), then iterates over benchmark names.

Fill workers allocate encoded memtable entries using `MemTableRep::Allocate`, encode a length-prefixed 16-byte internal key containing user key and incremented sequence, copy a value payload, and call `Insert`. Read workers build `LookupKey` objects and call `Get` with a callback that checks user-key equality. Sequential readers create an iterator and scan from first to last. Mixed read/write runs one writer while the remaining threads read until completion.

## State and Persistence Behavior
Benchmarks use an in-memory `Arena`, `WriteBufferManager`, and `MemTableRep`; there is no DB persistence. Each fill or mixed benchmark resets the memtable rep and sequence counter. Shared counters for bytes and hits are plain integers passed to threads, so metrics are approximate under concurrency.

## Dependencies and Integration Points
The benchmark exercises production memtable factories, `InternalKeyComparator`, `SliceTransform`, `WriteBufferManager`, port threads, system clock, and RocksDB config-string factory parsing. It is also connected to the microbench CMake file, which discovers and builds microbenchmark executables.

## Risks and Test Signals
This is benchmark code, not a correctness test. Concurrent byte counters and sequence increments are not synchronized, and the mixed workload intentionally focuses on throughput rather than exact metrics. Prefix hash reps require a fixed prefix extractor configured in this file. Useful signals are relative throughput, scan cost, and workload sensitivity across representations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/memtablerep_bench.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/skiplist.h -->
# sources/storage-engines/rocksdb/memtable/skiplist.h

## Purpose
`skiplist.h` defines the older generic `SkipList<Key, Comparator>` template derived from LevelDB. It is used where keys are stored separately from nodes, including bucket skiplists in hash-based memtable reps.

## Important APIs, Types, and Functions
- `SkipList(Comparator, Allocator*, max_height, branching_factor)` creates a head node, initializes relaxed `max_height_`, and allocates the predecessor cache `prev_`.
- `Insert(const Key&)` inserts a unique key with external synchronization.
- `Contains`, `Iterator::{Seek, SeekForPrev, Next, Prev, SeekToFirst, SeekToLast}` provide lookup and traversal.
- `ApproximateNumEntries(start_ikey, end_ikey)` estimates range size from sampled skiplist levels.
- `Node` stores `Key const key` and a flexible array of atomic next pointers.

## Control Flow
Search starts from the current top height and descends, reusing the last comparison result through `last_bigger`/`last_not_after`. `Insert()` has a fast path for sequential insertion using cached predecessors. If the cached predecessor does not bracket the new key, `FindLessThan()` recomputes all predecessors. Random height follows the configured branching factor, and raising `max_height_` uses relaxed storage because readers seeing either old or new head-level links remain correct. Links are initialized relaxed in the new node and published via release stores from predecessors.

## State and Persistence Behavior
Nodes are allocated from the provided allocator and never deleted individually. The skiplist only stores pointers and key copies/references in memory; it persists nothing. Reads can run concurrently with a single externally synchronized writer, provided the list outlives readers.

## Dependencies and Integration Points
The template depends on `Allocator`, RocksDB atomics, `Random`, and port utilities. `hash_skiplist_rep.cc` and promoted buckets in `hash_linklist_rep.cc` instantiate it for `const char*` memtable keys.

## Risks and Test Signals
Writes require external synchronization, unlike `InlineSkipList`'s CAS insertion path. Duplicate insertion is guarded by debug asserts. The visible `ApproximateNumEntries()` implementation calls `next->Key()`, but this `Node` type exposes the key as `key` and does not define `Key()`, making this path suspicious unless hidden compatibility exists elsewhere; consumers should verify compilation for instantiations using that method. `skiplist_test.cc` covers empty behavior, random insert/lookup, forward/backward iteration, and concurrent reader/single-writer visibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/skiplist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/skiplist_test.cc -->
# sources/storage-engines/rocksdb/memtable/skiplist_test.cc

## Purpose
`skiplist_test.cc` tests the generic `SkipList<Key, Comparator>` implementation using `uint64_t` keys. It validates core ordered-set behavior and the intended single-writer/concurrent-reader memory model.

## Important APIs, Types, and Helpers
- `TestComparator` compares `uint64_t` keys.
- `SkipTest` is the gtest fixture.
- `ConcurrentTest` builds composite `<key, generation, hash>` values, maintains atomic generation state, and validates readers against a snapshot.
- `TestState`, `ConcurrentReader`, and `RunConcurrent` coordinate background reader execution with foreground writes.

## Control Flow
`Empty` verifies an empty list does not contain arbitrary keys and that all iterator positioning APIs yield invalid iterators. `InsertAndLookup` inserts up to 2,000 random unique keys from a 5,000-key range into both the skiplist and a `std::set`, then compares `Contains`, seek-to-first/last, `Seek`, `SeekForPrev`, forward iteration, and backward iteration against the model.

The concurrency scaffold snapshots the current generation per logical key before reading. During iteration it validates every observed key hash and ensures the iterator never goes backward. For any gap between expected position and current key, it verifies missing generations were not present in the initial snapshot. `RunConcurrent` repeatedly starts a background reader, performs many writes on the foreground thread, sets a quit flag, and waits for the reader to finish.

## State and Persistence Behavior
All data is in an `Arena`; there is no persistence. Concurrency state is held in atomics and port mutex/condvar fields. The skiplist itself is intentionally not protected by the test mutex because the implementation is expected to allow lock-free readers with one writer.

## Dependencies and Integration Points
The test depends on `memtable/skiplist.h`, `memory/arena.h`, `rocksdb/env.h`, test harness, hash utilities, and random utilities. It provides regression coverage for the legacy skiplist used by hash memtable bucket implementations.

## Risks and Test Signals
The tests do not exercise `ApproximateNumEntries()` and do not cover multiple concurrent writers, which the implementation does not support. They do strongly exercise reader consistency under concurrent insertion and random seek/next mixes. Five `ConcurrentN` runs vary seeds to broaden interleavings.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/skiplist_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/skiplistrep.cc -->
# sources/storage-engines/rocksdb/memtable/skiplistrep.cc

## Purpose
`skiplistrep.cc` implements RocksDB's default skiplist-backed `MemTableRep` using `InlineSkipList<const MemTableRep::KeyComparator&>`. It adapts the low-level inline skiplist to the `MemTableRep` interface used by `MemTable`.

## Important APIs, Types, and Functions
- `SkipListRep` implements allocation, insertion, concurrent insertion, hinted insertion, point lookup, validation lookup, MultiGet, approximate range cardinality, random sampling, and iterator creation.
- `Iterator` wraps `InlineSkipList::Iterator` and supports validation variants.
- `LookaheadIterator` accelerates locality-heavy seeks by walking at most `lookahead_` steps from a remembered previous iterator position before falling back to a full seek.
- `SkipListFactory` registers the non-serialized `lookahead` option and includes it in the factory ID.

## Control Flow
`Allocate()` delegates to `skip_list_.AllocateKey` so node and key storage are packed by the underlying list. Insert functions cast the returned handle back to `char*` and call the corresponding `InlineSkipList` method. `Get()` creates a stack iterator, seeks to the lookup memtable key, and calls the callback until it stops. `GetAndValidate()` uses seek/next validation paths to detect out-of-order keys and callback validation errors. `MultiGet()` delegates to `InlineSkipList::MultiGet`.

`UniqueRandomSample()` chooses between linear reservoir-like sampling and repeated random seeks based on `target_sample_size > sqrt(num_entries)`. `GetIterator()` returns either a standard iterator or a lookahead iterator depending on the factory option.

## State and Persistence Behavior
All records live in the allocator backing the inline skiplist. `SkipListRep` stores comparator, optional prefix transform for lookahead behavior, and `lookahead_`. It persists nothing directly.

## Dependencies and Integration Points
The file depends on `db/memtable.h`, `memtable/inlineskiplist.h`, `rocksdb/memtablerep.h`, option metadata, and string utilities. It is created by `SkipListFactory::CreateMemTableRep` and is the baseline for memtable benchmarks and common RocksDB operation.

## Risks and Test Signals
Lookahead iterator correctness depends on user-key and prefix comparisons to avoid reusing a previous position across incompatible prefixes. Validation APIs are stronger than plain `Get()` and can surface corruption. Random sampling does not guarantee exact target sample size. Tests in `inlineskiplist_test.cc` cover the underlying structure extensively, while memtable integration tests elsewhere cover `MemTableRep` behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/skiplistrep.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/stl_wrappers.h -->
# sources/storage-engines/rocksdb/memtable/stl_wrappers.h

## Purpose
`stl_wrappers.h` provides a small adapter for using RocksDB memtable key comparators with STL containers and algorithms.

## Important APIs and Types
- `stl_wrappers::Base` stores a reference to `MemTableRep::KeyComparator`.
- `stl_wrappers::Compare` derives privately from `Base` and implements `bool operator()(const char* a, const char* b) const` as `compare_(a, b) < 0`.

## Control Flow
There is no complex control flow. `Compare` is constructed with a memtable comparator and can be passed to algorithms like `std::sort` to order encoded memtable keys consistently with RocksDB internal ordering.

## State and Persistence Behavior
The wrapper stores only a comparator reference. It does not own data and has no persistence.

## Dependencies and Integration Points
The header includes comparator, memtable rep, slice, and coding headers. In this subset, `vectorrep.cc` uses `stl_wrappers::Compare(compare_)` when lazily sorting its vector-backed bucket.

## Risks and Test Signals
Lifetime matters: the referenced comparator must outlive any STL comparator object using it. Ordering must be strict and consistent with the memtable's encoded key format. There is no dedicated test; coverage comes through vector memtable behavior and any STL sort/search users.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/stl_wrappers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/vectorrep.cc -->
# sources/storage-engines/rocksdb/memtable/vectorrep.cc

## Purpose
`vectorrep.cc` implements a vector-backed `MemTableRep` optimized for buffering writes and sorting lazily at read/iteration time. It is useful for workloads where append cost matters and sorted access can be deferred.

## Important APIs, Types, and Functions
- `VectorRep` implements `Insert`, `InsertConcurrently`, `Contains`, `MarkReadOnly`, `ApproximateMemoryUsage`, `BatchPostProcess`, `Get`, and `GetIterator`.
- `bucket_` is a shared vector of `const char*` memtable keys.
- `tl_writes_` stores per-thread vectors for concurrent insertion buffering.
- `Iterator` owns or shares a bucket snapshot and lazily sorts it with `stl_wrappers::Compare`.

## Control Flow
Single-threaded `Insert()` writes directly into `bucket_` under `rwlock_` and increments `bucket_size_`. `InsertConcurrently()` appends to a thread-local vector. `BatchPostProcess()` drains the calling thread's local vector into the shared bucket under write lock, updates size, deletes the local vector, and resets the thread-local pointer.

Reads take a read lock and either use the immutable shared bucket or copy the mutable bucket into a temporary vector. Iterators sort on first use. `Seek()` performs an `equal_range` binary search for the first entry not less than the encoded target. `Get()` seeks to the lookup memtable key and invokes the callback forward.

## State and Persistence Behavior
State is in memory only. `immutable_` controls whether readers may share and lazily sort the main bucket. `sorted_` records whether the shared immutable bucket has been sorted. Mutable reads copy the vector so they can sort without mutating active writer state.

## Dependencies and Integration Points
The implementation depends on `MemTableRep`, `Arena`, `ThreadLocalPtr`, `port::RWMutex`, `MutexLock`, option metadata, and `stl_wrappers::Compare`. `VectorRepFactory` registers the `count` reserve option and creates the representation.

## Risks and Test Signals
`Contains()` checks pointer equality with `std::find`, not comparator equality, so it only answers whether the exact key pointer exists. `SeekAndValidate()` returns `NotSupported` for non-empty memtables, and `SeekForPrev()` asserts false. Concurrent insertion requires callers to invoke `BatchPostProcess()` to publish thread-local writes. `ApproximateMemoryUsage()` counts vector pointer slots only, not key payload memory. Test signals are mostly generic memtable tests and benchmark behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/vectorrep.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/wbwi_memtable.cc -->
# sources/storage-engines/rocksdb/memtable/wbwi_memtable.cc

## Purpose
`wbwi_memtable.cc` implements the executable behavior of `WBWIMemTable`, a read-only memtable view over `WriteBatchWithIndex` content used when ingesting a transaction-like batch as an immutable memtable.

## Important APIs and Functions
- `WBWIMemTableIterator::WriteTypeToValueTypeMap` maps WBWI write record types to RocksDB internal value types.
- `WBWIMemTable::NewIterator(...)` constructs an arena-allocated `WBWIMemTableIterator` for flush or read paths.
- The private `NewIterator() const` creates a heap iterator for point lookups.
- `Get()` implements read lookup, merge handling, deletion handling, visibility callback checks, and unsupported type detection.
- `MultiGet()` loops over a `MultiGetRange` and delegates to `Get()` per key.

## Control Flow
Iterator creation asserts sequence numbers have been assigned and obtains a WBWI column-family iterator for `cf_id_`. `Get()` seeks the internal lookup key, then walks entries with the same user key. For visible entries, it records the output sequence, applies covering tombstone logic, and dispatches by value type: value returns through `HandleTypeValue`, deletions through `HandleTypeDeletion`, merge operands through `HandleTypeMerge`, and unsupported types produce corruption. If iteration ends while merge operands are accumulated, it returns `MergeInProgress`.

`MultiGet()` performs a straightforward per-key loop. When a final value is found, it pins the result, updates aggregate value size, marks the key done, and aborts remaining keys if the soft value-size limit is exceeded.

## State and Persistence Behavior
The class reads from an existing `WriteBatchWithIndex`; it does not mutate it. The assigned sequence range determines internal key ordering. It assumes the memtable is immutable and that no snapshot sequence lies inside the assigned sequence range.

## Dependencies and Integration Points
The implementation depends on `memtable/wbwi_memtable.h` and `db/memtable.h` helper routines for value, deletion, and merge handling. It integrates with transaction ingestion, flush iteration, and read-only memtable lookup paths.

## Risks and Test Signals
Several features are intentionally unsupported or asserted away: user-defined timestamps, blob index resolution, delete range, wide-column entity reads, and value preferred seqno. `MultiGet()` is functionally correct but not optimized because it creates point lookup iterators through `Get()`. No dedicated test is in this subset; correctness depends on WBWI/transaction ingestion tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/wbwi_memtable.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/wbwi_memtable.h -->
# sources/storage-engines/rocksdb/memtable/wbwi_memtable.h

## Purpose
`wbwi_memtable.h` declares `WBWIMemTable`, a `ReadOnlyMemTable` implementation backed by `WriteBatchWithIndex`, and `WBWIMemTableIterator`, which converts WBWI entries into internal-key iterator output with assigned sequence numbers.

## Important APIs, Types, and Functions
- `WBWIMemTable::SeqnoRange` stores lower and upper assigned sequence bounds.
- The constructor stores the shared WBWI, comparator, column family ID, immutable/mutable options, clock, and entry count including overwritten single deletes.
- `AssignSequenceNumbers()` sets the immutable sequence range exactly once.
- `NewIterator`, `Get`, and `MultiGet` implement the main read/flush interfaces.
- `WBWIMemTableIterator` implements `InternalIterator` over WBWI entries, including `Seek`, `SeekForPrev`, `Next`, `Prev`, `NextAndGetResult`, `key`, `value`, and `status`.

## Control Flow
WBWI entries do not contain sequence numbers, so `CurrentKeySeqno()` computes `lower_bound + update_count - 1`. `UpdateKey()` maps the WBWI write type to an internal `ValueType` and constructs an internal key. Flush iteration can emit overwritten `SingleDelete` records: when `for_flush` is true and the current WBWI entry reports an overwritten single delete, `Next()` first synthesizes a `kTypeSingleDeletion` at `lower_bound` before advancing the underlying iterator.

`Seek()` and `SeekForPrev()` translate an internal target to a user-key seek in WBWI, then step within equal user keys until the computed sequence number satisfies the internal target sequence constraint. Reverse and random access assert that overwritten-single-delete emission is not active because flush uses forward sequential iteration.

## State and Persistence Behavior
The memtable is read-only, references shared WBWI data, and tracks assigned sequence numbers plus minimum prepare-log reference. Many stats methods are placeholders returning zero or empty values. Persistence occurs when flush consumes the iterator and writes internal keys to SST files; this class only supplies the in-memory view.

## Dependencies and Integration Points
The header depends on `db/memtable.h` and `write_batch_with_index.h`. It integrates with transaction ingestion, read paths expecting `ReadOnlyMemTable`, flush job iteration, merge handling, and WAL retention through `GetMinLogContainingPrepSection`.

## Risks and Test Signals
The implementation requires WBWI overwrite mode. Unsupported areas are explicit: mempurge sampling, UDT timestamp stripping, range tombstones, newest UDT, and many size/stat estimates. Sequence assignment must happen before reads or iterator creation. The overwritten single-delete logic is subtle but important to prevent older values from incorrectly resurfacing after flush/compaction. Dedicated tests are not present in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/wbwi_memtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/write_buffer_manager.cc -->
# sources/storage-engines/rocksdb/memtable/write_buffer_manager.cc

## Purpose
`write_buffer_manager.cc` implements global write-buffer memory accounting, optional cache charging through dummy reservations, and write-stall queue coordination.

## Important APIs and Functions
- The constructor stores `buffer_size_`, derives `mutable_limit_` as seven-eighths of the hard limit, initializes atomic counters, and optionally creates a `CacheReservationManagerImpl<kWriteBuffer>`.
- `dummy_entries_in_cache_usage()` reports cache reservation bytes.
- `ReserveMem()` increments total and active memory, delegating cache-backed reservations to `ReserveMemWithCache()`.
- `ScheduleFreeMem()` subtracts from active mutable memory without reducing total memory.
- `FreeMem()` reduces total memory and calls `MaybeEndWriteStall()`.
- `BeginWriteStall()`, `MaybeEndWriteStall()`, and `RemoveDBFromQueue()` manage waiting DB stall interfaces.

## Control Flow
Without cache charging, `ReserveMem()` and `FreeMem()` update relaxed atomic counters directly when the manager is enabled. With cache charging, updates are serialized by `cache_res_mgr_mu_`, the local `memory_used_` counter is adjusted, and `UpdateCacheReservation()` is called; errors are deliberately permitted unchecked because the manager cannot yet prevent the underlying allocation.

Write stalls are represented by a queue of `StallInterface*`. `BeginWriteStall()` preallocates a list node outside the mutex, rechecks stall conditions under `mu_`, queues the waiter if still needed, and signals immediately if not queued. `MaybeEndWriteStall()` exits if stall thresholds still apply; otherwise it clears `stall_active_`, signals all queued waiters, and moves the list out for cleanup. `RemoveDBFromQueue()` removes a DB-specific waiter and signals it.

## State and Persistence Behavior
State is process memory only: buffer limits, active/used counters, cache reservation manager, stall flags, and waiter queue. No persisted data is written. The manager's state influences flushing, write stalls, and cache pressure.

## Dependencies and Integration Points
The file depends on `rocksdb/write_buffer_manager.h`, cache reservation roles, `DBImpl` stall interface declarations, `Status`, and coding utilities. `AllocTracker` and memtable allocation paths call into it. Tests in `write_buffer_manager_test.cc` verify flush thresholds and cache reservation behavior.

## Risks and Test Signals
Cache reservation failures are swallowed, so cache charging can underrepresent memory under strict capacity pressure, though tests cover degraded behavior. Atomic counters use relaxed ordering because they represent approximate pressure, while queue mutation is mutex-protected. Destructor debug asserts require the stall queue to be empty. The tests cover threshold transitions, delayed cache reservation shrinkage, no-limit cache charging, and full-cache cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/write_buffer_manager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/write_buffer_manager_test.cc -->
# sources/storage-engines/rocksdb/memtable/write_buffer_manager_test.cc

## Purpose
`write_buffer_manager_test.cc` validates `WriteBufferManager` memory-pressure and cache-charging behavior.

## Important Tests and Helpers
- `WriteBufferManagerTest.ShouldFlush` checks active and total memory threshold behavior for a 10 MiB manager.
- `ChargeWriteBufferTest.Basic` verifies cache dummy-entry reservation growth and delayed shrink with a 50 MiB write-buffer limit.
- `BasicWithNoBufferSizeLimit` verifies cache charging when write-buffer size is zero, meaning no flush pressure limit but cache cost still applies.
- `BasicWithCacheFull` uses strict LRU cache capacity to verify partial reservation failures and recovery after capacity increases.
- `kSizeDummyEntry` defines the expected cache reservation quantum of 256 KiB.

## Control Flow
The flush test reserves, schedules, frees, and resizes memory while asserting `ShouldFlush()` transitions. It distinguishes total memory over hard limit from active mutable memory over mutable limit, including cases where enough memory is already being flushed.

Cache tests create LRU caches, reserve memory in increments, and compare `dummy_entries_in_cache_usage()` plus pinned cache usage against expected reservation quanta and metadata overhead bounds. They then free memory in large and small chunks to verify delayed decrease behavior. The full-cache test intentionally exceeds strict cache capacity, observes partial reservation, frees memory, increases capacity, and verifies subsequent reservations can fully succeed.

## State and Persistence Behavior
All state is test-local memory. Cache pinned usage reflects dummy write-buffer reservations and is expected to return to zero after manager destruction in the basic cache test.

## Dependencies and Integration Points
The file includes `rocksdb/write_buffer_manager.h`, `rocksdb/advanced_cache.h`, and the RocksDB test harness. It directly exercises public manager APIs and indirect `CacheReservationManager` behavior via cache usage observations.

## Risks and Test Signals
The tests provide strong coverage for accounting thresholds and cache charging but do not cover write-stall queue behavior. Assertions include metadata overhead tolerances because cache bookkeeping adds implementation-dependent bytes. The strict-capacity case documents that reservation failure is tolerated and later corrected as memory is freed or cache capacity increases.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memtable/write_buffer_manager_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/microbench/CMakeLists.txt -->
# sources/storage-engines/rocksdb/microbench/CMakeLists.txt

## Purpose
`microbench/CMakeLists.txt` defines CMake build rules for RocksDB microbenchmark executables.

## Important Commands
- `find_package(benchmark REQUIRED)` locates Google Benchmark.
- `find_package(Threads REQUIRED)` locates thread support.
- `file(GLOB_RECURSE ALL_BENCH_CPP *.cc)` discovers benchmark source files recursively under `microbench`.
- The `foreach` loop derives each executable target name from the source basename.
- Each target links `benchmark::benchmark`, `Threads::Threads`, `${ROCKSDB_LIB}`, and `${THIRDPARTY_LIBS}`.
- `add_custom_target(microbench DEPENDS ${ALL_BENCH_TARGETS})` creates an aggregate target.

## Control Flow and State
CMake configuration discovers all `.cc` files at configure time, creates one executable per file, appends each target to `ALL_BENCH_TARGETS`, and creates a single aggregate target. There is no runtime state.

## Dependencies and Integration Points
This file depends on Google Benchmark, CMake thread discovery, the RocksDB library target variable, and third-party library variables defined by the parent build. It is a build-system integration point for microbenchmark sources, separate from the gflags-based `memtablerep_bench.cc` in the memtable folder.

## Risks and Test Signals
`GLOB_RECURSE` means newly added benchmark files may require rerunning CMake configure before targets appear, depending on generator behavior. Target names are derived from basenames, so duplicate filenames in different subdirectories would collide. The aggregate `microbench` target provides a quick build signal that all discovered microbenchmarks compile and link.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/microbench/CMakeLists.txt -->

# Research Group subset-b-008527

Grouped research for Pebble internal cache, compaction, compression, CRC, datadriven testing, and delete pacing files. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/cache_test.go -->
# sources/storage-engines/pebble/internal/cache/cache_test.go

## Purpose
This file tests Pebble's sharded block cache through the public `Cache` and `Handle` APIs. It validates CLOCK-Pro behavior against reference data, file/handle namespacing, explicit deletion and file eviction, reservation accounting, zero-sized cache behavior, concurrent replacement of existing keys, and lookup benchmark behavior.

## Important APIs, Types, And Functions
`TestCache` replays `testdata/cache` and compares expected hit/miss decisions. `setTestValue` allocates `Value`s, copies bytes, inserts with `Handle.Set`, and releases the caller ref. Other tests exercise `Peek`, `Get`, `Delete`, `EvictFile`, `NewHandle`, `Reserve`, `Size`, and `Unref`. `BenchmarkCacheGet` fills a large cache and runs parallel randomized `Get`s across levels and categories.

## Control Flow
Tests create one-shard or multi-shard caches, install small values, then force eviction or namespace separation. `TestCachePeek` first warms half the entries through `Get`, peeks the other half, inserts more data, and expects the `Get`-touched entries to survive. `TestReserve` shrinks effective capacity with a release callback, checks evictions, releases the reservation, and checks future insertions.

## State And Persistence Behavior
The tests cover in-memory cache state only. They assert size counters, per-handle key namespaces, and that caller references are released after cache insertion. No persistent files are written except the static reference trace read from `testdata/cache`.

## Dependencies And Integration Points
The suite uses `base.DiskFileNum`, `base.Level`, cache `Category` metrics categories, `require`, and Go concurrency primitives. It indirectly validates `clockpro.go`, `entry.go`, `value.go`, and reference-counting implementations.

## Risks And Edge Cases
Key risks are reference leaks, accidental access-bit updates from `Peek`, deletion of missing keys, eviction across handles, reservation double-release, zero target size, and races replacing an existing key. The stress test is intentionally narrow: it targets concurrent `Set` on existing entries, not all concurrent eviction/read paths.

## Test Signals
Strong signals are exact hit/miss trace conformance, expected `Size()` values after mutation, preserved h2 data after h1 file eviction, a panic string for double reservation release, and no race/panic during repeated concurrent replacement.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/clockpro.go -->
# sources/storage-engines/pebble/internal/cache/clockpro.go

## Purpose
This file implements the per-shard CLOCK-Pro block cache algorithm. It stores blocks by `(handleID, fileNum, offset)`, keeps per-file linked lists for efficient whole-file eviction, maintains hot/cold/test lists with three clock hands, accounts cache hits/misses by level and category, and integrates read-miss de-duplication through `readShard`.

## Important APIs, Types, And Functions
`key` identifies cache blocks and computes shard indexes with Fibonacci hashing. `shard` owns counters, maps, hands, sizes, counts, reservation state, and a `readShard`. Public shard methods include `init`, `get`, `getWithReadEntry`, `set`, `delete`, `evictFile`, `Free`, `Reserve`, `Size`, and `targetSize`. Internal mutation helpers include `metaAdd`, `metaDel`, `metaCheck`, `metaEvict`, `evict`, `runHandCold`, `runHandHot`, and `runHandTest`.

## Control Flow
Reads acquire the shard read lock, find an entry in `blocks`, acquire its `Value`, and mark it referenced unless `peekOnly` is true. Misses increment counters and optionally obtain a `readEntry`. `set` either inserts a new cold entry, replaces a resident hot/cold entry, or promotes a test entry to hot while increasing `coldTarget`. Eviction runs `runHandCold` until resident hot+cold bytes fit the target, with hot and test hands adjusting classification and `coldTarget`.

## State And Persistence Behavior
All state is volatile. Resident values are reference counted and manually allocated elsewhere. `blocks` maps block keys to entries; `files` maps file keys to circular file-link lists; `entries` is only present when Go allocation needs GC visibility. `sizeHot`, `sizeCold`, `sizeTest` and count mirrors are correctness-critical and checked by invariant code.

## Dependencies And Integration Points
The shard is used by `Cache` and `Handle` in `cache.go`, `read_shard.go` for miss coordination, `entry.go` for linked-list nodes, `value.go` for reference-counted buffers, `block_map.go` for Swiss-map storage, and `metrics.go` for counter aggregation.

## Risks And Edge Cases
Important risks are corrupted circular lists, stale hands pointing at freed entries, negative size/count accounting, oversized entries, reservations exceeding maximum size, nil values in test entries, and expensive file eviction under a shard lock. `evictFileRun` deliberately evicts only a few entries per mutex acquisition to reduce latency. The TODO on cold-entry replacement notes an algorithmic ambiguity.

## Test Signals
`cache_test.go` checks behavior externally, `clockpro_test.go` covers `Reserve`/`coldTarget`, and invariant builds use `metaCheck` to find entries remaining in maps or lists after deletion. Hit/miss metrics are indirectly exercised by `Get`/`Peek`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/clockpro.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/clockpro_normal.go -->
# sources/storage-engines/pebble/internal/cache/clockpro_normal.go

## Purpose
This build-tagged file supplies the normal, non-tracing implementation of `(*Cache).trace`.

## Important APIs, Types, And Functions
The only API is `func (c *Cache) trace(_ string, _ int64) {}` under `//go:build !tracing`.

## Control Flow
Calls compiled against `Cache.trace` become no-ops in ordinary builds. This keeps call sites shared with tracing builds without allocating or recording stack traces.

## State And Persistence Behavior
The file has no state and no persistence behavior. It intentionally does not mutate cache state.

## Dependencies And Integration Points
It integrates with tracing call sites in cache reference management and with `clockpro_tracing.go`, which provides the alternate build implementation.

## Risks And Edge Cases
The main risk is diagnostic: reference-count or cache lifetime bugs have less forensic data without the `tracing` build tag. Runtime behavior should otherwise be unchanged.

## Test Signals
There are no direct tests for this no-op implementation. Coverage is compile-time selection plus the normal cache test suite running without tracing.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/clockpro_normal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/clockpro_test.go -->
# sources/storage-engines/pebble/internal/cache/clockpro_test.go

## Purpose
This file tests one targeted CLOCK-Pro reservation regression: `Reserve` must clamp `coldTarget` when effective capacity shrinks, otherwise eviction can over-drain the cache.

## Important APIs, Types, And Functions
`TestReserveColdTarget` creates a one-shard cache, many handles, inserts one-byte values through `setTestValue`, calls `Cache.Reserve`, and checks `Cache.Size`.

## Control Flow
The test inserts 50 one-byte entries into a 100-byte cache, verifies size 50, reserves 51 bytes, and expects eviction down to 48 bytes rather than an empty cache. The scenario depends on shard-level CLOCK-Pro size/target logic.

## State And Persistence Behavior
Only in-memory cache state is affected. Handles are closed and the cache is unreferenced with defers.

## Dependencies And Integration Points
It uses the helper from `cache_test.go`, `NewWithShards`, `Handle`, and `require`. It specifically validates `shard.Reserve`, `targetSize`, `evict`, and `coldTarget` adjustment in `clockpro.go`.

## Risks And Edge Cases
The test protects an off-by-one/over-eviction path when reservation makes target capacity smaller than the previous `coldTarget`. It does not validate multi-shard distribution or release behavior, which are covered in `cache_test.go`.

## Test Signals
The signal is exact cache size before and after reservation. A result of zero would identify the historical bug called out in the comments.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/clockpro_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/clockpro_tracing.go -->
# sources/storage-engines/pebble/internal/cache/clockpro_tracing.go

## Purpose
This build-tagged file provides cache-level trace recording when Pebble is built with `tracing`.

## Important APIs, Types, And Functions
`func (c *Cache) trace(msg string, refs int64)` formats a message with the reference count and `debug.Stack`, then appends it to `c.tr.msgs` under `c.tr`'s mutex.

## Control Flow
Trace call sites invoke this method to capture stack-local history. The method serializes updates so multiple goroutines may record traces safely.

## State And Persistence Behavior
The only state is the in-memory trace slice on `Cache`. There is no persistence, and trace accumulation may increase memory use in diagnostic builds.

## Dependencies And Integration Points
It depends on `fmt` and `runtime/debug` and pairs with `clockpro_normal.go`. It complements `refcnt_tracing.go`, which traces per-value reference operations.

## Risks And Edge Cases
The implementation can be expensive because every trace captures a stack and appends a string. It is correctly restricted to tracing builds, but unbounded trace growth can matter during long diagnostic runs.

## Test Signals
No direct tests exist in this subset. Compile-time build tags and manual tracing/debug runs are the expected validation mechanism.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/clockpro_tracing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/entry.go -->
# sources/storage-engines/pebble/internal/cache/entry.go

## Purpose
This file defines cache entry metadata, linked-list manipulation, value reference ownership, and the allocator used for CLOCK-Pro entries. Entries are the nodes stored in shard `blocks`/`files` maps and threaded through the hot/cold/test and per-file circular lists.

## Important APIs, Types, And Functions
`entryType` enumerates `etTest`, `etCold`, and `etHot`. `entry` holds `key`, `val`, block/file links, size, type, and `referenced`. `newEntry`, `free`, `next`, `prev`, `link`, `unlink`, `linkFile`, `unlinkFile`, `setValue`, and `acquireValue` manipulate node state. Allocation helpers include `entryAllocNew`, `entryAllocFree`, `entryAllocPool`, `entryAllocCache`, and its allocation/free methods.

## Control Flow
New entries start cold and self-linked in both circular lists. `link`/`unlink` maintain the global CLOCK-Pro list, while `linkFile`/`unlinkFile` maintain the per-file list. `setValue` acquires the new value before publishing it and releases the old value afterward. Allocation normally uses pooled manual memory, but invariant/finalizer or race configurations switch to Go allocation.

## State And Persistence Behavior
Entry state is volatile but memory-safety-critical. The entry holds a cache reference on `Value` and must clear it before freeing. Finalizer builds poison failures by checking that freed entries are zeroed. No disk persistence exists.

## Dependencies And Integration Points
The file depends on `manual`, `buildtags`, `invariants`, `sync.Pool`, atomics, and `unsafe`. It is tightly integrated with `clockpro.go` list operations and `value.go` allocation policy.

## Risks And Edge Cases
Risks include storing Go pointers in manually allocated memory, leaking values when replacing entries, double-free or non-zero entry reuse, and list corruption. The code carefully aligns allocation policy with whether values are Go allocated so the GC can see references when necessary.

## Test Signals
Cache tests exercise entry replacement, deletion, file eviction, and stress replacement. Invariant/finalizer builds add leak/use-after-free detection beyond ordinary tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/entry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/metrics.go -->
# sources/storage-engines/pebble/internal/cache/metrics.go

## Purpose
This file defines cache hit/miss dimensionality and exposes aggregate cache metrics, including lifetime and recent-window hit/miss counters.

## Important APIs, Types, And Functions
`NumLevels`, `Levels`, and `levelIndex` map unknown plus L0-L6 into metrics indexes. `Category` enumerates background, SSTable data, SSTable value, blob value, filter, and index accesses. `Metrics` reports `HitsAndMisses`, byte `Size`, object `Count`, and two `Recent` windows. `HitsAndMisses` supports `Get`, `Hits`, `Misses`, aggregate by all, level, category, and `ToRecent`. `Cache.Metrics` and `hitsAndMisses` read shard counters.

## Control Flow
Cache operations increment atomic per-shard counters. `Metrics` snapshots counters, locks each shard briefly to read block count and hot+cold size, then asks the metrics window for ten-minute and one-hour baselines and subtracts those from current totals.

## State And Persistence Behavior
Metrics are in-memory counters only. They persist for the lifetime of a `Cache` object and reset when a cache is recreated. Recent windows depend on `c.metricsWindow`, defined outside this file.

## Dependencies And Integration Points
The file uses `base.Level`, Go `iter.Seq`, and `crtime.Mono`. It integrates with `clockpro.go` counters, `cache.go` metrics window state, and external observability code.

## Risks And Edge Cases
The level/category indexes must stay aligned with all cache call sites. `CategoryHidden` is defined in `cache.go` and intentionally skips counter updates. Recent calculations assume monotonic current counters and may be misleading if baselines are newer than current snapshots due to misuse.

## Test Signals
The subset does not include metrics-specific tests. Indirect signals come from cache operations using valid level/category combinations and benchmarks randomizing through the index ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/read_shard.go -->
# sources/storage-engines/pebble/internal/cache/read_shard.go

## Purpose
This file coordinates concurrent cache misses for the same block. It ensures that only one goroutine at a time reads a missing block, while waiters either consume the successfully read value or receive a turn after an error.

## Important APIs, Types, And Functions
`readShard` owns a Swiss map from cache `key` to `*readEntry` and a pointer to the parent shard. `acquireReadEntry` creates or refs an entry. `readEntry` stores the pending value, `isReading`, lazy waiter channel, accumulated `errorDuration`, read start time, and refcount. `waitForReadPermissionOrHandle`, `unrefAndTryRemoveFromMap`, `setReadValue`, and `setReadError` implement the state machine. `ReadHandle` exposes `Valid`, `SetReadValue`, and `SetReadError`.

## Control Flow
On miss, callers acquire a `readEntry`. The first caller sets `isReading` and returns a valid read handle. Concurrent callers wait on a lazily allocated channel or context cancellation. Success stores a retained value, closes the channel to wake all waiters, inserts into the cache with `markAccessed` if there were concurrent waiters, and unreferences the entry. Failure clears `isReading`, sends one token to let a waiter retry, records duration, and unreferences.

## State And Persistence Behavior
State is volatile and separate from resident cache entries. `readEntry` may retain a value until all waiters release. Entries are removed from `readMap` when their refcount reaches zero and then returned to a pool.

## Dependencies And Integration Points
It integrates with `shard.getWithReadEntry`, `Handle.GetWithReadHandle`, `Value` refs, the parent shard's `set`, context cancellation, and `swiss.Map`.

## Risks And Edge Cases
Risks include leaked read entries when callers fail to call `SetReadValue`/`SetReadError`, context cancellation causing wasted waiting, channel state races, and reference-count imbalance. The contract explicitly permits waiting on a shared load semaphore before doing the read.

## Test Signals
`read_shard_test.go` uses datadriven and randomized concurrent tests to validate turn taking, map cleanup, success fanout, error handoff, cancellation, and cache insertion after successful reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/read_shard.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/read_shard_test.go -->
# sources/storage-engines/pebble/internal/cache/read_shard_test.go

## Purpose
This file tests read-miss coordination, including deterministic state transitions and randomized concurrent readers for many blocks and handles.

## Important APIs, Types, And Functions
`testReader` wraps async `getWithReadEntry` and `waitForReadPermissionOrHandle`. Helpers include `newTestReader`, `getAsync`, `waitUntilFinishedWait`, `setReadValue`, and `setError`. `TestReadShard` runs `testdata/read_shard` commands. `testSyncReaders` and `TestReadShardConcurrent` run concurrent `Handle.GetWithReadHandle` calls.

## Control Flow
The datadriven test initializes a shard, starts named readers with optional canceled contexts, waits for each to either receive a value, error, or turn to read, injects success/error results, and prints `readMap` length or resident shard entries. The randomized test creates 50 block targets with five readers each; one reader per block may error, while others either publish or consume the expected value.

## State And Persistence Behavior
Only in-memory shard/read-entry state is used. The test verifies `readMap` cleanup and cache insertion state after transitions.

## Dependencies And Integration Points
It depends on `datadriven`, `testing/synctest`, `context`, `crypto/rand`, `testify/require`, the public `Handle.GetWithReadHandle` API, and internal `readEntry` APIs.

## Risks And Edge Cases
The tests intentionally cover canceled contexts, handoff after read errors, concurrent waiters, and ensuring values are available even if not yet in the resident block cache. Randomized coverage can miss some interleavings, but deterministic datadriven cases pin the state machine.

## Test Signals
Signals include map length returning to zero, expected printed shard entries, no unexpected errors in concurrent readers, and equality of every returned value to the per-block payload.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/read_shard_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/refcnt_normal.go -->
# sources/storage-engines/pebble/internal/cache/refcnt_normal.go

## Purpose
This file implements the normal, non-tracing reference count used by cache `Value`s.

## Important APIs, Types, And Functions
`refcnt` wraps `atomic.Int32`. `init`, `refs`, `acquire`, and `release` manage counts. `trace` and `traces` are no-ops under `//go:build !tracing`.

## Control Flow
`init` stores an initial count. `acquire` atomically increments and panics if the new count is `<= 1`, catching acquisition after free or uninitialized use. `release` decrements, panics on negative counts, and returns true when the count reaches zero.

## State And Persistence Behavior
The only state is an in-memory atomic integer embedded in a `Value`. There is no persistence.

## Dependencies And Integration Points
It is used by `value.go`, `entry.go`, and cache insertion/acquisition paths. Panic values use `redact.Safe` and `fmt`.

## Risks And Edge Cases
Reference count errors are fatal because they imply use-after-free, double release, or ownership bugs in manual memory. The normal build has no historical trace for debugging; tracing builds provide that.

## Test Signals
Cache tests exercise ordinary acquire/release flows. Invariant and tracing builds improve diagnosis, but this file has no direct unit test.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/refcnt_normal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/refcnt_tracing.go -->
# sources/storage-engines/pebble/internal/cache/refcnt_tracing.go

## Purpose
This file implements the tracing build variant of cache value reference counting, retaining stack traces for every reference operation.

## Important APIs, Types, And Functions
`refcnt` contains `atomic.Int32`, a mutex, and `msgs`. `init`, `refs`, `acquire`, `release`, `trace`, and `traces` mirror the normal API while recording stack-bearing messages.

## Control Flow
Initialization stores the count and traces `"init"`. `acquire` increments, validates the new count, and traces `"acquire"`. `release` decrements, validates non-negative counts, traces `"release"`, and returns whether the count reached zero. `traces` joins all recorded messages under lock.

## State And Persistence Behavior
State is in-memory per value. Trace messages can grow with reference churn and are used for diagnostics in finalizer/leak reports.

## Dependencies And Integration Points
It depends on `runtime/debug`, `strings`, `sync`, `atomic`, and `errors`. It integrates with `Value` finalizers and `entry` value ownership.

## Risks And Edge Cases
Tracing materially increases allocation, locking, and stack-capture cost. It is restricted by build tag for debugging. It still enforces the same correctness checks as the normal refcount.

## Test Signals
There are no direct tests here. Its signal is build compatibility and richer error output when cache reference bugs are reproduced under `tracing`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/refcnt_tracing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/value.go -->
# sources/storage-engines/pebble/internal/cache/value.go

## Purpose
This file defines `Value`, the immutable reference-counted buffer stored in the block cache, and its manual/Go allocation policy.

## Important APIs, Types, And Functions
`ValueMetadataSize` reserves metadata bytes for manual allocations. `Value` contains `buf` and `refcnt`. `Alloc`, `free`, `RawBuffer`, `Truncate`, `refs`, `acquire`, `Release`, and `Free` implement ownership and access. `valueEntryCanBeGoAllocated` and `valueEntryGoAllocated` control allocation strategy.

## Control Flow
`Alloc(0)` returns nil. Nonzero allocations either allocate a Go `Value` with manually allocated backing bytes or allocate metadata and payload in one manual block. New values start with refcount 1. Cache insertion acquires another reference through entries. `Release` frees when the count reaches zero; `Free` asserts the value has not been added to the cache before releasing.

## State And Persistence Behavior
Values are in-memory only. In invariant builds, `free` poisons bytes with `0xff` and finalizers detect leaked buffers. Manual allocations use `manual.BlockCacheData`.

## Dependencies And Integration Points
The file depends on `manual`, `buildtags`, `invariants`, `refcnt`, and `entry.go`. It is the buffer type returned by `Handle.Get`, `Peek`, and read-shard miss coordination.

## Risks And Edge Cases
Risks are leaks when callers forget `Release`/`Free`, mutation after cache insertion, truncating after publication, freeing cached values, and GC invisibility with cgo/manual memory. The allocation policy ensures Go-visible references when necessary.

## Test Signals
Cache tests repeatedly allocate, set, release, evict, and free values. Finalizer and tracing builds provide stronger leak/use-after-free detection than ordinary unit tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/value.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/iterator.go -->
# sources/storage-engines/pebble/internal/compact/iterator.go

## Purpose
This file implements `compact.Iter`, the forward-only iterator that transforms merged LSM input streams into compaction output keys. It collapses point versions within snapshot stripes, handles MERGE semantics, elides point/range tombstones when safe, interleaves range deletions and range keys, tracks snapshot-pinned output, and surfaces metadata for value separation.

## Important APIs, Types, And Functions
`Iter` owns the wrapped iterator, interleaving range-del/range-key iterators, tombstone/range-key compactors, buffers, snapshot stripe state, last range tombstone span, frontiers, and stats. `IterConfig` provides comparer, merge operator, snapshots, tombstone elision policy, bottommost-layer flag, and anomaly callbacks. Public methods include `NewIter`, `Frontiers`, `SnapshotPinned`, `ForceObsoleteDueToRangeDel`, `Stats`, `GetCurrentMeta`, `First`, `Next`, `Span`, `Error`, and `Close`. Core helpers include `nextInStripe`, `setNext`, `mergeNext`, `singleDeleteNext`, `skipDueToSingleDeleteElision`, `deleteSizedNext`, `saveKey`, `saveValue`, and `tombstoneCovers`.

## Control Flow
`NewIter` interleaves point keys with range deletions and range keys, initializes compactors and frontiers, and wraps iterators for invariant invalidation. `First` positions the input and calls `Next`. `Next` loops over candidates, advances frontiers, processes range spans through span compactors, skips keys visibly covered by range deletes, elides deletions in the bottom stripe when lower levels do not overlap, collapses SET/SETWITHDEL records, merges MERGE operands through the configured merger, applies SINGLEDEL rules, and validates DELSIZED tombstone sizes.

## State And Persistence Behavior
The iterator itself is transient, but its transformations determine durable SST contents. It may rewrite sequence numbers to zero for bottommost snapshot stripes, convert MERGE+SET to SET, transform MERGE+DEL to SETWITHDEL, convert inaccurate DELSIZED to DEL, and mark values as snapshot-pinned for output table properties.

## Dependencies And Integration Points
It depends on `base`, `keyspan`, `rangekey`, `invalidating`, tombstone elision/span compaction helpers, and `Frontiers`. It is consumed by `Runner` and upstream Pebble compaction code that writes output tables and stats.

## Risks And Edge Cases
Risks are severe: snapshot visibility, range-delete coverage, merge barriers, SINGLEDEL determinism, DELSIZED accounting, blob/lazy value cloning, key/value lifetime, and range span stability. Comments note a subtle range span stability violation and a TODO around snapshot-pinned semantics.

## Test Signals
`iterator_test.go` drives datadriven traces for ordinary collapse, SETWITHDEL, DELSIZED, range tombstones, range keys, snapshots, tombstone elision, bottommost sequence zeroing, blob handles, and anomaly callback output.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/iterator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/iterator_test.go -->
# sources/storage-engines/pebble/internal/compact/iterator_test.go

## Purpose
This file provides datadriven coverage for `compact.Iter`, including point-key collapse, snapshots, merges, range tombstones, range keys, bottommost compaction, blob references, SETWITHDEL, DELSIZED, and single-delete anomaly callbacks.

## Important APIs, Types, And Functions
`debugMerger` implements `base.ValueMerger`. `TestCompactionIter` parses test KVs/spans, configures `IterConfig`, and prints iterator outputs. `mockBlobValueFetcher`, `decodeBlobReference`, `encodeRemainingHandle`, and `makeInputIters` support lazy blob values and fake iterators.

## Control Flow
Datadriven `define` commands parse point KVs and spans, fragment range deletions, and store input slices. `iter` commands parse snapshot and option arguments, create a new compaction iterator, run `first`/`next` steps from input, print keys, values, spans, pinned/force-obsolete flags, missized counts, and callback side effects.

## State And Persistence Behavior
The tests do not write persistent DB state. They model compaction input streams in memory and validate the exact transformed stream that would be persisted by the runner.

## Dependencies And Integration Points
The file uses `datadriven`, `sstable.ParseTestKVsAndSpans`, `keyspan.Fragmenter`, `rangekey`, fake internal iterators, `valblk` handle encoding, and the compaction iterator API.

## Risks And Edge Cases
The tests are high-value because iterator behavior is easy to regress with small algorithm changes. Remaining risk is that datadriven fixtures must encode every important sequence; randomized stress is not present here.

## Test Signals
Exact textual output from `testdata/iter`, `iter_set_with_del`, and `iter_delete_sized` is the primary signal. Callback summaries catch ineffectual or nondeterministic single deletes and missized deletes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/iterator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/run.go -->
# sources/storage-engines/pebble/internal/compact/run.go

## Purpose
This file implements `Runner`, the data-writing half of compaction. It consumes `compact.Iter`, writes output SSTables and optional blob files, enforces output table splitting constraints, records pinned/missized statistics, and returns metadata required for version edits and cleanup.

## Important APIs, Types, And Functions
`Result`, `OutputTable`, `OutputBlob`, and `Stats` describe compaction output and errors. `RunnerConfig` supplies bounds, L0 split keys, grandparents, overlap limits, target file size, and a grant handle. `Runner` exposes `NewRunner`, `MoreDataToWrite`, `FirstKey`, `WriteTable`, `Finish`, and `TableSplitLimit`; helpers include `writeKeysToTable`, `validateWriterMeta`, and `spanStartOrNil`.

## Control Flow
`NewRunner` positions the iterator. Each `WriteTable` sets value-separation properties, appends an output table record, writes keys until an `OutputSplitter` asks to split or input is exhausted, finishes value separation, closes the writer, validates metadata, and records stats. Point keys go through `ValueSeparation.Add`; range spans are buffered and split/encoded around output table split keys.

## State And Persistence Behavior
The runner creates durable table/blob objects through supplied writers, but owns only metadata and accumulated stats. On failure, `Result` includes created objects for cleanup. Pending range spans may survive across table boundaries by keeping the unencoded suffix in `lastRangeDelSpan` or `lastRangeKeySpan`.

## Dependencies And Integration Points
It integrates `compact.Iter`, `OutputSplitter`, `sstable.RawWriter`, `objstorage`, manifest table/blob references, `valsep.ValueSeparation`, grant accounting, and compaction scheduler CPU/write-byte measurements.

## Risks And Edge Cases
Risks include output bounds exceeding compaction bounds or split keys, incorrect range-span splitting, writer close/metadata errors, value separation finish errors, pinned statistics undercounting range spans, and relying on approximate writer sizes for splitting.

## Test Signals
`run_test.go` validates `TableSplitLimit`. Span splitting is tested in `spans_test.go`, while full write paths are covered by broader Pebble compaction tests outside this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/run.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/run_test.go -->
# sources/storage-engines/pebble/internal/compact/run_test.go

## Purpose
This file tests hard output table split limits derived from grandparent overlap and L0 flush split keys.

## Important APIs, Types, And Functions
`TestTableSplitLimit` uses datadriven commands to build a manifest `Version`, initialize an `L0Organizer`, and call `Runner.TableSplitLimit` for requested start keys.

## Control Flow
The `define` command parses version debug text and prints the version plus flush split keys when present. The `split-limit` command constructs a minimal `Runner` with `Grandparents`, `L0SplitKeys`, and `MaxGrandparentOverlapBytes`, then prints either no limit or the selected key for each input.

## State And Persistence Behavior
All state is in-memory manifest/test metadata. No compaction outputs are written.

## Dependencies And Integration Points
It depends on `datadriven`, `manifest.ParseVersionDebug`, `manifest.NewL0Organizer`, `testutils.CheckErr`, and `Runner.TableSplitLimit`.

## Risks And Edge Cases
The test focuses only on split-limit selection, not actual writer boundary validation or range span carryover. It is sensitive to manifest ordering and L0 organizer flush split behavior.

## Test Signals
Expected datadriven output verifies limits from max grandparent overlap and from flush split keys, including the minimum of both when both apply.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/run_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/snapshots.go -->
# sources/storage-engines/pebble/internal/compact/snapshots.go

## Purpose
This file defines the snapshot sequence-number helper used to partition compaction processing into visibility stripes.

## Important APIs, Types, And Functions
`Snapshots` is `[]base.SeqNum`. `Index(seq)` returns the index of the first snapshot greater than `seq`, or `len(s)`. `IndexAndSeqNum(seq)` returns that index and snapshot sequence, or `SeqNumMax` if no greater snapshot exists.

## Control Flow
Both methods use binary search over an ascending snapshot slice. Compaction iterator code uses the returned index to decide whether versions are in the same snapshot stripe and whether a stripe is bottommost.

## State And Persistence Behavior
Snapshots are in-memory inputs from the DB's active snapshots. Their ordering affects durable compaction output because versions are collapsed only within stripes.

## Dependencies And Integration Points
The type depends on `base.SeqNum` and `sort.Search`. It is used by `Iter`, `RangeDelSpanCompactor`, and `RangeKeySpanCompactor`.

## Risks And Edge Cases
Callers must provide ascending snapshots. Duplicate snapshot numbers are tolerated by binary search but may create subtle stripe semantics; tests include duplicates. An empty slice maps every key to the bottom stripe with `SeqNumMax`.

## Test Signals
`snapshots_test.go` checks empty, single, multiple, boundary, and duplicate snapshot cases for both index and returned sequence.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/snapshots.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/snapshots_test.go -->
# sources/storage-engines/pebble/internal/compact/snapshots_test.go

## Purpose
This file tests the `Snapshots.IndexAndSeqNum` boundary behavior used by compaction stripe selection.

## Important APIs, Types, And Functions
`TestSnapshotIndex` is a table-driven test over `Snapshots`, input sequence numbers, expected index, and expected returned snapshot sequence.

## Control Flow
Each case constructs `Snapshots`, calls `IndexAndSeqNum`, and checks both returned values with fatal assertions.

## State And Persistence Behavior
The test is pure and in-memory. It validates logic that later affects durable compaction output.

## Dependencies And Integration Points
It uses `base.SeqNum` and the `Snapshots` methods in `snapshots.go`.

## Risks And Edge Cases
The cases cover empty snapshots, equality with a snapshot boundary, values below/above boundaries, and duplicate snapshot values. It does not separately call `Index`, but `IndexAndSeqNum` uses it directly.

## Test Signals
Failures indicate incorrect snapshot stripe assignment, which would make `compact.Iter` collapse too much or preserve too much data.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/snapshots_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/spans.go -->
# sources/storage-engines/pebble/internal/compact/spans.go

## Purpose
This file compacts range deletion and range key spans and provides a helper to split and encode spans into output SSTables.

## Important APIs, Types, And Functions
`RangeDelSpanCompactor` and `MakeRangeDelSpanCompactor` coalesce RANGEDELs by snapshot stripe and elide bottom-stripe tombstones when allowed. `RangeKeySpanCompactor` and `MakeRangeKeySpanCompactor` coalesce range keys by suffix within stripes and elide bottom-stripe unset/delete keys. `SplitAndEncodeSpan` writes the prefix of a span before a table split key and keeps the suffix for the next table.

## Control Flow
Range deletion compaction scans trailer-descending keys, keeps the newest tombstone per snapshot stripe, stops after the bottom stripe, and may drop it if the range is not in use. Range key compaction partitions keys by snapshot visibility, calls `rangekey.Coalesce`, and filters unset/delete keys in the last stripe if elidable. `SplitAndEncodeSpan` encodes all, none, or a prefix depending on `upToKey`.

## State And Persistence Behavior
Compactors reuse output span slices and mutate span buffers. Their output is later persisted in SST range-del/range-key blocks. `SplitAndEncodeSpan` mutates the input span's `Start` to the remaining split point.

## Dependencies And Integration Points
It depends on `keyspan`, `rangekey`, `sstable.RawWriter`, snapshots, and tombstone elision. It is used by `Iter` and `Runner`.

## Risks And Edge Cases
Risks include preserving too many or too few range tombstones across snapshots, incorrect suffix coalescing, eliding range-key tombstones while lower range keys still exist, and split-key mutation bugs that duplicate or drop parts of a span.

## Test Signals
`spans_test.go` uses datadriven tests for range deletion compaction, range key compaction, in-use ranges, and split/encode behavior with actual SST reading.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/spans.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/spans_test.go -->
# sources/storage-engines/pebble/internal/compact/spans_test.go

## Purpose
This file tests range deletion span compaction, range key span compaction, and splitting/encoding spans into SSTables.

## Important APIs, Types, And Functions
`TestRangeDelSpanCompactor` and `TestRangeKeySpanCompactor` run datadriven compact commands. `maybeParseInUseKeyRanges` parses optional in-use ranges. `TestSplitAndEncodeSpan` stores a span, encodes up to a key into an in-memory SST, reads it back, and prints encoded plus remaining spans.

## Control Flow
Compactor tests parse snapshots and in-use ranges, parse a `keyspan.Span`, instantiate the relevant compactor, compact into a reusable output span, and print either the span or `"."`. Split tests create a `MemObj`, `RawWriter`, call `SplitAndEncodeSpan`, close the writer, read back range deletions/range keys, and print both sides of the split.

## State And Persistence Behavior
Most tests are in-memory, but `TestSplitAndEncodeSpan` writes to an in-memory SST object to validate actual encoding/decoding behavior.

## Dependencies And Integration Points
It uses `datadriven`, `keyspan`, `sstable`, `colblk`, `objstorage.MemObj`, `testkeys`, and `require`. It validates `spans.go` together with SSTable span encoding.

## Risks And Edge Cases
The tests cover non-overlap ordering, snapshot stripe compaction, in-use elision, empty outputs, and partial range splits. They do not run the full compaction iterator/runner path, but they verify shared helpers in isolation.

## Test Signals
Signals are exact datadriven output for compacted spans and successful SST round-trip with at most one encoded span plus correct remaining span mutation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/spans_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/splitting.go -->
# sources/storage-engines/pebble/internal/compact/splitting.go

## Purpose
This file implements compaction output splitting and a generic frontier heap used to notify components when iteration advances past key boundaries.

## Important APIs, Types, And Functions
`ShouldSplit` is `NoSplit` or `SplitNow`. `OutputSplitter` tracks start key, limit, target size, grandparent boundaries, frontier state, and split key. Key methods are `NewOutputSplitter`, `ShouldSplitBefore`, `SplitKey`, `boundaryReached`, `setNextBoundary`, and `shouldSplitBasedOnSize`. `frontier`, `frontierReachedFn`, and `Frontiers` implement registered key-boundary callbacks with `Init`, `Update`, `Advance`, and heap operations.

## Control Flow
The splitter finds grandparent file boundaries after the output start, registers a frontier, and on each candidate key checks whether a hard limit or grandparent boundary was reached. It splits near grandparent boundaries when estimated size is between 0.5x and 2x target, splits immediately at 2x, and splits by size after exhausting boundaries. It uses `equalPrevFn` to avoid splitting a user key across tables.

## State And Persistence Behavior
State is transient per output table but determines durable SST boundaries and future write amplification. `SplitKey` unregisters the frontier and returns either the selected split or the configured limit.

## Dependencies And Integration Points
It depends on `manifest.LevelIterator`, `base.Compare`, and `Frontiers` advanced by `compact.Iter`. `Runner` instantiates it while writing tables.

## Risks And Edge Cases
Risks include boundary/frontier drift, splitting at or before start key, splitting inside a user key, too-small outputs, too-large outputs, and grandparent heuristic thresholds that are inherited but not deeply principled.

## Test Signals
`splitting_test.go` validates output splitter choices and frontier heap behavior through datadriven fixtures, including randomized first-key frontier advancement.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/splitting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/splitting_test.go -->
# sources/storage-engines/pebble/internal/compact/splitting_test.go

## Purpose
This file tests compaction output split decisions and the `Frontiers` callback heap.

## Important APIs, Types, And Functions
`TestOutputSplitter` parses grandparent table metadata and runs splitter decisions. `TestFrontiers` initializes frontiers from sorted key lists and advances over scan keys. `initTestFrontier` creates a frontier callback that steps through provided keys.

## Control Flow
For output splitting, the test builds a version with grandparents in L1, constructs an `OutputSplitter` with start key, optional limit, and target size, advances frontiers for input keys, and prints the chosen split. Frontier tests create multiple frontiers, call `Advance` for each scanned key, and print heap contents.

## State And Persistence Behavior
All state is in-memory. The tests model split decisions that would later shape durable table boundaries.

## Dependencies And Integration Points
It uses `datadriven`, `manifest.ParseTableMetadataDebug`, `manifest.NewVersionForTesting`, `base.DefaultComparer`, `testkeys`, and the `Frontiers`/`OutputSplitter` APIs.

## Risks And Edge Cases
The tests cover grandparent boundaries, limits, target-size thresholds, same-user-key avoidance, and frontiers whose callback returns multiple already-reached keys. They do not validate actual SST writer bounds; `run.go` handles that separately.

## Test Signals
Expected textual split keys and frontier states identify regressions in heap ordering, callback looping, and split heuristics.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/splitting_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/tombstone_elision.go -->
# sources/storage-engines/pebble/internal/compact/tombstone_elision.go

## Purpose
This file computes and applies policies for eliding point tombstones, range deletion tombstones, and range-key unset/delete markers during compaction.

## Important APIs, Types, And Functions
`TombstoneElision` stores a mode and ordered in-use key ranges. Constructors are `NoTombstoneElision` and `ElideTombstonesOutsideOf`; methods include `ElidesNothing`, `ElidesEverything`, and `String`. `pointTombstoneElider` and `rangeTombstoneElider` implement ordered `ShouldElide` checks. `SetupTombstoneElision` derives policies from a manifest version, L0 organizer, output level, and compaction bounds.

## Control Flow
Eliders advance an index over sorted in-use ranges as keys/ranges are queried in order. A point tombstone can be elided if no in-use range contains the key. A range tombstone can be elided if it does not overlap any in-use range. Setup calculates lower-level in-use ranges, optimizes the fully-covered case to no elision, and currently applies the same policy to point and range-key tombstones.

## State And Persistence Behavior
Elision state is transient but affects durable compaction output by dropping tombstones that cannot shadow lower-level data. Eliders mutate their in-use index and require ordered calls.

## Dependencies And Integration Points
It depends on `base.UserKeyBounds`, `manifest.Version.CalculateInuseKeyRanges`, and `manifest.L0Organizer`. It feeds `Iter`, `RangeDelSpanCompactor`, and `RangeKeySpanCompactor`.

## Risks And Edge Cases
Incorrect elision can resurrect deleted data or retain unnecessary tombstones. Ordered-call assumptions are enforced only under invariants. L0 needs special handling because L0 files overlap. A TODO notes that point-key and range-key in-use ranges should eventually be calculated separately.

## Test Signals
`tombstone_elision_test.go` checks raw eliders, setup-derived in-use ranges, and integration-style point/range elision decisions from manifest versions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/tombstone_elision.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/tombstone_elision_test.go -->
# sources/storage-engines/pebble/internal/compact/tombstone_elision_test.go

## Purpose
This file tests tombstone elision primitives and setup logic derived from manifest versions.

## Important APIs, Types, And Functions
`TestTombstoneElider` tests point and range eliders from explicit policies. `TestSetupTombstoneElision` parses versions and prints policies for output levels and bounds. `TestTombstoneElision` combines setup with point/range `ShouldElide` decisions.

## Control Flow
Datadriven `init` commands choose either no elision or explicit in-use ranges. `points` and `ranges` print elide/don't-elide decisions. Version-based tests build an `L0Organizer` and manifest `Version`, call `SetupTombstoneElision`, then feed requested keys/ranges through eliders.

## State And Persistence Behavior
All state is in-memory manifest/test metadata. The behavior validated affects future persisted compaction outputs by deciding which tombstones disappear.

## Dependencies And Integration Points
The tests depend on `datadriven`, `manifest.ParseVersionDebug`, `manifest.NewL0Organizer`, `base.UserKeyBounds`, `testkeys`, and the elision APIs.

## Risks And Edge Cases
Tests cover empty in-use sets, overlapping/adjacent lower-level spans, L0 handling, point versus range queries, and ordered query behavior. They do not yet validate the TODO for separate point/range-key in-use range calculation.

## Test Signals
Exact datadriven text demonstrates whether tombstones are retained when lower-level data overlaps and elided when outside all in-use ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compact/tombstone_elision_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/adaptive.go -->
# sources/storage-engines/pebble/internal/compression/adaptive.go

## Purpose
This file implements `AdaptiveCompressor`, a compressor that chooses between a fast and slow compression setting based on sampled relative size reduction.

## Important APIs, Types, And Functions
`AdaptiveCompressor` stores fast/slow compressors, reduction cutoff, sampling frequency, EWMA estimator, RNG, and a reusable buffer. `AdaptiveCompressorParams` configures fast/slow settings, cutoff, sample interval, EWMA half-life, and seed. `NewAdaptiveCompressor`, `Compress`, and `Close` form the API.

## Control Flow
`Compress` reads the current EWMA estimate. If not sampling, it records an unsampled block and chooses fast or slow according to whether the estimate is below the cutoff. If sampling, it compresses with both algorithms, records `1 - slowLen/fastLen`, and returns the fast result if the reduction is too small or the slow result otherwise.

## State And Persistence Behavior
State is per-compressor and in-memory: EWMA history, RNG sequence, and reusable buffer. `Close` closes both child compressors, drops very large buffers, and returns the object to a pool.

## Dependencies And Integration Points
It depends on `ewma.Bytes`, `math/rand/v2`, and the package-level `GetCompressor` abstraction. It is used wherever Pebble wants runtime codec adaptation for blocks.

## Risks And Edge Cases
Risks include biased sampling, bad cutoff selection, using a zero `SampleEvery`, and temporarily storing both fast and slow compressed results. Deterministic seeding is important for tests and reproducibility.

## Test Signals
`adaptive_test.go` checks that random data chooses the fast codec and highly compressible data chooses the slow codec under fixed seeds and parameters.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/adaptive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/adaptive_test.go -->
# sources/storage-engines/pebble/internal/compression/adaptive_test.go

## Purpose
This file tests adaptive compression decisions on incompressible and compressible workloads.

## Important APIs, Types, And Functions
`TestAdaptiveCompressorRand` configures fast MinLZ and slow Zstd with a 20% cutoff. `TestAdaptiveCompressorCompressible` configures no compression versus Zstd with a 60% cutoff.

## Control Flow
Each test creates an adaptive compressor with fixed sampling seed, repeatedly builds payloads, calls `Compress`, and asserts the returned `Setting`. Random payloads are expected to choose `MinLZFastest`; patterned payloads are expected to choose `ZstdLevel1`.

## State And Persistence Behavior
Only compressor EWMA/RNG state changes. No persistent artifacts are created.

## Dependencies And Integration Points
The tests depend on `math/rand/v2`, `testify/require`, MinLZ, Zstd, no-compression settings, and `AdaptiveCompressor`.

## Risks And Edge Cases
Tests rely on deterministic seeds and payload generation. They validate clear cases, not borderline cutoffs, zero/invalid sampling parameters, or close/reuse pooling behavior.

## Test Signals
Consistent returned settings across 100 iterations indicate the estimator and sampling path converge to the expected fast or slow choice.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/adaptive_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/compression.go -->
# sources/storage-engines/pebble/internal/compression/compression.go

## Purpose
This file defines Pebble's internal compression abstraction: algorithm identifiers, compression settings, presets, compressor/decompressor interfaces, and factory functions.

## Important APIs, Types, And Functions
`Algorithm` includes `NoAlgorithm`, `Snappy`, `MinLZ`, `Zstd`, `NumAlgorithms`, and `Unknown`. `Setting` stores algorithm plus optional level and supports `String`/`ParseSetting`. Presets include `NoCompression`, `SnappySetting`, MinLZ levels, and Zstd levels. `Compressor` and `Decompressor` define `Compress`, `DecompressInto`, `DecompressedLen`, and `Close`. `GetCompressor`, `GetDecompressor`, and `makePreset` dispatch implementations.

## Control Flow
Factories switch on the algorithm and return no-op, Snappy, MinLZ, or build-selected Zstd implementations. `ParseSetting` scans known algorithms by string prefix and parses a numeric suffix as level.

## State And Persistence Behavior
The `presets` slice is package-global and populated as preset vars initialize. Compression settings are stored in table/block metadata elsewhere; this file does not persist state itself.

## Dependencies And Integration Points
It imports MinLZ level constants and dispatches to `noop.go`, `snappy.go`, `minlz.go`, and `zstd_*`. SSTable/block code depends on these interfaces for codec-independent compression.

## Risks And Edge Cases
Invalid algorithms panic in factories. `ParseSetting` accepts any numeric suffix that fits in `uint8` after conversion, so callers must validate if needed. String names are part of diagnostics and test expectations.

## Test Signals
`compression_test.go` round-trips every preset, checks zstd decompression errors, and validates `Setting.String`/`ParseSetting` round-trip.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/compression.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/compression_test.go -->
# sources/storage-engines/pebble/internal/compression/compression_test.go

## Purpose
This file tests common compression factory behavior, round-trips for all presets, decompression error handling, and setting string parsing.

## Important APIs, Types, And Functions
`TestCompressionRoundtrip` iterates `presets`. `TestDecompressionError` builds malformed zstd-like bytes. Helper `decompress` uses `GetDecompressor`, `DecompressedLen`, and `DecompressInto`. `TestSettingString` checks `String` and `ParseSetting`.

## Control Flow
Round-trip tests create random payloads and random compressed output buffers, compress through a preset compressor, then decompress by returned algorithm and compare bytes. Error testing prefixes garbage with a plausible zstd decoded length and expects decompression failure. String testing loops all presets.

## State And Persistence Behavior
Tests are in-memory. No SST files are written. Leaktest wraps round-trip/error tests.

## Dependencies And Integration Points
It depends on `encoding/binary`, `math/rand/v2`, `leaktest`, `require`, and all compressor/decompressor implementations reachable from presets.

## Risks And Edge Cases
Tests cover payloads up to 10 KiB and malformed zstd, but not very large blocks except through `minlz_test.go`. The malformed zstd setup mutates only the varint prefix bytes, leaving payload as zeroed/garbage enough to expect an error.

## Test Signals
Signals are exact payload equality after decompression, non-nil error and nil result for bad zstd input, and successful preset string round-trips.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/compression_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/minlz.go -->
# sources/storage-engines/pebble/internal/compression/minlz.go

## Purpose
This file implements MinLZ compression/decompression adapters for the package compression interfaces.

## Important APIs, Types, And Functions
`minlzCompressor` stores a level and implements `Compress` and `Close`; `getMinlzCompressor` returns singleton fastest or balanced compressors. `minlzDecompressor` implements `DecompressInto`, `DecompressedLen`, and `Close`.

## Control Flow
Compression falls back to Snappy if the source exceeds `minlz.MaxBlockSize`; otherwise it calls `minlz.Encode`, panics on unexpected encode error, marks bytes for MSan, and returns a MinLZ setting. Decompression calls `minlz.Decode` into the supplied buffer, verifies the returned slice aliases the buffer exactly, marks bytes for MSan, and returns errors for decode or alias/length mismatch.

## State And Persistence Behavior
The singleton compressors are stateless except for level. Compressed blocks are persisted by callers, and the returned setting may be Snappy for oversized MinLZ inputs.

## Dependencies And Integration Points
It depends on `github.com/minio/minlz`, `snappyCompressor` fallback, `base.CorruptionErrorf`, and `msanWrite`.

## Risks And Edge Cases
The important edge case is oversized blocks. `minlz_test.go` also asserts MinLZ decompressor can decode Snappy fallback bytes, implying MinLZ decode compatibility or wrapper behavior must remain true. Buffer alias checks catch decompression APIs allocating or writing somewhere unexpected.

## Test Signals
`minlz_test.go` validates boundary sizes around `MaxBlockSize`, fallback behavior, and decompression equality.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/minlz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/minlz_test.go -->
# sources/storage-engines/pebble/internal/compression/minlz_test.go

## Purpose
This file tests MinLZ behavior at and above its maximum block size, including fallback compatibility.

## Important APIs, Types, And Functions
`TestMinLZLargeBlock` creates buffers of `minlz.MaxBlockSize + delta`, compresses with `MinLZFastest`, and decompresses using both the returned algorithm and explicit `MinLZ`.

## Control Flow
For deltas `-1`, `0`, `1`, and a random large positive value, the test fills deterministic bytes, compresses, decompresses into a same-sized buffer, checks equality, clears the buffer, then repeats using a MinLZ decompressor even if compression returned Snappy.

## State And Persistence Behavior
All data is in memory. The test validates behavior important for persisted blocks larger than MinLZ can encode.

## Dependencies And Integration Points
It uses `github.com/minio/minlz`, `GetCompressor`, `GetDecompressor`, MinLZ settings, and `require`.

## Risks And Edge Cases
The boundary around `MaxBlockSize` is the primary risk. The explicit MinLZ decompressor compatibility check is notable and should be preserved if fallback encodings change.

## Test Signals
Successful equality for all sizes and both decompressor choices indicates correct fallback and decode behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/minlz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/msan_off.go -->
# sources/storage-engines/pebble/internal/compression/msan_off.go

## Purpose
This build-tagged file provides the no-op MemorySanitizer hook for non-MSan builds.

## Important APIs, Types, And Functions
`func msanWrite(p []byte) {}` is compiled under `//go:build !msan`.

## Control Flow
Compression/decompression implementations call `msanWrite` after assembly or external codec writes. In non-MSan builds, calls do nothing.

## State And Persistence Behavior
No state is mutated and no persistence exists.

## Dependencies And Integration Points
It pairs with `msan_on.go` and is called from Snappy, MinLZ, and Zstd implementations.

## Risks And Edge Cases
The only risk is build selection: if an MSan build accidentally uses this file, sanitizer may report false positives or miss initialization.

## Test Signals
Compile-time build tags are the validation. Ordinary compression tests run through this no-op in non-MSan builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/msan_off.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/msan_on.go -->
# sources/storage-engines/pebble/internal/compression/msan_on.go

## Purpose
This build-tagged file implements the MemorySanitizer hook used after codec writes.

## Important APIs, Types, And Functions
`msanWrite(p []byte)` calls `runtime.MSanWrite` with the slice's first byte pointer and length when the slice is non-empty. It is compiled under `//go:build msan`.

## Control Flow
Codec implementations call this after producing compressed or decompressed bytes so MSan knows the memory has been initialized, including when assembly or C code performed writes outside Go's ordinary instrumentation.

## State And Persistence Behavior
It updates sanitizer metadata only. There is no Pebble state or persistence.

## Dependencies And Integration Points
It imports `runtime` and `unsafe`, and pairs with `msan_off.go`. Snappy, MinLZ, and Zstd adapters call the shared hook.

## Risks And Edge Cases
The function must avoid taking `&p[0]` for empty slices, which it does. Incorrect length or pointer would produce sanitizer inaccuracies.

## Test Signals
Validation is primarily MSan build/test execution. Non-MSan tests do not compile this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/msan_on.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/noop.go -->
# sources/storage-engines/pebble/internal/compression/noop.go

## Purpose
This file implements the no-compression codec for the package interfaces.

## Important APIs, Types, And Functions
`noopCompressor` implements `Compress` and `Close`. `noopDecompressor` implements `DecompressInto`, `DecompressedLen`, and `Close`.

## Control Flow
Compression copies `src` into `dst[:0]` and returns `NoCompression`. Decompression copies `src` into `dst` after slicing to source length. Decompressed length is simply `len(b)`.

## State And Persistence Behavior
The codec is stateless. It represents uncompressed persisted blocks; callers still treat it through the same compressor/decompressor abstraction.

## Dependencies And Integration Points
It is returned by `GetCompressor(NoAlgorithm)` and `GetDecompressor(NoAlgorithm)` and is used by adaptive compression tests as a fast codec.

## Risks And Edge Cases
Callers must allocate a destination of the exact decompressed length before `DecompressInto`; this implementation assumes `dst` is large enough. It does not validate aliasing or return corruption errors.

## Test Signals
`compression_test.go` round-trips the `NoCompression` preset through the common factory path.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/noop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/snappy.go -->
# sources/storage-engines/pebble/internal/compression/snappy.go

## Purpose
This file adapts Go Snappy compression/decompression to Pebble's compression interfaces.

## Important APIs, Types, And Functions
`snappyCompressor` implements `Algorithm`, `Compress`, and `Close`. `snappyDecompressor` implements `DecompressInto`, `DecompressedLen`, and `Close`.

## Control Flow
Compression calls `snappy.Encode` with capacity-limited destination, marks the result for MSan, and returns `SnappySetting`. Decompression calls `snappy.Decode` into the provided buffer, verifies length and aliasing, marks the destination for MSan, and returns errors on decode or buffer mismatch. `DecompressedLen` delegates to `snappy.DecodedLen`.

## State And Persistence Behavior
The codec is stateless. Snappy-compressed bytes are persisted by callers in SST blocks.

## Dependencies And Integration Points
It depends on `github.com/golang/snappy`, `base.CorruptionErrorf`, and `msanWrite`. It is used directly by factories and as MinLZ fallback for oversized inputs.

## Risks And Edge Cases
The aliasing check is important because callers expect decompression into a manually/accounted buffer. Compression uses `dst[:cap(dst):cap(dst)]`, which lets Snappy reuse full capacity.

## Test Signals
Common compression round-trip tests exercise Snappy. MinLZ large-block tests may exercise Snappy fallback paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/snappy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/zstd_cgo.go -->
# sources/storage-engines/pebble/internal/compression/zstd_cgo.go

## Purpose
This file implements Zstd compression/decompression using the DataDog CGo-backed zstd library when cgo is enabled and `pebblegozstd` is not set.

## Important APIs, Types, And Functions
`zstdCompressor` holds a level and `zstd.Ctx`; compressor instances are pooled. `UseStandardZstdLib` is true for test reproducibility. `Compress`, `Close`, and `getZstdCompressor` implement compression. `zstdDecompressor` with a pooled context implements `DecompressInto`, `DecompressedLen`, `Close`, and `getZstdDecompressor`.

## Control Flow
Compression reserves a varint prefix for decoded length, ensures capacity using `zstd.CompressBound`, writes the length, compresses into the buffer after the prefix, asserts no unexpected allocation, marks compressed bytes, and returns a Zstd setting. Decompression reads the varint length prefix, rejects empty source/destination, decompresses into `dst`, validates byte count, marks bytes, and reports corrupted length prefixes.

## State And Persistence Behavior
Compressed blocks include a uvarint decoded-length prefix. Compressor/decompressor contexts are pooled and must be closed to return them.

## Dependencies And Integration Points
It depends on `github.com/DataDog/zstd`, `encoding/binary`, `base`, and `msanWrite`. It is selected by build tags and returned by the common factories.

## Risks And Edge Cases
Risks include context reuse without `Close`, invalid varint prefixes, zero-length buffers, compression library allocation changes, and cgo availability. Tests may branch on `UseStandardZstdLib`.

## Test Signals
Common compression round-trip and malformed zstd tests exercise this implementation in cgo builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/zstd_cgo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/zstd_nocgo.go -->
# sources/storage-engines/pebble/internal/compression/zstd_nocgo.go

## Purpose
This file implements Zstd compression/decompression using the pure-Go klauspost library when cgo is unavailable or `pebblegozstd` is set.

## Important APIs, Types, And Functions
`zstdCompressor` holds a level and `*zstd.Encoder`, with a pool for wrapper structs. `UseStandardZstdLib` is false. `Compress`, `Close`, and `getZstdCompressor` implement compression. Stateless `zstdDecompressor` implements `DecompressInto`, `DecompressedLen`, `Close`, and `getZstdDecompressor`.

## Control Flow
Compression writes a varint decoded-length prefix into `compressedBuf`, encodes all bytes with the configured encoder appending after the prefix, marks the result, and returns Zstd setting. `Close` closes the encoder, clears it, and returns the wrapper to a pool. Decompression reads the prefix, creates a new decoder, decodes into `dst[:0]`, verifies length and aliasing, marks bytes, and closes the decoder.

## State And Persistence Behavior
Persisted block format matches the cgo variant's varint length prefix. Encoder state is per compressor and must be closed; decompressor creates a decoder per call.

## Dependencies And Integration Points
It depends on `github.com/klauspost/compress/zstd`, `encoding/binary`, `base`, and `msanWrite`. It is selected by build tags through `compression.go` factories.

## Risks And Edge Cases
Pure-Go zstd may produce different compressed bytes from the standard library, so reproducibility-sensitive tests check `UseStandardZstdLib`. Per-call decoder allocation can be more expensive than pooled cgo contexts.

## Test Signals
Compression round-trips and decompression-error tests exercise this path in non-cgo or `pebblegozstd` builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/compression/zstd_nocgo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/crc/crc.go -->
# sources/storage-engines/pebble/internal/crc/crc.go

## Purpose
This file implements Pebble's RocksDB-compatible CRC-32C checksum wrapper.

## Important APIs, Types, And Functions
Package-level `table` is a Castagnoli CRC table. `type CRC uint32` provides `New`, `Update`, and `Value`.

## Control Flow
`New` starts with zero CRC and updates with bytes. `Update` calls `crc32.Update` using the Castagnoli table. `Value` applies RocksDB-style masking by rotating right 15/left 17 and adding `0xa282ead8`.

## State And Persistence Behavior
The table is immutable package state. Checksums are stored by callers in little-endian format; this file only computes the uint32 value.

## Dependencies And Integration Points
It depends on Go's `hash/crc32`. It is used throughout Pebble for record/block checksum verification and compatibility with LevelDB/RocksDB checksum masking.

## Risks And Edge Cases
Changing the polynomial, masking rotation, or delta would break on-disk compatibility. The wrapper is simple but persistence-critical.

## Test Signals
No direct tests are listed in this subset. Indirect coverage comes from manifest/log/table read-write tests elsewhere that validate checksum round-trips and corruption detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/crc/crc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/datadrivenutil/datadrivenutil.go -->
# sources/storage-engines/pebble/internal/datadrivenutil/datadrivenutil.go

## Purpose
This file provides small parsing helpers for Pebble datadriven tests, making line, field, key-value, integer, and hex-byte extraction concise.

## Important APIs, Types, And Functions
`Lines.Next` consumes one line at a time. `Line.Fields` splits on whitespace plus optional delimiters. `Fields` supports `String`, `HasValue`, `Index`, `KeyValue`, `MustKeyValue`, and `HexBytes`. `Value` supports `Str`, `Bytes`, `Int`, `Uint64`, and `HexBytes`.

## Control Flow
Parsing is intentionally direct: `Lines.Next` searches for newline and mutates the receiver; `Fields` uses `strings.FieldsFunc`; key-value lookup scans fields for `key=`; numeric and hex conversions panic on invalid data.

## State And Persistence Behavior
State is limited to the mutable `Lines` string wrapper during parsing. There is no persistence.

## Dependencies And Integration Points
It depends on `encoding/hex`, `strconv`, `strings`, `unicode`, and `errors`. Datadriven tests across Pebble can use it to reduce custom parsing boilerplate.

## Risks And Edge Cases
`Fields.KeyValue` indexes `fs[i][len(key)]` after a length check of `>= len(key)`, so an exact field equal to the key without `=` would be risky if encountered; expected usage is `key=value` fields. Panic-on-parse is acceptable for tests but unsuitable for production parsing.

## Test Signals
No direct tests are in this subset. Its behavior is indirectly validated by any datadriven tests using these helpers.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/datadrivenutil/datadrivenutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/datatest/datatest.go -->
# sources/storage-engines/pebble/internal/datatest/datatest.go

## Purpose
This file provides reusable datadriven test helpers outside the root Pebble package, including batch definition parsing, compaction tracking, SST building, and ingest-and-excise command execution.

## Important APIs, Types, And Functions
`DefineBatch` parses operations into a `pebble.Batch`. `CompactionTracker`, `NewCompactionTracker`, and `WaitForInflightCompactionsToEqual` track compaction begin/end events. `RunBuildSSTCmd`, `WithDefaultWriterOpts`, and internal option helpers build SST files. `RunIngestAndExciseCmd` parses datadriven args and calls `DB.IngestAndExcise`.

## Control Flow
`DefineBatch` walks each input line, validates argument counts, converts `<nil>` keys to empty strings, and calls batch mutation APIs. `NewCompactionTracker` attaches event listeners that increment/decrement a condition-protected count. SST building parses writer options, creates a file, writes parsed test SST data, closes writer, and returns metadata. Ingest/excise collects `.sst` args and an optional `excise=start-end` span.

## State And Persistence Behavior
Batch helpers mutate caller-provided batches. SST building writes to the provided VFS path. Compaction tracking is in-memory listener state. Ingest/excise mutates the provided DB.

## Dependencies And Integration Points
It integrates with public Pebble APIs, `datadriven`, `sstable`, `objstorageprovider`, `vfs`, and event listeners.

## Risks And Edge Cases
The helpers are test-only but can trigger real DB mutations. Argument validation must stay aligned with public API semantics. `WaitForInflightCompactionsToEqual` requires listener attachment and can block indefinitely if expected events do not arrive.

## Test Signals
No direct tests are listed here; downstream datadriven tests using these helpers provide coverage through successful command execution and expected DB state.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/datatest/datatest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/deletepacer/delete_pacer.go -->
# sources/storage-engines/pebble/internal/deletepacer/delete_pacer.go

## Purpose
This file implements `DeletePacer`, a background queue that rate-limits deletion of obsolete files to reduce disk-performance cliffs while adapting to backlog and low free space.

## Important APIs, Types, And Functions
`DiskFreeSpaceFn` and `DeleteFn` abstract free-space measurement and deletion. `DeletePacer` stores options, logger, queue, pacing bytes, recent history, metrics, condition variable, notify channel, and wait group. `Open`, `Close`, `Enqueue`, `Metrics`, and `WaitForTesting` are the public surface. `queueEntry`, `RecentRateWindow`, and `maxQueueSize` support queue behavior.

## Control Flow
`Open` initializes defaults/history/condition state and starts `mainLoop` under a pprof label. The loop exits only when closed and queue empty, recalculates pacing rate from recent arrivals, backlog, queue bytes, free space, and disabled-pacing flags, waits while in debt, or deletes the next file outside the mutex. `Enqueue` records pacing bytes and history, grows the queue in chunks, updates in-queue metrics, appends entries, and non-blockingly wakes the goroutine. `Close` marks closed, wakes the loop, and waits; pacing is disabled for remaining jobs.

## State And Persistence Behavior
Queue and metrics are in-memory. Deletion side effects are delegated to `DeleteFn` and remove persistent files. Metrics track in-queue and deleted counts/sizes by file type and placement.

## Dependencies And Integration Points
It depends on options/rate calculation and obsolete-file definitions in the same package, `base.Logger`, `metrics.FileCountsAndSizes`, `crtime`, invariants, and pprof labels. Pebble file cleanup code enqueues obsolete table/blob files here.

## Risks And Edge Cases
Risks include queue growth, deletion lag under heavy compaction, low disk space requiring acceleration, enqueue after close, delete function panics or slow deletes, and condition waits. The max queue safety valve disables pacing and logs at most once per minute.

## Test Signals
This subset has no direct delete-pacer tests. Useful signals would include queue metrics, `WaitForTesting`, low-space rate behavior, close draining, and max-queue logging in package tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/deletepacer/delete_pacer.go -->

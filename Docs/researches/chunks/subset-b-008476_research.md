# sources/storage-engines/foundationdb/fdbserver/kvstore/VersionedBTree.actor.cpp lines 6745-11091

## Scope

This chunk covers the end of `VersionedBTree::commitSubtree`, the top-level B-tree commit actor, the public B-tree cursor used for point and range reads, the `KeyValueStoreRedwood` `IKeyValueStore` adapter, Redwood metrics formatting, and a large block of unit, correctness, and performance tests for Redwood's page, delta-tree, queue, insert, seek, and range-scan behavior. Earlier chunks define most page formats and helper types used here; this chunk shows how those pieces are committed, read, exposed through the storage-engine interface, and stressed.

## Purpose

The production code in this range closes the write path and exposes the read path:

- recursive commit processing turns mutation-buffer ranges into leaf/internal page updates, subtree clears, page rebuilds, remapped child detaches, root replacement, lazy-delete queue state, and pager commits;
- `BTreeCursor` gives snapshot-backed seek and bidirectional iteration over Redwood records, including page descent, sibling prefetch, cursor reuse, and arena lifetime handling for reads;
- `KeyValueStoreRedwood` adapts `VersionedBTree` to FoundationDB's `IKeyValueStore` contract for initialization, close/dispose, commit, set/clear, point read, prefix read, range read, error propagation, and storage-byte reporting.

The test and benchmark code in the same chunk provides direct validation signals for the lower-level delta encoding, `DeltaTree`/`DeltaTree2` mutation and seek semantics, full B-tree randomized correctness, restart recovery, page-cache cleanup, extent queue recovery, and several write/read workload shapes.

## Important APIs, Types, and Functions

- `VersionedBTree::commitSubtree(...)`: in this chunk, the internal-page branch builds `InternalPageSliceUpdate` objects per child range, avoids recursion for uniformly cleared or unchanged mutation spans, recursively commits changed children, then uses `InternalPageModifier` to patch, rebuild, or delete the parent page. It frees level-2 leaf children immediately for cleared ranges and queues deeper subtree deletion via `m_lazyClearQueue`.
- `VersionedBTree::commit_impl(Version writeVersion, Future<Void> previousCommit)`: owns a `CommitBatch`, swaps out the mutable mutation buffer, waits for prior commit serialization, sets the new oldest readable version, commits the whole root range, rebuilds the root if needed, stops and flushes lazy clearing, writes the commit header through the pager, and restarts incremental lazy clearing.
- `VersionedBTree::BTreeCursor`: snapshot cursor with a stack of `PathEntry` objects. Public operations include `init`, `seek`, `seekGTE`, `seekLT`, `moveNext`, `movePrev`, `prefetch`, `get`, `back`, `popPath`, and `toString`.
- `VersionedBTree::initBTreeCursor(...)`: obtains an `IPagerSnapshot`, parses or reuses the commit header's root pointer from snapshot metadata, and initializes the cursor at the root.
- `KeyValueStoreRedwood`: the `IKeyValueStore` implementation for `SSD_REDWOOD_V1`. It constructs a `DWALPager`, owns `VersionedBTree`, and translates interface calls to tree calls.
- `KeyValueStoreRedwood::readRange_impl(...)`: performs forward or reverse range reads with cursor seeks, optional sibling prefetch, row/byte limit accounting, page-bound checks, and arena dependency retention.
- `KeyValueStoreRedwood::readValue_impl(...)` and `readValuePrefix_impl(...)`: perform point lookup and optional value truncation while preserving page arena lifetime for the returned `Value`.
- Random/test helpers: `randomSize`, `randomString`, `randomKV`, `verifyRangeBTreeCursor`, `seekAllBTreeCursor`, `verify`, `randomReader`, `IntIntPair`, `deltaTest`, `randomRedwoodRecordRef`, `getDefaultKeyGenerator`, `commitAndReportCorrectnessProgress`, `commitAndReportLoadProgress`, `randomSeeks`, `randomScans`, `KVSource`, `getStableStorageBytes`, `prefixClusteredInsert`, `sequentialInsert`, `closeKVS`, `doPrefixInsertComparison`, and `randomRangeScans`.
- Metrics functions: `RedwoodMetrics::getFields` and `RedwoodMetrics::getIOLockFields` format global operation counters, per-level page counters, event counters, page/decode cache sizes, and IO lock active/waiting counts into either `TraceEvent` fields or human-readable strings.

## Control Flow

The internal-page portion of `commitSubtree` walks child records with a page cursor. For each logical child slice, it computes lower/upper subtree boundaries, decode boundaries, expected boundary records, and the mutation-buffer interval that can affect that subtree. If exactly one mutation range covers the slice and its overlap is uniformly clear or uniformly unchanged, the code skips recursion. Uniform clears mark the slice cleared and either free direct child leaf pages or enqueue lazy subtree deletion for deeper pages. Otherwise, the function recurses into the child page with the narrowed mutation range.

After all recursive calls complete, the parent reconstructs its page state using `InternalPageModifier`. Updates are applied in slice order, with the next slice boundary or the caller-provided upper boundary used to preserve decode boundaries. If multiple children were updated in place under this parent, the parent may be force-rewritten so child links can be detached from pager remaps. Depending on modifier state, the parent page is cleared and freed, updated in place through `updateBTreePage`, or rebuilt/split through `writePages`. Rebuild/update results are reflected in the caller's `InternalPageSliceUpdate`.

`commit_impl` serializes commits by waiting on `previousCommit`, treats repeated write versions with no mutations as no-ops, takes a read snapshot at the previous committed version, and commits from the root link over `[dbBegin, dbEnd)`. If `commitSubtree` changes the root, it writes a new empty root for a fully deleted tree or builds new root levels when the returned child-link records no longer fit in the old root. It then stops the lazy clear actor, waits for completed lazy frees, flushes the lazy clear queue, persists the updated commit header through `m_pager->commit`, increments commit metrics, and restarts lazy clearing.

`BTreeCursor::seek_impl` always descends from the root path entry. Internal pages are searched with `query.withMaxPageID()` and `seekLessThan`; null-child boundary records terminate the search as absent. Leaf pages seek the exact `RedwoodRecordRef` query and set cursor validity only for non-erased entries. `move_impl` first walks within or up the current path until it can move to a next/previous internal link, then descends to the leftmost or rightmost leaf record in that direction, skipping internal dummy records that have no child page.

`readRange_impl` chooses forward behavior for positive `rowLimit` and reverse behavior for negative `rowLimit`. It seeks once, optionally calls `BTreeCursor::prefetch`, then drains the current leaf cursor directly without awaiting per record. Page bounds avoid per-key end checks when the entire leaf is inside the requested range. When a page contributes results, the result arena depends on both the delta-tree decode arena and the `ArenaPage` arena. The scan stops when the row limit, byte limit, range bound, root boundary, or current leaf boundary is reached.

## State and Persistence Behavior

Commit state is versioned and pager-backed. `commit_impl` moves the mutable `MutationBuffer` into a `CommitBatch`, resets in-memory mutation count, records `writeVersion`, `readVersion`, and `newOldestVersion`, and updates `m_header.root`, `m_header.height`, and `m_header.lazyDeleteQueue` before committing the header as the pager commit record. The B-tree root is a `BTreeNodeLink`; empty-tree replacement allocates a new page ID and writes an empty height-1 root.

Page persistence is copy-on-write unless the code elects an in-place page update. Internal nodes may be rewritten just to detach remapped child page IDs after enough children have been updated in place. `detachRemappedPage` translates logical remaps to physical page IDs at the commit version and updates the optional `DecodeBoundaryVerifier`. Cleared subtrees are either synchronously freed at leaf-child height or deferred through `m_lazyClearQueue` for incremental background deletion. The commit path stops and drains lazy clearing before persisting the queue state, then restarts `incrementalLazyClear`.

Read state is snapshot isolated. `BTreeCursor` stores an `IPagerSnapshot` and path stack; page records are only guaranteed until cursor movement changes pages. Returned `RangeResult` and `Value` objects explicitly depend on page/decode arenas so zero-copy record references remain valid for the caller. `initBTreeCursor` caches the root link in `snapshot->extra` after parsing the commit metadata key, avoiding repeated commit-header decoding for the same snapshot.

`KeyValueStoreRedwood::commit` uses a monotonically increasing `m_nextCommitVersion`, forwards errors into `m_errorPromise`, and immediately advances oldest readable version to the committed version because this adapter does not keep history. `shutdown` coordinates simulation-only destructive sanity checks, cancellation, close/dispose, and final `m_closed` signaling.

## Dependencies and Integration Points

The code depends on earlier `VersionedBTree.actor.cpp` definitions for `RedwoodRecordRef`, `BTreePage`, `BTreeNodeLinkRef`, `InternalPageSliceUpdate`, `InternalPageModifier`, `MutationBuffer`, `RangeMutation`, `writePages`, `updateBTreePage`, `makeEmptyRoot`, `buildNewRootsIfNeeded`, `readPage`, `preLoadPage`, `DecodeBoundaryVerifier`, and Redwood metrics. It also uses Flow actor primitives (`ACTOR`, `Future`, `Promise`, `PromiseStream`, `wait`, `co_await`, `choose`, `waitNext`), FoundationDB containers/arena types, and deterministic test randomness.

The storage integration point is `keyValueStoreRedwoodV1`, which returns `KeyValueStoreRedwood` for `KeyValueStoreType::SSD_REDWOOD_V1`. Production operation relies on `DWALPager` for page allocation, snapshots, reads, updates, commits, extent queues, remap cleanup, page cache accounting, and close/dispose. Read operations integrate with `ReadOptions`, `ReadType::FETCH`, `PagerEventReasons`, IO priorities, `PriorityMultiLock`, and global Redwood metrics/histograms.

Test code integrates with FoundationDB's `TEST_CASE` framework and parameter system. It compares Redwood against the in-memory `written` version map, optionally compares storage behavior against SQLite (`SSD_BTREE_V2`) in prefix-size workloads, and uses `DecodeBoundaryVerifier` samples to target node-boundary clear ranges. Performance tests expose tunables such as page size, extent size, page cache size, remap cleanup window, concurrency, record counts, scan widths, and read limits.

## Risks and Edge Cases

- Internal dummy boundary records are subtle: cursor seek/move and commit-slice boundary code must skip null-child records in the right places while still preserving decode boundaries. Mistakes can make ranges unreadable or corrupt parent/child boundary invariants.
- The mutation-range shortcut in `commitSubtree` assumes one mutation range uniformly clears or leaves the subtree unchanged. Boundary-key handling around `subtreeLowerBound` decides whether the boundary record itself matters; off-by-one errors here can drop or resurrect a key.
- In-place updates plus pager remapping require parent rewrites and child detaches. If `parentInfo` is stale after awaits, or if large multi-page nodes are detached incorrectly, parent links can point at old remapped pages. The code explicitly reacquires `parentInfo` after recursion waits and skips multi-page node detaches.
- Lazy clearing is part of durable state. Failing to stop, wait, flush, and persist `m_lazyClearQueue` before the pager commit could leak pages or lose pending subtree deletion work across restart.
- `BTreeCursor` returns record references into page/decode arenas. Read paths must keep arena dependencies whenever returning values outside the cursor's lifetime; missing dependencies would become use-after-free bugs.
- Reverse range reads use negative `rowLimit` and increment it toward zero. Incorrect limit handling can report wrong `more` flags or overrun caller byte/row budgets.
- `KeyValueStoreRedwood::commit` advances oldest readable version immediately, so this adapter is not a historical MVCC store. Callers expecting old snapshots through this interface would be incompatible.
- Several benchmark/test loops are intentionally huge (`10e6`, `80e6`, `100e6`, `1e9` defaults). They are useful for manual performance work but too expensive for ordinary quick validation unless parameters are reduced.
- Some tests rely on destructive file deletion, cold restarts, and optional destructive sanity checks. They should run only against disposable test files.

## Test and Validation Signals

This chunk contains direct test coverage:

- `/redwood/correctness/unit/RedwoodRecordRef` validates child-page encoding/copying, delta size/write/apply behavior, common-prefix comparisons, and microbenchmarks for delta encoding and comparison.
- `Lredwood/correctness/unit/deltaTree/RedwoodRecordRef` and `RedwoodRecordRef2` validate `DeltaTree` and `DeltaTree2` record storage, existing-key insert failure, erase/reinsert behavior, forward/reverse/value-only iteration, and high-volume seek behavior.
- `Lredwood/correctness/unit/deltaTree/IntIntPair` cross-checks `DeltaTree` and `DeltaTree2` with a simpler comparable type, covering growth until full, deletions, seek LTE/GTE exact and adjacent cases, hinted seeks, and seek performance variants.
- `:/redwood/performance/mutationBuffer`, `:/redwood/pager/ArenaPage`, and `:/redwood/performance/extentQueue` exercise mutation-buffer insert/lookup/erase, arena-page ownership dependencies, and FIFO extent-queue persistence/recovery paths.
- `Lredwood/correctness/btree` is the main randomized B-tree correctness test. It generates sets and range clears across versions, verifies point and range reads against an external version map, randomly advances oldest readable version, injects cold restarts, optionally runs concurrent random readers, then performs `clearAllAndCheckSanity`.
- `:/redwood/performance/set`, `:/redwood/performance/prefixSizeComparison`, `:/redwood/performance/sequentialInsert`, `:/redwood/performance/randomRangeScans`, and `:/redwood/performance/histograms` provide load, seek, scan, storage-size, and metrics-formatting performance signals.

For focused validation after changing this area, the highest-signal tests are the randomized B-tree correctness test with reduced limits, the delta-tree unit tests, and a range-read workload that covers both positive and negative row limits with byte limits and prefetch enabled. Restart/cold-start paths should be included for changes touching commit header, root rebuild, lazy delete queue, or pager remapping behavior.

## Unresolved Cross-Chunk References

This chunk starts after the leaf-page branch of `commitSubtree` has already begun, so the complete mutation merge and leaf rebuild logic lives in the previous chunk. Key type definitions and helper implementations for `InternalPageSliceUpdate`, `InternalPageModifier`, `writePages`, `buildNewRootsIfNeeded`, `readPage`, lazy clearing, page formats, and metrics structs also begin earlier. The final per-file merge should connect those earlier definitions with this chunk's commit completion, cursor, adapter, and test coverage.

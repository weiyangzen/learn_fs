# subset-b-007866 Research

Grouped research for SeaweedFS filer chunk, metadata, deletion, notification, lazy remote, and store-wrapper files. Each section is bounded for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunk_section_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunk_section_test.go

## Purpose
Tests garbage removal for a `FileChunkSection`, a chunk-section helper defined elsewhere in the filer package. The file is narrowly focused on verifying that a section's `chunks` slice is compacted after a set of file IDs is declared garbage.

## Important APIs and Functions
`Test_removeGarbageChunks` constructs a section from `NewFileChunkSection(0)`, populates five `filer_pb.FileChunk` values, builds a `map[string]struct{}` of garbage IDs, and calls `removeGarbageChunks`.

## Control Flow and State
The test mutates in-memory `section.chunks`. Persistence is not involved. The state transition under test is five chunks becoming two surviving chunks after garbage IDs `0`, `2`, and `4` are removed.

## Dependencies and Integration Points
Depends on `filer_pb.FileChunk` and package-local chunk-section helpers. It complements the broader chunk compaction logic in `filechunks.go` by testing section-level removal, likely used when compacting or rewriting chunk metadata.

## Risks
The assertion only checks surviving length, not the exact surviving IDs or order. A buggy implementation that removes the wrong three chunks could still pass.

## Test Signals
Positive signal for basic garbage filtering. Coverage is minimal and does not exercise empty maps, all-garbage, no-garbage, duplicate file IDs, or order preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunk_section_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunks.go

## Purpose
Implements core file chunk accounting and visibility logic. Filer entries store file data as ordered `filer_pb.FileChunk` metadata; this file determines logical file size, ETags, visible intervals after overwrites, read views, compaction candidates, and chunk deltas.

## Important APIs and Types
`TotalSize`, `FileSize`, `ETag`, `ETagEntry`, and `ETagChunks` derive entry metadata from chunk and remote-entry state. `CompactFileChunks`, `SeparateGarbageChunks`, and `FindGarbageChunks` classify current versus garbage chunk IDs. `MinusChunks`, `DoMinusChunks`, and `DoMinusChunksBySourceFileId` compute deletion deltas, including sync cases where a destination chunk records its source file ID. `ChunkView` represents a client-visible slice of a chunk. `VisibleInterval` represents the newest visible owner of a logical file byte range.

## Control Flow and State
`FileSize` uses the max of stored attributes, remote metadata when newer, and chunk extent. `CompactFileChunks` resolves manifests, computes non-overlapping visible intervals, then keeps chunks whose file IDs are present in those intervals. `ViewFromChunks` resolves visible intervals for a requested offset and size, then projects them into `ChunkView` values with `OffsetInChunk`, `ViewOffset`, and `ViewSize`.

## Persistence Behavior
This file does not persist data. It computes metadata used by readers and by deletion code that later enqueues volume file IDs. Manifest resolution can involve lookups through `wdclient.LookupFileIdFunctionType`.

## Dependencies and Integration Points
Uses `filer_pb.FileChunk`, interval-list helpers from the filer package, manifest resolution helpers, `util` MD5 helpers, and `wdclient` lookup callbacks. It feeds read streaming, entry updates, metadata notifications, and delete cleanup.

## Risks
Correctness depends on timestamp ordering: newer `ModifiedTsNs` wins overlapping ranges. Tie handling and manifest resolution failures can affect compaction and deletion safety. `ETagChunks` assumes chunk ETags decode as base64 MD5 values. `ViewFromChunks` ignores errors from `NonOverlappingVisibleIntervals`, so callers may get partial or empty views if manifest resolution fails.

## Test Signals
Covered by `filechunks_test.go`, `filechunks2_test.go`, and `filechunks_read_test.go`, including overwrite cases, random writes, source-file-ID deltas, read views, and real bug cases. Tests emphasize interval correctness more than error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks2_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunks2_test.go

## Purpose
Adds regression tests for chunk delta and compaction behavior, especially sync scenarios where file IDs differ between clusters but `SourceFileId` links chunks back to their origin.

## Important APIs and Functions
`TestDoMinusChunks` exercises `DoMinusChunks` and `DoMinusChunksBySourceFileId`. `TestCompactFileChunksRealCase` runs `CompactFileChunks` against a real chunk layout and logs compacted versus garbage chunks through `printChunks`.

## Control Flow and State
The sync test models cluster A and cluster B appending and overwriting the same file. It first computes chunks deleted by an "empty file" event, then uses source-file-ID aware subtraction to ensure cluster A also removes chunks that correspond to B's source IDs.

## Persistence Behavior
No persistence. All test state is in-memory chunk slices.

## Dependencies and Integration Points
Depends on `filer_pb.FileChunk`, `assert`, package chunk helpers, and logging. The scenario integrates with filer sync semantics outside this file by validating the chunk ID mapping logic used when remote metadata events delete or replace data.

## Risks
The real-case compaction test logs results but has no assertions, so it is diagnostic rather than protective. The source-file-ID test is valuable but narrow.

## Test Signals
Strong signal that cross-cluster deletions require comparing both `FileId` and `SourceFileId`. Weak signal for the logged compaction case because failures would not fail the test unless the function panics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks2_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks_read.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunks_read.go

## Purpose
Computes visible, non-overlapping file intervals from a possibly overlapping list of resolved chunks. This is the sweep-line engine used by `NonOverlappingVisibleIntervals` and therefore by reads, compaction, and chunk deletion.

## Important APIs and Types
`readResolvedChunks` converts chunks into start/end `Point`s and returns `IntervalList[*VisibleInterval]`. `addToVisibles` and `appendVisibleInterfal` append visible ranges. `Point` carries coordinate `x`, timestamp `ts`, chunk pointer, and start/end flag.

## Control Flow and State
The algorithm creates two points for each chunk, sorts by offset, timestamp, and start/end ordering, then maintains a `container/list` ordered by timestamp. The tail is the current visible chunk. When a higher timestamp chunk starts, or the current highest timestamp chunk ends, the code emits a visible interval from `prevX` to the current point.

## Persistence Behavior
No persistence. It works only with resolved chunks; manifest chunks are unexpected and printed as a warning-like message.

## Dependencies and Integration Points
Uses Go `slices.SortFunc`, `container/list`, `filer_pb.FileChunk`, and package `IntervalList`. Called indirectly by read planners and compaction. It assumes manifest resolution has already expanded manifest chunks.

## Risks
The code uses `int(a.x - b.x)` and similar timestamp casts in sorting; very large differences can overflow `int` on some platforms. Equal timestamp behavior depends on insertion/removal order. The function clips chunks for overlap detection but appends original chunk offset points rather than clipped `start`/`stop` points, so correctness relies on later callers using compatible ranges; current tests cover common and random cases.

## Test Signals
`filechunks_read_test.go` includes randomized byte-array verification, sequential large chunks, and actual bug layouts. `filechunks_test.go` also validates expected visible intervals for overwrite patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks_read.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks_read_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunks_read_test.go

## Purpose
Tests `readResolvedChunks` over overlapping, random, sequential, and production-like chunk layouts.

## Important APIs and Functions
`TestReadResolvedChunks`, `TestReadResolvedChunks2`, `TestRandomizedReadResolvedChunks`, `TestSequentialReadResolvedChunks`, `TestActualReadResolvedChunks`, and `TestActualReadResolvedChunks2` all call `readResolvedChunks`. `randomWrite` writes expected timestamp ownership into an array and returns a matching chunk.

## Control Flow and State
Most tests construct chunk slices and inspect or print visible intervals. The randomized test builds a 1 MiB logical array and verifies every visible interval maps to the timestamp stored by simulated writes.

## Persistence Behavior
No persistence. The tests model only chunk metadata and in-memory expected state.

## Dependencies and Integration Points
Uses `filer_pb.FileChunk`, `math.MaxInt64`, random generation, and the package-private visible interval fields. It directly protects the sweep-line algorithm consumed by read planning and compaction.

## Risks
Several tests print output without assertions, so they are useful during manual debugging but weak in CI. Randomized testing lacks an explicit deterministic seed in this file, which can make rare failures harder to reproduce.

## Test Signals
The randomized test is the strongest signal because it verifies byte-range ownership. Actual-case tests document known layouts from production or bugs, but would not fail unless manually inspected or expanded with assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks_read_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunks_test.go

## Purpose
Main regression suite for chunk compaction, visible interval merging, read-view construction, and range projection.

## Important APIs and Functions
Tests `CompactFileChunks`, `NonOverlappingVisibleIntervals`, `ViewFromChunks`, `ViewFromVisibleIntervals`, and helper `addVisibleInterval`. `BenchmarkCompactFileChunks` measures compaction over interleaved chunks.

## Control Flow and State
The interval tests use table-driven cases for simple adjacent chunks, full overwrites, partial overwrites, disjoint writes, same-offset updates, large real updates, and a documented real bug. Read tests project logical ranges into `ChunkView` slices and assert file ID, chunk offset, view size, and view offset.

## Persistence Behavior
No persistence. State is in-memory slices and interval lists.

## Dependencies and Integration Points
Depends on `filer_pb.FileChunk`, package interval types, `assert`, and random generation. It is the closest direct test coverage for reader planning and garbage compaction behavior used by filer writes and deletes.

## Risks
Some tests use `t.Fatalf` after indexing `Expected[x]`; if the function returns more intervals than expected, the failure can be an index panic instead of a cleaner assertion. Random compaction test depends on random data but uses deterministic logical checks.

## Test Signals
Strong coverage of normal and edge overlap semantics. It validates both visible intervals and read views, including very large file offsets. Error paths, manifest resolution failures, and ETag behavior are not covered here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer.go

## Purpose
Defines the central `Filer` type and core metadata operations: construction, peer bootstrap/aggregation, store setup, entry creation/update/find/listing, TTL expiry, empty-directory cleanup, attributes, and shutdown.

## Important APIs and Types
`Filer` holds store, master client, deletion queues, metadata log buffer, config, remote storage, singleflight groups, lock manager, deletion retry queue, empty folder cleaner, and persisted log cache. Key methods include `NewFiler`, `MaybeBootstrapFromOnePeer`, `AggregateFromPeers`, `SetStore`, `CreateEntry`, `ensureParentDirectoryEntry`, `UpdateEntry`, `FindEntry`, `doListDirectoryEntries`, `DeleteEmptyParentDirectories`, `IsDirectoryEmpty`, `Shutdown`, `GetEntryAttributes`, and `IsDirectoryKeyObject`.

## Control Flow and State
`NewFiler` initializes clients, queues, config, lock manager, persisted-log cache, and starts deletion processing. `CreateEntry` handles root no-op, name-length checks, directory TTL reset, atime defaults, optional existing-entry reuse, inode assignment, parent creation, insert/update, metadata notification, and stale chunk deletion. `FindEntry` returns root, filters expired TTL/S3-expiry entries, deletes expired metadata/data, and falls back to lazy remote fetch on misses. Listing calls lazy remote listing, filters expired entries after iteration, then may clean empty parents.

## Persistence Behavior
Metadata persists through `VirtualFilerStore`. Store identity is persisted in KV key `filer.store.id`. Metadata events are appended to `LocalMetaLogBuffer`, which later flushes to filer system-log files. Data deletion is asynchronous via `fileIdDeletionQueue`.

## Dependencies and Integration Points
Integrates with masters through `wdclient.MasterClient`, peer metadata aggregation, distributed lock ring updates, S3 bucket naming, empty-folder cleanup, remote storage lazy fetch/list, stats, and store wrappers.

## Risks
Create/update correctness depends on callers holding proper path locks. TTL deletion during find/list has side effects in read paths. Parent auto-creation promotes files to directories to support S3 flat-key semantics, which is surprising for POSIX-like users. Shutdown assumes `Store` and `LocalMetaLogBuffer` are initialized. Lazy remote fallbacks trade consistency for availability.

## Test Signals
Inode behavior is covered by `filer_inode_test.go`; lazy remote miss/fetch/listing by `filer_lazy_remote_test.go`; wrapper context semantics by wrapper tests. This file's peer aggregation, TTL deletion, and empty-parent cleanup have limited direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_buckets.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_buckets.go

## Purpose
Provides bucket detection for filer entries.

## Important APIs and Functions
`IsBucket(entry *Entry) bool` returns true for directory entries whose parent path equals `f.DirBucketsPath` and whose directory name does not start with `.`.

## Control Flow and State
The function checks directory mode, splits `FullPath` into parent and name, compares to configured bucket root, and excludes hidden/system bucket-like names.

## Persistence Behavior
No persistence. It influences whether other code treats a directory deletion as collection deletion or bucket event handling.

## Dependencies and Integration Points
Used by deletion (`DeleteEntryMetaAndData`) to detect collection/bucket deletion, by rename checks, and by metadata event bucket notifications. Depends on `Entry.IsDirectory` and `util.FullPath.DirAndName`.

## Risks
Correctness depends entirely on `DirBucketsPath` being configured consistently. Hidden directories under bucket root are intentionally not buckets.

## Test Signals
Indirectly tested by remote deletion and bucket event tests; no dedicated table for edge names, root paths, or nil entries in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_buckets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_conf.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_conf.go

## Purpose
Loads, stores, matches, mutates, and serializes filer path configuration. These rules drive collection, replication, TTL, disk type, read-only, chunk-deletion, WORM, and quota-derived behavior.

## Important APIs and Types
`FilerConf` wraps a prefix trie of `filer_pb.FilerConf_PathConf`. Key functions are `ReadFilerConf`, `ReadFilerConfFromFilers`, `NewFilerConf`, `loadFromFiler`, `LoadFromBytes`, `MatchStorageRule`, `ClonePathConf`, `ApplyBucketQuotaReadOnly`, `GetCollectionTtls`, `mergePathConf`, `ToProto`, and `ToText`.

## Control Flow and State
Remote reads first try one of the supplied filer gRPC addresses, using either `ReadEntry` with a master client or `ReadInsideFiler`. Local loads read `/etc/seaweedfs/filer.conf` from inline content or chunks. Prefix matching uses a fast path: no match returns immutable `emptyPathConf`, one match returns the stored config, multiple matches merge all matching prefixes into a new config.

## Persistence Behavior
Config is persisted as a filer entry under `/etc/seaweedfs/filer.conf`, encoded as protobuf JSON. In-memory trie state is replaced or mutated by setters and reload paths.

## Dependencies and Integration Points
Depends on filer protobufs, `ptrie`, gRPC filer clients, master chunk reading, and utility proto text/JSON. Storage rules feed volume assignment, chunk deletion disabling, max filename lengths, and bucket quota read-only toggling.

## Risks
`doLoadConf` returns nil on `SetLocationConf` error, losing the original error. `MatchStorageRule` can return pointers callers must not mutate; unsafe callers can corrupt shared config. Merge semantics are mostly OR/non-empty, so nested rules cannot clear booleans inherited from broader prefixes.

## Test Signals
`filer_conf_test.go` covers prefix merge, clone completeness by reflection, nil clone, and quota read-only toggling. It does not cover load parse failures, gRPC failover, or text serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_conf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_conf_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_conf_test.go

## Purpose
Tests filer configuration prefix matching, cloning, and quota-driven read-only state.

## Important APIs and Functions
`TestFilerConf` validates `doLoadConf` and `MatchStorageRule`. `TestClonePathConf` uses reflection to ensure all exported fields are copied. `TestClonePathConfNil` covers nil input. `TestApplyBucketQuotaReadOnly` exercises quota transitions.

## Control Flow and State
The tests build in-memory protobuf config objects, load them into `FilerConf`, and assert merged fields. Quota tests mutate trie state by calling `ApplyBucketQuotaReadOnly` repeatedly.

## Persistence Behavior
No disk or filer persistence. The tests validate in-memory config behavior that would be used after loading persisted `/etc/seaweedfs/filer.conf`.

## Dependencies and Integration Points
Uses `filer_pb.FilerConf`, `reflect`, and `testify/assert`. Protects storage-rule consumers such as volume assignment, deletion, and quota enforcement.

## Risks
Reflection clone test requires every exported field in the fixture to be non-zero; new protobuf fields will fail until test data and `ClonePathConf` are updated, which is intentional. Merge clearing semantics are not tested beyond read-only inheritance.

## Test Signals
Good guard against missing clone fields and basic prefix trie behavior. No coverage for malformed JSON, failover reads, or concurrent config updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_conf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_delete_entry.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_delete_entry.go

## Purpose
Coordinates deletion of filer metadata, associated chunks, remote objects, hard link metadata, and bucket collections.

## Important APIs and Types
`DeleteEntryMetaAndData` is the public deletion entry point. `doBatchDeleteFolderMetaAndData` recursively deletes directory children. `doDeleteEntryMetaAndData` deletes a single entry. `DoDeleteCollection` asks the master to delete a collection. `maybeDeleteHardLinks` removes hard-link KV records. Callback types `OnChunksFunc` and `OnHardLinkIdsFunc` allow child traversal to collect cleanup work.

## Control Flow and State
Deletion loads the entry, honors `ifNotModifiedAfter`, detects buckets, recursively deletes children when needed, deletes the entry itself, then schedules chunk deletion unless hard links still reference data. Folder deletion pages through children, rejects non-recursive non-empty deletes, optionally deletes remote child objects, sends metadata notifications, collects chunks, deletes all folder children from the store, and notifies for the directory.

## Persistence Behavior
Metadata removal is synchronous through the store. Chunk deletion is asynchronous via `DeleteChunks`. Remote object deletion occurs before local metadata deletion for local-origin events. Bucket deletion calls the master collection-delete RPC.

## Dependencies and Integration Points
Uses `FindEntry`, `ListDirectoryEntries`, `Store.DeleteFolderChildren`, `Store.DeleteOneEntry`, `maybeDeleteFromRemote`, `NotifyUpdateEvent`, hard-link KV cleanup, and master collection deletion.

## Risks
Remote deletion happens before local metadata deletion, so a later local store failure can leave remote data removed but metadata still present. Recursive delete error handling depends on `ignoreRecursiveError`. Hard-link deletion has a noted collection limitation. Bucket deletion relies on `IsBucket` and store bucket-drop capability.

## Test Signals
Remote deletion behavior and failure ordering are covered by `filer_lazy_remote_test.go`. Generic non-empty folder and hard-link edge cases are less directly covered in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_delete_entry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_deletion.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_deletion.go

## Purpose
Runs asynchronous deletion of volume file IDs and retries transient failures with bounded exponential backoff.

## Important APIs and Types
`DeletionRetryItem`, `retryHeap`, and `DeletionRetryQueue` implement retry state. Constants define max attempts, delays, polling intervals, and batch sizes. Key methods are `AddOrUpdate`, `RequeueForRetry`, `GetReadyItems`, `Remove`, `Size`, `loopProcessingDeletion`, `processDeletionBatch`, `deleteFilesAndClassify`, `classifyDeletionOutcome`, `loopProcessingDeletionRetry`, `processRetryBatch`, `DeleteChunks`, `doDeleteChunks`, and `deleteChunksIfNotNew`.

## Control Flow and State
`NewFiler` starts `loopProcessingDeletion`. The loop consumes file IDs from an unbounded queue every 1123 ms, deduplicates batches, deletes through volume lookup, classifies each file ID, and adds retryable or missing-result failures to `DeletionRetryQueue`. A separate retry loop polls ready items every minute and requeues retryable failures until `MaxRetryAttempts` is exceeded.

## Persistence Behavior
Retry state is explicitly in-memory only and lost on filer restart. The durable metadata deletion has usually already occurred; this file handles eventual volume garbage cleanup. Manifest chunks are resolved before enqueuing data chunks plus manifest chunk IDs.

## Dependencies and Integration Points
Uses master volume lookup, `operation.DeleteFileIdsWithLookupVolumeId`, volume server delete results, storage deleted errors, filer config rules (`DisableChunkDeletion`), and chunk manifest resolution.

## Risks
In-memory retry queue can lose cleanup work after restart. Retryable classification is string-pattern based and brittle. `DeleteChunksNotRecursive` does not resolve manifests. Failed manifest resolution logs but still enqueues the manifest ID. Very large deletion batches can produce operational load.

## Test Signals
`filer_deletion_test.go` covers queue ordering, backoff, overflow protection, max attempts, retryable string matching, and duplicate file IDs. It does not mock volume server deletion classification in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_deletion.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_deletion_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_deletion_test.go

## Purpose
Unit tests the deletion retry queue and retryability classifier.

## Important APIs and Functions
Tests cover `NewDeletionRetryQueue`, `AddOrUpdate`, `GetReadyItems`, `RequeueForRetry`, `calculateBackoff`, `isRetryableError`, heap ordering, max attempts, overflow protection, and duplicate handling.

## Control Flow and State
The tests directly mutate queue internals under lock where needed to force readiness or heap order. They verify that newly added items are not immediately ready, backoff doubles and caps, max attempts are discarded after the final retry, and duplicate adds update the error without incrementing retry count.

## Persistence Behavior
No persistence. The tests exercise the in-memory queue, matching the production limitation documented in `filer_deletion.go`.

## Dependencies and Integration Points
Uses `container/heap`, `time`, and package retry constants. It protects the async deletion loop's failure handling but does not invoke actual volume deletion.

## Risks
Timing assertions allow 100 ms variance and could be sensitive on extremely slow CI. Because tests reach into unexported fields, internal representation changes require test updates.

## Test Signals
Good signal for queue mechanics and retry classifier strings. Missing signal for `processDeletionBatch`, `deleteFilesAndClassify`, manifest deletion, and integration with `fileIdDeletionQueue`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_deletion_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_hardlink.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_hardlink.go

## Purpose
Defines the hard-link ID marker and generator used by filer entries that share chunk/attribute state.

## Important APIs and Types
`HARD_LINK_MARKER` is byte `0x01`. `HardLinkId` is a byte slice documented as 16 random bytes plus marker byte. `NewHardLinkId` returns random bytes with the marker appended.

## Control Flow and State
The generator has no inputs. It uses `util.RandomBytes(16)` and appends the marker.

## Persistence Behavior
The ID is persisted in entry metadata and used as a KV key by `filerstore_hardlink.go` to store shared attributes and chunks.

## Dependencies and Integration Points
Integrated with `FilerStoreWrapper` hard-link read/write/delete and inode derivation in `filer_inode.go`.

## Risks
The type is mutable because it is a byte slice. Callers should avoid modifying IDs after persistence. Random collision risk is negligible but not checked here.

## Test Signals
Hard-link inode sharing is covered in `filer_inode_test.go`; hard-link KV counter behavior is not directly tested in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_hardlink.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_inode.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_inode.go

## Purpose
Backfills stable inode values for filer entries so persisted metadata aligns with FUSE derivation and hard-link identity.

## Important APIs and Functions
`ensureEntryInode(entry *Entry)` is a `Filer` method that sets `entry.Attr.Inode` if it is zero.

## Control Flow and State
Nil entries and entries with an inode are left untouched. Missing creation time is set to `time.Now()`. Hard-linked entries hash the `HardLinkId`; ordinary entries use `FullPath.AsInode(crtime.Unix())`.

## Persistence Behavior
The computed inode is persisted when the caller later inserts or updates the entry. This avoids needing a separate reverse inode index.

## Dependencies and Integration Points
Called from `CreateEntry`, parent directory auto-creation, and `UpdateEntry` when legacy entries lack inodes. Uses `util.HashStringToLong` and `util.FullPath.AsInode`.

## Risks
For non-hard-linked entries, inode changes if the path and creation time combination changes before persistence. Missing crtime uses wall clock, so legacy backfill is deterministic only after first persistence. Hard-link IDs must remain stable.

## Test Signals
`filer_inode_test.go` verifies FUSE-equivalent derivation, shared hard-link inode, create-time inode assignment, parent directory assignment, update preservation, and legacy backfill.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_inode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_inode_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_inode_test.go

## Purpose
Tests inode derivation and persistence behavior for filer entries, parents, updates, and hard links.

## Important APIs and Functions
Tests call `ensureEntryInode`, `CreateEntry`, and `UpdateEntry`. `newTestFilerWithStubStore` creates a filer with the shared stub store from lazy remote tests.

## Control Flow and State
The tests validate deterministic path/crtime derivation, hard-link ID hashing, assignment during creation, recursive parent auto-creation, update rejection when changing file to directory, preservation of existing inode, and backfilling legacy zero inode.

## Persistence Behavior
The stub store persists entries in memory, allowing assertions on stored inode values after create/update.

## Dependencies and Integration Points
Uses `NewFiler`, `NewFilerStoreWrapper`, the stub store, `util.FullPath`, `pb.ServerDiscovery`, and testify assertions. It connects inode code to the real create/update paths rather than only testing the helper.

## Risks
Relies on stub store behavior from another test file in the same package; changes to that stub can affect this test. Does not cover rename inode preservation.

## Test Signals
Strong coverage for inode assignment and preservation. Missing coverage for concurrent creates, hard-link KV updates, and rename/move paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_inode_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote.go

## Purpose
Implements lazy remote object lookup and remote deletion for filer paths mapped to remote storage mounts.

## Important APIs and Types
`lazyFetchContextKey` prevents recursion. `maybeLazyFetchFromRemote` stats a remote object on local store miss and persists a local `Entry`. `maybeDeleteFromRemote` deletes remote files or directories for local-origin metadata deletes.

## Control Flow and State
Lazy fetch first checks recursion guard, remote storage availability, mount mapping, and client resolution. It maps filer path to remote location, uses singleflight keyed by path, calls `StatFile`, builds an entry with remote metadata, and persists it with a timeout context marked to skip recursive lazy fetch. Store write failure still returns the in-memory entry and forgets the singleflight key for retry. Remote delete skips nil/non-mounted entries, resolves the named client, maps path, and calls `RemoveDirectory` or `DeleteFile`.

## Persistence Behavior
Lazy fetch writes metadata into the filer store via `CreateEntry`; it does not copy file content locally. Delete removes remote object before local metadata deletion through callers in `filer_delete_entry.go`.

## Dependencies and Integration Points
Uses `FilerRemoteStorage`, remote storage clients, `remote_pb.RemoteStorageLocation`, `singleflight`, `CreateEntry`, and delete paths. `FindEntry` invokes lazy fetch when the store misses.

## Risks
Availability-over-consistency behavior can return entries that were not persisted. Remote errors except client resolution are swallowed on fetch. Delete-before-metadata ordering can remove remote data even if local metadata deletion later fails. Context is decoupled for persistence with a fixed 30 second timeout.

## Test Signals
`filer_lazy_remote_test.go` covers fetch hits, not-under-mount, not found, persist failure, longest prefix, recursion guard, `FindEntry` integration, and many delete paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote_listing.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote_listing.go

## Purpose
Populates local directory metadata from a remote storage listing when a mounted directory has an enabled listing cache TTL.

## Important APIs and Types
`xattrRemoteListingSyncedAt` stores last listing sync time. `lazyListContextKey` prevents recursion. `maybeLazyListFromRemote` performs TTL-gated remote listing and persistence. `updateDirectoryListingSyncedAt` records the cache timestamp on the directory entry.

## Control Flow and State
The function skips recursive contexts, missing remote storage, unmapped paths, and mounts with `ListingCacheTtlSeconds <= 0`. It reads the local directory xattr directly from the store; if fresh, it returns. It then singleflights by directory, maps the path to remote, lists remote children, skips local-only entries, updates existing remote-backed entries while preserving local chunks/attrs, creates missing entries, and updates the synced-at xattr.

## Persistence Behavior
Writes or updates filer metadata only. Directory timestamps and remote file sizes/mtimes are stored locally; file content remains remote. Listing errors are logged and swallowed.

## Dependencies and Integration Points
Called at the start of directory listing in `filer.go`. Integrates with remote storage client `ListDirectory`, `CreateEntry`, direct store updates, xattrs, and lazy fetch recursion guards.

## Risks
Stale remote deletions are not removed from local metadata in this code. Existing local-only entries are deliberately preserved, which can mask remote changes with the same name. Errors are swallowed, so callers cannot distinguish stale from fresh listings. `context.WithoutCancel` preserves work after callers leave.

## Test Signals
Tests cover population, disabled TTL, TTL cache skip, not-under-mount, preserving local-only entries, merging remote-backed entries while preserving local fields, and recursion guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote_listing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote_test.go

## Purpose
Comprehensive unit tests for lazy remote fetch, remote-aware deletion, and lazy remote directory listing.

## Important APIs and Types
Defines `stubFilerStore`, `stubRemoteClient`, `stubClientMaker`, `countingRemoteClient`, `newTestFiler`, and `registerStubMaker`. Tests target `maybeLazyFetchFromRemote`, `FindEntry`, `DeleteEntryMetaAndData`, `doDeleteEntryMetaAndData`, and `maybeLazyListFromRemote`.

## Control Flow and State
The stub store maintains entries and KV maps with a mutex. Stub remote clients record delete/remove/list calls. Tests register temporary remote client makers by storage type, map directories to remote storage locations, and assert store/remote side effects.

## Persistence Behavior
In-memory store persistence verifies lazy fetch writes local metadata, remote delete failure ordering, local delete failure preservation, lazy listing entry creation/update, and xattr-based TTL caching.

## Dependencies and Integration Points
Exercises `FilerRemoteStorage`, `NewFilerStoreWrapper`, `wdclient.MasterClient`, `log_buffer`, remote storage client registry, and delete/list/fetch methods.

## Risks
Stubs do not model real remote latency, pagination, credentials, or failures beyond configured errors. Several tests share global remote client maker state but restore it with cleanup functions.

## Test Signals
Strong signal for lazy remote behavior: longest-prefix mount matching, recursion guards, fetch-on-miss integration, remote delete skipping for replicated events, keeping metadata on remote/client/local delete failures, not-found tolerance, recursive directory delete, lazy listing TTL, local-only preservation, and remote metadata merge. It does not cover remote listing deletion reconciliation or concurrent singleflight behavior under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_notify.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_notify.go

## Purpose
Builds and logs metadata change events, sends optional notifications, triggers local empty-folder cleanup, flushes metadata logs to filer storage, and reads persisted log buffers.

## Important APIs and State
`NotifyUpdateEvent`, `notifyUpdateEvent`, `newMetadataEvent`, `logMetaEvent`, `triggerLocalEmptyFolderCleanup`, `logFlushFunc`, `isChunkNotFoundError`, and `ReadPersistedLogBuffer` are the main APIs. `persistedLogReplaySem` caps concurrent persisted log replays at 64.

## Control Flow and State
Notification skips suppressed contexts, nil events, and system log paths. It appends the local filer signature if absent, builds a `SubscribeMetadataResponse`, optionally sends to `notification.Queue`, adds serialized data to `LocalMetaLogBuffer`, records test/instrumentation sinks, and updates empty-folder cleanup. Flush writes buffered data to `/topics/...`-style system log files by appending chunks until success.

## Persistence Behavior
Metadata events persist through log buffer flushes to filer entries. `ReadPersistedLogBuffer` replays these logs using `collectPersistedLogBuffer`, a readahead goroutine, and visitor close cleanup. Missing chunks/volumes during persisted replay can be skipped by lower iterator code.

## Dependencies and Integration Points
Uses protobuf marshaling, `notification.Queue`, `log_buffer`, filer append/upload, system log constants, empty-folder cleanup, persisted log readers, HTTP not-found errors, and context metadata-event suppression/sinks.

## Risks
`logFlushFunc` retries forever with sleep, which can stall shutdown or hide persistent write failures. Signatures prevent loops but rely on correct propagation. Readahead goroutine must be stopped on all returns; code explicitly does this. System log path filtering suppresses events below `SystemLogDir`.

## Test Signals
`filer_notify_test.go` checks protobuf preservation of chunk `SourceFileId`. Persisted replay behavior likely has tests elsewhere; this subset provides limited direct coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_notify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_notify_append.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_notify_append.go

## Purpose
Uploads flushed metadata log data as SeaweedFS file chunks and appends them to a system-log filer entry.

## Important APIs and Functions
`appendToFile(targetFile string, data []byte) error` assigns/uploads bytes and updates the target filer entry. `assignAndUpload` performs volume assignment and HTTP upload.

## Control Flow and State
Append first uploads data to a volume, then finds or creates the filer entry at `targetFile`, computes append offset from `TotalSize`, appends a protobuf file chunk from upload result, and calls `CreateEntry` to persist metadata. Assignment uses storage rules from `FilerConf`, overridden by `metaLogCollection` and `metaLogReplication`.

## Persistence Behavior
Data is persisted to a volume before metadata is updated. Metadata is stored as a filer entry under the system log path. If metadata update fails after upload, the uploaded chunk may become unreferenced until deletion/cleanup.

## Dependencies and Integration Points
Used by `logFlushFunc` in `filer_notify.go`. Integrates with master volume assignment, operation uploader, filer storage rules, chunk metadata conversion, and `CreateEntry`.

## Risks
Uses `context.Background`, so caller cancellation is ignored. Upload-before-metadata ordering can leak chunks on failure. Append offset relies on current chunk metadata and no concurrent append conflict; log buffer flushing likely serializes per file but this function itself has no lock.

## Test Signals
No direct test in this subset. Notification replay tests indirectly depend on successfully persisted log entries in integration scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_notify_append.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_notify_read.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_notify_read.go

## Purpose
Lists and reads persisted metadata log files in timestamp order across multiple filers, with chunk-level caching and streaming fallback.

## Important APIs and Types
`LogFileEntry`, `collectPersistedLogBuffer`, `CollectLogFileRefs`, `HasPersistedLogFiles`, `LogEntryItemPriorityQueue`, `OrderedLogVisitor`, `LogFileEntryCollector`, `LogFileQueueIterator`, and `LogFileIterator` are the core pieces.

## Control Flow and State
Collection lists day directories from `SystemLogDir`, then hour-minute log files. `OrderedLogVisitor` maintains one iterator per filer and a min-heap of next log entries by timestamp. `LogFileEntryCollector` incrementally enqueues more day/hour files. `LogFileQueueIterator` advances across files and skips unreadable deleted chunks. `LogFileIterator` first decodes immutable chunks through a shared cache; if a chunk is incomplete because records cross chunk boundaries, it falls back to streaming the whole file.

## Persistence Behavior
Reads persisted filer entries and their chunks; does not modify state. `CollectLogFileRefs` exposes chunk references without reading volume data for clients that can fetch directly.

## Dependencies and Integration Points
Uses filer directory listing, `NewChunkStreamReaderFromFiler`, persisted-log cache, protobuf log entry decoding, master client chunk reads, system log naming conventions, and `log_buffer.MessagePosition`.

## Risks
Ordering is per-entry timestamp with per-filer iterators; clock skew can still affect global semantics. Directory listing uses `context.Background` in collector paths, so caller cancellation is not consistently propagated. Chunk cache correctness depends on immutable log chunks. Invalid file names are skipped.

## Test Signals
No dedicated tests in the listed subset. `filer_notify.go` replay path depends on this code, and `isChunkNotFoundError` handles operational deletion races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_notify_read.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_notify_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_notify_test.go

## Purpose
Tests protobuf marshal/unmarshal preservation for metadata event notifications containing chunk metadata.

## Important APIs and Functions
`TestProtoMarshal` builds an `Entry`, converts it to protobuf, embeds it in `filer_pb.EventNotification`, marshals and unmarshals it, and checks `SourceFileId`.

## Control Flow and State
The test has only in-memory protobuf state. It prints the marshaled bytes after validating the important field.

## Persistence Behavior
No persistence. It protects serialized notification payload shape used by log buffers and external notifications.

## Dependencies and Integration Points
Uses `proto.Marshal`, `filer_pb.EventNotification`, `Entry.ToProtoEntry`, and chunk metadata fields used by filer sync.

## Risks
Only one field is asserted. The print statement is noisy in test output. It does not cover full `SubscribeMetadataResponse`, signatures, delete flags, or event replay.

## Test Signals
Narrow but useful signal that `SourceFileId` survives notification serialization, important for cross-cluster chunk delta logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_notify_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_on_meta_event.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_on_meta_event.go

## Purpose
Handles metadata events after local or remote processing, reloading configuration, notifying bucket-aware stores, and updating empty-folder cleanup state.

## Important APIs and Functions
`onMetadataChangeEvent` dispatches to specialized handlers. `onBucketEvents` maps create/delete/rename events under `DirBucketsPath` to store bucket callbacks. `onEmptyFolderCleanupEvents` mirrors creates/deletes/renames to the cleaner. `maybeReloadFilerConfiguration`, `readEntry`, `reloadFilerConfiguration`, `LoadFilerConf`, `LoadRemoteStorageConfAndMapping`, and `maybeReloadRemoteStorageConfigurationAndMapping` handle config reload paths.

## Control Flow and State
Config reload triggers only for events touching `/etc/seaweedfs` and new entry named `filer.conf`. Reload reads inline content or chunks and replaces `f.FilerConf`. Bucket events use event directory and `NewParentPath` to detect create/delete/rename into or out of bucket root. Empty-folder cleanup uses event timestamps.

## Persistence Behavior
This file primarily reads persisted config chunks and mutates in-memory `FilerConf`/remote config state. Store bucket callbacks may create/drop backend bucket structures depending on implementation.

## Dependencies and Integration Points
Uses filer protobuf event helpers, `StreamContent`, `FilerConf`, remote storage config loading, empty-folder cleanup, and `VirtualFilerStore` bucket callbacks.

## Risks
Remote storage reload is marked FIXME and not implemented for events. A typo in a log message is harmless. Config reload errors leave existing config in place. Bucket event correctness depends on metadata event directory fields.

## Test Signals
`filer_on_meta_event_test.go` covers rename into bucket root creating a bucket. Config reload and empty-folder event handling are not directly tested in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_on_meta_event.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_on_meta_event_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_on_meta_event_test.go

## Purpose
Tests bucket event handling for a rename into the bucket root.

## Important APIs and Types
Defines `bucketTrackingStore`, a minimal `FilerStore` plus `BucketAware` implementation recording created/deleted bucket names. `TestOnBucketEventsRenameIntoBucketsRootCreatesBucket` calls `onBucketEvents`.

## Control Flow and State
The test creates a filer with `DirBucketsPath` `/buckets`, sends a rename-like metadata response with old directory `/tmp` and `NewParentPath` `/buckets`, and asserts one bucket creation and no deletion.

## Persistence Behavior
No persistence. The tracking store records events in slices.

## Dependencies and Integration Points
Uses `NewFilerStoreWrapper`, `filer_pb.SubscribeMetadataResponse`, and package bucket event code. It validates wrapper forwarding of bucket callbacks to bucket-aware stores.

## Risks
The test models event shape manually; it does not assert `filer_pb.IsRename` construction from a real rename path. Other create/delete/rename-out cases are not tested.

## Test Signals
Useful regression for renamed directories becoming buckets when moved into the S3 bucket root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_on_meta_event_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_rename.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_rename.go

## Purpose
Validates whether a rename or move is allowed with respect to self-subdirectory moves and bucket boundaries.

## Important APIs and Functions
`CanRename(ctx, source, target, oldName) error` checks a candidate rename. `DetectBucket(source util.FullPath) string` extracts the bucket name from a path below `DirBucketsPath`.

## Control Flow and State
`CanRename` builds the full source path, rejects moving a directory under itself, loads the source entry, rejects renaming a bucket directory itself, detects source and target buckets, and rejects cross-bucket moves.

## Persistence Behavior
No writes. It reads source metadata through `FindEntry`.

## Dependencies and Integration Points
Uses bucket detection, `FindEntry`, and `util.FullPath.Child`. It protects S3 collection boundaries and directory move safety before actual rename logic elsewhere.

## Risks
The self-subdirectory check uses string prefix, which can overmatch paths such as `/foo` and `/foobar` unless path formatting prevents it. It requires `FindEntry` before bucket check, so lazy remote fetch or TTL side effects can occur.

## Test Signals
No direct tests in this subset. Bucket event tests cover related but not pre-rename validation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_rename.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_search.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_search.go

## Purpose
Implements directory listing with pagination, prefix filtering, glob include/exclude matching, and expired-entry refill.

## Important APIs and Functions
`splitPattern` extracts the literal prefix before `*` or `?`. `ListDirectoryEntries` materializes results and has-more state. `CountDirectoryEntries` counts up to a limit. `StreamListDirectoryEntries` streams entries through callbacks. `doListPatternMatchedEntries` applies glob filters. `doListValidEntries` refills listings after expired entries are skipped/deleted.

## Control Flow and State
Limits are capped to `math.MaxInt32 - 1`. Name patterns can contribute a prefix for efficient listing. Listing asks for `limit+1` to compute `hasMore`. Pattern filtering increments `missedCount` for skipped entries, then repeats listing to fill the requested count after misses.

## Persistence Behavior
This file delegates to `doListDirectoryEntries`, which may delete expired metadata and chunks. The search layer itself does not write.

## Dependencies and Integration Points
Uses `filepath.Match`, store listing through `doListDirectoryEntries`, TTL cleanup behavior in `filer.go`, and `util.FullPath` path normalization.

## Risks
For pattern matching, `nameToTest[len(prefix):]` assumes the entry name is at least as long as the prefix and aligned with listing prefix. Refill loops depend on `missedCount` and `lastFileName` moving forward to avoid repeated scans. Prefix and name pattern are documented as mutually exclusive but code allows prefix derived from pattern.

## Test Signals
No direct tests in this subset. Listing behavior is indirectly exercised by lazy listing and deletion tests through the stub store.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_search.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filerstore.go

## Purpose
Defines the storage backend interface for filer metadata and common backend capability/error contracts.

## Important APIs and Types
`FilerStore` requires initialization, CRUD, recursive child deletion, paged listing, prefixed listing, transactions, KV operations, and shutdown. `ListEachEntryFunc` is the listing callback. `BucketAware` adds bucket lifecycle callbacks and whole-bucket drop capability. `Debuggable` adds debug output. Constants/errors include `CountEntryChunksForGzip`, `ErrUnsupportedListDirectoryPrefixed`, `ErrUnsupportedSuperLargeDirectoryListing`, `ErrKvNotImplemented`, and `ErrKvNotFound`.

## Control Flow and State
This file has no implementation logic; it defines contracts implemented by backend packages and wrapped by `FilerStoreWrapper`.

## Persistence Behavior
Backends implementing this interface own metadata and KV persistence. KV is also used for filer store ID and hard-link state.

## Dependencies and Integration Points
All filer metadata operations depend on this interface. Store wrappers add metrics, path routing, hard-link handling, and context behavior.

## Risks
Interface semantics are broader than Go types express: `FindEntry` should return `filer_pb.ErrNotFound`, listings should be sorted/paged consistently, transaction behavior should match backend guarantees, and KV support is expected for some features.

## Test Signals
Wrapper tests and stubs exercise selected interface behavior. Backend-specific correctness is outside this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore_hardlink.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filerstore_hardlink.go

## Purpose
Implements hard-link metadata storage on top of the filer store wrapper's KV API.

## Important APIs and Functions
`handleUpdateToHardLinks` writes new hard-link state and removes old link state when an entry changes hard-link ID. `setHardLink` serializes attributes/chunks to KV under `HardLinkId`. `maybeReadHardLink` hydrates entry attributes/chunks from KV. `DeleteHardLink` decrements link count, updates ctime, rewrites KV, or deletes the KV record when count reaches zero.

## Control Flow and State
Directories are skipped. Insert/update writes shared blob when `HardLinkId` is set, then checks existing entry to remove an old hard-link record if ID changed. Reads transparently replace entry attributes/chunks from KV. Deletes skip hard-link counter changes when context `OP` is `MV`, preserving counts during moves.

## Persistence Behavior
Hard-link shared state persists in the default store KV namespace. Directory entries still persist separately with their `HardLinkId`; chunk metadata is shared via encoded blob.

## Dependencies and Integration Points
Called by `FilerStoreWrapper` insert/update/find/list/delete methods. Uses `Entry.EncodeAttributesAndChunks`, `DecodeAttributesAndChunks`, KV operations, and `ErrKvNotFound`.

## Risks
KV consistency is critical; if KV updates fail or are not transactional with entry updates, link counters and entry metadata can diverge. `maybeReadHardLink` returns errors but wrapper callers often ignore the returned error, potentially leaving partial entries. Context string key `OP` is untyped.

## Test Signals
No direct hard-link KV tests in this subset. Inode tests cover hard-link inode derivation only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore_hardlink.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore_translate_path.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filerstore_translate_path.go

## Purpose
Adapts a filer store to serve a mounted subtree by translating paths between global filer paths and backend-local paths.

## Important APIs and Types
`FilerStorePathTranslator` wraps an actual store plus `storeRoot`. `NewFilerStorePathTranslator` normalizes roots. `translatePath`, `changeEntryPath`, and `recoverEntryPath` handle path conversion. The type implements all `FilerStore` methods.

## Control Flow and State
For non-root store roots, global paths have the store root prefix stripped before backend calls. Entry-mutating methods temporarily rewrite `entry.FullPath`, defer recovery, and call the backend. Find/list methods translate returned entry paths back to global paths.

## Persistence Behavior
The underlying store persists local translated paths, not the global filer prefix. KV and transaction calls pass through unchanged.

## Dependencies and Integration Points
Used by `FilerStoreWrapper.AddPathSpecificStore` to route subtrees to separate backend stores. Depends on consistent prefix matching from the wrapper.

## Risks
Path slicing assumes inputs are under `storeRoot`; misuse can panic or corrupt paths. Mutating entries in place can surprise callers if recovery is skipped by panic. KV namespace is shared with the actual store and not root-prefixed.

## Test Signals
No direct tests in this subset. Wrapper tests cover some wrapper behavior but not path translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore_translate_path.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore_wrapper.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filerstore_wrapper.go

## Purpose
Adds routing, metrics, hard-link handling, MIME normalization, context policy, bucket callbacks, and prefix-list fallback around a `FilerStore`.

## Important APIs and Types
`VirtualFilerStore` extends `FilerStore` with hard-link, direct-delete, path-specific store, bucket, and store-comparison methods. `FilerStoreWrapper` stores a default backend, path prefix trie, store ID map, and fast-path flag. Methods implement CRUD/list/KV/transaction wrappers plus `AddPathSpecificStore`, `getActualStore`, `SameActualStore`, `normalizeEntryMimeForStore`, and `prefixFilterEntries`.

## Control Flow and State
Writes first check `ctx.Err()`, then strip cancellation before backend calls so active writes are not interrupted after admission. Reads strip cancellation without rejecting, allowing cleanup/recovery reads to complete. Insert/update serialize chunks, normalize file MIME, update hard-link KV, record metrics, and call actual store. Find/list hydrate hard links and deserialize chunks. Prefix-list fallback scans ordinary listing and filters names when a backend lacks native prefix listing.

## Persistence Behavior
Persists entries through selected actual store. Hard-link data and filer store ID KV go through the default store. Path-specific stores persist translated paths via `FilerStorePathTranslator`.

## Dependencies and Integration Points
Used by `Filer.SetStore` and most filer metadata operations. Integrates with stats, `ptrie`, hard-link helpers, protobuf chunk serialization hooks, and `BucketAware` stores.

## Risks
Context policy is subtle: canceled writes are rejected, but backend operations ignore later cancellation. Hard-link errors during delete are logged but deletion continues to prevent undeletable directories. Prefix fallback can scan extra pages and depends on sorted listing. `FindEntry` converts some missing table errors to not-found only for bucket-droppable stores.

## Test Signals
`filerstore_wrapper_test.go` covers MIME normalization, write rejection on canceled/deadline contexts, active write success, read success with canceled contexts, and rollback success with canceled contexts. Path-specific routing, metrics, prefix fallback, and hard-link KV are not directly tested here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore_wrapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore_wrapper_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filerstore_wrapper_test.go

## Purpose
Tests selected `FilerStoreWrapper` behavior around MIME normalization and context cancellation policy.

## Important APIs and Functions
`TestFilerStoreWrapperMimeNormalization`, `cancelledCtx`, `expiredCtx`, `TestFilerStoreWrapperWriteOpsRejectCancelledContext`, `TestFilerStoreWrapperWriteOpsSucceedWithActiveContext`, `TestFilerStoreWrapperReadOpsSucceedWithCancelledContext`, and `TestFilerStoreWrapperRollbackSucceedsWithCancelledContext`.

## Control Flow and State
Tests use the stub store, wrap it, run operation tables, and assert errors or persisted state. Write operation tests cover insert, insert-known-absent, update, delete, delete-one, delete-folder-children, transaction begin/commit, KV put/delete. Read tests verify find and KV get ignore canceled contexts.

## Persistence Behavior
In-memory stub store records entries and KV values, proving wrapper behavior before backend persistence.

## Dependencies and Integration Points
Uses `NewFilerStoreWrapper`, `Entry`, stub store, context cancellation/deadline, and testify assertions. It codifies the wrapper's policy used by all filer metadata operations.

## Risks
Does not cover path-specific stores, prefix fallback, bucket callbacks, hard-link hydration/deletion, or metrics. `TestFilerStoreWrapperWriteOpsSucceedWithActiveContext` reuses one path across operations in a way that depends on forgiving stub semantics.

## Test Signals
Strong signal for cancellation contracts and MIME normalization: files strip `application/octet-stream`, directories keep it, writes reject already-bad contexts, reads and rollback remain cleanup-friendly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore_wrapper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/foundationdb/doc.go -->
# sources/distributed-fs/seaweedfs/weed/filer/foundationdb/doc.go

## Purpose
Package documentation for the FoundationDB filer store backend.

## Important APIs and Types
No APIs are declared beyond package `foundationdb`. The comment states that the package provides a FoundationDB-based filer store using FDB's directory layer and key-value interface.

## Control Flow and State
No runtime control flow in this file.

## Persistence Behavior
Documents that persistence is backed by FoundationDB, a distributed ACID key-value database. Actual store behavior is implemented in other files not included in this subset.

## Dependencies and Integration Points
The comment references `github.com/apple/foundationdb/bindings/go/src/fdb` and notes that FoundationDB client libraries must be installed. It is compiled only with `go build -tags foundationdb`.

## Risks
Operational dependency on native FoundationDB client libraries and build tags. This doc file alone does not enforce build constraints.

## Test Signals
No tests in this file. Backend-specific tests are outside this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/foundationdb/doc.go -->

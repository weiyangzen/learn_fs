# subset-b-009581 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/dir_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/dir_test.go

## Purpose

This Go test suite exercises the non-HNS `DirInode` behavior in `gcsfuse/internal/fs/inode`. It validates how directory inodes resolve children from GCS object names, combine explicit directory marker objects with implicit-directory prefixes, expose FUSE dirents and `Core` records, mutate bucket contents, manage local unsynced child files, update type-cache state, and control list-cache invalidation. It is a high-signal regression suite for the directory layer that maps flat GCS object namespace semantics onto filesystem directory operations.

## Important APIs, Types, And Helpers

`DirTest` holds a context, `gcsx.SyncerBucket`, simulated clock, locked `DirInode`, and `metadata.TypeCache`. `resetInode` and `resetInodeWithTypeCacheConfigs` recreate a `NewDirInode` with configurable implicit dirs, nonexistent-type caching, managed-folder listing, cache size, and TTL. Helper methods `readAllEntries`, `readAllEntryCores`, `setSymlinkTarget`, `createLocalFileInode`, and `validateCore` drive repeated behaviors. The suite also defines `DirentSlice` for deterministic sorting of FUSE directory entries.

The tests cover public `DirInode` APIs including `ID`, `Name`, `Attributes`, `LookUpChild`, `ReadDescendants`, `ReadEntries`, `ReadEntryCores`, `CreateChildFile`, `CloneToChildFile`, `CreateChildSymlink`, `CreateChildDir`, `DeleteChildFile`, `DeleteChildDir`, `DeleteObjects`, `CreateLocalChildFileCore`, `LocalFileEntries`, `InsertFileIntoTypeCache`, `EraseFromTypeCache`, `ShouldInvalidateKernelListCache`, `InvalidateKernelListCache`, `Context`, and `Destroy`. They also reach into `dirInode.readObjectsUnlocked` and `dirInode.prefetcher` for behavior that is otherwise hard to observe.

## Control Flow And State Behavior

The central lookup flow tests priority among explicit directory marker objects (`name/`), regular files (`name`), symlink metadata on regular objects, conflict marker names, and implicit directories created by descendants. Explicit directory objects shadow regular files for normal lookup, while conflict-marker suffix lookup resolves the regular file side of a file/dir conflict. When `implicitDirs` is enabled, descendant objects can synthesize a directory `Core` without a backing `MinObject`; when disabled, those synthetic dirs are hidden.

Listing tests create a mix of explicit dirs, nonempty dirs, files, implicit dirs, symlinks, and unsupported paths. `ReadEntries` returns FUSE `Dirent` records and updates `prevDirListingTimeStamp`; `ReadEntryCores` returns typed `Core` records plus unsupported path prefixes. `readObjectsUnlocked` is tested with and without implicit dirs and with a start offset to ensure pagination/filtering logic remains stable while the inode lock is released.

Mutation tests verify creation with generation preconditions, cloning, symlink metadata including standard symlink content, deletion with generation/metageneration preconditions, recursive deletion of object subtrees, and local child file overlays. State persistence is mostly remote object state in the fake bucket, plus local in-memory inode state: lookup counts, type cache entries, local-file maps, list-cache timestamps, and lifecycle context cancellation.

## Dependencies And Integration Points

The suite uses `fake.NewFakeBucket`, `storageutil`, `gcsx.NewSyncerBucket`, `contentcache`, FUSE `fuseops`/`fuseutil`, `metadata.TypeCache`, `cfg.Config`, `semaphore.Weighted`, noop tracing/metrics, and `timeutil.SimulatedClock`. It implicitly tests integration between the inode layer and the storage layer's object create/update/delete/list semantics, including GCS generation preconditions and metadata-based symlink detection.

## Risks And Test Signals

Key risks covered are stale type-cache entries hiding a newly preferred object type until TTL expiry, incorrect precedence between file and directory objects, unsupported paths leaking into visible entries, local unsynced files appearing in the wrong parent, deletion incorrectly evicting or retaining cache state, and list-cache invalidation TTL regressions. Type-cache deprecation tests exercise a newer path that queries cached object data using `FetchOnlyFromCache` and falls back on cache misses. The tests do not execute real GCS behavior, so production risks remain around API pagination, managed folder support in real buckets, and concurrency under lock handoff.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/explicit_dir.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/explicit_dir.go

## Purpose

`explicit_dir.go` defines the inode wrapper used when a directory is backed by an explicit GCS object or folder and therefore has a stable source generation. It bridges the general `DirInode` interface with `GenerationBackedInode`-style behavior for directory markers, enabling the parent lookup layer to preserve generation/metageneration information for explicit directories.

## Important APIs, Types, And Functions

`ExplicitDirInode` embeds `DirInode` and adds `SourceGeneration() Generation`. `NewExplicitDirInode` accepts the same construction dependencies as `NewDirInode`, plus a `*gcs.MinObject` backing object. It creates a normal directory inode via `NewDirInode`, type-asserts the returned value to `*dirInode`, wraps it in `explicitDirInode`, and copies `Generation`, `MetaGeneration`, and `Size` from the supplied min object into an inode-local `Generation`.

`explicitDirInode` embeds `*dirInode` and stores the copied `generation`. `SourceGeneration` returns that stored value. `UpdateSize` is intentionally a no-op because directory inode size is not meaningful in this filesystem model.

## Control Flow And State Behavior

Construction delegates all directory behavior to `NewDirInode`: locking, lookup count, type cache, list behavior, context, and bucket dependencies are inherited from the wrapped `dirInode`. The only extra state is the immutable-looking `generation` snapshot captured at construction. If `m` is nil, the generation remains zero-valued, which is useful for callers that need an explicit-dir wrapper but lack source object generation metadata.

The wrapper does not update its generation after construction and does not persist anything itself. Persistence remains in the remote bucket directory marker object or HNS folder. `UpdateSize` deliberately avoids mutating state, preventing generic inode size update paths from changing directory generation-size bookkeeping.

## Dependencies And Integration Points

This file depends on `cfg.Config`, `gcsx.SyncerBucket`, `gcs.MinObject`, FUSE inode attributes, `timeutil.Clock`, and a metadata prefetch semaphore. It integrates directly with `NewDirInode` and with any caller that treats explicit directory objects as `GenerationBackedInode`s for delete/rename preconditions or conflict handling.

## Risks And Test Signals

The main risk is the unchecked `wrapped.(*dirInode)` assertion, which assumes `NewDirInode` always returns that concrete type. A future abstraction around `DirInode` construction would need to update this wrapper. Another risk is stale generation data if callers expect explicit directory generation to track later remote changes. Coverage is indirect through directory tests that validate explicit directory lookup, source generations for conflict cases, and directory deletion behavior; this file has no dedicated test file in the requested subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/explicit_dir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/file.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/file.go

## Purpose

`file.go` implements `FileInode`, the inode representation for regular GCS-backed or local-not-yet-synced files. It provides FUSE-facing file identity, attributes, reads, writes, truncation, mtime updates, flush/sync, lookup count handling, local unlink state, content cache integration, and streaming-write support. Its core job is to reconcile three states: the remote GCS source object (`src`), local staged temp-file content (`content`), and optional buffered streaming writes (`bwh`).

## Important APIs, Types, And Functions

`FileInode` stores dependencies (`SyncerBucket`, clocks, content cache, config, tracing, metrics, semaphores), immutable identity (`id`, `name`, base attrs), and mutable state guarded by `syncutil.InvariantMutex`. The important mutable fields are `src`, `content`, `local`, `unlinked`, `bwh`, `writeHandleCount`, MRD/kernel reader instances, and `lookupCount`.

`NewFileInode` initializes state, lookup counts, invariant checking, and either rapid-bucket multi-range downloader wrappers or a kernel range reader instance. `checkInvariants` enforces legal file names, non-local source-name matching, and temp-file invariants. `clobbered` stats GCS and compares `Generation` values; equal gen/metagen with larger remote size returns compare code `2` and is treated as a remote append clobber for sync but as an attribute size refresh in `Attributes`.

Read path functions include `openReader`, `ensureContent`, `Read`, and `CacheEnsureContent`. Write path functions include `Write`, `writeUsingTempFile`, `writeUsingBufferedWrites`, `flushUsingBufferedWriteHandler`, `SyncPendingBufferedWrites`, `Sync`, `Flush`, `syncUsingContent`, `Truncate`, and BWH initialization via `InitBufferedWriteHandlerIfEligible`/`areBufferedWritesSupported`.

## Control Flow And State Behavior

Reads are disallowed while streaming writes are in progress. Otherwise `Read` ensures local content exists, either from persistent content cache or a new temp file opened from the exact source generation, then reads from that temp file. Writes use BWH when available; otherwise they fault in temp content and write locally. Out-of-order streaming writes finalize the buffered object, record a fallback metric, then fall back to temp-file staging for the triggering write.

`Sync` and `Flush` are no-ops for clean files. With BWH, `Sync` only uploads pending buffers and may return a `MinObject` for zonal/rapid buckets; `Flush` finalizes and clears BWH. With staged content, `syncUsingContent` optionally fetches the latest GCS object, rejects clobbers, uploads via `SyncObject`, validates uploaded size, then updates `src`, reader wrappers, local/non-local state, and destroys temp content.

Attributes derive from base attrs plus source object metadata. `goog-reserved-file-mtime` is honored, then `gcsfuse_mtime` overrides it. Temp content and BWH state override size/mtime. Clobber checking can set `Nlink` to zero, or update inode size when only remote append size increased at the same generation. Local unlinked files also expose `Nlink` zero.

## Dependencies And Integration Points

The file integrates with `gcsx.SyncerBucket`, `gcs` requests/errors, `storageutil` object conversion, `contentcache`, `bufferedwrites`, `block` allocation limits, `kernel_readers`, `lru` MRD cache, `gcsfuse_errors.FileClobberedError`, `metrics`, `tracing`, FUSE attributes, and `cfg.WriteConfig`. It is a central dependency of file handle operations, directory-created local files, content cache paths, and rapid/zonal write semantics.

## Risks And Test Signals

Risks concentrate around clobber semantics, BWH lifecycle, generation-size comparison for zonal appends, local-file promotion after sync, temp-file cleanup, persistent content-cache invalidation, and reader wrapper min-object updates. There are also subtle differences between `Sync` and `Flush` for streaming writes and between rapid append versus overwrite metadata fetching. The requested test files cover read/write/truncate/mtime behavior, clobber errors, mock bucket request patterns, zonal versus non-zonal streaming writes, BWH fallback, local unlink handling, upload-size validation, and file-handle deregistration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/file_mock_bucket_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/file_mock_bucket_test.go

## Purpose

This suite tests `FileInode` against a testify mock bucket so it can assert exact storage calls and request choices that the fake bucket cannot expose. It focuses on clobber detection, forced metadata fetches, upload size validation, attribute refresh for remote appends, and streaming write initialization differences between zonal/rapid and regional buckets.

## Important APIs, Types, And Helpers

`FileMockBucketTest` owns a mock `storagemock.TestifyMockBucket`, simulated clock, optional backing `MinObject`, and locked `FileInode`. `createLockedInode` builds either a local file or an empty GCS-backed file using `gcsx.NewSyncerBucket`; for local files it creates an empty temp file immediately. `createGCSBackedFileInode` creates a locked non-local inode around a supplied min object for attributes-focused tests.

The test targets `Flush`, `Sync`, `Attributes`, and `InitBufferedWriteHandlerIfEligible`. It also reaches source generation state and uses `gcsfuse_errors.FileClobberedError` to classify failures.

## Control Flow And State Behavior

Local-file flush is expected to create an object without a preceding `StatObject`, because no remote source exists. Synced empty-file flush is expected to stat GCS first, including extended attributes, before creating/replacing the object. Upload size validation is checked by mocking `CreateObject` to return a size smaller than the temp-file size; `Flush` must fail and report the expected and actual sizes.

Clobber tests dirty an inode, then mock `StatObject` to return either the same generation/metageneration with larger size or a different generation. The first path models remote append at same generation and should become `FileClobberedError` with the remote-append message during sync. The second path validates classic generation/metageneration mismatch clobbering.

Attribute tests check the non-sync path where `Attributes(..., true)` sees remote size growth at the same generation. In that case the inode updates `src.Size` and `attrs.Size` rather than reporting `Nlink` zero. A no-change attribute test confirms a newer timestamp with same size/generation does not overwrite cached source attributes.

## Dependencies And Integration Points

The suite depends on `storagemock.TestifyMockBucket`, `mock.AnythingOfType` request matching, `storageutil`, `gcsx.SyncerBucket`, `contentcache`, `cfg.WriteConfig`, semaphores, noop tracing/metrics, and FUSE attrs. It complements fake-bucket tests by verifying storage call contracts and `FetchLatestGcsObject`/BWH initialization decisions.

## Risks And Test Signals

Important risks covered are accidental remote stat on local file flush, missing remote stat on synced-file overwrite, accepting partial uploads, treating remote append size growth as a normal sync, and fetching stale metadata for rapid append paths. The zonal append test asserts no `StatObject` for rapid appends, while zonal overwrite and regional writes must fetch metadata. Remaining risk is that mock expectations may not capture full request fields unless matched strictly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/file_mock_bucket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/file_streaming_writes_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/file_streaming_writes_test.go

## Purpose

This suite focuses on `FileInode` behavior when streaming writes are enabled through `bufferedwrites.BufferedWriteHandler`. It compares zonal/rapid buckets with non-zonal buckets, validates fallback from streaming to staged writes, and checks BWH lifecycle across write, sync, flush, truncate, unlink, and file-handle deregistration.

## Important APIs, Types, And Helpers

`FileStreamingWritesCommon` holds shared context, bucket, clock, backing object, and locked inode. `FileStreamingWritesTest` runs against a non-zonal fake bucket; `FileStreamingWritesZonalBucketTest` runs against a zonal fake bucket. `createInode` creates local or empty GCS-backed file inodes and installs a streaming write config. `createBufferedWriteHandler` calls `InitBufferedWriteHandlerIfEligible` and asserts BWH creation.

The suite directly exercises `IsUsingBWH`, `Write`, `Flush`, `Sync`, `SyncPendingBufferedWrites`, `Truncate`, `Attributes`, `SourceGeneration`, `SourceGenerationIsAuthoritative`, `Unlink`, and `DeRegisterFileHandle`. It defines `FakeBufferedWriteHandler` to force a generic BWH write error.

## Control Flow And State Behavior

Common tests verify BWH existence and reinitialization rules: flushing a zero-size object allows BWH to be created again, but flushing a nonzero object prevents streaming writes from being re-enabled for that object under the tested config. Negative truncation propagates an error.

Zonal tests assert source generation remains authoritative even while BWH exists, because zonal streaming writes can expose current object size through BWH and `SyncPendingBufferedWrites` may return a `MinObject`. Syncing pending writes in a zonal bucket promotes a local inode to non-local and updates `src.Size`. Non-zonal tests assert the opposite: pending BWH writes make source generation non-authoritative, `SyncPendingBufferedWrites` does not create a remote object, and `src.Size` remains unchanged until final flush.

Out-of-order write tests cover fallback. A sequential first write goes through BWH; an out-of-order second write finalizes current BWH data, clears BWH, creates staged temp content, and applies the second write through the temp-file path. Tests validate content holes, overwrites, mtime/size attributes, sync result, and clobber errors if the object is externally changed before fallback finalization.

## Dependencies And Integration Points

The suite uses fake GCS buckets, `gcsx.SyncerBucket`, `contentcache`, `bufferedwrites`, `gcsfuse_errors`, integration-test operations helpers, generated test strings, noop tracing/metrics, FUSE attrs, and semaphores. It is tightly integrated with `cfg.WriteConfig` and bucket type flags that decide rapid versus regional write behavior.

## Risks And Test Signals

Risks covered include BWH incorrectly surviving flush, staged fallback losing bytes or mtime, zonal sync failing to promote local files, non-zonal sync prematurely creating objects, unlink still uploading local data, clobbered flush overwriting remote state, and write-handle cleanup leaking BWH resources. The `FakeBufferedWriteHandler` test also verifies unexpected BWH errors are wrapped and returned without claiming GCS sync. Remaining risk is concurrency: these tests are single-threaded and do not stress global block semaphore contention except indirectly through configuration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/file_streaming_writes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/file_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/file_test.go

## Purpose

`file_test.go` is the primary regression suite for `FileInode`. It runs the same suite over non-zonal, zonal, and Pirlo rapid bucket modes and validates file identity, attributes, reads, staged writes, streaming-write eligibility, sync/flush persistence, local file promotion, truncate semantics, mtime behavior, clobber handling, content encoding, reader updates, unlink state, and file-handle accounting.

## Important APIs, Types, And Helpers

`FileTest` owns a fake bucket, simulated clock, initial object contents, backing `MinObject`, locked `FileInode`, and target `gcs.BucketType`. `createInodeWithLocalParam`, `createInodeWithEmptyObject`, and `createBufferedWriteHandler` set up the main test variants. `validateMrdInstanceMinObject` and `validateMrdWrapperMinObject` assert rapid-bucket reader wrappers receive copied, up-to-date min objects after inode state changes. `getWriteConfig` and `getWriteConfigWithEnabledRapidAppends` produce streaming write configs.

The suite covers `SourceGeneration`, `SourceGenerationIsAuthoritative`, `SyncPendingBufferedWrites`, `Attributes`, `Read`, `Write`, `Truncate`, `Destroy`, `Sync`, `Flush`, `SetMtime`, `CreateEmptyTempFile`, `InitBufferedWriteHandlerIfEligible`, `Unlink`, `UpdateSize`, `RegisterFileHandle`, and BWH support decisions.

## Control Flow And State Behavior

The staged read/write tests verify that reads fault content into a temp file, writes and truncates mutate only local content until sync/flush, and sync/flush creates a new GCS generation with `gcsfuse_mtime` metadata and updated reader wrappers. Local file tests create an inode with no backing object, stage empty or written content locally, and verify sync/flush promotes it to non-local with persisted object metadata. Truncate-up and truncate-down tests confirm size, zero-fill behavior, and mtime propagation.

Mtime tests split three paths: metadata update without faulting content, metadata update after clean content is faulted in, and local temp-file mtime update when content is dirty or the inode is local. Precondition and not-found errors from remote metadata updates are treated as unlinked/clobbered no-ops. Unlinked files ignore `SetMtime`. Attribute tests verify `gcsfuse_mtime` outranks `goog-reserved-file-mtime`.

Streaming tests inside this file validate eligibility for new/empty files and rapid appends to unfinalized objects, rejection for nonempty finalized objects, BWH size reflection in attributes/source generation, reading after flush, invalid config errors, and truncate-down fallback that finalizes then switches paths. Rapid append coverage confirms appending to an unfinalized zonal object writes expected content.

## Dependencies And Integration Points

The suite depends on fake GCS storage, `storageutil`, `gcsx.SyncerBucket`, `contentcache`, `gcsfuse_errors`, `cfg`, `util.OpenMode`, noop metrics/tracing, semaphores, FUSE attrs, and simulated time. It verifies integration with rapid bucket MRD reader state, GCS generation/metageneration preconditions, metadata conventions, and buffered-write configuration.

## Risks And Test Signals

The strongest signals are around preserving source generation until sync, rejecting clobbered sync/flush/openReader paths, validating uploaded size, ensuring reader wrappers are updated after object replacement, and correctly distinguishing sync from flush for streaming writes. Remaining risks include real storage API differences from the fake bucket, interaction with persistent disk content cache beyond basic construction, and multi-handle concurrency beyond counter increments/decrements.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/hns_dir_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/hns_dir_test.go

## Purpose

`hns_dir_test.go` validates `DirInode` behavior when hierarchical namespace support is enabled and compares it with non-HNS behavior for operations whose storage APIs differ. It focuses on HNS folder lookup, managed-folder style listing, folder rename/create/delete, file move, recursive deletion, and the type-cache-deprecation path that uses cache-only lookups before server fallback.

## Important APIs, Types, And Helpers

`hnsDirTest` holds shared context, `gcsx.SyncerBucket`, locked `DirInode`, testify mock bucket, optional `metadata.TypeCache`, clock, config, and parent inode context. `HNSDirTest` configures a hierarchical bucket; `NonHNSDirTest` configures a non-hierarchical bucket. `resetDirInodeWithTypeCacheConfigs` creates a `NewDirInode` with `EnableHns`, `EnableUnsupportedPathSupport`, managed-folder listing, and metadata cache settings. `createDirInodeWithTypeCacheDeprecationFlag` creates child dir inodes under a parent context.

The suite exercises `findExplicitFolder`, `LookUpChild`, `RenameFolder`, `RenameFile`, `DeleteChildDir`, `CreateChildDir`, `DeleteObjects`, `ReadEntries`, and cache-deprecated lookup paths.

## Control Flow And State Behavior

HNS lookup tests validate that explicit folders are found through `GetFolder`, not only directory marker objects. A not-found folder returns nil without error. For cached regular-file or symlink types, lookup goes through object stat; for explicit dir/unknown type, it can query `GetFolder`; cached nonexistent type suppresses remote lookup. Conflict marker names still allow object-side lookup when a folder also exists.

Rename tests validate HNS-specific `RenameFolder` and `MoveObject` requests, including propagation of `NotFoundError`. Create/delete tests split HNS and non-HNS behavior: HNS directory creation calls `CreateFolder`, while non-HNS creation creates an empty trailing-slash object with generation precondition. HNS deletion can need both object deletion and folder deletion; if folder deletion succeeds after object deletion fails, the directory inode is marked unlinked. If folder deletion fails, the error is surfaced and unlink state is retained false.

Recursive deletion tests verify deleting object names, descending through listed collapsed runs, and issuing both `DeleteObject` and `DeleteFolder` for HNS folders. HNS `ReadEntries` uses `IncludeFoldersAsPrefixes` and treats collapsed folder prefixes, explicit folder objects, and files as visible directory entries, with HNS implicit directories becoming explicit folder-type entries in the cache.

## Dependencies And Integration Points

The suite depends on `storagemock.TestifyMockBucket`, `gcsx.SyncerBucket`, GCS HNS folder APIs (`GetFolder`, `CreateFolder`, `DeleteFolder`, `RenameFolder`), object APIs (`StatObject`, `MoveObject`, `ListObjects`, `DeleteObject`), `metadata.TypeCache`, cache miss errors, FUSE dirents, config flags, and semaphores. It is the key test signal for integration between inode directory logic and HNS bucket semantics.

## Risks And Test Signals

Covered risks include using object APIs when HNS folder APIs are required, failing to update or bypass type cache correctly, wrong precedence between files and folders, recursive delete missing nested collapsed runs, and incorrect error handling when one of object/folder deletion succeeds. Type-cache-deprecated cache-hit/miss tests confirm cache-only requests are attempted first and server lookups happen only on cache miss. Remaining risks include real HNS pagination, managed folders in fake storage, and concurrent rename/delete interactions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/hns_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/inode.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/inode.go

## Purpose

`inode.go` defines the core inode interfaces and generation comparison primitive used by the gcsfuse filesystem layer. It is a contract file: concrete directory, file, symlink, and explicit directory inodes conform to these interfaces so FUSE operation code can lock, inspect, update, destroy, and unlink inode objects uniformly.

## Important APIs, Types, And Functions

`Inode` embeds `sync.Locker` and defines identity (`ID`, `Name`), lookup-count management (`IncrementLookupCount`, `DecrementLookupCount`), current FUSE attributes, size update, destruction, and unlink marking. The comments establish the locking contract: most methods require the inode lock unless documented otherwise, while `ID` and `Name` do not.

`BucketOwnedInode` extends `Inode` with `Bucket() *gcsx.SyncerBucket`, allowing callers to find the owning bucket for file/dir operations. `GenerationBackedInode` extends `Inode` with `SourceGeneration() Generation`, used where delete, rename, sync, or clobber logic needs the exact GCS generation/metageneration backing an inode.

`Generation` stores `Object`, `Metadata`, and `Size`. `Generation.Compare` orders latest GCS state against current inode state: object generation first, metadata generation second, then a special size-growth case. It returns `-1`, `0`, `1`, or `2`; `2` means object/metageneration match but latest size is greater, a zonal/rapid append scenario.

## Control Flow And State Behavior

The file contains no persistence logic itself, but its contracts drive state transitions in implementations. `DecrementLookupCount` returning true tells inode managers to call `Destroy` after lookup references reach zero. `UpdateSize` allows directory/file code to refresh cached inode size after remote append detection. `Unlink` marks inodes deleted locally even before or independent of remote storage mutation.

`Generation.Compare` intentionally ignores the case where latest size is smaller than current size if object/metageneration match, returning `0`; comments say small staleness in GCS object size is expected. That choice affects clobber handling in `FileInode.Attributes` and `FileInode.Sync`.

## Dependencies And Integration Points

Dependencies are small: `sync`, `gcsx`, FUSE inode IDs, and context. The interfaces are consumed across the inode package and higher-level filesystem operation managers. `Generation.Compare` is used by file clobber detection and generation-backed explicit directory/file handling.

## Risks And Test Signals

Risks include interface contract drift, especially lock requirements and destruction semantics, and misinterpreting `Compare` return code `2` as ordinary greater-than. The size-shrink ignored case is deliberate but can mask certain stale-size observations. `inode_test.go` covers all comparison branches, including object, metadata, equal, larger-size, and smaller-size cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/inode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/inode_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/inode_test.go

## Purpose

`inode_test.go` is a focused unit test for `Generation.Compare`, the ordering primitive used to detect stale, changed, or append-grown GCS objects relative to an inode's cached source generation. It protects clobber behavior shared by file and generation-backed inode code.

## Important APIs, Types, And Functions

The file imports the production `inode` package externally (`package inode_test`) and uses table-driven subtests in `TestGenerationCompare`. Each case supplies a `latest` and `current` `inode.Generation` plus the expected integer comparison result.

Covered cases include latest object generation greater and smaller, latest metadata generation greater and smaller when object generations match, same object/metageneration with larger latest size, same object/metageneration with smaller latest size, and exact equality.

## Control Flow And State Behavior

The test does not create inodes or mutate storage. It simply calls `tc.latest.Compare(tc.current)` for each table row and asserts equality. Its important behavioral assertion is that size growth at equal generation/metageneration returns `2`, while size shrink returns `0`. That matches the production comment that zonal buckets can append without changing generation/metageneration and that smaller latest size may be tolerated as staleness.

## Dependencies And Integration Points

Dependencies are `testing`, `testify/assert`, and `internal/fs/inode`. By testing from `inode_test`, it uses the exported API only, which keeps the comparison contract visible to external package users.

## Risks And Test Signals

The suite gives crisp coverage of `Generation.Compare` return values and protects callers that branch on `2`. A small issue is duplicate naming for one metadata-less-than case, but it does not reduce behavioral coverage. It does not test transitivity or table exhaustiveness over all combinations, but the comparison logic is simple enough that the branch tests are strong.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/inode_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/lookup_count.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/lookup_count.go

## Purpose

`lookup_count.go` provides a small helper embedded by inode implementations to track kernel lookup references. FUSE lookup counts decide when the filesystem must continue remembering an inode and when it can destroy local resources after forget operations reduce the count to zero.

## Important APIs, Types, And Functions

`lookupCount` stores the inode ID, current unsigned count, and a `destroyed` flag. `Init` records the inode ID for diagnostics. `Inc` increments the count and panics if the helper has already been destroyed. `Dec` decrements by a caller-provided amount, panics if destroyed or if `n` exceeds the current count, and returns true when the count reaches zero.

The helper is intentionally unexported and requires external synchronization. Concrete inodes call it while holding their own invariant mutexes, as seen in `FileInode.IncrementLookupCount`/`DecrementLookupCount` and directory equivalents.

## Control Flow And State Behavior

The state machine is simple: initialized count starts at zero, increments follow lookup responses, decrements follow forgets, and a zero result tells the caller to destroy the inode. The `destroyed` field is checked but not set in this file, so callers or embedding code would need to set it if they want post-destroy panic protection. In the current requested code, the main visible behavior is over-decrement protection and zero-count signaling.

No persistence exists. The count is process-local inode-manager state and is lost when the filesystem process exits.

## Dependencies And Integration Points

The file depends on `fmt` and FUSE inode IDs. It integrates with the `Inode` interface's lookup-count methods and with any inode manager that calls `Destroy` after `Dec` returns true. Panic messages include the inode ID where available, making internal misuse easier to diagnose during invariant-enabled tests.

## Risks And Test Signals

The important risk is misuse under missing locks or mismatched forget counts, either of which can corrupt lifecycle management. Another subtle point is that `destroyed` is not changed by `Dec`; if expected, that behavior must be implemented by embedding code. `dir_test.go` includes a lookup count test that increments three times and verifies destruction is signaled only after all three references are decremented. There is no direct panic-path test in the requested subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/lookup_count.go -->

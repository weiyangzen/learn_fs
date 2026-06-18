# subset-b-000004 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/manager.go -->
# sources/cloud-native/buildkit/cache/manager.go

## Purpose

`manager.go` defines the top-level BuildKit cache manager. It owns the in-memory cache record map, wires snapshotter/content/lease/metadata dependencies, creates mutable and immutable refs, rehydrates persisted refs on startup, resolves refs by content blob or chain IDs, exposes disk usage, and prunes unused cache records. This file is the central coordinator between `refs.go` lifecycle mechanics and `metadata.go` persistence.

## Important APIs, Types, and Functions

- `ManagerOpt` injects the snapshotter, content store, lease manager, GC callback, applier/differ, metadata store, cache root, mount pool root, and optional external prune checker.
- `Accessor`, `Controller`, and `Manager` define the public cache surface used by workers and solver code: `GetByBlob`, `Get`, `New`, `GetMutable`, `Merge`, `Diff`, `DiskUsage`, `Prune`, and `Close`.
- `cacheManager` stores `records`, `mu`, `muPrune`, containerd/BuildKit backends, mount pool, and a `flightcontrol.Group` used to deduplicate unlazy operations.
- `NewManager` wraps the configured snapshotter in a merge snapshotter, loads metadata via `init`, initializes the sharable mount pool, and returns a `Manager`.
- `GetByBlob` resolves or creates lazy/blob-backed immutable refs from an OCI descriptor and optional parent.
- `Get`, `get`, and `getRecord` load immutable refs by ID, validate lazy provider availability, handle equal mutable/immutable pairs, and recover or clean invalid metadata.
- `New` creates a new mutable snapshot ref, optionally based on a finalized/extracted immutable parent.
- `GetMutable` reopens an unlocked mutable ref, deleting stale equal immutable records if needed.
- `Merge`/`createMergeRef` and `Diff`/`createDiffRef` create synthetic immutable refs for merged filesystem views or differences.
- `Prune`, `prune`, `pruneOnce`, `DiskUsage`, `calculateKeepBytes`, and `sortDeleteRecords` implement usage reporting and garbage collection policy.

## Control Flow

Startup calls `MetadataStore.All()` and attempts `getRecord` for every persisted item. Records whose metadata cannot be reconciled with snapshotter state are cleared and their leases removed. Normal access flows through `cm.mu`, then per-record `cr.mu`, so callers either get an active ref, a lock error, a not-found error, or a lazy-provider error.

`GetByBlob` first computes `diffID`, `chainID`, and a separate `blobChainID` that distinguishes differently compressed blobs with the same uncompressed diff ID. It validates content availability unless descriptor handlers are provided. With a parent, it finalizes the parent and composes parent chain IDs. It prefers an exact `blobChainID` match, then a chain-ID match that may share an existing snapshot, otherwise it creates a new lease, records metadata, and returns a blob-only immutable ref.

`New` finalizes and extracts the parent before preparing a mutable snapshot. It creates a lease first, adds the snapshot resource, prepares the snapshotter key, initializes metadata, and stores a mutable `cacheRecord`. Special snapshotter handling adds stargz temporary labels and overlaybd read/write labels.

`Merge` flattens nested merge refs, clones parents, finalizes inputs, persists merge-parent metadata, and creates a committed immutable record whose actual snapshot is materialized later by `refs.go` mount/extract paths. `Diff` has an optimization where a lower ref that is an ancestor of upper becomes a merge of intervening single-layer diffs, maximizing layer reuse; otherwise it persists a diff ref directly.

`Prune` serializes all prune calls with `muPrune`, computes keep-byte thresholds, repeatedly calls `pruneOnce`, then optionally runs containerd GC. `pruneOnce` scans unlocked, unreferenced records, applies type/shared/filter/age rules, marks selected metadata as deleted while locked, releases locks before slow size computation and removal, emits `UsageInfo`, and deletes leases/metadata/snapshots through `cacheRecord.remove`.

`DiskUsage` snapshots record state, propagates in-use counts through parents, marks externally shared records, filters by age and filter expressions, and computes unknown sizes concurrently by temporarily acquiring refs.

## State and Persistence Behavior

Persistent state is held in the cache metadata store plus containerd leases and snapshotter/content state. Each cache record stores parent relationships, committed/deleted flags, snapshot ID, blob/diff/chain/blobchain data, image refs, usage count, last used timestamp, record type, cache policy, and size. Leases protect snapshots and content from containerd GC. Deletion is two-phase: records are marked deleted in metadata before removing backing state so restart can finish cleanup. Equal mutable/immutable metadata supports lazy commit recovery and is repaired if the mutable side is missing but the immutable snapshot exists.

## Dependencies and Integration Points

The manager integrates with containerd content, diff, leases, snapshots, filter, and GC APIs; BuildKit metadata, session, snapshot, disk, progress, flightcontrol, and logging utilities; OCI digest/image spec identities; and snapshotter-specific stargz/overlaybd behavior. `client.PruneInfo`, `client.DiskUsageInfo`, and `client.UsageInfo` form the user-facing API surface for cache usage and pruning.

## Risks and Edge Cases

- Lock ordering is critical: manager lock plus record locks protect the records map and ref counts, while pruning deliberately releases locks before expensive operations.
- Lazy refs require descriptor handlers. Missing handlers produce `NeedsRemoteProviderError`; incorrect blobchain metadata can cause reuse misses or logged errors.
- Chain ID and blobchain ID semantics are subtle. Chain ID allows snapshot reuse for same uncompressed content, while blobchain ID prevents conflating different compressed blob histories.
- Crash windows around mutable commit/finalize are mitigated but complex, especially equal mutable metadata and lease creation.
- Prune must avoid deleting internal/frontend/shared records unless `All` or filters allow it, and it batches deletes to avoid holding the manager lock too long.
- Disk usage for mutable in-use refs is reported as `0` because size is changing.

## Test Signals

`manager_test.go` heavily exercises this file: basic create/get/commit/release/prune, lazy `GetByBlob`, blobchain merge reuse, lazy extraction, reopen-after-commit behavior, restart recovery, pruning thresholds, merge/diff ops, broken-parent cleanup, readonly mounts, compression variants, and non-distributable descriptor persistence. `TestCalculateKeepBytes` directly validates keep-byte policy.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/manager_test.go -->
# sources/cloud-native/buildkit/cache/manager_test.go

## Purpose

`manager_test.go` is an integration-heavy test suite for BuildKit cache manager behavior. It creates real containerd metadata DBs, native snapshotters, content stores, lease managers, appliers, differs, and BuildKit metadata stores, then exercises cache refs across creation, mutation, lazy blob import, compression conversion, remote export preparation, merge/diff, prune, restart, and mount behavior.

## Important APIs, Types, and Functions

- `newCacheManager` builds an isolated test manager with containerd metadata DB, local content store, namespaced lease manager, native snapshotter by default, BuildKit metadata store, applier/differ, and mount pool.
- `cmOpt` and `cmOut` define test setup inputs and returned manager dependencies.
- Helper functions include `checkDiskUsage`, `checkNumBlobs`, `ensurePrune`, `pruneResultBuffer`, `mapToBlob`, `mapToBlobWithCompression`, `fileToBlob`, `mapToSystemTarBlob`, `checkInfo`, `checkDescriptor`, `checkVariantsCoverage`, `getCompressor`, `esgzBlobDigest`, `zstdBlobDigest`, and `isReadOnly`.
- Test cases cover the full lifecycle: `TestManager`, `TestLazyGetByBlob`, `TestMergeBlobchainID`, `TestSnapshotExtract`, `TestExtractOnMutable`, `TestSetBlob`, `TestPrune`, `TestLazyCommit`, `TestLoopLeaseContent`, `TestSharingCompressionVariant`, `TestConversion`, `TestGetRemotes`, `TestNondistributableBlobs`, `TestMergeOp`, `TestDiffOp`, `TestLoadHalfFinalizedRef`, `TestMountReadOnly`, `TestLoadBrokenParents`, and `TestCalculateKeepBytes`.

## Control Flow

Most tests create a namespaced context, temporary directories, native snapshotter, and a fresh manager. They then drive cache refs through public methods and inspect disk usage, snapshot directories, content-store blobs, metadata-derived IDs, or mount options. Lazy blob tests construct tar layer descriptors with `containerd.io/uncompressed` annotations and use `DescHandlers` backed by in-memory content buffers.

The compression tests generate all combinations of gzip, zstd, eStargz, and uncompressed blobs, then call `GetRemotes` with forced compression to ensure conversion and variant linking. The merge and diff tests build multiple refs, release parents, prune aggressively, and verify synthetic refs retain their parents until released. Restart tests close and reopen the manager over the same metadata/snapshotter state to validate recovery paths.

## State and Persistence Behavior

The tests validate that refs are tracked as in-use while handles are held and unused after release, that `CachePolicyRetain` prevents immediate mutable deletion, and that prune removes snapshots/content only when no active parent or derived ref depends on them. `TestLazyCommit` and `TestLoadHalfFinalizedRef` verify equal mutable/immutable state survives restarts and that half-finalized metadata can be recovered. `TestLoadBrokenParents` verifies a deleted parent does not leak references when a merge parent fails to load.

## Dependencies and Integration Points

The suite depends on containerd content, diff, metadata, lease, native snapshotter, archive/compression, local content store, BuildKit snapshot wrappers, winlayers, compression/converter utilities, solver remote descriptors, OCI descriptors, and filesystem mount helpers. Several tests are OS-gated because mount, overlay, merge, or lazy extraction behavior is unavailable or different on Windows/FreeBSD.

## Risks and Edge Cases

- Tests use real snapshotter and content-store state, so failures can indicate integration regressions rather than simple unit bugs.
- Parallel compression tests intentionally stress variant sharing and concurrency.
- Some helper-generated tar blobs use Go tar writer and system `tar` to catch format-specific conversion bugs.
- `TestLoopLeaseContent` creates a compression-variant graph loop and verifies variant walking/prune does not hang or leak.
- `TestNondistributableBlobs` checks URL/media-type preservation only when requested, protecting distribution semantics.

## Test Signals

This file itself is the primary test signal for `manager.go`, `refs.go`, `remote.go`, `metadata.go`, and compression helpers. It covers normal and crash-recovery flows, lazy and materialized refs, remote descriptor generation, content lease cleanup, pruning, mount read-only behavior, and disk usage accounting.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/metadata.go -->
# sources/cloud-native/buildkit/cache/metadata.go

## Purpose

`metadata.go` adapts the generic Bolt-backed metadata store from `cache/metadata` into cache-specific `RefMetadata` and internal `cacheMetadata` operations. It defines all cache metadata keys, public metadata methods, search helpers, chain/blobchain indexes, queued setters, typed getters, image ref tracking, usage tracking, and external metadata access.

## Important APIs, Types, and Functions

- Constants define persisted keys such as `snapshot.size`, `cache.equalMutable`, `cache.cachePolicy`, `snapshot.committed`, parent keys, diff/chain/blob keys, image refs, deletion marker, blob size, media type, and URLs.
- `MetadataStore` exposes `Search`; `RefMetadata` exposes the public metadata API included in `Ref`.
- `cacheManager.Search`, `search`, `getMetadata`, `searchBlobchain`, and `searchChain` bridge manager locking with metadata store lookups.
- `cacheMetadata` wraps `*metadata.StorageItem` and provides typed cache operations.
- Setters and queued setters include `queueDescription`, `queueCommitted`, `queueSnapshotID`, `queueDiffID`, `queueChainID`, `queueBlobChainID`, `queueBlob`, `queueBlobOnly`, `queueDeleted`, parent setters, `queueSize`, `queueBlobSize`, and cache policy operations.
- Generic helpers include `queueValue`, `setValue`, `SetString`, `ClearValueAndIndex`, `GetString`, `GetStringSlice`, `getTime`, `getBool`, `getInt64`, `appendStringSlice`, and `updateLastUsed`.

## Control Flow

Public searches acquire the manager lock and call metadata store `Search`. The manager-level `search` converts storage items to cache metadata, prefers already cached storage items through `getMetadata`, warns when an index points to missing metadata, and filters records marked deleted.

Metadata updates use two patterns. Immediate setters call `StorageItem.Update` through `setValue` or `setTime`. Queued setters add Bolt-bucket operations to the storage item queue and require a later `commitMetadata`. This batching is used when creating refs so related parent/blob/chain/commit fields become persistent together.

Usage updates increment the cached usage count and last-used timestamp in one transaction. String-slice appends deduplicate new values against existing values and skip writes when nothing changes.

## State and Persistence Behavior

The file defines the durable schema for cache records. Chain indexes (`chainid:`) and blobchain indexes (`blobchainid:`) are stored as metadata value indexes and are used by `GetByBlob` to reuse existing records. Snapshot ID falls back to record ID for older BuildKit metadata. Deletion is a persisted boolean so startup or prune can complete cleanup after a crash. Last-used state is updated when refs release and no other last-used-triggering ref remains.

## Dependencies and Integration Points

This wrapper depends on the `cache/metadata` package for storage, Bolt transactions for low-level operations, BuildKit client usage record types, OCI digests, and BuildKit logging. Public `RefMetadata` methods are consumed by external cache users and refs. Internal metadata is heavily consumed by `manager.go`, `refs.go`, and remote descriptor generation.

## Risks and Edge Cases

- `initializeMetadata` in `manager.go` skips initialization if `CreatedAt` is already set, so missing or corrupt creation timestamps can affect whether parent metadata is refreshed.
- `ClearValueAndIndex` must manually clear old index entries; stale indexes can otherwise return missing or wrong records.
- Typed getters silently return zero values on unmarshal errors, which favors resilience but can hide metadata corruption.
- `appendStringSlice` deduplicates through a map, so appended order is not deterministic.
- Public and internal getters share the same underlying storage item, so callers must respect manager/record locking expectations where applicable.

## Test Signals

`manager_test.go` indirectly validates these keys and indexes through blob reuse, chain/blobchain equality, lazy commit recovery, disk usage, prune, image/non-distributable metadata, and last-used pruning. The lower-level store behavior is covered by `cache/metadata/metadata_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/metadata/metadata.go -->
# sources/cloud-native/buildkit/cache/metadata/metadata.go

## Purpose

`cache/metadata/metadata.go` implements a small Bolt-backed metadata database used by BuildKit cache records. It stores per-record JSON values, secondary indexes, and larger external byte blobs. It provides in-memory `StorageItem` snapshots with queued transactional writes and thread-safe value access.

## Important APIs, Types, and Functions

- `Store` wraps a `db.DB` and exposes `NewStore`, `DB`, `All`, `Probe`, `Search`, `View`, `Clear`, `Update`, `Get`, and `Close`.
- Buckets are `_main` for record values, `_index` for secondary index entries, and `_external` for external byte payloads.
- `StorageItem` carries `id`, `values`, `queue`, mutexes, and a pointer back to `Store`.
- `StorageItem` methods include `Update`, `Keys`, `Get`, `GetExternal`, `SetExternal`, `Queue`, `Commit`, `Indexes`, `SetValue`, `ClearIndex`, `GetAndSetValue`, and helpers.
- `Value` stores JSON raw message plus optional index string; `NewValue` marshals arbitrary values; `Unmarshal` decodes into typed targets.
- `ErrSkipSetValue` lets compare-and-update callbacks intentionally avoid writing.

## Control Flow

`NewStore` opens the Bolt database and refuses to silently use a v1 legacy `metadata.db` beside a missing v2 database path, forcing explicit migration or removal. `All` scans `_main`, constructs `StorageItem` objects from nested buckets, and returns them in Bolt iteration order. `Get` returns an existing populated item plus `ok=true`, or an empty mutable item with `ok=false` so callers can queue creation writes.

Writes go through `Store.Update` to create the main bucket and record bucket. `StorageItem.Queue` accumulates bucket-mutating closures under `qmu`; `Commit` executes them in one update transaction and clears the queue only after success. `SetValue` updates the in-memory map and Bolt value while maintaining index entries. `Clear` deletes external data, removes index entries recorded by the storage item, and deletes the main record bucket.

`Search` scans `_index` by exact index key or prefix, resolves matching record IDs back through `_main`, logs stale index entries, and returns storage items. `Probe` is a cheaper existence check for an index prefix.

## State and Persistence Behavior

Each metadata value is JSON encoded with an optional secondary index. Index keys are stored as `index::recordID`, allowing multiple records under the same index prefix. External payloads are scoped by record ID and key under `_external`. `StorageItem` maintains an in-memory value map, so successful writes update both Bolt and the local snapshot. `GetExternal` copies Bolt byte slices before returning because Bolt buffers are invalid after the view transaction.

## Dependencies and Integration Points

The store uses BuildKit `util/db` and `boltutil` abstractions over bbolt, BuildKit logging for stale index diagnostics, and pkg/errors for stack wrapping. It is consumed by `cache/metadata.go`, which layers cache-specific schema and public ref metadata on top.

## Risks and Edge Cases

- `SetValue` adds new index entries but only clears old indexes when deleting a value; callers changing an indexed value need to ensure old indexes are not left stale unless storage semantics elsewhere handle it.
- `Search` has a `continue` path for malformed index keys before advancing the cursor; malformed keys matching the search prefix could loop forever.
- `Commit` clears the queued operations inside the update callback after all functions succeed. If a later function fails, earlier in-memory mutations may have happened before transaction rollback.
- `Get` intentionally returns an empty item for missing records; callers must check `ok` before assuming persistence.
- Legacy metadata detection blocks startup rather than attempting automatic migration.

## Test Signals

`metadata_test.go` validates value queue/commit/reopen behavior, `All`, `Clear`, exact index search cleanup, and external data storage/removal. Cache integration tests validate higher-level schema use.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/metadata/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/metadata/metadata_test.go -->
# sources/cloud-native/buildkit/cache/metadata/metadata_test.go

## Purpose

`metadata_test.go` provides focused unit coverage for the generic metadata store. It verifies basic value persistence, all-record enumeration, clearing records, exact index search, index cleanup on clear, and external byte payload handling.

## Important APIs, Types, and Functions

- `TestGetSetSearch` exercises `NewStore`, missing `Get`, `NewValue`, `Queue`, `Commit`, reopen persistence, `All`, `Clear`, and post-clear `Get`.
- `TestIndexes` writes three records with indexed values, searches exact index values, and verifies `Clear` removes index entries.
- `TestExternalData` verifies `SetExternal`, `GetExternal`, missing external data errors, persistence across `Get`, and external cleanup after `Clear`.

## Control Flow

Each test uses `t.TempDir()` and a standalone `storage.db`. Tests create missing `StorageItem` placeholders via `Get`, queue or set data, commit, and inspect the store before and after close/reopen or clear. The index test creates multiple records with overlapping and distinct indexes, then searches `tag:baz` and `tag:bax` to confirm matching record IDs.

## State and Persistence Behavior

The tests confirm queued writes create real records, JSON values survive store reopen, `All` returns created records, `Clear` removes main records and indexes, and external data is scoped to record IDs and deleted with the record. They also demonstrate that a missing `Get` returns a usable item for creation.

## Dependencies and Integration Points

The tests use bbolt bucket closures directly when queuing `SetValue`, `testify/require` assertions, and Go temporary directories. They do not depend on the higher-level cache manager, making them a narrow signal for the storage package.

## Risks and Edge Cases

- Coverage is exact-index oriented; prefix search and `Probe` are not directly tested.
- The tests do not exercise changing an indexed value to a different index, malformed index keys, concurrent `Queue`/`Commit`, or transaction rollback behavior after partial queued mutations.
- External data is tested only with small byte slices.

## Test Signals

These tests are the direct regression net for `cache/metadata/metadata.go`; they support cache manager confidence by proving the basic storage primitives work across close/reopen and cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/metadata/metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/opts.go -->
# sources/cloud-native/buildkit/cache/opts.go

## Purpose

`opts.go` defines lightweight option and descriptor-handler types that flow through cache ref creation, lookup, lazy remote-provider validation, and unlazy operations. It is the small glue layer between cache refs, session groups, content providers, and progress reporting.

## Important APIs, Types, and Functions

- `DescHandler` describes how to access a remote/lazy descriptor: a session-aware `content.Provider`, progress controller, snapshot labels, annotations, and a `Ref` string for sync/progress identity.
- `DescHandlers` maps blob digests to descriptor handlers and is passed as a `RefOption`.
- `descHandlersOf` extracts the first `DescHandlers` option from variadic ref options.
- `DescHandlerKey` aliases digest but is not used in this file.
- `NeedsRemoteProviderError` is a slice of missing digests and reports missing descriptor handlers for lazy blobs.
- `Unlazy` aliases `session.Group`, and `unlazySessionOf` extracts a session group from ref options.

## Control Flow

Cache manager methods accept variadic `RefOption` values. `descHandlersOf` scans those options when loading or creating refs so lazy blob records can be checked against available remote providers. `unlazySessionOf` is used by `GetByBlob` to optionally force unlazy of a newly created blob ref using a session group passed as an option.

## State and Persistence Behavior

This file defines no persistent state. `DescHandlers` are in-memory capabilities attached to returned refs so later `Extract`, `Mount`, `GetRemotes`, or content reads can materialize lazy content. `NeedsRemoteProviderError` carries transient missing-provider state to callers.

## Dependencies and Integration Points

The option types integrate containerd `content.Provider`, BuildKit `session.Group`, BuildKit progress, and OCI digests. They are consumed by `manager.go`, `refs.go`, and `remote.go` whenever lazy content may require a provider or snapshotter labels.

## Risks and Edge Cases

- `descHandlersOf` returns only the first `DescHandlers` instance; multiple maps are not merged.
- `unlazySessionOf` checks for `session.Group`, while the declared `Unlazy` alias is not directly matched unless values also satisfy `session.Group`.
- A nil or incomplete `DescHandler` can allow metadata creation but later fail during unlazy if a provider is required.

## Test Signals

`manager_test.go` uses `DescHandlers` extensively for lazy blob imports, extraction, compression conversion, and remote descriptor generation. Missing handler behavior is exercised indirectly through lazy access failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/refs.go -->
# sources/cloud-native/buildkit/cache/refs.go

## Purpose

`refs.go` implements the concrete mutable and immutable cache refs returned by the manager. It owns reference counting, parent ownership, mount behavior, lazy materialization, blob metadata and compression variant linking, layer-chain traversal, mutable commit/finalize semantics, size accounting, read-only mount wrapping, and sharable overlay mount pooling.

## Important APIs, Types, and Functions

- Public interfaces: `Ref`, `ImmutableRef`, `MutableRef`, `Mountable`, and `RefList`.
- Core state: `cacheRecord`, `immutableRef`, `mutableRef`, `parentRefs`, and `diffParents`.
- Ref creation helpers: `cacheRecord.ref`, `cacheRecord.mref`, `immutableRef.clone`, `LayerChain`, `layerChain`, `layerWalk`, `layerDigestChain`, and ancestor walkers.
- Lazy/materialization helpers: `isLazy`, `Extract`, `ensureLocalContentBlob`, `unlazy`, `unlazyDiffMerge`, `unlazyLayer`, `prepareRemoteSnapshotsStargzMode`, `prepareRemoteSnapshotsOverlaybdMode`, and `withRemoteSnapshotLabelsStargzMode`.
- Blob/descriptor helpers: `ociDesc`, `linkBlob`, `getBlobWithCompression`, `walkBlob`, `walkBlobVariantsOnly`, `getBlobDesc`, `addBlobDescToInfo`, `filterAnnotationsForSave`, `layerToDistributable`, and `layerToNonDistributable`.
- Lifecycle methods: `Mount`, `Release`, `Finalize`, mutable `Commit`, mutable `release`, `remove`, and `size`.
- Mount helpers: `setReadonly`, `readonlyOverlay`, `newSharableMountPool`, `sharableMountPool`, and `sharableMountable`.

## Control Flow

Records hold a shared mutex, a ref set, parent union, metadata, mount cache, optional equal mutable/immutable partner, and cached digest chain. `ref` and `mref` add handle objects to `refs`; `Release` removes handles, updates last-used metadata when the last last-used-triggering handle is released, and cleans view leases/mount cache. Mutable release removes non-retained records, or removes equal immutable records when appropriate.

Mutable `Commit` does not immediately commit the snapshotter snapshot. It creates a new immutable `cacheRecord` sharing the mutable record mutex and parent refs, records `equalMutable`, persists committed metadata on the immutable side, and returns an immutable ref. `Finalize` commits the mutable snapshot into the immutable snapshot ID, creates a lease, marks the mutable dead, asynchronously removes mutable state, clears equal-mutable metadata, and persists the immutable record.

Mounting an immutable ref extracts lazy content first, then creates or reuses a readonly view snapshot for immutable refs, or uses the equal mutable snapshot until finalization is required. Mutable mounts are wrapped in a sharable mount pool so multiple callers can bind-mount a shared overlayfs mount safely.

Lazy extraction distinguishes blob-only layers from merge/diff refs. For layers, `unlazyLayer` ensures the blob is present via `lazyRefProvider`, prepares a temporary snapshot, applies the layer with the applier, commits it to the target snapshot ID, and flips `blobOnly` false. For merge/diff, `unlazyDiffMerge` recursively unlazies layer inputs and calls the merge snapshotter with constructed diffs. Stargz and overlaybd paths try to prepare remote snapshots before falling back to full unlazy.

Compression variant support stores blob descriptor metadata in content labels and links variant blobs with GC labels in both directions. `walkBlobVariantsOnly` traverses this graph with a visited set. `ociDesc` reconstructs OCI descriptors from metadata/content labels, adds uncompressed and created-at annotations, and converts non-distributable media types depending on URL/preference.

## State and Persistence Behavior

Ref state spans memory (`refs`, mount cache, equal refs, lazy handler maps), metadata (`blobOnly`, diff/blob/chain IDs, snapshot ID, size, image refs, deleted flags), leases (record, view, compression variant), snapshotter snapshots/views, and content-store labels. Size is cached in metadata and recomputed through snapshotter usage plus linked blob variants. View snapshots use temporary leases and are deleted when refs are released. Sharable mount pool directories are cleaned on manager startup and unmounted/removed when reference counts drop.

## Dependencies and Integration Points

This file integrates containerd content, images, leases, mounts, snapshots, labels, errdefs, BuildKit config/session/snapshot/solver/compression/lease/progress/tracing/rootless/winlayers utilities, OCI descriptors/digests, OpenTelemetry tracing, and OS mount/user namespace helpers. It is called by `manager.go`, `remote.go`, and external worker code via the public ref interfaces.

## Risks and Edge Cases

- Ref counting and equal mutable/immutable sharing are subtle; mutable and immutable records may share a mutex and backing snapshot until finalization.
- `layerWalk` intentionally treats some diff refs as reused upper blobs, but other diffs become their own synthetic blob.
- Lazy extraction requires valid descriptor handlers and an applier; nil handlers or missing content produce runtime failures.
- Compression variant graphs can contain cycles; traversal must keep `visited`.
- Read-only overlay conversion rewrites `lowerdir` to include the former `upperdir`; incorrect option parsing could expose writable state.
- `sharableMountable` keeps a count and can panic on double release only under `BUILDKIT_DEBUG_PANIC_ON_ERROR=1`; otherwise under-release is tolerated but may hide misuse.
- Snapshotter-specific label injection for stargz uses temporary unique labels and best-effort cleanup.

## Test Signals

`manager_test.go` exercises ref commit/finalize/release, lazy extraction, mount readonly behavior, sharable mount pool cleanup, blob metadata, compression variant linking and loops, remote descriptor generation, merge/diff refs, broken parent recovery, and prune behavior. OS-gated tests cover Linux mount semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/refs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remote.go -->
# sources/cloud-native/buildkit/cache/remote.go

## Purpose

`remote.go` turns immutable cache refs into solver remotes: ordered OCI layer descriptors plus content providers that can read local content or lazily materialize remote blobs. It also enumerates compression variants and exposes an `Unlazier` path for prefetch/materialization.

## Important APIs, Types, and Functions

- `Unlazier` defines `Unlazy(ctx) error`.
- `immutableRef.GetRemotes` returns one or more `*solver.Remote` values for a ref, respecting compression config and an `all` variants flag.
- `appendRemote` appends a descriptor/provider to each parent remote.
- `getAvailableBlobs` recursively builds all available compression-variant remote chains.
- `immutableRef.getRemote` computes blob chains, reconstructs descriptors, forces compression if configured, adds distribution source annotations for lazy refs, and builds a lazy multiprovider.
- `getBlobWithCompressionWithRetry` tries existing variants, then calls `ensureCompression`.
- `lazyMultiProvider` implements `content.Provider` plus `Unlazy`.
- `lazyRefProvider` implements provider/info/unlazy behavior for a single descriptor/ref pair.

## Control Flow

`GetRemotes` creates a temporary lease, gets the main remote, and usually returns it immediately. When `all=true`, compression is not forced, and descriptors exist, it searches for all available chains whose topmost blob matches the requested compression type. It uses `getBlobWithCompression` for the topmost descriptor and recursively enumerates parent variants.

`getRemote` first calls `computeBlobChain` to ensure each layer has descriptor/blob metadata. It walks the layer chain, creates descriptors through `ociDesc`, detects missing media types from content, adds distribution source annotations for lazy image refs, optionally forces compression conversion, and registers each descriptor in a `lazyMultiProvider`.

`lazyRefProvider.ReaderAt` checks digest equality, calls `Unlazy`, then reads from the local content store. `Info` returns local content info when available; for lazy refs it returns digest/size without pulling content. `Unlazy` deduplicates pulls by digest with `unlazyG`, validates laziness, uses descriptor handler progress, copies remote content into the content store, links the blob to the ref, and optionally sets a human-readable description from image refs.

## State and Persistence Behavior

Remote generation may mutate cache/content state. `computeBlobChain`, compression conversion, `linkBlob`, and lazy copy can write blob metadata, content blobs, variant leases/labels, size invalidations, and cache descriptions. Temporary leases protect content during remote construction. Lazy provider maps are in-memory capabilities tied to returned remotes.

## Dependencies and Integration Points

The file integrates BuildKit cache config, solver remotes, session groups, content utilities, compression/converter helpers, lease utilities, pull progress, logs, containerd reference parsing, content stores, and OCI descriptors. It is the bridge between local cache refs and exporters/importers that consume `solver.Remote`.

## Risks and Edge Cases

- `all=true` can produce combinatorial chains across available parent compression variants, though each layer usually has few variants.
- Forced compression on lazy refs may trigger full unlazy when conversion is needed.
- Distribution source annotations are built by parsing image refs with a dummy scheme; malformed refs fail remote generation.
- `lazyMultiProvider.Info` can report existence for lazy content without local bytes, so callers must use `ReaderAt` to force materialization.
- `Unlazy` assumes non-nil descriptor handlers for lazy refs; missing handlers are guarded earlier but still checked.

## Test Signals

`TestGetRemotes`, `TestSharingCompressionVariant`, `TestLoopLeaseContent`, `TestConversion`, and `TestNondistributableBlobs` validate descriptor media types, annotations, compression variants, lazy/local content behavior, variant graph traversal, and non-distributable media/URL handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remote.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/azblob/exporter.go -->
# sources/cloud-native/buildkit/cache/remotecache/azblob/exporter.go

## Purpose

`azblob/exporter.go` implements BuildKit remote cache export to Azure Blob Storage. It serializes BuildKit cache chains, uploads missing layer blobs to Azure by content digest, writes cache manifests for configured names, and exposes the `remotecache.Exporter` interface.

## Important APIs, Types, and Functions

- `ResolveCacheExporterFunc` returns the resolver used by BuildKit to create an Azure Blob cache exporter from attrs/session context.
- `exporter` embeds `solver.CacheExporterTarget`, stores `v1.CacheChains`, Azure container client, and parsed config.
- `Name` returns a progress/display string.
- `Finalize` marshals cache chains, uploads blobs, enriches layer annotations, uploads manifests, and returns no extra metadata.
- `Config` returns default compression config for this backend.
- `uploadManifest` writes manifest bytes with Azure `Upload`, using last-writer-wins semantics.
- `uploadBlobIfNotExists` writes layer blobs with `UploadStream` and `IfNoneMatch: *` so content-addressed blobs are uploaded only if absent.
- `bytesToReadSeekCloser` adapts manifest bytes for Azure upload APIs.

## Control Flow

The resolver parses config with `getConfig`, creates or verifies the Azure container, creates a new v1 cache chain target, and returns an exporter. On `Finalize`, the exporter marshals chains into a cache config and descriptor/provider pairs. For each cache layer, it validates descriptor annotations, extracts the uncompressed diff ID, checks if the target blob key already exists, uploads missing content from the descriptor provider, then stores cache import annotations containing diff ID, size, media type, and created-at timestamp. After the config is updated, it is marshaled and uploaded once per configured cache name under the manifest prefix.

## State and Persistence Behavior

Layer blobs are persisted in Azure under `blobKey(config, digest)`. Manifests are persisted under `manifestKey(config, name)` and overwrite prior manifests for the same name. The exporter does not store local state beyond the cache chains accumulated through the embedded solver export target. Blob uploads are idempotent by digest; manifest writes are intentionally last-writer-wins.

## Dependencies and Integration Points

The file uses Azure SDK block blob/container clients, blob access conditions, BuildKit remotecache v1 chain serialization, cache import type annotations, session and solver interfaces, progress, compression defaults, containerd content readers, and OCI digests. It relies on `utils.go` for config, clients, paths, and existence checks.

## Risks and Edge Cases

- `Finalize` requires uncompressed annotations on every descriptor; missing annotations abort export.
- Layer upload and manifest upload use fixed five-minute timeouts, which may be too short for very large layers or slow networks.
- Blob existence check before upload is an optimization, but concurrent exporters are still handled by `IfNoneMatch` and BlobAlreadyExists.
- Manifests are uploaded sequentially for all names.
- Created-at parsing errors abort the export.

## Test Signals

No Azure-specific tests are in this subset. Generic remote-cache and manager tests cover descriptor annotations and cache chain construction indirectly; live Azure behavior would need integration tests or mocked Azure clients.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/azblob/exporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/azblob/importer.go -->
# sources/cloud-native/buildkit/cache/remotecache/azblob/importer.go

## Purpose

`azblob/importer.go` implements BuildKit remote cache import from Azure Blob Storage. It loads one or more named cache manifests, converts Azure-stored layer entries back into remotecache v1 descriptor/provider pairs, and returns a combined solver cache manager.

## Important APIs, Types, and Functions

- `ResolveCacheImporterFunc` creates an Azure cache importer from attrs/session context and returns an empty descriptor because this backend resolves by configured names.
- `importer.Resolve` loads configured manifests in parallel and converts each cache chain into a solver cache manager.
- `loadManifest` checks manifest existence, downloads JSON config, builds layer providers, parses v1 cache config, and returns cache chains.
- `makeDescriptorProviderPair` converts `CacheLayer` metadata into an OCI descriptor and Azure-backed provider.
- `fetcher.Fetch` downloads a blob body by descriptor digest.
- `ciProvider` combines `content.Provider` and `content.InfoProvider`, caching an existence check in `Info`.

## Control Flow

The resolver parses config and creates a container client. `Resolve` starts an errgroup over all configured names, calling `loadManifest` for each. Missing manifests produce empty cache chains rather than errors. Existing manifests are downloaded, logged, unmarshaled, and each layer is converted into a descriptor/provider pair. The v1 parser populates `CacheChains`; then `NewCacheKeyStorage` and `solver.NewCacheManager` wrap those chains for solver use. Multiple named manifests are combined with `solver.NewCombinedCacheManager`.

When a solver later needs layer content, `fetcher.Fetch` checks that the digest key exists in Azure and opens a download stream. `ciProvider.Info` verifies digest equality, returns cached info after the first successful check, and maps missing blobs to containerd not-found errors.

## State and Persistence Behavior

Importer state is in-memory: config, container client, parsed cache chains, and per-provider `checked` flags. It reads persistent Azure manifests and blobs but does not write Azure state. Descriptor annotations are reconstructed from cache layer annotations, including uncompressed diff ID and optional created-at timestamp.

## Dependencies and Integration Points

The importer integrates Azure blob downloads, BuildKit remotecache v1 parsing, solver cache manager construction, worker-backed cache key/result storage, contentutil fetcher adapters, progress reporting, containerd content/info provider interfaces, and OCI descriptors.

## Risks and Edge Cases

- Any error loading one configured manifest aborts the whole resolve, except a missing manifest which returns an empty chain.
- `ciProvider.checked` is read before locking, so concurrent `Info` calls have a benign data race risk unless callers serialize access.
- Missing or incomplete layer annotations abort import because descriptors require diff ID, size, and media type.
- `Fetch` performs an existence check before download, adding latency and a race where the blob can disappear between check and download.
- Manifest JSON is read fully into memory.

## Test Signals

No Azure importer tests are in this subset. Expected behavior is inferred from remotecache v1 contracts and generic cache tests that validate descriptors and provider behavior. Azure integration would benefit from mocked container clients or live-storage tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/azblob/importer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/azblob/utils.go -->
# sources/cloud-native/buildkit/cache/remotecache/azblob/utils.go

## Purpose

`azblob/utils.go` contains shared Azure Blob remote cache configuration, credential/client creation, object key generation, and blob existence checks. It is used by both Azure exporter and importer.

## Important APIs, Types, and Functions

- Attribute constants define supported cache attrs: `secret_access_key`, `account_name`, `account_url`, `prefix`, `manifests_prefix`, `blobs_prefix`, `name`, and `container`.
- `IOConcurrency` and `IOChunkSize` tune Azure stream upload behavior.
- `Config` stores account URL/name, container, prefixes, names, and secret access key.
- `getConfig` merges attrs with environment variables and defaults.
- `createContainerClient` creates an Azure client using shared key credentials or default Azure credentials, verifies the container, and creates it if absent.
- `manifestKey` and `blobKey` build Azure object keys.
- `blobExists` checks blob properties and maps BlobNotFound to `false`.

## Control Flow

`getConfig` requires `account_url` or `BUILDKIT_AZURE_STORAGE_ACCOUNT_URL`, parses it, derives account name from attrs/env/host, chooses a container from attrs/env/default, applies optional prefix, defaults manifest and blob prefixes, and splits `name` by semicolon with `buildkit` as default. `createContainerClient` chooses shared-key auth when a secret key is supplied, otherwise uses `DefaultAzureCredential`. It checks container properties with a 60-second timeout and creates a missing container with a five-minute timeout. `blobExists` checks properties with a 60-second timeout.

## State and Persistence Behavior

This file has no local persistence. It determines where remote persistent state lives by constructing keys with `filepath.Join(prefix, manifestsPrefix, name)` and `filepath.Join(prefix, blobsPrefix, digest.String())`. It can create the configured Azure container as a side effect.

## Dependencies and Integration Points

The file uses Azure identity and storage SDKs, OCI digests, URL parsing, environment variables, filepath key joining, and pkg/errors. Exporter/importer code relies on it for consistent config and key paths.

## Risks and Edge Cases

- `filepath.Join` uses OS path separators; on Windows this could create backslash-separated blob names unless normalized elsewhere.
- `name` splitting does not filter empty names, so `name=a;;b` can produce an empty manifest key segment.
- Account name derivation assumes the first hostname segment is the Azure storage account.
- Default credentials can involve multiple environment/managed identity flows and may fail later than config parsing.
- Container creation on importer setup may be surprising for read-only import use.

## Test Signals

No direct tests are present in this subset. Exporter/importer behavior depends on these helpers, so unit tests for attr/env precedence, key generation, timeout behavior, and Windows path normalization would be valuable.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/azblob/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/export.go -->
# sources/cloud-native/buildkit/cache/remotecache/export.go

## Purpose

`remotecache/export.go` defines the generic remote cache exporter contract and the content-addressed exporter used for registry/content backends. It serializes cache chains into OCI index or image-manifest artifacts, uploads layer blobs/config/manifest, and returns the exported manifest descriptor to clients.

## Important APIs, Types, and Functions

- `ResolveCacheExporterFunc` is the resolver signature for cache exporter backends.
- `Exporter` extends `solver.CacheExporterTarget` with `Name`, `Finalize`, and `Config`.
- `Config` carries compression settings.
- `CacheType`, `ExporterResponseManifestDesc`, and `CacheType.String` describe export artifact style.
- `NewExporter` builds a `contentCacheExporter` with v1 cache chains and content ingester.
- `ExportableCache` can hold either an OCI/Docker index or an OCI image manifest.
- `NewExportableCache`, `MediaType`, `AddCacheBlob`, `FinalizeCache`, `SetConfig`, and `MarshalJSON` abstract the artifact shape.
- `contentCacheExporter.Finalize` pushes layers, writes cache config, writes manifest/index, and returns descriptor metadata.
- `withRemoteCacheErrorDetails` enriches unexpected remote status errors.

## Control Flow

`NewExporter` creates a v1 cache chain target. During solver export, cache records are added to that target. `Finalize` marshals chains into a cache config plus descriptor/provider pairs. Empty layer sets produce a warning and skip export. Otherwise, it creates an `ExportableCache`, collects layer descriptors in cache-config order, and uses `images.Dispatch` with a concurrency semaphore to copy all layer blobs from their providers into the ingester.

After layer upload, descriptors are added to the manifest/index in order and media types are converted for OCI or Docker compatibility. The cache config JSON is content-addressed and written as a blob with BuildKit cache config media type. The config descriptor is inserted into the artifact, the final manifest/index JSON is written as another content blob, and its descriptor is marshaled into `cache.manifest` response metadata.

## State and Persistence Behavior

The exporter writes all cache artifacts to the configured content ingester under digest refs. The manifest/index references layer descriptors and the config descriptor. No local state is persisted by this file beyond the v1 chain target accumulated before finalization. The returned descriptor lets callers publish or reference the generated remote cache artifact.

## Dependencies and Integration Points

This file integrates containerd content/images/remotes errors, BuildKit remotecache v1 chains and config media types, solver cache export targets, content copy utilities, progress/logging, resolver concurrency limits, compression media-type conversion, OCI specs, and digest calculation. Registry cache exporters and related backends build on this generic exporter.

## Risks and Edge Cases

- Image-manifest cache format requires OCI media types; `NewExportableCache` rejects Docker media types in that mode.
- Empty cache exports return nil metadata after reporting a skipped export, so callers must handle no manifest descriptor.
- Layer copying is parallel, but manifest order is restored afterward from the original layer descriptor slice.
- Remote status errors are enriched only for `ErrUnexpectedStatus`; other errors pass through with normal wrapping.
- Any missing descriptor/provider pair for a cache layer aborts finalization.

## Test Signals

This subset does not include direct tests for `remotecache/export.go`. It is indirectly exercised by cache-chain and `GetRemotes` tests that validate descriptors, compression media types, and annotations; backend-specific exporter tests elsewhere would be needed for end-to-end artifact validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/export.go -->

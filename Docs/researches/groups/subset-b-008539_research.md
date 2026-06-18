# Group Research: subset-b-008539

This grouped report covers Pebble object-storage provider, remote storage, shared cache, obsolete-file cleanup, and DB open integration files. Each source file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/provider_test.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/provider_test.go

Purpose: This file is the high-level behavioral test suite for `objstorageprovider.Provider`, especially local objects, remote/shared objects, cold-tier blobs, readahead modes, remote backings, attach flows, not-exist handling, and parallel sync/crash behavior. The central test, `TestProvider`, is data-driven over `testdata/provider` and exercises provider open/close, create, read, remove, list, local link/copy, save/close remote backing handles, and attach.

Important APIs and helpers: Tests use `DefaultSettings`, `Open`, `Provider.Create`, `OpenForReading`, `Remove`, `List`, `Lookup`, `RemoteObjectBacking`, `AttachRemoteObjects`, `SetCreatorID`, `UsePreallocatedReadHandle`, and remote test stores created with `remote.NewInMem`, `remote.WithLogging`, and `remote.MakeSimpleFactory`. Helper functions `genData`, `checkData`, and `xor` produce deterministic byte patterns while tolerating invariant builds that mangle write buffers.

Control flow and state: The data-driven harness keeps multiple providers indexed by directory, a current provider, stored remote backings, and live backing handles. Opening with a creator ID enables remote shared storage and ref checking. Reads may configure speculative or informed readahead and exercise either pooled or preallocated read handles. `TestParallelSync` creates/removes many objects while concurrent goroutines call `Sync`, then crash-clones local storage to check persisted objects.

Persistence and integration: These tests are the broadest signal that local directory metadata, remote object catalog state, ref markers, remote locators, and provider metadata survive close/reopen. They also cover external custom object names and multi-locator attachment between providers.

Risks and test signals: The suite is sensitive to log ordering and remote ref-marker semantics. It intentionally enables ref checking regardless of build tags so shared object tests do not depend on invariant builds. It covers missing local/remote underlying files via `Provider.IsNotExistError`, and validates crash durability for local sync, but shared crash simulation is explicitly limited.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/provider_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/readahead.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/readahead.go

Purpose: This file implements shared dynamic readahead state used by local VFS read handles and remote read handles. It decides when sequential reads justify issuing prefetch/read-ahead and when random or far-away reads should reset the state.

Important types and functions: `readaheadState` tracks `numReads`, `maxReadaheadSize`, current `size`, `prevSize`, and `limit`. `makeReadaheadState` initializes state with `initialReadaheadSize` and caller-provided maximum. `maybeReadahead` returns a positive prefetch size when a read should trigger readahead. `recordCacheHit` feeds cache-hit positions into the same sequentiality model without issuing I/O. Both use `maybeReadaheadOrCacheHit`.

Control flow: The algorithm requires at least `minFileReadsForReadahead` sequential-ish reads before returning a prefetch size. It considers reads that overlap or advance beyond `limit` but remain within `maxReadaheadSize` as sequential. When readahead is issued, it updates `limit`, records `prevSize`, and doubles `size` up to the maximum. Reads within the previous readahead window increase `numReads` but do not issue another prefetch. Reads too far before or after the active window reset to one observed read.

State and persistence: The state is in-memory per read handle. It does not persist across handles or process restarts.

Dependencies and integration: It depends on `internal/invariants` to catch uninitialized state. Local VFS handles translate returned sizes into `Prefetch` or OS sequential reopens. Remote handles translate them into larger buffered object reads.

Risks and test signals: The main risk is off-by-one/window logic causing excessive prefetching or missing sequential reads after cache hits. Data-driven tests in `readahead_test.go` cover reset, cache-hit, sequential, random, and growth behavior by inspecting internal state after each command.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/readahead.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/readahead_test.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/readahead_test.go

Purpose: This file provides data-driven coverage for the dynamic readahead state machine in `readahead.go`. It validates both normal reads and cache-hit notifications against expected internal state snapshots.

Important functions: `TestMaybeReadahead` initializes `readaheadState` with a 256 KiB max and processes commands from `testdata/readahead`. Supported commands are `reset`, `read`, and `cache-read`. Each read parses `offset,size`, calls either `maybeReadahead` or `recordCacheHit`, and prints `readahead`, `numReads`, `size`, `prevSize`, and `limit`.

Control flow and state: The test exposes otherwise-private state, making it a white-box behavioral contract. `reset` preserves `maxReadaheadSize` while returning the state to initial conditions. `cache-read` verifies that cache hits affect sequentiality and `limit` without producing a prefetch size.

Dependencies and integration: The test uses `datadriven`, `require`, and string parsing only; it does not perform actual file or remote reads. This isolates the state machine from VFS or remote object storage behavior.

Risks and test signals: Because output includes every mutable field, the fixture catches changes in exponential growth, thresholding, random-read reset behavior, and cache-hit handling. It does not directly validate integration with `vfs.File.Prefetch` or remote buffers; those paths are exercised by provider and remote read-handle tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/readahead_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remote.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/remote.go

Purpose: This file implements the provider's remote/shared object subsystem: catalog initialization, remote storage lookup by locator, shared creator ID management, object creation/opening/removal, ref-marker maintenance, remote cache setup, and tracking of externally named objects.

Important types and functions: `remoteSubsystem` owns the `remoteobjcat.Catalog`, serialized catalog sync mutex, optional `sharedcache.Cache`, and shared creator ID state. `remoteLockedState` holds the pending catalog `Batch`, storage object cache, and external object index. Key methods include `remoteInit`, `SetCreatorID`, `sharedSync`, `sharedCreate`, `remoteOpenForReading`, `remoteSize`, `sharedUnref`, `ensureStorage`, and `GetExternalObjects`.

Control flow: `remoteInit` opens the local remote-object catalog, initializes creator ID if present, opens a shared cache if configured, reconstructs known remote objects, and resolves each object's `remote.Storage`. Creates call `sharedCreate`, which requires a creator ID, creates the remote object, and returns `sharedWritable`; `Finish` later creates the ref marker. Opens optionally verify ref markers in invariant/testing scenarios before reading the backing object. Sync copies and clears the pending catalog batch under provider mutex, then applies it under a catalog sync mutex; failed catalog writes restore the batch.

State and persistence: Persistent state lives in the remote object catalog and remote storage objects/ref markers. In-memory state includes known objects, storage handles, and external-object indexes. Ref-tracked cleanup removes this provider's marker and deletes the backing object only when no markers remain. Protected objects are not unrefed.

Dependencies and integration: It integrates with `remoteobjcat`, `sharedcache`, `remote.StorageFactory`, `objstorage.ObjectMetadata`, and provider metadata bookkeeping in `provider.go`.

Risks and test signals: The main risks are catalog batch ordering, reference-marker races, creator ID initialization, and locator resolution failures. Provider tests cover shared create/remove/reopen, attach, external object tracking, multi-locator attachment, and parallel sync.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remote.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remote_backing.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/remote_backing.go

Purpose: This file defines the binary metadata format used to export and attach remote object backings between providers. It allows shared objects or externally managed objects to be referenced by another DB instance while preserving cleanup/ref-check semantics.

Important APIs and types: `encodeRemoteObjectBacking`, `RemoteObjectBacking`, `CreateExternalObjectBacking`, `decodeRemoteObjectBacking`, and `AttachRemoteObjects` are the main entry points. `remoteObjectBackingHandle` protects an object from cleanup while a backing is held, and unprotects on `Close`. The wire format uses varint tags for creator ID, creator file number, cleanup method, ref-check origin, locator, and custom object name. Unknown tags are skipped if safe and rejected if `tagNotSafeToIgnoreMask` is set.

Control flow: Exporting validates the object is remote, writes creator metadata, adds a ref-check pair for `SharedRefTracking`, and optionally writes locator/custom-name strings. External backings omit normal creator fields and encode a custom object name with `SharedNoCleanup`. Attaching first decodes every backing and resolves storage, then creates local reference markers for ref-tracked objects and verifies the origin provider's marker exists. Only after validation does it add metadata for all objects under the provider mutex.

State and persistence: The encoded backing itself is transient, but attaching persists metadata through the remote catalog on provider `Sync` and may create remote marker objects immediately. The handle's protection state prevents premature unref while another provider is obtaining the backing.

Dependencies and integration: It depends on `objstorage.RemoteObjectBacking`, `remote.Locator`, ref-name helpers, provider metadata updates, and shared remote cleanup.

Risks and test signals: Compatibility of the tag format is critical. Cleanup is incomplete on partial attach failure, noted by TODOs. Tests cover round-tripping, safe/unsafe unknown tags, external object backing creation, attach persistence across reopen, and ref-check corruption behavior through provider tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remote_backing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remote_backing_test.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/remote_backing_test.go

Purpose: This file validates the remote backing encoding/decoding contract and basic attach persistence for shared and externally named objects.

Important tests: `TestSharedObjectBacking` iterates over `SharedRefTracking` and `SharedNoCleanup` for table and blob file types. It constructs remote metadata, obtains a `RemoteObjectBackingHandle`, checks `Get` before and after `Close`, decodes the buffer into a target file number, and verifies all remote metadata. It also appends safe unknown tags and an unsafe unknown tag to exercise compatibility behavior. `TestCreateSharedObjectBacking` verifies `CreateExternalObjectBacking` produces metadata with locator, custom object name, and no-cleanup. `TestAttachRemoteObjects` attaches a backing, syncs, reopens, and confirms the remote object remains listed with the expected file type and custom name.

Control flow and state: Tests open providers over `vfs.NewMem`, install a simple remote factory, set creator IDs, and use in-memory remote storage. The handle close test confirms backing handles are single-use after `Close` and that protection is released.

Dependencies and integration: The file relies on `supportedFileTypes`, `DefaultSettings`, `Open`, `remote.NewInMem`, and `remote.MakeSimpleFactory`. It is focused on wire-format and catalog integration, not full remote object data I/O.

Risks and test signals: It catches accidental wire-format breaks, missing ref-check fields for ref-tracked objects, and changes to custom-name semantics. It does not test cleanup after partial attach failure or origin ref-marker disappearance; those are covered more broadly in provider data-driven tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remote_backing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remote_obj_name.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/remote_obj_name.go

Purpose: This file centralizes naming for remote objects and reference-marker objects. Stable naming is required for shared storage interop, listing references, deleting objects, and cross-provider attachment.

Important functions: `remoteObjectName` returns either a custom object name or a generated name. Generated table names use `<hash>-<creator-id>-<creator-file-num>.sst`; blob names use the `.blob` suffix. `sharedObjectRefName` adds `.ref.<ref-creator-id>.<local-file-num>` for a specific referencing provider. `sharedObjectRefPrefix` returns the prefix used to list all references for a backing object. The provider method `sharedObjectRefName` fills in the current provider creator ID. `objHash` computes a 16-bit prefix from creator ID and creator file number to spread remote object names across blob-storage partitions.

Control flow and state: The functions are pure formatting helpers over `objstorage.ObjectMetadata`. They panic on unsupported file types and panic if ref names are requested for non-ref-tracked metadata. Custom object names bypass generated creator/file-number names but still use the same `.ref.` convention.

Dependencies and integration: Remote create/open/size/delete and backing encode/attach call these helpers. Ref cleanup in `sharedUnref` depends on prefix correctness, and tests compare against `base.MakeFilename` formatting.

Risks and test signals: Naming changes are backward-incompatible for remote storage objects already written. Hash collisions are acceptable because the full creator ID and creator file number remain in the object name. Tests cover randomized cross-checks, fixed examples for sstables and blob files, custom names, and ref marker formatting.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remote_obj_name.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remote_obj_name_test.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/remote_obj_name_test.go

Purpose: This file verifies the remote object and ref-marker naming format for table and blob objects, including randomized metadata and fixed examples.

Important tests: `TestSharedObjectNames` has a randomized `crosscheck` subtest that builds `ObjectMetadata` with random disk file numbers, file types, creator IDs, creator file numbers, and optional custom object names. It compares `remoteObjectName`, `sharedObjectRefPrefix`, and `sharedObjectRefName` against an independently assembled expected string. The `example` and `example-blobfile` subtests lock down exact strings for table and blob metadata with creator ID 456 and creator file number 789.

Control flow and state: Tests are pure string checks; no provider, remote store, or filesystem is needed. The randomized test exercises both generated names and custom-object-name override behavior.

Dependencies and integration: The expected generated name uses `objHash`, `base.MakeFilename`, and `DiskFileNum.String` formatting, so it catches divergence between helper formatting and Pebble filename conventions.

Risks and test signals: This file is a compatibility guard for remote object layout. A failing test likely indicates a breaking change for existing shared storage, remote catalog entries, or ref cleanup listing. It does not validate deletion/listing against actual `remote.Storage`; provider and remote tests cover those integration paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remote_obj_name_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remote_readable.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/remote_readable.go

Purpose: This file adapts `remote.ObjectReader` into Pebble's `objstorage.Readable` and `ReadHandle` interfaces. It adds optional shared-cache reads, corruption conversion for disappeared objects, read-before buffering for metadata/index access, dynamic readahead, and compaction-specific large reads.

Important types and functions: `NewRemoteReadable` constructs a standalone readable; provider `newRemoteReadable` additionally wires file number and cache. `remoteReadable` implements `ReadAt`, `Close`, `Size`, and `NewReadHandle`. `remoteReadHandle` implements buffered `ReadAt`, `SetupForCompaction`, `RecordCacheHit`, and pooled `Close`. Constants define 1 MiB normal remote max readahead and 8 MiB compaction readahead.

Control flow: `remoteReadable.readInternal` routes through `sharedcache.Cache.ReadAt` if available; compaction reads are marked read-only so they do not populate cache. Missing-object errors from the remote driver are marked as corruption. A read handle uses read-before only on the first read, then serves prefixes from its buffer when possible. Sequential reads use `readaheadState` to increase read size and fill the buffer, capped at EOF. Compaction handles bypass dynamic state and request the fixed 8 MiB size.

State and persistence: All buffering is per handle and reused through `sync.Pool`. The shared cache may write local cache files asynchronously, but this file itself persists no metadata.

Dependencies and integration: It depends on `remote.Storage`, `sharedcache`, `objstorage.ReadBeforeSize`, and the shared readahead state. File cache/table readers use these handles for remote SST and blob access.

Risks and test signals: Risks include memory growth from buffers, incorrect EOF capping, stale buffer reuse, and expensive compaction reads. Tests exercise data-driven read-before/readahead behavior and corruption conversion after underlying remote deletion.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remote_readable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remote_readable_test.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/remote_readable_test.go

Purpose: This file tests remote read-handle buffering/readahead behavior and corruption conversion when an opened remote object disappears.

Important types and tests: `testObjectReader` is a deterministic in-memory `remote.ObjectReader` that logs each `ReadAt` and `Close`. `TestRemoteReadHandle` is data-driven over `testdata/remote_read_handle`; it initializes a readable, creates read handles with a chosen `read-before-size`, optionally calls `SetupForCompaction`, performs reads, checks returned bytes, and emits the underlying remote read trace. `TestErrorWhenObjectDisappears` builds a real provider with in-memory remote storage, creates a shared object, opens it, deletes all underlying remote objects, and verifies the subsequent read returns a Pebble corruption error.

Control flow and state: The data-driven test keeps one reader/readable/read-handle across commands and closes old handles/readables as new ones are created. It directly observes whether a logical read became one larger remote read, a buffered hit, or an EOF.

Dependencies and integration: It uses `remote.NewInMem`, `remote.MakeSimpleFactory`, `DefaultSettings`, `Provider.Create`, `OpenForReading`, and `base.IsCorruptionError`. It does not use shared cache in the read-handle trace path.

Risks and test signals: The tests catch regressions in read-before one-shot semantics, compaction readahead, buffer prefix handling, EOF reporting, and conversion of remote not-exist errors into corruption. They do not measure memory accounting or cache write-back behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remote_readable_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remoteobjcat/catalog.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/remoteobjcat/catalog.go

Purpose: This file implements the durable local catalog of remote objects known to a Pebble store. The catalog is an append-only record log of `VersionEdit`s with atomic marker files for selecting the current catalog file.

Important types and functions: `Catalog` owns filesystem handles, creator ID, object map, marker, active catalog file/writer, and rotation helper under a mutex. `RemoteObjectMetadata` is the durable representation of a remote object. `CatalogContents` is returned by `Open`. `SetCreatorID`, `ApplyBatch`, `Checkpoint`, and `Close` are the public mutation/lifecycle APIs. `Batch` groups `AddObject` and `DeleteObject` operations.

Control flow: `Open` locates the marker, loads the selected catalog file if present, removes obsolete marker files, and returns sorted contents. `SetCreatorID` writes a creator-ID edit and refuses changes. `ApplyBatch` validates additions/deletions, writes the edit durably, then mutates the in-memory map. `writeToCatalogFileLocked` rotates on first write or when the record writer exceeds 1 MiB and `RotationHelper` says a snapshot is worthwhile. New catalog files write a full snapshot, sync the directory, move the marker, then remove the previous file.

State and persistence: Persistence depends on record flush plus file sync for each edit and atomic marker movement for rotation. The catalog stores remote object metadata, not object data or ref markers. `Checkpoint` copies the active catalog and marker into another FS/dir.

Dependencies and integration: The provider calls this during `remoteInit`, `sharedSync`, `SetCreatorID`, and checkpointing. It depends on `record`, `atomicfs.Marker`, `vfs`, and `VersionEdit`.

Risks and test signals: Risks include marker/catalog crash ordering, duplicate/deleted-object assertions, partial/corrupt record handling, and catalog-file cleanup. Tests cover data-driven open/batch/rotation/list/close behavior with open-file tracking.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remoteobjcat/catalog.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remoteobjcat/catalog_test.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/remoteobjcat/catalog_test.go

Purpose: This file provides data-driven coverage for the remote object catalog's durable behavior, rotation, validation, and file lifecycle.

Important tests and helpers: `TestCatalog` wraps a memory filesystem with open-file tracking and logging. Commands include `open`, `set-creator-id`, `batch`, `random-batches`, `close`, and `list`. Helpers parse object additions/deletions and support table/blob file types. The test uses `base.CatchErrorPanic` so assertion failures are rendered in expected output instead of crashing the data-driven run.

Control flow and state: The test maintains a single `*remoteobjcat.Catalog`, opening directories on demand, applying batches with add/delete lines, and printing loaded creator ID and object metadata. `random-batches` stresses large numbers of additions to trigger rotation. `close` verifies no catalog or marker file descriptors remain open.

Persistence and integration: The test repeatedly opens and closes catalogs over the same memory FS, confirming that marker-selected catalog files reconstruct creator ID and object state. The `list` command exposes marker/catalog files in the directory so expected output can assert rotation effects.

Risks and test signals: This catches duplicate additions, deleting missing objects, bad creator ID changes, rotation marker issues, and leaked open files. It is catalog-focused and does not create actual remote objects or ref markers; provider tests cover catalog integration with remote storage.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remoteobjcat/catalog_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remoteobjcat/version_edit.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/remoteobjcat/version_edit.go

Purpose: This file defines the on-disk record format for remote object catalog edits. A `VersionEdit` can add remote objects, delete objects, and set the immutable creator ID.

Important types and functions: `VersionEdit` contains `NewObjects`, `DeletedObjects`, and `CreatorID`. `Encode` writes varint-tagged records. `Decode` reads them, including optional per-new-object tags for locator and custom object name. `Apply` mutates a creator ID pointer and object map. Helper mappings convert between catalog object type codes and Pebble `base.FileType` values.

Control flow: Each new object record encodes file number, object type, creator ID, creator file number, cleanup method, optional locator/custom-name tags, and a zero terminator. Deleted-object and creator-ID records follow their own tags. Decode loops until EOF; unexpected EOF within a known tag becomes `errCorruptCatalog`, while unknown tags are hard errors. Apply sets creator ID first, then adds new objects and deletes removed objects, with invariant assertions for duplicate additions or missing deletions.

State and persistence: This is pure serialization logic, but it is the catalog's compatibility contract. It supports table and blob object types only. Locator redaction is preserved by reconstructing `remote.Locator` from a redactable string.

Dependencies and integration: `catalog.go` writes and reads these records through Pebble's `record` package. The provider's remote catalog metadata maps directly to `RemoteObjectMetadata`.

Risks and test signals: Unknown optional object tags currently fail instead of being skipped, so format extension must be deliberate. Tests round-trip varied edits with creator IDs, tables, blobs, locators, custom names, ref-tracking/no-cleanup methods, and deletions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remoteobjcat/version_edit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remoteobjcat/version_edit_test.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/remoteobjcat/version_edit_test.go

Purpose: This file verifies that `VersionEdit` serialization is stable for representative catalog edits.

Important tests: `TestVersionEditRoundTrip` enumerates empty edits, creator-ID-only edits, single table/blob additions, deletions, and mixed edits containing creator ID, multiple objects, locators, custom object names, cleanup methods, and deleted file numbers. `checkRoundTrip` encodes to a `bytes.Buffer`, decodes into a fresh `VersionEdit`, and compares with `pretty.Diff`.

Control flow and state: The tests are pure round-trip checks. They do not call `VersionEdit.Apply` or `Catalog.ApplyBatch`; the focus is whether an encoded byte stream reconstructs exactly the same struct fields.

Dependencies and integration: The cases use `base.FileTypeTable`, `base.FileTypeBlob`, `objstorage.SharedNoCleanup`, `objstorage.SharedRefTracking`, and `remote.MakeLocator`. This ties the test vectors to the file types and cleanup modes supported by the catalog.

Risks and test signals: It catches missing fields in encode/decode and accidental object-type mapping changes. It does not test corrupt input, unknown tags, duplicate object application, or catalog rotation; those are covered elsewhere or guarded by code assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/remoteobjcat/version_edit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/shared_writable.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/shared_writable.go

Purpose: This file adapts a remote `io.WriteCloser` into Pebble's `objstorage.Writable` interface and performs shared-object ref-marker creation on successful finish.

Important APIs and types: `NewRemoteWritable` is a test/tool constructor that wraps an arbitrary `io.WriteCloser`. `sharedWritable` stores an optional provider, object metadata, and the underlying remote storage writer. It implements `Write`, `StartMetadataPortion`, `Finish`, and `Abort`.

Control flow: `Write` forwards bytes to the remote writer and returns its error. `StartMetadataPortion` is a no-op because remote shared objects do not split metadata in this wrapper. `Finish` closes the remote writer, nils it, and if associated with a provider creates the ref marker through `sharedCreateRef`. If close or marker creation fails, it calls `Abort`. `Abort` closes any live writer and removes provider metadata for the file number, but a TODO notes it does not delete the remote object if creation already occurred.

State and persistence: The remote object is finalized by closing the underlying writer; a ref marker is separately persisted for ref-tracked cleanup. Provider metadata removal during abort prevents the object from remaining known locally, but remote garbage may remain if abort follows partial upload.

Dependencies and integration: `remote.go` returns `sharedWritable` from `sharedCreate`. Provider metadata is added before/around creation by provider logic, and `sharedCreateRef` enforces creator ID and cleanup semantics.

Risks and test signals: The biggest risk is leaked remote objects on abort or ref-marker creation failure. Data-driven provider tests exercise successful shared create/remove and ref tracking, but the TODO indicates incomplete cleanup for failed writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/shared_writable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/sharedcache/shared_cache.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/sharedcache/shared_cache.go

Purpose: This file implements a local filesystem-backed cache for remote/shared object reads. It caches fixed-size blocks from remote objects, shards the cache to reduce lock contention, and asynchronously writes cache fills after remote misses.

Important types and APIs: `Cache` owns shards, write workers, block math, sharding size, logger, and metrics. `Metrics` exposes counters and Prometheus histograms. `Open`, `Close`, `Metrics`, and `ReadAt` are the public APIs. Internal `shard`, `cacheBlockState`, `whereMap`, `logicalBlockID`, `blockMath`, and `writeWorkers` implement placement, LRU, locking, and async write-back.

Control flow: `ReadAt` first attempts a prefix read from cache with `get`. Full hits return immediately; partial/no hits read the remaining range from the remote object. For writeable reads, the miss range is block-aligned and rounded up, capped at EOF, copied back to the caller, and queued to workers for cache insertion. Read-only reads, used for compaction, bypass cache population. Shards are selected by hashing file number and sharding-block index. A shard get takes read locks, moves blocks to LRU front, and reads from the cache file. A shard set skips existing blocks, uses free blocks or evicts an unlocked LRU tail block, writes to the cache file, and releases the write lock.

State and persistence: Cache data is stored in `SHARED-CACHE-###` files, but the metadata mapping is in memory and intentionally not persistent; restart overwrites/reuses cache files from scratch. Metrics are atomic in-memory counters/histograms.

Dependencies and integration: `remote_readable.go` uses `Cache.ReadAt` for remote objects. The cache depends on `vfs`, `remote.ObjectReader`, `base.DiskFileNum`, and Prometheus histograms.

Risks and test signals: Risks include races around write locks/read locks, stale zeroed blocks from unaligned writes, queue blocking, no eviction candidate when all blocks are locked, non-persistent metadata after restart, and high memory allocation for adjusted miss buffers. Tests include data-driven cache behavior, randomized concurrent reads, and internal LRU/free-list checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/sharedcache/shared_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/sharedcache/shared_cache_helpers_test.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/sharedcache/shared_cache_helpers_test.go

Purpose: This test helper exposes a synchronization hook for the shared cache's asynchronous write-back workers.

Important API: `(*Cache).WaitForWritesToComplete` closes the current worker task channel, waits for all worker goroutines to exit, then restarts the same number of workers.

Control flow and state: Tests call this after a read miss to force queued cache writes to complete before issuing a second read that should hit. The helper reaches into unexported `writeWorkers` state because it is compiled in the same package for tests.

Dependencies and integration: It is used by `shared_cache_test.go` data-driven cache tests. It depends on `writeWorkers.tasksCh`, `doneWaitGroup`, `Start`, and `numWorkers`.

Risks and test signals: This is a test-only lifecycle manipulation. It would be unsafe as a production API because closing the queue while callers may concurrently enqueue writes would panic or race. In the controlled tests, it provides deterministic cache-hit expectations after asynchronous fills.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/sharedcache/shared_cache_helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/sharedcache/shared_cache_internal_test.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/sharedcache/shared_cache_internal_test.go

Purpose: This file unit-tests the shared cache shard's intrusive list primitives: the LRU doubly linked circular list and free singly linked list.

Important tests: `TestSharedCacheLruList` initializes a shard with 100 block states, then inserts and unlinks block indexes while checking list order and backlink correctness. `TestSharedCacheFreeList` pushes and pops indexes, asserting LIFO order and empty-list state.

Control flow and state: Both tests construct only a `shard` with `mu.blocks`; no cache files, worker goroutines, or remote reads are involved. Local `expect` closures walk list pointers and compare against expected integer slices.

Dependencies and integration: These primitives are used by `shard.set` when allocating or evicting blocks and by `shard.get` when moving accessed blocks to the front. Correctness is essential because corrupt list state can break eviction, leak blocks, or panic under invariants.

Risks and test signals: These tests catch pointer update regressions in simple cases, including removing head, tail, and sole LRU entry. They do not cover concurrent access or interactions with `whereMap` and locks; those are partly covered by randomized shared cache tests and invariant consistency checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/sharedcache/shared_cache_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/sharedcache/shared_cache_test.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/sharedcache/shared_cache_test.go

Purpose: This file tests shared-cache read behavior using data-driven fixtures and randomized concurrent reads.

Important tests and helpers: `TestSharedCache` walks `testdata/cache`, opens an object storage provider over a logging memory FS, initializes a `sharedcache.Cache`, writes deterministic object data, and issues `read` or `read-for-compaction` commands. It validates returned bytes and reports miss-count deltas after `WaitForWritesToComplete`. `TestSharedCacheRandomized` chooses shard counts and block sizes, writes a random-size object, and performs repeated reads from random offsets, optionally concurrently. Helpers parse byte-size arguments with K/M/G suffixes.

Control flow and state: Data-driven tests explicitly wait for asynchronous cache writes so a subsequent read can observe a hit. Compaction reads use `ReadOnly` and should not populate the cache. Randomized tests cover different block sizes, sharding block sizes, cache sizes, and concurrent read schedules.

Dependencies and integration: Tests use a real `objstorageprovider.Provider` for local object data, then pass its readable into `Cache.ReadAt`. This exercises cache logic against `objstorage.Readable`/`remote.ObjectReader`-like APIs without real remote storage.

Risks and test signals: The tests catch incorrect data reconstruction for unaligned offsets, shard/block boundary reads, partial hits, EOF capping, and basic concurrency races. The randomized seed is printed for reproduction. They do not assert detailed metrics or persistence across cache reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/sharedcache/shared_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/vfs.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/vfs.go

Purpose: This file implements the local filesystem backend of the object storage provider, including hot-tier objects, optional cold-tier blob objects, metadata-file discovery, directory syncing, and local size/remove/open/create operations.

Important types and functions: `localSubsystem` stores open directory handles. `localLockedState` tracks hot/cold object change counters and cold-tier metadata files. `localPath`, `metaFileType`, `metaPath`, and `offsetFromMetaPath` format/parse object paths. `localOpenForReading`, `vfsCreate`, `localRemove`, `localInit`, `localClose`, `localSync`, `localSize`, and cold metadata map helpers are the core methods.

Control flow: `localInit` opens the hot directory, lists or uses an initial listing, records table/blob objects, then optionally opens/list cold tier and records cold objects unless a hot duplicate exists. It also scans hot-tier blob metadata files for cold blobs, deleting stray metadata files without matching objects. `vfsCreate` creates a syncing file, wraps it in `fileBufferedWritable`, and for cold blobs wraps in a cold writable. `localOpenForReading` opens a VFS readable and, for cold blobs with known hot metadata, returns a cold readable overlay.

State and persistence: Objects are files in hot or cold directories. Cold blob metadata can be dual-written into hot-tier `.blobmeta.<offset>` files. Change counters avoid unnecessary directory syncs when only remote objects changed; `localSync` syncs directories whose counters advanced.

Dependencies and integration: Provider create/open/remove/size/list paths call these methods. Cold-tier wrappers live in adjacent files outside this subset. `FSCleaner` handles local deletion/archive semantics.

Risks and test signals: Risks include duplicate hot/cold file numbers, stale metadata files, unsynced directory entries, and unsupported cold-tier file types. Provider data-driven tests cover local, cold-tier, cold metadata, local readahead, and remove/list behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/vfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/vfs_readable.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/vfs_readable.go

Purpose: This file adapts a local `vfs.File` into Pebble's `objstorage.Readable` and `ReadHandle` interfaces. It adds dynamic prefetch, optional OS sequential readahead, handle pooling, finalizer leak checks, and preallocated read-handle support.

Important types and functions: `fileReadable` implements `ReadAt`, `Close`, `Size`, and `NewReadHandle`. `vfsReadHandle` implements `ReadAt`, `SetupForCompaction`, `RecordCacheHit`, and `Close`. `NewFileReadable`, `TestingCheckMaxReadahead`, `PreallocatedReadHandle`, and `UsePreallocatedReadHandle` are exported/test helpers. `fileMaxReadaheadSize` is 256 KiB.

Control flow: A new file readable stats the file to cache its size. Read handles initialize speculative readahead mode from `ReadaheadConfig`. `ReadAt` uses an alternate sequential file descriptor if one has been opened; otherwise it consults `readaheadState`. Depending on mode, it either calls `Prefetch` or switches to `vfs.SequentialReadsOption` once max readahead is reached. `SetupForCompaction` switches to informed mode and may immediately reopen sequentially. Cache-hit notifications advance readahead state unless OS-level or no readahead is active.

State and persistence: State is per readable/handle and not persisted. The underlying VFS file remains the source of truth. Pooling reuses handle objects; `PreallocatedReadHandle` avoids allocation for local reads.

Dependencies and integration: Provider local open uses `newFileReadable`. Table/block readers use `ReadHandle`s for point reads and compactions. `ReadaheadConfig` comes from provider settings.

Risks and test signals: Risks include leaked file descriptors, ignoring failed sequential reopen, short reads, and mismatched readahead modes. Invariant finalizers catch unclosed readables/handles. Provider tests exercise local readahead modes and preallocated handles.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/vfs_readable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/vfs_writable.go -->
# sources/storage-engines/pebble/objstorage/objstorageprovider/vfs_writable.go

Purpose: This file adapts a local `vfs.File` into an `objstorage.Writable` with buffered writes, sync-on-finish, close/abort lifecycle, and invariant testing that callers tolerate write-buffer mutation.

Important APIs and types: `NewFileWritable` and `newFileBufferedWritable` construct a `fileBufferedWritable` over a `bufio.Writer` and VFS file. Methods implement `Write`, `Finish`, `Abort`, and `StartMetadataPortion`. `firstError` returns the first non-nil error from two operations and is reused by other provider files.

Control flow: `Write` writes into the buffer and in invariant builds sometimes overwrites the caller's byte slice with `0xFF` to enforce the writable contract. `Finish` flushes the buffer, syncs the file if flushing succeeds, closes the file, nils internal fields, and returns the first error. `Abort` closes the file and drops references without syncing. `StartMetadataPortion` is a no-op for normal local files.

State and persistence: Data becomes durable only after successful flush, file sync, and close in `Finish`; directory syncing is handled at provider level through local change counters and `localSync`.

Dependencies and integration: `vfsCreate` wraps newly created local files with this writable, and tests/tools may call `NewFileWritable` directly.

Risks and test signals: Risks include partial flush/sync errors and callers incorrectly reusing mutated input buffers. Provider tests cover normal local writes, local link/copy data validation, and crash behavior through sync.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/vfs_writable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/remote/factory.go -->
# sources/storage-engines/pebble/objstorage/remote/factory.go

Purpose: This file provides a simple map-backed implementation of `remote.StorageFactory` for tests and small integrations.

Important APIs and types: `MakeSimpleFactory` converts a `map[Locator]Storage` into a `StorageFactory`. The private `simpleFactory` type implements `CreateStorage(locator Locator)`.

Control flow and state: `CreateStorage` performs a direct map lookup. If the locator exists, it returns the preconfigured storage instance. If not, it returns an error containing the redacted locator string. There is no cloning or lifecycle ownership beyond returning the stored object reference.

Dependencies and integration: Provider settings use `Remote.StorageFactory` to resolve locators found in the remote object catalog or encoded backings. Tests frequently use `MakeSimpleFactory` with `remote.NewInMem` stores for deterministic remote behavior.

Risks and test signals: Because returned storage instances are shared, tests can model multiple providers pointing at the same remote storage. Unknown locators fail at attach/open/init time, which provider tests exercise in the multi-locator attach case. Production storage factories would typically perform credential/config lookup instead of a static map.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/remote/factory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/remote/localfs.go -->
# sources/storage-engines/pebble/objstorage/remote/localfs.go

Purpose: This file implements `remote.Storage` on top of a Pebble `vfs.FS`, primarily for testing remote-storage semantics using local files.

Important types and functions: `NewLocalFS` constructs a `localFSStore` rooted at a directory. The store implements `Close`, `ReadObject`, `CreateObject`, `List`, `Delete`, `Size`, and `IsNotExistError`. `localFSReader` adapts a `vfs.File` to `remote.ObjectReader`. `objWriter` wraps a created file and syncs file plus directory on close.

Control flow: Reads open the named object under `dirname`, stat it for size, and return a reader. Reader `ReadAt` normalizes `io.EOF` with a full read to nil, matching `io.ReaderAt` semantics. Creates use `vfs.Create` and return an `objWriter`; closing syncs the file, closes it, and syncs the containing directory. `List` enumerates the directory and filters by prefix; delimiter support is intentionally unimplemented and panics if requested. Delete removes the file and syncs the directory.

State and persistence: Object data is durable local FS state. Store `Close` zeroes the struct; it does not delete objects.

Dependencies and integration: Tests can use it as a remote backend, though most provider tests use `NewInMem`. It depends on `vfs`, `oserror`, and path joining.

Risks and test signals: Risks include lack of delimiter support and path/name assumptions because object names are joined under one directory. The implementation is intentionally simple and not a production cloud storage driver.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/remote/localfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/remote/logging.go -->
# sources/storage-engines/pebble/objstorage/remote/logging.go

Purpose: This file wraps any `remote.Storage` implementation with operation logging for data-driven tests and debugging.

Important types and functions: `WithLogging` returns a `loggingStore`. It logs `Close`, `ReadObject`, reader `ReadAt`/`Close`, `CreateObject`, writer `Write` byte counts/`Close`, `List`, `Delete`, and `Size`. `loggingReader` and `loggingWriter` wrap object readers and writers. `errOrPrintf` renders either an error or formatted success detail.

Control flow: Each storage method calls the wrapped method and logs inputs plus success/error details. `List` sorts a copy of returned names for deterministic log output while preserving the original order returned to callers. Writer logging accumulates bytes written and emits the count on close.

State and persistence: The wrapper persists no object data and owns no independent resources; state is limited to the wrapped storage reference, log function, reader/writer names, and writer byte counts.

Dependencies and integration: Provider data-driven tests wrap `remote.NewInMem` with this logger to produce stable expected output for object creation, ref marker creation, listing, deletion, and reads.

Risks and test signals: Logging changes can break data-driven fixtures even when behavior is correct. The wrapper assumes the log callback is safe to call from the relevant goroutines. It delegates `IsNotExistError` directly to the wrapped storage, preserving provider error classification.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/remote/logging.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/remote/mem.go -->
# sources/storage-engines/pebble/objstorage/remote/mem.go

Purpose: This file implements an in-memory `remote.Storage` used by tests. It models object creation, deletion, listing, size, and read-after-delete errors without filesystem dependencies.

Important types and functions: `NewInMem` creates an `inMemStore` with a mutex-protected map of object name to `inMemObj`. `ReadObject` returns an `inMemReader` that stores object name and store pointer rather than a data slice, so deletion after open is observed. `CreateObject` returns an `inMemWriter` that buffers until close. `List`, `Delete`, `Size`, `IsNotExistError`, `getObj`, `addObj`, and `rmObj` implement the storage contract.

Control flow: Writers accumulate bytes in a `bytes.Buffer`; `Close` installs the object into the map and nils the store pointer. Writing after close panics under assertion. Reads look up the object on every `ReadAt`; missing object returns a custom not-exist error. Reads past EOF return `io.EOF`. List filters by prefix and panics for non-empty delimiter.

State and persistence: All state is memory-only and lost on `Close`, which zeroes the store. The custom not-exist error forces callers to use `Storage.IsNotExistError` rather than OS-specific checks.

Dependencies and integration: Provider tests and remote readable tests use this storage extensively. It supports shared storage across multiple providers by sharing one store instance.

Risks and test signals: It is not durable and does not simulate network failures, partial writes, or eventual consistency. It does deliberately simulate object disappearance after a reader is opened, which is important for corruption handling tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/remote/mem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/remote/storage.go -->
# sources/storage-engines/pebble/objstorage/remote/storage.go

Purpose: This file defines Pebble's remote object storage abstraction and related policy/identity types. It is the contract implemented by in-tree test stores and external shared-storage integrations.

Important APIs and types: `Locator` is a redactable storage identifier and implements safe formatting. `StorageFactory` resolves a `Locator` to a `Storage`. `CreateOnSharedStrategy` controls which newly created SSTables should live on shared storage, with `ShouldCreateShared` applying the strategy by LSM level and `SharedLevelsStart`. `Storage` defines object read/create/list/delete/size/not-exist classification. `ObjectReader` defines concurrent `ReadAt` and close. `ObjectKey` and `MakeObjectKey` identify a remote object by locator/name.

Control flow and semantics: `Storage.CreateObject` may buffer until close and callers must treat close errors as significant. `List` returns full names for a prefix; delimiter grouping is optional. `ObjectReader.ReadAt` must not return partial successful results and must allow parallel reads on the same reader.

State and persistence: This file stores no state; it defines the stable interfaces and strategy constants used by provider settings and DB open/compaction policy.

Dependencies and integration: `objstorageprovider` uses `StorageFactory` for locator resolution, `Storage` for shared object operations, `ObjectReader` for remote reads, and `CreateOnSharedStrategy` during table creation. DB open uses `CreateOnSharedNone` to decide minimum format compatibility.

Risks and test signals: Interface semantics are high impact: not-exist classification affects corruption handling, close errors affect object durability, and locator redaction affects logs/errors. Tests exercise in-memory/local implementations and provider shared-object flows.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/remote/storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/test_utils.go -->
# sources/storage-engines/pebble/objstorage/test_utils.go

Purpose: This file provides `MemObj`, a lightweight in-memory implementation of both `objstorage.Writable` and `objstorage.Readable`, for tests and tools that need an object without filesystem or remote-storage setup.

Important types and functions: `MemObj` wraps a `bytes.Buffer` and implements `Finish`, `Abort`, `Write`, `StartMetadataPortion`, `Data`, `ReadAt`, `Close`, `Size`, and `NewReadHandle`. `memObjReadHandle` is a type alias over `MemObj` implementing `ReadHandle` with no-op `Close`, `SetupForCompaction`, and `RecordCacheHit`.

Control flow: Writes append to the buffer and, in invariant builds, sometimes overwrite the input buffer to catch callers that assume a writable preserves it. `Abort` resets the buffer. `ReadAt` bounds-checks and copies from the buffer, returning an error if the read extends past the object size. `NewReadHandle` returns a handle over the same object; no read-before or readahead behavior is implemented.

State and persistence: State is process memory only. `Data` exposes the underlying buffer slice, so callers must treat it as mutable internal storage.

Dependencies and integration: This utility implements the core `objstorage` interfaces and is useful for unit tests that are not concerned with provider metadata, remote cleanup, or VFS durability.

Risks and test signals: Because reads use a generic error rather than `io.EOF`, it is not a perfect substitute for file-backed objects. It is intentionally simple and should not be used to validate readahead, cache, sync, or cleanup behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/test_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/obsolete_files.go -->
# sources/storage-engines/pebble/obsolete_files.go

Purpose: This file manages deletion of obsolete Pebble files and objects. It integrates the delete pacer, filesystem cleaners, object storage provider deletion, file-cache eviction, manifest/options retention, WAL recycling/deletion, and zombie object tracking.

Important APIs and types: Exported aliases expose `Cleaner`, `DeleteCleaner`, and `ArchiveCleaner`. `openDeletePacer` wires `deleteObsoleteFile` into `deletepacer`. `scanObsoleteFiles`, `disableFileDeletions`, `enableFileDeletions`, `deleteObsoleteFiles`, `maybeScheduleObsoleteObjectDeletion`, `mergeObsoleteFiles`, `objectInfo`, and `zombieObjects` implement DB cleanup logic.

Control flow: `scanObsoleteFiles` must run with `db.mu` and no active compaction/flush. It builds live file numbers from current versions and ingested flushables, scans the directory for old manifests/options, then scans `objProvider.List()` for table/blob objects no longer live. It records obsolete objects by placement and size when available. `deleteObsoleteFiles` respects deletion disablement, gets obsolete WALs, drains obsolete table/blob slices, retains the newest configured manifests, releases `db.mu`, prepares a deletion batch, evicts file-cache entries for table/blob files, and enqueues work to the delete pacer. `deleteObsoleteFile` uses the object provider for tables/blobs and the cleaner for other file types, then emits event listener callbacks.

State and persistence: Obsolete lists live in `d.mu.versions` until enqueued. Actual deletion/archive is asynchronous via delete pacer and cleaner/provider. `zombieObjects` tracks objects no longer in the latest LSM but still needed by iterators.

Dependencies and integration: DB open calls scan/delete after writing a new OPTIONS file. Version management and iterator lifecycle populate obsolete/zombie objects. Object storage provider abstracts local/remote placement.

Risks and test signals: Risks include deleting files still referenced by flushable ingests or iterators, path mistakes, unsorted retention lists, and remote ref cleanup behavior. Tests cover full-path stat regression and cleaner data-driven behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/obsolete_files.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/obsolete_files_test.go -->
# sources/storage-engines/pebble/obsolete_files_test.go

Purpose: This file tests obsolete-file cleanup behavior, including a regression for path-qualified stat calls and data-driven cleaner behavior.

Important tests and helpers: `TestScanObsoleteFilesUsesFullPath` opens a DB under non-root directory `db`, forces MANIFEST/OPTIONS rotation, wraps the memory FS in `statTrackingFS`, reopens the DB to trigger `scanObsoleteFiles`, and fails if `Stat` for MANIFEST/OPTIONS is called with a bare filename instead of `db/<name>`. `statTrackingFS` records such calls. `TestCleaner` is data-driven over `testdata/cleaner` and supports `open`, `batch`, `compact`, `flush`, `close`, `list`, and `create-bogus-file`.

Control flow and state: `TestCleaner` keeps a map of open DBs, uses a logging memory FS, can configure archive or readonly cleaning modes, disables asynchronous table stats output, and waits for cleanup to stabilize expected logs. It exercises deletion through normal DB write/flush/compact/open/close workflows rather than direct calls.

Dependencies and integration: The tests use full `pebble.Open`, `Options`, WAL directories, cleaners, batch helpers, compaction, and VFS logging. They validate cleanup as an integrated DB behavior.

Risks and test signals: The path regression test protects non-root and non-local filesystems where bare names resolve incorrectly. The data-driven test catches cleaner ordering and behavior changes, but expected logging can be sensitive to unrelated FS operation changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/obsolete_files_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/open.go -->
# sources/storage-engines/pebble/open.go

Purpose: This file implements Pebble DB opening and related read-only inspection helpers. It orchestrates option validation, recovery, directory locking, format-version handling, version-set initialization, WAL replay, object provider integration, cleanup scheduling, file cache setup, and background scheduling.

Important APIs and types: `FileCacheSize`, `Open`, `resolvedDirs`, `prepareOpenAndLockDirs`, `GetVersion`, `readOptionsFile`, `DBDesc`, `Peek`, `ErrDBDoesNotExist`, `ErrDBAlreadyExists`, `ErrDBNotPristine`, `checkConsistency`, and `walEventListenerAdaptor` are defined here. `Open` is the main public constructor.

Control flow: `Open` clones/validates options, recovers state, handles missing format-version markers and shared-storage minimum format, removes obsolete recovery files, creates cache and DB structures, initializes version sets for new or recovered DBs, initializes WAL manager/failover options, opens delete pacer and file cache, replays WALs, writes a new OPTIONS file, scans/deletes obsolete files, registers compaction scheduler, creates a new WAL, updates read state, ratchets format version if needed, schedules table stats/flush/compaction, closes recovery locks, and installs finalizer checks. Error defers clean up partially opened resources.

State and persistence: It writes OPTIONS files atomically through temp+rename+directory sync, may create/ratchet format markers, opens WALs, updates version state, and triggers obsolete cleanup. `prepareOpenAndLockDirs` creates/opens/locks data, WAL, failover, and recovery directories. `Peek` and `GetVersion` inspect existing files without fully opening the DB.

Dependencies and integration: It ties together `recoverState`, `manifest`, `wal`, `objstorage.Provider`, caches, delete pacer, compaction scheduler, and options. `checkConsistency` uses the object provider to compare local table sizes against MANIFEST state while skipping remote objects.

Risks and test signals: Risks include resource leaks on mid-open failure, format compatibility with shared objects, WAL failover identifier mismatch, lock handling, stale obsolete files, and remote objects skipped by synchronous consistency checks. Broad DB tests cover this path; subset cleanup tests validate open-triggered obsolete scanning.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/open.go -->

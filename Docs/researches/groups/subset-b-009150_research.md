# subset-b-009150 Research

Grouped source-tree-aligned research for the requested Kopia repository, object, splitter, site, snapshot, and policy files. Each section is bounded by the reconciliation markers expected by the research cron.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/object/object_manager_test.go -->
# sources/sync-backup/kopia/repo/object/object_manager_test.go

Purpose: exercises the object package end to end with a fake content manager, covering object writing, reading, seeking, compression, indirect-object creation, concatenation, async writes, checkpointing, and error propagation. The file is a high-value behavioral spec for `Manager`, `objectWriter`, `Open`, `VerifyObject`, and object IDs.

Important APIs/types/functions: `fakeContentManager` implements the content manager surface used by object manager tests: `GetContent`, `WriteContent`, `SupportsContentCompression`, `ContentInfo`, `Flush`, and `PrefetchContents`. `setupTest` builds a `Manager` with `format.ObjectFormat{Splitter:"FIXED-1M"}`. Helpers include `verifyFull`, `verifyIndirectBlock`, `indirectionLevel`, `mustWriteObject`, `makeMaybeCompressibleData`, and `verify`.

Control flow: writer tests feed bytes into `om.NewWriter`, call `Result`, and compare stable object IDs. Compression tests toggle content-manager compression support using a `compressionIDs` map and assert whether compression is represented in content metadata or `Z` object IDs. Indirection tests replace the writer splitter with a small fixed splitter, write different lengths, load index objects, and verify expected blob counts and metadata-compressor headers. Read/seek tests write randomized data, reopen via `Open`, and perform random `Seek`/`Read` samples plus boundary seeks past EOF.

State and persistence behavior: `fakeContentManager` persists content in an in-memory map keyed by deterministic content IDs from SHA-256. It optionally records compression header IDs. Tests validate that small direct objects may write one content, empty/direct cases write none or one, and larger content creates indirect index contents prefixed with metadata content prefix. Checkpoint tests prove buffered bytes are invisible until a splitter flush and that checkpoints are backed by valid content IDs.

Dependencies/integration: depends on `gather`, `content`, `compression`, `format`, `splitter`, `blob`, and `testlogging/testutil`; it uses `errgroup` for the checkpoint/result race. It integrates with `LoadIndexObject`, `Open`, `VerifyObject`, `Manager.Concatenate`, and registered compressors.

Risks: the async write path is race-sensitive, especially mutation of `indirectIndex` while `Result` or `Checkpoint` waits for writes. Compression behavior differs depending on content manager capabilities, so mismatches can change object ID formats. Concatenation can mix empty, direct, compressed, and indirect inputs and must preserve stream length. Error tests show failures may surface on `Write`, `Result`, or `Checkpoint` depending on sync/async flush timing.

Test signals: broad positive coverage across deterministic hashes, custom splitters, direct/indirect reads, all supported compressors, random seeking, EOF behavior, and writer failures. The race test explicitly guards checkpoint validity during concurrent `Result`. It does not use real blob storage; repository-level tests cover that layer.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/object/object_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/object/object_reader.go -->
# sources/sync-backup/kopia/repo/object/object_reader.go

Purpose: implements reading and verifying object data from repository content. It supports direct content objects, compressed direct objects, and recursively indirect objects whose index objects point at chunk object IDs.

Important APIs/types/functions: public `Open(ctx, r, objectID)` returns an `object.Reader`; `VerifyObject(ctx, cr, oid)` confirms all backing contents exist and returns content IDs. `objectReader` implements `Read`, `Seek`, `Close`, and `Length` over an indirect seek table. `LoadIndexObject` decodes JSON `indirectObject` entries, `newRawReader` loads direct content, and `iterateBackingContents` walks content dependencies.

Control flow: `openAndAssertLength` checks whether the ID is indirect. For indirect IDs, it loads the index object, computes total length from the last entry end offset, and returns an `objectReader`. For direct IDs, `newRawReader` gets content bytes, decompresses if the object ID has the compression flag, enforces optional asserted length, and wraps bytes in a `readerWithData`. `Read` lazily opens each chunk by recursively calling `openAndAssertLength`, reads it fully into memory, copies requested bytes, and advances chunk state. `Seek` resolves offsets through binary search on `IndirectObjectEntry.Start/endOffset`.

State and persistence behavior: reader state is transient: current overall position, chunk index, chunk bytes, and chunk-local position. Persistent state is the content manager data plus JSON index objects. `VerifyObject` persists nothing, but walks direct and indirect IDs and invokes `ContentInfo` for each backing content before adding it to a tracker.

Dependencies/integration: depends on `content.Reader`-style interfaces, `compression.DecompressByHeader`, JSON indirect object encoding from `object_writer.go`, `IndirectObjectEntry` and `Reader` definitions elsewhere in the object package, and `contentIDTracker` from the writer file.

Risks: indirect readers load each chunk fully into memory, so very large chunk sizes affect memory use. `openAndAssertLength` assumes non-empty indirect seek tables because it indexes the last entry. Invalid seek offsets below zero are not explicitly rejected before binary search. `VerifyObject` can duplicate work across repeated contents but de-duplicates return IDs through the tracker.

Test signals: object manager tests cover not-found mapping to `ErrObjectNotFound`, compressed and uncompressed reads, randomized seeks, EOF past end, length assertions through indirect chunks, and verification of backing contents.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/object/object_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/object/object_writer.go -->
# sources/sync-backup/kopia/repo/object/object_writer.go

Purpose: implements object writes on top of the content manager, including splitting, optional object-layer or content-layer compression, asynchronous content writes, checkpoints, and indirect index-object generation.

Important APIs/types/functions: `Writer` exposes `Write`, `Close`, `Checkpoint`, and `Result`. `objectWriter` tracks buffers, splitters, compression, prefix, indirect entries, async write semaphore, wait group, and stored write error. `WriterOptions` controls description, content ID prefix, data and metadata compressor names, splitter name, and async write concurrency. Helpers include `flushBufferLocked`, `prepareAndWriteContentChunk`, `maybeCompressedContentBytes`, `checkpointLocked`, and `writeIndirectObject`.

Control flow: `Write` holds `w.mu`, updates `totalLength`, uses `splitter.NextSplitPoint`, appends data to a gather buffer, and flushes at split points. `flushBufferLocked` reserves an indirect index slot and either writes synchronously or clones the buffer into an async goroutine gated by `asyncWritesSemaphore`. `prepareAndWriteContentChunk` decides whether compression belongs in content metadata or object bytes, writes content through `WriteContent`, and stores the resulting direct or compressed object ID in the indirect index. `Result` flushes any remaining or empty buffer and delegates to `checkpointLocked`; `Checkpoint` waits for async writes, returns empty for no flushed chunks, direct ID for one chunk, or writes a JSON index object and wraps it with an indirect ID.

State and persistence behavior: data chunks are persisted through `contentMgr.WriteContent`; indirect indexes are persisted as metadata-prefixed JSON objects when more than one chunk exists. Async write errors are stored and surfaced at checkpoint/result time. `Close` waits for async writes, closes splitter and gather buffer, and notifies the manager that the writer closed.

Dependencies/integration: depends on `gather` for reusable buffers, `content` for content IDs/prefixes, `compression` for compressors and header IDs, `splitter` for chunk boundaries, and manager methods such as `closedWriter` and `newDefaultSplitter`. Its indirect JSON is read by `LoadIndexObject` in `object_reader.go`.

Risks: async writes require careful index reservation before goroutine completion; missing a wait before checkpoint could return incomplete IDs, so `checkpointLocked` waits. Compression behavior changes with `SupportsContentCompression`, and metadata objects always move compression responsibility to the content layer. `Result` flushes an empty buffer for empty objects, so empty-object semantics depend on content manager behavior.

Test signals: object manager tests stress sync and async paths, checkpoint/result races, compression fallback, indirect metadata compression, write errors during sync flush, async flush, checkpoint, and faulty compressor registration.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/object/object_writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/object/objectid.go -->
# sources/sync-backup/kopia/repo/object/objectid.go

Purpose: defines the compact object identifier format used by Kopia object storage. Object IDs wrap content IDs and add optional indirection (`I`) and compression (`Z`) prefixes.

Important APIs/types/functions: `ID` stores `content.ID`, `indirection`, and `compression`. Public methods/functions include `String`, `Append`, `MarshalJSON`, `UnmarshalJSON`, `IndexObjectID`, `ContentID`, `IDsFromStrings`, `IDsToStrings`, `DirectObjectID`, and `ParseID`. Package helpers include `compressed` and `indirectObjectID`; `EmptyID` is the zero object ID.

Control flow: string formatting emits `I` repeated for indirection, then `Z` for direct compressed content, then the content ID. Parsing consumes leading `I`s, optional `Z`, optional legacy `D`, rejects simultaneous indirection and compression, and delegates the remaining bytes to `content/index.ParseID`.

State and persistence behavior: IDs are value types and persist as JSON strings. Indirect IDs do not point straight to content; `IndexObjectID` decrements indirection to obtain the object ID that stores the next-level index. `ContentID` returns false for indirect IDs and returns the compressed flag for direct IDs.

Dependencies/integration: integrates with the content index ID parser and all object reader/writer paths. Snapshot manifests and repository APIs persist object IDs via JSON marshaling.

Risks: the legacy `D` prefix remains accepted, so parsing rules must stay compatible with old repositories. Compression and indirection are mutually exclusive at the same level; allowing both would make reader dispatch ambiguous. `Append` and `String` must remain byte-for-byte compatible because tests and manifests rely on stable IDs.

Test signals: `objectid_test.go` covers valid/invalid parse forms, string/list conversion, and string rendering for direct, indirect, and compressed IDs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/object/objectid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/object/objectid_test.go -->
# sources/sync-backup/kopia/repo/object/objectid_test.go

Purpose: verifies object ID parsing and formatting compatibility.

Important APIs/types/functions: tests cover `ParseID`, `IDsFromStrings`, `IDsToStrings`, and `ID.String`. `mustParseID` is a local helper, and `TestMain` installs the shared test harness.

Control flow: `TestParseObjectID` enumerates accepted legacy/direct/indirect/compressed strings and malformed cases. Conversion tests parse multiple IDs from strings and render them back. String tests ensure `String()` preserves exact canonical text for parsed IDs.

State and persistence behavior: no persistence is performed, but JSON/string stability is indirectly protected by canonical string expectations. The tests validate compatibility with legacy `D` direct prefixes and multiple `I` indirection prefixes.

Dependencies/integration: uses `testutil.MyTestMain` and `testify/require`. It exercises parser integration with `content/index.ParseID` through `object.ParseID`.

Risks: parser changes could silently break old manifests or object references. Invalid combinations like compressed indirect IDs must remain rejected.

Test signals: focused unit tests for syntactic compatibility; behavior of IDs in readers/writers is covered in object manager and repository tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/object/objectid_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/open.go -->
# sources/sync-backup/kopia/repo/open.go

Purpose: contains repository open logic for local/direct blob access and API-server access. It builds the storage, cache, format, content, object, manifest, metrics, throttling, logging, retention, and close-management layers.

Important APIs/types/functions: `Options` controls tracing, content logs, time source, repository log disabling, upgrade behavior, callbacks, fatal handling, and test-only feature ignoring. Public `Open` dispatches between API server and direct configurations. Internal helpers include `getContentCacheOrNil`, `openAPIServer`, `openDirect`, `openWithConfig`, `deriveHMACSecret`, `handleMissingRequiredFeatures`, `wrapLockingStorage`, `addThrottler`, `upgradeLockMonitor`, and `throttlingLimitsFromConnectionInfo`.

Control flow: `Open` normalizes the config path, loads local config, rejects writable permissive cache loading, and dispatches to API-server or direct open. Direct open creates blob storage, wraps read-only storage if needed, applies client defaults, then `openWithConfig` creates format manager, checks required features, derives cache HMAC secret, applies throttling, retention locks, upgrade-lock waiting/monitoring, diagnostics logging, content manager, write manager, object manager, manifest manager, and ref-counted closer. API open derives a password-protected persistent content cache, creates immutable server parameters, and opens the gRPC repository.

State and persistence behavior: reads config and format/blobcfg blobs; may update config throttling when throttler settings change. It derives cache integrity/encryption material from repository secrets and password. Retention-enabled repositories wrap `PutBlob` options for protected prefixes. Upgrade monitoring checks format-manager loaded time on storage operations and may fatal-error on unsupported features.

Dependencies/integration: integrates with `blob.NewStorage`, `readonly`, `beforeop`, `storagemetrics`, `throttling`, `format.Manager`, `content.NewSharedManager`, `object.NewObjectManager`, `manifest.NewManager`, `repodiag`, feature gating, and cache protection.

Risks: open order is security-sensitive: feature and upgrade checks must happen before normal repository IO. Cache key derivation must match server repository settings or cache reads fail. `upgradeLockMonitor` invokes `OnFatalError`, which defaults to `os.Exit(1)`, so tests override or set test flags. Retention wrapping must only affect repository-managed blob prefixes.

Test signals: repository tests cover password changes, retention blob behavior, write sessions, derived keys, metrics, and API server callback behavior. Feature/upgrade paths are likely covered elsewhere in the repo.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/open.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/recently_read.go -->
# sources/sync-backup/kopia/repo/recently_read.go

Purpose: provides a small thread-safe ring/set cache for content IDs recently read by repository code.

Important APIs/types/functions: `recentlyRead` stores `contentList`, `next`, and `contentSet` under a mutex. Methods are `add(content.ID)` and `exists(content.ID)`.

Control flow: `add` is nil-safe, lazily initializes fixed-size storage based on `numRecentReadsToCache`, deletes the evicted ring slot from the set, inserts the new ID, and advances the ring pointer. `exists` is nil-safe and checks the set under the same mutex.

State and persistence behavior: purely in-memory, non-persistent, bounded by the configured ring length. Duplicate adds keep the set entry and still advance the ring.

Dependencies/integration: depends on `repo/content.ID` and a package-level `numRecentReadsToCache` defined elsewhere. It is intended as a helper for avoiding redundant recent-read work.

Risks: duplicate content IDs in the ring can cause one eviction to delete the set entry even if the same ID appears in another slot, making this a lossy recency hint rather than an exact cache. That is acceptable only if callers treat it as advisory.

Test signals: no direct tests in this file; expected to be covered indirectly by cache/read behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/recently_read.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/refcount_closer.go -->
# sources/sync-backup/kopia/repo/refcount_closer.go

Purpose: coordinates cleanup of shared repository resources when the last repository or writer reference closes.

Important APIs/types/functions: `closeFunc` is a context-aware cleanup callback. `refCountedCloser` holds atomic `refCount`, atomic `closed`, and ordered `closers`. Methods are `Close`, `addRef`, `registerEarlyCloseFunc`, and constructor `newRefCountedCloser`.

Control flow: new closers start with one reference. Each writer clone calls `addRef`. `Close` decrements the count and returns immediately unless it reaches zero. On final close, it panics if already closed, marks closed, invokes all cleanup functions, and returns `errors.Join` of their results. `registerEarlyCloseFunc` prepends a cleanup function by wrapping it into the front of the closer list.

State and persistence behavior: in-memory lifecycle state only. It controls persistent resource flushing/closing indirectly by invoking registered storage, metrics, diagnostics, and cache closers.

Dependencies/integration: used by direct and server repository parameter structs in `open.go`/`repository.go`. Depends on standard `sync/atomic` and `errors.Join`.

Risks: extra `Close` calls after the count reaches zero can decrement negative and avoid the already-closed panic path; callers must balance references. Registering early close functions mutates the slice without synchronization, so it should happen during setup.

Test signals: repository writer-scope and close-path tests indirectly exercise reference balancing; no direct unit tests in this file.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/refcount_closer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/repo_benchmarks_test.go -->
# sources/sync-backup/kopia/repo/repo_benchmarks_test.go

Purpose: benchmarks repository object writing with and without deduplication.

Important APIs/types/functions: `BenchmarkWriterDedup1M` writes the same 4 MiB zero buffer repeatedly. `BenchmarkWriterNoDedup1M` writes moving slices of random data to reduce deduplication. Both use `repotesting.NewEnvironment`, `RepositoryWriter.NewObjectWriter`, and object `Result`.

Control flow: the dedup benchmark primes the repository with one object, then repeatedly writes identical data in `b.Loop()`. The no-dedup benchmark fills a random buffer, resets timer, and writes shifting chunks, changing chunk size when the moving window reaches the buffer end.

State and persistence behavior: benchmarks create a test repository and persist object contents and indexes through normal repository paths. Writers are closed after results to return splitters/resources.

Dependencies/integration: integrates object writer, repository write manager, content deduplication, format v2, random data generation, and `testify/require`.

Risks: benchmark naming says `1M` but buffers are 4 MiB; no-dedup chunk-size mutation may create variable object sizes over time. Results can be sensitive to test storage backend and compression/metadata behavior.

Test signals: benchmark-only; useful for performance regressions in write/dedup paths, not correctness gates.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/repo_benchmarks_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/repository.go -->
# sources/sync-backup/kopia/repo/repository.go

Purpose: defines the public repository interfaces and implements direct repository operations for objects, manifests, write sessions, flushing, key derivation, metrics, and lifecycle.

Important APIs/types/functions: interfaces `Repository`, `RepositoryWriter`, `RemoteRetentionPolicy`, `RemoteNotifications`, `DirectRepository`, and `DirectRepositoryWriter` define the repo surface. `directRepository` holds blob/content/object/manifest managers and immutable parameters. Key functions include `NewDirectWriter`, `Flush`, `WriteSession`, `DirectWriteSession`, `replaceManifestsHelper`, and `handleWriteSessionResult`.

Control flow: read APIs delegate to object/content/manifest managers. `NewDirectWriter` creates an isolated content write manager, manifest manager, and object manager with a unique writer ID, then increments the shared closer reference. `Flush` runs before callbacks, flushes manifests then contents, and runs after callbacks. `WriteSession` and `DirectWriteSession` create writers, run callbacks, flush on success or configured failure, and close writers in a defer.

State and persistence behavior: write sessions isolate unflushed content visibility until `Flush`. Manifests are persisted via `PutManifest`/`ReplaceManifests`; content/index blobs persist through content manager flushes. `DeriveKey` uses either master key for password-change-capable formats or legacy format encryption key for old/upgraded v1 repositories. `UpdateDescription` mutates client options in memory.

Dependencies/integration: integrates `object.Manager`, `content.WriteManager/SharedManager`, `manifest.Manager`, `format.Manager`, blob storage, throttling, metrics, diagnostics, OpenTelemetry tracing, and snapshot policy callbacks.

Risks: write-session flush semantics are critical: errors should not flush unless `FlushOnFailure` is true. `replaceManifestsHelper` sleeps to avoid Windows timestamp flakiness, which can slow tight loops. `Close` handling relies on ref-count balance. `DeriveKey` must preserve legacy behavior for upgraded repositories.

Test signals: repository tests cover writer isolation/visibility, flush on success/failure, callbacks, object reads, metrics, retention, and key derivation across formats.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/repository.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/repository_test.go -->
# sources/sync-backup/kopia/repo/repository_test.go

Purpose: integration test suite for repository behavior across format versions and API/direct paths.

Important APIs/types/functions: tests use `formatSpecificTestSuite`, `writeObject`, `verify`, `verifyNotFound`, `mustParseObjectID`, and `ensureMapEntry`. Covered tests include writer ID stability, packing/dedup, HMAC formats, reader not-found, format-specific expected IDs, writer scope, retention blob handling, retention on object writes, write-session callbacks and failure flushing, password change, metrics, metric registry mapping, and `DeriveKey`.

Control flow: suite cases create repotesting environments for format versions, write objects through repository writers, flush/reopen repositories, compact indexes, and verify readback. Writer-scope tests create multiple independent writers and assert unflushed visibility isolation before and after flush. Retention tests wrap storage behavior through versioned maps and before-operation hooks. API callback tests connect through a test server and reuse write-session semantics.

State and persistence behavior: exercises real repository config, format blobs, blobcfg blobs, object/content blobs, content indexes, manifests, and cache/metrics state. It verifies that unflushed writer content remains private, flush makes content globally visible, retention settings protect selected blob prefixes, and changed passwords reopen only in supported formats.

Dependencies/integration: uses `repotesting`, `servertesting`, cache storage, epoch/indexblob prefixes, content/object/format internals, metrics IDs, and before-operation blob wrappers.

Risks: deterministic object ID expectations are brittle but intentional compatibility guards. Tests assume timing thresholds for metrics duration and Windows timestamp behavior in manifest replacement. Retention tests depend on storage wrapper behavior.

Test signals: very strong integration coverage for repository invariants; it does not directly exercise all open-time upgrade-lock branches but covers most direct user-visible repository operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/repository_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/server_repo_cache_enc_key.go -->
# sources/sync-backup/kopia/repo/server_repo_cache_enc_key.go

Purpose: defines supported key-derivation algorithms for encrypting local content cache used by API-server repository connections.

Important APIs/types/functions: `DefaultServerRepoCacheKeyDerivationAlgorithm` is `crypto.ScryptAlgorithm`. `SupportedLocalCacheKeyDerivationAlgorithms` returns scrypt and PBKDF2 algorithm names.

Control flow: no branching beyond returning the supported slice. `open.go` uses the default when server info omits an algorithm.

State and persistence behavior: no local state. The selected algorithm affects persistent cache encryption compatibility.

Dependencies/integration: depends on `internal/crypto` algorithm constants and is consumed by API server connection/cache code.

Risks: changing defaults or supported algorithms can make existing encrypted caches unreadable or alter connection performance/security properties. The returned slice is newly allocated by literal, so callers can mutate it without changing globals.

Test signals: indirectly covered by API server repository open tests; no direct unit test here.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/server_repo_cache_enc_key.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/server_repository_params.go -->
# sources/sync-backup/kopia/repo/server_repository_params.go

Purpose: stores immutable parameters shared by server-backed repository clients.

Important APIs/types/functions: `immutableServerRepositoryParameters` holds hash function, object format, client options, metrics registry, content cache, before-flush callbacks, and `refCountedCloser`. Methods `Metrics` and `ClientOptions` expose registry and client settings.

Control flow: simple getters; setup happens in `openAPIServer` and remote repository code.

State and persistence behavior: in-memory immutable session state. `contentCache` points to a persistent encrypted cache, but this struct only references it.

Dependencies/integration: depends on `cache.PersistentCache`, `metrics.Registry`, `format.ObjectFormat`, `hashing.HashFunc`, and repository callbacks. It embeds `refCountedCloser` for shared cleanup.

Risks: fields are not protected against mutation by referenced objects; callers should treat the struct as immutable by convention. Close lifetime is shared with remote repository clients.

Test signals: API server write-session test indirectly exercises before-flush callbacks and close behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/server_repository_params.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/splitter/splitter.go -->
# sources/sync-backup/kopia/repo/splitter/splitter.go

Purpose: defines the splitter interface, splitter size constants, registered splitter factories, and default algorithm for object chunking.

Important APIs/types/functions: `Splitter` exposes `NextSplitPoint`, `MaxSegmentSize`, `Reset`, and `Close`. `Factory` constructs splitters. `SupportedAlgorithms` returns sorted registered names. `GetFactory` fetches a factory by name. `splitterFactories` registers fixed sizes, BuzHash dynamic sizes, Rabin-Karp dynamic sizes, and legacy aliases. `DefaultAlgorithm` is `DYNAMIC-4M-BUZHASH`.

Control flow: registration is static. `SupportedAlgorithms` copies map keys and sorts them. `GetFactory` returns nil for unknown names, letting callers fall back to defaults.

State and persistence behavior: no persisted state, but chosen splitter names are stored in repository/object policy configuration and affect future content chunking/dedup behavior.

Dependencies/integration: used by object writers and snapshot splitter policy. Dynamic factories are wrapped with pooling for named modern algorithms.

Risks: changing factory names or default algorithm changes content chunking and deduplication characteristics. Legacy `DYNAMIC` maps to BuzHash instead of an old licensed implementation, so outputs differ from historical dynamic splitting.

Test signals: splitter tests verify fixed, BuzHash, Rabin-Karp, and pooled splitter stability over deterministic random data.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/splitter/splitter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/splitter/splitter_buzhash32.go -->
# sources/sync-backup/kopia/repo/splitter/splitter_buzhash32.go

Purpose: implements content-defined chunking with a 32-bit BuzHash rolling hash.

Important APIs/types/functions: `buzhash32Splitter` tracks rolling hash, mask, byte count, minimum size, and maximum size. Methods implement `Close`, `Reset`, `NextSplitPoint`, and `MaxSegmentSize`. `newBuzHash32SplitterFactory(avgSize)` creates configured splitters.

Control flow: `NextSplitPoint` skips split checks until roughly half the average size while still rolling the last sliding-window bytes, then scans until max size for `Sum32()&mask == 0`, resetting count and returning consumed bytes at split. If max size is reached without a hash hit, it forces a split.

State and persistence behavior: splitter state is in-memory rolling hash/count. Reset seeds the rolling hash with a zero sliding window for deterministic initial behavior.

Dependencies/integration: depends on `github.com/chmduquesne/rollinghash/buzhash32`, shared window/size constants, and splitter factory registration in `splitter.go`.

Risks: comments note avoiding interface dispatch for performance. Off-by-one behavior around `minSize - count - 1` and max-size forced splits directly affects chunk boundaries and dedup. Average size must be a power of two for the mask logic.

Test signals: splitter stability tests assert exact split count, average, min, and max for multiple BuzHash sizes and input feeding modes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/splitter/splitter_buzhash32.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/splitter/splitter_fixed.go -->
# sources/sync-backup/kopia/repo/splitter/splitter_fixed.go

Purpose: implements fixed-size object chunking.

Important APIs/types/functions: `fixedSplitter` stores current offset and chunk length. Methods implement `Close`, `Reset`, `NextSplitPoint`, and `MaxSegmentSize`. `Fixed(length)` returns a splitter factory.

Control flow: `NextSplitPoint` computes remaining bytes until the configured boundary. If the provided slice is shorter, it consumes all bytes and returns `-1`; otherwise it resets offset and returns the boundary length.

State and persistence behavior: in-memory byte count only. The configured length affects persisted object chunk boundaries when used by object writers.

Dependencies/integration: registered under fixed algorithm names and used in tests and repository defaults for older/test configurations.

Risks: zero or negative lengths are not guarded here; callers/factories must provide valid lengths. Deterministic fixed chunking can reduce content-defined dedup effectiveness across shifted data.

Test signals: splitter tests assert exact fixed split counts and segment sizes, including pooled fixed splitters.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/splitter/splitter_fixed.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/splitter/splitter_pool.go -->
# sources/sync-backup/kopia/repo/splitter/splitter_pool.go

Purpose: wraps splitter factories with `sync.Pool` reuse to reduce allocations in hot write paths.

Important APIs/types/functions: `recyclableSplitter` embeds a `Splitter` and its pool. Its `Close` resets, closes, and returns the underlying splitter to the pool. `pooled(f Factory)` returns a factory that gets splitters from the pool or creates new ones.

Control flow: pooled factory checks `pool.Get`; nil creates `recyclableSplitter{f(), pool}`, non-nil wraps the retrieved splitter. `Close` is the return-to-pool hook.

State and persistence behavior: in-memory object pooling only; no persisted data. Reused splitter state is reset before pooling.

Dependencies/integration: used for registered modern splitter factories in `splitter.go`; object writers must call `Close` to return splitters.

Risks: if callers forget `Close`, pooling is ineffective. Returning a splitter while still in use would corrupt chunking state, but normal writer ownership prevents that. Type assertion assumes only `Splitter` values are placed in the pool.

Test signals: splitter stability tests run pooled variants twice to detect state leakage through reuse.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/splitter/splitter_pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/splitter/splitter_rabinkarp64.go -->
# sources/sync-backup/kopia/repo/splitter/splitter_rabinkarp64.go

Purpose: implements content-defined chunking with a 64-bit Rabin-Karp rolling hash.

Important APIs/types/functions: `rabinKarp64Splitter` mirrors the BuzHash splitter with `rabinkarp64.RabinKarp64`, `mask`, `count`, `minSize`, and `maxSize`. Methods implement the splitter interface. `newRabinKarp64SplitterFactory(avgSize)` configures min/max/mask.

Control flow: reset seeds a zero window. `NextSplitPoint` fast-forwards until minimum size, then rolls each byte looking for `Sum64()&mask == 0`, or forces a split at max size.

State and persistence behavior: in-memory rolling hash state; splitter choice affects persisted chunk layout and dedup opportunities.

Dependencies/integration: depends on `github.com/chmduquesne/rollinghash/rabinkarp64`; registered under `DYNAMIC-*-RABINKARP` algorithms.

Risks: the file comment says not using Hash32 although this is 64-bit; the rationale is still interface-dispatch performance. As with BuzHash, average size must align with mask assumptions and off-by-one changes are format-affecting for chunk boundaries.

Test signals: splitter stability tests assert exact split statistics for Rabin-Karp sizes and feeding modes, including pooled reuse.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/splitter/splitter_rabinkarp64.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/splitter/splitter_test.go -->
# sources/sync-backup/kopia/repo/splitter/splitter_test.go

Purpose: validates deterministic chunk-boundary behavior for fixed, BuzHash, Rabin-Karp, and pooled splitters.

Important APIs/types/functions: `TestSplitterStability` drives all cases. Helpers `getSplitPoints`, `getSplitPointsByteByByte`, and `getSplitPointsRandomSlices` feed the same data in whole-slice, byte-by-byte, and random-slice modes.

Control flow: a deterministic random 5,000,000-byte buffer is generated. Each splitter factory is tested twice, possibly with reduced cases on constrained architectures. For each feeding mode, the test checks `MaxSegmentSize`, split count, average segment size, minimum split, and maximum split. Splitters are closed after use to test pool reset.

State and persistence behavior: no persistence, but expected stats encode the compatibility surface of chunking algorithms.

Dependencies/integration: depends on splitter factories and `testutil.ShouldReduceTestComplexity`.

Risks: exact numeric expectations are intentionally brittle; dependency updates to rollinghash or algorithm tweaks will fail tests and signal changed chunking behavior. Random-slice helper uses global `rand.Intn`, so test determinism depends on global seed stability for chunk feeding sizes, though split outcomes should be independent of input chunking.

Test signals: strong unit coverage for splitter determinism and state isolation across pooled reuse.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/splitter/splitter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/suite_test.go -->
# sources/sync-backup/kopia/repo/suite_test.go

Purpose: provides the repository package test harness for running format-specific tests against format versions 1, 2, and 3.

Important APIs/types/functions: `TestMain` delegates to `testutil.MyTestMain`. `formatSpecificTestSuite` stores a `format.Version`. `TestFormatV1`, `TestFormatV2`, and `TestFormatV3` call `testutil.RunAllTestsWithParam`.

Control flow: the test utility reflects over methods on `formatSpecificTestSuite` and runs each with the supplied format version.

State and persistence behavior: no direct persistence; it controls creation of repotesting repositories in suite methods.

Dependencies/integration: depends on `internal/testutil` and `repo/format`. It is the bridge that makes tests in `repository_test.go` execute against multiple repository formats.

Risks: adding suite methods can multiply runtime by three. Format-specific assumptions must be handled inside tests when behavior differs.

Test signals: meta-test harness only; actual assertions live in suite methods.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/token.go -->
# sources/sync-backup/kopia/repo/token.go

Purpose: encodes and decodes opaque repository connection tokens containing storage connection info and optional password.

Important APIs/types/functions: `tokenInfo` JSON schema has `Version`, `Storage`, and optional `Password`. `directRepository.Token` delegates to `EncodeToken`. `EncodeToken` marshals version `1` and raw-URL-base64 encodes it. `DecodeToken` decodes, unmarshals, checks version, and returns `blob.ConnectionInfo` plus password.

Control flow: decoding intentionally returns generic `"unable to decode token"` for base64 and JSON failures, and `"unsupported token version"` for version mismatch.

State and persistence behavior: tokens are serialized connection state and may persist passwords if provided. No repository mutation occurs.

Dependencies/integration: depends on `blob.ConnectionInfo` JSON and standard base64/JSON. Used for sharing or reconnecting to repositories.

Risks: tokens can contain plaintext passwords inside base64 JSON, so callers must treat them as secrets. Schema versioning is strict; future versions need migration or compatibility handling.

Test signals: no direct tests in this subset; token behavior may be covered elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/token.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/userhost.go -->
# sources/sync-backup/kopia/repo/userhost.go

Purpose: derives default username and hostname for repository client options and source labels.

Important APIs/types/functions: `GetDefaultUserName(ctx)` reads `os/user.Current`, logs and returns `"nobody"` on error, and strips Windows domain prefixes. `GetDefaultHostName(ctx)` reads `os.Hostname`, logs and returns `"nohost"` on error, lowercases and truncates at the first dot.

Control flow: both functions are fallback-safe and log errors through the repo logger. Hostname normalization reduces FQDNs to short lowercase hosts.

State and persistence behavior: no direct persistence, but returned values are stored in client options, session metadata, snapshot labels, and policy labels.

Dependencies/integration: uses standard `os`, `os/user`, `runtime`, `strings`, and package logger.

Risks: username/hostname normalization affects snapshot source identity; changes can split or merge policy/snapshot histories. Windows domain stripping assumes backslash separator.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/userhost.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/site/Makefile -->
# sources/sync-backup/kopia/site/Makefile

Purpose: defines build, serve, dependency install, cleanup, and generated CLI reference tasks for the Kopia Hugo site.

Important APIs/types/functions: targets are `all`, `install-tools`, `build`, `server`, `node_modules`, `clean`, and `gen-cli-reference-pages`. It includes `../tools/tools.mk` and uses variables such as `npm`, `cli2mdbin`, `hugo`, `TOOLS_DIR`, `npm_flags`, and `npm_install_or_ci`.

Control flow: `all` builds. `build` installs tools, generates CLI reference pages, installs node modules, then runs Hugo. `server` starts Hugo server with configurable `WATCH=false`. `node_modules` runs npm install/ci without audit then runs production audit excluding dev dependencies. Netlify production builds export `HUGO_ENV=production`.

State and persistence behavior: writes generated site output under `public/`, Hugo resources under `resources/`, node dependencies under `node_modules/`, and generated CLI reference content through `cli2md`. `clean` removes generated output, dependencies, and tool directory.

Dependencies/integration: integrates Hugo, npm, generated CLI reference tooling, Netlify environment variables, and repository-level tools.mk.

Risks: `clean` removes shared tool directory. The comment warns that putting tools under the site directory can break `make server` due to open-file pressure from `node_modules`. Audit omits dev dependencies even though all package dependencies are dev dependencies for the site build.

Test signals: build correctness is validated by running make targets externally; no test code here.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/site/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/site/hugo.toml -->
# sources/sync-backup/kopia/site/hugo.toml

Purpose: configures the Kopia documentation website built with Hugo and the Docsy theme.

Important APIs/types/functions: sets `baseURL`, title, robots, git info, content/static directories, language settings, disabled taxonomy kinds, Chroma/Pygments highlighting, top menu entries, blog permalinks, BlackFriday options, image processing, UI params, feedback text, footer links, and Hugo module imports for `github.com/google/docsy` and dependencies.

Control flow: Hugo reads this declarative config during build/server. Menu and module sections drive navigation and theme resolution. `services.googleAnalytics` is intentionally empty because analytics are handled manually, while feedback config is enabled but depends on analytics ID to function.

State and persistence behavior: no runtime state. The config controls generated URLs, rendered navigation, theme modules, and image processing output.

Dependencies/integration: integrates with Hugo extended version at least 0.73.0, Docsy modules, Git metadata, site content under `content`, static files under `static`, and GitHub edit links pointing at the `site` subdirectory on `master`.

Risks: `enableGitInfo` depends on Git availability in build environments. BlackFriday settings are legacy relative to modern Hugo/Goldmark defaults. Module proxy is set to `direct`, which can affect reproducibility/network behavior.

Test signals: validated by Hugo build; no automated test in this file.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/site/hugo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/site/package-lock.json -->
# sources/sync-backup/kopia/site/package-lock.json

Purpose: pins the npm dependency graph for the site build tooling.

Important APIs/types/functions: lockfile version is 3. Root package `site@0.0.1` has dev dependencies `autoprefixer`, `postcss`, and `postcss-cli`. The full lock contains 76 package entries, including PostCSS, Autoprefixer, Browserslist/caniuse data, chokidar/glob tooling, yargs, yaml, and supporting transitive packages.

Control flow: npm uses this file for deterministic install/ci in the Makefile `node_modules` target. Package entries include versions, resolved tarball URLs, integrity hashes, license metadata, engines, bins, peer dependencies, and funding fields.

State and persistence behavior: persists exact package resolution and integrity data, but not installed files. It is expected to stay in sync with `package.json`.

Dependencies/integration: consumed by npm and the site Makefile. It locks the dependency graph for CSS processing and likely theme-related PostCSS commands.

Risks: lockfile contains registry URLs and old transitive packages may age independently from `package.json` ranges. Updating package ranges without refreshing the lock can produce drift. Because dependencies are build-time tooling, supply-chain and audit posture matters for release builds.

Test signals: `npm ci`/`npm install` and `npm audit --omit=dev` in the Makefile are the operational checks; no source tests here.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/site/package-lock.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/site/package.json -->
# sources/sync-backup/kopia/site/package.json

Purpose: declares Node package metadata and development dependencies for the Kopia site.

Important APIs/types/functions: package name `site`, version `0.0.1`, description `"Kopia site."`, `main` set to `none.js`, license `ISC`, and dev dependencies `autoprefixer`, `postcss`, and `postcss-cli`.

Control flow: npm reads dependency ranges during install/ci; build commands are in the Makefile rather than npm scripts.

State and persistence behavior: no runtime state; this is the source of dependency intent, while `package-lock.json` pins actual versions.

Dependencies/integration: integrates with site CSS processing and the Makefile `node_modules` target.

Risks: no npm scripts means build behavior is split across Makefile and package metadata. Dependency ranges allow minor/patch updates unless lockfile is used.

Test signals: install/audit/build commands validate dependency usability.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/site/package.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/site/static/favicons/browserconfig.xml -->
# sources/sync-backup/kopia/site/static/favicons/browserconfig.xml

Purpose: provides Microsoft browser tile metadata for Kopia favicons.

Important APIs/types/functions: XML root `browserconfig` contains `msapplication/tile`, a `square150x150logo` pointing to `/favicons/mstile-150x150.png`, and tile color `#da532c`.

Control flow: browsers that support this metadata fetch it from the static site and use it for pinned tiles.

State and persistence behavior: static asset configuration only. It is copied into Hugo output with other static files.

Dependencies/integration: depends on the referenced PNG existing under static favicons and on the site serving `/favicons/...` paths.

Risks: missing or renamed favicon assets break tile rendering. Color changes affect platform branding.

Test signals: validated by static site build/output inspection or browser favicon checks; no code tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/site/static/favicons/browserconfig.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/manager.go -->
# sources/sync-backup/kopia/snapshot/manager.go

Purpose: manages snapshot manifests in the repository: listing sources, listing/loading/saving/updating snapshots, finding snapshots by root object, and locating previous manifests for incremental snapshots.

Important APIs/types/functions: constants `ManifestType`, `UsernameLabel`, `HostnameLabel`, and `PathLabel`; `ErrSnapshotNotFound`; functions `ListSources`, `ListSnapshots`, `LoadSnapshot`, `SaveSnapshot`, `LoadSnapshots`, `ListSnapshotManifests`, `FindSnapshotsByRootObjectID`, `UpdateSnapshot`, and `FindPreviousManifests`.

Control flow: snapshot source labels are converted by `sourceInfoToLabels` and `sourceInfoFromLabels`. Listing uses repository manifest label searches. Loading validates manifest type and maps missing manifests to `ErrSnapshotNotFound`. Saving validates host/user/path, clears `man.ID`, merges tags into labels while rejecting duplicate reserved keys, writes the manifest, and updates `man.ID`. `LoadSnapshots` launches goroutines with a 50-item semaphore and filters failed loads. `FindPreviousManifests` selects the latest complete snapshot and incomplete snapshots after it, optionally bounded by time.

State and persistence behavior: snapshot manifests persist through repository manifests with source labels plus optional tags. `UpdateSnapshot` writes a new manifest and deletes the old ID if changed. `LoadSnapshots` ignores failed individual loads after logging, so partially corrupt/missing sets can return successful subsets.

Dependencies/integration: depends on repository manifest APIs, `fs.UTCTimestamp`, `object.ID`, logging, and snapshot manifest structures from `manifest.go`.

Risks: concurrent `LoadSnapshots` writes distinct slice indexes but silently drops failures, which callers must tolerate. Tag keys colliding with reserved labels are rejected to preserve query semantics. Source label identity is sensitive to host/user/path normalization.

Test signals: likely covered by snapshot manager tests elsewhere; policy expiration code depends on listing snapshots from this file.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/manifest.go -->
# sources/sync-backup/kopia/snapshot/manifest.go

Purpose: defines persistent snapshot manifest and directory-entry schemas plus sorting/grouping helpers.

Important APIs/types/functions: `Manifest` stores ID, source, description, times, stats, incomplete reason, root entry, tags, storage stats, and pins. `UpdatePins`, `RootObjectID`, `Clone`, `GroupBySource`, and `SortByTime` are key methods/functions. Types include `EntryType`, `Permissions`, `DirEntry`, `DirManifest`, `StorageStats`, and `StorageUsageDetails`.

Control flow: `UpdatePins` merges additions/removals through a map, sorts pins, and reports whether anything changed. `Permissions` marshals non-zero values as octal strings and unmarshals using `strconv.ParseInt` with base detection. `Clone` shallow-copies manifest/entry and deep-copies `DirSummary`. Grouping maps manifests by `SourceInfo`; sorting clones input and orders by start time with end time tie-breaker, reversible via the `reverse` flag.

State and persistence behavior: JSON tags define durable manifest format. `RetentionReasons` is not persisted. `StorageStats` is persisted when populated but comments note ordering-dependent usage values. Atomic-check annotations mark storage usage counters.

Dependencies/integration: depends on `fs`, repository `manifest.ID`, and `object.ID`. Directory manifests are stored as object streams by snapshot upload/read paths.

Risks: `Permissions.MarshalJSON` returns `nil, nil` for zero permissions, which relies on JSON encoding behavior and may produce surprising output if used outside omitempty contexts. `Clone` does not deep-copy maps/slices like tags or pins. Storage stats depend on traversal order and should not be treated as absolute independent facts.

Test signals: sorting/grouping/pin behavior may be covered elsewhere; this file is schema-heavy and validated indirectly by snapshot save/load tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/manifest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/actions_policy.go -->
# sources/sync-backup/kopia/snapshot/policy/actions_policy.go

Purpose: defines snapshot action-command policy fields and inheritance behavior.

Important APIs/types/functions: `ActionsPolicy` contains non-inherited `BeforeFolder`/`AfterFolder` commands and inherited `BeforeSnapshotRoot`/`AfterSnapshotRoot` commands. `ActionCommand` stores command path, args, inline script, timeout, and mode. `ActionsPolicyDefinition` tracks definition sources for inherited root commands. Methods `Merge` and `MergeNonInheritable` apply inheritance.

Control flow: `Merge` fills unset snapshot-root commands from a source policy and records definition source. `MergeNonInheritable` copies folder-level commands from the most specific policy after inherited merge is complete.

State and persistence behavior: policy fields persist in policy manifests as JSON. Definition source info is computed, not persisted as part of the policy.

Dependencies/integration: used by `MergePolicies` and snapshot upload action execution code elsewhere. Depends on `snapshot.SourceInfo` for definition tracking.

Risks: folder-level commands are intentionally non-inheritable; treating them as inherited could execute commands in unintended directories. `Mode` is a free string, so validation likely lives elsewhere or may be lax.

Test signals: policy merge tests cover inherited policy mechanics broadly; action-specific execution is outside this file.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/actions_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/compression_policy.go -->
# sources/sync-backup/kopia/snapshot/policy/compression_policy.go

Purpose: defines file and metadata compression policy and file-level compressor selection.

Important APIs/types/functions: `CompressionPolicy` includes compressor name, only/never extension lists, no-parent flags, and min/max size thresholds. `MetadataCompressionPolicy` stores metadata compressor. Definition structs track source fields. Methods include `CompressorForFile`, `CompressionPolicy.Merge`, `MetadataCompressionPolicy.Merge`, and `MetadataCompressor`.

Control flow: `CompressorForFile` returns no compressor for `"none"`, below min, above max, or extension in `NeverCompress`. If `OnlyCompress` is non-empty and the extension is present, it returns the configured compressor; otherwise it falls through to the configured compressor. Merge helpers fill scalar values and union extension lists unless no-parent flags prevent future parent merges.

State and persistence behavior: policy persists as JSON in manifests. The chosen compressor affects object writer options and persisted object/content compression metadata.

Dependencies/integration: depends on `fs.Entry`, `repo/compression.Name`, and policy merge helpers.

Risks: `OnlyCompress` semantics as implemented do not restrict compression to only listed extensions; if a file extension is not in `OnlyCompress`, the function still returns the compressor unless blocked by `NeverCompress` or size. That behavior may be intentional or a policy bug. Extension lists must be sorted for `sort.SearchStrings`; merge sorts unioned lists, but user-provided lists used directly by `CompressorForFile` need ordering.

Test signals: no direct tests in this subset; compression behavior is indirectly visible in object/repository tests and policy merge tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/compression_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/error_handling_policy.go -->
# sources/sync-backup/kopia/snapshot/policy/error_handling_policy.go

Purpose: defines optional error-handling behavior for snapshot traversal.

Important APIs/types/functions: `ErrorHandlingPolicy` has optional booleans for file errors, directory errors, and unknown entry types. `ErrorHandlingPolicyDefinition` records definition sources. `Merge` fills unset optional values from a source policy.

Control flow: merge delegates to `mergeOptionalBool`, preserving the first non-nil value in most-specific-to-general policy order.

State and persistence behavior: optional booleans persist as JSON only when set, allowing explicit false to differ from unspecified.

Dependencies/integration: used by policy merging and snapshot upload error handling. Depends on `OptionalBool` and `snapshot.SourceInfo`.

Risks: nil vs false is semantically important; code consuming these fields must use `OrDefault` rather than direct boolean casts.

Test signals: `error_handling_policy_test.go` specifically verifies merge semantics for nil, false, true, and partial values.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/error_handling_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/error_handling_policy_test.go -->
# sources/sync-backup/kopia/snapshot/policy/error_handling_policy_test.go

Purpose: verifies `ErrorHandlingPolicy.Merge` preserves optional boolean semantics.

Important APIs/types/functions: `TestErrorHandlingPolicyMerge` uses table-driven cases over `IgnoreFileErrors` and `IgnoreDirectoryErrors`, `NewOptionalBool`, and `reflect.DeepEqual`.

Control flow: each case constructs a starting policy, merges a source policy, and compares the result with the expected policy. Cases cover nil/no-op, source false, source true, destination already false/true, and changing only one field.

State and persistence behavior: no persistence; validates in-memory merge behavior that later determines persisted/effective policy values.

Dependencies/integration: depends on `snapshot.SourceInfo` only for definition argument. Tests do not assert definition-source fields.

Risks: `IgnoreUnknownTypes` is not covered in this test despite being merged by the source file; it relies on the same helper path.

Test signals: focused coverage for first-value-wins optional bool behavior, including explicit false.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/error_handling_policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/expire.go -->
# sources/sync-backup/kopia/snapshot/policy/expire.go

Purpose: applies snapshot retention policy by identifying and optionally deleting expired snapshot manifests.

Important APIs/types/functions: `ApplyRetentionPolicy`, `getExpiredSnapshots`, and `getExpiredSnapshotsForSource`.

Control flow: `ApplyRetentionPolicy` delegates to a remote repository server when the repository implements `RemoteRetentionPolicy` and the source matches the connected client user/host. Otherwise it lists snapshots, computes expired IDs, and deletes them only when `reallyDelete` is true. Expiration groups manifests by source, loads the effective policy for each source, calls `RetentionPolicy.ComputeRetentionReasons`, and deletes snapshots with no retention reasons and no pins.

State and persistence behavior: dry-run mode returns candidate manifest IDs without mutation. Real delete removes snapshot manifests via `DeleteManifest`; underlying object/content garbage collection is separate. `RetentionReasons` are transient fields on loaded manifests.

Dependencies/integration: depends on snapshot listing/grouping, repository writer/delete APIs, remote retention interface, manifest IDs, and retention policy implementation from other files.

Risks: deletion is manifest-only and assumes later maintenance handles unreachable content. Remote delegation only applies to the client's own source; other sources are processed client-side. Pins prevent deletion even when retention reasons are empty.

Test signals: retention policy behavior is likely covered in retention tests outside this subset; this file has no direct tests here.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/expire.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/files_policy.go -->
# sources/sync-backup/kopia/snapshot/policy/files_policy.go

Purpose: defines file-selection policy for snapshot traversal.

Important APIs/types/functions: `FilesPolicy` includes ignore rules, dot-ignore filenames, no-parent flags, cache-directory ignoring, max file size, and one-file-system behavior. `FilesPolicyDefinition` tracks source locations. `Merge` applies inherited values.

Control flow: merge copies ignore rules only when target is empty, merges no-parent booleans, replaces dot-ignore files when target is empty, merges optional booleans, and fills max file size if unset.

State and persistence behavior: fields persist as JSON in policy manifests. Optional booleans distinguish unset from explicit false.

Dependencies/integration: consumed by snapshot upload/walk code and policy merge. Depends on `OptionalBool` and `snapshot.SourceInfo`.

Risks: `NoParentIgnoreRules` is merged as a boolean but does not appear to stop `IgnoreRules` merging in this file; contrast with compression `mergeStrings` no-parent behavior. The distinction between append/replace semantics for ignore rules and dot-ignore files should be preserved.

Test signals: policy manager tests exercise inherited policies generally; file-policy-specific behavior is not directly tested in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/files_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/log_detail.go -->
# sources/sync-backup/kopia/snapshot/policy/log_detail.go

Purpose: defines numeric log-detail levels used by snapshot logging policy.

Important APIs/types/functions: `LogDetail` integer type with constants `LogDetailNone` (0), `LogDetailNormal` (5), and `LogDetailMax` (10). `OrDefault` returns a default for nil pointers. `NewLogDetail` returns a pointer.

Control flow: straightforward nil-aware defaulting and pointer construction.

State and persistence behavior: values persist as JSON integers when used in policy structs; pointer fields allow omitting unset values.

Dependencies/integration: used by `logging_policy.go` and upload logging code.

Risks: numeric values are part of persisted policy semantics. Consumers must use pointer-aware defaulting to distinguish unset from zero/none.

Test signals: `log_detail_test.go` verifies JSON omitempty behavior and round-trip of pointer/non-pointer values.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/log_detail.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/log_detail_test.go -->
# sources/sync-backup/kopia/snapshot/policy/log_detail_test.go

Purpose: verifies JSON encoding behavior for `LogDetail` values and pointers.

Important APIs/types/functions: `TestLogDetail` marshals a struct containing value and pointer `LogDetail` fields with `omitempty`, then unmarshals and compares.

Control flow: sets a pointer to `LogDetailNone`, value fields to normal and max, marshals, checks exact JSON string, then unmarshals and asserts equality.

State and persistence behavior: confirms that nil/zero value fields are omitted, while a pointer to zero is emitted as `0`; this is critical for distinguishing explicit "none" from unspecified.

Dependencies/integration: uses standard JSON and `testify/require`.

Risks: changing field pointer usage or constants can alter persisted policy JSON semantics.

Test signals: strong focused test for omitempty/pointer behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/log_detail_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/logging_policy.go -->
# sources/sync-backup/kopia/snapshot/policy/logging_policy.go

Purpose: defines policy for controlling snapshot logging verbosity for directories and entries.

Important APIs/types/functions: `DirLoggingPolicy` has `Snapshotted` and `Ignored` levels. `EntryLoggingPolicy` adds `CacheHit` and `CacheMiss`. `LoggingPolicy` groups directory and entry policies. Definition structs track source fields. Each policy has a `Merge` method.

Control flow: merge fills unset `*LogDetail` fields from source policies and records definition source via `mergeLogLevel`. Top-level `LoggingPolicy.Merge` delegates to directory and entry merges.

State and persistence behavior: policy persists as JSON with pointer fields omitted when unset. Effective policies compute definition metadata in memory.

Dependencies/integration: consumed by snapshot upload logging. Depends on `LogDetail` and `snapshot.SourceInfo`.

Risks: explicit `LogDetailNone` must be a pointer to persist; non-pointer zero values disappear under omitempty in tests. Merge is first-value-wins and will not override a more specific log setting.

Test signals: `log_detail_test.go` covers JSON behavior; broader policy tests cover inheritance machinery.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/logging_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/optional.go -->
# sources/sync-backup/kopia/snapshot/policy/optional.go

Purpose: provides pointer-friendly optional scalar wrappers for policy fields.

Important APIs/types/functions: `OptionalBool`, `OptionalInt`, and `OptionalInt64` types each expose `OrDefault`; constructors are `NewOptionalBool`, `newOptionalInt`, and `newOptionalInt64`.

Control flow: `OrDefault` checks nil pointer and returns the supplied default; otherwise converts the pointed value to the base type.

State and persistence behavior: used as pointer fields in policy structs so JSON can distinguish unspecified, explicit zero/false, and non-zero/true values.

Dependencies/integration: used across retention, error handling, files, scheduling, upload, and other policy packages.

Risks: only bool constructor is exported; tests and package internals use unexported int constructors. Consumers outside the package must allocate integer pointers manually or use higher-level APIs.

Test signals: error-handling tests verify optional bool merge semantics; other optional types are indirectly exercised by policy manager tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/optional.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/os_snapshot_policy.go -->
# sources/sync-backup/kopia/snapshot/policy/os_snapshot_policy.go

Purpose: defines policy for OS-level snapshot mechanisms such as Windows Volume Shadow Copy.

Important APIs/types/functions: `OSSnapshotPolicy` contains `VolumeShadowCopy`. `VolumeShadowCopyPolicy` has an optional `OSSnapshotMode`. `OSSnapshotMode` constants are never, always, and when-available, with string constants and helper `NewOSSnapshotMode`, `OrDefault`, `String`, and `mergeOSSnapshotMode`.

Control flow: merge delegates from `OSSnapshotPolicy.Merge` to `VolumeShadowCopyPolicy.Merge`, which fills unset mode from the source policy and records definition source. `String` maps known modes to stable strings and falls back to `"never"`.

State and persistence behavior: policy persists mode values as bytes/numbers unless custom JSON is implemented elsewhere; string method is for presentation. Pointer mode preserves unset versus explicit never.

Dependencies/integration: consumed by snapshot upload code that decides whether to create OS snapshots. Depends on `snapshot.SourceInfo` for definition tracking.

Risks: unknown mode values stringify as `"never"`, which is safe but may hide invalid persisted values. JSON representation should be checked if user-facing config expects strings.

Test signals: `os_snapshot_policy_test.go` covers defaulting and string rendering for all defined modes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/os_snapshot_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/os_snapshot_policy_test.go -->
# sources/sync-backup/kopia/snapshot/policy/os_snapshot_policy_test.go

Purpose: verifies `OSSnapshotMode` defaulting and string conversion.

Important APIs/types/functions: `TestOSSnapshotMode` uses `NewOSSnapshotMode`, nil-pointer `OrDefault`, and `OSSnapshotMode.String`.

Control flow: asserts nil mode returns provided default, explicit mode overrides default, and each constant maps to expected string.

State and persistence behavior: no persistence; protects presentation/default behavior used by policy consumers.

Dependencies/integration: uses `testify/assert`.

Risks: does not cover merge behavior or JSON representation.

Test signals: focused coverage for mode helper semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/os_snapshot_policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/policy.go -->
# sources/sync-backup/kopia/snapshot/policy/policy.go

Purpose: defines the top-level snapshot policy schema, definition-source schema, target wrapper, validation entrypoint, and policy path validation.

Important APIs/types/functions: `ErrPolicyNotFound`, `TargetWithPolicy`, `Policy`, `Definition`, `Policy.String`, `Policy.ID`, `Policy.Target`, `ValidatePolicy`, and `validatePolicyPath`.

Control flow: `String` pretty-prints policy JSON. `ID` and `Target` read labels assigned by policy manager. `ValidatePolicy` delegates to scheduling and upload validation. `validatePolicyPath` rejects trailing slash/backslash except root paths.

State and persistence behavior: `Policy` fields persist as manifest JSON; `Labels` are not persisted in the payload but attached from manifest metadata. `Definition` is computed to explain where effective values came from.

Dependencies/integration: composes retention, files, error handling, scheduling, compression, splitter, actions, OS snapshot, logging, and upload policy subtypes. Uses path helpers from `policy_manager.go`.

Risks: `Policy.ID` assumes labels are populated and can return empty string otherwise. `validatePolicyPath` indexes the last byte and assumes non-empty path; callers only invoke it when path is non-empty.

Test signals: policy manager tests cover path validation and effective policy labels; scheduling/upload validation tests live elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/policy_manager.go -->
# sources/sync-backup/kopia/snapshot/policy/policy_manager.go

Purpose: implements policy persistence, lookup, hierarchy resolution, effective-policy calculation, source labels, and source-relative policy trees.

Important APIs/types/functions: constants `ManifestType`, `PolicyTypeLabel`, policy type values, and label aliases. Public functions include `GetEffectivePolicy`, `GetEffectivePolicyWithOverride`, `GetPolicyHierarchy`, `GetDefinedPolicy`, `SetPolicy`, `RemovePolicy`, `GetPolicyByID`, `ListPolicies`, `TreeForSource`, `TreeForSourceWithOverride`, and `LabelsForSource`. Helpers include `applicablePoliciesForSource`, `loadPolicyFromManifest`, `getParentPathOSIndependent`, `nestedRelativePathNormalizedToSlashes`, and Windows path utilities. `SubdirectoryPolicyMap` implements path lookup.

Control flow: hierarchy lookup walks path parents from most specific to root, then user@host, host, and global policies. Optional root override is inserted first and suppresses loading the same exact source policy. If no exact source policy exists, an artificial empty policy for the requested source is prepended. Effective policy merges that ordered list. `SetPolicy` validates and replaces manifests for source labels. Tree building computes the effective root policy, then finds all path policies for the same user/host and maps descendants to normalized relative paths.

State and persistence behavior: policies persist as repository manifests with labels generated by `LabelsForSource`; payload labels are reattached after loading. `ReplaceManifests` is used to atomically replace source policy sets at repository level. Duplicate concurrent policy manifests can exist; `GetDefinedPolicy` uses `manifest.PickLatestID`.

Dependencies/integration: depends on repository manifest APIs, snapshot source labels, `MergePolicies`, policy tree builder, and logging. Path utilities support both Unix and Windows-style paths independent of runtime OS.

Risks: source label correctness is central to inheritance. Path handling must preserve Windows drive roots and avoid treating Unix backslashes as separators in child-relative logic except where intended. `applicablePoliciesForSource` loads all path policies for a user/host, so large policy sets could be expensive. Artificial empty policies affect returned sources and effective labels.

Test signals: `policy_manager_test.go` heavily covers inheritance, conflict resolution, parent path calculation, applicable subpolicy trees, and valid/invalid path validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/policy_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/policy_manager_test.go -->
# sources/sync-backup/kopia/snapshot/policy/policy_manager_test.go

Purpose: validates policy manager inheritance, conflict resolution, OS-independent path logic, subdirectory policy discovery, and path validation.

Important APIs/types/functions: tests use `SetPolicy`, `GetEffectivePolicy`, `GetDefinedPolicy`, `applicablePoliciesForSource`, `getParentPathOSIndependent`, and `validatePolicyPath`. Helpers include `clonePolicy`, `policyWithLabels`, `policyWithKeepDaily`, and `policyWithKeepMonthly`.

Control flow: inheritance tests create host and path policies, compute effective policies for multiple source infos, and compare effective policy, contributing sources, and definition metadata. Conflict test writes concurrent global policies from two repository handles and accepts either latest competing value. Applicable-policy tests create Unix and Windows-style paths, then assert the relative policy tree keys for selected roots. Path validation tests enumerate accepted and rejected trailing slash/backslash cases.

State and persistence behavior: uses real repotesting repositories and manifest writes/flushes. Conflict test demonstrates duplicate policy manifests can happen under concurrent clients and are resolved by latest ID selection.

Dependencies/integration: depends on repo test environment, `go-cmp`, `testify/require`, and snapshot source info.

Risks: one map literal has duplicate `host-c`/`C:/Users` key, so one intended case is overwritten by Go map semantics. Tests cover many path cases but not every source-label combination.

Test signals: strong coverage for the most error-prone policy-manager behavior, especially cross-platform path handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/policy_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/policy_merge.go -->
# sources/sync-backup/kopia/snapshot/policy/policy_merge.go

Purpose: merges ordered policy hierarchy into one effective policy and tracks which source supplied each field.

Important APIs/types/functions: `MergePolicies` and merge helpers: `mergeOptionalBool`, `mergeOptionalInt`, `mergeOptionalInt64`, `mergeStringsReplace`, `mergeStrings`, `mergeString`, `mergeCompressionName`, `mergeInt64`, `mergeBool`, `mergeStringList`, `mergeLogLevel`, and `mergeActionCommand`.

Control flow: `MergePolicies` initializes labels for the requested source, applies supplied policies in most-specific-to-general order, stops early if a policy has `NoParent`, then merges default policies for every subpolicy category. After inherited merging, it copies non-inheritable folder actions from the most-specific policy. Helpers generally implement first-value-wins semantics and record `snapshot.SourceInfo` in definition structs.

State and persistence behavior: produces an in-memory effective policy and definition object; it does not write manifests. Effective fields ultimately drive snapshot behavior and may be displayed to users.

Dependencies/integration: combines all subpolicy merge methods, default policy globals from other files, compression names, and snapshot source info.

Risks: helper semantics differ: some list helpers replace only if empty, while `mergeStrings` unions and supports a no-parent stop flag. This makes subpolicy behavior non-uniform and easy to misuse. `NoParent` stops before default policy merge, meaning defaults are skipped when a user policy sets `NoParent`.

Test signals: policy manager tests verify effective retention merges and definitions; error-handling/logging/OS tests cover specific helper paths indirectly. More direct tests would help for list/no-parent semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/policy_merge.go -->

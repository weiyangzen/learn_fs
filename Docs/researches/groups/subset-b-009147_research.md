# Research: subset-b-009147

Grouped research for Kopia content manager, pack index, and index blob files. Each section preserves the source path in the title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_index_recovery.go -->
# sources/sync-backup/kopia/repo/content/content_index_recovery.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_index_recovery.go_research.md`.

Purpose: implements pack-local index recovery metadata. `WriteManager.RecoverIndexFromPackBlob` reads the encrypted local index embedded at the end of a pack blob, opens it through `index.Open`, returns recovered `Info` entries, and optionally commits them into the unflushed `packIndexBuilder`.

Important APIs and types: `packContentPostamble` records the local-index IV, offset, and encrypted length. `toBytes`, `findPostamble`, and `decodePostamble` encode and validate a CRC32-protected postamble. `SharedManager.buildLocalIndex` and `appendPackFileIndexRecoveryData` build a normal index, encrypt it, append it to pack data, then append the postamble.

Control flow, State and persistence: pack writing calls `appendPackFileIndexRecoveryData` from `preparePackDataContent` before upload. Recovery locates the postamble, decrypts the referenced local index, iterates every content record, and adds those records to the session index only when `commit` is true. The CRC is only corruption detection for locating metadata; authenticity still comes from decrypting the index payload.

Dependencies and integration: depends on `gather`, repository `format.Encryptor`, `blob.ID`, and the content `index` package. It integrates with pack writes in `content_manager_lock_free.go` and with recovery tests that delete committed index blobs.

Risks: postamble offsets and lengths are stored as `uint32`, so very large pack/index sizes rely on repository limits. `findPostamble` deliberately treats a valid CRC as a recovery hint, not a trust boundary. Committing recovered entries updates only local unflushed state until `Flush`.

Test signals: covered by `content_index_recovery_test.go`, which removes index blobs, verifies contents disappear, recovers without commit, then recovers with commit and flushes durable replacement indexes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_index_recovery.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_index_recovery_test.go -->
# sources/sync-backup/kopia/repo/content/content_index_recovery_test.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_index_recovery_test.go_research.md`.

Purpose: validates the pack-local recovery path used when repository index blobs are missing or damaged.

Important APIs and fixtures: the test uses `contentManagerSuite`, map-backed blob storage, `writeContentAndVerify`, `PackBlobIDPrefixes`, and `RecoverIndexFromPackBlob`. It explicitly deletes both legacy index blobs and epoch-style `x` blobs before reopening the manager.

Control flow and assertions: the test writes three contents, flushes them, removes all index blobs, closes and reopens the manager, and confirms all content lookups now return not found. It then iterates all pack blobs once with `commit=false`, expecting exactly three recovered entries but no visible content. A second scan uses `commit=true`, after which content reads work immediately. A final flush and reread confirm the recovered index entries can be persisted as normal index blobs.

State and persistence behavior: the test distinguishes transient recovery into `packIndexBuilder` from committed repository indexes. Recovery without commit is intentionally read-only. Recovery with commit rebuilds in-session index state but still requires `Flush` for durable repository-level indexes.

Dependencies and integration: exercises storage listing/deletion, pack blob prefixes, index blob prefixes, content manager reopen behavior, and seeded deterministic payload helpers.

Risks and coverage gaps: it validates the happy recovery path but not malformed postambles, incorrect lengths, corrupted local index ciphertext, or mixed valid and invalid packs. Those risks are handled by lower-level error returns rather than by this test.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_index_recovery_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_manager.go -->
# sources/sync-backup/kopia/repo/content/content_manager.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_manager.go_research.md`.

Purpose: central write/read content manager for Kopia's content-addressable storage. It hashes content IDs, compresses and encrypts payloads, batches content into pack blobs, tracks pending and committed indexes, handles deletion markers, and flushes session state to durable index blobs.

Important APIs and types: `WriteManager` owns mutable session state: pending/writing/failed packs, `packIndexBuilder`, flush barriers, session identity, upload accounting, and a shared committed read manager. `pendingPackInfo` stores pack data and `Info` records before upload. Public APIs include `WriteContent`, `GetContent`, `ContentInfo`, `DeleteContent`, `UndeleteContent`, `RewriteContent`, `Flush`, `DisableIndexFlush`, `EnableIndexFlush`, `Revision`, and construction helpers.

Control flow: `WriteContent` validates the prefix, hashes input, checks overlay and committed indexes for dedupe, then calls `addToPackUnlocked`. That path may auto-flush old indexes, compress/encrypt outside the main lock, retries failed packs, appends bytes to a pending pack, and uploads a full pack without holding the lock. `Flush` blocks new pack uploads, retries failed writes, waits for in-flight uploads, writes all pending packs, builds index shards, writes index blobs, commits the session marker, and adds new indexes to committed contents. Reads take an `RLock` so info lookup and payload fetch see a consistent pending-pack state.

State and persistence behavior: pending pack data is memory-resident until pack upload; uploaded pack entries live in `packIndexBuilder` until index flush; committed index blobs become visible after session commit. Deletions are represented as newer `Info` records with `Deleted=true` and monotonic timestamps. Failed pack writes remain in `failedPacks` for retry.

Dependencies and integration: depends on `blob.Storage`, `format.Provider`, `compression`, `gather`, `index`, `indexblob`, cache/log/session helpers, metrics, and `SharedManager` for committed reads and decryption.

Risks: lock ordering around `mu`, `indexesLock`, and session commits is critical. Timestamp ordering determines delete/recreate conflict resolution. Compression support is tied to index version. Failed writes must never lose `currentPackData`. Tests heavily cover these behaviors in `content_manager_test.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_manager_indexes.go -->
# sources/sync-backup/kopia/repo/content/content_manager_indexes.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_manager_indexes.go_research.md`.

Purpose: exposes operations around committed content index blobs: refreshing local index views, compacting index blobs, and parsing an encrypted index blob into `Info` entries.

Important APIs: `SharedManager.Refresh` invalidates the index blob manager cache and reloads pack indexes under `indexesLock`. `SharedManager.CompactIndexes` calls the active index blob manager's compaction operation, then reloads committed indexes while holding the same lock to avoid races with refresh. `ParseIndexBlob` decrypts a provided encrypted index blob and opens it with the generic `index.Open` reader.

Control flow and integration: refresh obtains the active `indexblob.Manager`, invalidates its cached active-list view, then calls `loadPackIndexesLocked`. Compaction logs options, asks the manager to compact active index blobs, and reloads the merged committed index set afterward. `ParseIndexBlob` is a utility path: decrypt into a `gather.WriteBuffer`, open the index using encryptor overhead for v1 original-length reconstruction, iterate all IDs, and collect results.

State and persistence behavior: these functions do not directly change pack data. `Refresh` and compaction mutate the in-memory committed-content index view; compaction can create replacement index blobs and supersede old ones through the index blob manager.

Dependencies: `blobcrypto`, `indexblob`, `maintenancestats`, `timetrack`, content logging, `blob.ID`, and `index`.

Risks and tests: the main risk is stale or racy index views after compaction; the explicit `indexesLock` guards that. `ParseIndexBlob` propagates decrypt/open/iteration failures. Content manager tests cover refresh visibility, compaction, permissive index loading, and index recovery interactions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_manager_indexes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_manager_iterate.go -->
# sources/sync-backup/kopia/repo/content/content_manager_iterate.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_manager_iterate.go_research.md`.

Purpose: implements content and pack iteration over both uncommitted session state and committed indexes, including optional parallel callback execution and unreferenced pack discovery.

Important APIs and types: `IterateOptions` selects an `IDRange`, deletion visibility, and callback parallelism. `IterateCallback`, `IteratePackOptions`, `PackInfo`, and `IteratePacksCallback` define iteration contracts. `maybeParallelExecutor` fans callback work to worker goroutines. `snapshotUncommittedItems` builds a cloned overlay from `packIndexBuilder`, pending packs, and writing packs.

Control flow: `IterateContents` defaults to `index.AllIDs`, wraps the callback for optional parallelism, snapshots uncommitted items under the write-manager lock, filters by delete state and range, invokes callbacks for overlay records first, refreshes indexes if needed, then scans committed contents. If there is no overlay and all IDs including deleted are requested serially, it uses a fast path. `IteratePacks` groups visible `Info` records by pack blob and optionally preserves content details. `IterateUnreferencedPacks` builds a bigmap set of referenced pack IDs, expands prefixes if requested parallelism exceeds the prefix count, scans blob storage, and reports pack blobs absent from the used set.

State and persistence behavior: iteration is observational but must merge pending and committed views consistently. Deleted pending records can suppress committed records unless `IncludeDeleted` is set.

Dependencies: `bigmap`, `blob.IterateAllPrefixesInParallel`, content logging, blob prefix helpers, and the index range model.

Risks and tests: parallel callback errors are captured asynchronously, so callers may observe partial processing before cancellation. Unreferenced scans depend on prefix coverage. `content_manager_test.go` covers default, deleted, range, parallel, callback failure, and unreferenced-pack cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_manager_iterate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_manager_lock_free.go -->
# sources/sync-backup/kopia/repo/content/content_manager_lock_free.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_manager_lock_free.go_research.md`.

Purpose: contains helper paths intentionally run outside or around the main write-manager lock: compression/encryption, pack preparation, read payload extraction, pack upload, IV derivation, and hashing.

Important APIs: `maybeCompressAndEncryptDataForPacking` handles optional compression, rejects compression for v1 indexes, disables metadata compression before index v2, and encrypts using an IV derived from the content ID. `getContentDataReadLocked` reads from a pending pack buffer or cache-backed blob section and calls `decryptContentAndVerify`. `preparePackDataContent` builds a per-pack `index.Builder`, adds padding, appends local recovery index data, and marks a pack finalized. `writePackFileNotLocked` uploads a pack blob and records metrics. `hashData` computes repository content hashes.

Control flow, State and persistence: pack data is prepared exactly once via `pp.finalized`. Pending pack records can include entries moved from older packs, deleted markers, or new content. If no live content remains after a preamble, the preamble buffer is reset while index entries are still returned. Padding uses random bytes to align to `paddingUnit`, then local recovery metadata is appended.

Dependencies: compression registry, format encryptor/hash provider, gather buffers, content and blob caches, OpenTelemetry tracing, metrics, and pack recovery code.

Risks: compression mutates the effective payload used for encryption, so cache keys include format metadata. Pending pack section reads must be protected while pack buffers can still grow. V1 original lengths are inferred from packed length and encryptor overhead. Tests cover failed-write aliasing, compression behavior, cache-by-format, and read/write aliasing.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_manager_lock_free.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_manager_metrics.go -->
# sources/sync-backup/kopia/repo/content/content_manager_metrics.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_manager_metrics.go_research.md`.

Purpose: defines the content manager metric counters and throughput measurements used by write, read, compression, encryption, hashing, dedupe, and upload paths.

Important APIs and types: `metricsStruct` groups metric handles. `initMetricsStruct` registers counters such as `content_uploaded_bytes`, `content_get_error_count`, `content_get_not_found_count`, `content_deduplicated`, `content_deduplicated_bytes`, compression byte counters, and throughput metrics for write, hash, encryption, read, decryption, decompression, and compression attempts.

Control flow and integration: this file has no runtime branching beyond construction. The returned struct is embedded in shared manager state and used by functions in `content_manager.go` and `content_manager_lock_free.go`: `WriteContent` observes pre-dedupe write throughput, `hashData` observes hashing, compression/encryption helpers update compression and encryption counters, `GetContent` reports success/not-found/error, and pack/index upload paths increment uploaded bytes.

State and persistence behavior: metrics are process-local telemetry, not repository state. They should not affect behavior or durability.

Dependencies: `internal/metrics.Registry`.

Risks and test signals: metric names are integration contracts for monitoring. Renaming or changing units can break dashboards. The code is indirectly covered through content manager tests that exercise all paths, but there are no dedicated metric assertions in this source set.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_manager_metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_manager_test.go -->
# sources/sync-backup/kopia/repo/content/content_manager_test.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_manager_test.go_research.md`.

Purpose: comprehensive behavioral suite for `WriteManager` and related content storage behavior across index formats v1 and v2.

Important fixtures: `contentManagerSuite` runs under `TestFormatV1` and `TestFormatV2`. Helpers build map/faulty/eventually-consistent blob stores, fake clocks, format providers, seeded content, hash expectations, and assertion helpers for content presence, deletion state, blob counts, retries, and cache contents.

Control-flow coverage: tests cover empty flushes, zero-length content, small pack packing, deduplication in pending and uncommitted states, internal pack flush on size, many writes with reopen, failed pack upload retry, concurrent managers, index compaction, delete/undelete/rewrite sequences, delete/recreate timestamp ordering, parallel writes, flush barriers, retry behavior under fault injection, disabled index flush counters, content iteration, unreferenced pack scanning, read/write aliasing, format compatibility, own-writes consistency, compression, cache key separation, prefetch hints, permissive cache loading, and legacy index poison tolerance.

State and persistence behavior: the suite asserts the intended transitions from session marker to pack blob to index blob, visibility boundaries between writers before refresh/reopen, monotonic timestamps for deletion and recreation under frozen time, and durability after flush and manager reopen.

Dependencies and integration: uses `blobtesting`, `faketime`, `fault`, `ownwrites`, cache storage, `indexblob`, `epoch`, compression providers, and repository format construction.

Risks and signal value: this is the primary regression net for lock ordering, failed writes, deleted-entry precedence, format compatibility, and cache correctness. Some loops are reduced under test-complexity settings, so very high-scale behavior is sampled rather than exhaustive.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_prefetch.go -->
# sources/sync-backup/kopia/repo/content/content_prefetch.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_prefetch.go_research.md`.

Purpose: implements cache prefetching for a set of content IDs, choosing between whole-pack blob prefetch and individual content fetches based on a caller hint and how much content is requested from each pack.

Important APIs: `prefetchOptions` stores thresholds for count and bytes. `defaultPrefetchOptions` switches to full-blob prefetch when at least two contents totaling at least 5 MB come from a pack. Hints map as `default` or empty to default, `contents` to individual content, `blobs` to whole blobs, and `none` to only resolve IDs without fetching. `WriteManager.PrefetchContents` returns the subset of IDs that resolved to known content info.

Control flow: under `RLock`, content IDs are resolved to `Info` records and grouped by `PackBlobID`. Unknown IDs are skipped. If hint is `none`, the method returns resolved IDs. Otherwise a work channel emits either pack blob prefetch jobs or content-ID jobs. `parallelFetches` workers call the content or metadata cache depending on pack prefix, or read individual contents through `getContentDataAndInfo`.

State and persistence behavior: prefetch is best-effort cache state only. It logs errors and continues, and does not change repository indexes or content data.

Dependencies: content and metadata caches, pack blob prefixes `p` and `q`, gather buffers, logging, and content lookup.

Risks and tests: the lock is held while workers run, which favors consistent info over write concurrency. Hint thresholds influence cache footprint. `TestPrefetchContent` verifies returned IDs and expected cache keys across hints and pack grouping cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_prefetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_reader.go -->
# sources/sync-backup/kopia/repo/content/content_reader.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_reader.go_research.md`.

Purpose: defines the read-facing content manager interface used by repository layers that need content access without depending on write-manager internals.

Important API: `Reader` exposes compression capability and format access, point reads through `GetContent` and `ContentInfo`, content and pack iteration, active session listing, optional epoch manager access, and full content verification through `VerifyContents`.

Control flow and integration: this file contains only an interface, so behavior is implemented by `WriteManager` and `SharedManager`-backed methods elsewhere in the package. The interface is broad enough for consumers that need maintenance or verification operations, not just plain reads.

State and persistence behavior: no state is stored here. The interface documents which repository operations are expected to be available from a read handle.

Dependencies: `context`, `epoch.Manager`, `format.Provider`, content `ID`, `Info`, iteration option/callback types, session info, and verify options from neighboring content files.

Risks and test signals: because it is an interface, compile-time implementation is the primary signal. Changes are API-sensitive: adding methods forces implementors and tests to update, while removing methods can break repository integration layers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/content_id_to_bytes.go -->
# sources/sync-backup/kopia/repo/content/index/content_id_to_bytes.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/content_id_to_bytes.go_research.md`.

Purpose: provides compact byte conversions used by binary index encoders and decoders. The binary representation stores one prefix byte followed by raw hash bytes.

Important APIs: `bytesToContentID` converts an encoded byte slice into an `ID`, accepting empty input as `EmptyID` and panicking if the slice is longer than the maximum supported ID length plus prefix. `contentIDToBytes` appends prefix plus hash bytes to a caller-provided output buffer. `contentIDBytesGreaterOrEqual` wraps bytewise comparison for binary searches.

Control flow, State and persistence: these helpers are pure except for the explicit panic on impossible oversized encoded IDs. They do not validate that the prefix is semantically valid; callers are index readers working from trusted or separately bounds-checked binary data.

Dependencies and integration: used by v1/v2 index builders and readers for sorted entry keys and exact/range search. The ordering must remain consistent with `ID.less` and string-like prefix ordering for merged iteration and range scans.

Risks and tests: an ordering mismatch would break binary search, `PrefixRange`, and merged index iteration. `packindex_internal_test.go` verifies round trips for empty, unprefixed, and prefixed IDs; broader pack index tests validate lookup and iteration over encoded keys.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/content_id_to_bytes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/id.go -->
# sources/sync-backup/kopia/repo/content/index/id.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/id.go_research.md`.

Purpose: defines content IDs and prefixes for content-addressable storage. IDs are optional one-character metadata prefixes plus a variable-length hash up to `hashing.MaxHashSize`.

Important APIs and types: `IDPrefix.ValidateSingle` accepts empty or one character in `g` through `z`. `ID` stores fixed hash bytes, prefix byte, and hash length. Methods cover JSON marshal/unmarshal, `Hash`, `AppendToJSON`, `Append`, `String`, `Prefix`, `HasPrefix`, and internal ordering through `less` and `comparePrefix`. Constructors are `IDFromHash` and `ParseID`; `EmptyID` is the zero ID.

Control flow and semantics: `ParseID` treats odd-length strings as prefixed and even-length strings as raw hex. Prefix validation rejects odd strings with prefixes outside `g` to `z`. `less` sorts unprefixed hex IDs before prefixed IDs and then compares raw hash bytes. `comparePrefix` optimizes empty prefix comparisons and falls back to string comparison otherwise.

State and persistence behavior: IDs are value objects serialized to JSON and encoded in pack indexes. The binary index encoding uses a prefix byte even for unprefixed IDs.

Dependencies: `encoding/hex`, `encoding/json`, `strings`, `bytes`, errors, and hashing constants.

Risks and tests: prefix/ordering rules are fundamental to range scans and pack index binary search. Tests validate valid ordering, JSON round trips, hash construction, invalid parses, prefix validation, `Hash`, `Append`, and `HasPrefix` behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/id.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/id_range.go -->
# sources/sync-backup/kopia/repo/content/index/id_range.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/id_range.go_research.md`.

Purpose: models inclusive/exclusive ID ranges used by index and content iteration.

Important APIs: `IDRange` contains `StartID` and `EndID` prefixes. `Contains` checks an `ID` using `comparePrefix`. `PrefixRange` creates a range for all IDs beginning with a requested prefix by using `prefix + maxIDCharacterPlus1`. Predeclared ranges include `AllIDs`, `AllPrefixedIDs`, and `AllNonPrefixedIDs`.

Control flow, State and persistence: this is pure range logic. `maxIDCharacterPlus1` is `{` (`0x7B`), one byte after lowercase `z`, making it a convenient exclusive upper bound for valid ID characters.

Dependencies and integration: used by `Index.Iterate`, `Merged.Iterate`, `WriteManager.IterateContents`, and tests. Correct behavior depends on `ID.comparePrefix` preserving the same lexical order as encoded index keys.

Risks and tests: incorrect boundaries could silently omit or include content during listing, pack grouping, and garbage-collection scans. `merged_test.go` and `content_manager_test.go` exercise all IDs, prefixed-only, non-prefixed-only, explicit ranges, and exact prefix ranges.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/id_range.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/id_test.go -->
# sources/sync-backup/kopia/repo/content/index/id_test.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/id_test.go_research.md`.

Purpose: unit-tests the `ID` and `IDPrefix` value semantics that all content index lookups depend on.

Important coverage: `TestIDValid` checks parsing, string formatting, JSON append truncation, JSON round trips, and pairwise ordering/compare-prefix behavior over empty, unprefixed, and prefixed IDs. `TestIDFromHash` validates construction from prefixes and max-length hashes. `TestParseInvalid` exercises too-short IDs, invalid hex, overlong hashes, and invalid prefixes. `TestIDPrefix`, `TestIDHash`, and `TestIDInvalidJSON` cover prefix validation, hash access, append output, `HasPrefix`, and malformed JSON.

Control flow, State and persistence: tests are pure and deterministic; they do not touch storage.

Dependencies and integration: uses `testify/require` and standard JSON formatting. These tests indirectly protect binary index code because ID ordering and prefix comparison must align with range and binary-search operations in v1/v2 indexes.

Risks and signal value: this file catches regressions in external JSON compatibility and internal ordering. It does not directly fuzz parse input beyond listed cases, but pack index fuzz tests add corrupted-binary coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/id_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/index.go -->
# sources/sync-backup/kopia/repo/content/index/index.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/index.go_research.md`.

Purpose: declares the read-only pack index abstraction and dispatches byte buffers to the correct binary index version implementation.

Important APIs: `Index` combines `io.Closer`, `ApproximateCount`, `GetInfo`, and range `Iterate`. `Open` first reads a v1-compatible header, then dispatches to `openV1PackIndex` or `openV2PackIndex`. `safeSlice` and `safeSliceString` wrap slice operations and convert panics from corrupt offsets or lengths into errors.

Control flow: index opening validates the header version and passes encryptor overhead to v1 because v1 does not persist original content length. Both v1 and v2 implementations use `safeSlice` during binary search and entry decoding.

State and persistence behavior: `Index` is immutable over a byte buffer and optional closer. It represents one index blob or local pack index; merged repository views are implemented separately by `Merged`.

Dependencies and integration: depends on hashing constants, errors, and lower-level index versions. Used by content index parsing, pack recovery, index blob loading, tests, and merged committed indexes.

Risks and tests: corrupt index bytes must not panic; `safeSlice` is the defensive boundary. Version dispatch must remain backward-compatible. Pack index tests open both versions, fuzz mutated bytes, and verify lookup and iteration behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/index_builder.go -->
# sources/sync-backup/kopia/repo/content/index/index_builder.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/index_builder.go_research.md`.

Purpose: builds binary pack indexes from `Info` records, including deduplication by content ID, stable sorted ordering, random uniqueness suffixes, and sharding for large index blobs.

Important APIs: `Builder` is a `map[ID]Info`. `Clone` copies the map. `Add` replaces entries only when the new info wins by `contentInfoGreaterThanStruct`. `sortedContents` bucket-sorts by prefix and first hash nibble, sorting buckets in parallel. `Build`, `buildStable`, `buildSortedContents`, `shard`, and `BuildShards` serialize indexes in v1 or v2 format.

Control flow: `Build` writes stable content then appends a 32-byte random suffix so otherwise identical indexes have unique blob IDs. `BuildShards` distributes IDs by FNV hash of `ContentID.String()` to keep shards below a maximum item count, builds each stable shard, and optionally appends random suffixes.

State and persistence behavior: the builder is mutable in memory until serialized. Persisted index contents are sorted immutable records. Stable builds are used where deterministic output matters; non-stable builds ensure encrypted blob names do not collide.

Dependencies: `gather`, crypto randomness, FNV, runtime CPU count, sorting, maps, and v1/v2 builders.

Risks and tests: bucket sorting assumes valid ID bytes and must remain order-compatible. Shard distribution must cover every ID exactly once. Tests validate stable prefixes, random suffix differences, sorted order, sharding counts, and v1/v2 round trips.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/index_builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/index_encode_util.go -->
# sources/sync-backup/kopia/repo/content/index/index_encode_util.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/index_encode_util.go_research.md`.

Purpose: small big-endian integer helpers for index binary formats.

Important APIs: `decodeBigEndianUint48`, `decodeBigEndianUint32`, `decodeBigEndianUint24`, `decodeBigEndianUint16`, and `encodeBigEndianUint24`. They use early bounds checks and manual shifts to support non-standard 24-bit and 48-bit fields used by v1/v2 entries.

Control flow, State and persistence: pure byte-slice encoding/decoding with no allocation. Panics from too-short slices are expected to be caught by caller-side bounds checks or `safeSlice` before decoding.

Dependencies and integration: used by v1 timestamp, offset, and length decoding and by v2 timestamp, offsets, 24-bit content lengths, pack IDs, and optional high-length-bit fields.

Risks and tests: off-by-one or endian mistakes would corrupt persisted index interpretation. Coverage is indirect through pack index v1/v2 round trips, per-content limit tests, and fuzzed open/iterate tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/index_encode_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/index_v1.go -->
# sources/sync-backup/kopia/repo/content/index/index_v1.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/index_v1.go_research.md`.

Purpose: implements version 1 binary pack indexes, the older format without per-content compression or encryption-key metadata.

Important APIs and types: `Version1`, `FormatV1`, `indexV1`, `indexBuilderV1`, `buildV1`, `v1ReadHeader`, and `openV1PackIndex`. Reader methods implement `ApproximateCount`, `GetInfo`, `Iterate`, and `Close`. Entries store key bytes and a fixed 20-byte value containing timestamp, format version, pack blob name offset/length, delete flag plus pack offset, and packed length.

Control flow: readers binary-search sorted keys with `findEntryPosition` or `findEntryPositionExact`, decode entries through `entryToInfoStruct`, and lazily resolve pack blob IDs from extra data with a mutex-backed offset cache. Builders prepare extra pack-name data, enforce a single key length, reject compression and encryption key IDs, write the header, sorted entries, and extra data.

State and persistence behavior: v1 does not persist original length, so readers compute `OriginalLength = PackedLength - encryptor overhead`. Deleted entries still require a pack blob ID in the serialized record.

Dependencies: `blob.ID`, big-endian helpers, `safeSlice`, sorting, buffering, and errors.

Risks and tests: v1 limitations are compatibility-sensitive. Compression must be rejected before writing. Pack index tests validate v1 round trips, original-length reconstruction, lookup, iteration, random suffix stability, and fuzzed corrupted indexes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/index_v1.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/index_v2.go -->
# sources/sync-backup/kopia/repo/content/index/index_v2.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/index_v2.go_research.md`.

Purpose: implements version 2 binary pack indexes, adding per-content compression metadata, format version, encryption key ID, compact pack ID tables, and larger optional length fields.

Important APIs and types: `Version2`, `FormatV2`, `indexV2`, `indexBuilderV2`, `indexV2FormatInfo`, `buildV2`, `newIndexBuilderV2`, `openV2PackIndex`, and parsing/writing helpers. Entries contain relative timestamp, pack offset plus deleted flag, 24-bit original and packed lengths, pack index, optional format index, optional extended pack index, and optional high length bits.

Control flow: builder analysis chooses entry size based on number of unique formats, pack count, and maximum lengths. It rejects too many formats, too many packs, content lengths at or above 28 bits, and pack offsets at or above 1 GiB. It writes sorted entries, pack side table, format side table, and pack-name extra data. Readers parse header, pre-read format and pack tables, binary-search keys, and decode entries back to `Info`.

State and persistence behavior: v2 persists enough metadata for compressed content and multiple format/encryption variants. `baseTimestamp` is present in the format but this source leaves it at zero during builds.

Dependencies: blob IDs, compression header IDs, big-endian helpers, safe slicing, sorting, and errors.

Risks and tests: compact fields create boundary risks for lengths, offsets, pack counts, and format IDs. Tests cover v2 round trips, per-content limits, too many formats, corrupted-byte fuzzing, sorting, and sharding.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/index_v2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/info.go -->
# sources/sync-backup/kopia/repo/content/index/info.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/info.go_research.md`.

Purpose: defines the persisted metadata record for one content entry in a pack index.

Important API: `Info` contains `PackBlobID`, `TimestampSeconds`, original and packed lengths, pack offset, compression header, `ContentID`, deletion flag, content format version, and encryption key ID. `Timestamp` converts `TimestampSeconds` to a `time.Time`.

Control flow, State and persistence: this is a plain value type used in builders, indexes, content manager overlays, recovery, iteration, and JSON/log output. Its timestamp and deleted fields are used by merge and replacement logic to determine the winning entry for duplicate content IDs.

Persistence behavior: fields map directly to index v1/v2 binary formats, though v1 cannot preserve all fields. In v1, compression and encryption key IDs must be zero and original length is reconstructed from packed length and encryptor overhead.

Dependencies: `blob.ID`, compression header IDs, and `time`.

Risks and tests: changes to this struct affect binary index compatibility, content cache keys, deletion semantics, and maintenance behavior. Tests throughout `content_manager_test.go`, `packindex_test.go`, and `merged_test.go` assert expected field preservation and merge precedence.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/merged.go -->
# sources/sync-backup/kopia/repo/content/index/merged.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/merged.go_research.md`.

Purpose: implements an `Index` that merges multiple immutable index shards and resolves duplicate content IDs to the newest effective `Info`.

Important APIs: `Merged` is a slice of `Index` implementing `ApproximateCount`, `Close`, `GetInfo`, and `Iterate`. `contentInfoGreaterThanStruct` defines precedence: higher timestamp wins, then non-deleted beats deleted, then lexicographically higher pack blob ID wins for deterministic ties. Internal heap types drive sorted multi-index iteration.

Control flow: `GetInfo` queries every shard and keeps the best matching record. `Iterate` starts one goroutine per shard, reads sorted `Info` streams into a min-heap, coalesces duplicate content IDs, and emits only the best record for each ID. A `done` channel stops shard goroutines if the callback fails, and `Close` joins close errors from all shards.

State and persistence behavior: merged indexes are read-only views over existing shard bytes. The merge rule is the core state-conflict policy for delete/recreate and concurrent writer histories.

Dependencies: `container/heap`, sync, joined errors, and the index interface.

Risks and tests: goroutine lifetime must not outlive closed indexes, hence `wg.Wait` is deferred. Tie-breaking must be deterministic across shard order. `merged_test.go` covers range iteration, callback error propagation, empty merges, close, and all tie-breaker combinations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/merged.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/merged_test.go -->
# sources/sync-backup/kopia/repo/content/index/merged_test.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/merged_test.go_research.md`.

Purpose: validates merged-index lookup, sorted iteration, range filtering, error propagation, close handling, and duplicate-resolution rules.

Important coverage: `TestMerged` builds three v2 indexes with overlapping and unique IDs, checks `ApproximateCount`, verifies `GetInfo` picks the newest timestamp, ensures non-deleted wins over deleted at equal timestamps, confirms callback errors propagate, checks empty merged iteration, and tests several `IDRange` values. `TestMergedGetInfoError` verifies shard lookup errors are wrapped and returned. `TestMergedIndexIsConsistent` permutes shard order to prove deterministic tie breaking by timestamp, deleted flag, and highest pack blob ID.

Control flow and fixtures: helper `indexWithItems` builds a `Builder`, serializes v2 bytes, and opens an index. `iterateIDRange` collects IDs in emitted order.

State and persistence behavior: tests focus on read-only merged views, not blob storage. They encode the conflict-resolution policy used by committed content indexes.

Dependencies: `testify/require`, pack index builder/open functions, and blob IDs.

Risks and gaps: tests do not force slow shard goroutines or close errors from custom indexes, but they strongly cover ordering and duplicate semantics that affect deletion and concurrent writer visibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/merged_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/one_use_index_builder.go -->
# sources/sync-backup/kopia/repo/content/index/one_use_index_builder.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/one_use_index_builder.go_research.md`.

Purpose: memory-oriented builder used for epoch index compaction where sorted output is needed once and the builder can be drained as it builds.

Important APIs: `OneUseBuilder` wraps an LLRB tree. `NewOneUseBuilder`, `Add`, `Length`, `sortedContents`, `shard`, and `BuildShards` mirror the regular builder API enough for compaction. `Info.Less` provides tree ordering by `ContentID`.

Control flow: `Add` replaces existing entries only if the new `Info` wins by the merged precedence rule. `sortedContents` repeatedly deletes the tree minimum, intentionally emptying the builder. `shard` also drains the tree, assigning items by FNV hash of `ContentID.String()`. `BuildShards` serializes each shard through `buildSortedContents` and optionally appends random uniqueness bytes.

State and persistence behavior: this builder is destructive by design. After sorting or sharding, `Length` becomes zero. Persisted output is the same v1/v2 binary index format as the regular builder.

Dependencies: `petar/GoLLRB/llrb`, `gather`, crypto randomness, FNV, and shared index builders.

Risks and tests: callers must not reuse it after sorting/sharding. Shard distribution must match regular builder semantics. `packindex_test.go` validates sorted order, stable output equivalence, shard counts, and that the builder is drained after sharding.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/one_use_index_builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/packindex_internal_test.go -->
# sources/sync-backup/kopia/repo/content/index/packindex_internal_test.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/packindex_internal_test.go_research.md`.

Purpose: narrow internal test for binary `ID` encoding helpers.

Important coverage: `TestRoundTrip` converts `EmptyID`, an unprefixed ID, and a prefixed ID through `contentIDToBytes` and `bytesToContentID`, asserting exact equality. It also checks that nil bytes decode to `EmptyID`.

Control flow, State and persistence: pure unit test, no storage or pack index files. It reaches unexported helpers by being in package `index`.

Dependencies and integration: uses `mustParseID` helper from the broader pack index test file. The behavior under test is used by both v1 and v2 binary index keys.

Risks and signal value: this catches accidental changes to the prefix-plus-hash binary representation. It does not test oversized byte slices, which intentionally panic in `bytesToContentID`; corrupted index tests exercise broader defensive parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/packindex_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/packindex_test.go -->
# sources/sync-backup/kopia/repo/content/index/packindex_test.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/packindex_test.go_research.md`.

Purpose: broad regression suite for pack index builders, binary encoders/decoders, sorting, sharding, and corrupted-input tolerance.

Important fixtures: deterministic helpers generate content IDs with mixed prefixes, pack blob IDs, offsets, original and packed lengths, format versions, compression IDs, encryption key IDs, and timestamps. `fakeEncryptionOverhead` models v1 original-length reconstruction.

Control-flow coverage: `TestPackIndex_V1` and `TestPackIndex_V2` build indexes through multiple paths, compare stable prefixes, require random suffix differences, open indexes, verify `GetInfo`, full iteration, prefix iteration, missing lookups, and fuzzed mutations. Limit tests validate v2 content length and pack offset boundaries. Sorting tests cover regular and one-use builders. Unique-format tests enforce the v2 255-format cap. Shard tests verify deterministic shard counts, lengths, and full ID coverage for both builders.

State and persistence behavior: tests confirm that serialized bytes are stable except for random uniqueness suffixes and that one-use builders drain on sharding. V1 field loss is explicitly normalized by replacing original length with packed length minus overhead.

Dependencies: `testify/require`, random data, SHA1 deterministic IDs, compression headers, blob IDs, and index internals.

Risks and gaps: fuzzing is mutation-based and not property-guided, but it meaningfully asserts corrupted index input should not panic when opened and partially iterated.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/index/packindex_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/indexblob/index_blob.go -->
# sources/sync-backup/kopia/repo/content/indexblob/index_blob.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/indexblob/index_blob.go_research.md`.

Purpose: declares the content index blob manager interface and shared compaction option types.

Important APIs: `Manager` supports writing encrypted index blobs, listing active index blobs with a consistency timestamp, compacting active indexes, and invalidating cached manager state. `CompactOptions` controls maximum small blobs, full compaction, deleted-entry dropping, explicit content dropping, and disabling eventual-consistency safety. `DefaultIndexShardSize` sets the default maximum entries per index shard. `addBlobsToIndex` populates metadata maps without replacing existing records.

Control flow, State and persistence: this file is mostly declarations. `CompactOptions.maxEventualConsistencySettleTime` returns zero only when safety is disabled. `addBlobsToIndex` normalizes raw `blob.Metadata` into indexblob `Metadata`.

Dependencies and integration: used by `SharedManager.Refresh`, `CompactIndexes`, write-manager index flushing, and index blob manager implementations elsewhere. It bridges content indexes with maintenance statistics and blob storage.

Risks and tests: option semantics affect garbage collection and index compaction safety on eventually consistent stores. This source set indirectly tests compaction through `content_manager_test.go`; manager implementation tests live outside the listed files.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/indexblob/index_blob.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/indexblob/index_blob_encryption.go -->
# sources/sync-backup/kopia/repo/content/indexblob/index_blob_encryption.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/indexblob/index_blob_encryption.go_research.md`.

Purpose: handles encryption, decryption, caching, metadata logging, and storage writes for index blobs.

Important APIs and types: `Metadata` extends `blob.Metadata` with superseded blobs and implements structured log writing. `EncryptionManager` owns blob storage, a `blobcrypto.Crypter`, an optional persistent cache, and logger. `GetEncryptedBlob` cache-loads encrypted bytes from storage, then decrypts into an output buffer. `EncryptAndWriteBlob` encrypts index data, derives a blob ID with prefix and suffix, writes it to storage, logs metadata, and returns `blob.Metadata`. `NewEncryptionManager` constructs the manager.

Control flow: reads go through `indexBlobCache.GetOrLoad` before decryption; writes encrypt into a temporary gather buffer, call `blob.PutBlobAndGetMetadata`, and log latency and write size. Errors are wrapped but preserve root causes for storage/encryption failures.

State and persistence behavior: encrypted index blobs are durable repository objects named by encrypted content hash plus optional session suffix. The cache stores encrypted payloads, not decrypted index contents.

Dependencies: `blobcrypto`, cache, gather, content logging, blob storage, and timing helpers.

Risks and tests: corrupted encrypted data must fail decrypt, cache misses must propagate blob-not-found, and write/encrypt failures must not report metadata. `index_blob_encryption_test.go` covers successful round trip, corruption, missing blob, put failure, and encryption failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/indexblob/index_blob_encryption.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/indexblob/index_blob_encryption_test.go -->
# sources/sync-backup/kopia/repo/content/indexblob/index_blob_encryption_test.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/indexblob/index_blob_encryption_test.go_research.md`.

Purpose: verifies index blob encryption manager behavior across success, corrupted ciphertext, missing blobs, storage write faults, and encryptor failures.

Important fixtures: a map blob store is wrapped with `blobtesting.FaultyStorage`. A test `format.ContentFormat` creates hashing and encryption providers. `blobcrypto.StaticCrypter` supplies the crypter. `failingEncryptor` injects an encryption error while satisfying the encryptor interface.

Control flow and assertions: the test encrypts and writes a small payload, compares returned metadata with storage metadata, decrypts it back successfully, flips a ciphertext byte and expects decrypt failure, checks a missing blob returns `blob.ErrBlobNotFound`, injects a `PutBlob` fault and expects that error, then replaces the crypter encryptor with `failingEncryptor` and expects the encryption error.

State and persistence behavior: confirms successful writes create real storage objects and failed writes/encryption paths return errors instead of silent partial success.

Dependencies and integration: exercises `EncryptionManager.GetEncryptedBlob` and `EncryptAndWriteBlob`; indirectly relies on repository encryption/hash construction.

Risks and gaps: does not assert persistent cache behavior because the test uses a nil cache field, but it covers the core storage and cryptographic failure boundaries.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/indexblob/index_blob_encryption_test.go -->

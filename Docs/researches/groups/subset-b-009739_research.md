# Research: subset-b-009739

Grouped research for rclone cache, chunker, and Cloudinary API support files. Each source file has a source-tree-aligned section bounded by reconciliation markers for deterministic per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/cache_internal_test.go -->
# sources/user-network-fs/rclone/backend/cache/cache_internal_test.go

## Purpose
This is the cache backend's internal integration test harness. It exercises cache behavior against either a configured remote, a cache remote wrapped by crypt, or an auto-created local remote. The tests focus on object discovery, stale metadata, wrapped-remote changes, chunk caching, directory notification, and helper behavior used by upload tests.

## Important APIs, Types, And Control Flow
`TestMain` parses `-remote-internal` and `-upload-dir-internal`, creates a global `runInstance`, and runs the package tests. The `run` helper owns temp upload paths, cache DB/chunk paths, crypt state, and backend-type detection. `newCacheFs` builds the configured cache filesystem, optionally synthesizes a local wrapped remote, configures crypt credentials when needed, opens the shared `cache.Persistent`, purges temp uploads, instantiates `cache.NewFs`, and registers cleanup. Helper methods write, update, list, read ranges, move, copy, remove, wait for background upload events, retry eventually consistent checks, and unwrap `*cache.Fs`.

## State And Persistence
The tests mutate real rclone config entries for synthesized local remotes, temporary upload directories, cache DB files under `config.GetCacheDir()/cache-backend`, persistent chunk files, and possibly VFS cache paths. They rely on cleanup through `operations.Purge`, `StopBackgroundRunners`, temp-file closure/removal, and `debug.FreeOSMemory`. Crypt fixtures include deterministic encrypted-name mappings and encrypted payload byte strings so tests can validate wrapped crypt behavior.

## Dependencies And Integration Points
The file integrates `backend/cache`, `backend/crypt`, `backend/local`, optional drive import, `fs/config`, `operations`, `fstest`, `object.NewStaticObjectInfo`, and `vfscommon`. It is intentionally built with `!plan9 && !js && !race`, reflecting timing and background-worker sensitivity. Several tests skip or retry when the wrapped remote is external or crypt-backed.

## Risks And Test Signals
The tests cover stale cache invalidation, cache read correctness across chunk boundaries, double updates, direct wrapped-FS mutation visibility, change notifications creating missing parent buckets, cache-write chunk timestamps, chunk-total-size cleanup preserving recent chunks, expired listings, and bug 2117 nested directory listings. Risks include long sleeps, global mutable `runInstance`, real config mutation, external remote eventual consistency, crypt fixture drift, and race-build exclusion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/cache_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/cache_test.go -->
# sources/user-network-fs/rclone/backend/cache/cache_test.go

## Purpose
This file wires the cache backend into rclone's generic filesystem conformance suite. It provides broad integration coverage for the public `fs.Fs`, `fs.Object`, and `fs.Directory` interfaces implemented by the deprecated cache backend.

## Important APIs, Types, And Control Flow
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestCache:"` and `NilObject: (*cache.Object)(nil)`. It declares methods the backend cannot implement, including `PublicLink`, random-write/chunk-writer APIs, directory metadata mutation, `ListP`, object MIME/ID/tier/metadata methods, and directory metadata/set-modtime methods.

## State And Persistence
The test suite creates and removes objects and directories through the cache remote selected by rclone test configuration. The actual persistent state is owned by the backend under test: Bolt metadata, chunk files, and wrapped remote contents.

## Dependencies And Integration Points
It imports `backend/cache`, blank-imports `backend/local` so local remotes are available, and delegates assertions to `fstest/fstests`. The build tags exclude Plan 9, JavaScript, and race builds.

## Risks And Test Signals
Primary signal is compatibility with rclone's standard backend contract. `SkipInvalidUTF8` documents a known weakness: invalid UTF-8 confuses cache path handling. Because most behavior lives in `fstests.Run`, failures usually indicate interface contract regressions rather than narrow unit failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/cache_unsupported.go -->
# sources/user-network-fs/rclone/backend/cache/cache_unsupported.go

## Purpose
This stub prevents Go from reporting "no buildable Go source files" for the cache package on unsupported platforms.

## Important APIs, Types, And Control Flow
The file contains only the package declaration for `cache` and no runtime symbols. Its build constraint is `plan9 || js`, complementing the cache implementation files that use `!plan9 && !js`.

## State And Persistence
There is no state, persistence, initialization, or side effect.

## Dependencies And Integration Points
It integrates only with Go build selection. On unsupported platforms, importing `backend/cache` yields an empty package rather than the full backend implementation.

## Risks And Test Signals
Risk is accidental addition of API surface here, which could mask unsupported behavior. Test signal is compile-only: packages importing `cache` should build on Plan 9 or JS only if they do not require implementation symbols.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/cache_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/cache_upload_test.go -->
# sources/user-network-fs/rclone/backend/cache/cache_upload_test.go

## Purpose
This test file targets the cache backend's temporary upload queue. It verifies that writes can land in a local temp filesystem, appear through cache immediately, then move asynchronously to the wrapped remote.

## Important APIs, Types, And Control Flow
Tests create cache filesystems with `tmp_upload_path` and `tmp_wait_time`, then use `runInstance` helpers from `cache_internal_test.go`. `testInternalUploadQueueOneFile` writes a large file, checks it exists in temp storage, waits for background upload notifications, verifies temp deletion, and reads from the final remote. Other tests cover temp-dir creation, queue persistence/reconciliation across restarts, moving existing files, temp path cleanup, multiple queued files, and operations on temp or already-uploading files.

## State And Persistence
State spans the temp upload directory, the persistent Bolt `pending` bucket, object metadata in the cache DB, and eventual files on the wrapped remote. Tests use `PurgeTempUploads` and `SetPendingUploadToStarted` helper methods from `utils_test.go` to force queue states. For crypt-wrapped roots they compare adjusted encrypted file sizes and encrypted path names.

## Dependencies And Integration Points
The tests depend on `cache.Persistent` pending-upload APIs, background uploader notifications (`BackgroundUploadStarted`, `Completed`, `Error`), wrapped/local/temp filesystem move/copy/dir-move features, and `walk.ListR` behavior indirectly through backend operations.

## Risks And Test Signals
Important signals are queue-to-upload completion, temp objects overriding source listings, started uploads blocking move/delete/dir-move, allowed copies of uploading objects, update behavior on temp objects, cleanup of empty temp parent directories, and eventual absence of queued temp files. Risks include timing-sensitive waits, remote-specific feature availability, tests that branch around unsupported move/copy features, and commented FIXME coverage for updating an actively uploading file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/cache_upload_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/directory.go -->
# sources/user-network-fs/rclone/backend/cache/directory.go

## Purpose
`directory.go` defines the cached directory wrapper used by the cache backend to persist directory metadata and satisfy `fs.Directory`.

## Important APIs, Types, And Control Flow
`Directory` stores an optional wrapped `fs.Directory`, the owning `*Fs`, normalized name and absolute directory path, cached modtime, size, item count, type string, and cache timestamp. `NewDirectory` creates a timestamped shallow directory for a remote. `ShallowDirectory` derives `Dir` and `Name` from `path.Join(f.Root(), remote)`. `DirectoryFromOriginal` converts a source `fs.Directory` into a cached record using source modtime, size, items, and current cache timestamp. Methods implement `Fs`, `String`, `Remote`, internal `abs`, `ModTime`, `Size`, `Items`, and `ID`.

## State And Persistence
Instances are JSON-serializable except for `Directory` and `CacheFs`, which are excluded. `Persistent.AddDir` and `AddBatchDir` store them as the `"."` key inside nested Bolt buckets. `CacheTs` drives info-age invalidation.

## Dependencies And Integration Points
The type depends on `fs.Directory`, `context`, `path`, and the cache backend's `cleanPath`/`cleanRootFromPath` semantics. Directory records are created by listing, mkdir, expiration, notification, and temp-upload cleanup paths.

## Risks And Test Signals
Path normalization and root trimming are the main correctness risks, especially for root directories and nested cache roots. `ID` returns empty if the original directory is absent, so consumers cannot rely on IDs for cached-only directories. Test signals appear in internal listing, mkdir/rmdir, notification, and nested-directory regression tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/directory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/handle.go -->
# sources/user-network-fs/rclone/backend/cache/handle.go

## Purpose
`handle.go` implements read handles for cached objects and the background upload worker for temp-write mode. It is the cache backend's main streaming and asynchronous upload control surface.

## Important APIs, Types, And Control Flow
`NewObjectHandle` creates a `Handle`, in-memory chunk cache, preload queue, worker pool, and starts read workers. `Read` calls `getChunk` at the current offset and copies bytes to the caller. `Seek` adjusts the current offset and preloads nearby chunks. Workers read offsets from `preloadQueue`, reuse range-capable readers when possible, fetch missing chunks from the wrapped object, then write chunks to memory and persistent storage. Plex integration initially limits workers to one and scales out when external playback is confirmed. The background upload path uses singleton `backgroundWriter` instances by cache FS string. `run` polls `Persistent.getPendingUpload`, moves files from temp FS to wrapped FS, cleans empty temp dirs, removes pending records, expires parent cache, emits change notification, and publishes upload state.

## State And Persistence
Read state includes current offset, seen chunk offsets, worker count, queue, transient memory cache, and persistent chunk files. Background upload state is in the Bolt pending bucket, temp filesystem files, `notifyCh`, and `running` flags protected by mutexes. Persistent chunks are stored under the object's absolute path with offset filenames.

## Dependencies And Integration Points
It depends on cache `Memory` and `Persistent`, `fs.RangeOption`/`RangeSeeker`, `operations.MoveFile`, Plex connector state, the wrapped object `Open`, temp FS features, and upstream notifications. It implements `io.ReadCloser` and `io.Seeker`.

## Risks And Test Signals
Risks include goroutine coordination around queue close and scale-in sentinels, range-reader reuse after errors, chunk retry timing, memory eviction by offset, persistent chunk races, background upload singleton lifecycle, and started-upload operations. Upload tests validate queue behavior, started/completed/error notifications, temp cleanup, and blocked mutations. Internal cache tests validate chunk size limits and cached read correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/handle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/object.go -->
# sources/user-network-fs/rclone/backend/cache/object.go

## Purpose
`object.go` defines the cache backend's `fs.Object` wrapper. It persists object metadata, lazily refreshes stale entries, routes reads through cache handles, and keeps temp-upload objects distinct from source objects.

## Important APIs, Types, And Control Flow
`Object` stores the wrapped object, parent FS, cache FS, normalized name/path, cached modtime/size/storable/type/timestamp, cached hash map, and refresh mutex. `NewObject` creates a placeholder and switches to `objectPendingUpload` when the persistent pending queue contains the absolute path. `ObjectFromOriginal` wraps a source object and populates metadata via `updateData`. `refresh` checks info-age and notification flags, while `refreshFromSource` reloads from either temp FS or wrapped FS. `Open` refreshes, creates a `Handle`, applies seek/range options, and returns a limited reader. `Update`, `Remove`, `SetModTime`, and `Hash` update source state and cache state.

## State And Persistence
Objects serialize to Bolt as JSON records under their parent directory bucket. `persist` writes metadata through `Persistent.AddObject`; `RemoveObject` clears object metadata and chunks. Hashes are cached lazily in `CacheHashes`. Temp-upload state is driven by `Persistent.SearchPendingUpload`.

## Dependencies And Integration Points
The type integrates `fs.Object`, `hash.Type`, `readers.NewLimitedReadCloser`, background upload pause/play controls, persistent cache expiration, upstream change notifications, and temp FS routing.

## Risks And Test Signals
Risks include stale object metadata when wrapped changes are not notified, concurrent refresh/update behavior, operations on started temp uploads, hash cache invalidation, and correct path cleaning under crypt wrappers. Tests exercise object not found, wrapped object discovery, direct wrapped mutations, double updates, temp-file operations, uploading-file blockers, and cache-write chunk invalidation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/plex.go -->
# sources/user-network-fs/rclone/backend/cache/plex.go

## Purpose
`plex.go` provides optional Plex integration for the cache backend so read worker behavior can adapt when Plex is actively playing a cached object.

## Important APIs, Types, And Control Flow
The file defines Plex JSON DTOs for play-session notifications and a `plexConnector` holding server URL, credentials/token, TLS mode, owner FS, websocket running state, cached session details, and token persistence callback. `newPlexConnector` validates URL and stores credentials; `newPlexConnectorWithToken` starts websocket listening immediately. `authenticate` posts to Plex login, extracts `user.authToken`, saves it, and starts `listenWebsocket`. The websocket loop receives notifications, fetches details for playing sessions into `stateCache`, and removes stopped sessions. `isPlaying` optionally decrypts a cache object remote through crypt wrapper and searches cached Plex session payloads for the remote path.

## State And Persistence
Runtime state includes websocket connection status, token, and an in-memory expiring cache of Plex session detail payloads. Token persistence is delegated to the callback passed by `NewFs`, which stores `plex_token` into the config mapper. No file storage is directly modified here.

## Dependencies And Integration Points
It depends on `net/http`, `x/net/websocket`, TLS config, `patrickmn/go-cache`, and cache `Fs.isWrappedByCrypt`. `Handle.startReadWorkers` and `confirmExternalReading` query Plex state to choose one worker until playback is confirmed.

## Risks And Test Signals
Risks include no explicit response body close in some HTTP paths, insecure TLS option, substring matching against raw session JSON, websocket reconnect behavior, and token handling. Test coverage is mostly indirect through read-worker behavior; explicit Plex integration tests are absent in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/plex.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/storage_memory.go -->
# sources/user-network-fs/rclone/backend/cache/storage_memory.go

## Purpose
`storage_memory.go` implements transient in-memory chunk storage for active cache readers.

## Important APIs, Types, And Control Flow
`Memory` wraps `patrickmn/go-cache`. `NewMemory` and `Connect` initialize the cache. `HasChunk`, `GetChunk`, `AddChunk`, and `AddChunkAhead` use keys formatted as `objectAbs-offset`. `CleanChunksByAge` removes expired entries. `CleanChunksByNeed` scans all keys, parses the trailing offset after the final hyphen, and deletes chunks older than the requested offset. `CleanChunksBySize` is a no-op because this layer is bounded by read flow, not byte accounting.

## State And Persistence
State is process-local only. Chunks are `[]byte` values in memory and disappear on handle close or process exit. `Handle.Close` flushes the underlying cache.

## Dependencies And Integration Points
Memory storage is used by `Handle` when `ChunkNoMemory` is false. Workers promote chunks from persistent storage to memory, downloads write to both layers, and `queueOffset` evicts already-read offsets.

## Risks And Test Signals
Risks include key parsing when object paths contain hyphens, unchecked type assertions in `GetChunk`, lack of size enforcement, and scanning all cache items for eviction. Read tests and max chunk size cleanup tests indirectly validate that memory behavior does not break persistent chunk delivery.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/storage_memory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/storage_persistent.go -->
# sources/user-network-fs/rclone/backend/cache/storage_persistent.go

## Purpose
`storage_persistent.go` implements the cache backend's durable metadata and chunk store using BoltDB plus filesystem chunk files.

## Important APIs, Types, And Control Flow
`GetPersistent` returns a singleton `Persistent` per DB path. `connect` creates the chunk data directory, opens Bolt, optionally purges, and creates root, root timestamp, data timestamp, and pending-upload buckets. Directory/object methods store directory metadata under nested buckets and object metadata as JSON key values. Chunk methods write chunk files under `dataPath/objectAbs/offset` and timestamp them in `DataTsBucket`. Cleanup computes total chunk size and deletes oldest timestamped chunks until under limit. Stats walks buckets and timestamp indexes. Pending upload methods add, search, claim, roll back, remove, update, list by dir, purge for tests, and reconcile queue records from temp FS contents.

## State And Persistence
Persistent state is split between Bolt buckets (`root`, `rootTs`, `dataTs`, `pending`) and chunk files on disk. The root bucket stores a directory tree: directories are nested buckets with `"."` metadata and objects are JSON values. Pending uploads store destination path, added time, and started flag. Chunk timestamps are big-endian nanosecond keys mapping to path/offset/size.

## Dependencies And Integration Points
It integrates bbolt transactions, `walk.ListR`, cache `Object`/`Directory`, temp upload background workers, cache stats/RC commands, cleanup loops, and tests via methods in `utils_test.go`.

## Risks And Test Signals
Risks include singleton lifetime with closed DB reuse, recursive `iterateBuckets` opening nested read transactions, timestamp key collisions for chunks written in the same nanosecond, stale chunk files when DB records are inconsistent, pending-upload queue races, and path/root normalization. Tests cover temp queue states, chunk timestamp lookup, cleanup by size, notification-created parent buckets, cache purge, and reconciliation behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/storage_persistent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/utils_test.go -->
# sources/user-network-fs/rclone/backend/cache/utils_test.go

## Purpose
This test-only file exposes small helpers on `Persistent` so cache upload tests can force pending-upload queue states.

## Important APIs, Types, And Control Flow
`PurgeTempUploads` deletes and recreates the pending upload bucket under the persistent DB while holding `tempQueueMux`. `SetPendingUploadToStarted` calls `updatePendingUpload` and sets the internal `Started` flag to true for a remote.

## State And Persistence
Both helpers mutate the Bolt `pending` bucket and are compiled only for `!plan9 && !js`. They do not touch temp filesystem files, so tests must keep DB and temp FS state coherent.

## Dependencies And Integration Points
The helpers depend on unexported package internals because this file is in package `cache`, not `cache_test`. They are consumed by `cache_upload_test.go` to isolate temp-file and uploading-file operation scenarios.

## Risks And Test Signals
Risk is that tests can create states not reachable through normal APIs, especially marking entries started without a live background upload. This is intentional for negative-path coverage around move/delete/update blockers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/chunker/chunker.go -->
# sources/user-network-fs/rclone/backend/chunker/chunker.go

## Purpose
`chunker.go` implements rclone's chunker backend, a wrapper filesystem that splits large logical files into multiple objects on an underlying remote and optionally stores a small metadata object at the logical file name.

## Important APIs, Types, And Control Flow
`NewFs` parses options, builds the wrapped remote, requires server-side move/copy capability, configures name format, metadata, hash mode, and transaction mode, then advertises masked features. `setChunkNameFormat`, `makeChunkName`, and `parseChunkName` define the data/control/temporary chunk naming contract. `List`/`processEntries` group chunks into `Object` wrappers while hiding temporary/control chunks. `NewObject` scans a directory to assemble one logical object. `put` uploads through `chunkingReader`, writes temporary chunk names, validates size, optionally finalizes small files as normal objects, renames chunks or records transaction ID, writes metadata, and rolls back on error. Object methods implement remove, server-side copy/move, open via `linearReader`, hash lookup from metadata or wrapped object, and metadata parsing/marshalling.

## State And Persistence
Persistent state lives entirely on the wrapped remote: data chunks, optional metadata object, and temporary transaction suffixes. In-memory state includes chunker options, regex/format strings, random transaction ID generator, object chunk slices, cached size, metadata hashes, `xactID`, and lazy metadata-read flags.

## Dependencies And Integration Points
Chunker integrates rclone core `fs`, `operations`, accounting wrappers, hash types, config parsing, path parsing, and optional wrapped features such as `Copy`, `Move`, `DirMove`, `ChangeNotify`, `PutStream`, metadata directories, cleanup, and quota. It wraps and unwraps FS/Object interfaces for stacked backends.

## Risks And Test Signals
Key risks are accidental exposure or mutation of chunk files, metadata version incompatibility, chunk number overflow, transaction ID collisions, orphan temp chunks after crashes, server-side copy/move partial failures, hash guarantees, and list performance because `NewObject` scans directories. Internal tests cover name parsing, corruption prevention, future metadata refusal, backwards compatibility between rename and norename transactions, server-side moves, small-file internals, metadata-like user input, chunk overflow, and hash-all behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/chunker/chunker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/chunker/chunker_internal_test.go -->
# sources/user-network-fs/rclone/backend/chunker/chunker_internal_test.go

## Purpose
This file provides chunker-specific internal tests beyond rclone's generic backend suite. It directly exercises unexported format parsing, object internals, transaction behavior, metadata safety, corruption prevention, and server-side move cases.

## Important APIs, Types, And Control Flow
`InternalTest` dispatches named subtests. `testChunkNameFormat` validates accepted and rejected name patterns, generated printf formats, regexes, data/control chunk names, temporary suffixes, old-style suffix parsing, and panic paths. `testSmallFileInternals` checks how small and empty files are represented under metadata-none, hash-all, and normal modes. `testPreventCorruption` ensures chunk-looking paths cannot be created, updated, moved, copied, or removed when that would corrupt a composite file. Other tests cover chunk number overflow, user content that resembles metadata, future metadata versions, rename/norename backwards compatibility, server-side move between differently configured derived chunker remotes, and `md5all` metadata creation on slow-hash bases.

## State And Persistence
Tests create files and chunks on the wrapped base remote, frequently bypassing chunker to simulate corrupt, legacy, or future states. They mutate `f.opt`, `f.useNoRename`, and chunk size directly, then restore them in defers. Cleanup uses `operations.Purge` on test directories.

## Dependencies And Integration Points
The file uses `fstests`, `fstest`, `operations`, `object.NewStaticObjectInfo`, config-derived remotes via `deriveFs`, random content, and `hash` checks. It is compiled inside package `chunker` so it can inspect unexported fields and methods.

## Risks And Test Signals
Signals are highly targeted: strict chunk-name contract, fail-hard behavior, safe handling of future metadata, refusal to update unsupported objects, compatibility from old rename chunks to new norename scanning, and correct metadata/hash behavior. Risks include tests depending on direct internal mutation and small chunk sizes, plus branch coverage that varies with wrapped backend features.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/chunker/chunker_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/chunker/chunker_test.go -->
# sources/user-network-fs/rclone/backend/chunker/chunker_test.go

## Purpose
This file connects the chunker backend to rclone's generic backend integration test suite.

## Important APIs, Types, And Control Flow
It defines `-bad-chars` to optionally enable invalid-character filename tests when a real remote is configured. `TestIntegration` creates `fstests.Opt` with `NilObject: (*chunker.Object)(nil)`, declares unsupported object and FS methods, and runs `fstests.Run`. Without `-remote`, it synthesizes a `TestChunker:` remote wrapping a local temporary directory and enables quick tests.

## State And Persistence
The generic test suite creates, updates, reads, lists, moves, and removes files through chunker. When no remote is specified, state is under `os.TempDir()/rclone-chunker-test-standard`; otherwise state is on the configured remote.

## Dependencies And Integration Points
It blank-imports `backend/all` so wrapped remotes are available, uses `fstest.RemoteName`, and depends on rclone's backend contract tests. Unsupported method lists document chunker's public feature boundaries.

## Risks And Test Signals
The main signal is that chunker still behaves like an rclone filesystem across standard operations. The bad-character flag documents backend-specific filename constraints. Internal metadata and chunk safety are mostly covered in `chunker_internal_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/chunker/chunker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cloudinary/api/types.go -->
# sources/user-network-fs/rclone/backend/cloudinary/api/types.go

## Purpose
This file defines small shared API types for the Cloudinary backend: an encoder extension interface and an update option passed from object update paths into put/upload logic.

## Important APIs, Types, And Control Flow
`CloudinaryEncoder` extends standard path/name encoding with `FromStandardFullPath`, allowing the backend to encode a full root-relative Cloudinary path. `UpdateOptions` carries `PublicID`, `ResourceType`, `DeliveryType`, `AssetFolder`, and `DisplayName`. It implements rclone's open-option style methods: `Header` returns key `"UpdateOption"` with a `resource/delivery/publicID` value, `Mandatory` returns false so unaware consumers can ignore it, and `String` formats a human-readable fully qualified public ID.

## State And Persistence
The file stores no state. `UpdateOptions` is a value object used to preserve Cloudinary identity metadata across an update-to-put handoff.

## Dependencies And Integration Points
It depends only on `fmt`. The option type integrates with Cloudinary backend upload/update code and rclone's generic option plumbing through `Header`, `Mandatory`, and `String` conventions.

## Risks And Test Signals
Risks are semantic rather than algorithmic: `Header` omits asset folder and display name, so consumers must get those fields by type assertion rather than header text; `Mandatory` being false means the option can be silently ignored by non-Cloudinary paths. Test signals should verify update preserves resource type, delivery type, public ID, asset folder, and display name where relevant.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cloudinary/api/types.go -->

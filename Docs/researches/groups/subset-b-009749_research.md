# subset-b-009749 Research Report

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mailru/mailru.go -->
# sources/user-network-fs/rclone/backend/mailru/mailru.go

## Purpose
`mailru.go` implements rclone's Mail.ru Cloud backend. It registers the `mailru` remote, authenticates through Mail.ru OAuth password credentials or stored tokens, translates rclone `fs.Fs` and `fs.Object` operations into Mail.ru JSON and binary API calls, and supplies Mail.ru-specific hash handling through `mrhash`. The file covers directory listing, object metadata, uploads, downloads, server-side copy and move, directory move, public links, cleanup, quota, deletion, and optional upload acceleration by "put by hash".

## Important APIs, Types, And Functions
Important exported surfaces are `NewFs`, `Fs`, `Object`, `Mkdir`, `Rmdir`, `Purge`, `List`, `NewObject`, `Put`, `Copy`, `Move`, `DirMove`, `PublicLink`, `CleanUp`, `About`, `Object.Update`, `Object.Open`, `Object.Hash`, and `Object.SetModTime`. The backend registers a custom `MrHashType` with rclone's hash registry and advertises optional features for case-insensitive names, empty directories, and server-side cross-config operations.

`Options` contains credentials, user agent override, hash checking, speedup settings, troubleshooting quirks, and encoding policy. `quirks` enables experimental binary listing, atomic mkdir semantics, and acceptance of unknown directory kinds. `serverPool` manages temporary download server URLs with lock counts and expirations. `treeState` and `treeRevision` parse Mail.ru's binary folder-list format.

Core helpers include `authorize`, `reAuthorize`, `accessToken`, `metaServer`, `uploadShard`, `readItemMetaData`, `itemToDirEntry`, `isDir`, `listM1`, `listBin`, `CreateDir`, `mkDirs`, `mkParentDirs`, `delete`, `moveItemBin`, `eligibleForSpeedup`, `parseSpeedupPatterns`, `putByHash`, `makeTempFile`, `upload`, `addFileMetaData`, `getTransferRange`, and the `endHandler` read closer.

## Control Flow
Construction parses config, reveals the password, trims the root, parses speedup patterns and quirks, builds a pacer and HTTP/rest clients, authorizes, initializes the download server pool, and probes the root unless a trailing slash declares it a directory. If the root is a file, `NewFs` returns an Fs pointing to the parent with `fs.ErrorIsFile`.

Listing chooses JSON `m1` folder listing by default, or binary listing when the `binlist` quirk is enabled. JSON listing posts `home` to `/api/m1/folder`; binary listing gets a meta server, sends an encoded operation, reads status/revision/space/fingerprint data, and iterates parse records through `treeState.NextRecord`. API items become rclone directories or objects after root-relative path normalization and Mail.ru hash decoding.

Writes call `Object.Update`. The method rejects unknown-size streams, creates parents, then tries several upload acceleration routes: instant source `MrHashType`, local-source hash, in-memory hashing, or a temporary local spool file. If put-by-hash fails or is ineligible, it uploads data to a dispatch-selected shard and verifies the returned Mail.ru hash. Finally it commits metadata through the binary add-file operation. Small files of at most `mrhash.Size` can skip upload and store content through the hash buffer.

Reads select a download server from `serverPool`, issue a GET with optional range headers, and wrap the body in `endHandler`. Full downloads are hashed during streaming and compared with the stored Mail.ru hash when EOF is reached; partial responses skip checksum validation. Copy and move create parents, call Mail.ru copy or binary rename endpoints, and copy fixes destination modtime by rewriting metadata if needed.

## State And Persistence Behavior
Persistent user-facing state is remote Mail.ru content plus OAuth tokens saved through `oauthutil.PutToken`. Runtime state includes `Fs.source`, cached meta and shard URLs with expiry times, `serverPool` download server locks, parsed speedup globs, and quirk flags. `Object` caches remote path, metadata freshness, size, modtime, and binary Mail.ru hash. The backend does not maintain a local directory cache; metadata is refreshed on demand.

Concurrency is protected by `authMu`, `metaMu`, `shardMu`, and `serverPool.mu`. Reauthorization is deliberately one-shot after a 403 when a password is configured. The download server pool increments lock counts on dispatch and decrements them when `endHandler` reaches EOF or closes. Upload spool files are created under rclone's temporary local Fs and purged with a deferred cleanup.

## Dependencies And Integration Points
The backend integrates with rclone's `fs`, config, obscure, OAuth, pacer, rest, object, operations, readers, hash, and encoder packages. It depends on `backend/mailru/api` for endpoints, response types, binary writer/reader constants, and OAuth constants, and on `backend/mailru/mrhash` for Mail.ru checksums. Server-side copy/move interacts with rclone's optional interfaces and allows cross-config operations only when usernames match.

## Risks And Edge Cases
The password OAuth flow and query-parameter token placement are service-specific and fragile. `reAuthorize` uses a background context because it is invoked from retry logic, so cancellation does not propagate. Binary listing is explicitly experimental and only emits level-one entries. `Object.Hash` returns the cached hash without forcing metadata, so callers must ensure metadata was loaded. Directory root move guards compare path lengths against roots and should be tested around empty roots. Speedup can consume memory or disk and depends on correct source hash reporting; the spool path validates SHA1 but still adds operational complexity. Partial downloads rely on server range behavior and fall back to discarding leading bytes if the server sends a full response.

## Test Signals
Important test signals include configured integration tests through `mailru_test.go`, upload/download hash mismatch behavior with `check_hash` on and off, speedup eligibility for patterns, max memory/disk and partial transfers, small-file commit without upload, OAuth token refresh after 403, binary and JSON list parity, mkdir quirks, copy/move/DirMove across same and different accounts, range reads, and server-pool lock release on EOF and early close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mailru/mailru.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mailru/mailru_test.go -->
# sources/user-network-fs/rclone/backend/mailru/mailru_test.go

## Purpose
`mailru_test.go` wires the Mail.ru backend into rclone's shared backend integration suite. It does not define local unit tests; its role is to ensure the full `mailru` `fs.Fs` and `fs.Object` implementation conforms to rclone's common filesystem contract when a configured `TestMailru:` remote is available.

## Important APIs, Types, And Functions
The only test function is `TestIntegration`. It calls `fstests.Run` with `fstests.Opt{RemoteName: "TestMailru:", NilObject: (*mailru.Object)(nil), SkipBadWindowsCharacters: true}`. `NilObject` tells the shared harness the concrete object type expected from the backend. `SkipBadWindowsCharacters` acknowledges Mail.ru or the backend encoding behavior around names that are problematic on Windows-like filesystems.

## Control Flow
At test runtime, rclone's integration harness reads the named remote from test configuration, constructs the backend through `mailru.NewFs`, and runs the standard operation matrix: object creation, listing, metadata, reads, updates, moves, removals, directory behavior, optional interfaces, and error behavior. The file itself simply delegates into that harness.

## State And Persistence Behavior
The test uses a real or configured test remote and therefore mutates remote Mail.ru state under the harness-controlled test root. There is no file-local state, fixture, or cleanup logic; `fstests.Run` owns setup and teardown.

## Dependencies And Integration Points
The file depends on `github.com/rclone/rclone/backend/mailru` and `github.com/rclone/rclone/fstest/fstests`. It is an integration point between backend-specific code and rclone's common backend contract tests.

## Risks And Edge Cases
Coverage depends on credentials and service availability, so it may be skipped or fail for environmental reasons unrelated to code changes. Backend-specific paths such as OAuth reauthorization, speedup, binary listing quirks, server pool contention, and hash mismatch error handling are not explicitly isolated here.

## Test Signals
A passing run is a broad conformance signal for object lifecycle and optional interface behavior. Focused unit tests would still be useful for speedup pattern parsing, `mrhash` integration, binary list parsing, and error mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mailru/mailru_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mailru/mrhash/mrhash.go -->
# sources/user-network-fs/rclone/backend/mailru/mrhash/mrhash.go

## Purpose
`mrhash.go` implements Mail.ru Cloud's custom checksum algorithm as a Go `hash.Hash`. The algorithm returns padded raw content for data of 20 bytes or less; for larger data it computes SHA1 over the prefix string `mrCloud`, then file data, then the decimal byte length. The package also provides one-shot sum and hex decoding helpers for backend metadata.

## Important APIs, Types, And Functions
Exports are `BlockSize`, `Size`, `ErrorInvalidHash`, `New`, `Sum`, and `DecodeString`. The private `digest` tracks bytes written, an underlying SHA1 state, and `small` content used for <=20 byte sums. `Write` forwards to SHA1, increments `total`, and appends to `small` while the total remains within `Size`. `Sum` returns padded `small` for small inputs or clones the SHA1 state with `cloneSHA1`, writes the decimal length, and returns the SHA1 sum for larger inputs.

`Reset` initializes SHA1 and writes the fixed `startString`. `Size` returns 20 and `BlockSize` returns SHA1's block size of 64. `DecodeString` hex-decodes and enforces exactly 20 bytes.

## Control Flow
Streaming callers construct a digest with `New`, call `Write` repeatedly, and call `Sum` any number of times. `Sum` is side-effect free for large files because it marshals/unmarshals the SHA1 binary state before appending the length suffix. For small files it allocates a fresh 20-byte zero-padded buffer.

## State And Persistence Behavior
All state is in the digest instance. There is no global mutable state beyond exported constants and the sentinel error. The implementation relies on `crypto/sha1` supporting `encoding.BinaryMarshaler` and `encoding.BinaryUnmarshaler`.

## Dependencies And Integration Points
The Mail.ru backend registers this constructor as the rclone `MailruHash` type and uses `DecodeString` to parse API hashes and `Sum` or streaming `New` to validate uploads/downloads. The package depends only on standard crypto, encoding, hash, hex, errors, and strconv packages.

## Risks And Edge Cases
`Reset` does not clear `small`; after writing a small value, calling `Reset`, and then summing an empty digest may include old bytes if `small` retained previous content. The tests only assert no panic after reset, not correctness of the reset result. `Write` appends an entire write when `total <= Size` after the write, so it correctly stops storing small content once the total crosses 20 bytes. `Sum` panics if SHA1 state cloning fails, which should not occur with standard `sha1.New` but is a hard failure mode.

## Test Signals
Tests validate expected hashes across boundaries around 20 bytes and large sizes, many chunk sizes, idempotent repeated `Sum`, non-panicking reset/sum behavior, `Size`, and `BlockSize`. Additional targeted coverage should assert `Reset` clears previous small data and `DecodeString` rejects bad length and malformed hex.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mailru/mrhash/mrhash.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mailru/mrhash/mrhash_test.go -->
# sources/user-network-fs/rclone/backend/mailru/mrhash/mrhash_test.go

## Purpose
`mrhash_test.go` verifies the Mail.ru hash implementation across chunking strategies and size boundaries. It supplies known expected hex digests for empty, tiny, boundary, and multi-megabyte streams of repeated `A` bytes.

## Important APIs, Types, And Functions
The central helper is `testChunk(t, chunk int)`. It creates a reusable chunk buffer, writes each target length to a fresh `mrhash.New()` digest in the requested chunk size, and compares `hex.EncodeToString(d.Sum(nil))` against table-driven expected values. `TestHashChunk16M`, `TestHashChunk8M`, `TestHashChunk4M`, `TestHashChunk2M`, `TestHashChunk1M`, `TestHashChunk64k`, `TestHashChunk32k`, `TestHashChunk2048`, and `TestHashChunk2047` run the same vectors under different write boundaries. `TestSumCalledTwice`, `TestSize`, and `TestBlockSize` cover interface behavior.

## Control Flow
Each vector writes zero or more full chunks, then a final remainder. It calls `Sum(nil)` twice and expects identical output, which confirms that `Sum` does not mutate the digest state. The chunk sizes intentionally cross large Mail.ru upload-like boundaries and non-power-of-two boundaries.

## State And Persistence Behavior
The tests are pure in-memory unit tests. They allocate buffers up to 16 MiB and do not touch remote services or filesystem state.

## Dependencies And Integration Points
The file imports `backend/mailru/mrhash` and `testify/assert`. It provides the main direct safety net for the hash type registered by the Mail.ru backend.

## Risks And Edge Cases
The helper's failure message prints the final write length `n`, not the tested total length, which can make failed cases harder to diagnose. `TestSumCalledTwice` checks only that reset/sum does not panic; it does not assert the digest after reset, leaving the `small` slice reset behavior under-specified. `DecodeString` is not tested.

## Test Signals
Passing vectors signal correct small-file padding, length-suffixed SHA1 behavior above 20 bytes, chunk-boundary independence, and stable repeated `Sum`. Missing signals include reset correctness, bad hex handling, and comparison with live Mail.ru metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mailru/mrhash/mrhash_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mega/mega.go -->
# sources/user-network-fs/rclone/backend/mega/mega.go

## Purpose
`mega.go` implements rclone's MEGA backend using `github.com/t3rm1n4l/go-mega`. It adapts MEGA's encrypted, tree-oriented API to rclone's object storage interfaces, including login/session reuse, directory lookup/creation, listing, upload/download, delete, purge, server-side move and directory move, public links, duplicate directory merging, and quota reporting.

## Important APIs, Types, And Functions
`Options` contains user, password, 2FA code, hidden persisted session ID and master key, debug, hard delete, HTTPS transfer mode, and encoding. `Fs` stores the remote name/root, parsed options, features, shared `*mega.Mega`, pacer, cached root node, and mkdir mutex. `Object` stores the `Fs`, remote path, and pointer to a MEGA node.

Primary functions are `NewFs`, `findRoot`, `findNode`, `findDir`, `findObject`, `lookupDir`, `lookupParentDir`, `mkdir`, `mkdirParent`, `List`, `Put`, `PutUnchecked`, `Mkdir`, `Rmdir`, `Purge`, `CleanUp`, `move`, `Move`, `DirMove`, `PublicLink`, `MergeDirs`, `About`, `Object.Open`, `Object.Update`, `Object.Remove`, and `Object.ID`. `openObject` wraps chunked MEGA downloads as an `io.ReadCloser`.

## Control Flow
`NewFs` parses config, reveals the password, creates a pacer, advertises duplicate-file and empty-directory support, then retrieves or creates a cached `*mega.Mega` keyed by username. New sessions login with password and optional 2FA, persist `session_id` and base64 master key, and cache the connection. Existing sessions call `LoginWithKeys`. Root probing distinguishes existing directories, missing roots, and file roots.

Path resolution starts from the go-mega root node and uses encoded path parts with `FS.PathLookup`. `findRoot` caches the root node and optionally creates it. `mkdir` serializes directory creation, finds the deepest existing ancestor, then creates missing parts one by one.

Writes use `Put` to replace an existing object or `PutUnchecked` to create duplicates. `Object.Update` requires known length, creates parent directories, opens a MEGA upload, reads and uploads each chunk sequentially, finishes to obtain a node, and deletes the previous node if replacing. Reads call `NewDownload`, wrap it in `openObject`, skip chunks or offsets for range support, and finish the download in `Close` to surface MAC errors.

Moves create destination parents, find source parents, call `Move` if the parent changed, then `Rename` if the leaf changed, waiting briefly for MEGA events. Directory removal and purge share `purgeCheck`; optional hard deletion is controlled by config.

## State And Persistence Behavior
The backend persists session ID and master key back to rclone config after password login. In-memory state is dominated by the go-mega filesystem tree, shared through `megaCache` by username. `Fs._rootNode` caches the current backend root and is cleared after deleting or moving the root. `mkdirMu` serializes mkdir/rmdir/purge operations that mutate tree structure.

`Object` uses a MEGA node pointer rather than a plain ID because go-mega expects the whole tree in memory. This makes server-side moves simpler within a shared `*mega.Mega` but requires event waiting for the tree to settle after mutation.

## Dependencies And Integration Points
The backend integrates with rclone config, obscure, encoder, pacer, readers, fshttp, and optional interfaces (`Purger`, `Mover`, `PutUncheckeder`, `DirMover`, `DirCacheFlusher`, `PublicLinker`, `MergeDirser`, `Abouter`, `IDer`). All remote behavior is through go-mega. There is no supported content hash and modtime setting returns `fs.ErrorCantSetModTime`.

## Risks And Edge Cases
`megaCache` is keyed only by username, so remotes with different session settings for the same user intentionally share state. Upload and download chunks are sequential, which limits performance. `openObject.Close` must be called to finish and validate downloads. Range reads skip entire chunks then slice within a chunk, so off-by-one behavior depends on go-mega `ChunkLocation`. Update deletes the old node only after new upload finish; duplicate handling and delete failure can leave both versions. Directory cache flush is a stub.

## Test Signals
The integration test exercises broad backend conformance. Additional valuable coverage would target cached login/session persistence, root-as-file behavior, duplicate files, root deletion cache clearing, range reads, update replacement failure paths, hard-delete behavior, and server-side move/rename across cached remotes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mega/mega.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mega/mega_test.go -->
# sources/user-network-fs/rclone/backend/mega/mega_test.go

## Purpose
`mega_test.go` connects the MEGA backend to rclone's shared integration tests. It validates that `mega.Fs` and `mega.Object` satisfy expected rclone filesystem semantics against a configured `TestMega:` remote.

## Important APIs, Types, And Functions
The file contains `TestIntegration`, which invokes `fstests.Run` with `RemoteName: "TestMega:"` and `NilObject: (*mega.Object)(nil)`. It imports the backend package and the common `fstests` harness.

## Control Flow
The shared harness constructs a MEGA remote, performs common backend operations, and checks results. This includes object put/get/list/remove workflows and optional interfaces detected from `Fs.Features` and interface assertions.

## State And Persistence Behavior
Tests mutate the configured MEGA account under the harness test root. Session ID/master key persistence can occur through backend config behavior during `NewFs`, but the test file itself has no local state or cleanup.

## Dependencies And Integration Points
It depends on `github.com/rclone/rclone/backend/mega` and `github.com/rclone/rclone/fstest/fstests`. It is the high-level compatibility signal for go-mega integration.

## Risks And Edge Cases
No unit tests isolate the backend's session cache, chunked read/write behavior, duplicate-file support, event waiting, hard-delete, root cache invalidation, or unsupported modtime/hash behavior. Integration outcomes depend on external credentials and MEGA service behavior.

## Test Signals
Passing integration tests are broad confidence that MEGA implements rclone's core contract. Focused tests would be needed for concurrency, cached node mutation, and failure-path correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mega/mega_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/memory/memory.go -->
# sources/user-network-fs/rclone/backend/memory/memory.go

## Purpose
`memory.go` implements an in-memory, bucket-based rclone backend. It is primarily useful for tests and performance experiments, with an optional discard mode that records object metadata and MD5 while dropping data so reads fail. The backend supports buckets, empty directories as buckets, listing, recursive listing, copy, streaming put, MIME metadata, nanosecond modtime precision, and MD5 hashes.

## Important APIs, Types, And Functions
`Options` has the `Discard` flag. `Fs` stores name, root, parsed bucket and directory, options, and features. Global `buckets` is a process-wide `bucketsInfo` containing a map of bucket names to `bucketInfo`. `bucketInfo` stores object path keys to `objectData`. `Object` holds its `Fs`, remote path, and pointer to `objectData`.

Important functions include `NewFs`, `parsePath`, `Fs.split`, `setRoot`, `NewObject`, `list`, `listDir`, `listBuckets`, `List`, `ListP`, `ListR`, `Put`, `PutStream`, `Mkdir`, `Rmdir`, `Copy`, `Hashes`, `Object.Open`, `Object.Update`, `Object.Remove`, `Object.Hash`, `SetModTime`, and `MimeType`.

## Control Flow
`NewFs` parses options, trims root, splits bucket/directory, fills features, and detects whether the configured root points to an existing object. If root is an object path, it returns an Fs rooted at the parent and `fs.ErrorIsFile`.

Object writes create a temporary `Object` and call `Update`. In normal mode, `Update` reads the whole input into memory, sets size, modtime, MIME type, and leaves hash lazy. In discard mode, it streams through MD5, records only size/hash/modtime/MIME, and leaves `data` nil. `Open` honors seek and range options by slicing the stored byte slice unless discard mode is enabled, in which case it returns `errWriteOnly`.

Listing delegates through `list.WithListP`. Bucket-root listing returns bucket directories. Bucket listing scans the map under the bucket read lock, emits direct child dirs when not recursing, and emits objects otherwise. `ListR` intentionally collects entries before calling the list helper to avoid deadlock between listing and callbacks that may remove objects. Copy shallow-copies `objectData` metadata and data slice pointer from another memory object.

## State And Persistence Behavior
All objects are process-global in `buckets`; they persist across Fs instances in the same process and disappear when the process exits. `bucketsInfo.mu` protects the bucket map, and each bucket has its own RW mutex for object maps. `objectData` fields themselves are not individually synchronized after lookup, so concurrent mutation of a live object's modtime/hash/data through existing object pointers can race if callers share objects unsafely.

Bucket removal deletes only empty buckets. Directory objects are virtual, inferred from object key prefixes. The backend does not persist explicit non-bucket empty directories.

## Dependencies And Integration Points
The backend integrates with rclone's bucket path helper, list helper, configstruct, hash, MIME detection, optional `Copier`, `PutStreamer`, `ListRer`, `ListPer`, and `MimeTyper` interfaces. It is often used by rclone tests via the `:memory:` connection string.

## Risks And Edge Cases
Global process state can leak between tests if roots collide. Copy duplicates the `objectData` struct but not the underlying data slice, which is acceptable for immutable updates because `Update` replaces the whole pointer but can surprise code that mutates slices directly. The listing scan uses map iteration order, so output order is intentionally nondeterministic. `Mkdir` with an empty bucket name can create an empty-name bucket if invoked at root in unusual paths. Discard mode advertises written objects but all reads fail.

## Test Signals
Integration tests run in quick mode against `:memory:`. The internal deadlock test specifically validates that fallback purge does not deadlock when recursive listing and removals interact. Useful additional tests include global-state isolation, discard mode reads/hashes, range reads, root-as-file detection, bucket deletion errors, and concurrent update/list behavior under the race detector.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/memory/memory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/memory/memory_internal_test.go -->
# sources/user-network-fs/rclone/backend/memory/memory_internal_test.go

## Purpose
`memory_internal_test.go` provides backend-specific internal tests for the memory backend. Its current focus is a regression test for purge/list deadlocks when the backend's native `Purge` feature is disabled and rclone falls back to listing and removing entries.

## Important APIs, Types, And Functions
`InternalTest` implements `fstests.InternalTester` for `*Fs` and registers the `PurgeListDeadlock` subtest. `testPurgeListDeadlock` creates a test run, makes the remote root, disables the backend `Purge` feature, writes 100 small objects, and calls `operations.Purge`.

## Control Flow
The shared fstest harness can detect and call `InternalTest`. The deadlock test forces the fallback purge path by disabling the optional feature, then creates enough files that listing and removal overlap meaningfully. The memory backend's `ListR` implementation collects entries before invoking callbacks; this test protects that design choice.

## State And Persistence Behavior
The test uses the memory backend's process-global bucket state through `fstest.NewRunIndividual`. It creates transient objects with a fixed test timestamp and relies on the harness for cleanup/isolation.

## Dependencies And Integration Points
The file imports the local backend package, local backend registration for comparison support, `operations.Purge`, `fstest`, `fstests`, and `testify/require`. It asserts the memory backend implements `fstests.InternalTester`.

## Risks And Edge Cases
The test detects gross deadlock by completion, but it does not assert final empty state or run under explicit timeout in this file. Because the memory backend is global, poor harness isolation could make object counts or bucket names interact with other tests.

## Test Signals
Passing confirms fallback purge can list and delete many files without locking itself. It specifically supports the `ListR` implementation comment that calling `list.Add` while holding the bucket read lock could deadlock.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/memory/memory_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/memory/memory_test.go -->
# sources/user-network-fs/rclone/backend/memory/memory_test.go

## Purpose
`memory_test.go` runs rclone's standard backend integration tests against the in-memory backend. It validates the memory backend as both a normal backend implementation and a fast test fixture.

## Important APIs, Types, And Functions
`TestIntegration` calls `fstests.Run` with `RemoteName: ":memory:"`, `NilObject: (*Object)(nil)`, and `QuickTestOK: true`. The package is `memory`, not `memory_test`, so it can pair with internal tests and access local types directly.

## Control Flow
The shared harness constructs a memory remote using connection string syntax, performs object and directory operations, and can run in quick-test mode because the backend is local and fast.

## State And Persistence Behavior
The test uses the backend's process-global `buckets` map. The harness is expected to create isolated test roots and clean them up, but no file-local cleanup exists.

## Dependencies And Integration Points
It imports `fstests` and uses the memory backend registration from the same package. It is the broad contract test complement to `memory_internal_test.go`.

## Risks And Edge Cases
Standard integration coverage may not stress discard mode, global-state collisions, or race behavior. Because the backend is memory-only, it may pass operation patterns that network backends fail under latency or eventual consistency.

## Test Signals
Passing indicates compatibility with rclone's common Fs/Object expectations, including put, list, read, update, remove, hashes, modtime, and optional interface behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/memory/memory_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/netstorage/netstorage.go -->
# sources/user-network-fs/rclone/backend/netstorage/netstorage.go

## Purpose
`netstorage.go` implements rclone's Akamai NetStorage backend. It maps rclone object operations to NetStorage action-header HTTP requests signed with Akamai ACS auth headers. It supports listing, recursive listing with resume, uploads with SHA256 trailer signing, downloads with range options, MD5 hashes, modtime setting, empty directories, quick-delete purge, directory creation/removal, symlink adaptation through `.rclonelink`, and backend commands for `du` and `symlink`.

## Important APIs, Types, And Functions
`Options` contains endpoint host/path, account, secret, and protocol. `Fs` stores endpoint URL, rest client, pacer, root type, implicit directory map, and stat cache. `Object` stores remote path, file type, size, mtime, MD5, full URL, and symlink target. XML response types are `Stat`, `File`, `List`, `ListResume`, `Du`, and `DuInfo`.

Important methods include `NewFs`, `Command`, `NewObject`, `initFs`, `url`, `getFileName`, `List`, `ListR`, `Put`, `PutStream`, `implicitCheck`, `Purge`, `Mkdir`, `Rmdir`, `Object.Update`, `Object.Open`, `Object.Remove`, `SetModTime`, `newObjectWithInfo`, `getAuth`, `callBackend`, `netStorageStatRequest`, `netStorageDirRequest`, `netStorageListRequest`, `netStorageUploadRequest`, `netStorageDownloadRequest`, `netStorageDuRequest`, `netStorageSymlinkRequest`, and signing helpers.

## Control Flow
`NewFs` parses config, prefixes protocol onto the host/path, reveals the secret, joins the root into the endpoint URL, installs `getAuth` as the rest signer, fills features, and stats the root. If the root is a file or symlink, the endpoint and root are adjusted to the parent and `fs.ErrorIsFile` is returned.

Every backend call uses an `X-Akamai-ACS-Action` action string. `getAuth` builds `X-Akamai-ACS-Auth-Data` with account, timestamp, and random request ID, then signs data, request URI, and action with HMAC-SHA256. `callBackend` chooses raw or XML REST calls, applies pacer retry policy for selected HTTP status codes, and maps 404 to rclone not-found errors.

Listing uses `dir` for direct children and `list` for recursion. Recursive listing follows `resume.start`, rebuilds URLs from the endpoint, trims NetStorage CP-code prefixes, and converts symlinks into `.rclonelink` objects for local backend compatibility. Upload first calls `implicitCheck` to create all parent directories, then uses chunked upload with `sha256=atend` and `mtime=atend`, writing final action/auth trailers when the reader reaches EOF. Downloads issue `action=download` and delegate range normalization to `fs.FixRangeOption`.

## State And Persistence Behavior
Remote state lives in NetStorage. Local mutable state includes `dirscreated`, which avoids repeated implicit mkdir calls, and `statcache`, which caches successful stat responses by trimmed URL. Both maps are mutex-protected. Mutating operations invalidate the stat cache for affected URLs and remove dirscreated entries on rmdir.

The backend does not maintain a full directory cache. Empty directory support is remote-backed through mkdir/rmdir. Symlinks are represented as synthetic `.rclonelink` objects on list/stat/download/upload/delete.

## Dependencies And Integration Points
The file integrates with rclone `fs`, config, obscure, fshttp, rest, pacer, list helper, hash, and optional `Purger`, `PutStreamer`, and `ListRer` interfaces. It depends on XML response contracts from Akamai NetStorage and the ACS authentication scheme.

## Risks And Edge Cases
`getAuth` assumes the action header exists and indexes it directly; callers must always set it. `generateRequestID` creates a new time-seeded random source for each call, which is simple but not collision-proof under extreme concurrency. `implicitCheck` explicitly does not detect conflicts with existing files or dirs and can create duplicates per its comment. Stat cache invalidation is URL-local and may miss parent list effects. Quick-delete purge is asynchronous and returns `fs.ErrorCantPurge` on failure to trigger fallback. Upload failure attempts to remove the object, which can mask partial remote behavior.

## Test Signals
The integration test covers broad behavior against a configured remote. Additional focused tests should cover ACS signing strings, base64 filename fallback, stat cache invalidation, `.rclonelink` conversions, implicit directory creation, list resume handling, upload trailer signing, and command outputs for `du` and `symlink`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/netstorage/netstorage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/netstorage/netstorage_test.go -->
# sources/user-network-fs/rclone/backend/netstorage/netstorage_test.go

## Purpose
`netstorage_test.go` runs the Akamai NetStorage backend through rclone's common integration suite. It validates backend conformance when a `TestnStorage:` remote is configured.

## Important APIs, Types, And Functions
The only test is `TestIntegration`, which calls `fstests.Run` with `RemoteName: "TestnStorage:"` and `NilObject: (*netstorage.Object)(nil)`.

## Control Flow
The shared harness constructs the backend, performs standard file and directory lifecycle operations, and checks optional interface behavior exposed by `netstorage.Fs`.

## State And Persistence Behavior
The test mutates the configured NetStorage account under the harness test root. It has no local fixtures or explicit cleanup beyond the shared harness.

## Dependencies And Integration Points
It imports `backend/netstorage` and `fstest/fstests`. The file is the primary automated signal that the signed HTTP backend works with rclone's common contract.

## Risks And Edge Cases
External NetStorage credentials, permissions, endpoint path, and service state determine whether the test can run. It does not isolate signing helpers, XML parsing, stat cache behavior, symlink conversion, or upload trailer construction.

## Test Signals
Passing integration tests indicate functional put/list/read/delete behavior. Focused unit tests would improve confidence in request signing and path/URL edge cases without needing Akamai service access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/netstorage/netstorage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/onedrive/api/types.go -->
# sources/user-network-fs/rclone/backend/onedrive/api/types.go

## Purpose
`types.go` defines Go representations for Microsoft Graph OneDrive API resources and request/response payloads used by rclone's OneDrive backend. It includes error formatting, identity and quota structures, drive/item/folder/file facets, timestamps, sharing and permission types, upload/copy/move/share request bodies, delta/list responses, version/site/drive responses, and normalization helpers for remote shared items.

## Important APIs, Types, And Functions
Key exports include `Error`, `Identity`, `IdentitySet`, `Quota`, `Drive`, `Timestamp`, `ItemReference`, `RemoteItemFacet`, `FolderFacet`, `HashesType`, `FileFacet`, `FileSystemInfoFacet`, `DeletedFacet`, `PackageFacet`, `SharedType`, `SharingInvitationType`, `SharingLinkType`, `PermissionsType`, `Role`, `PermissionsResponse`, `AddPermissionsRequest`, `UpdatePermissionsRequest`, `DriveRecipient`, `Item`, `Metadata`, `DeltaResponse`, `ListChildrenResponse`, create/upload/copy/move/share request and response structs, `AsyncOperationStatus`, version and site/drive response types.

Behavioral helpers include `Error.Error`, `Timestamp.MarshalJSON`, `Timestamp.UnmarshalJSON`, `ItemReference.GetID`, `Metadata.IsEmpty`, many `Item.Get*` normalizers, `Item.MalwareDetected`, `Item.IsRemote`, and permission accessors `PermissionsType.GetGrantedTo` and `GetGrantedToIdentities`.

## Control Flow
The file is mostly declarative. JSON marshaling/unmarshaling flows through struct tags. `Timestamp` uses a fixed millisecond UTC format. `Item` helper methods prefer `RemoteItem` fields when present and populated, otherwise fall back to direct item fields. ID helpers prefix item IDs with drive IDs when a normalized ID is needed and the ID does not already contain `#`.

## State And Persistence Behavior
There is no runtime state. These structs are transient data transfer objects for Graph API calls. The only persistence implication is JSON shape compatibility with Microsoft Graph and rclone's metadata code.

## Dependencies And Integration Points
The file is used across the OneDrive backend for listing, metadata, permissions, uploads, moves, copies, deltas, public links, versions, and drive/site discovery. `metadata.go` relies heavily on `Metadata`, `PermissionsType`, role constants, recipient request structs, `FileSystemInfoFacet`, and item normalization helpers.

## Risks And Edge Cases
`Metadata.IsEmpty` compares `m.FileSystemInfo == &FileSystemInfoFacet{}`, which compares pointers rather than pointed-to contents. A newly allocated empty `FileSystemInfoFacet` is therefore not considered empty, so callers may issue metadata PATCH calls with empty fileSystemInfo. This may be intentional to force timestamp bodies, but the name is misleading. Timestamp parsing accepts only the exact millisecond format used in `timeFormat`, so Graph variants without milliseconds could fail if used for these fields. Remote item fallback is field-by-field and can miss valid zero values, such as remote size 0.

## Test Signals
This file has no direct tests in the listed set. Good coverage would include timestamp round trips, `Error.Error` with and without inner codes, normalized ID behavior, remote item getters, permission accessor differences between personal and business drives, and `Metadata.IsEmpty` semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/onedrive/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/onedrive/metadata.go -->
# sources/user-network-fs/rclone/backend/onedrive/metadata.go

## Purpose
`metadata.go` implements OneDrive metadata support for files and directories. It maps rclone `fs.Metadata` keys to Microsoft Graph item metadata, controls optional permission read/write behavior, creates and updates directory metadata, preserves birth/modification times, and exposes metadata/modtime methods for OneDrive objects and directories.

## Important APIs, Types, And Functions
Important definitions include `systemMetadataInfo`, `rwChoices`, `rwChoice`, `rwRead`, `rwWrite`, `rwFailOK`, `rwOff`, `rwExamples`, and the `Metadata` struct. `Metadata` caches MIME type, description, mtime, btime, upload time, creator/modifier identities, malware/package/shared flags, normalized ID, current permissions, queued permissions, and add-only permission mode.

Key methods are `Metadata.Get`, `Set`, `toAPIMetadata`, `Write`, `RefreshPermissions`, `WritePermissions`, `orderPermissions`, `sortPermissions`, `processPermissions`, `addPermission`, `updatePermission`, `removePermission`, `Fs.getPermissions`, `Fs.newMetadata`, `needsUpdatePermissions`, `Object.fetchMetadataForCreate`, `Fs.fetchAndUpdateMetadata`, `Object.updateMetadata`, `Fs.MkdirMetadata`, `createDir`, `updateDir`, `newDir`, `Object.Metadata`, `DirSetModTime`, `Directory.SetModTime`, `Directory.Metadata`, `Directory.SetMetadata`, and directory interface methods.

## Control Flow
Reading metadata is mostly local: `Get` formats cached system fields into `fs.Metadata`. If permission reading is enabled, it makes a Graph `/permissions` call, caches the result, marshals it to JSON, and includes it as the `permissions` key.

Writing begins with `Set`, which accepts writable keys. `mtime` and `btime` parse RFC3339 input into cached times; `description` is logged and skipped because Microsoft no longer supports it; `permissions` is unmarshaled only when permission write is enabled. `toAPIMetadata` builds Graph `fileSystemInfo`, defaulting btime to mtime when btime is missing to avoid creation time being overwritten. `Write` PATCHes item metadata and optionally writes permissions afterward.

Permission writes compare current and queued permissions. `sortPermissions` divides changes into add/update/remove, protects owner roles, handles business sharing-link update limitations by remove+add, supports add-only mode, and orders user permissions before group permissions. `processPermissions` removes first, then adds, then updates, accumulating non-retry errors. `addPermission` can create public anonymous links and otherwise sends `/invite` requests with recipients derived from identity fields.

Directory metadata creation uses `MkdirMetadata`: find or create the directory, send metadata during create when possible, then perform an extra write for modtime because OneDrive needs it. Existing directories are updated through `updateDir`.

## State And Persistence Behavior
Metadata is cached per `Object` or `Directory` in `meta`. Remote persistence occurs through Graph PATCH, invite, permission PATCH/DELETE, public link creation, and directory create requests. `queuedPermissions` is cleared only after successful refresh following writes. The `rwFailOK` option converts permission write errors into logged errors and nil returns.

The code does not keep a global metadata cache. Directory IDs come from `dirCache`, and `normalizedID` is required before permission operations. `Directory.SetModTime` preserves known btime or uses mtime as btime, then writes only timestamps.

## Dependencies And Integration Points
The file depends on OneDrive `api` DTOs, rclone metadata helpers, pacer/rest call helpers from the surrounding backend, dircache, error aggregation, and optional directory/object metadata interfaces. It is integrated into upload session creation, object metadata update after upload/copy, directory create/update, and public link behavior.

## Risks And Edge Cases
`api.Metadata.IsEmpty` pointer semantics can make empty metadata appear non-empty, causing `Write` to issue PATCHes with empty `FileSystemInfo`. `Set` counts `permissions` as set even if the decoded slice is empty; that can trigger permission removal behavior. Permission identity extraction maps non-email identities to `ObjectID` from `User.ID`, but group/site/application identities are temporarily copied into `User`, which is pragmatic but subtle. `Write` refuses to run when only permissions are queued but `toAPIMetadata` is empty; callers that want permissions-only writes should call `WritePermissions`. Public link creation inside `addPermission` can return a new permission-like object without a Graph invite if there are no recipients.

## Test Signals
The included tests cover `orderPermissions` for personal and business drive identity fields, including JSON from business `grantedToV2`. Missing focused tests include `Set` parsing, `toAPIMetadata` btime fallback, permission diff sorting for add/update/remove/owner/link cases, failok behavior, recipient extraction, directory metadata create/update, and permissions-only writes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/onedrive/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/onedrive/metadata_test.go -->
# sources/user-network-fs/rclone/backend/onedrive/metadata_test.go

## Purpose
`metadata_test.go` unit-tests the permission ordering workaround in OneDrive metadata handling. The ordering places permissions involving users before group-only permissions to avoid a Microsoft Graph behavior where adding a group before an equivalent user permission can cause the user permission to be dropped.

## Important APIs, Types, And Functions
`TestOrderPermissions` defines table-driven inputs of `*api.PermissionsType` and expected ID order. It runs each case for `driveTypePersonal` and `driveTypeBusiness`, converting personal fields to V2 business fields for the latter. `TestOrderPermissionsJSON` unmarshals a business-style JSON permissions array and verifies user-before-group ordering. Both tests call `Metadata.orderPermissions`.

## Control Flow
For each case, the test constructs a minimal `Metadata{fs: &Fs{driveType: ...}}`, applies the ordering in place, collects permission IDs, and compares them with the expected stable order. Cases cover empty input, mixed user/group/none, same-type stability, all-user stability, and missing identity data.

## State And Persistence Behavior
The tests are pure unit tests. They allocate permission slices in memory and perform no Graph calls or filesystem operations.

## Dependencies And Integration Points
The file imports `encoding/json`, the OneDrive `api` package, and `testify` assertions. It directly exercises an unexported method because it is in package `onedrive`.

## Risks And Edge Cases
The table mutates `tt.input` when converting to business fields, but each subtest instance is scoped under the drive type loop and the personal run happens before business in the literal slice order. Future parallelization or reuse could make that mutation surprising. The tests do not cover `sortPermissions`, recipient filling, anonymous links, owner protection, or failok behavior.

## Test Signals
Passing tests confirm the Graph workaround preserves relative order except for moving any user-bearing permission ahead of non-user permissions and handles both personal and business identity field variants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/onedrive/metadata_test.go -->

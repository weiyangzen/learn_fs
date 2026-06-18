# Research: subset-b-009745

Grouped research for rclone backends under `sources/user-network-fs/rclone/backend`: hasher object behavior, HDFS, HiDrive API/backend/hash code, HTTP backend, and Huawei Drive API/backend code. Each section is source-tree aligned and bounded by reconciliation markers for per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hasher/object.go -->
# sources/user-network-fs/rclone/backend/hasher/object.go

## Purpose
This file implements the object-level behavior of rclone's `hasher` overlay backend. It wraps an underlying `fs.Object` so hashes can be passed through, cached in the hasher key/value database, calculated while reading or uploading, and pruned when object identity changes.

## Important APIs, Types, And Control Flow
`Object.Hash` is the central API. It first asks the wrapped object for pass-through hashes when the base remote supports them, then checks whether the requested type is supported by the hasher overlay, then consults `getHash`/`getRawHash` in the KV database using a fingerprint, and finally falls back to slow base hashes or automatic download hashing for small objects. `Open` detects partial reads from `SeekOption` and `RangeOption`; only full-object reads are wrapped with `hashingReader` so a complete stream updates cached checksums. `Put` wraps upload input with `newHashingReader` when source hashes are incomplete or slow, otherwise copies available source hashes into the cache after the base `Put`. `Update`, `Remove`, and `SetModTime` prune stale cache entries before delegating to the wrapped object.

## State And Persistence
Persistent state is the hasher database entry keyed by `path.Join(f.Fs.Root(), remote)`, a fingerprint, and hash names. `putRawHashes` writes through `kvPut` with `MaxAge`; `getRawHash` reads through `kvGet` and enforces age. The fingerprint is derived from size, optional modtime, and optional fast hash from the underlying remote, deliberately avoiding `fs.Fingerprint` to prevent hasher-produced hash recursion.

## Dependencies And Integration Points
The file depends on rclone `fs`, `hash`, and `operations.HashSums`, the backend's `kvGet`/`kvPut`/`pruneHash` helpers, and wrapped object interfaces. It integrates with `fs.OpenOption` range semantics, `hash.MultiHasher`, and rclone upload/download flows.

## Risks And Test Signals
Partial reads intentionally do not refresh hashes; incorrect range detection would poison cache data. Failed `fingerprint` returns suppress caching and may hide backend hash/modtime errors. `Put` may rehash streams only when `newHashingReader` succeeds; source-provided hashes are trusted if rehashing is not needed. `SetModTime` only prunes when the timestamp differs from the current modtime. Good tests exercise cache hits/misses, `MaxAge <= 0`, pass-through blank hashes, slow hash storage, partial `Open`, upload with and without complete source hashes, and pruning on update/remove/touch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hasher/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hdfs/fs.go -->
# sources/user-network-fs/rclone/backend/hdfs/fs.go

## Purpose
This file implements the filesystem-level HDFS backend for non-Plan 9 builds. It creates the HDFS client, wires Kerberos or simple-user authentication, exposes rclone `fs.Fs` methods, and implements directory, object, move, purge, and quota operations against `github.com/colinmarc/hdfs/v2`.

## Important APIs, Types, And Control Flow
`Fs` stores remote name, root, parsed `Options`, global config, HDFS client, feature set, and pacer. `NewFs` parses config, builds `hdfs.ClientOptions`, optionally loads Kerberos credentials with `getKerberosClient`, initializes the client, and returns `fs.ErrorIsFile` if the configured root is a file. `List`, `NewObject`, `Put`, `Mkdir`, `Rmdir`, `Purge`, `Move`, `DirMove`, and `About` implement the rclone backend surface. `ensureDirectory` and `ensureFile` translate HDFS stat results to rclone `fs.ErrorDirNotFound` and `fs.ErrorObjectNotFound`.

## State And Persistence
State is mainly the live HDFS client and root path. Persistent effects happen directly in HDFS: mkdirs, removes, recursive removes, renames, writes through object update, and quota reads via `StatFs`. `realpath` combines configured root and remote path through `xPath` and the configured encoder.

## Dependencies And Integration Points
The backend integrates with the HDFS Go client, gokrb5 config/credential cache loading, rclone encoders, pacer, and optional rclone interfaces `Purger`, `PutStreamer`, `Abouter`, `Mover`, and `DirMover`. Kerberos uses `KRB5_CONFIG` and `KRB5CCNAME`, accepting only file credential caches.

## Risks And Test Signals
`Move` relies on HDFS `Rename` behavior that overwrites because the library hard-codes overwrite. `DirMove` only checks destination existence, not detailed source type after stat failure. HDFS path encoding and root joining should be tested with leading slash, colon, and invalid UTF-8 cases. Kerberos has environment-dependent risks around unsupported credential cache types. Integration tests need a real `TestHdfs:` remote and should cover root-as-file, empty-directory support, quota reporting, same-remote moves, recursive purge, and non-empty `Rmdir`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hdfs/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hdfs/hdfs.go -->
# sources/user-network-fs/rclone/backend/hdfs/hdfs.go

## Purpose
This file registers the HDFS backend and defines its user-facing configuration schema for non-Plan 9 platforms.

## Important APIs, Types, And Control Flow
`init` registers `fs.RegInfo{Name: "hdfs"}` with `NewFs` and options for `namenode`, `username`, Kerberos `service_principal_name`, Kerberos `data_transfer_protection`, and path `encoding`. `Options` is the parsed config struct consumed by `NewFs` in `fs.go`. `xPath` normalizes HDFS paths by forcing a leading slash and joining root with a tail path.

## State And Persistence
This file has no runtime persistence beyond global backend registration. Configuration values are persisted by rclone's normal config system, not by this file.

## Dependencies And Integration Points
It depends on rclone `fs`, `config`, and `encoder`. The `Options` fields are used by the HDFS client construction and path conversion in `fs.go` and `object.go`.

## Risks And Test Signals
The `namenode` option is required and sensitive, and examples imply comma-separated HA NameNode addresses. `xPath` uses `path.Join`, so empty roots and dot-like components are normalized; tests should cover root/tail combinations, especially remote roots without a leading slash. Platform build tags mean this file is excluded on Plan 9.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hdfs/hdfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hdfs/hdfs_test.go -->
# sources/user-network-fs/rclone/backend/hdfs/hdfs_test.go

## Purpose
This is the HDFS integration-test entry point for rclone's generic backend test suite.

## Important APIs, Types, And Control Flow
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestHdfs:"` and `NilObject: (*hdfs.Object)(nil)`. The test suite then drives the backend through standard object, directory, upload, move, remove, and metadata behaviors when a matching test remote is configured.

## State And Persistence
The test persists data only in the configured test HDFS remote through `fstests`. It does not define local fixtures or mocks.

## Dependencies And Integration Points
It imports the backend package and `github.com/rclone/rclone/fstest/fstests`. It is gated by `!plan9`, matching the backend implementation.

## Risks And Test Signals
Because this file delegates entirely to `fstests`, failures depend on external HDFS availability and credentials. It is a broad behavioral signal, but it does not directly test Kerberos branches, HDFS overwrite semantics, `ErrReplicating` close retry, or path encoding edge cases unless the generic suite happens to hit them.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hdfs/hdfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hdfs/hdfs_unsupported.go -->
# sources/user-network-fs/rclone/backend/hdfs/hdfs_unsupported.go

## Purpose
This Plan 9-only stub keeps the `hdfs` package buildable on unsupported platforms by providing a package declaration when the real HDFS files are excluded.

## Important APIs, Types, And Control Flow
The file has only the `//go:build plan9` tag and `package hdfs`; it defines no registration, options, types, or functions.

## State And Persistence
There is no runtime state or persistence.

## Dependencies And Integration Points
Its only integration point is Go build selection. On Plan 9, importing this package succeeds as an empty package, but the backend is not registered.

## Risks And Test Signals
The main risk is accidental use expecting `NewFs` or `Object` on Plan 9; those symbols do not exist. Compile tests on Plan 9-like build tags are the relevant signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hdfs/hdfs_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hdfs/object.go -->
# sources/user-network-fs/rclone/backend/hdfs/object.go

## Purpose
This file implements HDFS object behavior: metadata access, range-capable reads, whole-object replacement writes, modtime updates, removal, and rclone object interface conformance.

## Important APIs, Types, And Control Flow
`Object` stores parent `Fs`, remote path, size, and modtime. `Open` opens an HDFS file, applies `SeekOption` or `RangeOption`, seeks to the requested offset, and wraps the reader with `readers.NewLimitedReadCloser` when a limit is set. `Update` creates parent directories, removes any existing target, creates a new file, copies input, closes with pacer retry for `hdfs.ErrReplicating`, stats the final object, sets modtime via `Chtimes`, and updates cached size. `Hash` always returns `hash.ErrUnsupported`.

## State And Persistence
Persistent effects are HDFS writes, deletion of any replaced object, chmod-like timestamp changes through `Chtimes`, and removal via `client.Remove`. Object fields cache the latest size and modtime after successful stat and timestamp operations.

## Dependencies And Integration Points
It uses the HDFS client from `Fs`, rclone open options, `readers.NewLimitedReadCloser`, and the `Fs` pacer for close retry. It integrates with the `Put` method in `fs.go`, which constructs an `Object` and delegates to `Update`.

## Risks And Test Signals
`Update` removes an existing destination before creating the replacement, so a copy or close failure can leave no old object and a cleanup attempt for the partial new file. `Open` does not explicitly reject negative offsets before `Seek`; HDFS seek behavior handles errors. The `ErrReplicating` close path is important because HDFS can acknowledge data before NameNode lease closure. Tests should cover overwrite failure cleanup, range reads, modtime persistence, unsupported hashes, and close retry behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hdfs/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hidrive/api/queries.go -->
# sources/user-network-fs/rclone/backend/hidrive/api/queries.go

## Purpose
This file provides query-parameter helpers and field presets for the HiDrive REST API. It centralizes path, directory/file, timestamp, list, and field selection parameter construction.

## Important APIs, Types, And Control Flow
Field presets include `HiDriveObjectNoMetadataFields`, `HiDriveObjectWithMetadataFields`, `HiDriveObjectWithDirectoryMetadataFields`, and `DirectoryContentFields`. `QueryParameters` embeds `url.Values`. `SetFileInDirectory` splits a file path into `dir` and `name` for create-style calls. `SetPath` sets the API `path` parameter. `SetTime` marshals `api.Time` as Unix seconds. `AddList` appends separator-joined values to an existing parameter, and `AddFields` prefixes field names before appending them to `fields`.

## State And Persistence
There is no persistent state. The helpers mutate in-memory `url.Values` used by REST calls.

## Dependencies And Integration Points
The helpers are used throughout `helpers.go` and `hidrive.go` for `/meta`, `/dir`, `/file`, copy/move, upload, truncate, and delete operations. They depend on `path.Clean`, `path.Split`, JSON marshaling, and URL query encoding.

## Risks And Test Signals
`SetFileInDirectory` cleans the directory component and can turn empty or relative paths into normalized values; endpoint semantics should be verified for root files. `AddList` overwrites then prepends old values, so ordering is old values first. Timestamp parameters include JSON number text, not RFC3339. Unit tests should validate query strings for root paths, nested file creation, multiple field additions, and timestamp encoding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hidrive/api/queries.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hidrive/api/types.go -->
# sources/user-network-fs/rclone/backend/hidrive/api/types.go

## Purpose
This file defines HiDrive API value types, error decoding structures, object metadata, and directory listing response shapes.

## Important APIs, Types, And Control Flow
`Time` marshals and unmarshals API timestamps as Unix seconds. `Error` implements `error` and preserves numeric code, message, and raw context. `HiDriveObject` models files, directories, and symlinks with IDs, names, paths, size, member count, times, hash fields, permissions, and MIME type. `HiDriveObject.ModTime` falls back from `mtime` to `ctime`. `UnmarshalJSON` sets default `Size` and `MemberCount` to `-1` and path-unescapes names. `DirectoryContent` defaults `TotalCount` to `-1`.

## State And Persistence
These are data transfer objects only. Defaults affect in-memory behavior when API fields are omitted.

## Dependencies And Integration Points
`hidrive.go` uses `HiDriveObject` to populate rclone objects and dirs. `helpers.go` uses `Error` through `isHTTPError` and `DirectoryContent` for pagination. The custom time representation is shared with query timestamp setters.

## Risks And Test Signals
Defaulting missing sizes/member counts to `-1` is important for distinguishing unknown values from zero. Path-unescaping names can hide malformed escapes by leaving the original on error. `Error.Code` is a `json.Number`, so callers must handle non-numeric codes. Tests should cover timestamp round trips, omitted fields, escaped names, directory content defaults, and `Error.Error` formatting with and without context.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hidrive/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hidrive/helpers.go -->
# sources/user-network-fs/rclone/backend/hidrive/helpers.go

## Purpose
This file contains the HiDrive backend's operational helper layer: retry decisions, path resolution, paginated directory iteration, metadata fetch, copy/move, directory creation/deletion, file create/overwrite/patch/truncate, parallel chunked uploads, scope creation, and repeatable reader utilities.

## Important APIs, Types, And Control Flow
`shouldRetry` handles context cancellation, OAuth token expiry on 401 with `Www-Authenticate`, generic retryable errors, and retryable HTTP codes. `resolvePath` joins root prefix, backend root, and encoded path. `iterateOverDirectory` and `paginateDirectoryAccess` issue `/dir` requests with `limit=offset,count` windows. `createDirectories` recursively creates parents after `fs.ErrorDirNotFound`. File helpers distinguish `createFile` POST, `overwriteFile` PUT, `patchFile` PATCH at offsets, and `resizeFile` truncate/extend. `updateFileChunked` reads fixed chunks, uses an errgroup plus semaphore for parallel `patchFile` calls, records successful byte ranges, and returns the first continuous uploaded size.

## State And Persistence
Stateful effects are API mutations: directories and files are created, moved, copied, deleted, patched, resized, and timestamped. Chunked uploads are explicitly non-atomic and can leave partially modified or sparse files. Retry state lives in pacers and OAuth token renewer side effects.

## Dependencies And Integration Points
The file depends on HiDrive DTO/query helpers, rclone pacer/rest/accounting/fserrors/ranges/readers, and `golang.org/x/sync` errgroup/semaphore. Top-level backend methods in `hidrive.go` compose these helpers for rclone interfaces.

## Risks And Test Signals
`uploadFileChunked` and `updateFileChunked` can create sparse files and partially update existing content when chunks fail. `UploadConcurrency` less than one can deadlock because it becomes the semaphore capacity. `createDirectories` does not roll back parents on later failure. `cachedReader` may buffer whole chunks for retryability. `patchFile` retries HTTP 423 locks. Tests should cover pagination boundaries, 401 token expiry, 404/409 error translation, recursive mkdir partial failures, chunk read errors versus upload errors, continuous-range calculation, and sparse/truncate behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hidrive/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hidrive/hidrive.go -->
# sources/user-network-fs/rclone/backend/hidrive/hidrive.go

## Purpose
This file registers and implements the HiDrive rclone backend. It handles OAuth setup, backend options, object metadata, listing, upload/update, server-side copy/move, directory operations, hash exposure, token renewal, and interface declarations.

## Important APIs, Types, And Control Flow
`init` registers the `hidrive` backend and custom HiDrive hash type. `NewFs` parses options, normalizes root prefix and root, creates an OAuth REST client, configures pacers, validates root prefix, checks whether root is missing, a directory, or a file, and returns `fs.ErrorIsFile` for file roots. `Fs.List` paginates directory entries and constructs `fs.Dir` or `Object` values. `Put` updates existing objects or delegates to `PutUnchecked`; `PutUnchecked` creates an initial file up to the cutoff atomically, creates parents once if needed, and then continues via `Object.Update` with a seek offset. `Copy`, `Move`, and `DirMove` use server-side operations and create destination parents on one retry. `Object` lazily reads metadata, exposes ID, size, modtime, HiDrive hash, range-capable `Open`, metadata patching for modtime, chunked or simple update, and removal.

## State And Persistence
Persistent state is remote HiDrive file and directory contents plus metadata. Object instances cache metadata once loaded. The OAuth token renewer may refresh token state through rclone's OAuth stack. Upload configuration controls whether mutations happen through single create/overwrite calls or non-atomic chunked patch/truncate operations.

## Dependencies And Integration Points
The backend depends on `api` types, `helpers.go`, `hidrivehash`, rclone `fs`, OAuth, rest, pacer, config/encoder, and hash registration. It implements `fs.Fs`, `Purger`, `PutStreamer`, `PutUncheckeder`, `Copier`, `Mover`, `DirMover`, `Shutdowner`, `fs.Object`, and `fs.IDer`.

## Risks And Test Signals
`Shutdown` calls `f.tokenRenewer.Shutdown()` without a nil check; construction paths without a token source would panic. `PutUnchecked` reads up to upload cutoff before object creation and may delete a failed partially uploaded object, but delete failure returns the object with the upload error. Metadata is lazy, so `Size`, `ID`, and `ModTime` use logging fallbacks when API reads fail. Names over 255 characters are noted as provider errors. Tests should cover root prefix validation, root-as-file, chunk cutoff/offset continuation, existing-object update, parent auto-creation, copy/move conflict handling, hash metadata, no-member-count listing, and token renewer behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hidrive/hidrive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hidrive/hidrive_test.go -->
# sources/user-network-fs/rclone/backend/hidrive/hidrive_test.go

## Purpose
This file hooks the HiDrive backend into rclone's generic integration test suite and provides test-only setters for upload chunking parameters.

## Important APIs, Types, And Control Flow
`TestIntegration` runs `fstests.Run` against `TestHiDrive:` with HiDrive's object type and `ChunkedUploadConfig` spanning one byte through `MaximumUploadBytes`. `SetUploadChunkSize` and `SetUploadCutoff` mutate `f.opt` and return the previous value so the generic tests can force chunked upload scenarios.

## State And Persistence
The test mutates backend upload options in memory during tests. Remote persistence is handled by the generic integration suite against the configured HiDrive remote.

## Dependencies And Integration Points
It integrates with `fstests.SetUploadChunkSizer` and `fstests.SetUploadCutoffer`, allowing generic test cases to exercise chunk boundaries.

## Risks And Test Signals
The test suite depends on a real `TestHiDrive:` remote and valid OAuth. It is a broad signal for standard rclone behavior and chunked uploads, but does not directly unit-test REST error mapping, token renewer nil behavior, recursive mkdir rollback absence, or sparse chunk failure semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hidrive/hidrive_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hidrive/hidrivehash/hidrivehash.go -->
# sources/user-network-fs/rclone/backend/hidrive/hidrivehash/hidrivehash.go

## Purpose
This package implements HiDrive's hierarchical content hash. It combines SHA-1 block hashes into position-embedded level hashes, supports streaming writes, and exposes binary marshal/unmarshal so hash state can be persisted or copied mid-stream.

## Important APIs, Types, And Control Flow
Constants define a 4096-byte level-0 block, 20-byte output size, and 256 sums per higher level. `writeByBlock` feeds a writer in exact block units while tracking bytes and all-zero blocks. `level` aggregates up to 256 SHA-1-sized sums; for non-null blocks it appends the block position byte before adding the SHA-1 sum into a big-endian checksum with carry. `hidriveHash.Write` hashes 4096-byte data blocks, maps all-zero blocks to `zeroSum`, and propagates full levels upward via `aggregateToLevel`. `Sum` snapshots state, pads a partial block with zeroes, folds incomplete levels, returns the final checksum, and restores state. Both `level` and `hidriveHash` implement binary marshaling.

## State And Persistence
Hash state includes level checksums, counts, partial block/hash bytes, all-null flags, and the last sum written. Binary marshaling serializes this state plus the underlying SHA-1 marshaled state. No external persistence is performed by the package itself.

## Dependencies And Integration Points
It depends on Go `crypto/sha1`, `hash`, `encoding.BinaryMarshaler`, and the internal `LevelHash` interface. `hidrive.go` registers `hidrivehash.New` as rclone's `HiDriveHash`.

## Risks And Test Signals
`level.Write` intentionally violates usual `hash.Hash` expectations by returning `ErrorHashFull` when full; `hidriveHash.aggregateToLevel` panics if a level write errors unexpectedly. `UnmarshalBinary` trusts encoded length fields enough to slice into `b`, so malformed lengths beyond short header cases can panic. Correctness depends on all-zero block handling and padding partial blocks on `Sum`. Tests should use official HiDrive vectors, mixed null ranges, arbitrary write chunk sizes, marshal/unmarshal continuation, reset, and invalid encodings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hidrive/hidrivehash/hidrivehash.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hidrive/hidrivehash/hidrivehash_test.go -->
# sources/user-network-fs/rclone/backend/hidrive/hidrivehash/hidrivehash_test.go

## Purpose
This file validates the custom HiDrive hash implementation against documentation-derived vectors and important hash.Hash behaviors.

## Important APIs, Types, And Control Flow
The tests define vector tables for position-embedded level additions, level writes, and full HiDrive hashes over generated repeated data/null-byte patterns. `TestLevelAdd`, `TestLevelWrite`, `TestLevelIsFull`, reset/size/block-size tests, marshal/unmarshal tests, and invalid encoding tests cover `level`. `TestWrite`, `TestReset`, `TestBinaryMarshaler`, `TestInvalidEncoding`, and `TestSum` cover `hidriveHash`. Helpers include an `infiniteReader` and `writeInChunks` to feed the same logical data with different physical write chunk sizes.

## State And Persistence
Tests persist no external state. They check in-memory hash state before and after reset and binary marshal/unmarshal.

## Dependencies And Integration Points
The tests import the public `hidrivehash` package and its internal `LevelHash` interface to validate level-specific methods. They use `testify/assert` for expectations and Go `encoding` interfaces for marshal checks.

## Risks And Test Signals
The suite strongly covers deterministic hash values, all-null content, non-block-aligned inputs, level capacity, write chunk independence, and state round trips. It only lightly covers invalid binary encodings; malformed length fields in otherwise long encodings are not exhaustively fuzzed. It does not benchmark large inputs or concurrency, which is acceptable because hash instances are not concurrency-safe.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hidrive/hidrivehash/hidrivehash_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hidrive/hidrivehash/internal/internal.go -->
# sources/user-network-fs/rclone/backend/hidrive/hidrivehash/internal/internal.go

## Purpose
This internal file defines the `LevelHash` interface used by tests and internal package consumers to expose level-specific hash operations without exporting the concrete `level` type.

## Important APIs, Types, And Control Flow
`LevelHash` embeds `encoding.BinaryMarshaler`, `encoding.BinaryUnmarshaler`, and `hash.Hash`, and adds `Add(sum []byte)` plus `IsFull() bool`. There is no executable control flow.

## State And Persistence
The interface defines behavior only. Implementations may have binary-marshaled state, but this file stores nothing.

## Dependencies And Integration Points
`hidrivehash.level` asserts conformance to this interface, and `hidrivehash_test.go` uses it to test `Add` and `IsFull` directly while keeping the concrete type unexported.

## Risks And Test Signals
Because this is an internal interface, its compatibility risk is small and limited to the `hidrivehash` package tree. Compile-time conformance and tests that type-assert `NewLevel()` to `internal.LevelHash` are the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hidrive/hidrivehash/internal/internal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/http/http.go -->
# sources/user-network-fs/rclone/backend/http/http.go

## Purpose
This file implements rclone's read-only HTTP backend. It treats HTML directory listings as folders, exposes linked files as objects, supports optional request headers and no-HEAD/no-slash modes, reads selected HTTP metadata, and offers a backend command to update config at runtime.

## Important APIs, Types, And Control Flow
`init` registers the backend, options, command help, and metadata keys. `NewFs` parses options and calls `httpConnection`, which normalizes the endpoint/root and uses `getFsEndpoint` to decide whether the root points to a file or directory. `parseName` and `parse` convert same-host/same-scheme single-level anchor hrefs into listing names. `List` reads an HTML directory and concurrently HEADs potential files to classify files versus directories unless entries already end with `/`. `Object.head` populates size, modtime, content type, content disposition, and other headers. `Open` issues GET and applies option headers. Mutating methods return `errorReadOnly`. `Command("set")` reparses new options and rebuilds the connection. `Metadata` returns supported headers in lower-case keys.

## State And Persistence
The backend stores endpoint URL, parsed root, custom headers, a shared HTTP client, and object metadata from HEAD/GET responses. It does not persist remote data and all write/delete/mkdir/update operations fail read-only. Runtime `set` updates in-memory config only for the running backend instance.

## Dependencies And Integration Points
It depends on Go `net/http`, `net/url`, MIME parsing, `golang.org/x/net/html`, rclone `fs`, `fshttp`, `rest`, hash interfaces, metadata interfaces, and command plumbing. It implements `fs.Fs`, `fs.PutStreamer` only to return read-only errors, `fs.Object`, `fs.MimeTyper`, `fs.Commander`, and `fs.Metadataer`.

## Risks And Test Signals
`List` uses `sync.WaitGroup.Go`, so it depends on the Go version/runtime API available in this source tree. No-HEAD mode returns unknown size/time and can misclassify HTML files when `NoSlash` is set. `parseName` excludes query strings and cross-host/scheme links, which is safe but may skip valid download URLs. `Remote` can be overridden by `Content-Disposition` filename, which may surprise path identity. Tests should cover all listing parsers, root-as-file detection, no-head behavior, custom headers, metadata extraction, range GET options, read-only errors, no-escape URLs, and backend `set`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/http/http.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/http/http_internal_test.go -->
# sources/user-network-fs/rclone/backend/http/http_internal_test.go

## Purpose
This file provides unit and integration-style tests for the HTTP backend using a local `httptest` server and static fixture files/listings.

## Important APIs, Types, And Control Flow
`prepareServer` serves fixture files, asserts configured headers on requests, injects metadata headers for `five.txt.gz`, and returns a config map. Tests cover root listing with and without `NoSlash`, subdirectory listing, object stat with and without leading slash, metadata extraction, normal and range reads with and without HEAD, MIME type, root paths that point to files, `parseName`, HTML parser fixtures for Apache/Memstore/Nginx/Caddy, and `getFsEndpoint` behavior across HEAD status and redirect cases.

## State And Persistence
Tests use local fixture files under `test/files` and `test/index_files`, local HTTP test servers, and temporary in-memory config. They do not mutate external remotes.

## Dependencies And Integration Points
The tests import rclone config and fstest helpers, `httptest`, local fixtures, and `testify`. They exercise unexported package functions because they are in package `http`.

## Risks And Test Signals
The tests provide strong signals for parsing, header injection, metadata, range reads, and root classification. They do not cover the backend `set` command, read-only method errors, no-escape path behavior, malformed `Content-Disposition`, concurrent `List` failure races, or HTTP status handling beyond selected root HEAD paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/http/http_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/huaweidrive/api/types.go -->
# sources/user-network-fs/rclone/backend/huaweidrive/api/types.go

## Purpose
This file defines Huawei Drive API request and response structures, constants, regional endpoint mappings, and small helpers used by the backend.

## Important APIs, Types, And Control Flow
`About`, `User`, `FileList`, and `File` model quota, account, listing, and file/folder metadata responses. `File.IsDir` checks the Huawei folder MIME type. Request types include `CreateFolderRequest`, `UpdateFileRequest`, and `CopyFileRequest`. Upload/change types include `ResumeUploadInitResponse`, `StartCursor`, `ChangeList`, and `ChangeItem`. Constants define MIME types, upload/form types, categories, and global API roots. `DomainToRootURL` maps provider domain names/regions to regional API roots; `GlobalDomains` marks domains that should not be switched. `BoolPtr` supports optional boolean update fields.

## State And Persistence
The file contains only DTOs and static maps. It does not perform persistence. The regional maps influence runtime endpoint selection in `huaweidrive.go`.

## Dependencies And Integration Points
The backend uses these types for all REST calls: about/quota, file listing, folder creation, metadata update, copy, resumable upload initialization, errors, and change notification.

## Risks And Test Signals
Many numeric API values are strings in `About` and must be parsed by callers. Metadata maps use `map[string]interface{}`, so type conversion is caller-controlled. Regional domain coverage must stay aligned with Huawei responses. Tests should verify `IsDir`, endpoint-domain switching values, bool pointer behavior, and JSON compatibility for update/create/copy/upload/change payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/huaweidrive/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/huaweidrive/huaweidrive.go -->
# sources/user-network-fs/rclone/backend/huaweidrive/huaweidrive.go

## Purpose
This file implements the Huawei Drive rclone backend. It handles OAuth, root detection, regional endpoint switching, directory caching, listing, upload modes, server-side copy/move, metadata, recycle cleanup, change notification, user info, and disconnect.

## Important APIs, Types, And Control Flow
`init` registers backend options and metadata capabilities. `NewFs` builds an OAuth REST client, resolves the concrete drive root ID via `/files/root` unless configured, optionally switches to a regional domain using `/about`, creates a `dircache.DirCache`, and handles root-as-file detection. `FindLeaf` and `CreateDir` satisfy dircache lookup/create hooks. `listDirectoryWithFilter` builds Huawei query strings and paginates `/files`. `List` and `ListR` populate dirs/objects and cache item metadata for later change notification. `Put` updates existing objects or recovers duplicate create races by looking up and updating. `Object.Update` spools unknown-size streams to a temp file, creates parents, and chooses empty, multipart, or resumable upload. Copy/move use `/copy` or PATCH updates and include verification/fallback for cross-directory move quirks. `Metadata` and `SetMetadata` map system/user metadata to Huawei fields/properties. `ChangeNotify` polls start cursors and change lists, deduplicates path notifications, and uses dircache plus item cache to resolve old and new paths.

## State And Persistence
Persistent remote effects include file/folder creation, upload replacement, deletion/recycle, directory purge, metadata updates, copies, moves, and recycle-bin cleanup. Local process state includes directory ID cache, item metadata cache, root folder ID, regional URLs, OAuth token in rclone config, and temporary files for unknown-size uploads. Huawei does not preserve requested modification times, so `Precision` returns `fs.ModTimeNotSupported`.

## Dependencies And Integration Points
The backend depends on Huawei DTOs, rclone `dircache`, OAuth, rest, pacer, metadata helpers, MIME detection, encoder, and standard multipart/HTTP packages. It implements many optional rclone interfaces: `Purger`, `Copier`, `Mover`, `DirMover`, `ListRer`, `CleanUpper`, `Abouter`, `ChangeNotifier`, `UserInfoer`, `Disconnecter`, `DirCacheFlusher`, `MimeTyper`, and `Metadataer`.

## Risks And Test Signals
Upload code buffers multipart uploads fully in memory below cutoff and spools unknown-size uploads to a local temp file. Resumable upload chunk size is clamped at runtime rather than rejected at config parse. Empty-file upload removes an existing object first, so replacement failure can lose the old file. `Remove` assumes `o.id` is populated. Query filters are manually formatted strings; escaping only handles single quotes in filenames. Error mapping collapses HTTP 409 to `fs.ErrorDirExists`, which may be too broad. Change notification only resolves parents already in dircache. Tests should cover root ID detection, regional switching, list pagination, dircache invalidation, duplicate create race recovery, all upload modes, metadata read/write, empty SHA256 behavior, cross-directory move fallback, cleanup, retry mapping, and cursor polling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/huaweidrive/huaweidrive.go -->

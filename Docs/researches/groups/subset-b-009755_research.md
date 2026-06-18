# Research Group subset-b-009755

This grouped report covers rclone network-storage backends for ShareFile, Sia, SMB, Storj, SugarSync, and Swift. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sharefile/sharefile.go -->
# sources/user-network-fs/rclone/backend/sharefile/sharefile.go

## Purpose

`sharefile.go` implements the main rclone backend for Citrix ShareFile. It registers the `sharefile` remote, performs OAuth setup and endpoint discovery, maps rclone `fs.Fs`/`fs.Object` operations onto ShareFile item APIs, maintains a directory ID cache, and handles ShareFile-specific timestamp and copy/move quirks.

## Important APIs, Types, and Functions

`Options` stores `root_folder_id`, upload cutoff/chunk size, endpoint, and encoding. `Fs` holds backend state: name/root, REST client, pacer, `dircache.DirCache`, upload buffer tokens, OAuth renewer, root ID, and the ShareFile timezone workaround location. `Object` stores remote path, metadata validity, size, modtime, item ID, and MD5. Key functions include `NewFs`, `readMetaDataForIDPath`, `FindLeaf`, `CreateDir`, `listAll`, `List`, `Put`, `PutUnchecked`, `purgeCheck`, `updateItem`, `move`, `Move`, `DirMove`, `Copy`, `Shutdown`, and object methods for hash, metadata, open, update, and remove.

## Control Flow

Initialization parses config, validates chunk size, creates an OAuth HTTP client, loads embedded `America/New_York` timezone data, resolves the root folder ID, initializes `dirCache`, and handles the common "root is actually a file" case by returning the parent `Fs` with `fs.ErrorIsFile`. Metadata reads go through directory-cache path resolution followed by `/Items(...)/ByPath` or `/Items(...)`. Listing reads `/Children` and converts folders to `fs.Dir` entries and files to `Object`s. Uploads create/find the parent folder and delegate object writes to `Object.Update`, which chooses normal or large upload behavior. Moves use a multi-step rename/move helper to avoid a ShareFile API overwrite bug. Copy may copy via a temporary folder because the API cannot rename while copying.

## State and Persistence Behavior

Runtime state includes cached directory IDs, cached upload buffers sized by `--transfers`, OAuth refresh state, and object metadata. Persistent configuration can include endpoint, OAuth token fields, root folder ID, and upload options. The backend stores no local data beyond config and embedded timezone data.

## Dependencies and Integration Points

It depends on `backend/sharefile/api`, rclone `fs`, `configstruct`, OAuth helpers, `dircache`, `encoder`, `pacer`, `random`, and `rest`. It implements rclone optional interfaces including hash reporting, purge, move, dir move, copy, directory cache flush, and shutdown. `upload.go` supplies the large-upload machinery used by `Object.Update`.

## Risks and Edge Cases

The backend contains explicit comments for ShareFile API bugs: patched modtimes are interpreted in Eastern time and only set to second precision, rename plus move can overwrite source-directory names, and copy cannot rename atomically. `Put` ignores open options when creating a missing object. Large uploads depend on buffer-token invariants and correct chunk sizes. `listAll` is non-paginated in this file, so very large folders depend on ShareFile API behavior. `Shutdown` assumes `tokenRenewer` is non-nil. Errors are parsed from JSON when possible but may include raw body text.

## Test Signals

`sharefile_test.go` runs rclone integration tests against `TestSharefile:` and exposes upload chunk/cutoff setters. Important signals include normal and chunked uploads, MD5 verification, server-side copy/move/dir move, directory cache invalidation, purge refusal for non-empty directories, timestamp precision, and root-as-file behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sharefile/sharefile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sharefile/sharefile_test.go -->
# sources/user-network-fs/rclone/backend/sharefile/sharefile_test.go

## Purpose

This file wires the ShareFile backend into rclone's generic integration test suite. It verifies the backend through the common `fstests` contract rather than backend-local unit tests.

## Important APIs, Types, and Functions

`TestIntegration` calls `fstests.Run` with `RemoteName: "TestSharefile:"`, `NilObject: (*Object)(nil)`, and a `ChunkedUploadConfig` using the backend's `minChunkSize` and `fstests.NextPowerOfTwo` chunk-size ceiling. Test-only methods `SetUploadChunkSize` and `SetUploadCutoff` expose the unexported setters used by generic upload tests. Interface assertions require `*Fs` to satisfy `fstests.SetUploadChunkSizer` and `fstests.SetUploadCutoffer`.

## Control Flow

The test harness discovers configuration for `TestSharefile:`, constructs the backend, then executes standard object, directory, move/copy, hash, purge, and chunked upload scenarios. The chunk-size setter lets the harness force boundary sizes and confirm the backend reinitializes its upload buffer token pool.

## State and Persistence Behavior

The file has no persistent state. It does mutate backend upload options during integration tests through the exposed setters, and those changes are confined to the in-memory `Fs` under test.

## Dependencies and Integration Points

It depends on `github.com/rclone/rclone/fstest/fstests` and the backend package itself. The strongest integration signal is conformance to rclone's common remote filesystem behavior against a live ShareFile account.

## Risks and Edge Cases

These are live integration tests and require valid remote configuration and network access. They do not unit-test ShareFile error parsing, timezone correction, or copy/move workaround branches directly. The test-only setters are compiled with the package and must remain consistent with internal validation.

## Test Signals

Success indicates the backend satisfies rclone's generic filesystem expectations, including chunked upload behavior. Failures around chunk sizes, modtimes, or move/copy operations usually point back to `sharefile.go` and `upload.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sharefile/sharefile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sharefile/tzdata_vfsdata.go -->
# sources/user-network-fs/rclone/backend/sharefile/tzdata_vfsdata.go

## Purpose

This generated file embeds a minimal timezone filesystem containing `America/New_York` for the ShareFile backend. ShareFile's update-item API parses patched modification times as Eastern local time, so the backend needs this timezone data even on systems where zoneinfo may be unavailable.

## Important APIs, Types, and Functions

The exported package variable `tzdata` is an `http.FileSystem`. It maps `/`, `/America`, and `/America/New_York` to generated directory and compressed-file objects. Internal generated types include `vfsgen۰FS`, `vfsgen۰CompressedFileInfo`, `vfsgen۰CompressedFile`, `vfsgen۰DirInfo`, and `vfsgen۰Dir`, each implementing pieces of `http.File` and `os.FileInfo`.

## Control Flow

`tzdata.Open` cleans the requested path, looks up the generated map entry, and returns either a directory wrapper or a gzip reader over the compressed timezone payload. `sharefile.NewFs` opens `America/New_York`, reads its decompressed bytes, and passes them to `time.LoadLocationFromTZData`. File reads lazily reset or fast-forward the gzip reader to satisfy `Seek` calls.

## State and Persistence Behavior

All data is compiled into the binary. Open file handles keep reader position only; no filesystem writes or external zoneinfo reads occur. Directory handles track an in-memory `pos` for `Readdir`.

## Dependencies and Integration Points

It depends on `compress/gzip`, `net/http`, `os`, and `time`. It is generated by `vfsgen` through `update-timezone.sh` and consumed only by the ShareFile backend's timestamp workaround.

## Risks and Edge Cases

The embedded timezone can become stale if New York DST rules change and the generator is not rerun. The generated identifiers contain non-ASCII characters, so tooling must preserve the file exactly. Corrupt compressed bytes would panic at open time, though they are generated constants.

## Test Signals

Useful signals are successful backend initialization on hosts without system zoneinfo, correct ShareFile `SetModTime` behavior across DST boundaries, and a generator diff after running `update-timezone.sh` with current Go zoneinfo.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sharefile/tzdata_vfsdata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sharefile/update-timezone.sh -->
# sources/user-network-fs/rclone/backend/sharefile/update-timezone.sh

## Purpose

This helper regenerates the embedded ShareFile timezone data used by `tzdata_vfsdata.go`. It extracts only `America/New_York` from Go's bundled zoneinfo and runs the backend generator.

## Important APIs, Types, and Functions

The script uses `go env GOROOT` to locate `lib/time/zoneinfo.zip`, `unzip` to extract `America/New_York`, `go run generate_tzdata.go` to create the generated Go asset file, and `rm -rf tzdata` for cleanup.

## Control Flow

With `set -e`, any failed command aborts. The script removes any prior temporary `tzdata` directory, recreates it, extracts one timezone file, returns to the backend directory, runs the Go generator, and removes the temporary tree.

## State and Persistence Behavior

It writes a temporary `tzdata/` directory and updates generated source through `generate_tzdata.go`. It does not edit rclone config or runtime state.

## Dependencies and Integration Points

It is referenced by `//go:generate ./update-timezone.sh` in `sharefile.go`. It depends on a Go toolchain, the Go distribution's zoneinfo archive, `unzip`, and the local generator source.

## Risks and Edge Cases

`rm -rf tzdata` is destructive relative to the backend directory and assumes that name is only temporary. Missing `unzip`, a stripped Go installation without zoneinfo, or generator failure leaves no updated embedded asset. It embeds Go's timezone snapshot, not necessarily the host OS snapshot.

## Test Signals

Run through `go generate` in the package and verify `tzdata_vfsdata.go` compiles. Behavioral confirmation comes from ShareFile modtime tests around Eastern time and DST transitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sharefile/update-timezone.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sharefile/upload.go -->
# sources/user-network-fs/rclone/backend/sharefile/upload.go

## Purpose

`upload.go` implements ShareFile large-file uploads for the main backend. It handles chunk calculation, buffering, per-chunk MD5, streamed versus threaded upload methods, finalization, and cleanup of upload responses.

## Important APIs, Types, and Functions

`largeUpload` stores upload context, parent `Fs`, target `Object`, source reader, accounting wrapper, total size, part count, ShareFile upload specification, thread count, and method mode. `newLargeUpload` validates the API method and prepares accounting. `transferChunk` posts one chunk to `ChunkURI` with index, offset, chunk hash, and final file hash when finishing. `finish` posts `FinishURI` for threaded uploads. `Upload` reads fixed-size buffers from the `Fs` token pool, hashes the whole file, dispatches chunks, collects errors, and finalizes. `parseUploadFinishResponse` validates ShareFile's completion payload through `Object.checkUploadResponse`.

## Control Flow

For known-size inputs, part count is computed from `ChunkSize`; unknown size uses streaming semantics. `Upload` loops until EOF, checks asynchronous error state, obtains a reusable buffer, fills it with `readers.ReadFill`, updates the whole-file MD5, and sends the chunk inline for streamed mode or in a goroutine for threaded mode. The final chunk adds `finish=true`, `fileSize`, and `fileHash`. After all workers finish, the code checks expected size, drains any worker error, and calls `finish` regardless of earlier errors.

## State and Persistence Behavior

Upload state is in memory. Buffers are borrowed from `Fs.bufferTokens` and must be returned at full configured capacity. ShareFile-side temporary upload state persists until the remote API finishes or abandons it.

## Dependencies and Integration Points

It depends on ShareFile API upload specification/finish types, rclone accounting wrappers, `readers.ReadFill`, the backend pacer/rest client, and object metadata validation in `sharefile.go`.

## Risks and Edge Cases

The `threads` field is computed but not directly used to bound goroutines here; actual concurrency is bounded by the buffer-token pool. The size error message appears to reverse expected/read values. Retrying all chunk errors after upload start can duplicate chunk posts depending on ShareFile idempotency. `finish` runs even after chunk errors, which may produce secondary errors or remote partial state.

## Test Signals

Integration chunked upload tests should cover known and unknown sizes, non-power-of-two final chunks, streamed and threaded server methods, remote MD5 validation, short reads, and failures that should cleanly report rather than corrupting the object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sharefile/upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sia/api/types.go -->
# sources/user-network-fs/rclone/backend/sia/api/types.go

## Purpose

This file defines Go structures matching the Sia daemon renter API JSON responses used by the rclone Sia backend.

## Important APIs, Types, and Functions

`DirectoriesResponse` contains directory and file slices for `/renter/dir`. `FilesResponse` and `FileResponse` wrap file metadata for list and stat endpoints. `FileInfo` mirrors Sia file fields such as access/change/create/mod times, filesize, health, redundancy, upload progress, `SiaPath`, and availability flags. `DirectoryInfo` mirrors aggregate and direct directory health, size, redundancy, file/subdirectory counts, and `SiaPath`. `Error` stores message, HTTP status text, and status code, and implements `Error()`.

## Control Flow

The backend's REST client unmarshals JSON into these types. `Error.Error` joins non-empty message and status fields, or returns a default string when both are blank.

## State and Persistence Behavior

These are transient DTOs with no persistence. Time fields are decoded into `time.Time` by Go's JSON machinery.

## Dependencies and Integration Points

The file depends only on `strings` and `time`. It is consumed by `sia.go` for listing, object metadata reads, and error handling.

## Risks and Edge Cases

The structs rely on Sia API field names staying stable. Many numeric fields are unsigned in the API but converted to signed sizes in the backend, so unexpectedly huge values could overflow when cast. `Error.Error` omits `StatusCode`, so logs may need extra wrapping for numeric diagnostics.

## Test Signals

Tests should unmarshal representative Sia daemon responses, including missing fields and error bodies, and verify `sia.go` maps file-not-found and directory-not-found messages to rclone sentinel errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sia/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sia/sia.go -->
# sources/user-network-fs/rclone/backend/sia/sia.go

## Purpose

`sia.go` implements rclone support for Sia decentralized cloud storage via a local or remote `siad` HTTP API.

## Important APIs, Types, and Functions

`Options` stores API URL, API password, user agent, and path encoder. `Fs` owns remote identity, root prefix, REST client, feature set, and pacer. `Object` stores remote path, modtime, and size. Major methods include `NewFs`, `List`, `NewObject`, `Put`, `PutStream`, `Mkdir`, `Rmdir`, object `Open`, `Update`, `Remove`, `readMetaData`, `errorHandler`, and `shouldRetry`.

## Control Flow

Initialization trims and parses `api_url`, configures an HTTP client with the Sia user agent, installs basic auth when `api_password` is present, and detects root-as-file when the root does not end with `/`. Reads use `/renter/stream/<path>` with rclone range options. Writes use `/renter/uploadstream/<path>?force=true`, then refresh metadata. Listing calls `/renter/dir/<prefix>/`, skips the directory itself, and converts returned directories/files to rclone entries. `Rmdir` first lists the target to confirm existence and emptiness, then posts `action=delete`.

## State and Persistence Behavior

The backend keeps only in-memory metadata and connection state. Persistence is on the Sia daemon side: uploaded streams become renter files, directory creation/deletion uses Sia renter state, and config may contain an obscured API password.

## Dependencies and Integration Points

It integrates rclone `fs`, `fshttp`, `rest`, `pacer`, `encoder`, and `obscure` with Sia renter endpoints. It exposes empty-directory support and streaming uploads, but no hashes and no settable modtime.

## Risks and Edge Cases

`errorHandler` relies on string matching because Sia errors are not structured with stable codes. `shouldRetry` only checks generic errors, not HTTP status retry codes. `Put` performs best-effort cleanup after failed upload with fixed retries. Empty-file range reads drop a problematic range option. The API security note warns that exposing siad remotely with disabled API security is unsafe.

## Test Signals

`sia_test.go` runs rclone's integration suite against `TestSia:`. Additional useful tests would mock Sia error messages, root-as-file detection, failed-upload cleanup, empty-file ranged opens, and empty/non-empty directory removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sia/sia.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sia/sia_test.go -->
# sources/user-network-fs/rclone/backend/sia/sia_test.go

## Purpose

This file connects the Sia backend to rclone's generic integration tests.

## Important APIs, Types, and Functions

`TestIntegration` invokes `fstests.Run` with `RemoteName: "TestSia:"` and `NilObject: (*sia.Object)(nil)`.

## Control Flow

The generic test suite constructs the configured `TestSia:` remote and exercises standard filesystem operations: listing, object creation, streaming, reads, updates, deletion, and directory behavior. There are no local setup helpers in this file.

## State and Persistence Behavior

The test file has no state. Test data persists only in the configured Sia daemon/renter environment for the duration of the integration suite and is cleaned up by `fstests`.

## Dependencies and Integration Points

It imports the backend as an external package (`sia_test`), which tests the public package boundary. It depends on `fstests` and an operational Sia daemon remote.

## Risks and Edge Cases

Coverage is broad but live-remote dependent. It does not directly unit-test Sia error string translation, API password handling, user-agent configuration, or failure cleanup paths.

## Test Signals

Passing integration tests signal the backend satisfies rclone's standard object and directory contract. Failures around modtime expectations should account for `fs.ModTimeNotSupported`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sia/sia_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/smb/connpool.go -->
# sources/user-network-fs/rclone/backend/smb/connpool.go

## Purpose

`connpool.go` manages SMB TCP sessions and mounted shares for the SMB backend. It amortizes authentication and share mounting across operations and drains idle connections safely.

## Important APIs, Types, and Functions

`conn` wraps a network connection pointer, `go-smb2` session, mounted share, and share name. `Fs.dial` creates NTLM or Kerberos initiators and establishes an SMB session. `newConnection` dials and optionally mounts a share. `conn.mountShare` switches mounted shares. `getConnection` retrieves or opens a connection. `putConnection` returns a connection to the pool or closes it if unhealthy. `drainPool` closes pooled connections when no active sessions remain. `addSession`, `removeSession`, and `getSessions` track active readers/writers.

## Control Flow

Operations call `getConnection` with a share name. The pool is searched under lock; each candidate is remounted to the requested share and discarded if remount fails. If none is usable, a new connection is opened through the pacer. On return, `putConnection` probes the session with `Echo` after non-routine errors and only pools healthy sessions. The idle timer nudges `drainPool`, which refuses to close idle connections while active sessions exist and otherwise closes pooled sessions in an `errgroup`.

## State and Persistence Behavior

State is in-memory only: `Fs.pool`, `poolMu`, active session count, mounted share per connection, and idle timer. Credentials come from config and Kerberos caches but are not persisted here.

## Dependencies and Integration Points

It depends on `cloudsoda/go-smb2`, rclone accounting TPS limiting, `fshttp` dialers, obscure password reveal, and `kerberos.go` when Kerberos is enabled. `smb.go` object/list/write methods use this pool for all server I/O.

## Risks and Edge Cases

Connections are remounted between shares, so concurrent use must be prevented by correct borrow/return discipline. Routine filesystem errors skip echo probing; other errors can evict a valid but transiently failing session. `drainPool` avoids closing while sessions are active, but leaked session counts would keep the pool alive. Kerberos creates a new factory per dial, limiting cache reuse across connections.

## Test Signals

Signals include repeated operations reusing sessions, idle timeout closing unused sessions, failures closing unhealthy connections, active reads preventing drain, Kerberos and NTLM authentication working, and no races under parallel list/read/write workloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/smb/connpool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/smb/filepool.go -->
# sources/user-network-fs/rclone/backend/smb/filepool.go

## Purpose

`filepool.go` supports SMB random-access writes by pooling open write handles to one target file. It is used by `OpenWriterAt` for concurrent `WriteAt` calls.

## Important APIs, Types, and Functions

`FsInterface` abstracts the subset of `Fs` needed by the pool. `file` couples an `*smb2.File` with its owning `conn`. `filePool` stores context, backend interface, share, path, mutex, and pooled handles. `newFilePool` constructs the pool. `get` returns an existing handle or opens one through a borrowed connection. `put` returns a healthy handle to the pool or closes/returns its connection with an error. `drain` closes all pooled handles concurrently and returns their connections.

## Control Flow

`smbWriterAt.WriteAt` asks the pool for a file handle, writes at an offset, and returns the handle with the write error. On an empty pool, `get` borrows a connection for the target share and opens the path write-only. On close, `smbWriterAt.Close` waits for writes, drains the file pool, and decrements the SMB session count.

## State and Persistence Behavior

The pool owns open file handles and their associated borrowed connections until drained or discarded. It has no persistent state; remote persistence is the target SMB file contents.

## Dependencies and Integration Points

It depends on `go-smb2` file handles and `errgroup`. `smb.go` uses it exclusively through `smbWriterAt` returned by `OpenWriterAt`.

## Risks and Edge Cases

A write error closes only that handle and probes/returns its connection through `putConnection`; other pooled handles may still exist. `drain` closes pooled idle handles but not handles currently checked out; `smbWriterAt.Close` coordinates this by waiting for its `WaitGroup`. Mock tests use zero-value `smb2.File`, so they do not validate real close errors.

## Test Signals

`filepool_test.go` covers construction, reuse, empty-pool error propagation, error discard, nil puts, drain, and concurrent get/put consistency. Integration signal comes from parallel multipart or VFS random writes through SMB.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/smb/filepool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/smb/filepool_test.go -->
# sources/user-network-fs/rclone/backend/smb/filepool_test.go

## Purpose

This file unit-tests the SMB `filePool` helper with a mocked backend interface.

## Important APIs, Types, and Functions

`mockFs` implements `FsInterface` and records whether `getConnection`, `putConnection`, and `removeSession` were called. `newMockFile` returns a `file` with zero-value SMB objects. Tests cover `newFilePool`, `filePool.get`, `filePool.put`, `filePool.drain`, and concurrent access.

## Control Flow

Tests seed the pool directly or configure mock errors, then call pool methods and assert internal state or mock call records. `TestFilePool_ConcurrentAccess` preloads ten files, runs ten goroutines that get and put handles, waits on a channel, and asserts the pool length returns to ten.

## State and Persistence Behavior

All state is local test memory. There are no network calls because the mock either returns an error or a dummy `conn`.

## Dependencies and Integration Points

It uses `testify/assert`, `context`, `sync`, and `go-smb2` types. It tests `filepool.go` in package `smb`, so it can access unexported types.

## Risks and Edge Cases

The tests do not exercise successful empty-pool opens because that would require a real `smbShare`. `drain` ignores possible close behavior of real SMB files. Assertions mostly validate pool bookkeeping rather than actual SMB semantics.

## Test Signals

Passing tests signal mutex-protected pool bookkeeping and error routing are stable. Race-detector runs are useful for the concurrent test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/smb/filepool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/smb/kerberos.go -->
# sources/user-network-fs/rclone/backend/smb/kerberos.go

## Purpose

`kerberos.go` provides Kerberos client construction and cache handling for SMB authentication.

## Important APIs, Types, and Functions

`KerberosFactory` stores `sync.Map` caches for clients, errors, and ccache mtimes plus injectable loaders for credential caches, clients, and krb5 config. `NewKerberosFactory` wires default gokrb5 functions. `GetClient` resolves a ccache path, stats it, reuses cached client/error when mtime is unchanged, otherwise reloads config and credentials and creates a new client. `resolveCcachePath` handles explicit paths, `KRB5CCNAME`, `FILE:` and `DIR:` schemes, and `/tmp/krb5cc_<uid>` fallback. `defaultLoadKerberosConfig` loads `KRB5_CONFIG` or `/etc/krb5.conf`.

## Control Flow

SMB dialing calls `NewKerberosFactory().GetClient`. Path resolution happens first. If the ccache file mtime matches cached state, cached error or client is returned. Otherwise the factory loads krb5 config, loads the ccache, creates a gokrb5 client, updates caches, and clears stale errors.

## State and Persistence Behavior

Factory state is in-memory cache. Persistent inputs are ccache files, `DIR:` primary files, and krb5 config files. This file never writes credentials.

## Dependencies and Integration Points

It depends on `jcmturner/gokrb5/v8` client/config/credentials packages and OS user/env/path helpers. `connpool.go` integrates the returned client into `smb2.Krb5Initiator`.

## Risks and Edge Cases

Because `connpool.go` creates a new factory for each dial, these caches may not persist across dials unless reused elsewhere. `DIR:` mode depends on a readable `primary` file. Unsupported ccache schemes fail. Cached errors persist until ccache mtime changes, so config-only fixes may not be retried if mtime is unchanged.

## Test Signals

`kerberos_test.go` validates path resolution and reload-on-mtime-change with injected loaders. Integration tests cover Kerberos SMB remotes using default and custom ccache locations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/smb/kerberos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/smb/kerberos_test.go -->
# sources/user-network-fs/rclone/backend/smb/kerberos_test.go

## Purpose

This file unit-tests SMB Kerberos credential cache path resolution and reload behavior.

## Important APIs, Types, and Functions

`TestResolveCcachePath` covers `FILE:` and `DIR:` environment forms, unsupported schemes, direct paths, and default `/tmp/krb5cc_<uid>` fallback. `TestKerberosFactory_GetClient_ReloadOnCcacheChange` creates a temporary ccache and injects mock `loadCCache`, `newClient`, and `loadConfig` functions into a `KerberosFactory`.

## Control Flow

Each path-resolution subtest sets `KRB5CCNAME`, calls `resolveCcachePath`, and checks the result or expected error. The reload test calls `GetClient` twice without file changes to confirm cache reuse, then modifies the ccache after a sleep to force mtime change and confirms the loader is called again.

## State and Persistence Behavior

Tests write temporary files/directories and environment variables scoped by `testing.T`. Factory caches live only for the test instance.

## Dependencies and Integration Points

It uses gokrb5 types only as mock return values, plus `testify/assert`. It directly tests unexported package helpers because it is in package `smb`.

## Risks and Edge Cases

The mtime test sleeps one second to avoid filesystem timestamp granularity issues, which can slow the suite and still depends on platform behavior. It does not validate real Kerberos config parsing or ticket usability.

## Test Signals

Passing tests indicate cache invalidation and ccache URI parsing behave as expected. Additional useful cases would cover cached-error reuse and `KRB5_CONFIG` selection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/smb/kerberos_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/smb/smb.go -->
# sources/user-network-fs/rclone/backend/smb/smb.go

## Purpose

`smb.go` implements the rclone SMB/CIFS backend. It maps rclone filesystem operations onto `go-smb2` share, file, directory, quota, and rename APIs.

## Important APIs, Types, and Functions

`Options` covers host, port, user/password/domain/SPN, Kerberos settings, special-share hiding, case sensitivity, idle timeout, and encoding. `Fs` stores backend state plus connection pool/session tracking. `Object` wraps remote path and `os.FileInfo`. Core methods include `NewFs`, `List`, `NewObject`, `Mkdir`, `Rmdir`, `Put`, `PutStream`, `Move`, `DirMove`, `About`, `OpenWriterAt`, `Shutdown`, `ensureDirectory`, path conversion helpers, and object `Open`, `Update`, `SetModTime`, `Remove`.

## Control Flow

Initialization parses config, sets feature flags including bucket/share semantics and partial uploads, starts an idle drain timer, and checks whether a non-directory root is a file. Paths are split into share and in-share path with `bucket.Split`. Listing at server root enumerates share names and hides `$` shares when configured; listing inside a share reads directory entries. Upload creates parents, opens/truncates the SMB file, streams data, closes it, and sets modtime. Reads borrow a connection, open the file, seek for range/seek options, and return a `boundReadCloser` that returns the connection on close. Server-side move/dir move require source and destination on the same share. `OpenWriterAt` pre-creates/truncates the file and returns a pooled random-access writer.

## State and Persistence Behavior

In-memory state includes connection pool, idle timer, active session count, and cached object stat info. Persistent effects occur on the SMB server: file contents, directories, renames, deletes, and timestamps.

## Dependencies and Integration Points

It depends on rclone `fs`, `bucket`, `encoder`, `pacer`, `readers`, and helper files `connpool.go`, `filepool.go`, and `kerberos.go`. It implements rclone optional interfaces for streaming uploads, mover, dir mover, usage, shutdown, and writer-at support.

## Risks and Edge Cases

The file contains duplicated unreachable returns in `String`. `DirMove` stats `dstPath` without converting to Samba path, unlike most operations. Root/share boundary cases return `fs.ErrorIsDir` or no-op directory operations. Active-session accounting must stay balanced to avoid premature or blocked drains. Mandatory unsupported open options are logged but not rejected in `Open`.

## Test Signals

Integration tests cover NTLM and Kerberos remotes. Unit tests cover `isPathDir`; filepool and kerberos helpers have separate unit tests. Strong signals include parallel reads/writes, random-access writer correctness, same-share move restrictions, share-root listing, special-share hiding, and timestamp preservation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/smb/smb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/smb/smb_internal_test.go -->
# sources/user-network-fs/rclone/backend/smb/smb_internal_test.go

## Purpose

This file unit-tests a small internal path helper used by SMB root detection.

## Important APIs, Types, and Functions

`TestIsPathDir` exercises `isPathDir`, which treats an empty path or any path ending in `/` as a directory and all other paths as potentially file-like.

## Control Flow

A table of paths is iterated with subtests. Each subtest calls `isPathDir` and reports a mismatch with `t.Errorf`.

## State and Persistence Behavior

No state or filesystem access is used.

## Dependencies and Integration Points

The test is in package `smb`, so it can access unexported `isPathDir`. `NewFs` uses this helper to skip file-root stat checks for explicit directory roots.

## Risks and Edge Cases

The helper is intentionally syntactic; it does not normalize before checking. Multiple trailing slashes are considered directory indicators. This test does not cover `betterPathClean` or `trimPathPrefix`.

## Test Signals

Passing tests protect the root-path distinction that controls whether `NewFs` probes for a file versus accepting a directory root.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/smb/smb_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/smb/smb_test.go -->
# sources/user-network-fs/rclone/backend/smb/smb_test.go

## Purpose

This file runs rclone's generic integration tests against SMB remotes, including NTLM and Kerberos configurations.

## Important APIs, Types, and Functions

`TestIntegration` uses `TestSMB:rclone`. `TestIntegration2` uses `TestSMBKerberos:rclone` with temporary `KRB5_CONFIG` and `KRB5CCNAME`. `TestIntegration3` uses `TestSMBKerberosCcache:rclone` and injects an extra `kerberos_ccache` config value. All pass `NilObject: (*smb.Object)(nil)`.

## Control Flow

Each test calls `fstests.Run`. Kerberos tests skip when `-remote` is supplied, then set temp env/config paths before invoking the suite. The third test also sets `RCLONE_TEST_CUSTOM_CCACHE_LOCATION`.

## State and Persistence Behavior

State is confined to temporary directories and environment variables plus the configured remote test shares. The integration suite creates and removes remote test data.

## Dependencies and Integration Points

It depends on `fstest` and `fstests`, plus external SMB test remotes. It validates the public backend package from `smb_test`.

## Risks and Edge Cases

These tests require external SMB infrastructure and valid Kerberos setup. They do not directly unit-test connection pooling, idle drain, or writer-at behavior, though generic operations exercise them indirectly.

## Test Signals

Passing tests indicate the backend works with normal credentials, default Kerberos ccache discovery, and custom ccache configuration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/smb/smb_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/storj/fs.go -->
# sources/user-network-fs/rclone/backend/storj/fs.go

## Purpose

`fs.go` implements rclone's Storj backend on top of `storj.io/uplink`. It handles access-grant configuration, bucket/object listing, uploads, bucket creation/removal, server-side move/copy, purge, and public links.

## Important APIs, Types, and Functions

`Options` stores access grant and optional satellite/API-key/passphrase inputs. `Fs` stores name, root, options, feature flags, parsed `uplink.Access`, and open `uplink.Project`. Key functions include registration config logic, `NewFs`, `connect`, `absolute`, `List`, `ListR`, `NewObject`, `Put`, internal `put`, `Mkdir`, `Rmdir`, `Move`, `Copy`, `Purge`, `PublicLink`, and `newPrefix`.

## Control Flow

Config can use an existing access grant or create one from satellite/API key/passphrase, saving the serialized grant. `NewFs` normalizes root to NFC, parses or requests access, opens a project, and validates file-root cases. Listings operate at project root by listing buckets, or inside a bucket by listing objects with a prefix; recursive listing sets `Recursive: true`. Uploads call `UploadObject`, set custom metadata `rclone:mtime`, copy the input, and commit. If bucket-not-found occurs during upload/commit, the bucket is ensured and a retry error is returned. Move/copy retry after ensuring destination bucket. Public links create a shared read-only access and register it through Storj Edge.

## State and Persistence Behavior

Runtime state is the open project and access. Persistent config may be updated with a serialized access grant. Remote state includes buckets, objects, custom metadata, and public edge credentials.

## Dependencies and Integration Points

It depends on rclone `bucket`, `config`, `fserrors`, Unicode normalization, `storj.io/uplink`, and `storj.io/uplink/edge`. It implements list recursive, put stream, move, copy, purge, and public link optional interfaces.

## Risks and Edge Cases

The file contains a duplicated unreachable `return f, fs.ErrorIsFile`. Bucket creation during upload intentionally returns a retry error, so callers must retry. Storj rate-limits repeated writes to the same key; commit maps `ErrTooManyRequests` to a retry after sleeping one second. Hashes are unsupported. Prefix-directory semantics are inferred from object listings, so empty subdirectories are not preserved below buckets.

## Test Signals

`storj_test.go` runs generic integration tests. Additional signals include access-grant creation and saving, root-as-file handling, bucket creation on first upload, recursive listing, server-side move/copy across buckets, purge behavior, and public link generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/storj/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/storj/object.go -->
# sources/user-network-fs/rclone/backend/storj/object.go

## Purpose

`object.go` implements rclone object behavior for Storj objects, including remote path derivation, metadata-backed modtime, range reads, updates, and deletion.

## Important APIs, Types, and Functions

`Object` stores parent `Fs`, absolute `bucket/key`, size, created time, and modified time. `newObjectFromUplink` translates `uplink.Object` metadata into an `Object`, preferring custom `rclone:mtime` over server created time. Methods implement `fs.Object`: `String`, `Remote`, `ModTime`, `Size`, `Fs`, `Hash`, `Storable`, `SetModTime`, `Open`, `Update`, and `Remove`.

## Control Flow

Object creation computes the absolute path by combining filesystem root and relative path, normalizing to NFC. `Remote` returns the full absolute path when the `Fs` root is empty, otherwise trims the root prefix and slash. `Open` converts rclone `RangeOption` or `SeekOption` into uplink `DownloadOptions` offset and length, rejecting unsupported mandatory options. `Update` delegates to `Fs.put` for the same remote path and replaces the receiver with the returned object on success. `Remove` splits `absolute` into bucket/key and calls `DeleteObject`.

## State and Persistence Behavior

Object metadata is cached in the struct. Remote persistence is handled by Storj object storage. `SetModTime` is unsupported after upload; modtime is stored at upload time as custom metadata.

## Dependencies and Integration Points

It depends on rclone `fs`, `hash`, `bucket`, Unicode normalization, and `uplink`. It is tightly coupled to `fs.go` for project access and upload/update behavior.

## Risks and Edge Cases

Suffix range handling uses negative offsets for `RangeOption` with only an end value, matching uplink semantics but requiring careful interpretation. Hashes and post-upload modtime changes are unsupported. Corrupt `rclone:mtime` metadata falls back silently to created time.

## Test Signals

Integration tests should cover range and seek reads, update replacing receiver metadata, delete behavior, root-relative path calculation for project-root and bucket-root remotes, and modtime round-tripping through custom metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/storj/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/storj/storj_test.go -->
# sources/user-network-fs/rclone/backend/storj/storj_test.go

## Purpose

This file connects the Storj backend to rclone's generic integration test suite on non-Plan 9 platforms.

## Important APIs, Types, and Functions

`TestIntegration` runs `fstests.Run` with `RemoteName: "TestStorj:"` and `NilObject: (*storj.Object)(nil)`.

## Control Flow

The generic suite builds the configured Storj remote and exercises standard rclone operations. Build tag `!plan9` matches the backend implementation files.

## State and Persistence Behavior

There is no local state beyond test execution. Remote buckets/objects are created and cleaned by the generic suite.

## Dependencies and Integration Points

It imports `backend/storj` externally as `storj_test` and depends on `fstests`. It requires a configured Storj test access grant.

## Risks and Edge Cases

Live Storj credentials and network are required. The generic suite may not cover public links or all bucket-creation retry behavior.

## Test Signals

Passing tests indicate core list, upload, read, update, delete, and directory behavior satisfy rclone contracts for Storj.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/storj/storj_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/storj/storj_unsupported.go -->
# sources/user-network-fs/rclone/backend/storj/storj_unsupported.go

## Purpose

This build-tagged file provides an empty `storj` package on Plan 9, where the main Storj backend is not built.

## Important APIs, Types, and Functions

There are no exported APIs or functions. The file contains only `//go:build plan9` and the package declaration.

## Control Flow

On Plan 9 builds, this file satisfies package existence while excluding `fs.go`, `object.go`, and tests guarded by `!plan9`.

## State and Persistence Behavior

No state or persistence exists.

## Dependencies and Integration Points

It integrates with Go build constraints to avoid compiling unsupported Storj/uplink code on Plan 9.

## Risks and Edge Cases

The backend is unavailable on Plan 9. Any code expecting registered `storj` support on that platform will not find it.

## Test Signals

A Plan 9 package build should succeed without registering the backend. Non-Plan 9 builds should ignore this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/storj/storj_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sugarsync/api/types.go -->
# sources/user-network-fs/rclone/backend/sugarsync/api/types.go

## Purpose

This file defines XML request and response structures for the SugarSync REST API used by the rclone backend.

## Important APIs, Types, and Functions

Authentication types include `AppAuthorization`, `TokenAuthRequest`, and `Authorization`. Storage resource types include `File`, `Collection`, `CollectionContents`, and `User`. Mutation payloads include `CreateFolder`, `MoveFolder`, `CreateSyncFolder`, `CreateFile`, `MoveFile`, `CopyFile`, `PublicLink`, `SetPublicLink`, and `SetLastModified`.

## Control Flow

The backend marshals these structs to XML for auth, folder/file creation, moves, copies, public-link toggles, and metadata updates. It unmarshals API XML into file, collection, collection-contents, user, and auth response structs.

## State and Persistence Behavior

The types are transient DTOs. Fields such as refs, parent links, file data URLs, public links, quota, and deleted-folder links represent remote SugarSync state but are not persisted locally by this file.

## Dependencies and Integration Points

It depends on `encoding/xml` and `time`. `sugarsync.go` uses the types for all SugarSync XML calls through rclone's `rest.Client`.

## Risks and Edge Cases

The structs rely on SugarSync XML names and nested shapes staying stable. Some fields are URLs or resource refs rather than simple IDs, so callers must pass them back exactly. `Collection.Type` is an attribute and root sync folders require API-version quirks handled in `sugarsync.go`.

## Test Signals

Useful tests marshal/unmarshal representative XML from SugarSync, including public-link and quota responses, and verify backend methods build expected XML for create, move, copy, and authorization requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sugarsync/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sugarsync/sugarsync.go -->
# sources/user-network-fs/rclone/backend/sugarsync/sugarsync.go

## Purpose

`sugarsync.go` implements the rclone backend for SugarSync's XML API. It handles interactive refresh-token setup, authorization renewal, directory caching, file and folder operations, copy/move, soft/hard delete, and public links.

## Important APIs, Types, and Functions

`Options` stores app credentials, delete mode, refresh/authorization tokens, cached user/root/deleted IDs, and encoding. `Fs` owns REST client, pacer, config mapper, auth mutex/expiry, and `dircache`. `Object` stores metadata, ID, size, and modtime. Key functions include `withDefault`, registration `Config`, `getAuthToken`, `getAuth`, `getUser`, `NewFs`, `errorHandler`, `FindLeaf`, `CreateDir`, `listAll`, `List`, `Put`, `PutUnchecked`, `delete`, `purgeCheck`, `Copy`, `Purge`, `moveFile`, `moveDir`, `Move`, `DirMove`, `PublicLink`, object metadata/read/update/remove, and `ID`.

## Control Flow

Config prompts for username/password only to obtain a refresh token. Runtime auth uses a REST signer: before each request, `getAuth` refreshes authorization if missing or near expiry, caches auth URL/expiry/user back into config, and sets the `Authorization` header. `NewFs` discovers and caches root/deleted IDs from `/user`, initializes dircache, and handles root-as-file. Listing pages through `/contents` with `max=500`. Upload creates an empty file resource if needed, then PUTs `/data`; if a newly created upload fails, it deletes or moves the partial file according to delete mode. Soft delete moves resources to the deleted folder; hard delete issues DELETE.

## State and Persistence Behavior

Persistent config can be updated with refresh token, authorization URL, authorization expiry, user URL, root ID, and deleted ID. Runtime state includes auth mutex, auth expiry, directory cache, object metadata, and pacer. Remote state includes files, folders, sync folders, deleted folder entries, public-link flags, and file data.

## Dependencies and Integration Points

It depends on SugarSync XML DTOs, rclone config/fs/http/rest/pacer/dircache/operations helpers, obscure credentials, and encoder. It implements purge, streaming upload, copy, move, dir move, dir-cache flush, public link, and ID interfaces.

## Risks and Edge Cases

The API returns HTML error bodies, parsed by regex for `<h3>`. Modtime setting is unsupported. Root sync-folder creation needs a non-canonical `*X-SugarSync-API-Version` header and may not return a location, requiring lookup. Hard-delete purge is disabled because deleting folders can orphan contents. Case-insensitive paths can make same-name copy unsafe. Auth refresh writes config during operations.

## Test Signals

Integration uses `TestSugarSync:Test` because root sync-folder moves can fail. Unit tests cover HTML error parsing. Strong signals include token renewal, paginated listing, upload cleanup, soft versus hard delete, copy overwrite cleanup, public links, and dircache correctness after moves/deletes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sugarsync/sugarsync.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sugarsync/sugarsync_internal_test.go -->
# sources/user-network-fs/rclone/backend/sugarsync/sugarsync_internal_test.go

## Purpose

This file unit-tests SugarSync's HTML error parser.

## Important APIs, Types, and Functions

`TestErrorHandler` builds synthetic `http.Response` values with different bodies and checks `errorHandler` output strings.

## Control Flow

Each subtest creates a response body from a string, status code, and status text, then calls `errorHandler`. Cases cover empty body, unknown HTML, blank `<h3>`, and a real-looking `<h3>Can not move sync folder.</h3>` body.

## State and Persistence Behavior

No persistent state is used. Each response body is an in-memory `io.NopCloser`.

## Dependencies and Integration Points

It depends on `testify/assert`, `bytes`, `io`, and `net/http`. It tests the unexported parser in package `sugarsync`.

## Risks and Edge Cases

The parser only extracts the first non-empty `<h3>` content and does not decode HTML entities. Tests assert exact error strings, so status formatting changes will be caught.

## Test Signals

Passing tests indicate SugarSync API HTML failures produce useful errors instead of opaque raw bodies when an `<h3>` message is present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sugarsync/sugarsync_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sugarsync/sugarsync_test.go -->
# sources/user-network-fs/rclone/backend/sugarsync/sugarsync_test.go

## Purpose

This file runs rclone's generic integration test suite against a SugarSync remote.

## Important APIs, Types, and Functions

`TestIntegration` calls `fstests.Run` with `RemoteName: "TestSugarSync:Test"` and `NilObject: (*sugarsync.Object)(nil)`.

## Control Flow

The generic suite creates the backend from the configured remote and exercises standard file and directory operations. The remote path includes `Test` to avoid known SugarSync limitations around moving root sync folders.

## State and Persistence Behavior

The file has no local state. The integration suite creates and removes remote SugarSync data under the configured test path.

## Dependencies and Integration Points

It imports the backend externally and depends on `fstests` plus valid SugarSync test credentials/tokens.

## Risks and Edge Cases

Live API availability and account state affect results. The generic suite may not fully cover auth refresh, soft-delete recovery semantics, or public-link behavior.

## Test Signals

Passing tests signal conformance to rclone's common backend behavior for SugarSync under the chosen test root.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sugarsync/sugarsync_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/swift/auth.go -->
# sources/user-network-fs/rclone/backend/swift/auth.go

## Purpose

`auth.go` defines a wrapper authenticator for the Swift backend that can override storage URL and auth token while delegating the rest of authentication behavior to an underlying Swift authenticator.

## Important APIs, Types, and Functions

`auth` stores `parentAuth`, `storageURL`, and `authToken`. `newAuth` constructs the wrapper. Methods implement `swift.Authenticator`: `Request`, `Response`, `StorageUrl`, `Token`, and `CdnUrl`. `Expires` implements `swift.Expireser` when the parent supports it.

## Control Flow

If a parent authenticator exists, request/response handling is delegated. `StorageUrl` and `Token` return configured override values when non-empty; otherwise they delegate to the parent or return empty strings. `Expires` type-asserts the parent to `swift.Expireser`.

## State and Persistence Behavior

The wrapper is immutable after construction and stores no persistent state. It preserves fixed token/storage URL overrides across re-authentication.

## Dependencies and Integration Points

It depends on `github.com/ncw/swift/v2`. `swiftConnection` uses it when user-supplied `storage_url` or `auth_token` should override values discovered during `Authenticate`.

## Risks and Edge Cases

If `parentAuth` is nil and no overrides are set, methods return empty values and no auth request is made. Expiry information is unavailable unless the parent provides it. Overrides can intentionally bypass service-catalog values, so stale tokens or URLs are user responsibility.

## Test Signals

Useful tests construct wrappers with nil and mock parents to verify override precedence, delegation, expiry passthrough, and behavior after Swift connection authentication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/swift/auth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/swift/swift.go -->
# sources/user-network-fs/rclone/backend/swift/swift.go

## Purpose

`swift.go` implements rclone's OpenStack Swift backend, including authentication, container/bucket behavior, paginated and recursive listing, uploads, dynamic large object segment handling, server-side copy, purge, metadata modtime, MD5 hashes, quota reporting, and MIME type support.

## Important APIs, Types, and Functions

`SharedOptions` defines chunking, large-object, segment-location, and encoding options. `Options` covers OpenStack auth fields, env auth, storage URL/token overrides, application credentials, storage policy, listing workarounds, and upload behavior. `Fs` stores the Swift connection, root container/directory, bucket cache, pacer, config, and features. `Object` stores remote path, size, last modified, content type, MD5, and headers. Key functions include `swiftConnection`, `NewFsWithConnection`, `NewFs`, `listContainerRoot`, `ListP`, `ListR`, `About`, `makeContainer`, `Purge`, `Copy`, segmented-upload helpers, object metadata/hash/large-object detection, `Open`, `updateChunks`, `Update`, `Remove`, and `urlEncode`.

## Control Flow

Initialization parses options, authenticates or applies environment credentials, wraps storage URL/token overrides, validates chunk size, sets root fields, auto-selects segment storage mode, and detects root-as-file. Listing uses Swift `ObjectsWalk` with delimiter for non-recursive listing and filters hidden `.file-segments` when segments live inside the container. Upload creates the container, sets modtime metadata, then either performs a single `ObjectPut` or uploads segments and writes a DLO manifest. Existing large-object segments are removed after successful replacement unless container versioning is enabled. Copy handles normal objects with `ObjectCopy` and large objects by copying each segment then uploading a manifest. Remove deletes the manifest/object first, then bulk-deletes segments when appropriate.

## State and Persistence Behavior

Runtime state includes connection auth, bucket cache, root split, object headers, and pacer. Persistent remote state includes containers, objects, metadata headers, segment containers or `.file-segments` directory objects, storage policies, and container versioning. Config can source credentials from environment but is not written here.

## Dependencies and Integration Points

It depends on `github.com/ncw/swift/v2`, rclone `fs`, `list`, `operations`, `bucket`, `encoder`, `pacer`, `random`, `readers`, and `atexit`. It implements purge, put stream, copy, recursive and paginated listing, MIME type, and usage interfaces.

## Risks and Edge Cases

Large-object handling is complex: DLO/SLO detection requires HEAD requests unless disabled, and `NoLargeObjects` can make hashes/copy/remove wrong if large objects exist. Segment cleanup is skipped when `leave_parts_on_error` is true or container versioning is enabled. Provider quirks drive automatic segment-location selection. Retry-after handling sleeps for short 429 delays and returns delayed retry errors for long ones. Directory markers must be filtered to avoid duplicate directories.

## Test Signals

Internal tests cover `urlEncode` and retry-after behavior. Integration tests should cover env and explicit auth, listing pagination workarounds, root-as-file, single and segmented uploads, DLO copy/remove cleanup, storage policy on segment containers, purge including directory markers, MD5 behavior, MIME metadata, and versioned containers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/swift/swift.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/swift/swift_internal_test.go -->
# sources/user-network-fs/rclone/backend/swift/swift_internal_test.go

## Purpose

This file unit-tests Swift backend helpers for URL encoding and `Retry-After` handling.

## Important APIs, Types, and Functions

`TestInternalUrlEncode` checks `urlEncode` preserves alphanumerics, `/`, `.`, `_`, and `-`, while percent-encoding spaces, `&`, punctuation, and UTF-8 bytes. `TestInternalShouldRetryHeaders` checks `shouldRetryHeaders` for Swift 429 errors with short and long `Retry-After` values.

## Control Flow

The URL test iterates known input/output pairs. The retry test constructs Swift headers and a `swift.Error{StatusCode: 429}`, verifies a one-second retry-after sleeps and returns `retry=true`, then changes the header to `3600` and verifies it returns a `fserrors.RetryAfter` without sleeping.

## State and Persistence Behavior

No persistent state is used. The short retry test intentionally waits for roughly one second.

## Dependencies and Integration Points

It depends on `github.com/ncw/swift/v2`, rclone `fserrors`, `testify/assert`, and the unexported helpers in `swift.go`.

## Risks and Edge Cases

The URL test logs mismatches but does not call `t.Errorf` or assert, so a mismatch may not fail the test. The sleep-based retry test adds wall-clock cost and may be timing-sensitive.

## Test Signals

Passing retry assertions confirm short retry-after delays are obeyed inline and long delays become scheduler-visible retry-after errors. URL encoding should be strengthened with assertions to protect DLO manifest paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/swift/swift_internal_test.go -->

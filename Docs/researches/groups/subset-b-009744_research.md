# Research: subset-b-009744

Grouped research for rclone backend implementations under FTP, Gofile, Google Cloud Storage, Google Photos, and hasher. Each section is source-tree aligned and bounded by reconciliation markers for per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/ftp/ftp.go -->
# sources/user-network-fs/rclone/backend/ftp/ftp.go

## Purpose
This file implements rclone's FTP/FTPS backend. It registers the `ftp` remote type, parses connection/security/proxy/encoding options, manages a pool of FTP control connections, and exposes the rclone `fs.Fs` and `fs.Object` operations for listing, upload, download, directory management, and server-side rename moves.

## Important APIs, Types, And Control Flow
The main exported types are `Options`, `Fs`, `Object`, and `FileInfo`. `NewFs` reveals the configured password or prompts when allowed, rejects simultaneous implicit and explicit TLS, initializes the connection pacer and optional concurrency token dispenser, dials once to validate credentials and discover FTP feature support, then handles the "root is a file" case by returning `fs.ErrorIsFile`.

Connection control is centered on `ftpConnection`, `getFtpConnection`, `putFtpConnection`, and `drainPool`. `ftpConnection` builds a `jlaffaye/ftp` dialer using rclone's HTTP dialer, optional SOCKS5 or HTTP CONNECT proxy logic, implicit/explicit TLS, EPSV/MLSD/UTF8/hidden-listing toggles, debug logging, and pacer retries. `getFtpConnection` consumes a token when `concurrency` is configured, reuses a pooled connection if possible, or opens a new connection. `putFtpConnection` validates potentially bad connections with `NOOP`, returns healthy connections to the pool, and resets the idle drain timer.

Object and directory operations use FTP commands through pooled connections. `findItem` prefers `MLST`/`GetEntry` when available, falls back to parent `LIST`, and normalizes names through the configured encoder. `List` runs `c.List` in a goroutine with a global timeout guard, then synthesizes rclone `Dir` and `Object` entries. `Put` recursively creates parent directories and calls `Object.Update`; `Update` uses `STOR`, optionally removes a partially uploaded file on failure, sets mtime, and refreshes metadata unless `no_check_upload` is enabled. `Open` supports seek/range reads via `RetrFrom` and wraps the response in `ftpReadCloser`, which returns or discards the connection during `Close`. `Move` and `DirMove` use `RNFR`/`RNTO` via `Rename`.

## State And Persistence
Runtime state is in the `Fs`: root, URL, credentials, TLS base config, connection pool, drain timer, pacer, feature flags, and feature-detection booleans for precise list times and MDTM/MFMT support. Persistent remote state is only FTP server state: directories, files, file mtimes, and renamed paths. The backend does not keep a local database. Pool state is cleaned by idle timeout or `Shutdown`.

## Dependencies And Integration Points
The implementation integrates `github.com/jlaffaye/ftp`, rclone's `fs` interfaces, `fshttp`, `pacer`, `accounting.LimitTPS`, `encoder.MultiEncoder`, proxy helpers, password obscuring, and rclone retry classification. It advertises `fs.Mover`, `fs.DirMover`, `fs.PutStreamer`, and `fs.Shutdowner`; hashes are unsupported.

## Risks And Test Signals
Major risks are FTP server variance: nonstandard MDTM writes, MLSD precision differences, LIST success for missing directories, unusual mkdir status codes, hidden-file listing behavior, TLS session resumption issues, proxy PASV address rewriting, and stuck data/control closes. Upload failure cleanup sleeps before deletion and can be fragile on slow servers. Tests should cover plain FTP, implicit and explicit FTPS, proxy paths, EPSV/MLSD/UTF8 toggles, low concurrency deadlock potential, range reads, close timeouts, directory marker behavior from LIST, and server-specific time precision.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/ftp/ftp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/ftp/ftp_internal_test.go -->
# sources/user-network-fs/rclone/backend/ftp/ftp_internal_test.go

## Purpose
This internal test file adds FTP-specific checks that run through rclone's `fstests.InternalTester` hook against real configured FTP remotes.

## Important APIs, Types, And Control Flow
`deriveFs` builds a derived remote string from the current test remote plus injected config options. `testUploadTimeout` creates a 100 MiB pattern reader and uploads it through a derived backend with controlled `concurrency` and `shut_timeout`, temporarily lowering global low-level retries and the I/O timeout after the initial control connection is established. It fails if upload blocks beyond a hard deadline. `testTimePrecision` normalizes hashed test remote names and asserts ProFTPd, PureFTPd, and VsFTPd precision is at most one second. `InternalTest` dispatches both tests.

## State And Persistence
The tests mutate global `fs.ConfigInfo` retry and timeout settings during execution and restore them with `defer`. They create a large remote test object and remove it afterward when upload succeeds. No local persisted state is created.

## Dependencies And Integration Points
The file depends on `fstests`, `fstest`, `object.NewStaticObjectInfo`, `readers.NewPatternReader`, config maps, and testify assertions. It exercises the production FTP backend through `fs.NewFs`, not by direct mocks.

## Risks And Test Signals
The upload timeout test is intentionally skipped in `testing.Short` because it is large and timing-sensitive. It targets deadlocks or I/O timeouts around data connection shutdown and concurrency tokens. The precision test documents the expected behavior for common FTP daemons and guards regressions in feature detection for `Precision`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/ftp/ftp_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/ftp/ftp_test.go -->
# sources/user-network-fs/rclone/backend/ftp/ftp_test.go

## Purpose
This file wires the FTP backend into rclone's generic filesystem integration test suite for several FTP server profiles.

## Important APIs, Types, And Control Flow
`TestIntegration` runs `fstests.Run` against `TestFTPRclone:`. Additional tests target ProFTPd, PureFTPd, and VsFTPd remotes and skip when the user supplied an explicit `-remote`, avoiding accidental multi-remote test runs. Each run declares `(*ftp.Object)(nil)` as the nil object type expected by the suite.

## State And Persistence
The test suite creates, reads, moves, and deletes objects on the configured FTP test remotes through `fstests`. This file itself has no persistent local state.

## Dependencies And Integration Points
It imports the production FTP package, `fstest`, and `fstests`. Server-specific remote names integrate with rclone's test configuration and the backend's internal test hook.

## Risks And Test Signals
Coverage comes from generic rclone backend behavior across four FTP implementations. It is strong for interoperability and weak for unit-level edge cases such as TLS option combinations or proxy behavior unless those remotes are configured that way.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/ftp/ftp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/gofile/api/types.go -->
# sources/user-network-fs/rclone/backend/gofile/api/types.go

## Purpose
This file defines JSON DTOs and small helpers for the Gofile API used by the backend.

## Important APIs, Types, And Control Flow
`Time` marshals and unmarshals RFC3339 timestamps. `Error` wraps Gofile's string status, implements `error`, and provides `IsError` and `Err` helpers used after REST calls. Core resource models are `Item`, `DirectLink`, `Contents`, `Metadata`, account response types, create/delete/upload/direct-link/update/move/copy request and response types, and `UploadServerStatus`. `ToNativeTime` and `FromNativeTime` convert between Go `time.Time` and Gofile's Unix timestamp values. `DirectUploadURL` returns the upload endpoint.

## State And Persistence
The file has no runtime state. It models API payloads that describe persistent Gofile server state such as folders, files, direct links, account stats, md5 checksums, and item modtimes.

## Dependencies And Integration Points
It depends only on `fmt` and `time`. The backend consumes these types through rclone's `rest.Client` JSON calls and maps `Item` fields into rclone objects/directories.

## Risks And Test Signals
Risks are API schema drift, especially status strings, child pagination metadata, direct-link payload shape, and timestamp format. Tests should decode representative success and error bodies, paged content responses, delete result maps, and upload/direct-link responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/gofile/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/gofile/gofile.go -->
# sources/user-network-fs/rclone/backend/gofile/gofile.go

## Purpose
This file implements rclone's Gofile backend. It registers the `gofile` remote, authenticates with bearer token, discovers and caches account/root folder IDs, maps Gofile folders to rclone directories through a directory cache, and implements listing, upload, update, removal, quota, public links, server-side moves/copies, directory modtimes, and duplicate-support behavior.

## Important APIs, Types, And Control Flow
Key types are `Options`, `Fs`, `Object`, and `Directory`. `NewFs` configures the REST client, sets the Authorization header, reads `account_id` and `root_folder_id` when missing and writes them back through the config mapper, initializes `dircache.DirCache`, and handles the "root is a file" case with a temporary parent `Fs`.

`listAll` is the primitive for paginated `/contents/{id}` listing; it supports directory-only, file-only, and server-side name filtering, decodes remote names through the encoder, and maps `error-notFound` to `fs.ErrorDirNotFound`. `List` lists one directory via `dirCache.FindDir`; `ListR` asks Gofile for recursive listings up to `maxDepth` and recurses manually when the API truncates nested children. `itemToDirEntry` caches folder IDs and constructs either `Directory` or `Object`.

Writes flow through `Put`, `PutUnchecked`, and `Object.Update`. `Put` checks for an existing object and updates it; `PutUnchecked` allows duplicates. `Update` finds or creates the parent folder, clears the old object ID while uploading a replacement, uploads multipart data to `api.DirectUploadURL`, and deletes the old item only after upload success. Directory operations use `CreateDir`, `Mkdir`, `Rmdir`, `Purge`, and `DirSetModTime`.

Server-side transforms use `rename`, `setModTime`, `move`, `moveTo`, `copy`, and `copyTo`. `Move` and `DirMove` adjust paths through dircache and Gofile move calls. `Copy` creates a new duplicate, then removes an existing destination only after the copy succeeds and resets modtime because Gofile copy does not preserve it. `PublicLink` creates or removes direct links for files or directories.

## State And Persistence
Local runtime state includes REST client, pacer, features, and directory cache. Config persistence is explicit: discovered `account_id` and `root_folder_id` are written into the config mapper. Remote persistent state includes Gofile folders/files, item modtimes, direct links, copied/moved items, and deletes. Directory cache entries are invalidated on purge and directory moves.

## Dependencies And Integration Points
The backend uses rclone `rest`, `dircache`, `list.Helper`, `pacer`, `fshttp`, `encoder`, and hash support. It implements many optional interfaces: `Purger`, `PutStreamer`, `PutUncheckeder`, `Copier`, `Abouter`, `Mover`, `DirMover`, `DirCacheFlusher`, `PublicLinker`, `MergeDirser`, `DirSetModTimer`, `ListRer`, `IDer`, `MimeTyper`, `ParentIDer`, and directory `SetModTimer`. It exposes MD5 from Gofile metadata.

## Risks And Test Signals
Risks include API status-string changes, duplicate-file semantics, replacing an existing file by upload-then-delete, stale dircache after direct remote changes, pagination and recursive max-depth behavior, rate-limit sleeps blocking goroutines, direct link cleanup failures, and copy/move response maps missing the source ID. Tests should cover paged listings, duplicate names, update failure preserving the old object, public link create/delete, move/copy into new and existing destinations, quota mapping, and `max_age` of dircache under external changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/gofile/gofile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/gofile/gofile_test.go -->
# sources/user-network-fs/rclone/backend/gofile/gofile_test.go

## Purpose
This file connects the Gofile backend to rclone's generic integration test suite.

## Important APIs, Types, And Control Flow
`TestIntegration` invokes `fstests.Run` with `RemoteName: "TestGoFile:"` and declares the nil object type as `(*gofile.Object)(nil)`.

## State And Persistence
All state is created on the configured Gofile test account by the generic suite. The file itself has no setup beyond selecting the remote.

## Dependencies And Integration Points
It imports the production `gofile` backend and `fstests`. The generic suite exercises object CRUD, listing, moves, hashes, and optional interfaces exposed by `gofile.go`.

## Risks And Test Signals
The test signal depends on a configured live Gofile account and mainly catches end-to-end API regressions. It does not isolate schema parsing or failure paths such as update replacement errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/gofile/gofile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlecloudstorage/googlecloudstorage.go -->
# sources/user-network-fs/rclone/backend/googlecloudstorage/googlecloudstorage.go

## Purpose
This file implements the rclone backend for Google Cloud Storage, not Google Drive. It registers the `gcs` prefixed remote, handles OAuth/service-account/environment/anonymous access, maps rclone paths to GCS buckets and object names, and implements bucket listing/creation/removal, object listing, upload, download, copy, metadata-based mtimes, and optional directory marker objects.

## Important APIs, Types, And Control Flow
The key types are `Options`, `Fs`, and `Object`. `NewFs` fills default ACLs, loads service-account credentials from JSON content or a shell-expanded file, selects authentication mode, initializes a Google Storage service with optional endpoint override, sets feature flags, and checks whether a bucket/path root is actually an object. `setRoot` and `split` manage bucket/path decomposition and encoder translation.

Listing is handled by `list`, `listDir`, `listBuckets`, `ListP`, and `ListR`. `list` wraps `Objects.List`, applies prefixes and delimiters, emits synthetic directories from `Prefixes`, treats trailing slash objects as directory markers, maps not-found to `fs.ErrorDirNotFound`, and checks marker existence for empty directories when `directory_markers` is enabled. `ListP` uses `list.WithListP`; root-level listings require `project_number`.

Writes and bucket lifecycle are handled by `Mkdir`, `mkdirParent`, `makeBucket`, `checkBucket`, `createDirectoryMarker`, `Put`, `PutStream`, and `Object.Update`. Uploads create parent buckets/directories unless writing a marker, attach mime type and mtime metadata, honor selected upload headers, storage class, object ACLs, and requester-pays user project. `Rmdir` removes directory markers or buckets depending on path depth. `Copy` uses GCS rewrite, handling multi-call rewrite tokens.

Object metadata uses `setMetaData`, `readObjectInfo`, `readMetaData`, `metadataFromModTime`, and `SetModTime`. Mtime is read from rclone `mtime`, then gsutil's `goog-reserved-file-mtime`, then GCS `Updated`. `SetModTime` copies the object to itself with updated metadata to avoid requiring PATCH permissions. `Open` downloads via the object's media link, supports range options, requester-pays query parameter, and gzip handling.

## State And Persistence
Runtime state includes authenticated HTTP client, storage service, bucket cache, pacer, root bucket/directory, and a one-time compressed-object warning. Remote persistent state includes buckets, objects, metadata, ACL/IAM policy choices, storage class, and optional slash-suffixed marker objects for empty directories. Local persistence is limited to OAuth token/config mechanisms managed by rclone.

## Dependencies And Integration Points
The backend integrates with `google.golang.org/api/storage/v1`, `googleapi`, `oauthutil`, `bucket.Cache`, rclone `list`, `fshttp`, `pacer.NewS3`, `encoder`, and requester-pays `user_project`. It implements `fs.Copier`, `fs.PutStreamer`, `fs.ListRer`, `fs.ListPer`, and object `MimeTyper`; MD5 is decoded from GCS base64 metadata.

## Risks And Test Signals
Risks include the deprecated storage API client, endpoint subpath limitations for uploads, service-account role limitations around bucket checks, directory marker edge cases with double slashes, gzip objects whose size/hash become unknown when decompressed, ACL behavior with bucket policy only, requester-pays propagation, and metadata update via self-copy. Tests should cover authenticated modes, bucket root and object root, directory markers, gzip downloads, range reads, storage-class headers, requester-pays, and rewrite continuation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlecloudstorage/googlecloudstorage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlecloudstorage/googlecloudstorage_test.go -->
# sources/user-network-fs/rclone/backend/googlecloudstorage/googlecloudstorage_test.go

## Purpose
This file runs the GCS backend through rclone's generic integration tests with and without directory markers.

## Important APIs, Types, And Control Flow
`TestIntegration` runs against `TestGoogleCloudStorage:`. `TestIntegration2` skips when an explicit `-remote` is set, then runs the same backend with extra config enabling `directory_markers`.

## State And Persistence
The tests create and delete buckets/objects through the configured GCS remote. The second test persists empty directory behavior remotely through marker objects during the run.

## Dependencies And Integration Points
It depends on the production `googlecloudstorage` package, `fstest`, and `fstests`. Extra config is passed through `fstests.ExtraConfigItem`.

## Risks And Test Signals
The tests verify broad fs behavior and specifically ensure the directory-marker feature remains compatible with the generic suite. They require live GCS credentials and project/bucket permissions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlecloudstorage/googlecloudstorage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlephotos/albums.go -->
# sources/user-network-fs/rclone/backend/googlephotos/albums.go

## Purpose
This file implements an in-memory album index for the Google Photos backend. It converts Google Photos flat album titles into a stable virtual directory tree and handles duplicate album titles.

## Important APIs, Types, And Control Flow
The `albums` type stores `dupes` by original title, `byID`, `byTitle`, and `path` mappings for partial directory paths. `newAlbums` initializes the maps. `add` cleans album titles, substitutes an ID-only title for empty/root-like titles, and calls `_add` under lock. `_add` tracks duplicates; when the second duplicate appears it removes and re-adds the first album so both visible names include `{ID}`, then indexes the album and records each parent path component. `del` and `_del` remove ID/title mappings and prune path entries while intentionally leaving `dupes` intact so duplicate naming remains stable. `get` and `getDirs` are locked readers.

## State And Persistence
State is process-local and protected by a mutex. It mirrors remote album metadata but does not persist locally. Deletions remove lookup/path state but leave duplicate history to avoid renaming albums after one duplicate disappears.

## Dependencies And Integration Points
It depends on Google Photos API `Album`, `path.Clean`, string path splitting, slices deletion, and the package helper `addID`. `googlephotos.go` uses it as the cached result of `listAlbums`, while `pattern.go` uses `get` and `getDirs` to synthesize album directories and album contents.

## Risks And Test Signals
Risks include stale album cache invalidation, mutation of `album.Title` while adding, stable duplicate naming after deletion, and path pruning when an album title is both a directory prefix and an album. Unit tests cover add, delete, duplicate naming, weird cleaned paths, title lookup, and directory lookup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlephotos/albums.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlephotos/albums_test.go -->
# sources/user-network-fs/rclone/backend/googlephotos/albums_test.go

## Purpose
This unit test file validates the Google Photos album index and its virtual directory behavior.

## Important APIs, Types, And Control Flow
`TestNewAlbums` checks map initialization. `TestAlbumsAdd` verifies normal albums, duplicate titles, subdirectory-like titles, and path-cleaned weird titles. `TestAlbumsDel` verifies ID/title removal, duplicate history retention, and path pruning. `TestAlbumsGet` and `TestAlbumsGetDirs` check lookup success and failure.

## State And Persistence
All state is in local `albums` instances built from synthetic `api.Album` values. There is no remote or filesystem persistence.

## Dependencies And Integration Points
The tests use `api.Album` and testify assertions. They directly inspect internal maps, making them precise guards for the path-index contract used by listing.

## Risks And Test Signals
The tests provide strong signals for duplicate-title stability and nested album path behavior, but they do not cover concurrent access or cache invalidation after live API changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlephotos/albums_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlephotos/api/types.go -->
# sources/user-network-fs/rclone/backend/googlephotos/api/types.go

## Purpose
This file defines the JSON payload types used by the Google Photos backend.

## Important APIs, Types, And Control Flow
`ErrorDetails` and `Error` model API failures and implement `error`. Album-related types include `Album`, `ListAlbums`, and `CreateAlbum`. Media listing types include `MediaItem` and `MediaItems`, with embedded media metadata and creation time. Search filter types include `Date`, `DateFilter`, `ContentFilter`, `MediaTypeFilter`, `FeatureFilter`, `Filters`, and `SearchFilter`. Upload commit types include `SimpleMediaItem`, `NewMediaItem`, `BatchCreateRequest`, `BatchCreateResponse`, and `BatchRemoveItems`.

## State And Persistence
There is no local state. The types represent persistent remote Google Photos resources, upload tokens being committed into media items, and filter state sent with list/search requests.

## Dependencies And Integration Points
It depends on `fmt` and `time`. `googlephotos.go` and `pattern.go` use these types for album listing/creation, media searching, upload batch creation, and album item removal.

## Risks And Test Signals
Risks include Google Photos API policy/schema changes, especially app-created-data limitations, upload result status codes, and filter fields. Tests should include JSON fixtures for errors, paged album/media listings, date/feature filters, and batch create responses with per-item failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlephotos/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlephotos/googlephotos.go -->
# sources/user-network-fs/rclone/backend/googlephotos/googlephotos.go

## Purpose
This file implements rclone's Google Photos backend. It exposes Google Photos as a virtual filesystem with media views, album views, shared album views, an upload staging tree, and a feature/favorites view, while respecting Google Photos API limitations around app-created data, mtimes, deletion, and original downloads.

## Important APIs, Types, And Control Flow
Key types are `Options`, `Fs`, `Object`, and `uploadedItem`. `init` registers `gphotos`, configuration warnings, read-only/read-size/start-year/include-archived/proxy options, and batcher options. `NewFs` creates an OAuth client, normalizes root, initializes authenticated and unauthenticated REST clients, pacer, album caches, upload dirtree, and a `batcher.Batcher`; it detects file-root paths through `patterns.match`.

Authentication support includes `UserInfo`, `Disconnect`, and `fetchEndpoint`, which read OpenID configuration endpoints and use the OAuth token source for revocation. `errorHandler` accepts JSON API errors and image/404 responses.

Listing uses `listAlbums`, `list`, `itemToDirEntry`, `listDir`, `listUploads`, and `List`. Albums are cached by shared/non-shared key. Media listing calls `/mediaItems:search`, adds `IncludeArchivedMedia` unless listing an album, skips duplicate first items across pages, replaces slashes in filenames, and deduplicates duplicate filenames by adding `{ID}`. `List` itself delegates path interpretation to `pattern.go`.

Writes use `Mkdir`, `Put`, `Object.Update`, `commitBatch`, and `commitBatchAlbumID`. `Mkdir` can create app albums or synthetic upload directories. `Update` validates that the virtual path is uploadable, creates or finds albums where required, rejects read-only or non-writeable albums, uploads bytes to `/uploads` to receive a token, then commits tokens through `/mediaItems:batchCreate`, batching by album ID. Uploads under `upload/` are also stored in the local `uploaded` dirtree.

Object operations include ID-aware `readMetaData`, optional size probing with `HEAD`, `downloadURL`, `Open` with optional gphotosdl proxy, unsupported hashes and modtime updates, and `Remove`, which only removes media from writable app-created albums through `batchRemoveMediaItems`. Album deletion is explicitly unsupported.

## State And Persistence
Runtime state includes OAuth token source, REST clients, pacer, start time for virtual directories, album caches, uploaded local dirtree, create mutex, and batcher. Remote persistence includes created albums and uploaded media items. Local `uploaded` state is process memory only, so the upload virtual tree is not durable across backend instances. Google OAuth token persistence is handled by rclone's OAuth utilities.

## Dependencies And Integration Points
The backend integrates `oauthutil`, `rest`, `batcher`, `dirtree`, `encoder`, Google OAuth endpoints, and the pattern and album helpers in this package. It implements `fs.UserInfoer`, `fs.Disconnecter`, `fs.MimeTyper`, and `fs.IDer`; it intentionally does not expose hashes or settable mtimes.

## Risks And Test Signals
Risks are dominated by Google Photos API restrictions and policy changes: only app-created data can be downloaded/edited under current scopes, albums cannot be deleted through this code, uploaded-tree state is memory-only, album cache invalidation is missing, filenames can collide, and `Remove` assumes `f.albums[false]` has been populated. Batch result ordering and album grouping are critical. Tests should cover virtual path matching, read-only mode, non-writeable albums, duplicate filenames, ID-based lookup, batch failures, proxy download URLs, `ReadSize`, and upload directory persistence limits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlephotos/googlephotos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlephotos/googlephotos_test.go -->
# sources/user-network-fs/rclone/backend/googlephotos/googlephotos_test.go

## Purpose
This integration-oriented test file exercises Google Photos behavior that the generic rclone test suite cannot model well because the backend is a virtual, API-limited filesystem.

## Important APIs, Types, And Control Flow
`TestIntegration` creates a Google Photos remote and a local `testfiles` remote. It creates a random app album, uploads a JPEG, checks object methods, optional size probing, unsupported modtime/hash behavior, download content type, album listing, date hierarchy visibility, `NewObject` with and without embedded IDs, file-root detection, and album item removal. It then tests synthetic `upload/` directories with `Mkdir`, `List`, and `Rmdir`, and uploads another file into the upload tree. Final subtests check `Name`, `Root`, `String`, `Features`, `Precision`, and `Hashes`. Helper tests cover `addID`, `addFileID`, and `findID`.

## State And Persistence
The test creates real Google Photos albums/media when credentials are configured. Uploaded synthetic directory state lives only in the backend instance. Album removal is expected to fail because API album deletion is unsupported; uploaded media removal from an album is tested.

## Dependencies And Integration Points
It uses rclone `fs`, local backend import, `fstest`, random name generation, testify, and package internals. It requires test image files and a configured `TestGooglePhotos:` remote unless skipped for missing config.

## Risks And Test Signals
The tests give strong end-to-end signals for Google Photos API compatibility, virtual paths, uploads, ID disambiguation, and downloads. They are slower and credential-dependent, and they do not test all error branches such as read-only mode, batch partial failures, or gphotosdl proxy behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlephotos/googlephotos_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlephotos/pattern.go -->
# sources/user-network-fs/rclone/backend/googlephotos/pattern.go

## Purpose
This file defines the Google Photos backend's virtual filesystem layout. It maps path strings to regex-backed directory patterns and converts matched paths into directory entries or search filters.

## Important APIs, Types, And Control Flow
`lister` is the subset of `Fs` used by pattern logic. `dirPattern` records a regex, upload/mkdir/file/upload-directory capabilities, and an optional `toEntries` callback. `patterns` defines the tree: root directories `media`, `album`, `shared-album`, `upload`, and `feature`; upload staging paths; all media; year/month/day date views; album/shared-album pseudo-directories; and `feature/favorites`.

`mustCompile` compiles regexes at init. `dirPatterns.match` joins root and item path, derives a prefix relative to root, filters by file-vs-directory pattern, and returns regex captures plus matching pattern. `years`, `months`, and `days` synthesize date hierarchy directories. `yearMonthDayFilter` validates and builds `api.SearchFilter` date filters. `featureFilter` builds a hardcoded FAVORITES filter. `albumsToEntries` combines synthetic album-prefix directories with actual album media listing and returns `fs.ErrorDirNotFound` when a non-root album path matches neither.

## State And Persistence
The file has no mutable persistent state beyond the package-level compiled `patterns` slice. It derives entries from the provided lister, album cache, and upload dirtree.

## Dependencies And Integration Points
It depends on the Google Photos API types, rclone `fs`, package album helpers, and Go regexp/time/path utilities. `googlephotos.go` calls `patterns.match` for `NewFs`, `List`, `Mkdir`, `Rmdir`, `Update`, `Remove`, and metadata lookup.

## Risks And Test Signals
Risks include regex ordering, ambiguous album/file paths, prefix calculation when the remote root is nested, date validation accepting impossible dates like February 31 because only numeric bounds are checked, and stale album/upload data. Unit tests cover matching, generated entries, date hierarchies, date filter validation, and album entry synthesis.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlephotos/pattern.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlephotos/pattern_test.go -->
# sources/user-network-fs/rclone/backend/googlephotos/pattern_test.go

## Purpose
This file unit-tests Google Photos virtual path matching and entry generation without calling the live API.

## Important APIs, Types, And Control Flow
`testLister` implements the pattern `lister` interface using in-memory album, name, and upload trees. `TestPatternMatch` checks root-relative and nested path matching for directories and files. `TestPatternMatchToEntries` invokes selected `toEntries` callbacks and inspects the first returned remotes. `TestPatternYears`, `TestPatternMonths`, and `TestPatternDays` verify date directory generation. `TestPatternYearMonthDayFilter` checks valid and invalid date filter construction. `TestPatternAlbumsToEntries` verifies album-prefix directory behavior and combined directory plus file listing.

## State And Persistence
All test state is in memory: synthetic albums, mock objects, and a `dirtree.DirTree` for uploaded entries. No network or disk state is used.

## Dependencies And Integration Points
The tests use `api`, `fs`, `dirtree`, `fstest`, `mockobject`, and testify. They are direct guards for `pattern.go` and indirectly protect `googlephotos.go` methods that depend on pattern capabilities.

## Risks And Test Signals
The tests are strong for route selection and expected virtual remotes, but they deliberately sample only the first few generated entries in long year/month/day outputs. They do not verify live API filter results or all regex branches exhaustively.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/googlephotos/pattern_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hasher/commands.go -->
# sources/user-network-fs/rclone/backend/hasher/commands.go

## Purpose
This file implements backend commands for the hasher overlay: dropping the checksum cache, dumping cache contents, and importing checksum files.

## Important APIs, Types, And Control Flow
`Command` dispatches `drop`, `dump`, `fulldump`, `import`, and `stickyimport`. `drop` stops and deletes the kv database. Dumps call `dbDump`, with `fulldump` including records outside the current wrapped root. Imports validate the hash type, ignore unsupported or unneeded hashes, open a SUM file through rclone's cache, parse it with `operations.ParseSumFile`, and either write sticky records with `anyFingerprint` or walk the wrapped hasher filesystem to bind checksums to existing objects by path.

`commandHelp` documents command usage. `dbDump` resolves the wrapped remote root when needed, handles disabled or inactive DBs, and delegates to `kvDump`. `dbImport` logs long imports, records checking transfers for non-sticky imports, and reports skipped vanished objects.

## State And Persistence
The commands read and mutate the hasher kv database. `drop` removes cached state, `import` writes records, and dumps print database content to stdout/logs. Sticky imports intentionally persist hash records without fingerprint validation.

## Dependencies And Integration Points
It depends on rclone `fs.Commander`, `cache.Get`, `fspath`, `hash.Type`, `operations.ParseSumFile`, `operations.ListFn`, `accounting`, and `kv`. It relies on object-level `putHashes` and filesystem `putRawHashes` implemented elsewhere in the hasher package.

## Risks And Test Signals
Risks include importing stale or mismatched checksum files, sticky import bypassing size/time fingerprint checks, disabled DB when `max_age=0`, large import performance, and partial failures being logged rather than fatal per object. Tests should cover command dispatch, bad args, unsupported hash types, inactive DB, dump formatting, sticky and non-sticky import semantics, and vanished objects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hasher/commands.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hasher/hasher.go -->
# sources/user-network-fs/rclone/backend/hasher/hasher.go

## Purpose
This file implements the main filesystem wrapper for the hasher backend. Hasher wraps another rclone remote and augments its hash capabilities by passing through fast native hashes, caching slow native hashes, and computing configured hashes locally when needed.

## Important APIs, Types, And Control Flow
`init` registers the `hasher` remote with `remote`, `hashes`, `max_age`, and `auto_size` options plus backend command help. `Options` captures those settings. `Fs` embeds the wrapped `fs.Fs` and stores wrapper metadata, kv DB handle, fingerprint strategy, and hash sets grouped as passed, slow, auto, keep, and supported.

`NewFs` rejects unsupported OSes and self-wrapping, derives the wrapped remote using `fspath.JoinRootPath` and `cache.Get`, adjusts root for file remotes, classifies underlying hashes based on `SlowHash`, parses configured hashes, starts the kv DB when `max_age > 0`, builds a feature mask from the base remote, enables `ListP`, and pins the base remote until finalization.

Most filesystem methods delegate to the underlying remote while preserving hasher wrapping and cache state. `wrapEntries`, `List`, `ListP`, and `ListR` wrap objects in hasher `Object`. `Purge`, `PutStream`, `PutUnchecked`, `Move`, and `DirMove` prune or move cached records around underlying operations. `Copy` delegates and wraps. Optional operations such as `CleanUp`, `About`, `ChangeNotify`, `UserInfo`, `Disconnect`, `MergeDirs`, `DirSetModTime`, `MkdirMetadata`, `DirCacheFlush`, and `PublicLink` pass through when available. `Shutdown` stops the kv DB and then the underlying remote. Object wrapper methods expose the hasher `Fs`, underlying object via `UnWrap`, and optional ID/tier/mime/metadata behavior.

## State And Persistence
Runtime state tracks the wrapped remote, optional wrapper parent, feature mask, and hash classification. Persistent state is the kv database created by `kv.Start(ctx, "hasher", f.Fs)` when caching is enabled. Cache records are pruned on overwrites/removes elsewhere, purged for directories, and migrated on moves. With `max_age=0`, the DB is disabled and caching paths must handle inactive DB behavior.

## Dependencies And Integration Points
The file integrates rclone's wrapper interfaces, feature masking, `cache.Get`, `kv`, `list.WithListP`, and hash/type parsing. Hash calculation, raw get/put, object update/remove/open, and fingerprint details are implemented in adjacent hasher package files; this file provides the wrapper and lifecycle surface they depend on.

## Risks And Test Signals
Risks include nil DB use in cache maintenance paths when `max_age=0`, feature masks advertising behavior incorrectly after wrapping, root/path mismatches when the wrapped remote points to a file, hash classification errors for slow or unsupported hashes, and cache records becoming stale after delegated operations not covered by pruning/move logic. Tests should exercise wrapping around local and nonlocal remotes, disabled cache mode, slow-hash remotes, server-side move/copy/dir-move, purge, shutdown idempotence, and optional interface passthrough.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hasher/hasher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hasher/hasher_internal_test.go -->
# sources/user-network-fs/rclone/backend/hasher/hasher_internal_test.go

## Purpose
This internal test file checks hasher behavior when uploading from a crypt remote, especially whether the hasher can generate and cache a checksum for content whose wrapped source may not expose the target hash directly.

## Important APIs, Types, And Control Flow
`putFile` writes a test object with fixed mtime. `testUploadFromCrypt` creates a temporary local remote, wraps it with an in-memory crypt remote, uploads a small file, prunes any existing hasher cache record, verifies the raw hash is absent, uploads from crypt into the hasher remote, and then checks that a hash record exists when caching is enabled. It purges the test directory afterward. `InternalTest` skips on unsupported kv platforms and runs the subtest.

## State And Persistence
The test creates a temporary local filesystem tree and removes it afterward. It mutates the hasher kv cache by pruning and then expecting a new hash record. Remote test data is purged through rclone operations.

## Dependencies And Integration Points
It uses crypt backend syntax, password obscuring, `fs.NewFs`, generic `fstests.PutTestContents`, operations purge, and hasher raw hash helpers from adjacent package files. It runs through the `fstests.InternalTester` hook.

## Risks And Test Signals
The test specifically guards upload-from-crypt hash capture and disabled-cache behavior. It depends on kv support and the crypt backend being importable through the test environment.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hasher/hasher_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hasher/hasher_test.go -->
# sources/user-network-fs/rclone/backend/hasher/hasher_test.go

## Purpose
This file wires hasher into rclone's generic filesystem integration suite.

## Important APIs, Types, And Control Flow
`TestIntegration` skips when kv is unsupported. It builds `fstests.Opt` with the configured remote or, when no remote is supplied, creates a temporary local-backed `TestHasher` remote. It marks `OpenWriterAt` and `OpenChunkWriter` unimplementable, runs the generic suite, then runs it again with `max_age=0` to test disabled cache mode.

## State And Persistence
Default test state uses a temp directory under the OS temp path and may create a hasher kv DB depending on `max_age`. The second run intentionally disables persistent cache records.

## Dependencies And Integration Points
It imports all rclone backends for integration tests, the production hasher package, `fstest`, `fstests`, and `kv`.

## Risks And Test Signals
The tests provide broad rclone interface coverage for both cached and no-cache modes, but they depend on generic suite behavior for most assertions. Specific command/import/dump behavior is not covered here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hasher/hasher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hasher/kv.go -->
# sources/user-network-fs/rclone/backend/hasher/kv.go

## Purpose
This file implements the hasher backend's kv database record format and database operations for prune, purge, move, get, put, and dump.

## Important APIs, Types, And Control Flow
`hashRecord` stores a fingerprint string, `operations.HashSums`, and creation time. `encode` and `decode` serialize records using gob. `kvPrune` deletes one key. `kvPurge` scans and deletes all keys below a directory prefix. `kvMove` moves either one file record or all records below a directory prefix; `moveHash` performs the delete and put. `kvGet` loads a record, validates fingerprint compatibility including `anyFingerprint`, validates age, and returns one hash value. `kvPut` loads an existing record, discards it if decoding fails, fingerprint differs, or age expired, then merges new hashes and stores the encoded record. `kvDump` emits either full DB output or root-scoped output and records counts for tests. `dumpLine` formats status, kept hash values, record age, and path.

## State And Persistence
The persistent state is a gob-encoded kv bucket keyed by wrapped remote paths. Records include their creation timestamp for expiry and a fingerprint to detect object changes. Directory purge and move operations rely on lexicographic prefix scans. Sticky imported records use `anyFingerprint` and are reported with `stk` status in dumps.

## Dependencies And Integration Points
It depends on rclone `kv`, `fs`, `hash`, and `operations.HashSums`. `commands.go` uses `kvDump`; `hasher.go` uses prune, purge, and move operations; object-level hash code in adjacent files uses `kvGet` and `kvPut`.

## Risks And Test Signals
Risks include gob incompatibility if `hashRecord` changes, prefix scans over path strings with ambiguous slashes, move overwriting existing destination records, `moveHash` deleting source before a failed destination put, age-based invalidation relying on local clock, and full dump holding DB access long enough to affect concurrent operations. Tests should cover decode failures, fingerprint mismatch, timeout, sticky records, directory purge/move prefixes, dump statuses, and put merging multiple hash types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/hasher/kv.go -->

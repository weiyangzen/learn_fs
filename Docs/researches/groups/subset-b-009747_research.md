# subset-b-009747 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/iclouddrive.go -->
# sources/user-network-fs/rclone/backend/iclouddrive/iclouddrive.go

## Purpose
Implements the writable iCloud Drive rclone backend for non-Plan9/non-Solaris builds. It adapts Apple iCloud Drive API calls to rclone `fs.Fs`, `fs.Object`, `fs.Mover`, `fs.DirMover`, `fs.Purger`, `fs.Copier`, `fs.Disconnecter`, and `fs.DirCacheFlusher` interfaces.

## Important APIs, Types, and Functions
`Options` carries Apple ID/password/client/cookie/trust-token fields plus the multi-encoder. `Fs` stores backend identity, root, root ID, config mapper for persisted auth, `dircache.DirCache`, iCloud API client, drive service, and pacer. `Object` stores remote, size, modtime, created time, drive/document/item IDs, ETag, and download URL.

Core directory helpers are `findItem`, `findLeafItem`, `FindLeaf`, `FindPath`, `FindDir`, `IDJoin`, `putFolderCache`, and `CreateDir`. Listing and object creation run through `listAll`, `List`, `NewObject`, `NewObjectFromDriveItem`, `readMetaData`, and `setMetaData`. Mutating behavior is in `Put`, `Object.Update`, `Object.Remove`, `Move`, `DirMove`, `purgeCheck`, `Purge`, and `Rmdir`. `Copy` is present but deliberately returns `fs.ErrorCantCopy` because the iCloud copy endpoint is marked broken.

## Control Flow
`NewFs` builds an authenticated iCloud client for `api.WsDrive`, trims the configured root, initializes a pacer, obtains `DriveService`, and creates a `dircache` rooted at `FOLDER::com.apple.CloudDocs::root`. If root lookup fails, it probes the parent as a possible file root and returns `fs.ErrorIsFile` when appropriate.

Directory lookup flows through `dircache`; `FindLeaf` lists all children under a normalized ID, compares names case-insensitively after NFC normalization, rejects file leaves as `fs.ErrorIsFile`, and returns an ID joined with the ETag. `List` resolves a dir ID, fetches all children through `GetItemByDriveID`, decodes names/extensions, caches folders, and converts files into `Object`s.

Uploads remove an existing file first, create an upload document, upload bytes, then call `UpdateFile` with receipt/signature/key/size and mtime/btime. Downloads fetch a fresh download URL by drive ID before streaming with range options. Moves split into an optional parent move followed by optional rename, because iCloud exposes them as separate calls.

## State and Persistence
Auth state and disconnect cleanup are delegated to shared iCloud helpers through the config mapper and `disconnectClient`. Directory state is cached in `dircache` as `drivewsid#etag`; cache entries are flushed after destructive operations. Object state is populated from API metadata and refreshed after upload/update. Empty files are emulated on download by returning an empty reader because Drive does not support real empty-file storage.

## Dependencies and Integration Points
The file depends on `backend/iclouddrive/api` for Drive endpoints, rclone `fs` interfaces, `configmap`, `fserrors`, `hash`, `dircache`, `encoder`, `pacer`, and Unicode normalization. It uses rclone's pacer retry contract around every remote call and uses the backend encoder before sending names to iCloud or exposing them to rclone.

## Risks and Edge Cases
iCloud occasionally returns status `unknown`; the backend alternates between ignoring unknown results for idempotent-looking operations and retrying unknown results for operations where final state is uncertain. `findItem` assumes `resp.StatusCode` is available when `item == nil`, which depends on API behavior after errors. `Object.Update` trashes the old file before completing the new upload, so a later create/upload/update failure can lose the previous version. ETag handling is embedded in string IDs using `#`, so any unexpected delimiter in IDs would be dangerous, though `IDJoin` strips prior ETags. Server-side copy is dead code after an unconditional `ErrorCantCopy`.

## Test Signals
Drive-specific local tests are not in this file's package; integration coverage is provided by `iclouddrive_test.go` against `TestICloudDrive:`. Important untested local seams include `ignoreResultUnknown`, `retryResultUnknown`, empty-file emulation, ID/ETag joining, and rollback behavior during update failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/iclouddrive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/iclouddrive_test.go -->
# sources/user-network-fs/rclone/backend/iclouddrive/iclouddrive_test.go

## Purpose
Defines the iCloud Drive integration test entrypoint for rclone's generic filesystem test suite.

## Important APIs, Types, and Functions
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestICloudDrive:"` and `NilObject: (*iclouddrive.Object)(nil)`.

## Control Flow
The test is gated by the same non-Plan9/non-Solaris build tag as the backend. When credentials/config for `TestICloudDrive:` exist, `fstests.Run` exercises the backend through rclone's common object, directory, upload, download, move, purge, and feature tests.

## State and Persistence
No local state is persisted by the test file itself. It relies on rclone test remote configuration and any remote iCloud state created and cleaned up by `fstests`.

## Dependencies and Integration Points
Imports the backend package and `github.com/rclone/rclone/fstest/fstests`. It is the main automated integration signal that the backend conforms to the rclone interface contract.

## Risks and Edge Cases
The test requires real iCloud credentials and network access, so it may not run in normal unit-test lanes. It does not isolate individual retry, normalization, or unknown-result behavior; failures will often appear as broad integration failures.

## Test Signals
Presence of this test means interface regressions can be caught by rclone's shared suite when the remote is configured. There are no pure unit tests for `iclouddrive.go` in this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/iclouddrive_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/iclouddrive_unsupported.go -->
# sources/user-network-fs/rclone/backend/iclouddrive/iclouddrive_unsupported.go

## Purpose
Provides a buildable package stub for unsupported Plan9 and Solaris platforms so the Go package does not fail with "no buildable Go source files."

## Important APIs, Types, and Functions
The file declares package `iclouddrive` only. It exports no functions, types, variables, or interface implementations.

## Control Flow
The file is selected only by `//go:build plan9 || solaris`. Runtime behavior is intentionally absent.

## State and Persistence
No state is maintained.

## Dependencies and Integration Points
It integrates only with Go's build constraint system. The real Drive and Photos implementations are excluded on these platforms.

## Risks and Edge Cases
Any consumer expecting iCloud Drive symbols on Plan9/Solaris will not have them. This is deliberate but means platform support is compile-placeholder only.

## Test Signals
No tests target this stub directly. Its value is compile-time package availability on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/iclouddrive_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/icloudphotos.go -->
# sources/user-network-fs/rclone/backend/iclouddrive/icloudphotos.go

## Purpose
Implements the read-only iCloud Photos backend, sharing auth/config with the iCloud Drive package while exposing libraries, albums, nested folders, photos, metadata, recursive listing, and change notification through rclone interfaces.

## Important APIs, Types, and Functions
`PhotosFs` stores root, options, iCloud client, config mapper, pacer, `dircache`, HTTP client, lazy `PhotosService`, and a mutex. `PhotosObject` stores remote metadata plus CloudKit master/zone/resource identifiers required to obtain fresh download URLs.

Key APIs are `NewFsPhotos`, `photosService`, `List`, `NewObject`, `newPhotosObject`, `FindLeaf`, `resolveAlbum`, `resolveAlbumPath`, `parseAlbumDirID`, `ListR`, `ChangeNotify`, `notifyZoneChange`, `Metadata`, and `Open`. Write operations `Put`, `Mkdir`, `Rmdir`, `CreateDir`, `PhotosObject.Update`, and `PhotosObject.Remove` return `fs.ErrorNotImplemented`.

## Control Flow
`NewFsPhotos` authenticates against `api.WsPhotos`, builds a read-oriented feature set, and initializes `dircache` at synthetic `photos-root`. Like Drive, it probes whether the configured root is actually a file and can return `fs.ErrorIsFile`.

`List` dispatches by directory ID shape: `photos-root` lists libraries, `lib:<library>` lists albums for a library, and `album:<library>:<path>` lists child albums for folder albums or files for leaf albums. `FindLeaf` mirrors this state machine for `dircache`, resolving libraries, top-level albums, and nested child albums. `NewObject` resolves parent album and then performs a name lookup inside the album.

`ListR` resolves the starting directory, emits directories via `list.Helper`, collects leaf album jobs, and lists album photos with a goroutine pool sized by `fs.GetConfig(ctx).Checkers`. `Open` performs a fresh `LookupDownloadURL` and streams through the configured HTTP client with rclone range headers. `ChangeNotify` starts a goroutine that receives poll intervals, polls CloudKit change tokens, and notifies affected directories.

## State and Persistence
The backend has no write persistence because it is read-only. It caches directory IDs in `dircache` and caches the lazily constructed `PhotosService`; `DirCacheFlush` resets both dircache and API-layer caches. `startTime` is used as a stable synthetic modtime for library/album directories. Object metadata is derived from API photo fields and returned through rclone metadata keys.

## Dependencies and Integration Points
Depends on `backend/iclouddrive/api` Photos types, rclone `fs`, `fshttp`, `hash`, `list`, `dircache`, and `pacer`. It uses the same retry helpers as Drive and the same encoder options. CloudKit record IDs, zones, and resource keys are integration-critical because download URLs are not treated as durable.

## Risks and Edge Cases
`parseAlbumDirID` strips the prefix with `strings.TrimPrefix`; callers usually guard with `HasPrefix`, but the helper itself accepts some non-`album:` strings as valid if they contain a colon. `ListR` protects `list.Helper` with a mutex but still depends on album caches and context cancellation working correctly under parallel listing. Change notification invalidates directories coarsely, especially when rooted at missing nested albums. Read-only methods returning `ErrorNotImplemented` must remain consistent with advertised features.

## Test Signals
`icloudphotos_test.go` covers smart album definitions, metadata formatting, nested album resolution, `FindLeaf`, `ListR` recursion from root and folder roots, and zone-change notification scope. There is no live integration harness in this file; real CloudKit behavior is exercised only when broader backend integration tests are configured.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/icloudphotos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/icloudphotos_test.go -->
# sources/user-network-fs/rclone/backend/iclouddrive/icloudphotos_test.go

## Purpose
Provides pure unit coverage for the iCloud Photos backend and related `api` smart album definitions without requiring real iCloud service calls.

## Important APIs, Types, and Functions
Test helpers `newTestPhotosFs`, `newTestPhotosService`, and `setEmptyPhotoCaches` construct in-memory `PhotosFs` and `api.PhotosService` values. Tests cover `api.SmartAlbums`, `parseAlbumDirID`, `PhotosObject.Metadata`, `resolveAlbum`, `FindLeaf`, `ListR`, and `notifyZoneChange`.

## Control Flow
The tests build synthetic library/album trees containing smart albums, user albums, folders, child albums, nested folders, and leaf albums. They pre-populate photo caches to keep `GetPhotos` and `GetPhotoByName` on the test path rather than HTTP. `ListR` tests initialize `dircache`, call `FindRoot`, collect directory callbacks, sort results, and assert expected nested paths.

## State and Persistence
All state is in memory. The tests intentionally inject `f.photos` and dircache roots instead of creating a real iCloud client. Object metadata tests use fixed timestamps and booleans.

## Dependencies and Integration Points
Uses `testify/assert`, `testify/require`, rclone `fs`, `dircache`, and the package-internal `api.NewTestPhotosService`. It validates that Photos backend helpers align with API-layer smart album and album tree contracts.

## Risks and Edge Cases
The tests do not verify HTTP download behavior, CloudKit `LookupDownloadURL`, real cache invalidation, or concurrent album failures in `ListR`. `TestParseAlbumDirID_Exhaustive` documents that the helper accepts `"notalbum:foo:bar"` as true because it only trims a prefix when present; production safety depends on caller guards.

## Test Signals
Strong unit signals exist for nested folder traversal, metadata omission for zero dimensions, smart album filter definitions, and notification scoping. The test suite makes expected synthetic directory paths explicit, which is useful when changing path encoding or dircache behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/icloudphotos_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/imagekit/client/client.go -->
# sources/user-network-fs/rclone/backend/imagekit/client/client.go

## Purpose
Defines the ImageKit API client constructor and shared client configuration used by the ImageKit rclone backend.

## Important APIs, Types, and Functions
`ImageKit` stores API/upload prefixes, timeout values, private/public keys, URL endpoint, and a `rest.Client`. `NewParams` carries required private key, public key, and URL endpoint. `New` validates inputs, creates an rclone HTTP client, sets the `rclone/imagekit` user agent, configures Basic Auth with private key and blank password, sets JSON accept headers, and returns an initialized `ImageKit`.

## Control Flow
`New` reads values from `NewParams`, rejects empty values, applies rclone HTTP config with `fs.AddConfig`, creates a `rest.Client`, and fills constants for `https://api.imagekit.io/v2` and `https://upload.imagekit.io/api/v2`.

## State and Persistence
No persistent state is written. Credentials live in the client object and HTTP Basic Auth state.

## Dependencies and Integration Points
Depends on rclone `fs`, `fshttp`, and `lib/rest`. The backend uses this constructor in `imagekit.NewFs`.

## Risks and Edge Cases
The validation error messages appear swapped: an empty private key reports that the URL endpoint is required, and an empty endpoint reports that the private key is required. Timeout fields are stored but not applied in this file. Public key is stored but not used by the shown client methods.

## Test Signals
There are no unit tests for `client.New`; integration testing is indirect through the ImageKit backend.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/imagekit/client/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/imagekit/client/media.go -->
# sources/user-network-fs/rclone/backend/imagekit/client/media.go

## Purpose
Implements ImageKit media-library file and folder API calls plus the response/parameter models used by the backend.

## Important APIs, Types, and Functions
Models include `FilesOrFolderParam`, `AITag`, `File`, `Folder`, folder operation params, `JobIDResponse`, and `JobStatus`. Methods include `File`, `Files`, `DeleteFile`, `Folders`, `CreateFolder`, `DeleteFolder`, `MoveFolder`, and `BulkJobStatus`.

## Control Flow
`Files` and `Folders` call `GET /files` with `skip`, `limit`, `path`, and `searchQuery`, defaulting to file or folder type filters. `Files` can include file versions by changing the search query. Folder create/delete validate nonzero fields with `validator.v2` before JSON requests. `MoveFolder` starts a bulk move job; `BulkJobStatus` fetches job state.

## State and Persistence
The methods do not cache state. They marshal request params and unmarshal ImageKit API responses into Go structs. Deletion and folder moves mutate remote ImageKit media-library state.

## Dependencies and Integration Points
Uses `lib/rest`, `net/url`, `validator.v2`, and ImageKit's REST endpoints under `ImageKit.Prefix`. Backend helpers in `util.go` page through `Files`/`Folders` and perform name lookups with search queries.

## Risks and Edge Cases
`File.Width` and `UploadResult.Width` use JSON tag `"Width"` with uppercase W, matching existing code but potentially surprising if ImageKit returns lowercase `width`. `File` calls ignore status to allow callers to inspect response status, while most other methods rely on rest error behavior. Search query strings are caller-built and must quote names correctly.

## Test Signals
No local unit tests target this client. Coverage comes from ImageKit integration tests and backend list/object operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/imagekit/client/media.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/imagekit/client/upload.go -->
# sources/user-network-fs/rclone/backend/imagekit/client/upload.go

## Purpose
Implements server-side file upload to ImageKit's upload API.

## Important APIs, Types, and Functions
`UploadParam` contains filename, folder, tags, and optional privacy flag. `UploadResult` models upload response fields including file ID, URL, thumbnail, dimensions, size, file path, AI tags, and version info. `ImageKit.Upload` performs the multipart upload.

## Control Flow
`Upload` rejects blank filenames, constructs form fields including `useUniqueFileName=false`, optional tags/folder/privacy, builds a multipart body with `rest.MultipartUpload`, and posts to `/files/upload` under `UploadPrefix`. The JSON response is decoded into `UploadResult`.

## State and Persistence
The method mutates remote ImageKit media-library state by creating or replacing a file depending on ImageKit's `useUniqueFileName=false` semantics. It has no local persistence.

## Dependencies and Integration Points
Uses rclone `lib/rest` multipart upload helpers and the shared authenticated `rest.Client`. Backend `Put`, `Object.Update`, and `uploadFile` call this method.

## Risks and Edge Cases
The upload body always uses `application/octet-stream`; MIME detection is left to ImageKit. No explicit size validation is done here. `useUniqueFileName=false` is critical to rclone overwrite semantics. As with media models, width uses JSON tag `"Width"`.

## Test Signals
No unit tests target upload construction. The integration test exercises uploads against `TestImageKit:` when configured.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/imagekit/client/upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/imagekit/client/url.go -->
# sources/user-network-fs/rclone/backend/imagekit/client/url.go

## Purpose
Generates public or signed ImageKit delivery URLs from existing file URLs and optional query parameters.

## Important APIs, Types, and Functions
`URLParam` contains path/source URL, endpoint override, signed flag, expiry seconds, and query parameters. `ImageKit.URL` returns a URL string and optional HMAC-SHA1 signature parameters.

## Control Flow
The function chooses an endpoint, normalizes a trailing slash, parses `Src`, merges caller query parameters, and serializes the URL. If signing is requested, it calculates expiry as `now + ExpireSeconds`, strips the endpoint prefix from the result URL to build the signing path, appends expiry to that path, computes HMAC-SHA1 using `PrivateKey`, and appends `ik-t` and `ik-s` query parameters.

## State and Persistence
No state is persisted. The only time-varying state is the current Unix timestamp used for signed URLs.

## Dependencies and Integration Points
Used by backend `PublicLink` and `Object.Open`. Depends on standard `crypto/hmac`, `sha1`, URL parsing, and the ImageKit private key.

## Risks and Edge Cases
`URLParam.Path` is unused. If `Src` does not start with the selected endpoint, signing will use the full URL as the path input after a no-op replace, which may produce invalid signatures. Negative or zero expiry values are not rejected. Signing includes query parameters already inserted into `resultURL`, so changes to query encoding affect signatures.

## Test Signals
There are no local tests for signature construction or endpoint edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/imagekit/client/url.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/imagekit/imagekit.go -->
# sources/user-network-fs/rclone/backend/imagekit/imagekit.go

## Purpose
Implements rclone's ImageKit.io media-library backend, adapting ImageKit file/folder APIs to filesystem listing, object access, upload, deletion, metadata, and public links.

## Important APIs, Types, and Functions
`Options` defines endpoint, public/private keys, signed URL preference, version listing, and encoder. `Fs` stores root, options, ImageKit client, pacer, and features. `Object` stores remote path, ImageKit file path, MIME type, timestamp, full `client.File`, and optional version ID.

Major methods are `NewFs`, `List`, `newObject`, `NewObject`, `Put`, `Mkdir`, `Rmdir`, `Purge`, `PublicLink`, `Object.Open`, `Object.Update`, `Object.Remove`, `Object.Metadata`, and `uploadFile`.

## Control Flow
`NewFs` parses config, creates the client, sets root to an absolute slash-prefixed path, fills features, and probes whether the root names an existing file by searching the parent folder and filename. `List` verifies non-root directories by querying folder existence, then fetches folders and files using paged helper methods. Folders are converted to `fs.Dir`; files are converted to `Object`, with old versions exposed through `version.Add`.

`NewObject` checks whether the target is a folder first, then searches a file by parent path and encoded filename. `Put` rejects zero-byte uploads and delegates to `uploadFile`. Object reads generate a delivery URL with `tr=orig-true` and `updatedAt` cache-busting, set a Range header, and compensate by discarding bytes locally if the server ignores range requests and returns 200. Updates upload with the existing privacy setting; new uploads use `OnlySigned` as `IsPrivateFile`. Metadata maps ImageKit system fields, embedded metadata, tags, coordinates, privacy, and AI tag sources into rclone metadata.

## State and Persistence
Remote state is the ImageKit media library. Local backend state is config/options, the client, and object snapshots from `client.File`. No dircache is used; each list/object lookup queries ImageKit. `Rmdir` checks emptiness via `List` before deleting; `Purge` deletes folders without listing children.

## Dependencies and Integration Points
Depends on the local ImageKit client package, rclone `fs`, `configstruct`, `hash`, `encoder`, `pacer`, `readers`, and `version`. It exposes rclone features including `ReadMimeType`, `ReadMetadata`, `FilterAware`, and `PublicLinker`.

## Risks and Edge Cases
`Rmdir` and `Purge` dereference `res.StatusCode` without checking whether `res` is nil after `DeleteFolder`. `Object.Open` creates a plain `http.Client{}` instead of using rclone's configured HTTP client, so proxy/TLS/transport settings may be bypassed. It always sets a `Range` header, even when not doing partial content, producing `bytes=0--1` when `count` stays `-1`. Upload helpers create unused `UseUniqueFileName` variables. Modtime precision is unsupported even though timestamps are returned as metadata.

## Test Signals
`imagekit_test.go` runs the generic rclone integration suite against `TestImageKit:` and skips fs check wrapping. There are no local unit tests for listing, URL generation, metadata mapping, or range fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/imagekit/imagekit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/imagekit/imagekit_test.go -->
# sources/user-network-fs/rclone/backend/imagekit/imagekit_test.go

## Purpose
Defines the ImageKit backend integration test entrypoint.

## Important APIs, Types, and Functions
`TestIntegration` sets `fstest.Verbose` to true and calls `fstests.Run` with `RemoteName: "TestImageKit:"`, `NilObject: (*Object)(nil)`, and `SkipFsCheckWrap: true`.

## Control Flow
When the test remote is configured, rclone's shared integration suite performs filesystem operations against ImageKit. `SkipFsCheckWrap` indicates the backend has behavior that should not be wrapped by the standard fs check layer.

## State and Persistence
No local state is persisted by the test file. Remote ImageKit state is created and cleaned by the integration suite.

## Dependencies and Integration Points
Imports rclone `fstest` and `fstests`. It is the only explicit test file for this backend.

## Risks and Edge Cases
No pure unit tests are provided for client validation, signed URL generation, list pagination, metadata mapping, or range handling. Integration tests require credentials and external service stability.

## Test Signals
The integration harness can catch broad API and interface regressions for configured developers/CI, but not small deterministic helper regressions in offline unit runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/imagekit/imagekit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/imagekit/util.go -->
# sources/user-network-fs/rclone/backend/imagekit/util.go

## Purpose
Provides ImageKit backend helper functions for paginated file/folder listing, name lookup, retry decisions, and path/name encoding.

## Important APIs, Types, and Functions
`getFiles`, `getFolders`, `getFileByName`, and `getFolderByName` wrap client API calls. `retryErrorCodes`, `shouldRetryHTTP`, and `Fs.shouldRetry` implement retry policy. `EncodePath`, `DecodePath`, `EncodeFileName`, and `DecodeFileName` centralize encoder usage.

## Control Flow
`getFiles` and `getFolders` loop with `Skip=len(current)` and `Limit=100`, appending results until the returned page has fewer than 100 entries. Name lookups issue a one-result filtered search query with `strconv.Quote(name)`. `shouldRetry` honors context cancellation, treats 429/503 specially with `X-RateLimit-Reset` as a millisecond retry delay, and retries generic transient errors or selected HTTP statuses.

## State and Persistence
No persistent state is maintained. Helpers return fresh slices or object pointers from ImageKit API results.

## Dependencies and Integration Points
Depends on the ImageKit client package, rclone `fs`, `fserrors`, and `pacer`. The main backend file uses these helpers for every list, object lookup, and retry-wrapped mutation.

## Risks and Edge Cases
Pagination assumes an empty or short page means completion; if ImageKit returns unstable ordering during concurrent changes, duplicates or misses are possible. `getFileByName` swallows all errors and returns nil, making some API failures indistinguishable from not found. `X-RateLimit-Reset` is interpreted as milliseconds; if ImageKit documents seconds or epoch time, retry delays may be wrong.

## Test Signals
No direct unit tests cover pagination or retry decisions. Integration tests exercise these paths indirectly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/imagekit/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/internetarchive/internetarchive.go -->
# sources/user-network-fs/rclone/backend/internetarchive/internetarchive.go

## Purpose
Implements an Internet Archive backend using IA's native IAS3/frontend APIs instead of a generic S3-compatible backend. It exposes IA items as buckets and item files as rclone objects, with metadata, hashes, public links, server-side copy, cleanup, usage reporting, and optional archive-processing wait behavior.

## Important APIs, Types, and Functions
`Options` contains IAS3/front endpoints, optional auth keys, item metadata, derive flag, checksum behavior, wait timeout, and encoder. `Fs` stores root, options, IAS3 and frontend REST clients, pacer, and context. `Object` stores remote, modtime, size, server hashes, and raw metadata JSON. API models include `IAFile`, `MetadataResponse`, `MetadataResponseRaw`, and `ModMetadataResponse`.

Core methods include `NewFs`, `split`, `requestMetadata`, `listAllUnconstrained`, `List`, `ListR`, `NewObject`, `Put`, `Object.Update`, `Object.Open`, `Object.Remove`, `SetModTime`, `Metadata`, `Copy`, `PublicLink`, `CleanUp`, `About`, `waitFileUpload`, `waitDelete`, `appendItemMetadataHeaders`, `listOrString`, and path/time helpers.

## Control Flow
`NewFs` parses endpoints, trims root, configures `rest.Client`s for IAS3 and frontend, applies LOW authorization when keys exist, configures S3-style pacing, and probes whether the root is a file. Listing starts from frontend `/metadata/:item`, converts metadata files into objects and virtual directories, then filters direct children for `List` or recursive descendants for `ListR`.

Uploads construct IAS3 `PUT` headers for rclone mtime/update tracking, auto bucket creation, cascade delete, old-version behavior, optional checksum, item metadata, and derive behavior. After the PUT, `waitFileUpload` either returns quickly with best-effort metadata or polls frontend metadata until a tracker and size match. Deletes call IAS3 `DELETE` and optionally poll until metadata disappears. Server-side copy uses IAS3 copy-source headers and the same tracker/wait flow.

`SetModTime` patches file metadata through the frontend metadata write API by removing and re-adding `rclone-mtime`. `Metadata` unmarshals raw IA file metadata, keeps only first values for multi-valued keys, preserves IA's original `mtime` as `rclone-ia-mtime`, and overwrites `mtime` with rclone's parsed modtime.

## State and Persistence
Remote state is IA item file metadata and IAS3 object data. Local persistent state is limited to config. Rclone mtimes are stored as IA file metadata under `rclone-mtime`, while update completion is tracked with a random `rclone-update-track` value. Directories are virtual and inferred from file paths. `history/` is treated as trash for cleanup and usage.

## Dependencies and Integration Points
Uses rclone `fs`, `configstruct`, `fserrors`, `fshttp`, `hash`, `bucket`, `encoder`, `pacer`, `random`, and `rest`, plus `ncw/swift` time parsing for IA float mtimes. It integrates with both IA IAS3 and archive.org frontend metadata/download endpoints.

## Risks and Edge Cases
`Mkdir` and `Rmdir` are no-ops because IA directories are virtual, which may surprise callers. Metadata polling can time out silently by design when `wait_archive` expires. When `wait_archive` is disabled, returned object size/hash may be intentionally unknown or blank after writes. `listAllUnconstrained` builds directory entries from all item metadata, so large IA items may make every list expensive. Path trimming is delicate because bucket/root paths are mixed with encoded and standard paths. `Copy` and upload rely on update trackers in metadata, which can be delayed by IA processing queues.

## Test Signals
The local test file is only an integration harness against `TestIA:lesmi-rclone-test/`. There are no unit tests for metadata parsing, path trimming, wait polling, item metadata header generation, or no-op directory semantics in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/internetarchive/internetarchive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/internetarchive/internetarchive_test.go -->
# sources/user-network-fs/rclone/backend/internetarchive/internetarchive_test.go

## Purpose
Defines the Internet Archive backend integration test entrypoint.

## Important APIs, Types, and Functions
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestIA:lesmi-rclone-test/"` and `NilObject: (*internetarchive.Object)(nil)`.

## Control Flow
The test delegates all behavior to rclone's common integration suite against a configured IA item path.

## State and Persistence
The file stores no state. Remote IA test state is managed by the generic test suite and IA's backend behavior.

## Dependencies and Integration Points
Imports the backend and rclone `fstests`. It is the main configured-service regression signal for the IA backend.

## Risks and Edge Cases
Because IA write/delete visibility is asynchronous unless `wait_archive` is configured, integration tests can be sensitive to remote processing delays. Offline unit coverage is absent.

## Test Signals
Broad filesystem conformance can be checked when `TestIA:` credentials and item are available. Helper-level regressions require additional tests outside this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/internetarchive/internetarchive_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/internxt/auth.go -->
# sources/user-network-fs/rclone/backend/internxt/auth.go

## Purpose
Implements Internxt authentication support: user metadata retrieval, JWT expiry parsing, OAuth token conversion/persistence, Basic auth derivation for bucket operations, token refresh, fallback relogin, and serialized re-authorization after 401 responses.

## Important APIs, Types, and Functions
`userInfo` stores root folder ID, bucket, bridge user, and user ID. `userInfoConfig` carries a token. Functions include `getUserInfo`, `parseJWTExpiry`, `jwtToOAuth2Token`, `computeBasicAuthHeader`, `refreshJWTToken`, `Fs.reLogin`, `Fs.refreshOrReLogin`, and `Fs.reAuthorize`.

## Control Flow
`getUserInfo` calls Internxt's refresh endpoint and validates required user fields. JWT conversion parses claims without validation to extract `exp`. `refreshJWTToken` loads the current rclone OAuth token, calls the refresh endpoint, parses the new JWT, saves it, and persists bucket if present.

`refreshOrReLogin` first attempts refresh. On non-401 errors it returns the refresh error. On 401 it decrypts the stored password, checks whether 2FA is required, performs a full login if possible, saves the new token, and refreshes config fields. `reAuthorize` serializes this path with `authMu` and sets `authFailed` as a circuit breaker after permanent failure.

## State and Persistence
Tokens are persisted through `oauthutil.PutToken` in the rclone config mapper. Bucket may be stored in config. In-memory `Fs` state updates include `cfg.Token`, `cfg.BasicAuthHeader`, bridge user, user ID, bucket, and root folder ID. `authFailed` prevents repeated failing reauth loops.

## Dependencies and Integration Points
Uses `github.com/internxt/rclone-adapter/auth` and config/errors packages, `golang-jwt/jwt/v5`, rclone `configmap`, `obscure`, `fserrors`, `fshttp`, and `oauthutil`. Called by `NewFs`, token renewer callbacks, and retry handling in `internxt.go`.

## Risks and Edge Cases
JWT parsing is unverified and only used for expiry extraction; malformed or missing `exp` prevents token storage. Re-login cannot proceed for 2FA accounts and requires users to reconnect. Once `authFailed` is set, subsequent 401 handling fails permanently for that `Fs`. `refreshOrReLogin` recomputes Basic auth using existing bridge/user values after refresh; if refresh changes those fields but they are not separately loaded, there is a consistency risk.

## Test Signals
No local unit tests cover token parsing, Basic auth derivation, refresh/relogin fallback, or circuit breaker behavior. Integration tests exercise auth only against real Internxt accounts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/internxt/auth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/internxt/internxt.go -->
# sources/user-network-fs/rclone/backend/internxt/internxt.go

## Purpose
Implements the main Internxt Drive rclone backend, including configuration, auth-aware retries, directory caching, list/create/delete operations, object download/upload/update, quota reporting, and shutdown.

## Important APIs, Types, and Functions
`Options` defines email/password/mnemonic, hash validation toggle, upload cutoff/chunk sizing/concurrency, and encoding. `Fs` stores root, config mapper, dircache, Internxt SDK config, features, pacer, OAuth token renewer, bridge user/user ID, and auth locking state. `Object` stores remote, file ID, UUID, size, and modtime.

Core methods include `shouldRetry`, `Config`, `NewFs`, `Mkdir`, `Rmdir`, `FindLeaf`, `CreateDir`, `preUploadCheck`, `convertFileMetaToFile`, `List`, `Put`, `Remove`, `NewObject`, `newObjectWithFile`, `About`, `Shutdown`, `Object.Open`, `Object.Update`, `recoverFromTimeoutConflict`, `restoreBackupFile`, and `Object.Remove`.

## Control Flow
`Config` performs a staged login flow: check email, optionally ask for 2FA, perform login, store mnemonic obscured, convert JWT into an OAuth token, save it, and clear temporary 2FA. `NewFs` validates upload sizing, reveals mnemonic, loads token, creates SDK config, fetches user info with retry and 401 re-auth fallback, fills bucket/root/basic auth, starts an OAuth renewer, and initializes `dircache`. If root lookup fails, it probes parent as a possible file root.

Directory operations use `dircache`: `FindLeaf` lists folders by parent UUID, `CreateDir` creates folders and handles conflicts by searching for an existing folder, `Rmdir` verifies no child folders/files before deletion. Listing fetches folders and files separately and converts file plain name/type into rclone remote names.

Uploads use a cautious overwrite strategy. Existing files are renamed to a unique backup before upload. Small files use `buckets.UploadFileStreamAuto`; large or unknown-size files use the multipart chunk writer. Empty-file limit errors map to `fs.ErrorCantUploadEmptyFiles`. Timeout or conflict errors are followed by existence checks to recover metadata when the upload likely succeeded. On success, backup files are deleted; on failure, `restoreBackupFile` tries to rename the backup back.

## State and Persistence
Remote Internxt state includes folders, file metadata, bucket objects, and pending thumbnails. Local state includes dircache mappings, OAuth token renewer, mutable upload options, and auth circuit state. Tokens and mnemonic are persisted in the rclone config mapper. `Shutdown` waits for thumbnail work and stops token renewal.

## Dependencies and Integration Points
Depends on Internxt adapter packages `auth`, `buckets`, `config`, `errors`, `files`, `folders`, and `users`; rclone `fs`, config helpers, `dircache`, `encoder`, `multipart`, `oauthutil`, `pacer`, and `random`. It implements rclone filesystem, object, about, shutdown, and dircache interfaces.

## Risks and Edge Cases
Upload overwrite safety depends on backup rename and restore succeeding; backup deletion failure can leave orphaned files. `preUploadCheck` intentionally treats existence-check errors as no existing file, which can allow conflicts later. `Remove` attempts object delete before folder delete, so ambiguous file/folder names may prefer file semantics. `About` subtracts pointers returned by usage values and assumes both are present. Auth failure circuit breaker can make later transient auth recovery impossible without recreating the Fs.

## Test Signals
`internxt_test.go` provides only generic integration coverage with chunked upload settings. No pure unit tests cover the staged config flow, retry reauth, backup rollback, timeout conflict recovery, or directory cache behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/internxt/internxt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/internxt/internxt_test.go -->
# sources/user-network-fs/rclone/backend/internxt/internxt_test.go

## Purpose
Defines the Internxt backend integration test entrypoint and configures rclone's shared test suite to exercise chunked uploads.

## Important APIs, Types, and Functions
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestInternxt:"` and `ChunkedUpload` config requiring 100 MiB minimum chunk size and multiple chunks.

## Control Flow
When a real `TestInternxt:` remote is configured, the generic suite exercises object and directory behavior, including multipart upload paths large enough to require multiple chunks.

## State and Persistence
No test-local persistence. Remote files/folders are managed by the shared integration framework.

## Dependencies and Integration Points
Uses rclone `fs` for size constants and `fstests` for the common test suite. It is the only explicit test file for Internxt in this subset.

## Risks and Edge Cases
The integration test requires account credentials, enough quota, and network availability. It does not provide deterministic offline coverage for auth refresh, rollback, conflict recovery, or single-part upload behavior.

## Test Signals
The chunked upload settings are an important signal that multipart behavior is expected to work and is part of backend conformance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/internxt/internxt_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/internxt/upload.go -->
# sources/user-network-fs/rclone/backend/internxt/upload.go

## Purpose
Implements Internxt multipart upload support through rclone's `fs.ChunkWriter` interface, including AES-CTR encryption per chunk, ordered encrypted-data hashing, part tracking, finalization, and Drive metadata registration.

## Important APIs, Types, and Functions
Sizing helpers are `checkUploadChunkSize`, `SetUploadChunkSize`, `checkUploadCutoff`, and `SetUploadCutoff`. `internxtChunkWriter` stores the `Fs`, remote/source, upload session, completed parts, target size, parent directory ID, final metadata, chunk size, hash sequencing state, and pending encrypted chunk buffers. Methods include `OpenChunkWriter`, `WriteChunk`, `recordCompletedPart`, `submitForHashing`, `Close`, and `Abort`. `hashWriter` adapts session hashing to `io.Writer`.

## Control Flow
`OpenChunkWriter` rejects files below cutoff, calculates chunk size for known-size files, warns once for streaming uploads, ensures the parent directory exists, creates a `buckets.ChunkUploadSession`, and returns writer info with configured concurrency.

`WriteChunk` creates a cipher stream at the chunk byte offset, encrypts plaintext into an in-memory multipart buffer, uploads the encrypted chunk through the session, records the ETag/part number, then rewinds the encrypted buffer and submits it for ordered hashing. `submitForHashing` feeds chunks to the session hash only when all prior chunks have been processed; out-of-order chunks are held in `pendingChunks`.

`Close` fails if pending hash buffers remain, sorts completed parts, calls `session.Finish`, then creates Internxt Drive file metadata with AES version `03-aes`, parent directory, original name/ext, size, and modtime. `Abort` closes pending buffers and logs.

## State and Persistence
Remote state includes uploaded encrypted chunks, finalized bucket object, and created Drive metadata. Local state includes part list, pending buffers, ordered hash cursor, and final `meta` consumed by `Object.Update`. Memory use scales with chunk size, upload concurrency, and out-of-order hash backlog.

## Dependencies and Integration Points
Uses Internxt `buckets`, rclone `fs`, `chunksize`, `multipart`, and `pool`. It is invoked by `multipart.UploadMultipart` through `Fs.OpenChunkWriter` in `Object.Update`.

## Risks and Edge Cases
`Abort` logs but does not call a remote abort/delete API, so failed multipart sessions may leave remote temporary state depending on SDK behavior. Hash correctness depends on every encrypted chunk being replayed in byte order; pending buffer leaks are guarded in `Close` but still fatal. Streaming uploads are bounded by max parts times chunk size. Memory pressure can be high for large chunks and concurrent out-of-order completion.

## Test Signals
The integration test config explicitly requires chunked uploads with multiple chunks. There are no local unit tests for ordered hash buffering, chunk-size validation, final metadata creation, or abort cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/internxt/upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/jottacloud/api/types.go -->
# sources/user-network-fs/rclone/backend/jottacloud/api/types.go

## Purpose
Defines shared Jottacloud API data models and XML/JSON time helpers for both classic XML endpoints and newer JSON endpoints.

## Important APIs, Types, and Functions
Time helpers include `jottaTimeFormat`, `unmarshalXMLTime`, `JottaTime`, and `Rfc3339Time`, with XML marshal/unmarshal and RFC3339 JSON marshal for the latter. Auth/config models include `LoginToken`, `WellKnown`, and `TokenJSON`. Newer JSON upload/account models include `AllocateFileRequest`, `AllocateFileResponse`, `UploadResponse`, `DeviceRegistrationResponse`, `CustomerInfo`, and `TrashResponse`.

Classic XML models include `Flag`, `DriveInfo`, `JottaDevice`, `JottaMountPoint`, `JottaFolder`, `JottaFile`, and `Error`. `Flag` marks an XML attribute as present during unmarshalling, mainly for deleted flags. `Error.Error` formats Jottacloud error responses.

## Control Flow
XML time unmarshalling decodes element text, returns zero time for empty strings, and parses either Jottacloud's classic `2006-01-02-T15:04:05Z0700` format or standard RFC3339 depending on wrapper type. XML structs map nested account/device/mountpoint/folder/file responses into Go fields. JSON structs are plain DTOs for OAuth/device/upload/account endpoints.

## State and Persistence
This file stores no runtime state. It defines serialization contracts used by higher-level Jottacloud API code. Zero times represent empty XML time elements, which is important for mountpoints and folders that may omit modification times.

## Dependencies and Integration Points
Uses standard `encoding/xml`, `errors`, `fmt`, and `time`. Backend API callers depend on these models for unmarshalling remote responses and marshaling request times.

## Risks and Edge Cases
`TokenJSON.ExpiresIn` is `int32` despite a comment that some providers return strings, so string values would need custom handling elsewhere or fail unmarshalling. `Flag.MarshalXMLAttr` always returns an error and is explicitly not for use. `JottaTime.String` formats zero time as year 1 rather than an empty string, which is acceptable only if callers avoid marshaling absent times. Metadata structs model only selected response fields.

## Test Signals
`types_test.go` covers one important XML edge case: empty `<modified></modified>` unmarshals to zero time without error. There are no tests for RFC3339 time, JSON token oddities, `Flag`, or error formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/jottacloud/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/jottacloud/api/types_test.go -->
# sources/user-network-fs/rclone/backend/jottacloud/api/types_test.go

## Purpose
Provides a focused regression test for Jottacloud XML time parsing when a mountpoint response contains an empty modification time.

## Important APIs, Types, and Functions
`TestMountpointEmptyModificationTime` builds a sample `<mountPoint>` XML document, unmarshals it into `JottaFolder`, and asserts `ModifiedAt` is zero.

## Control Flow
The test feeds XML with `<modified></modified>` into `xml.Unmarshal`. This exercises `JottaTime.UnmarshalXML` through `unmarshalXMLTime`, which treats an empty string as zero time and nil error.

## State and Persistence
No persistent state. The XML fixture is embedded in the test.

## Dependencies and Integration Points
Uses standard `encoding/xml`, `testing`, and `time`. It validates the behavior required by real Jottacloud mountpoint/folder responses that can include empty modification fields.

## Risks and Edge Cases
The test unmarshals into `JottaFolder` despite the fixture being a mountpoint; this works because the fields under test overlap, but it does not validate `JottaMountPoint` directly. It does not test non-empty classic time values, invalid time strings, or `Rfc3339Time`.

## Test Signals
The key signal is that empty XML times must stay non-fatal and become zero values. This protects listing code from failing on mountpoints with blank modification timestamps.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/jottacloud/api/types_test.go -->

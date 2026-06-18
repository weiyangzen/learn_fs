# Research: subset-b-009738

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/b2/b2.go -->
# sources/user-network-fs/rclone/backend/b2/b2.go

## Purpose
This file is the main rclone backend implementation for Backblaze B2. It registers the `b2` remote, parses configuration, authorizes the account, exposes the `fs.Fs` and `fs.Object` interfaces, maps rclone paths to B2 buckets and object names, and implements listing, object metadata, direct uploads, server-side copy, deletion/hiding, public links, lifecycle commands, and cleanup commands. Large-file upload and multipart copy mechanics are delegated to `upload.go`, but this file decides when to use them.

## Important APIs, types, and functions
`Options` captures backend configuration: account/key, endpoint, version and point-in-time listing flags, hard-delete mode, upload and copy cutoffs, chunk size and concurrency, checksum control, download URL/auth duration, lifecycle defaults, encoding, and SSE-C fields. `Fs` holds the active backend state: wrapped REST client, B2 authorization response, bucket existence cache, bucket ID/type maps, reusable upload URL cache, pacer, and upload concurrency token dispenser. `Object` stores per-object path, B2 file ID, modtime, SHA1, size, and MIME type.

`NewFs` validates configuration, normalizes root, configures SSE-C keys, creates the REST client and pacer, authorizes the account, handles application keys restricted to buckets, detects root paths that are actually files, and advertises features such as bucket support, MIME type read/write, and chunk writer support. `authorizeAccount` calls `/b2_authorize_account`, then sets the API root and authorization header.

Path and cache helpers include `parsePath`, `split`, `getBucketID`, `getbucketType`, `listBucketsToFn`, `setBucketID`, `clearBucketID`, `setBucketType`, and `clearBucketType`. `getUploadURL`, `returnUploadURL`, and `clearUploadURL` manage reusable upload URLs per bucket ID. `getRW` and `putRW` couple buffer allocation with an upload token.

Listing is centered on `list`, which calls `b2_list_file_names` or `b2_list_file_versions`, applies root/prefix filtering, version-at filtering, directory delimiter handling, and callback delivery. `itemToDirEntry`, `listDir`, `listBuckets`, `ListP`, and `ListR` adapt this to rclone listings. Version mode appends version timestamps to duplicate remotes and hides `hide` markers from normal entries.

Mutation APIs include `Put`, `PutStream`, `Mkdir`, `makeBucket`, `Rmdir`, `hide`, `deleteByID`, `purge`, `Purge`, `CleanUp`, `cleanUp`, `copy`, `Copy`, `OpenChunkWriter`, and `Remove`. `Update` handles direct upload, streaming unknown-size upload, and multipart upload dispatch. It stores modtime in `x-bz-info-src_last_modified_millis`, computes or appends SHA1 as required, sets MIME type, and applies SSE-C headers when configured.

Object metadata and read APIs include `newObjectWithInfo`, `NewObject`, `getMetaDataListing`, `getMetaData`, `readMetaData`, `decodeMetaDataRaw`, `decodeMetaData`, `decodeMetaDataFileInfo`, `ModTime`, `SetModTime`, `Hash`, `Size`, `Open`, `getOrHead`, `MimeType`, and `ID`. `openFile` verifies full reads by length and SHA1 when EOF is reached.

Backend commands are exposed through `Command`: `lifecycle` reads or writes bucket lifecycle rules, `cleanup` removes stale unfinished multipart uploads, and `cleanup-hidden` removes old hidden versions. `PublicLink` builds download URLs and appends a temporary download authorization token for private/snapshot buckets.

## Control flow and behavior
Startup flows from config parsing to authorization, then optionally bucket restriction validation and file-root detection. Listing starts by splitting an rclone remote into bucket and B2 object prefix. Root listing enumerates buckets, while bucket listings use B2 list APIs with delimiter or recursive mode. `VersionAt` changes the listing source to versions and suppresses versions newer than the configured timestamp, returning only the first visible version per B2 name.

Upload flow first ensures the bucket exists. Unknown-size uploads buffer one configured chunk to decide between direct upload and streaming large upload. Known-size uploads above `UploadCutoff` go through `multipart.UploadMultipart` and `OpenChunkWriter`; smaller uploads use B2 upload URL reuse and a single `/b2_upload_file` request. If the source lacks a SHA1, the body is wrapped in `hashAppendingReader` semantics from `upload.go` by setting `X-Bz-Content-Sha1: hex_digits_at_end` and extending content length. Server-side copy uses `/b2_copy_file` below `CopyCutoff` and large multipart copy above it.

Deletion follows B2 semantics: normal remove hides objects unless `HardDelete` is enabled; versioned remotes with a specific version suffix delete that file version; `VersionAt` rejects modification. Purge and cleanup list versions and delete in parallel using configured transfers, while respecting `operations.SkipDestructive`.

## State and persistence
Persistent remote state lives in B2 buckets, object versions, file metadata, lifecycle rules, and B2 large-file start markers. Local runtime state is in memory: bucket creation/existence cache, bucket ID/type maps guarded by mutexes, reusable upload URLs guarded by `uploadMu`, authorization data guarded by `authMu`, pacer state, and upload tokens. Object modtime is persisted as B2 file info under `src_last_modified_millis`; SHA1 for large files may be persisted under `large_file_sha1`; SSE-C secrets are config-derived and sent as headers/body fields rather than persisted locally by this code.

## Dependencies and integration points
The backend integrates with rclone interfaces from `fs`, accounting, `operations`, `list`, `multipart`, `bucket.Cache`, `encoder`, `pacer`, `pool`, and `rest`. It depends on `backend/b2/api` request/response types. It uses B2 Native API endpoints for authorization, bucket listing/creation/deletion/update, object listing, upload URL acquisition, direct upload, download by ID/path, hide/delete version, copy file, download authorization, lifecycle updates, and cleanup. The feature table advertises optional interfaces consumed by rclone core: purging, server-side copy, streaming upload, recursive/partial listing, public links, chunk writing, clean-up, and backend commands.

## Risks and edge cases
B2 version behavior is subtle: `--b2-versions` and `--b2-version-at` make writes unsafe and are explicitly blocked in write paths, but listing and metadata selection must still avoid returning hidden/deleted current versions incorrectly. Upload URL reuse must clear bad URLs on retryable upload failures or subsequent uploads can fail repeatedly. Direct uploads with `hex_digits_at_end` depend on correct content-length adjustment and reader behavior. Custom download URLs can omit native B2 headers or content length, so metadata fallback to listing values is important. Bucket names are globally unique, so duplicate bucket creation must verify ownership. Cleanup deletes versions in parallel and must respect dry-run/interactive destructive guards.

SSE-C support requires consistent algorithm/key/md5 handling across upload, download, and copy; mismatched handling can make objects unreadable. `getOrHead` can return an open response body, so errors after the call must close bodies correctly. `PublicLink` validates existence using both object lookup and a directory-style listing path, and private bucket links require `shareFiles` permission plus a valid auth duration. `Shutdown` is not implemented for this backend, so long-lived state is mostly request-local.

## Test signals
`b2_test.go` runs the generic fstests suite against `TestB2:` and advertises chunked upload settings plus setter interfaces for upload/copy cutoff testing. `b2_internal_test.go` exercises B2-specific URL encoding, B2 millisecond modtime encoding/decoding, metadata propagation through direct and large uploads, versioned listing and object lookup, point-in-time listing, cleanup of hidden versions, cleanup of unfinished large uploads, dry-run behavior, and lifecycle command behavior. Interface assertions at the bottom verify the advertised rclone feature contracts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/b2/b2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/b2/b2_internal_test.go -->
# sources/user-network-fs/rclone/backend/b2/b2_internal_test.go

## Purpose
This file contains B2-specific internal tests that supplement the generic rclone backend integration tests. The tests validate Backblaze-specific URL encoding, metadata and modtime storage, large-file metadata behavior, object version semantics, point-in-time views, cleanup of hidden versions and unfinished large uploads, and lifecycle command behavior.

## Important APIs, types, and functions
`encodeTest` enumerates B2 string encoding expectations from the Backblaze Native API documentation. `TestUrlEncode` validates `urlEncode`. `TestTimeString` and `TestParseTimeString` cover millisecond epoch conversion used for `x-bz-info-src_last_modified_millis`.

`OpenOptionToMetaData` strips `x-bz-info-` prefixes from `fs.OpenOption` headers for test comparison. `internalTestMetadata` is the main metadata test helper; it can change upload chunk size and cutoff via test-only setters, uploads randomized gzipped content with MIME type, metadata, and B2 info headers, then reads B2 metadata back and checks content type, upload time, modtime, SHA1, size, and download content. `InternalTestMetadata` runs that helper for a direct-sized object and a chunked large object.

`InternalTestVersions` creates, deletes, and recreates a file to generate B2 versions. It tests `--b2-versions` listing and version suffix reads, building a new Fs from a versioned file path, `--b2-version-at` listings before/after upload/delete/reupload timestamps, cleanup dry-run, and actual cleanup. `InternalTestCleanupUnfinished` creates unfinished large-file start markers with `newLargeUpload`, then validates dry-run and real cleanup. `listAllFiles` and `checkListing` are helpers for version/start-marker listings. `InternalTestLifecycleRules` reads, dry-runs, and applies lifecycle command changes. `InternalTest` registers the file's internal subtests with the generic fstests internal tester hook.

## Control flow and behavior
The tests are designed to run against a real B2 remote prepared by rclone's integration test framework. Metadata tests configure backend cutoffs to force direct or multipart paths, then use fstests helpers to upload and remove objects. Version tests intentionally sleep between operations so B2 upload timestamps differ enough for comparisons and version suffix generation. Cleanup tests run both dry-run and destructive paths and compare listings before and after. Lifecycle tests use the backend command implementation directly with option maps representing CLI `-o` values.

## State and persistence
The tests create real B2 objects, hidden versions, unfinished large-upload markers, and lifecycle rules. They mutate `f.opt.Versions`, `f.opt.VersionAt`, upload chunk size, and upload cutoff in-process, using defers to restore version flags where needed. Cleanup and lifecycle tests deliberately alter remote state and depend on test isolation from `fstests`.

## Dependencies and integration points
The file integrates with `fstest`, `fstests`, `fs/cache`, B2 `api` types, `bucket.Join`, `version.Remove`, rclone `object.NewStaticObjectInfo`, and `stretchr/testify` assertions. It exercises package-private B2 functions and methods, so it is in package `b2` rather than `b2_test`.

## Risks and edge cases
Timing sensitivity is a central risk: sleeps are used to avoid timestamp ambiguity, but remote clock or API latency could still affect version-at boundaries. Lifecycle tests assume an initial no-rule state and then modify bucket rules, which can conflict with pre-existing bucket configuration if tests are run against a reused remote. Cleanup tests are destructive by design and rely on dry-run checks and isolated paths. The metadata test stores only `mtime` from generic metadata because B2 metadata support is limited in this backend.

## Test signals
These tests provide direct coverage for code paths that generic fs tests cannot fully observe: B2-specific percent encoding, B2 metadata headers, large upload metadata, version suffix lookup, `VersionAt`, cleanup of old/hidden/start versions, and lifecycle command option parsing/application. The final interface assertion ensures `*Fs` implements `fstests.InternalTester`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/b2/b2_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/b2/b2_test.go -->
# sources/user-network-fs/rclone/backend/b2/b2_test.go

## Purpose
This file wires the B2 backend into rclone's generic integration test suite and exposes test-only setter methods so fstests can exercise variable chunk and cutoff behavior.

## Important APIs, types, and functions
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestB2:"`, a nil object prototype, and `ChunkedUploadConfig` requiring B2's minimum chunk size and multiple chunks. `SetUploadChunkSize`, `SetUploadCutoff`, and `SetCopyCutoff` wrap the unexported backend setters from `b2.go` for the test harness. Interface assertions confirm `*Fs` implements `fstests.SetUploadChunkSizer`, `fstests.SetUploadCutoffer`, and `fstests.SetCopyCutoffer`.

## Control flow and behavior
The generic test runner creates and manipulates files on the configured `TestB2:` remote, relying on the backend's advertised rclone interfaces. The setter methods let tests lower cutoffs or adjust chunk sizes to force multipart upload and multipart copy without changing production API visibility.

## State and persistence
The file itself stores no state. Test execution mutates the in-memory `Fs` upload/copy size fields and creates remote B2 test data through fstests.

## Dependencies and integration points
It depends on `github.com/rclone/rclone/fstest/fstests` for generic backend behavior tests and on `fs.SizeSuffix` for configuration setter types. It is package-local, so it can access unexported constants such as `minChunkSize` and object type `Object`.

## Risks and edge cases
The tests require a configured real remote named `TestB2:` and can be affected by B2 rate limits, eventual consistency, permissions, bucket lifecycle settings, and account-specific behavior. The explicit `NeedMultipleChunks` setting documents that the B2 chunked upload path requires multiple chunks for the generic chunked upload tests.

## Test signals
This is the top-level integration entry point for B2. Passing it signals the backend satisfies generic filesystem operations, while the setter assertions signal fstests can tune size thresholds to cover multipart behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/b2/b2_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/b2/upload.go -->
# sources/user-network-fs/rclone/backend/b2/upload.go

## Purpose
This file implements Backblaze B2 large-file uploads and multipart server-side copies. It handles starting/canceling/finishing B2 large files, uploading or copying parts with SHA1 tracking, buffering streaming input, concurrency control, and cleanup on failure.

## Important APIs, types, and functions
`hashAppendingReader` wraps a reader and appends the hex digest of all prior bytes after EOF. B2 uses this when `X-Bz-Content-Sha1` is `hex_digits_at_end`. `AdditionalLength` returns the appended digest length and `HexSum` returns the digest once the original stream has ended.

`largeUpload` stores all state for a B2 large upload or multipart copy: parent `Fs`, destination `Object`, operation kind, input reader and accounting wrapper, large-file ID, total size/part count, per-part SHA1 list guarded by mutex, reusable part upload URLs guarded by mutex, chunk size, source object for copy, and final file info.

`newLargeUpload` calculates chunk size and part count, resolves bucket ID, builds `b2_start_large_file` metadata including modtime, MIME type, custom `x-bz-info-*` headers, optional whole-file SHA1 metadata, and SSE-C config, then starts the large file. It unwraps accounting so buffered chunks can be accounted only when actually uploaded.

`getUploadURL` and `returnUploadURL` manage reusable B2 part upload URLs for a single large file. `addSha1` records part checksums in order. `WriteChunk` uploads one part by seeking to find size, rewinding on retry, appending the part SHA1 to the body, and calling the part upload URL. `copyChunk` calls `/b2_copy_part` for a byte range from the source object. `Close` calls `/b2_finish_large_file` with ordered SHA1s and captures returned metadata. `Abort` calls `/b2_cancel_large_file`.

`Stream` uploads unknown-size input by starting with an already-read first buffer, then reading additional chunk buffers and uploading each chunk in an errgroup. `Copy` performs multipart copy with an errgroup limited to configured upload concurrency and transfer accounting.

## Control flow and behavior
Known-size large upload setup calculates a safe chunk size with `chunksize.Calculator`, respecting B2's maximum part count. Unknown-size streaming uses the configured chunk size and fails if the stream exceeds the maximum part count. Large upload start stores metadata before parts are sent. Each part upload obtains a part upload URL, wraps the chunk for accounting, sends SHA1 at the end of the request body, and records the resulting SHA1 for finish. Retryable part failures clear the bad upload URL and let the pacer retry.

`Stream` reads one chunk at a time into pooled buffers while launching uploads concurrently; it stops early if the errgroup context is canceled. `Copy` computes byte ranges and submits `/b2_copy_part` requests up to `UploadConcurrency`. Both paths defer `Abort` through `atexit.OnError`, so unfinished large files are canceled when the operation returns an error.

## State and persistence
Remote persistent state includes the started B2 large file, uploaded parts, copied parts, final file version, or canceled large-file marker. Local state includes buffered chunks, part upload URL cache, SHA1 slice, errgroup context, and final response. The file relies on `Fs` upload token and pooled buffer management from `b2.go` for memory/concurrency limits.

## Dependencies and integration points
This file is invoked by `Object.Update`, `Fs.copy`, and `Fs.OpenChunkWriter` in `b2.go`, and by the generic multipart package through the `fs.ChunkWriter` interface implemented by `largeUpload` methods. It depends on B2 API types, rclone accounting, chunk-size calculation, pool buffers, transfer accounting, pacer/rest, and `golang.org/x/sync/errgroup`.

## Risks and edge cases
The SHA1 list must be complete and ordered; missing entries make finish fail or produce corrupt metadata. `WriteChunk` requires an `io.ReadSeeker`, so callers must provide seekable buffers. The streaming loop checks `part > maxParts`, which allows part number `maxParts` before failing and should be interpreted carefully against B2's 1..10000 limit. Retrying requires rewind and URL invalidation; failure to clear bad upload URLs can poison later attempts. Large uploads must be aborted on any failure or B2 start markers remain until cleanup. Memory pressure can be high because chunk size times transfer concurrency determines buffered data.

## Test signals
Coverage is indirect through `b2_test.go` generic chunked upload tests and `b2_internal_test.go` metadata, unfinished-upload cleanup, and large-size metadata tests. The `OpenChunkWriter` integration in `b2.go` also gives generic multipart tests a path into `largeUpload.WriteChunk` and `Close`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/b2/upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/box/api/types.go -->
# sources/user-network-fs/rclone/backend/box/api/types.go

## Purpose
This file defines the JSON request, response, and error types used by the Box backend. It isolates Box API schema details from the backend implementation and provides small helpers for Box time and error formatting.

## Important APIs, types, and functions
`Time` wraps `time.Time` for Box RFC3339 JSON encoding and decoding. `Error` models Box error responses and implements `error`, including status, code, context info, help URL, message, and request ID.

`ItemFields` lists the Box item fields requested by the backend. Item constants define folder/file types and active/trashed/deleted statuses. `ItemMini` is used for compact conflict and parent references. `Item` models files and folders, including IDs, sequence IDs, etags, SHA1, names, sizes, timestamps, status, parent, shared links, and owner. `Item.ModTime` prefers `content_modified_at` and falls back to `modified_at`.

`FolderItems` models paged folder listing and upload result responses. Request bodies include `Parent`, `CreateFolder`, `UploadFile`, `PreUploadCheck`, `UpdateFileModTime`, `UpdateFileMove`, `CopyFile`, `CreateSharedLink`, `UploadSessionRequest`, and `CommitUpload`. Multipart types include `UploadSessionResponse`, `Part`, and `UploadPartResponse`.

JWT configuration types `ConfigJSON`, `AppSettings`, and `AppAuth` model Box App config JSON. `User` models `/users/me` quota/user data. `FileTreeChangeEventTypes`, `Event`, and `Events` model Box change event responses used by `ChangeNotify`.

## Control flow and behavior
This file has little runtime control flow. JSON marshal/unmarshal methods translate Box time values. `Error.Error` builds readable error strings. `Item.ModTime` selects the best modification time for rclone object metadata. The backend uses the type definitions in REST calls and relies on struct tags for JSON mapping.

## State and persistence
These types represent Box remote state: files, folders, upload sessions, parts, shared links, users, app credentials, and events. They do not persist local state themselves.

## Dependencies and integration points
The file is imported by `backend/box/box.go` and `backend/box/upload.go`. It depends only on Go `encoding/json`, `fmt`, and `time`. Its request/response shapes must match Box API behavior for folder listing, pre-upload conflict detection, uploads, multipart sessions, JWT app auth, trash cleanup, user quota, and event polling.

## Risks and edge cases
`Item.Size` is `float64` because Box can return very large numbers in exponent notation; converting to `int64` later can lose precision if values exceed integer precision. `FolderItems.Order` is intentionally commented out because Box has returned inconsistent shapes. `Time.UnmarshalJSON` expects RFC3339 and will reject other Box timestamp shapes. `PreUploadCheckConflict.ContextInfo` depends on Box's conflict JSON shape. Event filtering depends on `FileTreeChangeEventTypes` staying current with Box event names that affect file trees.

## Test signals
There are no direct tests for these schema types in the listed files. They are exercised indirectly by Box integration tests, upload flows, pre-upload checks, quota calls, multipart upload commits, and change notification event parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/box/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/box/box.go -->
# sources/user-network-fs/rclone/backend/box/box.go

## Purpose
This file implements the main rclone backend for Box. It registers the `box` remote, supports OAuth2, access-token, and JWT app authentication, maps rclone paths to Box folder/file IDs, implements listing and metadata lookup, upload/update dispatch, directory creation/removal, server-side copy/move, public links, trash cleanup, quota reporting, change notifications from Box events, and rclone feature/interface declarations.

## Important APIs, types, and functions
Auth helpers include `usesJWTAuth`, `refreshJWTToken`, `getBoxConfig`, `getClaims`, `getSigningHeaders`, `getQueryParams`, and `getDecryptedPrivateKey`. They load Box app config from config contents or a file, decrypt the PKCS8 private key, build JWT claims, and configure token refresh.

`Options` stores upload cutoff, commit retry count, encoding, root folder ID, access token, list chunk size, owner filtering, and impersonation. `ItemMeta` caches sequence ID, parent ID, and name by Box item ID for change notification path reconstruction. `Fs` stores the wrapped REST client, dir cache, pacer, token renewer, upload token, and item metadata cache. `Object` stores rclone path, metadata-loaded flag, size, modtime, Box file ID, shared link, and SHA1.

`NewFs` configures auth and REST clients, validates upload cutoff, sets authorization or `as-user` headers, creates token renewers, initializes `dircache.DirCache`, handles file-root detection, and fills feature flags. `readMetaDataForPath` resolves a path through the directory cache and pre-upload conflict check, then fetches full file metadata. `errorHandler` converts Box error JSON into `api.Error`.

Directory and listing methods include `FindLeaf`, `CreateDir`, `listAll`, `ListP`, `Mkdir`, `Rmdir`, and `purgeCheck`. `listAll` pages through `/folders/{id}/items` with marker pagination, filters by type, active status, and owner, decodes names, and calls a callback. `ListP` converts folder items to rclone directories/objects, caches directory IDs, and updates `itemMetaCache`.

Object creation/mutation APIs include `createObject`, `preUploadCheck`, `Put`, `PutStream`, `PutUnchecked`, `deleteObject`, `Copy`, `Move`, `DirMove`, `Object.Update`, `Object.upload`, `Object.Remove`, `Object.Open`, `Object.SetModTime`, and metadata helpers. Large multipart upload is delegated to `upload.go`.

Other backend APIs include `About`, `PublicLink`, `deletePermanently`, `CleanUp`, `Shutdown`, `ChangeNotify`, `changeNotifyStreamPosition`, `getFullPath`, `changeNotifyRunner`, `DirCacheFlush`, and `Hashes`.

## Control flow and behavior
Startup selects auth mode. JWT mode refreshes a token during configuration and may start a renewer that refreshes through JWT; OAuth mode creates an oauth client and can renew by probing metadata; access-token mode simply sets the bearer header. `NewFs` then resolves the configured root folder. If root resolution fails, it tries the parent as an Fs root and returns `fs.ErrorIsFile` if the original path is a file.

Path resolution depends on `dircache`: directories are identified by Box folder IDs rather than paths. Listing finds a directory ID, pages folder items, caches subfolder IDs, converts files to `Object`, and records item metadata for future event processing. Uploads first resolve/create parent directories. `Put` uses Box's pre-upload check to decide whether to create or update a file; conflicts with folders produce `fs.ErrorIsDir`. `Object.Update` chooses simple multipart/form upload at or below cutoff and upload-session multipart above cutoff.

Copy uses Box server-side copy and works around Box's case-insensitive name handling and destination conflicts by copying to a temporary name, deleting the existing file, then moving the temp file into place. Move and DirMove call Box update endpoints for files or folders. Remove sends files to trash; `CleanUp` enumerates trash and permanently deletes files/folders concurrently.

`ChangeNotify` polls Box `/events`. It fetches the current stream position, then on each poll retrieves change events, filters duplicate event IDs, filters unsupported event types, compares sequence IDs to cached item metadata, invalidates directory cache entries for renamed/moved/deleted folders, reconstructs old and new paths when possible, and calls rclone notify callbacks once per path.

## State and persistence
Remote persistent state is Box files, folders, file versions, shared links, trash, and upload sessions. Local runtime state includes directory path-to-ID cache, item metadata cache for event handling, OAuth/JWT token renewer state, upload concurrency tokens, and REST/pacer state. `root_folder_id` allows the whole backend to be rooted at a non-root Box folder. Shared link URLs and SHA1/modtime/size/ID are cached in `Object` metadata.

## Dependencies and integration points
This file integrates with rclone `fs` optional interfaces, `dircache`, `oauthutil`, `jwtutil`, `encoder`, `rest`, `pacer`, `fshttp`, and Box API schema types. It uses the Box API roots `https://api.box.com/2.0` and `https://upload.box.com/api/2.0`. It also integrates with `fstests` through `box_test.go`, with `upload.go` for multipart sessions, and with rclone change-notification consumers such as VFS.

## Risks and edge cases
Box is case-insensitive and restricts file names, so copy/move paths must guard same-name case collisions and encoding constraints. `getDecryptedPrivateKey` type-asserts the parsed key to `*rsa.PrivateKey`; malformed config or non-RSA keys can panic if parsing succeeds with another type. `Shutdown` unconditionally calls `f.tokenRenewer.Shutdown()` and can panic if no token renewer was created. `listAll` uses `ListChunk` directly; values outside Box's documented 1..1000 range depend on config validation elsewhere. `Size` and `ModTime` use `context.TODO` or return current time on metadata read failure, which can hide errors from callers. Change notification path reconstruction is best-effort and only works for parents already in the directory cache.

Multipart/simple upload behavior depends on Box commit consistency and retry semantics in `upload.go`. Trash cleanup launches goroutines for each listed item with checker-limited concurrency; it reports only a count of failures, not all detailed errors. Access-token and impersonation modes rely on headers set at construction and do not refresh unless a token source exists.

## Test signals
`box_test.go` runs the generic rclone integration suite against `TestBox:`. There are no listed Box-specific unit tests for JWT auth, change notification, conflict copy handling, or trash cleanup. Interface assertions at the bottom document the intended rclone feature surface: purger, streamer, copier, abouter, mover, dir mover, dir cache flusher, public linker, cleaner, partial lister, shutdowner, object, and ID provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/box/box.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/box/box_test.go -->
# sources/user-network-fs/rclone/backend/box/box_test.go

## Purpose
This file connects the Box backend to rclone's generic filesystem integration test suite.

## Important APIs, types, and functions
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestBox:"` and a nil object prototype of `*box.Object`.

## Control flow and behavior
The generic fstests suite performs standard remote filesystem operations against a configured Box remote. Because the test package is `box_test`, it exercises Box through exported backend behavior rather than package-private helpers.

## State and persistence
The file itself has no persistent state. Test execution creates and removes data on the configured `TestBox:` remote.

## Dependencies and integration points
It imports the Box backend package and rclone `fstests`. It depends on external test configuration that defines `TestBox:`.

## Risks and edge cases
Coverage is broad but generic. It does not directly target Box-specific JWT auth, event polling, owner filtering, impersonation, upload-session commit retries, conflict-copy workaround, or trash cleanup. Integration runs can be affected by Box account limits, permissions, eventual consistency, and configured root folder.

## Test signals
Passing this test indicates the Box backend works with rclone's standard Fs/Object contract for the configured remote. It is the only test signal in the listed Box files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/box/box_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/box/upload.go -->
# sources/user-network-fs/rclone/backend/box/upload.go

## Purpose
This file implements Box multipart upload sessions for files above the backend upload cutoff. It creates sessions, uploads content parts with digest and byte-range headers, commits sessions with part manifests and whole-file digest, retries eventually consistent commits, aborts failed sessions, and updates object metadata from the committed result.

## Important APIs, types, and functions
`createUploadSession` calls Box upload-session creation endpoints, choosing the new-file endpoint with folder ID/name or the existing-file-version endpoint when `Object.id` is set. `sha1Digest` formats SHA1 bytes as an RFC3230-style `Digest` header.

`uploadPart` computes a SHA1 for a chunk, builds a `Content-Range`, wraps the chunk for accounting, and PUTs it to `/files/upload_sessions/{sessionID}`. `commitUpload` posts the ordered parts and content timestamps to `/commit`, sends the whole-file digest, handles `202 Accepted` with `Retry-After`, tolerates transient `parts_mismatch`, and retries up to configured `CommitRetries`. `abortUpload` deletes an upload session. `uploadMultipart` orchestrates the full session lifecycle.

## Control flow and behavior
`uploadMultipart` starts a session, records Box's server-chosen part size, defers session abort on error, unwraps accounting from the input, then reads exact chunks sequentially into byte slices. It updates the whole-file SHA1 sequentially while launching goroutines to upload each chunk. Upload concurrency is controlled by the `Fs.uploadToken` token dispenser. Uploaded part descriptors are stored by part index and later sent to `commitUpload`. After commit, it requires exactly one returned item and calls `setMetaData` on the object.

`commitUpload` loops until Box returns `200 OK` or `201 Created`, or retry budget is exhausted. It sleeps between accepted/not-ready responses or transient parts-mismatch failures. The error message mentions increasing low-level retries, but the actual limit comes from `--box-commit-retries`.

## State and persistence
Remote state includes the Box upload session, uploaded parts, final file or file version, and possibly an aborted session. Local state includes the session response, in-memory part buffers, ordered `api.Part` slice, whole-file SHA1 hash, error channel, wait group, and upload-token accounting. No chunks are persisted locally by this file.

## Dependencies and integration points
This file is called from `Object.Update` in `box.go` when `src.Size()` exceeds `UploadCutoff`. It depends on Box API schema types, rclone accounting, rest client behavior, pacer retry classification, and `atexit.OnError` for abort-on-failure cleanup.

## Risks and edge cases
`uploadMultipart` requires a known non-negative size; unknown-size `PutStream` still routes through `Put` and may not be suitable for multipart if size exceeds cutoff but is unknown. Every part is read fully into memory before upload, so memory use is roughly part size times active goroutines plus read-ahead. The goroutine closure captures `buf` by reference from the loop; because `buf` is redeclared each iteration it is intended to be distinct, but this pattern is worth care when refactoring. Commit consistency is explicitly handled with retry/sleep loops, but long Box delays can still exhaust `CommitRetries`. Abort runs only on returned error; process death can leave sessions server-side.

## Test signals
Multipart behavior is exercised indirectly by the generic Box integration test when file sizes exceed cutoff. There are no listed unit tests for digest formatting, accepted/parts-mismatch retry behavior, abort failure handling, or concurrent part upload ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/box/upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/cache.go -->
# sources/user-network-fs/rclone/backend/cache/cache.go

## Purpose
This file implements rclone's deprecated `cache` backend, a virtual wrapper around another remote that caches directory/object metadata and file chunks locally. It registers the backend, builds the wrapped remote, configures persistent DB and chunk storage, optional Plex integration, optional temporary upload staging, RC commands, change notification propagation, and most wrapper `fs.Fs` operations.

## Important APIs, types, and functions
Configuration constants define default chunk size, total chunk budget, cleanup interval, info age, read retries, worker count, memory-cache behavior, request rate limit, write caching, temp upload delay, and DB wait time. `Options` maps all cache settings, including wrapped remote, Plex credentials/token, chunk and DB paths, purge-on-start, workers, RPS, store-writes, temp upload path, temp wait, and DB wait.

`Fs` embeds the wrapped `fs.Fs` and stores wrapper/root/config/features, a `Persistent` cache handle, optional temp fs, cleanup timing/mutex/channel, rate limiter, Plex connector, background upload runner, upstream notification callbacks, and notification bookkeeping.

`NewFs` is the constructor. It emits the deprecation warning, validates chunk budget against worker/chunk size, rejects self-wrapping, resolves the wrapped remote via `fs/cache.Get`, handles file-root errors, opens the persistent DB/chunk store with `GetPersistent`, configures Plex, starts temp upload background runner when enabled, starts periodic chunk cleanup, subscribes to wrapped change notifications, fills masked feature flags, registers RC commands, and returns `fs.ErrorIsFile` when wrapping a file root.

RC helpers include `httpStats`, `httpExpireRemote`, and `rcFetch`. `httpExpireRemote` expires cached file or directory metadata and optionally chunks. `rcFetch` parses chunk slice syntax and prefetches selected chunks for named files, including crypt-aware filename unwrapping.

Core Fs methods include `Name`, `Root`, `Features`, `String`, `ChunkSize`, `InfoAge`, `TempUploadWaitTime`, `NewObject`, `List`, `ListR`, `Mkdir`, `Rmdir`, `DirMove`, `Put`, `PutUnchecked`, `PutStream`, `Copy`, `Move`, `Hashes`, `Purge`, `CleanUp`, `About`, `Stats`, `CleanUpCache`, `StopBackgroundRunners`, `UnWrap`, `WrapFs`, `SetWrapper`, `MergeDirs`, `DirCacheFlush`, `GetBackgroundUploadChannel`, `UserInfo`, `Disconnect`, `Shutdown`, and `Command`.

Change-notification helpers include `receiveChangeNotify`, `notifyChangeUpstreamIfNeeded`, `notifyChangeUpstream`, `ChangeNotify`, `isNotifiedRemote`, and crypt-aware `unwrapRemote`. Write helpers include `cacheReader` and the internal `put` dispatcher.

## Control flow and behavior
Startup wraps the configured source remote at the requested root, then creates local DB and chunk directories. The persistent cache stores source-tree entries keyed by the cache root plus remote path. If temp uploads are enabled, writes first land in a local temp fs and are queued for a background uploader; otherwise writes go directly to the wrapped remote, optionally teeing data through `cacheReader` to store chunks as they are uploaded.

`NewObject` first looks for a warm object in the persistent cache and checks `InfoAge`. If stale or missing, it probes the temp fs first when enabled, then the wrapped source, converts the original object to a cache object, persists it, and returns it. `List` similarly tries a warm cached directory listing, merges queued temp-upload objects, lists the source, removes cache entries no longer present in source, persists source objects and directories, updates directory metadata timestamp, and returns cached entries. `ListR` delegates to the wrapped `ListR` when possible while caching returned entries, otherwise recursively calls cache `List`.

Directory mutations call through to the wrapped fs or temp fs as needed, then update/expire cache entries and notify upstream wrappers. `Rmdir` and `DirMove` pause the background uploader when temp uploads are enabled to avoid moving/deleting files mid-upload. They inspect both source and temp fs, reject operations when temp uploads have started, update pending-upload metadata, and reconcile temp-upload queues.

`put` is the shared upload path. With temp upload enabled, it expires the parent, writes to temp fs, queues the destination in the persistent pending-upload table, and returns a cached object. With `StoreWrites`, it tees the input into local chunks while uploading to the wrapped remote. Otherwise it delegates directly. In all cases it removes stale cached object/chunks, persists the new object, expires the parent directory, and notifies upstreams.

`Copy` and `Move` require source objects to be cache objects wrapping the same underlying remote. They refresh the source from the true remote, handle temp-file special cases, call the wrapped feature method, then update/remove/expire cache state around source and destination parents. `Purge` purges local cache at root and delegates to wrapped purge. `CleanUp` trims chunk storage and delegates wrapped cleanup. `openRateLimited` is used by object read code outside this file to throttle source opens.

## State and persistence
The cache backend has substantial local persistent state: a DB file under `<db_path>/<remote>.db`, chunk files under `<chunk_path>/<remote>`, pending upload metadata for temp writes, cached directory entries, cached object metadata, cached chunks, and cleanup timestamps. Remote persistent state remains owned by the wrapped fs. Runtime state includes background cleanup goroutine, optional background upload runner, Plex websocket connector, rate limiter, registered RC commands, notification subscribers, and a map of recently notified remotes. `atexit` closes Plex, background runners, and the persistent DB.

## Dependencies and integration points
This file integrates with rclone config, fs feature masking/wrapping, `fs/cache` remote construction/pinning, `rc` remote-control calls, `walk`, `crypt` wrapper detection, `Persistent` cache APIs, `Object`/`Directory` helper types from sibling cache files, Plex connector code, background writer code, and `golang.org/x/time/rate`. It also receives change notifications from the wrapped fs and forwards invalidations to upstream wrappers such as VFS.

## Risks and edge cases
The backend is deprecated and complex. Stale metadata risk is governed by `InfoAge`; writes through other clients or remotes require change notifications or manual expiry. Temp upload mode introduces race risks around move/delete while background uploads are pending or started, requiring pause/play and pending queue reconciliation. `StopBackgroundRunners` sends on `cleanupChan`; because the channel has capacity one, repeated calls can block if not drained. The constructor registers global RC calls for each cache Fs instance, which can be surprising in multi-remote processes. `Purge` only purges all local cache for `dir == ""` and has a FIXME about root prefixes. `Shutdown` delegates to the wrapped fs but does not call `StopBackgroundRunners`, so lifecycle depends on atexit or explicit stop in some paths.

Path normalization and crypt wrapping are delicate: RC expiry/fetch may receive encrypted or decrypted names, and `cleanRootFromPath` assumes the path starts with the root before slicing. Cache invalidation after source listings removes stale entries by comparing sorted remotes, but temp-upload overlays can hide source entries. `List` has a TODO around empty cached directories. `MergeDirs` removes dirs by `dir.Remote()` rather than the absolute cache path pattern used elsewhere, which may need scrutiny against `Persistent.RemoveDir` expectations.

## Test signals
No cache tests are listed in this work item. Interface assertions document the intended wrapper surface: purger, copier, mover, dir mover, unchecked/streaming put, cleaner, unwrapper/wrapper, recursive lister, change notifier, abouter, user info, disconnect, commander, merge dirs, and shutdown. Behavior is likely covered elsewhere by cache backend tests and generic wrapper tests, but this file itself has no local test harness in the requested set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cache/cache.go -->

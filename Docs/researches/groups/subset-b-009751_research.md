# Research: subset-b-009751

Grouped research for rclone backends under `oracleobjectstorage`, `pcloud`, `pikpak`, `pixeldrain`, and the Premiumize.me API type definitions. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file outputs.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/oracleobjectstorage.go -->
# sources/user-network-fs/rclone/backend/oracleobjectstorage/oracleobjectstorage.go

## Purpose
This is the primary rclone backend implementation for Oracle Cloud Infrastructure Object Storage on supported platforms. It registers the `oracleobjectstorage` remote with prefix `oos`, exposes bucket-oriented filesystem behavior, and connects rclone's `fs.Fs` and `fs.Object` interfaces to the OCI Go SDK `objectstorage.ObjectStorageClient`.

## Important APIs, Types, and Functions
`Fs` stores the remote name/root, parsed `Options`, OCI client, bucket root split, bucket existence cache, and rclone pacer. `NewFs` parses config, validates SSE-C options, constructs the OCI client, initializes a pacer that mostly relies on OCI SDK retries, fills backend features, and handles the "root points to a file" rclone convention. `setUploadChunkSize`, `setUploadCutoff`, and `setCopyCutoff` are test/control hooks for chunked uploads and server-side copy thresholds. `List`, `ListP`, `ListR`, `list`, `listDir`, and `listBuckets` implement non-recursive and recursive listing over either the account bucket root or a specific bucket/prefix. `Mkdir`, `makeBucket`, `bucketExists`, `Rmdir`, `CleanUp`, `cleanUp`, `cleanUpBucket`, and `abortMultiPartUpload` manage buckets and unfinished multipart uploads. `Put` and `PutStream` delegate object creation to `Object.Update`, while `Metadata` exposes OCI object metadata through rclone's metadata surface.

## Control Flow
Initialization flows from config parsing to client creation, pacer setup, root parsing, feature filling, and optional file-root detection. Listing splits rclone paths into bucket and object prefix, lists buckets when no bucket is selected, or uses `ListObjects` with prefix/delimiter paging when inside a bucket. Recursive listing removes the delimiter and feeds every object summary through `itemToDirEntry`. Bucket creation uses `bucket.Cache.Create` so multiple calls do not repeatedly create or probe the same bucket. Cleanup first discovers pending uploads through command helpers in the same package, then aborts uploads older than the supplied age unless rclone destructive-operation policy skips them.

## State and Persistence
The backend keeps only process-local state: `root`, `rootBucket`, `rootDirectory`, the bucket cache, feature table, and the pacer. Persistent state lives in the remote service: buckets, objects, user metadata, storage tier, and multipart upload records. `Metadata` maps internal meta fields back to rclone metadata, translating the swift-style mtime metadata to RFC3339 and exposing content type and birth time from last-modified information. Bucket existence is cached but can be stale after external mutation or immediate bucket deletion.

## Dependencies and Integration Points
The file integrates rclone `fs`, `list`, `operations`, `bucket.Cache`, and `pacer` with Oracle's `oci-go-sdk/v65/objectstorage` and `common` packages. Metadata behavior also depends on helper functions/constants from adjacent files such as `metadataWithOpcPrefix`, `storageTierMap`, `metaMtime`, `metaMD5Hash`, `shouldRetry`, and `newObjectStorageClient`. Copy, multipart upload, commands, storage tier, and object update/open behavior are implemented across other files in the same backend.

## Risks and Edge Cases
Root listing cannot change region for buckets and treats OCI 301 responses as empty when no bucket is configured, which avoids hard failure but can hide inaccessible buckets. `newObjectWithInfo` appears to assign the decoded MD5 only when `base64ToMd5` returns an error, which is suspicious and should be checked against the actual helper semantics. Directory markers with zero size are skipped, so empty logical directories depend on object-prefix behavior rather than first-class directories. `cleanUp` logs cleanup failures only through a branch that checks the wrong `err` variable after `cleanErr`, which may suppress per-bucket cleanup errors. No-auth provider cannot list buckets and must be rooted directly at public bucket content.

## Test Signals
The integration test file exercises this backend through `fstests.Run`, including storage tiers and chunked upload configuration. This file also declares interface satisfaction for `fs.Fs`, `fs.Copier`, `fs.PutStreamer`, `fs.ListRer`, `fs.ListPer`, `fs.Commander`, `fs.CleanUpper`, and `fs.OpenChunkWriter`, making compile-time interface drift visible.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/oracleobjectstorage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/oracleobjectstorage_test.go -->
# sources/user-network-fs/rclone/backend/oracleobjectstorage/oracleobjectstorage_test.go

## Purpose
This file wires the Oracle Object Storage backend into rclone's standard integration test suite. It also exposes backend-specific setters needed by `fstests` to vary upload chunk size, upload cutoff, and copy cutoff.

## Important APIs, Types, and Functions
`TestIntegration` calls `fstests.Run` with remote name `TestOracleObjectStorage:`, storage tiers `standard` and `archive`, a nil object sentinel, and minimum chunk size configuration. `SetUploadChunkSize`, `SetUploadCutoff`, and `SetCopyCutoff` delegate to unexported backend setters. Compile-time assertions ensure `Fs` implements `fstests.SetUploadChunkSizer`, `fstests.SetUploadCutoffer`, and `fstests.SetCopyCutoffer`.

## Control Flow
The test suite is entirely driven by `fstests.Run`. During chunked upload and copy tests, the suite can call the setter interfaces to temporarily adjust backend thresholds, then restore previous values using the returned old setting.

## State and Persistence
Tests operate against a real configured remote, so persistent buckets/objects can be created, modified, tiered, or deleted in the OCI account behind `TestOracleObjectStorage:`. The setter methods mutate the in-memory `Fs.opt` fields only.

## Dependencies and Integration Points
The file depends on rclone's `fstests` package and the backend constants such as `minChunkSize`. It is coupled to the main backend's unexported setter methods.

## Risks and Edge Cases
Integration tests require real credentials, namespace, compartment, and bucket permissions. Archive-tier tests can be slow or constrained by OCI archive restore semantics. Setter methods are test-only surface and should remain simple wrappers so test behavior stays aligned with production validation.

## Test Signals
This file is itself the main signal for backend conformance. It verifies that the backend can satisfy rclone's common filesystem contract and that chunked upload knobs are test-controllable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/oracleobjectstorage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/oracleobjectstorage_unsupported.go -->
# sources/user-network-fs/rclone/backend/oracleobjectstorage/oracleobjectstorage_unsupported.go

## Purpose
This file provides a minimal buildable package for unsupported platforms: Plan 9, Solaris, and JavaScript/WASM. It prevents Go from reporting "no buildable Go source files" when the main backend is excluded by build tags.

## Important APIs, Types, and Functions
There are no runtime APIs. The file contains only build tags and the `package oracleobjectstorage` declaration with package documentation.

## Control Flow
No control flow exists. Selection is entirely compile-time via `//go:build plan9 || solaris || js`.

## State and Persistence
No state or persistence behavior exists.

## Dependencies and Integration Points
The file has no imports. It integrates only with Go's build constraint system and the package naming expected by rclone's backend tree.

## Risks and Edge Cases
Any source accidentally added without matching build tags could reintroduce unsupported-platform build failures. This file should remain dependency-free.

## Test Signals
The signal is successful package discovery/build on unsupported targets. There are no unit tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/oracleobjectstorage_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/waiter.go -->
# sources/user-network-fs/rclone/backend/oracleobjectstorage/waiter.go

## Purpose
This file implements a generic state waiter used by the Oracle Object Storage backend to wait for asynchronous OCI operations, notably work requests from server-side object copy. It resembles Terraform-style `StateChangeConf` logic but is local to this backend.

## Important APIs, Types, and Functions
`StateRefreshFunc` is a callback returning a result object, current state string, and error. `StateChangeConf` configures delay, pending and target states, timeout, minimum timeout, explicit polling interval, not-found tolerance, and required continuous target occurrences. `WaitForStateContext` runs the refresh loop and returns the target result or a structured error. `NotFoundError`, `UnexpectedStateError`, and `TimeoutError` provide typed failures with `Unwrap` support.

## Control Flow
`WaitForStateContext` starts a goroutine that waits for `Delay`, then repeatedly sends the last result, waits with exponential backoff or `PollInterval`, calls `Refresh`, and classifies the state. A nil result can be success when the target list is empty, otherwise it increments not-found retries. Matching target states must occur continuously for the configured count. Pending states reset the target occurrence counter. The caller loop watches refresh results, context cancellation, and timeout; after timeout it cancels the goroutine but gives it a 30-second grace period to return a final success.

## State and Persistence
All state is transient: retry counts, target occurrence count, last result, and calculated wait duration. There is no persisted data.

## Dependencies and Integration Points
The implementation depends on `context`, `time`, `slices`, `strings`, `fmt`, and rclone `fs.Errorf` for timeout grace logging. The copy helper in the OCI backend constructs a `StateChangeConf` to poll OCI work request lifecycle states.

## Risks and Edge Cases
The goroutine sends to a buffered result channel before each wait and after refresh; changes to buffer size or receive behavior could deadlock. `UnexpectedStateError.Error` formats `LastError` with `%s`, so a nil `LastError` would render awkwardly. `time.After` is used repeatedly, which is fine for bounded polling but can create avoidable timers in long waits. The timeout grace period can extend total wait time beyond the configured timeout.

## Test Signals
No direct unit tests are present for the waiter. Coverage comes indirectly from OCI copy tests or integration behavior that waits for work requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/waiter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pcloud/api/types.go -->
# sources/user-network-fs/rclone/backend/pcloud/api/types.go

## Purpose
This file defines JSON-facing API types for the pCloud backend. It centralizes response schemas, pCloud's timestamp format, embedded error handling, item metadata, upload/file operation responses, public link responses, quota responses, and diff responses.

## Important APIs, Types, and Functions
`Time` marshals/unmarshals pCloud timestamps using RFC1123Z wrapped in JSON quotes. `Error` represents pCloud's `result`/`error` response pattern, implements `error`, and `Update` converts either transport errors or nonzero API result codes into Go errors. `Item` models files/folders and includes `ModTime`, which falls back from `Modified` to `Created`. Other important response types are `ItemResult`, `Hashes`, `FileOpenResponse`, `FileChecksumResponse`, `FilePWriteResponse`, `UploadFileResponse`, `GetFileLinkResult`, `ChecksumFileResult`, `PubLinkResult`, `UserInfo`, and `DiffResult`.

## Control Flow
The types are passive, but `Error.Update` is called after most REST calls in `pcloud.go` and `writer_at.go`, determining whether API-level failures become retryable errors. `GetFileLinkResult.IsValid` checks host presence and link expiry with a 30-second safety margin, and `URL` selects the first host.

## State and Persistence
No local state is persisted. These structs mirror remote pCloud state such as IDs, folder contents, hashes, quotas, public links, diff IDs, and upload descriptors.

## Dependencies and Integration Points
The file depends only on `fmt` and `time`. It is consumed by the pCloud backend and writer-at code through rclone's `rest.Client.CallJSON` decoding.

## Risks and Edge Cases
The timestamp format is strict; API format drift will break unmarshal. `GetFileLinkResult.URL` always selects the first host and does not rotate hosts. `DiffResult.Entries` uses `[]map[string]any`, so downstream change-notify parsing is type-assertion heavy and can silently skip malformed entries.

## Test Signals
There is no direct unit test for this API package. Integration tests exercise decoding indirectly through listing, upload, hash, quota, and change notification flows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pcloud/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pcloud/pcloud.go -->
# sources/user-network-fs/rclone/backend/pcloud/pcloud.go

## Purpose
This is the main pCloud rclone backend. It registers the `pcloud` remote, handles OAuth and region-specific host selection, maps pCloud folders/files into rclone directory and object interfaces, and implements listing, upload, server-side copy/move, cleanup, public links, quota, hashes, and change notifications.

## Important APIs, Types, and Functions
`Options` stores encoding, root folder ID, hostname, and optional username/password used only for trash cleanup. `Fs` keeps OAuth token source, REST clients, directory cache, pacer, token renewer, and last diff ID. `Object` stores remote path, metadata, pCloud ID, hashes, and cached download link. `NewFs` constructs OAuth REST clients, fills features, initializes `dircache`, starts token-renewal support, and handles file-root detection. `shouldRetry` handles HTTP retry codes, pCloud 4xxx/5xxx API classes, expired tokens, and nonretryable result 1101. Directory methods include `FindLeaf`, `CreateDir`, `listAllRootRecursive`, `listAll`, `listHelper`, `ListP`, and `ListR`. Data methods include `Put`, `Object.Update`, `Open`, `Hash`, `SetModTime`, `Copy`, `Move`, `DirMove`, `PublicLink`, `About`, `CleanUp`, and `ChangeNotify`.

## Control Flow
Configuration first updates the OAuth token endpoint using the chosen pCloud hostname; the OAuth callback persists the hostname returned by pCloud. `NewFs` builds an OAuth REST client, optional password cleanup client, and `dircache` rooted at `root_folder_id`. Listing resolves a directory ID and calls `/listfolder`; recursive listing at the pCloud root has a special two-step flow because pCloud rejects `folderid=0&recursive=1`. Uploads require known size, disable chunked transfer encoding, set `Content-Length`, and use multipart POST for zero-length files. Server-side copy/move creates the destination path, calls `/copyfile`, `/renamefile`, or `/renamefolder`, then updates object metadata from the response. Change notification polls `/diff`, keeps the latest diff ID, resolves changed parent IDs through `dircache`, and emits rclone notifications for cached paths.

## State and Persistence
Persistent state is in pCloud: files, folders, hashes, trash, public links, and diff stream state. Local in-memory state includes `dircache`, cached object metadata/hash fields, cached download links, OAuth token renewal state, and `lastDiffID`. Config persistence occurs during OAuth setup when hostname is saved. Cleanup requires separate username/password because the pCloud trash API does not support OAuth in this implementation.

## Dependencies and Integration Points
The backend integrates with rclone `fs`, `config`, `oauthutil`, `dircache`, `encoder`, `pacer`, `rest`, and hash interfaces. It consumes schemas from `backend/pcloud/api`. It relies on pCloud endpoints including `/listfolder`, `/createfolder`, `/uploadfile`, `/copyfile`, `/renamefile`, `/renamefolder`, `/getfilelink`, `/checksumfile`, `/userinfo`, `/trash_clear`, and `/diff`.

## Risks and Edge Cases
pCloud does not accept uploads without a content length, so streaming is not supported by `Object.Update`. Recursive root listing needs a workaround for API result 1101. Cleanup silently disappears as a feature unless username/password are configured. `downloadURL` caches links and relies on the API expiry field. Change notifications only resolve changes whose parent directories are already known in `dircache`, so unseen paths may be ignored. `OpenWriterAt` logic is present as `XOpenWriterAt` but intentionally not exposed because pCloud fileops started returning access denied.

## Test Signals
The integration test runs rclone's standard backend suite against `TestPcloud:`. Compile-time assertions cover optional interfaces such as purger, cleanup, copier, mover, dir mover, dir cache flusher, public linker, list pager/recursive lister, abouter, shutdowner, change notifier, object, and IDer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pcloud/pcloud.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pcloud/pcloud_test.go -->
# sources/user-network-fs/rclone/backend/pcloud/pcloud_test.go

## Purpose
This file connects the pCloud backend to rclone's integration test harness.

## Important APIs, Types, and Functions
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestPcloud:"` and `NilObject: (*pcloud.Object)(nil)`.

## Control Flow
The file delegates all behavior to the shared `fstests` suite. It does not define backend-specific setup or option mutation.

## State and Persistence
Tests run against the real configured `TestPcloud:` remote, so they can create and remove folders/files in that account. There is no local persistent test state.

## Dependencies and Integration Points
The file imports the backend package externally as `pcloud_test`, which verifies public package usability rather than relying on unexported internals. It depends on `github.com/rclone/rclone/fstest/fstests`.

## Risks and Edge Cases
Coverage depends on credentials and pCloud API availability. Since no special skips are configured here, backend quirks must be handled in production code or shared fstest expectations.

## Test Signals
The main signal is full rclone filesystem conformance under `fstests.Run`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pcloud/pcloud_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pcloud/writer_at.go -->
# sources/user-network-fs/rclone/backend/pcloud/writer_at.go

## Purpose
This file implements an experimental/random-access writer for pCloud's fileops API. It is currently not exposed as an rclone feature because `pcloud.go` leaves `XOpenWriterAt` disabled by naming and comments note pCloud access-denied responses.

## Important APIs, Types, and Functions
`writerAt` implements `fs.WriterAtCloser` with `WriteAt` and `Close`. `fileOpenNew`, `fileOpen`, `fileChecksum`, `filePWrite`, and `fileClose` wrap pCloud `/file_open`, `/file_checksum`, `/file_pwrite`, and `/file_close` endpoints. `newSingleConnClient` in `pcloud.go` is essential because pCloud file descriptors are bound to a single TCP connection.

## Control Flow
`XOpenWriterAt` creates an empty target file, closes the initial descriptor, and returns a `writerAt` with the resulting file ID. Each `WriteAt` opens the file on a single-connection client, calculates SHA1 of the input buffer, asks pCloud for SHA1 of the destination range, skips writes when hashes match, writes changed ranges with `/file_pwrite`, and closes the descriptor. `Close` repeatedly fetches the object via a different connection to confirm the final size, sleeping between attempts.

## State and Persistence
The writer stores target size, remote path, and pCloud file ID. Remote state is the partially or fully written pCloud file. There is no local cache beyond each buffer and single-connection REST client.

## Dependencies and Integration Points
The file depends on pCloud API response types, rclone `fs`, `rest.Client`, SHA1 hashing, and URL parameter construction. It integrates with `Fs.newSingleConnClient`, `dirIDtoNumber`, `fileIDtoNumber`, and backend retry/error handling.

## Risks and Edge Cases
The fileops API requires connection affinity, so any transport change could break descriptors. `WriteAt` opens and closes a descriptor per chunk; if `fileChecksum` succeeds but `fileClose` fails after `filePWrite`, the caller receives a partial success with an error. `Close` cannot verify unknown sizes and falls back to a blind one-second sleep. The implementation is disabled because pCloud reportedly returns access denied for the creation mode.

## Test Signals
There are no direct tests. Potential coverage would require enabling `OpenWriterAt` and running rclone tests that exercise sparse/random writes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pcloud/writer_at.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pikpak/api/types.go -->
# sources/user-network-fs/rclone/backend/pikpak/api/types.go

## Purpose
This file defines the JSON schemas and helper methods for the PikPak backend. It covers files, folders, tasks, quota, sharing, upload tickets, resumable upload credentials, captcha tokens, OAuth token conversion, filters, and archive/decompression-related types.

## Important APIs, Types, and Functions
`Time` wraps RFC3339 timestamps and tolerates `null`/empty values on unmarshal. Constants define Drive kinds, phases, upload modes, thumbnail sizes, and list page size. `Error` and `ErrorDetails` model PikPak error responses. `Filters.Set` uses reflection to populate typed filter maps for list queries. `Link.Valid` validates download links, preferring the URL `expire` query parameter and falling back to the `Expire` field with a 10-second safety window. Core models include `File`, `FileList`, `Task`, `TaskList`, `Form`, `Resumable`, `ResumableParams`, `NewFile`, `NewTask`, `About`, `Share`, `User`, `VIP`, `RequestShare`, `RequestBatch`, `RequestNewFile`, `RequestNewTask`, `RequestDecompress`, `CaptchaToken`, `CaptchaTokenRequest`, and `Token`.

## Control Flow
Most types are passive decode targets. Active behavior appears in time marshal/unmarshal, filter construction, link validation, captcha token expiry checks, and token expiry conversion from `expires_in`. `Link.Valid` first parses URL query expiry because real PikPak links can have more reliable expiry embedded in the URL than in the JSON field.

## State and Persistence
No local persistence occurs in this file. The structs represent remote PikPak state and credentials. Captcha tokens include an `Expiry` field populated by helper code before being persisted to rclone config.

## Dependencies and Integration Points
The file depends on `fmt`, `net/url`, `reflect`, `strconv`, and `time`. It is consumed by `pikpak.go`, `helper.go`, and `multipart.go` for REST request/response encoding, retry classification, list filters, download link validation, and upload selection.

## Risks and Edge Cases
`Filters.Set` assumes field names are valid and map element types match the parsed value; invalid callers can panic through reflection. Many fields are `any` or partially documented, so API schema drift may be silently ignored. `Link.Valid` treats an expired URL query as authoritative even if the `Expire` field is future. `Token.Expiry` relies on local receipt time and does not account for clock skew beyond OAuth defaults elsewhere.

## Test Signals
`types_test.go` directly tests `Link.Valid` across nil, empty, future, expired, precedence, buffer, and fallback cases. Other types are tested indirectly through backend integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pikpak/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pikpak/api/types_test.go -->
# sources/user-network-fs/rclone/backend/pikpak/api/types_test.go

## Purpose
This file unit-tests PikPak download link validity logic.

## Important APIs, Types, and Functions
`TestLinkValid` table-tests `(*Link).Valid` with nil links, empty URLs, URL `expire` query values, fallback `Expire` fields, invalid query values, and the 10-second expiry buffer.

## Control Flow
Each table row constructs a link and expected boolean, then runs as a subtest. Cases verify that URL query expiry is preferred over the struct field when parseable, and that invalid/missing query expiry falls back to `Expire`.

## State and Persistence
There is no persistent state. The test uses `time.Now()` at execution time to generate future and past expiries.

## Dependencies and Integration Points
The file depends on `fmt`, `testing`, and `time`. It validates behavior used by `Object.Open` through `setMetaDataWithLink`.

## Risks and Edge Cases
Because expected times are relative to `time.Now()`, extremely slow or paused test execution around the 5-second buffer case could theoretically be flaky, though the one-hour cases are stable. The test does not cover malformed URLs where `url.Parse` itself fails.

## Test Signals
This is focused unit coverage for cached link expiry, a critical path for reusing or refreshing PikPak download links.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pikpak/api/types_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pikpak/helper.go -->
# sources/user-network-fs/rclone/backend/pikpak/helper.go

## Purpose
This file contains PikPak backend helper operations: API calls for users, VIP, tasks, shares, file metadata, decompression, GCID/CID hashing, captcha signing/token persistence, and a `pikpakClient` wrapper that injects captcha tokens into REST calls.

## Important APIs, Types, and Functions
Request helpers include `requestDecompress`, `getUserInfo`, `getVIPInfo`, `requestBatchAction`, `requestNewTask`, `requestNewFile`, `getFile`, `patchFile`, `getTask`, `waitTask`, `deleteTask`, `getAbout`, and `requestShare`. Hashing helpers include `getGcid`, `readGcid`, `calcGcid`, `unWrapObjectInfo`, and `calcCid`. Auth helpers include `genDeviceID`, `md5Sum`, `calcCaptchaSign`, `newCaptchaTokenRequest`, `CaptchaTokenSource`, `newCaptchaTokenSource`, `requestToken`, `refreshToken`, `Invalidate`, `Token`, `pikpakClient`, `newPikpakClient`, `SetCaptchaTokener`, `CallJSON`, and `Call`.

## Control Flow
Most request helpers build `rest.Opts`, call `f.rst.CallJSON` under the backend pacer, and delegate retry classification to `f.shouldRetry`. Batch actions return a task ID and then call `waitTask`, which sleeps briefly before requiring task completion. `getFile` retries while the application/octet-stream link is absent or invalid. `getGcid` first calculates a CID from source ranges and asks PikPak's resource API for a GCID; if unavailable, upload code computes GCID locally. `readGcid` either buffers the stream in memory or in an unlinked temp file while hashing so upload can replay the data. Captcha token flow loads an existing token from config, refreshes it with action-specific metadata when invalid, stores the refreshed JSON token back into the config mapper, and injects `x-captcha-token` into JSON calls.

## State and Persistence
Captcha tokens are persisted in rclone config under `captcha_token`. Device ID is generated and persisted elsewhere by `pikpak.go`. GCID buffering can create temporary files named with `rclone-pikpak-gcid-` for large streams; they are removed/unlinked and closed through cleanup. The helper layer otherwise works with remote persistent state: files, tasks, shares, quotas, and decompression jobs.

## Dependencies and Integration Points
The file depends on rclone `fs`, `configmap`, `fserrors`, `rest`, and backend `api` types. It uses standard crypto/hash packages and HTTP/URL utilities. It is tightly coupled to `Fs.rst`, `Fs.pacer`, `Options`, and `f.shouldRetry` from `pikpak.go`.

## Risks and Edge Cases
`getFile` assumes `info.Links.ApplicationOctetStream` is non-nil before calling `Valid`, which relies on actual API shape. `waitTask` uses a fixed short initial sleep and a retrying `getTask`, so long-running tasks depend on pacer retry policy. `readGcid` must always have its cleanup called to avoid temp-file leaks on platforms where unlinking an open file is not enough. Captcha token persistence through `configmap.Mapper.Set` may not flush to disk immediately depending on caller context. `genDeviceID` uses `math/rand`, which is fine for client identity but not cryptographic randomness.

## Test Signals
There are no direct helper tests for GCID/CID, captcha signing, or task waiting. These paths are exercised indirectly by PikPak integration tests and by the API link-validity unit test for the link refresh path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pikpak/helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pikpak/multipart.go -->
# sources/user-network-fs/rclone/backend/pikpak/multipart.go

## Purpose
This file implements PikPak resumable multipart uploads using the AWS S3 SDK against PikPak-provided Aliyun-style resumable credentials. It handles chunk buffering, concurrent upload, abort-on-error, and final multipart completion.

## Important APIs, Types, and Functions
`getPool` and `NewRW` manage a global rclone buffer pool for upload chunks. `pikpakChunkWriter` stores chunk size, total size, concurrency, source reader, completed S3 parts, S3 client, and multipart upload state. `Fs.newChunkWriter` creates the S3 client, computes effective chunk size, applies upload headers, and starts `CreateMultipartUpload`. `Upload` reads source chunks and uploads them concurrently. `WriteChunk` uploads a single part and records its ETag. `Abort` cancels the multipart upload. `Close` sorts completed parts and calls `CompleteMultipartUpload`.

## Control Flow
`Upload` creates a token dispenser for upload concurrency, unwraps accounting, reads up to `chunkSize` into pooled `pool.RW` buffers, and starts an errgroup goroutine per chunk. On any later error, an `atexit.OnError` callback cancels context and aborts the multipart session. `WriteChunk` seeks the buffer to determine size, rewinds it, and calls S3 `UploadPart`. Early chunks use normal retry classification; later chunks force at least retry behavior after errors. Completion waits for all goroutines, then finalizes the multipart upload.

## State and Persistence
Local transient state includes buffer pool pages, token counts, completed part slices protected by a mutex, and multipart upload IDs. Remote persistent state is the in-progress S3-compatible object upload in PikPak's storage provider. Abort is best-effort on upload errors.

## Dependencies and Integration Points
The file depends on AWS SDK v2 `s3` and `types`, rclone accounting, chunk-size calculator, pacer, pool, atexit, and PikPak `api.ResumableParams`. It is called by `Fs.uploadByResumable` in `pikpak.go`.

## Risks and Edge Cases
Memory usage scales with `--transfers * --pikpak-upload-concurrency * chunk_size`, with a global pool cache. Unknown-size streaming uploads are capped by chunk size times 10,000 parts. Completed parts must be sorted before finalization; this file does so in `Close`. Abort can fail and only logs from the error callback. Single-reader chunk staging means source read errors stop scheduling but already-started uploads can continue until context cancellation is observed.

## Test Signals
PikPak integration tests configure chunked upload min/max sizes, indirectly exercising this multipart path for files above the cutoff. No direct unit tests cover part ordering, abort, or retry behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pikpak/multipart.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pikpak/pikpak.go -->
# sources/user-network-fs/rclone/backend/pikpak/pikpak.go

## Purpose
This is the main PikPak rclone backend. It registers `pikpak`, handles username/password OAuth-like authorization plus captcha tokens, maps PikPak Drive files/folders into rclone interfaces, and implements listing, upload, server-side copy/move, trash cleanup, public links, quota/user info, and backend commands for offline downloads and decompression.

## Important APIs, Types, and Functions
`Options` stores credentials, device/user IDs, user agent, root folder, trash and media-link behavior, hash buffering threshold, chunk sizing, upload concurrency, and encoding. `Fs` stores REST client, HTTP client, dircache, pacer, config mapper, and token mutex. `Object` stores path, IDs, size, MIME type, parent, GCID, MD5, cached link, and link mutex. Auth/control functions include `pikpakAuthorize`, `newFs`, `NewFs`, `reAuthorize`, `shouldRetry`, `errorHandler`, `getClient`, and `newClientWithPacer`. Filesystem functions include `FindLeaf`, `listAll`, `itemToDirEntry`, `List`, `CreateDir`, `Mkdir`, `About`, `PublicLink`, `deleteObjects`, `untrashObjects`, `purgeCheck`, `CleanUp`, `moveObjects`, `renameObject`, `DirMove`, `Move`, `copyObjects`, `Copy`, `uploadByForm`, `newS3Client`, `uploadByResumable`, `upload`, `Put`, `UserInfo`, `Command`, and object methods including `Open`, `Update`, `upload`, `Hash`, `MimeType`, `ID`, `ParentID`, and `Remove`.

## Control Flow
Configuration ensures a token exists or runs `pikpakAuthorize`, which decodes the password, ensures a 32-character device ID, obtains captcha-backed signin token, and persists an OAuth token. `NewFs` parses options, validates chunk/cutoff, creates clients, derives user ID from the access token, sets captcha token handling, initializes `dircache`, and handles file-root detection. Listing builds JSON filters for phase, trash state, and kind, pages through `/drive/v1/files`, decodes names, and caches folder IDs. Upload first tries server-side GCID resolution via CID; if unavailable it computes GCID locally, requests a new file/upload ticket, returns early for instant uploads, otherwise uses resumable S3 singlepart or multipart upload, then waits for any task completion. Updating an existing object uploads to a temporary name, deletes the old object, then renames the temp object. Copy/move paths compensate for PikPak collision behavior by moving/copying by ID, locating resulting files, deleting or renaming conflicts, and rolling back when possible.

## State and Persistence
Persistent config state includes device ID, OAuth token, and captcha token. Remote persistent state includes files, folders, trash state, tasks, shares, quota, and upload sessions. Local state includes dircache mappings, cached object metadata/link, pacer state, and token mutex. GCID calculation may temporarily buffer source content in memory or disk via helpers. `UseTrash` controls whether deletes are permanent or move items to trash; `TrashedOnly` changes listing semantics.

## Dependencies and Integration Points
The backend integrates with rclone `fs`, `config`, `oauthutil`, `dircache`, `encoder`, `pacer`, `rest`, `random`, and AWS SDK v2 S3 clients. It consumes `backend/pikpak/api` schemas and helper/multipart functions. Remote endpoints span `user.mypikpak.com`, `api-drive.mypikpak.com`, and S3-compatible upload endpoints created from `ResumableParams`.

## Risks and Edge Cases
PikPak modtimes cannot be set, so precision is `ModTimeNotSupported` and syncs should not rely on remote modification time. The backend disables multithreaded downloads because media/original links can be restrictive. Collision handling during copy/move is complex and rollback may not perfectly restore names if PikPak auto-renames items. Updating deletes the old object before final rename, so a rename failure after delete leaves the new temp object and removed old object. Captcha and invalid refresh-token recovery mutate config at runtime. Uploads can be instant server-side transfers when GCID matches, so accounting needs explicit server-side marking.

## Test Signals
The integration test runs `fstests.Run` against `TestPikPak:` and exposes upload chunk size/cutoff setters. Compile-time assertions cover purger, cleanup, copier, mover, dir mover, commander, dir cache flusher, public linker, abouter, user info, object, MIME type, ID, and parent ID interfaces; `ListR`, `ChangeNotifier`, and `PutStreamer` are intentionally commented out.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pikpak/pikpak.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pikpak/pikpak_test.go -->
# sources/user-network-fs/rclone/backend/pikpak/pikpak_test.go

## Purpose
This file wires the PikPak backend into rclone's integration test suite and exposes upload sizing setters for chunked upload tests.

## Important APIs, Types, and Functions
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestPikPak:"`, a nil object sentinel, and chunked upload min/max sizes. `SetUploadChunkSize` and `SetUploadCutoff` delegate to backend setters. Compile-time assertions ensure `Fs` implements the corresponding fstest setter interfaces.

## Control Flow
The shared fstest suite drives backend behavior. During chunked upload scenarios, fstests can temporarily modify chunk size and upload cutoff through the setter methods.

## State and Persistence
The setters mutate only in-memory options. The integration test uses the configured `TestPikPak:` account and may create files, folders, trash entries, upload tasks, and shares depending on test coverage.

## Dependencies and Integration Points
The file depends on rclone `fs` and `fstests`, plus backend constants `minChunkSize` and `maxChunkSize`.

## Risks and Edge Cases
Tests require valid PikPak credentials and can be sensitive to captcha, quota, VIP/task limits, and remote API throttling. Since this backend has task-based side effects, failed tests may leave remote tasks or trashed files.

## Test Signals
The file provides integration-level filesystem conformance and validates that upload sizing constraints are externally adjustable for tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pikpak/pikpak_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pixeldrain/api_client.go -->
# sources/user-network-fs/rclone/backend/pixeldrain/api_client.go

## Purpose
This file is the low-level PixelDrain filesystem API wrapper for the rclone backend. It defines decoded API models, error normalization, retry handling, metadata-to-query mapping, path escaping, and REST helpers for upload, read, stat, change log, update, mkdir, rename, delete, and user info.

## Important APIs, Types, and Functions
Data models include `FilesystemPath`, `FilesystemNode`, `ChangeLog`, `ChangeLogEntry`, `UserInfo`, `SubscriptionType`, and `APIError`. Error sentinels include `errNotFound`, `errExists`, and `errAuthenticationFailed`. `apiErrorHandler` maps PixelDrain status codes to rclone errors. `shouldRetry` wraps context and HTTP retry classification. `paramsFromMetadata`, `nodeToObject`, `nodeToDirectory`, and `escapePath` adapt rclone paths and metadata. REST helpers are `put`, `read`, `stat`, `changeLog`, `update`, `mkdir`, `rename`, `delete`, and `userInfo`.

## Control Flow
API errors are decoded from JSON and the response body is closed immediately so higher-level handlers do not leak bodies on error. Paths are prefixed with the configured root and URL-escaped segment by segment. `put` sets `make_parents=true`, `stat` uses a `?stat` query so files return metadata rather than contents, `update` and `rename` use multipart params with action names, and `delete` optionally adds `recursive=true`. `rename` first validates that the source is a PixelDrain `Fs` with the same root folder ID, then posts a target path using the destination filesystem's prefix.

## State and Persistence
No independent local state is held here. It mutates remote PixelDrain filesystem nodes and exposes remote change logs. Metadata fields such as mtime, birth time, mode, shared state, and logging_enabled are sent as API parameters.

## Dependencies and Integration Points
The file depends on rclone `fs`, `fserrors`, `rest`, and standard HTTP/URL/JSON packages. It is called by `pixeldrain.go` to implement all high-level rclone interfaces.

## Risks and Edge Cases
`FilesystemPath.Base` trusts `BaseIndex`, so malformed API responses can panic. `escapePath` uses simple slash splitting and URL-escapes each segment, which is correct for ordinary paths but depends on `pathPrefix` invariants. `apiErrorHandler` returns `APIError.Error` as only the status code, losing message context unless callers inspect the concrete value. Change logs require server-side logging to be enabled and are limited by PixelDrain's retention semantics.

## Test Signals
No direct unit tests target this API wrapper. Integration tests exercise it through the high-level PixelDrain backend.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pixeldrain/api_client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pixeldrain/pixeldrain.go -->
# sources/user-network-fs/rclone/backend/pixeldrain/pixeldrain.go

## Purpose
This is the main PixelDrain Filesystem rclone backend. It registers the `pixeldrain` remote, configures API key access and root folder selection, exposes metadata support, and maps PixelDrain filesystem nodes into rclone directories, objects, change notifications, public links, quota, and server-side rename/move operations.

## Important APIs, Types, and Functions
`Options` stores API key, root folder ID, and API URL. `Fs` stores the root path, REST client, pacer, authentication flag, and normalized `pathPrefix`. `Object` wraps a `FilesystemNode`. `NewFs` parses config, sets metadata feature support, builds REST root URL, configures basic auth with the API key, verifies login for `me`, initializes path prefix, and handles file-root detection. High-level methods include `List`, `NewObject`, `Put`, `Mkdir`, `Rmdir`, `Purge`, `Move`, `DirMove`, `ChangeNotify`, `PutStream`, `DirSetModTime`, `PublicLink`, `About`, and object methods for metadata, hash, open, update, remove, MIME, size, and modtime.

## Control Flow
Initialization sets `pathPrefix` to `/<root_folder_id>/<root>/` and hides that prefix from rclone by stripping it from API responses and re-adding it to requests. Listing stats the directory, rejects file roots, and converts children into dirs or objects. Upload collects metadata from options/source, defaults `mtime` from source modtime, and delegates to `put`. Move and DirMove call the shared `rename` helper and translate incompatibility/not-found/exists errors into rclone interface errors. ChangeNotify enables logging for non-`/me/` roots, then polls `changeLog` at the interval supplied by rclone and emits object/directory notifications.

## State and Persistence
Persistent state is remote PixelDrain filesystem content, metadata, sharing state, and change logging state. Local state is limited to options, path prefix, REST client, pacer, and object node snapshots. `DirSetModTime`, `SetModTime`, `PublicLink`, and `Update` mutate remote metadata or sharing flags.

## Dependencies and Integration Points
The backend uses rclone `fs`, `configstruct`, `fshttp`, `hash`, `pacer`, and `rest`. It delegates all HTTP details to `api_client.go`. It supports SHA256 hashes and rclone metadata keys `mode`, `mtime`, and `btime`.

## Risks and Edge Cases
Unauthenticated access to `root_folder_id=me` is rejected, while shared roots can be accessed without login. ChangeNotify assumes the first interval value is available and immediately reads from the channel. `Update` mutates the object's local node before `Put`; if the remote upload fails, the object snapshot may temporarily contain desired rather than actual values. Public link generation rewrites `/api` to `/d/` in `APIURL`, which is simple but assumes the standard URL shape. PixelDrain rejects invalid UTF-8, reflected in tests.

## Test Signals
The integration test runs `fstests.Run` against `TestPixeldrain:` and skips invalid UTF-8 cases. Compile-time assertions cover filesystem, info, purge, move, dir move, change notify, put stream, dir modtime, public link, about, object, dir entry, MIME, and metadata interfaces.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pixeldrain/pixeldrain.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pixeldrain/pixeldrain_test.go -->
# sources/user-network-fs/rclone/backend/pixeldrain/pixeldrain_test.go

## Purpose
This file connects the PixelDrain backend to rclone's integration test harness.

## Important APIs, Types, and Functions
`TestIntegration` runs `fstests.Run` with `RemoteName: "TestPixeldrain:"`, a nil object sentinel, and `SkipInvalidUTF8: true`.

## Control Flow
All behavior is delegated to shared rclone filesystem tests. The only backend-specific control is skipping invalid UTF-8 because PixelDrain rejects it server-side.

## State and Persistence
The test uses a real configured PixelDrain filesystem and can create, update, share, and delete remote nodes. No local test state is persisted.

## Dependencies and Integration Points
The test imports `pixeldrain` externally and `fstests`, verifying public package integration.

## Risks and Edge Cases
Test reliability depends on API key validity, PixelDrain service availability, and root folder permissions. Invalid UTF-8 is explicitly skipped, so that behavior is documented but not expected to pass.

## Test Signals
The file provides integration-level conformance coverage for PixelDrain's rclone backend.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/pixeldrain/pixeldrain_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/premiumizeme/api/types.go -->
# sources/user-network-fs/rclone/backend/premiumizeme/api/types.go

## Purpose
This file defines API response and item types for the Premiumize.me backend. It provides shared response status handling plus schemas for folders, upload info, breadcrumbs, items, and account information.

## Important APIs, Types, and Functions
`Response` stores API `status` and optional `message`, implements `Error`, and `AsErr` returns nil only when status is `success`. Constants `ItemTypeFolder` and `ItemTypeFile` identify item kinds. `Item` models files/folders with breadcrumbs, IDs, links, stream links, size, type, transcode status, IP, and MIME type. `Breadcrumb`, `FolderListResponse`, `FolderCreateResponse`, `FolderUploadinfoResponse`, and `AccountInfoResponse` represent specific API responses.

## Control Flow
The only active logic is `Response.AsErr`, which converts unsuccessful API responses into errors for callers after JSON decoding. The rest of the file is passive data modeling.

## State and Persistence
No local state is persisted. The structs represent remote folder contents, upload tokens/URLs, and account quota/premium state.

## Dependencies and Integration Points
The file depends only on `fmt`. It is used by the Premiumize.me backend's REST client code to decode API responses and apply uniform error handling.

## Risks and Edge Cases
`AsErr` treats any status other than exact `"success"` as failure, so API status spelling changes would become hard errors. `AccountInfoResponse` uses floats for limit and space usage, which callers must interpret carefully as API-provided fractions/values. Several `Item` fields are always present in the struct even if only relevant for files.

## Test Signals
No direct tests are present for this schema file. Coverage is expected indirectly through the Premiumize.me backend tests and integration behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/premiumizeme/api/types.go -->

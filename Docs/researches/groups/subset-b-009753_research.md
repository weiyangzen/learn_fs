# subset-b-009753 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/s3.go -->
# sources/user-network-fs/rclone/backend/s3/s3.go

## Purpose
This file is the core rclone S3 backend. It registers the `s3` remote, defines the user-visible option surface, connects AWS SDK v2 clients, normalizes provider quirks, and implements the `fs.Fs` and `fs.Object` operations for bucket listing, recursive listing, object reads, object uploads, server-side copy, delete, purge, storage tiers, metadata, versioning, public links, and backend commands.

## Important APIs, Types, And Functions
The main configuration type is `Options`, which holds credentials, endpoint/region, SSE and SSE-C settings, requester-pays, transfer sizing, listing behavior, directory markers, gzip behavior, versioning, SDK logging, object lock, and provider-quirk tristates. `Fs` stores parsed options, root bucket/directory, the AWS `*s3.Client`, HTTP clients, bucket creation cache, pacer, feature flags, and versioning cache. `Object` stores the rclone remote, S3 object metadata, MD5/cache fields, version ID, storage class, HTTP system metadata, and Object Lock metadata.

`init` registers the backend, config wizard hook, metadata help, and a large option list. `NewFs` parses configuration, validates chunk/cutoff settings, normalizes SSE-C keys, creates the HTTP and S3 clients, applies provider quirks, builds features, detects file roots, and returns the initialized backend. `s3Connection` builds AWS SDK configuration from static, anonymous, environment, IBM IAM, or STS assume-role credentials; configures endpoint, dual-stack, path style, acceleration, v2 signing, data-integrity settings, request fixups, and SDK logging.

Listing is built around `bucketLister` with implementations for ListObjects v1, ListObjectsV2, and ListObjectVersions. `list` drives paginated listing, URL-encoding fallback on XML syntax failures, directory marker handling, version/delete-marker mapping, and callback delivery. `List`, `ListP`, and `ListR` adapt that into rclone directory entries. Uploads use `prepareUpload`, `uploadSinglepartPutObject`, `uploadSinglepartPresignedRequest`, `OpenChunkWriter`, `s3ChunkWriter.WriteChunk`, `s3ChunkWriter.Close`, and `uploadMultipart`. Server-side copy uses `copy`, `copyMultipart`, and `Copy`. Metadata flows through `headObject`, `readMetaData`, `setMetaData`, `Metadata`, and `SetModTime`.

Backend commands are exposed by `Command`: `restore`, `restore-status`, `list-multipart-uploads`, `cleanup`, `cleanup-hidden`, `versioning`, and `set`. Optional interfaces are declared at the end for purging, copying, streaming, recursive listing, chunk writing, metadata, MIME type, and tier support.

## Control Flow
Backend construction starts with config decoding and invariant checks, then creates a shared HTTP client with S3 redirect handling, builds the SDK client, applies quirk-derived defaults, and wires rclone feature flags. Most API operations run through `f.pacer.Call` or `CallNoRetry`; retry decisions combine context cancellation, Smithy API errors, S3 timeout codes, selected HTTP status codes, and generic rclone retry helpers. A 301 on bucket operations can trigger `updateRegionForBucket` when the backend is rooted in a bucket.

Read path: `NewObject` either uses listing metadata, resolves versioned paths through `getMetaDataListing`, or performs `HEAD`. `Open` builds `GetObjectInput`, applies range and HTTP options, adjusts Accept-Encoding middleware, and updates cached object metadata from the GET response. If `download_url` is configured, reads bypass SDK GET and use the REST client against the external URL while still synthesizing metadata from HTTP headers.

Write path: `Put` constructs an `Object` and calls `Update`. `Update` chooses multipart if size is unknown or above `UploadCutoff`; otherwise it prepares a `PutObjectInput` and uses either SDK `PutObject` or a presigned PUT. Multipart writes are delegated through rclone's multipart helper and this backend's `OpenChunkWriter`, which creates the multipart upload, writes parts with MD5 tracking, completes the upload, and returns ETag/version data. After upload, `Update` either synthesizes a HEAD result when `NoHead` is set and size is known, or fetches the object with `HEAD`, then verifies multipart ETag where enabled and applies Object Lock after-upload calls if requested.

Copy path: `Copy` prepares upload metadata from the source object, decides whether metadata replacement is required, and calls `copy`. `copy` fills destination/source/SSE/Object Lock fields and either sends `CopyObject` or runs `copyMultipart`, which creates a multipart upload, copies byte ranges concurrently with `errgroup`, tracks completed parts, and completes or aborts on error.

## State And Persistence Behavior
Persistent remote state lives in S3 buckets, objects, versions, delete markers, metadata, storage classes, multipart uploads, and Object Lock settings. Rclone-specific state is stored as object metadata: `mtime` records modtime and `md5chksum` stores MD5 when ETag cannot be trusted or multipart checksums are needed. Directory markers optionally persist empty folders as zero-byte trailing-slash objects.

In-memory state includes bucket existence cache, versioning tristate cache guarded by `versioningMu`, object metadata caches, and `sync.Once` warnings for compressed downloads and stream-upload size limits. `NoHead` intentionally relies on upload responses and local request data instead of immediately re-reading persisted object metadata. `VersionAt` mode is read-only for modification/deletion paths.

## Dependencies And Integration Points
The file depends heavily on AWS SDK v2 S3/ST​S/manager packages, Smithy middleware, rclone core `fs` interfaces, pacer, bucket utilities, encoder, list helpers, multipart helper, accounting/operations, REST helpers, Swift timestamp formatting, and provider definitions from adjacent S3 backend files. Generated helpers from `setfrom.go` bridge AWS SDK request/response structs. `v2sign.go` supplies the legacy signer when `v2_auth` is enabled.

Externally, this file integrates with AWS S3 and many S3-compatible providers through the provider quirk table, with rclone config and rc backend commands, with the metadata framework, and with generic transfer, check, purge, and test harness interfaces.

## Risks And Edge Cases
The option and provider matrix is broad; behavior can regress for non-AWS providers when defaults for path style, URL-encoded listings, `x-id`, Accept-Encoding signing, data integrity, multipart uploads, ETag trust, Object Lock, or ListObjectVersions ordering change. Version support is delicate because delete markers are represented as `ObjectVersion` values with `Size == isDeleteMarker`, and old-version names encode timestamps into paths. `Object.split` removes version suffixes, which the code comments note can misinterpret real file names under some version modes.

Object Lock support buffers entire single-part bodies to compute Content-MD5, which is correct for provider compatibility but can be memory-expensive for large single-part uploads near `UploadCutoff`. Single-part upload retry is deliberately disabled because readers are not generally rewindable. Multipart retry relies on `io.ReadSeeker` chunk readers and has special retry behavior after the first few chunks. In `uploadSinglepartPresignedRequest`, the `Date` response parse branch appears inverted (`lastModified` is assigned only when parsing returns an error), which may leave timestamps less useful on that path.

`download_url` synthesizes S3 metadata from arbitrary HTTP headers and depends on the configured URL already matching the bucket path layout. `NoHead` can miss server-side changes to metadata or size. `CleanUp` contains a suspicious condition in the loop (`if err != nil` after `cleanErr`) that could affect error propagation. Metadata validation drops invalid metadata keys/values, which is safer than sending bad headers but may surprise callers.

## Test Signals
Adjacent tests cover redirect token stripping, dual-stack options, retain-date parsing, internal metadata and gzip/decompression behavior, `NoHead`, version sorting/delete-marker merge, removal of `aws-chunked` content-encoding, version and version-at behavior, bucket creation quirk expectations, hidden-version cleanup, and Object Lock paths including retention, legal hold, after-upload API calls, multipart uploads, and presigned uploads. Generic rclone `fstests` exercise the backend interface against configured S3 remotes and directory marker config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/s3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/s3_internal_test.go -->
# sources/user-network-fs/rclone/backend/s3/s3_internal_test.go

## Purpose
This file contains S3 backend internal and integration-style tests that require a live backend instance. It validates metadata preservation, gzip handling, no-HEAD upload behavior, version listing semantics, delete marker merging, `aws-chunked` content-encoding cleanup, bucket-creation quirks, hidden-version cleanup, and S3 Object Lock support.

## Important APIs, Types, And Functions
Helper functions `gz` and `md5sum` build compressed test payloads and expected hashes. Methods on `*Fs` implement the `fstests.InternalTester` contract: `InternalTestMetadata`, `InternalTestNoHead`, `InternalTestVersions`, `InternalTestObjectLock`, and umbrella `InternalTest`. Standalone tests cover `versionLess`, `mergeDeleteMarkers`, and `removeAWSChunked`.

`InternalTestMetadata` writes an object with system metadata and user metadata, then reads it back through `Object.Metadata` and exercises downloads with and without `f.opt.Decompress`. `InternalTestVersions` enables bucket versioning, writes/removes/rewrites a file, then checks `--s3-versions`, `--s3-version-at`, version-suffixed object lookup, `NewFs` file-root detection, bucket already-exists quirk inference, and `CleanUpHidden`. `InternalTestObjectLock` creates a temporary Object Lock-enabled bucket and tests retention, legal hold, after-upload Object Lock APIs, multipart Object Lock upload, and presigned Object Lock upload.

## Control Flow
The tests mutate `f.opt` directly around subtests and restore settings with defers. Live S3 state is prepared by uploading objects with `fstests.PutTestContents` or direct SDK calls, then validated through normal backend methods. Version tests intentionally sleep between operations because AWS S3 LastModified precision may be one second. Object Lock tests create and later tear down a dedicated bucket, including explicit version/delete-marker cleanup with `DeleteObjects`.

## State And Persistence Behavior
These tests create real objects, object versions, delete markers, bucket versioning state, and an Object Lock-enabled temporary bucket. They use defers to remove objects, suspend versioning, reset backend options, clear legal holds, bypass governance retention for cleanup, and delete the temporary bucket. The tests also verify cached object metadata by clearing `o.meta` in the legal-hold subtest before re-reading.

## Dependencies And Integration Points
The file depends on rclone `fstest` and `fstests`, AWS SDK S3 types, Smithy API errors, bucket path helpers, random string generation, version path helpers, and testify assertions. It is tightly coupled to unexported backend internals such as `f.opt`, `setGetVersioning`, `pacer`, `rootBucket`, `setObjectLegalHold`, and the delete-marker sentinel.

## Risks And Edge Cases
Tests are provider-sensitive. Impossible Cloud and Cloudflare get special handling for metadata/gzip behavior. Object Lock tests skip when quirks say unsupported or when the provider accepts bucket flags without functional Object Lock. Direct mutation of `f.rootBucket` and options makes cleanup correctness important, especially under failures. Time-based version tests can be slow and rely on provider timestamp precision. The `removeAWSChunked` expectations intentionally remove spaces around remaining tokens when `aws-chunked` was present, so formatting changes in that helper may require test updates.

## Test Signals
This file is itself a major test signal for the backend. It complements generic `fstests` by checking behavior not fully covered by the public `fs.Fs` contract: provider metadata fidelity, version and delete-marker semantics, Object Lock API compatibility, and low-level helper behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/s3_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/s3_test.go -->
# sources/user-network-fs/rclone/backend/s3/s3_test.go

## Purpose
This file contains package-level tests for the S3 backend and wires the backend into rclone's generic integration test suite. It focuses on HTTP redirect security behavior, AWS dual-stack option mapping, generic backend conformance, directory marker config coverage, cutoff setter interfaces, and Object Lock retain-date parsing.

## Important APIs, Types, And Functions
`SetupS3Test` builds a minimal AWS-provider `Options` plus the backend HTTP client. Four redirect tests validate `s3CheckRedirect`: security tokens are stripped when a redirect crosses hosts, remain stripped for later redirects, are preserved for same-host redirects, and redirect loops stop after ten hops.

`TestIntegration` and `TestIntegration2` call `fstests.Run` with `NilObject: (*Object)(nil)`, storage tier expectations, minimum chunk size, and optional directory marker config. `TestAWSDualStackOption` checks that `UseDualStack` maps to AWS SDK endpoint options. Exported wrappers `SetUploadChunkSize`, `SetUploadCutoff`, and `SetCopyCutoff` expose private setters to `fstests` interfaces. `TestParseRetainUntilDate` validates RFC3339 inputs, timezone offsets, duration inputs, and invalid strings.

## Control Flow
Redirect tests set up `httptest.Server` instances and send requests through the backend-created client, asserting headers observed by servers. Integration tests rely on external rclone remote configuration unless skipped by `fstest.RemoteName`. Dual-stack tests create SDK clients with and without the option and inspect the resulting SDK client options. Retain-date parsing tests capture `now` once and allow small timing tolerance for duration-derived dates.

## State And Persistence Behavior
Most tests are local and ephemeral. Generic integration tests create and delete remote objects and buckets through `fstests`. `TestIntegration2` only runs when a specific remote is not supplied and injects `directory_markers=true` into the test config. Redirect tests do not persist state beyond temporary HTTP servers.

## Dependencies And Integration Points
The file integrates with `net/http/httptest`, AWS SDK endpoint option constants, rclone `fs` option interfaces, `fstest`/`fstests`, and testify. It directly tests unexported backend functions and also asserts that `*Fs` satisfies upload/copy cutoff setter interfaces used by generic tests.

## Risks And Edge Cases
The redirect security tests are important because AWS session tokens should not be forwarded to different hosts after S3/CDN redirects. If redirect logic changes to compare only adjacent redirects instead of the original chain, the cross-host second-hop test can catch leakage. Integration tests depend on external credentials and provider behavior, so they may be skipped or provider-specific. Duration-based retain-date tests are tolerant but still time-sensitive.

## Test Signals
This file gives fast local coverage for redirect behavior and parser/setter logic, plus broad remote coverage through `fstests.Run`. It is the main public conformance entry point for the S3 backend.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/s3_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/setfrom.go -->
# sources/user-network-fs/rclone/backend/s3/setfrom.go

## Purpose
This generated file provides explicit field-copy helpers between AWS SDK v2 S3 request/response structs. The backend uses these helpers where it previously would have used reflective struct copying, especially while adapting ListObjects v1/version responses into v2-shaped responses, synthesizing HEAD output from PUT input, and copying upload/copy metadata between request types.

## Important APIs, Types, And Functions
The functions are all package-private and named `setFrom_<destination>_<source>`. Important mappings include `ListObjectsInput` from `ListObjectsV2Input`, `ListObjectsV2Output` from `ListObjectsOutput`, `ListObjectVersionsInput` from `ListObjectsV2Input`, `ObjectVersion` from `DeleteMarkerEntry`, `ListObjectsV2Output` from `ListObjectVersionsOutput`, `types.Object` from `types.ObjectVersion`, multipart-create input from `HeadObjectOutput`, `CopyObjectInput`, or `PutObjectInput`, upload-part-copy input from copy input, HEAD output from GET output or PUT input, and copy input from PUT input.

## Control Flow
There is no independent control flow; callers allocate destination structs and invoke these helpers to copy overlapping fields. The generated functions perform direct assignment only and do not validate values, deep-copy maps/slices, transform enum meanings, or apply backend policy.

## State And Persistence Behavior
The helpers mutate destination structs in memory. Because maps, slices, and pointers are assigned directly, callers share referenced data with the source structs unless they clone separately. No remote state is changed by this file alone.

## Dependencies And Integration Points
The file depends only on AWS SDK v2 S3 and S3 `types`. It is generated by `go run gen_setfrom.go` and consumed throughout `s3.go`. It is an integration layer between the SDK's many similar-but-not-identical struct shapes and the backend's desire to keep request metadata consistent across listing, copy, upload, no-HEAD, and multipart operations.

## Risks And Edge Cases
Generated code must stay aligned with the AWS SDK version. If the SDK adds fields relevant to integrity checks, Object Lock, SSE, or metadata and the generator is not rerun, the backend may silently omit those fields in one path while preserving them in another. Direct pointer/map assignment can be intentional but means later mutation can alias source data. Manual edits would be overwritten and are discouraged by the generated header.

## Test Signals
There are no direct tests for this generated file, but many S3 tests indirectly exercise it: version/delete-marker tests use version/list conversions, metadata and Object Lock tests use PUT/COPY/HEAD conversions, `NoHead` relies on synthetic HEAD output from PUT input, and multipart copy/upload flows depend on request conversions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/setfrom.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/v2sign.go -->
# sources/user-network-fs/rclone/backend/s3/v2sign.go

## Purpose
This file implements legacy S3 Signature Version 2 signing behind the AWS SDK v2 `HTTPSignerV4` interface. It supports older S3-compatible services that do not accept v4 signatures, such as older Ceph deployments.

## Important APIs, Types, And Functions
`s3ParamsToSign` lists subresource and response override query parameters that must be included in the S3 v2 canonical resource. `v2Signer` stores a pointer to backend `Options`. Its `SignHTTP` method sets the `Date` header, canonicalizes the escaped path, extracts Content-MD5 and Content-Type, collects and sorts `x-amz-*` headers, includes selected query parameters, computes an HMAC-SHA1 over the v2 string-to-sign using `SecretAccessKey`, base64-encodes the result, and sets the `Authorization: AWS accessKey:signature` header.

## Control Flow
`s3Connection` installs `v2Signer` when `--s3-v2-auth` is enabled or the region is `other-v2-signature`, except for IBM COS IAM where a separate signer is used. The SDK invokes `SignHTTP` during request finalization, even though the implementation ignores v4-specific inputs such as `payloadHash`, `service`, `region`, and signer option callbacks.

## State And Persistence Behavior
The signer mutates outgoing HTTP requests by setting `Date` and `Authorization`. It reads credentials from `Options` and does not maintain its own cache or persistent state.

## Dependencies And Integration Points
The implementation depends on standard HMAC/SHA1/base64/http utilities and AWS SDK v2 signer interface types. It integrates with the S3 backend's request middleware and option handling. It is intentionally compatible-shaped with v4 signing even though it produces v2 signatures.

## Risks And Edge Cases
Signature v2 is legacy and less broadly supported. Canonicalization correctness is sensitive to path escaping, query parameter inclusion, repeated query values, and `x-amz-*` header ordering/value joining. The code uses `time.Now()` instead of the `signingTime` parameter, which is acceptable for normal use but makes deterministic signing tests harder. It references `v2.opt.SecretAccessKey` and `AccessKeyID` directly rather than the `credentials` argument, so assume-role or environment credential flows should not be expected to work through this signer unless options contain the final static credentials.

## Test Signals
There are no direct unit tests in this subset for v2 signatures. Coverage is likely through live provider integration when `v2_auth` is configured. High-value tests would check known AWS v2 signing examples, repeated subresource query parameters, and canonical `x-amz-*` headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/v2sign.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/api/types.go -->
# sources/user-network-fs/rclone/backend/seafile/api/types.go

## Purpose
This file defines JSON request and response DTOs for the Seafile backend API package. It isolates Seafile's inconsistent HTTP JSON shapes behind Go structs used by the backend implementation.

## Important APIs, Types, And Functions
Authentication types include `AuthenticationRequest` and `AuthenticationResult`. Account/server/library types include `AccountInfo`, `ServerInfo`, `DefaultLibrary`, `CreateLibraryRequest`, `Library`, and `CreateLibrary`. File/directory listing types include `FileType`, `FileTypeDir`, `FileTypeFile`, `FileDetail`, `DirEntries`, `DirEntry`, and `DirectoryDetail`. Mutation types include `Operation` plus constants for copy/move/rename, `FileOperationRequest`, `FileInfo`, `CreateDirRequest`, `ShareLinkRequest`, `SharedLink`, and `BatchSourceDestRequest`.

## Control Flow
There is no executable control flow. These structs are populated by JSON marshal/unmarshal calls in other Seafile backend files. Field tags map Go names to the exact JSON keys expected or returned by Seafile endpoints.

## State And Persistence Behavior
The structs represent remote Seafile state such as libraries, files, directories, usage, auth tokens, and share links. They do not persist anything directly. The comments note duplicate shapes because different Seafile API calls return similar objects with different JSON keys or types.

## Dependencies And Integration Points
This file has no imports. It is consumed by the Seafile backend's REST API layer. The `api` package boundary keeps transport schemas separate from rclone `fs` types and backend object logic.

## Risks And Edge Cases
The main risk is schema drift or endpoint inconsistency: Seafile may return different timestamp formats (`int64` mtime vs string `last_modified`), different ID field names (`id`, `repo_id`, `obj_id`), and different object-name fields. Missing fields default to zero values, so callers must distinguish absent values from legitimate zero sizes/times where necessary. `FileType` and `Operation` are string aliases without validation.

## Test Signals
No direct tests are present in this file. Tests for Seafile API behavior would need to exercise JSON parsing and backend operations that consume these DTOs, especially mixed old/new API file detail responses and copy/move/rename responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/object.go -->
# sources/user-network-fs/rclone/backend/seafile/object.go

## Purpose
This file implements the Seafile backend's `Object`, representing a file in a Seafile library. It supplies rclone object identity, size/modtime, open/download, upload/update, delete, and ID behavior.

## Important APIs, Types, And Functions
`Object` stores its parent `*Fs`, Seafile object ID, remote path, path within the library, size, modification time, and library ID. It implements `String`, `Remote`, `ModTime`, `Size`, `Fs`, `Hash`, `Storable`, `SetModTime`, `Open`, `Update`, `Remove`, and `ID`.

`Open` obtains a temporary download link with `o.fs.getDownloadLink` and streams data through `o.fs.download` with the object size and requested open options. `Update` obtains an upload link with `o.fs.getUploadLink`, calls `o.fs.upload`, retries up to three additional times on `ErrorInternalDuringUpload`, and updates the object's `size` and `id` from the upload response. `Remove` delegates to `o.fs.deleteFile`.

## Control Flow
Read flow is link acquisition followed by download. Write flow loops from retry 0 through 3, reacquiring a fresh upload link each time because Seafile upload links are single-use. Only the specific `ErrorInternalDuringUpload` error is retried; all other upload or link errors return immediately. Successful upload mutates local object fields and returns.

## State And Persistence Behavior
Remote state is the file content and metadata in Seafile. Local object state caches ID, size, modtime, library ID, and path. `SetModTime` returns `fs.ErrorCantSetModTime`, so mtime is read-only from this object implementation. Hashes are unsupported and return `hash.ErrUnsupported`.

## Dependencies And Integration Points
The file integrates with the parent Seafile `Fs` API helpers for download links, upload links, upload, and deletion. It implements rclone `fs.DirEntry`, `fs.ObjectInfo`, `fs.Object`, and optional `fs.IDer` behavior. It depends on rclone `fs`, `hash`, contexts, IO, and time.

## Risks And Edge Cases
The retry loop reuses the same `io.Reader` after a failed upload. If `o.fs.upload` consumes bytes before returning `ErrorInternalDuringUpload`, a retry with the same non-seeked reader may upload truncated or empty content unless the upload helper buffers or rewinds elsewhere. Unknown-size upload handling is not explicit in this file despite the comment; correctness depends on `o.fs.upload`. Modtime is not updated after successful upload, only size and ID are. Download and upload links are temporary, so operations are sensitive to expiration and single-use semantics.

## Test Signals
No direct tests for `Object` are in this subset. Expected coverage would come from Seafile backend integration tests for read, write, delete, ID, unsupported hashes, and the temporary 500 retry behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/pacer.go -->
# sources/user-network-fs/rclone/backend/seafile/pacer.go

## Purpose
This file provides shared request pacing for Seafile remotes. It ensures that all remotes pointing at the same Seafile host and port reuse one `fs.Pacer`, reducing request bursts against the same server.

## Important APIs, Types, And Functions
Constants configure pacing: minimum sleep 100 ms, maximum sleep 10 s, and decay constant 2. Package globals `pacers` and `pacerMutex` store shared pacers by normalized remote key. `init` initializes the map. `getPacer` parses the remote, returns an existing pacer if present, or creates a new default pacer with the configured bounds. `parseRemote` normalizes a URL to `hostname:port`, defaulting to 443 for HTTPS and 80 otherwise.

## Control Flow
`getPacer` locks the map, normalizes the remote URL, checks for an existing pacer, creates one if absent, stores it, and returns it. `parseRemote` uses `url.Parse`; on parse failure it logs and returns the shared key `default`.

## State And Persistence Behavior
State is process-local and global to the package. Pacers persist for the lifetime of the process and are never removed from the map. This is intentional for remote reuse but means many distinct hosts could accumulate pacers over a long-running process.

## Dependencies And Integration Points
The file depends on rclone `fs` and `lib/pacer`, standard URL parsing, sync, and time. Other Seafile backend code calls `getPacer` during backend construction or API setup.

## Risks And Edge Cases
The map key ignores URL scheme except for default-port selection, so `http://host:443` and `https://host` can share `host:443` despite differing schemes. Paths are ignored, which is correct for server-level pacing. Invalid remotes all share `default`, which prevents crashes but can couple unrelated malformed configurations. No cleanup exists for the global map.

## Test Signals
No tests in this subset cover pacer normalization or sharing. Useful tests would cover explicit ports, default HTTPS/HTTP ports, invalid URLs, and same-host remote reuse.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/pacer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/renew.go -->
# sources/user-network-fs/rclone/backend/seafile/renew.go

## Purpose
This file implements a small background renewal helper used by the Seafile backend to refresh expiring tokens, such as decryption tokens. It repeatedly invokes a caller-provided renewal callback on a ticker until shut down.

## Important APIs, Types, And Functions
`Renew` holds a `time.Ticker`, the `run func() error` callback, a `done` channel, and a `sync.Once` for idempotent shutdown. `NewRenew` constructs the ticker and starts `renewOnExpiry` in a goroutine. `renewOnExpiry` selects on ticker ticks or shutdown and logs callback errors. `Shutdown` stops the ticker and closes the done channel once.

## Control Flow
Creation immediately starts the goroutine. On each tick, `run` is called synchronously. If it returns an error, the error is logged but the loop continues. When `Shutdown` closes `done`, the goroutine returns. `Shutdown` can be called multiple times safely because channel close and ticker stop are protected by `sync.Once`.

## State And Persistence Behavior
State is in-memory only: a ticker, goroutine, done channel, and callback. Remote token state is changed only through the supplied callback, not by this helper directly. Shutdown prevents future renewals but does not wait for an already-running callback to finish.

## Dependencies And Integration Points
The file depends on `sync`, `time`, and rclone `fs` logging. It is intended to be owned by Seafile backend lifecycle code that knows when renewal is needed and when to shut it down.

## Risks And Edge Cases
If `run` blocks for longer than the ticker interval, renewals serialize and ticks may be dropped by the ticker. There is no context cancellation for the callback and no panic recovery. `Shutdown` does not wait for goroutine exit, so callers needing strict lifecycle ordering would need an additional acknowledgement mechanism. Errors are logged but not surfaced to the owner.

## Test Signals
`renew_test.go` verifies idempotent shutdown and that renewal fires at least once under a short interval. It does not test error logging, long-running callbacks, or shutdown during callback execution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/renew.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/renew_test.go -->
# sources/user-network-fs/rclone/backend/seafile/renew_test.go

## Purpose
This file tests the Seafile `Renew` helper's basic lifecycle behavior: shutdown can be called twice safely, and a short ticker interval invokes the renewal callback within a reasonable time.

## Important APIs, Types, And Functions
`TestShouldAllowShutdownTwice` creates a `Renew` with an hourly interval and a no-op callback, then calls `Shutdown` twice. `TestRenewalInTimeLimit` uses an `atomic.Int64` counter callback, waits one second with a 100 ms ticker, shuts down, and asserts the count is greater than zero and less than eleven.

## Control Flow
Both tests call `NewRenew`, which starts the background goroutine. The first test immediately shuts it down twice to catch double-close panics. The second sleeps to allow ticks, then checks a broad count range to avoid depending on exact scheduler timing.

## State And Persistence Behavior
The tests use only in-memory ticker/goroutine state and an atomic counter. They do not interact with Seafile or persistent token state.

## Dependencies And Integration Points
The file depends on `sync/atomic`, `testing`, `time`, and testify assertions. It directly exercises the public constructor and shutdown method from `renew.go`.

## Risks And Edge Cases
The timing test is intentionally tolerant because CI scheduling can delay goroutines. It still assumes that at least one 100 ms tick will run within one second and that no more than ten ticks will be counted; a heavily stalled or time-skewed environment could make it flaky. The tests do not assert that no callbacks occur after shutdown.

## Test Signals
These tests provide minimal but useful coverage for idempotent shutdown and liveness. Additional coverage could test callback errors, callback blocking, and shutdown while a callback is active.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/renew_test.go -->

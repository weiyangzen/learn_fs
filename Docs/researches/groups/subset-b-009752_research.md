# Research: subset-b-009752

Grouped research for rclone backend files in premiumizeme, protondrive, putio, qingstor, quatrix, and S3 provider/signing support. Each section is source-tree aligned and bounded by reconciliation markers for deterministic per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/premiumizeme/premiumizeme.go -->
# sources/user-network-fs/rclone/backend/premiumizeme/premiumizeme.go

## Purpose
Implements rclone's `premiumizeme` backend for premiumize.me cloud storage. It registers OAuth/API-key configuration, maps rclone filesystem operations onto premiumize.me folder/item REST endpoints, and exposes object metadata, upload, delete, move, quota, public-link, directory-cache, and shutdown behavior.

## Important APIs, Types, And Functions
The main exported types are `Options`, `Fs`, and `Object`. `init` registers the backend with OAuth shared options plus hidden `api_key` and encoding controls. `NewFs` builds the REST client, OAuth token renewer, pacer, features, and `dircache.DirCache`; it also handles roots that point at files by returning `fs.ErrorIsFile`. Core helpers include `parsePath`, `shouldRetry`, `errorHandler`, `baseParams`, `readMetaDataForPath`, `listAll`, `createObject`, `renameLeaf`, and `remove`. `Fs` implements listing, mkdir/rmdir/purge, put/update, move/dirmove, public links, quota, hashes, and cache flush. `Object` implements rclone object metadata, open, update, remove, mime type, and ID.

## Control Flow
Construction chooses OAuth unless `api_key` is set, then wraps all API calls in `f.pacer.Call` with retry handling for network errors plus HTTP 429, 500, 502, 503, 504, and 509. Directory lookup flows through `dircache`: `FindLeaf` searches `/folder/list`, `CreateDir` posts `/folder/create`, and `List` turns API content into `fs.Dir` or `Object`. Upload flow requests `/folder/uploadinfo`, validates that the returned upload host resolves, optionally renames an existing file aside, uploads multipart form data to the returned URL, removes the old file after success, and rereads metadata. Move flow separates rename and parent-directory move because premiumize.me has different endpoints for those operations.

## State And Persistence
Persistent service state is remote folders, files, item IDs, server-created upload URLs/tokens, shareable download links, and quota. Local state is limited to the in-memory dir cache, object metadata cache fields, the OAuth token source/renewer, and pacer timing. The backend does not write repository files; rclone config stores OAuth credentials or an API key outside this source file.

## Dependencies And Integration Points
This file integrates with rclone's `fs`, `config`, `oauthutil`, `rest`, `pacer`, `dircache`, `encoder`, `hash`, and `fshttp` packages plus local `premiumizeme/api` response types. It uses the premiumize.me API under `https://www.premiumize.me/api`, OAuth endpoints under premiumize.me, and rclone feature interfaces `Purger`, `Mover`, `DirMover`, `Abouter`, `PublicLinker`, `Shutdowner`, `MimeTyper`, and `IDer`.

## Risks And Test Signals
Risks include `Shutdown` calling `f.tokenRenewer.Shutdown()` even when API-key mode leaves `tokenRenewer` nil, upload replacement temporarily renaming the old file and depending on rollback if the upload fails, case-insensitive name matching causing ambiguous matches, `PublicLink` returning the existing download URL rather than creating an explicit permission, and metadata using creation time because modtime is unsupported. Test signals should cover OAuth and API-key auth, root-as-file setup, empty directories, upload replacement rollback, move plus rename across folders, purge safety on root, public-link behavior, retryable status handling, and nil-renewer shutdown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/premiumizeme/premiumizeme.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/premiumizeme/premiumizeme_test.go -->
# sources/user-network-fs/rclone/backend/premiumizeme/premiumizeme_test.go

## Purpose
Defines the premiumize.me backend integration test entry point for rclone's standard `fstests` suite.

## Important APIs, Types, And Functions
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestPremiumizeMe:"` and `NilObject: (*premiumizeme.Object)(nil)`. There are no local unit helpers or mocks.

## Control Flow
When the test remote is configured, the shared fstests harness creates the backend and exercises rclone filesystem behavior such as put, list, update, remove, directory handling, and optional features advertised by `premiumizeme.Fs`.

## State And Persistence
The test persists data only on the configured `TestPremiumizeMe:` remote during integration runs. It does not create local fixtures.

## Dependencies And Integration Points
Depends on `github.com/rclone/rclone/fstest/fstests` and the backend package. It is discovered by Go's test runner and relies on external credentials/config.

## Risks And Test Signals
Coverage is broad but only when integration credentials exist. It does not isolate retry, OAuth renewal, API-key shutdown, upload rollback, or case-insensitive conflict behavior with deterministic unit tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/premiumizeme/premiumizeme_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/protondrive/protondrive.go -->
# sources/user-network-fs/rclone/backend/protondrive/protondrive.go

## Purpose
Proton Drive backend: authenticates with Proton credentials or cached reusable tokens; wraps Proton-API-Bridge; maps encrypted Proton links into rclone files/directories; supports list, upload, download, move, delete, quota, logout, hash, MIME, and dir-cache behavior.

## Important APIs, Types, And Functions
Important surface: Options, Fs, Object, protonLogger, get/set/clear config map helpers, app-version helpers, newProtonDrive, NewFs, List, FindLeaf, CreateDir, Put, Mkdir, Rmdir, Purge, About, Move, DirMove, Disconnect, and object Open/Update/Remove/Hash methods.

## Control Flow
NewFs reveals obscured secrets, configures rclone HTTP transport/logging, tries reusable login then username/password/TOTP fallback, creates a dircache rooted at the Proton main share, and returns fs.ErrorIsFile for file roots. Listing decrypts directory data through the bridge; upload rejects unknown sizes and calls UploadFileByReader; download calls DownloadFileByID and wraps range limits.

## State And Persistence
remote links, revisions, trash, encrypted attrs, reusable token config keys, package-level auth callback state, dircache, object metadata, API bridge cache.

## Dependencies And Integration Points
Proton-API-Bridge, go-proton-api, semver, totp, rclone fs/config/obscure/fshttp/dircache/encoder/pacer/readers/hash.

## Risks And Test Signals
Risks and useful test signals: global auth callback state for simultaneous remotes, stale cache with external clients, no multi-threaded downloads, 429/503 delegated to SDK, root purge prevention, destination conflicts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/protondrive/protondrive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/protondrive/protondrive_internal_test.go -->
# sources/user-network-fs/rclone/backend/protondrive/protondrive_internal_test.go

## Purpose
Proton Drive internal unit tests: validates app-version derivation and retry classification without live credentials.

## Important APIs, Types, And Functions
Important surface: protonDriveAppVersionPattern, TestProtonDriveAppVersionFromRcloneVersion, TestShouldRetry.

## Control Flow
table tests call helper functions with releases, dev/beta builds, invalid versions, API errors, wrapped errors, and canceled contexts

## State And Persistence
in-memory only.

## Dependencies And Integration Points
go-proton-api APIError and testify assert.

## Risks And Test Signals
Risks and useful test signals: covers main intended cases; gaps include alpha/RC and SDK retry-after integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/protondrive/protondrive_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/protondrive/protondrive_test.go -->
# sources/user-network-fs/rclone/backend/protondrive/protondrive_test.go

## Purpose
Proton Drive integration test: runs the standard rclone fstests suite against TestProtonDrive.

## Important APIs, Types, And Functions
Important surface: TestIntegration with RemoteName and NilObject.

## Control Flow
delegates backend-contract operations to fstests

## State And Persistence
remote test data and rclone config credentials.

## Dependencies And Integration Points
fstest/fstests and protondrive backend.

## Risks And Test Signals
Risks and useful test signals: credential and account-state dependent; cache/draft/rate behavior may affect runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/protondrive/protondrive_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/putio/error.go -->
# sources/user-network-fs/rclone/backend/putio/error.go

## Purpose
Put.io retry/status helper: centralizes HTTP status validation and retry classification.

## Important APIs, Types, And Functions
Important surface: checkStatusCode, statusCodeError, Temporary, shouldRetry.

## Control Flow
SDK or direct HTTP errors are converted, 429 maps to pacer RetryAfter using x-ratelimit-reset or 60s, 5xx are temporary, context cancellation stops retry

## State And Persistence
no persistent state.

## Dependencies And Integration Points
go-putio, rclone fserrors/pacer, net/http.

## Risks And Test Signals
Risks and useful test signals: nil responses, stale reset headers, missing tests for malformed headers and SDK conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/putio/error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/putio/fs.go -->
# sources/user-network-fs/rclone/backend/putio/fs.go

## Purpose
Put.io filesystem implementation: constructs OAuth client, dircache and SDK client; implements directory operations, TUS upload, server-side copy/move, quota and cleanup.

## Important APIs, Types, And Functions
Important surface: Fs, NewFs, CreateDir, FindLeaf, List, Put, PutUnchecked, createUpload, sendUpload, transferChunk, Copy, Move, DirMove, About, CleanUp.

## Control Flow
NewFs configures OAuth and file-root handling. Upload creates a TUS resource then PATCHes 48 MiB repeatable chunks, resolving offset mismatches with HEAD. Copy uses a temporary suffix before overwrite/rename.

## State And Persistence
remote files, folders, upload sessions, trash, dircache, OAuth config, transient upload locations.

## Dependencies And Integration Points
go-putio SDK, rclone oauth/fshttp/dircache/pacer/readers/hash.

## Risks And Test Signals
Risks and useful test signals: upload session loss, offset mismatch complexity, atoi panic on invalid IDs, copy overwrite sequencing, direct upload endpoint behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/putio/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/putio/object.go -->
# sources/user-network-fs/rclone/backend/putio/object.go

## Purpose
Put.io object implementation: handles object metadata lookup, CRC32 hash, MIME, modtime, direct download, update and removal.

## Important APIs, Types, And Functions
Important surface: Object, NewObject, newObjectWithInfo, readEntry, setMetadataFromEntry, Hash, Size, ID, MimeType, SetModTime, Open, Update, Remove.

## Control Flow
metadata lookup uses dircache then /child?name; Open obtains a storage URL and direct GETs with range headers; Update removes the old file and uploads replacement unless ignored filename regex matches

## State And Persistence
remote file metadata/content/type/timestamps; local cached putio.File and modtime.

## Dependencies And Integration Points
go-putio, rclone fs/hash/fserrors, direct HTTP.

## Risks And Test Signals
Risks and useful test signals: old object lost if replacement upload fails after remove, Open requires populated file, ignored files silently skip upload.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/putio/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/putio/putio.go -->
# sources/user-network-fs/rclone/backend/putio/putio.go

## Purpose
Put.io backend registration: registers OAuth config, constants, ignored system-file regex, options and interface assertions.

## Important APIs, Types, And Functions
Important surface: putioConfig, ignoredFiles, Options, init, interface assertions.

## Control Flow
package init registers backend and config flow; runtime behavior lives in fs.go/object.go/error.go

## State And Persistence
global descriptors and regex only; OAuth persists in rclone config.

## Dependencies And Integration Points
rclone fs/config/oauthutil/obscure/dircache/encoder.

## Risks And Test Signals
Risks and useful test signals: OAuth secret maintenance, NoOffline token behavior, fixed chunk/rate defaults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/putio/putio.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/putio/putio_test.go -->
# sources/user-network-fs/rclone/backend/putio/putio_test.go

## Purpose
Put.io integration test: runs standard rclone fstests against TestPutio.

## Important APIs, Types, And Functions
Important surface: TestIntegration with RemoteName and NilObject.

## Control Flow
delegates to fstests

## State And Persistence
remote account test data only.

## Dependencies And Integration Points
fstest/fstests.

## Risks And Test Signals
Risks and useful test signals: does not deterministically test TUS retry or offset recovery.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/putio/putio_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/qingstor/qingstor.go -->
# sources/user-network-fs/rclone/backend/qingstor/qingstor.go

## Purpose
QingStor backend: maps QingStor buckets/keys to rclone filesystem operations including bucket listing, object listing, copy, upload/download, cleanup, hashes and MIME.

## Important APIs, Types, And Functions
Important surface: Options, Fs, Object, qsServiceConnection, NewFs, List, ListR, Put, Copy, Mkdir, Rmdir, CleanUp, readMetaData, Open, Update, Remove, Hash.

## Control Flow
NewFs validates upload options and endpoint, creates SDK service, detects file roots by HEAD. Listing paginates buckets/objects; Update delegates to uploader; SetModTime copies object to itself for smaller objects.

## State And Persistence
remote buckets, objects, multipart uploads; local bucket cache and object metadata.

## Dependencies And Integration Points
yunify QingStor SDK, rclone bucket/list/fshttp/hash/encoder.

## Risks And Test Signals
Risks and useful test signals: unsupported build targets, endpoint parsing, SDK retry option not wired, multipart checksum/concurrency caveat, ETag MD5 ambiguity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/qingstor/qingstor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/qingstor/qingstor_test.go -->
# sources/user-network-fs/rclone/backend/qingstor/qingstor_test.go

## Purpose
QingStor integration test: runs standard fstests and exposes chunk-size/cutoff setters.

## Important APIs, Types, And Functions
Important surface: TestIntegration, SetUploadChunkSize, SetUploadCutoff.

## Control Flow
fstests can force chunked upload behavior

## State And Persistence
remote QingStor test data.

## Dependencies And Integration Points
fstest/fstests and fs.

## Risks And Test Signals
Risks and useful test signals: live-service dependent; endpoint and uploader unit coverage absent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/qingstor/qingstor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/qingstor/qingstor_unsupported.go -->
# sources/user-network-fs/rclone/backend/qingstor/qingstor_unsupported.go

## Purpose
QingStor unsupported-platform shim: keeps package buildable on plan9/js.

## Important APIs, Types, And Functions
Important surface: package declaration under build tag.

## Control Flow
selected instead of real backend on unsupported targets

## State And Persistence
none.

## Dependencies And Integration Points
Go build constraints.

## Risks And Test Signals
Risks and useful test signals: backend unavailable on those targets by design.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/qingstor/qingstor_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/qingstor/upload.go -->
# sources/user-network-fs/rclone/backend/qingstor/upload.go

## Purpose
QingStor upload helper: implements single and multipart upload machinery.

## Important APIs, Types, And Functions
Important surface: uploadInput, uploader, multiUploader, chunk, completedParts, newUploader, singlePartUpload, upload, nextReader, initiate, send, complete, abort.

## Control Flow
reads first chunk to choose single vs multipart, starts worker goroutines, uploads parts, computes MD5 over part buffers, sorts completed parts, completes or aborts on error

## State And Persistence
remote multipart upload session; local reader position, upload ID, parts, shared error, MD5 hash.

## Dependencies And Integration Points
QingStor SDK, rclone atexit/logging, sync/io/md5.

## Risks And Test Signals
Risks and useful test signals: memory use for non-seekable readers, ignored bucket-init errors, part numbering, checksum with concurrency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/qingstor/upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/quatrix/api/types.go -->
# sources/user-network-fs/rclone/backend/quatrix/api/types.go

## Purpose
Quatrix API DTOs: defines JSON payloads and helpers for Quatrix REST calls.

## Important APIs, Types, And Functions
Important surface: ProfileInfo, IDList, DeleteParams, FileInfo, File, JSONTime, upload/download/copy/move params and responses.

## Control Flow
backend serializes these for id lookup, metadata, delete, upload, finalize, copy and move; JSONTime converts fractional Unix seconds

## State And Persistence
DTOs only; represent remote file IDs, quota, timestamps, upload keys.

## Dependencies And Integration Points
strconv/time and quatrix.go REST client.

## Risks And Test Signals
Risks and useful test signals: type-code drift, float timestamp precision, project-folder semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/quatrix/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/quatrix/quatrix.go -->
# sources/user-network-fs/rclone/backend/quatrix/quatrix.go

## Purpose
Quatrix backend: maps Quatrix file APIs to rclone operations with dynamic chunked uploads, metadata, delete, copy, move and quota.

## Important APIs, Types, And Functions
Important surface: Options, Fs, Object, fileID, metadata, setMTime, deleteObject, Copy, Move, DirMove, uploadSession, dynamicUpload, finalize.

## Control Flow
NewFs configures bearer auth, custom transport, root ID and dircache. Upload creates/modifies a session, sends Content-Range chunks sized by UploadMemoryManager, finalizes with mtime, and deletes partial files on error.

## State And Persistence
remote file IDs, upload keys, trash/hard delete, quota; local dircache, object metadata, memory manager.

## Dependencies And Integration Points
quatrix/api, rclone rest/fshttp/dircache/multipart/pacer.

## Risks And Test Signals
Risks and useful test signals: unknown-size upload loop, memory pressure, hash returns empty nil, project folder filtering, overwrite semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/quatrix/quatrix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/quatrix/quatrix_test.go -->
# sources/user-network-fs/rclone/backend/quatrix/quatrix_test.go

## Purpose
Quatrix integration test: runs standard rclone fstests against TestQuatrix.

## Important APIs, Types, And Functions
Important surface: TestIntegration with RemoteName and NilObject.

## Control Flow
delegates to fstests

## State And Persistence
remote Quatrix account data.

## Dependencies And Integration Points
fstest/fstests.

## Risks And Test Signals
Risks and useful test signals: does not isolate dynamic chunking or hard-delete/project-folder behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/quatrix/quatrix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/quatrix/upload_memory.go -->
# sources/user-network-fs/rclone/backend/quatrix/upload_memory.go

## Purpose
Quatrix upload memory manager: chooses dynamic chunk sizes from transfer speed and configured shared memory budget.

## Important APIs, Types, And Functions
Important surface: UploadMemoryManager, NewUploadMemoryManager, Consume, Return.

## Control Flow
static mode caps at minimal chunk; dynamic mode returns previous borrow, estimates speed*time chunk, borrows from shared pool, and records per-file borrow

## State And Persistence
in-memory mutex-protected shared pool and fileUsage map.

## Dependencies And Integration Points
rclone ConfigInfo and Quatrix Options.

## Risks And Test Signals
Risks and useful test signals: Return must be called on all paths, file ID reuse, zero speed minimal chunks, concurrent accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/quatrix/upload_memory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/gen_setfrom.go -->
# sources/user-network-fs/rclone/backend/s3/gen_setfrom.go

## Purpose
S3 setFrom generator: ignored-build generator for copying matching fields across AWS SDK S3 structs.

## Important APIs, Types, And Functions
Important surface: outputFile, genSetFrom, main.

## Control Flow
reflects destination/source pointer fields, emits assignments for same-name assignable fields, writes generated boilerplate

## State And Persistence
optional output file only.

## Dependencies And Integration Points
AWS SDK v2 s3/types, reflect/flag/io.

## Risks And Test Signals
Risks and useful test signals: stale generated code after SDK changes; assignable-only matching.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/gen_setfrom.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/ibm_signer.go -->
# sources/user-network-fs/rclone/backend/s3/ibm_signer.go

## Purpose
IBM IAM S3 signer: signs IBM COS requests with IAM bearer token headers instead of normal SigV4 credentials.

## Important APIs, Types, And Functions
Important surface: Authenticator, IbmIamSigner, SignHTTP, NoOpCredentialsProvider.

## Control Flow
SignHTTP gets a token from injected or IBM SDK authenticator, sets Authorization and ibm-service-instance-id; no-op provider satisfies AWS SDK credential requirement

## State And Persistence
no local persistence; authenticator may cache tokens.

## Dependencies And Integration Points
IBM go-sdk-core and AWS SDK v2 signer/credentials.

## Risks And Test Signals
Risks and useful test signals: token fetch per sign, ignored SigV4 params, empty instance ID, placeholder creds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/ibm_signer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/ibm_signer_test.go -->
# sources/user-network-fs/rclone/backend/s3/ibm_signer_test.go

## Purpose
IBM signer unit test: verifies IAM signer header setting with a mock authenticator.

## Important APIs, Types, And Functions
Important surface: MockAuthenticator, TestSignHTTP.

## Control Flow
constructs request, signs it, asserts Authorization and instance-id headers

## State And Persistence
in-memory only.

## Dependencies And Integration Points
Go test/http/time/context and AWS credentials.

## Risks And Test Signals
Risks and useful test signals: happy path only; missing token-error/no-op provider coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/ibm_signer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/AWS.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/AWS.yaml

## Purpose
Embedded S3 provider descriptor for Amazon Web Services (AWS) S3. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `AWS`, `description` is `Amazon Web Services (AWS) S3`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 26 entries (us-east-1, us-east-2, us-west-1, us-west-2, ca-central-1, plus 21 more); endpoint: empty/default-inheriting map; location_constraint: 25 entries (us-east-2, us-west-1, us-west-2, ca-central-1, eu-west-1, plus 20 more); acl: empty/default-inheriting map; storage_class: 8 entries (STANDARD, REDUCED_REDUNDANCY, STANDARD_IA, ONEZONE_IA, GLACIER, plus 3 more); server_side_encryption: 2 entries (AES256, aws). Advanced booleans: bucket_acl, directory_bucket, leave_parts_on_error, requester_pays, sse_customer_algorithm, sse_customer_key, sse_customer_key_base64, sse_customer_key_md5, sse_kms_key_id, sts_endpoint, use_accelerate_endpoint. Quirks: might_gzip=false, use_unsigned_payload=false, use_data_integrity_protections=true.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `AWS` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `AWS` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/AWS.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Alibaba.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Alibaba.yaml

## Purpose
Embedded S3 provider descriptor for Alibaba Cloud Object Storage System (OSS) formerly Aliyun. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Alibaba`, `description` is `Alibaba Cloud Object Storage System (OSS) formerly Aliyun`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: endpoint: 25 entries (oss-accelerate.aliyuncs.com, oss-accelerate-overseas.aliyuncs.com, oss-cn-hangzhou.aliyuncs.com, oss-cn-shanghai.aliyuncs.com, oss-cn-qingdao.aliyuncs.com, plus 20 more); acl: empty/default-inheriting map; storage_class: 3 entries (STANDARD, GLACIER, STANDARD_IA). Advanced booleans: bucket_acl. Quirks: use_multipart_etag=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Alibaba` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Alibaba` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Alibaba.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/ArvanCloud.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/ArvanCloud.yaml

## Purpose
Embedded S3 provider descriptor for Arvan Cloud Object Storage (AOS). It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `ArvanCloud`, `description` is `Arvan Cloud Object Storage (AOS)`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: endpoint: 2 entries (s3.ir-thr-at1.arvanstorage.ir, s3.ir-tbz-sh1.arvanstorage.ir); location_constraint: 2 entries (ir-thr-at1, ir-tbz-sh1); acl: empty/default-inheriting map; storage_class: 1 entries (STANDARD). Advanced booleans: bucket_acl. Quirks: list_version=1, force_path_style=true, list_url_encode=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `ArvanCloud` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `ArvanCloud` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/ArvanCloud.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/BizflyCloud.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/BizflyCloud.yaml

## Purpose
Embedded S3 provider descriptor for Bizfly Cloud Simple Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `BizflyCloud`, `description` is `Bizfly Cloud Simple Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 2 entries (hn, hcm); endpoint: 2 entries (hn.ss.bfcplatform.vn, hcm.ss.bfcplatform.vn); acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: force_path_style=true, list_url_encode=false, use_multipart_etag=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `BizflyCloud` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `BizflyCloud` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/BizflyCloud.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Ceph.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Ceph.yaml

## Purpose
Embedded S3 provider descriptor for Ceph Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Ceph`, `description` is `Ceph Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: empty/default-inheriting map; endpoint: empty/default-inheriting map; location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map; server_side_encryption: 2 entries (AES256, aws). Advanced booleans: bucket_acl, sse_customer_algorithm, sse_customer_key, sse_customer_key_base64, sse_customer_key_md5, sse_kms_key_id. Quirks: list_version=1, force_path_style=true, list_url_encode=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Ceph` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Ceph` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Ceph.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/ChinaMobile.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/ChinaMobile.yaml

## Purpose
Embedded S3 provider descriptor for China Mobile Ecloud Elastic Object Storage (EOS). It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `ChinaMobile`, `description` is `China Mobile Ecloud Elastic Object Storage (EOS)`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: endpoint: 30 entries (eos-wuxi-1.cmecloud.cn, eos-jinan-1.cmecloud.cn, eos-ningbo-1.cmecloud.cn, eos-shanghai-1.cmecloud.cn, eos-zhengzhou-1.cmecloud.cn, plus 25 more); location_constraint: 30 entries (wuxi1, jinan1, ningbo1, shanghai1, zhengzhou1, plus 25 more); acl: 4 entries (private, public-read, public-read-write, authenticated-read); storage_class: 3 entries (STANDARD, GLACIER, STANDARD_IA); server_side_encryption: 1 entries (AES256). Advanced booleans: bucket_acl, sse_customer_algorithm, sse_customer_key, sse_customer_key_base64, sse_customer_key_md5. Quirks: list_version=1, force_path_style=true, list_url_encode=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `ChinaMobile` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `ChinaMobile` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/ChinaMobile.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Cloudflare.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Cloudflare.yaml

## Purpose
Embedded S3 provider descriptor for Cloudflare R2 Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Cloudflare`, `description` is `Cloudflare R2 Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 1 entries (auto); endpoint: empty/default-inheriting map. Advanced booleans: none. Quirks: force_path_style=true, use_multipart_etag=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Cloudflare` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Cloudflare` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Cloudflare.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Cubbit.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Cubbit.yaml

## Purpose
Embedded S3 provider descriptor for Cubbit DS3 Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Cubbit`, `description` is `Cubbit DS3 Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 1 entries (eu-west-1); endpoint: 2 entries (s3.cubbit.eu, s3.{tenant_name}.cubbit.eu); acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: use_multipart_etag=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Cubbit` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Cubbit` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Cubbit.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/DigitalOcean.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/DigitalOcean.yaml

## Purpose
Embedded S3 provider descriptor for DigitalOcean Spaces. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `DigitalOcean`, `description` is `DigitalOcean Spaces`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: empty/default-inheriting map; endpoint: 10 entries (syd1.digitaloceanspaces.com, sfo3.digitaloceanspaces.com, sfo2.digitaloceanspaces.com, fra1.digitaloceanspaces.com, nyc3.digitaloceanspaces.com, plus 5 more); location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: list_url_encode=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `DigitalOcean` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `DigitalOcean` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/DigitalOcean.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Dreamhost.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Dreamhost.yaml

## Purpose
Embedded S3 provider descriptor for Dreamhost DreamObjects. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Dreamhost`, `description` is `Dreamhost DreamObjects`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: empty/default-inheriting map; endpoint: 1 entries (objects-us-east-1.dream.io); location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: list_url_encode=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Dreamhost` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Dreamhost` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Dreamhost.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Exaba.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Exaba.yaml

## Purpose
Embedded S3 provider descriptor for Exaba Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Exaba`, `description` is `Exaba Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: empty/default-inheriting map; endpoint: empty/default-inheriting map; location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: force_path_style=true.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Exaba` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Exaba` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Exaba.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Fastly.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Fastly.yaml

## Purpose
Embedded S3 provider descriptor for Fastly Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Fastly`, `description` is `Fastly Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 11 entries (au-east-1, eu-central, eu-south-1, eu-west-1, jp-central-1, plus 6 more); endpoint: 11 entries (au-east-1.object.fastlystorage.app, eu-central.object.fastlystorage.app, eu-south-1.object.fastlystorage.app, eu-west-1.object.fastlystorage.app, jp-central-1.object.fastlystorage.app, plus 6 more). Advanced booleans: none. Quirks: force_path_style=true, use_already_exists=false, use_multipart_etag=false, use_multipart_uploads=false, etag_is_not_md5=true.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Fastly` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Fastly` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Fastly.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/FileLu.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/FileLu.yaml

## Purpose
Embedded S3 provider descriptor for FileLu S5 (S3-Compatible Object Storage). It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `FileLu`, `description` is `FileLu S5 (S3-Compatible Object Storage)`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 5 entries (global, us-east, eu-central, ap-southeast, me-central); endpoint: 5 entries (s5lu.com, us.s5lu.com, eu.s5lu.com, ap.s5lu.com, me.s5lu.com); acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: list_version=2, force_path_style=true, list_url_encode=false, use_multipart_etag=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `FileLu` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `FileLu` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/FileLu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/FlashBlade.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/FlashBlade.yaml

## Purpose
Embedded S3 provider descriptor for Pure Storage FlashBlade Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `FlashBlade`, `description` is `Pure Storage FlashBlade Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: endpoint: empty/default-inheriting map. Advanced booleans: none. Quirks: might_gzip=false, force_path_style=true.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `FlashBlade` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `FlashBlade` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/FlashBlade.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/GCS.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/GCS.yaml

## Purpose
Embedded S3 provider descriptor for Google Cloud Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `GCS`, `description` is `Google Cloud Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: empty/default-inheriting map; endpoint: 1 entries (https); location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: use_accept_encoding_gzip=false, sign_accept_encoding=false, use_already_exists=true, use_x_id=false, copy_cutoff=9223372036854775807, object_lock_supported=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `GCS` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `GCS` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/GCS.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/HCP.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/HCP.yaml

## Purpose
Embedded S3 provider descriptor for Hitachi Content Platform (HCP). It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `HCP`, `description` is `Hitachi Content Platform (HCP)`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: empty/default-inheriting map; endpoint: empty/default-inheriting map; location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: force_path_style=true, list_url_encode=true, use_multipart_etag=false, list_versions_oldest_first=true.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `HCP` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `HCP` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/HCP.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Hetzner.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Hetzner.yaml

## Purpose
Embedded S3 provider descriptor for Hetzner Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Hetzner`, `description` is `Hetzner Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 3 entries (hel1, fsn1, nbg1); endpoint: 3 entries (hel1.your-objectstorage.com, fsn1.your-objectstorage.com, nbg1.your-objectstorage.com); location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Hetzner` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Hetzner` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Hetzner.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/HuaweiOBS.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/HuaweiOBS.yaml

## Purpose
Embedded S3 provider descriptor for Huawei Object Storage Service. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `HuaweiOBS`, `description` is `Huawei Object Storage Service`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 15 entries (af-south-1, ap-southeast-2, ap-southeast-3, cn-east-3, cn-east-2, plus 10 more); endpoint: 15 entries (obs.af-south-1.myhuaweicloud.com, obs.ap-southeast-2.myhuaweicloud.com, obs.ap-southeast-3.myhuaweicloud.com, obs.cn-east-3.myhuaweicloud.com, obs.cn-east-2.myhuaweicloud.com, plus 10 more); acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: list_url_encode=false, list_version=1, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `HuaweiOBS` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `HuaweiOBS` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/HuaweiOBS.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/IBMCOS.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/IBMCOS.yaml

## Purpose
Embedded S3 provider descriptor for IBM COS S3. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `IBMCOS`, `description` is `IBM COS S3`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: empty/default-inheriting map; endpoint: 62 entries (s3.us.cloud-object-storage.appdomain.cloud, s3.dal.us.cloud-object-storage.appdomain.cloud, s3.wdc.us.cloud-object-storage.appdomain.cloud, s3.sjc.us.cloud-object-storage.appdomain.cloud, s3.private.us.cloud-object-storage.appdomain.cloud, plus 57 more); location_constraint: 32 entries (us-standard, us-vault, us-cold, us-flex, us-east-standard, plus 27 more); acl: 4 entries (private, public-read, public-read-write, authenticated-read). Advanced booleans: ibm_api_key, ibm_resource_instance_id, ibm_iam_endpoint, bucket_acl. Quirks: list_version=1, force_path_style=true, list_url_encode=false, use_multipart_etag=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `IBMCOS` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `IBMCOS` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/IBMCOS.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/IDrive.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/IDrive.yaml

## Purpose
Embedded S3 provider descriptor for IDrive e2. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `IDrive`, `description` is `IDrive e2`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: force_path_style=true, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `IDrive` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `IDrive` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/IDrive.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/IONOS.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/IONOS.yaml

## Purpose
Embedded S3 provider descriptor for IONOS Cloud. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `IONOS`, `description` is `IONOS Cloud`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 6 entries (de, eu-central-2, eu-central-3, eu-central-4, eu-south-2, plus 1 more); endpoint: 6 entries (s3.eu-central-1.ionoscloud.com, s3.eu-central-2.ionoscloud.com, s3.eu-central-3.ionoscloud.com, s3.eu-central-4.ionoscloud.com, s3.eu-south-2.ionoscloud.com, plus 1 more); acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: force_path_style=true, list_url_encode=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `IONOS` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `IONOS` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/IONOS.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/ImpossibleCloud.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/ImpossibleCloud.yaml

## Purpose
Embedded S3 provider descriptor for Impossible Cloud Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `ImpossibleCloud`, `description` is `Impossible Cloud Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 7 entries (eu-central-2, eu-west-1, eu-west-2, eu-west-3, eu-east-1, plus 2 more); endpoint: 7 entries (eu-central-2.storage.impossibleapi.net, eu-west-1.storage.impossibleapi.net, eu-west-2.storage.impossibleapi.net, eu-west-3.storage.impossibleapi.net, eu-east-1.storage.impossibleapi.net, plus 2 more); location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: none; S3 defaults apply.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `ImpossibleCloud` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `ImpossibleCloud` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/ImpossibleCloud.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Intercolo.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Intercolo.yaml

## Purpose
Embedded S3 provider descriptor for Intercolo Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Intercolo`, `description` is `Intercolo Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 1 entries (de-fra); endpoint: 1 entries (de-fra.i3storage.com); acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: use_unsigned_payload=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Intercolo` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Intercolo` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Intercolo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Leviia.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Leviia.yaml

## Purpose
Embedded S3 provider descriptor for Leviia Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Leviia`, `description` is `Leviia Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: empty/default-inheriting map; endpoint: 1 entries (s3.leviia.com); acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Leviia` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Leviia` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Leviia.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Liara.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Liara.yaml

## Purpose
Embedded S3 provider descriptor for Liara Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Liara`, `description` is `Liara Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: endpoint: 1 entries (storage.iran.liara.space); acl: empty/default-inheriting map; storage_class: 1 entries (STANDARD). Advanced booleans: bucket_acl. Quirks: force_path_style=true, list_url_encode=false, use_multipart_etag=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Liara` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Liara` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Liara.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Linode.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Linode.yaml

## Purpose
Embedded S3 provider descriptor for Linode Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Linode`, `description` is `Linode Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: endpoint: 21 entries (nl-ams-1.linodeobjects.com, us-southeast-1.linodeobjects.com, in-maa-1.linodeobjects.com, us-ord-1.linodeobjects.com, eu-central-1.linodeobjects.com, plus 16 more); acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: none; S3 defaults apply.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Linode` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Linode` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Linode.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/LyveCloud.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/LyveCloud.yaml

## Purpose
Embedded S3 provider descriptor for Seagate Lyve Cloud. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `LyveCloud`, `description` is `Seagate Lyve Cloud`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: empty/default-inheriting map; endpoint: 2 entries (s3.us-west-1.{account_name}.lyve.seagate.com, s3.eu-west-1.{account_name}.lyve.seagate.com); location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: use_multipart_etag=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `LyveCloud` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `LyveCloud` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/LyveCloud.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Magalu.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Magalu.yaml

## Purpose
Embedded S3 provider descriptor for Magalu Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Magalu`, `description` is `Magalu Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: endpoint: 2 entries (br-se1.magaluobjects.com, br-ne1.magaluobjects.com); acl: empty/default-inheriting map; storage_class: 2 entries (STANDARD, GLACIER_IR). Advanced booleans: bucket_acl. Quirks: list_version=1, force_path_style=true, list_url_encode=false, use_multipart_etag=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Magalu` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Magalu` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Magalu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Mega.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Mega.yaml

## Purpose
Embedded S3 provider descriptor for MEGA S4 Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Mega`, `description` is `MEGA S4 Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: endpoint: 11 entries (s3.eu-amsterdam.megas4.com, s3.eu-luxembourg.megas4.com, s3.eu-paris.megas4.com, s3.eu-barcelona.megas4.com, s3.ca-montreal.megas4.com, plus 6 more). Advanced booleans: bucket_acl. Quirks: list_version=2, force_path_style=true, list_url_encode=true, use_multipart_etag=false, use_already_exists=false, copy_cutoff=9223372036854775807.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Mega` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Mega` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Mega.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Minio.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Minio.yaml

## Purpose
Embedded S3 provider descriptor for Minio Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Minio`, `description` is `Minio Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: empty/default-inheriting map; endpoint: empty/default-inheriting map; location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map; server_side_encryption: 2 entries (AES256, aws). Advanced booleans: bucket_acl, sse_customer_algorithm, sse_customer_key, sse_customer_key_base64, sse_customer_key_md5, sse_kms_key_id. Quirks: force_path_style=true.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Minio` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Minio` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Minio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Netease.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Netease.yaml

## Purpose
Embedded S3 provider descriptor for Netease Object Storage (NOS). It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Netease`, `description` is `Netease Object Storage (NOS)`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: empty/default-inheriting map; endpoint: empty/default-inheriting map; location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: list_version=1, list_url_encode=false, use_multipart_etag=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Netease` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Netease` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Netease.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/OVHcloud.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/OVHcloud.yaml

## Purpose
Embedded S3 provider descriptor for OVHcloud Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `OVHcloud`, `description` is `OVHcloud Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 15 entries (gra, rbx, sbg, eu-west-par, de, plus 10 more); endpoint: 15 entries (s3.gra.io.cloud.ovh.net, s3.rbx.io.cloud.ovh.net, s3.sbg.io.cloud.ovh.net, s3.eu-west-par.io.cloud.ovh.net, s3.de.io.cloud.ovh.net, plus 10 more); acl: empty/default-inheriting map; storage_class: 8 entries (EXPRESS_ONEZONE, STANDARD, STANDARD_IA, ONEZONE_IA, GLACIER, plus 3 more). Advanced booleans: bucket_acl. Quirks: none; S3 defaults apply.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `OVHcloud` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `OVHcloud` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/OVHcloud.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Other.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Other.yaml

## Purpose
Embedded S3 provider descriptor for Any other S3 compatible provider. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Other`, `description` is `Any other S3 compatible provider`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 1 entries (other-v2-signature); endpoint: empty/default-inheriting map; location_constraint: empty/default-inheriting map; acl: 6 entries (private, public-read, public-read-write, authenticated-read, bucket-owner-read, plus 1 more). Advanced booleans: bucket_acl. Quirks: list_version=1, force_path_style=true, list_url_encode=false, use_multipart_etag=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Other` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Other` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Other.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Outscale.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Outscale.yaml

## Purpose
Embedded S3 provider descriptor for OUTSCALE Object Storage (OOS). It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Outscale`, `description` is `OUTSCALE Object Storage (OOS)`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 5 entries (eu-west-2, us-east-2, us-west-1, cloudgouv-eu-west-1, ap-northeast-1); endpoint: 5 entries (oos.eu-west-2.outscale.com, oos.us-east-2.outscale.com, oos.us-west-1.outscale.com, oos.cloudgouv-eu-west-1.outscale.com, oos.ap-northeast-1.outscale.com); acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: force_path_style=true.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Outscale` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Outscale` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Outscale.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Petabox.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Petabox.yaml

## Purpose
Embedded S3 provider descriptor for Petabox Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Petabox`, `description` is `Petabox Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 5 entries (us-east-1, eu-central-1, ap-southeast-1, me-south-1, sa-east-1); endpoint: 6 entries (s3.petabox.io, s3.us-east-1.petabox.io, s3.eu-central-1.petabox.io, s3.ap-southeast-1.petabox.io, s3.me-south-1.petabox.io, plus 1 more); acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Petabox` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Petabox` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Petabox.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Qiniu.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Qiniu.yaml

## Purpose
Embedded S3 provider descriptor for Qiniu Object Storage (Kodo). It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Qiniu`, `description` is `Qiniu Object Storage (Kodo)`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 7 entries (cn-east-1, cn-east-2, cn-north-1, cn-south-1, us-north-1, plus 2 more); endpoint: 7 entries (s3-cn-east-1.qiniucs.com, s3-cn-east-2.qiniucs.com, s3-cn-north-1.qiniucs.com, s3-cn-south-1.qiniucs.com, s3-us-north-1.qiniucs.com, plus 2 more); location_constraint: 7 entries (cn-east-1, cn-east-2, cn-north-1, cn-south-1, us-north-1, plus 2 more); acl: empty/default-inheriting map; storage_class: 4 entries (STANDARD, LINE, GLACIER, DEEP_ARCHIVE). Advanced booleans: bucket_acl. Quirks: use_multipart_etag=false, list_url_encode=false, force_path_style=true, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Qiniu` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Qiniu` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Qiniu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Rabata.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Rabata.yaml

## Purpose
Embedded S3 provider descriptor for Rabata Cloud Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Rabata`, `description` is `Rabata Cloud Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 3 entries (us-east-1, eu-west-1, eu-west-2); endpoint: 3 entries (s3.us-east-1.rabata.io, s3.eu-west-1.rabata.io, s3.eu-west-2.rabata.io); location_constraint: 3 entries (us-east-1, eu-west-1, eu-west-2). Advanced booleans: none. Quirks: none; S3 defaults apply.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Rabata` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Rabata` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Rabata.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/RackCorp.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/RackCorp.yaml

## Purpose
Embedded S3 provider descriptor for RackCorp Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `RackCorp`, `description` is `RackCorp Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 19 entries (global, au, au-nsw, au-qld, au-vic, plus 14 more); endpoint: 19 entries (s3.rackcorp.com, au.s3.rackcorp.com, au-nsw.s3.rackcorp.com, au-qld.s3.rackcorp.com, au-vic.s3.rackcorp.com, plus 14 more); location_constraint: 19 entries (global, au, au-nsw, au-qld, au-vic, plus 14 more); acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: use_multipart_etag=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `RackCorp` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `RackCorp` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/RackCorp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Rclone.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Rclone.yaml

## Purpose
Embedded S3 provider descriptor for Rclone S3 Server. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Rclone`, `description` is `Rclone S3 Server`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: endpoint: empty/default-inheriting map. Advanced booleans: none. Quirks: force_path_style=true, use_multipart_etag=false, use_already_exists=false, copy_cutoff=9223372036854775807.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Rclone` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Rclone` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Rclone.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Scaleway.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Scaleway.yaml

## Purpose
Embedded S3 provider descriptor for Scaleway Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Scaleway`, `description` is `Scaleway Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 3 entries (nl-ams, fr-par, pl-waw); endpoint: 3 entries (s3.nl-ams.scw.cloud, s3.fr-par.scw.cloud, s3.pl-waw.scw.cloud); acl: empty/default-inheriting map; storage_class: 3 entries (STANDARD, GLACIER, ONEZONE_IA). Advanced booleans: bucket_acl. Quirks: max_upload_parts=1000.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Scaleway` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Scaleway` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Scaleway.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/SeaweedFS.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/SeaweedFS.yaml

## Purpose
Embedded S3 provider descriptor for SeaweedFS S3. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `SeaweedFS`, `description` is `SeaweedFS S3`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: empty/default-inheriting map; endpoint: 1 entries (localhost); location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: list_version=1, force_path_style=true, list_url_encode=false, use_multipart_etag=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `SeaweedFS` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `SeaweedFS` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/SeaweedFS.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Selectel.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Selectel.yaml

## Purpose
Embedded S3 provider descriptor for Selectel Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Selectel`, `description` is `Selectel Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 6 entries (ru-1, ru-3, ru-7, gis-1, kz-1, plus 1 more); endpoint: 6 entries (s3.ru-1.storage.selcloud.ru, s3.ru-3.storage.selcloud.ru, s3.ru-7.storage.selcloud.ru, s3.gis-1.storage.selcloud.ru, s3.kz-1.storage.selcloud.ru, plus 1 more). Advanced booleans: none. Quirks: list_url_encode=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Selectel` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Selectel` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Selectel.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Servercore.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Servercore.yaml

## Purpose
Embedded S3 provider descriptor for Servercore Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Servercore`, `description` is `Servercore Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 5 entries (ru-1, gis-1, ru-7, uz-2, kz-1); endpoint: 5 entries (s3.ru-1.storage.selcloud.ru, s3.gis-1.storage.selcloud.ru, s3.ru-7.storage.selcloud.ru, s3.uz-2.srvstorage.uz, s3.kz-1.srvstorage.kz). Advanced booleans: bucket_acl. Quirks: list_url_encode=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Servercore` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Servercore` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Servercore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/SpectraLogic.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/SpectraLogic.yaml

## Purpose
Embedded S3 provider descriptor for Spectra Logic Black Pearl. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `SpectraLogic`, `description` is `Spectra Logic Black Pearl`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: endpoint: empty/default-inheriting map. Advanced booleans: none. Quirks: force_path_style=true.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `SpectraLogic` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `SpectraLogic` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/SpectraLogic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Storj.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Storj.yaml

## Purpose
Embedded S3 provider descriptor for Storj (S3 Compatible Gateway). It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Storj`, `description` is `Storj (S3 Compatible Gateway)`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: endpoint: 1 entries (gateway.storjshare.io). Advanced booleans: none. Quirks: use_already_exists=false, copy_cutoff=9223372036854775807, min_chunk_size=67108864.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Storj` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Storj` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Storj.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Synology.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Synology.yaml

## Purpose
Embedded S3 provider descriptor for Synology C2 Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Synology`, `description` is `Synology C2 Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 5 entries (eu-001, eu-002, us-001, us-002, tw-001); endpoint: 5 entries (eu-001.s3.synologyc2.net, eu-002.s3.synologyc2.net, us-001.s3.synologyc2.net, us-002.s3.synologyc2.net, tw-001.s3.synologyc2.net); location_constraint: empty/default-inheriting map. Advanced booleans: none. Quirks: use_multipart_etag=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Synology` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Synology` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Synology.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/TencentCOS.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/TencentCOS.yaml

## Purpose
Embedded S3 provider descriptor for Tencent Cloud Object Storage (COS). It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `TencentCOS`, `description` is `Tencent Cloud Object Storage (COS)`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: endpoint: 18 entries (cos.ap-beijing.myqcloud.com, cos.ap-nanjing.myqcloud.com, cos.ap-shanghai.myqcloud.com, cos.ap-guangzhou.myqcloud.com, cos.ap-chengdu.myqcloud.com, plus 13 more); acl: 6 entries (default, public-read, public-read-write, authenticated-read, bucket-owner-read, plus 1 more); storage_class: 3 entries (STANDARD, ARCHIVE, STANDARD_IA). Advanced booleans: bucket_acl. Quirks: list_version=1, use_multipart_etag=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `TencentCOS` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `TencentCOS` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/TencentCOS.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Wasabi.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Wasabi.yaml

## Purpose
Embedded S3 provider descriptor for Wasabi Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Wasabi`, `description` is `Wasabi Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: empty/default-inheriting map; endpoint: 14 entries (s3.wasabisys.com, s3.us-east-2.wasabisys.com, s3.us-central-1.wasabisys.com, s3.us-west-1.wasabisys.com, s3.ca-central-1.wasabisys.com, plus 9 more); location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: none; S3 defaults apply.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Wasabi` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Wasabi` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Wasabi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Zadara.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Zadara.yaml

## Purpose
Embedded S3 provider descriptor for Zadara Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Zadara`, `description` is `Zadara Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 1 entries (us-east-1); endpoint: empty/default-inheriting map. Advanced booleans: none. Quirks: force_path_style=true.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Zadara` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Zadara` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Zadara.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Zata.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/Zata.yaml

## Purpose
Embedded S3 provider descriptor for Zata (S3 compatible Gateway). It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Zata`, `description` is `Zata (S3 compatible Gateway)`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 1 entries (us-east-1); endpoint: 1 entries (idr01.zata.ai); location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: use_multipart_etag=false, might_gzip=false, use_unsigned_payload=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Zata` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Zata` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/Zata.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/us3.yaml -->
# sources/user-network-fs/rclone/backend/s3/provider/us3.yaml

## Purpose
Embedded S3 provider descriptor for US3 Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `US3`, `description` is `US3 Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: endpoint: 23 entries (s3-cn-bj.ufileos.com, s3-cn-wlcb.ufileos.com, s3-cn-sh2.ufileos.com, s3-cn-gd.ufileos.com, s3-hk.ufileos.com, plus 18 more); acl: 2 entries (private, public-read); storage_class: 3 entries (STANDARD, ARCHIVE, STANDARD_IA). Advanced booleans: bucket_acl. Quirks: list_version=1, use_multipart_etag=false, use_already_exists=false, list_url_encode=true.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `US3` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `US3` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/provider/us3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/providers.go -->
# sources/user-network-fs/rclone/backend/s3/providers.go

## Purpose
S3 provider loader: embeds provider YAML and mutates S3 registration options/examples/quirks.

## Important APIs, Types, And Functions
Important surface: YamlMap, Quirks, Provider, addProvidersToInfo, loadProvider, loadProviders, constructProviders.

## Control Flow
loads provider/*.yaml, fatal-errors on missing/invalid Other, sorts AWS first and Other last, merges map examples and provider booleans into fs.Options

## State And Persistence
compile-time embedded YAML and runtime option descriptors.

## Dependencies And Integration Points
embed, yaml.v3, ordered-map, rclone fs.

## Risks And Test Signals
Risks and useful test signals: duplicate provider names, option-name switch drift, schema drift, fatal provider load failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/s3/providers.go -->

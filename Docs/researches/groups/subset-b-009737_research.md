# Research Group: subset-b-009737

This grouped report covers the Azure Blob auth/backend files, Azure Files backend files, and B2 API type files listed for `subset-b-009737`. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azureblob/auth/auth.go -->
# Research: sources/user-network-fs/rclone/backend/azureblob/auth/auth.go

## Purpose
This package centralizes authentication and Azure SDK client construction for rclone's Azure storage backends. It defines common config options and a generic `NewClient` factory used by both Blob and Files backends, abstracting over SDK client option types and shared-key credential types.

## Important APIs, Types, and Functions
- `ConfigOptions` declares shared rclone config keys: account/key, SAS URL, connection string, service principal credentials, certificate auth, username/password, environment auth, managed identity, Azure CLI auth, emulator, and endpoint override.
- `Options` is the parsed config struct embedded by Azure backend options.
- `servicePrincipalCredentials` and `parseServicePrincipalCredentials` load `az ad sp create-for-rbac` JSON containing `appId`, `password`, and `tenant`.
- `transporter`, `newTransporter`, and `Do` wrap rclone's `fshttp.NewTransport` as an Azure `policy.Transporter`, adding an APN/rclone user agent via context config.
- `NewClientOpts[Client, ClientOptions, SharedKeyCredential]` is the generic adapter layer that supplies Azure SDK constructors and a callback to inject `policy.ClientOptions`.
- `NewClientResult` returns the constructed SDK client, optional token credential, booleans for shared-key/anonymous auth, and the container parsed from a container-level SAS.
- `NewClient` selects exactly one authentication path and builds the SDK service client.

## Control Flow
`NewClient` first builds Azure policy client options with rclone's transport, then lets the backend copy those into the concrete SDK options. Authentication is selected by a priority-ordered `switch`: environment/default Azure credential, emulator, account/key, SAS URL, connection string, client secret, client certificate, username/password, service principal file, managed identity, workload identity, Azure CLI, or anonymous account-only access. SAS URLs are parsed to distinguish account-level SAS from blob container-level SAS; for container SAS, the endpoint is rewritten without the container path and the result records the constrained container. If a client was not already built by SAS or connection string, `NewClient` derives `https://<account>.<defaultBaseURL>` unless an endpoint override exists, then instantiates the concrete SDK client with shared key, token credential, or no credential.

## State and Persistence
The file persists no remote state itself. It mutates the passed `Options` in limited cases by filling account/key/endpoint defaults for environment or emulator auth and by resolving endpoint from account. Credentials are passed in memory to Azure SDK constructors. The filesystem side effect is reading certificate files or service-principal JSON files after shell expansion.

## Dependencies and Integration Points
It depends on `azcore`, `policy`, `azidentity`, and blob SAS parsing from Azure SDK; rclone config, obscure password reveal, environment expansion, and HTTP transport utilities; and backend-provided constructors. `azureblob.NewFs` and `azurefiles.newFsFromOptions` supply the concrete `NewClientOpts`.

## Risks and Edge Cases
- Auth selection is priority based; conflicting config values silently prefer earlier branches, except MSI identity ID conflicts are explicitly rejected.
- `ClientCertificatePassword` handling appears to reveal `opt.Password` rather than `opt.ClientCertificatePassword`, which risks certificate auth failure when a separate certificate password is configured.
- MSI object ID is declared in config but explicitly unsupported in the current branch.
- Workload identity branch is ordered after `UseMSI`, so configs with both `UseMSI` and workload fields will take the MSI branch.
- Container-level SAS validation applies only when `conf.Blob` is true; Azure Files treats SAS differently through the generic no-credential client path.
- Anonymous auth requires `account` and depends on public endpoint access; missing endpoint with missing account fails.

## Test Signals
There is no direct test file for `auth.go` in this group. Azure Files has a skipped `InternalTestAuth` matrix that would exercise connection string, account/key, and SAS URL via `newFsFromOptions`, but credentials are intentionally blank. Azure Blob and Files integration tests indirectly validate working client construction for configured remotes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azureblob/auth/auth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azureblob/azureblob.go -->
# Research: sources/user-network-fs/rclone/backend/azureblob/azureblob.go

## Purpose
This file implements rclone's Microsoft Azure Blob Storage backend on supported platforms. It registers the `azureblob` remote, maps rclone filesystem operations to Azure Blob SDK APIs, handles containers as buckets, supports metadata/tags, tiering, directory markers, gzip behavior, chunked upload, server-side copy, and cleanup of problematic uncommitted block state.

## Important APIs, Types, and Functions
- `Options` embeds shared Azure auth options and adds blob-specific knobs such as `chunk_size`, copy concurrency/cutoff, access tier, archive overwrite policy, checksum disable, encoding, public access, directory markers, no-head behavior, snapshot delete policy, and gzip decompression.
- `Fs` stores backend state: root, parsed options, Azure `service.Client`, cached `container.Client`s, auth mode flags, bucket cache, pacer, upload/copy concurrency tokens, public access, gzip warning state, and cached user delegation credentials.
- `Object` stores per-blob state: remote, modtime, base64 MD5, size, MIME type, tier, user metadata, blob tags, and content encoding.
- Registration in `init` exposes metadata help, config options, and feature flags.
- `NewFs` parses config, validates access tier/public access/list chunk/chunk size, constructs auth client via `auth.NewClient`, configures gzip accept-encoding policy, initializes caches and features, and detects when the root path names an existing blob.
- Listing is implemented by `list`, `listDir`, `listContainers`, `ListP`, and `ListR` using Azure pagers.
- Upload paths are `Put`, `PutStream`, `prepareUpload`, `uploadSinglepart`, `OpenChunkWriter`, `azChunkWriter.WriteChunk`, `azChunkWriter.Close`, and `uploadMultipart`.
- Copy paths are `Copy`, `copySinglepart`, `copyMultipart`, `getAuth`, and `getUserDelegation`.
- Metadata helpers include `mapMetadataToAzure`, `assembleCopyParams`, `applyMappedMetadata`, `setMetadata`, `Metadata`, `SetModTime`, and decode helpers for property/download/list responses.
- Container and directory operations are `Mkdir`, `makeContainer`, `createDirectoryMarker`, `Rmdir`, `Purge`, `deleteContainer`, and `isEmpty`.
- Tier operations are `AccessTier`, `SetTier`, `GetTier`, and `parseTier`.

## Control Flow
Reads and listings split rclone remotes into container and blob path using `bucket.Split` plus encoding transforms. At the root, list operations enumerate containers; below a container, blob hierarchy/list pagers produce `fs.Dir` and `Object` entries. Directory marker support treats zero-size slash-suffixed blobs or `hdi_isfolder=true` metadata as directories and can create/remove marker blobs during mkdir/rmdir.

Uploads first call `prepareUpload`, which ensures parent containers/directories, maps metadata and tags, sets default content type, preserves mtime in user metadata, optionally computes Content-MD5 from source hash, and applies upload headers. Small known-size uploads read into a retryable multipart buffer and call `blockblob.Upload`; large or unknown-size uploads use rclone's multipart helper and `OpenChunkWriter`. Each chunk gets a random-suffixed block ID, transactional MD5, retry pacing, and later `CommitBlockList` with metadata, tags, tier, and HTTP headers.

Copies first validate same backend type, create parents, then choose single-part `StartCopyFromURL` or multipart `StageBlockFromURL` plus `CommitBlockList`. Same-storage-account copies prefer Copy Blob when enabled. Microsoft Entra ID cross-account copies force multipart because token auth is not used directly by Copy Blob. Source auth is converted to a plain URL for same-account copies, a user-delegation SAS for token credentials, a shared-key SAS for shared key credentials, or the existing URL for anonymous/SAS remotes.

Downloads reject archive-tier blobs, honor range/seek options, issue `DownloadStream`, refresh metadata from the download response, and either return compressed bytes or wrap a gzip reader when `--azureblob-decompress` is enabled.

## State and Persistence
Persistent remote state includes containers, block blobs, metadata, tags, content headers, access tiers, snapshots deletion behavior, and optional directory marker blobs. Local backend state caches container clients, container existence/deletion status, object metadata, user delegation SAS keys, and warning `sync.Once`s. `metadataMu` is a package-level lock protecting object metadata map access. Uncommitted blocks are remote transient state; `clearUncommittedBlocks` attempts to resolve `InvalidBlobOrBlock` by re-committing existing committed block IDs or committing an empty list and deleting the created blob.

## Dependencies and Integration Points
The backend integrates with Azure `azblob` service/container/blob/blockblob clients, Azure SAS/user delegation APIs, rclone `fs` optional interfaces, config mapping, bucket cache, encoders, pacer retries, chunk size calculator, multipart upload helper, memory pool accounting, transfer accounting, and `errgroup`. It shares auth with Azure Files through `backend/azureblob/auth`.

## Risks and Edge Cases
- Directory marker logic must distinguish real zero-byte files from folders; metadata or trailing slash can make a blob appear as a directory.
- Metadata is case-insensitive in Azure but normalized to lower case locally; duplicate casing could otherwise break shared-key signing.
- `getMetadata` creates pointers to range-loop values, which is acceptable because each `v` escapes per iteration but remains subtle.
- `NoHeadObject` can create objects without metadata until a later read/download fills fields.
- Gzip decompression makes size and hash unknown and changes download bytes, so sync comparisons can be affected.
- Archive-tier overwrite can delete the old blob first when `archive_tier_delete` is enabled, which is an explicit data-loss tradeoff if the replacement upload fails.
- Single-part copy sets mapped headers post-copy; there is a window where copied headers may not yet match requested metadata.
- Multipart copy uses large concurrency and optional global token limiting; misconfigured high concurrency can stress service limits.
- User delegation SAS caching depends on wall-clock expiry and token permissions.
- The retry path for `InvalidBlobOrBlock` serializes around in-flight operations and clears uncommitted blocks only once; overlap with other writers to the same blob remains hazardous.

## Test Signals
`azureblob_internal_test.go` covers block ID creation/validation, backend feature flags, recovery from uncommitted blocks during multipart upload/copy, metadata/header/tag propagation across upload and copy paths, invalid tag rejection, mtime injection under metadata mode, and gzip download behavior. `azureblob_test.go` runs full fstests twice, once with directory markers enabled, tests chunked upload configuration hooks, and validates accepted access tiers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azureblob/azureblob.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azureblob/azureblob_internal_test.go -->
# Research: sources/user-network-fs/rclone/backend/azureblob/azureblob_internal_test.go

## Purpose
This file provides Azure Blob backend internal integration tests that go beyond generic fstests. It exercises implementation-specific block ID generation, feature flags, uncommitted block recovery, gzip content-encoding behavior, and metadata/header/tag mapping across upload and server-side copy paths.

## Important APIs, Types, and Functions
- `TestBlockIDCreator` validates `newBlockIDCreator`, `newBlockID`, and `checkID`.
- `(*Fs).testFeatures` checks that `SetTier` and `GetTier` feature flags are enabled.
- `ReadSeekCloser` adapts a `strings.Reader` for direct SDK `StageBlock`.
- `stageBlockWithoutCommit` creates remote uncommitted block state without committing a blob.
- `testWriteUncommittedBlocks` forces multipart upload/copy over existing uncommitted block IDs.
- `gz` and `md5sum` support gzip behavior checks.
- `testGzipEncoding` verifies compressed-object reads with and without backend decompression.
- `InternalTest` registers internal subtests for fstests.
- `getProps`, `assertHeadersAndMetadata`, and `getTagsMap` inspect Azure properties and tags through SDK calls.
- `testMetadataPaths` covers metadata mapping for single-part/multipart uploads and copies.

## Control Flow
The block ID test uses deterministic random bytes after checking randomness is nonzero and distinct. The uncommitted block test stages uncommitted data, confirms no object exists, uploads a multi-chunk object over that path, then stages another path and copies over it to confirm cleanup/retry behavior. Metadata tests create source objects with `fstests.PutTestContentsMetadata`, use rclone config contexts with `Metadata` and `MetadataSet`, perform uploads or `f.Copy`, then read raw blob properties and tags to assert Azure headers/user metadata/tags. The invalid tag subtest builds a static object with malformed `x-ms-tags` and expects `Put` to fail.

## State and Persistence Behavior
These tests mutate live Azure containers by creating blobs, uncommitted blocks, tags, headers, and copied objects, with most subtests deferring object removal. `testWriteUncommittedBlocks` intentionally creates transient uncommitted block state to exercise production cleanup. `testGzipEncoding` toggles `f.opt.Decompress` within a subtest and restores it.

## Dependencies and Integration Points
The tests use Azure SDK `blob` and `blockblob` clients directly, rclone `fstests`, `fstest` items, random data generation, object metadata helpers, and `testify` assertions. They rely on a configured live Azure Blob test remote and are integrated through the backend's `InternalTest` hook.

## Risks and Edge Cases
- Tests are integration-heavy and depend on service credentials, network behavior, and Azure support for tags/tier operations.
- `testing.Short()` skips the metadata-path suite, so fast test runs miss much of the metadata regression coverage.
- The uncommitted block test manipulates remote state that can linger if cleanup fails before deferred removal.
- Gzip tests validate a compressed payload path where `Size()` and `Hash()` intentionally become unknown under decompression.
- Metadata tests assume Azure service casing/behavior for headers and tags while normalizing user metadata keys.

## Test Signals
This file itself is the primary signal for several tricky backend behaviors: random block IDs, uncommitted block repair, gzip accept/decompress semantics, metadata mapper integration, copy metadata fallback, tag parsing, and tier feature advertisement.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azureblob/azureblob_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azureblob/azureblob_test.go -->
# Research: sources/user-network-fs/rclone/backend/azureblob/azureblob_test.go

## Purpose
This file wires the Azure Blob backend into rclone's generic filesystem integration test suite and adds a focused unit test for access tier validation. It also exposes test-only setters used by fstests to tune chunk size and copy cutoff.

## Important APIs, Types, and Functions
- `TestIntegration` runs `fstests.Run` against `TestAzureBlob:` with tier tests for Hot, Cool, and Cold, chunked upload enabled, and `use_copy_blob=false`.
- `TestIntegration2` runs the same generic suite with `directory_markers=true` unless an explicit remote is supplied.
- `(*Fs).SetUploadChunkSize` and `(*Fs).SetCopyCutoff` adapt private setters to fstests interfaces.
- Interface assertions ensure `Fs` satisfies `fstests.SetUploadChunkSizer` and `fstests.SetCopyCutoffer`.
- `TestValidateAccessTier` validates case-insensitive accepted tiers and rejection of empty/unknown values.

## Control Flow
Both integration tests delegate broad behavior to `fstests.Run`, which exercises object create/read/update/delete, listing, copy/move capabilities where advertised, hashes, modtimes, and optional internal tests. The second test skips when `-remote` is provided to avoid unexpected config mutation and specifically validates directory marker mode. The access tier test iterates a table of tier strings through `validateAccessTier`.

## State and Persistence Behavior
The integration tests create and remove containers/blobs in the configured Azure test remote. Extra config changes are scoped through fstests. The setter methods mutate `f.opt.ChunkSize` and `f.opt.CopyCutoff` during tests and return old values for restoration.

## Dependencies and Integration Points
The file depends on rclone `fs`, `fstest`, and `fstests`, plus `testify/assert`. It is the public test entry point that indirectly triggers `Fs.InternalTest` from `azureblob_internal_test.go`.

## Risks and Edge Cases
- Live Azure credentials and remote naming are required for full coverage.
- `use_copy_blob=false` biases tests toward multipart/server-side copy behavior and may not fully cover same-account Copy Blob defaults.
- `TestIntegration2` is skipped under explicit `-remote`, so directory marker coverage can be absent in custom test runs.
- The access tier unit test does not include all behavior around archive tier update/delete, only validation.

## Test Signals
The file verifies broad conformance to rclone's filesystem contract, chunked upload tunability, tier feature expectations, and access-tier input validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azureblob/azureblob_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azureblob/azureblob_unsupported.go -->
# Research: sources/user-network-fs/rclone/backend/azureblob/azureblob_unsupported.go

## Purpose
This platform stub prevents Go from reporting "no buildable Go source files" for the `azureblob` package on unsupported targets. The real backend is excluded on `plan9`, `solaris`, and `js`; this file keeps the package present there.

## Important APIs, Types, and Functions
The file declares only package `azureblob` under build tag `plan9 || solaris || js`. It exports no types, functions, variables, or registration hooks.

## Control Flow
There is no runtime control flow. Build constraints select this file only where `azureblob.go` is not compiled.

## State and Persistence Behavior
No state is held and no persistence occurs.

## Dependencies and Integration Points
The only integration point is Go's build system. On unsupported platforms the backend has no implementation and no `fs.Register` call from this package.

## Risks and Edge Cases
Code importing platform-specific backend symbols will not find them on these targets unless guarded by matching build tags. This is intentional because the Azure SDK/backend implementation is not available there.

## Test Signals
There are no tests for this stub. Successful package loading/building on unsupported targets is the only signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azureblob/azureblob_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azurefiles/azurefiles.go -->
# Research: sources/user-network-fs/rclone/backend/azurefiles/azurefiles.go

## Purpose
This file implements rclone's Microsoft Azure Files backend on supported platforms. It maps rclone filesystem operations onto Azure File Share APIs for a configured share, including directory creation/removal, listing, uploads with preallocated size, server-side copy/move, random-access writes, MIME/MD5/modtime properties, and quota reporting.

## Important APIs, Types, and Functions
- `Options` embeds shared Azure auth options and adds `share_name`, `chunk_size`, `max_stream_size`, `upload_concurrency`, and encoding.
- `Fs` stores backend name/root/options, feature flags, a share client, and the root directory client.
- `Object` stores remote, size, MD5 bytes, modtime, and content type.
- `newFsFromOptions` builds the Azure Files service client through the shared auth helper, sets `FileRequestIntent=backup` for token credentials, binds to the configured share/root directory, advertises features, and detects file roots.
- `NewFs` parses config and delegates to `newFsFromOptions`.
- Path helpers `absPath`, `dirClient`, and `fileClient` encode rclone paths under `root`.
- Directory and listing methods include `absMkdir`, `Mkdir`, `mkParentDir`, `Rmdir`, `List`, and `ListP`.
- Object methods include `NewObject`, `setMetadata`, `getMetadata`, `Hash`, `MimeType`, `ModTime`, `SetModTime`, `Open`, `Update`, and `Remove`.
- Server-side operations are `Move`, `DirMove`, and `Copy`.
- Random write support is implemented by `writerAt`, `WriteAt`, `Close`, and `OpenWriterAt`.
- `About` returns share usage from `GetStatistics`.

## Control Flow
Initialization constructs a generic Azure service client using shared auth callbacks, then obtains a share client and root directory client for `ShareName`. `NewFs` also probes whether the configured root points to a file; if so it rewrites root to the parent and returns `fs.ErrorIsFile`.

Listing checks directory existence with `GetProperties`, pages `ListFilesAndDirectories`, converts directories to `fs.Dir` entries with LastWriteTime/ID/size when present, and converts files to `Object` entries with size and modtime from listing properties.

Uploads call `Update`. If size is unknown, the file is temporarily created at `max_stream_size` and the stream is counted; otherwise the known size is used. New files create parent directories and call `Create`; existing files are resized if needed. The data is sent through `UploadStream` with configured chunk size/concurrency. MD5 comes from source hash if available or is calculated via `io.TeeReader`. After upload, `SetHTTPHeaders` sets final content length, SMB LastWriteTime, MD5, content type, and supported content headers, truncating unknown-size uploads to actual bytes.

Reads honor range and seek options with `DownloadStream`. Server-side `Move` and `DirMove` use Azure rename APIs with parent creation and destination existence checks. `Copy` calls `StartCopyFromURL`, polls while pending, and returns the new object. `OpenWriterAt` creates/truncates a file and `WriteAt` resizes as needed under a mutex before uploading byte ranges.

## State and Persistence
Persistent remote state includes shares, directories, files, file sizes, content, SMB LastWriteTime, content headers, and Content-MD5. Unknown-size uploads may temporarily reserve up to `max_stream_size` bytes. Local state is minimal: object metadata caches, feature flags, and writerAt size protected by a mutex. There is no pacer/retry layer in this file despite a TODO noting it.

## Dependencies and Integration Points
The backend depends on Azure `azfile` service/share/directory/file clients, file error helpers, the shared Azure auth package, rclone `fs` optional interfaces, config parsing, path encoders, list helper, hash support, and counting readers. It advertises `PutStreamer`, `Abouter`, `Mover`, `DirMover`, `Copier`, `OpenWriterAter`, `ListPer`, and MIME support.

## Risks and Edge Cases
- `share_name` is documented as required but `newFsFromOptions` does not explicitly validate non-empty input before creating a share client.
- Unknown-size uploads can consume `max_stream_size` quota temporarily; interruption before final `SetHTTPHeaders` may leave an oversized partial file.
- There is no backend pacer/retry wrapper, so transient Azure failures surface directly.
- The TODO block notes incomplete metadata support and HTTP header gaps; only selected headers from open options are written.
- `SetModTime` preserves current MD5/content type values, but if they were not loaded it may set nil/empty properties.
- `ModTime` returns `time.Now()` when unknown, which can destabilize comparisons for objects created from sparse listing data without LastWriteTime.
- `Copy` uses the source file URL directly; cross-auth/cross-account scenarios are constrained by what the URL permits.
- `writerAt.Close` does not set MD5, modtime, or content type after random writes.

## Test Signals
`azurefiles_test.go` runs generic fstests against `TestAzureFiles:`. `azurefiles_internal_test.go` defines a skipped auth matrix for connection string, account/key, and SAS URL construction. There are no focused tests in this group for unknown-size upload truncation, random writes, copy/move edge cases, or header preservation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azurefiles/azurefiles.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azurefiles/azurefiles_internal_test.go -->
# Research: sources/user-network-fs/rclone/backend/azurefiles/azurefiles_internal_test.go

## Purpose
This file defines Azure Files backend internal tests, currently limited to an authentication construction matrix that is skipped by default because required credentials are not stored in the repository.

## Important APIs, Types, and Functions
- `(*Fs).InternalTest` registers the `Authentication` subtest for rclone fstests.
- The interface assertion confirms `*Fs` implements `fstests.InternalTester`.
- `InternalTestAuth` enumerates connection string, account/key, and SAS URL option shapes and calls `newFsFromOptions`.
- `randomString` produces a random directory name from an ASCII letter set for mkdir checks.

## Control Flow
`InternalTest` calls `t.Run("Authentication", f.InternalTestAuth)`. `InternalTestAuth` immediately calls `t.Skip`, so the credential cases are not executed unless the skip is removed and real values are supplied. The intended flow constructs a filesystem from each credential style, asserts no error, creates a random directory, and asserts mkdir succeeds.

## State and Persistence Behavior
In its current skipped state, no remote state is changed. If enabled, it would create random directories in the hard-coded share `test-rclone-oct-2023`.

## Dependencies and Integration Points
The test imports the shared Azure auth options, rclone fstests internal tester hook, context, math/rand, strings, and `testify/assert`. It directly targets `newFsFromOptions`, which makes it useful for auth behavior that would otherwise require config mapping.

## Risks and Edge Cases
- The test is skipped unconditionally, so it provides no automated CI signal.
- Credential fields in the table are empty placeholders and the share name is hard-coded.
- `math/rand` is unseeded, which is fine for test names but not unique across all possible parallel runs.
- It does not clean up directories after intended creation.

## Test Signals
Only the compile-time interface assertion and skipped-test registration are active. When manually enabled with credentials, it would validate that the shared auth helper can construct Azure Files clients for three credential styles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azurefiles/azurefiles_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azurefiles/azurefiles_test.go -->
# Research: sources/user-network-fs/rclone/backend/azurefiles/azurefiles_test.go

## Purpose
This file wires the Azure Files backend into rclone's generic filesystem integration test suite.

## Important APIs, Types, and Functions
- `TestIntegration` creates a nil `*Object` marker and calls `fstests.Run` with `RemoteName: "TestAzureFiles:"`.

## Control Flow
The generic fstests runner drives backend operations through the advertised rclone interfaces. The file does not customize chunk sizes, features, tiers, or extra config.

## State and Persistence Behavior
When run with a configured `TestAzureFiles:` remote, fstests create, list, update, read, copy/move where supported, and remove files/directories in the Azure File Share.

## Dependencies and Integration Points
The file depends only on Go testing and rclone `fstests`. It indirectly exercises `azurefiles.go` methods and may invoke `Fs.InternalTest` from `azurefiles_internal_test.go`, though that internal auth test skips.

## Risks and Edge Cases
- Coverage depends on live Azure Files credentials and an available test share.
- No backend-specific options are varied, so unknown-size uploads, OpenWriterAt, and some copy/move edge cases may not receive focused coverage here.
- Failures are likely integration/environment sensitive.

## Test Signals
This is the main automated conformance signal for the Azure Files backend against rclone's filesystem contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azurefiles/azurefiles_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azurefiles/azurefiles_unsupported.go -->
# Research: sources/user-network-fs/rclone/backend/azurefiles/azurefiles_unsupported.go

## Purpose
This platform stub keeps the `azurefiles` package buildable on unsupported targets where the real backend is excluded.

## Important APIs, Types, and Functions
The file declares package `azurefiles` under build tag `plan9 || js` and exports no implementation.

## Control Flow
There is no runtime control flow. The Go build system selects this file for unsupported platforms.

## State and Persistence Behavior
No state or persistence behavior exists.

## Dependencies and Integration Points
The only dependency is build-tag selection. Since the implementation file is not compiled, the backend is not registered on these platforms.

## Risks and Edge Cases
Code expecting Azure Files backend symbols must be guarded for these platforms. This is intentional package hygiene rather than functional backend behavior.

## Test Signals
There are no direct tests; successful package loading/building on unsupported targets is the signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/azurefiles/azurefiles_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/b2/api/types.go -->
# Research: sources/user-network-fs/rclone/backend/b2/api/types.go

## Purpose
This file defines Go representations of Backblaze B2 API request and response payloads plus small helpers for B2 error fatality, millisecond timestamps, and versioned filenames. It is a schema and utility layer consumed by higher-level B2 backend code.

## Important APIs, Types, and Functions
- `Error` models B2 JSON error responses, implements `error`, and marks HTTP 403 as fatal via `Fatal`.
- `Bucket`, `LifecycleRule`, and `ServerSideEncryption` model bucket configuration and encryption settings.
- `Timestamp` wraps `time.Time` with B2's millisecond-since-epoch JSON encoding and filename version helpers.
- `HasVersion`, `Timestamp.AddVersion`, and `RemoveVersion` delegate version parsing/formatting to `lib/version`.
- `File` and `FileInfo` model listed and uploaded file versions.
- `StorageAPI` and `AuthorizeAccountResponse` represent authorization discovery, allowed capabilities, upload/download API URLs, and part-size recommendations.
- Request/response structs cover bucket listing, file listing, upload URL, download authorization, bucket creation/update/delete, file delete/hide/info, large file start/upload part/finish/cancel, file copy, and part copy.

## Control Flow
Most types are passive JSON schemas. `Timestamp.MarshalJSON` converts UTC nanoseconds to integer milliseconds and writes a JSON number. `UnmarshalJSON` parses a JSON number into seconds plus nanosecond remainder and forces UTC. `Equal` returns false if either side is zero before calling `time.Equal`. Version helpers only wrap shared filename-version utilities. `Error.Fatal` makes retry policy callers treat 403 authorization failures as non-retryable.

## State and Persistence Behavior
The file has no persistence side effects. It defines in-memory structs that serialize to and from B2 API JSON. Timestamp conversion truncates sub-millisecond precision during marshaling, matching B2's contract.

## Dependencies and Integration Points
It depends on rclone `fserrors.Fataler` for fatal retry classification and `lib/version` for timestamp-in-filename behavior. Higher-level B2 API client code relies on the JSON tags matching B2 endpoints, especially optional fields for lifecycle rules, encryption, metadata directives, destination buckets, and large file operations.

## Risks and Edge Cases
- `Timestamp.MarshalJSON` has a pointer receiver; callers with non-addressable values may rely on encoding/json addressability behavior.
- Timestamp marshaling truncates nanoseconds to milliseconds, so round trips lose sub-millisecond precision.
- `Timestamp.Equal` deliberately returns false for two zero timestamps, which is nonstandard and must be understood by callers.
- `StorageAPI.Allowed.NamePrefix` is `any`, reflecting flexible/null API values but pushing type handling to callers.
- Struct comments include one stale copy/paste note: `DeleteBucketRequest` says "used to create a bucket".
- Schema drift in B2 API fields would not be caught without integration tests or JSON fixture tests.

## Test Signals
`types_test.go` tests timestamp marshal/unmarshal, zero detection, and `Equal` semantics. There are no tests in this group for request/response JSON field coverage, fatal error classification, version filename helpers, or encryption/copy schemas.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/b2/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/b2/api/types_test.go -->
# Research: sources/user-network-fs/rclone/backend/b2/api/types_test.go

## Purpose
This file tests the B2 API `Timestamp` helper semantics: millisecond JSON encoding/decoding, zero detection, and equality behavior.

## Important APIs, Types, and Functions
- Package-level fixtures define `emptyT`, `t0` at `1970-01-01T01:01:01.123456789Z`, and `t1` at `2001-02-03T04:05:06.123000000Z`.
- `TestTimestampMarshalJSON` calls `MarshalJSON` directly and compares decimal millisecond strings.
- `TestTimestampUnmarshalJSON` parses a millisecond number and compares the resulting `time.Time`.
- `TestTimestampIsZero` checks zero and nonzero values.
- `TestTimestampEqual` asserts that zero timestamps are never equal and nonzero timestamps compare as expected.

## Control Flow
The tests directly invoke methods rather than going through `encoding/json`. They use `require.NoError` before assertions where parsing/marshaling can fail. Equality tests include same-value comparisons with gocritic suppressions because identical receiver/argument calls are intentional.

## State and Persistence Behavior
No persistent state is touched. Fixtures are immutable package variables for test use.

## Dependencies and Integration Points
The test imports the `api` package externally as `api_test`, which validates exported behavior only. It uses rclone `fstest.Time` to create fixed UTC times and `testify` for assertions.

## Risks and Edge Cases
- Direct `MarshalJSON` calls do not test standard `encoding/json` interaction with pointer receiver methods.
- Tests do not cover invalid unmarshal input, negative or zero epoch values, sub-millisecond truncation beyond the selected fixture, filename version helpers, or `Error.Fatal`.
- The marshal expectation for `t0` confirms truncation from `.123456789` to `.123`, but this is implicit rather than named in the test.

## Test Signals
The tests pin the B2 timestamp contract and the deliberately nonstandard zero equality behavior, providing regression coverage for API time conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/b2/api/types_test.go -->

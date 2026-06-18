# subset-b-009750 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/onedrive/onedrive.go -->
# sources/user-network-fs/rclone/backend/onedrive/onedrive.go

Purpose: implements rclone's Microsoft OneDrive backend, including configuration, OAuth setup, drive selection, path addressing, directory caching, listing, uploads, server-side copy/move, metadata, public links, version cleanup, and change notifications. It registers the backend as `onedrive` and registers the `quickxor` hash type backed by `quickxorhash.New`.

Important APIs, types, and functions: `Options` carries region, upload, tenant, drive, metadata, link, version, hash, and encoding settings. `Fs` stores REST clients, pacer, dircache, drive identity, OAuth token renewer, and negotiated hash type. `Object` stores remote path, ID, size, mod time, hash, MIME type, OneNote state, and metadata. `Directory` is the directory entry with ID and metadata. `Config`, `chooseDrive`, `getRegionURL`, and `makeOauthConfig` implement the interactive configuration state machine for personal, business, SharePoint, URL, site ID, drive ID, search, tenant URL, national cloud, and client credential cases. `NewFs` validates chunk/cutoff settings, builds Graph root URLs, creates OAuth REST clients, fills features, resolves root IDs, configures hash behavior, creates `dircache`, and handles the `fs.ErrorIsFile` root-as-file case. The backend implements rclone interfaces for `fs.Fs`, `Purger`, `Copier`, `Mover`, `DirMover`, `DirCacheFlusher`, `Abouter`, `PublicLinker`, `CleanUpper`, `ListRer`, `ListPer`, `Shutdowner`, metadata and directory metadata interfaces.

Control flow: metadata lookup uses `readMetaDataForPath`, which prefers direct path addressing except for personal-drive shared-folder cases where it resolves a base normalized ID and calls `readMetaDataForPathRelativeToID`. URL construction is centralized in `newOptsCall`, `newOptsCallWithIDPath`, `newOptsCallWithRootPath`, and `newOptsCallWithPath`; these also contain China-region Vnet Graph API rewrites, so most methods avoid hand-built URLs. Listing uses `List` through `list.WithListP`, `ListP` for non-recursive pages, and `ListR` only when the `delta` option is enabled. `_listAll` handles pagination and deleted-item filtering for both children and delta responses. `itemToDirEntry` converts API items into `Directory` or `Object`, updates `dirCache`, and hides OneNote package entries unless configured otherwise.

Mutation and transfer flow: `Put` calls `createObject` then `Object.Update`. `Update` starts token renewal while active, rejects OneNote content writes, and chooses multipart for known sizes greater than or equal to `upload_cutoff`, singlepart for smaller known sizes, and rejects unknown sizes. Multipart uses `createUploadSession`, repeatable chunk readers, `uploadFragment`, position recovery on 416 responses, and cancellation through `atexit.OnError`. Singlepart uses `PUT /content` and then metadata update. `Copy` uses Graph async copy with a work-location poller, rejects unsupported personal/business cross-drive cases, removes existing destinations, waits via `waitForJob`, and then reapplies modtime and metadata. `Move` and `DirMove` PATCH parent references and preserve timestamps but reject cross-drive moves. Deletes use normal DELETE or `/permanentDelete` when `hard_delete` is set. `CleanUp` walks objects and removes old versions concurrently, bounded by global checker count.

State and persistence: remote state is Microsoft Graph drive items, permissions, versions, metadata, share links, and upload sessions. Local state is in-memory only: `dirCache`, pacer state, object metadata caches, OAuth token renewer, and config-derived options. Object IDs may be normalized as `driveID#itemID` for shared items. Modtime and creation time are mapped through OneDrive `fileSystemInfo`; hashes are extracted from Graph file hash facets and converted to rclone's selected hash representation.

Dependencies and integration points: depends on rclone `fs`, config, OAuth, `rest`, `dircache`, `operations`, `walk`, `pacer`, `readers`, `encoder`, and backend-specific `api`, `metadata`, and `quickxorhash` packages. It integrates deeply with Microsoft Graph v1.0, SharePoint tenant v2.0 URL mode, national cloud endpoints, rclone metadata mappers, range/open options, and optional change notification polling via delta links.

Risks: URL helper regressions are high risk, especially China-region rewrites, shared-with-me normalized IDs, and tenant URL routing. `ListR` relies on delta listing and on directories appearing before children; it also filters from drive root when mounted below root. Upload code rejects unknown-size streams and stores chunks in memory. Singlepart uploads can create extra versions because metadata is applied after content. Copy/move behavior differs across personal, business, and SharePoint drives. Permissions metadata is complex and drive-type dependent. `waitForJob` uses unauthenticated `http.Get` against Graph job URLs and loops until the global timeout. Size and hash values can be server-inconsistent.

Test signals: `onedrive_test.go` runs rclone integration tests for normal and China remotes and exposes upload chunk sizing. `onedrive_internal_test.go` exercises metadata, permissions, singlepart zero-byte upload, directory metadata, copy/move metadata preservation, and metadata mapper behavior. The quickxor package has table-vector and block-size tests for hash correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/onedrive/onedrive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/onedrive/onedrive_internal_test.go -->
# sources/user-network-fs/rclone/backend/onedrive/onedrive_internal_test.go

Purpose: defines OneDrive backend internal integration tests that go beyond generic fstests, primarily validating metadata and permissions behavior for files, directories, singlepart uploads, server-side copy/move, and metadata mapper integration. It is compiled in the `onedrive` package so it can access backend internals and mutate `f.opt.MetadataPermissions`.

Important APIs and helpers: `TestMain` delegates to `fstest.TestMain`. `(*Fs).InternalTest` implements `fstests.InternalTester` and dispatches subtests on fresh remotes using `fstest.NewRunIndividual`. `TestWritePermissions`, `TestUploadSinglePart`, `TestReadPermissions`, `TestReadMetadata`, `TestDirectoryMetadata`, `TestServerSideCopyMove`, and `TestMetadataMapper` are the test cases. Helpers include `putWithMeta`, `compareMeta`, `compareTimeStrings`, `marshalPerms`, `unmarshalPerms`, `defaultPermissions`, `normalize`, `randomFilename`, and `resetTestDefaults`.

Control flow: each subtest enables rclone metadata in context, sets OneDrive metadata permission mode as needed, writes a test file or directory, performs the operation under test, retrieves metadata through `fs.GetMetadata` or object `Metadata`, and compares expected metadata against actual. `TestWritePermissions` creates a permission, updates its role, and removes it, branching for personal vs business schema differences. `TestUploadSinglePart` forces an empty content string so the production code uses `uploadSinglepart`. `TestDirectoryMetadata` uses `operations.MkdirMetadata`, `operations.SetDirModTime`, `Fs.DirSetModTime`, and `operations.CopyDirMetadata`, then checks that writing a child does not mutate directory modtime. `TestServerSideCopyMove` writes metadata and permissions, then verifies `Copy` and `Move` preserve metadata except expected ID changes. `TestMetadataMapper` configures `ci.MetadataMapper` to inject permission JSON during a local-to-remote copy.

State and persistence behavior: the tests deliberately create remote OneDrive objects, permissions, and directories. Global test variables include fixed times and `content`, and `TestUploadSinglePart` mutates `content` temporarily before resetting it. `resetTestDefaults` disables metadata, sets permissions mode to off, and finalizes the run after each isolated subtest.

Dependencies and integration points: uses `fstest`, `fstests`, `operations`, `fs.Metadata`, rclone local backend import, OneDrive `api.PermissionsType`, and `testify` assertions. The hard-coded `testUserID` is a Microsoft documentation demo user used to avoid sharing with self; the tests assume a test tenant/account where such sharing behavior is possible.

Risks: these are live remote tests and can be brittle across personal/business API differences, tenant policies, sharing restrictions, role/identity schema differences, and timestamp precision. The package-level `content` mutation in `TestUploadSinglePart` would be unsafe if subtests ran in parallel. Permission comparison intentionally normalizes IDs/link/share IDs for copy/move because the backend cannot preserve those exactly.

Test signals: this file is itself the main signal for high-risk OneDrive metadata code. It demonstrates expected metadata keys, optional keys, unsupported description behavior, personal-drive utime precision tolerance, business-drive permission normalization, and the fact that zero-byte uploads exercise a distinct singlepart path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/onedrive/onedrive_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/onedrive/onedrive_test.go -->
# sources/user-network-fs/rclone/backend/onedrive/onedrive_test.go

Purpose: supplies the generic rclone integration test entry points for the OneDrive backend and exposes test-only upload chunk size control.

Important APIs: `TestIntegration` runs `fstests.Run` against `TestOneDrive:` with `NilObject: (*Object)(nil)`. `TestIntegrationCn` runs the same suite against `TestOneDriveCn:` unless a `-remote` flag is supplied. `(*Fs).SetUploadChunkSize` delegates to the production `setUploadChunkSize`, and the compile-time assertion registers `Fs` as `fstests.SetUploadChunkSizer`.

Control flow: the integration suite exercises rclone's generic filesystem contract. The `ChunkedUpload` config uses `fstests.NextMultipleOf(chunkSizeMultiple)`, ensuring test-selected chunk sizes respect OneDrive's required 320 KiB multiple. The China test has a guard to avoid conflicting with an explicitly requested remote.

State and persistence behavior: these tests operate on configured live remotes and rely on fstests to create, mutate, and clean remote objects. The file itself holds no persistent state.

Dependencies and integration points: depends on `fs`, `fstest`, and `fstests`. It is coupled to the production `chunkSizeMultiple` constant and `setUploadChunkSize` validation path.

Risks: coverage depends on externally configured `TestOneDrive:` and `TestOneDriveCn:` remotes. The China test is easy to skip unintentionally when `-remote` is set. Generic fstests cover core behavior but not all metadata and permission nuances; those are in `onedrive_internal_test.go`.

Test signals: confirms the backend participates in the standard rclone contract and that chunk-size mutation works under the generic chunked upload test harness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/onedrive/onedrive_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/onedrive/quickxorhash/quickxorhash.go -->
# sources/user-network-fs/rclone/backend/onedrive/quickxorhash/quickxorhash.go

Purpose: implements Microsoft's QuickXorHash as a Go `hash.Hash`, used by the OneDrive backend for the `quickxor` rclone hash type. It is a non-cryptographic rolling XOR hash with a 20-byte output and 64-byte preferred block size.

Important APIs and types: constants `BlockSize`, `Size`, `shift`, `widthInBits`, and `dataSize` define the algorithm dimensions. `quickXorHash` stores a `data` array of `dataSize` bytes and a cumulative `size`. `New` returns a `hash.Hash`; `Sum(data []byte)` is a convenience one-shot function. Methods `Write`, `Sum`, `Reset`, `Size`, and `BlockSize` satisfy `hash.Hash`.

Control flow: `Write` XORs input bytes into a circular `data` buffer, first filling any remainder from previous writes and then processing full `dataSize` cycles. `xorBytes` uses `crypto/subtle.XORBytes`. `checkSum` walks the internal data array, applies the 11-bit rotating shift into a 21-byte scratch buffer, folds byte 20 into byte 0, and XORs the little-endian file length into the final eight bytes. `Sum` appends the first 20 bytes of `checkSum` without mutating state. `Reset` zeroes all state.

State and persistence behavior: all state is in-memory inside `quickXorHash`; no external persistence exists. The `size` counter is part of the hash result, so two inputs with equal XOR state but different lengths produce different sums.

Dependencies and integration points: depends only on the standard `hash` interface and `crypto/subtle`. The OneDrive backend registers it through `hash.RegisterHash("quickxor", "QuickXorHash", 40, quickxorhash.New)` and decodes Graph QuickXorHash values from base64 to hex for comparisons.

Risks: correctness is sensitive to circular offset handling across multiple `Write` calls and to the final bit shifting/folding. It is not cryptographic and should only be used for service-compatible integrity comparisons. The implementation assumes `subtle.XORBytes` behavior and ignores its return except to advance by the number XORed.

Test signals: the companion tests validate many base64 vectors, chunked writes at multiple block sizes, `Size`, `BlockSize`, `Reset`, `hash.Hash` conformance, and benchmark throughput.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/onedrive/quickxorhash/quickxorhash.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/onedrive/quickxorhash/quickxorhash_test.go -->
# sources/user-network-fs/rclone/backend/onedrive/quickxorhash/quickxorhash_test.go

Purpose: verifies the QuickXorHash implementation against fixed vectors and hash interface behavior.

Important APIs: `testVectors` holds base64-encoded inputs and expected base64 hash outputs for many sizes, including empty input, small inputs, block-boundary inputs, and larger random-looking payloads. `TestQuickXorHash` checks one-shot `Sum`. `TestQuickXorHashByBlock` checks incremental `New().Write().Sum()` with block sizes from 1 to 512. `TestSize`, `TestBlockSize`, `TestReset`, and the `hash.Hash` assertion cover interface shape. `BenchmarkQuickXorHash` measures 1 MiB buffers.

Control flow: each vector is decoded, hashed, and compared to the decoded expected output. The block test loops through the same vectors while writing input in varying chunk sizes, making it the main guard for `Write` remainder and circular data behavior. The benchmark resets the hasher each iteration, writes a 1 MiB random buffer, and calls `Sum`.

State and persistence behavior: no persistent state; tests use random bytes only in the benchmark. The reset test records the zero hash, mutates the hasher with one byte, resets, and expects the zero hash again.

Dependencies and integration points: uses standard `crypto/rand`, `encoding/base64`, `fmt`, `hash`, and `testing`, plus `testify` `assert` and `require`. It tests only the local quickxor package, but its correctness protects OneDrive hash comparisons.

Risks: expected vectors are embedded in source and are the authority for compatibility. Benchmark randomness is not deterministic, but benchmark output is not a correctness gate. The vectors include multiline base64 strings, so accidental formatting damage can break decoding.

Test signals: strong algorithmic coverage for one-shot and incremental writes; no direct fuzzing or collision/security claims, which is appropriate for a non-cryptographic service hash.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/onedrive/quickxorhash/quickxorhash_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/opendrive/opendrive.go -->
# sources/user-network-fs/rclone/backend/opendrive/opendrive.go

Purpose: implements rclone's OpenDrive backend using OpenDrive's JSON API. It handles username/password session login, directory ID caching, listing, object CRUD, chunked uploads, server-side copy/move, quota reporting, and MD5 hashes.

Important APIs and types: `Options` holds username, password, encoding, chunk size, and default access mode. `Fs` stores backend name/root, options, features, REST client, pacer, `UserSessionInfo`, and `dirCache`. `Object` stores remote path, file ID, parent folder ID, modtime, MD5, and size. `init` registers `opendrive` and its options. `NewFs` reveals the password, logs in through `/session/login.json`, initializes root dircache with OpenDrive root ID `0`, fills features, and handles root-as-file.

Control flow: directory operations are based on `dircache.DirCache`, with `FindLeaf` listing `/folder/list.json/{session}/{pathID}` and matching encoded names case-insensitively, and `CreateDir` posting to `/folder.json`. `List` resolves directory ID, calls `/folder/list.json`, creates `fs.Dir` entries for folders and `Object` entries for files, and caches folder IDs. Object lookup uses `Object.readMetaData`; if the file ID is known it prefers `/file/info.json/{id}` because `/folder/itembyname.json` is unreliable for newly created files, otherwise it queries by parent directory and encoded leaf.

Mutation and transfer flow: `Put` ensures the parent directory exists, creates a file ID with `/upload/create_file.json` if needed, then calls `Object.Update`. Upload opens a server upload session with `/upload/open_file_upload.json`, reads chunks into a reusable buffer using `readers.NewRepeatableLimitReaderBuffer`, posts each chunk as multipart form data to `/upload/upload_file_chunk.json`, checks `TotalWritten`, closes via `/upload/close_file_upload.json`, sets modtime through `/file/filesettings.json`, sets access through `/file/access.json`, and refreshes metadata. `Copy` and `Move` use `/file/move_copy.json`; same-parent file moves use `/file/rename.json` to avoid move/copy behavior. `DirMove` uses `/folder/move_copy.json` or `/folder/rename.json`. `Purge` and `Rmdir` delete folders through `/folder/remove.json`; object `Remove` calls `DELETE /file.json/{session}/{id}`.

State and persistence behavior: remote persistent state is OpenDrive files/folders, session-scoped upload temp locations, access flags, timestamps, and hashes. Local in-memory state includes `session`, `dirCache`, object fields, and pacer state. The backend stores no token file directly; session lifetime is managed by API retry behavior. Access mode maps `"private"`, `"public"`, and `"hidden"` to integer flags.

Dependencies and integration points: uses rclone `fs`, config, obscure password reveal, `fshttp`, `rest`, `pacer`, `dircache`, `encoder`, `readers`, and `hash`. It implements `fs.Fs`, `Purger`, `Copier`, `Mover`, `DirMover`, `DirCacheFlusher`, `Abouter`, `Object`, `IDer`, and `ParentIDer`.

Risks: API behavior is uneven: listing may report deleted folders, same-parent move/copy can silently truncate long names, and item-by-name can lag newly created files. `Move` returns `fs.ErrorCantCopy` for wrong source type, likely a minor semantic bug. Upload chunks are buffered in memory by configured chunk size. `purgeCheck` only checks files when refusing non-empty folder removal, so child folders may require API-side enforcement. Session expiration relies on retrying HTTP 401 without explicit re-login. MD5 and size parsing sometimes ignores conversion errors.

Test signals: `opendrive_test.go` runs standard fstests against `TestOpenDrive:`. There are no specialized unit tests for upload chunk failure, rename fallbacks, access mapping, or session renewal in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/opendrive/opendrive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/opendrive/opendrive_test.go -->
# sources/user-network-fs/rclone/backend/opendrive/opendrive_test.go

Purpose: provides the standard rclone integration test entry point for the OpenDrive backend.

Important APIs: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestOpenDrive:"` and `NilObject: (*opendrive.Object)(nil)`. The test package is `opendrive_test`, so it validates the public backend package boundary rather than internals.

Control flow: fstests creates the remote from configured test credentials, runs the generic filesystem behavior suite, and validates common operations such as put, list, open, remove, hashes, modtime, directory operations, and optional interfaces advertised by the backend.

State and persistence behavior: all state is in the configured live OpenDrive remote and whatever temporary files/directories fstests creates. This file has no local persistent state.

Dependencies and integration points: depends on `github.com/rclone/rclone/backend/opendrive` and `github.com/rclone/rclone/fstest/fstests`.

Risks: coverage is only as broad as generic fstests and requires a working `TestOpenDrive:` remote. It does not directly exercise edge cases visible in implementation, such as same-parent rename fallbacks, long-name truncation prevention, access levels, upload partial-write errors, or session expiration.

Test signals: confirms the backend conforms to rclone's generic filesystem contract under live credentials, but specialized behavior lacks targeted tests in this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/opendrive/opendrive_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/opendrive/types.go -->
# sources/user-network-fs/rclone/backend/opendrive/types.go

Purpose: defines JSON request and response DTOs for OpenDrive API calls and the backend-specific error type.

Important APIs and types: `Error` wraps OpenDrive `error.code` and `error.message` and implements `Error()`. `Account` is the login request. `UserSessionInfo` models login/session response fields used primarily for `SessionID`, while preserving many returned account fields. `FolderList`, `Folder`, and `File` model listing and file metadata. Request/response structs include `createFolder`, `createFolderResponse`, `moveCopyFolder`, `renameFolder`, `moveCopyFolderResponse`, `removeFolder`, `moveCopyFile`, `moveCopyFileResponse`, `renameFile`, `createFile`, `createFileResponse`, `modTimeFile`, `openUpload`, `openUploadResponse`, `closeUpload`, `closeUploadResponse`, `permissions`, `uploadFileChunkReply`, and `usersInfoResponse`.

Control flow integration: `opendrive.go` serializes these structs through `rest.CallJSON`. Login sends `Account` and receives `UserSessionInfo`. Listing decodes `FolderList` into folders and files. Upload flow creates a file, opens upload, uploads chunks, closes upload, sets permissions, and refreshes metadata using this file's DTOs. Copy/move and rename paths switch between move/copy and rename request structs depending on parent directory.

State and persistence behavior: these structs are transient JSON carriers for persistent OpenDrive remote state. Several numeric values are encoded as JSON strings, such as `File.Size`, `File.DateModified`, `usersInfoResponse.StorageUsed`, and `MaxStorage`; the tags are critical for correct decoding.

Dependencies and integration points: only imports `encoding/json` and `fmt`. `json.RawMessage` is used for `IsAccountUser` because the API may return inconsistent shapes.

Risks: field names mirror OpenDrive's mixed casing exactly, so tag drift can break behavior silently. Some response fields represent numbers as strings while similar fields use integers, which can cause parse or zero-value issues. Many structs include fields not actively used by the backend; they may become stale relative to API behavior. Error responses without message/code are normalized by `errorHandler` in `opendrive.go`.

Test signals: no direct tests target these DTOs. They are indirectly covered by live `opendrive_test.go` integration behavior and by any operations that decode corresponding API responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/opendrive/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/byok.go -->
# sources/user-network-fs/rclone/backend/oracleobjectstorage/byok.go

Purpose: handles Oracle Object Storage bring-your-own-key and SSE-C/SSE-KMS option validation and request header population. It is compiled only on supported non-Plan9, non-Solaris, non-JS platforms.

Important APIs: `validateSSECustomerKeyOptions` rejects mutually exclusive KMS and customer-key settings and delegates to `populateSSECustomerKeys`. `populateSSECustomerKeys` reads a base64 AES key from `SSECustomerKeyFile` or `SSECustomerKey`, decodes it, computes a base64 SHA256 checksum, validates or fills `SSECustomerKeySha256`, and defaults `SSECustomerAlgorithm` to `AES256`. `useBYOKPutObject`, `useBYOKHeadObject`, `useBYOKGetObject`, and `useBYOKCopyObject` copy relevant option values into OCI SDK request structs.

Control flow: `NewFs` in the main backend calls `validateSSECustomerKeyOptions` before creating the OCI client. Upload preparation calls `useBYOKPutObject`; object metadata and downloads call `useBYOKHeadObject` and `useBYOKGetObject`; server-side copy calls `useBYOKCopyObject`. KMS key IDs are used for put/copy, while SSE-C customer headers are needed for put/head/get/copy.

State and persistence behavior: mutates the in-memory `Options` during setup by populating key, checksum, and algorithm fields. It reads key material from local disk when configured. The persistent remote effect is server-side encryption metadata/behavior on OCI objects.

Dependencies and integration points: uses standard crypto/base64/os/string helpers and OCI SDK `common` and `objectstorage` request types. It relies on `expandPath` from `client.go` for `~` expansion.

Risks: key material is sensitive and is stored in `Options` as strings after loading. Error text for decoding always mentions `sse_customer_key_file` even if the inline key was used. Misconfigured checksum blocks startup, which is appropriate for integrity but can be user-visible. SSE headers must be kept in sync across put, multipart create/part, head, get, and copy paths or encrypted objects may become unreadable.

Test signals: no direct tests in this subset. Behavior is indirectly covered only if Oracle integration tests run with SSE options.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/byok.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/client.go -->
# sources/user-network-fs/rclone/backend/oracleobjectstorage/client.go

Purpose: builds and configures the OCI Object Storage SDK client, selects authentication providers, wires rclone's HTTP client, and defines retry behavior plus no-auth support for public buckets.

Important APIs: `expandPath` cleans paths and expands leading `~`. `getConfigurationProvider` selects instance principal, user principal, resource principal, workload identity, no-auth, or default config provider based on `Options.Provider`. `newObjectStorageClient` creates `objectstorage.ObjectStorageClient`, applies region/endpoint overrides, and calls `modifyClient`. `modifyClient` installs `fshttp.NewClient(ctx)` and no-auth signer when configured. `shouldRetry` handles context cancellation, OCI `common.ServiceError` request timeouts, generic retryable errors, and HTTP retry status codes. `noAuthConfigurator` and `noAuthSigner` satisfy OCI SDK interfaces with empty credentials and no signing.

Control flow: main `NewFs` calls `newObjectStorageClient`; all backend SDK requests then use the configured client and shared `shouldRetry` inside pacer calls. User principal config warns if the config file path does not exist but still returns a custom profile provider, letting the SDK surface final auth errors.

State and persistence behavior: no persistent state is written. It reads local OCI config files indirectly through SDK providers and may inspect file existence. The client stores HTTP client, signer, host, region, and auth behavior in memory.

Dependencies and integration points: integrates OCI Go SDK `common`, `auth`, and `objectstorage`; rclone `fshttp`, `fs`, and `fserrors`. The no-auth path is used with option provider `no_auth` and is important for public bucket reads where listing all buckets is not allowed.

Risks: `expandPath` assumes paths beginning with `~` have at least two characters and uses `cleanedPath[2:]`, so a bare `~` could be mishandled. No-auth returns empty region and unknown auth type, so endpoint/region configuration must be correct elsewhere. Retry policy combines SDK retries with rclone pacer and intentionally low pacer retry count in the main backend; changing this can multiply retries. Missing config file is logged but not fatal at provider creation.

Test signals: no direct unit tests in this subset. Integration tests exercise client creation for configured providers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/command.go -->
# sources/user-network-fs/rclone/backend/oracleobjectstorage/command.go

Purpose: implements Oracle Object Storage backend commands exposed through `rclone backend`: `rename`, `list-multipart-uploads`, `cleanup`, and `restore`.

Important APIs: `commandHelp` documents command syntax and options. `(*Fs).Command` dispatches by command name. `rename` validates args, reads object metadata, builds `RenameObjectRequest`, and calls OCI `RenameObject`. `listMultipartUploadsAll`, `listMultipartUploads`, `findLatestMultipartUpload`, `listMultipartUploadsObject`, and `listMultipartUploadParts` enumerate unfinished multipart uploads and parts. `restore` walks filtered objects and calls `RestoreObjects` for archived objects.

Control flow: command dispatch parses option values such as cleanup `max-age` and restore `hours`. Multipart listing either targets the current bucket/prefix from `f.split("")` or lists all buckets then each bucket's uploads. Pagination follows `OpcNextPage`. Exact lookup for resume filters upload objects equal to the requested path and sorts by newest upload. `restore` uses `operations.ListFn`, which may invoke callbacks concurrently, so it protects output accumulation with a mutex and uses a per-object request copy.

State and persistence behavior: `rename` changes object names server-side. `cleanup` aborts pending multipart uploads via main backend cleanup helpers, respecting dry-run/interactive through `operations.SkipDestructive`. `restore` requests temporary restoration from Archive tier and returns per-object statuses. Listing commands only read remote multipart state.

Dependencies and integration points: depends on OCI SDK request/response types, rclone `fs`, `operations`, duration parsing, filters through `operations.ListFn`, and the backend's `split`, `listBuckets`, `cleanUp`, and pacer/client fields. Multipart resume in `multipart.go` depends on `findLatestMultipartUpload` and `listMultipartUploadParts`.

Risks: multipart listing treats a requested object/directory as a prefix for non-exact calls, so paths like `dir` can match `dirKey`. `restore` writes to a shared `err` variable inside concurrent callbacks, which can race logically even though output slice is protected. `rename` returns `fs.ErrorNotAFile` after metadata read failure and logs an extra warning if the object path appears to include the bucket name. Commands are live remote mutations and must honor destructive-operation safeguards.

Test signals: no direct command tests in this subset. Generic Oracle integration tests do not necessarily cover backend commands, multipart cleanup, or archive restore behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/command.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/copy.go -->
# sources/user-network-fs/rclone/backend/oracleobjectstorage/copy.go

Purpose: implements server-side copy for Oracle Object Storage and waits for the asynchronous OCI work request to finish.

Important APIs: `(*Fs).Copy` validates the source is an Oracle `*Object`, creates a destination `Object`, calls `f.copy`, then returns `f.NewObject` for the copied remote. `copy` builds `CopyObjectDetails` with source/destination names, region, namespace, bucket, object metadata, and BYOK headers. `copyObjectWaitForWorkRequest` polls work request state using `StateChangeConf`. `getObjectStorageErrorFromWorkRequest` collects work request error messages.

Control flow: before copy, if destination bucket differs from source, the backend checks and creates it if necessary. The copy request is submitted through `ObjectStorageClient.CopyObject`; OCI returns `OpcWorkRequestId`. The waiter treats accepted/in-progress/canceling as pending and completed/canceled/failed as terminal. Failed work requests are expanded by listing work request errors. The returned destination object is fetched after copy so metadata and size reflect server state.

State and persistence behavior: creates or overwrites remote destination objects and may create destination buckets. Metadata is copied from `srcObj.meta` using `metadataWithOpcPrefix`; callers should ensure source metadata has been loaded when metadata fidelity matters. Local state is limited to temporary request structs.

Dependencies and integration points: depends on OCI SDK `objectstorage` and `common`, BYOK helper `useBYOKCopyObject`, main backend bucket helpers, pacer/retry logic, and `StateChangeConf` from `waiter.go`.

Risks: server-side copy requires OCI IAM policy granting objectstorage service permissions; otherwise users must fall back to download/upload. Work request polling uses `context.Background()` inside the refresh function rather than the caller context for each `GetWorkRequest`, reducing cancellation precision. Canceled work requests are listed as target states but only failed state triggers an explicit error check, so canceled behavior depends on waiter result semantics. Metadata copying can miss metadata if the source object's `meta` map is nil.

Test signals: Oracle integration tests may exercise copy through fstests and copy cutoff controls, but no direct work-request failure or IAM-policy test is in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/multipart.go -->
# sources/user-network-fs/rclone/backend/oracleobjectstorage/multipart.go

Purpose: implements multipart uploads for Oracle Object Storage through rclone's chunk writer abstraction, including resume support, per-part MD5 validation, multipart commit validation, metadata preparation, storage tier handling, and abort behavior.

Important APIs and types: `uploadInfo` carries a prepared `PutObjectRequest` and source MD5 hex. `objectChunkWriter` stores chunk size, object size, bucket/key/upload ID, completed parts, existing parts for resume, MD5-of-parts state, upload info, and the target object. `Object.uploadMultipart` delegates to `multipart.UploadMultipart`. `Fs.OpenChunkWriter` prepares upload state and returns `fs.ChunkWriterInfo` plus an `objectChunkWriter`. `WriteChunk`, `Close`, and `Abort` implement the chunk writer lifecycle. `prepareUpload` builds the base put request and metadata. `createMultipartUpload` creates or resumes an OCI multipart upload.

Control flow: `OpenChunkWriter` calls `Object.prepareUpload`, clamps `MaxUploadParts`, calculates chunk size with `chunksize.Calculator` for known sizes, warns once for unknown-size stream limits, and creates/resumes an upload. `WriteChunk` rejects negative chunk numbers, optionally delays accounting, reads the chunk to compute binary/base64 MD5, records MD5 in ordered position, skips matching existing uploaded parts on resume, then uploads via `UploadPart` with SSE options copied from the put request. After the first eight parts, upload errors are retried once more broadly to tolerate large-transfer instability. `Close` commits all completed parts, aborts if OCI reports `InvalidUploadPart`, and validates OCI's multipart MD5 as base64(md5(concat(part MD5s))) plus part count. `Abort` calls backend abort helper unless the caller leaves parts on error.

State and persistence behavior: remote state includes multipart upload IDs, uploaded parts, committed objects, and orphaned parts when `LeavePartsOnError` is true. Local state includes completed part details and MD5 bytes protected by mutexes because chunks can upload concurrently. `prepareUpload` persists rclone modtime as `mtime` metadata and may store `md5chksum` metadata for multipart checksum tracking, especially when ETags are not plain MD5 under SSE.

Dependencies and integration points: integrates `github.com/rclone/rclone/lib/multipart`, `pool.DelayAccountinger`, `chunksize`, OCI SDK multipart APIs, BYOK option propagation through object option helpers, and command multipart listing for resume. Metadata extraction uses `fs.GetMetadataOptions` and standard headers.

Risks: concurrent part upload ordering requires careful mutex-protected state and correct MD5 byte placement. Resume assumes same chunk sizing; comments say mismatched chunk size should abort but this file only skips exact part-MD5 matches and creates new uploads when no usable upload is found. Unknown-size uploads are bounded by chunk size times max parts. `Close` uses `partsToCommit` append order, which may reflect concurrent completion order; OCI may or may not require sorted parts. Invalid metadata keys/values are dropped after logging, which can surprise metadata users.

Test signals: Oracle integration tests configure minimum chunk size and chunk/cutoff setters. There are no direct tests for resume, corrupted commit, leave-parts behavior, or concurrent part ordering in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/multipart.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/object.go -->
# sources/user-network-fs/rclone/backend/oracleobjectstorage/object.go

Purpose: implements Oracle Object Storage object behavior: metadata reads/writes, hashes, modtime, MIME type, storage tier get/set, open with ranges/response headers, delete, singlepart and multipart update dispatch, and request option mapping.

Important APIs and types: constants `metaMtime`, `metaMD5Hash`, and `ociMetaPrefix` define metadata conventions. `Object` stores `Fs`, remote path, MD5, size, last modified, metadata map, MIME type, and storage tier pointer. Core methods include `split`, `readMetaData`, `headObject`, `decodeMetaDataHead`, `decodeMetaDataObject`, `setMetaData`, `base64ToMd5`, `Hash`, `ModTime`, `SetModTime`, `Remove`, `Open`, `Update`, `applyPutOptions`, `applyGetObjectOptions`, `applyMultipartUploadOptions`, `applyPartUploadOptions`, and `metadataWithOpcPrefix`.

Control flow: reads call `HeadObject` with BYOK headers and decode headers/metadata through `setMetaData`. `Open` builds `GetObjectRequest`, applies range and response-header options, fetches the object, decodes metadata from the GET response, adjusts size from `ContentRange` when present, and returns the response body. `Update` ensures the bucket exists, chooses multipart for unknown size or sizes at/above cutoff unless the reader is detectably zero length, and otherwise prepares a put request and calls `PutObject` without retry wrapper multiplication. After upload, it clears cached metadata and re-reads it. `SetModTime` updates metadata then self-copies the object to persist changed metadata.

State and persistence behavior: object metadata is cached in `o.meta` after a head/get; `readMetaData` is a no-op if cache is present. Remote persistent state includes object content, headers, `opc-meta-*` metadata, storage tier, and server last-modified. Rclone modtime is stored in user metadata as a Swift float string under `mtime`; birth time is approximated from last modified in `Metadata` in the main backend. MD5 is decoded from OCI base64 `ContentMd5` or from `md5chksum` metadata for multipart/SSE cases.

Dependencies and integration points: uses OCI SDK object APIs, rclone `fs`, `hash`, Swift time conversion, BYOK helpers, multipart helpers, and main backend bucket/cache functions. It implements rclone object interfaces plus MIME and tier methods. Option mapping bridges rclone `OpenOption` headers to OCI request fields.

Risks: `setMetaData` appears to assign `o.md5 = md5` only when `base64ToMd5` returns an error for `metaMD5Hash`, likely inverted logic that can lose metadata MD5. Similar inverted checks exist in main backend listing code outside this file. `ModTime` returns cached `lastModified` directly when `UseServerModTime` is true, even if metadata has not been read. `SetModTime` copies object to itself, which can be expensive and depends on copy permissions/work requests. `metadataWithOpcPrefix` drops source keys that already have the prefix, which is intentional for some call sites but can omit prefixed metadata in copy. `isZeroLength` only detects common reader types.

Test signals: generic Oracle integration tests cover object operations, tiers, and chunked upload basics. There are no targeted unit tests for metadata MD5 fallback, range `ContentRange` parsing, self-copy modtime updates, or header option mapping in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/options.go -->
# sources/user-network-fs/rclone/backend/oracleobjectstorage/options.go

Purpose: defines Oracle Object Storage backend constants, authentication provider identifiers/help text, the `Options` configuration struct, and the full option registration list consumed by backend `init`.

Important APIs: constants define copy/upload limits and defaults: `maxSizeForCopy`, `maxUploadParts`, `defaultUploadConcurrency`, `minChunkSize`, `defaultUploadCutoff`, `maxUploadCutoff`, `minSleep`, and `defaultCopyTimeoutDuration`. Provider constants cover user principal, instance principal, resource principal, workload identity, environment auth, and no auth. `Options` contains provider, compartment, namespace, region, endpoint, encoding, OCI config file/profile, upload/copy cutoffs, multipart concurrency and limits, checksum behavior, storage tier, resume/cleanup flags, bucket checking, and SSE/BYOK fields. `newOptions` returns `[]fs.Option` with help, defaults, advanced flags, examples, and provider restrictions.

Control flow integration: main backend registration calls `newOptions`. `NewFs`, `client.go`, `multipart.go`, `object.go`, `copy.go`, and `byok.go` consume these fields to configure auth, client endpoint, bucket operations, upload strategy, copy behavior, metadata/checksum handling, storage tier, multipart cleanup/resume, and encryption headers. Test files use setters in the main backend to mutate chunk/cutoff options.

State and persistence behavior: options are parsed from rclone config into `Options`. Sensitive values include namespace, compartment, and SSE material. Runtime code may mutate SSE checksum/algorithm fields after validation. Options directly influence remote persistent state such as bucket creation, object storage tier, object metadata checksums, and encryption mode.

Dependencies and integration points: uses rclone `fs`, `config`, and `encoder`. The default encoder encodes invalid UTF-8, slash, and dot to keep OCI keys compatible with rclone's path model and SDK limitations.

Risks: option bounds are enforced outside this file, so new options must be paired with validation in backend construction/setters. The default `chunk_size` help text describes 5 MiB and `minChunkSize`, consistent with OCI minimum part size. `environmentAuth` is presented as default, but `getConfigurationProvider` falls through to the SDK default provider rather than explicitly handling that constant. SSE options are mutually exclusive in `byok.go`; registration help must stay aligned with that validation.

Test signals: Oracle integration tests expose setters for chunk size, upload cutoff, and copy cutoff; no tests directly validate option metadata/help text or all provider modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/oracleobjectstorage/options.go -->

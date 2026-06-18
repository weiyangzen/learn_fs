# subset-b-009742 research

Grouped research for the rclone Google Drive backend files, Drive metadata/upload/test fixtures, and Dropbox batching/content-hash helpers in this work item. Each section is source-tree aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drive/drive.go -->
# sources/user-network-fs/rclone/backend/drive/drive.go

## Purpose
`drive.go` is the main rclone backend implementation for Google Drive. It registers the `drive` remote, defines configuration, constructs authenticated Drive clients, maps Drive files/folders/docs/shortcuts into rclone `fs.Fs`, `fs.Object`, and `fs.Directory` interfaces, and implements listing, upload/update, server-side copy/move, trash cleanup, change notification, metadata-aware operations, and backend commands.

## Important APIs, types, and functions
- `Options` is the complete config surface: OAuth scopes, service account/env auth, Shared Drive root selection, listing filters, Google Docs import/export settings, upload cutoffs/chunk sizes, v2 download threshold, retry/pacer controls, shortcut behavior, metadata read/write modes, encoding, and resource keys.
- `Fs` holds runtime state: Drive v3/v2 services, OAuth HTTP client, directory cache, root folder ID, pacer, export/import format caches, ListR grouping state, resource-key cache, and permission cache.
- `baseObject`, `Object`, `documentObject`, `linkObject`, and `Directory` model regular binary objects, exported Google Docs, synthetic link files for Docs, and folders.
- `init` registers the backend and its config wizard, metadata help, OAuth options, and all advanced Drive options. It also registers MIME extension mappings used by Google Docs export/import logic.
- `NewFs`/`newFs` parse config, validate upload knobs, create OAuth/service-account clients, initialize Drive services and feature flags, resolve root folder IDs, initialize `dircache`, parse import/export extensions, and detect whether the requested root is a file.
- `list`, `ListP`, and `ListR` build Drive query expressions and convert Drive API `File` records into rclone entries. `ListR` runs worker goroutines and batches multiple parent IDs, with a fallback for a known Drive grouped-query empty-result bug.
- `NewObject`, `getRemoteInfoWithExport`, `newObjectWithInfo`, `newRegularObject`, `newDocumentObject`, and `newLinkObject` resolve one remote path and build the correct object wrapper, including Google Docs export naming and shortcut dereferencing.
- `Put`, `PutUnchecked`, `Object.Update`, `documentObject.Update`, `Copy`, `Move`, `DirMove`, `MkdirMetadata`, `DirSetModTime`, `Purge`, `CleanUp`, `PublicLink`, `ChangeNotify`, and `Command` implement the backend's rclone optional interfaces.
- Shortcut helpers `joinID`, `splitID`, `actualID`, `shortcutID`, and `resolveShortcut` preserve both the target Drive ID and shortcut file ID so callers can intentionally act on the underlying object or the shortcut placeholder.

## Control flow
Backend construction starts in `NewFs`: configuration is parsed, root ID is chosen from explicit root, team drive, or Drive root lookup, `dircache` maps paths to IDs, export/import formats are prepared, then `FindRoot` determines whether the remote path is a directory or a file parent. Listing is query driven: `list` assembles filters for trash state, parent IDs, shared-with-me/starred roots, case-sensitive title validation, Google Docs export stems, directory/file filters, optional age filters, Shared Drive corpora, appDataFolder spaces, resource-key headers, and paginated fields. Each returned item is name-decoded, shortcut-resolved when enabled, filtered again for exact title/export name, then passed to a callback.

Object creation branches on Drive MIME/checksum state. Regular uploaded files have hashes and media download URLs. Google Docs are represented either as exported document objects with an added extension and unknown size, or as synthetic link objects generated from templates. Unknown or unexportable Docs are hidden unless `--drive-show-all-gdocs` allows them. Dangling shortcuts can be exposed as unreadable regular-looking objects when not skipped so users can delete them.

Uploads use regular Drive create/update for objects below `UploadCutoff`, and the custom resumable uploader in `upload.go` for larger or unknown-size data. Importable local files can be converted to Google Docs by matching source MIME type against configured import formats, stripping the export extension from the Drive name, and validating that the chosen export type does not silently change unless allowed. Metadata is merged before upload/update and finalized afterward through callbacks for owner, permissions, and labels.

Server-side copy/move uses Drive `Files.Copy` or `Files.Update` with add/remove parents. Copy may copy shortcut content or shortcut files depending on config, preserves Doc descriptions specially, and deletes an existing destination object after successful copy. Move chooses the source parent from the object's recorded `parents` when possible, avoiding directory-cache ambiguity when duplicate folder names exist. Folder moves use `dircache.DirMove` plus a Drive update. Trash and cleanup code chooses between setting `Trashed` and hard delete based on config and context.

## State and persistence behavior
Persistent remote state lives in Google Drive files, folders, permissions, labels, trash state, and revisions. Local runtime state includes `dirCache`, `dirResourceKeys`, permission cache, ListR grouping/empty-directory state, and cached global export/import format maps guarded by `sync.Once`. Config updates through the `set` backend command mutate both the in-memory `Options` and the config mapper for chunk size/service account file. Object metadata is cached in `baseObject.metadata` when fetched or parsed; `Metadata` lazily reloads from Drive when absent.

Drive ID state is nuanced: shortcut-resolved IDs can be composite `actualID<TAB>shortcutID`. APIs that need the real content ID call `actualID`; APIs that should operate on the visible shortcut file call `shortcutID`. Resource keys for link-shared folders are cached by directory ID and injected into list/download/copy headers.

## Dependencies and integration points
This file integrates heavily with rclone core packages: `fs` optional interfaces, `dircache`, `pacer`, `oauthutil`, `fshttp`, `filter`, `operations`, `cache`, `fspath`, metadata helpers, hash sets, and encoders. External dependencies are Google Drive v3/v2 clients, Google OAuth/JWT/default credentials, and Google API error/field helpers. It calls into sibling files for metadata handling (`systemMetadataInfo`, `metadataFields`, `fetchAndUpdateMetadata`) and resumable upload (`Fs.Upload`). Tests in `drive_test.go` and `drive_internal_test.go` exercise the exported optional interfaces and internal backend commands.

## Risks and edge cases
- Google Drive allows duplicate names, multiple parents, shortcuts, Shared Drive inheritance, resource keys, and eventual consistency; many operations rely on careful ID/parent handling.
- Query escaping for names with backslashes and quotes is critical and is covered by internal tests.
- `shouldRetry` contains string/reason based fatal handling for upload/download quotas, which is necessarily brittle against undocumented Google error changes.
- ListR batching includes a workaround that disables grouping on suspicious empty results; concurrency around channels, wait groups, and overflow must remain correct to avoid missed directories or deadlocks.
- Updating Google Docs requires import formats and refuses type changes; link objects cannot be updated.
- Deleting objects with multiple parents is refused for safety.
- Metadata owner/permission/label writes happen after upload and may partially fail depending on `failok` flags.
- Some operations use sleeps/workarounds for Drive bugs, such as setting copied Google Doc modtimes after a delay.

## Test signals
`drive_test.go` runs full rclone integration tests against `TestDrive:` and advertises upload chunk/cutoff setters. `drive_internal_test.go` adds targeted tests for scopes, MIME extension mappings, export/import formats, retry policy, document import/update/export/link behavior, shortcut creation, untrash, copy/move by ID, query escaping, age-filter query integration, single-quote folders, and duplicate-parent move behavior. The mocked `test/about.json` supplies deterministic import/export format data for internal tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drive/drive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drive/drive_internal_test.go -->
# sources/user-network-fs/rclone/backend/drive/drive_internal_test.go

## Purpose
This file supplies unit-style and integration-style internal tests for the Drive backend. It validates helper functions that do not need a live remote, loads deterministic Drive format fixtures, and defines `Fs.InternalTest` so rclone's generic integration suite can run Drive-specific scenarios against a configured `TestDrive:`.

## Important APIs, types, and functions
- `TestDriveScopes` validates default scope expansion, comma trimming, and appfolder detection.
- `TestInternalLoadExampleFormats` reads `test/about.json`, unmarshals export/import formats, and seeds `_exportFormats`/`_importFormats` with `fixMimeTypeMap`.
- `TestInternalParseExtensions`, `TestInternalFindExportFormat`, `TestMimeTypesToExtension`, `TestExtensionToMimeType`, `TestExtensionsForExportFormats`, and skipped `TestExtensionsForImportFormats` verify MIME/extension mapping and Google Docs export selection.
- Methods on `*Fs` such as `InternalTestShouldRetry`, `InternalTestDocumentImport`, `InternalTestDocumentUpdate`, `InternalTestDocumentExport`, `InternalTestDocumentLink`, `InternalTestShortcuts`, `InternalTestUnTrash`, `InternalTestCopyOrMoveID`, `InternalTestQuery`, `InternalTestAgeQuery`, `InternalTestSingleQuoteFolder`, and `InternalTestMoveDuplicateParent` are picked up through `fstests.InternalTester`.
- `InternalTest` orders these tests, including nested document import/update/export/link tests that depend on prior remote state.

## Control flow
Pure tests run directly under `go test` and set global format caches where needed. Live remote tests operate through an initialized `*Fs`: they create/copy test files from local fixtures, call backend object methods and backend commands, then assert behavior through rclone listing/check helpers or direct Drive API reads. The document tests are nested because each step depends on the documents created or updated by the previous step.

## State and persistence behavior
The tests mutate the configured Drive remote: they upload sample documents, create and remove shortcuts, create trash/untrash trees, issue copy/move-by-ID operations into temporary local directories, create special-name folders, and create duplicate Drive folders directly through the API. Cleanup is explicit with `Remove`, `Rmdir`, `Purge`, direct `delete`, and `DirCacheFlush` in duplicate-parent scenarios. The file also mutates global `_exportFormats` and `_importFormats` once for deterministic MIME behavior.

## Dependencies and integration points
The tests depend on rclone's local backend, `fs`, `filter`, `operations`, `sync`, `fstest`, `fstests`, random content generation, testify assertions, and Google Drive API structs/errors. They are tightly coupled to behavior in `drive.go`, `metadata.go`, and `upload.go` because they exercise upload conversion, object export, command dispatch, query construction, shortcut resolution, and retry classification.

## Risks and edge cases
- Tests that use a live Drive remote depend on credentials, remote state, API quota, and Drive eventual consistency.
- `InternalTestDocumentImport` temporarily enables `AllowImportNameChange` and must restore it.
- Query tests escape both single quotes and backslashes, guarding a common Drive search failure mode.
- `InternalTestMoveDuplicateParent` covers a subtle Shared Drive risk: moving from a duplicate-name folder must remove the object's actual parent, not the parent guessed by directory cache.
- The skipped import-format extension test indicates known incompleteness or instability in import MIME coverage.

## Test signals
This file is itself the test signal for many Drive backend invariants. It checks retry fatalization for rate/download/upload quota cases, Google Docs import/export/link rendering, shortcut command errors and success paths, trash restore counts, copy/move ID destination naming, filter-aware age queries, single-quote folder listing, and duplicate-parent move correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drive/drive_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drive/drive_test.go -->
# sources/user-network-fs/rclone/backend/drive/drive_test.go

## Purpose
This is the top-level Drive backend integration test entry point. It delegates to rclone's generic filesystem test suite with Drive-specific object type and chunked-upload settings.

## Important APIs, types, and functions
- `TestIntegration` calls `fstests.Run` with `RemoteName: "TestDrive:"`, `NilObject: (*Object)(nil)`, and a `ChunkedUploadConfig` using Drive's `minChunkSize` and `fstests.NextPowerOfTwo`.
- `SetUploadChunkSize` and `SetUploadCutoff` expose Drive's private setters to the generic test harness.
- Interface assertions ensure `*Fs` implements `fstests.SetUploadChunkSizer` and `fstests.SetUploadCutoffer`.

## Control flow
When integration tests run, `fstests.Run` constructs the `TestDrive:` remote, exercises standard rclone filesystem semantics, and uses the setter hooks to vary upload chunk and cutoff behavior. The actual backend behavior under test lives in `drive.go` and `upload.go`.

## State and persistence behavior
The test suite creates, updates, lists, moves, copies, and deletes objects on the configured Drive test remote. The setters mutate in-memory upload settings on the active `Fs`, allowing tests to probe chunk size/cutoff boundaries without changing persistent config.

## Dependencies and integration points
The file depends on rclone's `fs` package and `fstest/fstests`. It integrates with Drive constants and methods from `drive.go` and uses upload behavior from `upload.go`.

## Risks and edge cases
- Requires a configured `TestDrive:` remote and live Google Drive access.
- Chunk size validation is important because Drive resumable uploads require power-of-two chunks at least `googleapi.MinUploadChunkSize`.
- Failures may reflect remote API quota or account state rather than deterministic local behavior.

## Test signals
The file is a broad conformance signal: it asserts the Drive backend satisfies rclone's standard filesystem contract and that chunked upload knobs can be controlled by the test framework.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drive/drive_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drive/metadata.go -->
# sources/user-network-fs/rclone/backend/drive/metadata.go

## Purpose
`metadata.go` implements Drive metadata read/write support for rclone. It documents system metadata keys, augments Drive field selection, reads owners/permissions/labels/folder attributes into `fs.Metadata`, writes supported metadata back into Drive API request structs, and creates post-upload callbacks for metadata that cannot be set in the initial file create/update request.

## Important APIs, types, and functions
- `systemMetadataInfo` describes Drive-owned metadata keys such as `content-type`, `mtime`, `btime`, sharing flags, owner, permissions, folder color, description, starred, and labels.
- `metadataFields`, `permissionsFields`, and `labelsFields` define extra Drive API fields required for metadata-aware listing/getting.
- `getPermission`, `setPermissions`, `cleanPermissionForWrite`, `cleanAndCachePermission`, and `cleanPermission` read, cache, sanitize, and write Drive permissions.
- `getLabels`, `setLabels`, `labelFieldsToFieldModifications`, and `cleanLabel` read labels and translate label field values into Drive `ModifyLabelsRequest` structures.
- `baseObject.parseMetadata` converts a Drive `File` into rclone metadata, including user `Properties` and selected system metadata.
- `setOwner`, `updateMetadata`, and `fetchAndUpdateMetadata` apply metadata during create/update workflows and return callbacks for owner, permissions, and labels.

## Control flow
Read flow starts when `drive.go` includes `metadataFields` in file fields and calls `parseMetadata`. User properties are copied first so they can override or coexist with system values. System booleans, MIME type, owner, permissions, folder color, description, starred, creation time, modification time, and labels are then inserted depending on configured read modes. Permission reading may use already returned `Permissions`, or fetch individual `PermissionIds` concurrently through an `errgroup` limited by `ci.Checkers`; inherited shared-drive permissions and owner permissions are excluded from serialized metadata.

Write flow starts in `fetchAndUpdateMetadata`, which reads source metadata through rclone metadata options and calls `updateMetadata`. That function walks each key, mutates the Drive `File` request for fields that can be set directly, places unknown keys into `Properties`, and appends callbacks for owner transfer, permissions creation, and labels modification. The caller executes the callback after upload/update returns an actual Drive file ID.

## State and persistence behavior
Permissions are cached in `Fs.permissions` under `permissionsMu` by permission ID after cleaning output-only fields. Label and permission writes persist to Drive through Drive API calls after upload. User metadata persists in Drive `properties`. Creation time can only be set on fresh uploads, while modification time can be set on updates. `MetadataOwner`, `MetadataPermissions`, and `MetadataLabels` bit flags control read/write/failok behavior independently.

## Dependencies and integration points
This file depends on `fs.Metadata`, rclone metadata option helpers, `fserrors.NoRetryError`, `errcount`, `errgroup`, and Google Drive API permission/label/file structs. It is called from object construction, metadata getters, `createDir`, `updateDir`, `PutUnchecked`, `Object.Update`, and `Copy` in `drive.go`.

## Risks and edge cases
- Permission metadata can be expensive: shared drives may require per-permission fetches to determine inheritance.
- Owner transfer has policy and notification constraints and can fail after file upload; `failok` controls whether that fails the transfer.
- Permissions and labels are post-upload callbacks, so partial metadata application is possible if later callbacks fail.
- Label writes require pre-existing label/field IDs; this code maps values but does not create label definitions.
- Boolean and JSON metadata parsing errors abort updates unless the key's feature is disabled.
- Unknown metadata keys become Drive user properties, which could collide with user-supplied keys.

## Test signals
Drive integration tests indirectly exercise metadata through upload/copy/update flows when metadata is enabled. The code itself includes no standalone tests in this subset, so high-risk paths such as permission inheritance filtering, label modification, and owner transfer depend on broader integration coverage or manual Drive API validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drive/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drive/test/about.json -->
# sources/user-network-fs/rclone/backend/drive/test/about.json

## Purpose
`about.json` is a deterministic fixture containing a sample Google Drive About response subset for `importFormats` and `exportFormats`. It lets Drive internal tests exercise MIME conversion logic without requiring a live About API call.

## Important data
- `importFormats` maps ordinary MIME types such as text, CSV, PDF, images, OpenDocument, Microsoft Office, JSON, and script text variants to Google Apps MIME targets such as document, spreadsheet, presentation, drawing, and script.
- `exportFormats` maps Google Apps document, spreadsheet, jam, script, presentation, form, and drawing MIME types to exportable MIME outputs such as PDF, Office formats, OpenDocument formats, plain text, HTML, ZIP, JSON, SVG, PNG, and JPEG.

## Control flow
`TestInternalLoadExampleFormats` reads this JSON file, unmarshals the maps, runs them through `fixMimeTypeMap`, and stores them in package globals `_exportFormats` and `_importFormats`. Later tests use these globals through `findExportFormat`, `findImportFormat`, and extension validation helpers.

## State and persistence behavior
The file is static test data. It does not persist runtime state, but loading it mutates package-level format caches for the duration of the test process.

## Dependencies and integration points
It is consumed by `drive_internal_test.go`. Its MIME values must align with extension registrations in `drive.go`; otherwise tests such as `TestExtensionsForExportFormats` or document import/export tests can fail.

## Risks and edge cases
- Fixture drift from current Google Drive capabilities may hide production behavior changes.
- Some duplicate/legacy MIME types are intentionally represented, relying on Drive backend custom MIME extension registrations.
- Import format validation is partially skipped in tests, so this fixture's import side is less strongly enforced than export side.

## Test signals
The fixture supports deterministic tests for export format choice, MIME extension mappings, and document import/export behavior. It is not executable by itself but is essential to avoiding network-dependent About format tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drive/test/about.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drive/upload.go -->
# sources/user-network-fs/rclone/backend/drive/upload.go

## Purpose
`upload.go` implements Drive resumable uploads for large or unknown-size objects. It starts a resumable upload session, sends data in configured chunks, retries each chunk through the backend pacer, and returns the final Drive `File` metadata.

## Important APIs, types, and functions
- `statusResumeIncomplete` is HTTP 308, the Drive resumable-upload in-progress response.
- `resumableUpload` stores the owning `Fs`, remote name for logging, session URI, media reader, content type, total length, and final returned `drive.File`.
- `Fs.Upload` starts a Drive upload session using POST for creates or PATCH for updates, sets upload metadata headers, handles `keepRevisionForever`, and then calls `resumableUpload.Upload`.
- `makeRequest` builds a chunk request with `Content-Range` using either known total size or `*` for initially unknown total size.
- `transferChunk` sends a chunk, handles 308 as nonterminal, checks non-308 responses, and decodes the final response body.
- `resumableUpload.Upload` reads chunks from the input, uses repeatable readers for known-size transfers and buffer reads for unknown-size transfers, retries through `pacer.Call`, and reports incomplete sessions as retryable.

## Control flow
The caller passes object metadata and content to `Fs.Upload`. A resumable session is created against `https://www.googleapis.com/upload/drive/v3/files` with `uploadType=resumable`; update calls expand `{fileId}` and use PATCH. Once Google returns a `Location`, `resumableUpload.Upload` loops from offset zero, preparing a chunk no larger than `opt.ChunkSize`. Known-size uploads stop when `start >= ContentLength`; unknown-size uploads read until EOF, then set `ContentLength` to the final byte count so the last `Content-Range` closes the upload. Each chunk is retried unless the status is 308, 201, or 200. The final response is decoded into `rx.ret`.

## State and persistence behavior
The upload persists file contents and metadata to Google Drive. Locally, only the resumable session URI, current offset, chunk buffer, and final returned metadata are held. The configured chunk size controls memory usage because one buffer of that size is allocated per upload instance.

## Dependencies and integration points
This file depends on `drive.go` for `Fs`, `partialFields`, `shouldRetry`, `opt.ChunkSize`, `opt.KeepRevisionForever`, and the authorized HTTP client. It uses rclone reader helpers for repeatable and fill reads, Google API response helpers, and `fserrors.RetryErrorf` so higher layers can restart incomplete sessions.

## Risks and edge cases
- The session start request is retried, but simple media create/update elsewhere deliberately uses no-retry behavior; callers must choose the correct path.
- Unknown-size uploads depend on EOF handling to send a final chunk with a concrete total length.
- If `rx.ret` remains nil after all chunks, the function returns a retryable incomplete-upload error.
- Chunks require repeatable readers for retry; known-size mode uses `NewRepeatableLimitReaderBuffer`, while unknown-size mode buffers each chunk in memory.
- Nonstandard local status codes 598/599 are used internally for decode/client errors.

## Test signals
`drive_test.go` configures generic chunked upload integration tests with Drive's minimum chunk size and power-of-two sizing. The main integration suite exercises this uploader whenever object size meets or exceeds `UploadCutoff` or size is unknown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drive/upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/dropbox/batcher.go -->
# sources/user-network-fs/rclone/backend/dropbox/batcher.go

## Purpose
`batcher.go` implements the Dropbox backend's synchronous batch commit path for upload sessions. Dropbox permits many upload batches to be started, but only one batch may be committed at a time, so this file provides the commit helper used by the backend's batcher.

## Important APIs, types, and functions
- `finishBatch` wraps `UploadSessionFinishBatchV2`, pacing/retrying the API call and returning a batch result.
- `commitBatch` calls `finishBatch`, validates the number of returned entries, and maps each Dropbox per-entry result into either a `*files.FileMetadata` result slot or an error slot.

## Control flow
`commitBatch` receives ordered upload finish arguments plus parallel result/error slices supplied by the caller. It finalizes the batch with Dropbox, checks that Dropbox returned exactly one entry per requested item, then iterates entries by index. Success entries populate `results[i]`; failed entries build a descriptive error tag from the top-level tag and nested failure, lookup, path, or properties tags and store it in `errors[i]`.

## State and persistence behavior
The persistent effect is on Dropbox: upload sessions are committed into real files. Locally, the function mutates caller-provided result and error slices in place. No durable local state is written here.

## Dependencies and integration points
This file depends on the Dropbox SDK `files` package, the backend `Fs` pacer, `f.srv.UploadSessionFinishBatchV2`, and the backend-specific `shouldRetryExclude` retry classifier. It is part of the Dropbox upload pipeline outside this file.

## Risks and edge cases
- Return order is assumed to align with request order; wrong ordering would misassign results.
- A mismatch in returned entry count aborts the whole commit with an error.
- Retry policy intentionally retries all errors after the first chunk except excluded errors; misclassification can duplicate expensive commits or fail too early.
- Error reporting compresses nested Dropbox failure information into a string tag, which is useful but may omit full structured details.

## Test signals
No tests are included in this subset for `batcher.go`. Coverage likely comes from Dropbox backend upload integration tests. Key test cases should include mixed success/failure batches, returned entry count mismatch, nested failure tags, and retry-excluded errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/dropbox/batcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/dropbox/dbhash/dbhash.go -->
# sources/user-network-fs/rclone/backend/dropbox/dbhash/dbhash.go

## Purpose
`dbhash.go` implements Dropbox's content hash algorithm. Dropbox hashes each 4 MiB block with SHA-256, concatenates those block digests, and SHA-256 hashes the concatenation to produce the final checksum.

## Important APIs, types, and functions
- Constants expose `BlockSize`, `Size`, and the internal `bytesPerBlock` of 4 MiB.
- `digest` implements `hash.Hash` with a current block hash, total hash, byte count within the current block, and guards around `Sum` usage.
- `New` returns a reset `hash.Hash` implementation.
- `Write` feeds arbitrary input across 4 MiB block boundaries and writes each completed block digest into the total hash.
- `writeBlockHash` appends the current block digest to `totalHash` and resets block state.
- `Sum` finalizes any partial block into the total hash and returns the total hash digest.
- `Reset`, `Size`, and `BlockSize` satisfy `hash.Hash`.
- Package-level `Sum` computes a checksum for a byte slice and returns a fixed-size array.

## Control flow
Callers create a digest with `New`, stream data through `Write`, then call `Sum`. `Write` slices the input into whatever fits before the next 4 MiB boundary, updates the block hash, and flushes the block digest whenever the block reaches 4 MiB. `Sum` flushes a non-empty final partial block and then returns the SHA-256 digest of all block digests. Empty input returns the SHA-256 of empty data because no block digest is written.

## State and persistence behavior
All state is in memory. `digest.n` tracks current block fill, `blockHash` tracks the current block, `totalHash` tracks the concatenated block digests, and `sumCalled`/`writtenMore` protect against unsupported `Sum`, then `Write`, then `Sum` reuse. `Reset` clears all state.

## Dependencies and integration points
The implementation only depends on the Go standard library `crypto/sha256` and `hash` interfaces. The Dropbox backend can use it wherever Dropbox content hashes are needed for verification or metadata comparison.

## Risks and edge cases
- `Sum` mutates internal state by flushing a partial block, despite the `hash.Hash` contract saying `Sum` should not change state. The code documents that calling `Sum`, then `Write`, then `Sum` panics.
- The exported `Size` constant is set to `sha256.BlockSize` rather than `sha256.Size`, so package-level `Sum` returns a 64-byte array with only the first 32 bytes populated by the digest. The `hash.Hash.Size()` method still reports 32 via `totalHash.Size()`. This API shape is covered by tests and may be relied upon.
- Panics occur if underlying hash writes unexpectedly return errors, which standard SHA-256 should not do.
- Boundary correctness at exactly 4 MiB and multiples is essential to match Dropbox.

## Test signals
`dbhash_test.go` validates known Dropbox content hashes across many lengths around 4 MiB and 8 MiB boundaries and across many caller chunk sizes. It also tests the documented `Sum` reuse panic, `Size`, `BlockSize`, and package-level `Sum` behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/dropbox/dbhash/dbhash.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/dropbox/dbhash/dbhash_test.go -->
# sources/user-network-fs/rclone/backend/dropbox/dbhash/dbhash_test.go

## Purpose
This file tests the Dropbox content hash implementation against known expected hashes, different caller write chunk sizes, boundary lengths, and selected API behavior.

## Important APIs, types, and functions
- `testChunk` streams repeated `A` bytes into `dbhash.New()` using a caller-selected chunk size and checks expected hex digests for lengths from zero through 8 MiB plus one.
- `TestHashChunk16M`, `TestHashChunk8M`, `TestHashChunk4M`, `TestHashChunk2M`, `TestHashChunk1M`, `TestHashChunk64k`, `TestHashChunk32k`, `TestHashChunk2048`, and `TestHashChunk2047` run the same expected-length matrix with different write sizes.
- `TestSumCalledTwice` verifies allowed and disallowed `Sum` call ordering.
- `TestSize`, `TestBlockSize`, and `TestSum` verify API dimensions and package-level checksum output.

## Control flow
For each write chunk size, the helper allocates a chunk of `A` bytes, writes whole chunks until less than one chunk remains, writes the remainder, calls `Sum(nil)`, hex encodes it, and compares against the expected digest for that total length. Boundary lengths include one less than, exactly, and one greater than 4 MiB and 8 MiB.

## State and persistence behavior
Tests are pure in-memory checks. They exercise digest internal state transitions indirectly through writes, sums, resets, and panic assertions.

## Dependencies and integration points
The file imports the public `dbhash` package and testify assertions. It validates `dbhash.go` independently of the rest of the Dropbox backend.

## Risks and edge cases
- The `fmt.Sprintf` message currently reports `n` from the final write rather than the total tested length; this affects failure diagnostics only.
- `TestSum` expects the fixed array shape returned by `dbhash.Sum`, including implicit trailing zero bytes because the array length is 64 while the actual digest is 32 bytes.
- The tests cover many boundary and chunking combinations but do not test random data or interleaved `Reset` after partial writes beyond the `Sum` call-order case.

## Test signals
The expected hashes give strong regression coverage for the Dropbox algorithm, especially block-boundary handling and write chunk independence. The panic test codifies the implementation's nonstandard `Sum` state behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/dropbox/dbhash/dbhash_test.go -->

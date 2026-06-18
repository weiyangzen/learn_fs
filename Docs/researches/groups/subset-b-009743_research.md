# subset-b-009743 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/dropbox/dropbox.go -->
# sources/user-network-fs/rclone/backend/dropbox/dropbox.go

Purpose: This is rclone's Dropbox backend. It registers the `dropbox` remote, builds OAuth/team/namespace clients, maps rclone filesystem operations to Dropbox files, sharing, users, and team APIs, handles Dropbox Paper/export-only files, and implements listing, uploads, server-side copy/move, public links, quota, change notifications, and object metadata.

Important APIs and types: `Options` carries chunk sizing, impersonation, shared file/folder modes, batching, namespace, export, pacing, and encoding settings. `Fs` owns the Dropbox SDK clients, pacer, batcher, namespace, root paths, and feature set. `Object` stores Dropbox file ID, shared URL, remote path, size, modtime, content hash, and export state. Key functions include `getOauthConfig`, `NewFs`, `headerGenerator`, `getMetadata`, `possibleMetadatas`, `getFileMetadata`, `ListP`, `Put`, `Mkdir`, `Copy`, `Move`, `PublicLink`, `DirMove`, `About`, `ChangeNotify`, `chooseExportFormat`, `Object.Open`, `uploadChunked`, `checkPathLength`, `Object.Update`, and `Object.Remove`.

Control flow: Initialization registers the Dropbox hash and config options, then `NewFs` parses config, migrates old bearer tokens, creates OAuth clients, resolves team impersonation, configures SDK clients, validates export formats, optionally mounts shared folders or lists shared files, chooses root namespace when requested, and detects file roots. Metadata lookup first tries exact Dropbox paths and then possible export-derived paths such as Paper documents with user-preferred extensions. Directory listing uses `ListFolder`/`ListFolderContinue`, converts only the final `PathDisplay` component to preserve Dropbox casing behavior, filters hidden exports, and emits `fs.Dir` or `Object`. Uploads either call single `Upload` or chunked upload sessions with optional batch commit; chunked sessions retry append offsets carefully and then finish or enqueue a batch commit. Change notification gets a recursive cursor, longpolls through the unauthenticated client, follows continuation pages, and emits changed paths relative to the configured root.

State and persistence behavior: Runtime state includes cached root strings, selected namespace, export extension preferences, pacer decay, the upload batcher, object metadata, and the token saved by rclone OAuth. `NewFs` may persist a converted token with `config.SetValueAndSave`. Dropbox state changes include create/delete folders, copy/move paths, shared-link permissions, shared-folder mounts, upload sessions, batch commit state, and Paper export reads. Object modtime is set only on upload because Dropbox cannot mutate modtime after the fact, and `SetModTime` deliberately returns `fs.ErrorCantSetModTimeWithoutDelete`.

Dependencies and integration points: The file integrates Dropbox SDK packages `auth`, `files`, `sharing`, `team`, and `users`; rclone `fs` interfaces; `oauthutil`; `batcher`; `pacer`; `operations.RemoveExisting`; `encoder`; and the Dropbox content hash implementation in `dbhash`. It advertises `fs.Copier`, `Purger`, `PutStreamer`, `Mover`, `PublicLinker`, `DirMover`, `ListPer`, `Abouter`, `Shutdowner`, `Object`, and `IDer`.

Risks: Dropbox error typing is inconsistent, so retry classification partly relies on error strings. Shared-file/shared-folder modes intentionally disable most mutating operations. Exportable files are name-munged and may collide with real files or become list-only depending on `skip_exports` and `show_all_exports`. Chunked uploads buffer a chunk in memory and have complex offset recovery. `checkPathLength` counts runes rather than Dropbox's exact character accounting. ChangeNotify sleeps on Dropbox backoff inside the worker goroutine and depends on longpoll limits. Shared received-file listing contains a direct `fmt.Printf` debug print. Namespace and impersonation options are sensitive to OAuth scopes.

Test signals: Integration tests exercise the backend through `fstests`. Internal tests cover per-component Dropbox path length limits across ASCII and multibyte runes and Paper export behavior, including import as markdown, lookup through the exported extension, and exported HTML content. `fstests.SetUploadChunkSizer` support lets integration tests vary chunk size boundaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/dropbox/dropbox.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/dropbox/dropbox_internal_test.go -->
# sources/user-network-fs/rclone/backend/dropbox/dropbox_internal_test.go

Purpose: This file contains Dropbox-specific internal tests beyond the generic rclone integration suite. It validates filename length prechecks and the special Dropbox Paper export path.

Important APIs and types: The tests call `checkPathLength`, use `maxFileNameLength`, call `Fs.importPaperForTest`, `Fs.InternalTestPaperExport`, and expose `Fs.InternalTest` through `fstests.InternalTester`. The Paper test uses Dropbox SDK `files.PaperCreateArg` and `ImportFormatMarkdown`, plus rclone object lookup/open APIs.

Control flow: `TestInternalCheckPathLength` builds repeated rune strings for ASCII, pound sign, smiley, and CJK characters, both as whole names and path components, then asserts that lengths up to 255 pass and 256 fail. `importPaperForTest` creates a Paper document under the remote root from markdown content. `InternalTestPaperExport` changes preferred export extension to HTML, resolves `export.html`, opens it, reads the content, and checks expected rendered HTML fragments. `InternalTest` registers that subtest for the generic test harness.

State and persistence behavior: The path-length test is pure. The Paper test creates a real Dropbox Paper document in the integration remote and reads it back through the export path, mutating remote test state.

Dependencies and integration points: It integrates Dropbox Paper creation with rclone's export metadata mapping and `fstests.InternalTester`. It depends on the backend's pacer and SDK client being configured by the integration harness.

Risks: Paper tests require a Dropbox account and API behavior that supports Paper creation/export. The content assertions are intentionally small and may be sensitive to Dropbox export formatting changes. `checkPathLength` test asserts the backend's rune-count approximation, not Dropbox's exact server-side length metric.

Test signals: Strong signals are exact pass/fail path length cases and successful Paper import, lookup as `export.html`, readable object stream, and rendered snippets including bold text and link markup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/dropbox/dropbox_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/dropbox/dropbox_test.go -->
# sources/user-network-fs/rclone/backend/dropbox/dropbox_test.go

Purpose: This is the generic Dropbox backend integration-test entry point. It delegates most behavior checks to rclone's shared filesystem test suite.

Important APIs and types: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestDropbox:"`, a nil `*Object`, and `ChunkedUploadConfig{MaxChunkSize: maxChunkSize}`. `Fs.SetUploadChunkSize` adapts the unexported `setUploadChunkSize` helper to the `fstests.SetUploadChunkSizer` interface.

Control flow: The shared test harness constructs the configured remote, runs standard object, directory, upload, move/copy, hash, and feature tests, and can adjust upload chunk size within backend constraints.

State and persistence behavior: The test mutates a real Dropbox test remote configured outside this file. The only local state is the temporary chunk-size override during selected tests.

Dependencies and integration points: It depends on `fstests`, a configured `TestDropbox:` remote, and backend support for `SetUploadChunkSizer`.

Risks: Coverage is mostly external to this file and depends on remote credentials, Dropbox API availability, and the generic test suite's expectations. Backend-specific export and path-length details are covered in `dropbox_internal_test.go`.

Test signals: Passing `fstests.Run` is the broad compatibility signal; chunked upload tests can exercise maximum chunk-size validation through the adapter.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/dropbox/dropbox_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/fichier/api.go -->
# sources/user-network-fs/rclone/backend/fichier/api.go

Purpose: This file contains the low-level 1Fichier API helpers used by the backend: retry classification, file/folder listing, shared-folder access, folder mutations, file move/copy/rename/delete, upload-node discovery, multipart form upload, and upload finalization.

Important APIs and types: Important functions include `parseFichierError`, `shouldRetry`, `createObject`, `readFileInfo`, `getDownloadToken`, `listSharedFiles`, `listFiles`, `listFolders`, `listDir`, `newObjectFromFile`, `makeFolder`, `removeFolder`, `deleteFile`, `moveFile`, `moveDir`, `copyFile`, `renameFile`, `getUploadNode`, `uploadFile`, and `endUpload`. It uses request/response DTOs from `structs.go`, `rest.Opts`, `dircache`, and rclone `fs.DirEntry`/`fs.Dir`.

Control flow: API calls are wrapped in `f.pacer.Call` or `CallNoRetry` with JSON requests to the 1Fichier API. Listing resolves a directory ID from `dirCache`, fetches files and folders separately, converts server names through the configured encoder, emits objects/directories, and stores folder IDs back into `dirCache`. Uploads first obtain an upload node, POST the file as multipart form data to `/upload.cgi` with an upload ID, then call `/end.pl` on that node to retrieve final links. Shared folder listing switches between GET and POST depending on password presence.

State and persistence behavior: The file maintains no persistent local state, but it updates `dirCache` when listing folders and creates/deletes/moves/copies server-side 1Fichier objects. Upload state is provider-side and keyed by upload node ID. `shouldRetry` may sleep for 30 seconds for parsed flood errors `#374` or `#412`.

Dependencies and integration points: It integrates with `lib/rest`, `fs.Pacer`, `fserrors`, `dircache.DirCache`, 1Fichier's JSON endpoints, and encoding conversion. Higher-level `fichier.go` operations call these helpers to implement rclone interfaces, while `object.go` calls `getDownloadToken` and `deleteFile`.

Risks: 1Fichier overloads HTTP 403 for many API failures, so parsing numeric codes out of error strings is fragile. The flood-control sleep blocks the pacer caller. Upload IDs are validated only for alphanumeric length, and upload finalization assumes at least one returned link. Listing and dates depend on exact server time formats. Shared-folder response handling has limited password and error coverage.

Test signals: There are no direct unit tests for these helpers; the `fichier` integration test exercises them through standard filesystem operations against `TestFichier:`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/fichier/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/fichier/fichier.go -->
# sources/user-network-fs/rclone/backend/fichier/fichier.go

Purpose: This is the main 1Fichier rclone backend. It registers configuration, builds the REST client and directory cache, exposes filesystem features, and implements list, object lookup, upload, mkdir/rmdir, server-side move/copy, quota, and public-link operations.

Important APIs and types: `Options` stores API key, shared folder ID, file/folder passwords, CDN flag, and encoding. `Fs` stores root/name, feature set, options, `dirCache`, HTTP client, pacer, and REST client. Key methods include `FindLeaf`, `CreateDir`, `Name`, `Root`, `String`, `Precision`, `Hashes`, `Features`, `NewFs`, `List`, `NewObject`, `Put`, `putUnchecked`, `PutUnchecked`, `Mkdir`, `Rmdir`, `Move`, `DirMove`, `Copy`, `About`, and `PublicLink`.

Control flow: `NewFs` parses options, makes shared-folder remotes rootless, trims root, creates an authenticated REST client with bearer API key, initializes `dirCache`, then resolves the root. If root lookup fails it probes the parent and object to implement `fs.ErrorIsFile`. `List` delegates to shared folder listing when configured, otherwise calls `listDir`. `Put` checks for an existing object and updates it or calls `PutUnchecked`; `putUnchecked` rejects >300 GB and zero-byte uploads, gets an upload node, ensures the parent path, uploads, finalizes, parses size, and returns an object from the returned link. Move, DirMove, and Copy combine `dirCache` lookups with API helper calls and refresh metadata after successful server-side operations.

State and persistence behavior: Local runtime state is mostly `dirCache` and pacer timing. Server-side state changes include folders, duplicate file uploads, old-version deletion on update, move/copy/rename operations, and file removals. Quota is read from account info. PublicLink returns the object's 1Fichier URL rather than creating a separate sharing artifact.

Dependencies and integration points: It implements `fs.Fs`, `fs.Mover`, `fs.DirMover`, `fs.Copier`, `fs.PublicLinker`, `fs.PutUncheckeder`, and `dircache.DirCacher`. It depends on `fshttp`, `rest`, `pacer`, `encoder`, `hash.Whirlpool`, and helpers in `api.go` and `object.go`.

Risks: Empty files cannot be uploaded. Unknown-size updates are rejected at object level. Server-side move/copy error handling trusts response shapes and first returned URL. `DirMove` depends on `dirCache.DirMove` and the provider's inability to atomically rename and move without overwrite risk. Root-as-file detection mutates `f` after features have already been filled, requiring a workaround noted in comments.

Test signals: The integration test runs the generic rclone suite against `TestFichier:`. The backend advertises Whirlpool hashing, duplicate files, empty directories, and MIME reads, so those generic tests are the main behavioral signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/fichier/fichier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/fichier/fichier_test.go -->
# sources/user-network-fs/rclone/backend/fichier/fichier_test.go

Purpose: This file is the generic integration-test entry point for the 1Fichier backend.

Important APIs and types: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestFichier:"`.

Control flow: The shared rclone test harness constructs the remote from configuration and runs standard filesystem behavior checks.

State and persistence behavior: It mutates the configured 1Fichier test remote and has no local state beyond the test harness.

Dependencies and integration points: It depends on `fstests` and a valid `TestFichier:` remote with suitable credentials.

Risks: There are no local unit tests for parsing retry error codes, upload finalization, or dircache behavior. Failures may reflect provider rate limiting, and `api.go` includes explicit flood sleep handling because integration tests can provoke it.

Test signals: Passing `fstests.Run` is the only signal in this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/fichier/fichier_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/fichier/object.go -->
# sources/user-network-fs/rclone/backend/fichier/object.go

Purpose: This file implements the 1Fichier `Object` side of rclone's object interface: metadata access, hash, open/download, update, remove, MIME type, and ID.

Important APIs and types: `Object` contains `fs`, `remote`, and a cached `File` DTO. Methods include `String`, `Remote`, `ModTime`, `Size`, `Fs`, `Hash`, `Storable`, `SetModTime`, `setMetaData`, `Open`, `Update`, `Remove`, `MimeType`, and `ID`.

Control flow: `Open` fixes range options against the known size, obtains a download token for the object's URL, then makes a GET request to the token URL with open options. `Update` rejects unknown sizes, uploads a duplicate object through `putUnchecked`, deletes the old object only after the upload succeeds, then replaces the receiver with the new object. `Hash` supports only Whirlpool and returns the stored checksum. `ModTime` parses the provider date string and falls back to current time on parse failure.

State and persistence behavior: Object metadata is cached in the `file` field and replaced after update. Provider state changes happen through duplicate upload plus old-object deletion, or direct deletion via file URL. Modtime cannot be changed server-side.

Dependencies and integration points: It uses helpers from `api.go`, DTOs from `structs.go`, rclone `fs.Object`, `fs.MimeTyper`, `fs.IDer`, `hash.Whirlpool`, and `rest` for downloads.

Risks: Updating a file is not atomic: a successful upload followed by failed delete leaves duplicates. Unknown-size updates are refused. Modtime parsing depends on `2006-01-02 15:04:05`. Range support depends on `rest` open option handling and the 1Fichier token URL. `SetModTime` is unsupported.

Test signals: Generic `fstests` exercise object read/write/remove/hash/MIME behavior through `fichier_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/fichier/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/fichier/structs.go -->
# sources/user-network-fs/rclone/backend/fichier/structs.go

Purpose: This file defines JSON request and response structures for the 1Fichier API endpoints used by the backend.

Important APIs and types: Request types include `FileInfoRequest`, `ListFolderRequest`, `ListFilesRequest`, `DownloadRequest`, `RemoveFolderRequest`, `RemoveFileRequest`, `MakeFolderRequest`, `MoveFileRequest`, `MoveDirRequest`, `CopyFileRequest`, and `RenameFileRequest`. Response/data types include `GenericOKResponse`, `MakeFolderResponse`, `MoveFileResponse`, `MoveDirResponse`, `CopyFileResponse`, `RenameFileResponse`, `GetUploadNodeResponse`, `GetTokenResponse`, `SharedFolderResponse`, `SharedFile`, `EndFileUploadResponse`, `File`, `FilesList`, `Folder`, `FoldersList`, and `AccountInfo`.

Control flow: There is no executable flow in this file; the structures are marshaled and unmarshaled by `rest.CallJSON` in `api.go` and consumed by higher-level methods in `fichier.go` and `object.go`.

State and persistence behavior: The structs model provider state such as folder IDs, file URLs, checksums, quota counters, upload links, and account storage values. They do not maintain local state.

Dependencies and integration points: The JSON tags are the contract between the backend and 1Fichier's endpoints. `File` drives object metadata, `FoldersList` drives directory caching, `EndFileUploadResponse` drives post-upload object creation, and `AccountInfo` drives `About`.

Risks: Several 1Fichier JSON fields use inconsistent capitalization such as `Status` and `Message`; tag drift would silently break behavior. Some response slices are assumed non-empty by callers. Large `AccountInfo` coverage is broad but not validated locally.

Test signals: There are no direct tests for the DTOs; integration coverage validates only fields touched by standard operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/fichier/structs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filefabric/api/types.go -->
# sources/user-network-fs/rclone/backend/filefabric/api/types.go

Purpose: This package defines Enterprise File Fabric API data types and custom JSON codecs used by the `filefabric` backend.

Important APIs and types: `Time`, `Int`, and `String` handle provider JSON that can use custom date formats, quoted numbers, unquoted numbers, or mixed string encodings. `Status` implements `OKError` with `OK`, `Error`, and `GetCode`. API response types include `GetTokenByAuthTokenResponse`, `ApplianceInfo`, `GetFolderContentsResponse`, `Item`, `CustomPermissions`, `DoCreateNewFolderResponse`, `DoInitUploadResponse`, `UploaderResponse`, `UploadStatus`, `DoCompleteUploadResponse`, `DeleteResponse`, `FileResponse`, `MoveFilesResponse`, `TasksResponse`, and `Task`. `ItemFields` is generated by reflecting JSON tags on `Item`.

Control flow: Custom unmarshalling normalizes zero dates, quoted integers, and mixed string encodings. `fields`/`mustFields` build a pipe-delimited field list used by list calls to request only needed `Item` fields. Status-bearing response structs are passed into `filefabric.Fs.rpc`, where non-OK statuses become retryable or terminal errors.

State and persistence behavior: These types model remote metadata, upload state, background tasks, and session-token responses. They do not persist local data, but values such as tokens, version labels, folder IDs, file IDs, upload codes, content types, and task IDs are persisted or acted on by `filefabric.go`.

Dependencies and integration points: The file depends on `encoding/json`, `time`, reflection, and the backend's `rpc` method. `Item` is central to directory listings and object metadata; `Status` is central to retry and token-expiry handling.

Risks: The provider returns inconsistent JSON types, so custom codecs are necessary but can mask malformed data. `String.UnmarshalJSON` falls back to raw bytes if normal string decoding fails. Version or API schema drift can break `ItemFields` assumptions or field names. Zero-time handling is specific to `"0000-00-00 00:00:00"`.

Test signals: There are no direct tests in this subset for the codecs. The FileFabric integration test indirectly exercises these structures through listing, uploads, moves, and metadata operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filefabric/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filefabric/filefabric.go -->
# sources/user-network-fs/rclone/backend/filefabric/filefabric.go

Purpose: This is rclone's Enterprise File Fabric backend. It registers the remote, manages permanent-token to session-token authentication, maps File Fabric RPC calls to rclone filesystem operations, handles version-specific capabilities, directory caching, upload/finalize flows, background tasks, metadata updates, moves, copies, trash cleanup, and object operations.

Important APIs and types: `Options` stores URL, root folder ID, permanent token, cached session token/expiry/version, and encoding. `Fs` stores the REST client, config mapper, `dirCache`, pacer, token mutex, token expiry, token-expired flag, capability flags, and precision. `Object` stores path, metadata state, size, modtime, file ID, and content type. Key methods include `NewFs`, `getToken`, `rpc`, `setCapabilities`, `FindLeaf`, `CreateDir`, `listAll`, `List`, `Put`, `Mkdir`, `purgeCheck`, `Copy`, `waitForBackgroundTask`, `renameLeaf`, `move`, `Move`, `DirMove`, `CleanUp`, `DirCacheFlush`, `Object.readMetaData`, `Object.modifyFile`, `Object.Open`, `Object.Update`, and `Object.Remove`.

Control flow: `NewFs` parses options, trims URL/root, creates a REST client, initializes features, reads appliance version if missing, restores token expiry, builds `dirCache`, and probes root metadata to handle file roots or cache folder IDs. `rpc` always posts form data to `/api/rpc.php`, injects a token from `getToken` unless explicitly supplied, and uses a pacer plus status-aware retry handling. `getToken` serializes refresh with a mutex, refreshes empty/expired/invalid tokens using the permanent token, writes token and expiry back to the config mapper, refreshes appliance info, and updates capabilities. Listing pages through `getFolderContents`, filters trashed items, normalizes names, and updates `dirCache`. Upload initializes an upload, registers an abort-on-error cleanup, PUTs content to the uploader endpoint, validates success and size, completes the upload, then fixes MIME type if the server stored the wrong value.

State and persistence behavior: Local state includes cached token, token expiry, version, capabilities, precision, directory IDs, and object metadata. The backend writes refreshed token, expiry, and version into the config mapper. Server-side state includes folders/files, soft deletes, trash, uploads, metadata such as `fi_localtime` and `fi_contenttype`, and asynchronous background tasks. Zero-byte files are represented with a special MIME type and read back as empty streams.

Dependencies and integration points: It depends on `backend/filefabric/api`, rclone `fs` interfaces, `dircache`, `rest`, `pacer`, `fshttp`, `atexit.OnError`, `random.String`, and `log.Trace`. It implements `fs.Purger`, `Copier`, `Mover`, `DirMover`, `DirCacheFlusher`, `CleanUpper`, `MimeTyper`, and `IDer`.

Risks: Token refresh and status retry are central and race-sensitive, hence the mutex and atomic invalidation flag. Version comparison is string-based and assumes labels sort usefully. Background tasks are polled without a timeout besides context. Moves and renames may require multiple API calls and temporary names. Upload cancellation is best-effort. `Size` uses `context.TODO()` when lazily reading metadata. Empty-file MIME substitution is a provider workaround that can leak if not consistently corrected.

Test signals: The integration test delegates to `fstests` using `TestFileFabric:` and a nil `*filefabric.Object`. There are no local unit tests for token refresh, custom codecs, background task polling, or upload abort paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filefabric/filefabric.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filefabric/filefabric_test.go -->
# sources/user-network-fs/rclone/backend/filefabric/filefabric_test.go

Purpose: This is the generic integration-test entry point for the Enterprise File Fabric backend.

Important APIs and types: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestFileFabric:"` and `NilObject: (*filefabric.Object)(nil)`.

Control flow: The shared rclone test suite constructs the configured remote and exercises standard filesystem behavior.

State and persistence behavior: It mutates the configured File Fabric remote and any token/version values the backend persists through its config mapper.

Dependencies and integration points: It depends on the backend package and `fstests`, plus a configured `TestFileFabric:` remote.

Risks: Provider version, token expiry, and background task timing may affect integration reliability. This file adds no unit-level coverage for File Fabric's custom authentication and upload flows.

Test signals: Passing `fstests.Run` is the broad compatibility signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filefabric/filefabric_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filelu/api/types.go -->
# sources/user-network-fs/rclone/backend/filelu/api/types.go

Purpose: This package defines response structures for FileLu API calls used by the backend.

Important APIs and types: The DTOs include `MultipartInitResponse`, `CreateFolderResponse`, `DeleteFolderResponse`, `FolderListResponse`, `FileDirectLinkResponse`, `FileInfoResponse`, `DeleteFileResponse`, and `AccountInfoResponse`. Nested anonymous structs model upload IDs, session IDs, upload server, folder IDs, object paths, file codes, paths, sizes, hashes, and account storage strings.

Control flow: There is no executable logic; `filelu_client.go`, `filelu_file_uploader.go`, and `filelu_object.go` unmarshal these responses from `rest.CallJSON` or manual HTTP calls.

State and persistence behavior: The structs represent remote folder/file metadata, upload session state, direct links, deletion status, and quota fields. They do not store local state.

Dependencies and integration points: The file depends only on `encoding/json` for `json.Number`. It is the schema contract for FileLu list, upload, delete, account, and file-info operations.

Risks: The backend assumes status `200` means success and often trusts nested fields. Storage values are strings parsed elsewhere as GB. Several nested response shapes are anonymous, which reduces reuse and makes schema drift harder to test directly.

Test signals: No direct DTO tests exist; generic FileLu integration tests indirectly cover the fields used by standard operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filelu/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filelu/filelu.go -->
# sources/user-network-fs/rclone/backend/filelu/filelu.go

Purpose: This is the main FileLu rclone backend. It registers configuration, creates HTTP/REST clients, exposes features, and implements root handling, listing, uploads, directory creation/removal, quota, purge, and move-by-copy/delete behavior.

Important APIs and types: `Options` stores API key, encoding, upload cutoff, and chunk size. `Fs` stores name/root/options/features, endpoint, pacer, REST/client handles, and target filename. Key methods include `NewFs`, `Mkdir`, `About`, `Purge`, `List`, `Put`, `Move`, and `Rmdir`.

Control flow: `NewFs` parses config, requires the FileLu key, trims root, builds clients, fills features, and probes root-as-file by temporarily changing root and calling `NewObject`. `List` builds a full API path, calls `getFolderList`, filters nested top-level folders when listing root, strips the backend root from folder paths, and returns `fs.Dir` or lightweight `Object` entries. `Put` delegates to `Object.Update`. `Move` either copies to a local absolute path if the destination looks local, or opens the source, uploads to the destination path, then removes the source. `Rmdir` lists a directory first and refuses to delete if it contains files or folders.

State and persistence behavior: Local state is limited to the root string, options, and cached object fields in listings. Server-side state changes include folder create/delete, upload, purge, and file removal after move. `About` parses provider storage strings into bytes.

Dependencies and integration points: It depends on rclone `fs`, `configstruct`, `fshttp`, `rest`, `pacer`, `encoder`, and helpers in the sibling FileLu files. It advertises empty-directory support, slow hashes, `fs.Purger`, `fs.Abouter`, `fs.Mover`, and `fs.Object`.

Risks: `Move` has surprising local-filesystem behavior for absolute or Windows-looking destinations, which is unusual for a cloud backend. Remote moves are copy/upload/delete, not atomic. Listing uses current time for folder and file modtimes. Root-as-file detection is heuristic. The pacer is a bare `pacer.New()` rather than configured with min/max. Errors from `Mkdir` during multipart parent creation can be ignored in one path.

Test signals: The integration test runs `fstests` against `TestFileLu:` with invalid UTF-8 skipped. There are no local unit tests for path stripping, local-destination moves, or quota parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filelu/filelu.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filelu/filelu_client.go -->
# sources/user-network-fs/rclone/backend/filelu/filelu_client.go

Purpose: This file contains FileLu API client helpers for multipart initialization/completion, folder CRUD/listing, direct download links, file delete, account info, and file info.

Important APIs and types: Functions include `multipartInit`, `completeMultipart`, `createFolder`, `getFolderList`, `deleteFolder`, `getDirectLink`, `deleteFile`, `getAccountInfo`, and `getFileInfo`. It uses DTOs from `backend/filelu/api`, `rest.Opts`, the backend HTTP client, and FileLu key authentication on query parameters.

Control flow: Most helpers issue GET requests through `f.srv.CallJSON` inside the pacer and check `Status == 200`. `completeMultipart` uses a raw POST to the upload server with `X-RC-Upload-Id`, `X-Sess-ID`, and `X-Object-Path` headers and expects HTTP 202. `getFolderList` converts remote folder paths and file names back to standard encoding. `getFileInfo` returns `fs.ErrorObjectNotFound` if status is not 200 or the result list is empty.

State and persistence behavior: The helpers do not store local state; they create, list, and delete provider state. Multipart upload state is represented by upload ID, session ID, server, and object path supplied by the provider.

Dependencies and integration points: Higher-level methods in `filelu.go`, `filelu_file_uploader.go`, and `filelu_object.go` call these helpers. They integrate with rclone retry classification through `shouldRetry`, `shouldRetryHTTP`, and `fserrors.ShouldRetry`.

Risks: API keys are sent as query parameters. Retry handling sometimes wraps errors before returning retry decisions. Completion reads and returns response bodies only on non-202. Folder-not-found detection is string based. There is limited validation of returned server URLs and multipart IDs.

Test signals: There are no direct unit tests; the generic FileLu integration suite indirectly exercises folder, upload, download, and delete helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filelu/filelu_client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filelu/filelu_file_uploader.go -->
# sources/user-network-fs/rclone/backend/filelu/filelu_file_uploader.go

Purpose: This file implements FileLu upload paths: fixed-size multipart uploads for large objects, upload-part requests, simple form upload through an upload server, and upload-server discovery.

Important APIs and types: Functions include `multipartUpload`, `uploadPart`, `uploadFile`, `getUploadServer`, `uploadFileWithDestination`, and `respBodyClose`.

Control flow: `multipartUpload` ensures the parent directory, initializes multipart upload, buffers input up to configured chunk size using 1 MiB reads, uploads each part with numbered PUT requests, uploads a final partial part, then completes the multipart upload. `uploadFile` ensures the target directory exists, lists existing entries and deletes an existing file with the same remote, gets an upload server/session, and posts a multipart form containing session ID, account type, folder path, and file content. `uploadFileWithDestination` streams multipart data through an `io.Pipe` from a goroutine while the HTTP request is sent and decodes an array response for `file_code` and `file_status`.

State and persistence behavior: Upload state is held in provider session IDs and multipart upload IDs. Local transient state includes chunk buffers, a pipe, multipart writer, and a boolean used to decide whether to attempt cleanup after copy failure. Server-side state may include deletion of an existing destination before upload completion.

Dependencies and integration points: Called by `Object.Update` and `Fs.Move`. It uses raw `net/http` for upload servers and `rest` for upload-server discovery. It relies on encoding helpers and FileLu API conventions.

Risks: `multipartUpload` appends to a buffer and uploads the whole buffer when length is at least chunk size, so reads larger than `chunk_size` could produce oversized parts. The simple upload path deletes existing files before upload, creating a data-loss window. `uploadFileWithDestination` references `result[0].FileStatus` even when `len(result) == 0`, which can panic on empty responses. The `isDeletionRequired` flag is written from a goroutine without synchronization. Retry around a streaming `io.Pipe` request is fragile because the body cannot be replayed.

Test signals: No direct tests cover upload edge cases; integration tests are the main signal for normal-size uploads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filelu/filelu_file_uploader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filelu/filelu_helper.go -->
# sources/user-network-fs/rclone/backend/filelu/filelu_helper.go

Purpose: This file provides FileLu backend utility methods for file-code lookup, feature/name/root/hash/precision methods, encoding conversion, retry classification, and root splitting.

Important APIs and types: `errFileNotFound`, `getFileCode`, `Features`, `fromStandardPath`, `toStandardPath`, `Hashes`, `Name`, `Root`, `Precision`, `String`, `isFileCode`, `shouldRetry`, `shouldRetryHTTP`, and `rootSplit`.

Control flow: `getFileCode` lists the parent directory and scans files for an exact server path match, returning the provider file code. `isFileCode` checks a strict 12-character lowercase alphanumeric shape. Retry helpers delegate to rclone retry rules and selected HTTP status codes. `rootSplit` separates the first path component from the rest.

State and persistence behavior: The helpers do not persist state. `getFileCode` performs a remote list and depends on current provider state.

Dependencies and integration points: `filelu_object.go` uses `getFileCode`, `isFileCode`, hash/metadata helpers, and retry helpers. `filelu_client.go` and upload code share the retry helpers.

Risks: `Hashes` advertises an empty set, while `Object.Hash` has an MD5 implementation for some file-code-derived cases, creating a capability mismatch. `getFileCode` relies on exact path construction after list normalization. `Precision` reports unsupported modtimes, while objects still cache `time.Now()` for listings and lookups.

Test signals: No direct helper tests exist; integration tests cover helper behavior only indirectly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filelu/filelu_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filelu/filelu_object.go -->
# sources/user-network-fs/rclone/backend/filelu/filelu_object.go

Purpose: This file implements FileLu object lookup, download, update, removal, hashing, and basic object metadata methods.

Important APIs and types: `Object` stores `fs`, `remote`, `size`, and `modTime`. Methods include `Fs.NewObject`, `Object.Open`, `Object.Update`, `Object.Remove`, `Object.Hash`, `String`, `Fs`, `Remote`, `Size`, `ModTime`, `SetModTime`, and `Storable`.

Control flow: `NewObject` joins root and remote, resolves a file code by listing the parent, fetches file info, parses size, and returns an object. `Open` gets a direct link and size, decodes range/seek options, performs a full HTTP GET to the direct link, optionally discards bytes to reach the offset, and wraps the body with `io.LimitReader` for count-limited reads. `Update` selects simple upload or multipart upload based on `upload_cutoff`, then updates cached size and modtime. `Hash` supports MD5 only if it can infer a file code from the root or a 12-character code in parentheses in the remote name.

State and persistence behavior: Object metadata is cached locally but often uses `time.Now()` rather than provider modtime. Updates create or replace remote files. Removal deletes the remote file by full path. Direct-link downloads update the cached size.

Dependencies and integration points: It calls FileLu client helpers, upload helpers, raw HTTP client, rclone range/seek options, and hash interfaces.

Risks: Range reads are client-side skips over a full direct-link response rather than server Range requests, so large offsets are inefficient. Hash availability is path-shape dependent and not aligned with `Fs.Hashes`. `NewObject` loses provider modtime. Multipart upload is selected solely by size and assumes known positive sizes. `SetModTime` is unsupported.

Test signals: Generic `fstests` exercise normal object lifecycle; invalid UTF-8 is skipped by `filelu_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filelu/filelu_object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filelu/filelu_test.go -->
# sources/user-network-fs/rclone/backend/filelu/filelu_test.go

Purpose: This is the generic integration-test entry point for the FileLu backend.

Important APIs and types: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestFileLu:"`, nil object, and `SkipInvalidUTF8: true`.

Control flow: The shared rclone test harness runs standard filesystem behavior tests against the configured remote.

State and persistence behavior: It mutates the configured FileLu remote and has no additional local state.

Dependencies and integration points: It depends on `fstests` and valid FileLu credentials under `TestFileLu:`.

Risks: Skipping invalid UTF-8 means the encoding-heavy path in `filelu.go` has reduced generic test coverage. FileLu-specific multipart, range, and hash edge cases have no local unit tests.

Test signals: Passing `fstests.Run` is the primary signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filelu/filelu_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filelu/utils.go -->
# sources/user-network-fs/rclone/backend/filelu/utils.go

Purpose: This file contains a single utility for converting FileLu storage quota strings into byte counts.

Important APIs and types: `parseStorageToBytes(storage string) (int64, error)` parses a floating-point value from the string with `fmt.Sscanf` and multiplies it by 1024^3.

Control flow: `Fs.About` calls this helper for total and used storage strings from the account-info response.

State and persistence behavior: There is no state; it is a pure parser.

Dependencies and integration points: It depends on `fmt` and the assumption that FileLu account storage strings are numeric GB values.

Risks: Units are implicit and always treated as GiB, so strings with explicit units or different units would parse only the leading number and produce incorrect values. There are no tests for decimal, empty, or unit-suffixed inputs.

Test signals: No direct tests exist; `About` integration is the only coverage path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filelu/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filen/filen.go -->
# sources/user-network-fs/rclone/backend/filen/filen.go

Purpose: This is rclone's Filen backend. It uses the Filen Go SDK to authenticate, browse encrypted cloud storage, upload/download files, expose BLAKE3 hashes, support chunked writing, move/copy-like operations through SDK rename/move primitives, recursive listing, quota, and trash cleanup.

Important APIs and types: `Options` stores credentials/API key, internal key material, base folder UUID, encoding, and upload concurrency. `Fs` stores root `Directory`, SDK handle, encoder, features, concurrency, and pacer. `Directory` implements rclone directory entries with SDK directory objects. `Object` wraps SDK files and tracks `isMoved`. `chunkWriter` wraps SDK `FileUpload` for concurrent chunk uploads while preserving hash order. Key methods include `NewFs`, `List`, `NewObject`, `Put`, `PutStream`, `OpenChunkWriter`, `Mkdir`, `Rmdir`, `Object.Open`, `Object.Update`, `Object.Remove`, `Move`, `DirMove`, `ListR`, `About`, `CleanUp`, and helper move/path functions.

Control flow: `NewFs` reveals password/API key, creates an SDK client either from internal TS config or API-key login, resolves root or file-root parent, builds features, and stores the SDK directory root. `List` resolves and reads a directory, then wraps returned SDK directories/files. `Put` creates parent directories, creates an encrypted incomplete file with MIME and timestamps, and uploads through the SDK. `OpenChunkWriter` validates chunk-size multiple of SDK chunk size, creates an incomplete file, and returns a `chunkWriter`; `WriteChunk` splits each rclone chunk into SDK chunks, hashes chunks in logical order even if uploaded out of order, uploads with pacer retry, and records bucket/region response for completion. Moves lock the SDK, then choose rename, move, or a temporary UUID rename plus move plus final rename to avoid destination overwrite problems. Recursive listing builds UUID-to-path maps from SDK recursive results.

State and persistence behavior: Local state includes the SDK session/key material, root directory object, object file pointers, moved-object invalidation, chunk-writer hash buffers, total uploaded size, and upload bucket/region channel. Remote state changes include encrypted file creation, metadata updates, trashing files/directories, move/rename operations, recursive listings, and global trash cleanup. `CleanUp` empties all Filen trash, not only the mounted root.

Dependencies and integration points: It depends heavily on `github.com/FilenCloudDienste/filen-sdk-go`, SDK client/types, `uuid`, `errgroup`, rclone `fs` interfaces, `encoder`, `obscure`, `pacer`, and `list.Helper`. It implements `fs.Mover`, `DirMover`, `Purger`, `PutStreamer`, `CleanUpper`, `ListRer`, `Abouter`, `OpenChunkWriter`, `Directory`, `Object`, `MimeTyper`, `IDer`, `ParentIDer`, and `ChunkWriter`.

Risks: The backend relies on SDK encryption/auth behavior and internal config fields. Move-with-rename uses best-effort deferred rollback that prints to stdout on failure. `chunkWriter` stores out-of-order chunk bytes in memory until hashes can be written in order; high concurrency and out-of-order writes can increase memory. `Abort` is a no-op. Range parsing in `Object.Open` passes `End+1` as limit to the SDK and depends on SDK interpretation. `CleanUp` may affect trash outside the mounted root. Rmdir returns generic errors for missing/non-empty directories rather than always rclone sentinel errors.

Test signals: The integration test runs `fstests` against `TestFilen:`. There are no local unit tests for chunk-writer ordering, move rollback, recursive path reconstruction, or internal TS config authentication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filen/filen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filen/filen_test.go -->
# sources/user-network-fs/rclone/backend/filen/filen_test.go

Purpose: This is the generic integration-test entry point for the Filen backend.

Important APIs and types: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestFilen:"` and `NilObject: (*Object)(nil)`.

Control flow: The shared rclone test suite constructs a Filen remote and exercises standard filesystem behavior.

State and persistence behavior: It mutates the configured Filen test remote, including encrypted files, directories, trash, and metadata.

Dependencies and integration points: It depends on `fstests`, the Filen backend, the Filen SDK, and configured credentials/API key.

Risks: Filen-specific chunk-writer concurrency, global trash cleanup, move rollback, and recursive listing helpers are not unit-tested here.

Test signals: Passing `fstests.Run` is the broad backend compatibility signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filen/filen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filescom/filescom.go -->
# sources/user-network-fs/rclone/backend/filescom/filescom.go

Purpose: This is rclone's Files.com backend. It registers configuration, builds Files.com SDK clients, maps rclone filesystem operations to file/folder/migration/bundle APIs, supports API-key or username/password sessions, and implements listing, upload/download, mkdir/rmdir/purge, server-side copy/move, public links, hashes, modtime, and MIME metadata.

Important APIs and types: `Options` stores site, username, password, API key, and encoding. `Fs` stores file, folder, migration, and bundle SDK clients plus pacer. `Object` stores remote path, size, CRC32, MD5, MIME type, and modtime. Key functions include `NewFs`, `newClientConfig`, `readMetaDataForPath`, `List`, `createObject`, `Put`, `PutStream`, `mkdir`, `mkParentDir`, `Mkdir`, `DirSetModTime`, `purgeCheck`, `Copy`, `waitForAction`, `Move`, `DirMove`, `PublicLink`, `Hashes`, `Object.Hash`, `Object.readMetaData`, `Object.SetModTime`, `Object.Open`, `Object.Update`, and `Object.Remove`.

Control flow: `newClientConfig` validates a site subdomain/custom domain, configures the SDK HTTP client, uses API key if present, or reveals the password and creates a session. `NewFs` trims root, builds clients, fills features, and detects file roots by reading metadata at the root. `List` obtains a folder iterator, converts display names through the encoder, and creates directory or object entries. Uploads use the SDK upload helper with destination path and provided mtime, then refresh metadata. Downloads build a Range header from rclone range/seek options and capture the SDK response body through `ResponseBodyOption`. Copy/move operations start SDK actions and wait for file migrations to complete. Public links create bundles with optional expiry.

State and persistence behavior: Local state is the SDK config/session ID, root, feature set, and cached object metadata. Remote state includes folder creation, recursive or checked deletion, uploads, copy/move migrations, bundle links, file modtime updates, and object removals. `purgeCheck` can retry folder-not-empty errors to handle eventual consistency during child deletion.

Dependencies and integration points: It depends on `github.com/Files-com/files-sdk-go/v3` clients for file, folder, file migration, bundle, and session APIs; rclone `fs` interfaces; `fshttp`; `obscure`; `encoder`; and `pacer`. It advertises `Purger`, `PutStreamer`, `Copier`, `Mover`, `DirMover`, `PublicLinker`, `MimeTyper`, CRC32, and MD5.

Risks: SDK `ResponseError` retry matching is type-dependent. CRC32 formatting uses `%08s`, padding with spaces rather than zeros if the SDK returns short strings. `Object.Open` always sets a Range header; if count is zero, the computed end can be `offset-1`. Copy rejects case-only equal paths because the backend is case-insensitive. `PublicLink` ignores the `unlink` parameter. Session creation requires password reveal and stores the session only in memory.

Test signals: The integration test runs `fstests` against `TestFilesCom:`. No local unit tests cover SDK config validation, migration wait failures, Range header construction, or CRC32 formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filescom/filescom.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filescom/filescom_test.go -->
# sources/user-network-fs/rclone/backend/filescom/filescom_test.go

Purpose: This is the generic integration-test entry point for the Files.com backend.

Important APIs and types: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestFilesCom:"` and `NilObject: (*filescom.Object)(nil)`.

Control flow: The shared rclone test suite constructs the configured remote and runs standard filesystem tests.

State and persistence behavior: It mutates the configured Files.com remote and any server-side sessions/actions created by backend operations.

Dependencies and integration points: It depends on `fstests`, the Files.com backend package, the Files.com SDK, and configured test credentials.

Risks: Provider migrations, session auth, and bundle links are not unit-tested locally. The generic suite is the only signal for SDK integration.

Test signals: Passing `fstests.Run` is the primary compatibility signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/filescom/filescom_test.go -->

# Research: subset-b-009746

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/huaweidrive/huaweidrive_test.go -->
## Research: sources/user-network-fs/rclone/backend/huaweidrive/huaweidrive_test.go

### Purpose
This file is a broad test suite for the Huawei Drive rclone backend. It combines a real integration test entry point, constructor and interface checks, encoding and query-filter unit tests, API type and response-shape validation, retry/error classification tests, and behavioral assertions for metadata, modtime, MIME type, upload mode selection, domain mapping, and root-folder detection logic. It is not production code, but it documents many backend contracts that the implementation is expected to preserve.

### Important APIs, Types, and Functions
Key test targets include `NewFs`, `Fs.Name`, `Fs.Root`, `Fs.String`, `Fs.Precision`, `Fs.Hashes`, `Object.Hash`, `Object.Storable`, `Object.String`, `Object.SetModTime`, `Object.MimeType`, `parsePath`, `NewQueryFilter`, and the `QueryFilter` builder methods. It also validates package constants such as `rcloneClientID`, `rootURL`, `uploadURL`, `defaultChunkSize`, `retryErrorCodes`, OAuth scopes and auth/token URLs, and API constants from `backend/huaweidrive/api`.

`TestIntegration` delegates to `fstests.Run` against `TestHuaweiDrive:` and declares the backend's NilObject and Windows-character skip behavior. Compile-time interface tests assert that `Fs` implements `fs.Fs`, `fs.Copier`, `fs.Mover`, `fs.DirMover`, `fs.ListRer`, `fs.Abouter`, `fs.Purger`, `fs.CleanUpper`, `fs.UserInfoer`, `fs.Disconnecter`, and `fs.DirCacheFlusher`, while `Object` implements `fs.MimeTyper`.

### Control Flow and Behavior
The tests cover construction failure for empty config, simple accessors, and Huawei's no-modtime-preservation behavior. Encoding tests build the expected `encoder.MultiEncoder` flags and verify full-width or visible replacement of reserved characters, leading/trailing spaces, leading dots/tildes, right periods, path separators, invalid UTF-8/control characters, and round-tripping where possible.

`TestQueryFilter` exercises composable filtering by parent folder, MIME type equality/inequality, filename equality and containment, recycled/directly-recycled flags, favorites, and edited-time ranges. It also verifies quote escaping in filenames. Later tests use small in-memory examples to model root-folder detection: prefer parent IDs that are not themselves file IDs, then fall back to the most common parent when all parents are known file IDs.

### State and Persistence
The file directly inspects lightweight state such as `Fs.rootFolderID`, `Options.RootFolderID`, `Options.ChunkSize`, `Options.ListChunk`, `Options.UploadCutoff`, and object metadata fields (`remote`, `size`, `modTime`, `id`, `sha256`, `mimeType`, `hasMetaData`). It does not persist state itself, but its assertions pin config defaults, cached root-folder behavior, and auth/domain configuration that production code depends on.

### Dependencies and Integration Points
The tests depend on rclone core packages (`fs`, `fstest/fstests`, `configmap`, `hash`, `encoder`), the Huawei API type package, standard `mime`, `path`, `time`, and HTTP primitives. `TestIntegration` is the only test that expects a configured live remote; the rest are unit-level checks over local structs and pure helpers.

### Risks and Edge Cases
The suite highlights risk areas: Huawei rejects many filename characters; modtimes are not preserved even if API parameters exist; only SHA256 is expected; temporary Huawei error codes must remain retryable; some MIME detections vary by host OS; root-folder auto-detection can be heuristic; and changing OAuth scopes, URLs, or domain maps can break authentication or regional routing. Several tests model behavior rather than calling the exact production function, so they can drift if the implementation changes without the test being updated to exercise the real path.

### Test Signals
The test file itself is the signal. It provides regression coverage for encoding policy, query generation strings, API JSON model fields, retry/non-retry classification, upload type thresholds, interface conformance, and object metadata methods. The integration test is gated by availability of `TestHuaweiDrive:` and is likely skipped or externally configured in normal CI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/huaweidrive/huaweidrive_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/client.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/api/client.go

### Purpose
`client.go` defines the top-level iCloud API client used by both Drive and Photos services. It owns credentials, the mutable `Session`, a REST client, a service-specific PCS-cookie scope, optional session persistence callback, and lazy construction of `DriveService`. It centralizes authentication reuse, reauthentication on expired sessions, and disk caching of Apple webservice endpoint metadata.

### Important APIs, Types, and Functions
The exported constants define Apple endpoints (`baseEndpoint`, `setupEndpoint`, `authEndpoint`) and account webservice keys (`WsDrive`, `WsDocs`, `WsPhotos`). `Client` stores the lowercased Apple ID, password, remote cache namespace, PCS webservice key, REST client, `Session`, callback, cached `DriveService`, and mutex. `New` creates a client and seeds trust token, cookies, and client ID into a fresh `Session`.

`DriveService` lazily calls `NewDriveService`. `Request` wraps `Session.Request` and reauthenticates on status 401, 421, or 423 before retrying once. `Authenticate` serializes auth with the client mutex, calls `authenticateSession`, then ensures ADP/PCS cookies for the configured service. `IntoReader` JSON-marshals request bodies. `RequestError` represents successful HTTP responses that contain a failing iCloud inner status.

### Control Flow
Authentication uses the cheapest valid path first. If saved cookies and `AccountInfo.Webservices` exist, validation is skipped and requests fail lazily if the session is bad. If cookies exist without in-memory endpoints, `loadCachedWebservices` tries `webservices.json`. If still needed, `ValidateSession` is attempted. On failure, cookies are cleared and a full SRP sign-in is started through `Session.SignIn`; if 2FA is required, the caller must continue the interactive config flow. Otherwise `AuthWithToken` finalizes the account session and webservice endpoints are cached.

### State and Persistence
The stateful pieces are `Session` fields, saved cookies/trust token handled by callers, and `webservices.json` under `config.GetCacheDir()/iclouddrive-photos/<remoteName>/`. The remote name is sanitized with `filepath.Base` for cache namespacing. `ClearCacheDir` removes all cached files for a remote. The session callback is invoked after a successful full auth and after new PCS cookies are acquired.

### Dependencies and Integration Points
This file uses rclone `fs`, `config`, `fshttp`, and `rest` packages. It integrates directly with `Session` from `session.go`, `DriveService` from `drive.go`, and shared cache helpers from `photos.go` (`cacheSubdir`, `saveJSONCache`). Photos code constructs `Client` with `pcsWSKey=WsPhotos`; Drive uses `WsDrive`.

### Risks and Edge Cases
Skipping validation when cookies and endpoints are present improves startup time but moves stale-session failures to first request. Reauth under `Request` returns `trust token expired, please reauth` when Apple demands 2FA. `loadCachedWebservices` trusts unexpired disk endpoint metadata if JSON parses and is non-empty; service URL changes or stale cache can cause later request failures. The client mutex protects auth and drive-service initialization but not all direct session field reads elsewhere.

### Test Signals
There is no direct `client.go` unit test in this subset. Behavior is indirectly tested through session tests, Photos HTTP tests that instantiate `Client`/`Session`, and backend config flows in `icloud.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/drive.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/api/drive.go

### Purpose
`drive.go` implements iCloud Drive API operations as a `DriveService`. It wraps Apple's drivews and docws endpoints for item lookup, folder listing, download URL resolution, uploads, file updates, folder creation, move, rename, trash, and type conversion between several Apple response shapes.

### Important APIs, Types, and Functions
`DriveService` stores the owning `Client`, root drive ID, drive endpoint, and docs endpoint. Lookup methods include `GetItemByDriveID`, `GetItemsByDriveID`, `GetDocByPath`, `GetItemByPath`, `GetDocByItemID`, `GetItemRawByItemID`, and `GetItemsInFolder`. Mutation methods include `MoveItemToTrashByItemID`, `MoveItemToTrashByID`, `CreateNewFolderByItemID`, `CreateNewFolderByDriveID`, `RenameItemByItemID`, `RenameItemByDriveID`, `MoveItemByItemID`, `MoveItemByDriveID`, `CopyDocByItemID`, `CreateUpload`, `Upload`, and `UpdateFile`.

Important models are `UpdateFileInfo`, `FileFlags`, `DriveItemRaw`, `DriveItemRawInfo`, `DocumentUpdateResponse`, `Document`, `DocumentData`, `SingleFileResponse`, `UploadResponse`, `FileRequest`, `CreateFoldersResponse`, and `DriveItem`. Helpers include `NewUpdateFileInfo`, `DriveItemRaw.SplitName`, `ModTime`, `CreatedTime`, `IntoDriveItem`, `Document.DriveID`, `DriveItem.IsFolder`, `DownloadURL`, `FullName`, `GetDocIDFromDriveID`, `DeconstructDriveID`, `ConstructDriveID`, and `GetContentTypeForFile`.

### Control Flow
Most methods construct JSON payloads with `IntoReader`, set session headers via `Session.GetHeaders`, select either drivews or docws, then call `Client.Request` for auth-aware retry. Item-ID methods often first resolve a document to a drivews ID, because mutation endpoints operate on drivews IDs. Rename, move, and trash operations inspect per-item status and, when `force` is true and Apple reports `ETAG_CONFLICT`, retry once using the latest returned etag.

Downloads first resolve a `FileRequest` to either `DataToken.URL` or `PackageToken.URL`. `DownloadFile` then performs a raw GET and recursively follows Apple's nonstandard HTTP 330 redirect if a `Location` header is available. Uploads are two-phase: `CreateUpload` requests an upload URL and document ID, `Upload` posts the file body to that URL, and `UpdateFile` commits document metadata and content receipts.

### State and Persistence
This layer does not persist local state. It consumes session cookies and webservice endpoints from `Client.Session.AccountInfo.Webservices`. It maps server timestamps into `time.Time` and constructs returned `DriveItem` values after updates. `NewUpdateFileInfo` sets default update flags (`add_file`, conflict allowed, writable/executable visible file flags).

### Dependencies and Integration Points
The service depends on `Client.Request`, `Session.GetHeaders`, rclone `rest` and `fs.OpenOption`, standard `mime`, `url`, `uuid`, and time parsing. Higher-level backend code uses these methods to implement rclone filesystem operations. The `defaultZone` constant anchors CloudDocs document operations unless a drive ID includes a different zone.

### Risks and Edge Cases
Several methods assume non-empty server arrays and access `[0]` without length checks, so malformed or empty Apple responses can panic. `NewDriveService` assumes both drive and docs webservice entries exist. `SplitName` relies on filename text because Apple extension fields are noted as unreliable. MIME detection falls back to `text/plain`, which satisfies API requirements but may be semantically weak for unknown binary files. Etag force retries are limited and should not mask persistent conflicts.

### Test Signals
No direct drive API unit test appears in this subset. Huawei tests cover a similar MIME fallback concept, but this file is mainly validated by higher-level iCloud Drive backend tests outside the listed files and by live integration behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/drive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/photos.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/api/photos.go

### Purpose
`photos.go` implements the CloudKit-facing iCloud Photos service used by the rclone Photos backend. It discovers photo libraries/zones, builds smart and user album models, lists media through CloudKit records/query partitions, caches libraries/albums/photos/sync tokens on disk, applies incremental changes/zone deltas when possible, classifies smart album membership, builds file entries for originals/Live Photo companions/edited derivatives/RAW alternatives, and resolves fresh download URLs.

### Important APIs, Types, and Functions
Top-level service types are `PhotosService`, `Library`, `Album`, `Photo`, and `Filter`. Construction happens through `NewPhotosService`; tests can use `NewTestPhotosService` and `Album.SetTestPhotoCache`. Library APIs include `GetLibraries`, `GetLibraryAlbumCounts`, `PollForChanges`, `resolveZone`, and `LookupDownloadURL`. Library methods include `GetAlbums`, `GetAlbumCounts`, `checkForChanges`, `applyPendingDelta`, `saveSyncToken`, `readSyncToken`, `zoneIDMap`, and cache invalidation helpers. Album methods include `GetPhotos`, `GetPhotoByName`, `fetchPhotoCount`, `fetchPhotosParallel`, `buildPartitionQuery`, and disk-cache load/save helpers.

Important parsing helpers are `parsePhotoRecords`, `buildPhotos`, `classifySmartAlbums`, `deduplicateFilenames`, `parseDeltaRecords`, `deltaContainsAlbumChanges`, `relationAlbumRecordFromRecordName`, and `albumCacheKey`. CloudKit model structs include `albumRecord`, `albumQueryResponse`, `changesZoneResponse`, `changesZoneResult`, `deltaParseResult`, `photoRecord`, and typed field wrappers such as `ckStringField`, `ckResourceField`, and `ckReferenceField`.

### Control Flow
`NewPhotosService` verifies the `ckdatabasews` webservice is active, builds the CloudKit database root URL, and probes indexing state. `GetLibraries` first returns in-memory libraries if present, but still attempts rediscovery and merge. With disk cache, it loads `libraries.json`, batch-checks zone deltas, then attempts rediscovery; with no cache, it discovers zones from private and shared `changes/database`. Discovery admits only `PrimarySync` and `SharedSync*` zones.

`GetAlbums` returns cached in-memory albums, then disk `albums.json` if `cacheValid` is true, otherwise constructs smart album templates and fetches paginated user albums (`CPLAlbumByPositionLive`). Folder albums recursively query children by `parentId`. Shared libraries with the known invalid index error fall back to smart albums only. `GetPhotos` first checks and applies deltas, then serves memory or disk photo caches. If cache is unavailable/currentness cannot be proven, it fetches counts and performs parallel start-rank partition queries, with tail probing for stale or zero counts.

### State and Persistence
Photos state lives under `Client.CacheDir()`: `libraries.json`, per-zone `albums.json`, per-zone `syncToken`, and per-album photo caches named by a 16-hex-character SHA256 prefix of the album object type. Writes use temp-file plus rename via `atomicWriteFile`. `PhotosService.mu` protects the service library map, `Library.mu` protects albums, `Library.deltaMu` serializes pending delta application, and each `Album.mu` protects filename-keyed `photoCache`. `Library.cacheValid` is atomic and marks whether disk caches can be used.

Delta handling buffers the first changed page from `changes/zone` until albums are populated. It then drains remaining pages, classifies deleted IDs, new master/asset pairs, album membership changes, and asset-only metadata updates. It incrementally updates unaffected cached albums, invalidates affected user or smart album caches, clears album metadata cache on `CPLAlbum` changes, and advances the sync token only after successful application.

### Dependencies and Integration Points
The code depends on rclone `fs`, `pacer`, and `rest`, the shared `Client`/`Session` auth layer, CloudKit private/shared database endpoints, and `golang.org/x/text/unicode/norm` for NFC filename normalization. It integrates with rclone checkers for parallelism and with backend ChangeNotify through `PollForChanges`, which intentionally uses a separate in-memory notification token.

### Risks and Edge Cases
This is the highest-risk file in the subset. It relies on undocumented CloudKit record types, index names, field names, and Apple-specific error strings. Cache correctness depends on careful sync-token advancement and lock ordering. Some deltas cannot be safely applied and force cache invalidation. Empty or malformed Apple responses can degrade listing completeness or return errors. Filename dedup mutates `Photo` objects, so shared pointers must be copied before dedup. `GetPhotos` may issue many partition queries for large libraries and depends on server behavior that 200 records equal about 100 photos. Shared-library discovery must distinguish transient shared database failures from authoritative `ZONE_NOT_FOUND`.

### Test Signals
`photos_test.go` provides substantial regression coverage for stale-cache prevention on paged delta failure, library rediscovery and merge behavior, shared-zone preservation/drop decisions, user album retry behavior, smart-album fallback, folder child retry, media variant construction, NFC normalization, filename fallback, smart album classification, dedup stability, delta parsing, nested album invalidation, `FlushCaches` race safety, smart-album table shape, atomic writes, and album cache-key determinism.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/photos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/photos_test.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/api/photos_test.go

### Purpose
`photos_test.go` is the regression suite for `photos.go`. It builds local HTTP test services and temp cache directories to validate CloudKit request flow, library discovery, cache behavior, delta application, album construction, media parsing, filename normalization/deduplication, and atomic cache writes without contacting Apple.

### Important APIs, Types, and Functions
Test helpers include `setTestCacheDir`, `newHTTPTestPhotosService`, `writeJSON`, `readJSONBody`, `testAlbumRecordJSON`, and `newUserAlbumForTest`. They exercise `GetLibraries`, `GetAlbums`, `GetPhotos`, `buildPhotos`, `parsePhotoRecords`, `classifySmartAlbums`, `GetPhotoByName`, `deduplicateFilenames`, `deltaContainsAlbumChanges`, `parseDeltaRecords`, `applyPendingDelta`, `FlushCaches`, `buildSmartAlbums`, `atomicWriteFile`, and `albumCacheKey`.

### Control Flow
The HTTP tests install handlers that inspect request paths and JSON bodies. Library tests verify that cached libraries still trigger private/shared `changes/database` rediscovery, that merge preserves existing library objects and buffered deltas, and that shared-zone failures either preserve cached zones or drop them when a per-zone probe returns `ZONE_NOT_FOUND`. Album tests confirm private-library user album failures surface and allow retry, while known SharedSync index failures return only smart albums without caching the partial result.

Media construction tests build synthetic `photoRecord` masters/assets to cover original files, Live Photo MOV companions, nil/invalid filename or download URL cases, `filenameEnc` STRING vs base64 bytes, NFC normalization, `itemType` fallback names, edited JPEG/video derivatives, slo-mo metadata-only behavior, RAW alternatives, duplicate-extension `-alt` suffixing, combined edited+RAW variants, and extensionless Live Photo names.

### State and Persistence
Tests redirect rclone's cache directory to `t.TempDir()` and verify on-disk cache files directly. They create `libraries.json`, zone `syncToken`, album cache JSON files, and confirm atomic writes leave no `.tmp`. They inspect `pendingDelta`, `cacheValid`, `photoCache`, and `lib.albums` to validate in-memory cache transitions.

### Dependencies and Integration Points
The suite uses `httptest`, rclone `fs/config/pacer/rest`, and `testify` assertions. The tests deliberately avoid real network by pointing `Session.srv` at local test servers. They integrate with package-private fields because they are in package `api`, which lets them inspect locks, pending deltas, and cache internals.

### Risks and Edge Cases Covered
The strongest risk coverage is stale cache avoidance: a paged delta failure must not serve old cached photos and must clear `pendingDelta` so future checks are not stuck. Tests also cover CloudKit deleted relation records with missing `recordType`, malformed JSON records, asset-only smart album invalidation, nested folder album invalidation, shared pointer contamination during filename dedup, and concurrent `FlushCaches` with delta application.

### Test Signals
The file is high-value evidence for Photos correctness. It exercises both pure parsing logic and HTTP/cache control flow. Running it with the Go race detector would add value for `TestFlushCaches_NoPendingDeltaRace`, whose comments explicitly reference race detection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/photos_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/session.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/api/session.go

### Purpose
`session.go` implements Apple's iCloud session lifecycle. It manages cookies, Apple auth headers, SRP sign-in, 2FA push and SMS verification, trust-token exchange, session validation, Advanced Data Protection PCS cookie acquisition, and request header construction for both setup and idmsa endpoints.

### Important APIs, Types, and Functions
`Session` stores session token, `scnt`, session ID, account country, trust token, client ID, auth attributes, frame ID, cookies, account info, a mutex, REST client, and a `needs2FA` flag. `SignIn` orchestrates SRP auth through `authStart`, `authFederate`, `authSRPInit`, and `authSRPComplete`. `AuthWithToken`, `ValidateSession`, `TrustSession`, `RequestPushNotification`, `Validate2FACode`, `GetAuthState`, `RequestSMSCode`, and `ValidateSMSCode` cover post-SRP account login and 2FA flows.

Cookie and debug helpers include `mergeCookies`, `extractHeaders`, `GetCookieString`, `cookieValueFingerprint`, `authStateBodySummary`, `cookieDebugSummary`, `cookieDebugSummaries`, and `cookieJarDebugSummaries`. ADP helpers include `ensurePCSCookies`, `acquirePCSCookiesFor`, `pcsServices`, and `hasPCSCookiesFor`. Header helpers include `getSRPAuthHeaders`, `GetAuthHeaders`, `GetHeaders`, and `GetCommonHeaders`.

### Control Flow
`SignIn` starts an OAuth-like idmsa auth session, federates the Apple ID, creates an SRP client, sends public value `A`, decodes server salt and `B`, derives the password key, computes proofs, and completes sign-in. `authSRPComplete` treats HTTP 200 as success, 409 as 2FA required, 412 as a repair flow, 403 as invalid credentials, and other statuses as hard errors.

For 2FA, push validation posts a security code then trusts the session and calls `AuthWithToken`. SMS flow first retrieves auth state, optionally unwraps `phoneNumberVerification`, handles singular phone fallback, requests an SMS code, validates it, trusts the session, and logs into setup. `Request` wraps JSON REST calls and extracts cookies/session headers after successful calls. PCS acquisition polls `/requestPCS` every 10 seconds up to 30 attempts and verifies expected PCS cookies are present after a success response.

### State and Persistence
This file mutates only in-memory `Session` state; callers persist cookies, trust token, and selected auth state. `extractHeaders` updates cookies, account country, session ID, session token, trust token, scnt, and auth attributes from response headers. `mergeCookies` replaces cookies by name and removes existing cookies when Apple sends empty-value tombstones. `NewSession` creates a UUID frame ID and installs a request filter that forces the Safari-like iCloud user agent.

### Dependencies and Integration Points
The session layer depends on `srp.go` for SRP math, `Client.Authenticate` in `client.go`, backend config flow in `icloud.go`, rclone `fshttp` and `rest`, and Apple's `idmsa.apple.com/appleauth/auth` and setup webservice endpoints. It provides the cookie/header source for Drive and Photos requests.

### Risks and Edge Cases
The code is sensitive to Apple's private auth protocol, headers, status codes, and response nesting. Cookie handling must process tombstones correctly or stale 2FA/PCS cookies can poison later requests. PCS polling can block for up to five minutes and requires user approval. Debug helpers intentionally fingerprint rather than log secrets, which reduces leakage risk. `Session.Request` only extracts headers after no transport/error return; auth failure paths use direct calls where needed to capture response bodies and headers.

### Test Signals
`session_test.go` directly verifies cookie merging and empty-cookie deletion. Other behavior is indirectly exercised by config flows and Photos/Client tests. SRP cryptographic behavior is covered separately in `srp_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/session.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/session_test.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/api/session_test.go

### Purpose
`session_test.go` is a focused regression test for `Session.extractHeaders` and cookie management. It verifies that Apple response headers update session state and that Set-Cookie tombstones remove stale cookies instead of leaving empty cookie values in the jar.

### Important APIs, Types, and Functions
The tests construct `Session` values through `NewSession`, populate `Session.Cookies`, build synthetic `http.Response` objects with `Set-Cookie` and `X-Apple-Session-Token` headers, and call the package-private `extractHeaders` method. Assertions inspect `Session.Cookies`, `Session.SessionToken`, and `GetCookieString`.

### Control Flow
`TestExtractHeadersMergesCookies` starts with one cookie, sends an updated cookie with the same name and a new cookie, and checks that the existing entry is replaced and the new entry is appended. It also verifies that `X-Apple-Session-Token` is captured. `TestExtractHeadersDeletesEmptyCookies` starts with an HSA login cookie and a normal cookie, sends an empty-value Set-Cookie for the HSA login cookie, and expects only the normal cookie to remain.

### State and Persistence
The tests manipulate only in-memory session state. They validate the invariant that `GetCookieString` skips empty cookies because those cookies should have been removed by `mergeCookies` where possible.

### Dependencies and Integration Points
This file depends only on `net/http`, `testing`, and `testify`. It protects behavior used by the SRP/2FA config flow and all subsequent Drive/Photos requests that reuse session cookies.

### Risks and Edge Cases
Apple auth flows frequently set cookies with the same names or empty values to clear state. If merge semantics regress, stale 2FA cookies can remain, new auth cookies may not replace old values, and serialized cookie strings can become invalid. These tests do not cover domain/path-sensitive duplicate cookies; merge is name-only.

### Test Signals
The tests are small but high signal for a previous class of session persistence bugs. They should run quickly and deterministically in unit test suites.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/session_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/srp.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/api/srp.go

### Purpose
`srp.go` implements the client side of Apple's SRP-6a authentication variant for iCloud sign-in. It provides the RFC 5054 2048-bit group parameters, generates the client secret/public value, derives Apple's password key, computes the shared secret, and produces M1/M2 proofs used by `Session.SignIn`.

### Important APIs, Types, and Functions
Package variables define `srpN`, `srpG`, `srpNLenBytes`, and `srpHashFunc`. `srpClient` stores secret `a`, public `A`, multiplier `k`, and output proofs/session key `M1`, `M2`, and `K`. `newSRPClient` uses `crypto/rand` to create a 32-byte secret and compute `A = g^a mod N`. `getABytes` returns `A` padded to the group length. `processChallenge` validates server `B`, computes `x`, `u`, shared secret `S`, key `K`, and proofs.

Helper functions include `derivePassword`, `padToN`, `srpHash`, `hashToInt`, `getMultiplier`, `calculateX`, `calculateU`, `calculateS`, `calculateK`, `calculateM1`, and `calculateM2`.

### Control Flow
The SRP flow begins by generating `a` and `A`. After Apple returns salt, iteration count, protocol, `B`, and challenge `c`, `derivePassword` hashes the password with SHA-256 and runs PBKDF2-SHA256 using either raw SHA-256 bytes (`s2k`) or hex-encoded SHA-256 (`s2k_fo`). `processChallenge` rejects invalid `B <= 0` or `B >= N`, computes `x = H(salt | H(":" | derivedKey))`, computes `u = H(pad(A) | pad(B))`, rejects zero `u`, computes `S = (B - k*g^x)^(a + u*x) mod N`, hashes it into `K`, and builds Apple-style proofs.

### State and Persistence
The SRP client is ephemeral and holds sensitive derived values only in memory during sign-in. No data is persisted by this file. The Apple ID is lowercased by `Client.New` before it reaches the proof calculation path, because Apple's proof expects that client-side normalization.

### Dependencies and Integration Points
This file depends on Go crypto packages (`crypto/rand`, `crypto/sha256`, `crypto/pbkdf2`), `math/big`, and `hash`. It is used only by `session.go`'s `SignIn` flow.

### Risks and Edge Cases
Cryptographic correctness is critical. Padding must be exactly 256 bytes; username omission in `calculateX` is Apple-specific; `calculateM1` uses `H(g) XOR H(N)` with padded `g`; and unsupported password protocols must error rather than guessing. The implementation validates `B` and `u`, but it does not expose server proof verification beyond calculating `M2` for Apple protocol exchange.

### Test Signals
`srp_test.go` extensively validates padding, multiplier determinism, password derivation variants, `x`, `u`, `K`, `M1`, `M2`, random client generation, deterministic challenge processing with a server-side key check, invalid `B` rejection, group constants, and SHA-256 hashing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/srp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/srp_test.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/api/srp_test.go

### Purpose
`srp_test.go` is a pure unit test suite for Apple's SRP implementation. It validates arithmetic helpers, password derivation variants, proof construction, challenge processing, invalid inputs, and group/hash constants without network access.

### Important APIs, Types, and Functions
The tests cover `padToN`, `getMultiplier`, `derivePassword`, `calculateX`, `calculateU`, `calculateK`, `calculateM1`, `calculateM2`, `newSRPClient`, `srpClient.processChallenge`, `srpN`, `srpG`, `srpNLenBytes`, and `srpHash`.

### Control Flow
Most tests compute expected values manually using the same primitives and compare them to helper outputs. `TestProcessChallenge` uses fixed client and server secrets to build a valid synthetic `B = (k*v + g^b) mod N`, runs `processChallenge`, checks that `M1`, `M2`, and `K` are populated and deterministic, then independently computes the server-side shared secret `(A * v^u)^b mod N` to prove both sides derive the same key.

### State and Persistence
The tests use fixed in-memory values for deterministic checks except `TestNewSRPClient`, which expects two generated clients to have different random secrets. No persistent state is involved.

### Dependencies and Integration Points
The suite uses `crypto/sha256`, `encoding/hex`, `math/big`, `testing`, and `testify`. It protects the `Session.SignIn` authentication path, because any mismatch in these helpers would break iCloud login.

### Risks and Edge Cases Covered
Coverage includes zero padding, values already the size of `N`, deterministic multiplier and proof construction, distinct `s2k` vs `s2k_fo` PBKDF2 inputs, unsupported protocol errors, invalid server `B=0` and `B=N`, known group prefix, generator value, and hash compatibility with standard SHA-256. The tests are arithmetic-heavy but do not use live Apple vectors, so compatibility still depends on Apple's protocol not changing.

### Test Signals
This is high-value cryptographic regression coverage. Failing tests should be treated as authentication-breaking unless the Apple SRP protocol or implementation requirements have intentionally changed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/srp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/icloud.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/icloud.go

### Purpose
`icloud.go` is the rclone registration and configuration entry point for the combined iCloud Drive and Photos backend. It registers the `iclouddrive` remote, exposes a `service` option that routes to Drive or Photos, drives the interactive SRP/2FA/SMS config state machine, persists auth credentials, creates authenticated API clients, and clears auth/cache state on disconnect.

### Important APIs, Types, and Functions
Constants define `configAuthSession`, `configService`, `serviceDrive`, and `servicePhotos`. `configAuthState` and `smsPhone` represent temporary auth state that must survive multi-step config prompts. Helpers include `saveAuthSession`, `loadAuthSession`, `restoreAuthSession`, `resumeConfigClient`, `saveAuthCredentials`, `triggerSMSFlow`, `newICloudClient`, `disconnectClient`, and `NewServiceFs`. `Config` is the main rclone config state machine. `init` registers backend metadata, options, and read-only Photos metadata keys (`width`, `height`, `added-time`, `favorite`, `hidden`).

### Control Flow
On initial config, `Config` requires Apple ID, reveals the obscured password, ignores stale trust token/cookies, creates a fresh API client, and calls `Authenticate`. If Apple requires 2FA, it fetches auth state. Accounts without trusted devices but with trusted phone numbers are sent into SMS flow. Otherwise it explicitly requests a trusted-device push, stores auth session state, and prompts for a 2FA code or `sms`.

In `2fa_do`, the saved session is restored to avoid another SRP round trip. A literal `sms` branches to phone selection or SMS trigger; otherwise the code is validated via trusted-device flow and credentials are saved. `2fa_sms_select` parses the selected `ID_mode`, requests the SMS code, saves state, and prompts for the code. `2fa_sms_*` validates the SMS code, trusts the session, saves trust token/cookies, clears temporary state, and clears cache.

### State and Persistence
Temporary auth session state is JSON-marshaled, base64-encoded, and stored in config key `_auth_session`. Long-lived credentials are `configTrustToken` and `configCookies`. `saveAuthCredentials` clears `_auth_session` and removes the remote cache through `api.ClearCacheDir`. `newICloudClient` installs a callback that persists updated cookies when the API session changes. `disconnectClient` clears trust token, cookies, auth-session state, and deletes the API cache dir.

### Dependencies and Integration Points
This file integrates rclone `fs.Register`, `configmap`, `configstruct`, `obscure`, `encoder`, and the iCloud API package. `NewServiceFs` routes to `NewFs` for Drive and `NewFsPhotos` for Photos, both defined elsewhere in the backend. It scopes PCS cookie acquisition through `newICloudClient` by passing `WsDrive` or `WsPhotos` from the service-specific constructors.

### Risks and Edge Cases
The config flow relies on Apple private auth behavior and may need updates when Apple changes 2FA push semantics; comments note iOS 26.4+ requiring explicit push notification. Losing `_auth_session` between config steps forces reconfiguration. SMS state encodes phone ID/mode in the state string and must parse cleanly. Fresh config intentionally ignores old trust tokens/cookies to force reauthentication, while normal backend creation requires a trust token and returns a reconnect hint if missing.

### Test Signals
No direct tests for `icloud.go` are in this subset. Its behavior is indirectly protected by `session.go`/`session_test.go` for cookie/auth primitives and by service-specific backend tests elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/icloud.go -->

# subset-b-009741 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/crypt/crypt.go -->
# sources/user-network-fs/rclone/backend/crypt/crypt.go

Purpose: Implements rclone's `crypt` backend as a transparent wrapper over another `fs.Fs`, encrypting/decrypting path names and optionally file data while forwarding most storage operations to the wrapped remote. It registers config options for remote selection, filename mode/encoding, data encryption, passwords, metadata, strict-name handling, server-side operations, and suffix behavior.

Important APIs, types, and functions: `Options` is the config contract; `Fs` wraps the underlying remote plus `Cipher`; `Object` wraps encrypted objects; `ObjectInfo` rewrites source metadata for uploads. `NewCipher`, `newCipherForConfig`, and `NewFs` construct the cipher and wrapped remote. Listing uses `add`, `addDir`, `encryptEntries`, `ListP`, and `ListR`. Upload/read paths run through `put`, `Put`, `PutStream`, `PutUnchecked`, `Object.Open`, and `Object.Update`. Optional integrations include `Copy`, `Move`, `DirMove`, `MkdirMetadata`, `DirSetModTime`, `MergeDirs`, `PublicLink`, `ChangeNotify`, `Command`, `UserInfo`, `Disconnect`, and `Shutdown`.

Control flow: `NewFs` reveals obscured passwords, creates a `Cipher`, rejects self-wrapping remotes, encrypts the requested root as a file first and then as a directory, then masks wrapper features with the underlying remote. All incoming cleartext paths are encrypted before underlying operations; all returned object and directory remotes are decrypted before surfacing. Uploads encrypt the data stream unless `no_data_encryption` is set, optionally tee encrypted bytes through a hasher for destination integrity, and wrap object info so encrypted size/name/hash metadata is passed downstream. Reads convert cleartext seek/range options into encrypted file ranges using `DecryptDataSeek`.

State and persistence behavior: The backend persists no data itself; durable state lives in the wrapped remote as encrypted names and encrypted file content. Runtime state includes the cipher, wrapper pointer, masked feature table, config options, and nonce-derived upload metadata. Cache pinning keeps the wrapped remote alive until finalization. `ComputeHash` can reopen encrypted content to recover the nonce and recompute encrypted-source hashes.

Dependencies and integration points: Depends on rclone core `fs`, `cache`, `configstruct`, `obscure`, `fspath`, `hash`, `accounting`, and `list`; cryptographic primitives live in sibling `cipher.go`. It integrates with nearly every optional rclone wrapper interface while intentionally suppressing hashes and MIME type leakage at the crypt layer.

Risks: Path translation bugs can expose, hide, or duplicate files; strict name mode changes list failures from logged skips to hard errors. Server-side copy/move only works for crypt-wrapped objects and can be dangerous across incompatible configs. No-data-encryption still encrypts names but changes size/hash semantics. MIME type is deliberately hidden, which can surprise downstream tooling. Range reads and nonce/hash recomputation depend on cipher internals.

Test signals: `crypt_test.go` runs fstests for standard base32/base64/base32768, off, obfuscate, and no-data-obfuscate modes. `crypt_internal_test.go` adds ObjectInfo hash/size and encrypted-hash recomputation checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/crypt/crypt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/crypt/crypt_internal_test.go -->
# sources/user-network-fs/rclone/backend/crypt/crypt_internal_test.go

Purpose: Provides package-internal tests for `crypt.Fs` behavior that cannot be verified through the public fstests alone, especially encrypted `ObjectInfo` metadata and hash computation.

Important APIs, types, and functions: `makeTempLocalFs` creates and cleans a temporary local backend; `uploadFile` writes test objects; `testObjectInfo` validates `Fs.newObjectInfo`; `testComputeHash` validates `Fs.ComputeHash`; `(*Fs).InternalTest` plugs these checks into `fstests.Run`.

Control flow: Tests upload plaintext to a temporary local remote, encrypt equivalent data with the target crypt cipher to capture the expected nonce and encrypted bytes, then wrap both normal and `fs.OverrideRemote` object infos. `testComputeHash` uploads the same contents to local and crypt remotes, reads the nonce from the encrypted object via `ComputeHash`, and compares the recomputed encrypted hash with the underlying remote object's hash.

State and persistence behavior: Temporary local files are created per test and removed through `t.Cleanup`. The tests rely on crypt upload nonce state and the wrapped remote's hash support but do not mutate global configuration.

Dependencies and integration points: Uses rclone `fs`, `object`, `hash`, random data helpers, and testify. The `InternalTest` method is discovered by fstests as a backend-specific extension point.

Risks: Hash checks skip if the wrapped remote reports no hashes, so some backends only cover ObjectInfo behavior. The tests intentionally reach into unexported cipher/encrypter details, making them sensitive to crypt internals.

Test signals: Passing tests show encrypted source size is adjusted, remote names are encrypted, local encrypted hashes can be supplied for uploads, override wrappers are unwrapped, and `ComputeHash` matches the stored encrypted object hash.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/crypt/crypt_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/crypt/crypt_test.go -->
# sources/user-network-fs/rclone/backend/crypt/crypt_test.go

Purpose: Runs rclone's generic filesystem test suite against the crypt backend across the main filename/data encryption configurations.

Important APIs, types, and functions: `TestIntegration` uses an externally supplied `-remote`; `TestStandardBase32`, `TestStandardBase64`, `TestStandardBase32768`, `TestOff`, `TestObfuscate`, and `TestNoDataObfuscate` build temporary local crypt configs. Each invokes `fstests.Run` with `crypt.Object` as the nil object type and declares unsupported writer/MIME methods.

Control flow: If an explicit remote is configured, only `TestIntegration` runs. Otherwise each mode creates an `ExtraConfig` crypt remote pointing to a temp directory with an obscured password and mode-specific settings. Obfuscate tests skip on macOS because generated control-character filenames conflict with the platform.

State and persistence behavior: Tests write to temp directories under `os.TempDir`; fstests owns cleanup and lifecycle. Config is injected in-memory through `ExtraConfig`, avoiding permanent rclone config mutation.

Dependencies and integration points: Imports local, drive, and swift backends for test availability, plus `fstest`, `fstests`, and `obscure`. These tests exercise crypt through the public rclone backend interface rather than package internals.

Risks: Temporary directory names are shared by some mode tests, so failed cleanup can leave residue. Generic fstests provide broad behavioral coverage but do not directly assert ciphertext layout or every optional wrapper interface.

Test signals: Coverage confirms crypt can create, list, read, update, delete, and traverse data with standard encodings, off mode, obfuscation, and no-data-encryption mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/crypt/crypt_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/crypt/pkcs7/pkcs7.go -->
# sources/user-network-fs/rclone/backend/crypt/pkcs7/pkcs7.go

Purpose: Implements PKCS#7 block padding and unpadding for cryptographic buffers whose lengths must be multiples of a block size.

Important APIs, types, and functions: Exported errors distinguish malformed padding cases. `Pad(n, buf)` appends padding bytes to the supplied slice. `Unpad(n, buf)` validates and strips padding, returning a subslice or a specific error.

Control flow: Both functions panic for invalid block sizes `n <= 1` or `n >= 256`. `Pad` computes `n - len(buf)%n`, appends that byte value repeatedly, and verifies the result is aligned. `Unpad` checks empty input, block alignment, padding length bounds, zero padding, and equality of all trailing padding bytes before slicing.

State and persistence behavior: There is no persistent state. `Pad` mutates/appends to the caller-provided slice, while `Unpad` returns a view into the original slice.

Dependencies and integration points: Depends only on `errors`. It is intended for use by crypt filename/data cipher code where exact padding validation matters for authentication and decode errors.

Risks: Callers must copy input before `Pad` if they need immutability. Panics on invalid block sizes are deliberate and should be kept away from user-controlled parameters. `Unpad` exposes detailed error reasons, which is useful internally but should not be converted into a padding oracle in network-facing contexts.

Test signals: `pkcs7_test.go` covers normal pad/unpad round trips, malformed padding variants, and invalid block-size panics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/crypt/pkcs7/pkcs7.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/crypt/pkcs7/pkcs7_test.go -->
# sources/user-network-fs/rclone/backend/crypt/pkcs7/pkcs7_test.go

Purpose: Verifies PKCS#7 padding behavior for successful round trips, malformed padding, and invalid block size panics.

Important APIs, types, and functions: `TestPad` enumerates expected padded byte strings for block sizes 8 and 16 and immediately unpads them. `TestUnpad` enumerates error cases for empty, unaligned, too-long, zero-length, and inconsistent padding.

Control flow: Table-driven assertions compare exact padded strings, then assert `Unpad` recovers the original bytes. Error tests assert both the exact exported error value and a nil result. Panic assertions cover `n == 1` and `n == 256` for both functions.

State and persistence behavior: The tests use in-memory byte slices only and have no external state.

Dependencies and integration points: Uses `testing`, `fmt`, and testify assertions. It gives low-level confidence to any crypt code consuming `pkcs7.Pad` and `pkcs7.Unpad`.

Risks: Tests focus on fixed examples rather than randomized block sizes or all possible malformed suffixes. They intentionally assert exact error values, so changing error taxonomy is a compatibility-visible change.

Test signals: Passing tests indicate padding bytes, full-block padding, round-trip slicing, error classification, and panic boundaries match expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/crypt/pkcs7/pkcs7_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/api/dataversetypes.go -->
# sources/user-network-fs/rclone/backend/doi/api/dataversetypes.go

Purpose: Defines the JSON response shapes consumed from Dataverse dataset APIs by the DOI backend.

Important APIs, types, and functions: `DataverseDatasetResponse` wraps status and data. `DataverseDataset` exposes `LatestVersion`. `DataverseDatasetVersion` carries `LastUpdateTime` and `Files`. `DataverseFile` combines a directory label with `DataverseDataFile` metadata. `DataverseDataFile` stores IDs, filenames, content type, file sizes, original-file fields, and MD5.

Control flow: This file has no executable control flow; fields are populated by `rest.CallJSON` in `dataverseProvider.ListEntries`.

State and persistence behavior: The structs are transient API decode models. Values are later converted into DOI `Object` instances and cached by the provider.

Dependencies and integration points: It is in package `api` and is imported by `backend/doi/dataverse.go`. JSON tags are the integration contract with Dataverse.

Risks: Schema drift or missing fields can produce zero values, affecting object size, names, MIME type, MD5, and modtime. Original-file fields override display name, size, and content type when present, so model accuracy matters for tabular or transformed files.

Test signals: No direct tests exist; Dataverse behavior is indirectly guarded only if provider integration tests are added.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/api/dataversetypes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/api/inveniotypes.go -->
# sources/user-network-fs/rclone/backend/doi/api/inveniotypes.go

Purpose: Defines JSON models for InvenioRDM and Zenodo record/file APIs used by the DOI backend.

Important APIs, types, and functions: `InvenioRecordResponse` and `InvenioRecordResponseLinks` expose the canonical record `self` URL. `InvenioFilesResponse` contains file `Entries`. Each `InvenioFilesResponseEntry` carries key, checksum, size, updated timestamp, MIME type, and content link.

Control flow: There is no logic; `invenio.go` and `zenodo.go` decode these structs from API responses.

State and persistence behavior: Instances are transient decode results and are converted into cached DOI `Object` metadata.

Dependencies and integration points: Package `api` is imported by DOI provider implementations. The checksum is later trimmed for `md5:` prefixes, and timestamp strings are parsed as RFC3339.

Risks: The checksum field may contain algorithms other than MD5; current provider code simply trims `md5:` and returns the result as MD5. Bad timestamps degrade to the unset time with a log message.

Test signals: `doi_internal_test.go` uses these types in a mock Zenodo server and verifies listing, size, content, MD5, and MIME type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/api/inveniotypes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/api/types.go -->
# sources/user-network-fs/rclone/backend/doi/api/types.go

Purpose: Defines generic DOI resolver API models for handle resolution.

Important APIs, types, and functions: `DoiResolverResponse` contains response code, handle, and values. `DoiResolverResponseValue` models individual handle records. `DoiResolverResponseValueData` carries format and an arbitrary `Value`.

Control flow: No executable logic. `resolveDoiURL` decodes this structure and searches for a value with type `URL` and data format `string`.

State and persistence behavior: Values are transient resolver responses. The resolved URL drives provider detection and endpoint setup, but the response itself is not stored.

Dependencies and integration points: Used by `doi.go` and DOI resolver tests. The `any` value requires runtime type assertion after JSON decoding.

Risks: Resolver responses with non-string URL data, missing URL values, or non-success response codes are rejected. If multiple URL values exist, the current loop keeps the last matching value.

Test signals: Mock resolver tests in `doi_internal_test.go` exercise successful URL resolution and path construction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/dataverse.go -->
# sources/user-network-fs/rclone/backend/doi/dataverse.go

Purpose: Implements DOI provider support for Dataverse-hosted datasets.

Important APIs, types, and functions: `activateDataverse` recognizes URLs with `persistentId`; `resolveDataverseEndpoint` builds `/api/datasets/:persistentId/`; `dataverseProvider.ListEntries` converts Dataverse dataset files into DOI `Object`s; `newDataverseProvider` wires the provider into `Fs`.

Control flow: Detection extracts `persistentId` from the resolved DOI URL. Listing first checks the backend cache, then GETs the dataset endpoint through the rclone REST client and pacer. It parses dataset `LastUpdateTime`, builds content URLs under `/api/access/datafile/{id}?format=original`, and maps each file to object remote, size, MD5, and content type, preferring original-file fields when present.

State and persistence behavior: The provider caches a slice of value-copied `Object` metadata under key `files`, then returns fresh pointers on later calls. Persistent data remains remote at Dataverse content URLs.

Dependencies and integration points: Depends on DOI `Fs`, `rest`, Dataverse API models, `path`, `url`, `time`, and rclone logging/pacer behavior. It satisfies the `doiProvider` interface consumed by `doi.go`.

Risks: A single dataset update time is used for all files. Cache invalidation is coarse and only refreshed by rebuilding or changing the session. Directory labels and original file names are joined with `path.Join`, which can normalize empty or unusual path elements. Missing MD5/content type fields surface as empty values.

Test signals: There are no Dataverse-specific tests in the listed files; behavior is analogous to the mocked Zenodo provider flow.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/dataverse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/doi.go -->
# sources/user-network-fs/rclone/backend/doi/doi.go

Purpose: Provides a read-only rclone backend for datasets addressed by DOI, resolving the DOI through a handle resolver, detecting the hosting provider, listing dataset files, and exposing HTTP downloads as rclone objects.

Important APIs, types, and functions: `Provider`, `Options`, `Fs`, `Object`, and `doiProvider` define the backend surface. `parseDoi`, `resolveDoiURL`, `resolveEndpoint`, `httpConnection`, `NewFs`, `List`, `NewObject`, `Object.Open`, `Object.Hash`, `Object.MimeType`, `Command`, and `ShowMetadata` implement core behavior.

Control flow: `NewFs` trims root, parses config, normalizes DOI input, creates an HTTP client, REST client, pacer, metadata cache, and feature set, then calls `httpConnection`. Endpoint resolution calls the DOI resolver, honors explicit provider selection, or auto-detects Dataverse, Zenodo, and Invenio. The selected provider lists all entries; if the configured root is a file, `NewFs` returns `fs.ErrorIsFile` with root adjusted to the parent. `List` filters provider entries under the current root and synthesizes directory entries. `Open` performs HTTP GET with range options and handles a non-compliant redirect by manually following `Location`.

State and persistence behavior: The backend is read-only; `Mkdir`, `Rmdir`, `Put`, `PutStream`, `Remove`, `Update`, and `SetModTime` all reject changes. Runtime state includes provider, endpoint URL, REST client root, pacer, config, and provider metadata cache.

Dependencies and integration points: Uses rclone `fs`, config, HTTP, REST, pacer, cache, hash, and provider files `dataverse.go`, `invenio.go`, and `zenodo.go`. It exposes backend commands `metadata` and `set`; `set` mutates the live options and reconnects.

Risks: Hashes advertise MD5 and return provider-supplied strings, which may be empty or malformed. Cache staleness can persist after provider-side changes. Auto-detection performs network calls and can misclassify generic Invenio-like pages. Read-only errors are plain backend errors rather than capability masking. Manual redirect handling may miss multi-hop or unusual redirect semantics.

Test signals: Internal tests cover DOI parsing and a mocked Zenodo resolver/list/download flow; `doi_test.go` wires the backend to generic fstests for a configured `TestDoi:` remote.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/doi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/doi_internal_test.go -->
# sources/user-network-fs/rclone/backend/doi/doi_internal_test.go

Purpose: Unit-tests DOI parsing and exercises the DOI backend against mocked resolver and Zenodo/Invenio-style APIs.

Important APIs, types, and functions: `TestParseDoi` covers accepted DOI forms. `prepareMockDoiResolverServer` emits handle API responses. `prepareMockZenodoServer` serves record metadata, file listings, and file contents. `md5Sum` helps populate API checksums. `TestZenodoRemote` verifies listing, object lookup, hash, open, and MIME type.

Control flow: The mock resolver returns a URL for the DOI. The mock Zenodo server returns a canonical record `self` URL, file entries with content URLs, and content bytes. `TestZenodoRemote` constructs `NewFs` with explicit provider `zenodo`, lists entries, sorts them, asserts object metadata, opens both files, and compares downloaded bytes.

State and persistence behavior: All state is in httptest servers and in-memory maps. Servers are closed with `t.Cleanup`. The backend's metadata cache is naturally exercised by repeated list/object operations.

Dependencies and integration points: Uses `httptest`, `encoding/json`, rclone `configmap`, `hash`, `fs.MimeTyper`, and the DOI API model structs. It tests network-facing provider code without external services.

Risks: The parse test comment for `dx.doi.org` uses `https://dxdoi.org/...`, which still passes because the hostname suffix is `doi.org`; this may obscure intended coverage. The mock checksum omits the `md5:` prefix commonly seen in Invenio responses, so trimming logic is only partially covered.

Test signals: Passing tests show DOI normalization, resolver requests with `index=1`, Zenodo endpoint derivation, provider file listing, MD5 propagation, MIME type propagation, and file download behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/doi_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/doi_test.go -->
# sources/user-network-fs/rclone/backend/doi/doi_test.go

Purpose: Hooks the DOI backend into rclone's generic integration test harness.

Important APIs, types, and functions: `TestIntegration` invokes `fstests.Run` with `RemoteName: "TestDoi:"` and `NilObject: (*Object)(nil)`.

Control flow: The test expects a configured `TestDoi:` remote and then lets fstests exercise standard filesystem behavior for the read-only DOI backend.

State and persistence behavior: Any state depends on the configured remote and provider. The backend itself remains read-only during these tests, so mutation tests should observe read-only errors.

Dependencies and integration points: Uses `fstest/fstests` and the package-local `Object` type. This is the external-service complement to `doi_internal_test.go`.

Risks: Without a configured remote, the test harness may skip or fail depending on fstests configuration. Generic tests may include mutation expectations that need backend read-only handling to be accepted.

Test signals: When configured, this provides broad compatibility coverage for listing, object reads, metadata, and expected unsupported write operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/doi_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/invenio.go -->
# sources/user-network-fs/rclone/backend/doi/invenio.go

Purpose: Implements DOI provider detection and file listing for InvenioRDM-compatible repositories, also reused for Zenodo after endpoint resolution.

Important APIs, types, and functions: `activateInvenio`, `resolveInvenioEndpoint`, `checkInvenioAPIURL`, `invenioProvider.ListEntries`, and `newInvenioProvider` are the main surfaces. `invenioRecordRegex` extracts record IDs from resolved URLs.

Control flow: Endpoint resolution first GETs the resolved DOI URL, scans `Link` headers for a linkset API URL, validates it with `checkInvenioAPIURL`, and falls back to guessing `/api/records/{id}` from the final request URL. Listing checks the provider cache, GETs `{endpoint}/files`, parses RFC3339 update times, strips an `md5:` checksum prefix, and creates DOI `Object` entries using content links.

State and persistence behavior: File metadata is cached under `files` as value copies, then returned as new pointers. No remote data is mutated.

Dependencies and integration points: Uses `parseLinkHeader` from `link_header.go`, Invenio API models, rclone REST/pacer/retry logic, and DOI `Fs`. Zenodo uses this provider after resolving the canonical Zenodo endpoint.

Risks: Link header parsing is simple and comma-splits without full RFC quoting support. Endpoint guessing depends on URL path shape. Cache staleness is not time-bounded. Non-MD5 checksums may be misreported as MD5 after prefix trimming if provider behavior changes.

Test signals: Mock Zenodo tests cover the shared Invenio file-listing structure; link header parsing has its own unit test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/invenio.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/link_header.go -->
# sources/user-network-fs/rclone/backend/doi/link_header.go

Purpose: Provides a small parser for HTTP `Link` headers used to discover Invenio API/linkset endpoints.

Important APIs, types, and functions: `headerLink` stores href, rel, type, and extra attributes. `parseLinkHeader` parses a comma-separated header into links. `parseLink` parses a single link-value. `parseKeyValue` parses `key=value` attributes and removes surrounding double quotes.

Control flow: `parseLinkHeader` splits on commas, trims spaces, delegates to `parseLink`, and drops invalid entries. `parseLink` splits on semicolons, requires the first part to be `<...>`, and maps lowercased `rel` and `type` specially while preserving other keys in `Extras`.

State and persistence behavior: Stateless string parsing only.

Dependencies and integration points: Uses regexp and strings. `resolveInvenioEndpoint` consumes parsed links looking for `rel=linkset` and `type=application/linkset+json`.

Risks: The parser is intentionally lightweight and does not handle commas or semicolons inside quoted attribute values. Regexes are greedy, so unusual angle-bracket content could parse broadly. Attribute key casing for extras is preserved, while rel/type matching is lowercased.

Test signals: `link_header_internal_test.go` covers a single link with quoted attributes and a multi-link pagination-style header.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/link_header.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/link_header_internal_test.go -->
# sources/user-network-fs/rclone/backend/doi/link_header_internal_test.go

Purpose: Unit-tests the DOI backend's lightweight `Link` header parser.

Important APIs, types, and functions: `TestParseLinkHeader` compares parsed output with expected `headerLink` values for a linkset header and a multi-link pagination header.

Control flow: The test first verifies whitespace-tolerant parsing of href, `rel`, `type`, and empty extras. It then parses four comma-separated links and asserts the exact ordered slice.

State and persistence behavior: In-memory parsing only, no external state.

Dependencies and integration points: Uses testify assertions. These cases support Invenio endpoint discovery, where linkset headers are preferred over URL guessing.

Risks: Tests do not cover malformed entries, unquoted values, extras, mixed-case keys, or quoted commas/semicolons. The exact-slice assertion documents current order-preserving behavior.

Test signals: Passing tests show basic RFC-style link headers are parsed into the shape expected by `resolveInvenioEndpoint`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/link_header_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/zenodo.go -->
# sources/user-network-fs/rclone/backend/doi/zenodo.go

Purpose: Resolves Zenodo DOIs to the canonical Zenodo API record endpoint used by the shared Invenio provider.

Important APIs, types, and functions: `zenodoRecordRegex` extracts the record ID from DOI strings containing `zenodo.`. `resolveZenodoEndpoint` constructs `/api/records/{recordID}`, fetches it, and returns the `Links.Self` API URL with provider `Zenodo`.

Control flow: The resolver derives a record ID from the DOI, resolves an API URL relative to the DOI target, GETs JSON through the pacer, parses the canonical `self` link, and returns it as the endpoint.

State and persistence behavior: Stateless endpoint resolution only; the resulting endpoint is stored later in `Fs`.

Dependencies and integration points: Uses DOI API `InvenioRecordResponse`, rclone REST/pacer/retry logic, and the main DOI provider selection in `doi.go`. Listing is performed by `newInvenioProvider`.

Risks: DOI parsing depends on the `zenodo.` substring and will reject concept DOI or alternate Zenodo DOI formats if they do not match. Empty or malformed `self` links can parse into unusable endpoints unless caught by downstream calls.

Test signals: `TestZenodoRemote` covers successful record ID extraction, API record lookup, endpoint self-link handling, and subsequent listing/opening through the shared provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/doi/zenodo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drime/api/types.go -->
# sources/user-network-fs/rclone/backend/drime/api/types.go

Purpose: Defines Drime API request and response models for listing, metadata, CRUD operations, uploads, multipart upload lifecycle, and quota.

Important APIs, types, and functions: `Item` is the central file/folder metadata type, with `User` and `Permissions` nested details. Listing and upload types include `Listing`, `UploadResponse`, `CreateFolderRequest/Response`, `DeleteRequest/Response`, `UpdateItemRequest/Response`, `MoveRequest/Response`, `CopyRequest/Response`, multipart create/sign/complete/entry/abort types, and `SpaceUsageResponse`. `Error` implements Go's `error` interface.

Control flow: This file is mostly data definitions. `Error.Error` formats Drime API error messages. All other structs are populated or marshaled by `drime.go` REST calls.

State and persistence behavior: Structs are transient API payloads. Persistent state lives in Drime; runtime state is copied into `Object` metadata and `drimeChunkWriter` upload state.

Dependencies and integration points: Uses `encoding/json` for `json.Number`, `fmt`, and `time`. JSON tags are the contract between `drime.go` and the Drime API.

Risks: Many fields are `any`, so type safety is limited for rarely used metadata. Numeric IDs rely on `json.Number.String()`. API schema drift can break listing, uploads, moves, or quota without compile-time detection.

Test signals: No direct unit tests exist; `drime_test.go` runs integration fstests against a real configured Drime remote.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drime/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drime/drime.go -->
# sources/user-network-fs/rclone/backend/drime/drime.go

Purpose: Implements the rclone backend for Drime cloud storage, including directory caching, listing, upload/download, delete, move/copy, quota, MIME metadata, and multipart chunked uploads.

Important APIs, types, and functions: `Options`, `Fs`, and `Object` define backend state. Construction and configuration flow through `init`, `NewFs`, `checkUploadChunkSize`, `setUploadChunkSize`, and `setUploadCutoff`. Metadata/listing uses `dircache` plus `readMetaDataForPath`, `getItem`, `FindLeaf`, `CreateDir`, `listAll`, `itemToDirEntry`, and `List`. Mutations use `Put`, `PutUnchecked`, `Object.Update`, `deleteObject`, `purgeCheck`, `Rmdir`, `Purge`, `patch`, `rename`, `move`, `moveTo`, `Move`, `DirMove`, `copy`, `copyTo`, and `Copy`. Multipart upload is implemented by `OpenChunkWriter`, `drimeChunkWriter.WriteChunk`, `Close`, and `Abort`. Object methods expose `Open`, `Remove`, `ID`, `ParentID`, and `MimeType`.

Control flow: `NewFs` parses config, validates chunk size, creates an authenticated REST client, installs an error handler, initializes `dircache`, and detects whether the root is a file. Listing resolves a directory ID, pages `/drive/file-entries`, decodes provider names, filters files/folders, and caches folder IDs. Uploads update existing objects or create unchecked objects; small files POST `/uploads`, while unknown or cutoff-exceeding sizes use rclone multipart orchestration. Multipart upload creates an upload, signs each part URL, PUTs chunks without bearer auth, completes the upload, then creates a Drime file entry. Moves and copies are server-side API operations with rename handling; directory moves poll children after rename to work around eventual consistency.

State and persistence behavior: Persistent data lives in Drime. Runtime state includes access token headers, workspace/root options, dircache path-to-ID mappings, pacer retry state, object metadata, and active multipart state including upload ID, key, completed parts, and byte count. Updates delete the previous object only after the replacement upload succeeds.

Dependencies and integration points: Uses rclone `fs`, `dircache`, `rest`, `pacer`, `multipart`, `chunksize`, `encoder`, and Drime API models. It advertises optional interfaces for purge, put stream, copy, move, dir move, cache flush, quota, chunk writer, object IDs, parent IDs, and MIME type.

Risks: API behavior quirks are encoded directly, including POST plus `X-HTTP-Method-Override` for updates and eventual-consistency polling after directory rename. Hashes are unsupported despite the API exposing a hash field. `copy` assumes at least one returned entry. Upload replacement semantics can leave duplicates if delete fails after successful upload. Multipart memory and maximum stream size depend on chunk size and concurrency.

Test signals: `drime_test.go` runs generic fstests against `TestDrime:` with chunked-upload configuration and exposes setters so fstests can vary chunk size/cutoff. There are no local mocks for error handling or multipart edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drime/drime.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drime/drime_test.go -->
# sources/user-network-fs/rclone/backend/drime/drime_test.go

Purpose: Integrates the Drime backend with rclone's generic filesystem test suite and exposes test-only upload tuning hooks.

Important APIs, types, and functions: `TestIntegration` calls `fstests.Run` for `TestDrime:` with `(*Object)(nil)` and minimum chunk size. `SetUploadChunkSize` and `SetUploadCutoff` forward to unexported setters. Interface assertions confirm the backend satisfies fstests upload tuning interfaces.

Control flow: The integration test uses the configured Drime remote and enables chunked upload testing with `minChunkSize`. Fstests can temporarily adjust chunk size and cutoff to force multipart paths.

State and persistence behavior: Test state lives on the configured Drime account and is managed by fstests. Setter methods mutate the live `Fs` options for the duration of tests.

Dependencies and integration points: Uses rclone `fs` size suffixes and `fstests`. It directly supports coverage of `OpenChunkWriter`, small uploads, and regular object operations in `drime.go`.

Risks: Requires real credentials/configuration, so CI coverage may be limited. There are no mocked tests for API error bodies, pagination, move/copy edge cases, or multipart abort behavior.

Test signals: When configured, passing fstests demonstrate listing, upload/download, deletion, directory handling, metadata basics, and chunked upload compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/drime/drime_test.go -->

# subset-b-008209 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/update-notifier_test.go -->
# sources/object-store/minio/cmd/update-notifier_test.go

## Purpose
Tests the update-notification message builder that tells operators their MinIO binary is older than the latest release. The file is focused on formatting behavior rather than network or update mechanics.

## Important APIs, Control Flow, and Dependencies
`TestPrepareUpdateMessage` calls `prepareUpdateMessage(downloadURL, older)` across durations from seconds to years. It verifies suppression for empty URLs, zero or negative age, and inclusion of two colorized lines for valid update notices. It depends on `internal/color` helpers and string containment checks, so it intentionally validates user-facing text fragments rather than exact full terminal layout.

## State, Persistence, and Integration
The test has no persistent state. It integrates with update notifier code outside this subset through `prepareUpdateMessage`, and with terminal-color conventions through `color.YellowBold` and `color.CyanBold`.

## Risks and Test Signals
The table covers pluralization and coarse duration rounding for seconds, minutes, hours, days, weeks, months, and years. It does not test terminal width handling or ANSI-disabled output. A regression in message wording will fail these tests because expected substrings are literal.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/update-notifier_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/update.go -->
# sources/object-store/minio/cmd/update.go

## Purpose
Implements MinIO binary update discovery, download, verification, and commit support, plus environment detection used in update URLs and User-Agent construction.

## Important APIs, Types, and Functions
Release helpers convert between official `Version` RFC3339 timestamps and `RELEASE.<timestamp>` tags: `minioVersionToReleaseTime`, `releaseTimeToReleaseTag`, `releaseTagToReleaseTime`, and `releaseInfoToReleaseTime`. `GetCurrentReleaseTime` falls back to the executable mod time for source/non-official builds. Platform detectors include `IsDocker`, `IsDCOS`, `IsKubernetes`, `IsBOSH`, `IsSourceBuild`, and `IsPCFTile`; `getHelmVersion` parses Kubernetes pod label files.

`getUserAgent` builds the update client identity with OS, arch, MinIO version/tag/commit, deployment environment, package metadata, and CPU information. `downloadReleaseURL`, `parseReleaseData`, and `getLatestReleaseTime` fetch and parse checksum metadata. `getDownloadURL` maps deployment context to either docs, container pull command, or binary URL. `downloadBinary` streams an update binary and zstd-compresses a copy while retaining the raw bytes. `verifyBinary` validates permissions, checksum, and minisign signature through `selfupdate`; `commitBinary` completes the staged update. `updateInProgress` is an atomic guard shared by verify and commit.

## Control Flow
Update checking fetches a checksum file with an update-specific transport, parses a hex checksum and release-info token, converts the release tag to time, and chooses an operator-facing download target. Applying an update downloads the candidate binary, verifies checksum/signature through `selfupdate.PrepareAndCheckBinary`, then later commits through `selfupdate.CommitBinary`.

## State, Persistence, and Dependencies
Persistent effects occur only through executable self-update staging/commit and executable metadata reads. Network dependencies include MinIO release URLs, minisign files, proxy/root CA settings, and internode dial settings. Environment variables shape behavior, especially `MINIO_UPDATE_MINISIGN_PUBKEY` and deployment indicators. Errors are normalized to `AdminError` codes for admin API callers.

## Risks and Test Signals
Main risks are incorrect release parsing, environment misclassification, unbounded binary buffering in memory, signature URL mutation, and update serialization via `updateInProgress`. Tests in `update_test.go` cover parsing, download URL selection, release-data fetch, and helm label parsing, but do not exercise `verifyBinary`, `commitBinary`, or large binary memory behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/update_test.go -->
# sources/object-store/minio/cmd/update_test.go

## Purpose
Validates release-tag parsing, deployment-specific update URL selection, Helm label parsing, release metadata download, and release metadata parsing for `update.go`.

## Important APIs and Control Flow
`TestMinioVersionToReleaseTime` distinguishes official RFC3339 versions from release tags and development builds. `TestReleaseTagToNFromTimeConversion` checks conversion between UTC time and release tags, including accepted hotfix suffixes and invalid prefixes. `TestDownloadURL` verifies binary URLs, container pull commands, Kubernetes docs, and Mesos docs based on runtime and environment variables. Later tests create temporary Helm label data, run local `httptest` servers, call `downloadReleaseURL`, and feed malformed and valid strings into `parseReleaseData`.

## State, Persistence, and Dependencies
The file mutates process environment through `t.Setenv`, writes a temporary label file for Helm parsing, and uses local HTTP test servers. It does not touch the real updater or network.

## Risks and Test Signals
The tests provide good coverage for release metadata parsing and user-facing URL decisions. They do not verify minisign, self-update filesystem behavior, User-Agent CPU/package fields, concurrency on `updateInProgress`, or zstd download buffering.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/update_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/url_test.go -->
# sources/object-store/minio/cmd/url_test.go

## Purpose
Benchmarks allocation/performance tradeoffs for retrieving query parameters from HTTP requests.

## Important APIs and Control Flow
`BenchmarkURLQueryForm` parses the request form once with `req.ParseForm()` and repeatedly reads `req.Form.Get("uploadId")` in parallel. `BenchmarkURLQuery` repeatedly calls `req.URL.Query().Get("uploadId")` in parallel without pre-parsing.

## State, Persistence, and Dependencies
No persistent state. The dependency surface is only the standard `net/http` request parser and Go benchmark framework.

## Risks and Test Signals
This is performance-only coverage; no correctness assertion is made. It is useful as a signal when changing request parsing in hot S3 paths, but it will not fail normal tests unless benchmarks are explicitly run.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/url_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/user-provider-utils.go -->
# sources/object-store/minio/cmd/user-provider-utils.go

## Purpose
Maps access keys, credentials, and claims to MinIO user-provider identities for built-in IAM, LDAP, OpenID, certificate, and custom providers.

## Important APIs and Control Flow
`getUserWithProvider` validates or normalizes a username depending on `madmin.BuiltinProvider` or `madmin.LDAPProvider`. Built-in validation checks `globalIAMSys.GetUser`; LDAP validation requires LDAP user-system mode and resolves usernames to normalized DNs through `globalIAMSys.LDAPConfig.GetValidatedDNForUsername`. Without validation, LDAP inputs must still parse as DNs.

`guessUserProvider` classifies credentials: regular non-temp/non-service accounts are built-in; LDAP claims imply LDAP; subject claims imply OpenID unless the parent user contains a provider prefix separator, in which case that prefix is returned. `populateProviderInfoFromClaims` attaches provider-specific information to `madmin.InfoAccessKeyResp`. OpenID info is resolved by matching role ARN claims against configured OpenID providers, then extracting display/user ID claims configured for that provider. LDAP info exposes the LDAP username claim.

## State, Persistence, and Dependencies
The file reads global IAM and server config state but does not persist changes. It depends on `madmin` provider constants, `auth.Credentials`, LDAP/OpenID config stores, and claim constants.

## Risks and Test Signals
Risks include stale global IAM config, ambiguous parent-user separators, missing claims, and returning `errNoSuchUser` versus `errIAMActionNotAllowed` in provider mismatch cases. No direct tests in this subset cover this file.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/user-provider-utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/utils.go -->
# sources/object-store/minio/cmd/utils.go

## Purpose
Provides broad shared command-layer helpers: object error normalization, request/path parsing, checksum readers, S3 limits, profiling, HTTP/TLS transports, audit context, directory object encoding, OpenID test login flow, and small generic utilities.

## Important APIs, Types, and Functions
`ErrorRespToObjectError` translates `minio.ErrorResponse` and network failures into object-layer errors such as quorum errors, bucket/object not found, invalid range, access denied, SHA mismatch, and multipart errors. Path helpers include `request2BucketObjectName`, `path2BucketObjectWithBasePath`, `path2BucketObject`, `trimLeadingSlash`, `unescapePath`, and best-effort unescape variants. `validateLengthAndChecksum` wraps `r.Body` with checksum verification for `Content-MD5` or newer content checksum headers.

S3 constants and checks define object, part-size, and part-ID limits. Profiler support is implemented through `profilerWrapper`, `startProfiler`, `getProfileData`, and `setDefaultProfilerRates`, covering CPU, fgprof CPU/IO, heap, block, mutex, threads, goroutines, and trace profiles. Transport helpers create internode, cloud-backend, and remote-target HTTP transports with global DNS, root CA, TLS cipher, TCP, and timeout settings. Context and logging helpers include `newContext`, `updateReqContext`, `auditLogInternal`, and `dumpRequest`. Object helpers include `GenETag`, `ToS3ETag`, `encodeDirObject`, `decodeDirObject`, `isDirObject`, and `filterStorageClass`.

## Control Flow
Most helpers are leaf functions called throughout S3/admin/storage paths. Profiling start creates temporary files or records baseline profiles, then returns a stopper that reads profile data and cleans temporary directories. `newContext` extracts mux bucket/object vars and request metadata into `logger.ReqInfo`. `MockOpenIDTestUserInteraction` performs a multi-step Dex/OIDC login flow and exchanges an auth code for an ID token.

## State, Persistence, and Dependencies
Persistent effects are limited to temporary profile files and audit log emission. Global state is heavily referenced: DNS cache, root CAs, TCP options, IAM config, profiler registry, endpoint layout, deployment ID, Veeam flag, and request trace/loggers. Dependencies include MinIO internals, `madmin`, `minio-go`, OIDC/OAuth2, fgprof, pprof/trace, and Go HTTP/TLS packages.

## Risks and Test Signals
Risk is high because this file is shared infrastructure. Error mapping omissions can leak backend-specific errors, checksum wrapping changes request body semantics, profiler code toggles global runtime profile rates, and transport helpers determine TLS/HTTP2 posture. Tests in `utils_test.go` cover S3 size limits, path splitting, invalid profiler type, request dumping, ETag conversion, ceiling math, ignored errors, REST query expansion, longest common prefix, and MinIO mode selection; many helpers remain untested in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/utils_test.go -->
# sources/object-store/minio/cmd/utils_test.go

## Purpose
Provides unit coverage for selected shared helpers in `utils.go`.

## Important APIs and Control Flow
The tests cover `isMaxObjectSize`, `isMinAllowedPartSize`, and `isMaxPartID`; bucket/object path extraction across edge-case slash layouts; invalid profiler type handling; a local `checkURL` helper; JSON request dumping with escaped percent handling; `ToS3ETag`; `ceilFrac`; `IsErrIgnored`; `restQueries`; `lcp` prefix mode; and `getMinioMode` under global erasure flags.

## State, Persistence, and Dependencies
The file mutates package globals `globalIsDistErasure` and `globalIsErasure` without explicit restoration, so test ordering assumptions matter. It constructs HTTP requests but does not use network or disk.

## Risks and Test Signals
Coverage is useful for utility edge cases, especially URL/request formatting and S3 boundary constants. It does not cover checksum wrapping, TLS/transport helpers, profiler success paths, audit logging, OpenID test interaction, Veeam storage-class filtering, or error-response mapping.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/veeam-sos-api.go -->
# sources/object-store/minio/cmd/veeam-sos-api.go

## Purpose
Implements Veeam Smart Object Storage API virtual objects for MinIO, exposing `system.xml` and `capacity.xml` without storing them as normal objects.

## Important APIs, Types, and Functions
`systemInfo`, `capacityInfo`, and `apiEndpoints` model XML responses. Constants define the hidden SOSAPI object paths and Veeam User-Agent substring. `isVeeamSOSAPIObject` recognizes the virtual object names. `isVeeamClient` checks request info for Veeam clients. `veeamSOSAPIHeadObject` delegates to `veeamSOSAPIGetObject` and returns only object metadata. `veeamSOSAPIGetObject` constructs XML for system capabilities or capacity information, computes an ETag, applies optional HTTP ranges, and wraps a reader with `NewGetObjectReaderFromReader`.

## Control Flow
For `system.xml`, the code returns protocol version, MinIO release model name, capacity capability, and recommended 4096 KB block size. For `capacity.xml`, it obtains bucket quota and bucket usage; hard quota takes precedence, otherwise total usable backend capacity is computed from `StorageInfo`. Available space is capacity minus used bytes.

## State, Persistence, and Dependencies
The objects are virtual and not persisted. Capacity reads depend on `newObjectLayerFn`, `globalBucketQuotaSys`, `GetTotalUsableCapacity`, and current backend info. `globalVeeamForceSC` is read from `_MINIO_VEEAM_FORCE_SC` and used by `utils.go` storage-class filtering.

## Risks and Test Signals
Risks include stale or expensive capacity calculations, negative available values when usage exceeds quota/capacity, range-handling mistakes, and User-Agent substring fragility. No direct tests in this subset exercise the Veeam XML paths.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/veeam-sos-api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/version_test.go -->
# sources/object-store/minio/cmd/version_test.go

## Purpose
Checks that the package-level `Version` format can be parsed as an official MinIO RFC3339 timestamp.

## Important APIs and Control Flow
`TestVersion` assigns `Version = "2017-05-07T06:37:49Z"` and verifies `time.Parse(time.RFC3339, Version)` succeeds.

## State, Persistence, and Dependencies
The test mutates the global `Version` variable and does not restore it. It uses only Go's `time` package.

## Risks and Test Signals
This is a narrow format smoke test. It does not validate build-time version injection, release tag conversion, or interactions with `GetCurrentReleaseTime`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/warm-backend-azure.go -->
# sources/object-store/minio/cmd/warm-backend-azure.go

## Purpose
Implements the warm-tier `WarmBackend` adapter for Azure Blob Storage.

## Important APIs, Types, and Functions
`warmBackendAzure` stores an `azblob.Client`, bucket/container, prefix, and access tier. `tier` maps configured storage class to an Azure `blob.AccessTier`. `getDest` applies the tier prefix. `PutWithMeta` converts metadata to Azure pointer values and uploads with `UploadStream`, concurrency 4, optional access tier, and metadata. `Get` rejects negative offsets and uses `DownloadStream` with an HTTP range. `Remove` deletes a blob. `InUse` lists one blob with the configured prefix. `azureConf.Validate` enforces account name, exactly one auth mechanism, and bucket. `NewClient` supports service-principal or shared-key auth. `azureToObjectError` and `azureCodesToObjectError` translate Azure response codes/statuses to MinIO object errors.

## Control Flow
Instantiation validates config, derives a default endpoint when missing, creates the Azure client, and returns a prefixed backend. Runtime calls translate object names through `getDest`, execute SDK operations, and normalize SDK errors.

## State, Persistence, and Dependencies
State is remote Azure blob data and metadata. Dependencies are Azure identity/blob SDKs, `madmin.TierAzure`, global slash separator, and MinIO object error types. The backend does not use `remoteVersionID` on get/remove beyond returning upload version IDs.

## Risks and Test Signals
Risks include mismatched prefix handling, unsupported storage class silently producing nil tier, auth ambiguity, range semantics when length is zero, and incomplete error-code mapping. No direct tests in this subset cover Azure backend behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/warm-backend-azure.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/warm-backend-gcs.go -->
# sources/object-store/minio/cmd/warm-backend-gcs.go

## Purpose
Implements the warm-tier `WarmBackend` adapter for Google Cloud Storage.

## Important APIs, Types, and Functions
`warmBackendGCS` stores a GCS client, bucket, prefix, and storage class. `PutWithMeta` creates an object writer, assigns storage class and metadata, copies data to the writer, and closes it. `Get` uses `ReadCompressed(true)` and `NewRangeReader` to preserve compressed object bytes. `Remove` deletes the object. `InUse` lists one object with prefix and delimiter. `newWarmBackendGCS` validates credentials and bucket, builds a scoped storage client with a MinIO tier User-Agent, and returns the backend. `gcsToObjectError` maps GCS plain errors and `googleapi.Error` reasons/messages into MinIO object-layer errors.

## Control Flow
Object keys are prefixed through `getDest`. Writes stream into GCS, reads honor byte ranges and avoid GCS decompressive transcoding, and deletes/listing translate SDK errors into MinIO errors.

## State, Persistence, and Dependencies
State is remote GCS object data and metadata. Dependencies include `cloud.google.com/go/storage`, Google API errors, credential JSON from `madmin.TierGCS`, and internal `xioutil.Copy`.

## Risks and Test Signals
`PutWithMeta` contains two consecutive `xioutil.Copy(w, data)` calls before closing. For normal readers the second copy reads EOF, but for unusual readers it can block, duplicate data, or surface a second read error; this deserves scrutiny. GCS version IDs are explicitly unsupported and `remoteVersionID` is a no-op. No direct tests in this subset cover GCS behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/warm-backend-gcs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/warm-backend-minio.go -->
# sources/object-store/minio/cmd/warm-backend-minio.go

## Purpose
Specializes the S3 warm-tier backend for MinIO targets, including MinIO-specific multipart sizing and trailing-header support.

## Important APIs and Control Flow
`warmBackendMinIO` embeds `warmBackendS3` and satisfies `WarmBackend`. `optimalPartSize` chooses a multipart part size from object size using MinIO constants: 5 TiB maximum object size, 10,000 parts, 5 GiB maximum part size, and 128 MiB configured minimum. Unknown size `-1` is treated as 5 TiB. `PutWithMeta` calculates part size and calls `minio.Client.PutObject` with storage class, explicit part size, disabled content SHA256, and user metadata. `newWarmBackendMinIO` validates static credentials and bucket, parses endpoint, creates a static V4 client with global remote transport and trailing headers, sets app info, and embeds the S3 backend.

## State, Persistence, and Dependencies
State is remote MinIO object data and version IDs. Dependencies include `minio-go`, static credentials, `madmin.TierMinIO`, global remote target transport, and inherited S3 `Get`, `Remove`, and `InUse` methods.

## Risks and Test Signals
Risks include part-size calculation for boundary/unknown sizes, 5 TiB limit errors, credential validation, and behavior differences from generic S3 due to disabled SHA256 and trailing headers. No direct tests in this subset cover this file.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/warm-backend-minio.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/warm-backend-s3.go -->
# sources/object-store/minio/cmd/warm-backend-s3.go

## Purpose
Implements the warm-tier `WarmBackend` adapter for generic S3-compatible storage.

## Important APIs, Types, and Functions
`warmBackendS3` holds a `minio.Client`, `minio.Core`, bucket, prefix, and storage class. `ToObjectError` delegates error mapping to `ErrorRespToObjectError`. `PutWithMeta` uploads with content MD5, storage class, and user metadata. `Get` applies optional version ID and byte range, then uses `Core.GetObject` to preserve range options. `Remove` applies optional version ID. `InUse` lists one object/common prefix under the tier prefix. `newWarmBackendS3` validates mutually exclusive authentication modes and bucket, supports IAM role, web identity role, and static V4 credentials, builds a client with global remote transport and region, and sets tier app info.

## Control Flow
Config validation rejects partial static credentials, partial web-identity settings, AWS role mixed with other credentials, and empty bucket. Runtime object operations prefix object names and convert S3 errors into local object errors.

## State, Persistence, and Dependencies
State is remote S3 object data, metadata, and version IDs. Dependencies include `minio-go`, AWS IAM/web identity credential providers, global HTTP transport, `madmin.TierS3`, and MinIO object error types.

## Risks and Test Signals
Risks include auth-mode ambiguity, endpoint parsing that uses only host/scheme, range handling only when length is positive, versioned deletes, and prefix/listing semantics in `InUse`. No direct tests in this subset cover S3 warm backend behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/warm-backend-s3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/warm-backend.go -->
# sources/object-store/minio/cmd/warm-backend.go

## Purpose
Defines the common remote warm-tier backend interface and validates tier permissions by probing put/get/delete operations.

## Important APIs, Types, and Functions
`WarmBackendGetOpts` describes byte ranges. `WarmBackend` requires `Put`, `PutWithMeta`, `Get`, `Remove`, and `InUse`. `checkWarmBackend` writes `probeobject`, reads it, drains the body, and removes it, translating failures into backend-down, bucket-not-found, invalid-credential, or operation-specific `tierPermErr` values. `tierOp` and `tierPermErr` label failed GET/PUT/DELETE probes. `remoteVersionID` abstracts provider-specific version identifiers. `newWarmBackend` selects an implementation from `madmin.TierConfig` for S3, Azure, GCS, or MinIO, converts construction errors to invalid config, and optionally probes.

## Control Flow
Tier creation is type-dispatched, logs invalid construction errors, then optionally performs the active probe. Probe errors preserve `BackendDown`, special-case common credential/bucket errors on get, and wrap other operation failures with the failed permission.

## State, Persistence, and Dependencies
The probe has real remote side effects: it creates and deletes a fixed object named `probeobject` in the configured tier. Dependencies include all provider constructors, `madmin` tier config, tier logging, and object-error classifiers.

## Risks and Test Signals
Risks include probe object collisions, partial cleanup after failed get/delete, remote version ID handling differences, and broad conversion of constructor failures to `errTierInvalidConfig`. No direct tests in this subset cover warm backend probing.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/warm-backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-disk-id-check.go -->
# sources/object-store/minio/cmd/xl-storage-disk-id-check.go

## Purpose
Wraps `xlStorage` with disk-ID validation, deadline enforcement, health monitoring, metrics, and storage tracing to detect drive swaps, stale disks, hung disks, and storage API behavior.

## Important APIs, Types, and Functions
`storageMetric` enumerates tracked storage operations. `xlStorageDiskIDCheck` holds write/delete counters, error counters, per-operation call counts and last-minute latencies, the expected disk ID, wrapped storage, health tracker, metrics cache, and monitor context. `lockedLastMinuteLatency` accumulates per-second latency/size samples locklessly before folding into `lastMinuteLatency`. `newXLStorageDiskIDCheck` initializes counters from storage attributes, sets empty disk ID, starts optional writable monitoring, and prepares metric accumulators.

The wrapper implements many storage methods: volume creation/list/stat/delete, directory listing, file read/write/append/create/rename, object metadata read/write/update, version deletion, bulk deletion, part reads, scanner, abandoned-data cleanup, and disk info. Each method usually calls `TrackDiskHealth`, delegates to `xlStorage`, adds deadlines through `xioutil.WithDeadline` or `DeadlineWorker`, and records metrics with `done`.

`checkDiskStale` compares cached disk ID with the current `format.json` disk ID and returns `errDiskNotFound` on mismatch. `DiskInfo` can return cached metrics in no-op mode and reports faulty status for admin/prometheus. `updateStorageMetrics` increments call/error counters, updates latency, and emits storage traces. `diskHealthTracker`, `TrackDiskHealth`, `monitorDiskWritable`, and `monitorDiskStatus` mark disks faulty when operations hang/fail and bring them back after write/read/delete succeeds. `diskHealthReader` and `diskHealthWriter` update health from low-level streaming I/O.

## Control Flow
Every tracked operation first rejects canceled contexts, existing faulty status, and stale disk IDs. Non-recursive tracking installs a context marker to avoid deadlocks and increments the waiting count. On completion, nil or EOF errors count as success and update `lastSuccess`; errors such as faulty disk and deadline exceeded update availability/timeout counters. The monitor periodically writes a sentinel buffer into `minioMetaTmpBucket`, reads it back, and if timeout/faulty errors occur, marks the disk offline and starts a recovery loop that retries write/read/delete until successful.

## State, Persistence, and Dependencies
Persistent state includes disk `format.json` ID, storage write/delete attributes, and temporary healthcheck objects in the MinIO metadata temp bucket. In-memory state includes atomics for counters, cached disk ID, disk health, metrics cache, and context lifecycle. Dependencies include `xlStorage`, global drive config, global tracing, scanner idle mode, logger, `madmin` trace/metrics types, grid byte buffers, and internal deadline/cache helpers.

## Risks and Test Signals
This is operationally sensitive. Risks include false-positive disk offline decisions under slow I/O, stale disk-ID reads, leaked waiting counters, monitor temp-object cleanup failures, recursive tracking bypasses, and inconsistent write/delete accounting. `ReadParts` indexes `partMetaPaths[0]` without local empty-slice protection. No direct tests in this subset cover disk health tracking or disk-ID mismatch behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-disk-id-check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-errors.go -->
# sources/object-store/minio/cmd/xl-storage-errors.go

## Purpose
Provides small OS/syscall error classifiers used by XL storage and other disk-facing code.

## Important APIs and Control Flow
Functions classify errors with `errors.Is` or `errors.As`: no space (`ENOSPC`), invalid arg (`EINVAL`), I/O (`EIO`), is dir (`EISDIR`), not dir (`ENOTDIR`), name too long (`ENAMETOOLONG`), too many symlinks (`ELOOP`), not empty (`ENOTEMPTY`, Solaris `EEXIST`, Windows `ERROR_DIR_NOT_EMPTY`), path not found, invalid Windows handle, cross-device (`EXDEV`), too many files (`ENFILE`/`EMFILE`), not-exist, permission/read-only, and exist.

## State, Persistence, and Dependencies
No state or persistence. Dependencies are Go `errors`, `os`, `runtime`, `syscall`, and MinIO's `globalWindowsOSName`.

## Risks and Test Signals
The main risk is platform-specific errno interpretation, especially Windows and Solaris branches. `xl-storage-errors_test.go` covers several common classifiers but not all exported helpers.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-errors_test.go -->
# sources/object-store/minio/cmd/xl-storage-errors_test.go

## Purpose
Tests selected syscall error classifiers from `xl-storage-errors.go`.

## Important APIs and Control Flow
`TestSysErrors` creates `os.PathError` values wrapping `ENAMETOOLONG`, `ENOTDIR`, and either Unix `ENOTEMPTY` or Windows `0x91`, then verifies the corresponding helper returns true. On Windows it also checks `isSysErrPathNotFound` for errno `0x03`.

## State, Persistence, and Dependencies
No persistence. The test branches on `runtime.GOOS` and depends on syscall errno constants.

## Risks and Test Signals
The file confirms key path classification behavior but does not test no-space, invalid-arg, I/O, symlink loop, invalid handle, cross-device, too-many-files, permission, or existence helpers.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-errors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-utils.go -->
# sources/object-store/minio/cmd/xl-storage-format-utils.go

## Purpose
Bridges raw xl.meta bytes to `FileInfo`/`FileInfoVersions` and provides deterministic weak hashing helpers used for metadata signatures.

## Important APIs and Control Flow
`getFileInfoVersions` calls `getAllFileInfoVersions`, then optionally partitions tier free versions into `FreeVersions` while keeping normal versions in `Versions`, and updates `NumVersions`. `getAllFileInfoVersions` handles indexed meta v2 directly when present, otherwise loads/converts `xlMetaV2`; an empty version list is represented as a synthetic latest delete marker with `timeSentinel1970`. `getFileInfo` similarly handles indexed and non-indexed metadata, optional inline data extraction, null version handling, legacy `DataDir` fallback, and empty-version delete marker synthesis.

`hashDeterministicString` and `hashDeterministicBytes` produce order-independent weak hashes by xoring xxh3 hashes of keys and values with fixed salts.

## State, Persistence, and Dependencies
No direct persistence, but the functions decode persisted xl.meta data and inline data. Dependencies include `xlMetaV2`, indexed meta helpers, `FileInfo`, lifecycle tier-free-version semantics, and `zeebo/xxh3`.

## Risks and Test Signals
Risks include incorrect partitioning of free versions, synthetic delete marker semantics, inline data lookup mismatches, and relying on weak non-cryptographic hashes for signatures. `xl-storage-format-utils_test.go` covers deterministic hash stability/sensitivity and free-version partitioning.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-utils_test.go -->
# sources/object-store/minio/cmd/xl-storage-format-utils_test.go

## Purpose
Tests deterministic metadata hashing and `getFileInfoVersions` handling of regular versus tier-free versions.

## Important APIs and Control Flow
`Test_hashDeterministicString` verifies that map iteration order does not alter the hash over 100 clear/repopulate cycles, and that added, deleted, modified, enlarged, or key/value-flipped entries change the hash. `TestGetFileInfoVersions` builds an `xlMetaV2` with multiple versions, transitions one version, creates a free version, serializes metadata, then verifies filtering mode separates free versions and inclusive mode returns all version IDs in expected modtime order.

## State, Persistence, and Dependencies
The test serializes in-memory xl metadata through `xl.AppendTo`; it does not write disk files. It depends on lifecycle transition constants, `mustGetUUID`, and `xlMetaV2` behavior.

## Risks and Test Signals
The tests strongly signal expected version ordering and free-version partition behavior. They do not cover indexed meta v2 input, inline data extraction, synthetic empty-version delete markers, or byte-map hashing.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v1.go -->
# sources/object-store/minio/cmd/xl-storage-format-v1.go

## Purpose
Defines legacy XL metadata v1 structures, validation, JSON checksum handling, conversion to `FileInfo`, and disk-independent metadata signatures.

## Important APIs, Types, and Functions
Constants identify legacy `xl.json`, metadata versions `1.0.0`/`1.0.1`, and format `xl`. `xlMetaV1Object` models legacy object metadata: version/format, stat, erasure info, release, metadata map, parts, and dummy version/data-dir fields for legacy use. `StatInfo`, `ErasureInfo`, `ObjectPartInfo`, `ChecksumInfo`, and `BitrotAlgorithm` are core persisted metadata types. `ErasureInfo.Equal` compares algorithm, data/parity, block size, and distribution while intentionally ignoring disk index and checksums. `ChecksumInfo.MarshalJSON` and `UnmarshalJSON` convert `part.N`, algorithm names, and hex hashes, validating bitrot algorithm availability. `ToFileInfo` validates and converts v1 metadata into `FileInfo` with `XLV1` and one version. `Signature` shallow-copies metadata, zeroes disk-local fields, hashes metadata deterministically, msgp-serializes, and folds xxhash into four bytes.

## State, Persistence, and Dependencies
These types describe persisted XL metadata and messagepack/JSON encodings. Dependencies include bitrot algorithms, erasure coding constants, `FileInfo`, deterministic hash helpers, msgp generation, jsoniter, and xxhash.

## Risks and Test Signals
Risks include legacy compatibility, signature instability if generated encoding changes, weak four-byte signature collisions, and checksum JSON accepting malformed names/hashes only through parser errors. Generated tests cover msgp round trips for these types, but not all semantic validation paths.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v1.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v1_gen.go -->
# sources/object-store/minio/cmd/xl-storage-format-v1_gen.go

## Purpose
Generated `msgp` serialization code for legacy XL metadata v1-related types.

## Important APIs and Control Flow
The file implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `BitrotAlgorithm`, `ChecksumInfo`, `ErasureInfo`, `ObjectPartInfo`, `StatInfo`, `checksumInfoJSON`, and `xlMetaV1Object`. It uses map or scalar encodings depending on type, skips unknown fields, wraps errors with field paths, reuses existing slices/maps where possible, clears maps before refill, and resets omitted optional fields such as `ObjectPartInfo.Index`, `Checksums`, and `Error` when absent.

## State, Persistence, and Dependencies
This code is pure serialization but defines on-disk/wire compatibility for legacy metadata. It depends on `github.com/tinylib/msgp/msgp` and the struct layouts in `xl-storage-format-v1.go`.

## Risks and Test Signals
Generated code should not be hand-edited. Compatibility risk is high because field names/tags and omitted-field clearing affect persisted metadata decoding. `xl-storage-format-v1_gen_test.go` provides round-trip and benchmark coverage for each generated type, but semantic validation remains in non-generated code.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v1_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v1_gen_test.go -->
# sources/object-store/minio/cmd/xl-storage-format-v1_gen_test.go

## Purpose
Generated tests and benchmarks for msgp serialization of legacy XL metadata v1 types.

## Important APIs and Control Flow
For each generated type, tests marshal to bytes, unmarshal back, assert no leftover bytes, verify `msgp.Skip` consumes the object, encode/decode through `msgp.Writer`/`Reader`, and warn if `Msgsize` underestimates encoded length. Benchmarks measure marshal, append-style marshal, unmarshal, encode, and decode paths.

## State, Persistence, and Dependencies
No persistence; all data is zero-value in-memory fixtures. Dependencies are `bytes`, `testing`, and `tinylib/msgp`.

## Risks and Test Signals
The tests catch basic generated-code corruption and size-estimate issues. They do not cover non-zero field combinations, backward compatibility fixtures, malformed encodings, or semantic validity of decoded metadata.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v1_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v2-legacy.go -->
# sources/object-store/minio/cmd/xl-storage-format-v2-legacy.go

## Purpose
Maintains backward compatibility for older xl.meta v2 header and version encodings.

## Important APIs and Control Flow
`xlMetaV2VersionHeader.unmarshalV` dispatches header decoding for version 1, version 2, current header version, or errors on unknown versions. `unmarshalV1` decodes a never-released four-field array: version ID, mod time, type, and flags. `xlMetaV2Version.unmarshalV` rejects metadata versions newer than supported, clears stale `ObjectV2.PartIndices`, decodes current msgp format, normalizes pre-v2 delete-marker replication timestamps to UTC, and nils `ObjectV2.PartETags` when all entries are empty. `xlMetaV2VersionHeaderV2` decodes the released pre-EcN/EcM five-field header from bytes or streaming reader.

## State, Persistence, and Dependencies
The file decodes persisted legacy xl.meta v2 data. Dependencies include current xl.meta v2 structs/constants, `VersionType`, `xlFlags`, replication metadata keys, `time`, and `tinylib/msgp`.

## Risks and Test Signals
Risks include losing compatibility with old metadata, timestamp normalization altering replication behavior, and stale slice contents leaking across reused structs. No direct tests in this subset target these legacy decoding branches.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v2-legacy.go -->

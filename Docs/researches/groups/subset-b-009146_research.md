# subset-b-009146 research

Grouped research report for Kopia repository blob storage backends, blob wrappers, compression, repository connection/cache helpers, and committed content index/read-manager files. Each section preserves the exact source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/s3/s3_storage.go -->
# sources/sync-backup/kopia/repo/blob/s3/s3_storage.go

Purpose: implements Kopia's `blob.Storage` provider for S3-compatible object stores using `minio-go`, including object reads, writes, metadata, listing, deletion, retention extension, TLS customization, credentials, and repository-local storage-class configuration.

Important APIs/types/functions: `s3Storage` embeds `Options` and `blob.DefaultProviderImplementation` and owns a `*minio.Client` plus optional `StorageConfig`. Public storage methods are `GetBlob`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `ExtendBlobRetention`, `ListBlobs`, `ConnectionInfo`, `String`, and `DisplayName`. Constructors are `New`, `newStorage`, and `newStorageWithCredentials`; `getCustomTransport` controls TLS verification and Root CA support; `translateError` maps provider errors to blob-layer sentinels.

Control flow: `New` builds the raw storage, optionally wraps it for point-in-time behavior, then returns a retrying wrapper. Reads set S3 byte ranges for partial and zero-length reads, stream from `GetObject`, and validate exact length. Writes reject unsupported `DoNotRecreate` and `SetModTime`, derive per-prefix storage class, optionally set S3 Object Lock retention, upload with multipart disabled and MD5 enabled, and then read back modtime when requested. Startup builds static/env/IAM or STS-assume-role credentials, creates a MinIO client, and loads `.storageconfig` if present.

State and persistence behavior: user data is stored as S3 objects named `Prefix + blobID`; `.storageconfig` is hidden from normal listing. S3 server timestamps and version IDs become metadata where available. Retention uses provider object-lock state, and deletes are idempotent when the object is absent.

Dependencies/integration: integrates with `blob.AddSupportedStorage("s3", Options{}, New)`, `retrying`, `maybePointInTimeStore`, MinIO S3 APIs, Kopia gather buffers, clock abstraction for retention, and blob sentinel errors consumed by higher repository layers.

Risks and edge cases: S3 error messages are partly string-matched for expired tokens. Zero-length range handling uses a fake range and skips reading. `PutObject` has a special EOF/empty-stream path. Object lock requires valid retention mode and provider support; MD5 behavior matters for locked AWS buckets. TLS options can intentionally disable verification, so callers must treat that as a security-sensitive configuration.

Test signals: `s3_storage_test.go` covers AWS, MinIO, STS, custom assume-role credentials, invalid credentials fast failure, token expiration, object lock/retention behavior, TLS bypass and provided root CAs, provider validation, connection-info round trips, and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/s3/s3_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/s3/s3_storage_config.go -->
# sources/sync-backup/kopia/repo/blob/s3/s3_storage_config.go

Purpose: defines the optional S3 `.storageconfig` JSON document that lets a bucket choose S3 storage classes by blob ID prefix.

Important APIs/types/functions: `ConfigName` is `.storageconfig`; `PrefixAndStorageClass` maps a `blob.ID` prefix to a storage-class string; `StorageConfig` holds `BlobOptions`; `Load` and `Save` JSON-decode/encode; `getStorageClassForBlobID` scans options in order and returns the first matching storage class.

Control flow: `newStorageWithCredentials` reads `ConfigName` through the normal `GetBlob` path during S3 storage startup. `putBlob` calls `storageConfig.getStorageClassForBlobID` for every uploaded blob and passes the result to MinIO `PutObjectOptions`.

State and persistence behavior: the config is persisted in the S3 bucket as a hidden Kopia blob and excluded from `ListBlobs`. Prefix ordering is significant because the first match wins; an empty result means default provider storage class.

Dependencies/integration: depends only on JSON, `io`, string prefix checks, and `blob.ID`; it is tightly integrated with `s3_storage.go` upload behavior.

Risks and edge cases: malformed JSON blocks opening the S3 storage. Overlapping prefixes require deliberate order. There is no validation of provider-specific storage-class names here, so invalid names fail later during upload.

Test signals: behavior is indirectly exercised by S3 storage startup and upload tests; direct tests should include malformed JSON, overlapping prefixes, and hidden-list filtering.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/s3/s3_storage_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/s3/s3_storage_test.go -->
# sources/sync-backup/kopia/repo/blob/s3/s3_storage_test.go

Purpose: integration-heavy test suite for the S3 provider across real AWS-compatible services, local MinIO, credential modes, TLS modes, object locking, and provider-validation checks.

Important APIs/types/functions: helpers include `startDockerMinioOrSkip`, `getProviderOptions`, `testStorage`, `testPutBlobWithInvalidRetention`, `createClient`, bucket helpers, `createMinioSessionToken`, and the `customProvider` that can force expired STS credentials. Test cases cover provider credentials from environment variables, AWS, AWS STS, MinIO, custom assume-role credentials, retention buckets, invalid credentials, TLS options, and MD5 requirements.

Control flow: most tests construct `Options`, create or discover a bucket, open storage through `New` or `newStorage`, assign a unique prefix, run `blobtesting.VerifyStorage`, assert connection-info round trips, and optionally run `providervalidation.ValidateProvider`. MinIO tests launch Docker containers with deterministic fake credentials. Token expiration toggles a custom provider from valid to expired and back to validate retry/refresh behavior.

State and persistence behavior: tests create temporary prefixes/buckets and clean old data through `blobtesting.CleanupOldData`. Retention tests use locked and unlocked AWS buckets and verify expected failures or successful locked writes. TLS tests generate local certificates or use badssl endpoints to verify custom transports.

Dependencies/integration: depends on Docker, MinIO, AWS/Wasabi environment variables, provider-validation helpers, Kopia blobtesting utilities, TLS test utilities, MinIO STS, and retrying wrappers.

Risks and edge cases: many tests are provider-gated and skipped without credentials or Linux/amd64 Docker support. Fast-failure tests guard against retry loops on bad credentials. TLS tests intentionally contact external badssl hosts and may be network-sensitive.

Test signals: success means the provider satisfies the blob contract under partial/full reads, writes, listing, deletion, connection serialization, STS token refresh, object lock requirements, and TLS customization.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/s3/s3_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/s3/s3_versioned.go -->
# sources/sync-backup/kopia/repo/blob/s3/s3_versioned.go

Purpose: adds version-listing support for S3 buckets with object versioning, exposing helpers used by point-in-time storage and version-aware tests.

Important APIs/types/functions: `versionMetadata` extends `blob.Metadata` with `IsLatest`, `IsDeleteMarker`, and provider `Version`. Methods are `IsVersioned`, `getBlobVersions`, `listBlobVersions`, private `list`, `toBlobID`, and `infoToVersionMetadata`.

Control flow: `IsVersioned` asks S3 for bucket versioning and returns `Enabled()`. `getBlobVersions` calls `list` with exact-key matching and converts no-result into `blob.ErrBlobNotFound`. `listBlobVersions` calls the same `list` with recursive prefix listing. `list` sets `WithVersions`, consumes MinIO object info from a channel, stops early on exact-key mismatch, converts each object to `versionMetadata`, and wraps callback/list errors.

State and persistence behavior: this file does not persist new state; it observes S3's versioned object history, including delete markers. Object names are stripped of the configured Kopia prefix when surfaced as blob IDs.

Dependencies/integration: used by `s3_pit.go`/point-in-time behavior and tests that inspect historical versions. It depends on MinIO `ListObjects` with `WithVersions` and the S3 provider's object-name mapping.

Risks and edge cases: exact-match mode relies on S3 listing order with prefix and stops when a different key appears. Delete markers are represented as zero-length metadata with marker flags. Provider versioning semantics can differ between AWS and S3-compatible services.

Test signals: `s3_versioned_test.go` verifies exact blob-version listing, prefix listing, delete-marker behavior, metadata conversion, historical-version reads, and version ordering across S3 and Wasabi versioned providers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/s3/s3_versioned.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/s3/s3_versioned_test.go -->
# sources/sync-backup/kopia/repo/blob/s3/s3_versioned_test.go

Purpose: validates S3 versioned-object helpers and point-in-time selection primitives against real versioned S3-compatible providers and deterministic in-memory version metadata.

Important APIs/types/functions: tests include `TestGetBlobVersions`, `TestGetDifferentBlobVersions`, `TestSingleBlobVersionsListPrefixes`, `TestListMultipleBlobPrefixes`, `TestGetBlobWithVersion`, `TestGetVersionMetadata`, `TestInfoToVersionMetadata`, `TestGetOlderThan*`, and `TestNewestAtUnlessDeleted*`. Helpers create random blob names/content, put versioned blobs, delete blobs to create delete markers, list versions, compare metadata, and clean all versions by `RemoveObjects`.

Control flow: provider-backed tests open a versioned store from environment credentials, write multiple versions for one or more blob IDs, list exact IDs and prefixes, delete current blobs, and verify historical versions remain accessible. Pure tests build ordered `versionMetadata` slices and check timestamp-based selection and delete-marker handling.

State and persistence behavior: versioned provider tests create multiple object versions under a unique test prefix, then explicitly remove every version and delete marker during cleanup. The suite models provider listing order as blob-name ascending and per-blob versions newest-first.

Dependencies/integration: depends on the S3 provider test credential map, MinIO object metadata, retry helpers, clock, gather buffers, and the point-in-time helpers in adjacent S3 files.

Risks and edge cases: tests depend on versioned buckets being configured correctly and on provider-specific timestamp/version metadata. Comparison intentionally ignores timestamps and `IsLatest` in some places because provider responses differ after newer writes.

Test signals: failures indicate broken exact/prefix version enumeration, inability to read a specific version, incorrect delete-marker handling, wrong conversion from provider object info, or point-in-time selection regressions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/s3/s3_versioned_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/sftp/sftp_options.go -->
# sources/sync-backup/kopia/repo/blob/sftp/sftp_options.go

Purpose: defines JSON-serializable configuration for the SFTP/SSH blob provider.

Important APIs/types/functions: `Options` includes remote `Path`, `Host`, `Port`, `Username`, password or key credentials, known-hosts file/data, external SSH command settings, embedded `sharded.Options`, and embedded `throttling.Limits`. `knownHostsFile` defaults to `$HOME/.ssh/known_hosts`.

Control flow: `sftp_storage.go` consumes these options to build either an internal SSH client or an external `ssh -s sftp` process, choose password versus public-key auth, validate absolute file paths, and construct sharded storage under `Path`.

State and persistence behavior: options can embed sensitive password/key/known-hosts data into connection info; `kopia:"sensitive"` tags mark password and key data. The remote path is the root for sharded `.f` blob files and `.shards` metadata.

Dependencies/integration: embeds sharding and throttling option structs, allowing the same provider config to influence directory layout and rate limits when higher layers wrap storage.

Risks and edge cases: relative key or known-hosts paths are rejected by storage setup. Embedded known-hosts data is later written to a temporary file because the SSH knownhosts parser accepts file paths only.

Test signals: `sftp_storage_test.go` checks absolute-path validation, embedded versus file-based credentials, password and key authentication, provider validation, and connection-info round trips.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/sftp/sftp_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/sftp/sftp_storage.go -->
# sources/sync-backup/kopia/repo/blob/sftp/sftp_storage.go

Purpose: implements a sharded Kopia `blob.Storage` provider on top of SFTP, supporting internal SSH, external SSH subprocesses, reconnects, capacity, atomic temp-file writes, host-key verification, and credential handling.

Important APIs/types/functions: `sftpStorage` embeds `sharded.Storage`; `sftpImpl` implements sharded `Impl`; `sftpConnection` wraps an SFTP client and close function. Core methods are `GetBlobFromPath`, `GetMetadataFromPath`, `PutBlobInPath`, `DeleteBlobInPath`, `ReadDir`, `GetCapacity`, `ConnectionInfo`, `DisplayName`, and `Close`. Setup helpers include `getHostKeyCallback`, `getSigner`, `createSSHConfig`, `getSFTPClientExternal`, `getSFTPClient`, and `New`.

Control flow: `New` creates a sharded storage, attaches a reconnecting connection manager, opens a connection without the caller's cancellation, ensures the remote root exists, and returns a retrying wrapper. Reads open files, stream whole or ranged content, seek for partial reads, and enforce exact length. Writes copy potentially fragmented `blob.Bytes` into a contiguous buffer, create a random temp file and missing directories, write/close it, atomically `PosixRename` it into place, and optionally set or return modtime.

State and persistence behavior: remote blobs are stored by the shared sharded layout beneath `Options.Path`; writes are staged as `*.tmp.<random>` and become visible only after rename. `.shards` may be persisted by the sharded layer. Active SSH/SFTP connection state is held in the reconnecter and closed by provider `Close`.

Dependencies/integration: integrates `github.com/pkg/sftp`, `x/crypto/ssh`, knownhosts, `internal/connection`, `dirutil`, `sharded`, and `retrying`. It maps not-found and connection-lost conditions to blob or reconnect semantics.

Risks and edge cases: error detection for not-exist includes string matching. External SSH argument splitting is simple whitespace splitting. Temporary known-hosts data touches disk briefly. `DoNotRecreate` and retention are unsupported. Atomicity depends on server support for `PosixRename`.

Test signals: SFTP tests launch an `atmoz/sftp` Docker server, validate key/password auth, embedded credentials, provider validation, canceled-constructor context reuse, invalid host fast failure, and rejection of relative key/known-hosts files.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/sftp/sftp_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/sftp/sftp_storage_test.go -->
# sources/sync-backup/kopia/repo/blob/sftp/sftp_storage_test.go

Purpose: integration tests for the SFTP provider against a Dockerized SSH/SFTP server and validation tests for credential path handling.

Important APIs/types/functions: helpers generate SSH keys, start `atmoz/sftp`, wait for a TCP banner, scan host keys, create SFTP storage with optional embedded credentials, clear blobs, and read credential files. Tests are `TestSFTPStorageValid`, `TestInvalidServerFailsFast`, `TestSFTPStorageRelativeKeyFile`, and `TestSFTPStorageRelativeKnownHostsFile`.

Control flow: the main test starts a container with one key-auth and one password-auth user, opens storage with a context that is canceled after construction, clears any blobs, runs the standard blob storage contract suite and provider validation, asserts connection-info round trips, and closes. It repeats with key material and known-hosts data embedded in options, then tests password auth.

State and persistence behavior: remote data lives under `/upload` or `/upload2` in the container and is deleted before and after validation. Temporary local credential directories and known-host files are cleaned by test cleanup handlers.

Dependencies/integration: requires Docker, `ssh-keygen`, `ssh-keyscan`, Linux/amd64 CI allowance, blobtesting, provider-validation, and the SFTP provider itself.

Risks and edge cases: container startup and key scanning are timing-sensitive. Invalid-host fast failure guards against reconnect/retry loops. Relative-path tests protect against unsafe config serialization and working-directory-dependent credentials.

Test signals: success confirms SFTP satisfies the shared blob contract under key/password auth, supports embedded connection info, rejects unsafe relative paths, and fails quickly on unreachable servers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/sftp/sftp_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/sharded/sharded.go -->
# sources/sync-backup/kopia/repo/blob/sharded/sharded.go

Purpose: provides reusable directory-sharding logic for providers whose blobs are files in a hierarchical namespace, such as filesystem, SFTP, and WebDAV.

Important APIs/types/functions: `Impl` is the provider-specific file API; `Storage` wraps an `Impl`, root path, sharding options, and cached `Parameters`; `CompleteBlobSuffix` marks complete blobs as `.f`. Methods implement the blob contract: `GetBlob`, `ListBlobs`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `GetShardedPathAndFilePath`, plus parameter loading through `getParameters`.

Control flow: operations first load or create `.shards`, compute shard directory and final file path, then delegate to the provider-specific `Impl`. Listing walks directories through a `parallelwork.Queue`, filters `.f` files, reconstructs full blob IDs from path prefix plus file name, applies caller prefix filtering, and streams metadata through a result channel while callback errors stop processing.

State and persistence behavior: sharding parameters are cached in memory and, if absent, initialized from defaults and best-effort written to `.shards`. Blob files are identified by `.f`; unrelated files and incomplete names are ignored during listing.

Dependencies/integration: used by providers that implement `Impl`; depends on `Parameters` from `sharded_parameters.go`, gather buffers for `.shards`, `parallelwork`, `errgroup`, and blob metadata/error types.

Risks and edge cases: if `.shards` exists but is malformed, operations fail until a valid parameters file is loaded or the file is removed. Listing concurrency must close channels correctly on callback failure. The default shard layout differs between create and open for legacy compatibility.

Test signals: `sharded_test.go` verifies legacy/latest default layouts, multiple shard specs, ignored foreign files, prefix listing under overrides, malformed `.shards`, and deep clone behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/sharded/sharded.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/sharded/sharded_options.go -->
# sources/sync-backup/kopia/repo/blob/sharded/sharded_options.go

Purpose: defines the shared option block embedded by providers that use directory sharding.

Important APIs/types/functions: `Options` contains `DirectoryShards []int` for shard segment sizes and optional `ListParallelism int` for parallel directory walking.

Control flow: `sharded.New` fills default `DirectoryShards` when nil: latest create mode uses `{1,3}` while open/legacy mode uses `{3,3}`. `ListBlobs` reads `ListParallelism`, defaulting to one worker.

State and persistence behavior: the effective directory-shard configuration can be persisted into `.shards` by `sharded.Storage`; the options themselves are also part of provider connection configs.

Dependencies/integration: anonymously embedded in SFTP, WebDAV, filesystem, and other sharded provider option structs.

Risks and edge cases: nil versus empty slices are meaningful. An explicit empty slice disables sharding in cache backing stores, while nil allows defaults.

Test signals: sharded and WebDAV tests run several shard specs and verify file paths/listing behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/sharded/sharded_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/sharded/sharded_parameters.go -->
# sources/sync-backup/kopia/repo/blob/sharded/sharded_parameters.go

Purpose: defines persisted sharding parameters and the algorithm mapping blob IDs to shard directories and remaining file names.

Important APIs/types/functions: `ParametersFile` is `.shards`; `PrefixAndShards` defines prefix-specific shard overrides; `Parameters` holds default shards, `UnshardedLength`, and overrides. `DefaultParameters`, `Load`, `Save`, `Clone`, `getShardsForBlobID`, and `GetShardDirectoryAndBlob` are the key functions.

Control flow: `GetShardDirectoryAndBlob` returns the root unchanged when the blob ID is short enough; otherwise it applies the first matching override or defaults, repeatedly moving leading ID segments into subdirectories until no segment can be taken.

State and persistence behavior: parameters are JSON-encoded in `.shards`. `Clone` deep-copies slice fields and overrides so later mutations cannot affect the clone.

Dependencies/integration: consumed by `sharded.Storage` and provider tests; uses path joins, JSON, and string prefix checks.

Risks and edge cases: override order controls matching. Shard sizes at or above remaining ID length stop further splitting. Misconfigured zero/negative values would produce unusual layouts, so tests emphasize representative valid specs.

Test signals: `TestShardedFileStorageShardingMap` validates default and override paths, short IDs, and prefix listing; `TestClone` verifies deep-copy isolation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/sharded/sharded_parameters.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/sharded/sharded_test.go -->
# sources/sync-backup/kopia/repo/blob/sharded/sharded_test.go

Purpose: verifies sharded storage layout compatibility, path mapping, prefix listing, malformed parameter handling, and parameter cloning using filesystem-backed storage.

Important APIs/types/functions: tests include `TestShardedOpenLegacyFileStorage`, `TestShardedOpenLatestFileStorage`, `TestShardedFileStorage`, `TestShardedFileStorageShardingMap`, `TestShardedFileStorageShardingMap_Invalid`, and `TestClone`.

Control flow: legacy/latest tests open filesystem storage with nil sharding options under create/open modes and assert expected `.f` paths. General storage tests run `blobtesting.VerifyStorage` across many shard specs and list parallelism values. Mapping tests write a custom `.shards` JSON file, upload blobs, assert exact file paths, and list every prefix. Malformed tests confirm bad `.shards` blocks operations until removed, then cached valid parameters tolerate later file corruption.

State and persistence behavior: tests create temp repositories with `.shards`, `.f` blob files, and ignored foreign files. Clone tests serialize before/after mutation to prove no shared slices.

Dependencies/integration: depends on filesystem provider, sharded package, gather buffers, blobtesting, and temp directories.

Risks and edge cases: default layout compatibility is important for existing repositories. Prefix listing must remain correct across nested shard directories and overrides.

Test signals: failures indicate path-layout regression, broken prefix filtering, unsafe parameter cache behavior, or shallow-copy bugs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/sharded/sharded_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/storage.go -->
# sources/sync-backup/kopia/repo/blob/storage.go

Purpose: defines Kopia's central blob storage interfaces, sentinel errors, retention options, metadata model, and shared helper functions for listing, deletion, range validation, and metadata aggregation.

Important APIs/types/functions: interfaces include `Bytes`, `OutputBuffer`, `Volume`, `Lister`, `Reader`, and `Storage`. Data types include `Capacity`, `RetentionMode`, `PutOptions`, `ExtendOptions`, `ID`, and `Metadata`. Helpers include `ListAllBlobs`, `IterateAllPrefixesInParallel`, `EnsureLengthExactly`, `IDsFromMetadata`, `TotalLength`, `MinTimestamp`, `MaxTimestamp`, `DeleteMultiple`, `PutBlobAndGetMetadata`, and `ReadBlobMap`.

Control flow: storage implementations expose common read/list/write/delete/retention/capacity behavior. Prefix iteration fans out `ListBlobs` calls under a semaphore and returns the first callback/listing error. `DeleteMultiple` uses `errgroup` with caller-supplied parallelism. `PutBlobAndGetMetadata` ensures `GetModTime` is populated so callers receive a timestamp.

State and persistence behavior: this file stores no durable state but documents the required backend semantics: durability, read-after-write, atomic visibility, monotonic-ish timestamps, and low-latency reads. `DefaultProviderImplementation` supplies common unsupported/no-op behavior.

Dependencies/integration: every repository storage provider depends on these contracts and sentinel errors. Azure retention mode is imported for the `Locked` mode constant, and logging is used in `ReadBlobMap`.

Risks and edge cases: `IterateAllPrefixesInParallel` assumes callers make callbacks thread-safe. Passing nonpositive parallelism to `DeleteMultiple` would create a zero-capacity semaphore problem for nonempty input. `EnsureLengthExactly` treats negative expected length as full-read/no-check.

Test signals: `storage_test.go` covers listing, parallel prefix iteration, length validation, metadata helpers, parallel deletion, JSON formatting, and `PutBlobAndGetMetadata`; provider suites rely on these contracts.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/storage_extend_test.go -->
# sources/sync-backup/kopia/repo/blob/storage_extend_test.go

Purpose: format-version matrix tests for repository-level blob retention extension behavior.

Important APIs/types/functions: methods on `formatSpecificTestSuite` are `TestExtendBlobRetention` and `TestExtendBlobRetentionUnsupported`. They use repotesting environments, object writers, fake time, encryption/HMAC settings, `blob.ListAllBlobs`, `RetentionStorage.GetRetention`, and `BlobStorage().ExtendBlobRetention`.

Control flow: the positive test creates a repository with retention enabled, writes and flushes an object, checks that the last blob has governance retention near the expected expiry, extends retention, and verifies the new expiry. The unsupported test creates a repository without retention, writes data, then expects `object locking unsupported` from `ExtendBlobRetention`.

State and persistence behavior: tests write real repository format blobs and pack/index blobs into test storage for each supported format version. Fake time controls expected retention timestamps.

Dependencies/integration: integrates repo creation/open options, encryption formats, content/object writing, root storage retention hooks, and the blob retention API.

Risks and edge cases: test assumes a fixed count of four blobs after the write/flush sequence. It verifies the last blob only, so broader retention coverage depends on repository writer behavior.

Test signals: success confirms retention configuration reaches storage writes and that unsupported retention remains a clear sentinel error across format versions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/storage_extend_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/storage_test.go -->
# sources/sync-backup/kopia/repo/blob/storage_test.go

Purpose: unit tests for blob package helper functions and metadata utilities.

Important APIs/types/functions: covers `ListAllBlobs`, `IterateAllPrefixesInParallel`, `EnsureLengthExactly`, `IDsFromMetadata`, `MaxTimestamp`, `MinTimestamp`, `TotalLength`, `DeleteMultiple`, `Metadata.String`, and `PutBlobAndGetMetadata` using in-memory `blobtesting.NewMapStorage`.

Control flow: tests populate map storage, list by prefixes, collect concurrent callback results under a mutex, inject callback errors, validate range-length outcomes, compute metadata aggregates, delete selected IDs in parallel, compare JSON formatting, and verify put metadata uses the storage-assigned fixed timestamp.

State and persistence behavior: all state is in-memory `blobtesting.DataMap` and optional key-time maps. `DeleteMultiple` mutates the map by removing selected blob IDs.

Dependencies/integration: depends on blobtesting, gather buffers, testify assertions, and the public blob package.

Risks and edge cases: concurrent prefix iteration requires test callback locking, mirroring real caller obligations. Tests do not cover invalid `DeleteMultiple` parallelism.

Test signals: failures indicate broken helper semantics that would affect every provider and repository maintenance path.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/storagemetrics/storage_metrics.go -->
# sources/sync-backup/kopia/repo/blob/storagemetrics/storage_metrics.go

Purpose: wraps any `blob.Storage` with metrics counters and latency distributions for storage operations, bytes transferred, list item counts, and errors.

Important APIs/types/functions: `blobMetrics` holds the wrapped storage plus counters/distributions. It implements all `blob.Storage` methods, recording durations for `GetBlob`, `GetCapacity`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `ExtendBlobRetention`, `ListBlobs`, `Close`, and `FlushCaches`. `NewWrapper` creates metric instruments in a `metrics.Registry`.

Control flow: each method starts a timer, delegates to the base storage, observes duration, increments an error counter when appropriate, and updates byte or item counters. `GetBlob` separates full reads (`length < 0`) from partial reads, counting actual output length. `ListBlobs` wraps the callback to count delivered items.

State and persistence behavior: no durable state; metrics live in the provided registry. The wrapper preserves connection info, display name, read-only state, and base errors.

Dependencies/integration: used by repository managers to expose blob I/O observability; depends on internal metrics and timetrack packages plus the blob interface.

Risks and edge cases: `ExtendBlobRetention` creates fields but `NewWrapper` currently does not initialize `extendBlobRetentionDuration` or `extendBlobRetentionErrors`, so calling it through this wrapper would panic. Tests do not cover that method.

Test signals: `storage_metrics_test.go` verifies counters and duration counts for put/get/metadata/capacity/delete/close/flush/list and pass-through metadata methods.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/storagemetrics/storage_metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/storagemetrics/storage_metrics_test.go -->
# sources/sync-backup/kopia/repo/blob/storagemetrics/storage_metrics_test.go

Purpose: validates that the storage metrics wrapper records bytes, item counts, latency distribution samples, errors, and pass-through metadata correctly.

Important APIs/types/functions: test cases are operation-specific: `TestStorageMetrics_PutBlob`, `GetBlob`, `GetMetadata`, `GetCapacity`, `DeleteBlob`, `Close`, `FlushCaches`, `ListBlobs`, and `Misc`. `requireCounterValue` checks registry snapshots.

Control flow: tests wrap in-memory map storage with `blobtesting.NewFaultyStorage`, configure one injected fault for an operation, call the operation once expecting the injected error and again expecting normal behavior, then assert error counters and duration distribution counts. Get/list tests also verify byte and item counters.

State and persistence behavior: map storage holds small test blobs; metrics state is in `metrics.Registry` snapshots. Faulty storage mutates its fault list as operations consume configured faults.

Dependencies/integration: depends on blobtesting fault injection, gather buffers, metrics registry snapshots, and the storagemetrics wrapper.

Risks and edge cases: there is no test for `ExtendBlobRetention`, leaving a gap around the uninitialized retention metric fields in `NewWrapper`.

Test signals: success proves normal and failing operations are counted once, full/partial downloads are distinguished, uploads count only on success, and base connection info/display name are preserved.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/storagemetrics/storage_metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/suite_test.go -->
# sources/sync-backup/kopia/repo/blob/suite_test.go

Purpose: drives blob package format-specific tests across all repository format versions.

Important APIs/types/functions: `formatSpecificTestSuite` carries a `format.Version`; `TestFormatV1`, `TestFormatV2`, and `TestFormatV3` invoke `testutil.RunAllTestsWithParam` with the suite.

Control flow: the test utility discovers methods on `formatSpecificTestSuite`, such as retention extension tests in `storage_extend_test.go`, and runs them once per format version.

State and persistence behavior: this file has no state itself; it causes each suite method to create separate test repositories for each format version.

Dependencies/integration: integrates Kopia format version constants with the testutil parameterized-suite runner.

Risks and edge cases: new suite methods automatically run for all versions, which is desirable but can surprise if a test is not format-agnostic.

Test signals: failures identify format-version-specific behavior differences in shared blob/repository tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/throttling/throttler.go -->
# sources/sync-backup/kopia/repo/blob/throttling/throttler.go

Purpose: implements a configurable token-bucket-based throttler for blob operation rates, byte bandwidth, and concurrent read/write limits.

Important APIs/types/functions: `SettableThrottler` extends `Throttler` with `Limits`, `SetLimits`, and `OnUpdate`; `Limits` contains per-second operation and byte limits plus concurrency caps. `tokenBucketBasedThrottler` owns operation buckets, byte buckets, semaphores, current limits, update handlers, and a rate window. `NewThrottler` constructs and validates it.

Control flow: `BeforeOperation` consumes list/read/write operation tokens and acquires read/write semaphores for metadata/get and put/delete. `AfterOperation` releases the matching semaphore. Upload/download methods consume or return byte tokens. `SetLimits` applies all limits to buckets/semaphores under lock, rolls back on validation failure, stores limits, and invokes update handlers.

State and persistence behavior: all state is in memory: token counts, semaphore channels, current limits, and callbacks. No durable persistence is involved.

Dependencies/integration: used by `throttling_storage.go` and embedded provider options. Depends on the local `tokenBucket` and `semaphore` types.

Risks and edge cases: update handlers run under the mutex, so callbacks must avoid reentering throttler methods. `BeforeOperation` does not rate-limit `ExtendBlobRetention` in the current switch even though the wrapper names the operation.

Test signals: `throttler_test.go` measures read/write/list/upload/download rates and large-window burst behavior under concurrent workers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/throttling/throttler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/throttling/throttler_test.go -->
# sources/sync-backup/kopia/repo/blob/throttling/throttler_test.go

Purpose: timing-based tests for token-bucket throttling limits across operation rates and bandwidth limits.

Important APIs/types/functions: `TestThrottler`, `TestThrottlerLargeWindow`, and helper `testRateLimiting` exercise `NewThrottler`, `BeforeDownload`, `ReturnUnusedDownloadBytes`, `BeforeUpload`, and `BeforeOperation`.

Control flow: `TestThrottler` creates limits and, for each limit type, starts three workers for three seconds that repeatedly perform throttled operations while accumulating totals. It asserts actual rate stays within 85% to 115% of target. The large-window test starts full, consumes a minute worth of download quota immediately, then verifies the next quota chunk blocks around one second.

State and persistence behavior: throttler state is in-memory token buckets and semaphores; tests use wall-clock timing through `clock.Now`/`timetrack`.

Dependencies/integration: depends on random sizes, goroutines, atomics, and testify. Timing margins account for scheduling variability.

Risks and edge cases: tests are inherently timing-sensitive and can be noisy on overloaded machines. They do not test dynamic `SetLimits` or update handlers.

Test signals: failures indicate token refill math, burst capacity, refund handling, or operation bucket mapping has regressed.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/throttling/throttler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/throttling/throttling_semaphore.go -->
# sources/sync-backup/kopia/repo/blob/throttling/throttling_semaphore.go

Purpose: provides a small dynamically configurable semaphore used to cap concurrent throttled reads and writes.

Important APIs/types/functions: `semaphore` holds a mutex-protected channel. `Acquire` sends to the channel if limited, `Release` receives if possible, `SetLimit` replaces the channel for a nonnegative limit, and `newSemaphore` constructs an unlimited semaphore.

Control flow: callers fetch the current channel under lock, then block on send for acquisition. Setting limit to zero or less-than? zero disables limiting by setting the channel to nil; negative limits return an error. `Release` uses a nonblocking receive so limit reductions do not deadlock releases from operations acquired on an older channel.

State and persistence behavior: no persistence; the channel object is the current concurrency state. Replacing the channel can orphan tokens from old channels, which is intentional for dynamic limit changes.

Dependencies/integration: used by `tokenBucketBasedThrottler` for concurrent reads and writes.

Risks and edge cases: changing limits while operations are active can make a release observe a different channel than acquisition; the nonblocking release avoids deadlock but means old acquisition tokens are discarded.

Test signals: `throttling_semaphore_test.go` validates unlimited default, negative-limit rejection, and observed max concurrency under several limits.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/throttling/throttling_semaphore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/throttling/throttling_semaphore_test.go -->
# sources/sync-backup/kopia/repo/blob/throttling/throttling_semaphore_test.go

Purpose: verifies concurrency cap behavior of the throttling semaphore.

Important APIs/types/functions: `TestThrottlingSemaphore` uses `newSemaphore`, `SetLimit`, `Acquire`, and `Release`.

Control flow: the test first confirms default unlimited acquire/release and negative-limit error. For limits 3, 5, and 7, it starts ten goroutines each repeatedly acquiring, incrementing a protected concurrency counter, sleeping briefly, decrementing, and releasing; then it asserts max observed concurrency never exceeds the configured limit.

State and persistence behavior: only in-memory counters and semaphore channel state are used.

Dependencies/integration: depends on goroutines, wait groups, mutexes, time sleeps, and testify assertions.

Risks and edge cases: sleep makes the test probabilistic, so it asserts only upper bound and positivity instead of exact max concurrency.

Test signals: failures indicate the semaphore permits too many concurrent holders or fails to block at all.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/throttling/throttling_semaphore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/throttling/throttling_storage.go -->
# sources/sync-backup/kopia/repo/blob/throttling/throttling_storage.go

Purpose: wraps `blob.Storage` so all storage calls pass through a `Throttler` for operation, byte, and concurrency control.

Important APIs/types/functions: `Throttler` defines before/after operation hooks plus upload/download byte acquisition and download refund. `throttlingStorage` embeds `blob.Storage` and overrides `GetBlob`, `GetMetadata`, `ListBlobs`, `PutBlob`, `DeleteBlob`, and `ExtendBlobRetention`. `NewWrapper` constructs the wrapper.

Control flow: each operation calls `BeforeOperation`, defers `AfterOperation`, and delegates to the base storage. `GetBlob` pre-acquires requested length or a 20 MB estimate for unknown full reads, resets output, delegates, then acquires more or refunds unused bytes based on actual output length. `PutBlob` acquires upload bytes equal to data length before delegating.

State and persistence behavior: no durable state; throttling state lives in the supplied throttler and data persists only through the wrapped storage.

Dependencies/integration: typically used with `tokenBucketBasedThrottler` and provider options embedding `throttling.Limits`. It preserves the rest of the base storage interface through embedding.

Risks and edge cases: a failed full read with no bytes refunds the full 20 MB estimate. `ExtendBlobRetention` uses its own operation name, but the concrete token-bucket throttler currently ignores that name, so it only gets before/after callback visibility.

Test signals: `throttling_storage_test.go` checks exact wrapper call ordering, unknown-length estimates/refunds, extra acquisition for large downloads, partial-read byte acquisition, upload byte acquisition, and operation hooks.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/throttling/throttling_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/throttling/throttling_storage_test.go -->
# sources/sync-backup/kopia/repo/blob/throttling/throttling_storage_test.go

Purpose: verifies that the throttling storage wrapper calls throttler hooks in the expected order with the expected byte counts.

Important APIs/types/functions: `mockThrottler` records activity for every `Throttler` method. `TestThrottling` wraps map storage with a logging wrapper inside the throttling wrapper.

Control flow: the test attempts a missing full read, uploads a small blob, uploads a 30 MB blob, reads small and large blobs with unknown length, reads a partial range, gets metadata, deletes, and lists. For each operation it compares the recorded sequence against an exact expected trace.

State and persistence behavior: map storage holds two blobs; the mock holds an activity slice reset between operations.

Dependencies/integration: depends on blobtesting map storage, blob logging wrapper, gather buffers, and the throttling wrapper.

Risks and edge cases: exact sequence assertions are intentionally strict and may require updates if logging wrapper behavior changes. The test does not cover `ExtendBlobRetention`.

Test signals: failures indicate wrapper ordering changes, missing `AfterOperation`, incorrect unknown-download estimate/refund math, or incorrect upload/download byte acquisition.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/throttling/throttling_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/throttling/token_bucket.go -->
# sources/sync-backup/kopia/repo/blob/throttling/token_bucket.go

Purpose: implements the rate-limiting primitive used by the throttler for operation and byte quotas.

Important APIs/types/functions: `tokenBucket` tracks name, time/sleep hooks, mutex, last refill time, current tokens, max tokens, and refill time unit. Methods are `replenishTokens`, `sleepDurationBeforeTokenAreAvailable`, `Take`, `TakeDuration`, `Return`, `SetLimit`, `sleepWithContext`, and `newTokenBucket`.

Control flow: `TakeDuration` replenishes tokens based on elapsed time, subtracts requested tokens, and returns zero if enough tokens remain or a duration proportional to the deficit. `Take` sleeps for that duration. `Return` refunds tokens up to max. `SetLimit` validates nonnegative limits and caps existing token count.

State and persistence behavior: token counts are in-memory and protected by a mutex. Limit zero means unlimited/no sleeping because `sleepDurationBeforeTokenAreAvailable` returns zero when `maxTokens == 0`.

Dependencies/integration: used by `tokenBucketBasedThrottler`; logging reports sleeps; tests override `now` and `sleep` hooks for deterministic time.

Risks and edge cases: the implementation intentionally allows `numTokens` to go negative to represent debt. `SetLimit` contains a duplicate assignment but is harmless. Context cancellation only affects the sleep helper, not token accounting already performed.

Test signals: `token_bucket_test.go` validates deterministic refill, sleeping, debt, max cap, and refund behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/throttling/token_bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/throttling/token_bucket_test.go -->
# sources/sync-backup/kopia/repo/blob/throttling/token_bucket_test.go

Purpose: deterministic unit test for token bucket refill, debt, sleep duration, and refund behavior.

Important APIs/types/functions: `TestTokenBucket` constructs a bucket, overrides `now` and `sleep`, and uses helper `verifyTakeTimeElapsed`.

Control flow: the test consumes zero/all tokens, takes more than available to force 500 ms sleep and negative token debt, advances fake time, verifies refill to max, consumes sequential chunks, forces one-second and 100 ms waits, and checks `Return` caps tokens at max.

State and persistence behavior: fake current time advances only through the test sleep hook or explicit `advanceTime`; bucket state remains in memory.

Dependencies/integration: depends on context, time, and testify assertions.

Risks and edge cases: because the test accesses package-private fields, it catches internal accounting changes but may need updates for alternate implementations.

Test signals: failures indicate broken refill math, max-token capping, debt handling, or refund behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/throttling/token_bucket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/webdav/webdav_options.go -->
# sources/sync-backup/kopia/repo/blob/webdav/webdav_options.go

Purpose: defines configuration for the WebDAV blob provider.

Important APIs/types/functions: `Options` contains WebDAV `URL`, `Username`, sensitive `Password`, optional trusted certificate fingerprint, `AtomicWrites`, and embedded `sharded.Options` plus `throttling.Limits`.

Control flow: `webdav_storage.go` consumes these options to create a `gowebdav.Client`, set identity encoding, optionally trust a single certificate fingerprint, choose sharded layout, and decide whether writes use a temporary random path or write directly.

State and persistence behavior: options are serialized in connection info; password is marked sensitive. Sharded options affect persisted file layout on the WebDAV server.

Dependencies/integration: shared with CLI/config paths and the WebDAV provider constructor.

Risks and edge cases: `AtomicWrites` trades compatibility for atomic visibility; when false, writes depend on server rename support.

Test signals: WebDAV tests exercise built-in and external servers, shard specs, credentials, connection-info round trips, and validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/webdav/webdav_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/webdav/webdav_storage.go -->
# sources/sync-backup/kopia/repo/blob/webdav/webdav_storage.go

Purpose: implements WebDAV-backed Kopia blob storage using the shared sharded layout, HTTP/WebDAV file operations, optional temp-file renames, retry-on-transient errors, and certificate-fingerprint trust.

Important APIs/types/functions: `davStorage` embeds `sharded.Storage`; `davStorageImpl` implements sharded `Impl`. Key methods are `GetBlobFromPath`, `GetMetadataFromPath`, `PutBlobInPath`, `DeleteBlobInPath`, `ReadDir`, `ConnectionInfo`, `DisplayName`, `translateError`, `httpErrorCode`, `isRetriable`, and `New`.

Control flow: `New` creates a `gowebdav.Client`, disables transport compression via `Accept-Encoding: identity`, optionally sets a TLS transport trusting one certificate, constructs sharded storage, and returns a retrying wrapper. Reads use full or ranged streams, special-case zero-length reads, translate HTTP errors, and exact-length-check output. Writes buffer the whole blob, write either final path or random temp path, create missing parent directories on first failure, optionally rename temp to final path, and fill `GetModTime` via metadata.

State and persistence behavior: blobs are `.f` files in the sharded layout under the WebDAV root. Non-atomic mode leaves temporary random names only if write/rename cleanup fails. `SetModTime`, retention, and do-not-recreate are unsupported.

Dependencies/integration: depends on `gowebdav`, Kopia retry helpers, TLS utility, sharded storage, and blob sentinel errors. It shares on-disk layout with filesystem storage.

Risks and edge cases: `math/rand` temp names are not cryptographic. Some servers return 403 instead of 404 for missing parents, so mkdir retry logic matters. HTTP errors are parsed from `os.PathError` text. Atomic direct writes can expose partial data if the server does not provide atomic PUT semantics.

Test signals: `webdav_storage_test.go` runs external/built-in WebDAV validation, many shard specs, auth handling, and a 404-to-403 transform for missing PUTs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/webdav/webdav_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/webdav/webdav_storage_test.go -->
# sources/sync-backup/kopia/repo/blob/webdav/webdav_storage_test.go

Purpose: validates the WebDAV provider against an optional external server and an in-process authenticated WebDAV server.

Important APIs/types/functions: `basicAuth`, `TestWebDAVStorageExternalServer`, `TestWebDAVStorageBuiltInServer`, `TestWebDAVStorageBuiltInServerWithMissingAsForbidden`, `transformMissingPUTs`, and `verifyWebDAVStorage`.

Control flow: external tests read URL/user/password from environment. Built-in tests serve a temp directory through `x/net/webdav` behind basic auth, run multiple shard configurations, clear existing blobs, run `blobtesting.VerifyStorage`, assert connection-info round trips, run provider validation, and close storage. The forbidden-missing test wraps PUT responses to convert 404 into 403 to exercise fallback directory creation.

State and persistence behavior: test blobs are stored in temp directories served over HTTP and removed between shard-spec runs.

Dependencies/integration: depends on `httptest`, `x/net/webdav`, provider-validation, blobtesting, and WebDAV provider code.

Risks and edge cases: external server tests are environment-gated. Built-in server behavior may not match every WebDAV implementation, so the 403 transform broadens coverage for common server quirks.

Test signals: success confirms authentication, sharded layout, provider validation, cleanup, and missing-parent retry behavior work over WebDAV.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/blob/webdav/webdav_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/buildinfo.go -->
# sources/sync-backup/kopia/repo/buildinfo.go

Purpose: initializes user-visible build metadata and version from linker-provided values or Go module build information.

Important APIs/types/functions: global variables are `BuildInfo`, `BuildVersion`, and `BuildGitHubRepo`. `init` calls `getBuildInfoAndVersion`; `getRevisionString` formats VCS settings into `time-revision(+dirty)`.

Control flow: if both linked info and version are set, they win. Otherwise `debug.ReadBuildInfo` is queried. Missing version defaults to `v0-unofficial` unless module version is nonempty and not `(devel)`. Missing info becomes the revision string built from `vcs.revision`, `vcs.time`, and `vcs.modified`.

State and persistence behavior: process-global variables are set at init time only. No files are read or written.

Dependencies/integration: consumed by CLI/about/version reporting and packaging. Uses standard `runtime/debug` and falls back to stdlib logging before Kopia logging is configured.

Risks and edge cases: missing VCS settings produce `-(unknown_revision)`. Dirty detection is case-insensitive only for value `true`. Go toolchain behavior around `(devel)` is explicitly handled.

Test signals: `buildinfo_test.go` validates revision string combinations for missing revision, VCS time, revision, and dirty state.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/buildinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/buildinfo_test.go -->
# sources/sync-backup/kopia/repo/buildinfo_test.go

Purpose: unit tests for formatting VCS build settings into Kopia's build revision string.

Important APIs/types/functions: `TestGetRevisionString` supplies slices of `debug.BuildSetting` to `getRevisionString`.

Control flow: table cases cover no settings, dirty-only, time-only, time plus dirty, full revision, short revisions, and dirty full revision. Each subtest compares exact formatted output.

State and persistence behavior: no persistent state; the test avoids touching package globals by calling the helper directly.

Dependencies/integration: depends on standard `runtime/debug` settings shape and testify `require`.

Risks and edge cases: exact string assertions intentionally lock the current formatting contract, including leading hyphen when time is absent.

Test signals: failures indicate version output changed and downstream CLI or diagnostics expectations may need updates.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/buildinfo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/caching.go -->
# sources/sync-backup/kopia/repo/caching.go

Purpose: reads and updates repository-local caching options and resolves default cache directories.

Important APIs/types/functions: `GetCachingOptions`, `SetCachingOptions`, and `setupCachingOptionsWithDefaults` operate on `LocalConfig` and `content.CachingOptions`.

Control flow: reads load config and return `CloneOrDefault`. Setting options loads config, normalizes options, computes cache directory defaults when content cache is enabled, copies cache size/duration fields into local config, and writes the config file. If content cache size is zero, caching is reset to an empty options object.

State and persistence behavior: modifies the repository local config file. Default cache directory is `$UserCacheDir/kopia/<sha256(uniqueID || configPath)[:16]>`, which makes it stable per repository/config while avoiding collisions. Custom directories are stored as absolute paths.

Dependencies/integration: used by connect/open/config commands and content manager cache setup. Depends on OS cache directory discovery, SHA-256, and `content.CachingOptions`.

Risks and edge cases: when `uniqueID` is nil, hashing uses only config path, which is appropriate for post-connect updates but less repository-specific. Failure to resolve user cache or absolute custom path blocks setting cache options.

Test signals: covered indirectly by repository connect/open and cache manager tests; direct tests should verify default path stability and reset behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/caching.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compression_ids.go -->
# sources/sync-backup/kopia/repo/compression/compression_ids.go

Purpose: reserves stable four-byte header IDs for every supported or historically supported content compressor.

Important APIs/types/functions: `HeaderID` is a `uint32`; constants cover gzip, zstd, s2, pgzip, removed LZ4, and deflate variants.

Control flow: compressor implementations register themselves with one of these IDs and write the big-endian ID as a compression header. `DecompressByHeader` uses the ID to dispatch.

State and persistence behavior: these IDs are persisted inside compressed repository content, so values are wire/storage format and must not be reused incompatibly. `headerLZ4Removed` remains reserved for old repositories even though the implementation is unsupported.

Dependencies/integration: used by every compressor implementation and content read/decompression paths.

Risks and edge cases: changing IDs or reusing removed IDs would make existing repositories unreadable or misdecoded.

Test signals: compressor tests iterate registered IDs, round-trip data, and verify wrong compressors reject mismatched headers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compression_ids.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compressor.go -->
# sources/sync-backup/kopia/repo/compression/compressor.go

Purpose: central registry and common header handling for Kopia content compressors.

Important APIs/types/functions: `Name`, `Compressor`, global maps `ByHeaderID`, `ByName`, `HeaderIDToName`, `IsDeprecated`, and `isUnsupported`; registration helpers; `compressionHeader`; `DecompressByHeader`; `IsSupported`; `verifyCompressionHeader`; and `mustSucceed`.

Control flow: compressors register during package init. Registration panics on duplicate header IDs or names. Compression implementations write a four-byte big-endian header; decompression either dispatches by header or verifies a known header before decoding. Unsupported compressors can be registered for name/ID recognition while `IsSupported` returns false.

State and persistence behavior: global registry maps are process-wide and determine how persisted compression headers are interpreted. The four-byte header is stored in compressed content.

Dependencies/integration: used by content read/write managers and compressor implementations; depends on `internal/impossible` for panic-on-impossible errors.

Risks and edge cases: global mutable maps are not synchronized after init, so registration should remain init-time. Duplicate IDs/names panic. Header mismatch errors are security/format critical because they prevent decoding with the wrong algorithm.

Test signals: `compressor_test.go` verifies all supported compressors round-trip, compress zeros, generally do not compress random data, and cannot decode each other's headers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compressor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compressor_deflate.go -->
# sources/sync-backup/kopia/repo/compression/compressor_deflate.go

Purpose: registers deflate compressor variants using `klauspost/compress/flate`.

Important APIs/types/functions: init registers `deflate-best-speed`, `deflate-default`, and `deflate-best-compression`; `newDeflateCompressor` builds a pooled writer; `deflateCompressor` implements `HeaderID`, `Compress`, and `Decompress`.

Control flow: compression writes the header, takes a `flate.Writer` from a sync pool, resets it to the output, copies input through it, closes to flush, and returns writer to the pool. Decompression optionally verifies the header, creates a flate reader, and copies decompressed bytes to output.

State and persistence behavior: compressed streams persist the assigned deflate header ID followed by deflate payload. Writer pool state is in-memory only.

Dependencies/integration: registered in the central compression maps and used by content manager compression choices.

Risks and edge cases: decompression does not explicitly close the flate reader, which may be acceptable for this implementation but is worth noting if resource behavior changes. Writer pool reuse depends on `Close` before returning to pool.

Test signals: compressor tests round-trip deflate variants and validate header mismatch rejection.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compressor_deflate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compressor_gzip.go -->
# sources/sync-backup/kopia/repo/compression/compressor_gzip.go

Purpose: registers gzip compressor variants using the standard `compress/gzip` package.

Important APIs/types/functions: init registers `gzip`, `gzip-best-speed`, and `gzip-best-compression`; `gzipCompressor` has header ID, header bytes, and a writer pool; `gzipDecoderPool` reuses decoder objects.

Control flow: `Compress` writes the Kopia compression header, takes/resets a gzip writer, streams input, closes to finish the gzip trailer, and returns it to the pool. `Decompress` optionally verifies the header, takes a pooled reader, resets it on input, copies to output, and returns it.

State and persistence behavior: output stores a Kopia header followed by gzip stream bytes. Pools are process-local and reduce allocations.

Dependencies/integration: registered in global compression registry and used by content formatting when selected.

Risks and edge cases: `mustSucceed(dec.Reset(input))` will panic on malformed gzip setup errors; later stream corruption is returned by copy errors. Pool correctness depends on reset/close sequencing.

Test signals: compressor tests validate gzip round trips, wrong-header failures, and basic compression ratio expectations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compressor_gzip.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compressor_lz4.go -->
# sources/sync-backup/kopia/repo/compression/compressor_lz4.go

Purpose: preserves the historical LZ4 compressor name/header while making it explicitly unsupported in current Kopia versions.

Important APIs/types/functions: init calls `registerUnsupportedCompressor("lz4", lz4Compressor{})`; `errLZ4NotSupported` explains that v0.22.3 or older is needed for legacy repositories; `lz4Compressor` implements `HeaderID`, `Compress`, and `Decompress`.

Control flow: registration adds the name/header to global maps, marks it deprecated and unsupported, and both compression/decompression calls return the fixed unsupported error.

State and persistence behavior: `headerLZ4Removed` remains reserved for existing content and must not be reused. No new LZ4 content can be created by this implementation.

Dependencies/integration: `IsSupported("lz4")` returns false even though `ByName`/`ByHeaderID` can recognize it.

Risks and edge cases: repositories that still contain LZ4-compressed data cannot be read by this version. Keeping the ID registered avoids silent reinterpretation by a future compressor.

Test signals: compressor tests skip unsupported IDs; direct coverage should assert `IsSupported("lz4") == false` and the explanatory error.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compressor_lz4.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compressor_pgzip.go -->
# sources/sync-backup/kopia/repo/compression/compressor_pgzip.go

Purpose: registers parallel gzip variants using `github.com/klauspost/pgzip`.

Important APIs/types/functions: init registers `pgzip`, `pgzip-best-speed`, and `pgzip-best-compression`; `pgzipCompressor` owns header bytes and writer pool; `pgzipDecoderPool` reuses `pgzip.Reader` instances.

Control flow: compression writes the Kopia header, resets a pooled pgzip writer to output, streams input, closes to flush, and returns it. Decompression optionally verifies header, resets a pooled reader, copies output, and returns the reader.

State and persistence behavior: persisted payload is Kopia header plus gzip-compatible pgzip stream. Pools are in-memory only.

Dependencies/integration: registered in compression registry and benchmarked alongside other compressors.

Risks and edge cases: pgzip concurrency can affect CPU usage and output size. `mustSucceed` on reader reset assumes reset errors are impossible at that point.

Test signals: shared compressor tests and benchmarks cover round-trip, header mismatch, and performance behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compressor_pgzip.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compressor_s2.go -->
# sources/sync-backup/kopia/repo/compression/compressor_s2.go

Purpose: registers S2 compressor variants, including better compression and parallel writer configurations.

Important APIs/types/functions: constants define parallel concurrency 4 and 8. init registers `s2-default`, `s2-better`, `s2-parallel-4`, and `s2-parallel-8`; `s2Compressor` implements the common compressor interface; `s2DecoderPool` reuses readers.

Control flow: compression writes the Kopia header, resets a pooled `s2.Writer` with configured options, copies input, closes, and returns it. Decompression optionally verifies header, resets a pooled `s2.Reader`, and streams decoded bytes.

State and persistence behavior: output stores a Kopia header followed by S2 stream data. Parallelism affects runtime resources, not file format ID beyond the selected registered header.

Dependencies/integration: registered in global compression maps and used by content manager when selected.

Risks and edge cases: parallel variants can use more goroutines/CPU. Decoder pool reset to nil on return helps avoid retaining input readers.

Test signals: shared compressor tests validate S2 variants round-trip, reject wrong headers, and compress zero data effectively.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compressor_s2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compressor_test.go -->
# sources/sync-backup/kopia/repo/compression/compressor_test.go

Purpose: validates all supported compressors for round-trip correctness, header isolation, rough compression behavior, and benchmark performance.

Important APIs/types/functions: `TestCompressor` iterates `ByHeaderID`, skipping unsupported IDs; `BenchmarkCompressor`, `compressionBenchmark`, and `decompressionBenchmark` iterate supported names from `ByName`.

Control flow: for each supported compressor, the test compresses zero data and expects output smaller than input, verifies every other compressor rejects the header, decompresses with the correct compressor, then repeats with random data expecting it not to shrink. Benchmarks cover zero, repeated-pattern, and random data for compression/decompression.

State and persistence behavior: all data is in memory buffers. The test exercises the persisted four-byte header contract by passing full compressed data to `Decompress(..., withHeader=true)`.

Dependencies/integration: depends on crypto random data, sorted compressor names, testutil `TestMain`, and the global compression registry.

Risks and edge cases: the random-data non-compression assertion is heuristic but reasonable for the registered algorithms. Unsupported compressors are skipped, so LZ4 unsupported behavior is not directly asserted.

Test signals: failures indicate broken compressor registration, header collisions, wrong-header acceptance, round-trip corruption, or unexpectedly poor/basic compression behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compressor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compressor_zstd.go -->
# sources/sync-backup/kopia/repo/compression/compressor_zstd.go

Purpose: registers Zstandard compressor variants using `klauspost/compress/zstd`.

Important APIs/types/functions: init registers `zstd`, `zstd-fastest`, `zstd-better-compression`, and deprecated `zstd-best-compression`; `zstdCompressor` implements common compressor methods; `zstdDecoderPool` reuses single-concurrency decoders.

Control flow: compression writes header, takes/resets a pooled zstd encoder, streams input, closes to flush, and returns it. Decompression optionally verifies the header, resets a pooled decoder on input, copies decoded bytes, and returns the decoder after resetting to nil.

State and persistence behavior: compressed content carries a Kopia header that selects the zstd level variant. Best-compression remains readable but marked deprecated for new selection behavior.

Dependencies/integration: registered in global compression maps and frequently used as metadata compressor in repository tests.

Risks and edge cases: decoder reset errors are returned; encoder creation errors panic through `mustSucceed` during pool initialization. Deprecated status affects UI/selection but not read compatibility.

Test signals: compressor tests and content formatter tests exercise zstd round-trips and repository read/write paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/compression/compressor_zstd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/connect.go -->
# sources/sync-backup/kopia/repo/connect.go

Purpose: connects a local Kopia config file to an initialized repository storage, persists storage/client/cache settings, verifies the connection, and supports disconnecting and client-option updates.

Important APIs/types/functions: `ConnectOptions` embeds `ClientOptions` and `content.CachingOptions`; `ErrRepositoryNotInitialized`; functions `Connect`, `verifyConnect`, `Disconnect`, and `SetClientOptions`.

Control flow: `Connect` reads the repository format blob from storage, maps missing blob to `ErrRepositoryNotInitialized`, parses format JSON, captures storage connection info, applies default client options, sets up cache options using repository unique ID, writes local config, then opens and closes the repository to verify password/config. Verification failure triggers `Disconnect` cleanup. `Disconnect` loads config, removes absolute cache directory and maintenance lock, then removes the config file.

State and persistence behavior: writes and deletes the local config file, cache directory, and maintenance lock path. It never initializes repository storage; it requires the format blob to exist.

Dependencies/integration: integrates blob storage, format parsing, local config serialization, repo open/close, cache option setup, and OS file removal.

Risks and edge cases: `Disconnect` refuses to delete relative cache directories to avoid unsafe removal. A failed verification can remove a just-written config and cache. Password verification depends on `Open`.

Test signals: covered through repository connect/open tests elsewhere; direct tests should cover missing format blob, malformed format JSON, failed verify cleanup, and relative-cache refusal.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/connect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/caching_options.go -->
# sources/sync-backup/kopia/repo/content/caching_options.go

Purpose: defines content/cache configuration values and small helpers used by repository read/write managers.

Important APIs/types/functions: `DurationSeconds` with `DurationOrDefault`; `CachingOptions` fields for cache directory, content and metadata size/limit bytes, list cache duration, sweep ages, and non-serialized `HMACSecret`; methods `EffectiveMetadataCacheSizeBytes`, `CloneOrDefault`, and `CacheSubdirOrEmpty`.

Control flow: duration helper returns default on zero. Effective metadata size falls back to content cache size for legacy configs. Clone handles nil by returning an empty options object. Cache subdir returns empty if cache or cache directory is unset.

State and persistence behavior: most fields serialize into local config; `HMACSecret` is intentionally excluded from JSON and supplied from repository format/security context.

Dependencies/integration: used by `repo/caching.go`, `committed_read_manager.go`, content caches, list cache, own-writes cache, and index blob cache.

Risks and edge cases: zero values are meaningful defaults, so callers must use helper methods instead of raw fields when default behavior matters. HMAC secret omission from JSON is security-sensitive.

Test signals: cache and committed content index tests indirectly exercise clone/default and sweep-age behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/caching_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/committed_content_index.go -->
# sources/sync-backup/kopia/repo/content/committed_content_index.go

Purpose: manages the set of committed content indexes currently in use by a repository reader, including cache population, index merging, deleted-content filtering, small-index combination, revision tracking, and cache expiry.

Important APIs/types/functions: `committedContentIndex`, `committedContentIndexCache`, `smallIndexEntryCountThreshold`, `getContent`, `addIndexBlob`, `listContents`, `use`, `combineSmallIndexes`, `fetchIndexBlobs`, `missingIndexBlobs`, and `newCommittedContentIndex`.

Control flow: loading starts by identifying missing index blobs, fetching them in parallel, caching them, and then `use` merges the requested active index blob set. `merge` reuses already-open indexes, opens missing ones from cache, optionally skips bad cache entries in permissive mode, combines small indexes into one in-memory segment, and returns a new merged view. `use` swaps the active map, increments revision, closes indexes no longer active, and asks the cache to expire unused entries.

State and persistence behavior: active index state is protected by `mu`; `rev` is atomic and increments after content visibility changes. Cache state may be memory-only or disk-backed under `<cache>/indexes`. `deletionWatermark` filters deleted entries whose deletion timestamp is not after the watermark.

Dependencies/integration: used by `SharedManager` to answer content lookup/listing. Depends on index builders/openers, format provider mutable parameters, gather buffers, blob IDs, content logging, and clock/cache options.

Risks and edge cases: revision increments must happen after visibility updates or callers can cache inconsistent results. Combining small indexes must preserve entry ordering and close newly opened indexes on errors. Permissive cache loading can hide corrupt/missing index blobs and should only be used deliberately.

Test signals: cache tests verify cache implementations used by this manager; broader content manager tests cover lookup/listing. Direct tests should cover deleted watermark behavior, small-index combination, revision changes, and permissive open failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/committed_content_index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/committed_content_index_cache_test.go -->
# sources/sync-backup/kopia/repo/content/committed_content_index_cache_test.go

Purpose: shared test suite for disk and memory committed-content-index cache implementations.

Important APIs/types/functions: `TestCommittedContentIndexCache_Disk`, `TestCommittedContentIndexCache_Memory`, `testCache`, `mustBuildIndex`, and `mustParseID`.

Control flow: the shared test verifies cache miss, failed open for missing index, adding an index, hit detection, duplicate add idempotency, opening indexes and reading expected pack IDs, closing opened indexes, expiring unused indexes, advancing fake time for disk cache safety, and confirming removed indexes are gone.

State and persistence behavior: disk cache stores `.sndx` files in a temp directory and uses fake time for sweep age; memory cache stores opened `index.Index` objects in a map.

Dependencies/integration: depends on content index builders, gather bytes, blob IDs, faketime, test logging, and both cache implementations.

Risks and edge cases: disk cache intentionally keeps young unused files until sweep age elapses. The test confirms duplicate writes are safe.

Test signals: failures indicate cache hit/miss, index serialization/opening, duplicate write, or expiry behavior has regressed.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/committed_content_index_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/committed_content_index_disk_cache.go -->
# sources/sync-backup/kopia/repo/content/committed_content_index_disk_cache.go

Purpose: disk-backed implementation of `committedContentIndexCache` for cached committed index blobs.

Important APIs/types/functions: `diskCommittedContentIndexCache`, `simpleIndexSuffix`, `indexBlobPath`, `openIndex`, `hasIndexBlobID`, `addContentToCache`, and `expireUnused`.

Control flow: index blobs map to `<cache>/<blobID>.sndx`. `addContentToCache` skips if the file exists, otherwise writes bytes to an atomic temp file and renames it into place, tolerating races if another process created the file. `openIndex` mmaps the file through platform-specific `mmapFile` and opens an index with an unmap closer. `expireUnused` lists `.sndx` files, removes currently used IDs, and deletes remaining files only when older than `minSweepAge`.

State and persistence behavior: persists raw index bytes as `.sndx` files under the cache directory. Expiry is age-gated to avoid deleting indexes another process may have just created.

Dependencies/integration: used by `newCommittedContentIndex` when `CachingOptions.CacheDirectory` is set. Depends on atomic temp writes, mmap platform files, content logging, and index openers.

Risks and edge cases: concurrent writers rely on atomic rename and existence recheck. Expiry logging must tolerate files disappearing after directory listing. Platform-specific mmap close behavior is critical for FD usage and Windows file locking.

Test signals: cache tests cover add/open/expire and duplicate writes; Linux FD test ensures Unix mmap does not retain one file descriptor per open index.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/committed_content_index_disk_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/committed_content_index_disk_cache_unix.go -->
# sources/sync-backup/kopia/repo/content/committed_content_index_disk_cache_unix.go

Purpose: Unix-specific mmap helper for disk committed-content index cache.

Important APIs/types/functions: `(*diskCommittedContentIndexCache).mmapFile` opens a file, maps it read-only with `mmap.Map`, closes the file descriptor immediately, and returns the mapping plus an unmap closer.

Control flow: on open or mmap error, it wraps and returns the error while closing the file on mmap failure. After successful mmap, it closes the file descriptor because Unix mappings remain valid after close. If close fails, it still returns the mapping and a closer that unmaps then returns the close error.

State and persistence behavior: no new persistent state; it maps existing `.sndx` files into memory and releases file descriptors early.

Dependencies/integration: build-tagged for non-Windows. Used by `diskCommittedContentIndexCache.openIndex`.

Risks and edge cases: close errors are deferred until index close. Correct early FD close is important for repositories with many cached indexes.

Test signals: Linux FD growth test opens 200 indexes and verifies descriptor count does not grow proportionally.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/committed_content_index_disk_cache_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/committed_content_index_disk_cache_windows.go -->
# sources/sync-backup/kopia/repo/content/committed_content_index_disk_cache_windows.go

Purpose: Windows-specific mmap helper for disk committed-content index cache.

Important APIs/types/functions: `(*diskCommittedContentIndexCache).mmapFile` opens the index file with retries, maps it read-only, and returns a closer that unmaps and then closes the file.

Control flow: it retries `os.Open` up to eight times with exponential backoff from 10 ms to about 1.28 s, logging retry attempts. After successful open, mmap failure closes the file. Unlike Unix, the file descriptor stays open until unmap because Windows requires it.

State and persistence behavior: no new persistent state; it holds an open file handle for the life of the mmap.

Dependencies/integration: build-tagged for Windows. Used by `diskCommittedContentIndexCache.openIndex` and content cache loading.

Risks and edge cases: keeping handles open can affect file deletion/expiry behavior on Windows. Retry logic protects against a rare just-written file open race.

Test signals: not covered by the Linux FD test; Windows-specific tests should exercise open retry and close/unmap ordering.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/committed_content_index_disk_cache_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/committed_content_index_fd_linux_test.go -->
# sources/sync-backup/kopia/repo/content/committed_content_index_fd_linux_test.go

Purpose: Linux-specific regression test ensuring mmap-backed disk index cache does not retain a file descriptor for every opened index.

Important APIs/types/functions: `countFDsLinux` reads `/proc/self/fd`; `TestCommittedContentIndexCache_Disk_FDsNotGrowingOnOpen_Linux` creates many cached indexes and opens them all.

Control flow: the test creates 200 small index files in a disk cache, counts file descriptors, opens every index and keeps the mappings alive, counts descriptors again, and asserts the delta is at most 32. It then closes all indexes.

State and persistence behavior: `.sndx` cache files live in a temp directory; mmap objects remain alive until closed by the test.

Dependencies/integration: Linux `/proc`, disk cache, mmap behavior from the Unix implementation, index builders, faketime, and test logging.

Risks and edge cases: the test is not parallel to avoid FD noise. The local `var lm *repodiag.LogManager` is nil before `lm.NewLogger("test")`, which appears risky unless `LogManager` methods tolerate nil receivers.

Test signals: a large FD delta would mean Unix mmap no longer closes descriptors promptly, which matters for repositories with many indexes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/committed_content_index_fd_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/committed_content_index_mem_cache.go -->
# sources/sync-backup/kopia/repo/content/committed_content_index_mem_cache.go

Purpose: in-memory implementation of `committedContentIndexCache` for repositories without a cache directory.

Important APIs/types/functions: `memoryCommittedContentIndexCache` holds a mutex-protected map from index blob ID to `index.Index`; methods implement `hasIndexBlobID`, `addContentToCache`, `openIndex`, and `expireUnused`.

Control flow: adding content opens an index directly from byte slices and stores it in the map. Opening returns the stored index or an error if absent. Expiry builds a new map containing only requested used IDs.

State and persistence behavior: all index data and opened index objects are memory-resident and lost when the process exits. Expiry immediately drops unused map entries.

Dependencies/integration: selected by `newCommittedContentIndex` when cache directory is empty. Depends on gather bytes and index openers.

Risks and edge cases: stored indexes are shared objects; close ownership is managed by the committed-content index. Re-adding an existing ID replaces the map entry without explicitly closing the old index.

Test signals: shared cache tests verify add/open/hit/expire behavior for memory cache.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/committed_content_index_mem_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/committed_read_manager.go -->
# sources/sync-backup/kopia/repo/content/committed_read_manager.go

Purpose: builds and manages the shared read side of Kopia content storage: committed index loading, content and metadata caches, index blob managers, local pack-index recovery, decryption/decompression, epoch support, and repository diagnostics.

Important APIs/types/functions: `SharedManager`, `IndexBlobReader`, constants for cache sweep ages and index refresh, `LoadIndexBlob`, `IndexReaderV0`, `IndexReaderV1`, `readPackFileLocalIndex`, `loadPackIndexesLocked`, `indexBlobManager`, `decryptContentAndVerify`, `IndexBlobs`, cache construction helpers, `setupCachesAndIndexManagers`, `EpochManager`, `CloseShared`, `shouldRefreshIndexes`, `PrepareUpgradeToIndexBlobManagerV1`, and `NewSharedManager`.

Control flow: construction clones/defaults options, initializes caches and V0/V1 index managers, then loads active pack indexes under `indexesLock`. Index loading chooses V0 or V1 manager based on mutable epoch parameters, retries on missing blobs with cache flush and backoff, fetches missing encrypted index blobs into the committed index cache, swaps active indexes, sets refresh deadline, and warns on too many index blobs. Content reads decrypt using content ID-derived IV, verify format encryption, and decompress when `CompressionHeaderID` is set.

State and persistence behavior: owns persistent caches under `CachingOptions.CacheDirectory` for contents, metadata, list/own-writes backing stores, and index blobs; committed index state is memory plus optional disk `.sndx` cache. It tracks refresh deadline, statistics, metrics, and diagnostic loggers. Close releases index/cache resources, flushes epoch manager, and syncs logs.

Dependencies/integration: central integration point for blob storage, filesystem cache storage, sharded cache layout, listcache, ownwrites, persistent cache protection, indexblob managers, epoch manager, format/encryption/hashing, compression registry, repodiag logging, and content stats/metrics.

Risks and edge cases: cache setup order is important because index blob managers depend on wrapped cached storage. Local pack-index recovery first reads only the postamble tail and falls back to full blob. Permissive cache loading skips bad index blobs. V1 epoch setup passes a callback that calls `sm.indexBlobManagerV1`, so initialization order must remain valid. Closing assumes all cache/index manager fields were initialized.

Test signals: content formatter and broader content-manager tests exercise end-to-end write/read, encryption/decompression, flushing, and cache paths; index cache tests cover committed index cache pieces. Direct tests should cover refresh retry behavior, V0/V1 selection, local-index recovery fallback, and close ordering.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/committed_read_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_formatter_test.go -->
# sources/sync-backup/kopia/repo/content/content_formatter_test.go

Purpose: end-to-end tests for content hashing, encryption, decryption, formatting, writing, flushing, and reading across all supported hash and encryption algorithms.

Important APIs/types/functions: `TestFormatters`, `verifyEndToEndFormatter`, and `mustCreateFormatProvider` use `hashing.SupportedAlgorithms`, `encryption.SupportedAlgorithms`, `NewManagerForTesting`, `WriteContent`, `GetContent`, and `Flush`.

Control flow: for each hash/encryption pair, the test computes a content ID, encrypts random data, decrypts it, and compares SHA-1 of plaintext. It then creates an in-memory content manager and writes several payload sizes/patterns without compression, reads each before and after `Flush`, and compares bytes.

State and persistence behavior: storage state is an in-memory `blobtesting.DataMap` with key timestamps. Format provider uses test HMAC secret, zero master key, mutable parameters, and selected algorithms.

Dependencies/integration: exercises hashing, encryption, format provider, content manager, blob map storage, gather buffers, and committed read/write paths.

Risks and edge cases: algorithm matrix can be expensive but gives broad compatibility coverage. The test focuses on no-compression content writes; compression-specific behavior is covered elsewhere.

Test signals: failures indicate broken hash/encryption setup, content ID derivation, encrypt/decrypt round-trip, content manager read/write before flush, or committed read after flush.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/content_formatter_test.go -->

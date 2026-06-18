# subset-b-008429 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BackupAgentBase.cpp -->
# sources/storage-engines/foundationdb/fdbclient/BackupAgentBase.cpp

Purpose: This file implements shared backup-agent primitives for time parsing, backup state text, mutation-log key layout, restore mutation application, backup log cleanup, and default backup key ranges. It is the low-level glue between the higher-level `DatabaseBackupAgent`/file backup agents and FoundationDB system keyspaces such as `backupLogKeys`, `applyLogKeys`, `backupLatestVersionsPrefix`, and task/config subspaces.

Important APIs and types: Key exported functions include `BackupAgentBase::formatTime`, `parseTime`, `getState`, `getStateText`, `getStateName`, `isRunnable`, `getCurrentTime`, `getLogRanges`, `getApplyRanges`, `getLogKey`, `decodeBKMutationLogKey`, `readCommitted`, `applyMutations`, `eraseLogData`, `cleanupLogMutations`, `cleanupBackup`, `addDefaultBackupRanges`, `getSystemBackupRanges`, and `systemBackupMutationMask`. The file manipulates `RCGroup`, `MutationRef`, `CommitTransactionRequest`, `FlowLock`, `KeyRangeMap<Version>`, `ReadYourWritesTransaction`, and backup/DR subspaces.

Control flow: Restore reads backup log ranges by hashed version buckets, groups raw log parts by commit version, serializes those parts back into one transaction payload, decodes each mutation, filters it through a key-version map so snapshot data is not overwritten by older log records, rewrites prefixes for DR or restore targets, and sends lock-aware commit requests directly to the commit proxy. The apply loop advances in `APPLY_BLOCK_SIZE` batches, dynamically adjusts read/commit lock budgets, coalesces key-version cache entries, and waits for background commit actors. Cleanup scans version-history records for a destination UID, identifies the oldest backup/DR tag, and conditionally clears shared log ranges without deleting data still needed by another tag.

State and persistence behavior: The file defines the persistent key names used under backup config/state/error/range/task/future subspaces. Backup mutation data is sharded by destination UID, a one-byte hash, big-endian version, and part index. Apply progress is persisted with `applyMutationsBeginRange`; key-version cache counts and entries live under `applyMutationsKeyVersion*` ranges. Cleanup updates or clears `backupLatestVersionsPrefix`, `logRangesRange`, `destUidLookupPrefix`, and raw blog ranges, using lock-aware system-key transactions.

Dependencies and integration points: It depends on `BackupAgent.h`, `DatabaseBackupAgent` constants, commit proxy interfaces, management APIs, system data key ranges, simulator hooks, and client knobs for block sizes, lock budgets, retry limits, and backup consistency checks. It integrates with `DatabaseBackupAgent.cpp` tasks, restore paths that decode range files, the timekeeper code used by backup descriptions, and simulation tests that verify log key containment.

Risks: The hashed key layout must remain consistent between `getLogRanges` and `getLogKey`; any mismatch loses log records. `decodeBackupLogValue` assumes exact binary payload boundaries and valid mutation types. Prefix rewriting and clear-range splitting are correctness-sensitive, especially around `allKeys.end` and `strinc(removePrefix)`. Cleanup is shared-data aware, but mistakes in version-history comparisons could clear logs still needed by another backup or DR. Memory pressure is controlled by `FlowLock`, so incorrect expected-size accounting can overrun restore workers.

Test signals: In-file unit coverage includes `/backup/logversion`, which checks that generated log keys fall inside computed log ranges. Related tests in `BackupContainerFileSystem.cpp` validate timestamp parsing and backup container restore continuity. Operational signals include `BA_DecodeBackupLogValue`, `ApplyMutationsError`, `BA_LogError`, cleanup console warnings, and trace details for invalid versions, missing data, and commit throttling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BackupAgentBase.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BackupContainer.cpp -->
# sources/storage-engines/foundationdb/fdbclient/BackupContainer.cpp

Purpose: This file implements common `IBackupContainer` utilities: backup file length-prefix appends, URL dispatch to concrete containers, backup discovery, human/JSON descriptions, and timekeeper conversions between wall-clock time and FoundationDB versions.

Important APIs and types: It defines `IBackupFile::appendStringRefWithLen`, `isBlobstoreUrl`, `IBackupContainer::ExpireProgress::toString`, `BackupFileList::toStream`, `BackupDescription::resolveVersionTimes`, `toString`, `toJSON`, `IBackupContainer::getURLFormats`, `openContainer`, `listContainers`, `timeKeeperVersionFromDatetime`, and `timeKeeperEpochsFromVersion`. It creates `BackupContainerLocalDirectory`, `BackupContainerBlobStore`, and optionally Azure containers, and uses `KeyBackedMap<int64_t, Version>` for timekeeper data.

Control flow: `openContainer` caches containers by URL in production, but skips the cache in simulation for `blobstore://` and `file://` URLs to avoid sharing connection pools or encryption settings across simulated processes. It parses the URL prefix, falls back to the global file backup proxy when needed, asks `IBlobStoreEndpoint::fromString` to parse blob URLs, validates backup resources, sets encryption metadata fields, and records `lastOpenError` on invalid input. `listContainers` delegates discovery to local directory listing or blobstore index listing after ensuring a blobstore base URL has no resource path.

State and persistence behavior: The file itself persists no backup payload, but it formats metadata read elsewhere into `BackupDescription`. Time conversion reads the system timekeeper prefix with system-key and lock-aware transaction options. `lastOpenError` is process-global diagnostic state and the container cache is a static map keyed only by URL, with simulation exceptions for correctness.

Dependencies and integration points: It is the main factory joining CLI/agent URL strings to local, blobstore, and Azure implementations. It depends on `BackupAgentBase` for time formatting/parsing, `BackupContainerFileSystem` derivatives for concrete behavior, `IBlobStoreEndpoint` for cloud endpoints, `ReadYourWrites` and `KeyBackedTypes` for timekeeper access, and `JsonBuilder` for machine-readable descriptions.

Risks: The production cache key ignores proxy and encryption parameters, so callers rely on URL uniqueness and the simulation-only bypass for cases that intentionally vary encryption against the same file URL. Timekeeper conversion approximates versions from the nearest recorded epoch and can fail if the cluster has no records. URL diagnostics depend on `lastOpenError`, which is shared process state. Blobstore discovery rejects non-empty resource paths, which is correct for listing but easy for callers to confuse with opening a single backup.

Test signals: The `/backup/containers/url`, `/backup/containers_list`, and `/backup/time` tests in the filesystem container test area exercise URL opening/listing and timestamp round trips. Useful runtime signals are `BackupContainer`, `InvalidAzureBackupUrl`, and `BackupContainerDescribe*` traces plus JSON fields such as `Restorable`, log bounds, snapshot bytes, file-level encryption, and relative day calculations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BackupContainer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BackupContainerBlobStore.cpp -->
# sources/storage-engines/foundationdb/fdbclient/BackupContainerBlobStore.cpp

Purpose: This file implements the blobstore-backed `BackupContainerFileSystem` adapter. It maps backup container paths onto object-store buckets, keeps a separate index namespace for named backups, wraps object reads/writes in optional file encryption and read-ahead caching, and deletes backup data recursively.

Important APIs and types: The core type is `BackupContainerBlobStore` plus private `BackupContainerBlobStoreImpl`. Important methods are `dataPath`, `indexEntry`, `validateBackupUrl`, `readFile`, `writeFile`, `writeEntireFile`, `deleteFile`, `listFiles`, `create`, `exists`, `deleteContainer`, `listURLs`, and `getBucket`. The nested `BackupFile` adapts `IAsyncFile` append/sync behavior to `IBackupFile`.

Control flow: Backup data is stored under `data/<backup-name>/...` when used as a backup container. Index objects live under `backups/<backup-name>`, allowing backup names with slashes without confusing data layout. `create` ensures the bucket exists and writes the index object if missing, then waits for encryption setup when configured. Listing trims the raw `dataPath("")` prefix and URL-decodes object names from provider XML responses before returning container-relative names. Reads use `AsyncFileBlobStoreRead`, optionally `AsyncFileEncrypted`, then optional `AsyncFileReadAheadCache`. Writes use `AsyncFileBlobStoreWrite` and finish with `sync`.

State and persistence behavior: Persistent state consists of the object bucket, the backup index entry, and all backup data objects below the data prefix. The default bucket is `FDB_BACKUPS_V2`, but the URL `bucket` parameter overrides it and unknown parameters fail URL validation. `exists` checks only the index object, not full data content. `deleteContainer` first verifies the index exists, deletes all data-prefix objects through `IBlobStoreEndpoint::deleteRecursively`, then deletes the index entry.

Dependencies and integration points: It depends on `IBlobStoreEndpoint`, `AsyncFileBlobStore`, `AsyncFileEncrypted`, `AsyncFileReadAhead`, HTTP URL decoding, and the abstract naming/listing logic in `BackupContainerFileSystem`. It is constructed by `IBackupContainer::openContainer` after blob URL parsing and by `listContainers_impl` as a dummy object to derive bucket parameters.

Risks: `writeEntireFile` writes raw object content directly through the endpoint and does not apply file-level encryption, which is acceptable for property/index-style files but must not be used for encrypted data payloads unless intended. `validateBackupUrl` allows slashes in backup names, so the index/data namespace separation is essential. Listing relies on provider URL-decoded names and a correct prefix length. Delete ordering means interrupted deletes can leave an index or data prefix inconsistent until retried.

Test signals: The shared backup container simulation tests cover blob URLs when `FDB_TEST_BACKUP_URL` is supplied and exercise object writes, listings, descriptions, expiry, deletion, and edge file sizes such as multipart minimums. Runtime traces include `BackupContainerBlobStoreInvalidParameter`, `BackupContainerDoesNotExist`, and blob endpoint request/list/delete traces.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BackupContainerBlobStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BackupContainerBlobStore.h -->
# sources/storage-engines/foundationdb/fdbclient/BackupContainerBlobStore.h

Purpose: This header declares the final blobstore backup container class, the object-store implementation of `BackupContainerFileSystem`. It exposes the concrete API needed by the backup container factory while hiding path mapping and bucket/index details.

Important APIs and types: `BackupContainerBlobStore` inherits from `BackupContainerFileSystem` and `ReferenceCounted<BackupContainerBlobStore>`. It stores `Reference<IBlobStoreEndpoint> m_bstore`, backup resource name `m_name`, bucket `m_bucket`, and `isBackup`. Public members include the constructor, reference-count overrides, `getURLFormat`, `validateBackupUrl`, `readFile`, static `listURLs`, `writeFile`, `writeEntireFile`, `deleteFile`, `listFiles`, `create`, `exists`, `deleteContainer`, and `getBucket`. Private helpers `dataPath` and `indexEntry` define the persistent object layout.

Control flow: Callers do not instantiate this class directly except through the backup container factory or listing helper. After construction, all high-level backup operations flow through `BackupContainerFileSystem` APIs and are lowered into blobstore object operations by the `.cpp` implementation. The `friend class BackupContainerBlobStoreImpl` grants private helper access to static actor implementations.

State and persistence behavior: The header documents the state split: all backup data goes into one bucket, while backup-specific path prefixes and index entries determine existence and discovery. `exists` is explicitly defined as checking the index entry, which separates container identity from the presence of individual range/log/snapshot files.

Dependencies and integration points: It includes `AsyncFileBlobStore`, `BackupContainerFileSystem`, and `IBlobStore`, making it the typed bridge between backup filesystem semantics and provider-specific S3/GCS endpoint implementations. `IBackupContainer::getURLFormats` and `openContainer` rely on its static URL helpers.

Risks: The class is `final`, so behavior customization must happen in `IBlobStoreEndpoint` or the common filesystem layer. The `isBackup` flag changes path-prefix semantics, so non-backup use must be careful not to rely on backup index layout. Because encryption fields are inherited from `BackupContainerFileSystem`, constructor arguments must remain aligned with read/write implementations.

Test signals: Header-level contract is covered indirectly by compile-time use in `BackupContainer.cpp`, blobstore container tests, and any provider-specific backup URL tests. Behavioral signals come from the `.cpp` implementation: successful bucket/index creation, encrypted read/write wrapping, and URL validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BackupContainerBlobStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BackupContainerFileSystem.cpp -->
# sources/storage-engines/foundationdb/fdbclient/BackupContainerFileSystem.cpp

Purpose: This is the common filesystem-style backup container implementation shared by local, blobstore, and Azure backends. It defines backup file naming schemes, snapshot manifests, listing/parsing logic, backup description/restorability analysis, data expiry, restore-set selection, encryption metadata handling, version-property files, and extensive simulation tests.

Important APIs and types: Public methods include `writeLogFile`, `writeTaggedLogFile`, `writeRangePartitionedLogFile`, `writeRangeFile`, `writePartitionListFile`, `readKeyspaceSnapshot`, `writeKeyspaceSnapshotFile`, `listLogFiles`, `old_listRangeFiles`, `listRangeFiles`, `listKeyspaceSnapshots`, `dumpFileList`, `describeBackup`, `expireData`, `writeEncryptionMetadata`, `getSnapshotFileKeyRange`, `getRestoreSet`, `VersionProperty::{get,set,clear}`, `logBeginVersion`, `logEndVersion`, `expiredEndVersion`, `unreliableEndVersion`, `logType`, `encryptionMetadataFileName`, `setEncryptionKey`, and `createTestEncryptionKeyFile`. Internal helpers parse `RangeFile`, `LogFile`, and `KeyspaceSnapshotFile` names and compute continuity for default and partitioned logs.

Control flow: Writers generate deterministic directory layouts from versions: `logs/` and `plogs/` for mutation logs, `rlogs/` for range-partitioned logs, old `ranges/` for compatibility, `kvranges/snapshot.<version>/...` for range files, and `snapshots/` for JSON manifests. `describeBackup` verifies container existence, reads metadata properties, reads encryption metadata, falls back to scanning when metadata is missing or unsafe, lists logs and snapshots, computes contiguous log coverage, and marks snapshots/restorable version bounds. `getRestoreSet` walks snapshots from newest to oldest, reads each manifest, filters range files by requested key ranges, and finds matching log coverage to the target version. `expireData` describes the backup, resolves relative versions, checks whether expiry would preserve a requested restorable point unless forced, marks `unreliable_end_version` before deletion, deletes old logs/ranges/manifests with bounded concurrency, then advances `expired_end_version`.

State and persistence behavior: Persistent files include range/log payloads, JSON snapshot manifests with optional key-range maps or bulkdump metadata, version property files (`log_begin_version`, `log_end_version`, `expired_end_version`, `unreliable_end_version`, `mutation_log_type`), and `properties/encryption_metadata`. Encryption metadata is JSON with `is_encryption_enabled` and `encryption_block_size`; missing metadata is treated as legacy unencrypted, while malformed or inconsistent metadata is corrupt. The class also reads a global stream cipher key from an encryption key file and stores setup as a future.

Dependencies and integration points: It depends on `BackupAgent`, `IBackupContainer`, `JsonBuilder`, `StreamCipher`, `AsyncFileEncrypted`, backend `readFile`/`writeFile`/`listFiles` operations, file backup decode helpers, Flow unit tests, and client knobs for version bucket sizes, concurrency, encryption block size, multipart edge cases, and simulation behavior. It integrates directly with restore code through `RestorableFileSet` and with backup agents through file naming and manifest writes.

Risks: Restorability depends on filename parsing, sorted version intervals, metadata repair, and log continuity calculations. Expiry intentionally marks data unreliable before deletion, so interrupted operations preserve safety but can reduce reported restorability until cleanup completes. BulkDump and rangefile snapshots share base names with suffix logic for "both" mode, which is compatibility-sensitive. `writeEntireFileFallback` uses `&fileContents[0]`, so zero-length strings rely on current call sites avoiding invalid access. Encryption metadata handling is strict and converts most read errors into `file_not_readable`.

Test signals: In-file tests exercise local directory encrypted and unencrypted containers, optional external backup URL containers, URL listing, timestamp parsing, partitioned log continuity, non-partitioned log continuity, missing-log restorability, continuous log end metadata, expiry behavior, read/write verification, snapshot manifest key ranges, and delete-container behavior. Strong assertions include file counts, restorable set presence, min/max restorable versions, contiguous log end, metadata repair, and expected `backup_does_not_exist` after deletion.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BackupContainerFileSystem.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BackupContainerLocalDirectory.cpp -->
# sources/storage-engines/foundationdb/fdbclient/BackupContainerLocalDirectory.cpp

Purpose: This file implements `file://` backup containers on a local filesystem path. It provides atomic-ish append file creation, recursive listing, local deletion, URL discovery, optional file encryption, and simulation-specific file-opening workarounds.

Important APIs and types: The concrete class is `BackupContainerLocalDirectory`; the anonymous namespace contains `BackupFile`, an `IBackupFile` implementation with buffered writes and temp-to-final rename, plus `listFiles_impl`. Public methods implemented are `getURLFormat`, constructor URL validation, `listURLs`, `create`, `exists`, `readFile`, `writeFile`, `writeEntireFile`, `deleteFile`, `listFiles`, and `deleteContainer`.

Control flow: The constructor strips `file://`, removes trailing slashes, converts to an absolute path outside simulation unless relative paths are allowed by knob, and records a `backup_invalid_url` reason on invalid paths. Writes create parent directories, open a unique `.temp` file with atomic-create flags, optionally wrap it in `AsyncFileEncrypted`, buffer appends until `BACKUP_LOCAL_FILE_WRITE_BLOCK`, flush blocks to fixed offsets, truncate/sync, then rename to the final path. Reads open uncached read-only files, optionally create per-simulated-process symlinks ending in `.lnk`, and may wrap reads in randomized read-ahead cache during simulation.

State and persistence behavior: The local directory itself is the backup container. Listing recursively returns paths relative to `m_path`, hides `.part` and `.temp` files, and hides simulator `.lnk` artifacts. `create` intentionally does not create the directory for unencrypted local containers, because creation must happen on machines that actually write files. `deleteContainer` first calls `describeBackup` and refuses to erase a directory that does not look like a valid backup, then recursively removes it and reports a deletion count.

Dependencies and integration points: It depends on Flow platform filesystem helpers, `IAsyncFileSystem`, `AsyncFileEncrypted`, `AsyncFileReadAheadCache`, simulator process identity, fault injection, and the common `BackupContainerFileSystem` behavior for descriptions, encryption setup, and deletion validation. The factory in `BackupContainer.cpp` uses it for `file://` URLs.

Risks: Local containers are local to each agent host, so operators must ensure a shared filesystem or correct placement. Relative path handling differs between simulation and production and is knob-controlled. Simulation symlink creation assumes POSIX behavior and writable directories. `deleteContainer` is deliberately conservative but still ultimately erases `m_path` recursively after a successful description. Buffered writes plus rename protect readers from temp files, but interrupted writes leave hidden `.temp` files.

Test signals: In-file and common tests cover local directory containers with and without encryption, missing-log restorability, continuous log end, expiry, delete behavior, hidden temp files, read/write content verification, and time parsing. Fault injection points simulate blob-style HTTP request failures on local operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BackupContainerLocalDirectory.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BackupContainerLocalDirectory.h -->
# sources/storage-engines/foundationdb/fdbclient/BackupContainerLocalDirectory.h

Purpose: This header declares the local-filesystem `BackupContainerFileSystem` implementation for `file://` backup URLs. It is the factory-visible contract for local backup containers.

Important APIs and types: `BackupContainerLocalDirectory` inherits from `BackupContainerFileSystem` and `ReferenceCounted<BackupContainerLocalDirectory>`. It declares reference-count overrides, static `getURLFormat`, the constructor taking a URL plus optional encryption key and block size, static `listURLs`, and final overrides for `create`, `exists`, `readFile`, `writeFile`, `writeEntireFile`, `deleteFile`, `listFiles`, and `deleteContainer`. Its only direct data member is `std::string m_path`.

Control flow: The header keeps all implementation details in the `.cpp`; callers use it through `IBackupContainer` or `BackupContainerFileSystem` references. Static URL helpers let the shared factory advertise and discover local backup containers.

State and persistence behavior: `m_path` is the root of all persistent state for the container. Existence is defined as directory existence, while file-level format, metadata properties, encryption metadata, and backup manifests are inherited from the common filesystem layer.

Dependencies and integration points: It includes `BackupContainerFileSystem.h` and Flow futures/reference counting. It is included by `BackupContainer.cpp` and `BackupContainerFileSystem.cpp` for factory dispatch and tests.

Risks: Since the class exposes only a root path and filesystem operations, safety depends on constructor validation and the `.cpp` delete guard. Any new method must preserve the common container contract, especially relative paths, encryption setup, and source-tree-style path listing.

Test signals: Compile-time use verifies that local containers satisfy all abstract `BackupContainerFileSystem` methods. Runtime behavior is covered by `/backup/containers/localdir/*` tests and shared backup container tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BackupContainerLocalDirectory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BackupTLSConfig.cpp -->
# sources/storage-engines/foundationdb/fdbclient/BackupTLSConfig.cpp

Purpose: This file applies backup-agent TLS and blob credential configuration before network use. It bridges command-line or environment-provided backup TLS settings into global FoundationDB network options and blob credential file discovery.

Important APIs and types: It implements `BackupTLSConfig::setupBlobCredentials` and `BackupTLSConfig::setupTLS`. The relevant fields are `blobCredentials`, `tlsCertPath`, `tlsCAPath`, `tlsKeyPath`, `tlsPassword`, and `tlsVerifyPeers`. It uses `g_network->global(INetwork::enBlobCredentialFiles)` and `setNetworkOption` with `FDBNetworkOptions`.

Control flow: `setupBlobCredentials` reads `FDB_BLOB_CREDENTIALS`, splits it on `:`, ignores empty entries, appends them to the instance list, then appends all collected credential paths to the network-global blob credential vector if present. `setupTLS` conditionally sets certificate path, CA path, TLS password, key path, and peer verification. Each option is wrapped in its own `try/catch`; failures print a clear stderr message and return `false`.

State and persistence behavior: No files are written. The durable inputs are credential/TLS files outside this code. Runtime state is process-global network configuration and the global blob credential file vector consumed by `IBlobStoreEndpoint::updateSecret`.

Dependencies and integration points: It depends on `NativeAPI.actor.h`, `flow/network.h`, `BackupTLSConfig.h`, and the blob credential loading code in `BlobStoreCommon.cpp`. It is used by backup command-line tools and agents before opening blobstore containers or TLS cluster connections.

Risks: `FDB_BLOB_CREDENTIALS` uses `:` as a separator, which is natural on Unix but awkward for Windows-style paths. TLS options must be applied before network initialization or connection use. Error reporting goes to stderr, so callers must honor the boolean return value. Blob credential global state is append-only for the process and can accumulate duplicates.

Test signals: There are no in-file tests. Useful validation is startup behavior with valid/invalid TLS paths, blobstore authentication with credentials supplied by environment and command line, and errors emitted by `BlobCredentialFile*` traces when `BlobStoreCommon` reads the configured files.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BackupTLSConfig.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BlobStoreCommon.cpp -->
# sources/storage-engines/foundationdb/fdbclient/BlobStoreCommon.cpp

Purpose: This file implements provider-neutral blobstore endpoint behavior: URL parsing, knob serialization, credential file loading, recursive listing/deletion, whole-object writes, connection pooling, proxy/TLS connection setup, request retries, rate limiting, stats, and common HTTP error mapping.

Important APIs and types: Key types and functions include `IBlobStoreEndpoint::ConnectionPoolData::~ConnectionPoolData`, `Stats::getJSON`, `Stats::operator-`, `BlobKnobs::{BlobKnobs,set,getURLParameters}`, `IBlobStoreEndpoint::tryReadJSONFile`, `getResourceURL`, `fromString`, `updateSecret`, `listObjects`, `deleteRecursively`, `writeEntireFile`, `connect`, `returnConnection`, and `doRequest`. It constructs `S3BlobStoreEndpoint` or `GCSBlobStoreEndpoint` based on URL provider parameters.

Control flow: `fromString` normalizes encoded ampersands, validates the `blobstore://` prefix, parses optional credentials, host/service, resource, proxy, provider, region, GCS project, extra headers, and numeric knob parameters. Unknown parameters are either returned to the caller as ignored backup-specific parameters or treated as URL errors. Requests acquire endpoint concurrency, obtain or create a reusable connection, refresh credentials if needed, merge headers, apply provider auth headers, rate-limit, send via `HTTP::doRequest`, accept configured success codes, and retry retryable errors or 500/502/503/429 responses with exponential backoff and `Retry-After` handling.

State and persistence behavior: Runtime state includes global aggregate request stats, per-endpoint blob stats, rate limiters, a connection pool with expiration times, and endpoint credentials loaded from network-global JSON credential files. `deleteRecursively` streams listings and issues bounded concurrent deletes while updating optional deleted count/byte counters. `writeEntireFile` packetizes content, computes MD5 or SHA-256 base64 integrity hashes depending on `enable_object_integrity_check`, and delegates provider-specific buffer upload.

Dependencies and integration points: It depends on S3 and GCS endpoint subclasses, Flow networking, HTTP, hostname parsing, async files, generic actors, OpenSSL SHA, MD5, base64, and client knobs. It is used by `BackupContainerBlobStore`, async blob files, backup TLS credential setup, and any code constructing blobstore resource URLs.

Risks: URL parsing accepts many short knob aliases and all knob values are numeric, so typo handling depends on whether the caller supplies an ignored-parameter map. Pooled connections must be closed in simulation to satisfy Sim2Conn invariants. Retrying must reset packet buffer sent counts and request headers each attempt; this file explicitly does so. 429 attempts do not count against retry limits, so persistent throttling can delay operations. Whole-file writes reject content larger than `multipart_max_part_size`; larger payloads need multipart paths elsewhere.

Test signals: There are no direct unit tests in this file, but blob backup tests exercise URL parsing, list/delete/write requests, read cache knobs, request failures, and simulation connection behavior. Trace signals include `BlobStoreEndpointBadURL`, credential-file warnings, connection reuse/new/expired counters, `BlobStoreDoRequestError`, retryable request failures, connect timeout mapping, and per-endpoint stats JSON.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BlobStoreCommon.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BuildFlags.h.in -->
# sources/storage-engines/foundationdb/fdbclient/BuildFlags.h.in

Purpose: This CMake-configured header template exposes build metadata as constants and a JSON string. It records compile date/time, git hash, FoundationDB version, architecture, compiler, Boost version, CMake version, ccache use, glibc version when available, and the active C++ standard.

Important APIs and types: It defines `C_VERSION_MAJOR`, `C_VERSION_MINOR`, constants such as `kDate`, `kTime`, `kGitHash`, `kFdbVersion`, `kArch`, `kCompiler`, `kBoostVersion`, `kCMakeVersion`, `kCCacheEnabled`, `kCVersionMajor`, `kCVersionMinor`, `kCppStandard`, and the function `jsonBuildInformation()`. It uses `JSONDoc` and `json_spirit`.

Control flow: At configure time, CMake substitutes placeholders like `@FDB_VERSION@`, `@CURRENT_GIT_VERSION_WNL@`, and compiler/system values. At compile time, preprocessor macros fill date, time, glibc, Boost, and `__cplusplus`. `jsonBuildInformation` creates a JSON object, sets each metadata field, formats glibc as `major.minor`, and returns pretty-printed JSON with a trailing newline.

State and persistence behavior: There is no runtime persistence. The generated header bakes build state into every binary that includes it. `__DATE__` and `__TIME__` make outputs sensitive to compile time and can affect reproducibility unless the build system controls those macros.

Dependencies and integration points: This template is consumed by the build system to generate `BuildFlags.h`. It depends on Boost version macros being available through build includes and on `fdbclient/JSONDoc.h`. The resulting JSON is typically surfaced by binaries or diagnostics that report build provenance.

Risks: Defining non-`inline` namespace-scope constants and a non-`inline` function in a header can create ODR/linkage concerns if included in multiple translation units without internal linkage expectations. Placeholder substitution must escape values appropriately for C++ string literals. Non-glibc platforms report `0.0`, which consumers must not treat as an actual libc version.

Test signals: Validation consists of successful configured builds and JSON parseability of `jsonBuildInformation()`. Useful checks assert that substituted fields are not raw `@...@` placeholders in generated artifacts and that `cpp_standard`/glibc fields match the compiler environment.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BuildFlags.h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BulkDumping.cpp -->
# sources/storage-engines/foundationdb/fdbclient/BulkDumping.cpp

Purpose: This small file provides the construction entry point for bulk dump jobs in fdbclient. It converts caller-supplied range, job root, bulk load type, and transport method into a `BulkDumpState`.

Important APIs and types: It includes `fdbclient/BulkDumping.h` and implements `createBulkDumpJob(const KeyRange& range, const std::string& jobRoot, const BulkLoadType& type, const BulkLoadTransportMethod& transportMethod)`. The return type is `BulkDumpState`.

Control flow: The function has no branching or side effects. It returns `BulkDumpState(range, type, transportMethod, jobRoot)`, preserving the caller-provided values while matching the constructor's argument order.

State and persistence behavior: No state is persisted in this file. Any durable job metadata, dump manifest, or transport-specific state is owned by `BulkDumpState` and downstream bulk load/dump code.

Dependencies and integration points: This file is a thin linkage point for code that wants to create bulk dump jobs without directly invoking the `BulkDumpState` constructor. Snapshot manifest support in `BackupContainerFileSystem.cpp` recognizes bulkdump metadata, so this function is part of the broader backup and bulk-load ecosystem even though it does not touch containers directly.

Risks: The main risk is constructor-order drift: if `BulkDumpState` changes, this wrapper must be updated so `jobRoot`, type, and transport do not get misbound. Because it performs no validation, callers or `BulkDumpState` must reject invalid ranges, empty roots, or unsupported transport combinations.

Test signals: Tests should verify that a created job preserves the key range, root path, bulk load type, and transport method. Integration signals come from bulk dump snapshot manifests and restore/import workflows that consume `BulkDumpState`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BulkDumping.cpp -->

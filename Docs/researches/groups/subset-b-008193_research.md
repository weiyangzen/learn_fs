# subset-b-008193 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-sets.go -->
# sources/object-store/minio/cmd/erasure-sets.go

## Purpose
Implements the multi-set erasure object layer that presents many fixed erasure sets as one `ObjectLayer`. It owns disk placement, reconnect monitoring, per-set lockers, object-name-to-set routing, fan-out operations that must span sets, and healing of missing `format.json` files on replacement disks.

## Important APIs, types, and functions
- `erasureSets` holds `sets`, reference `formatErasureV3`, protected `erasureDisks`, distributed lockers, endpoints, set geometry, pool index, distribution algorithm, and deployment ID.
- `connectEndpoint`, `findDiskIndex`, and `findDiskIndexByDiskID` validate a drive against the reference format before a `StorageAPI` is accepted into a set slot.
- `newErasureSets` builds per-set `erasureObjects`, lockers, endpoint closures, cleanup goroutines, and the background disk reconnect loop.
- `hashKey`, `sipHashMod`, `crcHashMod`, `getHashedSetIndex`, and `getHashedSet` are the object placement boundary.
- Object APIs such as `PutObject`, `GetObjectNInfo`, multipart methods, metadata/tag/tier methods, and `HealObject` delegate to the hashed set.
- `DeleteObjects`, `deletePrefix`, `StorageInfo`, `LocalStorageInfo`, `Shutdown`, and cleanup routines fan out across sets when needed.
- `HealFormat`, `formatsToDrivesInfo`, and `newHealFormatSets` integration repair fresh unformatted drives without changing established topology.

## Control flow
Startup constructs endpoint strings, lockers keyed by host, and one `erasureObjects` per set. Initial disks are placed by disk ID, then periodic `monitorAndConnectEndpoints` calls `connectDisks`, which tries only missing/offline/reconnected endpoints, loads `format.json`, checks topology, and installs the disk under `erasureDisksMu`. Normal object traffic hashes the object name using the format's distribution algorithm and forwards to exactly one set. Bulk delete groups input objects by hashed set and runs per-set deletes concurrently, while prefix force delete walks all sets. Copy optimizes metadata-only same-set copies and otherwise streams source data into the destination set.

## State and persistence behavior
The persistent authority is `format.json`: deployment ID, set UUID matrix, per-drive `This` UUID, and distribution algorithm. Runtime state includes the mutable disk matrix, local drive maps, lock clients, cleanup timers, and audit tags. `HealFormat` writes missing `format.json` files to unformatted replacement drives, records before/after drive states, updates local drive maps, and may start active write monitoring.

## Dependencies and integration points
This file integrates `StorageAPI`, `formatErasureV3`, `erasureObjects`, distributed `dsync` locks, madmin heal/storage types, global API cleanup intervals, global background heal state, audit logging, site/decommission/tiering object APIs, and endpoint/pool metadata. It also depends on SipHash/CRC for stable placement and `xsync.MapOf` for deleted bucket discovery.

## Risks and edge cases
Changing hash algorithms or deployment ID handling can move objects across sets. Incorrect disk reordering checks can accept the wrong physical drive or reject a valid replacement. `HealFormat` is sensitive to quorum, reference-format equality, unformatted/offline/corrupt distinction, and local-vs-remote reconnection behavior. Background cleanup and reconnect goroutines rely on global timers and can mask operational races if tests run with global state.

## Test signals
`erasure-sets_test.go` covers CRC/SipHash stability, invalid cardinality and unknown algorithms, creation of a 16-drive erasure set, and stable object-to-set mapping. Broader healing and object routing are mostly exercised by integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-sets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-sets_test.go -->
# sources/object-store/minio/cmd/erasure-sets_test.go

## Purpose
Unit and benchmark coverage for erasure-set hashing and basic set initialization. It protects object placement compatibility and verifies that a formatted endpoint set can be wrapped as an `erasureSets` object layer.

## Important APIs, types, and functions
- `BenchmarkCrcHash` and `BenchmarkSipHash` measure placement hash performance for key sizes from 16 to 1024 bytes.
- `TestSipHashMod` and `TestCrcHashMod` assert fixed bucket indexes for representative object names, Unicode, paths, and raw bytes.
- `TestNewErasureSets` exercises endpoint parsing, `waitForFormatErasure`, parity calculation through `ecDrivesNoConfig`, and `newErasureSets`.
- `TestHashedLayer` constructs synthetic sets and asserts `getHashedSet` returns the expected set under legacy `CRCMOD`.

## Control flow
Hash tests feed table entries into `hashKey` with a fixed UUID and cardinality 200, then separately assert `-1` for invalid cardinality or unknown algorithms. Initialization allocates 16 temporary disk paths, checks invalid `waitForFormatErasure` calls, formats disks, creates a `PoolEndpoints` wrapper, computes default parity, and initializes the erasure set layer. `TestHashedLayer` uses pointer identity to ensure object names map to stable set instances.

## State and persistence behavior
Tests create temporary disk paths and format metadata under them through the normal erasure formatting path. No long-lived state is intended; cleanup is via deferred `os.RemoveAll`. The fixed `testUUID` makes SipHash outputs deterministic.

## Dependencies and integration points
The tests use endpoint parsing, filesystem-backed storage setup, format waiting, parity lookup, erasure-set construction, and global test temp directory helpers. They are tightly coupled to placement algorithms in `erasure-sets.go`.

## Risks and edge cases
The expected hash indexes are compatibility fixtures; a legitimate algorithm change requires an explicit migration story. Initialization covers a single local 16-drive setup and does not validate reconnect, multi-pool, distributed lockers, or heal-format behavior.

## Test signals
Signals are exact hash outputs, exact invalid-argument errors from format waiting, successful `newErasureSets`, and pointer-equality mapping for legacy hashed sets. Benchmarks provide allocation/performance regression signals for hashing and do not assert behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-sets_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-utils.go -->
# sources/object-store/minio/cmd/erasure-utils.go

## Purpose
Small erasure-coding helper layer for reconstructing contiguous data from encoded shards and extracting deployment IDs embedded in multipart upload IDs for site-replication forwarding.

## Important APIs, types, and functions
- `getDataBlockLen` totals data-shard lengths across the first `dataBlocks` entries.
- `writeDataBlocks` writes a requested range from data shards to an `io.Writer`, honoring offset and length across shard boundaries.
- `getDeplIDFromUpload` decodes a base64 raw URL upload ID and returns the prefix before the first dot.

## Control flow
`writeDataBlocks` rejects negative offset/length, checks shard count and available data length, skips whole shards until the requested offset is reached, then writes either the remaining full shard or the final truncated slice. `getDeplIDFromUpload` decodes the upload ID, splits at the first dot, and returns an error if the encoded value is malformed.

## State and persistence behavior
The file has no persistent state. Its output is derived entirely from in-memory shard slices or a request upload ID. `writeDataBlocks` accepts a context but does not currently test it inside the loop, so cancellation must be handled by the writer or caller.

## Dependencies and integration points
`writeDataBlocks` returns Reed-Solomon errors used by erasure decode paths and is consumed by tests in `erasure_test.go`. `getDeplIDFromUpload` is used by upload forwarding middleware to route multipart operations to the peer deployment that initiated the upload.

## Risks and edge cases
Range math must stay correct across uneven shard sizes, short data, and partial final writes. `writeDataBlocks` increments by bytes reported by the writer but does not verify full writes without error. Upload ID parsing assumes deployment ID and upload suffix are dot-separated after raw URL base64 decoding.

## Test signals
`TestErasureEncodeDecode` reconstructs shards and calls `writeDataBlocks` to compare decoded bytes with original random data. Upload ID parsing is indirectly covered through site-replication upload forwarding behavior elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure.go -->
# sources/object-store/minio/cmd/erasure.go

## Purpose
Defines the single erasure-set object layer state and shared utilities for disk status, storage info, online-disk selection, cleanup, and namespace scanning. It is the per-set implementation that `erasureSets` composes and routes object operations into.

## Important APIs, types, and functions
- `erasureObjects` stores set geometry, pool/set indexes, disk/locker/endpoint closures, and namespace lock map.
- `defaultWQuorum` and `defaultRQuorum` compute write/read quorums from data/parity layout.
- `diskErrToDriveState`, `getDisksInfo`, `getOnlineOfflineDisksStats`, and `getStorageInfo` translate storage errors and metrics into admin API structures.
- `getOnlineDisksWithHealingAndInfo` orders usable disks before scanning and healing disks.
- `cleanupDeletedObjects` removes `.minio.sys/tmp/.trash` contents on local disks using deadline workers and dynamic sleepers.
- `nsScanner` performs bucket data-usage scanning, cache loading/saving, bucket randomization, per-disk worker scheduling, and periodic update publication.

## Control flow
Administrative calls snapshot the current disk slice from the closure and query disks concurrently. Disk selection shuffles indexes, records errors, filters offline/healing disks, and orders non-scanning disks before scanning and optional healing disks. The namespace scanner loads the prior root cache, randomizes bucket order with new buckets first, starts a saver goroutine that periodically emits cache clones, bounds scanner parallelism by `GOMAXPROCS`, and runs `NSScanner` on selected disks while preserving per-bucket cache state.

## State and persistence behavior
Persistent state includes data-usage cache files saved through the erasure object layer and `.trash` directories removed from local drive paths. Runtime state is mostly closures into the parent `erasureSets`, disk health snapshots, and scanner channels. Storage-info output exposes disk UUIDs, mount paths, inode stats, healing/scanning flags, and per-API metrics.

## Dependencies and integration points
This file integrates `StorageAPI`, endpoint metadata, `madmin` disk/storage structures, MinIO disk scanners, data-usage cache types, global drive and cleanup configs, namespace locking, and error quorum reducers used by bucket metadata operations.

## Risks and edge cases
Quorum formulas affect availability semantics. Disk state translation must distinguish offline, corrupt, unformatted, permission, faulty, and root-mount conditions. Scanner correctness depends on consuming the update channel, saving final state on close, and not scanning only healing disks. The utilization calculation uses integer division before conversion, which may under-report non-100% usage.

## Test signals
Direct tests in this group focus on erasure encode/decode setup rather than these admin/scanner paths. The main signals come from integration tests that inspect admin disk states, scanner data-usage caches, healing behavior, and storage info output.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure_test.go -->
# sources/object-store/minio/cmd/erasure_test.go

## Purpose
Tests Reed-Solomon erasure encode/decode behavior and provides a helper setup for filesystem-backed erasure tests. It validates that data and parity reconstruction produce original payload bytes under supported shard loss patterns.

## Important APIs, types, and functions
- `erasureEncodeDecodeTests` enumerates data/parity counts, missing shard counts, whether parity should be reconstructed, and expected failure.
- `TestErasureEncodeDecode` drives `NewErasure`, `EncodeData`, `DecodeDataAndParityBlocks`, `DecodeDataBlocks`, and `writeDataBlocks`.
- `erasureTestSetup` and `newErasureTestSetup` create temporary XL storage disks and a test bucket for later erasure tests.

## Control flow
The test fills a random 256-byte buffer, encodes it, nils selected data and parity shards, decodes with or without parity reconstruction, validates expected success/failure, checks reconstructed shard presence when successful, writes data shards back to a buffer, and compares with the original bytes.

## State and persistence behavior
The main test uses in-memory buffers. `newErasureTestSetup` creates filesystem-backed disks and a `testbucket` volume, returning paths and `StorageAPI` handles for callers to clean up.

## Dependencies and integration points
This test depends on MinIO's erasure implementation, Reed-Solomon semantics, random data generation, `writeDataBlocks` from `erasure-utils.go`, and XL storage test setup helpers.

## Risks and edge cases
The table covers several shard loss combinations but uses one small payload size. It verifies byte equality but not large-object block boundaries, checksums, writer short-write behavior, or context cancellation. Failure expectations encode erasure tolerance limits and will need updates if quorum/reconstruction policy changes.

## Test signals
Signals include expected decode errors for unrecoverable shard loss, non-nil reconstructed shards for successful cases, and exact decoded byte equality with original random data.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/etcd.go -->
# sources/object-store/minio/cmd/etcd.go

## Purpose
Wraps etcd v3 key operations used by MinIO configuration and bucket DNS/federation code, normalizing timeout errors and applying a consistent operation timeout.

## Important APIs, types, and functions
- `errEtcdUnreachable` is the user-facing sentinel for deadline failures.
- `etcdErrToErr` maps nil, `context.DeadlineExceeded`, and other etcd errors into MinIO-style errors with endpoint context.
- `saveKeyEtcdWithTTL`, `saveKeyEtcd`, `deleteKeyEtcd`, and `readKeyEtcd` implement grant/put, put, delete, and get operations.

## Control flow
Every public helper creates a timeout context with `defaultContextTimeout`. TTL saves first grant a lease, then put the key with that lease. Normal saves optionally delegate to TTL mode. Reads return `errConfigNotFound` if etcd returns no matching key.

## State and persistence behavior
State is persisted in the configured etcd cluster under caller-provided keys. TTL writes depend on etcd lease expiration. The helper itself stores no process-local state.

## Dependencies and integration points
The file depends on `go.etcd.io/etcd/client/v3`, MinIO logging helpers, `defaultContextTimeout`, `options` with TTL, and `errConfigNotFound`. It is used by centralized config, bucket DNS, federation, and health/readiness code that checks `globalEtcdClient`.

## Risks and edge cases
Only `context.DeadlineExceeded` is treated as unreachable; other connectivity failures become generic unexpected errors. TTL grant uses the same timeout as put, so slow etcd can fail before writes occur. `readKeyEtcd` iterates returned KVs even though exact-key reads normally return only one match.

## Test signals
No direct tests in this group. Expected signals are integration paths that simulate missing config, unreachable etcd in readiness checks, and successful centralized config reads/writes.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/etcd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/event-notification.go -->
# sources/object-store/minio/cmd/event-notification.go

## Purpose
Implements the bucket event notification dispatcher that maps bucket notification rules to target IDs, builds S3-compatible event payloads, and sends events to configured targets and HTTP listeners.

## Important APIs, types, and functions
- `EventNotifier` owns an `event.TargetList` and bucket-to-`event.RulesMap` map under an RW mutex.
- `NewEventNotifier`, `GetARNList`, `InitBucketTargets`, `AddRulesMap`, `RemoveNotification`, `RemoveAllBucketTargets`, `Targets`, and `Send` manage notifier state and dispatch.
- `eventArgs` captures event name, bucket, object info, request/response data, host, and user agent.
- `eventArgs.ToEvent` builds the `event.Event` object.
- `sendEvent` strips sensitive metadata, publishes listener events, and invokes `globalEventNotifier`.

## Control flow
Bucket metadata loads notification configs through `set`, validates against registered targets, and stores a rules map. On an object event, `sendEvent` ignores source-replication requests, normalizes actual size, removes encryption/internal metadata, publishes unescaped events to subscribed HTTP listeners, and asks `EventNotifier.Send` to match bucket/object rules and send an escaped event to targets. Target sending can be synchronous based on API config.

## State and persistence behavior
Notification rules are runtime maps derived from persisted bucket metadata. Target definitions come from global notification target configuration. Events include request IDs, node IDs, origin endpoint, deployment ID, object version/ETag/size/content type/user metadata, and sequencer derived from object mod time or current time.

## Dependencies and integration points
Integrates bucket metadata, `internal/event`, target lists, global site region, global API sync-events config, global HTTP listener pubsub, encryption metadata scrubbing, object info sizing, and policy ARN formatting.

## Risks and edge cases
Rule map updates must clone input to avoid caller mutation. Sensitive metadata scrubbing is critical before publishing. Remove events intentionally omit object ETag/size/user metadata. `GetARNList` hides `httpclient+` listener targets. `ToEvent` assumes response element keys exist and falls back to first API endpoint when `globalMinioEndpoint` is empty.

## Test signals
No direct tests here. Signals normally include bucket notification integration tests, ListenNotification subscribers, target delivery behavior, source-replication suppression, and validation errors for missing ARNs.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/event-notification.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/fmt-gen.go -->
# sources/object-store/minio/cmd/fmt-gen.go

## Purpose
Defines the hidden `fmt-gen` CLI command that generates a `format.json.zip` bundle for an erasure server pool without contacting drives. It is an operational tool for prebuilding per-drive format files.

## Important APIs, types, and functions
- `fmtGenFlags` accepts parity, deployment ID, and address flags.
- `fmtGenCmd` registers hidden command metadata, usage text, global flags, and `fmtGenMain`.
- `fmtGenMain` builds server context/endpoints, creates `format.json.zip`, generates `formatErasureV3` layouts per pool, and embeds one `format.json` per drive path.

## Control flow
The command parses common server arguments, creates endpoint pools, opens a zip writer, loops through each pool, creates a new erasure format matching set count and drives per set, optionally applies the requested deployment ID, clones the format for each drive with `Erasure.This` set to that drive's UUID, marshals JSON, and writes it under `host/path/.minio.sys/format.json` in the zip.

## State and persistence behavior
The only output is local `format.json.zip`. The generated JSON contains deployment ID, backend format, erasure version, distribution algorithm, set UUID matrix, and per-drive `This` UUID. It does not mutate actual storage endpoints.

## Dependencies and integration points
Depends on MinIO CLI, endpoint layout parsing, `newFormatErasureV3`, zip embedding helpers, and common server context initialization. It shares the format schema with startup and healing code in `format-erasure.go`.

## Risks and edge cases
Because output is topology-defining, endpoint parsing or drive order mistakes can generate unusable or dangerous format files. The `parity` flag is declared but not used directly in this file. Existing `format.json.zip` is overwritten by `os.Create`.

## Test signals
No direct tests in this group. Operational validation is that the zip contains one correctly addressed `format.json` per endpoint and that startup accepts the generated layout.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/fmt-gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/format-erasure.go -->
# sources/object-store/minio/cmd/format-erasure.go

## Purpose
Defines erasure `format.json` schemas, migration, validation, quorum selection, disk initialization, and replacement-disk format generation. This is the persistence contract that prevents drive-order corruption and keeps erasure deployments stable across restarts and healing.

## Important APIs, types, and functions
- Constants define backend names, erasure versions, distribution algorithms, and the offline disk UUID.
- `formatErasureV1`, `formatErasureV2`, and `formatErasureV3` model historical and current `format.json` forms.
- `newFormatErasureV3`, `Drives`, and `Clone` create and copy layouts.
- `formatGetBackendErasureVersion`, `formatErasureMigrate`, `formatErasureMigrateV1ToV2`, and `formatErasureMigrateV2ToV3` upgrade old formats.
- `loadFormatErasureAll`, `loadFormatErasure`, `saveFormatErasure`, and `saveFormatErasureAll` read/write disk metadata.
- `checkFormatErasureValue`, `checkFormatErasureValues`, `formatErasureV3Check`, and `getFormatErasureInQuorum` validate format consistency.
- `initStorageDisksWithErrors`, `initFormatErasure`, `fixFormatErasureV3`, `ecDrivesNoConfig`, and `newHealFormatSets` support bootstrap and healing.

## Control flow
Bootstrap opens all endpoints concurrently, creates a reference layout, clones it for each drive with a unique `This` UUID, warns if a host has too many drives in a set, writes each format through a temporary file plus rename, and returns a quorum reference format with `This` cleared. Startup loads formats concurrently, validates version/backend/drive count/set width, then selects the majority drive count as the reference. Migration reads existing JSON, detects erasure version, upgrades V1 to V2, then V2 to V3, moving old multipart data to a trash path during V2-to-V3 migration.

## State and persistence behavior
Persistent state is `.minio.sys/format.json` on every disk. Writes are intended to be atomic at the storage layer by writing a UUID-named temp file and renaming it to `format.json`; heal writes may also persist a healing tracker. V2-to-V3 migration renames `.minio.sys/multipart` into `.minio.sys/tmp/.trash/<uuid>`.

## Dependencies and integration points
Integrates storage disks, endpoint topology, storage-class parity lookup, healing trackers, quorum reducers, logger/color warnings, filesystem migration helpers, and format consumers in `erasure-sets.go`.

## Risks and edge cases
This file is high risk: wrong quorum logic, UUID matching, set-size validation, or migration behavior can make data unavailable or accept foreign drives. `getFormatErasureInQuorum` groups by total drive count rather than a full hash, relying on later strict checks. `fixFormatErasureV3` only repairs empty `This` for local single-set migrated formats.

## Test signals
`format-erasure_test.go` covers empty `This` repair, V1-to-V3 migration, invalid format values, quorum selection/check failures, healing format generation, and benchmarks for quorum and storage initialization.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/format-erasure.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/format-erasure_test.go -->
# sources/object-store/minio/cmd/format-erasure_test.go

## Purpose
Unit and benchmark coverage for erasure format migration, validation, quorum selection, repair, and initialization scaling. It protects the disk metadata compatibility layer used by erasure startup and healing.

## Important APIs, types, and functions
- `TestFixFormatV3` verifies local repair of empty `Erasure.This`.
- `TestFormatErasureEmpty` checks detection of empty `This` while ignoring nil formats.
- `TestFormatErasureMigrate` validates V1-to-V3 migration and rejection of unknown backend/version.
- `TestCheckFormatErasureValue` exercises invalid metadata fields.
- `TestGetFormatErasureInQuorumCheck` validates quorum reference selection and strict format comparison failures.
- `getFormatErasureInQuorumOld` and benchmarks compare old hash-based quorum with current drive-count quorum.
- `TestNewFormatSets` verifies `newHealFormatSets` preserves deployment ID.
- Storage initialization benchmarks cover hundreds to thousands of endpoints.

## Control flow
Tests build synthetic format layouts, clone them across disk slots, mutate selected fields to simulate missing disks or corruption, and assert validation results. Migration writes an old `format.json` to a temp disk root, runs migration, then reads back the file to assert version, UUID, and set preservation. Benchmarks create large format arrays or endpoint lists and repeatedly run quorum or initialization code.

## State and persistence behavior
Several tests write temp `format.json` files and temporary disk directories, all under test-managed roots. Benchmarks allocate random disk paths. The tested persisted state is the JSON schema and its migration side effects.

## Dependencies and integration points
Depends on temp disk helpers, endpoint construction, JSON marshal/unmarshal, filesystem writes, SHA-256 for the old quorum implementation, and erasure format APIs from `format-erasure.go`.

## Risks and edge cases
Some invalid cases use intentionally synthetic formats that may not match all production invalid states. The quorum test checks loss of more than half the formats but does not cover same drive count with conflicting UUID matrix in current quorum selection beyond later `formatErasureV3Check` mutation cases. Benchmarks do not clean up all random disk paths in the shown helper.

## Test signals
Signals are exact success/failure of migration, repaired `This` UUID equality, invalid-value errors, strict mismatch failures for set count, set size, and UUID changes, `errErasureReadQuorum` when quorum is lost, deployment ID preservation in heal formats, and allocation/runtime benchmark metrics.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/format-erasure_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/format-meta.go -->
# sources/object-store/minio/cmd/format-meta.go

## Purpose
Defines the common top-level metadata embedded by backend-specific `format.json` schemas. It provides the shared version, backend format, and deployment ID fields used by erasure format code.

## Important APIs, types, and functions
- `formatConfigFile` names the persisted metadata file: `format.json`.
- `formatMetaVersionV1` is the current top-level metadata schema version.
- `formatMetaV1` contains JSON fields `version`, `format`, and `id`.

## Control flow
There is no executable control flow. Backend-specific structs embed `formatMetaV1` and add a backend object such as `xl`.

## State and persistence behavior
The struct represents on-disk `.minio.sys/format.json` state. `Version` guards schema compatibility, `Format` selects backend implementation, and `ID` is the deployment identifier used by hashing, replication, and operational identity.

## Dependencies and integration points
Used by `format-erasure.go` and other backend format files. Startup, migration, heal format generation, and `fmt-gen` all rely on these fields.

## Risks and edge cases
Changing this schema would require migration across all backend format implementations. Incorrect deployment ID preservation can affect object placement and replication identity.

## Test signals
Tests in `format-erasure_test.go` indirectly validate `Version`, `Format`, and `ID` behavior during migration, validation, quorum selection, and heal-format creation.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/format-meta.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/format_string.go -->
# sources/object-store/minio/cmd/format_string.go

## Purpose
Generated `stringer` output for the `format` enum from `untar.go`. It converts compression/archive format constants into stable human-readable strings.

## Important APIs, types, and functions
- Compile-time index checks in `_()` ensure enum values still match generated ordering.
- `_format_name` and `_format_index` encode names for `Unknown`, `Gzip`, `Zstd`, `LZ4`, `S2`, and `BZ2`.
- `(format).String()` returns the enum name or `format(<n>)` for out-of-range values.

## Control flow
The string method bounds-checks the enum and slices the generated name table by index offsets. Invalid values are formatted with `strconv.FormatInt`.

## State and persistence behavior
No runtime or persistent state. It is generated code and should be regenerated rather than manually edited when enum constants change.

## Dependencies and integration points
Used wherever MinIO displays or logs the `format` enum. The file depends only on `strconv` and enum constants defined elsewhere.

## Risks and edge cases
Manual edits can desynchronize constants and strings. The compile-time array-index checks catch changed numeric constants during build.

## Test signals
No direct tests in this group; build success is the primary signal that generated constants match enum values.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/format_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/ftp-server-driver.go -->
# sources/object-store/minio/cmd/ftp-server-driver.go

## Purpose
Implements the goftp server driver that maps FTP filesystem operations to MinIO S3 operations through the MinIO Go client. It also authenticates FTP users against MinIO IAM or LDAP and publishes FTP trace metrics.

## Important APIs, types, and functions
- `ftpDriver` implements `ftp.Driver`; `NewFTPDriver` points it at local MinIO API address.
- Path helpers `buildMinioPath` and `buildMinioDir` normalize FTP paths to bucket/object paths.
- `minioFileInfo` adapts `minio.ObjectInfo` to `os.FileInfo`.
- `ftpTrace`, `ftpMetrics.log`, and `globalFtpMetrics` publish trace events.
- Driver methods implement `Stat`, `ListDir`, `CheckPasswd`, `getMinIOClient`, `DeleteDir`, `DeleteFile`, `Rename`, `MakeDir`, `GetFile`, and `PutFile`.

## Control flow
Each FTP operation logs a trace through a deferred closure, obtains a MinIO client for the FTP session, converts the FTP path into bucket/object components, and invokes S3 APIs. Root listing lists buckets; bucket paths check bucket existence or create/delete buckets; object paths stat/list/get/put/remove objects. LDAP login can bind directly or mint temporary STS credentials with LDAP claims and site-replication hooks. Non-LDAP users use stored access/secret keys, while temporary credentials are rejected for normal IAM users.

## State and persistence behavior
Persistence happens through MinIO object operations: bucket creation/removal, zero-byte directory marker objects, object upload/download/delete, and recursive directory deletion by listing and removing objects. LDAP temporary users may be persisted in IAM state and replicated. Trace events include user, command, parameters, login state, source, path, duration, bytes, and error.

## Dependencies and integration points
Depends on `goftp.io/server/v2`, MinIO Go client, IAM/LDAP systems, site replication IAM hook, remote-target HTTP transport with forwarded client IP, madmin trace pubsub, MIME database, and MinIO path/bucket helpers.

## Risks and edge cases
FTP semantics do not perfectly match object storage: directories are markers or prefixes, rename and append are not implemented, `Stat` returns a dummy directory on `NoSuchKey` to satisfy LIST behavior, and recursive delete can fail silently if the listing goroutine sees an error before sending it. LDAP credential minting and policy checks are security-sensitive.

## Test signals
No direct tests in this group. Expected signals are FTP integration tests for login, bucket/object list/stat, upload/download/delete, TLS forwarding, LDAP behavior, and trace emission.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/ftp-server-driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/ftp-server.go -->
# sources/object-store/minio/cmd/ftp-server.go

## Purpose
Starts and configures the optional FTP/FTPS server front-end for MinIO. It parses `--ftp` key-value arguments, configures TLS and passive mode, and launches a goftp server backed by `ftpDriver`.

## Important APIs, types, and functions
- `globalRemoteFTPClientTransport` is the HTTP transport used by FTP driver clients.
- `minioLogger` implements goftp logging methods while masking PASS commands and honoring `serverDebugLog`.
- `startFTPServer` parses address, passive port range, TLS key/cert, and force-TLS settings; creates the server; and calls `ListenAndServe`.

## Control flow
Arguments are split as `key=value` and validated. Address parsing enforces a numeric port between 1 and 65535, with default 8021. TLS key/cert must be supplied together; if MinIO's S3 API is already TLS-enabled and FTP TLS files are not provided, it reuses MinIO cert files. `force-tls` requires TLS to be configured. The server is then created with welcome text, `NewFTPDriver`, simple permissions, passive/public IP options, explicit FTPS, logger, and TLS settings.

## State and persistence behavior
This file creates a long-running listener; it does not persist data itself. Data operations are handled by `ftp-server-driver.go`. Startup failures call `logger.Fatal`, terminating the process.

## Dependencies and integration points
Depends on goftp server options, MinIO global TLS/cert settings, version/license constants, FTP driver, and logger. It integrates with command-line server startup and optional S3 TLS configuration.

## Risks and edge cases
Invalid or partial TLS inputs are fatal. Reusing S3 TLS certs assumes those files are usable for FTP. Unknown argument keys are ignored by the switch, which can hide typos. The listener blocks in `ListenAndServe` and must be launched from an appropriate goroutine by caller code.

## Test signals
No direct tests in this group. Operational signals are successful listener startup, fatal validation for malformed args, PASS masking in debug logs, and FTPS behavior under explicit/forced TLS.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/ftp-server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/generic-handlers.go -->
# sources/object-store/minio/cmd/generic-handlers.go

## Purpose
Defines generic HTTP middleware and request classifiers used before S3/admin/KMS handlers. It enforces request/header limits, rejects malicious or reserved requests, redirects browser users, forwards federated buckets and site-replication multipart requests, adds response headers, and catches panics.

## Important APIs, types, and functions
- Limit constants define max body, header, user metadata, and bucket counts.
- `containsReservedMetadata` and `isHTTPHeaderSizeTooLarge` validate request metadata.
- `setRequestLimitMiddleware`, `setBrowserRedirectMiddleware`, `setRequestValidityMiddleware`, `setBucketForwardingMiddleware`, `addCustomHeadersMiddleware`, `setCriticalErrorHandler`, and `setUploadForwardingMiddleware` are middleware layers.
- Request classifiers include `guessIsBrowserReq`, `guessIsHealthCheckReq`, `guessIsMetricsReq`, `guessIsRPCReq`, `isAdminReq`, and `isKMSReq`.
- Helpers include `getRedirectLocation`, `parseAmzDateHeader`, `hasBadHost`, `hasBadPathComponent`, and `hasMultipleAuth`.

## Control flow
The limit middleware rejects reserved internal metadata and over-large headers before wrapping the body with `MaxBytesReader`. Validity middleware rejects bad hosts, dot/dot-dot path components, bad query values, multiple auth mechanisms, unauthorized access to reserved buckets, invalid bucket names, and SSE-C over plaintext. Browser middleware redirects anonymous browser GET/HEAD requests to the console for selected resources. Federation middleware looks up bucket DNS in etcd-backed config and proxies to a remote host if the bucket belongs elsewhere. Upload forwarding decodes the deployment ID from multipart upload IDs and proxies to the initiating site-replication peer.

## State and persistence behavior
The middleware mutates HTTP responses, request URLs for proxying, and global rejected-request counters. It reads global browser, DNS/federation, domain, TLS, site-replication, and forwarder state. It does not persist durable data.

## Dependencies and integration points
Integrates S3 auth detection, crypto SSE-C detection, MinIO grid routes, metrics routes, DNS store, forwarding transport, audit logging, trace context, global HTTP stats, bucket helpers, and admin/KMS route prefixes.

## Risks and edge cases
This is security-sensitive. Operator precedence in `guessIsMetricsReq` means later metric paths are accepted regardless of auth type unless intentionally relying on route protection elsewhere. Path validation trims Unicode whitespace and limits 32 KiB paths. Reserved metadata allows only mapped replication headers. Proxy branches must clear response headers before forwarding to avoid leaking local headers.

## Test signals
`generic-handlers_test.go` covers RPC route detection, header/user-metadata size limits, reserved metadata detection, SSE-C-over-HTTP rejection, and `hasBadPathComponent` benchmark cases. Federation and upload forwarding need integration coverage.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/generic-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/generic-handlers_contrib.go -->
# sources/object-store/minio/cmd/generic-handlers_contrib.go

## Purpose
Adds a request classifier for login and STS requests that should bypass bucket federation and upload forwarding middleware.

## Important APIs, types, and functions
- `guessIsLoginSTSReq` returns true for `/login...` paths or POST `/` requests authenticated as STS.

## Control flow
The function rejects nil requests, checks path prefix against `loginPathPrefix`, then checks for root-path POST with `authTypeSTS`.

## State and persistence behavior
No state is mutated or persisted. It reads request method/path and computed auth type.

## Dependencies and integration points
Used by generic forwarding middleware to avoid proxying login/STS calls as bucket traffic. Depends on `loginPathPrefix`, `SlashSeparator`, and `getRequestAuthType`.

## Risks and edge cases
The classifier is intentionally broad for `/login` prefixes. Incorrect classification can route authentication requests through bucket federation or skip forwarding for legitimate object paths that match the login prefix.

## Test signals
No direct tests in this group. Behavior is indirectly covered by auth, browser login, STS, and federation middleware tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/generic-handlers_contrib.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/generic-handlers_test.go -->
# sources/object-store/minio/cmd/generic-handlers_test.go

## Purpose
Tests selected generic HTTP handler helpers: RPC request detection, header-size enforcement, reserved metadata blocking, SSE-C TLS enforcement, and bad path component scanning performance.

## Important APIs, types, and functions
- `TestGuessIsRPC` checks legacy `/minio/lock` and current grid route paths.
- `generateHeader`, `isHTTPHeaderSizeTooLargeTests`, and `TestIsHTTPHeaderSizeTooLarge` build limit-boundary headers.
- `containsReservedMetadataTests` and `TestContainsReservedMetadata` distinguish internal reserved metadata from permitted crypto/replication headers.
- `sseTLSHandlerTests` and `TestSSETLSHandler` validate `setRequestValidityMiddleware` SSE-C behavior under TLS and non-TLS.
- `Benchmark_hasBadPathComponent` covers path scanner cases and throughput.

## Control flow
Tests construct synthetic requests/headers, call helper functions or wrap an OK handler with middleware, and compare booleans or HTTP response codes. `TestSSETLSHandler` temporarily mutates `globalIsTLS` and restores it with a deferred closure.

## State and persistence behavior
No persistence. The only global mutation is `globalIsTLS` during SSE-C middleware testing.

## Dependencies and integration points
Depends on request auth helpers, grid route constants, crypto metadata constants, HTTP test recorder, and generic middleware functions from `generic-handlers.go`.

## Risks and edge cases
Coverage is focused and does not test reserved bucket blocking, host validation, federation forwarding, browser redirect, metrics auth precedence, multiple-auth detection, or upload forwarding. Header size generation approximates sizes through key lengths.

## Test signals
Signals are true/false classifier results, exact HTTP 200 vs error behavior for SSE-C over TLS/plain HTTP, metadata limit boundary booleans, reserved metadata booleans, and benchmark failures if path scanning returns unexpected results.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/generic-handlers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/global-heal.go -->
# sources/object-store/minio/cmd/global-heal.go

## Purpose
Implements background healing orchestration for local drives and queued bucket/object healing. It creates the reserved background heal sequence, reports local heal state, scans erasure sets, and heals objects/versions while updating trackers and global counters.

## Important APIs, types, and functions
- `bgHealingUUID` identifies the always-on background heal sequence.
- `newBgHealSequence` initializes a `healSequence` with `healDeleteDangling`.
- `getLocalBackgroundHealStatus` reports scanned counts, healing disks, set status, and storage-class parity.
- `healEntryResult` carries per-entry progress from concurrent heal workers.
- `(*erasureObjects).healErasureSet` drives bucket/object scanning and healing for one erasure set.
- `healBucket` and `healObject` enqueue work into global background heal state.

## Control flow
`healErasureSet` finds the background sequence, copies queued buckets, heals bucket metadata first, reads disk info, sizes worker concurrency from disk request capacity or config, and starts a result collector that updates the healing tracker. For each bucket it loads versioning/lifecycle/object-lock/replication state, selects online disks including the healing disk at the end, rejects insufficient non-healing disks, lists raw metadata recursively, and schedules `healEntry` workers for agreed or partial entries. Each entry skips directories and internal metacache/trash/multipart paths, resolves versions, ignores versions newer than heal start or expired by lifecycle, calls `HealObject`, checks the healed disk state, updates counters, and records progress.

## State and persistence behavior
State spans global heal sequences, healing trackers saved to disk, background scanned/healed/failed counters, queued buckets, local disk healing flags, and lifecycle expiry queues. The function persists tracker updates and may enqueue lifecycle expiry or restored-object deletion during healing.

## Dependencies and integration points
Integrates erasure metadata listing, object healing, lifecycle, object lock, replication, bucket versioning, storage-class parity, madmin heal/status types, worker pools, global heal config, global HTTP request throttling, and local storage info.

## Risks and edge cases
Healing must avoid rewriting newly uploaded versions, expired objects, internal metadata paths, and all-healing sets. Partial metadata resolution with quorum one is intentionally permissive but can surface inconsistent entries. Worker/result channel coordination and tracker updates are concurrency-sensitive. Insufficient disks or listing errors leave buckets queued for retry.

## Test signals
No direct tests in this group. Signals come from healing integration tests, madmin background-heal status, tracker persistence, successful object reconstruction, lifecycle skip behavior, and logged failures for list/heal errors.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/global-heal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/globals.go -->
# sources/object-store/minio/cmd/globals.go

## Purpose
Centralizes process-wide constants, server context, and global subsystem pointers used by MinIO server startup, request handling, storage, security, replication, healing, metrics, and optional protocols.

## Important APIs, types, and functions
- Constants define default ports, modes, owner/storage class defaults, reserved directory suffixes, disk reserve thresholds, memory/request limits, and TLS cache sizing.
- `init` wires `pubsub.GetByteBuffer` to `grid.GetByteBuffer` to avoid circular dependencies.
- `poolDisksLayout`, `disksLayout`, and `serverCtxt` capture parsed server startup configuration, credentials, FTP/SFTP options, memory/network timeouts, and disk layout.
- Global variables hold configuration systems, IAM/policy/lifecycle/bucket metadata systems, event targets, TLS/certs, HTTP server, stats, endpoints/nodes, DNS/etcd, KMS, replication, heal state, forwarders, local drive maps, subnet keys, and service-freeze state.
- Auth plugin accessors/mutators protect plugin pointers with `globalAuthPluginMutex`.
- `errSelfTestFailure` is a startup safety sentinel.

## Control flow
Aside from the `init` hook and plugin getters/setters, this file is declarative global state. Other packages initialize and mutate these globals during startup, config reloads, request handling, healing, and shutdown.

## State and persistence behavior
The file itself persists nothing, but many globals point to persistent subsystems: config, IAM, bucket metadata, lifecycle, KMS, etcd/DNS, replication, tiers, and drive maps. Some values are atomics or mutex-protected; many are conventional package globals that require disciplined initialization order.

## Dependencies and integration points
This is a hub for most MinIO command package integrations: HTTP, console, IAM, policy plugins, storage class, DNS, etcd, KMS, grid, pubsub, certs, drive config, compression, subnet/callhome, replication, healing, and object performance tooling.

## Risks and edge cases
Global mutable state increases test coupling and startup-order sensitivity. Concurrent access must respect documented mutexes or atomics, especially local drive maps, auth plugins, compression config, deployment ID, and service freeze. Adding globals here expands process-wide coupling.

## Test signals
No direct tests in this group. Signals are broad: race tests, startup/shutdown integration tests, config reload tests, plugin set/get behavior, and subsystem initialization failures that expose nil or stale globals.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/globals.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/grid.go -->
# sources/object-store/minio/cmd/grid.go

## Purpose
Initializes global persistent websocket grid managers for internode RPC and distributed lock traffic. It creates separate managers for storage/admin grid routes and lock-grid routes.

## Important APIs, types, and functions
- `globalGrid` and `globalLockGrid` are atomic pointers to `grid.Manager`.
- `globalGridStart` and `globalLockGridStart` are startup gates for grid connections.
- `initGlobalGrid` creates the main grid manager with `grid.RoutePath`.
- `initGlobalLockGrid` creates the lock grid manager with `grid.RouteLockPath`.

## Control flow
Each initializer derives hosts and local node from endpoint pools, uses DNS-cache-backed internode dialers configured for websockets, sets TLS roots/ciphers/curves, provides cached auth tokens and validation callbacks, wires byte counters and trace output, and stores the resulting manager atomically. The lock initializer uses the lock route path in its websocket connector and manager options.

## State and persistence behavior
No durable state. Runtime state is the globally stored manager and startup gate channels. Incoming/outgoing counters mutate global connection stats.

## Dependencies and integration points
Depends on endpoint pools, DNS cache, internode HTTP dialer/TCP options, MinIO crypto TLS policy, storage request token validation, cached auth tokens, global trace pubsub, and MinIO grid package.

## Risks and edge cases
Internode connectivity depends on correct endpoint host discovery, DNS resolution, TLS roots, route path, and auth token validation. Both managers use `globalGridStart` as the block channel in the shown code; if the separate lock gate is expected, this may be intentional coupling or a subtle configuration risk.

## Test signals
No direct tests here. Signals come from distributed startup, internode RPC, lock acquisition, byte counters, and grid route health under TLS and DNS changes.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/grid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/handler-api.go -->
# sources/object-store/minio/cmd/handler-api.go

## Purpose
Stores runtime API configuration and request throttling behavior for S3 handlers. It calculates request concurrency from configuration or memory limits, exposes thread-safe getters, and implements `maxClients` admission control.

## Important APIs, types, and functions
- `apiConfig` holds request pool, cluster deadline, list quorum, CORS origins, replication/transition worker settings, cleanup intervals, O_DIRECT/gzip/root/sync-events flags, and object version cap.
- `cgroupMemLimit` and `availableMemory` derive memory budgets from cgroup or host memory.
- `(*apiConfig).init` applies `api.Config` to runtime state and resizes workers/request pool.
- Getter methods expose immutable copies or defaults under `RWMutex`.
- `maxClients` enforces request pool capacity and service-freeze behavior.
- `getReplicationOpts`, `getTransitionWorkers`, `isSyncEventsEnabled`, and `getObjectMaxVersions` feed background subsystems.

## Control flow
Initialization chooses cluster deadline and CORS defaults, calculates per-node max requests from configured limit or memory divided by estimated per-request erasure memory, replaces the request pool only when capacity changes, resizes replication and transition workers, updates cleanup intervals, and signals stale-upload cleanup goroutines when the interval changes. `maxClients` increments incoming/queued stats, optionally waits for service unfreeze, emits rate-limit headers, admits if it can send into the pool, returns 499 on client cancellation, or returns `ErrTooManyRequests` if full.

## State and persistence behavior
State is in-memory runtime configuration guarded by a mutex. It affects cleanup timers, request concurrency, metrics, and background worker counts but does not persist configuration itself.

## Dependencies and integration points
Depends on MinIO API config, global server memory limit, erasure block sizes, replication pool, transition state, HTTP stats, service-freeze global, context trace metadata, and stale upload cleanup channel in `erasure-sets.go`.

## Risks and edge cases
Concurrency resizing leaves a short overlap where existing requests use the old pool. Request limits based on memory estimates can be too high or low for unusual layouts. `maxClients` uses non-blocking admission and can reject bursts immediately. Correct 499 auditing depends on response recorder behavior after cancellation.

## Test signals
No direct tests in this group. Signals include request throttling integration tests, rate-limit headers, busy/too-many-request responses, cleanup interval changes, and worker pool resizing behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/handler-api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/handler-utils.go -->
# sources/object-store/minio/cmd/handler-utils.go

## Purpose
Provides shared HTTP handler utilities for region parsing, metadata extraction, event request/response element extraction, streaming content-encoding cleanup, stats collection, virtual-host resource mapping, unmatched-route errors, host naming, and proxying.

## Important APIs, types, and functions
- `parseLocationConstraint` and `isValidLocation` implement S3 bucket region validation.
- `supportedHeaders`, `validSSEReplicationHeaders`, `replicationToInternalHeaders`, and user metadata prefixes drive metadata extraction.
- Directive helpers validate COPY/REPLACE behavior.
- `extractMetadataFromReq`, `extractMetadata`, and `extractMetadataFromMime` canonicalize headers/query values into object metadata.
- `extractReqParams` and `extractRespElements` build event notification maps.
- `trimAwsChunkedContentEncoding`, `collectInternodeStats`, `collectAPIStats`, `getResource`, `extractAPIVersion`, `errorResponseHandler`, `getHostName`, and `proxyRequest` are shared handler helpers.

## Control flow
Location parsing decodes XML only when a non-empty body exists and defaults empty locations to the configured site region. Metadata extraction canonicalizes headers, copies known system headers, maps replication headers back to internal names, copies user metadata by prefix, adds a default content type, removes unencrypted length/MD5 advisory-sensitive headers, and trims `aws-chunked` from content encoding. Stats wrappers update global and per-bucket counters after handler execution. `errorResponseHandler` returns upgrade-required responses for peer/storage/admin version mismatches or generic bad-request errors for unsupported APIs.

## State and persistence behavior
No durable persistence. It mutates metadata maps, request/response stats, response headers, audit logs, and proxy request URLs. Event parameter extraction exposes principal, source IP, range, and replication-source flags.

## Dependencies and integration points
Integrates auth parsing, XML decoding, global site region, bucket metadata sys, HTTP stats, trace context, event notification, virtual-host domains, madmin admin API versioning, forwarder/proxy transport, and MinIO API error mapping.

## Risks and edge cases
Metadata canonicalization must avoid duplicate/header-case confusion and strip sensitive advisory headers. `getResource` must handle IPv6/ports and reserved minio subdomain correctly. `errorResponseHandler` is user-facing for unsupported routes and version mismatches, so message/status changes affect clients. Proxying clears local headers before forwarding.

## Test signals
`handler-utils_test.go` covers location XML parsing, metadata extraction including multiple values and nil headers, and virtual-host resource mapping for domains and IP hosts. Other behavior is integration-tested through S3/admin routing and proxy paths.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/handler-utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/handler-utils_test.go -->
# sources/object-store/minio/cmd/handler-utils_test.go

## Purpose
Tests region constraint parsing, metadata extraction, and virtual-host resource construction for shared HTTP handler utilities.

## Important APIs, types, and functions
- `TestIsValidLocationConstraint` exercises `parseLocationConstraint` under valid XML, empty location, malformed XML, and non-XML bodies.
- `TestExtractMetadataHeaders` validates `extractMetadataFromMime` for content type, ignored headers, user metadata prefixes, canonicalization, multiple values, and nil input.
- `TestGetResource` validates `getResource` for virtual-host style domains, IPv6 hosts, IP:port hosts, non-matching domains, and nil domains.

## Control flow
The location test initializes a temporary FS object layer and config region, builds requests with XML bodies or invalid bodies, and compares returned API error codes. Metadata tests pass synthetic headers into extraction and compare maps with `reflect.DeepEqual`. Resource tests call `getResource` with path/host/domain triples and assert the expected path-style resource.

## State and persistence behavior
The location test creates temporary storage/config state through `prepareFS` and `newTestConfig`, then removes the filesystem directory. Other tests are in-memory.

## Dependencies and integration points
Depends on MinIO test storage setup, global server config region, XML marshaling, HTTP headers, textproto MIME headers, and resource/domain logic from `handler-utils.go`.

## Risks and edge cases
Coverage does not include replication header mapping, sensitive metadata deletion, `aws-chunked` trimming, stats wrappers, proxying, or error response routing. Region tests use the default empty region behavior and a configured default region but do not test mismatched non-empty regions beyond expected helper behavior.

## Test signals
Signals are exact API error codes, extracted metadata maps, expected failure for nil metadata input, and exact resource strings for virtual-host and path-style requests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/handler-utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/hasher.go -->
# sources/object-store/minio/cmd/hasher.go

## Purpose
Provides small helper functions for MD5 and SHA-256 sums and hex-encoded hashes.

## Important APIs, types, and functions
- `getSHA256Hash` returns hex-encoded SHA-256.
- `getSHA256Sum` returns raw SHA-256 bytes using MinIO's internal SHA-256 implementation.
- `getMD5Sum` returns raw MD5 bytes.
- `getMD5Hash` returns hex-encoded MD5.

## Control flow
Each sum function constructs a hash, writes the full input byte slice, and returns the digest. Hash functions hex-encode the corresponding sum.

## State and persistence behavior
No state or persistence. Outputs are deterministic functions of input bytes.

## Dependencies and integration points
Uses Go `crypto/md5`, `encoding/hex`, and MinIO internal SHA-256 package. These helpers are likely consumed by ETag, checksum, metadata, and test code elsewhere in `cmd`.

## Risks and edge cases
MD5 is not collision-resistant and should only be used for S3 compatibility/integrity semantics, not new security decisions. Functions ignore write errors because hash writers never fail.

## Test signals
No direct tests in this group. Expected coverage is through checksum, ETag, and authentication/signature tests that compare known digests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/hasher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/healingmetric_string.go -->
# sources/object-store/minio/cmd/healingmetric_string.go

## Purpose
Generated `stringer` output for the `healingMetric` enum from `erasure-healing.go`. It maps metric constants to stable names for logging/metrics display.

## Important APIs, types, and functions
- Compile-time checks assert `healingMetricBucket`, `healingMetricObject`, and `healingMetricCheckAbandonedParts` numeric values.
- `_healingMetric_name` and `_healingMetric_index` encode `Bucket`, `Object`, and `CheckAbandonedParts`.
- `(healingMetric).String()` returns the generated name or `healingMetric(<n>)` for out-of-range high values.

## Control flow
The string method checks the upper bound and slices the generated compact name table. Unlike some stringer outputs, negative enum values are not explicitly rejected before indexing, so callers should not pass negative values.

## State and persistence behavior
No state or persistence. It is generated code and should be regenerated when enum constants change.

## Dependencies and integration points
Used by erasure healing metrics/logging code. Depends only on `strconv` and enum constants defined elsewhere.

## Risks and edge cases
Manual edits or enum changes without regeneration can break names or compile-time checks. Negative enum values can index before bounds if ever constructed.

## Test signals
Build success verifies generated constant checks. Runtime metric tests elsewhere should catch unexpected string names.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/healingmetric_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/healthcheck-handler.go -->
# sources/object-store/minio/cmd/healthcheck-handler.go

## Purpose
Implements Kubernetes/operator-facing health endpoints for cluster write quorum, cluster read quorum, readiness, and liveness. It separates external dependency readiness from basic process liveness.

## Important APIs, types, and functions
- `checkHealth` validates object layer, bucket metadata system, and IAM system initialization.
- `ClusterCheckHandler` reports write health and maintenance drain status.
- `ClusterReadCheckHandler` reports read health.
- `ReadinessCheckHandler` checks initialization, peer-call bypass, request queue pressure, KMS key generation, and etcd reachability.
- `LivenessCheckHandler` checks initialization and request queue pressure without external systems.

## Control flow
Cluster handlers build a request context with the configured cluster deadline, call `objLayer.Health` with maintenance/deployment options from query parameters, set quorum/storage-class/healing headers, and return OK, service unavailable, or precondition failed for maintenance. Readiness and liveness mark server status if the object layer is missing, allow internode peer calls, return busy when queued requests exceed capacity, and readiness additionally verifies KMS and etcd with timeouts.

## State and persistence behavior
No durable state. Handlers read global object layer, IAM/bucket metadata init state, API config, HTTP queue stats, KMS, and etcd client. They write response status and MinIO-specific health headers.

## Dependencies and integration points
Integrates health routes, object-layer `Health`, global API deadlines, KMS `GenerateKey`, etcd `Get`, MinIO API error conversion, request queue stats, and internal peer-call headers.

## Risks and edge cases
Readiness can fail due to external KMS/etcd even when the server process is alive; liveness intentionally avoids those calls to prevent restart loops. Queue-pressure comparison depends on request pool capacity and can behave oddly if capacity is zero. Cluster maintenance uses 412 to tell orchestrators a node should not be removed.

## Test signals
No direct tests in this group. Expected signals include HTTP status codes/headers for healthy/unhealthy quorum, KMS/etcd failures, peer calls, busy queues, GET vs HEAD response shapes, and maintenance precondition behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/healthcheck-handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/healthcheck-router.go -->
# sources/object-store/minio/cmd/healthcheck-router.go

## Purpose
Registers MinIO health check routes under the reserved `/minio/health` path prefix.

## Important APIs, types, and functions
- Constants define `/health`, `/live`, `/ready`, `/cluster`, `/cluster/read`, and the full `/minio/health` prefix.
- `registerHealthCheckRouter` attaches GET and HEAD handlers for cluster, cluster-read, liveness, and readiness checks.

## Control flow
The function creates a subrouter from `router.PathPrefix(healthCheckPathPrefix)` and binds each endpoint/method pair to the corresponding handler wrapped by `httpTraceAll`.

## State and persistence behavior
No persistent state. It mutates the provided mux router during server setup.

## Dependencies and integration points
Depends on `github.com/minio/mux`, standard HTTP methods, route constants shared with request classifiers, health handlers from `healthcheck-handler.go`, and tracing middleware.

## Risks and edge cases
Route constants must remain in sync with `guessIsHealthCheckReq`; otherwise middleware may mishandle health calls. Only GET and HEAD are registered, so other methods fall through to generic error handling.

## Test signals
No direct tests in this group. Signals are router integration tests that verify `/minio/health/live`, `/ready`, `/cluster`, and `/cluster/read` reach the expected handlers for GET and HEAD.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/healthcheck-router.go -->

# subset-b-008211 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage.go -->
# sources/object-store/minio/cmd/xl-storage.go

## Purpose
This file is MinIO's local erasure-set storage backend implementation. `xlStorage` implements the `StorageAPI` surface for a local disk path: disk initialization, volume lifecycle, raw file I/O, `xl.meta` metadata reads/writes, version metadata mutation, trash-based deletes, multipart/part movement, bitrot verification, data usage scanning, and disk identity reporting.

## Important APIs, Types, and Functions
Core constants define the metadata file names (`xlStorageFormatFile`, `xlStorageFormatFileBackup`), small-file inline threshold, and legacy null version marker. `xlStorage` holds drive path, endpoint indexes, direct-I/O capability, cached `format.json` data, disk ID, disk-info cache, filesystem identity, scan state, trash purge channel, rotational-disk walk locks, and global sync/direct-I/O flags.

Initialization is handled by `newXLStorage`, `getValidPath`, `getDiskInfo`, `makeFormatErasureMetaVolumes`, and `checkODirectDiskSupport`. Identity and health are exposed through `DiskInfo`, `GetDiskID`, `SetDiskID`, `GetDiskLoc`, `Healing`, `IsOnline`, `IsLocal`, `Hostname`, `Endpoint`, and `Close`.

Namespace APIs include `MakeVolBulk`, `MakeVol`, `ListVols`, `StatVol`, `DeleteVol`, `ListDir`, `Delete`, `DeleteBulk`, `RenameFile`, and `StatInfoFile`. Metadata and version APIs include `ReadXL`, `ReadVersion`, `WriteMetadata`, `UpdateMetadata`, `DeleteVersion`, `DeleteVersions`, `renameLegacyMetadata`, `readRaw`, `readMetadataWithDMTime`, and `readAllDataWithDMTime`. Data APIs include `ReadAll`, `WriteAll`, `AppendFile`, `CreateFile`, `ReadFile`, `ReadFileStream`, `RenameData`, `RenamePart`, `ReadParts`, `ReadMultiple`, `CheckParts`, `VerifyFile`, and `CleanAbandonedData`.

## Control Flow
`newXLStorage` validates or creates the endpoint path, rejects root drives, captures filesystem/disk properties, creates MinIO internal volumes, migrates/loads `format.json`, checks expected pool/set/disk ordering, decides direct-I/O support, and initializes a cached `DiskInfo` callback. Regular operations first resolve a volume directory, validate effective path length, then call local filesystem helpers (`OpenFile`, `Rename`, `renameAll`, `readDir`, `mkdirAll`, `Remove`, `Lstat`) while translating OS errors into MinIO domain errors.

Read flow for objects starts with `ReadVersion`: optional original-volume access check, volume/path validation, raw metadata read from `xl.meta` or legacy `xl.json`, `getFileInfo` decoding, and optional inline or small-part data loading. Write flow for metadata usually serializes `xlMetaV2`, writes bytes with sync semantics, and for `writeAllMeta` uses a temp file in `.minio.sys/tmp` followed by `renameAll` to atomically replace the final metadata. `RenameData` is the commit path for object data: it loads existing destination metadata, preserves legacy data if needed, adds free versions for overwritten null versions, writes new metadata under the source temp location, renames data directories, optionally backs up old metadata under the old data dir, then atomically renames source metadata into the destination.

Delete flow mutates metadata with `xlMetaV2.DeleteVersion`, moves unreferenced data dirs to `.minio.sys/tmp/.trash`, rewrites metadata when versions remain, or removes `xl.meta` and empty parents when the last version is gone. Bulk deletes and volume force-deletes use trash renames; immediate purge is asynchronous through `immediatePurge` unless queue pressure forces blocking removal.

`NSScanner` bridges the storage layer to MinIO lifecycle, replication, object-lock, versioning, tier, usage-cache, and scanner metrics subsystems. It walks metadata files, decodes versions, applies lifecycle/replication accounting actions, emits data-usage entries, and queues free versions for tier cleanup.

## State and Persistence
Persistent state is stored directly under `drivePath`: buckets/volumes as directories, objects as directories containing `xl.meta`, parts under version data dirs, legacy objects as `xl.json`, MinIO internal state under `.minio.sys`, and trash under `.minio.sys/tmp/.trash`. `format.json` is cached in memory with its `os.FileInfo` and periodically rechecked to detect disk replacement or ordering mismatch. Extended attributes on `format.json` track total writes/deletes. Metadata writes use synchronous/direct or O_SYNC/O_DSYNC modes depending on platform and size, then atomic rename where required. Data writes use `Fdatasync` and checked `Close` to avoid silent loss.

## Dependencies and Integration Points
The file depends heavily on MinIO internal packages: `disk`, `ioutil`, `cachevalue`, scanner/lifecycle/replication systems, storage-class tiering, logger, xattr, and metadata codecs (`xlMetaV2`, `formatErasureV3`, `FileInfo`). It is called by erasure object-layer code and storage REST wrappers. It integrates with global configuration (`globalDriveConfig`, `globalAPIConfig`, `globalFSOSync`, `globalStorageClass`), global object-layer access, bucket metadata systems, disk health checks, scanner metrics, and platform-specific `readMode`/`writeMode`.

## Risks and Edge Cases
Correctness depends on careful error translation; a wrong OS error mapping can make healing, retries, or S3 responses incorrect. `RenameData` is complex and has partial-failure windows around metadata, data-dir, and backup renames; recovery depends on later healing and backup metadata. `CleanAbandonedData` appears to serialize `newBuf` but writes `buf`, which is a risk if this snapshot is representative. Direct-I/O support varies by filesystem; unsupported or misdetected direct I/O fails startup for erasure disks. Root-drive detection and disk-ID ordering checks are safety gates with operational impact. Path-length validation is platform sensitive. Trash growth, immediate purge backpressure, xattr availability, and legacy `xl.json` migration paths are operational risk areas.

## Test Signals
The companion tests exercise path validation, volume CRUD, disk-not-found/access-denied mapping, reads, writes, appends, renames, metadata version delete, bitrot verification, stat behavior, umask behavior, and Windows UNC/path-component errors. Coverage is strongest for local filesystem edge cases and legacy metadata reads; it is weaker for `NSScanner`, `RenameData` crash recovery, xattr counters, direct-I/O probing, and trash-purge pressure.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage_noatime_notsupported.go -->
# sources/object-store/minio/cmd/xl-storage_noatime_notsupported.go

## Purpose
This platform-specific file defines read and write open flags for platforms where MinIO does not use Linux `O_NOATIME`/`O_DSYNC` behavior, namely non-Unix plus Darwin and FreeBSD builds.

## Important APIs, Types, and Functions
It exports package variables `readMode = os.O_RDONLY` and `writeMode = os.O_SYNC`. These variables are consumed by `xl-storage.go` when opening files for metadata and data reads/writes.

## Control Flow
There is no runtime control flow; build tags select this file at compile time. Storage reads open normally, and sync metadata writes use `os.O_SYNC` when `openFileSync` combines `writeMode` with `os.O_WRONLY`.

## State and Persistence Behavior
The file affects persistence semantics indirectly. `O_SYNC` asks the kernel to make writes synchronous on platforms in this build set, while read opens update access times according to platform defaults.

## Dependencies and Integration Points
The only dependency is Go's `os` package. The variables integrate with `readMetadataWithDMTime`, `readAllDataWithDMTime`, `ReadFile`, `ReadFileStream`, `AppendFile`, `writeAllInternal`, and other `xlStorage` open paths.

## Risks and Test Signals
Risk is platform divergence: Darwin/FreeBSD/non-Unix may have different sync and atime cost from Linux. Test coverage is indirect through the cross-platform storage tests; there is no specific test for these flag values.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage_noatime_notsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage_noatime_supported.go -->
# sources/object-store/minio/cmd/xl-storage_noatime_supported.go

## Purpose
This Linux/Unix build file defines optimized open flags for MinIO storage on Unix platforms that support no-atime reads and data-synchronous writes.

## Important APIs, Types, and Functions
It defines `readMode = os.O_RDONLY | 0x40000 | syscall.O_NONBLOCK`, where `0x40000` is `O_NOATIME`, and `writeMode = 0x1000 | syscall.O_NONBLOCK`, where `0x1000` is `O_DSYNC`.

## Control Flow
There is no runtime branching. Build tags select this file for `unix && !darwin && !freebsd`, and `xlStorage` inherits the flags for all ordinary read opens and sync metadata writes.

## State and Persistence Behavior
`O_NOATIME` avoids read-side access-time updates, reducing metadata churn on storage disks. `O_DSYNC` makes synchronous writes persist file data needed for consistency without necessarily syncing unrelated metadata. `O_NONBLOCK` avoids syscall behavior around epoll setup on files.

## Dependencies and Integration Points
The file depends on `os` and `syscall`. Its values are used by the central storage implementation in `xl-storage.go`, so any platform mismatch affects every local disk operation.

## Risks and Test Signals
The numeric constants are Linux-specific and can be fragile if used on an unsupported target, but build tags constrain that. Test coverage is mostly behavioral through storage read/write tests and Unix umask tests, not direct assertions of no-atime behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage_noatime_supported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage_test.go -->
# sources/object-store/minio/cmd/xl-storage_test.go

## Purpose
This file is the broad unit/integration test suite for the local MinIO `xlStorage` backend. It builds temporary disk trees, initializes `xlStorage`, and validates filesystem behavior, error translation, metadata handling, bitrot checks, and basic StorageAPI operations.

## Important APIs, Types, and Functions
Helper functions include `newLocalXLStorage`, `newLocalXLStorageWithDiskIdx`, `newXLStorageTestSetup`, and `createPermDeniedFile`. Major tests cover `checkPathLength`, `isValidVolname`, `getDiskInfo`, `ReadVersion`, `ReadAll`, `newXLStorage`, `MakeVol`, `DeleteVol`, `StatVol`, `ListVols`, `ListDir`, `Delete`, `ReadFile`, `ReadFile` with `BitrotVerifier`, `GetDiskID` behavior after format changes, `AppendFile`, `RenameFile`, `DeleteVersion`/`DeleteVersions`, `StatInfoFile`, `VerifyFile`, and `readMetadata`.

## Control Flow
Most tests are table-driven. Setup creates a temp directory, initializes a local storage disk, writes a synthetic erasure `format.json`, and wraps the disk in `xlStorageDiskIDCheck`. Tests then create volumes/files directly through `xlStorage` APIs or filesystem calls, invoke the API under test, and compare exact MinIO error values or output bytes. Permission-denied cases are skipped or adjusted on Windows.

## State and Persistence Behavior
The tests exercise real filesystem state: directories as volumes, object data files, object directories containing `xl.meta`, old `xl.json` metadata, chmod-protected directories, removed disk roots, and modified `format.json`. Version tests create 50 versions in `xl.meta`, delete individual and bulk versions, and verify metadata removal after the last version.

## Dependencies and Integration Points
The suite depends on Go testing, temp directories, `os`, `syscall`, random data, UUIDs, MinIO bitrot verifier APIs, testdata `xl.meta`, and the real storage helper functions. It integrates with platform-specific behavior by checking `runtime.GOOS` and by using wrapper types that enforce disk ID checks.

## Risks and Test Signals
Strong signals include path-length handling, exact error mapping for missing volumes/files, permission translation, append/read semantics, unexpected EOF handling, bitrot corruption detection, rename type mismatch, and metadata version deletion. Gaps include scanner behavior, concurrent operation races, direct-I/O probing, trash-purge queue pressure, xattr counters, detailed `RenameData` recovery, and object lifecycle/replication interactions.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage_unix_test.go -->
# sources/object-store/minio/cmd/xl-storage_unix_test.go

## Purpose
This Unix-only test file verifies that `xlStorage` respects the process umask when creating volume directories and files.

## Important APIs, Types, and Functions
`getUmask` reads the current umask by temporarily setting it to zero and restoring it. `TestIsValidUmaskVol` validates `MakeVol` directory permissions. `TestIsValidUmaskFile` validates file creation through `AppendFile` and `StatInfoFile`.

## Control Flow
Each test creates a temp disk, initializes local storage, creates a volume or file, stats the result, and compares observed permissions against `0777 - umask` for directories or verifies successful file stat for file creation.

## State and Persistence Behavior
The tests use real filesystem mode bits. They confirm storage code passes permissive modes (`0777` for directories, `0666` for files) and relies on the OS umask to apply local policy.

## Dependencies and Integration Points
The file depends on Unix-like build tags, `syscall.Umask`, `os.Stat`, and `newLocalXLStorage`. It validates behavior in `mkdirAll`, `MakeVol`, `AppendFile`, and `StatInfoFile`.

## Risks and Test Signals
Risk is platform-specific mode handling: changing creation modes in the storage layer could bypass administrator umask expectations. These tests provide direct Unix coverage but do not inspect exact file mode in the file test beyond successful stat.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage_windows_test.go -->
# sources/object-store/minio/cmd/xl-storage_windows_test.go

## Purpose
This Windows-only test file validates `xlStorage` path behavior under Windows/UNC-style path handling.

## Important APIs, Types, and Functions
`TestUNCPaths` appends objects with leading slashes, nested paths, and Unicode names, including an overlong component expected to fail. `TestUNCPathENOTDIR` validates that a path whose parent component is an existing file maps to `errFileAccessDenied`.

## Control Flow
Tests create a temp local storage disk and a volume, then use `AppendFile` and `Delete` for each path case. The ENOTDIR test writes `/file` then attempts `/file/obj1`.

## State and Persistence Behavior
The tests exercise real Windows filesystem paths and MinIO path normalization. The main persistence signal is preventing invalid or ambiguous path components from creating inconsistent object trees.

## Dependencies and Integration Points
The file depends on Windows build tags, `newLocalXLStorage`, `MakeVol`, `AppendFile`, and `Delete`. It complements the shared tests that branch on `runtime.GOOS`.

## Risks and Test Signals
Windows path handling is historically error-prone because slash handling, Unicode length, and ENOTDIR equivalents differ from Unix. These tests guard path creation and error mapping, but they do not cover reserved Windows volume characters, which are handled by `isValidVolname`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/account-server/1.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/account-server/1.conf

## Purpose
SAIO account-server config for node 1. It runs the account WSGI app on `127.0.0.1:6212` with one worker against `/srv/1/node`.

## Important Sections
`[DEFAULT]` sets device path, disables mount checking and fallocate, assigns `LOG_LOCAL2`, recon cache `/var/cache/swift`, and enables eventlet debug. `[pipeline:main]` is `healthcheck recon account-server`. `[app:account-server]` loads `egg:swift#account`; filters load `recon` and `healthcheck`. `[account-replicator]` defines an rsync module template.

## Control Flow and Integration
Swift's PasteDeploy loader builds the healthcheck/recon/account pipeline. Account daemon tools read their own sections from the same file. The account replicator uses the rsync module template with replication IP/port expansion.

## State, Risks, and Test Signals
Persistent state is under `/srv/1/node/accounts`; recon state under `/var/cache/swift`. `user = <your-user-name>` and `disable_fallocate = true` mark this as a developer SAIO config, not production. Risk is mis-substitution of user or rsync template. Test signal is functional SAIO account service startup and recon/healthcheck availability.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/account-server/1.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/account-server/2.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/account-server/2.conf

## Purpose
SAIO account-server config for node 2. It mirrors the node 1 account pipeline but binds to `127.0.0.2:6222` and stores data under `/srv/2/node`.

## Important Sections
`[DEFAULT]` sets `LOG_LOCAL3`, recon cache `/var/cache/swift2`, one worker, disabled mount checks, and eventlet debug. `[pipeline:main]` is `healthcheck recon account-server`. The app and filters load Swift account, recon, and healthcheck entry points. Account replicator uses the standard account rsync module template.

## Control Flow and Integration
PasteDeploy constructs the account server pipeline. The config participates in the four-node SAIO ring simulation by using node-specific loopback IP, port, log facility, device root, and recon cache.

## State, Risks, and Test Signals
State persists under `/srv/2/node/accounts`. Risks are the placeholder user, non-production mount/fallocate choices, and mismatch between ring device definitions and the bind/device values. Test signal is that node 2 account services can start and replicate with the other SAIO nodes.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/account-server/2.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/account-server/3.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/account-server/3.conf

## Purpose
SAIO account-server config for node 3. It binds the account service to `127.0.0.3:6232` and uses `/srv/3/node`.

## Important Sections
Defaults set `LOG_LOCAL4`, `/var/cache/swift3`, one worker, disabled mount checks, disabled fallocate, placeholder user, and eventlet debugging. The pipeline is `healthcheck recon account-server`; account, recon, and healthcheck are loaded from Swift egg entry points. Account daemon sections are present for replicator, auditor, and reaper.

## Control Flow and Integration
This file is loaded by Swift service scripts for account-server family daemons. It maps the third simulated SAIO account node into the same pipeline and replication model as the other configs.

## State, Risks, and Test Signals
State lives under `/srv/3/node/accounts`; recon cache under `/var/cache/swift3`. Risks are development-only defaults and ring/config drift. Test signal is successful account-node startup, healthcheck responses, recon cache updates, and replication participation.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/account-server/3.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/account-server/4.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/account-server/4.conf

## Purpose
SAIO account-server config for node 4. It binds to `127.0.0.4:6242` and uses `/srv/4/node`.

## Important Sections
Defaults set `LOG_LOCAL5`, recon cache `/var/cache/swift4`, one worker, disabled mount checks/fallocate, placeholder user, and eventlet debug. Pipeline and filters are the standard account-server `healthcheck recon account-server` chain. Replicator, auditor, and reaper sections are present.

## Control Flow and Integration
Swift service launch uses this config to build the fourth account server in a local multi-node SAIO environment. Replication uses the templated account rsync module.

## State, Risks, and Test Signals
Persistent account DBs are under `/srv/4/node/accounts`. Risks are non-production defaults and any mismatch with generated rings or rsyncd configuration. Test signal is startup, healthcheck, recon, and cross-node account replication.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/account-server/4.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-reconciler/1.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/container-reconciler/1.conf

## Purpose
SAIO container-reconciler config for process shard 0 of 4. It configures logging and a proxy client pipeline used by the reconciler to repair misplaced container/object records.

## Important Sections
`[DEFAULT]` sets placeholder user and `LOG_LOCAL2`, with many optional logging/StatsD settings commented. `[container-reconciler]` sets `processes = 4` and `process = 0`. `[pipeline:main]` is `catch_errors proxy-logging cache proxy-server`, loading Swift proxy, memcache, proxy logging, and catch-errors filters.

## Control Flow and Integration
The reconciler daemon reads the shard assignment and uses the embedded proxy pipeline to issue internal requests. Four config files split work by process number.

## State, Risks, and Test Signals
State is mainly remote Swift cluster state manipulated through proxy-server requests; local persistence is logs and cache. Risk is duplicate or missing work if process/processes settings across the four files are inconsistent. Test signal is successful reconciler startup and balanced processing of misplaced-object queues.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-reconciler/1.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-reconciler/2.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/container-reconciler/2.conf

## Purpose
SAIO container-reconciler config for process shard 1 of 4.

## Important Sections
It mirrors the shard 0 config with `LOG_LOCAL3`, `processes = 4`, and `process = 1`. The PasteDeploy pipeline is `catch_errors proxy-logging cache proxy-server`.

## Control Flow and Integration
This daemon instance handles the second reconciler work partition and talks through the local proxy pipeline. It must be paired with the other three process configs for full queue coverage.

## State, Risks, and Test Signals
Primary risk is shard misconfiguration that overlaps or omits reconciler work. It also inherits developer-only placeholder user and optional logging defaults. Test signal is that process 1 starts and reconciler logs show distinct partition processing.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-reconciler/2.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-reconciler/3.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/container-reconciler/3.conf

## Purpose
SAIO container-reconciler config for process shard 2 of 4.

## Important Sections
Defaults use `LOG_LOCAL4` and placeholder user. `[container-reconciler]` sets `processes = 4`, `process = 2`. The internal client pipeline is `catch_errors proxy-logging cache proxy-server`.

## Control Flow and Integration
The reconciler loads this config to process one quarter of reconciler queue work and uses the configured proxy app/filter chain for internal Swift requests.

## State, Risks, and Test Signals
No direct object storage path is configured here; state changes happen through proxy requests. Risk is process-index drift from the sibling configs. Test signal is successful launch and observed processing for shard 2.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-reconciler/3.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-reconciler/4.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/container-reconciler/4.conf

## Purpose
SAIO container-reconciler config for process shard 3 of 4.

## Important Sections
Defaults use `LOG_LOCAL5`. `[container-reconciler]` sets `processes = 4`, `process = 3`. The proxy client pipeline is `catch_errors proxy-logging cache proxy-server`.

## Control Flow and Integration
This is the fourth reconciler worker config and completes the process index set `0..3`. It integrates with Swift proxy/memcache middleware for internal operations.

## State, Risks, and Test Signals
Risk centers on shard assignment consistency and placeholder SAIO values. Test signal is startup plus reconciler progress without duplicate ownership of queue partitions.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-reconciler/4.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-server/1.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/container-server/1.conf

## Purpose
SAIO container-server config for node 1, binding `127.0.0.1:6211` and storing container DBs under `/srv/1/node`.

## Important Sections
Defaults set disabled mount/fallocate, one worker, `LOG_LOCAL2`, recon cache `/var/cache/swift`, and eventlet debug. Pipeline is `healthcheck recon container-server`. Daemon sections include container replicator, updater, auditor, sync, and sharder. Sharder is enabled with low thresholds: `auto_shard = true`, `shard_container_threshold = 100`, scanner batch 10, and cleave batch 2.

## Control Flow and Integration
The container server receives proxy/internal container requests through the configured pipeline. Replicator and sharder use rsync templates and internal client config for sync. The low sharding thresholds are intended for probe tests.

## State, Risks, and Test Signals
Container DBs persist under `/srv/1/node/containers`; recon cache under `/var/cache/swift`. Risks are non-production sharding thresholds, placeholder user, and ring/config mismatch. Test signal is container CRUD, replication, recon, sync, and sharding probe behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-server/1.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-server/2.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/container-server/2.conf

## Purpose
SAIO container-server config for node 2, binding `127.0.0.2:6221` with devices under `/srv/2/node`.

## Important Sections
Defaults use `LOG_LOCAL3`, recon cache `/var/cache/swift2`, one worker, disabled mount checks/fallocate, and eventlet debug. Pipeline is `healthcheck recon container-server`. Replicator, updater, auditor, sync, and sharder sections mirror node 1, including low sharder thresholds.

## Control Flow and Integration
Swift loads this pipeline for the second simulated container node. Replicator/sharder/sync daemons use their sections to maintain replicated container DB state and shard large containers.

## State, Risks, and Test Signals
Container state lives under `/srv/2/node/containers`. Risks are SAIO-only tuning and mismatch with ring definitions. Test signal is startup and participation in container replication/sharding across all four nodes.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-server/2.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-server/3.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/container-server/3.conf

## Purpose
SAIO container-server config for node 3, binding `127.0.0.3:6231` and using `/srv/3/node`.

## Important Sections
Defaults set `LOG_LOCAL4`, recon cache `/var/cache/swift3`, disabled mount/fallocate, one worker, and eventlet debug. Pipeline is `healthcheck recon container-server`. The sharder is auto-enabled with test-friendly thresholds and rsync module template.

## Control Flow and Integration
The third container node serves requests and runs container background daemons. Container sync points at `/etc/swift/internal-client.conf`.

## State, Risks, and Test Signals
Container DBs persist under `/srv/3/node/containers`. Risks include placeholder user and test-only sharder settings. Test signals include probe tests that depend on the explicit low batch sizes.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-server/3.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-server/4.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/container-server/4.conf

## Purpose
SAIO container-server config for node 4, binding `127.0.0.4:6241` with devices under `/srv/4/node`.

## Important Sections
Defaults use `LOG_LOCAL5`, recon cache `/var/cache/swift4`, disabled mount/fallocate, one worker, placeholder user, and eventlet debug. Pipeline is `healthcheck recon container-server`; background sections configure replicator, updater, auditor, sync, and auto sharder.

## Control Flow and Integration
This file completes the four-node container service set. It integrates with recon/healthcheck middleware, container replication over rsync, internal-client based sync, and sharder probe settings.

## State, Risks, and Test Signals
Container state is under `/srv/4/node/containers`. Risks are ring mismatch and developer-only config values. Test signal is complete four-node container availability and sharding behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-server/4.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-sync-realms.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/container-sync-realms.conf

## Purpose
Defines the SAIO container-sync realm named `saio`.

## Important Sections
The `[saio]` section sets `key`, `key2`, and `cluster_saio_endpoint = http://127.0.0.1:8080/v1/`.

## Control Flow and Integration
Container sync middleware/daemon reads this file to authenticate and locate the target cluster endpoint for sync realm references. `key` and `key2` support shared-secret rotation.

## State, Risks, and Test Signals
The file does not persist object state but controls cross-cluster synchronization authorization. The `changeme` keys are test-only and unsafe in production. Test signal is container-sync acceptance of the realm and successful internal sync calls to the SAIO proxy.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/container-sync-realms.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/internal-client.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/internal-client.conf

## Purpose
Defines an internal Swift proxy client pipeline for daemons that need to issue cluster requests without using the public proxy config.

## Important Sections
Pipeline is `catch_errors proxy-logging cache symlink keymaster encryption proxy-server`. The proxy app enables `account_autocreate` and account management. Keymaster uses a placeholder `encryption_root_secret`; encryption and symlink middleware are enabled.

## Control Flow and Integration
Container sync, sharder, expirer, and other internal clients can load this pipeline to perform internal object/account/container operations. Middleware order ensures errors/logging/cache, symlink handling, keymaster, encryption, then proxy app.

## State, Risks, and Test Signals
State changes are remote Swift requests; local persistence is only middleware cache/log effects. Placeholder encryption secret is a security risk outside SAIO. Test signal is successful daemon internal requests, especially encrypted/symlink object handling.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/internal-client.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/object-expirer.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/object-expirer.conf

## Purpose
SAIO object-expirer daemon config. It scans expiration queues and deletes expired objects through a proxy pipeline.

## Important Sections
Defaults set placeholder user, `log_name = object-expirer`, `LOG_LOCAL6`, and info logging. `[object-expirer]` sets `interval = 300` and documents concurrency/process partition settings. Pipeline is `catch_errors cache proxy-server`.

## Control Flow and Integration
The expirer wakes every 300 seconds, reads queue objects, and uses the configured proxy app with cache and catch-errors middleware to issue deletes. Process options can partition work when run with multiple workers.

## State, Risks, and Test Signals
Expiration queue state is stored in Swift objects/containers, not in this file. Risks are low visibility if logging is misconfigured and accidental single-process bottleneck if concurrency/process settings remain defaults. Test signal is expiration queue processing and successful deletes through the proxy.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/object-expirer.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/object-server/1.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/object-server/1.conf

## Purpose
SAIO object-server config for node 1, binding `127.0.0.1:6210` with object data under `/srv/1/node`.

## Important Sections
Defaults set disabled mount/fallocate, one worker, `LOG_LOCAL2`, recon cache `/var/cache/swift`, and eventlet debug. Pipeline is `healthcheck recon object-server`. Background sections include object replicator, reconstructor, updater, auditor, and relinker.

## Control Flow and Integration
The object server serves object PUT/GET/DELETE through healthcheck and recon middleware. Background daemons use the same config to replicate, reconstruct EC fragments, update containers, audit disks, and relink during policy changes.

## State, Risks, and Test Signals
Object files persist under `/srv/1/node/objects` and policy-specific datadirs. Risks are SAIO-only mount/fallocate choices and ring/config mismatch. Test signal is object CRUD, recon, replication/reconstruction, updater, auditor, and relinker startup.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/object-server/1.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/object-server/2.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/object-server/2.conf

## Purpose
SAIO object-server config for node 2, binding `127.0.0.2:6220` with `/srv/2/node`.

## Important Sections
Defaults use `LOG_LOCAL3`, recon cache `/var/cache/swift2`, disabled mount/fallocate, one worker, and eventlet debug. Pipeline is `healthcheck recon object-server`; object background daemon sections are present.

## Control Flow and Integration
This is the second object service in the four-node SAIO layout and integrates with object replication, reconstruction, updates, auditing, and relinking.

## State, Risks, and Test Signals
Object state persists under `/srv/2/node`. Risks include placeholder user and mismatch between rings and bind/device settings. Test signal is node 2 object service participating in replication and object operations.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/object-server/2.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/object-server/3.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/object-server/3.conf

## Purpose
SAIO object-server config for node 3, binding `127.0.0.3:6230`.

## Important Sections
Defaults set device root `/srv/3/node`, `LOG_LOCAL4`, recon cache `/var/cache/swift3`, disabled mount/fallocate, one worker, and eventlet debug. Pipeline is `healthcheck recon object-server`. Replicator, reconstructor, updater, auditor, and relinker sections are present.

## Control Flow and Integration
Swift service scripts load this file to run the third object-server instance and its related object daemons.

## State, Risks, and Test Signals
Object fragments/files persist under `/srv/3/node`. Risks are development-only values and ring drift. Test signal is object healthcheck/recon plus background object daemon behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/object-server/3.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/object-server/4.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/object-server/4.conf

## Purpose
SAIO object-server config for node 4, binding `127.0.0.4:6240`.

## Important Sections
Defaults use `/srv/4/node`, `LOG_LOCAL5`, recon cache `/var/cache/swift4`, disabled mount/fallocate, one worker, placeholder user, and eventlet debug. Pipeline is `healthcheck recon object-server`; object background sections are present.

## Control Flow and Integration
This config completes the four object-server nodes in SAIO. It integrates with object replication/reconstruction and probe tests that expect four local loopback nodes.

## State, Risks, and Test Signals
Object data persists under `/srv/4/node`. Risks are test-only settings and ring mismatch. Test signal is full object-ring operation across all configured nodes.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/object-server/4.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/proxy-server.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/proxy-server.conf

## Purpose
SAIO public proxy-server config. It exposes Swift at `127.0.0.1:8080` with a feature-rich middleware chain used by local development and probe tests.

## Important Sections
The pipeline includes `catch_errors`, `gatekeeper`, `healthcheck`, two `proxy-logging` passes, `cache`, `etag-quoter`, `listing_formats`, `bulk`, `tempurl`, `ratelimit`, `crossdomain`, `container_sync`, `tempauth`, `staticweb`, copy/quota/SLO/DLO/versioned-writes/symlink/keymaster/encryption middleware, and `proxy-server`. Tempauth defines admin/test users. Container sync points to realm `//saio/saio_endpoint`. Versioned writes and object versioning are enabled. S3API is defined but commented as opt-in by pipeline placement.

## Control Flow and Integration
PasteDeploy applies middleware in the listed order. Public and internal client requests pass through authentication, formatting, large-object handling, versioning, symlink, encryption, and logging before the proxy app routes to rings. The duplicate proxy logging captures middleware-originated requests.

## State and Persistence Behavior
The proxy itself persists little local state; it routes to account/container/object servers and uses memcache. Middleware changes Swift cluster state: versioned writes, quotas, SLO/DLO manifests, tempurl auth, container sync, symlink targets, and encryption metadata.

## Risks and Test Signals
This is intentionally broad for SAIO; production would need real auth, secrets, TLS, and tuned middleware. Placeholder encryption secret and tempauth users are unsafe outside development. Test signals include successful proxy startup, auth with configured users, versioned-write behavior, encrypted object handling, and probe coverage across middleware.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/proxy-server.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/swift.conf -->
# sources/object-store/openstack-swift/doc/saio/swift/swift.conf

## Purpose
SAIO global Swift config defining hash path secrets and storage policies.

## Important Sections
`[swift-hash]` sets placeholder `swift_hash_path_prefix` and `swift_hash_path_suffix`. Storage policy 0 is replication policy `gold` and default. Policy 1 is replication policy `silver`. Policy 2 is erasure-coding policy `ec42` using `liberasurecode_rs_vand` with 4 data and 2 parity fragments.

## Control Flow and Integration
Swift rings and path hashing depend on the immutable hash prefix/suffix. Account, container, object, proxy, and background daemons read policies through Swift's storage policy registry.

## State and Persistence Behavior
Changing hash secrets after data exists makes stored paths unreachable. Policies determine object placement and on-disk policy datadirs; changing or removing policies affects object-server/reconstructor behavior.

## Risks and Test Signals
The `changeme` secrets are SAIO placeholders. Test signal is ring/policy loading and ability to PUT/GET objects under replicated and EC policies in the local environment.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/doc/saio/swift/swift.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/docker/rootfs/etc/swift/account-server.conf -->
# sources/object-store/openstack-swift/docker/rootfs/etc/swift/account-server.conf

## Purpose
Docker rootfs account-server config for a single containerized Swift node. It binds account service to `127.0.0.1:6202` and uses `/srv/node/`.

## Important Sections
Defaults set two workers, disabled mount check, and `LOG_LOCAL5`. Pipeline is `healthcheck recon account-server`, with account, recon, and healthcheck entry points. Account replicator, auditor, and reaper sections are present with defaults.

## Control Flow and Integration
Container startup scripts can run the account server and account background daemons using this file. It is simpler than SAIO multi-node configs because it targets one rootfs environment.

## State, Risks, and Test Signals
Account DBs persist under `/srv/node/accounts`. Risk is `mount_check = false`, appropriate for containers but unsafe if production expects mounted disks. Test signal is account service healthcheck and background daemon startup in Docker.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/docker/rootfs/etc/swift/account-server.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/docker/rootfs/etc/swift/container-server.conf -->
# sources/object-store/openstack-swift/docker/rootfs/etc/swift/container-server.conf

## Purpose
Docker rootfs container-server config binding `127.0.0.1:6201` with storage under `/srv/node/`.

## Important Sections
Defaults set two workers, disabled mount check, and `LOG_LOCAL4`. Pipeline is `healthcheck recon container-server`. Background sections include replicator, updater, auditor, and sync.

## Control Flow and Integration
The container image uses this config for the container service and maintenance daemons. It omits the SAIO sharder tuning and node-specific loopback IPs.

## State, Risks, and Test Signals
Container DBs persist under `/srv/node/containers`. Risk is that disabled mount checks allow writing to the root filesystem if volume mounts are missing. Test signal is container service startup, healthcheck, recon, and updater/replicator operation in Docker.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/docker/rootfs/etc/swift/container-server.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/docker/rootfs/etc/swift/object-server.conf -->
# sources/object-store/openstack-swift/docker/rootfs/etc/swift/object-server.conf

## Purpose
Docker rootfs object-server config binding `127.0.0.1:6200` with object storage under `/srv/node/`.

## Important Sections
Defaults set two workers, disabled mount check, and `LOG_LOCAL3`. Pipeline is `healthcheck recon object-server`. Object replicator, updater, and auditor sections are present.

## Control Flow and Integration
Object server and object maintenance daemons load this file inside the Docker rootfs. It is a compact single-node counterpart to the SAIO object configs.

## State, Risks, and Test Signals
Object data persists under `/srv/node/objects` or policy datadirs. Disabled mount checks are a container convenience but an operational risk. Test signal is object PUT/GET/DELETE through the proxy and object daemon startup.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/docker/rootfs/etc/swift/object-server.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/docker/rootfs/etc/swift/proxy-server.conf -->
# sources/object-store/openstack-swift/docker/rootfs/etc/swift/proxy-server.conf

## Purpose
Docker rootfs proxy-server config exposing Swift on `0.0.0.0:8080` with debug logging and a broad middleware chain.

## Important Sections
Defaults set syslog address, `LOG_LOCAL2`, debug level, `log_name = proxy-server`, and `user = swift`. Pipeline includes catch-errors, gatekeeper, healthcheck, proxy-logging, cache, etag-quoter, listing formats, bulk, tempurl, ratelimit, s3api, tempauth, staticweb, copy, quotas, SLO/DLO, versioned writes, symlink, proxy logging, and proxy-server. Tempauth users are defined; S3API is active in the pipeline.

## Control Flow and Integration
External Docker traffic enters this proxy. Middleware performs request validation, auth, S3 compatibility, large-object/versioning/symlink handling, logging, and final proxy routing.

## State and Persistence Behavior
Proxy state is mostly externalized to backend services and memcache. Middleware creates persistent Swift metadata for versioning, large objects, quotas, tempurl behavior, symlinks, and S3-related request semantics.

## Risks and Test Signals
Tempauth users and placeholder encryption settings are not production-grade. Debug logging can expose sensitive request details if log headers are later enabled. Test signal is Docker proxy reachability, tempauth login, S3API behavior, and object/account/container operations.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/docker/rootfs/etc/swift/proxy-server.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/docker/rootfs/etc/swift/swift.conf -->
# sources/object-store/openstack-swift/docker/rootfs/etc/swift/swift.conf

## Purpose
Docker rootfs global Swift config with concrete hash path secrets and a default single-replica storage policy.

## Important Sections
`[swift-hash]` sets fixed prefix/suffix values. `[storage-policy:0]` defines `1replica` as the default replication policy. An EC42 policy is present but commented out.

## Control Flow and Integration
All Swift services in the container read this file for path hashing and policy registry setup. The single-replica policy simplifies Docker development.

## State and Persistence Behavior
Hash secrets must remain stable for existing data. The one-replica default affects durability and ring placement expectations. Enabling the commented EC policy would require matching rings and object-server/reconstructor support.

## Risks and Test Signals
Single replica is not durable and is intended for local/container testing. Test signal is service startup with policy registry and successful object placement under policy 0.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/docker/rootfs/etc/swift/swift.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/__init__.py -->
# sources/object-store/openstack-swift/swift/__init__.py

## Purpose
Defines Swift package version discovery for installed packages and source checkouts.

## Important APIs, Types, and Functions
Module globals `__version__` and `__canonical_version__` are populated. The code first tries `importlib.metadata.distribution('swift')`; on older Python it falls back to `pkg_resources`; if no installed distribution metadata exists, it uses `pbr.version.VersionInfo('swift')`.

## Control Flow
Import-time control flow selects the lightest available version source: installed package metadata first, then pbr for source checkouts. Missing distribution metadata is tolerated until the pbr fallback.

## State and Persistence Behavior
No persistent state is written. The module exposes version strings used by other Swift code, CLI output, packaging, or logs.

## Dependencies and Integration Points
Depends on Python packaging metadata APIs and `pbr`. It integrates at package import time, so broken packaging metadata or missing pbr in source mode can make importing `swift` fail.

## Risks and Test Signals
Import-time dependency on pbr is a risk for incomplete development environments. Test signal is importing `swift` from both installed and checkout contexts and seeing valid version strings.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/account/__init__.py -->
# sources/object-store/openstack-swift/swift/account/__init__.py

## Purpose
This is an empty package marker for `swift.account`.

## Important APIs, Types, and Functions
The file defines no symbols.

## Control Flow
There is no runtime control flow beyond Python package import mechanics.

## State and Persistence Behavior
No state is read or written.

## Dependencies and Integration Points
Its integration point is package discovery: modules such as `swift.account.backend`, `auditor`, `reaper`, and `replicator` live under this package.

## Risks and Test Signals
Risk is minimal; deleting it could affect environments that still rely on explicit package marker files. Test signal is successful import of `swift.account` and submodules.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/account/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/account/auditor.py -->
# sources/object-store/openstack-swift/swift/account/auditor.py

## Purpose
Defines the account database auditor daemon. It extends the common `DatabaseAuditor` to validate account DB consistency, especially totals across storage policies.

## Important APIs, Types, and Functions
`AccountAuditor` sets `server_type = "account"` and `broker_class = AccountBroker`. `_audit(info, broker)` loads policy stats with migrations enabled, sums `container_count`, `object_count`, and `bytes_used`, and returns `InvalidAccountInfo` if any total differs from `account_stat`. `main()` parses daemon options and calls `run_daemon`.

## Control Flow
The common auditor framework opens DBs and calls `_audit`. This subclass compares global account totals against `policy_stat` totals, returning an exception object on mismatch.

## State and Persistence Behavior
The auditor reads account SQLite DBs through `AccountBroker`; with `do_migrations=True`, it may trigger schema migrations for policy stats. It does not directly repair inconsistent counts beyond invoking broker migration paths.

## Dependencies and Integration Points
Depends on `AccountBroker`, `InvalidAccountInfo`, `run_daemon`, `DatabaseAuditor`, and `parse_options`. It integrates with account-server config `[account-auditor]` sections and the broader Swift daemon framework.

## Risks and Test Signals
Migrations during audit can alter DB schema, so audit runs need normal DB locking expectations. It catches aggregate-policy drift but not every per-container corruption. Test signal is auditor detection of mismatched policy totals and clean pass on valid account DBs.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/account/auditor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/account/backend.py -->
# sources/object-store/openstack-swift/swift/account/backend.py

## Purpose
Implements Swift's account database broker. `AccountBroker` encapsulates SQLite schema creation, container record merging, account/global stats, policy stats, listing semantics, deletion detection, and legacy schema migrations.

## Important APIs, Types, and Functions
`DATADIR = 'accounts'` identifies the on-disk account DB directory. `POLICY_STAT_TRIGGER_SCRIPT` defines triggers keeping `policy_stat` in sync with container inserts/deletes. `AccountBroker` extends `DatabaseBroker` and sets account DB metadata fields.

Schema methods are `_initialize`, `create_container_table`, `create_account_stat_table`, `create_policy_stat_table`, and `get_db_version`. Data APIs include `_commit_puts_load`, `put_container`, `merge_items`, `make_tuple_for_pickle`, `empty`, `get_info`, `get_policy_stats`, `list_containers_iter`, `_is_deleted`, `_is_deleted_info`, `is_status_deleted`, `_populate_instance_cache`, and `path`. Migration helpers are `_migrate_add_container_count` and `_migrate_add_storage_policy_index`.

## Control Flow
Creating a new DB validates that `self.account` is set, creates the container table plus triggers, initializes account stats, and creates policy stats. Container updates are append/merge oriented: `put_container` creates a record and delegates to `put_record`; `merge_items` deletes old active/deleted rows for the container and inserts the winning record after timestamp comparison.

Listing commits pending puts, builds SQL based on marker/end_marker/prefix/delimiter/reverse flags, handles reserved names, works around legacy schema differences, and synthesizes subdir rows when delimiter grouping is requested. Policy stats reads attempt the modern schema, then migrate or degrade gracefully when older DBs lack `container_count`, `policy_stat`, or `storage_policy_index`.

## State and Persistence Behavior
State is a SQLite account DB containing `container`, `account_stat`, and `policy_stat` tables plus triggers. `container_insert` and `container_delete` update aggregate account stats and hash; policy triggers update per-policy counts/bytes. `incoming_sync` is updated during replication merges with source sync points. Deletion state is derived from `status = DELETED` or delete timestamp newer than put timestamp with zero containers.

## Dependencies and Integration Points
Depends on `sqlite3`, `Timestamp`/`NormalTimestamp`, `DatabaseBroker`, `zero_like`, and `RESERVED_BYTE`. It integrates with account server request handling, account replicator, auditor, reaper, and any code that lists containers or reads account totals.

## Risks and Edge Cases
Triggers make aggregate correctness dependent on insert/delete discipline; direct updates are forbidden by trigger. Legacy migration paths are complex and must preserve stats while adding storage policy support. `merge_items` timestamp conflict logic is critical for replication convergence. Delimiter listing logic mutates markers in subtle ways, especially with reverse listings. Reserved-byte filtering can hide internal namespace entries unless explicitly allowed. Schema migrations during reads can surprise callers if DB permissions/locking are constrained.

## Test Signals
Expected tests should cover schema creation, policy stat migrations, merge conflict resolution, listings with marker/prefix/delimiter/reverse/reserved names, deletion detection, and auditor total validation. This file itself has no tests, but `auditor.py`, `reaper.py`, and account-server behavior depend on it.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/account/backend.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/account/reaper.py -->
# sources/object-store/openstack-swift/swift/account/reaper.py

## Purpose
Defines the account reaper daemon, which deletes containers and objects belonging to accounts marked deleted. It scans local primary account DBs, deletes objects through object servers, deletes containers through container servers, and records progress metrics.

## Important APIs, Types, and Functions
`AccountReaper` extends `Daemon`. Initialization reads devices, mount checking, interval, Swift directory, timeouts, bind IP/port, concurrency, DB preallocation, delay/reap warning settings, and creates green pools. Ring helpers are `get_account_ring`, `get_container_ring`, and `get_object_ring`. Main work methods are `run_forever`, `run_once`, `reap_device`, `reset_stats`, `reap_account`, `reap_container`, and `reap_object`. `main()` parses daemon options and runs the daemon.

## Control Flow
`run_forever` sleeps a randomized initial offset and repeatedly calls `run_once`. `run_once` iterates devices, validates mounted drives, and calls `reap_device`. `reap_device` walks account DB paths by partition/suffix/hash, checks whether the local device is a primary for the partition, opens account DBs, and reaps those with deleted status and non-empty listings.

`reap_account` enforces delay_reaping, pages through containers, shards container ownership when multiple account primaries exist, spawns `reap_container`, waits, logs stats, and warns if an account remains unreaped too long. `reap_container` lists objects from a selected container node, spawns object deletes, then sends container deletes to all container nodes with account update headers. `reap_object` gets the policy-specific object ring and sends object deletes to all object nodes with container update headers.

## State and Persistence Behavior
The reaper reads account DBs from the account datadir and mutates cluster state via direct DELETE requests. It does not remove account DBs itself; final DB reclamation is left to account replication/reclaim. In-memory counters track return code classes and deleted/remaining/possibly remaining objects and containers for logging/metrics.

## Dependencies and Integration Points
Depends on eventlet-style `GreenPool`, `Timeout`, Swift rings, direct client functions, `AccountBroker`, `check_drive`, storage policies, request helper headers, daemon utilities, logging utilities, and account/container/object server direct APIs.

## Risks and Edge Cases
Concurrency is split as square root of configured concurrency, so non-square values create float pool sizes if the GreenPool implementation does not coerce. The chosen container listing node is `nodes[-1]`, so failures there can leave containers remaining until retry. Partial success increments "possibly remaining" stats. Policy lookup failures leave objects remaining. The code updates object stats inside the loop over object nodes, which may overcount per-object outcomes if this exact version is used. Reaper safety depends on correct primary-device detection and replication network headers.

## Test Signals
Good tests should mock rings and direct clients to cover deleted account discovery, delay_reaping, container shard selection, object delete success/failure/timeout, invalid policy, stats accounting, and warning thresholds. Operational signals are reaper logs, return-code metrics, and decreasing container/object counts for deleted accounts.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/account/reaper.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/account/replicator.py -->
# sources/object-store/openstack-swift/swift/account/replicator.py

## Purpose
Defines the account replicator daemon by specializing Swift's common database replicator for account databases.

## Important APIs, Types, and Functions
`AccountReplicator` extends `db_replicator.Replicator` and sets `server_type = 'account'`, `brokerclass = AccountBroker`, `datadir = DATADIR`, and `default_port = 6202`. `main()` adds `--devices` and `--partitions` options for one-shot scoped replication, parses options, and runs the daemon.

## Control Flow
The common replicator framework handles scanning devices/partitions, comparing DB states, rsync/HTTP replication, and cleanup. This subclass supplies the account-specific broker, datadir, and default port.

## State and Persistence Behavior
Persistent state is account SQLite DBs under the `accounts` datadir and replication metadata such as sync points in DB tables. The replicator converges account DBs across nodes and eventually reclaims tombstoned DBs.

## Dependencies and Integration Points
Depends on `AccountBroker`, `DATADIR`, `swift.common.db_replicator`, `run_daemon`, and `parse_options`. It integrates with account-server config `[account-replicator]`, rsync modules, rings, and broker merge logic.

## Risks and Test Signals
Most risk is inherited from common DB replication: stale sync points, rsync config mismatch, broker migration compatibility, and scoped `--devices`/`--partitions` only applying in once mode. Test signal is account DB convergence across replicas and correct handling of scoped one-shot replication.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/account/replicator.py -->

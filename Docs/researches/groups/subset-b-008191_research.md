# subset-b-008191 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-metadata-utils_test.go -->
## sources/object-store/minio/cmd/erasure-metadata-utils_test.go

Purpose: validates low-level erasure metadata utility behavior used by the object layer before higher-level object and multipart paths rely on it. The file exercises disk counting, quorum error reduction, object-to-disk distribution hashing, disk shuffling, and evaluation of disks after per-disk errors.

Important APIs and functions under test: `diskCount`, `reduceReadQuorumErrs`, `reduceWriteQuorumErrs`, `hashOrder`, `shuffleDisks`, `evalDisks`, `getRandomDisks`, `initObjectLayer`, `mustGetPoolEndpoints`, and `erasureServerPools`/`xlStorage` setup helpers. `Test_hashOrder` also probes distribution statistically by repeatedly checking which disk ordinal appears first.

Control flow: table-driven tests verify deterministic outputs for small cases, then integration-style setup creates 16 temporary disks and an erasure object layer to test shuffling against actual `StorageAPI` instances. `TestReduceErrs` builds representative error arrays, including wrapped `context.Canceled`, and checks read/write reducers against fixed quorum values. `TestHashOrder` asserts stable rotations for many object names, including unicode and invalid byte input.

State and persistence behavior: the tests create temporary disk roots for object-layer initialization but do not persist application objects. Their main state is in-memory disk slices and temporary storage roots removed with `removeRoots`.

Dependencies and integration points: depends on MinIO test helpers for erasure disks, `StorageAPI`, `xlStorage`, `erasureServerPools`, and quorum errors. These tests are upstream signals for `erasure-metadata.go`, `erasure-object.go`, and multipart/object code paths that assume deterministic disk ordering and meaningful quorum error reduction.

Risks: coverage is strong for deterministic cases but `TestEvalDisks` currently calls `testShuffleDisks`, so it does not appear to directly assert `evalDisks` behavior despite the test name. `Test_hashOrder` logs distribution rather than asserting statistical bounds, making it diagnostic rather than a failing correctness gate.

Test signals: validates that ignored disk errors do not dominate reductions, that wrapped cancellations collapse to `context.Canceled`, and that `hashOrder` returns nil for invalid counts. These signals protect against regressions in object placement and quorum handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-metadata-utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-metadata.go -->
## sources/object-store/minio/cmd/erasure-metadata.go

Purpose: central metadata adapter for MinIO erasure-coded objects. It converts internal `FileInfo`/`ErasureInfo` metadata into S3-facing `ObjectInfo`, manages object parts, finds a quorum-consistent `FileInfo`, computes object read/write quorum from xl.meta copies, and exposes helpers for tier-free-version and replication state metadata.

Important APIs and functions: `ErasureInfo.GetChecksumInfo`, `ShardFileSize`, `ShardSize`; `FileInfo.IsValid`, `ToObjectInfo`, `TransitionInfoEquals`, `MetadataEquals`, `ReplicationInfoEquals`, `AddObjectPart`, `ObjectToPartOffset`; `findFileInfoInQuorum`/`pickValidFileInfo`; `writeAllMetadataWithRevert`, `writeAllMetadata`, `writeUniqueFileInfo`; `listObjectParities`, `commonParity`, `objectQuorumFromMeta`; tier-free-version methods; `GetInternalReplicationState`/`getInternalReplicationState`.

Control flow: `ToObjectInfo` decodes directory-object names, normalizes null version IDs for versioned buckets, lifts metadata headers into strongly typed object fields, strips response-internal metadata, resolves storage class, restore status, checksums, inline-data status, replication, purge, and transition information. `findFileInfoInQuorum` hashes only quorum-relevant fields for candidate metadata with matching modtime or etag, counts matching hashes, and then overlays successor modtime and version count only if those secondary properties also reach quorum. `objectQuorumFromMeta` first checks a baseline read quorum, chooses the common parity from usable metadata, then derives read quorum as data blocks and write quorum as data blocks plus one for symmetric data/parity layouts.

State and persistence behavior: the file persists only by calling per-disk `WriteMetadata` or `Delete` through `StorageAPI`. `writeAllMetadataWithRevert` writes xl.meta concurrently, evaluates write quorum, and optionally reverts successful writes on quorum failure. `writeUniqueFileInfo` disables revert for cases where unique per-disk metadata must remain coordinated by the caller. Tier-free-version and replication helpers encode state into reserved metadata keys.

Dependencies and integration points: depends on lifecycle state for tiered parity handling, replication status types, crypto metadata detection, MinIO HTTP header constants, SHA-256 hashing, and errgroup parallelism. Object and multipart implementations call these helpers for every metadata read/write, quorum decision, object-info response, tag/restore/transition state, and part index calculation.

Risks: quorum hashing intentionally ignores `DataDir`, allowing reads across disks with different data directories after historical rebalance races; this is necessary compatibility behavior but means data validation must happen later in bitrot readers. Incorrect parity inference can cause read/write quorum to be too permissive or too strict. Metadata map mutation requires callers to clone or own maps correctly. Revert-on-failure deletes `xl.meta` at the prefix, so callers must pass correct buckets and prefixes.

Test signals: `erasure-metadata_test.go` covers part insertion/replacement, object offset mapping, quorum selection including successor modtime/NumVersions, transition equality, tier-free-version skip marker, and tiered/non-tiered parity selection. `erasure-object_test.go` indirectly verifies `objectQuorumFromMeta` under storage-class variations.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-metadata_test.go -->
## sources/object-store/minio/cmd/erasure-metadata_test.go

Purpose: unit coverage for the metadata helpers that maintain `FileInfo` part layout, choose quorum-consistent metadata, compare transition state, handle tier-free-version markers, and compute per-object parity/quorum.

Important APIs and functions under test: `FileInfo.AddObjectPart`, `objectPartIndex`, `FileInfo.ObjectToPartOffset`, `findFileInfoInQuorum`, `FileInfo.TransitionInfoEquals`, `SetSkipTierFreeVersion`/`SkipTierFreeVersion`, `listObjectParities`, and `commonParity`. It uses `newFileInfo`, `UTCNow`, `mustGetUUID`, storage-class-sized erasure metadata, and lifecycle transition fields.

Control flow: tests build synthetic `FileInfo` arrays with controlled erasure indexes, modtimes, parts, successor modtimes, version counts, transition metadata, and invalid entries. `TestFindFileInfoInQuorum` uses helper-generated arrays to validate both quorum failures and secondary-property quorum overlays. `TestListObjectParities` constructs tiered and non-tiered cases across 15- and 16-disk layouts to assert the difference between simple-majority tiered metadata quorum and EC data-block quorum.

State and persistence behavior: all state is in memory. The tests do not initialize disks except through synthetic `FileInfo` values, making them fast and tightly scoped to pure metadata behavior.

Dependencies and integration points: integrates with the same metadata primitives consumed by `erasure-object.go` and `erasure-multipart.go`. The tests encode assumptions about `humanize.MiByte` part sizes, lifecycle transition complete semantics, invalid erasure indexes, and the `InsufficientReadQuorum` error type.

Risks: tests assert type class for `InsufficientReadQuorum` rather than full error internals in some places, so changes to quorum reason classification may need additional coverage. `ObjectToPartOffset` accepts a negative offset case as valid in the current logic, which is an unusual behavior and should be preserved only if all callers constrain public ranges beforehand.

Test signals: strong regression signals for sorted part insertion, replacement of existing parts, offset-to-part mapping boundaries, quorum threshold behavior, secondary version summary propagation, transition metadata equality, and parity derivation for transitioned objects.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-multipart-conditional_test.go -->
## sources/object-store/minio/cmd/erasure-multipart-conditional_test.go

Purpose: regression tests for conditional multipart APIs when the existing object cannot be read with quorum. It specifically verifies that conditional requests do not proceed or degrade into object-not-found decisions when MinIO cannot reliably evaluate `If-Match` or `If-None-Match`.

Important APIs and functions under test: `NewMultipartUpload`, `CompleteMultipartUpload`, `PutObject`, `PutObjectPart`, `GetObjectInfo`, `prepareErasure16`, `isErrReadQuorum`, and `ObjectOptions.CheckPrecondFn`/`HasIfMatch`. It also uses `xhttp.IfNoneMatch`, `xhttp.IfMatch`, multipart `CompletePart`, and `humanize.MiByte`.

Control flow: each test creates a 16-disk erasure layer, uploads an initial object, captures its ETag, then overrides the set's disk getter to nil out the first eight disks. With EC 8+8, this leaves only eight disks where read quorum is nine. Subtests run conditional initiate and complete paths with `if-none-match`, correct `if-match`, and wrong `if-match` cases.

State and persistence behavior: the tests create real bucket/object/multipart state in temporary erasure roots. They mutate the in-memory disk view through `erasureDisksMu` to simulate a read quorum failure without physically deleting data.

Dependencies and integration points: directly exercises conditional branches in `erasure-multipart.go`, which call `getObjectInfo` before initiating or completing multipart operations. It depends on object-layer locking and read quorum semantics from `erasure-object.go` and `erasure-metadata.go`.

Risks: the test manipulates shared disk slice contents in place; this is acceptable for isolated tests but requires care if helpers begin sharing disk slices across subtests. The second `NewMultipartUpload` wrong-ETag subtest logs instead of failing when a non-read-quorum error appears, so that scenario is a weaker guard than the surrounding cases.

Test signals: protects issue 21603 behavior: conditional multipart operations must return read quorum errors when preconditions cannot be evaluated. It covers both initiate and complete operations.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-multipart-conditional_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-multipart.go -->
## sources/object-store/minio/cmd/erasure-multipart.go

Purpose: implements erasure-coded S3 multipart upload lifecycle: initiate, list uploads, upload parts, list parts, complete, abort, and cleanup stale multipart state. It persists upload metadata and part shards under `.minio.sys/multipart`, then atomically promotes completed data into the target bucket/object namespace.

Important APIs and functions: `getUploadIDDir`, `getMultipartSHADir`, `checkUploadIDExists`, `cleanupMultipartPath`, `cleanupStaleUploads`, `cleanupStaleUploadsOnDisk`, `ListMultipartUploads`, `newMultipartUpload`/`NewMultipartUpload`, `renamePart`, `PutObjectPart`, `GetMultipartInfo`, `listParts`, `ListObjectParts`, `readParts`, `objPartToPartErr`, `CompleteMultipartUpload`, and `AbortMultipartUpload`.

Control flow: initiate optionally evaluates conditional headers under a namespace lock, determines parity from storage class and availability-optimized settings, creates a `FileInfo` with fresh `DataDir`, stores upload checksum requirements, shuffles disks by erasure distribution, and writes upload `xl.meta`. Part upload validates the upload, enforces requested checksum type, erasure-encodes the incoming stream into temporary part shards, serializes same-part replacements with a part lock, holds an upload read lock, and renames temp shards plus serialized `ObjectPartInfo` metadata into the upload's data directory. Complete revalidates conditionals, reads requested part metadata in quorum, verifies ETags and checksums including encrypted ETag handling, enforces minimum part size, computes final size and multipart checksum/ETag, cleans skipped parts, takes the object lock, calls `renameData` from multipart namespace to final bucket/object, commits old data-dir cleanup, queues partial-heal state as needed, and removes the upload directory on success.

State and persistence behavior: multipart state lives under `minioMetaMultipartBucket` keyed by SHA-256 of bucket/object and upload UUID. Temporary part shards are written under `minioMetaTmpBucket`; committed part shards and `.meta` files live under upload `DataDir`; final object metadata is written with `RenameData`. Stale uploads and tmp directories are moved into deleted/tmp areas rather than synchronously deep-deleted. Abort deletes the upload ID path after validating it exists.

Dependencies and integration points: depends on erasure encoding/decoding, bitrot writers, namespace locks, checksum/hash package, crypto metadata and SIO sizing, storage-class config, global deployment ID, global byte pools, readahead for large streams, `StorageAPI` operations (`ListDir`, `RenamePart`, `ReadParts`, `DeleteBulk`, `ReadVersion`, `StatVol`), and object helpers such as `objectQuorumFromMeta`, `writeAllMetadata`, `renameData`, `commitRenameDataDir`, and `addPartial`.

Risks: conditional paths are high-risk because they must not treat read-quorum failure as non-existence. ETag comparison is complex under encryption because persisted ETags can be encrypted or transformed. Part listing requires both `part.N` and `part.N.meta` quorum; partial failures can expose invalid-part errors. Cleanup runs across disks best-effort and must not remove live upload state. Availability-optimized parity upgrades change object quorum and must be reflected in metadata consistently.

Test signals: `erasure-object_test.go` checks repeated `PutObjectPart` replacement. `erasure-multipart-conditional_test.go` verifies conditional initiate and complete behavior under read quorum failure. Metadata tests cover part list helpers that complete depends on indirectly.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-multipart.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-object-conditional_test.go -->
## sources/object-store/minio/cmd/erasure-object-conditional_test.go

Purpose: regression tests for conditional single PUT behavior when existing-object metadata cannot be read with quorum. The intended invariant is that `PutObject` with conditional headers must fail with a read quorum error instead of overwriting or misclassifying the object state.

Important APIs and functions under test: `PutObject`, `GetObjectInfo`, `prepareErasure16`, `isErrReadQuorum`, `ObjectOptions.CheckPrecondFn`, and HTTP metadata keys `xhttp.IfNoneMatch`/`xhttp.IfMatch`.

Control flow: the test creates a 16-disk erasure setup, uploads an initial object, reads its ETag, then overrides the first eight disks to `nil` while holding the erasure disk mutex. Three subtests try `If-None-Match: *`, correct `If-Match`, and wrong `If-Match`, each using a `CheckPrecondFn` that would normally evaluate object info.

State and persistence behavior: uses real temporary erasure roots and a real object, then simulates disk outage through the set disk function. No final cleanup beyond standard shutdown/root removal is needed.

Dependencies and integration points: directly exercises the precondition branch at the start of `erasureObjects.putObject`, which calls `getObjectInfo` under the object namespace lock. It depends on read quorum calculations from `erasure-metadata.go` and disk availability behavior in the erasure set.

Risks: disk-slice mutation is intentionally invasive and should remain isolated. The second subtest does not set `HasIfMatch`, while the multipart variant does for some cases; this still covers read-quorum propagation through `CheckPrecondFn`, but `HasIfMatch`-specific logic is less directly tested here.

Test signals: protects issue 21603 for single-object PUT. The key signal is that all conditional writes return read quorum errors when the existing object cannot be verified.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-object-conditional_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-object.go -->
## sources/object-store/minio/cmd/erasure-object.go

Purpose: core erasure object implementation for MinIO object operations: copy metadata, get object data/info, put objects, delete objects/versions, update metadata/tags, transition objects to remote tiers, restore transitioned objects, and decommission tiered metadata. It is the main bridge between S3 object semantics and per-disk erasure-coded `xl.meta` plus part data.

Important APIs and functions: `countOnlineDisks`, `CopyObject`, `GetObjectNInfo`, `getObjectWithFileInfo`, `GetObjectInfo`, `deleteIfDangling`, `readAllRawFileInfo`, `pickLatestQuorumFilesInfo`, `readAllXL`, `getObjectFileInfo`, `getObjectInfo`, `getObjectInfoAndQuorum`, `renameData`, `putMetacacheObject`, `PutObject`/`putObject`, `deleteObjectVersion`, `DeleteObjects`, `commitRenameDataDir`, `deletePrefix`, `DeleteObject`, `addPartial`, `PutObjectMetadata`, `PutObjectTags`, `updateObjectMetaWithOpts`, `DeleteObjectTags`, `GetObjectTags`, `TransitionObject`, `RestoreTransitionedObject`, `restoreTransitionedObject`, and `DecomTieredObject`.

Control flow: reads acquire namespace read locks, fetch metadata from disks, compute quorum, pick a valid `FileInfo`, reject delete markers appropriately, and then either return metadata, stream inline data, pull remote tier data, or erasure-decode requested byte ranges part by part through bitrot readers. Writes optionally evaluate preconditions under a write lock, determine parity/storage class, create per-disk `FileInfo`, erasure-encode to temp bucket or inline buffers, fill metadata/ETag/checksum fields, lock the object, `renameData` into final namespace, clean old data directories, and queue MRF heal work for offline or version-divergent disks. Deletes use majority write quorum, create delete markers or delete versions depending on versioning/replication/lifecycle options, and bulk-delete versions per disk for multi-object operations.

State and persistence behavior: object data is stored as erasure shards in `bucket/object/<DataDir>/part.N` with `xl.meta` holding versions, erasure layout, metadata, checksums, transition markers, replication state, inline data, and delete markers. Temporary writes go through `minioMetaTmpBucket`; `RenameData` atomically installs new metadata and data while returning old data dir/version divergence. `commitRenameDataDir` removes old data shards after successful rename. Dangling objects may be deleted via `DeleteVersion` and audited. Transition moves content to a configured tier and replaces local data with transition metadata; restore rehydrates either through single PUT or multipart using original part boundaries.

Dependencies and integration points: integrates with `StorageAPI`, erasure coding, bitrot readers/writers, namespace locking, global storage class, lifecycle, object lock, replication config/state, crypto/SSE, hash checksums, SIO encrypted sizing, remote tier drivers, event/audit logging, global MRF partial-heal queue, byte pools, and metadata helpers from `erasure-metadata.go`. Multipart completion reuses `renameData` and `commitRenameDataDir`.

Risks: correctness depends on distinguishing read quorum, write quorum, inconsistent metadata, and not-found errors. Inline-data and non-inline metadata can coexist across disks and must be filtered carefully. `getObjectFileInfo` has fast-path behavior that can return early for inline data but must wait for all disks to resolve latest versions. Dangling deletion is destructive and gated by `isObjectDangling`; incorrect classification could remove recoverable data. Transition/restore paths combine local locks, remote tier IO, and metadata mutation, so partial failures must leave retryable restore headers and heal signals. A minor code smell: `joinErrs` iterates over `range s` rather than `range errs`, which appears to produce empty joined error tags.

Test signals: `erasure-object_test.go` covers repeated part replacement, delete basics, versioned deletes across one/two pools, delete quorum failures, read/write no-quorum behavior, inline-to-non-inline overwrite, storage-class-derived quorum, mixed inline/non-inline metadata, and outdated disks. `erasure-object-conditional_test.go` verifies conditional PUT under read quorum failure.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-object_test.go -->
## sources/object-store/minio/cmd/erasure-object_test.go

Purpose: integration-style tests for erasure object behavior across multipart part replacement, deletes, quorum failures, inline data, storage-class quorum derivation, mixed inline metadata, and outdated disk data. The file uses real temporary erasure object layers and fault-injection disk wrappers.

Important APIs and functions under test: `PutObject`, `GetObjectNInfo`, `GetObjectInfo`, `DeleteObject`, `DeleteObjects`, `NewMultipartUpload`, `PutObjectPart`, `objectQuorumFromMeta`, `readAllFileInfo`, and setup helpers `prepareErasure16`, `prepareErasure`, `prepareErasurePools`, `prepareErasureSets32`, `ExecObjectLayerTestWithDirs`. Faults are injected with `newNaughtyDisk`, direct disk nils, data-dir deletion, and storage-class updates.

Control flow: tests create buckets and objects, then mutate disk availability or contents to verify expected error behavior. Delete tests cover invalid names, missing objects, versioned deletes, duplicate delete requests, two-pool version placement, and erasure-set object distribution. No-quorum tests remove data or make disks fail after a few calls, then check read/write errors. Inline tests upload a tiny object then overwrite with larger data to ensure reads remain correct. `TestObjectQuorumFromMeta` uploads objects under multiple storage-class configs and asserts derived read/write quorums. Archive-based and outdated-disk tests verify reads across inconsistent disk states.

State and persistence behavior: creates and removes temporary filesystem roots, writes real `xl.meta` and part data, sometimes reads disk files directly, deletes data directories while preserving metadata, and unzips a sample mixed inline/non-inline `xl.meta` fixture. It mutates global storage-class config and object-layer globals in selected tests.

Dependencies and integration points: depends on MinIO erasure setup helpers, `StorageAPI`, disk mutexes, `naughtyDisk`, storage-class package, filesystem paths, crypto random input, MD5 checks, and `testdata/xl-meta-inline-notinline.zip`. It exercises the interactions between `erasure-object.go`, `erasure-multipart.go`, and `erasure-metadata.go`.

Risks: many tests mutate global storage class or disk getter state; cleanup and reset discipline are important to avoid order sensitivity. Tests are heavier than pure unit tests and may be skipped/fragile on platform-specific filesystem behavior; `TestGetObjectWithOutdatedDisks` skips Windows. Some no-quorum tests compare wrapped errors with `errors.Is`, while others compare exact object errors, so error wrapping changes can affect tests unevenly.

Test signals: provides broad regression coverage for write/read/delete quorum boundaries, availability-optimized parity behavior, object version deletion semantics, MRF-worthy partial states, inline data compatibility, storage-class quorum computation, and read repair tolerance for outdated disks.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-object_test.go -->

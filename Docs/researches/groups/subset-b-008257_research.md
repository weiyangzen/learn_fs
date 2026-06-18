# subset-b-008257 Research

Grouped research for RustFS ecstore store API read planning, storage API traits, object API data models, and erasure-format store initialization.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store_api/readers.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store_api/readers.rs

## Purpose

`readers.rs` is the read/write stream adaptation layer for ecstore object I/O. It wraps upload streams in `PutObjReader`, builds `GetObjectReader` pipelines for normal, ranged, compressed, encrypted, and encrypted-plus-compressed object reads, and translates S3-visible byte ranges into the physical offsets that erasure/disk code should fetch. It also resolves server-side encryption material for RustFS-managed SSE, SSE-C, and MinIO-compatible metadata layouts, including rio-v2 DARE package alignment when the `rio-v2` feature is enabled.

## Important APIs, Types, and Functions

- `PutObjReader` owns a `HashReader` upload stream. `new`, `as_hash_reader`, `from_vec`, `size`, and `actual_size` provide a minimal adapter used by `ObjectIO::put_object` and multipart write APIs. `from_vec` computes a SHA-256 hex digest for non-empty in-memory data.
- `GetObjectReader` owns `Box<dyn AsyncRead + Unpin + Send + Sync>` plus the visible `ObjectInfo`. `new` returns `(reader, storage_offset, storage_length)`, allowing the storage layer to fetch only the needed physical byte span before applying read transforms. `read_all` is a convenience collector, and `AsyncRead` delegates to the boxed stream.
- `HTTPRangeSpec` models inclusive HTTP ranges and suffix ranges. `from_object_info` turns `ObjectOptions.part_number` into a plaintext range over multipart parts, using `actual_size` when present. `get_offset_length` and `get_length` validate and clamp ranges against visible resource size.
- `ReadPlan` is the internal planner. It records physical `storage_offset`, physical `storage_length`, visible `object_size`, and a `ReadTransform`.
- `ReadTransform` has `Plain`, `Compressed`, and `Encrypted` variants. The encrypted variant can additionally carry compression metadata so decryption, decompression, and final visible range slicing happen in the right order.
- `RangedDecompressReader` skips bytes in a sequential decompressed stream, then returns only the requested range. With `new_draining`, it drains the remaining stream after the requested bytes are returned to avoid upstream erasure-pipeline broken pipes.
- `StreamConsumer` drains an inner stream on drop for rio-v2 paths where downstream range readers may stop early.
- `SkipReader` discards a fixed number of bytes from an already-decrypted stream, mainly for DARE package interior offsets.
- Encryption helpers include `resolve_encryption_material`, `resolve_ssec_material`, `resolve_managed_material`, `normalize_managed_metadata`, `decrypt_local_sse_dek`, `decrypt_rustfs_local_sse_dek`, and, behind `rio-v2`, MinIO object-key unsealing helpers such as `try_unseal_minio_object_key`.
- Offset helpers include `get_compressed_offsets`, rio-v2 `get_encrypted_offsets`, `encrypted_plaintext_size`, `is_multipart_encrypted_object`, `multipart_plaintext_size`, and `multipart_part_numbers`.

## Control Flow

`GetObjectReader::new` delegates to `ReadPlan::build` and then `ReadPlan::into_reader`. Planning first injects a part-number range from `ObjectOptions` when no explicit HTTP range was supplied. It then determines whether the object is compressed via `ObjectInfo::compression_read_plan` and encrypted via `ObjectInfo::is_encrypted`. Active restore requests deliberately disable encryption and compression transforms so the restore path reads plain restored data with plain range semantics.

For compressed, unencrypted reads, planning computes the visible size with `ObjectInfo::get_actual_size`. A requested visible range is mapped through `get_compressed_offsets`, which walks multipart parts, uses per-part compression indexes when available, and returns a physical compressed offset plus a decompressed skip amount. The physical fetch length is `oi.size - physical_off` so decompression can continue from the located block to the end. `into_reader` then wraps the storage reader in `crate::rio::decompression_reader`, optionally `StreamConsumer`, and either `RangedDecompressReader` for partial visible ranges or `LimitReader` for full decompressed output.

For encrypted reads, planning first resolves material. SSE-C requires caller headers for algorithm, base64 key, and key MD5, and validates the supplied key against stored metadata. Managed SSE accepts RustFS metadata and, under `rio-v2`, MinIO-style metadata normalized into RustFS header names. If a global KMS service exists, it decrypts the encrypted DEK; otherwise local fallback decryption uses `__RUSTFS_SSE_SIMPLE_CMK`, `RUSTFS_SSE_S3_MASTER_KEY`, or an all-zero key. The planner derives plaintext size from encrypted original-size metadata, multipart part actual sizes, or compressed actual size. Ranged encrypted reads either fetch the whole object for legacy backends, map the requested plaintext offset to a DARE package boundary via `get_encrypted_offsets`, or, for encrypted compressed rio-v2 objects, use `get_compressed_offsets` to land on a compression block and DARE package boundary. `into_reader` constructs the correct rio decrypt reader, skips package-internal bytes if needed, decompresses if needed, and applies visible range slicing.

Plain reads are the simple fallback: `HTTPRangeSpec` is evaluated against `oi.size`; `storage_offset`, `storage_length`, and visible object size are all plain object values. No wrapper is added around the storage reader.

`RangedDecompressReader::poll_read` loops, reading into an internal scratch buffer, advancing `current_offset`, discarding bytes until `target_offset`, and then copying bounded bytes into the caller buffer until `target_length` is reached. If EOF appears before the target offset, it returns `UnexpectedEof`. Its drop path starts draining only after the target range has been returned.

## State and Persistence Behavior

This file does not persist object metadata itself, but it interprets persistent `ObjectInfo.user_defined` metadata and `ObjectInfo.parts` fields written elsewhere. Important persisted metadata includes compression scheme and actual-size headers, RustFS managed-encryption DEK/IV/context/original-size headers, SSE-C key MD5 and original-size headers, and MinIO internal encryption headers under `rio-v2`. The returned `GetObjectReader.object_info.size` is rewritten to the visible response size, while the original `ObjectInfo` metadata is cloned. No durable writes are performed; spawned drain tasks are transient runtime cleanup.

## Dependencies and Integration Points

The module depends on `tokio::io::AsyncRead`, `HashReader`, `LimitReader`, `ObjectInfo`, `ObjectOptions`, `CompressionAlgorithm`, `rustfs_rio`/`crate::rio` encryption and compression readers, `rustfs_kms` global encryption service, `rustfs_utils::http` SSE header constants, `rustfs_utils::path::path_join_buf`, `aes-gcm`, `base64`, `md5`, and rio-v2-only `hmac`, `sha2`, and `serde`. It is consumed by implementations of `ObjectIO::get_object_reader` and by tests that instantiate readers directly. Its `(storage_offset, storage_length)` output is a critical integration point with erasure-coded object retrieval because storage must pass the matching physical byte span into the reader pipeline.

## Risks and Edge Cases

- Range semantics cross three coordinate systems: visible plaintext, compressed stream, and encrypted DARE package offsets. Bugs here can return wrong bytes while still producing plausible lengths.
- Legacy encryption backends fetch the whole encrypted object for ranged reads, which is correct but potentially expensive for large objects.
- `local_sse_master_key` falls back to an all-zero key when no KMS or local key env var is configured. That supports compatibility/tests but is security-sensitive if accidentally relied on in production.
- Case-insensitive metadata lookup reduces compatibility risk, but metadata normalization has many feature-gated branches; non-rio-v2 builds cannot consume MinIO sealed-key variants.
- `RangedDecompressReader::new_with_drain` rejects `offset >= total_size`, so a zero-length range exactly at EOF is invalid even though some HTTP-style interpretations may allow an empty body.
- Drain tasks are spawned and not awaited; they intentionally clean up upstream readers but may hide downstream errors.
- `ObjectInfo::is_encrypted` can classify objects as encrypted from broad metadata prefixes. If metadata is incomplete, reads fail late with "encrypted object metadata is incomplete."

## Test Signals

The file has extensive in-module tests. They cover `HTTPRangeSpec` suffix and part-number behavior, compressed range physical offset planning, headerless MinIO/rio-v2 compression indexes, `RangedDecompressReader` normal, partial, zero-length, and out-of-bounds behavior, restore-request bypass of transforms, missing SSE-C header rejection, managed SSE full and ranged reads, local managed fallback, MinIO metadata compatibility under rio-v2, SSE-C full and ranged reads, sealed object-key reads, DARE package offset selection, and encrypted-plus-compressed range reads. These tests are strong signals for read-planning behavior but mostly use in-memory cursors rather than full erasure backend integration.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store_api/readers.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store_api/traits.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store_api/traits.rs

## Purpose

`traits.rs` defines the async interface boundary for ecstore storage implementations. It decomposes the full object-store API into focused traits for object I/O, bucket operations, object metadata and lifecycle operations, listing/walking, multipart upload, healing, and namespace locking. `StorageAPI` then composes the major operation groups into the unified storage contract used by higher-level S3 handlers and service code.

## Important APIs, Types, and Functions

- `ObjectIO` exposes `get_object_reader` and `put_object`. Reads accept bucket/object names, optional `HTTPRangeSpec`, request headers, and `ObjectOptions`, and return `GetObjectReader`. Writes accept `PutObjReader` and return `ObjectInfo`.
- `BucketOperations` contains `make_bucket`, `get_bucket_info`, `list_bucket`, and `delete_bucket`.
- `ObjectOperations` covers `get_object_info`, `verify_object_integrity`, `copy_object`, delete by version, regular delete, batch delete, metadata update, tag get/put/delete, partial markers, transition, and restore of transitioned objects.
- `ListOperations` covers V2 listing, version listing, and a streaming `walk` that sends `ObjectInfoOrErr` through an mpsc channel and accepts a `CancellationToken`.
- `MultipartOperations` includes listing active uploads, creating uploads, copying and uploading parts, fetching multipart metadata, listing parts, aborting uploads, and completing uploads.
- `HealOperations` exposes format, bucket, object, pool/set lookup, and abandoned part checks for repair workflows.
- `NamespaceLocking` exposes `new_ns_lock` for code that needs object mutation coordination without depending on the whole API.
- `StorageAPI` is a marker-like composed trait requiring `ObjectIO + BucketOperations + ObjectOperations + ListOperations + MultipartOperations + HealOperations + Debug`.

## Control Flow

This file has no implementation control flow beyond async trait method declarations. Its control-flow importance is architectural: callers can depend on a narrow trait such as `BucketOperations` or `NamespaceLocking`, while full storage implementations can satisfy `StorageAPI`. Several methods take `self: Arc<Self>` instead of `&self` where implementations may need to spawn or retain shared ownership during asynchronous listing, restoration, or multipart completion.

## State and Persistence Behavior

The traits do not store state. They define operations that mutate or inspect persistent state managed by implementors: bucket namespace, object metadata and content, multipart upload state, tags, replication/delete markers, transitioned objects, format healing, and locks. Types such as `ObjectOptions`, `ObjectInfo`, `FileInfo`, `ObjectToDelete`, `DeletedObject`, `MultipartUploadResult`, `PartInfo`, and `HealResultItem` carry the state contract across the boundary.

## Dependencies and Integration Points

The file imports from `super::*`, so it relies on the store API module prelude for all domain types and async support. It depends on `async_trait` for async methods in traits and on `Arc` for methods that need owned shared receivers. The primary integration points are S3 front-end handlers, erasure-backed storage implementations, metadata/lifecycle/replication subsystems, healing code, and namespace lock management.

## Risks and Edge Cases

- The unified API is broad; implementors must keep many operations behaviorally consistent around versioning, replication, lifecycle, and locking.
- Many methods accept `ObjectOptions`, which is a large option bag. Missing or misinterpreted flags can cause subtle behavior differences between implementations.
- `delete_objects` returns per-object errors as `Vec<Option<Error>>`, so callers must preserve positional alignment with input objects.
- `copy_object_part` and `copy_object` have many arguments and depend on matching source/destination options correctly.
- `StorageAPI` does not include `NamespaceLocking`, so consumers that require lock creation must request that trait separately.

## Test Signals

There are no tests in this file because it is purely trait definitions. Behavioral coverage must come from concrete implementors and integration tests that exercise bucket/object/list/multipart/heal paths through these contracts.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store_api/traits.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store_api/types.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store_api/types.rs

## Purpose

`types.rs` defines the store API data model used by ecstore operations. It contains option structs for object requests, object metadata views, multipart/listing/delete result models, walking options, and helper logic for HTTP preconditions, actual-size calculation, compression/encryption metadata interpretation, version-marker pagination, replication state projection, and conversion from low-level `FileInfo` metadata into public `ObjectInfo`.

## Important APIs, Types, and Functions

- `HTTPPreconditions` stores `If-Match`, `If-None-Match`, `If-Modified-Since`, and `If-Unmodified-Since` values. Its private helpers ignore empty ETag condition strings.
- `ObjectLockRetentionOptions` models object-lock retention mode, retain-until time, and governance bypass.
- `ObjectOptions` is the central request option bag. It includes part selection, versioning flags, deletion flags, decommission/rebalance skips, replication/lifecycle/transition state, user metadata, preconditions, checksum options, and capacity-scope token.
- `ObjectOptions` methods update delete replication state, replica status, compute purge/delete-marker statuses, derive put replication state from metadata, and enforce preconditions with `precondition_check`.
- `MultipartUploadResult`, `PartInfo`, and `CompletePart` model multipart lifecycle data. `CompletePart` converts from `s3s::dto::CompletedPart`, preserving checksum fields.
- `ObjectInfo` is the main object metadata view. It includes bucket/name, storage class, mod time, logical and actual sizes, user metadata, erasure layout, version/delete-marker fields, transition and restore state, tags, parts, content fields, replication state, checksum bytes, and an optional `PutObjReader`.
- `ObjectInfo` methods detect compression/encryption, resolve compression read plans, compute encrypted/decrypted/actual sizes, convert from `FileInfo`, build listings from sorted metacache entries, project replication state, and expose checksum maps.
- `VersionMarker` and `versions_after_marker` implement null-version and UUID-version pagination for version listings.
- Listing/result models include `ListObjectsInfo`, `ListObjectsV2Info`, `MultipartInfo`, `ListMultipartsInfo`, `ListPartsInfo`, `ObjectToDelete`, `DeletedObject`, `ListObjectVersionsInfo`, `WalkOptions`, `WalkVersionsSortOrder`, and `ObjectInfoOrErr`.

## Control Flow

`ObjectOptions::precondition_check` first validates requested part number when multipart metadata is available. It then applies HTTP preconditions in S3/HTTP style: matching `If-None-Match` returns `NotModified`, `If-Modified-Since` returns `NotModified` when the object has not changed since the supplied timestamp, `If-Match` must match the object ETag or returns `PreconditionFailed`, and `If-Unmodified-Since` is checked only when `If-Match` is absent. ETag comparison strips quotes and treats `"*"` as a wildcard on the condition side.

`ObjectInfo::get_actual_size` prefers the explicit `actual_size` field. For compressed objects it then uses actual-size metadata, otherwise sums part `actual_size` values and errors if no actual size can be inferred while stored size is nonzero. For encrypted objects it checks RustFS and SSE-C original-size metadata, plus generic actual-size metadata, before falling back to stored `size`.

`ObjectInfo::from_file_info` converts low-level file metadata into API metadata. It decodes directory object names, assigns null UUIDs for unversioned entries in versioned buckets, extracts content headers and ETag, moves object tags into an `Arc<String>`, parses expiration metadata, projects replication state and status, constructs `TransitionedObject`, cleans internal metadata, chooses storage class, parses restore state, converts part metadata into `ObjectPartInfo`, and builds the final `ObjectInfo`.

`from_meta_cache_entries_sorted_versions` and `from_meta_cache_entries_sorted_infos` iterate sorted metacache entries, synthesize directory prefix entries when a delimiter is present, skip duplicate prefixes, convert object entries into `ObjectInfo`, and consult bucket versioning configuration. The versioned variant applies `after_version_marker` only to the first object entry by taking the marker option once, and skips entries with non-empty version purge status.

## State and Persistence Behavior

This file does not perform direct disk I/O, but it is the main projection layer for persistent object metadata. It reads metadata stored in `FileInfo`, including erasure information, part tables, replication internals, transition status, restore headers, tags, checksums, compression headers, encryption headers, and storage-class headers. It uses `Arc` for large cloned metadata fields (`user_defined`, `user_tags`, `parts`) and deliberately drops `put_object_reader` during `Clone` because streams cannot be cloned. Several result structs mirror S3 pagination state and must preserve marker/truncation fields accurately across calls.

## Dependencies and Integration Points

The module depends on the parent `store_api` prelude for domain types and constants. It integrates with `rustfs_filemeta` (`FileInfo`, `FileInfoVersions`, `MetaCacheEntriesSorted`, `ObjectPartInfo`, `ReplicationState`), bucket versioning config (`get_versioning_config`), lifecycle/transition types, replication status helpers, checksum parsing via `rustfs_rio::read_checksums`, storage class config constants, metadata cleanup and directory decoding helpers, and HTTP metadata helpers from `rustfs_utils`. The S3 API layer consumes these structs to build responses, while storage implementations consume `ObjectOptions` to decide behavior.

## Risks and Edge Cases

- `ObjectOptions` is large and loosely grouped; incompatible flags can be set together unless individual operations validate them.
- `ObjectInfo::is_encrypted` is metadata-prefix based. It avoids false positives for original-size-only old metadata, but broad prefix matches can still classify incomplete metadata as encrypted.
- Actual-size logic for compressed objects depends on metadata or part actual sizes. Missing part actual sizes on nonempty compressed objects return an error.
- Version listing marker behavior intentionally applies the version marker only to the first object entry; changing this would break pagination.
- `from_meta_cache_entries_sorted_*` suppresses parse errors by logging and continuing, which favors availability but can hide corrupt entries from callers.
- `Clone` shares `Arc` fields and drops `put_object_reader`; code expecting cloned upload streams would fail silently by seeing `None`.
- `decrypt_checksums` still has a TODO for encrypted checksum handling and currently returns part checksums or raw object checksum metadata.

## Test Signals

Tests cover null and UUID version markers, one-time version-marker application across multiple entries, actual-size precedence and compressed metadata/part fallbacks, errors for compressed size mismatch, empty ETag precondition handling, preservation of replication decisions from `FileInfo`, encryption detection for old metadata and current RustFS/SSE metadata including case-insensitive keys, and `ObjectInfo::clone` behavior with shared `Arc` fields and omitted reader state.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store_api/types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store_init.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store_init.rs

## Purpose

`store_init.rs` handles erasure-store disk connection and format initialization. It opens configured endpoints, loads `format.json` from all disks, validates format quorum and erasure layout, initializes completely unformatted deployments on the first disk path, migrates compatible MinIO format metadata when present, saves new format files atomically, and exposes helper logic for default parity calculation.

## Important APIs, Types, and Functions

- `init_disks` asynchronously calls `new_disk` for every endpoint and returns parallel vectors of `Option<DiskStore>` and `Option<DiskError>`.
- `connect_load_init_formats` is the main bootstrap coordinator. It loads all formats, checks fatal disk errors and format validity, initializes or migrates when all disks are unformatted and this is the first disk, waits/errors appropriately for first-disk coordination, and otherwise returns a quorum format.
- `quorum_unformatted_disks`, `should_init_erasure_disks`, and `check_disk_fatal_errs` classify disk error sets.
- `init_format_erasure` builds a new `FormatV3`, assigns `erasure.this` per set/drive slot, applies an optional deployment UUID, writes all format files, and returns the quorum format.
- `try_migrate_format` searches existing disks for MinIO migrating metadata, validates expected set count, drive count, and erasure version, rewrites per-disk `erasure.this`, saves RustFS format files, and returns the quorum format.
- `get_format_erasure_in_quorum` selects the format layout with majority drive-count agreement, clones a representative, and clears `erasure.this` to nil before returning it as the cluster-level format.
- `check_format_erasure_values` and `check_format_erasure_value` validate meta version, erasure version, total format count, and set drive count.
- `load_format_erasure_all` and `load_format_erasure` read format files across disks, map missing format files to `UnformattedDisk`, optionally attach disk info for healing, and set disk IDs when not healing.
- `save_format_file_all` and `save_format_file` write format JSON through a temporary UUID-named file, rename it to the canonical format file, set the disk ID, and reduce write errors by quorum.
- `ec_drives_no_config` computes default parity for a set drive count via storage-class config defaults.

## Control Flow

Bootstrap starts with `init_disks`, which fans out endpoint connection attempts and preserves endpoint order in disk/error vectors. `connect_load_init_formats` then loads formats from available disks. If every disk has a fatal homogeneous error such as unsupported disk, access denied, or non-directory path, startup fails immediately. Existing format values are validated before any init decision.

When `first_disk` is true and every disk is unformatted, the code first tries `try_migrate_format`. Migration reads `FORMAT_CONFIG_FILE` from `MIGRATING_META_BUCKET` on each available disk until it finds parseable data. It rejects layout mismatches and non-V3 erasure formats, then constructs per-disk cloned formats with slot-specific `erasure.this`, saves them to RustFS metadata, and returns quorum. If migration fails, `init_format_erasure` creates a new format and writes one slot-specific copy per disk.

If a quorum of disks is unformatted but not all disks are ready for initialization, `connect_load_init_formats` returns coordination errors: `NotFirstDisk` for non-first disk callers and `FirstDiskWait` for first-disk callers waiting on partial formatting. Otherwise it selects the format in quorum and returns it.

Format save uses a two-step write: write JSON to a UUID temporary object under the RustFS metadata bucket, then rename to `FORMAT_CONFIG_FILE`. `save_format_file_all` performs all saves concurrently and applies `reduce_write_quorum_errs` over the result vector.

## State and Persistence Behavior

This file directly persists cluster format state. It reads `FORMAT_CONFIG_FILE` from `RUSTFS_META_BUCKET` and migration candidates from `MIGRATING_META_BUCKET`. It writes new format JSON to a temporary object then atomically renames it to the canonical format path on each disk, and updates each `DiskStore`'s in-memory disk ID with the slot UUID. Returned cluster-level formats intentionally set `erasure.this` to nil so callers do not treat one disk's slot ID as global state. In heal mode, `load_format_erasure` attaches live disk info to the loaded `FormatV3`.

## Dependencies and Integration Points

The module depends on disk APIs (`DiskStore`, `DiskAPI`, `new_disk`, `DiskOption`, `DiskInfoOptions`, `DiskError`, metadata bucket constants), format types (`FormatV3`, `FormatMetaVersion`, `FormatErasureVersion`), quorum helpers (`count_errs`, `reduce_write_quorum_errs`), endpoint configuration, storage-class config (`lookup_config`, `STANDARD`), `futures::join_all`, `uuid::Uuid`, and tracing. It is part of startup and healing paths for erasure-coded object storage, and its output `FormatV3` determines set/drive topology for higher-level erasure sets.

## Risks and Edge Cases

- `check_format_erasure_values` validates each present format against the total number of disk slots; mixed or stale formats can block startup before quorum selection.
- `get_format_erasure_in_quorum` groups only by `drives()` count, not by full deployment ID or complete set topology. That may be sufficient for current `FormatV3::drives` semantics, but it is a sensitive quorum criterion.
- Migration uses the first compatible MinIO format found. If multiple disks carry divergent but layout-compatible migrating formats, the first one in disk order wins.
- `save_format_file_all` indexes `formats[i]` for every disk, so caller-provided format vectors must exactly match disk length.
- The temporary-write then rename sequence depends on disk backend rename semantics for atomicity.
- Missing disk stores are represented as `DiskNotFound`, which participates in quorum reduction rather than being filtered out.
- The bootstrap state machine distinguishes all-unformatted from quorum-unformatted; partial unformatted deployments return coordination errors rather than initializing.

## Test Signals

No tests are defined in this file. Existing confidence likely comes from disk/format integration tests elsewhere. Useful focused tests would cover all-unformatted first-disk initialization, partial unformatted coordination errors, fatal homogeneous disk errors, quorum selection with mixed formats, migration from MinIO metadata, write quorum reduction, and validation failures for mismatched set sizes or erasure versions.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store_init.rs -->

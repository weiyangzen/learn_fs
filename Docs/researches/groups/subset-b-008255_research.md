# Research: subset-b-008255

Grouped research report for `subset-b-008255`. Each section preserves the source path and is wrapped for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/set_disk/heal.rs -->
# sources/object-store/rustfs/crates/ecstore/src/set_disk/heal.rs

## Purpose
Implements object and object-directory healing for a single erasure set. It repairs missing or stale shards by reading quorum metadata, selecting the latest valid `FileInfo`, reconstructing data through erasure coding, writing healed shards under `.rustfs/tmp`, and atomically renaming them back to the bucket/object path. It also builds `HealResultItem` status before/after drive state.

## Important APIs, Types, And Functions
The main API is `SetDisks::heal_object(bucket, object, version_id, opts)`, returning a `HealResultItem` and optional `DiskError`. `heal_object_dir_locked` and `heal_object_dir` repair missing object directories, optionally removing dangling directories. `default_heal_result` renders drive state when normal healing cannot proceed. The implementation depends heavily on `FileInfo`, `ObjectInfo`, `HealOpts`, `HealDriveInfo`, `DriveState`, erasure coding readers/writers, `read_all_fileinfo`, `object_quorum_from_meta`, `list_online_disks`, `pick_valid_fileinfo`, `disks_with_all_parts`, and `delete_if_dangling`.

## Control Flow
`heal_object` optionally takes a namespace write lock, reads all versions/metadata, exits early for all-not-found, computes read/write quorum from metadata, filters online disks by common mod time or ETag, and picks the quorum `FileInfo`. It marks drives as ok/missing/corrupt/offline, exits on dry-run or no-op, checks whether data or metadata loss exceeds parity tolerance, and deletes dangling versions if repair is impossible. For repairable data, it shuffles disks by erasure distribution, cleans metadata for target drives, reconstructs each part from bitrot readers to bitrot writers, updates `FileInfo` checksums/inline data, and renames healed temp data to the final location.

## State And Persistence Behavior
State changes are persisted by `rename_data` on each outdated disk and by optional deletes of remote data directories or dangling versions. Temporary data is written beneath `RUSTFS_META_TMP_BUCKET` using a UUID and cleaned with `delete_all`. The function mutates the result’s drive states after successful rename and records capacity scope for healed disks.

## Dependencies And Integration Points
This file integrates namespace locks, disk APIs, erasure coding, storage-class inline decisions, environment-controlled zero-copy reads, heal-channel types, object metadata consensus helpers, and object deletion logic. It is called through `Sets::heal_object` and `ECStore::handle_heal_object`.

## Risks
There is complex index alignment between disks, metadata, part-error maps, and erasure distribution; mistakes can heal the wrong shard. `latest_meta.data_dir.unwrap()` assumes a data directory for non-deleted local objects. `default_heal_result` pushes offline entries and then pushes another state for every disk, which may duplicate drive entries for offline disks. Temp cleanup occurs after each rename attempt, so partial failures require careful validation.

## Test Signals
No local tests in this file. Coverage is indirect through read/write/quorum helper tests and higher-level heal paths. Strong regression tests would cover stale metadata-only repair, data shard reconstruction, dry-run, dangling deletes, distribution mismatch refusal, and offline disk result rendering.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/set_disk/heal.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/set_disk/list.rs -->
# sources/object-store/rustfs/crates/ecstore/src/set_disk/list.rs

## Purpose
Provides a small set-wide recursive delete helper. Despite the filename, this file currently contains `SetDisks::delete_all`, used by heal and bucket cleanup code to remove a prefix from every disk in a set.

## Important APIs, Types, And Functions
`delete_all(&self, bucket, prefix) -> Result<()>` clones the current disk vector, calls `DiskAPI::delete` with `DeleteOptions { recursive: true }` on each online disk, records errors, and returns `Ok(())` regardless of collected disk failures.

## Control Flow
The method reads `self.disks`, clones the vector to release the lock, builds one async delete future per disk, and awaits all with `join_all`. Missing disks are represented as `DiskError::DiskNotFound`; successful deletes push `None` into the local `errors` vector and failures push `Some(error)`.

## State And Persistence Behavior
The only persisted effect is best-effort recursive deletion of the requested bucket/prefix on every available disk. The accumulated `errors` vector is not reduced against write quorum and is not logged, so callers cannot tell whether all, some, or no disks deleted the prefix.

## Dependencies And Integration Points
Depends on `DiskStore`, `DiskAPI::delete`, and `DeleteOptions` from the set-disk module prelude. It is used by healing to remove temporary UUID directories and by store bucket deletion to clean metadata prefixes.

## Risks
Returning success unconditionally can hide cleanup failures and leave temporary or metadata objects on a subset of disks. For healing, stale temp directories may waste capacity; for bucket metadata cleanup, partial deletion can leave inconsistent internal state. If callers require quorum semantics, they need a stricter helper.

## Test Signals
No tests in this file. Useful tests would inject per-disk delete failures and assert intended best-effort behavior or enforce a future quorum/error-reporting contract.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/set_disk/list.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/set_disk/lock.rs -->
# sources/object-store/rustfs/crates/ecstore/src/set_disk/lock.rs

## Purpose
Collects namespace-lock error mapping plus disk membership, online-disk selection, reconnection, and endpoint renewal for a `SetDisks` shard. It is the bridge between logical object operations and the mutable runtime health of drives.

## Important APIs, Types, And Functions
Lock helpers are `format_lock_error`, `format_lock_error_from_error`, and `map_namespace_lock_error`, with quorum failures mapped to `StorageError::NamespaceLockQuorumUnavailable`. Disk selection helpers include `get_disks_internal`, `get_local_disks`, `get_online_disks`, `get_online_local_disks`, `drive_membership_snapshot`, and `get_online_disks_with_healing_and_info`. Reconnection uses `connect_disks`, `renew_disk`, `connect_endpoint`, and `find_disk_index`.

## Control Flow
Online selection builds a `DriveMembershipSnapshot`, filters strict online or scanner/heal candidates, randomizes order, probes `disk_info` through the metadata processor, orders non-scanning disks before scanning and healing disks, and performs one runtime reprobe if all candidates initially fail. `connect_disks` closes bad or unlocated disks and calls `renew_disk` for their endpoints. `renew_disk` reconnects, loads format metadata, finds the disk’s expected set/disk index by UUID, enables health checks, updates global local-disk maps for distributed erasure, and swaps the disk into `self.disks`.

## State And Persistence Behavior
This file mutates in-memory disk membership, health-check state, and global local-disk maps. It reads persisted `format.json` through `load_format_erasure` to validate disk identity before reattaching a drive.

## Dependencies And Integration Points
It depends on `rustfs_lock`, `DriveMembershipSnapshot`, endpoint construction, global local disk state, distributed-erasure mode, format loading, `send_heal_disk`, and processor pools. All set-disk operations use these helpers to choose candidates and renew failed drives.

## Risks
Holding write access while awaiting `disk_info` in `get_online_disk_with_healing_and_info` can serialize or block other disk state operations. Correctness depends on keeping `DiskInfo` aligned with shuffled disks; the newer processor path explicitly preserves submitted indexes. Global map mutation can race with other initialization or renewal paths if assumptions drift.

## Test Signals
Tests cover disk/info alignment after shuffling, membership filtering of suspect/returning/offline states, one-shot reprobe recovery, and health monitoring on renewed disks. These are strong regression signals for this file’s highest-risk behaviors.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/set_disk/lock.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/set_disk/metadata.rs -->
# sources/object-store/rustfs/crates/ecstore/src/set_disk/metadata.rs

## Purpose
Implements metadata consensus and erasure-layout helpers for set-disk operations. It decides whether an object has read/write quorum, which metadata version is authoritative, and how disks and metadata should be reordered to match erasure distribution.

## Important APIs, Types, And Functions
Key functions include `all_not_found_metadata`, `reduce_common_data_dir`, multipart path helpers `get_upload_id_dir` and `get_multipart_sha_dir`, `common_parity`, `object_quorum_from_meta`, `list_online_disks`, `pick_valid_fileinfo`, `find_file_info_in_quorum`, `shuffle_disks_and_parts_metadata_by_index`, `shuffle_disks_and_parts_metadata`, `shuffle_parts_metadata`, `shuffle_disks`, and `shuffle_check_parts`.

## Control Flow
Quorum computation first handles all-not-found metadata, reduces read errors, derives per-disk parity from valid metadata, selects the common parity that itself has quorum, then returns data and write quorum. Online disk selection finds a common mod time, or falls back to common ETag when mod-time quorum is unavailable. `find_file_info_in_quorum` filters valid metadata by the common selector, hashes part numbers/sizes and erasure layout, requires a hash quorum, and returns a representative `FileInfo` with quorum-agreed version properties.

## State And Persistence Behavior
This file does not write persistent state. It interprets persisted xl metadata (`FileInfo`) and maps it onto in-memory disk positions. Multipart upload IDs are decoded from URL-safe base64 where possible and mapped into the deterministic SHA-256 multipart directory.

## Dependencies And Integration Points
It is used by read, write, multipart, and heal paths. It depends on `DiskError` reducers, `FileInfo`, `OffsetDateTime`, `Uuid`, SHA-256 hashing, and object property structs.

## Risks
Tie-breaking in `common_time_and_occurrence` chooses the latest timestamp when counts tie, which affects authoritative version selection. Metadata hashing omits some TODO fields such as remote, encrypted, and compressed details, so future metadata variants need careful expansion. Shuffle helpers assume one-based erasure indices and valid distribution lengths.

## Test Signals
No tests in this file, but many downstream tests rely on it. Focused tests should cover parity selection for delete markers, ETag fallback, conflicting metadata hashes, distribution mismatch fallback, and upload-id decoding compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/set_disk/metadata.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/set_disk/multipart.rs -->
# sources/object-store/rustfs/crates/ecstore/src/set_disk/multipart.rs

## Purpose
Provides set-level multipart upload discovery and validation helpers. It lists committed part numbers that are present on quorum drives and verifies that a multipart upload ID has valid metadata quorum.

## Important APIs, Types, And Functions
`collect_list_parts_results` runs per-disk listing tasks with early failure when read quorum becomes impossible. `empty_upload_fallback_possible` distinguishes empty/missing upload directories from ordinary quorum failures. `reduce_quorum_part_numbers` only returns part numbers that have both `part.N` and `part.N.meta` on at least read quorum drives. `SetDisks::list_parts` and `check_upload_id_exists` are the exposed helpers.

## Control Flow
`list_parts` calls `DiskAPI::list_dir` against `RUSTFS_META_MULTIPART_BUCKET`, collects per-disk results, reduces read errors, and then reduces the returned filenames into sorted quorum part numbers. `check_upload_id_exists` maps upload ID to its multipart metadata path, reads all file info, maps `FileNotFound` to `InvalidUploadID`, computes object quorum, optionally checks write quorum, selects online disks by metadata consensus, and returns the authoritative upload `FileInfo` with all disk metadata.

## State And Persistence Behavior
This file is read-only. It inspects multipart metadata in the internal multipart bucket and does not mutate upload state.

## Dependencies And Integration Points
It depends on metadata path helpers, disk list/read APIs, quorum reducers, `OBJECT_OP_IGNORED_ERRS`, `FileInfo`, and storage error mapping. It is consumed by higher-level multipart upload handlers for listing parts, completing uploads, and validating upload IDs.

## Risks
The collector treats panicked tasks as non-successes but only fails once quorum is impossible; this is intentional but can obscure a systemic panic if quorum still succeeds. `reduce_quorum_part_numbers` requires both payload and `.meta`, so partial stale metadata is excluded. Empty-upload fallback must stay aligned with S3 multipart semantics.

## Test Signals
Tests cover early quorum failure, tolerance of one panicked task when quorum is met, `FileNotFound` fallback for empty upload dirs, early failure when fallback is impossible, and quorum filtering of part numbers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/set_disk/multipart.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/set_disk/read.rs -->
# sources/object-store/rustfs/crates/ecstore/src/set_disk/read.rs

## Purpose
Implements set-level metadata and data reads for erasure-coded objects. It reads file metadata across disks, chooses quorum object state, reads multipart part metadata, batches small multi-file reads, and streams object ranges by decoding erasure shards.

## Important APIs, Types, And Functions
Collector helpers `collect_read_multiple_results` and `collect_read_parts_results` run early-quorum `JoinSet` tasks. `read_parts`, `read_all_fileinfo`, `read_version_optimized`, `read_all_xl`, `read_all_raw_file_info`, `pick_latest_quorum_files_info`, `read_multiple_files`, `get_object_fileinfo`, `get_object_info_and_quorum`, and `get_object_with_fileinfo` make up the read surface.

## Control Flow
Metadata reads fan out to all disks with `read_version` or raw xl reads, merge versions, and reduce errors to a quorum-selected `FileInfo`. `get_object_fileinfo` computes read quorum, reduces errors, selects online disks by common metadata, picks valid file info, and enqueues background heal if any disk had metadata errors. `get_object_with_fileinfo` validates byte-range bounds, maps offsets to parts, creates bitrot readers for the required erasure shard ranges, checks that available shards meet data quorum, optionally enqueues heal for missing shards, and calls `erasure.decode` into the caller’s async writer.

## State And Persistence Behavior
Read operations are mostly non-mutating, but they can enqueue heal requests when metadata or data shard gaps are detected. The object stream itself is reconstructed from persisted part files and optional inline metadata bytes. Zero-copy behavior is controlled by `ENV_OBJECT_ZERO_COPY_ENABLE`.

## Dependencies And Integration Points
This file integrates disk `read_version`, `read_xl`, `read_multiple`, and `read_parts`; `FileMeta` version merging; quorum helpers; erasure coding; bitrot readers; object error mapping; heal channel; and processor pools.

## Risks
Index alignment across shuffled disks, `files`, and erasure distribution is critical. `files[idx].data_dir.unwrap_or_default()` can silently form paths with an empty data dir for bad metadata. `read_version_optimized` uses `self.format.erasure.sets.len()` as `required_reads`, which is set count rather than per-set data quorum and should be reviewed before relying on it broadly.

## Test Signals
Tests cover early failure and panic tolerance for both multi-file and part-read collectors. More integration tests are needed for range reads across part boundaries, background heal enqueue, inline data, legacy checksum selection, and versioned delete-marker behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/set_disk/read.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/set_disk/replication.rs -->
# sources/object-store/rustfs/crates/ecstore/src/set_disk/replication.rs

## Purpose
Provides a metadata-only restore helper for transitioned/restored objects. It removes the `x-amz-restore` marker from user metadata by issuing an in-place copy.

## Important APIs, Types, And Functions
`SetDisks::update_restore_metadata(bucket, object, obj_info, opts)` clones `ObjectInfo`, sets `metadata_only = true`, removes `X_AMZ_RESTORE` from `user_defined`, preserves the version ID, and calls `copy_object` from the object to itself with source and destination `ObjectOptions`.

## Control Flow
The method constructs a mutable metadata-only object info value, mutates user metadata through `Arc::make_mut`, derives `version_id`, and delegates all persistence and quorum behavior to the normal copy-object path. The `_opts` parameter is currently unused.

## State And Persistence Behavior
Persistent state changes are indirect: the in-place copy updates object metadata on the erasure set without rewriting object data when the copy path honors `metadata_only`.

## Dependencies And Integration Points
It depends on the object copy implementation, `ObjectInfo`, `ObjectOptions`, and the S3 restore metadata key constant. It is likely used by lifecycle/tier restore flows after a restored object’s expiry metadata changes.

## Risks
Correctness is delegated to `copy_object`; if metadata-only handling changes there, restore metadata updates may rewrite data or mishandle versions. The ignored `_opts` may hide caller intent such as locking or preconditions.

## Test Signals
No tests in this file. Useful coverage would assert that restore metadata is removed for a specific version and that other user metadata and object data are preserved.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/set_disk/replication.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/set_disk/write.rs -->
# sources/object-store/rustfs/crates/ecstore/src/set_disk/write.rs

## Purpose
Implements set-level write-side quorum helpers for object data, multipart parts, metadata updates, dangling deletes, prefix deletion, and HTTP precondition checks.

## Important APIs, Types, And Functions
Key methods are `default_read_quorum`, `default_write_quorum`, `rename_data`, `commit_rename_data_dir`, `cleanup_multipart_path`, `rename_part`, `eval_disks`, `write_unique_file_info`, `update_object_meta`, `update_object_meta_with_opts`, `delete_if_dangling`, `delete_prefix`, and `check_write_precondition`.

## Control Flow
`rename_data` fans out per-disk `rename_data`, records old data dirs/signatures, rolls back successful writes with `delete_version(... undo_write ...)` if write quorum fails, then returns online disks, common old data dir, and cleanup candidates. `rename_part` clears stale destination part paths, renames temp part payload and metadata, cleans up on quorum failure, and returns successful disks. Metadata writes fan out and revert successful metadata on quorum failure. `check_write_precondition` reads current object info without taking a lock and applies If-Match/If-None-Match logic.

## State And Persistence Behavior
This file writes and deletes persisted object metadata/data across disks. Rollback is best effort and quorum-driven. `delete_if_dangling` writes delete-version markers for dangling/corrupt object states and annotates diagnostic tags in memory. `delete_prefix` recursively removes a prefix with majority write quorum.

## Dependencies And Integration Points
It depends on disk write APIs, quorum reducers, multipart bucket constants, object options, metadata update options, path helpers, global processors, and object-info read paths. It is called by object and multipart handlers and by healing.

## Risks
Partial rollback failures can leave mixed old/new data dirs. `cleanup_multipart_path` logs but does not surface delete failures before overwrite. `delete_if_dangling` builds diagnostic tags that are not audited yet. Preconditions rely on callers already holding any required write lock, as stated in the comment.

## Test Signals
No local tests in this file. Tests should cover rename rollback on quorum failure, multipart overwrite cleanup, metadata replacement with `replace_user_metadata`, dangling delete decisions, and precondition behavior for delete markers and missing objects.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/set_disk/write.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/sets.rs -->
# sources/object-store/rustfs/crates/ecstore/src/sets.rs

## Purpose
Defines `Sets`, the pool-level router over multiple `SetDisks` erasure sets. It builds per-set disk groups, hashes object names to sets, forwards storage traits to the chosen set, monitors endpoints, handles multi-set bulk deletes, and heals disk format metadata for a pool.

## Important APIs, Types, And Functions
`Sets::new` constructs the shard layout from disks, endpoints, format metadata, parity, and global lock clients. Routing helpers are `get_hashed_set_index`, `get_disks`, and `get_disks_by_key`. Trait implementations cover `ObjectIO`, `ObjectOperations`, `MultipartOperations`, `HealOperations`, `StorageAPI`, and `NamespaceLocking`. Support functions include `apply_delete_objects_results`, `init_storage_disks_with_errors`, `formats_to_drives_info`, and `new_heal_format_sets`.

## Control Flow
Construction iterates format sets/drives, attaches local distributed disks from global maps when needed, validates disk IDs, builds lock-client sets per host, and spawns `monitor_and_connect_endpoints`. Object operations mostly hash the object key and delegate to one `SetDisks`. `delete_objects` groups input by hashed set, runs bounded concurrent per-set deletes, and writes results back to original order. `heal_format` reconnects endpoints, loads format metadata, finds a quorum reference format, writes missing format files to unformatted disks, closes stale disk handles, and renews disks.

## State And Persistence Behavior
`Sets` owns in-memory `Arc<SetDisks>` shards and a broadcast exit signal. It persists `format.json` during format healing and mutates live disk membership through `renew_disk`. It does not persist object data directly; delegated set operations do.

## Dependencies And Integration Points
This file integrates endpoints, disk initialization, format quorum, global local-disk maps, lock clients, hash utilities, heal commands, and all storage trait surfaces. `ECStore` holds `Vec<Arc<Sets>>` pools and delegates through these routers.

## Risks
Many bucket/list operations remain `unimplemented!()` at this layer, so callers must use `ECStore` or implemented paths. Namespace locking always delegates to `disk_set[0]`, which centralizes lock construction but may be surprising for multi-set pools. Construction assumes format set dimensions match endpoint ordering.

## Test Signals
Tests cover preserving delete result order across out-of-order set batches. Indirect tests in other files cover disk renewal. More tests should cover hash routing stability, distributed local disk substitution, format healing, and namespace lock quorum across lock clients.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/sets.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store.rs

## Purpose
Defines `ECStore`, the top-level erasure-coded object store implementing storage, bucket, object, list, multipart, heal, namespace locking, and admin traits. This file wires public trait methods to handler modules and exposes accessors for global configuration and service singletons during migration.

## Important APIs, Types, And Functions
Important types are `ECStore`, `PoolErr`, `PoolObjInfo`, `PoolAvailableSpace`, and `ServerPoolsAvailableSpace`. Helper functions include `has_xlmeta_files`, `enqueue_transition_after_write`, and `should_enqueue_transition_immediately`. Trait impls delegate to `handle_*` methods in `store/{bucket,heal,init,list,multipart,object,peer,rebalance}.rs`.

## Control Flow
S3-style operations enter through trait methods and are routed to handler methods. Successful writes, copies, and multipart completes pass through `enqueue_transition_after_write`, which schedules lifecycle transition and expiry for non-internal buckets. Admin APIs call handler methods for backend and storage info. Accessor impls return process-global config, endpoints, region, tier manager, notification system, bucket metadata system, host, port, and address.

## State And Persistence Behavior
`ECStore` owns pool routers, peer system, pool and rebalance metadata locks, decommission cancellation tokens, migrated local disk maps, tier config manager, event notifier, and a bucket monitor. This file itself mostly coordinates state; persistence occurs in handler modules and delegated pools/sets.

## Dependencies And Integration Points
It is the integration hub for bucket metadata, lifecycle queues, notification, disk endpoints, remote peers, store initialization, tiering, object metadata, S3 DTOs, locking, and storage admin traits.

## Risks
The file mixes current source-of-truth globals with new per-store fields, so migration boundaries must remain clear. `enableObjcetLockConfig` is misspelled but consistently referenced. `has_xlmeta_files` recursively scans local files and can be expensive for large buckets. Trait delegation makes behavior depend on many submodules.

## Test Signals
Tests cover storage-info helpers, local disk lookup/cache backfill, transition suppression for internal metadata buckets, and pool available-space filtering. Handler-specific behavior is tested in submodules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store/bucket.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store/bucket.rs

## Purpose
Implements top-level bucket operations for `ECStore`: create, stat, list, and delete buckets, including metadata persistence, object-lock/versioning initialization, table-bucket delete guards, and cleanup of internal bucket metadata.

## Important APIs, Types, And Functions
Helpers include `should_override_created_from_metadata`, `validate_table_bucket_delete_allowed`, `table_catalog_metadata_exists`, `validate_table_bucket_delete_guard`, and `bucket_delete_metadata_cleanup_prefixes`. Handler methods are `handle_make_bucket`, `handle_get_bucket_info`, `handle_list_bucket`, and `handle_delete_bucket`.

## Control Flow
`handle_make_bucket` validates names, optionally takes a namespace write lock, asks peers to create the bucket, tries best-effort bucket heal on `BucketExists`, rolls back peer-created state on non-exists errors, creates `BucketMetadata`, initializes object-lock/versioning XML if requested, saves metadata, and updates the metadata system. Delete validates names, takes a lock, verifies bucket existence, enforces table-bucket catalog guard, recursively scans local disks for `xl.meta` unless forced, calls peer delete, deletes internal metadata prefixes, and updates the bucket monitor.

## State And Persistence Behavior
Persists bucket metadata via `BucketMetadata::save` and `set_bucket_metadata`. Delete removes bucket data through peers and cleans `RUSTFS_META_BUCKET` prefixes for table catalog and bucket metadata. Empty-directory remnants do not count as objects; only `xl.meta` files do.

## Dependencies And Integration Points
Depends on peer system bucket operations, namespace locks, bucket metadata system, object-lock/versioning serializers, local disk enumeration, `has_xlmeta_files`, table-bucket metadata conventions, and the global bucket monitor.

## Risks
Local recursive emptiness scans can be expensive and only see local disks. `delete_all` cleanup is best effort and may hide per-disk metadata deletion failures. Bucket creation rollback after peer failure is also best effort. Table-bucket guards depend on metadata state being available and accurate.

## Test Signals
Tests cover created-time override rules, table-bucket delete guard behavior, and metadata cleanup prefixes including table catalog metadata. Additional integration tests should cover lock errors, peer rollback, force delete, and object-lock/versioning metadata serialization.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store/bucket.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store/heal.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store/heal.rs

## Purpose
Implements `ECStore` heal handlers across pools. It aggregates format healing, delegates bucket healing to peers, runs object healing across active pools, and checks abandoned multipart parts.

## Important APIs, Types, And Functions
Constants define structured logging fields/events for heal operations. Handler methods are `handle_heal_format`, `handle_heal_bucket`, `handle_heal_object`, and `handle_check_abandoned_parts`.

## Control Flow
`handle_heal_format` initializes an aggregate `HealResultItem`, calls each pool’s `heal_format`, counts `NoHealRequired`, appends before/after drive states, logs completion, and returns `NoHealRequired` only if all pools did. `handle_heal_object` logs the start event, encodes directory-object names, skips suspended pools, runs pool heal calls concurrently, decodes result object names, returns the first success, then the first non-not-found error, and finally synthesizes file/version not found. `handle_check_abandoned_parts` delegates to the only pool or checks every pool and returns the first error.

## State And Persistence Behavior
This file mostly coordinates. Actual format writes occur in `Sets::heal_format`; actual object repair occurs in `SetDisks::heal_object`; peer bucket heal may create missing bucket structure.

## Dependencies And Integration Points
Depends on pool routers, peer system, heal options/results, object path encode/decode helpers, suspension checks, error classifiers, and tracing logs. It is the implementation behind `ECStore`’s `HealOperations` trait.

## Risks
The loop selecting the first non-not-found error uses an immediate `return match` inside a `for`; because `continue` is inside the match arm, it still scans not-found errors, but the structure is easy to misread and should be handled carefully in edits. Result vectors are sized by futures actually pushed, not all pools, while `errs` capacity uses all pools. Suspended pools are silently skipped.

## Test Signals
No direct tests in this file. Useful tests would cover multi-pool success/error precedence, all-pools not found, suspended pool skipping, object name encode/decode, and aggregate `NoHealRequired` behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store/heal.rs -->

# subset-b-008240 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/tier_last_day_stats.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/tier_last_day_stats.rs

Purpose: Maintains rolling 24-hour tier usage counters for lifecycle transition accounting. `DailyAllTierStats` maps tier names to `LastDayTierStats`, and each `LastDayTierStats` stores 24 hourly `TierStats` bins plus the last update timestamp.

Important APIs and types: `LastDayTierStats::add_stats` advances the ring to the current UTC hour and adds a `rustfs_data_usage::TierStats` value into the current bin. `total` folds all bins using `TierStats::add`. `forward_to` is the key time-window maintenance method: it clears bins crossed since `updated_at`, or clears all bins if 24 or more hours have elapsed. The private `merge` helper aligns two snapshots to the newer timestamp before adding bins.

Control flow and state: The file is in-memory only. State mutation happens by hour, keyed from `OffsetDateTime::now_utc().hour()`. A timestamp with Unix value `0` is treated as unset and replaced with current time. The rolling window depends on wall-clock UTC and not a monotonic clock.

Dependencies and integration: Depends on `rustfs_data_usage::TierStats` arithmetic and `time::OffsetDateTime`. It is expected to be consumed by lifecycle/tier accounting code that aggregates transitioned object statistics by storage tier.

Risks: Clock jumps can clear or preserve bins unexpectedly because elapsed time is computed from wall-clock timestamps. `merge` is dead code and untested in current use. The hourly array is indexed by UTC hour, so sparse updates across day boundaries are handled, but only at hour precision.

Test signals: One unit test verifies that `total` sums multiple added records. There is no test for `forward_to` window clearing, day rollover, or `merge` alignment.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/tier_last_day_stats.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/tier_sweeper.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/tier_sweeper.rs

Purpose: Converts lifecycle transition metadata into remote-tier delete journal work and performs bounded remote deletes. It protects the remote tier delete path with a concurrency semaphore, an inflight metric, and a signer/header-error circuit breaker.

Important APIs and types: `ObjSweeper` captures bucket/object versioning and transition state, derives lifecycle `ObjectOpts`, decides `should_remove_remote_object`, and enqueues a `Jentry` to `GLOBAL_ExpiryState`. `Jentry` implements `ExpiryOp` with a stable hash over tier and object names. `delete_object_from_remote_tier` obtains the tier driver from `GLOBAL_TierConfigMgr` and calls `remove`. `transitioned_delete_journal_entry` and `transitioned_force_delete_journal_entry` are small public helpers for regular and force-delete paths.

Control flow and state: A remote object is journaled only after `TRANSITION_COMPLETE`. Non-versioned buckets, suspended buckets, and concrete version IDs are eligible; null/current version handling is intentionally more conservative. The sweeper chooses an expiry worker channel by operation hash and records missed tasks if no channel exists or send fails. Remote delete first checks the breaker, acquires `REMOTE_DELETE_LIMITER`, increments `REMOTE_DELETE_INFLIGHT`, then resolves and invokes the tier driver.

Dependencies and integration: Integrates with lifecycle state (`GLOBAL_ExpiryState`, `TransitionedObject`), global tier config (`GLOBAL_TierConfigMgr`), signer error markers, metrics, `tokio::Semaphore`, `uuid`, `sha2`, and `xxhash_rust`.

Risks: The circuit breaker only opens for signer/header failures, so other repeated remote failures are counted but do not short-circuit. `GLOBAL_TierConfigMgr.write()` is held while acquiring/removing through the driver, which may serialize remote deletes more than expected. Several fields and methods are `dead_code` or allow-linted, suggesting incomplete integration.

Test signals: Unit tests cover signer/header error detection and breaker threshold/window recovery. No tests cover versioning matrix journal decisions, worker enqueue failures, or remote driver interactions.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/tier_sweeper.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/metadata.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/metadata.rs

Purpose: Defines the persisted bucket metadata record, its MessagePack wire format, compatibility decoders, config byte fields, parsed config caches, and disk load/save functions. This is the central persistence contract for bucket policy, lifecycle, notification, object lock, versioning, encryption, tagging, quota, replication, target, CORS, logging, website, accelerate, request-payment, public-access-block, ACL, and table-bucket state.

Important APIs and types: `BucketMetadata` stores raw config bytes, updated-at timestamps, and parsed `Option<T>` caches. `decode_from` and `encode_to` implement a MinIO-compatible map format behind a 4-byte little-endian format/version header. `marshal_msg`, `unmarshal`, and `check_header` wrap codec operations. `update_config` routes known config filenames to the correct byte field and timestamp. `save` parses configs, writes the header and MessagePack body, and persists to `.buckets/<bucket>/.metadata.bin`. `load_bucket_metadata`, `load_bucket_metadata_parse`, and `read_bucket_metadata` read from the object store and optionally parse.

Control flow and state: Unknown MessagePack fields are skipped via `msgp_decode::skip_msgp_value`, preserving forward compatibility. Legacy times can be ext8, compact arrays, nil, or bin-wrapped values; legacy byte arrays and numeric booleans are accepted. `default_timestamps` backfills missing updated-at values from creation time. `parse_all_configs` logs per-config parse warnings and continues, so raw bytes can be retained even when a parsed cache is invalid.

Dependencies and integration: Uses `read_config`/`save_config`, `resolve_object_store_handle`, S3 DTO config types, `rustfs_policy::BucketPolicy`, quota and target modules, `ObjectLockApi`, `VersioningApi`, and SHA-256 helpers for table-bucket catalog paths.

Risks: `encode_to` hardcodes a map length of 41; adding fields requires synchronized updates. `parse_all_configs` can leave stale parsed `Option` values if a later invalid non-empty config is parsed on an already-populated struct. Save requires a global object store handle, limiting isolated tests. Table-bucket presence is a byte-marker check.

Test signals: Tests cover round-trip serialization, complete metadata examples, table-bucket marker toggling, and clearing cached policy state. `metadata_test.rs` adds broader compatibility coverage for legacy formats.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/metadata.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/metadata_sys.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/metadata_sys.rs

Purpose: Provides the global bucket metadata cache and public async accessors for bucket-level configuration. It initializes metadata for existing buckets, reloads missing entries from disk, updates/deletes config blobs, and exposes typed getters used by policy, quota, lifecycle, object lock, replication, and API handlers.

Important APIs and types: `GLOBAL_BucketMetadataSys` is a `OnceLock<Arc<RwLock<BucketMetadataSys>>>`. Top-level functions include `init_bucket_metadata_sys`, `get`, `update`, `delete`, `created_at`, and many typed getters. `BucketMetadataSys` owns `metadata_map: RwLock<HashMap<String, Arc<BucketMetadata>>>`, an `Arc<ECStore>`, and an `initialized` flag.

Control flow and state: Initialization batches bucket loads by `GLOBAL_Endpoints.es_count() * 10`, heals buckets, loads metadata, caches it, and updates `BucketTargetSys`. `get_config` returns cached metadata or loads from disk, inserting the result; if initialized and load fails, it maps the condition to `errBucketMetadataNotInitialized`. Updates call `load_bucket_metadata_parse`, mutate raw bytes through `BucketMetadata::update_config`, save the full metadata record, then replace the cache entry. Deletes route through `update_and_parse` with empty bytes; lifecycle delete has a placeholder parse hook.

Dependencies and integration: Integrates with global endpoint topology, erasure-mode checks, object-store healing, metadata persistence, bucket target system, config deserialization, and S3 DTO types. Public getters are the narrow interface consumed by policy, object lock, lifecycle, notification, quota, replication, website, CORS, and encryption paths.

Risks: The global `OnceLock` cannot be reinitialized in-process, which complicates tests and multi-store scenarios. `update_and_parse` obtains the global object store rather than using `self.api`, so cache instances are not fully self-contained. Failed parse warnings can still allow saved raw bytes. Several TODOs mark missing distributed refresh and notifier/target reload behavior.

Test signals: No local unit tests in this file. Behavior is indirectly covered by metadata codec tests and downstream modules that use the typed getters.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/metadata_sys.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/metadata_test.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/metadata_test.rs

Purpose: Dedicated compatibility tests for the bucket metadata MessagePack codec. It focuses on ensuring RustFS can read MinIO-style metadata and legacy Rust/RMP-serde variants.

Important APIs and types: The file uses `BucketMetadata::marshal_msg` and `BucketMetadata::unmarshal`. `TEST_BUCKET_METADATA_HEX` is a large serialized fixture with many populated fields and timestamp values. Tests exercise time encoding, field aliases, bin/array encodings, numeric booleans, and full-field round trips.

Control flow and state: Tests decode fixed hex fixtures into bytes, unmarshal into `BucketMetadata`, and assert names, timestamps, raw config byte prefixes, lock flags, and updated-at fields. The complete round-trip test constructs a metadata instance with policy, lifecycle, versioning, encryption, tagging, quota, object-lock, notification, replication, bucket-target, public-access-block, and ACL bytes, serializes it, then validates the decoded fields.

Dependencies and integration: Uses `faster_hex`, `rmp::encode`, `time::OffsetDateTime`, and S3-compatible config bytes. It validates behavior implemented in `metadata.rs` and `msgp_decode.rs`.

Risks: The huge fixture is opaque and hard to audit manually, but it provides high-value regression coverage. Some tests are timestamp-precision tolerant by comparing Unix seconds, so nanosecond precision is not checked in every path. The file is compiled only under `#[cfg(test)]` via `bucket/mod.rs`.

Test signals: Strong coverage for codec compatibility: ext8 time, legacy compact time arrays, bin-wrapped ext time, legacy field aliases with byte arrays, bin16/array16 values, numeric bools, and full metadata serialization.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/metadata_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/migration.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/migration.rs

Purpose: Migrates legacy meta-bucket artifacts into the RustFS meta bucket. It handles bucket metadata, replication resync metadata, and IAM config normalization from older JSON/time field shapes into RustFS-compatible forms.

Important APIs and types: `try_migrate_bucket_metadata` lists buckets and copies `.metadata.bin` plus `.replication/resync.bin` from `MIGRATING_META_BUCKET` to `RUSTFS_META_BUCKET` when missing. `try_migrate_iam_config` paginates under `config/iam/`, normalizes supported IAM objects, and writes missing targets. Internal helpers include `normalize_iam_config_blob`, path classifiers for identity/group/policy/mapping files, `normalize_bucket_meta_blob`, and `migrate_one_if_missing`.

Control flow and state: Migration is idempotent: an existing target object causes a skip. Unsupported paths are skipped, incompatible data logs a warning and is not written, and empty reads are ignored. IAM normalization fills missing versions/update timestamps, converts legacy policy mapping field aliases, and preserves policy document create/update dates. Resync metadata is decoded and re-encoded through replication helpers.

Dependencies and integration: Relies on generic store traits (`BucketOperations`, `ListOperations`, `ObjectIO`, `ObjectOperations`), meta bucket constants, `PutObjReader`, IAM policy/user types, HTTP headers, and replication resync encode/decode.

Risks: Migration silently skips on listing/read failures, which is safe for startup but can hide incomplete migration unless logs are monitored. Existing target objects are never overwritten, so corrupted partial target state will not self-heal. Bucket migration uses disk bucket listing rather than listing legacy meta objects, which assumes all relevant buckets are visible through `list_bucket`.

Test signals: Unit tests cover legacy policy mapping timestamp/field normalization and resync metadata re-encoding. There are no tests with a fake store for pagination, idempotent copy, or read/write failure paths.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/migration.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/mod.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/mod.rs

Purpose: Declares the bucket module tree for `ecstore`. It is the public composition point for bucket subsystems such as metadata, policy, lifecycle, replication, quota, versioning, object lock, tagging, targets, and migration.

Important APIs and types: The file exports most child modules with `pub mod`, keeps `msgp_decode` private to the bucket module, and gates `metadata_test` behind `#[cfg(test)]`.

Control flow and state: There is no runtime logic. Its state impact is compile-time module visibility. Private `msgp_decode` limits low-level MessagePack helpers to internal bucket metadata code.

Dependencies and integration: Downstream code imports bucket APIs through these module declarations. `metadata.rs` uses sibling modules such as `quota`, `target`, `object_lock`, and `versioning`; `metadata_sys`, `policy_sys`, and `object_lock` rely on this layout.

Risks: Public module exports define the crate's internal API surface. Adding modules here may expose unstable implementation details. The test module split means codec compatibility tests in `metadata_test.rs` are compiled only for test builds.

Test signals: No direct tests. The file is validated indirectly by the Rust compiler and by tests under declared modules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/msgp_decode.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/msgp_decode.rs

Purpose: Supplies private MessagePack helpers for bucket metadata compatibility. It can skip unknown values and read/write the specific msgp ext8 timestamp format used by RustFS/MinIO metadata.

Important APIs and types: `skip_msgp_value` recursively consumes one MessagePack value, including arrays and maps. `MSGP_TIME_EXT_TYPE` and `MSGP_TIME_LEN` define ext type 5 with 12 bytes of payload. `read_msgp_ext8_time` reads seconds and nanoseconds from big-endian data. `write_msgp_time` writes ext8 timestamps from `OffsetDateTime`.

Control flow and state: The helpers are stateless stream operations over `Read`/`Write`. Skip behavior first reads a marker, determines scalar payload length or recursively descends into container elements, then reads and discards payload bytes.

Dependencies and integration: Used by `metadata.rs` for unknown-field forward compatibility and timestamp encoding. Depends on `rmp::Marker`, `byteorder::BigEndian`, `time::OffsetDateTime`, and the crate `Error`/`Result` type.

Risks: `skip_msgp_value` treats `Marker::Reserved` as zero length, which may let malformed input pass farther than expected. Ext16/Ext32 skip lengths include extra bytes in addition to the type byte in a way that should be checked against the rmp marker contract if those markers appear. The time reader only accepts ext8 type 5; other timestamp encodings are handled by `metadata.rs`.

Test signals: No local tests, but `metadata_test.rs` covers ext8 writing/reading indirectly and unknown legacy formats through the full metadata decoder.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/msgp_decode.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/object_lock/mod.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/object_lock/mod.rs

Purpose: Defines the object lock module boundary and small extension traits over S3 DTO types.

Important APIs and types: Exports `objectlock` and `objectlock_sys`. `ObjectLockApi::enabled` is implemented for `ObjectLockConfiguration` and returns true when `ObjectLockEnabled` equals `ENABLED`. `ObjectLockStatusExt::valid` is implemented for `ObjectLockLegalHoldStatus` and accepts only `ON` and `OFF`.

Control flow and state: Stateless trait adapters centralize DTO string comparisons so metadata and enforcement code do not repeat them. `BucketMetadata::versioning` uses `ObjectLockApi::enabled` to treat object lock as versioning-enabling state.

Dependencies and integration: Depends on S3 DTO object-lock types. Consumed by `metadata.rs` and object-lock enforcement paths.

Risks: String comparison depends on the DTO constants' exact casing and representation. The file validates legal hold status values but does not validate retention modes or dates; those live in `objectlock.rs` and `objectlock_sys.rs`.

Test signals: No direct tests. Behavior is indirectly covered by object-lock parser/system tests and metadata versioning behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/object_lock/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/object_lock/objectlock.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/object_lock/objectlock.rs

Purpose: Parses per-object object-lock metadata headers into S3 DTO retention and legal-hold values. It also exposes a time source helper and constants for object-lock error text.

Important APIs and types: `utc_now_ntp` returns current UTC time. `get_object_retention_meta` reads `x-amz-object-lock-mode` and `x-amz-object-lock-retain-until-date` from user metadata, parses mode and ISO8601 date, and returns `ObjectLockRetention`. `get_object_legalhold_meta` parses `x-amz-object-lock-legal-hold`. `parse_ret_mode` accepts GOVERNANCE and COMPLIANCE case-insensitively. `parse_legalhold_status` accepts ON and OFF case-insensitively.

Control flow and state: All functions are stateless and intentionally non-panicking for malformed metadata. Invalid modes or legal-hold values return DTOs with `None` status/mode. Date parse failures simply omit `retain_until_date`.

Dependencies and integration: Uses `s3s::dto` object-lock types, S3 header constants, `HashMap<String, String>` user metadata, and `time` ISO8601 parsing. `objectlock_sys.rs` builds deletion/modification decisions on these parsed DTOs.

Risks: Header lookup assumes metadata keys are lower-case exactly as `s3s::header` constants. Invalid or unparsable retention date becomes absent rather than an error, so callers must decide whether to reject invalid user input earlier. Error constants are currently unused.

Test signals: Unit tests cover valid/invalid mode parsing, valid/invalid legal hold parsing, empty metadata, retention with mode/date, and invalid value behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/object_lock/objectlock.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/object_lock/objectlock_sys.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/object_lock/objectlock_sys.rs

Purpose: Implements object-lock enforcement decisions for deletion and retention modification. It combines explicit object metadata with bucket default retention from metadata_sys.

Important APIs and types: `BucketObjectLockSys::get` returns a bucket's `DefaultRetention`. `is_retention_active` validates mode and future retain-until date. `check_retention_for_modification` enforces S3 semantics for COMPLIANCE and GOVERNANCE changes. `add_years` handles leap-day rollover. `is_object_locked_by_metadata` is a synchronous metadata-only check. `ObjectLockBlockReason` distinguishes `LegalHold` and `Retention` with user-facing messages. `check_object_lock_for_deletion` is the full async deletion gate.

Control flow and state: Delete markers bypass locks. Legal hold ON always blocks deletion. Explicit retention is evaluated before bucket default retention. COMPLIANCE cannot be shortened, cleared, or mode-changed; GOVERNANCE can be shortened or changed only with bypass. Default retention computes retain-until from `ObjectInfo.mod_time` plus configured days or years.

Dependencies and integration: Reads bucket default object-lock config through `metadata_sys::get_object_lock_config`, parses metadata through `objectlock.rs`, and consumes `store_api::ObjectInfo`.

Risks: Default retention is ignored when object modification time is absent. Bypass permission is assumed to be checked by the caller that passes `bypass_governance`. `check_retention_for_modification` compares `new_mode != Some(mode_str)`, so callers must pass canonical DTO strings to avoid false mode-change detection.

Test signals: Extensive unit tests cover year arithmetic, active/expired retention, compliance and governance modification semantics, legal holds, delete-marker behavior, and metadata-only lock checks. Async default-retention deletion behavior is not directly tested here.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/object_lock/objectlock_sys.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/policy_sys.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/policy_sys.rs

Purpose: Thin policy authorization facade over bucket metadata. It retrieves a bucket policy and evaluates request arguments, falling back to owner-only access when no policy exists.

Important APIs and types: `PolicySys::is_allowed` accepts `BucketPolicyArgs` and calls `BucketPolicy::is_allowed`. `PolicySys::get` reads `BucketMetadataSys` and returns the parsed `BucketPolicy`.

Control flow and state: `is_allowed` attempts to load the policy for `args.bucket`. If it succeeds, policy evaluation decides. If config is not found, or another error occurs after logging, the result falls back to `args.is_owner`. No state is mutated in this file.

Dependencies and integration: Depends on the global metadata system and `rustfs_policy` types. It is likely called by S3 API authorization paths needing bucket policy checks.

Risks: Non-ConfigNotFound errors are logged but still result in owner fallback; that is safe for non-owners but may mask availability/config problems for owners. It does not expose raw policy JSON; raw retrieval is in `metadata_sys`.

Test signals: No direct tests. Policy correctness depends on `rustfs_policy` tests and metadata system behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/policy_sys.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/quota/checker.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/quota/checker.rs

Purpose: Enforces bucket quota checks around object operations and persists quota config changes through bucket metadata.

Important APIs and types: `QuotaChecker` owns an `Arc<RwLock<BucketMetadataSys>>`. `check_quota` delegates to `check_quota_with_usage_reporting`. `get_quota_config` reads raw quota JSON from metadata, returning an unlimited default when absent. `set_quota_config` serializes `BucketQuota` and calls metadata `update`. `get_quota_stats`, `bucket_exists`, and `get_real_time_usage` support API reporting.

Control flow and state: If no quota is configured, operations are allowed and usage calculation is skipped unless forced. With a quota, current usage is read from `get_bucket_usage_memory`; PUT/POST/COPY add operation size and may be rejected, while DELETE is always allowed and subtracts with saturation for remaining reporting. Quota sync/check metrics are recorded through `rustfs_common::metrics`.

Dependencies and integration: Depends on `metadata_sys`, `data_usage::get_bucket_usage_memory`, `rustfs_config::QUOTA_CONFIG_FILE`, quota DTOs/errors from `quota/mod.rs`, and metrics.

Risks: Usage comes from memory and defaults to zero on missing/error in `get_real_time_usage`, which can under-enforce quota if the usage cache is cold or unavailable. Concurrent writers can race between usage check and object write. `current_usage + operation_size` is not saturating for expected PUT/COPY usage and could overflow in extreme values.

Test signals: Unit tests cover simple quota DTO allowance calculations and no-limit result shape. They do not instantiate a fake metadata system or test usage-cache failures/concurrency.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/quota/checker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/quota/mod.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/quota/mod.rs

Purpose: Defines the bucket quota configuration schema, quota operation/result types, and public error response contract.

Important APIs and types: `QuotaType` currently supports only `Hard`, with serde aliases for uppercase/lowercase compatibility. `BucketQuota` stores optional byte limit, quota type, created timestamp, and optional updated timestamp. Methods include `marshal_msg`, `unmarshal`, `new`, `get_quota_limit`, `check_operation_allowed`, and `get_remaining_quota`. `QuotaCheckResult`, `QuotaOperation`, `QuotaError`, and `QuotaErrorResponse` define enforcement outcomes and API errors.

Control flow and state: The module is mostly data modeling. `BucketQuota::new` stamps `created_at` with current UTC time. Quota checks allow all operations when `quota` is `None`; otherwise they use saturating addition/subtraction helpers where implemented.

Dependencies and integration: Re-exports `checker`. Uses `rustfs_config` error code constants and API path, `serde`, `thiserror`, and `time` RFC3339 serde. `metadata.rs` stores this schema as `quota.json`; `QuotaChecker` enforces it.

Risks: Only hard quota exists, so future soft quota behavior would require enum and checker updates. `check_operation_allowed` uses saturating addition, while checker expected usage uses normal addition. Error response intentionally uses PascalCase fields; changing serde names would break external contract.

Test signals: Unit tests cover legacy quota JSON without quota_type, RustFS format, uppercase `HARD`, marshal/unmarshal, and PascalCase error response serialization.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/quota/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/replication/config.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/replication/config.rs

Purpose: Adds replication decision logic to S3 `ReplicationConfiguration`. It filters rules, determines whether an object/delete/resync operation should replicate, and extracts target ARNs.

Important APIs and types: `ObjectOpts` describes an operation: object name, tags, version ID, delete marker status, SSE-C flag, replication type, replica/existing flags, and optional target ARN. `ReplicationConfigurationExt` provides `replicate`, `has_existing_object_replication`, `filter_actionable_rules`, `get_destination`, `has_active_rules`, and `filter_target_arns`.

Control flow and state: `filter_actionable_rules` skips disabled rules, target mismatches, invalid empty object names for normal operations, disabled existing-object rules, prefix mismatches, and tag-filter mismatches. Resync and All operations include rules early. Matched rules are sorted by priority when destinations match. `replicate` handles delete semantics separately: versioned delete markers require enabled delete-marker replication, versioned object deletes require enabled delete replication, and non-versioned deletes follow delete-marker replication. Non-delete operations use `rule.metadata_replicate`.

Dependencies and integration: Uses `rustfs_filemeta::ReplicationType`, S3 replication DTOs, `ReplicationRuleExt` from sibling rule module, and tag decoding from bucket tagging. Re-exported by `replication/mod.rs` for replication pool/resync paths.

Risks: Sorting only orders rules when destinations are equal; multi-destination ordering remains original/unspecified. `replicate` returns based on the first actionable rule, so later matching rules are ignored. Tag decode failures likely become empty maps depending on `decode_tags_to_map`, affecting filtered replication.

Test signals: Tests cover target ARN extraction with multiple destinations, role fallback, excluding disabled existing-object targets for existing-object operations, and including them for heal operations.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/replication/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/replication/datatypes.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/replication/datatypes.rs

Purpose: Defines shared replication resync status values and their display strings.

Important APIs and types: `ResyncStatusType` enum includes `NoResync`, `ResyncPending`, `ResyncCanceled`, `ResyncStarted`, `ResyncCompleted`, and `ResyncFailed`. `is_valid` treats every value except `NoResync` as valid. `Display` maps statuses to user-facing strings such as `Ongoing`, `Completed`, `Failed`, `Pending`, and `Canceled`.

Control flow and state: Stateless enum helpers. Serialization derives allow the status to appear in persisted replication state and API responses.

Dependencies and integration: Used by replication resync state and migration normalization of `.replication/resync.bin`. Re-exported by `replication/mod.rs`.

Risks: `NoResync` displays as an empty string, so UI/API consumers must not confuse it with missing data. Adding statuses requires updating both `is_valid` and `Display`.

Test signals: No direct tests in this file. Migration tests indirectly exercise resync status encode/decode around this type.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/replication/datatypes.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/replication/mod.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/replication/mod.rs

Purpose: Assembles the replication subsystem module tree and re-exports its public API.

Important APIs and types: Private modules include `config`, `replication_pool`, `replication_resyncer`, `replication_state`, and `rule`; `datatypes` is public. The file re-exports config extensions, datatypes, pool/resyncer APIs, `BucketStats` from replication state, and rule extensions.

Control flow and state: No runtime logic. It determines which replication internals are visible to the rest of `ecstore`.

Dependencies and integration: Downstream modules import replication decisions, resync helpers, and state through this module. `migration.rs` imports `decode_resync_file` and `encode_resync_file` from the re-exported replication API.

Risks: Broad `pub use` exports can make internal types part of the effective crate API and increase coupling. Private module declarations still expose many items through re-exports.

Test signals: No direct tests. Compilation and tests in child modules validate this wiring.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/replication/mod.rs -->

# Research: subset-b-008239 lifecycle module files

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/bucket_lifecycle_ops.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/bucket_lifecycle_ops.rs

## Purpose

This file is the operational side of bucket lifecycle management in RustFS ecstore. It turns lifecycle evaluation results into side effects: queuing and executing expiry work, queuing and executing tier transitions, expiring transitioned objects from remote warm tiers, deleting local object versions, scheduling replication delete work, validating transition tiers, restoring transitioned objects, and periodically cleaning stale multipart upload state.

It sits between lifecycle policy evaluation (`core.rs` and `evaluator.rs`), bucket metadata systems, object APIs on `ECStore`, remote tier drivers, replication, object lock, event notification, and scanner metrics. The file owns long-lived global worker state through `GLOBAL_ExpiryState` and `GLOBAL_TransitionState`.

## Important APIs, Types, and Functions

- `LifecycleSys` wraps lifecycle config lookup through `metadata_sys::get_lifecycle_config` and exposes `trace` closures for lifecycle audit/debug logging.
- `ExpiryOp`, `ExpiryTask`, `FreeVersionTask`, `NewerNoncurrentTask`, and `Jentry` form the dynamic task set consumed by expiry workers.
- `ExpiryState` owns per-worker Tokio MPSC channels, missed-task counters, worker resizing, and the expiry worker loop.
- `TransitionTask`, `TransitionWorker`, `TransitionState`, and `ImmediateEnqueueFailure` own transition queueing, async-channel backpressure handling, worker resizing, active task metrics, compensation backfill, and last-day tier stats.
- `init_background_expiry`, `TransitionState::init`, and `init_background_stale_multipart_upload_cleanup` start the background systems.
- `validate_transition_tier` checks lifecycle transition storage classes against `GLOBAL_TierConfigMgr`.
- `enqueue_transition_immediate`, `enqueue_immediate_expiry`, `enqueue_transition_for_existing_objects`, and `enqueue_expiry_for_existing_objects` are scanner/S3 event entry points that evaluate lifecycle rules and enqueue or apply work.
- `transition_object`, `get_transitioned_object_reader`, `expire_transitioned_object`, `apply_expiry_on_transitioned_object`, and `apply_expiry_on_non_transitioned_objects` are the main object-operation side effects.
- `post_restore_opts`, `put_restore_opts`, and `RestoreRequestOps::validate` build and validate restore-related `ObjectOptions`.
- `LifecycleOps for ObjectInfo` converts storage object metadata into lifecycle `ObjectOpts` and identifies remote transitioned objects.
- `eval_action_from_lifecycle` is a secondary guard around `lc.eval`, suppressing deletes that conflict with object lock or active replication.
- `apply_lifecycle_action`, `apply_expiry_rule`, and `apply_transition_rule` are dispatch helpers used by scanner-like callers.
- Multipart cleanup helpers (`read_stale_multipart_candidate`, `stale_upload_lifecycle_due`, `cleanup_stale_multipart_uploads_in_set`, etc.) discover incomplete multipart metadata on disks, evaluate abort rules, and delete stale upload directories.

## Control Flow

Expiry work starts when callers call `apply_expiry_rule`, `enqueue_immediate_expiry`, or scanner enqueue paths. `ExpiryState::enqueue_by_days` hashes a task by bucket/object and routes it to a stable worker channel. `ExpiryState::worker` receives boxed `ExpiryOp` values, downcasts to the concrete task type, and dispatches:

- `ExpiryTask` calls `apply_expiry_on_transitioned_object` if the object is already transitioned, otherwise `apply_expiry_on_non_transitioned_objects`.
- `NewerNoncurrentTask` batches noncurrent-version deletes through `delete_object_versions`.
- `Jentry` deletes an object from a remote tier journal entry.
- `FreeVersionTask` deletes remote tier state and then deletes the local free-version marker from a pool set.

Transition work starts when lifecycle evaluation returns `TransitionAction` or `TransitionVersionAction`. `TransitionState::queue_transition_task` uses a bounded async-channel. Immediate S3 write sources first try `try_send`, then wait for `transition_queue_send_timeout`; on timeout or closed queues they schedule per-bucket compensation through `enqueue_transition_for_existing_objects`. Scanner sources do not block; queue-full scanner attempts are recorded and deferred to future scans/backfill. `TransitionState::worker_with_cancel` receives tasks, calls `transition_object`, records metrics, updates daily tier stats, and sends object transition complete/failed events.

Existing-object scanning flows page through `list_object_versions` with marker/version-marker continuation. Transition scanning calls `enqueue_transition_with_lifecycle` for every version. Expiry scanning calls `eval_action_from_lifecycle`, delays once for recent date-expiry config changes, and either applies due deletes immediately or enqueues them.

Stale multipart cleanup periodically lists local multipart sha directories on each set, reads `xl.meta` metadata when available, merges duplicate disk candidates by preferring metadata-rich records, computes the earlier of default stale expiry and lifecycle `AbortIncompleteMultipartUpload` due time, deletes due upload directories through `set.delete_all`, and then removes empty multipart sha directories from local disks.

## State and Persistence Behavior

Global in-memory state:

- `GLOBAL_ExpiryState` stores expiry worker channels, receiver handles, and counters for missed expiry, free-version, tier journal tasks, and worker count.
- `GLOBAL_TransitionState` stores the bounded transition queue, worker cancellation tokens/handles, active task counters, queue-full/timeout counters, compensation-bucket deduplication, and last-day tier stats.

Persistent side effects:

- Local object and version metadata are mutated via `ECStore::delete_object`, set-level `delete_object_version`, and `api.transition_object`.
- Remote tier objects are deleted via `delete_object_from_remote_tier`; transitioned reads use tier drivers from `GLOBAL_TierConfigMgr`.
- Multipart metadata under `RUSTFS_META_MULTIPART_BUCKET` is read and deleted directly through disk/set APIs.
- Lifecycle configs, object-lock configs, and replication configs are read from bucket metadata systems.
- Delete replication work is scheduled by constructing `DeletedObjectReplicationInfo` and calling `schedule_replication_delete`.
- S3 event notifications are emitted for lifecycle expiration and transition complete/failure.

Notable persistence safeguards include setting `ObjectOptions.expiration.expire`, choosing `version_id` for version deletes, setting `delete_prefix`/`delete_prefix_object` for delete-all lifecycle actions, marking `skip_decommissioned` only after remote-tier delete success, and preserving user metadata/tags when building restore options.

## Dependencies and Integration Points

The file depends on:

- lifecycle policy types/functions from `core.rs` and version-aware `Evaluator` from `evaluator.rs`.
- lifecycle audit source/action data from `bucket_lifecycle_audit`.
- tier journal and warm backend APIs from `tier_sweeper`, `tier_last_day_stats`, and `tier::warm_backend`.
- bucket metadata, versioning, object lock, replication, event notification, metrics, and global service cancellation.
- `ECStore` plus object/list/multipart operation traits from `store_api`.
- `s3s::dto` lifecycle, restore, replication, and timestamp DTOs.
- `rustfs_filemeta` metadata helpers for restore status, replication state, and free-version markers.

This file is a central integration point for scanner-driven ILM behavior and immediate S3 write-path ILM behavior. It also provides reader support for transitioned objects, so GET paths can retrieve data from configured warm tiers.

## Risks and Edge Cases

- Worker queues are bounded and can drop/defer work. The code tracks missed tasks and schedules transition compensation for immediate-source transition failures, but expiry enqueue failures depend on future scans.
- `ExpiryState` uses a write lock around enqueue calls; long or repeated enqueues can contend with worker resizing.
- Several operations deliberately treat object-not-found/version-not-found as benign, but remote tier failures may leave remote data or local metadata divergent until journal/compensation catches up.
- Transition worker counters must stay balanced around all success and error paths; task panic would leave active counts wrong.
- Date-expiry config update grace is a single 5-second delay for an existing-object scan; highly concurrent config updates may still race scanner decisions.
- `LifecycleOps::to_lifecycle_opts` omits some `ObjectInfo` fields (`user_defined`, replication status) that `core.rs` can evaluate, while `enqueue_immediate_expiry` constructs options through the same helper before `Evaluator`; callers that need lock/replication metadata must pass it separately.
- Stale multipart cleanup reads local disks and deletes set paths; incorrect metadata parsing or upload-id encoding would risk deleting active uploads, although initiation time and lifecycle/default due checks reduce this.
- `Transition::next_due` in `core.rs` unwraps `obj.mod_time`; transition callers must provide valid `mod_time`.

## Test Signals

This file has extensive unit and integration-style tests under its `tests` module. Coverage includes expiry enqueue misses without workers, scanner transition queue full metrics, queue capacity and timeout environment handling, transition worker resizing/cancellation, compensation deduplication, date-expiry grace checks, remote delete option handling, lifecycle deleted-object construction, replication state construction/reuse, stale multipart candidate merge behavior, stale multipart cleanup with default expiry and lifecycle abort rules including size filters, multipart metadata sanitization, repeated part overwrite behavior, and empty multipart sha-directory cleanup. One ECStore fresh-boot test is ignored because it requires isolated global object layer state.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/bucket_lifecycle_ops.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/core.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/core.rs

## Purpose

This file is the policy-evaluation core for bucket lifecycle rules. It validates S3 lifecycle configurations, matches lifecycle rules against object metadata, computes due times for expiration and transition actions, chooses the highest-priority lifecycle event for an object/version, and defines the object/event option structures consumed by operational code in `bucket_lifecycle_ops.rs`.

It implements lifecycle behavior directly on `s3s::dto::BucketLifecycleConfiguration` and related DTOs, while re-exporting `IlmAction` as the action enum used across the lifecycle package.

## Important APIs, Types, and Functions

- Constants `TRANSITION_COMPLETE` and `TRANSITION_PENDING` define transition status markers shared with object metadata.
- `RuleValidate for LifecycleRule` validates rule-level constraints: legacy prefix/filter conflict, delete-marker-with-tags conflict, and at least one lifecycle action.
- `lifecycle_rule_prefix` selects the effective non-empty prefix from legacy `Prefix`, `Filter.Prefix`, or `Filter.And.Prefix`.
- `Lifecycle for BucketLifecycleConfiguration` provides `has_transition`, `has_expiry`, `has_active_rules`, `validate`, `filter_rules`, `eval`, `predict_expiration`, `eval_inner`, and `noncurrent_versions_expiration_limit`.
- `LifecycleCalculate` provides `next_due` for `LifecycleExpiration`, `NoncurrentVersionTransition`, and `Transition`.
- `expected_expiry_time` implements S3-compatible day-based rounding to the configured ILM processing boundary, with `days == 0` returning `UNIX_EPOCH` for immediate expiry.
- `abort_incomplete_multipart_upload_due` computes the earliest due time for abort-incomplete-multipart-upload lifecycle rules.
- `ObjectOpts` is the normalized object/version input used by lifecycle evaluation.
- `Event` is the evaluation result, carrying `IlmAction`, rule id, due time, noncurrent limits, and storage class.
- `ExpirationOptions` and `TransitionOptions` are options attached to object operations when applying lifecycle actions.

## Control Flow

Validation starts at `BucketLifecycleConfiguration::validate`. It rejects more than 1000 rules, empty rule sets, invalid statuses, negative expiration/noncurrent days, non-midnight expiration dates, rule IDs over 255 characters, duplicate IDs, and object-lock-incompatible all-version/delete-marker actions. It delegates rule structural checks to `RuleValidate`.

Rule matching starts in `filter_rules`: disabled rules are skipped, effective prefixes must match the object name, tag filters are evaluated through `rule.rs`, and size bounds are applied for non-delete-marker objects. Matching rules are cloned and returned in lifecycle order.

Evaluation starts with `eval`, which passes `OffsetDateTime::now_utc()` into `eval_inner`. `eval_inner` rejects missing or zero modification times, adds restore-expiry delete events when restored copies have expired, then walks matching rules and pushes candidate events for:

- expired-object-delete-marker and `DelMarkerExpiration` delete-marker behavior,
- noncurrent version expiration by `NoncurrentDays`,
- noncurrent version transitions,
- latest or unversioned object expiration by date/days, including `ExpiredObjectAllVersions`,
- current-version transitions by date/days.

At the end, candidate events are sorted so already-due deletes win over transitions at the same due time, otherwise the earliest due event wins. If no event applies, a default `NoneAction` event is returned.

`predict_expiration` is a read-only prediction path for latest non-delete-marker objects. It ignores expired-object-delete-marker rules and returns the closest future or configured expiration event without requiring it to be due now.

`noncurrent_versions_expiration_limit` extracts the configured noncurrent retention counts/days for scanner batching logic.

## State and Persistence Behavior

This file has no durable persistence and no background state. It is pure policy logic apart from:

- current-time reads through `OffsetDateTime::now_utc`,
- environment reads for `RUSTFS_ILM_PROCESS_TIME` and deprecated `_RUSTFS_ILM_PROCESS_TIME`,
- debug logging for evaluation and expiry-time computation.

The output `Event` and option structs are later persisted indirectly by `bucket_lifecycle_ops.rs` when it deletes objects, transitions objects, or writes restore metadata.

## Dependencies and Integration Points

The file depends on `s3s::dto` lifecycle DTOs, `time`, `uuid`, `rustfs_config`, `rustfs_filemeta`, `rustfs_common::metrics::IlmAction`, and `crate::store_api::ObjectInfo`. Tag and size matching are delegated to `crate::bucket::lifecycle::rule::Filter`.

It is used by:

- `bucket_lifecycle_ops.rs` for scanner and immediate action decisions.
- `evaluator.rs` for version-list evaluation with object-lock and replication suppression.
- stale multipart cleanup for `AbortIncompleteMultipartUpload` due-time calculation.
- bucket lifecycle validation paths elsewhere in the metadata/API layer.

## Risks and Edge Cases

- `Transition::next_due` unwraps `obj.mod_time` when `days` is set; callers must ensure current-version transition candidates have a modification time.
- `has_active_rules` indexes the first transition with `rule_transitions[0]` when transitions are present, assuming non-empty vectors.
- `filter_rules` clones matching rules, which is simple but potentially expensive for very large rule sets near the 1000-rule limit.
- Some lifecycle logic only inspects the first transition/noncurrent transition, so multiple transition entries may not be fully honored.
- `eval_inner` accepts `_newer_noncurrent_versions` but currently does not use that argument; version-list logic in `evaluator.rs` tracks spared noncurrent versions separately, while this core method skips rules with `newer_noncurrent_versions > 0`.
- `Event::default` uses `due = UNIX_EPOCH`, so callers must check `action` and not treat default due as an actionable immediate event.
- Object-lock validation permits ordinary days-based expiration on locked buckets, but operational code must still check actual retention before deleting individual object versions.

## Test Signals

The test module is broad. It verifies zero and negative expiration days, zero and negative noncurrent days, abort-incomplete-only rules, non-midnight expiration dates, prediction selecting the closest expiry, duplicate and too-long rule IDs, case-sensitive status validation, latest object expiration before/after due, current and noncurrent transitions, noncurrent expiration including zero-day immediate expiry, noncurrent expiration-limit extraction, prefix/filter/tag matching, expired-object-delete-marker due behavior, object-lock compatibility for delete marker and all-version extensions, configurable processing-boundary rounding, legacy prefix/filter conflict rules, and `ExpiredObjectAllVersions` evaluation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/core.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/evaluator.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/evaluator.rs

## Purpose

This file provides a version-list evaluator around the core lifecycle policy. It evaluates all versions of one object together so lifecycle delete-all behavior, noncurrent-version counting, object-lock suppression, and replication suppression can be applied consistently across a version stack.

## Important APIs, Types, and Functions

- `Evaluator` stores an `Arc<BucketLifecycleConfiguration>` plus optional object-lock retention config and optional replication config.
- `Evaluator::new` constructs the evaluator for a lifecycle policy.
- `with_lock_retention` and `with_replication_config` attach optional guard configs.
- `is_pending_replication` checks for active replication rules and non-empty version purge status.
- `is_object_locked` checks bucket object-lock enablement and then delegates metadata-level retention checks to `is_object_locked_by_metadata`.
- private `eval_inner` evaluates an ordered `&[ObjectOpts]` at a supplied time and returns parallel `Event` values.
- public `eval` validates that the input slice is non-empty and that `objs.len() == objs[0].num_versions`, then evaluates using current UTC time.

## Control Flow

`eval` first enforces version-count consistency. `eval_inner` initializes default events, tracks `newer_noncurrent_versions`, and walks versions in order. For each object version it asks `policy.eval_inner(obj, now, newer_noncurrent_versions)` for a raw lifecycle event.

Delete-all actions are special. If object lock is enabled for the bucket, they are suppressed. Otherwise the event is recorded for that version and the evaluator stops scanning the remaining versions, because deleting all versions makes later per-version decisions unnecessary.

Version delete actions are sanitized defensively. A version delete for a nil/missing version id becomes `NoneAction`; object-lock metadata suppresses deletion; pending replication suppresses deletion. After event handling, the evaluator increments `newer_noncurrent_versions` for non-latest versions that are not being deleted, preserving newer noncurrent versions for later rule decisions.

## State and Persistence Behavior

The evaluator has no persistence and no background state. It reads policy/config objects passed by `Arc`, inspects `ObjectOpts`, and returns a vector of lifecycle `Event` values. Actual deletes, transitions, and replication scheduling happen in `bucket_lifecycle_ops.rs`.

## Dependencies and Integration Points

The evaluator depends on:

- `core.rs` through `Lifecycle`, `Event`, and `ObjectOpts`.
- `objectlock_sys::is_object_locked_by_metadata` for retention checks.
- `ReplicationConfig` plus `ReplicationConfigurationExt::has_active_rules`.
- `s3s::dto` object-lock and lifecycle DTOs.
- `IlmAction` for action matching.

It is used by `enqueue_immediate_expiry` in `bucket_lifecycle_ops.rs`, which builds a full version list for a just-written object name, attaches object-lock and replication configs from bucket metadata, evaluates events, and then applies or batches due expiry actions.

## Risks and Edge Cases

- Correct behavior depends on the caller passing all versions for a single object in the order expected by `newer_noncurrent_versions` accounting.
- `eval` only compares the slice length to `objs[0].num_versions`; it does not verify that every `ObjectOpts` belongs to the same object name or bucket.
- `is_pending_replication` checks `!obj.version_purge_status.is_empty()` under active rules, so replication suppression is tied to how `ObjectOpts` was populated. If callers omit purge status, deletes may not be suppressed here.
- Delete-all actions stop scanning remaining versions only when object lock does not suppress them; this is intentional but makes object-lock configuration a major branch in version-stack behavior.

## Test Signals

There are no local tests in this file. Behavior is indirectly covered by lifecycle operation tests that call immediate expiry evaluation and by core lifecycle tests that cover raw event calculation. Direct tests would be valuable for version order, `num_versions` mismatch errors, object-lock suppression, pending replication suppression, and delete-all short-circuit behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/evaluator.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/mod.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/mod.rs

## Purpose

This file is the module declaration and public wiring point for the bucket lifecycle package. It exposes the lifecycle submodules and aliases `core` as `lifecycle`, which lets the rest of ecstore import `crate::bucket::lifecycle::lifecycle::{...}` while the implementation file remains named `core.rs`.

## Important APIs, Types, and Functions

The module declarations are:

- `bucket_lifecycle_audit`
- `bucket_lifecycle_ops`
- `core`
- `evaluator`
- `rule`
- `tier_last_day_stats`
- `tier_sweeper`

The only re-export is `pub use self::core as lifecycle;`.

## Control Flow

There is no runtime control flow. Rust module loading makes each child module available, and the `core` re-export establishes the stable import path used by lifecycle operation code and other consumers.

## State and Persistence Behavior

There is no state or persistence in this file.

## Dependencies and Integration Points

This file integrates the lifecycle package with the crate module tree. The alias is important because `bucket_lifecycle_ops.rs` imports `crate::bucket::lifecycle::lifecycle::{ExpirationOptions, Lifecycle, ObjectOpts, TransitionOptions, ...}` and `evaluator.rs` imports `crate::bucket::lifecycle::lifecycle::{Event, Lifecycle, ObjectOpts}`.

Changing this file can break all downstream module paths even though it has no business logic.

## Risks and Edge Cases

- Removing or renaming `pub use self::core as lifecycle` would break existing imports throughout lifecycle operations.
- Adding modules here affects compile visibility but not behavior by itself.
- There are no guards or tests specific to this module declaration file.

## Test Signals

There are no local tests. Compile success of the lifecycle package is the primary signal that module declarations and the `lifecycle` alias remain valid.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/rule.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/rule.rs

## Purpose

This file implements lifecycle rule filter helpers for tag and object-size matching, plus minimal transition validation. It is used by `core.rs` when deciding whether a lifecycle rule applies to an object or multipart upload candidate.

## Important APIs, Types, and Functions

- `Filter` trait defines `test_tags(&self, user_tags: &str) -> bool` and `by_size(&self, sz: i64) -> bool`.
- `impl Filter for LifecycleRuleFilter` decodes object tags and checks single-tag, AND-tag, top-level size, and AND-size constraints.
- `requires_tag_matching` returns whether the filter has any tag constraints.
- `tag_matches` requires both tag key and value to be present and equal to decoded user tags.
- `and_tags_match` requires all tags in the AND operator to match.
- `and_size_matches` applies AND-scoped greater-than and less-than size constraints.
- `TransitionOps` trait defines `validate`.
- `impl TransitionOps for Transition` rejects transitions that specify both `Date` and positive `Days`, and rejects missing storage class.

## Control Flow

`test_tags` returns true immediately when a lifecycle filter has no tag constraints. When tag constraints exist, it decodes the URL-encoded S3 tag string through `decode_tags_to_map`, then requires both the top-level `Tag` and every `And.Tags` entry to match when present.

`by_size` clamps negative object sizes to zero, then applies top-level `ObjectSizeGreaterThan` and `ObjectSizeLessThan`, followed by any AND-scoped size constraints. Bounds are strict: size must be greater than the minimum and less than the maximum.

`TransitionOps::validate` enforces that a transition has exactly one timing mode in practice for date/positive-days conflicts and that a storage class exists.

## State and Persistence Behavior

The file is stateless and performs no persistence. It transforms provided filter DTOs and tag strings into boolean decisions used by lifecycle evaluation.

## Dependencies and Integration Points

It depends on `crate::bucket::tagging::decode_tags_to_map` and `s3s::dto::{LifecycleRuleAndOperator, LifecycleRuleFilter, Tag, Transition}`.

`core.rs` calls:

- `<LifecycleRuleFilter as Filter>::test_tags(filter, &obj.user_tags)` during rule filtering.
- `<LifecycleRuleFilter as Filter>::by_size(filter, obj.size as i64)` for non-delete-marker object filtering.

Stale multipart cleanup in `bucket_lifecycle_ops.rs` constructs `ObjectOpts` with object name, user tags, size, and initiation time; those options flow through `core.rs` and this filter logic for abort-incomplete rules.

## Risks and Edge Cases

- `TransitionOps::validate` allows `date` plus `days == 0`; the error text says exactly one of Days or Date should be present, but the implementation only rejects date plus positive days.
- `test_tags` relies on `decode_tags_to_map`; malformed tag strings may decode to an empty or partial map depending on that helper.
- Missing tag key or value always fails that specific tag match.
- Size bounds are strict, matching S3 lifecycle filter semantics, so boundary equality does not match.
- Negative sizes are clamped to zero, avoiding accidental lower-bound matches for invalid size inputs.

## Test Signals

Local unit tests cover single-tag matching, all-tags matching for AND filters, strict object-size bounds, and the fact that filters without tag constraints accept any tag string. There are no local tests for transition validation, malformed tag decoding, combined top-level and AND size constraints, or date plus zero-day transition behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/rule.rs -->

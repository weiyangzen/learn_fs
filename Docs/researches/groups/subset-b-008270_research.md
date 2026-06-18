# subset-b-008270 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/config_manager.rs -->
# sources/object-store/rustfs/crates/notify/src/config_manager.rs

## Purpose
Coordinates notification target configuration with the live runtime. It owns the shared server `Config`, constructs configured targets through `TargetRegistry`, activates replay-capable target runtimes through `NotifyRuntimeFacade`, and persists target config mutations back into the object-store backed server config.

## Important APIs, types, and functions
- `NotifyConfigManager` holds `Arc<RwLock<Config>>`, `Arc<TargetRegistry>`, `NotifyRuleEngine`, and `NotifyRuntimeFacade`.
- `init` clones the current config, creates targets, activates them with replay, and replaces the runtime target set.
- `reload_config` updates the in-memory config, rebuilds targets from a supplied `Config`, activates replay, and commits the replacement runtime.
- `set_target_config`, `remove_target`, and `remove_target_config` wrap persistent config mutation through `update_config_and_reload`.
- `runtime_target_id_for_subsystem` maps config subsystem names such as `notify_webhook` to runtime target types such as `webhook`; target names are lowercased.
- `notify_configuration_hint` emits an operator hint for empty notification target configuration.

## Control flow
Initialization and reload both follow the same path: read or accept a `Config`, call `TargetRegistry::create_targets_from_config`, pass the resulting target boxes to `NotifyRuntimeFacade::activate_targets_with_replay`, then call `replace_targets`. Mutating APIs read the persisted server config via `rustfs_ecstore::config::com::read_config_without_migrate`, apply a closure, skip reload if unchanged, save the new config, then reload.

## State and persistence behavior
The authoritative target configuration is persisted with `save_server_config` through the global object-store handle. The manager also updates the shared in-memory `Config` behind an async `RwLock`. Runtime target state is replaced atomically through the runtime facade after config persistence succeeds. `remove_target_config` protects referential integrity by asking `NotifyRuleEngine::is_target_bound_to_any_bucket` before deletion.

## Dependencies and integration points
Integrates `rustfs_config::notify` subsystem constants, `rustfs_ecstore` global storage/config APIs, `rustfs_targets` target creation and `TargetID`, `TargetRegistry`, `NotifyRuleEngine`, and `NotifyRuntimeFacade`. Logging uses structured `tracing` fields for lifecycle and config update events.

## Risks and edge cases
Target removal fails if server storage is not initialized, so API callers must distinguish runtime-only state from persisted config state. The config key path lowercases type/name; callers using mixed-case names must rely on this normalization. Deleting an unbound target is idempotent, but a target bound to any bucket rule is blocked to avoid dangling bucket notifications. Empty target sets are legal and logged with an idle hint.

## Test signals
Tests confirm empty `init` and `reload_config` succeed, and verify subsystem-to-runtime target ID mappings for webhook, AMQP, MQTT, Kafka, NATS, Pulsar, Redis, and Postgres. The persistence paths are not deeply integration-tested here because they require initialized object-store config storage.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/config_manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/error.rs -->
# sources/object-store/rustfs/crates/notify/src/error.rs

## Purpose
Defines the notification crate's public error surface, separating lifecycle state failures from target, configuration, bucket-rule, storage, and I/O failures.

## Important APIs, types, and functions
- `LifecycleError` has `AlreadyInitialized` and `NotInitialized` variants for the global `OnceLock` lifecycle.
- `NotificationError` wraps `TargetError`, `LifecycleError`, `io::Error`, string-backed configuration/read/save/storage errors, ARN errors, target lookup errors, and initialization failures.
- `thiserror::Error` derives user-facing error messages and `#[from]` conversions for target and lifecycle errors.

## Control flow
The file has no runtime logic; it supplies variants consumed by global initialization, target registry/config managers, XML/bucket config handling, and runtime facade shutdown/replacement calls.

## State and persistence behavior
No state is stored here. Variants such as `ReadConfig`, `SaveConfig`, and `StorageNotAvailable` represent persistence failures emitted by `NotifyConfigManager`.

## Dependencies and integration points
Depends on `rustfs_targets::{TargetError, arn::TargetID}`, standard `io`, and `thiserror`. It is re-exported from `lib.rs`, making these errors part of the crate API.

## Risks and edge cases
Several variants carry plain strings, so downstream matching on error causes is less structured for configuration and storage failures. `Io(io::Error)` is not marked with `#[from]`, so conversions must be explicit where used.

## Test signals
There are no direct tests in this file; coverage is indirect through APIs returning `NotificationError`, especially global lifecycle tests, config manager tests, and runtime facade target replacement tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/event.rs -->
# sources/object-store/rustfs/crates/notify/src/event.rs

## Purpose
Models S3-compatible notification events and builds them from RustFS object-operation context. It covers bucket/object metadata, request/response details, source information, event schema versioning, replication suppression hints, and restore-completed Glacier payloads.

## Important APIs, types, and functions
- Serializable structs: `Identity`, `Bucket`, `Object`, `Metadata`, `Source`, `GlacierEventData`, `RestoreEventData`, and `Event`.
- `Event::new_test_event` builds synthetic events for unit tests.
- `Event::mask` delegates to `EventName::mask`.
- `Event::new(EventArgs)` creates production events from `rustfs_ecstore::store_api::ObjectInfo`.
- `EventArgs` carries event name, bucket, object info, request params, response elements, version id, host, port, and user agent.
- `EventArgs::is_replication_request` only honors `x-rustfs-source-replication-request` values `true` or `1`.
- `EventArgsBuilder` provides fluent construction for callers and tests.

## Control flow
`Event::new` computes a sequencer from object mod time or current timestamp, ensures `x-amz-request-id` and `x-amz-id-2` response keys exist, URL-encodes the object key, extracts principal/region from request params, and fills bucket/object metadata. Removed-object events omit size, ETag, content type, and user metadata. Non-removed events copy object metadata except keys prefixed with `x-amz-meta-internal-`. Restore-completed events add `glacier_event_data` when both expiry and storage class/tier are available.

## State and persistence behavior
No durable state is managed. Event values are serialized outbound to notification targets and stored in target queues when targets have a backing store. The sequencer uses timestamp-derived values rather than a persisted monotonic counter.

## Dependencies and integration points
Depends on `chrono`, `time`, `url::form_urlencoded`, `hashbrown::HashMap`, `rustfs_s3_types::{EventName, event_schema_version}`, `rustfs_s3_ops::is_object_removed_event`, and `rustfs_ecstore::store_api::ObjectInfo`. It feeds `NotifyPipeline`, `EventNotifier`, target stores, and global `notifier_global::notify`.

## Risks and edge cases
The event object key is URL-encoded before dispatch; the rule engine must compensate by matching decoded keys when bucket filters are written against raw keys. Removed events intentionally omit object details, which affects consumers expecting size or ETag on deletes. Replication suppression only accepts the RustFS header, not MinIO compatibility headers, to avoid dropping normal console deletes. `timestamp_nanos_opt().unwrap_or(0)` can collapse sequencers to zero if chrono cannot represent the timestamp.

## Test signals
Tests assert AWS-compatible event schema versions, Glacier restore payload contents and formatting, and replication-header behavior including case-insensitive `true`, numeric `1`, falsey values, and ignored MinIO replication headers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/event.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/event_bridge.rs -->
# sources/object-store/rustfs/crates/notify/src/event_bridge.rs

## Purpose
Compatibility/re-export module for the live event bridge API. It exposes `LiveEventHistory` and `NotifyEventBridge` from `pipeline`.

## Important APIs, types, and functions
- `pub use crate::pipeline::{LiveEventHistory, NotifyEventBridge};`
- `NotifyEventBridge` is a type alias to `NotifyPipeline` in `pipeline.rs`.

## Control flow
No local control flow exists. Callers importing from `event_bridge` receive the pipeline implementation.

## State and persistence behavior
State is owned by `NotifyPipeline` and `LiveEventHistory`; this file stores nothing.

## Dependencies and integration points
Integrates older or semantically clearer bridge naming with the current pipeline module. It is re-exported from `lib.rs`.

## Risks and edge cases
Because this is only a re-export, documentation or API drift must be tracked in `pipeline.rs`. Removing it would be a public API break for consumers using `NotifyEventBridge`.

## Test signals
No direct tests. Coverage comes from pipeline/live event tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/event_bridge.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/factory.rs -->
# sources/object-store/rustfs/crates/notify/src/factory.rs

## Purpose
Exposes built-in notification target plugin descriptors for the notify crate.

## Important APIs, types, and functions
- `builtin_target_descriptors` returns `BuiltinTargetDescriptor<Event>` values from `rustfs_targets::catalog::builtin::builtin_notify_target_descriptors`.
- `builtin_target_plugins` maps descriptors into cloneable `TargetPluginDescriptor<Event>` values.

## Control flow
The module delegates descriptor construction to `rustfs_targets`, then maps descriptors to plugin descriptors for registration in `TargetRegistry::new`.

## State and persistence behavior
No state is stored and no config is persisted. Target instances created from these descriptors may later have stores/replay behavior depending on target type and KVS config.

## Dependencies and integration points
Links the notify crate's concrete `Event` payload type to the generic target plugin catalog. Used by `registry.rs`.

## Risks and edge cases
Plugin availability and valid fields are defined outside this crate. Any mismatch between `rustfs_config::notify` keys and target plugin descriptors breaks target creation at registry/config-manager time.

## Test signals
Tests verify the AMQP descriptor is present, exposes the expected AMQP fields, and can create an AMQP target with `TargetID { id: "primary", name: "amqp" }` and no store for the provided base config.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/factory.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/global.rs -->
# sources/object-store/rustfs/crates/notify/src/global.rs

## Purpose
Provides the process-global notification system and the main notification entry points used by object operations and bucket notification management.

## Important APIs, types, and functions
- Static `NOTIFICATION_SYSTEM: OnceLock<Arc<NotificationSystem>>`.
- `initialize` creates a `NotificationSystem`, runs async initialization, then stores it once.
- `initialize_live_events` stores a system without loading configured targets/rules so live listeners can receive in-process events.
- `notification_system`, `is_notification_system_initialized`, `notification_metrics_snapshot`, and `notification_target_metrics` expose global state.
- `notifier_global::notify` builds and sends an `Event` unless the system is uninitialized or the operation is a RustFS replication request.
- `add_bucket_notification_rule`, `add_event_specific_rules`, and `clear_bucket_notification_rules` are public helpers around bucket rule loading/clearing.

## Control flow
`initialize` constructs and initializes the full runtime before setting `OnceLock`, so failure to build targets prevents global publication. `notifier_global::notify` fetches the global system, logs and returns if absent, filters replication events, constructs `Event::new(args)`, and sends through `NotificationSystem::send_event`. Rule helpers build `BucketNotificationConfig` with patterns from prefix/suffix inputs, then call into `NotificationSystem`.

## State and persistence behavior
The global `OnceLock` can only be set once per process. Bucket rule helper calls update in-memory bucket rule state through the notification system; target config persistence is handled elsewhere by `NotifyConfigManager`. Metrics snapshots return defaults when the global system does not exist.

## Dependencies and integration points
Connects object-store operations to `NotificationSystem`, `EventArgs`, `EventName`, `BucketNotificationConfig`, `TargetID`, and `rustfs_config::server_config::Config`. This is the major public integration surface re-exported by `lib.rs`.

## Risks and edge cases
There is no reset path for tests or process reconfiguration after `OnceLock` is set. `initialize_live_events` intentionally bypasses configured targets/rules, so external notifications remain disabled in that mode. The `add_event_specific_rules` helper calls `new_pattern(Some(prefix), Some(suffix))` even when either string is empty, which still works for many cases but differs from the explicit empty filtering used by `add_bucket_notification_rule`.

## Test signals
No direct test module in this file. Its behavior is indirectly exercised by notification system integration tests, event replication filtering tests, and bucket config/rule engine tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/global.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/integration.rs -->
# sources/object-store/rustfs/crates/notify/src/integration.rs

## Purpose
Defines the high-level `NotificationSystem` facade and aggregate notification metrics. It wires together notifier dispatch, target registry, config management, bucket rule management, live event pipeline, runtime views, health/status snapshots, and shutdown behavior.

## Important APIs, types, and functions
- `LiveEventBatch` returns recent live events with a cursor (`next_sequence`) and truncation flag.
- `NotificationMetrics` tracks processing, processed, failed, skipped counts, and uptime through atomics.
- `NotificationMetricSnapshot` and `NotificationTargetMetricSnapshot` are exported metric DTOs.
- `NotificationSystem::new` builds all shared components and `NotifyServices`.
- Facade methods expose target queries, subscriber checks, live event subscription/history, target/bucket config mutation, reload, event sending, status, target metrics/health, runtime status, and shutdown.
- `load_config_from_file` reads and unmarshals a server `Config` then reloads the system.

## Control flow
Construction creates a broadcast channel, metrics, subscriber view, rule engine, notifier, registry, shared config, replay worker manager, stream concurrency semaphore, and live event history, then assembles `NotifyServices`. `init` delegates to config manager initialization. `send_event` routes through `NotifyPipeline`, which records/broadcasts live events before target dispatch. `Drop` logs a metrics/status snapshot and emits final metric values through the `metrics` crate.

## State and persistence behavior
Runtime state is held in shared Arcs: target list, config lock, rule engine map, subscriber index, replay workers, live event history, and metric counters. Persistent target config writes are delegated to `NotifyConfigManager`. Bucket notification config lives in memory via rule engine and subscriber snapshot; this file does not persist bucket XML by itself.

## Dependencies and integration points
Integrates `EventNotifier`, `TargetRegistry`, `NotifyServices`, `LiveEventHistory`, `BucketNotificationConfig`, target replay workers, `metrics`, `tokio` sync primitives, `rustfs_config`, and `rustfs_targets` runtime snapshots.

## Risks and edge cases
Metric counters use relaxed atomics and `fetch_sub` on processing counts; incorrect caller pairing of increment/decrement could underflow in debug or wrap in release. `Drop` cannot await async shutdown, so callers should explicitly call `shutdown` for target/replay cleanup. Live event history is bounded and can truncate client catch-up responses.

## Test signals
Tests cover live event history cursor/truncation behavior and confirm `NotificationSystem` exposes live event listeners, records sent live events, and returns recent event batches.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/integration.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/lib.rs -->
# sources/object-store/rustfs/crates/notify/src/lib.rs

## Purpose
Crate root for RustFS notification support. It declares internal modules and re-exports the public API for notification events, global lifecycle, runtime management, rule configuration, targets, metrics, and status views.

## Important APIs, types, and functions
- Internal modules include config, event, global, pipeline, rule engine, runtime facade/view, services, status, bucket config manager, and subscriber view.
- Public modules: `factory`, `integration`, `notifier`, `registry`, and `rules`.
- Re-exports include `NotificationSystem`, `NotificationError`, `Event`, `EventArgs`, `EventArgsBuilder`, `NotifyConfigManager`, `NotifyRuleEngine`, `NotifyRuntimeFacade`, `NotifyRuntimeView`, `NotifyServices`, and global functions.

## Control flow
No executable control flow beyond module resolution and public exports.

## State and persistence behavior
No local state. Publicly exposes stateful components implemented in other modules, including the process-global notification system from `global.rs`.

## Dependencies and integration points
This root module defines the public surface consumed by RustFS server code and other crates. It also keeps several implementation modules private while exposing selected types.

## Risks and edge cases
Changing module visibility or re-exports is a public API change. `bucket_config_manager` is private as a module but `NotifyBucketConfigManager` is re-exported, so internals remain hidden while the type stays accessible.

## Test signals
No direct tests. Compilation of downstream tests validates the re-export surface.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/notification_system_subscriber.rs -->
# sources/object-store/rustfs/crates/notify/src/notification_system_subscriber.rs

## Purpose
Maintains a fast, consistent subscriber view per bucket for pre-dispatch checks such as `has_subscriber`.

## Important APIs, types, and functions
- `NotificationSystemSubscriberView` wraps a `SubscriberIndex`.
- `new` creates an empty index.
- `has_subscriber(bucket, event)` checks the index using the event mask in the current snapshot.
- `apply_bucket_config` compiles a `BucketNotificationConfig` into a `BucketRulesSnapshot`, debug-checks mask consistency, and atomically stores it.
- `clear_bucket` clears a bucket's snapshot.

## Control flow
Bucket config loading calls `apply_bucket_config` after rule compilation. Read paths call `has_subscriber`, which is a quick snapshot/mask read without reconstructing rules.

## State and persistence behavior
State is in-memory only, stored inside `SubscriberIndex` using `ArcSwap` snapshot cells. Persistence of bucket notification XML/config is outside this file.

## Dependencies and integration points
Depends on `BucketNotificationConfig`, `SubscriberIndex`, `BucketRulesSnapshot`, `DynRulesContainer`, and `EventName`. It is created in `NotificationSystem::new` and passed into `NotifyBucketConfigManager`.

## Risks and edge cases
Correctness depends on compiling masks and rules from the same source. The debug assertion catches inconsistent mask computation in debug builds only. This view is a subscriber fast path, not the authoritative dispatch matcher; it must stay in sync with `NotifyRuleEngine`.

## Test signals
No local tests. Indirect tests in services, rule config, and bucket config manager paths validate empty setup and compiled subscriber behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/notification_system_subscriber.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/notifier.rs -->
# sources/object-store/rustfs/crates/notify/src/notifier.rs

## Purpose
Implements event dispatch to configured runtime targets after bucket rule matching. It also owns the shared runtime target list and send-concurrency limiter.

## Important APIs, types, and functions
- `EventNotifier` holds `NotificationMetrics`, `NotifyRuleEngine`, `SharedNotifyTargetList`, and a send `Semaphore`.
- `send` matches target IDs, skips missing/disabled targets, spawns per-target save tasks, and waits for them.
- `get_arn_list`, `remove_all_bucket_targets`, `target_list`, and `init_bucket_targets_shared` expose runtime target list operations.
- `TargetList` wraps `TargetRuntimeManager<Event>` and supports add/get/keys/values, close-aware removal/clear, runtime metrics, health snapshots, status snapshots, and mutable runtime access for `NotifyRuntimeFacade`.

## Control flow
`send` extracts bucket, object key, and event name from an `Event`, asks the rule engine for matching targets, increments skipped metrics if none match, then reads the target list. For each matching runtime target it skips disabled targets, builds an `EntityTarget<Event>`, spawns a task gated by the send semaphore, calls `target.save`, and updates metrics based on success/failure and whether the target has a deferred store. Missing runtime targets are logged and counted as skipped. The function awaits all spawned tasks before returning.

## State and persistence behavior
The target list is in-memory runtime state. Targets may persist events internally through their `store()` implementation; the notifier only calls `save`. Metrics are updated around task execution. `remove_all_bucket_targets` and close-aware target-list methods call target close paths through the target runtime manager.

## Dependencies and integration points
Uses `rustfs_targets::{Target, EntityTarget, TargetRuntimeManager, SharedTarget}`, `TargetID`, `NotifyRuleEngine`, `NotificationMetrics`, `tokio::spawn`, and `tokio::sync::{RwLock, Semaphore}`. Send concurrency is configured by `ENV_NOTIFY_SEND_CONCURRENCY` with a default from `rustfs_config`.

## Risks and edge cases
Disabled targets are skipped without incrementing the skipped counter in the per-target branch. Metrics for deferred targets decrement processing rather than incrementing processed because final delivery comes from replay/queue processing. Because `send` waits for all target tasks, slow direct targets affect caller latency up to target `save` duration. Missing runtime targets can occur when bucket rules reference targets not currently active.

## Test signals
Tests verify encoded key matching behavior through the rule engine, disabled targets are not called, and prefix/suffix filters dispatch only matching objects. Test targets implement the target trait and count save calls.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/notifier.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/pipeline.rs -->
# sources/object-store/rustfs/crates/notify/src/pipeline.rs

## Purpose
Provides the event pipeline between object operations, live in-process listeners, recent-event history, and external target dispatch.

## Important APIs, types, and functions
- `LiveEventHistory` stores a bounded `VecDeque<(sequence, Arc<Event>)>` and the next sequence number.
- `record` appends an event and evicts older entries over `MAX_RECENT_LIVE_EVENTS` (1024).
- `snapshot_since(after_sequence, limit)` returns a `LiveEventBatch`.
- `NotifyPipeline` owns an `EventNotifier`, a broadcast sender, and shared live history.
- `has_live_listeners`, `subscribe_live_events`, `recent_live_events_since`, and `send_event` are the public pipeline API.
- `NotifyEventBridge` aliases `NotifyPipeline`.

## Control flow
`send_event` records the event under the live history write lock, sends it to the broadcast channel ignoring send errors, then awaits notifier dispatch. Recent-event reads take a read lock and return events with sequence greater than the supplied cursor up to the limit.

## State and persistence behavior
History is in-memory, bounded, and sequence-numbered. Broadcast subscribers are in-process only. Durable queueing, if any, is implemented by target stores after notifier dispatch.

## Dependencies and integration points
Connects `NotificationSystem::send_event`, live listener APIs, and `EventNotifier::send`. Uses `tokio::sync::{broadcast, RwLock}`.

## Risks and edge cases
Broadcast send errors are ignored, which is appropriate when there are no receivers but hides lagged/closed channel details. `snapshot_since` reports truncation when the requested limit is reached, not necessarily when older events have already been evicted; clients must use `next_sequence` defensively. `recent_live_events_since` coerces limit to at least one.

## Test signals
Tests confirm listener count transitions and that sent events are recorded in recent history with expected sequence and object key.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/pipeline.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/registry.rs -->
# sources/object-store/rustfs/crates/notify/src/registry.rs

## Purpose
Manages target plugin registration and target construction from notification configuration.

## Important APIs, types, and functions
- `TargetRegistry` wraps `TargetPluginRegistry<Event>`.
- `new` registers all built-in notify target plugins.
- `supports_target_type` queries plugin support.
- `create_target` creates one target from target type, instance id, and KVS.
- `create_targets_from_config` delegates full config/environment target discovery and creation using `NOTIFY_ROUTE_PREFIX`.

## Control flow
The registry is built at notification system construction time. Config initialization/reload asks it to create all enabled targets concurrently through the underlying plugin registry.

## State and persistence behavior
Registry state is plugin metadata only. Target runtime state is returned to callers and managed by `NotifyRuntimeFacade`/`EventNotifier`.

## Dependencies and integration points
Uses `factory::builtin_target_plugins`, `rustfs_targets::{TargetPluginRegistry, Target, TargetError}`, `rustfs_config::server_config::{Config, KVS}`, and `NOTIFY_ROUTE_PREFIX`. It is the bridge between server config/env target settings and concrete target instances.

## Risks and edge cases
Create behavior depends on plugin registry semantics, including environment override handling and enabled filtering. Unsupported target types fail in the lower registry. Any new notify target must be present in the built-in catalog or registered here.

## Test signals
A unit test confirms the AMQP target type is registered.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/registry.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rule_engine.rs -->
# sources/object-store/rustfs/crates/notify/src/rule_engine.rs

## Purpose
Stores per-bucket notification rules and resolves event/object pairs into target IDs for dispatch.

## Important APIs, types, and functions
- `NotifyRuleEngine` wraps `Arc<AsyncShardedHashMap<String, RulesMap, FxBuildHasher>>` with cached snapshots.
- `set_bucket_rules`, `get_bucket_rules`, and `clear_bucket_rules` mutate/query bucket rules.
- `has_subscriber` checks whether a bucket has rules for an event.
- `match_targets` returns all target IDs matching a bucket, event, and object key.
- `is_target_bound_to_any_bucket` scans all bucket rules for a target ID.
- `decoded_object_key_for_matching` percent-decodes encoded keys only when decoding changes the key.

## Control flow
Bucket config loading calls `set_bucket_rules`, which removes empty maps or inserts non-empty maps. Dispatch calls `match_targets`; this first matches the supplied object key and then, if the key contains percent escapes that decode successfully to a different string, also matches the decoded key and unions the results.

## State and persistence behavior
Bucket rules are in-memory in a sharded async map. There is no direct persistence here; bucket notification configuration loading supplies the maps.

## Dependencies and integration points
Uses `RulesMap`, `TargetIdSet`, `EventName`, `TargetID`, `starshard::AsyncShardedHashMap`, `percent_encoding`, and structured tracing. Called by `EventNotifier`, `NotifyConfigManager`, and bucket config APIs.

## Risks and edge cases
The target-bound scan iterates all bucket maps, which may be expensive with many buckets but is used for config deletion safety rather than per-event dispatch. Matching both raw and decoded keys is necessary because events encode keys while rules are often raw; malformed percent encodings simply skip the decoded pass.

## Test signals
Tests cover bucket rule lifecycle, subscriber checks, target-bound checks, matching results, and clearing behavior. Additional notifier tests cover encoded/decoded key matching and suffix-filter non-bypass.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rule_engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/config.rs -->
# sources/object-store/rustfs/crates/notify/src/rules/config.rs

## Purpose
Defines `BucketNotificationConfig`, the validated in-memory bucket notification configuration, and compiles it into both precise dispatch rules and fast subscriber snapshots.

## Important APIs, types, and functions
- `BucketNotificationConfig { region, rules: RulesMap }`.
- `new`, `add_rule`, `get_rules_map`, and `set_region` provide construction and mutation.
- `from_xml` parses `NotificationConfiguration`, applies defaults, validates region/ARNs, and converts queue configs into `RulesMap` entries.
- `validate` checks region equality and target ARN membership.
- `compile_snapshot` adapts `RulesMap` into `BucketRulesSnapshot<DynRulesContainer>`.
- Internal `RuleView` and `CompiledRules` adapt event keys into the `RulesContainer` trait used by subscriber snapshots.

## Control flow
XML parsing uses `NotificationConfiguration::from_reader`, `set_defaults`, and `validate`. Each queue config contributes its target ID, event list, and filter-derived pattern to `RulesMap::add_rule_config`. Snapshot compilation creates one `RuleView` per event key in the map and ORs event masks to produce the bucket snapshot mask.

## State and persistence behavior
This type is in-memory and serializable/deserializable. It does not persist itself; callers load it into `NotifyRuleEngine` and `NotificationSystemSubscriberView`.

## Dependencies and integration points
Uses `RulesMap`, `xml_config`, `subscriber_snapshot`, `EventName`, `TargetID`, and serde. It is consumed by global rule helpers, bucket config manager, and notification system facade methods.

## Risks and edge cases
`CompiledRules` currently tracks event presence only for subscriber checks, not full pattern/target details. `validate` reconstructs ARNs from target IDs and region, so ARN formatting must match `TargetID::to_arn`. Empty patterns are converted to match-all by `RulesMap`.

## Test signals
Integration tests in `config_test.rs` exercise XML parsing, prefix/suffix filters, no-filter match-all, multiple queues, region defaults, ARN validation, capitalized filter names, and compound event expansion.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/config_test.rs -->
# sources/object-store/rustfs/crates/notify/src/rules/config_test.rs

## Purpose
Integration-style unit tests for XML bucket notification configuration, from S3 XML parsing through `BucketNotificationConfig` to `RulesMap` event/object matching.

## Important APIs, types, and functions
- Uses `BucketNotificationConfig::from_xml`, `RulesMap::has_subscriber`, and `RulesMap::match_rules`.
- Builds ARNs with `rustfs_targets::arn::{ARN, TargetID}` and XML strings with queue configurations.
- Covers direct `FilterRule` layout and `FilterRuleList` wrapper layout.

## Control flow
Each test creates XML, supplies current region and allowed ARN list, parses into config, inspects generated rules, and asserts event/key matching. Compound event tests verify `ObjectCreatedAll` expands to concrete create events. Multiple queue tests ensure distinct target IDs are preserved per pattern.

## State and persistence behavior
No persistent state. Tests use in-memory XML cursors and in-memory rule maps.

## Dependencies and integration points
Exercises `xml_config`, `BucketNotificationConfig`, `RulesMap`, `pattern`, `EventName::expand/mask`, and `TargetID` ARN conversion together.

## Risks and edge cases
The URL-encoded key test documents that direct `RulesMap` matching of encoded spaces may or may not match; production encoded-key compensation happens in `NotifyRuleEngine`, not directly in `RulesMap`. Several tests print debug information, which can add noise but helps diagnose pattern generation.

## Test signals
Signals include expected matches for `uploads/*.csv`, prefix-only, suffix-only, no-filter match-all, specific event-only matching, capitalized filter names, multiple queues/targets, and compound event expansion excluding tagging events.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/config_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/mod.rs -->
# sources/object-store/rustfs/crates/notify/src/rules/mod.rs

## Purpose
Module hub for notification rule parsing, pattern matching, rule maps, subscriber snapshots, target ID sets, and XML configuration.

## Important APIs, types, and functions
- Declares private modules `config`, `pattern_rules`, `rules_map`, `subscriber_index`, `subscriber_snapshot`, and `target_id_set`.
- Public modules: `pattern` and `xml_config`.
- Test modules are included only under `cfg(test)`.
- Re-exports `BucketNotificationConfig`, `PatternRules`, `RulesMap`, subscriber index/snapshot types, `TargetIdSet`, `NotificationConfiguration`, and parse error aliases.

## Control flow
No runtime logic. It organizes module visibility and API exports.

## State and persistence behavior
No local state. Re-exported types manage in-memory rules and snapshots elsewhere.

## Dependencies and integration points
This is the import surface for `crate::rules::*` used by config manager, global helpers, notifier tests, rule engine, and bucket config manager.

## Risks and edge cases
Changing re-exports can break callers even when internal modules remain intact. `xml_config` is public while most rule internals are private, reflecting the expected external XML API.

## Test signals
Compilation of rule tests validates module wiring. No direct tests in this file.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/pattern.rs -->
# sources/object-store/rustfs/crates/notify/src/rules/pattern.rs

## Purpose
Builds and evaluates wildcard object-key patterns from S3 notification prefix/suffix filters.

## Important APIs, types, and functions
- `new_pattern(prefix, suffix)` appends `*` after a non-empty prefix when needed, prepends `*` before a non-empty suffix when needed, concatenates both, and collapses `**` to `*`.
- `match_simple(pattern_str, object_name)` matches using `wildmatch::WildMatch`, with explicit match-all handling for `"*"` and empty-pattern no-match behavior.

## Control flow
Pattern construction handles prefix, suffix, both, or neither. Matching short-circuits `"*"` to true and `""` to false, then delegates wildcard matching.

## State and persistence behavior
Stateless helper module. Patterns are stored later in `PatternRules`.

## Dependencies and integration points
Used by XML filter conversion, global rule helpers, `PatternRules`, and tests. Depends on the `wildmatch` crate.

## Risks and edge cases
`*` matches across slashes, which is relied on by tests for nested paths. Empty prefix/suffix combinations can produce an empty pattern, but `RulesMap::add_rule_config` normalizes empty patterns to `"*"`. Direct callers of `match_simple("", key)` get false.

## Test signals
Tests cover prefix/suffix combinations, duplicate-star collapse, match-all behavior, empty patterns, nested slash matching, and complex wildcard forms.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/pattern.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/pattern_rules.rs -->
# sources/object-store/rustfs/crates/notify/src/rules/pattern_rules.rs

## Purpose
Stores target subscriptions by object-key pattern for a single event and resolves object keys to target ID sets.

## Important APIs, types, and functions
- `PatternRules { rules: HashMap<String, TargetIdSet> }`.
- `add`, `match_simple`, `match_targets`, `is_empty`, `inner`, `contains_target_id`, and `remove_pattern`.
- Set operations: `union`, `difference`, `union_in_place`, `difference_in_place`.
- `match_targets` uses a serial path below `PAR_THRESHOLD` 128 and a rayon parallel fold/reduce path for large rule sets.

## Control flow
Rules are added by pattern and target ID. Matching iterates patterns, applies `pattern::match_simple`, and extends a result set with all matching targets. Difference operations remove matching target IDs per pattern and drop empty pattern entries.

## State and persistence behavior
In-memory, serde-serializable rule map. It is embedded in `RulesMap` and not persisted directly by this module.

## Dependencies and integration points
Uses `hashbrown`, `rayon`, `TargetID`, `TargetIdSet`, and `pattern`. Called by `RulesMap` for event-specific matching and merging/removal.

## Risks and edge cases
The parallel path only helps large rule maps and depends on `TargetID` hashing/clone costs. Wildcard matching semantics come from `wildmatch`; because `*` matches slashes, prefix filters include nested subpaths. Difference behavior removes target IDs, not entire patterns unless their set becomes empty.

## Test signals
Tests in `pattern_rules_test.rs` cover basic matching, multiple patterns/targets, prefix/suffix bug scenarios, match-all, empty rules, union/difference, removal, and target containment.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/pattern_rules.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/pattern_rules_test.rs -->
# sources/object-store/rustfs/crates/notify/src/rules/pattern_rules_test.rs

## Purpose
Comprehensive tests for `PatternRules` and `RulesMap` matching, set operations, event expansion, and target containment.

## Important APIs, types, and functions
- Pattern tests call `PatternRules::add`, `match_simple`, `match_targets`, `union`, `difference`, and `remove_pattern`.
- Rules map tests call `RulesMap::add_rule_config`, `has_subscriber`, `match_rules`, `remove_map`, and `contains_target_id`.
- Uses `EventName` compound and concrete variants plus `TargetID`.

## Control flow
The tests construct small rule maps by hand and assert matching outcomes for keys/events. Compound event tests add `ObjectCreatedAll` and then match concrete create events. Removal tests compare maps with same or different target IDs to verify difference semantics.

## State and persistence behavior
No persisted state; all maps and target IDs are local to tests.

## Dependencies and integration points
Validates the lower-level rules data structures used by `BucketNotificationConfig` and `NotifyRuleEngine`.

## Risks and edge cases
The tests encode the expectation that wildcard `*` matches nested paths and that empty filter strings become match-all only when passed through `RulesMap::add_rule_config`. They do not exercise the rayon branch because rule counts are small.

## Test signals
Signals include exact target membership, empty/non-empty target sets, event-specific routing, object-created compound expansion, and correct removal when the same target/pattern exists in another map.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/pattern_rules_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/pattern_test.rs -->
# sources/object-store/rustfs/crates/notify/src/rules/pattern_test.rs

## Purpose
Focused bug-reproduction and edge-case tests for prefix/suffix pattern construction and wildcard matching.

## Important APIs, types, and functions
- Tests `pattern::new_pattern` and `pattern::match_simple`.
- Covers prefix-only, suffix-only, prefix+suffix, empty pattern, complex paths, multiple slashes, and wildcard behavior.

## Control flow
Each test builds a pattern from prefix/suffix inputs or uses a literal pattern, then asserts matching and non-matching object keys.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Validates the primitive pattern helper used by XML filter parsing, global rule helpers, `PatternRules`, and `RulesMap`.

## Risks and edge cases
The tests intentionally confirm `*` spans slashes, so nested object keys match prefix/suffix rules. Empty pattern remains no-match at this helper layer, which differs from the match-all normalization in `RulesMap`.

## Test signals
Expected signals are exact generated pattern strings such as `uploads/*.csv`, positive nested matches, negative wrong-prefix/wrong-suffix matches, and match-all behavior for `"*"`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/pattern_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/rules_map.rs -->
# sources/object-store/rustfs/crates/notify/src/rules/rules_map.rs

## Purpose
Organizes notification rules by `EventName`, expands compound event subscriptions, and provides fast event-mask checks plus precise object-key matching.

## Important APIs, types, and functions
- `RulesMap { map: HashMap<EventName, PatternRules>, total_events_mask: u64 }`.
- `add_rule_config` normalizes empty pattern to `"*"`, expands compound events via `EventName::expand`, inserts pattern/target rules, and updates the mask.
- `add_map`, `remove_map`, `remove_rule`, `remove_rules`, and `update_rule` support map mutations.
- `has_subscriber` uses the total mask.
- `match_rules` returns targets for a concrete event/key.
- `contains_target_id`, `inner`, `is_empty`, and `iter_events` expose inspection.

## Control flow
Rules are stored under concrete expanded event names. Matching first checks the event mask, then looks up the concrete event and delegates to `PatternRules::match_targets`. Removal recalculates the mask to avoid stale subscriber bits.

## State and persistence behavior
In-memory and serde-serializable. It is stored inside `BucketNotificationConfig` and in `NotifyRuleEngine` bucket maps.

## Dependencies and integration points
Uses `PatternRules`, `TargetIdSet`, `EventName`, `TargetID`, `hashbrown`, and serde. It is central to dispatch matching and subscriber snapshot compilation.

## Risks and edge cases
`has_subscriber(ObjectCreatedAll)` returns true if any object-created bit is present, which is useful as a broad mask check but not equivalent to all concrete events being configured. `match_rules` expects concrete event names after expansion; callers using compound events directly may get no precise pattern map entry.

## Test signals
Tests cover basic routing, compound expansion, prefix/suffix bug flow, multiple patterns, prefix-only, suffix-only, no-filter match-all, different event types, map removal, and target containment.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/rules_map.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/subscriber_index.rs -->
# sources/object-store/rustfs/crates/notify/src/rules/subscriber_index.rs

## Purpose
Provides a concurrent bucket-to-snapshot index for fast subscriber checks with atomic whole-snapshot replacement.

## Important APIs, types, and functions
- `SubscriberIndex` holds `ShardedHashMap<String, Arc<ArcSwap<BucketRulesSnapshot<DynRulesContainer>>>>` plus a cached empty rules container.
- `new` accepts the empty rules container.
- `load_snapshot` returns the current snapshot or an empty snapshot.
- `has_subscriber` checks the snapshot event mask.
- `store_snapshot` creates or updates an `ArcSwap` cell for a bucket.
- `clear_bucket` replaces an existing bucket cell with an empty snapshot.
- `Default` builds a minimal empty rules container.

## Control flow
Writers compile a complete snapshot first and call `store_snapshot`, which swaps it atomically. Readers call `load_snapshot` and then inspect mask bits without observing intermediate state.

## State and persistence behavior
All state is in-memory. `clear_bucket` leaves the bucket cell present but with an empty snapshot.

## Dependencies and integration points
Uses `arc_swap`, `starshard::ShardedHashMap`, `BucketRulesSnapshot`, `DynRulesContainer`, and `EventName`. Wrapped by `NotificationSystemSubscriberView`.

## Risks and edge cases
The default missing-bucket path allocates a new empty snapshot each read, though it reuses the empty rules container. Bucket cells are not removed on clear, so many created/cleared buckets may leave empty cells.

## Test signals
No direct tests in this file. Behavior is exercised through subscriber view and bucket config manager usage.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/subscriber_index.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/subscriber_snapshot.rs -->
# sources/object-store/rustfs/crates/notify/src/rules/subscriber_snapshot.rs

## Purpose
Defines generic snapshot traits and the immutable bucket subscriber snapshot used by `SubscriberIndex`.

## Important APIs, types, and functions
- `RuleEvents` exposes subscribed event names.
- `RulesContainer` exposes an iterator over rules and a default `is_empty`.
- `BucketRulesSnapshot<R>` stores `event_mask` and `Arc<R>`.
- Methods: `empty`, `has_event`, `is_empty`, and `debug_assert_mask_consistent`.
- Type aliases: `DynRulesContainer` and `BucketSnapshotRef`.

## Control flow
Snapshot consumers check `event_mask` for fast event filtering. Debug builds can recompute the mask from rule event lists and assert consistency.

## State and persistence behavior
Snapshots are immutable in-memory values shared through `Arc`; replacement is handled by `SubscriberIndex`.

## Dependencies and integration points
Uses `EventName` and `Arc`. Implemented by the compiled rules adapter in `rules/config.rs` and used by subscriber view/index.

## Risks and edge cases
`is_empty` returns true if the mask is zero or the rules container is empty. If mask and rules diverge in release builds, the debug assertion would not run and subscriber checks may be wrong.

## Test signals
No direct tests. `NotificationSystemSubscriberView::apply_bucket_config` calls `debug_assert_mask_consistent`, and higher-level tests exercise subscriber behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/subscriber_snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/target_id_set.rs -->
# sources/object-store/rustfs/crates/notify/src/rules/target_id_set.rs

## Purpose
Defines the target-ID set type used throughout notification rule matching.

## Important APIs, types, and functions
- `pub type TargetIdSet = HashSet<TargetID>`.
- `new_target_id_set` converts a vector of target IDs into a set; it is crate-private and currently allowed dead code.

## Control flow
No significant logic beyond vector-to-set collection.

## State and persistence behavior
No owned state; the type alias is used inside rule maps and pattern rules.

## Dependencies and integration points
Uses `hashbrown::HashSet` and `rustfs_targets::arn::TargetID`. Used by `PatternRules`, `RulesMap`, and `NotifyRuleEngine`.

## Risks and edge cases
Set ordering is nondeterministic, so tests that collect into vectors must account for order unless only one target is present. The helper is unused, indicating either planned Go-style API compatibility or leftover scaffolding.

## Test signals
Indirectly covered by rule matching tests that assert target membership and set lengths.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/target_id_set.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/xml_config.rs -->
# sources/object-store/rustfs/crates/notify/src/rules/xml_config.rs

## Purpose
Parses, serializes, defaults, and validates S3 bucket notification XML configuration for queue targets.

## Important APIs, types, and functions
- `ParseConfigError` covers XML, filter, duplicate event/filter/queue, unsupported config type, ARN/target parsing, region, validation, and I/O errors.
- `FilterRule::validate` accepts only prefix/suffix and rejects `.`/`..` path segments, overlong values, backslashes, and invalid UTF-8.
- `S3KeyFilter` validates duplicate prefix/suffix rules and builds wildcard patterns.
- Custom `Deserialize` for `S3KeyFilter` handles `<Filter><S3Key><FilterRule>...` and `<FilterRuleList>` forms.
- `QueueConfig` validates events, duplicate events, filters, region, and ARN presence.
- `NotificationConfiguration` parses XML, rejects Lambda/Topic configs, validates duplicate queues, and fills default regions/xmlns.

## Control flow
`NotificationConfiguration::from_reader` deserializes XML with `quick_xml`. `set_defaults` fills missing queue ARN region and XML namespace. `validate` rejects unsupported lambda/topic entries, validates each queue, and checks duplicate `(Id, ARN)` pairs. `BucketNotificationConfig::from_xml` then consumes these validated queue configs.

## State and persistence behavior
The structs are serializable/deserializable data models. No persistence is performed here.

## Dependencies and integration points
Uses `quick_xml`, serde, `EventName`, `rustfs_targets::arn::{ARN, ArnError, TargetIDError}`, `hashbrown::HashSet`, and the local `pattern` helper. It is the XML front door for bucket notification configuration.

## Risks and edge cases
Lambda and Topic configs are explicitly unsupported even though structs exist for partial parsing. Duplicate queue detection uses `(Id, ARN)`, so identical ARN with different IDs is allowed. ARN validation requires callers to provide the current active ARN list. Unknown XML fields inside `S3Key` produce deserialization errors.

## Test signals
Covered by `config_test.rs`, which validates direct and wrapped filter rules, region defaulting, allowed ARN checks, prefix/suffix matching, capitalized filter names, and compound event expansion.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/rules/xml_config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/runtime_facade.rs -->
# sources/object-store/rustfs/crates/notify/src/runtime_facade.rs

## Purpose
Encapsulates target runtime activation, replay worker management, target replacement, and shutdown behind the generic `rustfs_targets` runtime adapter.

## Important APIs, types, and functions
- `NotifyRuntimeFacade` holds shared target list, replay worker manager, and a `PluginRuntimeAdapter<Event>`.
- `new` constructs a `BuiltinPluginRuntimeAdapter` with replay event callbacks, replay-start logging, concurrency limiting, poll/retry durations, and shutdown reason.
- `activate_targets_with_replay` initializes targets and replay workers.
- `replace_targets` commits a `RuntimeActivation` into target runtime and replay workers.
- `stop_replay_workers` and `shutdown` stop replay processing and close targets.

## Control flow
Activation is delegated to the runtime adapter. Replacement locks `replay_workers` before `target_list` and asks the adapter to replace runtime targets. Shutdown logs lifecycle state, observes active replay workers, locks in the same order, calls adapter shutdown, logs errors, sleeps briefly, and logs stopped.

## State and persistence behavior
Runtime facade manages in-memory target runtime state and replay worker handles. Replay workers may drain persisted target stores, but persistence is implemented by target/store types. Replay event callbacks update notification metrics and record final target failures for dropped/permanent/exhausted events.

## Dependencies and integration points
Uses `rustfs_targets::{BuiltinPluginRuntimeAdapter, PluginRuntimeAdapter, ReplayEvent, ReplayWorkerManager, RuntimeActivation, Target}`, notification metrics, `SharedNotifyTargetList`, semaphores, and tracing.

## Risks and edge cases
Lock ordering is explicitly documented as replay workers then target list; violating it elsewhere can deadlock. Shutdown is best-effort and logs adapter errors rather than returning them. Replay callback only increments processed for delivered events and failed for final failure classes; retryable/unreadable events do not change aggregate counters.

## Test signals
Tests verify empty replay worker stopping, empty activation, and replacement committing a runtime target visible through `NotifyRuntimeView` with no replay workers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/runtime_facade.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/runtime_view.rs -->
# sources/object-store/rustfs/crates/notify/src/runtime_view.rs

## Purpose
Provides read-only views of runtime targets, per-target metrics, target health, and combined runtime/replay status.

## Important APIs, types, and functions
- `NotifyRuntimeView` holds shared target list and replay worker manager.
- `get_active_targets`, `get_all_targets`, and `get_target_values` expose runtime target IDs/handles.
- `snapshot_target_metrics` converts target runtime snapshots into `NotificationTargetMetricSnapshot`.
- `snapshot_target_health` returns `RuntimeTargetHealthSnapshot` values.
- `runtime_status_snapshot` combines target runtime and replay worker status.

## Control flow
Each method reads the relevant lock and delegates to `TargetList`/target runtime methods. Status snapshot reads replay workers and target list together.

## State and persistence behavior
No mutation. It observes in-memory target runtime state and replay workers. Target queue lengths and delivery counts come from target runtime snapshots.

## Dependencies and integration points
Used by `NotificationSystem` facade and runtime facade tests. Depends on `TargetList`, `ReplayWorkerManager`, `TargetID`, `SharedTarget<Event>`, and rustfs-targets runtime snapshot types.

## Risks and edge cases
`get_active_targets` currently returns all target IDs in the runtime list; disabled/inactive health is visible only through health snapshots. Snapshot order follows target runtime ordering and should not be assumed unless the runtime manager guarantees sorting.

## Test signals
Tests cover empty queries/snapshots and a non-empty runtime with online and disabled targets, asserting target IDs, delivery metrics, health state, and runtime status counts.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/runtime_view.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/services.rs -->
# sources/object-store/rustfs/crates/notify/src/services.rs

## Purpose
Aggregates the notification subsystem's service facades into one cloneable struct used by `NotificationSystem`.

## Important APIs, types, and functions
- `NotifyServices` fields: `bucket_config_manager`, `config_manager`, `pipeline`, `runtime_facade`, `runtime_view`, and `status_view`.
- `NotifyServices::new` wires shared dependencies into each facade.

## Control flow
The constructor receives already-created shared dependencies from `NotificationSystem::new`, builds runtime view/facade over the shared target list and replay workers, builds config manager over shared config/registry/rule engine/runtime facade, builds bucket config manager over notifier/rule engine/subscriber view, builds pipeline over notifier/live events, and builds status view over metrics.

## State and persistence behavior
The struct owns cloneable service handles; state is in the shared Arcs passed in. Persistence remains in config manager, and runtime state remains in target list/replay workers.

## Dependencies and integration points
It is the composition layer between `NotificationSystem` and lower services. Depends on notification metrics, registry, rule engine, target list, replay workers, broadcast channel, live history, and subscriber view.

## Risks and edge cases
The constructor has many arguments, so dependency ordering mistakes are possible; clippy's too-many-arguments lint is explicitly allowed. All services sharing the same `NotifyRuleEngine` clone is critical for dispatch/subscriber consistency.

## Test signals
A unit test builds services with empty dependencies and asserts the runtime view is empty and status metrics start at zero.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/services.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/status_view.rs -->
# sources/object-store/rustfs/crates/notify/src/status_view.rs

## Purpose
Provides aggregate status and metric snapshots for the notification system.

## Important APIs, types, and functions
- `NotifyStatusView` wraps `Arc<NotificationMetrics>`.
- `get_status` returns a string map with uptime, processing, processed, failed, and skipped event counts.
- `snapshot_metrics` returns the typed `NotificationMetricSnapshot`.

## Control flow
Methods read atomic counters from `NotificationMetrics` and format them for status callers or Prometheus collection paths.

## State and persistence behavior
No owned mutable state beyond the shared metrics reference. Metrics are in-memory process counters.

## Dependencies and integration points
Used by `NotificationSystem::get_status`, `snapshot_metrics`, and `Drop` logging/metrics emission. Depends on `hashbrown::HashMap` and `NotificationMetrics`.

## Risks and edge cases
The status map values are strings, so typed consumers should prefer `snapshot_metrics`. Uptime changes continuously, making exact tests inappropriate.

## Test signals
Tests verify an empty metrics snapshot has zero counters and that the status map exposes all expected keys.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/status_view.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/Cargo.toml -->
# sources/object-store/rustfs/crates/object-capacity/Cargo.toml

## Purpose
Package manifest for the RustFS object-capacity crate, which provides capacity scan and refresh core functionality.

## Important APIs, types, and functions
- Package metadata uses workspace version, edition, license, repository, rust version, and homepage.
- Library doctests are disabled.
- Criterion benchmark `capacity_scan` is configured with `harness = false`.
- Dependencies include RustFS config/constants, I/O metrics, utilities, futures, tokio sync/time, tracing, uuid, and walkdir.
- Dev dependencies include criterion, serial_test, temp-env, tempfile, and tokio test-util.

## Control flow
Cargo uses this manifest to compile the library and opt-in benchmark target. There is no application control flow.

## State and persistence behavior
No runtime state. Dependency choices indicate the crate scans filesystem paths, emits metrics/logs, and uses async coordination.

## Dependencies and integration points
The crate integrates with workspace RustFS config and metrics crates and uses `walkdir` for filesystem traversal. The benchmark in `benches/capacity_scan.rs` depends on the bench target declared here.

## Risks and edge cases
Workspace dependency versions/features control behavior; enabling only tokio `sync` and `time` in normal dependencies means code needing filesystem or runtime features must get them elsewhere or under dev features. `harness = false` is required for Criterion benchmarks.

## Test signals
Manifest-level signal is successful cargo metadata/build/bench discovery. No direct tests are defined in this file.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/benches/capacity_scan.rs -->
# sources/object-store/rustfs/crates/object-capacity/benches/capacity_scan.rs

## Purpose
Criterion benchmark for `scan_used_capacity_disks`, measuring exact single-disk scans, sampled large scans, and mixed multi-disk scans using temporary filesystem fixtures.

## Important APIs, types, and functions
- Constants define exact file size (4 KiB), sampled file size (1 byte), and sampling trigger file count (202,048).
- `DiskSpec` describes fixture file count and size.
- `CapacityScanFixture` owns temp dirs and `CapacityDiskRef` entries.
- `populate_files` creates sharded bucket directories and object files with fixed payloads.
- `bench_capacity_scan` builds a current-thread tokio runtime, creates fixtures, and registers Criterion groups.
- Bench target uses `criterion_group!` and `criterion_main!`.

## Control flow
Fixture construction creates temp directories, populates files, and records drive paths. The benchmark creates one exact 10k-file fixture, one sampled 202k-file fixture, and one four-disk mixed fixture. Each Criterion bench blocks on `scan_used_capacity_disks`, black-boxing disk refs and summaries.

## State and persistence behavior
State is temporary filesystem content under `TempDir`; directories remain alive for the fixture lifetime through `_dirs`. No repository or production state is modified. The sampled fixture intentionally creates many tiny files to cross the scanner's sampling threshold.

## Dependencies and integration points
Depends on `rustfs_object_capacity::{CapacityDiskRef, scan_used_capacity_disks}`, Criterion, Tokio runtime, `tempfile`, standard filesystem APIs, and `black_box`.

## Risks and edge cases
The benchmark creates over 200k files, so setup can be slow and filesystem-dependent. Results will vary by storage backend, directory entry caching, and OS. The sharding formula clamps bucket directory count between 1 and 256, giving broad directory coverage without one file per directory.

## Test signals
Criterion output provides performance timing for `capacity_scan_exact/single_disk_10k_4k`, `capacity_scan_sampled/single_disk_202k_1b`, and `capacity_scan_multi_disk/four_disks_mixed_exact`. Successful benchmark setup also validates scanner compatibility with multiple temp disk roots.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/benches/capacity_scan.rs -->

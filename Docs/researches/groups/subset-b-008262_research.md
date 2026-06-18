# Research: subset-b-008262

This grouped report covers the requested heal and IAM files. Each section is wrapped with the exact source-path markers expected by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/storage.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/storage.rs

## Purpose
`storage.rs` defines the heal crate's storage abstraction and the `ECStore`-backed implementation used by heal tasks. It converts high-level heal operations into `rustfs_ecstore` object, bucket, format, listing, and admin calls while normalizing errors into `rustfs_heal::Error` and adding structured tracing.

## Important APIs, Types, and Functions
`DiskStatus` is a broad enum for disk health states, although the current `get_disk_status` implementation is still a placeholder returning `Ok`. `HealStorageAPI` is the async trait consumed by `HealTask`, `ErasureSetHealer`, tests, and manager paths. It exposes metadata/data read-write methods, object integrity checks, EC rebuild, disk formatting/status, bucket metadata repair, paged and full object listing, direct `heal_object`, `heal_bucket`, `heal_format`, and resume disk lookup.

`ECStoreHealStorage` wraps `Arc<ECStore>`. Key implementation details include `get_object_meta` mapping object-not-found to `Ok(None)`, `get_object_data` reading via `get_object_reader` with a 16 MiB safety cap, `verify_object_integrity` stream-copying to `tokio::io::sink`, and `object_exists` setting `ObjectOptions { no_lock: true }` so background heal scheduling avoids an extra namespace read lock. `is_transient_object_exists_message` and `is_transient_object_exists_error` classify quorum, lock, timeout, cancellation, slowdown, and transport failures as transient skips.

## Control Flow
Most methods log start, invoke one `ECStore` operation, then translate `Ok`, not-found, transient, and hard-failure cases. `ec_decode_rebuild` is two-stage: run `heal_object` with deep recreate/update parity, then read the healed object data. `list_objects_for_heal` loops over `list_objects_for_heal_page`; the page method calls `list_objects_v2` with `MAX_KEYS = 1000`. `get_disk_for_resume` parses `pool_N_set_M`, calls `StorageAdminApi::disk_set_inventory`, flattens the returned disk list, and returns the first available `DiskStore`.

## State and Persistence
The struct itself persists no mutable state beyond the `Arc<ECStore>`. Durable effects are delegated to ECStore: object writes/deletes, format healing, bucket healing, and reconstructed shards/metadata. The full-listing helper can accumulate all object names in memory; the paged API is the safer primitive for large buckets.

## Dependencies and Integration Points
This file sits between `heal::task` and `rustfs_ecstore`. It depends on `rustfs_common::heal_channel::{HealOpts, HealScanMode}`, `rustfs_madmin::heal_commands::HealResultItem`, `rustfs_storage_api::{BucketInfo, DiskSetSelector, StorageAdminApi}`, `tokio::io`, and `tracing`. `get_disk_for_resume` depends on `heal::utils::parse_set_disk_id`, so canonical disk identifiers must remain compatible across event, task, and resume code.

## Risks and Test Signals
Known risks are the placeholder disk status, the 16 MiB cap in `get_object_data` conflicting with large-object callers, memory-heavy `list_objects_for_heal`, and string-based transient classification. The inline tests cover transient object-exists detection for lock/quorum failures and ensure object-not-found is not treated as transient. Integration tests exercise object, bucket, and format healing through this implementation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/storage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/task.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/task.rs

## Purpose
`task.rs` implements heal work units. It models heal request types, priorities, options, status, in-memory progress/result state, cancellation, timeout handling, metrics, and the concrete execution paths for object, bucket, metadata, MRF, EC decode, and erasure-set healing.

## Important APIs, Types, and Functions
`HealType` covers `Object`, `Bucket`, `ErasureSet`, `Metadata`, `MRF`, and `ECDecode`. `HealPriority` orders work from low through urgent. `HealOptions` bridges task-facing options to `HealOpts` and carries timeout plus optional pool/set selectors. `HealTaskStatus` records pending/running/completed/failed/cancelled/timeout states. `HealRequest` adds id generation, priority, `force_start`, and queue timestamps; helper constructors set expected priorities for object, bucket, metadata, and EC decode requests.

`HealTask` owns shared status/progress/result-item locks, creation/enqueue/start/complete timestamps, a monotonic start instant for timeout math, a `CancellationToken`, and an `Arc<dyn HealStorageAPI>`. Public methods include `from_request`, metric label helpers, `execute`, `cancel`, `get_status`, `get_progress`, and `get_result_items`.

## Control Flow
`execute` atomically marks the task running, records queue-delay and task-start metrics, dispatches by `HealType`, then marks completed, cancelled, timeout, or failed. `await_with_control` wraps storage futures with cancellation and optional remaining timeout. Object healing prechecks existence, skips transient existence errors as completed skip work, optionally recreates missing objects, calls storage `heal_object`, treats not-found during delete-like races as deleted, optionally deletes corrupted objects when `remove_corrupted` and not dry-run, records result items, and updates progress. Bucket healing verifies bucket existence, calls `heal_bucket`, then optionally calls `heal_bucket_objects`, which pages object listings and heals each object. Metadata, MRF, and EC decode are focused variants of object heal with different `HealOpts`. Erasure-set healing optionally lists all buckets, heals format, resolves a resume disk, does a bucket prepass, constructs `ErasureSetHealer`, and runs resumable set healing.

## State and Persistence
Task state is in-memory behind `tokio::sync::RwLock`; persistent effects are delegated to `HealStorageAPI` and the erasure-set healer. `result_items` retains `HealResultItem`s for caller inspection. Timestamps support observability and timeout status, but no task record is persisted by this file.

## Dependencies and Integration Points
The file integrates `HealProgress`, `HealStorageAPI`, `ErasureSetHealer`, `rustfs_common::heal_channel::HealOpts`, `DATA_USAGE_CACHE_NAME`, ECStore metadata constants, `metrics`, `tracing`, `uuid`, and `tokio_util::CancellationToken`. It is the main consumer of `storage.rs` and hands resumable work to the erasure-set healing subsystem.

## Risks and Test Signals
The logic relies on string matching for not-found and transient data-usage-cache lock errors. Some progress calls use different totals across object paths, which consumers must interpret carefully. Recursive bucket healing is sequential and can run long on large buckets, though it checks cancellation before listings and per object. Inline tests use a `MockStorage` to verify recursive object visits, bucket-metadata remove suppression, and data-usage-cache transient skips. External bug-fix tests verify transient object-exists skip avoids recreate and status creation is stable.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/task.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/utils.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/utils.rs

## Purpose
`utils.rs` centralizes formatting, normalization, and parsing of heal set disk identifiers. The canonical string format is `pool_<pool_idx>_set_<set_idx>`, and compact external input like `3_5` can be normalized into the canonical form.

## Important APIs, Types, and Functions
`format_set_disk_id` formats unsigned pool and set indexes. `format_set_disk_id_from_i32` accepts signed endpoint indexes and returns `None` for negative values, preventing invalid endpoint metadata from being converted into heal work. `normalize_set_disk_id` returns canonical identifiers unchanged and converts compact `pool_set` numbers through `parse_compact_set_disk_id`. `parse_set_disk_id` validates the canonical four-token shape and returns `(usize, usize)` or `Error::TaskExecutionFailed` with a targeted message.

## Control Flow
The helpers are deliberately small and deterministic. Normalization first detects an existing `pool_` prefix; otherwise it attempts a compact split on `_` and parses both sides as `usize`. Parsing enforces exact token names and count before numeric conversion, which means malformed names fail before storage resume disk inventory is attempted.

## State, Dependencies, and Integration
There is no mutable state or persistence. The only dependency is the heal crate `Error`/`Result`. `storage.rs` uses `parse_set_disk_id` in `get_disk_for_resume`, while event conversion and tests depend on `format_set_disk_id_from_i32` to guard negative endpoint indexes.

## Risks and Test Signals
`normalize_set_disk_id` accepts any string beginning with `pool_` without validating the full canonical form, so callers that need validated indexes must still call `parse_set_disk_id`. Unit tests cover unsigned formatting, signed negative rejection, compact normalization, prefixed pass-through, invalid compact input, canonical parsing, and invalid canonical errors.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/lib.rs -->
# sources/object-store/rustfs/crates/heal/src/lib.rs

## Purpose
The heal crate root exposes public heal APIs, initializes global heal runtime singletons, and provides process-wide cancellation and observability counters for active heal work. It is the entry point other crates use to configure and access `HealManager` and the heal-channel processor.

## Important APIs, Types, and Functions
The module exports `Error`, `Result`, `HealManager`, `HealOptions`, `HealPriority`, `HealRequest`, `HealType`, and `HealChannelProcessor`. `init_ahm_services_cancel_token`, `get_ahm_services_cancel_token`, `create_ahm_services_cancel_token`, and `shutdown_ahm_services` manage a `OnceLock<CancellationToken>`. `init_heal_manager` creates and starts a `HealManager`, stores it in `GLOBAL_HEAL_MANAGER`, initializes the common heal channel, stores a mutex-protected `HealChannelProcessor`, and spawns the processor in the background. `get_heal_manager`, `get_heal_channel_processor`, `current_heal_active_tasks`, `current_heal_queue_length`, and crate-private setters expose global runtime state.

## Control Flow
Initialization is strict and one-shot. `init_heal_manager` starts the manager before publishing it, initializes the channel receiver, stores the processor singleton, then spawns a background async task that locks the processor and calls `start(receiver)`. Failures during singleton setup map to configuration errors; failures inside the spawned processor are logged rather than returned.

## State and Persistence
All state is process-local: two `OnceLock` singleton references, one cancellation token, and two relaxed atomics. Persistent heal effects occur downstream in storage/task code, not here.

## Dependencies and Integration Points
This file ties `rustfs_common::heal_channel` to the heal manager and accepts any `Arc<dyn heal::storage::HealStorageAPI>`. It depends on `tokio`, `tokio_util`, `Arc`, `OnceLock`, atomics, and `tracing`. Other runtime modules call the getters to submit work or report gauges.

## Risks and Test Signals
The cancellation token creation helper panics if called after initialization because it uses `expect`; callers needing fallibility should use `init_ahm_services_cancel_token`. The background processor failure is only logged, so supervisors need log/metric monitoring. No tests are in this file; coverage comes indirectly through manager/channel integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/tests/endpoint_index_test.rs -->
# sources/object-store/rustfs/crates/heal/tests/endpoint_index_test.rs

## Purpose
This integration test validates that local ECStore endpoints carry valid pool, set, and disk indexes before store initialization. It specifically guards the endpoint metadata that later heal event conversion and set-disk-id formatting rely on.

## Important APIs and Flow
The test creates a temporary directory, four disk directories, converts each path into an `Endpoint`, sets `pool_idx = 0`, `set_idx = 0`, and a per-disk index, and constructs `PoolEndpoints` plus `EndpointServerPools`. It asserts each endpoint index is in range, calls `rustfs_ecstore::store::init_local_disks`, then builds an `ECStore` with a loopback ephemeral address and a new cancellation token.

## State and Persistence
All state is temporary filesystem state owned by `tempfile::TempDir`. The test formats local disk directories and initializes an `ECStore` but does not create buckets or objects.

## Dependencies and Integration Points
The test uses `rustfs_ecstore::disk::endpoint::Endpoint`, endpoint pool types, `TempDir`, `SocketAddr`, and `tokio_util::CancellationToken`. It supports heal utilities and event paths by confirming endpoint indexes can be explicitly set and survive pool construction.

## Risks and Test Signals
The test runs multi-threaded and performs real disk initialization, so filesystem permission and platform path behavior can affect it. It is a positive-path test only; invalid indexes are covered in `heal_bug_fixes_test.rs`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/tests/endpoint_index_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/tests/heal_bug_fixes_test.rs -->
# sources/object-store/rustfs/crates/heal/tests/heal_bug_fixes_test.rs

## Purpose
This regression test file captures known heal edge cases that previously risked panics, incorrect request construction, timestamp unwrap failures, or unsafe task transitions. It complements integration tests by using focused mock storage and simple unit-level assertions.

## Important Tests and APIs
The event tests cover `HealEvent::DiskStatusChange` with invalid negative endpoint indexes returning an error rather than panicking, valid endpoint indexes producing `HealType::ErasureSet`, object corruption mapping to high-priority object heal, and EC decode failures mapping to urgent `ECDecode`. Utility tests cover `format_set_disk_id_from_i32` for negative and valid values. Resume tests instantiate `ResumeState` and `ResumeCheckpoint` to verify timestamp creation paths are non-panicking. `test_heal_task_status_atomic_update` builds a full `HealStorageAPI` mock and confirms a new task begins pending. `test_heal_task_transient_object_exists_skip_avoids_recreate` verifies a transient existence-check error marks the task completed without calling `heal_object`.

## Control Flow and State
Most tests are synchronous unit tests. The async transient-skip test uses atomics to count `object_exists` and `heal_object` calls, then executes a real `HealTask` against a mock. This validates task state transitions and progress completion without touching disk.

## Dependencies and Integration Points
The file integrates `heal::event`, `heal::task`, `heal::utils`, `heal::resume`, `HealStorageAPI`, ECStore endpoint types, and `rustfs_common::heal_channel::HealOpts`. It is a cross-module bug-fix safety net rather than a single-module test.

## Risks and Test Signals
The mock implementations are broad and mostly no-op, so they verify control-flow intent but not ECStore behavior. The strongest signal is that transient object-exists failures no longer trigger recreate work, protecting background healing from lock/quorum race amplification.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/tests/heal_bug_fixes_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/tests/heal_integration_test.rs -->
# sources/object-store/rustfs/crates/heal/tests/heal_integration_test.rs

## Purpose
This serial integration suite validates heal storage and manager behavior against a real local four-disk ECStore. It intentionally damages bucket directories, format metadata, and object shard files, then verifies healing restores readability and expected on-disk files.

## Important Helpers and Tests
`setup_test_env` initializes tracing once, creates a shared `/tmp/rustfs_heal_heal_test_<uuid>` four-disk environment, sets endpoint indexes, formats disks, builds `ECStore` on `127.0.0.1:9001`, initializes bucket metadata, and wraps storage in `ECStoreHealStorage`. `non_inline_test_data` creates data larger than the inline threshold so tests manipulate real part files. `wait_for_path_exists` polls for async restoration.

The serial tests cover direct object heal after deleting one `part.*` shard, manager-submitted recursive bucket heal after deleting a bucket directory, format heal after deleting `format.json`, combined format/bucket/object healing after wiping one disk directory, and dry-run direct calls to `heal_format`, `heal_bucket`, and `heal_object`.

## Control Flow, State, and Persistence
The suite uses a `OnceLock` global environment to reuse expensive ECStore setup. Tests create real buckets and objects, remove filesystem paths with `std::fs`, call heal APIs, and read objects back through `get_object_reader` to prove data integrity. `serial_test::serial` prevents concurrent mutation of the shared disk set.

## Dependencies and Integration Points
The file exercises `ECStore`, endpoint pools, bucket/object operations, `ECStoreHealStorage`, `HealManager`, `HealRequest`, `HealOptions`, `HealOpts`, `walkdir`, `HeaderMap`, and Tokio filesystem/time APIs. It is the highest-value signal that `storage.rs` correctly delegates to ECStore.

## Risks and Test Signals
The hard-coded port `9001` can conflict with other local processes, and shared global state can cause bucket-name collisions if tests are rerun in a long-lived process. The tests are filesystem-heavy and time-bound, but they cover non-inline object data, format recovery, bucket recovery, and direct storage API contracts.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/tests/heal_integration_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/Cargo.toml -->
# sources/object-store/rustfs/crates/iam/Cargo.toml

## Purpose
This manifest defines the `rustfs-iam` crate: the Identity and Access Management component for RustFS. It declares workspace metadata, docs configuration, lint inheritance, runtime dependencies, dev dependencies, and disables doctests for the library target.

## Important Configuration
The package description positions the crate around user management, roles, and permissions. Dependencies include local RustFS crates for credentials, config, ECStore persistence, policy evaluation, crypto, admin models, utilities, and IO metrics. Third-party dependencies cover async traits, Tokio, time serialization, serde/JSON, `arc-swap`, futures, base64, JWTs, tracing, `moka`, `reqwest`, `openidconnect`, HTTP, and URL parsing. Dev dependencies include `serial_test` and `temp-env`.

## Integration Points
The manifest shows IAM is not a standalone policy-only crate: it persists through `rustfs-ecstore`, exposes/consumes policy types via `rustfs-policy`, handles credentials via `rustfs-credentials`, and supports OIDC discovery/client behavior through `openidconnect`, `reqwest`, `http`, and `url`. `arc-swap` is used by `cache.rs` for atomic snapshot publication.

## Risks and Test Signals
Because many dependencies are inherited from the workspace, version and feature compatibility are controlled outside this file. Disabling doctests avoids doc-example breakage but also removes one documentation validation path. The broad dependency set suggests IAM changes can affect storage, auth, OIDC, admin APIs, and crypto paths.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/cache.rs -->
# sources/object-store/rustfs/crates/iam/src/cache.rs

## Purpose
`cache.rs` implements IAM's in-memory cache as atomically published immutable snapshots. It lets readers observe a consistent `CacheState` while writers clone and replace only changed maps under a mutex, avoiding partial multi-map updates.

## Important APIs, Types, and Functions
`CacheState` groups policy docs, users, user policies, STS accounts/policies, groups, user-group memberships, and group policies. Each map is an `Arc<CacheEntity<T>>`, where `CacheEntity` wraps a `HashMap<String, T>` and `load_time`. `Cache` owns `ArcSwap<CacheState>` plus a `Mutex<()>` write lock. `snapshot` returns an `arc_swap::Guard`; `with_write_lock` clones current state, tracks the current pointer, runs a mutation closure on `LockedCache`, and stores a new state only if dirty.

`LockedCache` exposes replacement and add/update/delete helpers. `exec` ignores stale writes when the target entity's `load_time >= t`, then clones the entity and applies the mutation. `build_user_group_memberships` derives reverse user-to-group membership from `groups`. `CacheInner` is a read facade with `get_user` checking permanent users then STS accounts; policy authorization methods currently warn and deny/return empty.

## Control Flow and State
Readers load one snapshot and dereference all maps from that stable state. Writers serialize through the mutex and publish one new `Arc<CacheState>`, preserving snapshot consistency for concurrent readers. Replacement methods update load time to `now_utc`; add/delete methods rely on caller-supplied timestamps for stale-update suppression.

## Dependencies and Integration Points
The file depends on `arc-swap`, `rustfs_policy::{UserIdentity, Args, PolicyDoc}`, `time::OffsetDateTime`, `GroupInfo`, `MappedPolicy`, and `tracing`. It is consumed by IAM manager/sys code as the fast read path over persistent IAM objects.

## Risks and Test Signals
The authorization methods are TODOs that deny by default, so callers relying on `CacheInner::is_allowed` get conservative false results. Stale suppression is per-entity `load_time`, so a newer update to one key can block older but still valid changes to another key in the same entity. Tests cover concurrent add/update/delete behavior and prove old snapshots do not observe multi-map writes published after they were loaded.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/cache.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/error.rs -->
# sources/object-store/rustfs/crates/iam/src/error.rs

## Purpose
`error.rs` defines the IAM crate's canonical `Error` enum, `Result<T>` alias, conversion boundaries to policy/storage/IO/JSON/base64 errors, equality/clone behavior, and helper predicates used by callers to identify common IAM error classes.

## Important APIs and Types
`Error` includes transparent policy errors, string and crypto errors, missing user/account/service/temp/group/policy variants, policy-in-use/group-not-empty, invalid argument/service/action/token/access-key/secret-key/expiration states, credential initialization/malformed states, policy too large, config not found, IO, and already-initialized errors. `Error::other` wraps arbitrary errors into `Error::Io(std::io::Error::other(...))`.

Conversions preserve `ConfigNotFound` when crossing to/from `rustfs_ecstore::StorageError`, map each `rustfs_policy::error::Error` variant explicitly, and wrap serde/base64 errors into IO-other. `PartialEq` compares important payloads directly and otherwise falls back to discriminant plus display string. `Clone` preserves simple variants and converts non-cloneable complex variants into `StringError` or fresh IO errors.

## Control Flow and State
There is no runtime state. The file's control flow is conversion logic and helper predicates such as `is_err_config_not_found`, `is_err_no_such_policy`, `is_err_no_such_user`, `is_err_no_such_account`, `is_err_no_such_temp_account`, `is_err_no_such_group`, and `is_err_no_such_service_account`.

## Dependencies and Integration Points
This file binds IAM to `rustfs_policy`, `rustfs_crypto`, `jsonwebtoken`, `rustfs_ecstore`, `serde_json`, `base64-simd`, and standard IO errors. It is used across IAM store/manager/sys/OIDC code to keep external error semantics stable.

## Risks and Test Signals
Cloning `PolicyError`, `CryptoError`, and `JWTError` changes the variant to `StringError`, which can affect code that clones then pattern-matches. Converting IAM errors to `std::io::Error` always uses `ErrorKind::Other`, losing original IO kind except in the stored IAM variant before conversion. Tests cover IO conversion, storage and policy conversion, `other`, JSON conversion, helper predicates, IO preservation expectations, and display strings.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/keyring.rs -->
# sources/object-store/rustfs/crates/iam/src/keyring.rs

## Purpose
`keyring.rs` loads IAM encryption/decryption keys from environment variables and exposes the current encryption key plus ordered decryption keys for key rotation. It keeps the active key first and deduplicates old keys.

## Important APIs, Types, and Functions
`ENV_IAM_MASTER_KEY` and `ENV_IAM_MASTER_KEY_OLD_KEYS` define the environment contract. `Keyring` stores `current_key: Option<Vec<u8>>` and `decrypt_keys: Vec<Vec<u8>>`. `normalize_key` trims and drops empty strings. `parse_old_keys` parses a comma-separated list, trimming and skipping empty entries. `push_unique_key` preserves insertion order while deduplicating. `build_keyring` builds current plus old decrypt keys. Public functions are `encrypt_key`, `decrypt_keys`, and `current_key_and_old_keys`.

## Control Flow and State
There is no cached state; every public call reads environment variables via `rustfs_utils::get_env_opt_str` and rebuilds the keyring. If a current key exists, it is included as the first decryption key and returned as the encryption key. `current_key_and_old_keys` returns old keys excluding the current key when current exists; without current, all configured old keys are returned as old/decrypt-only keys.

## Dependencies and Integration Points
The module depends only on RustFS environment utility helpers. It is intended for IAM store crypto paths that need encrypt-current/decrypt-many semantics during master-key rotation.

## Risks and Test Signals
Keys are treated as raw UTF-8 bytes from environment strings; there is no length, entropy, or encoding validation here. Re-reading environment variables on every call keeps rotation responsive but can produce inconsistent key views if the environment changes mid-operation. Tests cover old-key parsing, current-then-old ordering, deduplication, and old-key-only operation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/keyring.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/lib.rs -->
# sources/object-store/rustfs/crates/iam/src/lib.rs

## Purpose
The IAM crate root declares public modules and owns global initialization/access for the process-wide IAM system and OIDC system. It wires ECStore-backed object storage into `IamCache` and then into `IamSys`.

## Important APIs, Types, and Functions
Public modules include `cache`, `error`, `keyring`, `manager`, `oidc`, `oidc_state`, `store`, `sys`, and `utils`. Two `OnceLock` singletons hold `Arc<IamSys<ObjectStore>>` and `Arc<OidcSys>`. `init_iam_sys` is the async initializer for IAM: it is idempotent if already initialized, creates an `ObjectStore` from `Arc<ECStore>`, awaits `IamCache::new` for initial load, constructs `IamSys`, and stores it. `get` returns the global IAM system or `IamSysNotInitialized`, with a defensive `is_ready` check. `get_global_iam_sys` returns an optional clone. `init_oidc_sys` initializes OIDC, treating missing/broken provider setup as non-fatal by installing an empty system. `get_oidc` returns the optional OIDC singleton.

## Control Flow and State
IAM initialization only publishes the singleton after storage adapter creation and cache loading complete. A racing second `set` returns `IamSysAlreadyInitialized`; an already-populated singleton at function entry returns `Ok(())`. OIDC initialization logs provider readiness when configured and logs warnings for non-fatal failures or singleton races.

## Dependencies and Integration Points
This file integrates `rustfs_ecstore::store::ECStore`, `store::object::ObjectStore`, `manager::IamCache`, `sys::IamSys`, `oidc::OidcSys`, crate `Error/Result`, and `tracing`. It is the runtime boundary other RustFS crates call before using IAM services.

## Risks and Test Signals
`OnceLock` means there is no built-in reset for tests or reconfiguration in the same process. OIDC init failures are intentionally non-fatal, which improves server startup but can hide provider misconfiguration unless logs are monitored. This file has no local tests; its behavior is covered indirectly by IAM manager/sys/OIDC integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/lib.rs -->

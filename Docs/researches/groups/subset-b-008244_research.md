# subset-b-008244 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/config/com.rs -->
# sources/object-store/rustfs/crates/ecstore/src/config/com.rs

## Purpose
This file is the ecstore server-config persistence and migration layer. It reads and writes metadata-bucket config objects, translates between RustFS internal `Config`/`KVS` maps and the external MinIO-style JSON object shape, migrates compatible legacy config from the migrating metadata bucket, and applies dynamic runtime config such as storage-class parity to globals. It is the main bridge between stored `.rustfs.sys/config/config.json`, admin config defaults, notification/audit/OIDC subsystem KVS, and runtime object-store initialization.

## Important APIs, types, and functions
Important public APIs are `read_config`, `read_config_no_lock`, `read_config_with_metadata`, `save_config`, `delete_config`, `save_config_with_opts`, `try_migrate_server_config`, `read_config_without_migrate`, `save_server_config`, and `lookup_configs`. `CONFIG_PREFIX`, `STORAGE_CLASS_SUB_SYS`, and `COMMA_SEPARATED_LISTS` define shared config naming behavior. `TargetConfigDescriptor` and the `notify_target_descriptors`/`audit_target_descriptors` tables map external target groups such as `notify.webhook` and `logger.kafka` onto concrete RustFS subsystem keys and default KVS lists. Private helpers decode storage class, OIDC, notify, and audit object shapes, render semantic external JSON, compare semantic equality, and detect standard object-server config.

## Control flow
Reads go through object-layer `get_object_reader` against `RUSTFS_META_BUCKET`, map not-found variants to `ConfigNotFound`, and reject empty config bodies. `read_config_without_migrate` reads `config/config.json` without a namespace lock, falls back to `handle_missing_config`, and merges decoded config defaults. Missing config is only persisted by the first local cluster node; other nodes build an in-memory default plus dynamic lookup. `try_migrate_server_config` first refuses to overwrite an existing RustFS config, then reads the same path from `MIGRATING_META_BUCKET`, decodes either internal or external-compatible data, normalizes it to object JSON, and saves it with max parity.

Serialization first attempts `Config::unmarshal`; on failure it parses external JSON and applies recognized storageclass, openid, notify, and logger/audit maps. Saves preserve existing unknown JSON top-level fields where possible, render `version`, `region`, `storageclass`, `openid`, `notify`, and `logger`, remove internal subsystem aliases, and skip writes if the current object is already standard and semantically unchanged. `lookup_configs` calls dynamic storage-class handling, deriving parity against each set drive count and updating `GLOBAL_STORAGE_CLASS` from the first set.

## State and persistence behavior
The persistent object is `config/config.json` in `RUSTFS_META_BUCKET`. Generic config writes use `max_parity`; migration reads and existence checks use `no_lock` to avoid boot-time lock fragility. The encoder intentionally preserves external JSON shape rather than writing raw internal KVS maps. Secret-like defaults rely on `hidden_if_empty` to suppress empty values in rendered target/OIDC objects, but non-empty secrets are still represented in persisted config. Dynamic storage-class state is copied into the process-global storage-class lock through `set_global_storage_class`; the stored config remains the source of truth.

## Dependencies and integration points
The file depends on `ObjectIO`, `ObjectOperations`, `StorageAdminApi`, `ObjectOptions`, and `PutObjReader` from the store API, metadata bucket constants from `disk`, subsystem constants/defaults from `rustfs_config`, and global cluster-node role detection. `config/mod.rs` calls `read_config_without_migrate`, `lookup_configs`, and `set_global_server_config` during startup. Admin config rendering and storage-class lookup depend on the internal KVS keys produced here. Notification, audit, and OIDC defaults come from sibling config modules.

## Risks and edge cases
The conversion logic is broad and is a compatibility boundary: changing key aliases, default merging, boolean normalization, hidden-empty handling, or instance-name detection can silently drop admin config. `parse_storage_class_value` supports both string and object parity shorthand, while target sections support shorthand default instances; both are easy to misclassify. Save idempotency depends on semantic equality that only compares storageclass, OIDC, notify, and audit, so future subsystems need explicit inclusion. Migration is best-effort and logs then skips on many errors, which is appropriate at boot but can hide bad legacy config. The `read_server_config` TODO for decryption means encrypted config support is incomplete in this path.

## Test signals
The embedded tests cover internal and external decode shapes, legacy `hiddenIfEmpty`, storageclass round trips, OIDC array and boolean conversion, notify/audit target decode and encode, shorthand target detection, semantic equality across legacy/external shapes, standard object-shape detection, and a distributed-lock read scenario where one locker is unhealthy. These tests strongly exercise config conversion and read-lock behavior. They do not cover actual migration from `MIGRATING_META_BUCKET`, encrypted config, multi-set dynamic storage-class errors beyond logging, or persistence races between nodes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/config/com.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/config/heal.rs -->
# sources/object-store/rustfs/crates/ecstore/src/config/heal.rs

## Purpose
This file defines the heal subsystem's default configuration and a small runtime config holder for bitrot/heal scanning. It is currently a lightweight companion to `config/mod.rs`, which registers `DEFAULT_KVS` under `HEAL_SUB_SYS` so admin config views expose the bitrot scan cycle default.

## Important APIs, types, and functions
`DEFAULT_KVS` contains one `KV` for `HEAL_BITROT_CYCLE` using `DEFAULT_HEAL_BITROT_CYCLE_SECS`. `Config` stores `bitrot`, `sleep`, `io_count`, `drive_workers`, and `cache`, with accessors `bitrot_scan_cycle`, `get_workers`, and `update`. The private `parse_bitrot_config` accepts boolean strings or month-suffixed values and returns a `Duration`.

## Control flow
The default path is simple: `config::init` registers `DEFAULT_KVS`, and callers can later build/update a `Config`. `parse_bitrot_config` first tries `parse_bool`; enabled maps to zero duration and disabled attempts to map to a negative seconds duration. If parsing as boolean fails, only strings ending in `m` are accepted and must be at least one month.

## State and persistence behavior
This file does not persist state directly. The only persisted representation is KVS data managed by the broader server-config system. Runtime `Config` values are plain struct state, and `update` copies selected fields from a new config without updating `cache`.

## Dependencies and integration points
It depends on `rustfs_config` heal constants, `server_config::KV/KVS`, `rustfs_utils::string::parse_bool`, and ecstore `Error/Result`. It is imported by `config/mod.rs` for default registration.

## Risks and edge cases
`Duration::from_secs_f64(-1.0)` will panic in Rust because `Duration` cannot be negative, so a disabled boolean value is a latent bug if `parse_bitrot_config` is used. The month-to-seconds calculation multiplies by `30 * 24 * 60`, which is minutes rather than seconds, likely undercounting by a factor of 60. The parser is private and currently untested, so these issues may remain dormant until wired into runtime config loading. `update` omits `cache`, which may be intentional but makes `bitrot_scan_cycle` stale after updates.

## Test signals
There are no local tests in this file. `config/mod.rs` has a default-registration test that verifies `HEAL_BITROT_CYCLE` is present with the default seconds value, but no tests exercise `Config` update behavior or `parse_bitrot_config`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/config/heal.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/config/mod.rs -->
# sources/object-store/rustfs/crates/ecstore/src/config/mod.rs

## Purpose
This module wires together ecstore configuration submodules, global config state, and startup initialization. It exposes storage-class globals, initializes server config from the object store, registers default KVS for storage class, scanner, heal, notify, audit, and OIDC subsystems, and delegates migration.

## Important APIs, types, and functions
The module exports `com`, `heal`, and `storageclass`, keeps `audit`, `notify`, `oidc`, and `scanner` private, and defines `GLOBAL_STORAGE_CLASS`, `GLOBAL_CONFIG_SYS`, and `RUSTFS_CONFIG_PREFIX`. `ConfigSys::init` reads config without migration, applies dynamic lookup, and installs the result via `set_global_server_config`. Public helpers include `get_global_storage_class`, `set_global_storage_class`, `init_global_config_sys`, `try_migrate_server_config`, and `init`.

## Control flow
Startup code calls `init` to build a `HashMap` of default KVS by subsystem and passes it to `register_default_kvs`. Later `init_global_config_sys` delegates to `ConfigSys::init`, which loads `config/config.json`, calls `lookup_configs` for dynamic values such as storage class, and sets the global server config. Migration is intentionally separate: `try_migrate_server_config` only forwards to `com::try_migrate_server_config`.

## State and persistence behavior
The module itself persists nothing. It coordinates two process-global states: the full server config inside `rustfs_config::server_config`, and the ecstore `GLOBAL_STORAGE_CLASS` `RwLock`. `get_global_storage_class` clones the current storage-class config on a successful read lock; `set_global_storage_class` silently skips the update if the lock is poisoned/unavailable.

## Dependencies and integration points
This file is the integration point for all config default providers in this folder and for constants in `rustfs_config::{notify,audit,oidc}`. `ECStore` is the object-store implementation passed into initialization. Storage-class data produced here influences object placement and inlining through other ecstore paths.

## Risks and edge cases
`init` is idempotent only to the extent `register_default_kvs` is idempotent; repeated registration semantics live outside this file. Silent lock failures in storage-class getters/setters avoid panics but can hide poisoned-lock problems. Because `notify`, `audit`, `oidc`, and `scanner` are private modules, external callers must go through central config registration rather than direct defaults. Default registration order matters if `register_default_kvs` treats duplicates specially.

## Test signals
Tests verify global server config round-tripping for storage-class KVS and default registration for scanner and heal. They confirm that `init` registers scanner speed/delay/max wait/cycle object defaults and the heal bitrot-cycle default. They do not run full `ConfigSys::init` against an `ECStore` or validate every notify/audit/OIDC default.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/config/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/config/notify.rs -->
# sources/object-store/rustfs/crates/ecstore/src/config/notify.rs

## Purpose
This file defines default notification target KVS for every supported event sink. It is data-heavy configuration scaffolding used by `config/mod.rs` and `config/com.rs` so admin config can render, parse, and persist notify targets consistently.

## Important APIs, types, and functions
The exported statics are `DEFAULT_NOTIFY_WEBHOOK_KVS`, `DEFAULT_NOTIFY_MQTT_KVS`, `DEFAULT_NOTIFY_AMQP_KVS`, `DEFAULT_NOTIFY_NATS_KVS`, `DEFAULT_NOTIFY_PULSAR_KVS`, `DEFAULT_NOTIFY_REDIS_KVS`, `DEFAULT_NOTIFY_POSTGRES_KVS`, `DEFAULT_NOTIFY_KAFKA_KVS`, and `DEFAULT_NOTIFY_MYSQL_KVS`. Each is a `LazyLock<KVS>` built from `KV` entries with a key, default string value, and `hidden_if_empty` flag.

## Control flow
There is no executable control flow beyond lazy initialization. `config::init` registers these defaults under `NOTIFY_*_SUB_SYS`. `config/com.rs` uses the same default KVS objects in target descriptors to merge default instances, decode external `notify` JSON, and omit unchanged/default values during external rendering.

## State and persistence behavior
The statics are immutable after initialization. Persisted notification config is stored as server-config KVS or rendered external JSON elsewhere. Defaults include queue directories and queue limits, disabled `enable` flags, target-specific booleans such as AMQP persistence, Kafka TLS/SASL, NATS TLS, Pulsar TLS validation, Redis TLS, and empty credential/TLS fields. Empty sensitive fields are usually marked `hidden_if_empty`, reducing empty secret noise in rendered output.

## Dependencies and integration points
The file depends entirely on constants from `rustfs_config` and `rustfs_config::notify`, plus `server_config::KV/KVS`. It integrates with admin config registration, server-config JSON conversion, and any event notification subsystem that consumes these KVS keys to build concrete clients.

## Risks and edge cases
Because this file is a schema-by-data contract, changing keys, defaults, or `hidden_if_empty` flags can break admin compatibility or alter runtime event target behavior. Some credential-like fields are hidden only when empty; non-empty secrets are still persisted and may render unless higher layers redact them. Defaults vary by backend, for example AMQP `persistent` defaults on, Kafka `acks` defaults to `1`, MySQL table defaults to `rustfs_events`, and Redis channel uses `NOTIFY_REDIS_DEFAULT_CHANNEL`; accidental normalization across backends would change semantics. There are no validators here, so malformed values are accepted until later client setup.

## Test signals
This file has no local tests. `config/com.rs` tests exercise several notify defaults indirectly through decode/encode cases for webhook, MQTT, Kafka, AMQP, and MySQL, including default-instance merging and boolean rendering. NATS, Pulsar, Redis, and Postgres defaults are not directly covered in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/config/notify.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/config/oidc.rs -->
# sources/object-store/rustfs/crates/ecstore/src/config/oidc.rs

## Purpose
This file defines the default KVS for OpenID Connect identity-provider settings. It provides the baseline admin/server-config schema for the `identity_openid` subsystem consumed by config registration and external JSON conversion.

## Important APIs, types, and functions
The only exported item is `DEFAULT_IDENTITY_OPENID_KVS`, a `LazyLock<KVS>`. It includes enable state, discovery/config URL, client ID/secret, scopes, other audiences, redirect URI behavior, claim naming/prefixing, role policy, display name, groups/roles/email/username claim keys, and default claim values from `rustfs_config::oidc`.

## Control flow
There is no runtime algorithm in this file. `config::init` registers the default KVS under `IDENTITY_OPENID_SUB_SYS`. `config/com.rs` clones these defaults when decoding named OIDC providers, normalizes booleans and comma-separated list values, and renders providers only when a config URL is present.

## State and persistence behavior
The KVS is static process data. Actual OIDC provider instances are persisted in server config and may be stored as internal `identity_openid` KVS or external `openid` JSON. `OIDC_CLIENT_SECRET` is marked `hidden_if_empty`, preventing empty secret fields from being rendered, but non-empty secrets remain part of config data.

## Dependencies and integration points
The file depends on `rustfs_config::server_config::{KV,KVS}`, generic `ENABLE_KEY`/`EnableState`, and all OIDC key/default constants from `rustfs_config::oidc`. It integrates with server config defaults, admin config, and any identity layer that reads OIDC settings from global server config.

## Risks and edge cases
Defaults are a compatibility contract for admin tooling and identity startup. Changing default scopes, claim names, or redirect URI dynamic behavior can alter login behavior even without explicit user config. The file does not validate URLs, scopes, or claim names; validation must happen in higher-level OIDC setup. Secret visibility depends on consumers respecting `hidden_if_empty` and redaction policies.

## Test signals
There are no local tests. `config/com.rs` tests cover OIDC decode and encode behavior, including boolean enable/dynamic redirect conversion, list conversion for scopes and audiences, default provider naming, and semantic equality between internal and external OIDC shapes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/config/oidc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/config/scanner.rs -->
# sources/object-store/rustfs/crates/ecstore/src/config/scanner.rs

## Purpose
This file defines scanner subsystem default KVS. These values configure object scanner pacing, cycle limits, bitrot cadence, cache save timeout, concurrency, yielding, and alert thresholds as admin-visible server config defaults.

## Important APIs, types, and functions
The only exported item is `DEFAULT_KVS`, a `LazyLock<KVS>`. It contains keys for scanner speed, delay/max wait/cycle/start delay, maximum cycle duration/object/directory counts, bitrot cycle, idle mode, cache save timeout, max concurrent set and disk scans, yield frequency, and alert thresholds for excessive versions, version size, and folders.

## Control flow
No algorithm runs in this file beyond lazy construction of the KVS list. `config::init` registers `DEFAULT_KVS` under `SCANNER_SUB_SYS`. Runtime scanner code elsewhere reads the registered server config.

## State and persistence behavior
The static KVS acts as the default schema. Several timing/override fields default to an empty string and `hidden_if_empty: true`, meaning they are optional overrides rather than concrete default values. Numeric limits are stored as strings, matching the server-config KVS format.

## Dependencies and integration points
This file depends on scanner key and default constants from `rustfs_config` and on `server_config::KV/KVS`. It integrates with admin config registration and whatever scanner implementation consumes these keys during scheduling and local snapshot/cache updates.

## Risks and edge cases
Because all values are strings, invalid future changes are only caught by downstream parsers. Empty hidden fields must remain distinguishable from explicit zero values. Concurrency and cycle-limit defaults influence system load; changing them can affect background I/O behavior. Alert threshold defaults are not validated here.

## Test signals
There are no local tests. `config/mod.rs` verifies that scanner defaults are registered and checks representative values for speed, delay, max wait, and max objects. It does not verify every scanner key or downstream parser behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/config/scanner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/config/storageclass.rs -->
# sources/object-store/rustfs/crates/ecstore/src/config/storageclass.rs

## Purpose
This file implements storage-class configuration for erasure coding parity, placement optimization mode, and inline shard thresholds. It maps admin KVS and environment overrides into a runtime `Config` used by object storage paths to choose parity and inline behavior.

## Important APIs, types, and functions
Public constants define S3 storage-class names, internal config keys (`standard`, `rrs`, `optimize`, `inline_block`), environment overrides, and EC scheme limits. `default_parity_count` chooses default standard parity by drive count. `StorageClass` stores a parity value. `Config` exposes `get_parity_for_sc`, `should_inline`, `inline_block`, and `capacity_optimized`. `lookup_config` is the main builder, using KVS plus `RUSTFS_STORAGE_CLASS_*` environment variables. `parse_storage_class`, `validate_parity`, and `validate_parity_inner` enforce `EC:N` syntax and parity relationships.

## Control flow
`lookup_config` resolves standard parity from `RUSTFS_STORAGE_CLASS_STANDARD`, then KVS `standard`, then `default_parity_count`. RRS parity resolves from `RUSTFS_STORAGE_CLASS_RRS`, then KVS `rrs`, then zero for single-drive sets or one parity otherwise. It validates that parity does not exceed half the set width for set sizes over two and that standard parity is not lower than RRS when both are nonzero. `optimize` currently reads only the environment variable. `inline_block` reads `RUSTFS_STORAGE_CLASS_INLINE_BLOCK` as a byte-size string or falls back to 128 KiB, warning if an override exceeds that recommendation.

## State and persistence behavior
The file itself keeps only static defaults. Runtime `Config` instances are cloned into `GLOBAL_STORAGE_CLASS` by `config/com.rs`. Persisted admin config stores string KVS values; environment variables override those values at lookup time and are not written back. Uninitialized `Config` returns no parity and default inline behavior.

## Dependencies and integration points
It depends on ecstore `Error/Result`, `rustfs_config::server_config`, `bytesize`, `serde`, `std::env`, and tracing warnings. Object-write and layout code can use `get_global_storage_class`, `get_parity_for_sc`, `should_inline`, and `capacity_optimized`. `config/com.rs` also converts external JSON storageclass fields into this module's KVS keys.

## Risks and edge cases
`lookup_config` ignores the KVS `optimize` value and only reads `OPTIMIZE_ENV`, while `DEFAULT_KVS` and config conversion preserve an `optimize` KVS; that may make persisted optimize settings ineffective. `INLINE_BLOCK` similarly only reads the environment despite being in defaults/external config. `validate_parity` and commented minimum-parity checks allow zero parity, which is needed for single-drive setups but risky if accidentally configured in larger sets. Unknown S3 storage classes fall back to standard parity when initialized.

## Test signals
Local tests verify that `lookup_config` reads RRS from the internal `rrs` key, and intentionally ignores the old `REDUCED_REDUNDANCY` key name. Broader config tests in `com.rs` verify storageclass encode/decode and admin set/load preservation. There are no local tests for env overrides, inline thresholds, optimize KVS behavior, or parity validation failures.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/config/storageclass.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/data_movement.rs -->
# sources/object-store/rustfs/crates/ecstore/src/data_movement.rs

## Purpose
This file implements object data movement helpers used when moving objects between pools/sets, such as rebalance or migration. It preserves object metadata, versions, ETags, checksums, compressed indexes, and mod times while copying either multipart or single-part objects through the normal object-store APIs.

## Important APIs, types, and functions
`IndexedDataMovementReader` wraps an async reader and optional `rustfs_rio::Index`, implementing `AsyncRead`, `EtagResolvable`, `HashReaderDetector`, and `TryGetIndex`. Public helpers include `decode_part_index`, `put_obj_reader_from_chunk`, `new_multipart_abort_flag`, `should_abort_multipart_upload`, and `mark_multipart_upload_completed`. The central operation is `migrate_object`, which is `pub(crate)`. Supporting helpers build `ObjectOptions` for new multipart, complete multipart, and put-object stages; resolve abort errors; detect overwrite-resume eligibility; compare source/target `ObjectInfo`; and look up target-pool object info.

## Control flow
`migrate_object` clones source `ObjectInfo` from the supplied `GetObjectReader`. Multipart objects start a new multipart upload with data-movement options, then read each source part fully, rebuild a `PutObjReader` with per-part actual size and optional compressed index, upload each part preserving part ETag, and complete the upload with source version/modtime/ETag options. If completion returns a data-movement overwrite error, the code checks whether the target pool already contains an equivalent object and treats the operation as complete if so. On any multipart failure before completion, it aborts the upload unless the completion flag was cleared. Single-part objects build a `HashReader` around the source stream and call `put_object` with preserved metadata options.

## State and persistence behavior
The file does not own durable state, but it writes object data through `ECStore` into destination placement selected by store internals. `ObjectOptions` set `data_movement`, `src_pool_idx`, optional `version_id`, `versioned`, user metadata, `mod_time`, and `preserve_etag`, making moved objects retain source identity. Multipart abort state is an in-memory `AtomicBool` scoped to one migration attempt.

## Dependencies and integration points
It depends on `ECStore`, `ObjectIO`, `ObjectOperations`, `MultipartOperations`, `ObjectInfo`, `ObjectOptions`, `PutObjReader`, `rustfs_rio` hash/index traits, `bytes`, `sha2`, `hex_simd`, and object-name directory encoding. It integrates with pool-level object APIs such as `handle_new_multipart_upload_with_pool_idx`, `put_object_part`, `complete_multipart_upload`, `abort_multipart_upload`, `put_object`, and direct target-pool `get_object_info`.

## Risks and edge cases
Multipart movement reads each part into memory as a full `Vec<u8>`, so very large parts can create memory pressure. Index decoding silently drops invalid indexes, which preserves movement but can affect compressed object metadata. Resume-as-complete depends on strict equivalence across version, delete marker, logical size, effective actual size, ETag, checksum, and mod time; if any field is unavailable or normalized differently, legitimate resumes may fail. Abort failure wraps the primary error, so callers see cleanup failure context rather than only the original stage. The single-part path does not perform overwrite-resume equivalence handling.

## Test signals
Tests cover abort-flag defaults and completion marking, stage-error formatting, overwrite-resume gating, invalid and valid part-index decoding, metadata preservation in multipart and put options, equivalence comparison including effective actual size, source-pool rejection, target mismatch rejection, target lookup error propagation, and ignoring non-overwrite errors. There are no integration tests here for full `migrate_object` success/failure against a live `ECStore`, large memory behavior, abort cleanup, or single-part overwrite races.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/data_movement.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/data_usage.rs -->
# sources/object-store/rustfs/crates/ecstore/src/data_usage.rs

## Purpose
This module manages data-usage accounting for ecstore. It persists cluster-wide usage summaries, loads them with compatibility repair, aggregates local per-disk scanner snapshots, computes exact bucket usage by listing, maintains an immediate in-memory usage overlay for quota/admin freshness, and loads/saves binary `DataUsageCache` files.

## Important APIs, types, and functions
Public constants include `DATA_USAGE_ROOT` and `DATA_USAGE_CACHE_NAME`, while lazy paths define `.usage.json` and `.bloomcycle.bin` metadata objects. Key APIs are `store_data_usage_in_backend`, `load_data_usage_from_backend`, `aggregate_local_snapshots`, `compute_bucket_usage`, `record_bucket_object_write_memory`, `increment_bucket_usage_memory`, `record_bucket_object_delete_memory`, `decrement_bucket_usage_memory`, `get_bucket_usage_memory`, `replace_bucket_usage_memory_from_info`, `apply_bucket_usage_memory_overlay`, `sync_memory_cache_with_backend`, `create_cache_entry_from_summary`, `cache_to_data_usage_info`, `load_data_usage_cache`, and `save_data_usage_cache`. It re-exports local snapshot helpers from `data_usage/local_snapshot.rs`.

## Control flow
Backend persistence writes JSON to `buckets/.usage.json` through config-object helpers, skipping the write when an existing persisted `last_update` is newer or equal. Loading first reads the primary object, records system-path failure metrics on errors, falls back to `.bkp`, returns default data on missing config, repairs old `bucket_sizes`/`buckets_usage` shapes, and maps legacy per-bucket replication counters into `replication_info` using bucket replication config roles.

`aggregate_local_snapshots` walks pools, sets, and local disks, deduplicates physical disks by endpoint/path, reads per-disk JSON snapshots, deletes corrupted snapshot files best-effort, patches missing meta fields, and merges bucket totals into one `DataUsageInfo`. `compute_bucket_usage` pages through `list_objects_v2` and counts non-directory objects, delete markers, sizes, and versions. Memory overlay calls ensure cache hydration from backend, updates bucket usage on writes/deletes, periodically refreshes the cache with a TTL and single updater flag, and overlays newer in-memory entries onto persisted responses. Binary cache helpers read `DataUsageCache` through set disks with fallback paths and save primary plus asynchronous backup.

## State and persistence behavior
Persistent state includes JSON `.usage.json` and `.usage.json.bkp` under the bucket metadata prefix, binary `.usage-cache.bin` and backup through `save_data_usage_cache`, and per-disk local snapshots re-exported from the submodule. Process state includes `USAGE_MEMORY_CACHE` and `USAGE_CACHE_UPDATING`, both `OnceLock<Arc<RwLock<...>>>`. Cache entries carry both refresh time and usage update time so newer memory mutations can survive older scanner/backend refreshes.

## Dependencies and integration points
The module depends on `rustfs_data_usage` types, config-object read/write helpers, `ECStore` pool/disk topology, object listing, bucket replication config lookup, system-path failure metrics, `GLOBAL_OBJECT_API`, and `resolve_object_store_handle`. It is an accounting bridge between scanner output, object write/delete fast paths, admin/quota reads, and persisted metadata objects.

## Risks and edge cases
The in-memory overlay is intentionally eventually consistent and process-local; restarts lose unpersisted mutations. `update_usage_cache_if_needed` uses background refresh for mildly stale data and synchronous refresh for very stale data, so callers may see stale values within the TTL. Corrupted local snapshots are deleted, which enables recovery but loses forensic data. `compute_bucket_usage` uses `list_objects_v2` without deleted versions and estimates versions from listed object metadata, so it may not be a complete versioned-bucket audit. Backup save is spawned and ignored, so backup write failures are silent. `load_data_usage_cache` has retry logic but breaks on many errors and may return default cache on decode failure without surfacing corruption.

## Test signals
Tests cover aggregation behavior when one snapshot is corrupted, memory overlay after delete, overwrite preserving object count, newer persisted usage suppressing older memory overlay, and scanner sync preserving newer memory updates. They directly validate timestamp conflict resolution and saturating counters. Missing coverage includes backend primary/backup load failure paths, monotonic write skipping, replication-info migration, full disk traversal, exact bucket listing, binary cache save/load, and global-object refresh spawning.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/data_usage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/data_usage/local_snapshot.rs -->
# sources/object-store/rustfs/crates/ecstore/src/data_usage/local_snapshot.rs

## Purpose
This file defines the local per-disk data-usage snapshot format and filesystem helpers. Scanner code can write one JSON snapshot per local disk, and `data_usage.rs` can aggregate those snapshots into cluster-wide `DataUsageInfo`.

## Important APIs, types, and functions
Public constants are `DATA_USAGE_DIR`, `DATA_USAGE_STATE_DIR`, and `LOCAL_USAGE_SNAPSHOT_VERSION`. `LocalUsageSnapshotMeta` records disk ID plus optional pool, set, and disk indexes. `LocalUsageSnapshot` stores format version, metadata, last update time, per-bucket `BucketUsageInfo`, cached counts, and total object bytes. Methods `new` and `recompute_totals` initialize and recalculate cached totals. Path helpers are `snapshot_file_name`, `snapshot_object_path`, `data_usage_dir`, `data_usage_state_dir`, and `snapshot_path`. I/O helpers are `read_snapshot`, `write_snapshot`, and `ensure_data_usage_layout`.

## Control flow
Writers call `LocalUsageSnapshot::new`, populate `buckets_usage`, call `recompute_totals`, and write via `write_snapshot`, which creates `.rustfs.sys/datausage` and writes pretty JSON to `<disk-id>.json`. Readers call `read_snapshot`, which returns `Ok(None)` for missing files, deserializes JSON into `LocalUsageSnapshot`, and reports malformed content as an ecstore error. `ensure_data_usage_layout` creates both the snapshot directory and `datausage/state`.

## State and persistence behavior
Snapshots are persisted directly on each disk under `<root>/<RUSTFS_META_BUCKET>/datausage/<disk-id>.json`; state files use `<root>/<RUSTFS_META_BUCKET>/datausage/state`. The format is JSON plus an explicit `format_version` for future evolution. Writes overwrite existing files and are not atomic: they serialize to a buffer and call `fs::write`.

## Dependencies and integration points
The file depends on `BucketUsageInfo`, metadata bucket naming, ecstore `Error/Result`, `serde`, `tokio::fs`, and standard path/time types. It is re-exported and consumed by `data_usage.rs`, especially `aggregate_local_snapshots`, which patches missing meta indexes and merges totals.

## Risks and edge cases
There is no version compatibility check on read, so newer snapshot formats deserialize only if serde can map them into the current struct. Non-atomic writes can leave partial JSON if the process crashes mid-write; aggregation treats that as corruption and may delete the file. Disk IDs are used directly in filenames, so callers must ensure IDs are path-safe. `SystemTime` JSON compatibility depends on serde's representation for the target environment.

## Test signals
There are no local tests in this file. `data_usage.rs` tests indirectly exercise `LocalUsageSnapshot::new` and `recompute_totals` during aggregation fixtures. Filesystem read/write/layout behavior is not covered in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/data_usage/local_snapshot.rs -->

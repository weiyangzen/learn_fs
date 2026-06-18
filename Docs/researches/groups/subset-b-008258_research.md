# subset-b-008258 Research

## Group Scope

This grouped report covers RustFS `ecstore` listing, bucket utility, tier configuration, warm-backend, and legacy bitrot compatibility files. Each file section is wrapped with the exact reconciliation markers requested by the worker contract.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store_list_objects.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store_list_objects.rs

## Purpose

`store_list_objects.rs` implements ECStore object listing and walk behavior. It backs S3 ListObjectsV2, ListObjectVersions, internal listing over erasure sets, and streaming walks by faning out to set/disk metacache readers, merging sorted `MetaCacheEntry` streams, resolving quorum metadata, and converting the result into `ObjectInfo` API payloads.

## Important APIs and Types

`ListPathOptions` is the central listing request structure. It carries bucket, prefix, base directory, marker, separator, limit, disk-quorum mode, deletion/version flags, recursive behavior, transient-cache flags, and optional metacache identity plus pool/set indices.

Public and integration-facing APIs include `ECStore::inner_list_objects_v2`, `ECStore::list_objects_generic`, `ECStore::inner_list_object_versions`, `ECStore::list_path`, `ECStore::walk_internal`, `SetDisks::list_path`, and helpers such as `max_keys_plus_one`. Internal orchestration helpers include `list_merged`, `gather_results`, `merge_entry_channels`, `select_from`, `send_or_cancel`, `get_list_quorum`, `get_quorum_disks`, and `calc_common_counter`.

Marker helpers encode and parse RustFS cache tags of the form `[rustfs_cache:v1,...]`, preserving list cache id and pool/set cursor. Version helpers parse `"null"` and UUID version markers into `VersionMarker` and only apply a version marker when the key marker entry is present.

## Control Flow

ListObjectsV2 chooses `start_after` when no continuation token is supplied, delegates to `list_objects_generic`, and maps the generic result into `ListObjectsV2Info`. Generic listing caps `max_keys` at 1000, requests `max_keys + 1` for truncation detection, optionally short-circuits exact single-object lookups through `get_object_info`, then calls `list_path`.

`list_path` validates arguments, normalizes marker/prefix/separator/recursive settings, computes `base_dir`, marks reserved buckets as transient, and spawns two async tasks: `list_merged` produces merged metacache entries and `gather_results` filters/limits them into a `MetaCacheEntriesSortedResult`. Cancellation is coordinated with `CancellationToken` and a broadcast error channel. A full limit is represented by `err == None`; EOF is represented by `Unexpected`, so higher layers reinterpret that sentinel when deciding truncation.

`list_merged` starts one `SetDisks::list_path` task for every set across every pool, merges their output channels, and reduces set errors so all-not-found becomes an empty listing. `SetDisks::list_path` chooses online disks based on the configured list quorum (`strict`, `disk`, `reduced`, `optimal`, `auto`), may select fallback disks, builds metadata resolution quorum, and delegates raw disk walking to `list_path_raw`.

`merge_entry_channels` performs a k-way sorted merge over per-set channels, deduplicates names, merges version metadata from matching entries with `merge_file_meta_versions`, respects cancellation during receives/sends, and skips duplicate or stale names with a `last` guard. `walk_internal` follows a similar set fan-out but streams `ObjectInfoOrErr` to a caller channel, either latest-only or all versions.

## State and Persistence Behavior

This file does not persist application state directly. It consumes disk/metacache state and may assign a reusable list id on returned `MetaCacheEntriesSorted` when the listing is non-transient and appears truncated. Reserved or invalid buckets force transient behavior, avoiding disk cache reuse. The only external configuration state read here is `RUSTFS_API_LIST_QUORUM`, normalized to supported quorum modes with `strict` as default.

## Dependencies and Integration Points

The implementation depends on bucket argument validation, versioning configuration, `rustfs_filemeta` entry/version resolution, erasure-set disk discovery, `list_path_raw`, object-info conversion APIs, Tokio channels/tasks, cancellation tokens, tracing, UUID parsing, and RustFS path helpers. It integrates with S3 API response structs from `store_api` and with lower-level disk metadata readers through `SetDisks`.

## Risks and Edge Cases

The EOF/full-limit convention is subtle: `Unexpected` is treated as normal EOF in several paths, while `None` means the limit filled and more data may exist. Incorrect propagation can produce false errors or wrong truncation markers. `max_keys <= 0` still drives an effective limit of zero and later clears results, so callers must not assume disk IO is skipped for all zero-count requests. Delimiter collapse re-evaluates truncation after object/prefix separation, which is easy to regress. `auto` quorum depends on mutation counters and may fall back to strict if no quorum-disks set is selected. The merge code assumes each input channel is sorted; unsorted producers could drop or reorder results because of the `last` dedupe guard. Version marker behavior is intentionally only active when the key-marker entry is included.

## Test Signals

The in-file tests cover prompt return after gather limits, include-marker behavior for version listings, default marker skipping, version-marker gating, max-key lookahead capping, list quorum env parsing, metadata resolver version limits, null/UUID version marker parsing, cache marker round trips and unsupported marker tags, walk error reduction, sorted/deduplicated merge output, and cancellation while merging or sending to a full output channel.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store_list_objects.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store_test.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store_test.rs

## Purpose

`store_test.rs` is a focused unit-test module for ECStore disk de-duplication. It validates that duplicate administrative disk records collapse to unique entries before server-info or storage views expose them.

## Important APIs and Types

The tests call `ECStore::deduplicate_disks` with vectors of `rustfs_madmin::Disk`. The identity signal used by the scenarios is the combination of endpoint, drive path, pool index, set index, and disk index, with large `total_space` values included as representative disk metadata.

## Control Flow

`test_deduplicate_disks` builds one disk and 231 identical duplicates, asserts the input count, calls the dedupe function, and expects one output. `test_deduplicate_multiple_unique_disks` builds two distinct drive paths plus one duplicate of the first, then expects two output disks.

## State and Persistence Behavior

The file has no durable state. It constructs in-memory disk structs and verifies pure transformation behavior.

## Dependencies and Integration Points

The test depends on the `ECStore` implementation in `store.rs` and the `rustfs_madmin::Disk` DTO used by admin/server-info surfaces. It is a regression signal for integrations that aggregate disks from multiple sets or endpoints and need stable unique reporting.

## Risks and Edge Cases

The tests cover exact duplicates and a simple multi-disk case, but they do not prove behavior when only some identity fields differ, when endpoint aliases resolve to the same disk, or when a disk has default/empty path fields. Ordering guarantees are also not asserted.

## Test Signals

Both tests are direct unit tests. A failure likely means admin disk reporting may duplicate entries or overcount capacity/drive inventory.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store_utils.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store_utils.rs

## Purpose

`store_utils.rs` provides metadata cleanup helpers and bucket-name validation utilities used by ECStore request handling. It strips transient or standard metadata fields before persistence/response use and rejects reserved or invalid bucket names.

## Important APIs and Types

`clean_metadata` removes standard storage class plus selected generated headers (`md5Sum`, `etag`, `expires`, object tagging, and `last-modified`). `remove_standard_storage_class` removes `x-amz-storage-class` only when it equals the configured `STANDARD`. `clean_metadata_keys` removes arbitrary caller-provided keys.

Bucket validation is exposed through `is_reserved_or_invalid_bucket`. Private helpers include `is_meta_bucket`, `is_reserved_bucket`, and `check_bucket_name`. Static `LazyLock<Regex>` values validate IP-address form, strict S3-like lowercase bucket names, and a non-strict RustFS-compatible mode that allows uppercase, underscores, and colons.

## Control Flow

Bucket validation trims a trailing slash, checks empty/length/IP-address constraints, chooses strict or non-strict regex, rejects `..`, `.-`, and `-.`, then rejects RustFS metadata buckets and the reserved bucket name `rustfs`. The public API returns a boolean that is true for both reserved and invalid entries.

## State and Persistence Behavior

The module only mutates caller-provided metadata maps. It has no durable state. Regexes are compiled once through `LazyLock` and reused across calls.

## Dependencies and Integration Points

It depends on storage-class config constants, disk metadata bucket constants, and HTTP header constants from `rustfs_utils`. Listing code uses `is_reserved_or_invalid_bucket` to mark listings transient for reserved/invalid buckets, and write/read paths can use metadata cleanup before persisting object metadata.

## Risks and Edge Cases

The public validator reports reserved and syntactically invalid names with the same boolean, which is convenient for filtering but loses reason detail. Non-strict mode intentionally allows names that strict S3 clients would reject. The IP-address regex checks dotted decimal shape but not octet ranges. `clean_metadata_keys` performs exact key removal, so case-normalized header maps are expected.

## Test Signals

The in-file tests cover empty/whitespace, length bounds, IP-shaped names, dot/dash invalid patterns, reserved metadata buckets, `rustfs`, invalid starts/ends, strict versus non-strict uppercase/underscore/colon behavior, valid dotted/numeric/min/max names, trailing slash stripping, and repeated calls against cached regexes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store_utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/mod.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/mod.rs

## Purpose

`tier/mod.rs` is the module barrel for ECStore tiering support. It declares the tier configuration manager, admin DTOs, generated stubs, admin error constants, the warm-backend trait, and concrete warm-backend implementations.

## Important APIs and Types

The file exposes submodules `tier`, `tier_admin`, `tier_config`, `tier_gen`, `tier_handlers`, `warm_backend`, and provider modules for Aliyun, Azure, GCS, Huawei Cloud, MinIO, R2, RustFS, generic S3, AWS SDK S3, and Tencent.

## Control Flow

There is no runtime control flow. Compilation inclusion through this file makes the provider modules available to `crate::tier::*` paths and lets `warm_backend::new_warm_backend` select concrete implementations.

## State and Persistence Behavior

No state is stored in this file. State lives in `TierConfigMgr`, persisted config objects, and backend clients defined by child modules.

## Dependencies and Integration Points

The integration point is Rust's module system. Adding a new tier provider requires declaration here plus factory/config updates elsewhere.

## Risks and Edge Cases

The module includes both `warm_backend_s3` and `warm_backend_s3sdk`, but the current factory imports the transition-client `warm_backend_s3` implementation. The SDK variant can compile yet remain unused unless the factory is changed.

## Test Signals

There are no tests in this file; coverage comes from child module tests and compile-time module resolution.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/tier.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/tier.rs

## Purpose

`tier.rs` implements the tiering configuration manager: in-memory tier map, backend driver cache, add/edit/remove/list/verify operations, config serialization, legacy/external config compatibility, periodic reload, initial load, and migration from legacy metadata-bucket locations.

## Important APIs and Types

`TierConfigMgr` contains `tiers: HashMap<String, TierConfig>`, a skipped `driver_cache: HashMap<String, WarmBackendImpl>`, and `last_refreshed_at`. Public methods include `new`, `unmarshal`, `marshal`, `add`, `remove`, `verify`, `list_tiers`, `get`, `edit`, `get_driver`, `reload`, `clear_tier`, `save`, `save_tiering_config`, `refresh_tier_config`, and `init`.

Compatibility types `ExternalTierConfigMgr`, `ExternalTierConfig`, `ExternalTierS3`, `ExternalTierAzure`, `ExternalTierGcs`, and `ExternalTierCompatible` encode the MessagePack-like external format. Constants define `tier-config.bin`, legacy `tier-config.json`, format/version headers, and external type ids. `try_migrate_tiering_config`, `is_err_config_not_found`, and helpers handle config migration and missing-object interpretation.

## Control Flow

Add/edit paths validate tier existence/name rules, build a concrete warm backend, optionally check whether the backend already contains data, then update `tiers` and `driver_cache`. Removal obtains or constructs a driver, optionally rejects non-empty backends, then removes both config and cached driver. `get_driver` lazily constructs and caches a backend if one is not already present.

Save paths encode `TierConfigMgr` into the external binary format and put it under `.rustfs.sys/config/tier-config.bin` with max parity. Load first tries `tier-config.bin`, decodes either legacy JSON or external binary, then falls back to legacy `tier-config.json`. If no config exists and the first cluster node is local, it creates and saves an empty config; non-first nodes return an empty in-memory manager. `try_migrate_tiering_config` skips if the target exists, otherwise tries legacy JSON in the RustFS metadata bucket and compatible binary from the migrating metadata bucket.

External encoding maps native S3/Azure/GCS/MinIO to external type ids. Extended compatible providers such as RustFS, Aliyun, Tencent, Huawei Cloud, and R2 are encoded as S3-compatible payloads with `XTierType` hints so they can round-trip back to provider-specific `TierType`s.

## State and Persistence Behavior

The authoritative persisted config is an object in `RUSTFS_META_BUCKET` under the config prefix. The in-memory `driver_cache` is deliberately skipped by serde and rebuilt on demand or after reload. `last_refreshed_at` tracks local reload time. Secrets are present in persisted config but redacted by `TierConfig` cloning/listing behavior from `tier_config.rs`.

## Dependencies and Integration Points

The module integrates with admin error definitions, `TierCreds`, `TierConfig`, warm-backend factory/probe functions, global object-store handle resolution, object APIs (`ObjectIO`, `ObjectOperations`, `put_object`, `get_object_reader`, `get_object_info`), cluster-local-first-node detection, metadata bucket constants, `read_config`, MessagePack serde, JSON serde, and Tokio timers.

## Risks and Edge Cases

The manager stores secrets in memory and persisted config; only clone/list redaction protects display paths. `add` calls `new_warm_backend(&tier_config, true)` but backend factory currently does not use its `probe` argument directly, so validation depends on later `in_use` or explicit `verify`. Error mapping in `add` uses substring checks such as `"connect"`, `"authorization"`, and `"bucket"`, which can misclassify provider errors. `refresh_tier_config` captures one random jitter value outside the loop, so jitter is stable per task. Migration silently logs and skips incompatible configs, which is safe but can hide operator mistakes without debug logs. `clear_tier` accepts `force` but does not use it.

## Test Signals

Tests verify external blob round-trip for standard S3 and extended hinted RustFS tiers, legacy JSON decode fallback, and formatting of the object-layer-not-initialized save error. Broader live-backend add/edit/remove behavior is not unit-tested here.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/tier.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/tier_admin.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/tier_admin.rs

## Purpose

`tier_admin.rs` defines the administrative credentials payload used to edit tier credentials.

## Important APIs and Types

`TierCreds` is a serde-serializable/deserializable DTO with access/secret keys, AWS role flags, web identity token file and role ARN fields, and a `creds_json` byte vector intended for providers such as GCS. Serde renames preserve expected admin API field names like `accessKey`, `secretKey`, `awsRole`, `awsRoleWebIdentityTokenFile`, and `awsRoleArn`.

## Control Flow

The file contains no functions. `TierConfigMgr::edit` consumes `TierCreds` and applies its fields differently for S3, compatible providers, Azure, GCS, and R2.

## State and Persistence Behavior

`TierCreds` is transient request state. Updated credentials are persisted only when the tier manager saves the modified `TierConfig`.

## Dependencies and Integration Points

It depends only on serde and integrates with admin tier edit handlers and `TierConfigMgr::edit`.

## Risks and Edge Cases

`creds_json` has no serde rename in the current struct, so JSON compatibility depends on the default field name unless callers use another translation layer. The struct can carry partial credentials; enforcement happens in tier manager edit logic, not here.

## Test Signals

There are no direct tests for this DTO. Coverage should verify admin API serialization and provider-specific credential update behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/tier_admin.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/tier_config.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/tier_config.rs

## Purpose

`tier_config.rs` defines the serde model for configured remote tiers and provider-specific credential/location fields. It also provides tier-type conversion helpers, redacted cloning for display/listing, and small provider construction helpers.

## Important APIs and Types

`TierType` enumerates `Unsupported`, `S3`, `RustFS`, `MinIO`, `Aliyun`, `Tencent`, `Huaweicloud`, `Azure`, `GCS`, and `R2`, with serde lowercase names, `Display`, `new`, and `as_lowercase`.

`TierConfig` stores version, type, name, and exactly one optional provider payload. Provider structs include `TierS3`, `TierRustFS`, `TierMinIO`, `TierAliyun`, `TierTencent`, `TierHuaweicloud`, `TierAzure`, `TierGCS`, and `TierR2`. `ServicePrincipalAuth` and `TierAzure::is_sp_enabled` model Azure service principal credentials. `TierS3::create` and `TierMinIO::create` are dead-code-marked builder-style helpers.

## Control Flow

`TierConfig::clone` branches on `tier_type`, clones only the active provider payload, and redacts sensitive fields (`secret_key` for access-key providers and `creds` for GCS). Accessor helpers `endpoint`, `bucket`, `prefix`, and `region` similarly branch on `tier_type` and return provider fields or log unexpected unsupported types.

## State and Persistence Behavior

The structs are the persisted shape used by legacy JSON and internal config conversion. `version` and `name` are skipped in serde on `TierConfig`, while provider fields use serde renames for expected external/admin names. The redacted `Clone` affects returned/listed configs but not original in-memory or persisted values.

## Dependencies and Integration Points

The module depends on serde, `Display`, and tracing. It is consumed by `tier.rs` for persistence and admin operations and by warm-backend constructors for provider-specific endpoint/credential data.

## Risks and Edge Cases

The custom `Clone` intentionally drops inactive provider payloads and redacts secrets, which is correct for display but risky if code uses `clone` expecting a fully reusable config. Some helpers are private/dead-code and may not be enforced by construction paths. `TierType::new` only accepts display-case strings like `"S3"` rather than serde lowercase values. Azure service-principal option-builder code is present only as commented Go-like reference, not Rust behavior.

## Test Signals

There are no direct tests in this file. Effective tests should cover serde compatibility, redaction behavior, `TierType` conversions, Azure SP detection, and provider config round-trips through `tier.rs`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/tier_config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/tier_gen.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/tier_gen.rs

## Purpose

`tier_gen.rs` is a generated/stub extension point for `TierConfigMgr` message sizing.

## Important APIs and Types

It imports `TierConfigMgr` and adds `msg_size(&self) -> usize`, currently hard-coded to return `100`.

## Control Flow

There is no meaningful control flow. The method is marked `dead_code`, so it is likely a placeholder for generated msgpack sizing compatibility.

## State and Persistence Behavior

No state is read or written. The size value is not derived from tier contents.

## Dependencies and Integration Points

The only integration point is the inherent `impl TierConfigMgr`. If callers begin relying on this method for buffer allocation, the constant return value will be inaccurate.

## Risks and Edge Cases

The hard-coded `100` can undercount or overcount real serialized configs. Because it is currently dead code, the immediate risk is low; the future risk is silent misuse.

## Test Signals

No direct tests exist. A future generated serialization path should test this against actual encoded size.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/tier_gen.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/tier_handlers.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/tier_handlers.rs

## Purpose

`tier_handlers.rs` centralizes admin-facing tier error constants as `AdminError` values with S3/admin-compatible codes, messages, and HTTP statuses.

## Important APIs and Types

Lazy statics include `ERR_TIER_ALREADY_EXISTS`, `ERR_TIER_NOT_FOUND`, `ERR_TIER_NAME_NOT_UPPERCASE`, `ERR_TIER_BUCKET_NOT_FOUND`, `ERR_TIER_INVALID_CREDENTIALS`, `ERR_TIER_RESERVED_NAME`, `ERR_TIER_PERM_ERR`, and `ERR_TIER_CONNECT_ERR`.

## Control Flow

There is no runtime control flow beyond lazy initialization. Callers clone the static `AdminError` values and sometimes append provider-specific details to the message.

## State and Persistence Behavior

No persistent state exists. Error instances are process-local constants.

## Dependencies and Integration Points

The module depends on `AdminError`, `http::StatusCode`, and `lazy_static`. `tier.rs` and `warm_backend.rs` use these values to map validation, probe, connectivity, credential, and in-use failures to admin responses.

## Risks and Edge Cases

`ERR_TIER_PERM_ERR` and `ERR_TIER_CONNECT_ERR` use HTTP 200 OK status codes, which may be intentional MinIO compatibility but can surprise generic HTTP clients. Static messages are broad, so provider-specific diagnostics may require message mutation after cloning.

## Test Signals

There are no direct tests. Admin API tests should assert both error code and HTTP status, especially for compatibility-sensitive statuses.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/tier_handlers.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend.rs

## Purpose

`warm_backend.rs` defines the common warm-tier backend trait, metadata-to-put-options promotion, backend probing, and the factory that turns a `TierConfig` into a concrete provider client.

## Important APIs and Types

`WarmBackendImpl` is a boxed async trait object. `WarmBackendGetOpts` carries range options. `WarmBackend` defines `put`, `put_with_meta`, `get`, `remove`, and `in_use`. `build_transition_put_options` maps object metadata into `PutObjectOptions` fields for content headers, cache/expires, object-lock mode/retain/legal-hold, replication status defaults, storage class, and user metadata.

`check_warm_backend` writes, reads, and removes a fixed `probeobject`. `new_warm_backend` switches on `TierType` and calls the concrete provider constructor for S3, RustFS, MinIO, Aliyun, Tencent, Huaweicloud, Azure, GCS, and R2.

## Control Flow

The factory validates that the matching provider payload exists, constructs the backend, maps construction failures to `XRustFSAdminTierInvalidConfig`, and returns unsupported-type errors for unknown tiers. `check_warm_backend` reports missing tier, put/get/remove failures as admin permission-style errors.

`build_transition_put_options` extracts recognized HTTP/S3 headers from metadata, parses timestamps as RFC3339 or RFC2822, maps object-lock string values into typed S3 DTO wrappers, removes promoted headers from the user metadata map, and returns the remaining metadata as user metadata.

## State and Persistence Behavior

The file does not persist state. It constructs clients and mutates only local metadata maps. `check_warm_backend` does write and remove a remote probe object, so it has observable remote-side effects.

## Dependencies and Integration Points

It integrates provider modules, tier config DTOs, admin errors, transition API reader/put options, S3 object-lock/replication DTOs, RustFS HTTP header helpers, bytes, time parsing, and tracing. `TierConfigMgr` uses it for add/edit/verify/driver-cache population.

## Risks and Edge Cases

The `probe` parameter in `new_warm_backend` is present but not used in the visible code; callers may assume construction performs a probe when it does not. `check_warm_backend` treats all put/get/remove failures as permission errors and currently comments out bucket/signature-specific mapping. Metadata header lookup/removal depends on canonical key handling by `HeaderExt`. Probe object naming is fixed and could collide with user data if the backend/prefix is not isolated.

## Test Signals

Tests cover content header promotion, object-lock header preservation, timestamp parsing effect on retention, and filtering of promoted headers out of user metadata. Factory selection and live provider probing are not unit-tested here.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_aliyun.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_aliyun.rs

## Purpose

`warm_backend_aliyun.rs` implements the Aliyun OSS warm-tier adapter by wrapping the generic transition-client S3 backend shape with Aliyun-specific endpoint, bucket lookup, and multipart upload options.

## Important APIs and Types

`WarmBackendAliyun(WarmBackendS3)` exposes `new` and implements `WarmBackend`. Constants define 5 TiB maximum object size, 10,000 parts, and 128 MiB minimum part size. `optimal_part_size` computes a multipart size aligned to the minimum.

## Control Flow

`new` requires both access and secret keys, requires a bucket, parses the endpoint, builds static Signature V4 credentials, enables trailing headers and DNS bucket lookup, derives host plus default port, creates a `TransitionClient` with provider id `"aliyun"`, and stores a trimmed prefix in the wrapped S3 backend.

`put_with_meta` computes part size, builds transition put options from metadata, sets part size and disables content SHA256, then calls the wrapped transition client's `put_object`. `get`, `remove`, and `in_use` delegate to the wrapped backend.

## State and Persistence Behavior

No local durable state exists. Remote state changes happen through put/remove/list operations against the configured bucket and prefix.

## Dependencies and Integration Points

The adapter depends on Aliyun tier config, transition API credentials/client/core, bucket lookup type, shared warm-backend metadata handling, and the generic `WarmBackendS3` helper for destination paths and delegated operations.

## Risks and Edge Cases

Endpoint host validation is explicit, but region/provider-specific signing behavior depends on `TransitionClient`. The `tier` argument is unused. `optimal_part_size(-1)` assumes maximum object size. Content SHA256 is disabled for compatibility, which may reduce end-to-end integrity checks if the remote expects it.

## Test Signals

No direct tests exist. Provider tests should cover missing credentials/bucket, invalid endpoint, part-size bounds, prefix joining, and put/get/remove delegation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_aliyun.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_azure.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_azure.rs

## Purpose

`warm_backend_azure.rs` implements an Azure warm-tier adapter using the RustFS transition-client abstraction and an S3-compatible wrapper.

## Important APIs and Types

`WarmBackendAzure(WarmBackendS3)` exposes `new` and implements `WarmBackend`. It has the same multipart sizing constants and `optimal_part_size` routine used by the other compatible provider wrappers.

## Control Flow

`new` validates access/secret keys and bucket, parses the endpoint, builds static Signature V4 credentials, enables trailing headers and DNS bucket lookup, derives host plus default port, creates a `TransitionClient` with provider id `"azure"`, and wraps it in `WarmBackendS3`. `put_with_meta` sets computed part size and disables content SHA256 before uploading; reads, removals, and in-use checks delegate.

## State and Persistence Behavior

The adapter keeps only an in-memory client, core, bucket, prefix, and empty storage class. Persistent state is remote object data in the configured tier bucket.

## Dependencies and Integration Points

It depends on `TierAzure`, transition API credentials/client types, shared `build_transition_put_options`, and the `WarmBackend` trait. It is selected by `new_warm_backend` for `TierType::Azure`.

## Risks and Edge Cases

Despite `TierAzure` having service-principal fields, this adapter only uses access/secret key fields. Azure-native authentication and blob API semantics are not represented in this implementation; compatibility relies on the transition client provider. No direct tests enforce endpoint handling or Azure SP behavior.

## Test Signals

No direct tests exist. Required coverage should include credential validation, endpoint host/port derivation, SP-auth expectations, multipart part-size calculation, and compatibility put/get/remove behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_azure.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_gcs.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_gcs.rs

## Purpose

`warm_backend_gcs.rs` implements the Google Cloud Storage warm-tier adapter using `google_cloud_storage` rather than the RustFS transition-client S3 compatibility layer.

## Important APIs and Types

`WarmBackendGCS` stores an `Arc<Storage>`, bucket, prefix, and storage class, exposes `new` and `get_dest`, and implements `WarmBackend`. It validates `TierGCS.creds` and bucket, parses credentials JSON as a Google authorized-user credential, and constructs a storage client with the configured endpoint.

## Control Flow

`put_with_meta` reads the entire `ReaderImpl` into memory, writes it with `write_object(...).send_buffered()`, and returns the object generation as the remote version id. `get` reads the object stream chunk by chunk into a `Vec<u8>` and returns a cursor-backed `ReadCloser`. `remove` is effectively a no-op with commented delete code. `in_use` returns `false` with commented listing code.

## State and Persistence Behavior

Object data is persisted remotely in GCS on put. Local state is only the in-memory storage client and config. Because `remove` is no-op and `in_use` always false, lifecycle/admin operations may not reflect remote state for GCS tiers.

## Dependencies and Integration Points

It depends on Google auth/storage crates, `bytes`, `TierGCS`, `WarmBackend`, and RustFS transition reader abstractions. `new_warm_backend` selects it for `TierType::GCS`.

## Risks and Edge Cases

The adapter currently ignores metadata, range options, version/generation in reads/removes, storage class, and real in-use checks. Full-object buffering on put/get can be expensive for large tiered objects. The no-op remove can leave remote data behind. Authorized-user credential parsing may not support all GCS service-account JSON forms.

## Test Signals

No tests are present. High-priority coverage would assert delete behavior, generation-specific reads, range reads, metadata preservation, in-use listing, credential formats, and memory behavior for large objects.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_gcs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_huaweicloud.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_huaweicloud.rs

## Purpose

`warm_backend_huaweicloud.rs` implements the Huawei Cloud OBS warm-tier adapter as an S3-compatible wrapper over `WarmBackendS3`.

## Important APIs and Types

`WarmBackendHuaweicloud(WarmBackendS3)` exposes `new`, implements `WarmBackend`, and uses the shared multipart constants and `optimal_part_size` helper.

## Control Flow

`new` validates access/secret keys and bucket, parses endpoint URL, creates static Signature V4 credentials, enables trailing headers and DNS bucket lookup, derives host/default port, creates a `TransitionClient` with provider id `"huaweicloud"`, and wraps it. `put_with_meta` computes part size, promotes metadata into put options, sets part size and disables content SHA256, and uploads. Other trait methods delegate.

## State and Persistence Behavior

Only in-memory client/config state is kept locally. Remote puts and removes mutate the configured bucket/prefix.

## Dependencies and Integration Points

It depends on `TierHuaweicloud`, transition API client/credential types, `WarmBackendS3`, and shared warm-backend metadata handling. It is selected by the tier factory for `TierType::Huaweicloud`.

## Risks and Edge Cases

Provider behavior is mostly generic S3 compatibility, so Huawei-specific error mapping and auth quirks are not explicit here. The `tier` argument is unused, and no tests validate endpoint or part-size behavior.

## Test Signals

No direct tests exist. Useful tests would mirror the Aliyun/Tencent compatible-provider matrix: missing fields, invalid endpoint, part-size bounds, prefix handling, and remote CRUD behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_huaweicloud.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_minio.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_minio.rs

## Purpose

`warm_backend_minio.rs` implements a MinIO-compatible warm-tier adapter by wrapping the generic transition-client S3 backend.

## Important APIs and Types

`WarmBackendMinIO(WarmBackendS3)` exposes `new`, implements `WarmBackend`, and shares multipart sizing constants with the other compatible wrappers.

## Control Flow

`new` requires access/secret keys and bucket, parses endpoint, builds static Signature V4 credentials with trailing headers enabled, derives host plus default port, creates a `TransitionClient` with provider id `"minio"`, and stores a slash-trimmed prefix. `put_with_meta` computes part size, promotes metadata, disables content SHA256, and delegates to `put_object`. `get`, `remove`, and `in_use` delegate.

## State and Persistence Behavior

The adapter has no durable local state. It persists and deletes remote objects in the target MinIO bucket/prefix.

## Dependencies and Integration Points

It depends on `TierMinIO`, transition client APIs, `WarmBackendS3`, and shared metadata promotion. `TierConfigMgr` creates it for `TierType::MinIO`.

## Risks and Edge Cases

The adapter does not use a MinIO-specific bucket lookup override, unlike some cloud wrappers. Provider-specific errors are surfaced as generic IO errors. Tests do not cover MinIO endpoint schemes, path-style versus virtual-host behavior, or non-empty detection.

## Test Signals

No direct tests exist. Integration tests should validate path style, credentials, prefix joining, multipart settings, object-lock metadata handling through shared options, and `in_use`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_minio.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_r2.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_r2.rs

## Purpose

`warm_backend_r2.rs` implements a Cloudflare R2 warm-tier adapter over the RustFS transition-client S3-compatible layer.

## Important APIs and Types

`WarmBackendR2(WarmBackendS3)` exposes `new`, implements `WarmBackend`, and includes the shared 5 TiB/10,000 part/128 MiB part-size calculation.

## Control Flow

`new` validates credentials and bucket, parses endpoint, builds static Signature V4 credentials, enables trailing headers, derives host/default port, constructs a `TransitionClient` with provider id `"r2"`, and wraps it. `put_with_meta` computes multipart part size, applies shared put options, disables content SHA256, and uploads. Other trait methods delegate.

## State and Persistence Behavior

Local state is in-memory client/config only. Remote object data is persisted under the configured R2 bucket/prefix.

## Dependencies and Integration Points

It depends on `TierR2`, transition client types, `WarmBackendS3`, and `build_transition_put_options`. `new_warm_backend` selects it for `TierType::R2`.

## Risks and Edge Cases

R2-specific requirements such as account-scoped endpoints and region conventions are not validated beyond generic URL host parsing. Content SHA256 is disabled. No tests assert R2 endpoint handling or compatibility.

## Test Signals

No direct tests exist. Coverage should include R2 endpoint validation, credentials, part-size bounds, prefix behavior, in-use listing, and provider error mapping.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_r2.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_rustfs.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_rustfs.rs

## Purpose

`warm_backend_rustfs.rs` implements RustFS-to-RustFS warm-tiering over the transition-client S3-compatible API.

## Important APIs and Types

`WarmBackendRustFS(WarmBackendS3)` exposes `new`, implements `WarmBackend`, and contains the common compatible-provider multipart constants and `optimal_part_size`.

## Control Flow

`new` validates access/secret keys and bucket, parses the endpoint, explicitly rejects URLs without a host, creates static Signature V4 credentials, enables trailing headers, derives host/default port, constructs a `TransitionClient` with provider id `"rustfs"`, and wraps it with bucket/prefix data. `put_with_meta` computes part size, promotes metadata, disables content SHA256, and delegates upload; reads/removes/in-use checks delegate.

## State and Persistence Behavior

No local durable state exists. The adapter writes and removes remote RustFS objects in the configured bucket/prefix.

## Dependencies and Integration Points

It depends on `TierRustFS`, transition API credentials/client, `WarmBackendS3`, and shared metadata option conversion. The tier manager uses it for `TierType::RustFS`, including legacy compatible tier migration through hints.

## Risks and Edge Cases

The adapter relies on S3-compatible semantics between RustFS clusters. The `tier` argument is unused. Disabling content SHA256 and using fixed multipart thresholds should be validated against RustFS server expectations. Endpoint validation has a specific regression test because earlier host extraction could panic.

## Test Signals

The in-file async test verifies that `new` returns an error rather than panicking when the endpoint URL has no host. Additional tests should cover valid endpoint construction, part-size behavior, metadata propagation, and remote CRUD.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_rustfs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_s3.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_s3.rs

## Purpose

`warm_backend_s3.rs` is the primary generic S3 warm-tier adapter using RustFS's transition-client abstraction.

## Important APIs and Types

`WarmBackendS3` stores `Arc<TransitionClient>`, `TransitionCore`, bucket, prefix, and storage class. `new` builds the client from `TierS3`; `get_dest` prefixes object keys; the `WarmBackend` impl provides put/get/remove/in-use behavior.

## Control Flow

`new` parses the endpoint, validates AWS role/web-identity/static-credential combinations, requires a bucket, builds static Signature V4 credentials, derives secure mode and region, extracts endpoint host, creates a `TransitionClient` with provider id `"s3"`, trims the prefix, and stores the storage class. `put_with_meta` applies `build_transition_put_options`, forces content MD5, uploads, and returns the remote version id. `get` applies optional version id and byte range, then uses `TransitionCore::get_object`. `remove` applies optional version id and maps optional remove errors. `in_use` lists one object/prefix under the configured prefix.

## State and Persistence Behavior

Local state is only the in-memory client and destination configuration. Remote state is object data in S3 and optional version ids returned by S3-compatible APIs.

## Dependencies and Integration Points

It depends on RustFS transition API clients, credentials, object get/put/remove option types, URL parsing, shared metadata-to-put-options conversion, and path separator constants. Other compatible provider wrappers embed this struct and delegate read/remove/list behavior.

## Risks and Edge Cases

Only static credentials are actually supported in this implementation; AWS role and web identity paths are validated but not used to build providers. `Url::host()` is converted to string without preserving path components; endpoints requiring path-style nuances depend on transition-client behavior. `get_dest` does simple prefix/object concatenation and assumes callers pass unprefixed keys.

## Test Signals

No tests are present in this file. Shared tests in `warm_backend.rs` cover metadata option conversion, while provider integration tests should cover credential modes, endpoint parsing, versioned reads/removes, ranges, storage class, and in-use listing.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_s3.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_s3sdk.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_s3sdk.rs

## Purpose

`warm_backend_s3sdk.rs` is an alternate generic S3 warm-tier adapter implemented with the official AWS SDK for Rust rather than the RustFS transition client.

## Important APIs and Types

It defines another `WarmBackendS3` type local to this module, holding `Arc<aws_sdk_s3::Client>`, bucket, prefix, and storage class. It implements the same `WarmBackend` trait and uses AWS SDK `Credentials`, `RegionProviderChain`, `Client`, and `ByteStream`.

## Control Flow

`new` performs similar endpoint and credential validation to the transition-client S3 adapter, creates static AWS credentials, configures the AWS SDK with endpoint URL and region provider, and builds a client. `put_with_meta` reads the entire `ReaderImpl` into a `ByteStream`, sends `put_object`, and returns the version id if present. `get` builds a get request with optional version id and range, collects the full response body into memory, and returns a cursor-backed `ReadCloser`. `remove` sends delete object with optional version id. `in_use` calls `list_objects_v2` on the bucket and checks returned prefixes/contents.

## State and Persistence Behavior

State is local client/config only. Remote object data is persisted in S3. This SDK implementation currently buffers full objects for put/get rather than streaming through the returned reader.

## Dependencies and Integration Points

The module depends on AWS SDK crates, RustFS transition reader types, `TierS3`, and `WarmBackend`. It is declared in `mod.rs` but the visible factory imports `warm_backend_s3::WarmBackendS3`, so this implementation appears unused unless selected elsewhere.

## Risks and Edge Cases

The SDK variant ignores metadata and storage class in `put_with_meta`, does full in-memory buffering, and lists the entire bucket root for `in_use` without applying prefix or max-keys. It also validates but does not implement AWS role/web-identity auth. Because its type name duplicates the transition-client module type, imports must be explicit to avoid confusion.

## Test Signals

No direct tests exist. Before enabling this adapter, tests should cover metadata/storage class propagation, prefix-scoped in-use checks, streaming memory behavior, range overflow, endpoint compatibility, and credential providers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_s3sdk.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_tencent.rs -->
# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_tencent.rs

## Purpose

`warm_backend_tencent.rs` implements the Tencent COS warm-tier adapter as an S3-compatible wrapper over `WarmBackendS3`.

## Important APIs and Types

`WarmBackendTencent(WarmBackendS3)` exposes `new`, implements `WarmBackend`, and includes the common multipart constants and `optimal_part_size` helper.

## Control Flow

`new` validates credentials and bucket, parses endpoint, builds static Signature V4 credentials, enables trailing headers and DNS bucket lookup, derives host/default port, creates a `TransitionClient` with provider id `"tencent"`, and wraps it. `put_with_meta` computes part size, applies shared put options, disables content SHA256, and uploads. Get/remove/in-use delegate to the wrapped S3 backend.

## State and Persistence Behavior

The adapter keeps no durable local state. It mutates remote Tencent COS object data through put/remove operations.

## Dependencies and Integration Points

It depends on `TierTencent`, transition API client/credentials, `WarmBackendS3`, and shared metadata conversion. It is selected by `new_warm_backend` for `TierType::Tencent`.

## Risks and Edge Cases

Tencent-specific signing, endpoint, and region requirements are delegated to the transition client and not validated here. The `tier` argument is unused. No direct tests cover the provider matrix or multipart edge cases.

## Test Signals

No direct tests exist. Integration coverage should verify credential validation, endpoint parsing, bucket lookup behavior, multipart upload options, prefix handling, and remote CRUD.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_tencent.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/tests/legacy_bitrot_read_test.rs -->
# sources/object-store/rustfs/crates/ecstore/tests/legacy_bitrot_read_test.rs

## Purpose

`legacy_bitrot_read_test.rs` is an integration test for reading legacy HighwayHash256S-protected object data through `create_bitrot_reader`. It isolates bitrot compatibility from full ECStore object reads by loading `xl.meta`, deriving checksum/part parameters, and reading either inline data or an erasure-coded part directly.

## Important APIs and Types

Helpers include `workspace_root`, `legacy_test_data_exists`, and `run_legacy_bitrot_test_for_object`. The test uses `create_bitrot_reader`, disk endpoint construction, `new_disk`, `STORAGE_FORMAT_FILE`, `get_file_info`, `FileInfoOpts`, and `HashAlgorithm::HighwayHash256SLegacy`.

## Control Flow

The existence check skips when `RUSTFS_SKIP_LEGACY_TEST=1` or when expected local fixture metadata is absent. For each object, the helper reads `xl.meta`, parses file info with inline data included, rejects deleted/no-part objects, computes shard size and part checksum info, switches to `HighwayHash256SLegacy` when metadata marks legacy checksum use, and then chooses inline or EC-part reading.

Inline objects pass the in-memory data slice to `create_bitrot_reader` and read into a shard-sized buffer. EC objects derive the data directory and `part.1` path, construct a local disk endpoint with pool/set/disk indices all zero, create a disk without cleanup/health check, and pass that disk plus object part path to `create_bitrot_reader`.

## State and Persistence Behavior

The test reads local fixture directories and does not intentionally mutate object data. It creates a disk abstraction with cleanup disabled. Environment variables control skip/root/disk behavior according to the module docs, although the current test body overrides root/disk with a hard-coded `/Users/weisd/project/minio` and `test`.

## Dependencies and Integration Points

It integrates with RustFS bitrot readers, disk endpoint/local disk initialization, file metadata parsing, and legacy MinIO/RustFS fixture layout. It is intended to be run from the workspace root with legacy test data present.

## Risks and Edge Cases

The hard-coded root and disk in `test_legacy_bitrot_read` conflict with the documented environment-variable defaults and can make the test non-portable. `legacy_test_data_exists` checks workspace `test1` fixtures but the actual test reads `/Users/weisd/project/minio`, so skip detection and execution target can diverge. Only `part.1` is read for EC objects, and successful nonzero read is the assertion rather than full-content verification. The helper prints diagnostics with `eprintln!` but maps most failures to `false`, losing precise assertion context.

## Test Signals

The test asserts that `ktvzip.tar.gz` and `path_traversal.md` can be read through the bitrot reader. It specifically signals compatibility with legacy HighwayHash256S metadata, inline data, local disk part reads, and file-info parsing for old `xl.meta` formats.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/tests/legacy_bitrot_read_test.rs -->

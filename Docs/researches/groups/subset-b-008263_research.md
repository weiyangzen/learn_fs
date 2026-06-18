# Research: subset-b-008263

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/manager.rs -->
# sources/object-store/rustfs/crates/iam/src/manager.rs

## Purpose

`manager.rs` is the high-level IAM cache and mutation coordinator. It wraps a pluggable `Store` backend, keeps an in-memory `Cache` coherent with persisted IAM objects, performs initial and periodic reloads, exposes policy/user/group/service-account operations to admin and auth paths, and handles notification-driven cache refreshes. The file is the boundary where persisted IAM documents become fast authorization state.

## Important APIs, Types, and Functions

`IamState` tracks `Uninitialized`, `Loading`, `Ready`, and `Error` states. `IamCache<T: Store>` owns the backend `api`, the shared `cache`, background reload channel, role map, timestamp, and sync metrics counters. `IamSyncMetricsSnapshot` exposes reload duration, age, success count, and failure count.

Construction flows through `IamCache::new()` and `init()`. `init()` persists the IAM format file, retries full load three times, sets state to `Ready` or `Error`, then optionally spawns a 120-second reload loop unless `RUSTFS_SKIP_BACKGROUND_TASK` is set. `_notify()` sends timestamps to that loop, and `load()` calls `Store::load_all()`, updates `last_timestamp`, and records metrics.

Read APIs include `is_ready`, `get_user`, `get_mapped_policy`, `get_policy`, `get_policy_doc`, `list_polices`, `list_policy_docs`, `list_policy_docs_internal`, `merge_policies`, `list_temp_accounts`, `list_sts_accounts`, `list_service_accounts`, `get_user_info`, `get_users`, `get_bucket_users`, `get_users_with_mapped_policies`, `policy_db_get`, `is_temp_user`, `get_group_description`, `list_groups`, and `update_groups`.

Mutation APIs include `set_policy`, `delete_policy`, `add_user`, `delete_user`, `update_user_secret_key`, `add_user_ssh_public_key`, `set_user_status`, `add_service_account`, `update_service_account`, `set_temp_user`, `policy_db_set`, `add_users_to_group`, `set_group_status`, `remove_members_from_group`, and `remove_users_from_group`. Notification handlers (`group_notification_handler`, `policy_notification_handler`, `policy_mapping_notification_handler`, `user_notification_handler`) reconcile cache state after external changes.

Helper functions cover format path building, default canned policy injection, token signing key retrieval, JWT claim extraction with and without required `exp`, policy filtering, and group-description construction.

## Control Flow

Initial startup writes `config/iam/format.json` via `save_iam_formatter()`, but only the first local cluster node writes if the file is missing or older than version 1. Full reload delegates to `Store::load_all()` and only marks the system ready after a successful cache replacement. Later reloads are ticker-driven or channel-driven; channel timestamps older than `last_timestamp` are ignored.

Most mutating methods validate inputs, persist through `Store`, and then update cache with an `OffsetDateTime::now_utc()` timestamp. This makes persistent success the normal prerequisite for in-memory visibility. Several paths intentionally tolerate missing secondary data: missing mapped policies are often treated as empty, while unexpected backend errors propagate.

Policy resolution starts from a comma-separated `MappedPolicy`, loads missing docs lazily when possible, and merges concrete `Policy` values with `Policy::merge_policies`. Bucket-scoped list operations call asynchronous `match_resource()` for each policy document and filter results.

User deletion has cascading behavior. Deleting a regular user first removes group memberships, then deletes child service accounts and STS/temp accounts from the store and cache. User notification deletion mirrors this cascade when a regular user disappears elsewhere.

Group membership operations maintain both `groups` and the reverse `user_group_memberships` map. Group deletion is represented by calling `remove_users_from_group()` with an empty member list; this refuses to delete non-empty groups, deletes group policy mapping, deletes group info, and removes reverse memberships.

## State and Persistence Behavior

The manager does not directly serialize IAM records except for the format marker. It persists users, groups, policies, policy mappings, and temporary accounts through `Store`. Cache updates are granular for single-object operations and wholesale for `load_all()`.

`load_user()` is a targeted cache warmup path. It tries service accounts first, loads parent regular policy when relevant, otherwise tries regular and STS identities, loads STS parent mapped policies, and pulls referenced policy docs before writing all gathered objects into cache.

`update_service_account()` mutates service-account metadata and session policy by decoding the existing session JWT with either the current secret or missing-exp allowance, adjusting claims, enforcing `MAX_SVCSESSION_POLICY_SIZE`, and resigning the token with the selected secret.

`policy_db_get_internal()` combines direct user policies with group policies from credentials groups and cache-built memberships. A disabled group currently causes an early empty result for the user path, which is a behavior to watch because one disabled group can suppress otherwise valid policies.

## Dependencies and Integration Points

The file depends on the local `Cache`, `Store`, error helpers, IAM sys constants, and object-store IAM prefix. External integration includes `rustfs_credentials`, `rustfs_policy` for policy/user/JWT primitives, `rustfs_madmin` admin DTOs, `rustfs_ecstore::global::is_first_cluster_node_local`, `rustfs_utils` env/path helpers, `tokio` for async background work, `futures::join_all`, and `tracing`.

It is consumed by admin handlers, STS flows, auth code that resolves users and policies, notification/watch paths, and the object-backed store implementation. `extract_jwt_claims*` also ties the manager to global action credentials.

## Risks and Edge Cases

`_notify()` unwraps channel send and can panic if the receiver is closed. Background reload errors are logged but do not downgrade `IamState`, so `is_ready()` may stay true after repeated reload failures.

Several lazy loads ignore missing policies by design, but missing or stale cache entries can temporarily produce empty authorization sets. `filter_policies_from_docs()` uses `pollster::block_on()` inside a synchronous helper, which can be risky if `match_resource()` ever requires an async runtime interaction that should not be blocked.

`delete_policy()` has surprising error handling: in the `is_from_notify` branch, a delete error that is not `NoSuchPolicy` removes the cache entry and returns `Ok`, while `NoSuchPolicy` is returned as an error. This may be intentional notification semantics, but it deserves review.

Service-account update depends on decoding the existing JWT before changing the secret. Expiration validation is marked TODO. Policy and group ordering is mostly HashSet-derived, so returned comma strings and member lists may be nondeterministic.

## Test Signals

Tests cover initial load failure preserving `Error` state and recording three failures, IAM format serialization/path helpers, default policy construction, JWT extraction failure paths, empty policy filtering, mapped policy behavior, user/policy/group data shape, status/session constants, credential validation, policy merge, and disabled group description preserving policy. These tests give useful regression signals for initialization, serialization, and helpers, but they do not exercise real object-store persistence, background reload races, notification cascades, or most mutating admin flows.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/oidc.rs -->
# sources/object-store/rustfs/crates/iam/src/oidc.rs

## Purpose

`oidc.rs` implements the RustFS OpenID Connect provider manager. It supports browser authorization-code flow with PKCE, ID-token verification, RP-initiated logout URL generation, web-identity JWT verification for STS-style flows, provider discovery/JWKS refresh, environment and persisted-provider configuration loading, claim-to-policy mapping, and plugin-auth HTTP metrics.

## Important APIs, Types, and Functions

`OidcProviderConfig` is the central provider configuration, including ID, enabled flag, discovery URL, client credentials, scopes, alternate audiences, redirect behavior, claim names, role policy, display name, roles/groups/email/username claims, and `hide_from_ui`. Its manual `Debug` redacts `client_secret`.

`SourcedOidcProviderConfig` pairs a config with `Env` or `Persisted` source, and `merge_oidc_provider_configs()` gives environment configs precedence over persisted configs by provider ID. `OidcProviderValidationResult`, `OidcProviderSummary`, and `OidcClaims` are public result/DTO types.

`OidcSys` owns enabled provider configs, discovered provider metadata in an `RwLock<HashMap<String, ProviderState>>`, the `OidcStateStore`, and a custom `ReqwestHttpClient`. Key methods are `new`, `empty`, `has_providers`, `list_providers`, `list_visible_providers`, `authorize_url`, `exchange_code`, `create_logout_token`, `build_logout_url`, `map_claims_to_policies`, `verify_web_identity_token`, `state_store`, and `get_provider_config`.

Provider metadata helpers include `discover_provider`, `refresh_provider_state`, `ensure_provider_state`, `ensure_provider_state_if_stale`, `get_provider_state`, and `find_provider_by_issuer`. Config helpers parse environment variables and `ServerConfig` KVS entries. Standalone helpers normalize issuer URLs, build trailing-slash candidates, decode JWT payloads, and extract string/group claims with case-insensitive lookup.

`ReqwestHttpClient` adapts reqwest to `openidconnect::AsyncHttpClient`, chooses a no-proxy client for loopback/local OIDC URIs, and records rolling success/failure/RTT samples in `OIDC_PLUGIN_AUTHN_METRICS`.

## Control Flow

`OidcSys::new()` loads effective provider configs from global server config and environment. Disabled providers are skipped. Each enabled provider is discovered immediately; discovery failures are logged and leave that provider out of the active map.

`authorize_url()` validates provider ID, ensures metadata is not stale, creates PKCE challenge/verifier and nonce, configures a `CoreClient` from stored metadata, adds configured scopes, stores an `OidcAuthSession` keyed by OAuth state, and returns the generated authorization URL.

`exchange_code()` consumes the stored state, reconstructs the provider client, exchanges the code with the stored PKCE verifier and callback redirect URI, requires an ID token, verifies signature/issuer/audience/expiry/nonce, and retries once after refreshing provider metadata if verification fails. After verification it decodes the JWT payload to support custom claims and returns normalized claims, provider ID, consumed session, and raw ID token.

`verify_web_identity_token()` decodes the untrusted JWT payload only to find `iss`, finds a discovered provider with a normalized issuer match, refreshes stale metadata, parses the JWT as `CoreIdToken`, verifies signature/issuer/audience/expiry while skipping nonce, retries after JWKS refresh on failure, and then extracts claims using provider-specific claim names.

`create_logout_token()` stores a one-time opaque handle for a raw ID token. `build_logout_url()` consumes that handle, verifies the provider and metadata, returns `Ok(None)` when no end-session endpoint is advertised, parses the stored token as `CoreIdToken`, and builds an RP-initiated logout GET URL.

## State and Persistence Behavior

OIDC provider state is process-local. Configs are loaded from environment and persisted server config but are not written here. Discovered metadata and JWKS are cached in memory with a 24-hour staleness threshold (`OIDC_JWKS_REFRESH_INTERVAL`). Refresh failures during stale checks log warnings and keep the old metadata, while verification failures force a refresh attempt and retry.

Authorization and logout state are delegated to `OidcStateStore`, which is in-memory and single-use. Browser auth sessions store provider ID, PKCE verifier, nonce, and optional post-login redirect. Logout sessions store provider ID and ID token behind an opaque token.

Metrics state is global process-local rolling data protected by `Mutex`. Poisoned locks are recovered by taking the inner value and warning.

## Dependencies and Integration Points

The implementation is built on `openidconnect` core types for discovery, clients, tokens, verifier behavior, PKCE, nonce, state, and logout request construction. It integrates with `reqwest`, `url`, `rustfs_config` OIDC constants and server config, `rustfs_policy::policy::get_claim_case_insensitive`, `OidcStateStore`, `tokio::time::sleep`, and `tracing`.

Higher-level HTTP handlers are expected to call `authorize_url`, `exchange_code`, logout methods, and provider listing APIs. STS `AssumeRoleWithWebIdentity` style logic can use `verify_web_identity_token` and `map_claims_to_policies`.

## Risks and Edge Cases

`decode_jwt_payload()` intentionally does not validate tokens and must only be trusted after verification, except for the issuer lookup preflight. The code uses the unverified issuer to select a provider, then performs actual verification; this is appropriate but should remain explicit in future changes.

Provider discovery tries both trailing-slash variants and retries transient transport errors, but a provider whose discovery document issuer differs for other reasons will be excluded at startup. Startup discovery failure only logs; `has_providers()` may be false even though config exists.

`map_claims_to_policies()` maps group and configured claim values directly to policy names with optional prefix. This is flexible but depends on administrators maintaining policy names that match external claims and avoiding broad default `role_policy` values.

The HTTP metrics name says plugin authn but records every request through the OIDC discovery/token HTTP adapter, so interpretation should account for discovery, JWKS, and token exchange calls. `list_providers()` includes hidden providers intentionally for replication/admin use; UI callers must use `list_visible_providers()`.

## Test Signals

Tests cover string and group claim extraction, case-insensitive and ambiguous claim behavior, canonical group/role merging, JWT payload decode, issuer/config URL normalization, trailing-slash discovery candidates, mocked discovery success/failure, env/persisted config parsing, env-over-persisted precedence, hidden-provider listing semantics, secret redaction in debug output, enable-state parsing, mapping claims to policies, and loopback proxy bypass. These are strong helper/config tests, but full token exchange and real ID-token signature verification depend on integration coverage outside this file.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/oidc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/oidc_state.rs -->
# sources/object-store/rustfs/crates/iam/src/oidc_state.rs

## Purpose

`oidc_state.rs` provides a small process-local state store for OIDC browser flows. It stores PKCE verifiers and nonces between authorization redirect and callback, and stores logout ID tokens behind one-time opaque handles so browser storage does not need to retain the raw ID token.

## Important APIs, Types, and Functions

`OidcAuthSession` stores `provider_id`, `pkce_verifier`, `nonce`, and optional `redirect_after`. `OidcLogoutSession` stores `provider_id` and `id_token`.

`OidcStateStore` owns two `moka::future::Cache` instances: `cache` for auth sessions and `logout_cache` for logout sessions. It also keeps `last_capacity_log_at` as an `Arc<AtomicU64>` to rate-limit capacity warnings. `new()` configures both caches with `OIDC_STATE_CAPACITY` of 10,000 entries; auth state has a 5-minute TTL and logout state has a 1-hour TTL.

Public methods are `insert`, `take`, `contains`, `insert_logout`, `take_logout`, and `contains_logout`. `Default` delegates to `new()`. Internal helpers `now_unix_secs()` and `should_log_capacity_warning()` implement warning rate limiting.

## Control Flow

The auth flow stores state via `insert()` when `OidcSys::authorize_url()` builds an authorization URL. Callback handling calls `take()`, which removes and returns the session atomically through `moka`'s `remove`. A second use of the same OAuth state returns `None`, giving the higher-level flow replay protection.

`insert()` checks the auth cache's approximate `entry_count()` after insertion. At most once per 60 seconds, it runs pending cache tasks and logs either an approaching-capacity warning at 9,000 entries or a reached-capacity warning at 10,000 entries.

Logout follows the same single-use shape with `insert_logout()` and `take_logout()`, but it uses the separate 1-hour logout cache and does not currently emit capacity warnings.

## State and Persistence Behavior

All state is in memory. Sessions are lost across process restarts, and multi-node deployments need sticky handling or a higher-level design that tolerates callback routing to a node without the original state. No secrets are written to disk by this module.

The caches are bounded. At capacity, `moka` may evict according to its policy, so under heavy login/logout pressure some outstanding states may disappear before TTL. The capacity warning is rate-limited by `AtomicU64::compare_exchange`.

## Dependencies and Integration Points

This file integrates directly with `oidc.rs`, especially `authorize_url`, `exchange_code`, `create_logout_token`, and `build_logout_url`. It depends on `moka::future::Cache`, standard atomic/time primitives, `Arc`, and `tracing::warn`.

## Risks and Edge Cases

Because state is process-local, callback routing matters in clustered deployments. Replay protection is good because `take()` removes entries, but `contains()` is non-consuming and should not be used as an authorization decision by itself.

Only auth cache insertion emits capacity warnings; logout cache saturation is silent. `entry_count()` can be approximate and expired entries may not be fully purged until pending tasks run, so warnings should be treated as operational signals rather than exact accounting.

## Test Signals

Tests cover auth insert/contains/take, missing auth state, multiple auth entries, and logout insert/contains/take. They verify single-use behavior and field preservation, but do not test TTL expiry, capacity warning rate limiting, eviction behavior, or clustered callback behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/oidc_state.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/store.rs -->
# sources/object-store/rustfs/crates/iam/src/store.rs

## Purpose

`store.rs` defines the IAM persistence abstraction and shared serialized data structures used by the IAM manager and concrete stores. It keeps `manager.rs` independent from object storage details while standardizing paths, user types, policy mappings, and group records.

## Important APIs, Types, and Functions

`pub mod object` exposes the object-backed implementation. The `Store` trait is async, cloneable, sendable, sync, and `'static`. It defines the complete persistence contract: generic IAM config save/load/delete; user identity save/load/list/delete and secret lookup; group save/load/list/delete; policy document save/load/list/delete; mapped policy save/load/list/delete; and `load_all()` for full cache hydration.

`UserType` distinguishes `Svc`, `Sts`, `Reg`, and `None`. `prefix()` maps those to IAM directory fragments, while `to_u64()` and `from_u64()` provide stable numeric conversion.

`MappedPolicy` serializes a comma-separated policy mapping. It uses `policy` as the canonical JSON field and accepts legacy `policies`. `updatedAt` is serialized as RFC3339 and accepts legacy `update_at`. `new()` sets version 1 and current timestamp; `to_slice()` and `policy_set()` split non-empty comma values.

`GroupInfo` serializes group version, status, member list, and optional RFC3339 `updatedAt` with legacy alias support. `GroupInfo::new()` creates an enabled version-1 group with current update time.

## Control Flow

This file has no runtime control flow beyond helpers. Its design shapes how callers interact with storage: `manager.rs` can request targeted loads after cache misses, perform full reloads, and save records without knowing whether the backend is object storage or another implementation.

The trait separates user identity from mapped policy, which lets regular users, STS users, service accounts, and groups share the same policy-mapping shape while being persisted under different locations by concrete stores.

## State and Persistence Behavior

`MappedPolicy` and `GroupInfo` are the persistent JSON contracts. Their serde aliases preserve compatibility with older MinIO/RustFS style records. Timestamp serialization through `rustfs_policy::serde_datetime` means output is RFC3339, not an internal numeric timestamp.

`UserType::prefix()` is a logical prefix helper; `object.rs` uses a more detailed path mapping for actual object keys. `UserType::None` exists as a neutral value and maps to empty prefix/numeric zero.

## Dependencies and Integration Points

The trait depends on the IAM `Cache`, local `Result`, `rustfs_policy::auth::UserIdentity`, `rustfs_policy::policy::PolicyDoc`, serde, `HashMap`, `HashSet`, and `time::OffsetDateTime`. It is implemented by `store/object.rs` and consumed heavily by `manager.rs`.

## Risks and Edge Cases

`MappedPolicy::to_slice()` and `policy_set()` do not trim before returning/inserting; they filter on `trim().is_empty()` but preserve original spacing in non-empty values. Inputs like `"readwrite, readonly"` may produce `" readonly"` unless higher layers trim. This can affect policy lookup.

The trait has generic async methods (`save_iam_config`, `load_iam_config`) that make object safety unlikely, so stores are used as generic type parameters rather than trait objects. That matches `IamCache<T>` but constrains dependency injection style.

`UserType::from_u64()` returns `None` for invalid values and `Some(UserType::None)` for zero, so callers must distinguish no conversion from the explicit none variant.

## Test Signals

Tests verify RFC3339 serialization and MinIO-style deserialization for `MappedPolicy` and `GroupInfo`. They provide focused compatibility coverage for persistent JSON shape, but there are no trait conformance tests here; concrete behavior is tested in backend modules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/store/object.rs -->
# sources/object-store/rustfs/crates/iam/src/store/object.rs

## Purpose

`store/object.rs` is the object-backed implementation of the IAM `Store` trait. It stores IAM metadata in the `.rustfs.sys` system bucket under `config/iam`, handles encrypted and legacy plaintext/encrypted config formats, lists IAM object trees, loads records concurrently during full reload, and writes the final cache snapshot used by the IAM manager.

## Important APIs, Types, and Functions

The file defines public `LazyLock<String>` prefixes for IAM root, users, service accounts, groups, policies, STS users, and policy DB subtrees. Path helpers build canonical object keys for identity (`identity.json`), policy (`policy.json`), group members (`members.json`), and mapped policy JSON files.

`ObjectStore` wraps `Arc<ECStore>` and implements `Store`. Public construction is `ObjectStore::new()`. `StringOrErr` is used by listing channels to stream either discovered object names or errors.

Encryption helpers are central: `decrypt_data_with_source()` accepts plaintext JSON, current IAM master-key stream encryption, old master keys, legacy secret-key encryption, and legacy `access:secret` stream encryption. `prepare_data_for_storage()` encrypts with the configured IAM master key when present, otherwise stores plaintext. `should_lazy_rewrite()`, `begin_lazy_rewrite()`, `complete_lazy_rewrite()`, `maybe_schedule_lazy_rewrite()`, and `lazy_rewrite_iam_config()` opportunistically rewrite plaintext or old-key data using the current master key with ETag preconditions.

Listing/loading helpers include `split_path`, `list_iam_config_items`, `list_all_iamconfig_items`, `load_policy_doc_concurrent`, `load_user_concurrent`, `load_mapped_policy_internal`, `load_mapped_policy_concurrent`, and `check_storage_readiness`.

## Control Flow

Generic `load_iam_config()` reads object data with metadata, decrypts it, schedules a lazy rewrite if appropriate, and deserializes JSON. Decrypt failure is logged and returned as `ConfigNotFound` while preserving the object. `save_iam_config()` serializes JSON, applies encryption if configured, and retries `save_config()` up to five times with exponential backoff. `delete_iam_config()` delegates to `delete_config()`.

User loading normalizes missing access keys to the object name, deletes expired identities and their mapped policy, and extracts JWT claims for session-token credentials. Service accounts without expiration use the missing-exp claim extractor. If claim extraction fails for temporary credentials, the temp identity and mapped policy are deleted.

List methods walk a prefix in `.rustfs.sys`, normalize Windows separators, strip the prefix, and stream names through a bounded channel. `list_all_iamconfig_items()` walks the IAM root once, classifies entries by top-level prefix, and uses a last-slash split for `policydb/*` entries so policy mapping files are grouped correctly.

`load_all()` is the full cache hydration path. It lists all IAM config objects, starts with default canned policies, loads policy docs and regular users in batches of 32 concurrent futures, loads groups and group policies, loads user mapped policies, loads service accounts into the user cache, loads STS parent policies for service accounts whose parent is not a regular user, loads STS identities and STS mapped policies, and finally replaces cache entities only if the cache still matches the snapshot captured at start. If concurrent cache mutations occurred, the full reload commit is skipped with a warning.

## State and Persistence Behavior

Persistent IAM state lives under `.rustfs.sys/config/iam`: regular users under `users/<name>/identity.json`, service accounts under `service-accounts/<name>/identity.json`, STS under `sts/<name>/identity.json`, groups under `groups/<name>/members.json`, policies under `policies/<name>/policy.json`, and mapped policies under `policydb/users`, `policydb/sts-users`, `policydb/service-accounts`, or `policydb/groups`.

The store preserves backward compatibility with plaintext JSON and legacy encryption. When a current IAM master key is configured, old formats are lazily rewritten after reads. Rewrites are protected by a global `IAM_LAZY_REWRITE_TRACKER` to avoid duplicate rewrites and by object ETag `If-Match` preconditions to avoid overwriting newer data. Failed rewrites enter a 60-second cooldown.

`load_policy()` fills `create_date` and `update_date` from object modification time when loading version-0 policy documents. Full reload defaults include canned policies even when no policy objects exist.

## Dependencies and Integration Points

This module integrates with `rustfs_ecstore` config helpers (`read_config_with_metadata`, `read_config_no_lock`, `save_config`, `save_config_with_opts`, `delete_config`), object walking, `ECStore`, `ObjectOptions`, and HTTP preconditions. It records system-path failures through `rustfs_io_metrics` and classifies failures through `rustfs_ecstore::error`.

It depends on IAM `Cache`/`CacheEntity`, errors, keyring, manager JWT helpers/default policies, `rustfs_crypto`, `rustfs_credentials`, `rustfs_policy`, `tokio` channels/spawn, cancellation tokens, `join_all`, and tracing. `manager.rs` relies on this implementation for startup load, targeted cache repair, and all IAM persistence.

## Risks and Edge Cases

`check_storage_readiness()` requires `format.json` to exist before saving identities. This protects boot-time writes but can block writes if format initialization failed or if a deployment intentionally lacks the probe object.

`load_iam_config()` maps decrypt failures to `ConfigNotFound`, which prevents deletion but can make corruption indistinguishable from absence to callers. Some higher-level paths then convert that to `NoSuchUser` or `NoSuchPolicy`.

`save_iam_config()` increments attempts before computing backoff, so the first retry waits 400 ms rather than the documented 200 ms. The loop allows five retry attempts after the initial failure before returning the final error.

Batch loops in `load_all()` call concurrent loaders with the full remaining vector before `split_off(32)`, so when there are 32 or more entries the first iteration may load more than 32 despite the apparent batching intent. This is worth checking for large IAM installations.

Listing is asynchronous and channel based; errors cancel the token, but spawned tasks may continue briefly. Full reload commit uses snapshot matching to avoid overwriting concurrent mutations, but this means a large reload can do all I/O and then drop results if the cache changed.

## Test Signals

Tests cover plaintext JSON acceptance, legacy secret-key and access-secret encryption compatibility, corrupt and short encrypted data failures, plaintext storage when no IAM master key is configured, current master-key encryption round trip, and old-key fallback during rotation. These tests strongly cover crypto compatibility helpers. There is no direct test coverage here for object walking, full `load_all()` cache replacement, storage readiness probing, lazy rewrite ETag behavior, save retry timing, or expired/temp identity deletion against a real or fake `ECStore`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/store/object.rs -->

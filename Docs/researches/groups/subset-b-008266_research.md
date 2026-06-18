# Research: subset-b-008266

Grouped research for Keystone and KMS files under `sources/object-store/rustfs/crates`. Each section is source-tree aligned and intended for deterministic reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/Cargo.toml -->
# sources/object-store/rustfs/crates/keystone/Cargo.toml

## Purpose
This manifest defines the `rustfs-keystone` crate, an OpenStack Keystone authentication integration for RustFS. It packages token validation, EC2 credential support, identity mapping, and Tower middleware into a reusable authentication crate.

## Important APIs, Types, and Functions
The manifest exposes a library crate named `rustfs-keystone` and registers one integration test target named `integration` at `tests/integration/mod.rs`. It depends on async/runtime and web middleware crates (`tokio`, `reqwest`, `tower`, `http`, `hyper`, `http-body`, `http-body-util`, `bytes`, `futures`), serialization/error/logging crates (`serde`, `serde_json`, `thiserror`, `tracing`, `time`, `moka`), and RustFS internal contracts (`rustfs-credentials`, `rustfs-policy`, `rustfs-utils`). Dev dependencies add `tower` utilities, `tokio` test utilities, and `temp-env`.

## Control Flow and Integration Points
The dependency graph matches the crate's main flow: environment config is loaded through `rustfs-utils`, Keystone HTTP calls are made with `reqwest`, validated identities are converted into `rustfs-credentials::Credentials`, roles map to `rustfs-policy`, and middleware plugs into Tower/Hyper request handling. The explicit integration test target centralizes tests through `tests/integration/mod.rs`.

## State and Persistence Behavior
The manifest itself has no runtime state. By enabling `moka`, `time`, and HTTP stack dependencies, it supports in-memory token caching and async Keystone API interactions implemented in source files.

## Dependencies
All dependencies are workspace-pinned. `hyper` is requested with `server`; middleware uses `http-body` and `http-body-util` to erase body types. `moka` is used for token caches. `temp-env` supports environment-driven configuration tests.

## Risks and Edge Cases
The manifest enables broad `tokio` features and `hyper` server features, which may increase compile surface for a focused auth crate. `reqwest` TLS behavior is controlled at runtime in `client.rs`; the manifest does not constrain TLS features here. Test coverage depends on the custom integration target and unit tests in modules.

## Test Signals
The `[[test]]` target ensures `tests/integration/mod.rs` runs as a single integration suite. Module-level unit tests exercise config parsing, identity mapping, middleware task-local storage, and token-to-credential conversion.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/src/auth.rs -->
# sources/object-store/rustfs/crates/keystone/src/auth.rs

## Purpose
`auth.rs` implements `KeystoneAuthProvider`, the high-level bridge from Keystone tokens or EC2-style credentials into RustFS `Credentials`. It owns token caches, calls `KeystoneClient`, and constructs RustFS credential claims used by downstream auth and policy logic.

## Important APIs, Types, and Functions
`KeystoneAuthProvider::new` wraps a `KeystoneClient` in `Arc` and creates two `TokenCache` instances: one keyed by Keystone token string and one keyed by EC2 access/signature. `without_cache` disables cache checks for tests. `authenticate_with_token` validates an `X-Auth-Token`, rejects expired tokens, caches successful responses, and returns RustFS credentials. `authenticate_with_ec2` validates EC2 credentials through Keystone, converts the returned `EC2Credential` into a minimal `KeystoneToken`, caches it, and returns credentials. Helper methods include `invalidate_token`, `clear_caches`, `is_admin`, `get_project_id`, and `get_user_id`.

## Control Flow
Token authentication first checks `token_cache` when enabled, validates cache expiry with `KeystoneToken::is_expired`, then calls `client.validate_token`. After validation, it separately checks expiration and inserts the token into cache. EC2 authentication builds a cache key from `access_key:signature`, validates via `client.validate_ec2_credentials`, converts to a synthetic token, and caches the synthetic token.

## State and Persistence Behavior
All state is in-memory. `TokenCache` is a `moka::future::Cache` configured by constructor capacity/TTL. Cache entries store cloned `Arc<KeystoneToken>` values and can be invalidated per token or globally. No identity mapping is persisted.

## Dependencies and Integration Points
The provider depends on `KeystoneClient`, `KeystoneToken`, `EC2Credential`, `TokenCache`, and `KeystoneError` from the crate. It emits `rustfs_credentials::Credentials` with Keystone-specific claims in `serde_json::Value` form. Middleware calls `authenticate_with_token`; future SigV4 paths can call `authenticate_with_ec2`.

## Risks and Edge Cases
`ec2_to_keystone_token` is explicitly a placeholder: it sets username to `user_id`, project name to `project_id`, default role to `Member`, and a 24-hour expiry without fetching full Keystone user/project/role data. EC2 cache keys include the signature but not `string_to_sign`, which may be insufficient if the same access key/signature pair can arise over different signing strings. `keystone_token_to_credentials` uses an empty secret key and `keystone:<user_id>` access key, so downstream code must understand that session/token auth differs from normal S3 credentials. The token returned by `parse_token_v3` is currently empty, so `session_token` may be empty after live validation.

## Test Signals
Unit tests verify Keystone token conversion into RustFS credentials and admin role detection with case-insensitive `admin`. There are no tests using a mock Keystone server for success/failure cache paths or EC2 authentication.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/src/auth.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/src/client.rs -->
# sources/object-store/rustfs/crates/keystone/src/client.rs

## Purpose
`client.rs` implements `KeystoneClient`, the HTTP client for Keystone token validation, EC2 credential validation/listing, and admin-token acquisition. It is the network-facing layer used by `KeystoneAuthProvider`.

## Important APIs, Types, and Functions
`KeystoneClient::new` configures a `reqwest::Client`, Keystone auth URL/version, optional admin credentials, admin token cache, domain, and TLS verification behavior. `validate_token` dispatches between v3 and v2.0; v3 is implemented by `validate_token_v3`, while v2.0 returns `UnsupportedVersion`. `parse_token_v3` extracts user, project, domain, roles, `expires_at`, and `issued_at` from Keystone JSON. `validate_ec2_credentials` posts to `/v3/ec2tokens`. `get_ec2_credentials` uses `get_admin_token` to list OS-EC2 credentials. `clear_admin_token` clears cached admin auth.

## Control Flow
For token validation, the client sends `GET {auth_url}/v3/auth/tokens` with both `X-Auth-Token` and `X-Subject-Token` set to the user token. 404 and 401 become `InvalidToken`; other non-success statuses become `AuthenticationFailed`; successful JSON is parsed into `KeystoneToken`. For admin operations, `get_admin_token` first checks an async `RwLock<Option<AdminToken>>`, authenticates with password if missing/expired, reads `X-Subject-Token` from response headers, parses token expiry from the body, and caches it.

## State and Persistence Behavior
Admin token state is process-local in `Arc<RwLock<Option<AdminToken>>>`. User token and EC2 caches live in `auth.rs`, not this client. No disk persistence occurs. Timeout is hard-coded to 30 seconds in the reqwest builder, independent of `KeystoneConfig::timeout_seconds`.

## Dependencies and Integration Points
The client depends on `reqwest`, `serde_json`, `time`, `tokio::sync::RwLock`, and tracing. It integrates with Keystone v3 endpoints `/v3/auth/tokens`, `/v3/ec2tokens`, and `/v3/users/{user}/credentials/OS-EC2`. `EC2Credential::parse_access_key` is used as a fallback to infer user/project identifiers from an access key.

## Risks and Edge Cases
`parse_token_v3` sets `KeystoneToken.token` to `String::new()` rather than preserving the subject token, which affects credentials' `session_token`. TLS verification can be disabled with `danger_accept_invalid_certs`, and only a warning protects production use. Admin auth requires username/password but AppCred or token auth are not supported. `validate_ec2_credentials` discards the returned body and infers user/project from the access key, so it may not reflect authoritative Keystone EC2 credential metadata. v2.0 is advertised by config but unsupported at runtime.

## Test Signals
The unit test only checks constructor field assignment. Network behavior, parsing variants, admin token caching, TLS behavior, and EC2 credential parsing are not covered by active tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/src/client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/src/config.rs -->
# sources/object-store/rustfs/crates/keystone/src/config.rs

## Purpose
`config.rs` defines environment-driven configuration for Keystone integration. It controls whether Keystone auth is enabled, how Keystone is contacted, cache behavior, tenant prefixing, implicit tenants, and optional role-to-policy mappings.

## Important APIs, Types, and Functions
`KeystoneConfig` contains fields for `enable`, `auth_url`, `version`, admin credentials/project/domain, `verify_ssl`, cache size/TTL, tenant prefixing, implicit tenants, timeout, and `role_mappings`. `RoleMapping` maps Keystone role names to RustFS policy names. `from_env` reads `RUSTFS_KEYSTONE_*` variables. `get_version`, `get_cache_ttl`, `get_timeout`, `get_admin_domain`, and `validate` provide typed access and validation. `Default` represents Keystone disabled with v3 defaults and caching/tenant prefix enabled.

## Control Flow
`from_env` first reads `RUSTFS_KEYSTONE_ENABLE`; if disabled, it returns `Default`. If enabled, it requires `RUSTFS_KEYSTONE_AUTH_URL`, then reads optional admin credentials and booleans/numerics with defaults. `validate` no-ops when disabled, requires non-empty `auth_url` when enabled, validates version, and warns if admin credentials are missing.

## State and Persistence Behavior
Configuration is immutable data after construction and has no persistence. Runtime caches and clients consume its values. `role_mappings` is present but `from_env` never populates it.

## Dependencies and Integration Points
The file uses `rustfs_utils` environment helpers and converts version strings to `KeystoneVersion` for `KeystoneClient`. `KeystoneAuthProvider` consumes cache settings and `KeystoneIdentityMapper` can consume tenant-prefix and role mapping fields.

## Risks and Edge Cases
`timeout_seconds` is exposed but `KeystoneClient::new` currently uses a fixed 30-second reqwest timeout, so the config value may be ignored unless wired elsewhere. Enabling v2.0 passes validation but token validation later returns `UnsupportedVersion`. Missing admin credentials only warn even though EC2 credential listing requires them. Environment configuration cannot define `role_mappings`.

## Test Signals
Unit tests cover defaults, version parsing, full environment loading via `temp_env`, and invalid version handling. They do not cover `validate` warnings or runtime consumption of timeout/role mappings.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/src/error.rs -->
# sources/object-store/rustfs/crates/keystone/src/error.rs

## Purpose
`error.rs` defines the Keystone crate's error taxonomy and result alias. It centralizes authentication, transport, parsing, configuration, authorization, and service-state failures.

## Important APIs, Types, and Functions
`pub type Result<T> = std::result::Result<T, KeystoneError>` is the crate-wide result type. `KeystoneError` variants include `InvalidToken`, `TokenExpired`, `InvalidCredentials`, `AuthenticationFailed`, `HttpError`, `ParseError`, `ConfigError`, `UnsupportedVersion`, project/user not found variants, `InsufficientPermissions`, `InternalError`, `Timeout`, and `ServiceUnavailable`. `is_retryable` classifies timeout/service-unavailable/HTTP errors. `is_auth_error` classifies token/credential/authentication failures.

## Control Flow and Integration Points
Client code maps HTTP send failures into `HttpError`, bad Keystone responses into `InvalidToken`, `InvalidCredentials`, or `AuthenticationFailed`, and JSON failures into `ParseError`. Config parsing emits `ConfigError`. Middleware uses the display string in XML error responses.

## State and Persistence Behavior
No state or persistence. Errors are displayable through `thiserror`.

## Dependencies
The only direct dependency is `thiserror::Error`.

## Risks and Edge Cases
The retry classifier treats every `HttpError` as retryable, even errors that may represent permanent DNS/TLS/configuration failures. `Timeout` and `ServiceUnavailable` variants exist but the current client often maps transport errors into `HttpError`, so specific retry semantics may be underused. Error strings can be exposed in middleware XML details after XML escaping.

## Test Signals
No direct unit tests exist for classification helpers. Behavior is indirectly exercised where other modules assert error paths.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/src/identity.rs -->
# sources/object-store/rustfs/crates/keystone/src/identity.rs

## Purpose
`identity.rs` maps Keystone identity concepts to RustFS authorization and multi-tenant storage concepts. It translates Keystone roles to policy names, applies/removes project ID bucket prefixes, and provides simplified role-based permission checks.

## Important APIs, Types, and Functions
`KeystoneIdentityMapper` stores an `Arc<KeystoneClient>`, a `role_policy_map`, and an `enable_tenant_prefix` flag. `new` seeds default mappings for `admin`, `Admin`, `Member`, `_member_`, `ResellerAdmin`, `SwiftOperator`, `objectstore:admin`, and `objectstore:creator`. Public methods include `add_role_mapping`, `add_role_mappings`, `map_roles_to_policies`, `apply_tenant_prefix`, `remove_tenant_prefix`, `is_project_bucket`, `extract_project_id`, `create_default_policies`, `has_permission`, and `is_tenant_prefix_enabled`.

## Control Flow
Role mapping is a direct hash lookup; unmapped roles are ignored. Bucket prefixing prepends `<project_id>:` when enabled and a project ID is present. `is_project_bucket` allows all buckets when prefixing is disabled, requires a matching prefix when a project ID is present, and allows only unprefixed buckets when no project ID is present. `has_permission` first grants admin/reseller-admin, then applies broad action prefix checks for mapped read-write and read-only policies.

## State and Persistence Behavior
The mapper is in-memory and mutable only through explicit role mapping methods. The stored client is currently unused but preserves room for future Keystone lookups.

## Dependencies and Integration Points
It depends on `rustfs_policy::policy::Policy` for parsing default policy JSON. It consumes roles produced in `KeystoneToken`/`Credentials` and bucket project IDs extracted by `KeystoneAuthProvider`.

## Risks and Edge Cases
Bucket prefixing uses a colon separator and simple string matching; bucket names containing colons may be treated as project-prefixed. `extract_project_id` returns the substring before the first colon without validating it. `create_default_policies` silently skips invalid policy JSON parse failures. `has_permission` is intentionally simplified and resource-agnostic: it ignores the `_resource` argument and grants based only on action prefixes.

## Test Signals
Unit tests cover tenant prefix apply/remove, project bucket checks, project ID extraction, role mapping, simplified permission checks, and custom mapping insertion. They do not validate parsed `Policy` semantics beyond successful creation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/src/identity.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/src/lib.rs -->
# sources/object-store/rustfs/crates/keystone/src/lib.rs

## Purpose
`lib.rs` is the public crate surface for RustFS Keystone integration. It documents supported features, declares modules, re-exports the primary types, and defines core shared data structures such as `KeystoneToken`, `EC2Credential`, `KeystoneVersion`, and `TokenCache`.

## Important APIs, Types, and Functions
Public modules are `auth`, `client`, `config`, `error`, `identity`, and `middleware`. Re-exports include `KeystoneAuthProvider`, `KeystoneClient`, `KeystoneConfig`, `RoleMapping`, `KeystoneError`, `Result`, `KeystoneIdentityMapper`, `KEYSTONE_CREDENTIALS`, and `KeystoneAuthLayer`. `KeystoneVersion` supports `V2_0` and `V3`. `KeystoneToken` stores token identity, project/domain, roles, and timestamps with helpers `is_expired`, `has_role`, and `is_admin`. `EC2Credential` stores EC2 access/secret/user/project/trust data and parses access keys. `TokenCache` wraps `moka::future::Cache<String, Arc<KeystoneToken>>`.

## Control Flow and Integration Points
Downstream code imports the crate-level re-exports to configure clients, validate tokens, install middleware, and inspect task-local Keystone credentials. Token expiry and role checks are shared by auth provider and callers. EC2 credential parsing supports `client.rs` fallback behavior after Keystone EC2 validation.

## State and Persistence Behavior
`TokenCache` stores token info in memory with capacity and TTL configured at construction. It supports async get/insert/invalidate/clear. The module itself has no disk persistence.

## Dependencies
The crate root uses `moka`, `serde`, `time`, `Arc`, and `Duration`. It relies on `time::OffsetDateTime` for token lifetimes.

## Risks and Edge Cases
`KeystoneToken::has_role` is case-sensitive, while `is_admin` checks only exact `admin` or `Admin`; `KeystoneAuthProvider::is_admin` is more permissive and also accepts `reseller_admin`. `EC2Credential::parse_access_key` always returns `Some`, even for empty strings, and only treats exactly one colon as a user/project separator. `TokenCache::clear` invalidates all entries but does not call `run_pending_tasks`, so invalidation timing follows moka's async behavior.

## Test Signals
There are no direct tests in `lib.rs`; shared types are covered indirectly by `auth.rs`, `client.rs`, middleware, and identity unit tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/src/middleware.rs -->
# sources/object-store/rustfs/crates/keystone/src/middleware.rs

## Purpose
`middleware.rs` implements Tower middleware that intercepts HTTP requests with Keystone token headers, validates them, and exposes resulting RustFS credentials through task-local storage for downstream request handlers.

## Important APIs, Types, and Functions
`KEYSTONE_CREDENTIALS` is a Tokio task-local `Option<Credentials>`. `KeystoneAuthLayer` is a Tower `Layer` holding an optional `Arc<KeystoneAuthProvider>`. `KeystoneAuthMiddleware<S>` implements `Service<Request<Incoming>>` and returns responses with an erased `UnsyncBoxBody`. Helpers include `extract_keystone_token`, which reads `X-Auth-Token`, and `xml_escape`, which escapes XML error details.

## Control Flow
If no provider is configured, the middleware passes the request through unchanged except for body boxing. If a provider exists, it checks `X-Auth-Token`. With a token, it calls `authenticate_with_token`; success scopes `KEYSTONE_CREDENTIALS` to `Some(credentials)` while calling the inner service. Failure returns an immediate 401 XML response with `WWW-Authenticate: Keystone`. If no token is present, the request passes through to normal S3 authentication.

## State and Persistence Behavior
State is request-scoped via Tokio task-local storage and provider-scoped via the provider's caches. No middleware state is persisted. The task-local scope ends after the inner service future resolves.

## Dependencies and Integration Points
The middleware depends on Hyper request bodies, HTTP response/status types, Tower `Layer`/`Service`, `http-body-util` for body conversion, and `rustfs_credentials::Credentials`. It integrates with upstream HTTP routing and downstream auth handlers that call `KEYSTONE_CREDENTIALS.try_with`.

## Risks and Edge Cases
Only `X-Auth-Token` is supported; Swift's `X-Storage-Token` is explicitly deferred. A malformed header value is ignored because `to_str().ok()` returns `None`, causing fallback to S3 auth rather than a 400/401. When Keystone auth fails, fallback is intentionally disabled. XML error details include the display string from the error after escaping; this can reveal operational details. The middleware clones `inner` per call, which is standard Tower practice only if the wrapped service is clone-safe for concurrent use.

## Test Signals
Unit tests cover layer construction, header extraction, XML escaping, and task-local scope behavior. Comments state valid/invalid token tests require a mock Keystone server and are not yet implemented. Integration tests also focus on task-local behavior rather than live middleware HTTP calls.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/src/middleware.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/tests/integration/middleware_tests.rs -->
# sources/object-store/rustfs/crates/keystone/tests/integration/middleware_tests.rs

## Purpose
This integration test module verifies Keystone middleware construction and Tokio task-local credential behavior from outside the crate, using the public `rustfs_keystone` API.

## Important APIs, Types, and Functions
Helpers `create_test_auth_provider` and `create_test_credentials` construct a disabled-real-network provider and test `Credentials`. Tests cover `KeystoneAuthLayer::new`, `KEYSTONE_CREDENTIALS.scope`, task isolation across spawned Tokio tasks, `None` scopes, claims preservation, nested scopes, auth provider construction with cache enabled/disabled, sequential scopes, and outside-scope access.

## Control Flow
Most async tests enter a task-local scope with `Some(Credentials)` or `None`, read `KEYSTONE_CREDENTIALS` using `try_with`, and assert values or absence. The isolation test spawns two concurrent tasks with different scoped credentials and confirms each task sees its own parent user. The nested-scope test confirms inner scope overrides outer scope while active.

## State and Persistence Behavior
The tests create only in-memory credentials and providers. They do not start a Keystone server or persist anything. `create_test_auth_provider` disables SSL verification against localhost but never sends requests.

## Dependencies and Integration Points
The file imports `rustfs_credentials::Credentials`, public middleware task-local storage, and public `KeystoneAuthLayer`, `KeystoneAuthProvider`, `KeystoneClient`, and `KeystoneVersion`. It validates that external crates can use the public API surface.

## Risks and Edge Cases
These tests do not exercise actual Tower service invocation, HTTP body boxing, 401 responses, XML escaping, header parsing, or Keystone network validation. Test credentials use a claim shape under `"keystone"` that differs from production `auth.rs`, which inserts flat keys such as `"keystone_user_id"` and `"keystone_roles"`.

## Test Signals
The suite gives strong signal for task-local scoping semantics and public constructor compatibility. It gives weak signal for end-to-end middleware authentication correctness.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/tests/integration/middleware_tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/tests/integration/mod.rs -->
# sources/object-store/rustfs/crates/keystone/tests/integration/mod.rs

## Purpose
`mod.rs` is the integration-test entrypoint declared by `Cargo.toml`. It currently includes the `middleware_tests` module.

## Important APIs, Types, and Functions
The file has one module declaration: `mod middleware_tests;`. It contains no direct tests or helper functions.

## Control Flow and Integration Points
Cargo runs this file as the `integration` test target. The module declaration pulls in `middleware_tests.rs`, allowing that file's tests to run as an external crate integration suite.

## State and Persistence Behavior
No runtime state or persistence.

## Dependencies
Dependencies are inherited from the integration test target and the child module.

## Risks and Edge Cases
Only middleware integration tests are wired. Other Keystone integration areas, such as client parsing against a mock Keystone API or identity mapper behavior from an external crate, are not represented here.

## Test Signals
The existence of this file confirms the integration suite is intentionally scoped to middleware tests at present.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/keystone/tests/integration/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/Cargo.toml -->
# sources/object-store/rustfs/crates/kms/Cargo.toml

## Purpose
This manifest defines `rustfs-kms`, the RustFS Key Management Service crate for key generation, storage, backend integration, object encryption, and cryptographic helpers.

## Important APIs, Types, and Functions
The manifest configures package metadata, workspace lint inheritance, crypto dependencies (`aes-gcm`, `chacha20poly1305`, `rand`, `sha2`, `base64`, `zeroize`), async/runtime dependencies (`async-trait`, `tokio`, `uuid`, `jiff`), configuration/serialization/error/logging dependencies, caching via `moka`, and Vault access through `reqwest` and `vaultrs`. Linux targets additionally enable `tokio` `io-uring`.

## Control Flow and Integration Points
The dependency set supports local file backends, Vault KV2, Vault Transit, dynamic API configuration, caching, and object encryption services. Internal RustFS dependencies include `rustfs-utils` and `rustfs-security-governance`.

## State and Persistence Behavior
The manifest itself has no runtime state. It enables backends that persist key material locally or in Vault and a cache layer that stores metadata in memory.

## Dependencies
All versions come from the workspace. Dev dependencies include `tempfile` and `temp-env` for local backend and configuration tests.

## Risks and Edge Cases
The crate includes multiple cryptographic and backend modes in one build with no feature gating beyond an empty default feature set. `tokio` is enabled with `full`, and Linux adds `io-uring`, increasing platform-specific build surface. Vault functionality relies on `vaultrs` and `reqwest`; operational TLS/auth behavior is controlled in configuration source files.

## Test Signals
The manifest does not define explicit integration targets in this subset. Unit tests in backend, cache, and API modules are discovered normally.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/examples/kms_local_demo.rs -->
# sources/object-store/rustfs/crates/kms/examples/kms_local_demo.rs

## Purpose
`kms_local_demo.rs` is an executable walkthrough for the local KMS backend. It demonstrates global service initialization, local backend configuration, key creation, data-key generation, object encryption/decryption, key listing, cache stats, health check, and shutdown.

## Important APIs, Types, and Functions
The example imports request/response-facing types such as `CreateKeyRequest`, `DescribeKeyRequest`, `GenerateDataKeyRequest`, `ListKeysRequest`, `EncryptionAlgorithm`, `KeySpec`, `KeyUsage`, `KmsConfig`, and `init_global_kms_service_manager`. It uses `KmsConfig::local(...).with_default_key(...).with_cache(true)`, `service_manager.configure`, `start`, `stop`, and `get_global_encryption_service`.

## Control Flow
The demo initializes the global service manager, creates `examples/local_data` if missing, configures a local backend with a default key, starts the service, creates a master key, describes it, optionally generates a data key, encrypts a plaintext object through `encrypt_object`, decrypts it through `decrypt_object`, asserts round-trip equality, lists keys, prints cache stats, checks backend health, and stops the service.

## State and Persistence Behavior
The local backend writes persistent key files under `examples/local_data`. The example creates or reuses that directory but does not remove it. It stores cache state only for the life of the process through the configured service.

## Dependencies and Integration Points
It integrates with the global KMS service manager and high-level object encryption service, not the backend traits directly. It uses `std::io::Cursor` and `tokio::io::AsyncReadExt` to feed/read object data.

## Risks and Edge Cases
The example writes into the repository's `examples/local_data` path, so repeated runs leave keys behind and may collide on fixed key names. Console text includes user guidance and assumes high-level `encrypt_object` will create/use keys as needed. It does not configure a local master key for encryption-at-rest in the shown `KmsConfig::local` call unless defaults do so elsewhere.

## Test Signals
This is an example, not an automated test. It can serve as a manual smoke test for local backend and object encryption round trips.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/examples/kms_local_demo.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/examples/kms_vault_kv_demo.rs -->
# sources/object-store/rustfs/crates/kms/examples/kms_vault_kv_demo.rs

## Purpose
`kms_vault_kv_demo.rs` is an executable walkthrough for the Vault KV2-backed KMS configuration. It demonstrates using Vault as persistent key storage while exercising the same high-level encryption workflow as the local demo.

## Important APIs, Types, and Functions
It uses the same public KMS API types as the local demo plus `KmsError` and `url::Url`. Vault address is read from `RUSTFS_KMS_VAULT_ADDRESS` with a localhost default, and the token is read from `RUSTFS_KMS_VAULT_TOKEN` with a development fallback of `dev-token`. Configuration uses `KmsConfig::vault(vault_url, vault_token).with_default_key(...).with_cache(true)`.

## Control Flow
The demo initializes and configures the global KMS service with Vault, starts it, obtains the global encryption service, tries to describe a fixed master key, creates it if `KmsError::KeyNotFound` occurs, describes it again, optionally generates a data key, encrypts and decrypts object data, verifies round-trip equality, lists keys, prints cache stats, checks Vault health, stops the service, and prints Vault inspection tips.

## State and Persistence Behavior
Keys persist in Vault under the configured KV path. The fixed key ID `demo-key-master-1` is reused across runs, so the example handles existing keys. Process-local cache is enabled. No local files are written by this example except normal build/runtime outputs.

## Dependencies and Integration Points
The example integrates with a running Vault server, Vault token auth, the global KMS manager, and the object encryption service. It demonstrates error-specific handling for `KeyNotFound`.

## Risks and Edge Cases
The default token `dev-token` and localhost Vault address are development-oriented. Production use requires a real token and TLS/auth hardening. The example assumes the Vault backend supports the high-level object flow; it does not validate Vault mount setup beyond health/key operations. The final tips mention paths under `secret/rustfs/kms/keys`, matching KV2 storage assumptions rather than the dedicated Transit backend.

## Test Signals
This is a manual smoke/demo program. It gives practical integration guidance but no automated assertion beyond plaintext/decrypted equality during execution.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/examples/kms_vault_kv_demo.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/api_types.rs -->
# sources/object-store/rustfs/crates/kms/src/api_types.rs

## Purpose
`api_types.rs` defines request/response DTOs for dynamic KMS configuration, service lifecycle/status reporting, and AWS-KMS-like key management operations. It is the contract layer between API handlers/service management and backend configuration/types.

## Important APIs, Types, and Functions
Configuration requests include `ConfigureLocalKmsRequest`, `ConfigureVaultKmsRequest`, `ConfigureVaultTransitKmsRequest`, and tagged enum `ConfigureKmsRequest`. Lifecycle/status types include `ConfigureKmsResponse`, `StartKmsRequest`, `StartKmsResponse`, `StopKmsResponse`, `KmsStatusResponse`, `KmsConfigSummary`, `CacheSummary`, and `BackendSummary`. Key operations include `CreateKeyRequest/Response`, `DeleteKeyRequest/Response`, `ListKeysRequest/Response`, `DescribeKeyRequest/Response`, `CancelKeyDeletionRequest/Response`, `UpdateKeyDescriptionRequest/Response`, `TagKeyRequest/Response`, and `UntagKeyRequest/Response`. Conversion methods turn configuration requests into `KmsConfig`.

## Control Flow
Serde deserializes `ConfigureKmsRequest` by `backend_type`, accepting aliases for local, Vault KV2, and Vault Transit. Vault auth deserialization goes through strict `StrictVaultAuthMethod` to reject unknown fields. `to_kms_config` methods fill defaults for timeout, retries, cache size/TTL, mount names, key paths, TLS skip settings, and `allow_insecure_dev_defaults`. `KmsConfigSummary::from` redacts sensitive values by emitting only booleans and auth method type.

## State and Persistence Behavior
These are pure data types and converters. They do not persist state, but the resulting `KmsConfig` controls backend persistence and cache behavior. Debug for local configure requests redacts `master_key`; Vault auth secret redaction depends on `VaultAuthMethod`'s debug implementation.

## Dependencies and Integration Points
The module depends on `crate::config` for backend config structs, `crate::service_manager::KmsServiceStatus`, and `crate::types::{KeyMetadata, KeyUsage}`. API handlers can deserialize JSON into these types and call `to_kms_config`.

## Risks and Edge Cases
There is a visible contract tension: the earlier imported `ListKeysRequest` from `crate::types` is used in backends, while this file also defines API-facing `ListKeysRequest`/`ListKeysResponse` near the bottom with a different shape. That can confuse imports and documentation. `allow_insecure_dev_defaults` defaults to false, which tests confirm, but callers must surface validation errors clearly. `DescribeKeyResponse` and other bottom DTOs include `success/message` fields in this file's API-facing shape, while backend trait responses in the read source use type aliases/imports from `crate::types`; keeping names distinct is important.

## Test Signals
Unit tests cover backend type aliases, Vault Transit deserialization, local deserialization, rejection of insecure defaults unless opted in, unknown field rejection, start request strictness, Vault Transit summary contents, debug redaction for configure requests, and status summary omission of secrets.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/api_types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/backends/local.rs -->
# sources/object-store/rustfs/crates/kms/src/backends/local.rs

## Purpose
`local.rs` implements a local file-backed KMS backend. It stores master key metadata and encrypted or base64-encoded key material as JSON files and provides both the low-level `KmsClient` trait and the simplified `KmsBackend` wrapper.

## Important APIs, Types, and Functions
`LocalKmsClient` holds `LocalConfig`, an in-memory `RwLock<HashMap<String, MasterKeyInfo>>` cache, optional `Aes256Gcm` master cipher, and `AesDekCrypto`. `StoredMasterKey` is the on-disk JSON shape. Core helpers include `new`, `derive_master_key`, `master_key_path`, `decode_stored_key`, `load_master_key`, `save_master_key`, `get_key_material`, `encrypt_with_master_key`, and `decrypt_with_master_key`. `LocalKmsBackend::new` validates `KmsConfig` and wraps a client.

## Control Flow
Client construction creates the key directory and derives an AES-256-GCM cipher from configured `master_key` using SHA-256 plus a static salt. Key creation validates algorithm, generates key material, saves it atomically through a temp file and rename, and caches metadata. Data-key generation creates random DEK material, encrypts it with the master key via `AesDekCrypto`, wraps it in `DataKeyEnvelope`, and serializes the envelope as ciphertext. Decryption parses the envelope, checks encryption context compatibility, and decrypts the encrypted DEK. Listing scans `.key` files and applies status/usage filters. The backend wrapper converts between client-level `KeyInfo`/`MasterKeyInfo` and API-level metadata responses.

## State and Persistence Behavior
Master keys persist as `<key_id>.key` JSON under `LocalConfig.key_dir`. When `master_key` is configured, stored key material is encrypted with AES-256-GCM and a 12-byte nonce; otherwise raw key material is base64 encoded with a warning that keys are not encrypted at rest. Writes are atomic via `.tmp` then rename, with optional Unix file permissions applied to the temp file. Metadata is cached in memory but key material is re-read from disk for encryption/decryption.

## Dependencies and Integration Points
The backend depends on RustFS KMS config, types, error handling, `AesDekCrypto`, `generate_key_material`, `serde_json`, `jiff::Zoned`, `tokio::fs`, and crypto/base64/rand crates. It implements both `KmsClient` and `KmsBackend`, so it can be used by lower-level KMS code and the service manager.

## Risks and Edge Cases
Several low-level state transitions (`enable_key`, `disable_key`, `schedule_key_deletion`, `cancel_key_deletion`, `rotate_key`) regenerate key material, which can make existing encrypted data undecryptable if those methods are used directly. The simplified backend wrapper's scheduled deletion/cancel paths explicitly preserve existing key material, creating different safety semantics than the lower-level trait. `encrypt` returns raw AEAD ciphertext without carrying nonce, and tests note direct decrypt of `encrypt()` results is not implemented. `describe_key` can serve stale metadata from cache if files are changed externally. Key IDs are used directly in file names without visible path sanitization in this file.

## Test Signals
Unit tests cover key lifecycle, data-key generation/decryption with context, direct encryption response shape, and loading a legacy RFC3339 timestamp. They do not cover deletion wrapper semantics, path traversal, concurrent writes, cache invalidation, or encryption-at-rest failure modes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/backends/local.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/backends/mod.rs -->
# sources/object-store/rustfs/crates/kms/src/backends/mod.rs

## Purpose
`backends/mod.rs` defines the backend abstraction layer for KMS implementations and exposes the concrete backend modules: local, Vault KV2, and Vault Transit.

## Important APIs, Types, and Functions
`KmsClient` is the low-level async trait with operations for data-key generation, direct encrypt/decrypt, key lifecycle (`create_key`, `describe_key`, `list_keys`, enable/disable, schedule/cancel deletion, rotate), health checks, and backend info. `KmsBackend` is the simplified service-manager-facing trait with owned request/response DTOs for create, encrypt, decrypt, generate data key, describe, list, delete, cancel deletion, and health check. `BackendInfo` carries backend type, version, endpoint, healthy flag, and arbitrary metadata with builder `with_metadata`.

## Control Flow
Concrete backend modules implement one or both traits. The split allows internal KMS logic to use a richer client-style interface with operation context while higher-level APIs use request/response DTOs. Health checks differ by trait: `KmsClient::health_check` returns `Result<()>`, while `KmsBackend::health_check` returns `Result<bool>`.

## State and Persistence Behavior
The module owns no state. It defines contracts that let backends decide whether to store data locally, in Vault KV, in Vault Transit, and/or in memory.

## Dependencies and Integration Points
It depends on `async_trait`, `std::collections::HashMap`, crate `Result`, and `crate::types::*`. The service manager and encryption service rely on these traits to abstract backend-specific behavior.

## Risks and Edge Cases
The two traits expose overlapping but not identical semantics, which can lead to wrapper inconsistencies. For example, a backend can implement safer key-material preservation in `KmsBackend` while the lower-level `KmsClient` method has different behavior. Request/response type names from `crate::types` must remain distinct from similarly named API DTOs in `api_types.rs`.

## Test Signals
No tests are defined in this module. Trait behavior is tested through concrete backend unit tests and examples.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/backends/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/backends/vault.rs -->
# sources/object-store/rustfs/crates/kms/src/backends/vault.rs

## Purpose
`vault.rs` implements a Vault KV2-backed KMS backend using `vaultrs`. Despite comments about Transit, this file stores key data and base64-encoded key material in Vault KV2 and performs data-key wrapping locally with `AesDekCrypto`.

## Important APIs, Types, and Functions
`VaultKmsClient` holds a `VaultClient`, `VaultConfig`, KV mount, key path prefix, and `AesDekCrypto`. `VaultKeyData` is the serialized Vault record with algorithm, usage, timestamps/status/version, description, metadata/tags, and `encrypted_key_material`. Helpers include `new`, `key_path`, `encrypt_key_material`, `decrypt_key_material`, `get_key_material`, `encrypt_with_master_key`, `decrypt_with_master_key`, `store_key_data`, `store_key_metadata`, `get_key_data`, `list_vault_keys`, and physical `delete_key`. `VaultKmsBackend` wraps the client and updates API-facing metadata.

## Control Flow
Client construction builds Vault settings with token auth and optional namespace; AppRole returns an unimplemented backend error. Key creation checks KV existence, generates AES key material, base64 encodes it, and stores a `VaultKeyData` record. Data-key generation creates plaintext DEK material, encrypts it with master key material through local AEAD, stores encrypted DEK/nonce/context in `DataKeyEnvelope`, and returns the serialized envelope. Decrypt parses that envelope, validates encryption context compatibility, and unwraps the DEK. Listing uses `kv2::list` and describes each key. Delete either marks keys pending deletion or physically deletes KV metadata on force-immediate when already pending.

## State and Persistence Behavior
Key metadata and key material persist in Vault KV2 under `{key_path_prefix}/{key_id}` in `kv_mount`. Key material is only base64 encoded by `encrypt_key_material`; comments explicitly say production should use Transit for additional encryption, but the current implementation does not. Runtime state is mostly in Vault; there is no local metadata cache in this file.

## Dependencies and Integration Points
The backend depends on `vaultrs::kv2`, Vault client settings, KMS config/types/errors, local encryption helpers, base64, serde, jiff, and tracing. It implements both backend traits and is used by `KmsConfig::vault`/Vault KV2 configuration.

## Risks and Edge Cases
Key material in Vault KV2 is not cryptographically wrapped by Vault Transit in this implementation, just base64 encoded. `get_key_material` self-heals missing, undecodable, or wrong-length key material by generating new material and storing it, which can permanently break decryption of data encrypted with the old material. `encrypt` uses a simple XOR of plaintext with key material rather than AEAD, while data-key wrapping uses `AesDekCrypto`; direct encrypt/decrypt semantics are inconsistent. `cancel_key_deletion` builds an enabled response but does not call `update_key_metadata_in_storage`, so the pending state may remain persisted. AppRole is accepted in config types but rejected at client construction.

## Test Signals
The only test is ignored and requires a running Vault instance. It covers client creation, key creation/description, data-key generation, and health check. There are no active unit tests for deletion, cancellation, metadata persistence, or the self-healing key-material paths.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/backends/vault.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/backends/vault_transit.rs -->
# sources/object-store/rustfs/crates/kms/src/backends/vault_transit.rs

## Purpose
`vault_transit.rs` implements a KMS backend backed by HashiCorp Vault Transit. Unlike the KV2 backend, cryptographic encrypt/decrypt operations are delegated to Vault Transit keys, while RustFS-specific metadata is tracked in an in-memory cache.

## Important APIs, Types, and Functions
`TransitKeyMetadata` stores usage, description, tags, state, creation/deletion dates, origin, creator, and current version. `VaultTransitKmsClient` holds a `VaultClient`, `VaultTransitConfig`, and `RwLock<HashMap<String, TransitKeyMetadata>>`. Helpers include `canonicalize_context`, `map_vault_error`, `read_transit_key`, `create_transit_key`, `transit_encrypt`, `transit_decrypt`, metadata cache accessors, `key_info`, `key_metadata_response`, and `ensure_key_active`. `VaultTransitKmsBackend` wraps the client and implements the simplified API trait.

## Control Flow
Client construction configures Vault address, token auth, and optional namespace; AppRole is rejected as unimplemented. Key creation creates an AES-256-GCM96 Transit key and stores metadata in memory. Data-key generation creates plaintext DEK material locally, encrypts it with Vault Transit using canonicalized encryption context as associated data, stores Transit ciphertext bytes in a `DataKeyEnvelope`, and returns serialized envelope. Decryption parses the envelope, validates context compatibility, decodes the Transit ciphertext, and asks Vault to decrypt. Direct encrypt/decrypt uses Transit ciphertext bytes for `EncryptResponse`; the simplified backend decrypt path expects a `DataKeyEnvelope`.

## State and Persistence Behavior
Vault Transit persists cryptographic keys. RustFS metadata such as descriptions, tags, deletion state, origin, and creation date is only held in `metadata_cache`. If metadata is missing after restart, `get_key_metadata` reads the Transit key and synthesizes default metadata. Deletion with pending windows is represented in this in-memory metadata until force deletion removes the Transit key.

## Dependencies and Integration Points
The file uses `vaultrs::transit::{data, key}` and Transit request builders, base64, `jiff::Zoned`, KMS config/types/errors, and Tokio `RwLock`. It supports constructing from either explicit Vault Transit config or a Vault KV2 config by extracting address/auth/namespace/mount path.

## Risks and Edge Cases
Metadata is not persisted, so key states, tags, descriptions, and scheduled deletion dates are lost across process restarts and can be synthesized as enabled. `health_check` fails if listing Transit keys is not permitted, even if encrypt/decrypt permissions exist. `KmsClient::decrypt` expects a data-key envelope and cannot directly decrypt bytes returned by `KmsClient::encrypt`; this mirrors a broader direct-encrypt contract mismatch. Pending deletion is only enforced by `ensure_key_active`, so synthesized metadata after restart may allow use of previously pending keys. AppRole remains unimplemented.

## Test Signals
No tests are defined in this file. Behavior must be validated through higher-level service tests or live Vault integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/backends/vault_transit.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/cache.rs -->
# sources/object-store/rustfs/crates/kms/src/cache.rs

## Purpose
`cache.rs` provides a simple async metadata cache for KMS key metadata using `moka`. It is intended to improve repeated key metadata lookup performance.

## Important APIs, Types, and Functions
`KmsCache` wraps `Cache<String, KeyMetadata>`. Public methods are `new`, `get_key_metadata`, `put_key_metadata`, `remove_key_metadata`, `clear`, and `stats`. Test-only helpers include custom TTL construction, cache info, and contains-key checks.

## Control Flow
`new` constructs a cache with max capacity and fixed 5-minute TTL. `get_key_metadata` awaits a cache lookup. `put_key_metadata` inserts cloned metadata and runs pending tasks. `remove_key_metadata` removes a key. `clear` invalidates all entries and runs pending tasks. `stats` returns current entry count and a hard-coded zero miss count.

## State and Persistence Behavior
All cache state is in-memory and TTL-bound. It stores metadata only, not key material. Data is lost on process restart and invalidated by capacity/TTL policies.

## Dependencies and Integration Points
The cache depends on `moka::future::Cache`, `std::time::Duration`, and `crate::types::KeyMetadata`. Service layers can use it alongside backend metadata calls.

## Risks and Edge Cases
`put_key_metadata`, `remove_key_metadata`, and `clear` take `&mut self`, which limits sharing behind immutable `Arc` without external locking even though moka caches are internally concurrent. `stats` labels the second value as misses but always returns zero because moka's miss count is not exposed. TTL is fixed in `new` rather than accepting `CacheConfig` values; test-only helper supports custom TTL but production API does not.

## Test Signals
Unit tests verify put/get/clear behavior, TTL expiry with a short test TTL, and contains-key helper behavior. They do not test capacity eviction or concurrent access.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/cache.rs -->

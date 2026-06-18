# subset-b-008267 Research

Grouped research for the requested KMS and lock crate files. Each source section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/config.rs -->
# sources/object-store/rustfs/crates/kms/src/config.rs

## Purpose
Defines KMS runtime configuration, backend selection, secure defaults, redaction rules, and environment loading. It is the policy gate for whether local/Vault development defaults are allowed.

## Important APIs, Types, And Functions
`KmsBackend` selects `Local`, `VaultKV2`/legacy `Vault`, or `VaultTransit`. `KmsConfig` carries backend config, default key id, timeout, retry count, cache settings, and `allow_insecure_dev_defaults`. `BackendConfig` wraps `LocalConfig`, `VaultConfig`, and `VaultTransitConfig`. `VaultAuthMethod` supports token and AppRole. `TlsConfig` captures Vault TLS paths and `skip_verify`. `CacheConfig` controls key metadata cache sizing.

Constructors include `KmsConfig::local`, `vault`, `vault_approle`, and `vault_transit`, plus builder helpers for default key, insecure development mode, timeout, and caching. `from_env` reads `RUSTFS_KMS_*` variables, builds backend-specific config, and calls `validate`. `KMS_CONFIG_REDACTION_RULES`, custom `Debug` implementations, and `redacted_secret*` avoid leaking secret material in diagnostics.

## Control Flow
`validate` checks timeout and retry count first, then validates backend-specific invariants. Local mode requires an absolute key directory; outside explicit development mode it also requires a non-empty master key and rejects temp-directory storage. Vault modes require HTTP(S) scheme, non-empty mount path, and outside development mode reject HTTP, the default `dev-token`, and TLS verification skipping. HTTPS without custom TLS config is logged as a warning rather than rejected.

`from_env` starts from `Default`, parses backend, default key, timeout, retry attempts, cache toggle, and the development opt-in flag, then replaces `backend_config` with the selected backend's env-derived config. It fails closed through `validate`.

## State And Persistence
All config structs derive serde serialization/deserialization, so this file defines the persisted shape for KMS service configuration. Secrets are serialized for persistence but redacted only in debug output and by the security governance redaction rule list. `Duration` fields are serialized using serde's standard representation for the type.

## Dependencies And Integration
Uses `rustfs_utils` env helpers, `rustfs_security_governance` redaction rules, `serde`, `url`, `PathBuf`, and `tracing`. `service_manager.rs` validates `KmsConfig` before accepting or starting a service. Backend constructors consume `BackendConfig`.

## Risks And Edge Cases
The default local config is intentionally invalid for production because it lacks a master key and uses a temp directory. `from_env` default local key dir is relative, which also fails validation unless callers provide an absolute path. Vault token auth is the only env path; AppRole must be configured programmatically or by deserializing config. TLS `client_key_path` is not validated alongside `client_cert_path`, so invalid mTLS combinations may fail later in backend setup.

## Test Signals
Tests cover default config fail-closed behavior, local and Vault dev-default opt-in, Vault Transit config, legacy Vault serde aliases, redaction rule validity, debug redaction without breaking persistence, env parsing, and skip-TLS rejection without the explicit development flag.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/encryption/ciphers.rs -->
# sources/object-store/rustfs/crates/kms/src/encryption/ciphers.rs

## Purpose
Implements AEAD object-data ciphers used after KMS produces a plaintext data key. It provides a common trait over AES-256-GCM and ChaCha20-Poly1305 and helpers for cipher construction and IV generation.

## Important APIs, Types, And Functions
`ObjectCipher` defines `encrypt`, `decrypt`, `algorithm`, `key_size`, `iv_size`, and `tag_size`. `AesCipher::new` and `ChaCha20Cipher::new` validate 32-byte keys and wrap the crypto library cipher instances. `create_cipher` maps `EncryptionAlgorithm::Aes256` and `AwsKms` to AES-256-GCM, and `ChaCha20Poly1305` to ChaCha20-Poly1305. `generate_iv` returns a random 12-byte nonce/IV for all supported algorithms.

## Control Flow
Encryption validates IV length, constructs a nonce, runs AEAD encryption with supplied AAD, then splits the library's ciphertext-plus-tag into separate ciphertext and 16-byte tag. Decryption validates IV and tag lengths, recombines ciphertext and tag, and calls AEAD decrypt with matching AAD.

## State And Persistence
Cipher structs hold initialized cipher state only; no persistence. Generated IVs and authentication tags are returned to callers and later stored in object encryption metadata.

## Dependencies And Integration
Depends on `aes_gcm`, `chacha20poly1305`, `rand`, `KmsError`, and `EncryptionAlgorithm`. `service.rs` uses `create_cipher` and `generate_iv` for SSE-S3, SSE-KMS, and SSE-C object encryption/decryption.

## Risks And Edge Cases
`AwsKms` is implemented as AES-256-GCM at the object cipher layer, which is reasonable because KMS wraps the DEK rather than encrypting object bytes remotely. Nonce reuse under the same key would be catastrophic for AEAD security; this file uses random IV generation, so call sites must not override it with repeated IVs. Error reporting reuses `invalid_key_size` for invalid IV/tag sizes, which may be semantically confusing.

## Test Signals
Tests cover AES and ChaCha encrypt/decrypt round trips with AAD, factory selection, random IV length and uniqueness, invalid key sizes, and invalid IV size rejection.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/encryption/ciphers.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/encryption/dek.rs -->
# sources/object-store/rustfs/crates/kms/src/encryption/dek.rs

## Purpose
Provides a backend-shared interface for encrypting and decrypting data encryption keys with master key material, plus an envelope format for storing encrypted DEKs and context.

## Important APIs, Types, And Functions
`DataKeyEnvelope` stores key id, master key id, key spec, encrypted key bytes, nonce, encryption context, and creation time using compatibility time serde. `DekCrypto` is an async trait with `encrypt`, `decrypt`, `algorithm`, and `key_size`. `AesDekCrypto` implements AES-256-GCM wrapping for DEK plaintexts. `generate_key_material` creates random `AES_256` or `AES_128` key bytes.

## Control Flow
`AesDekCrypto::encrypt` validates 32-byte master key material, creates an AES-GCM cipher, generates a random 12-byte nonce, and returns ciphertext plus nonce. `decrypt` validates nonce and key material length, reconstructs the nonce array, and decrypts the ciphertext.

## State And Persistence
`DataKeyEnvelope` is the persisted/wire shape for encrypted data keys and retains the encryption context needed for authenticated decryption. It serializes `jiff::Zoned` through `time_serde::zoned`, accepting both current timezone-annotated and legacy RFC3339 strings.

## Dependencies And Integration
Uses `async_trait`, `aes_gcm`, `jiff`, `rand`, `serde`, and `HashMap`. Local and Vault KV-style backends can use this layer to wrap generated DEKs with stored master key material.

## Risks And Edge Cases
`generate_key_material` can produce `AES_128`, but `AesDekCrypto` accepts only 32-byte wrapping keys. Callers must keep key-spec usage consistent. The AEAD wrapping path does not include external AAD directly; context binding must be implemented by the envelope/backend protocol, not this encrypt call alone.

## Test Signals
Async tests cover AES DEK encrypt/decrypt round trip, invalid key and nonce sizes, key generation sizes and unsupported algorithms, envelope serde, and backward-compatible timestamp parsing.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/encryption/dek.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/encryption/mod.rs -->
# sources/object-store/rustfs/crates/kms/src/encryption/mod.rs

## Purpose
Declares the encryption submodules and re-exports the DEK-facing API for the rest of the KMS crate.

## Important APIs, Types, And Functions
Exports `ciphers` and `dek` modules. Re-exports `AesDekCrypto`, `DataKeyEnvelope`, `DekCrypto`, and `generate_key_material`.

## Control Flow
No runtime control flow; it is a module boundary and public API convenience layer.

## State And Persistence
No state. Persistence types are re-exported from `dek.rs`.

## Dependencies And Integration
Used by KMS backends and services that need DEK wrapping APIs without importing the deeper module path.

## Risks And Edge Cases
`ciphers` is public as a submodule but only DEK items are re-exported. External callers needing object ciphers must import through `encryption::ciphers` if visibility allows from crate boundaries.

## Test Signals
No tests in this file; behavior is covered in `ciphers.rs` and `dek.rs`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/encryption/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/error.rs -->
# sources/object-store/rustfs/crates/kms/src/error.rs

## Purpose
Centralizes KMS error taxonomy and conversions into a crate-wide `Result<T>`.

## Important APIs, Types, And Functions
`KmsError` variants cover configuration, key lookup, invalid keys, cryptographic failure, backend failure, access denied, duplicate key, invalid operation, internal errors, serde, I/O, cache, validation, unsupported algorithms, invalid sizes, and encryption context mismatch. Constructor helpers provide consistent creation. Conversion impls map `std::io::Error`, `serde_json::Error`, `url::ParseError`, and `reqwest::Error`; helper methods map AES-GCM and ChaCha errors.

## Control Flow
There is no complex control flow; errors are built at call sites and propagated with `Result`. Conversions normalize external library failures into KMS-specific categories.

## State And Persistence
No state. Errors derive `Clone`, making them usable in async/test paths that need owned copies, but source error details are stringified rather than retained for most conversions.

## Dependencies And Integration
Uses `thiserror`, crypto crates, `serde_json`, `url`, and `reqwest`. All KMS modules import `KmsError` and `Result`.

## Risks And Edge Cases
Crypto helper conversion messages may be terse because AEAD error types often do not expose details. `invalid_parameter` and `invalid_key_state` both map to `InvalidOperation`, which simplifies API shape but loses specificity. `reqwest::Error` is always categorized as backend error.

## Test Signals
No direct tests in this file, but constructors and variants are exercised throughout config, encryption, manager, and service tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/lib.rs -->
# sources/object-store/rustfs/crates/kms/src/lib.rs

## Purpose
Defines the public crate boundary for RustFS KMS, documents the KMS architecture, and re-exports API types, configuration, errors, manager/service types, and core KMS types.

## Important APIs, Types, And Functions
Public modules include `api_types`, `backends`, `config`, `manager`, `service`, `service_manager`, and `types`; `cache`, `encryption`, `error`, and `time_serde` are internal. Public re-exports include configuration, `KmsError`, `KmsManager`, `ObjectEncryptionService`, `DataKey`, service manager functions, status, and API request/response DTOs. Backward-compatible functions include deprecated `init_global_services`, `shutdown_global_services`, and current `is_encryption_service_healthy`.

## Control Flow
The only runtime logic delegates global health checks to `get_global_encryption_service` and then to `ObjectEncryptionService::health_check`. Deprecated global init/shutdown are no-ops/logging placeholders because dynamic service management moved to `KmsServiceManager`.

## State And Persistence
Global state is owned by `service_manager.rs`; this file exposes accessors but does not store it directly.

## Dependencies And Integration
This is the integration surface consumed by other RustFS crates. The documentation explicitly states the master key -> DEK -> object data hierarchy and warns that generated DEKs must not be cached by key id alone.

## Risks And Edge Cases
Deprecated no-op functions may mislead legacy callers into thinking a passed `ObjectEncryptionService` was globally installed. The `#![deny(clippy::unwrap_used)]` lint raises quality for this crate, but tests still use `expect`, which is acceptable.

## Test Signals
Tests cover global service lifecycle, versioned reconfiguration preserving old `Arc` service references while new calls use a new version, and serialization of concurrent reconfiguration through the service manager mutex.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/manager.rs -->
# sources/object-store/rustfs/crates/kms/src/manager.rs

## Purpose
Coordinates KMS backend operations and optional key metadata caching behind a cloneable manager used by object encryption services.

## Important APIs, Types, And Functions
`KmsManager` stores an `Arc<dyn KmsBackend>`, `Arc<RwLock<KmsCache>>`, and `KmsConfig`. Public async methods delegate create/encrypt/decrypt/generate data key/describe/list/delete/cancel deletion/health check. It also exposes `get_default_key_id`, `cache_stats`, and `clear_cache`.

## Control Flow
Create, describe, delete, and cancel deletion update or consult the metadata cache when enabled. Encrypt, decrypt, generate data key, list keys, and health check delegate directly to the backend. `describe_key` checks cache first, then backfills cache from the backend response.

## State And Persistence
The manager's only state is in-memory metadata cache. It intentionally does not cache generated DEKs or ciphertext blobs; generated data keys are delegated every time to preserve per-object context binding.

## Dependencies And Integration
Depends on the `KmsBackend` trait, `KmsCache`, config, request/response types, and Tokio `RwLock`. `service.rs` wraps it for object-level SSE behavior, and `service_manager.rs` constructs it for each service version.

## Risks And Edge Cases
Cache TTL from `CacheConfig` is not passed into `KmsCache::new` here, only `max_keys`; if `KmsCache` supports TTL separately, that config may be ignored. Cache invalidation is limited to delete/cancel/create/describe paths and depends on backend responses being authoritative.

## Test Signals
Tests cover local backend create key, generate data key, describe, cache stats, health check, and a regression asserting generated data key ciphertext differs across different object contexts and decrypts only with its own context.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/service.rs -->
# sources/object-store/rustfs/crates/kms/src/service.rs

## Purpose
Implements S3-compatible object encryption/decryption on top of `KmsManager`, including SSE-S3, SSE-KMS-style behavior, and SSE-C customer-key encryption.

## Important APIs, Types, And Functions
`DataKey` holds a 32-byte plaintext key and 12-byte nonce and zeroizes key material on drop. `ObjectEncryptionService` delegates master-key APIs to `KmsManager` and provides `create_data_key`, `decrypt_data_key`, `encrypt_object`, `decrypt_object`, `encrypt_object_with_customer_key`, `decrypt_object_with_customer_key`, `metadata_to_headers`, and `headers_to_metadata`. `EncryptionResult` combines ciphertext and `EncryptionMetadata`. Helpers build canonical object encryption context and maintain an internal key-id header.

## Control Flow
`encrypt_object` reads the whole async reader into memory, determines the KMS key id from argument or default, builds encryption context, auto-creates an SSE-S3 key when using `AES256` and missing, requires non-AES/SSE-KMS keys to already exist, generates a DEK, creates the object cipher, generates an IV, serializes context as AAD, encrypts, and returns metadata containing IV/tag/context/encrypted data key. `decrypt_object` optionally validates expected context, parses algorithm, decrypts the encrypted data key through KMS using stored context, reconstructs AAD, and decrypts object ciphertext.

SSE-C validates a 32-byte customer key and optional MD5, uses the customer key directly for AES-256-GCM, stores no encrypted data key, marks `key_id` as `sse-c`, and requires that marker during decrypt.

## State And Persistence
Object encryption metadata is the persistence bridge: algorithm, key id, key version, IV, tag, context, timestamp, original size, and encrypted data key must be stored with the object. `metadata_to_headers` serializes this metadata into S3-facing and internal headers; `headers_to_metadata` reconstructs it, defaulting timestamp/size values unavailable from headers.

## Dependencies And Integration
Uses `KmsManager`, object cipher helpers, KMS types, base64, `jiff::Zoned`, `tokio::io::AsyncRead`, serde JSON for AAD/context, and `zeroize`. Integrates with S3 metadata/header handling via standard `x-amz-server-side-encryption` headers plus RustFS internal headers.

## Risks And Edge Cases
The implementation reads whole objects into memory despite crate-level documentation mentioning streaming; large objects need a streaming path. Context JSON serialization order for `HashMap` is not guaranteed across maps; this code decrypts using the stored metadata context, so round trips work, but independently reconstructed context bytes would be risky. `metadata_to_headers` uses `unwrap_or_default` for context serialization, which can silently emit an empty/invalid context header on serialization error. `decrypt_data_key` returns a zero nonce placeholder and relies on callers to restore stored nonce.

## Test Signals
Tests cover SSE-S3 encrypt/decrypt with auto-created default key, SSE-C encrypt/decrypt, metadata/header round trip with internal key id preservation, context validation failures, and `decrypt_data_key` rejecting mismatched object encryption context.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/service.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/service_manager.rs -->
# sources/object-store/rustfs/crates/kms/src/service_manager.rs

## Purpose
Manages dynamic KMS configuration, lifecycle, health, and zero-downtime reconfiguration using versioned service instances.

## Important APIs, Types, And Functions
`KmsServiceStatus` captures not configured, configured, running, and error states. `KmsServiceManager` stores current versioned service in `ArcSwap<Option<ServiceVersion>>`, configuration/status in Tokio `RwLock`s, a monotonic `AtomicU64` version counter, and a lifecycle `Mutex`. Public methods include `configure`, `start`, `stop`, `reconfigure`, `get_manager`, `get_encryption_service`, `get_service_version`, and `health_check`. Global helpers use a `OnceLock<Arc<KmsServiceManager>>`.

## Control Flow
`configure` validates before mutating state. `start` serializes through the lifecycle mutex, requires a stored config, creates backend/manager/service, atomically publishes the new service, and marks running. `stop` atomically clears the current service but leaves configuration available. `reconfigure` validates, stores the new config, creates a new service version without stopping old references, atomically swaps it in, and keeps old operations alive through `Arc` ownership.

## State And Persistence
State is in-memory process-global service state; it does not persist config itself. `ArcSwap` lets readers get the current service without awaiting locks, while lifecycle operations remain serialized.

## Dependencies And Integration
Constructs `LocalKmsBackend`, `VaultKmsBackend`, or `VaultTransitKmsBackend` from `BackendConfig`, then wraps them in `KmsManager` and `ObjectEncryptionService`. Logging uses structured tracing fields for KMS service state events.

## Risks And Edge Cases
If `create_service_version` fails during reconfigure, the config has already been replaced and status becomes error while the previously published service may still be present in `current_service`; callers using `get_encryption_service` can still receive the old service. This may be intentional for availability but creates config/status/service skew to monitor. Version counter increments before backend creation, so failed attempts consume version numbers.

## Test Signals
Tests in this file verify invalid default local config is rejected before state update. Additional lifecycle, versioning, and concurrent reconfiguration tests live in `lib.rs`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/service_manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/time_serde.rs -->
# sources/object-store/rustfs/crates/kms/src/time_serde.rs

## Purpose
Provides serde adapters for `jiff::Zoned` timestamps with backward compatibility for legacy RFC3339 timestamp strings.

## Important APIs, Types, And Functions
`zoned::serialize` and `zoned::deserialize` handle required `Zoned` fields. `option_zoned::serialize` and `option_zoned::deserialize` handle `Option<Zoned>`. `parse_zoned_compat` first parses full `Zoned` format and falls back to parsing a `Timestamp` converted to UTC.

## Control Flow
Deserialization reads a string, attempts current `Zoned` parsing, then attempts legacy `Timestamp` parsing. Optional deserialization maps through the same parser and transposes the result.

## State And Persistence
No runtime state. It defines timestamp persistence compatibility for KMS envelopes and any structs using these adapters.

## Dependencies And Integration
Uses `jiff::{Timestamp, Zoned, TimeZone}` and serde traits. `dek.rs` uses `zoned` for `DataKeyEnvelope.created_at`; other KMS types may use it as needed.

## Risks And Edge Cases
Legacy RFC3339 values lose original timezone naming and are normalized to UTC. Parse failures include the legacy value in the error string, so callers should avoid feeding sensitive strings as timestamps.

## Test Signals
Tests confirm current timezone-annotated strings and legacy RFC3339 strings parse and result in UTC timezone metadata.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/time_serde.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/types.rs -->
# sources/object-store/rustfs/crates/kms/src/types.rs

## Purpose
Defines the core KMS domain model: master/data key metadata, request/response DTOs, object encryption metadata, algorithms, key specs, and operation context.

## Important APIs, Types, And Functions
Key data types include `DataKeyInfo`, `MasterKeyInfo`, `KeyInfo`, `KeyMetadata`, `EncryptionMetadata`, `HealthStatus`, and `ObjectEncryptionContext`. API DTOs include generate/encrypt/decrypt/list/create/describe/generate-data-key/delete/cancel-delete requests and responses. Enums include `KeyUsage`, `KeyStatus`, `EncryptionAlgorithm`, `KeySpec`, and `KeyState`. Helpers include constructors and builder-style context setters, `KeySpec::key_size/as_str`, `EncryptionAlgorithm::as_str/key_size/iv_size`, and `FromStr` for algorithm parsing.

## Control Flow
Most logic is DTO construction and conversion. `DataKeyInfo::clear_plaintext` zeroizes plaintext material and removes it. `Drop for DataKeyInfo` calls that cleanup. `From<MasterKeyInfo> for KeyInfo` maps metadata into both metadata and tags.

## State And Persistence
All major structs derive serde traits and form persisted/wire schemas for KMS APIs and object metadata. `DataKeyInfo` has explicit memory hygiene for optional plaintext bytes, while many request/response structs containing plaintext vectors rely on caller lifecycle and do not zeroize on drop.

## Dependencies And Integration
Used throughout manager, backends, service, and API layers. Depends on `jiff::Zoned`, serde, `HashMap`, `uuid`, and `zeroize`.

## Risks And Edge Cases
There is overlap between older generic types (`GenerateKeyRequest`, `MasterKeyInfo`, `DataKeyInfo`) and newer KMS-like DTOs (`GenerateDataKeyRequest`, `KeyMetadata`), which may cause integration confusion. `EncryptionMetadata.encrypted_at` uses plain `Zoned` serde rather than `time_serde`, so compatibility differs from `DataKeyEnvelope`. `From<MasterKeyInfo>` clones metadata and also uses it as tags, conflating two concepts.

## Test Signals
No direct tests in this file; behavior is exercised through backend, manager, and service tests that construct these DTOs and validate serde/algorithm behavior indirectly.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/kms/src/types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/Cargo.toml -->
# sources/object-store/rustfs/crates/lock/Cargo.toml

## Purpose
Declares the `rustfs-lock` crate metadata, workspace inheritance, lint participation, dependencies, and library doctest setting.

## Important APIs, Types, And Functions
This is manifest-only. The package describes distributed locking for RustFS and advertises locking/asynchronous/distributed keywords. It disables doctests for the library.

## Control Flow
No runtime control flow.

## State And Persistence
No state. It controls build-time dependency resolution through workspace dependency entries.

## Dependencies And Integration
Runtime dependencies include RustFS IO metrics and utils, async/futures, serde/JSON, Tokio, tonic, tracing, uuid, thiserror, parking_lot, smallvec, smartstring, and crossbeam-queue. Workspace lints apply to the crate.

## Risks And Edge Cases
No feature flags are declared here despite source comments mentioning lock enablement through environment variables. Remote lock support is not exposed as a feature in this manifest.

## Test Signals
The manifest disables doctests; regular unit/integration tests are controlled by Rust source modules and workspace test commands.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/client/local.rs -->
# sources/object-store/rustfs/crates/lock/src/client/local.rs

## Purpose
Implements a local `LockClient` backed by the fast in-process global lock manager, with sharded storage of RAII guards so locks remain held until explicitly released.

## Important APIs, Types, And Functions
`LocalClient` stores guard shards, a shard mask, and optional injected `GlobalLockManager`. Constructors include `new`, `with_shard_count`, and `with_manager`. `get_lock_manager` returns the injected manager or global singleton. `get_shard_index/get_shard` map lock ids to shard maps. The `LockClient` impl covers acquire, release, refresh, force release, check status, stats, close, and online/local checks.

## Control Flow
`acquire_lock` translates generic `LockRequest` into `ObjectLockRequest::new_write` for exclusive or `new_read` for shared, preserving acquire timeout. On success it stores the returned `FastLockGuard` under the request lock id in the appropriate shard and returns acquired `LockInfo`. Timeout/conflict fast-lock errors become failure `LockResponse`s. `release` removes and drops the stored guard, triggering actual lock release.

## State And Persistence
State is in-memory guard storage split across 64 shards by default. Locks do not expire automatically locally; `refresh` is a no-op success and `check_status` fabricates current timing metadata from stored guards.

## Dependencies And Integration
Uses crate-level fast lock types, `GlobalLockManager`, generic lock DTOs, Tokio `RwLock`, and `HashMap`. `ClientFactory::create_local` returns this implementation as `Arc<dyn LockClient>`. Distributed locks can compose local clients for quorum simulations.

## Risks And Edge Cases
`with_shard_count` panics if the count is not a power of two. `check_status` derives resource from `lock_id.resource` and uses default metadata/priority rather than the original request fields. TTL is recorded in `LockInfo` but not enforced by this client. `get_stats` returns defaults rather than fast-lock manager metrics.

## Test Signals
No direct tests in this file; behavior is covered indirectly through distributed and namespace tests that use local clients and fast-lock guards.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/client/local.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/client/mod.rs -->
# sources/object-store/rustfs/crates/lock/src/client/mod.rs

## Purpose
Defines the generic lock client trait abstraction and factory for constructing local lock clients.

## Important APIs, Types, And Functions
`LockClient` is an async trait requiring acquire, release, refresh, force release, status, stats, close, online, and local checks. It provides default batch acquire/release implementations using `join_all`. `ClientFactory::create_local` returns an `Arc<dyn LockClient>` backed by `LocalClient`.

## Control Flow
Batch methods fan out all requests concurrently and collect `Result<Vec<_>>`, short-circuiting if any individual operation returns an error. Remote client support is present only as commented stubs.

## State And Persistence
No state in this module. Trait implementors own lock state.

## Dependencies And Integration
Uses `async_trait`, `futures::future::join_all`, `Arc`, and crate lock DTOs. `DistributedLock` depends on this trait for quorum-based fan-out across local or future remote clients.

## Risks And Edge Cases
Default batch acquire can leave earlier successful locks held if a later request returns an error rather than a failure response; implementors with atomic batch semantics should override it. Remote support is not active.

## Test Signals
No direct tests. Trait behavior is exercised through mock clients in `distributed_lock.rs` tests and through `LocalClient`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/client/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/distributed_lock.rs -->
# sources/object-store/rustfs/crates/lock/src/distributed_lock.rs

## Purpose
Implements quorum-based distributed locking over multiple `LockClient`s, returning RAII guards that release all underlying client locks asynchronously.

## Important APIs, Types, And Functions
`DistributedLockGuard` holds the public aggregate lock id, underlying `(LockId, client)` entries, lock type, and disarm state. It exposes `lock_id`, `disarm`, `is_disarmed`, and `release`; `Drop` calls release. `DistributedLock` stores clients, namespace, and write quorum. Public methods include `new`, `namespace`, `get_resource_key`, `lock_guard`, `lock_guard_quiet`, and `rlock_guard`; internal methods implement quorum acquisition, retry, cleanup, and failure classification.

## Control Flow
Acquisition clones a request to all clients in a `JoinSet`. For distributed attempts, each retry uses a fresh lock id and a bounded per-attempt timeout. Success is reached when individual successful locks meet the required quorum: configured quorum for exclusive locks and majority-like read quorum for shared locks. The returned lock id is an aggregate id, while the guard stores real per-client lock ids for release.

Failures are classified as retryable contention, non-retryable, or unrecoverable quorum. Partial successes are rolled back by background release cleanup. Pending late successes are also cleaned up asynchronously to avoid leaked locks. If hard RPC failures make quorum impossible, acquisition returns `LockError::QuorumNotReached`; contention/timeouts normally return `Ok(None)`.

## State And Persistence
No persistent state. Runtime state includes outstanding per-client lock entries owned by `DistributedLockGuard`. Drop/release spawns asynchronous cleanup with retries and metric decrement.

## Dependencies And Integration
Uses `LockClient`, generic lock DTOs, `LockError`, `futures::join_all`, Tokio `JoinSet`, `uuid`, tracing, and `rustfs_io_metrics` lock-held counters. It is the distributed coordination layer above local or remote lock clients.

## Risks And Edge Cases
Cleanup is best-effort and asynchronous; after all retry attempts, unreleased entries are only logged. If dropped outside an active Tokio runtime, it creates a current-thread runtime in a spawned OS thread, which is pragmatic but can hide cleanup latency. Failure classification depends on string prefixes for remote RPC failures and timeouts, so remote clients must preserve those message contracts. Read quorum differs from configured write quorum and should be reviewed against consistency requirements.

## Test Signals
Extensive tests cover remote RPC failure classification, warning policy, quorum impossible errors, retrying remote timeouts and transient timeouts, bounded per-attempt timeouts, clients ignoring budget, partial quorum rollback and retry with fresh lock ids, preserving non-retryable failures, and late-success cleanup so only retry-attempt locks remain active.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/distributed_lock.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/error.rs -->
# sources/object-store/rustfs/crates/lock/src/error.rs

## Purpose
Defines the lock crate's error taxonomy, retry/fatal classification, conversions, and `Result<T>` alias.

## Important APIs, Types, And Functions
`LockError` variants include timeout, resource not found, permission denied, network, internal, already locked, invalid handle, configuration, serialization, deserialization, insufficient nodes, quorum not reached, queue full, and not owner. Constructor helpers mirror the variants. `is_retryable` marks timeout/network/internal errors; `is_fatal` marks not-found/permission/configuration. Manual `Clone` recreates source-carrying errors with synthetic `io::Error`s.

## Control Flow
Conversions map I/O kinds, serde JSON categories, and tonic status codes into `LockError`. Classification helpers are used by callers to decide retry or escalation policy.

## State And Persistence
No state. Error values may carry `LockId` and durations. Source errors are boxed and not faithfully preserved across `Clone`.

## Dependencies And Integration
Uses `thiserror`, `tonic`, `serde_json`, and crate `LockId`. Distributed lock acquisition emits `QuorumNotReached`; client and fast-lock layers can use the other variants.

## Risks And Edge Cases
`std::io::ErrorKind::TimedOut` maps to `Internal` rather than `Timeout`, though `is_retryable` still treats it as retryable. `tonic::DeadlineExceeded` also maps to `Internal`, which may make user-facing errors less precise. Cloned network/serde errors lose original source type.

## Test Signals
Tests cover constructor output shapes, retryable classification, and fatal classification.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/disabled_manager.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/disabled_manager.rs

## Purpose
Implements a no-op fast-lock manager used when locking is disabled via environment configuration, allowing lock call sites to proceed without actual synchronization.

## Important APIs, Types, And Functions
`DisabledLockManager` stores a `LockConfig` only for shape compatibility. It provides `new`, `with_config`, `acquire_lock`, `acquire_read_lock`, `acquire_read_lock_versioned`, `acquire_locks_batch`, metrics/info/count/pool accessors, cleanup methods, and shutdown. Its `LockManager` trait impl marks `is_disabled` as true.

## Control Flow
All acquire paths immediately return disabled `FastLockGuard`s. Batch acquire returns every requested key as successful with no failures. Info and metrics queries return empty values, cleanup returns zero, and shutdown is a no-op.

## State And Persistence
No lock state is stored; guards are no-op disabled guards. There is no persistence or expiry behavior.

## Dependencies And Integration
Uses fast-lock guard, manager trait, metrics, batch/result/config/object types, and `Arc<str>` owners. It plugs into the same `LockManager` trait as the real fast lock manager so higher layers can switch based on env configuration.

## Risks And Edge Cases
The inherent `acquire_read_lock_versioned` creates a write request despite its read-oriented name, which may be harmless while disabled but is semantically suspicious. The trait implementation calls `self.acquire_write_lock` even though this file does not define an inherent `acquire_write_lock`; if the trait has no usable default, this is recursive or fails depending on trait definition and should be checked. Disabled mode removes all mutual exclusion, so it is only safe where external coordination is unnecessary.

## Test Signals
No tests in this file. Coverage should verify disabled acquire returns no-op guards for read/write/batch, `is_disabled` is true, metrics are empty, and the trait `acquire_write_lock` path does not recurse.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/disabled_manager.rs -->

# Research: subset-b-008825

Grouped research for TiKV cloud storage/KMS providers and codec buffer helpers. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/azure/src/azblob.rs -->
# sources/storage-engines/tikv/components/cloud/azure/src/azblob.rs

## Purpose
Implements TiKV's Azure Blob storage backend behind the shared `cloud::blob` traits. It translates `kvproto::brpb::AzureBlobStorage` into a local `Config`, chooses an Azure authentication path, builds `ContainerClient`s, and exposes `put`, `get`, and `get_part` for backup/restore flows. Iteration and deletion are intentionally unsupported here.

## Important APIs, Types, And Functions
- `Config` stores bucket/prefix/endpoint, explicit account/shared-key/SAS credentials, environment credentials, Azure AD client-secret credential info, encryption scope, and customer-provided encryption key data. Its custom `Debug` redacts secrets.
- `Config::from_input` validates the required bucket field, converts empty strings to `None`, loads environment variables, and maps `AzureCustomerKey` into `EncryptionCustomer`.
- `Config::get_account_name`, `parse_plaintext_account_url`, and `parse_env_plaintext_account_url` implement the account/key lookup and connection-string construction used by shared-key authentication.
- `AzureUploader` reads the whole `PutResource` into memory, applies upload headers for encryption scope, customer-provided key, or access tier, and retries one `put_block_blob` operation inside a 15 minute timeout.
- `ContainerBuilder` abstracts Azure SDK client construction. Implementations are `DefaultContainerBuilder`, `SharedKeyContainerBuilder`, and `TokenCredContainerBuilder`.
- `TokenCredContainerBuilder` caches bearer tokens and refreshes them with a `RwLock<Option<(AccessToken, Arc<ContainerClient>)>>` plus an async mutex so most callers can keep using a still-valid client while one task refreshes.
- `AzureStorage` implements `BlobStorage`; `IterableStorage` and `DeletableStorage` return the shared unsupported error.

## Control Flow
`AzureStorage::from_input` calls `Config::from_input`, then `AzureStorage::new`. `new` validates mutually exclusive encryption/access-tier combinations and picks credentials in priority order: explicit SAS token, explicit shared key, Azure AD env client-secret variables, environment shared key, then Azure SDK `DefaultAzureCredential`. Reads call `maybe_prefix_key`, build a blob `get` request with an optional byte range and optional customer encryption key, collect Azure response chunks into a `Vec<u8>`, and expose that vector as an async reader. Writes call `AzureUploader::run`, which buffers all input with `cloud::blob::read_to_end`, retries `upload`, and records `AZBLOB_UPLOAD_DURATION`.

## State And Persistence Behavior
The module is stateless with respect to TiKV metadata, but it persists and retrieves object bytes in Azure Blob Storage. Local mutable state is credential/client cache only: shared-key/SAS builders hold a stable `ContainerClient`; token builders cache access tokens until they approach expiry. Prefix handling is purely string-based and prepends `prefix.trim_end_matches('/')` to object names.

## Dependencies And Integration Points
It depends on `azure_storage`, `azure_storage_blobs`, `azure_identity`, `azure_core`, `oauth2`, `tokio`, `futures`, TiKV `tikv_util::stream::retry`, and shared `cloud::blob`/`cloud::metrics` contracts. Its input and customer key types come from `kvproto::brpb`. It is re-exported by the Azure crate `lib.rs` for use by external storage and backup code.

## Risks And Edge Cases
- Uploads buffer the entire object in memory before retrying, so very large backup files can create high memory pressure.
- `AzureUploader::adjust_put_builder` silently prefers encryption scope over customer key over access tier; `check_config` prevents invalid input combinations, but the priority still matters if new fields are added.
- Reads collect all response chunks into memory before exposing a stream, so partial consumers do not get true streaming behavior.
- Azure SDK errors in read/upload are generally mapped to `InvalidInput` except timeouts, which can reduce retry fidelity.
- Token refresh uses `std::sync::RwLock` in async code; lock hold times are short, but blocking behavior should be considered under high concurrency.
- List and delete are unsupported, so callers must feature-detect via trait usage.

## Test Signals
Unit tests cover backend URL formatting with endpoint and percent-encoded prefix, env credential loading and debug redaction, config validation for access-tier/encryption conflicts, and an ignored Azurite end-to-end blob put/get test. There are no active networkless tests for Azure credential priority, token refresh, range reads, or delete/list behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/azure/src/azblob.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/azure/src/kms.rs -->
# sources/storage-engines/tikv/components/cloud/azure/src/kms.rs

## Purpose
Implements Azure Key Vault/Managed HSM as a `cloud::kms::KmsProvider`. It generates plaintext data keys with Azure Managed HSM random bytes, encrypts them with a Key Vault key, and decrypts encrypted data keys for TiKV encryption-at-rest workflows.

## Important APIs, Types, And Functions
- `AzureKms` stores tenant/client identifiers, Key Vault and HSM `KeyClient`s, the current `KeyId`, and debug-visible service URLs/names.
- `AzureKms::new` chooses credential mode in priority order: embedded certificate, certificate file, then client secret. It deliberately constructs separate credential instances for Key Vault and HSM.
- `AzureKms::new_with_credentials` creates both Azure `KeyClient`s and transfers the provider config into the runtime struct.
- `KmsProvider::generate_data_key` calls HSM `get_random_bytes` for 32 bytes, then Key Vault `encrypt` with RSA-OAEP-256, returning `DataKeyPair`.
- `KmsProvider::decrypt_data_key` calls Key Vault `decrypt` with RSA-OAEP-256 and returns raw plaintext bytes.
- `convert_azure_error` normalizes Azure SDK errors into `cloud::Error::KmsError(KmsError::Other(...))`.

## Control Flow
Construction asserts that `config.azure` exists, unwraps Azure-specific settings, and validates that at least one credential source exists. Runtime generation first obtains random material from Managed HSM, then encrypts that material under `current_key_id`. Decryption sends the encrypted key bytes to Key Vault. Both KMS calls map Azure SDK errors through `convert_azure_error`.

## State And Persistence Behavior
No TiKV state is persisted locally. Remote persistent state is the Azure Key Vault key and Managed HSM resources configured outside TiKV. `AzureKms` keeps client objects and immutable IDs/URLs for repeated calls. Plaintext key data is returned in memory and `PlainKey` debug redacts it.

## Dependencies And Integration Points
The module integrates `azure_security_keyvault`, `azure_identity`, `azure_core::auth::TokenCredential`, and the local certificate credential extension. Shared KMS types come from `cloud::kms`; errors use `cloud::error`. `STORAGE_VENDOR_NAME_AZURE` is reused as the provider name.

## Risks And Edge Cases
- Wrong-key/auth failures are not distinguished from other Azure failures; `convert_azure_error` always yields `KmsError::Other`, so decrypt auth problems may not become `WrongMasterKey`.
- Configuration validation is mostly presence-based; malformed URLs and key IDs fail later when Azure clients or APIs are called.
- The code uses `assert!(config.azure.is_some())`, so misuse can panic rather than returning a structured error.
- RSA-OAEP-256 is hard-coded; the comment notes algorithm choice is still a TODO.
- Separate Key Vault/HSM clients are required; credential reuse changes should preserve this isolation.

## Test Signals
`test_init_azure_kms` verifies missing credential failure and successful construction with client secret. `test_azure_kms` is effectively a manual end-to-end test guarded by a vendor mismatch branch and placeholder config; active tests do not exercise network calls, error mapping, or certificate credentials.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/azure/src/kms.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/azure/src/lib.rs -->
# sources/storage-engines/tikv/components/cloud/azure/src/lib.rs

## Purpose
Defines the Azure cloud provider crate boundary. It wires internal blob, KMS, and token-credential modules and re-exports the public provider types used by the rest of TiKV.

## Important APIs, Types, And Functions
- `pub use azblob::{AzureStorage, Config}` exposes the Azure Blob storage implementation and its blob config type.
- `pub use kms::AzureKms` exposes the Azure KMS provider.
- `pub use token_credentials::certificate_credentials::ClientCertificateCredentialExt` exposes the local certificate credential implementation needed by Azure KMS.
- `STORAGE_VENDOR_NAME_AZURE` is the canonical vendor name string `"azure"`.

## Control Flow
There is no runtime control flow beyond module initialization. Consumers import the re-exported types and construct them from kvproto/shared cloud config.

## State And Persistence Behavior
No state is held in this file; state lives in the provider structs re-exported here.

## Dependencies And Integration Points
This file integrates the Azure crate into the shared TiKV cloud provider selection layer through a stable vendor name and public type exports.

## Risks And Edge Cases
The crate re-exports `Config` from `azblob`; if KMS config is also named `Config` in consumers, import ambiguity can occur. Vendor string changes would break configuration matching.

## Test Signals
No tests exist in this file. Coverage is indirect through `azblob.rs`, `kms.rs`, and downstream provider selection tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/azure/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/azure/src/token_credentials/certificate_credentials.rs -->
# sources/storage-engines/tikv/components/cloud/azure/src/token_credentials/certificate_credentials.rs

## Purpose
Provides a stable local implementation of Azure client-certificate token credentials. It builds a JWT client assertion from a base64 PKCS#12 certificate and exchanges it with Azure AD for an `AccessToken`.

## Important APIs, Types, And Functions
- `ClientCertificateCredentialExt` implements `azure_core::auth::TokenCredential`.
- `ClientCertificateCredentialExt::new` accepts tenant ID, client ID, base64 PKCS#12 certificate, and password.
- `ClientCertificateCredentialExt::build` reads a certificate file and base64-encodes it before constructing the credential.
- `CertificateCredentialOptions` supplies authority host and `send_certificate_chain`; defaults to Azure public login and sends x5c.
- `sign`, `get_thumbprint`, and `as_jwt_part` build the signed JWT assertion.
- `get_token` decodes PKCS#12, extracts cert and private key, creates JWT header/payload, signs it, posts a form-encoded client-credentials request, parses `AadTokenResponse`, and returns `AccessToken`.

## Control Flow
Every `get_token` call reparses the PKCS#12 certificate, computes SHA-1 thumbprint, builds a JWT expiring in `DEFAULT_REFRESH_TIME` seconds, and posts to `{authority}/{tenant}/oauth2/v2.0/token`. HTTP failures are converted with Azure core response helpers; JSON success bodies provide `access_token` and `expires_in`.

## State And Persistence Behavior
The struct stores certificate material and password in memory. `clear_cache` is a no-op, and despite the comment mentioning caching, this implementation does not cache tokens internally. Any cache is in callers such as `TokenCredContainerBuilder`.

## Dependencies And Integration Points
It uses `openssl` for PKCS#12 parsing, certificate serialization, hashing, and signing; `azure_core` for HTTP, base64 helpers, requests, and `TokenCredential`; `serde` for response parsing; `time` for expiration; and `url::form_urlencoded` for request bodies. Azure KMS consumes this credential for certificate-based authentication.

## Risks And Edge Cases
- Certificate and password are stored as plain `String`s in memory and debug output includes struct fields through derived `Debug`; caller logs should avoid formatting this type.
- Token lifetime is driven by `expires_in`, but JWT assertion lifetime is a fixed 300 seconds.
- No token cache means repeated token requests can be expensive unless wrapped by a higher-level cache.
- The SHA-1 thumbprint and x5c formatting must match Azure AD expectations; subtle base64 flavor changes could break authentication.
- `ext_expires_in` and `token_type` are parsed but not validated.

## Test Signals
This file has no local unit tests. Coverage is indirect through Azure KMS construction tests; there are no active tests for JWT construction, x5c chain handling, password-protected certificates, or HTTP error handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/azure/src/token_credentials/certificate_credentials.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/azure/src/token_credentials/mod.rs -->
# sources/storage-engines/tikv/components/cloud/azure/src/token_credentials/mod.rs

## Purpose
Declares the Azure token credential submodule.

## Important APIs, Types, And Functions
- `pub mod certificate_credentials;` makes `certificate_credentials.rs` available to the crate and public re-exports in `lib.rs`.

## Control Flow
No runtime logic is present.

## State And Persistence Behavior
No state is held here.

## Dependencies And Integration Points
This module boundary lets `crate::ClientCertificateCredentialExt` be exported from the crate root and used by Azure KMS.

## Risks And Edge Cases
The module currently exposes only certificate credentials; additional credential types should be added deliberately to avoid confusing Azure SDK built-ins with local extensions.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/azure/src/token_credentials/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp/Cargo.toml -->
# sources/storage-engines/tikv/components/cloud/gcp/Cargo.toml

## Purpose
Defines the legacy GCP provider crate package and dependency graph. This crate implements GCS and GCP KMS using `tame-gcs`, `tame-oauth`, `hyper`, and hand-written REST/KMS JSON calls.

## Important APIs, Types, And Functions
- Package `gcp`, version `0.0.1`, edition 2021, unpublished Apache-2.0 crate.
- Runtime dependencies include `cloud`, `kvproto`, `tikv_util`, `tame-gcs`, `tame-oauth`, `hyper`, `hyper-tls`, `serde`, `serde_json`, `crc32c`, `regex`, `lazy_static`, and `tokio`.
- Dev dependency `matches` supports tests.

## Control Flow
No executable logic lives in the manifest, but the selected dependencies define runtime behavior: HTTP requests flow through Hyper/TLS and auth flows through tame OAuth providers.

## State And Persistence Behavior
No state is stored in the manifest.

## Dependencies And Integration Points
The manifest ties the crate into workspace crates `cloud`, `kvproto`, `tikv_util`, and workspace logging crates. It enables `tame-gcs`'s `async-multipart` feature for uploads.

## Risks And Edge Cases
This crate is the older GCP implementation and differs from `gcp_v2`; dependency upgrades can affect request construction, OAuth support, retry classification, and multipart behavior. `base64 = 0.13` is older than the API style used by newer crates.

## Test Signals
The manifest itself has no tests; crate tests in `src/gcs.rs` and `src/kms.rs` validate endpoint rewriting, option parsing, key-id parsing, and base64 serialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp/src/client.rs -->
# sources/storage-engines/tikv/components/cloud/gcp/src/client.rs

## Purpose
Provides the legacy GCP HTTP/auth client used by GCS and KMS. It builds a Hyper HTTPS client, loads service-account/authorized-user/default credentials, injects OAuth authorization headers, and maps request failures into retry-aware errors.

## Important APIs, Types, And Functions
- `GcpClient` holds an optional `TokenProviderWrapper` and a Hyper client.
- `with_svc_info`, `with_default_provider`, and `load_from` construct clients from embedded service account info, default provider lookup, or a credential file.
- `set_auth` obtains or exchanges OAuth tokens and inserts the `Authorization` header.
- `make_request` applies auth when configured, sends the request, and turns non-success status into `RequestError`.
- `CredentialType` parses the JSON `type` field for `service_account` or `authorized_user`.
- `RequestError` models Hyper, OAuth, GCS, and invalid-endpoint failures and implements `RetryError`.

## Control Flow
Credential loading reads a path when provided, deserializes just enough JSON to determine credential type, then constructs the appropriate tame OAuth provider. Requests call `set_auth` if a provider exists. `set_auth` may synchronously return an existing token or perform an HTTP token request with the same Hyper client, parse the response, and insert an auth header before the original request is sent.

## State And Persistence Behavior
The client stores token-provider state in an `Arc<TokenProviderWrapper>`; any token caching is owned by tame-oauth internals. It reads credential files from disk but does not write any local state.

## Dependencies And Integration Points
Used by `gcs.rs` for GCS object requests and by `kms.rs` for Cloud KMS REST calls. It depends on `hyper`, `hyper_tls`, `http`, `tame_oauth`, `tame_gcs`, `serde`, and TiKV `RetryError`.

## Risks And Edge Cases
- Without explicit service info, `with_default_provider` must find usable environment/default credentials or construction fails.
- Error mapping turns some Hyper failures into `InvalidInput` `io::Error`s while retry classification still marks connect/closed/incomplete/body-aborted as retryable.
- HTTP 401/403 become permission denied and are non-retryable; 408/429/5xx OAuth status codes are retryable.
- The function name `load_from(credentail_path)` contains a typo in the parameter but not behavior.
- Auth token HTTP errors are represented as OAuth HTTP status errors with limited response body context.

## Test Signals
No local tests in this file. Behavior is indirectly exercised through legacy GCS/KMS tests and any integration tests using credential files or mocked endpoints.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp/src/client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp/src/gcs.rs -->
# sources/storage-engines/tikv/components/cloud/gcp/src/gcs.rs

## Purpose
Implements the legacy GCS blob storage backend behind `BlobStorage`, `IterableStorage`, and `DeletableStorage` using `tame-gcs` request builders and the local `GcpClient`.

## Important APIs, Types, And Functions
- `Config` stores `BucketConf`, parsed predefined ACL, storage class, and optional service-account info from `credentials_blob`.
- `Config::from_input` validates bucket, endpoint, prefix, storage class, ACL, and service-account JSON.
- `GcsStorage` owns `Config` and `GcpClient`.
- `maybe_prefix_key` and `strip_prefix_if_needed` implement object key namespace mapping.
- `make_request` rewrites hard-coded `www.googleapis.com` URLs to a custom endpoint if configured, then delegates to `GcpClient`.
- `put` handles zero-length objects with `insert_simple` and non-empty objects with buffered `insert_multipart`.
- `get_range`, `get`, and `get_part` expose full or byte-range reads.
- `GcsPrefixIter` pages `Object::list` results for `iter_prefix`.
- `delete` sends `Object::delete` with retry and metrics.

## Control Flow
Construction converts kvproto input into typed options and creates a GCP client from service-account info when present. Put prefixes the name, builds an `ObjectId`, and either inserts an empty object or reads the whole stream into a `Vec<u8>` before building a multipart request. Reads construct a download request, optionally set a `Range` header, send it, and flatten the Hyper body into an async reader. Listing uses `try_unfold` over page tokens until GCS returns no `page_token`.

## State And Persistence Behavior
Persistent data is in GCS objects. Local state is immutable config and client/auth state. Prefixes are stored as configuration and not persisted separately. Uploads are not resumable at this layer; they re-read buffered data for each retry.

## Dependencies And Integration Points
Depends on shared `cloud::blob` traits and metrics, `kvproto::brpb::Gcs`, `tame_gcs` request builders, `tame_oauth` service account parsing, Hyper, futures, and crate `utils::retry`. It integrates with TiKV backup/restore storage selection through the exported `GcsStorage`.

## Risks And Edge Cases
- Non-empty uploads buffer the entire object in memory and clone the buffer inside retry closures.
- `get_part` computes `off + len - 1`; `len == 0` would underflow.
- Endpoint rewriting strips known GCS suffixes and only rewrites URLs starting with `https://www.googleapis.com`; unusual generated URLs may bypass custom endpoints.
- GCS object names from list with missing `name` become an empty key.
- Range stream body errors are converted to `Interrupted`, encouraging retry, but callers reading the stream must perform retries at the right layer.

## Test Signals
Unit tests cover custom endpoint rewriting, storage-class parsing, predefined-ACL parsing, and backend URL formatting. There are no active tests for upload retry memory behavior, delete/list pagination, partial read underflow, or credential parsing failure modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp/src/gcs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp/src/kms.rs -->
# sources/storage-engines/tikv/components/cloud/gcp/src/kms.rs

## Purpose
Implements legacy GCP Cloud KMS as a `KmsProvider` using hand-built JSON REST calls through `GcpClient`. It generates HSM random bytes, encrypts them with a configured CryptoKey, and decrypts encrypted data keys.

## Important APIs, Types, And Functions
- `GcpKms` stores shared KMS `Config`, parsed location prefix, and `GcpClient`.
- `GcpKms::new` validates key ID with a regex, normalizes a trailing slash, derives `projects/.../locations/...`, and loads credentials from the optional credential file.
- `do_json_request` serializes request JSON, sends a POST to `https://cloudkms.googleapis.com/v1/{key}:method?alt=json`, records metrics, reads the whole response body, and deserializes it.
- `generate_data_key` calls `generateRandomBytes`, validates CRC32C, calls `encrypt`, validates CRC32C, and returns `DataKeyPair`.
- `decrypt_data_key` sends ciphertext with CRC32C and validates returned plaintext CRC32C.
- `serde_base64_bytes` encodes request/response bytes as JSON base64 strings.
- `Crc32Error` is retryable and converts to `CloudError`.

## Control Flow
Construction rejects keys not matching `projects/{project}/locations/{location}/keyRings/{ring}/cryptoKeys/{key}` and strips exactly one trailing slash. Generation makes two sequential KMS calls: random bytes at the location resource, then encryption at the key resource. Decryption makes one KMS call at the key resource. All REST calls use Cloud Platform OAuth scope.

## State And Persistence Behavior
The provider keeps immutable config and a reusable HTTP/auth client. It persists no local state. Remote KMS keys and generated ciphertext are controlled by GCP Cloud KMS; returned plaintext only lives in memory.

## Dependencies And Integration Points
Uses `cloud::kms` contracts, `cloud::metrics`, `GcpClient`, `hyper`, `tame_gcs` error wrappers for HTTP request construction, `serde`, `base64`, `crc32c`, `regex`, and `lazy_static`. It is exported by the legacy GCP crate root.

## Risks And Edge Cases
- HTTP/KMS API failures are wrapped as `KmsError::Other`; auth/wrong-key distinction is weaker than `gcp_v2`.
- `do_json_request` calls `serde_json::to_string(...).unwrap()`, relying on request serialization never failing.
- Response bodies are fully buffered in memory.
- CRC32C fields are deserialized from strings into `u32`; missing fields fail deserialization as GCS request errors rather than a dedicated CRC error.
- The key-id regex forbids cryptoKeyVersion IDs, as intended by tests.

## Test Signals
Unit tests cover invalid/valid key IDs, trailing slash normalization, location extraction, and base64 byte serde including non-ASCII bytes. No tests mock the REST client for generate/decrypt control flow or error mapping.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp/src/kms.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp/src/lib.rs -->
# sources/storage-engines/tikv/components/cloud/gcp/src/lib.rs

## Purpose
Defines the legacy GCP provider crate root, re-exporting GCS and KMS implementations and providing small shared request utilities.

## Important APIs, Types, And Functions
- Re-exports `gcs::{Config, GcsStorage}` and `kms::GcpKms`.
- `STORAGE_VENDOR_NAME_GCP` is the canonical `"gcp"` vendor string.
- `utils::retry` wraps `tikv_util::stream::retry_ext`, logs retryable failures, and increments `CLOUD_ERROR_VEC` labels.
- `utils::read_from_http_body` reads a Hyper body into bytes and converts it into a `tame_gcs::ApiResponse`.

## Control Flow
Provider modules call `utils::retry` around cloud operations. On each failed attempt, the fail hook logs context and increments metrics before retry logic decides whether to continue. `read_from_http_body` is used by list operations to convert HTTP responses into typed tame-gcs responses.

## State And Persistence Behavior
This file holds no persistent state. Metrics counters/histograms in the shared `cloud` crate are updated by helper calls.

## Dependencies And Integration Points
Integrates `slog_global` logging, `cloud::metrics`, Hyper body types, `tame_gcs::ApiResponse`, and TiKV retry helpers. Public exports are consumed by provider selection code.

## Risks And Edge Cases
- Retry helper metric labels use `"gcp"` and caller-provided operation names; new operations should keep label cardinality bounded.
- `read_from_http_body` buffers full response bodies, acceptable for metadata but risky if reused for large object data.
- Vendor string must remain aligned with shared constants and configuration values.

## Test Signals
No direct tests. Indirect coverage comes from GCS/KMS module tests and metrics assertions in `gcp_v2` for comparable behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp_v2/Cargo.toml -->
# sources/storage-engines/tikv/components/cloud/gcp_v2/Cargo.toml

## Purpose
Defines the newer GCP provider crate using generated Google Cloud Rust clients for Storage and KMS, with optional FIPS crypto-provider support.

## Important APIs, Types, And Functions
- Package `gcp_v2`, version `0.0.1`, edition 2021, unpublished Apache-2.0 crate.
- Feature `fips = ["rustls/fips"]` toggles FIPS provider installation.
- Runtime dependencies include `google-cloud-storage`, `google-cloud-gax`, `google-cloud-auth`, `google-cloud-kms-v1` all at `1.0.0`, plus `rustls`, `tokio`, `futures`, `async-stream`, `bytes`, `crc32c`, `cloud`, `kvproto`, and `tikv_util`.
- Dev dependencies include `prometheus` and `tempfile`.

## Control Flow
No runtime logic lives here, but dependency choices drive `gcp_v2` behavior: async generated clients, rustls provider setup, generated KMS/storage builders, and external-account/service-account credential support.

## State And Persistence Behavior
No manifest state beyond Cargo metadata.

## Dependencies And Integration Points
This crate coexists with legacy `gcp`; shared storage/KMS contracts come from `cloud`, and kvproto input still uses `brpb::Gcs`.

## Risks And Edge Cases
Google client versions and rustls feature flags are critical integration points. The `anyhow` dependency appears present but not central in the reviewed source. FIPS behavior depends on process-global rustls crypto-provider initialization.

## Test Signals
Integration tests in `tests/metrics.rs` depend on Tokio, tempfile, and generated clients. Unit tests in `src/lib.rs`, `src/kms.rs`, and `src/credentials.rs` validate credential mode, metrics, and KMS stubs.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp_v2/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp_v2/src/credentials.rs -->
# sources/storage-engines/tikv/components/cloud/gcp_v2/src/credentials.rs

## Purpose
Centralizes GCP v2 credential handling and rustls crypto-provider initialization. It supports default credentials, JSON service-account credentials, JSON external-account credentials, and FIPS/non-FIPS rustls provider setup.

## Important APIs, Types, And Functions
- `CredentialsMode` is either `Default` or `Json(String)`; its `Debug` redacts JSON contents.
- `validate_credentials_json` ensures the credential blob is syntactically valid JSON.
- `ensure_default_rustls_provider` installs or validates a process-global rustls provider. Under `fips`, it requires the aws-lc-rs FIPS provider; otherwise it installs ring.
- `build_credentials` parses JSON, checks its `type`, and builds `google_cloud_auth::credentials::Credentials` for `service_account` or `external_account`; default mode returns `None`.

## Control Flow
Callers validate credentials synchronously during config parsing but defer `build_credentials` until async client initialization to avoid `tokio::spawn` from non-Tokio threads. Rustls provider setup is idempotent if an acceptable provider is already installed and errors if an incompatible provider was installed first.

## State And Persistence Behavior
Credential JSON is held in memory inside `CredentialsMode::Json`. Rustls provider state is process-global. The module reads no files itself; file reads happen in callers before creating `CredentialsMode`.

## Dependencies And Integration Points
Used by `gcp_v2::GcsStorage` and `gcp_v2::GcpKms`. Depends on `google_cloud_auth`, `serde_json`, and `rustls`.

## Risks And Edge Cases
- Only `service_account` and `external_account` JSON credential types are supported; authorized-user credentials supported by legacy `gcp` are rejected here.
- Rustls provider initialization is global; if another crate initializes a non-FIPS provider before a FIPS build calls this, setup fails.
- `validate_credentials_json` only checks JSON syntax; semantic validation happens later in `build_credentials`.
- Credential JSON remains resident in memory for the lifetime of storage/KMS structs.

## Test Signals
`test_ensure_default_rustls_provider` verifies idempotent provider setup and that `provider.fips()` matches the build feature. KMS tests also verify that external-account JSON is recognized instead of rejected as unsupported.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp_v2/src/credentials.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp_v2/src/kms.rs -->
# sources/storage-engines/tikv/components/cloud/gcp_v2/src/kms.rs

## Purpose
Implements GCP Cloud KMS using the generated `google-cloud-kms-v1` client. It is the v2 replacement for legacy hand-built REST KMS and integrates richer error mapping, lazy async client construction, CRC32C checks, custom endpoints, and external-account credentials.

## Important APIs, Types, And Functions
- `GcpKms` stores shared KMS config, parsed location, optional endpoint, credential mode, and a `OnceCell<KeyManagementService>`.
- `GcpKms::new` validates GCP config, ensures rustls provider, strips a trailing key-id slash, parses the key id, reads optional credential file as UTF-8 JSON, validates it, and stores `CredentialsMode`.
- `get_client` lazily builds the generated KMS client with optional endpoint and credentials.
- `map_kms_call_error` maps unauthenticated/permission-denied gRPC or HTTP 401/403 to `WrongMasterKey`; other GAX errors become `KmsError::Other`.
- `generate_data_key` calls `generate_random_bytes` with HSM protection, checks data CRC32C, encrypts with plaintext CRC32C, verifies `verified_plaintext_crc32c`, checks ciphertext CRC32C, and returns `DataKeyPair`.
- `decrypt_data_key` sends ciphertext and CRC32C, checks plaintext CRC32C, and returns plaintext bytes.
- `parse_key_id`, `check_crc32`, `Crc32Error`, `GaxKmsError`, and `GaxBuildKmsError` provide validation and retry semantics.

## Control Flow
Construction performs all static validation and defers network/client work until first KMS call. The first call initializes the client in `OnceCell`; later calls clone the generated client handle. Data-key generation is a three-step validation path: generate random bytes, encrypt them, validate all service-provided integrity fields. Decrypt is a single service call followed by integrity validation.

## State And Persistence Behavior
`GcpKms` persists no local data beyond cached client/config/credential JSON. Remote KMS state is the configured CryptoKey. Plaintext key bytes live only in memory and are wrapped in `PlainKey` for redacted debug output.

## Dependencies And Integration Points
Uses `cloud::kms`, `cloud::metrics`, `google_cloud_kms_v1`, `google_cloud_gax`, `bytes`, `crc32c`, `tokio::sync::OnceCell`, and local credentials helpers. Exported from `gcp_v2::lib`.

## Risks And Edge Cases
- `parse_key_id` requires exactly eight slash-separated components and therefore rejects key version names, matching intended master-key semantics.
- `check_crc32` casts optional `i64` to `u32`; negative service values would wrap, though such values should not be produced by Google APIs.
- Missing CRC fields and failed `verified_plaintext_crc32c` are retryable `Other` errors, which is appropriate for integrity uncertainty but may repeat a persistent server/schema problem.
- Credential files are read synchronously during construction; large or blocked files can delay config setup.
- Metrics labels use cloud `"gcp"` even though provider name is `"gcp_v2"`, preserving existing metric compatibility but making provider distinction external to the label.

## Test Signals
Unit tests use generated KMS stubs for roundtrip generate/decrypt and metrics increments, verify permission-denied maps to `WrongMasterKey`, check external-account credentials are accepted, and ensure custom endpoint without credentials stays in default credential mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp_v2/src/kms.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp_v2/src/lib.rs -->
# sources/storage-engines/tikv/components/cloud/gcp_v2/src/lib.rs

## Purpose
Implements the v2 GCS blob storage backend using generated `google-cloud-storage` clients. It preserves TiKV's `BlobStorage`, `IterableStorage`, and `DeletableStorage` contracts while using resumable uploads, generated data/control clients, deferred credentials, custom endpoints, and retry-aware error mapping.

## Important APIs, Types, And Functions
- `GcsApiError` wraps `google_cloud_storage::Error`, maps HTTP/gRPC/transport statuses to `io::ErrorKind`, and implements retry classification.
- `PutResourceSource` adapts TiKV `PutResource` into `google_cloud_storage::streaming_source::StreamingSource` with exact size hints and 256 KiB read chunks.
- `Config` stores bucket, normalized prefix, URL prefix, endpoint, storage class, and predefined ACL.
- `GcsStorage` wraps an `Arc<GcsStorageInner>` so cloned storage shares lazily initialized clients.
- `GcsStorageInner` lazily creates separate `Storage` data and `StorageControl` control clients with optional endpoint and credentials.
- `GcsStorage::from_input` validates rustls provider, parses kvproto input, validates storage class/ACL, validates credential JSON, and stores credential modes.
- `put_with_client` performs forced resumable upload with storage class and predefined ACL options.
- `get_range`, `iter_prefix`, and `delete` implement reads, listing, and deletion using generated clients and TiKV retry helpers.

## Control Flow
Construction is synchronous and avoids building Google credentials to prevent `tokio::spawn` panics on non-Tokio backup worker threads. First data/control operation initializes the appropriate client in async context. `put` computes a full object path and bucket resource name, gets the data client, then uses `put_with_client`; `put_with_client` unsafely widens the reader lifetime but awaits the buffered upload before returning. Reads create an async stream that retries initial `read_object` request construction/send, then yields response chunks. Listing loops on `next_page_token`. Delete retries generated control API calls.

## State And Persistence Behavior
Persistent state is GCS object data. Local state is config, optional credential JSON, endpoints, and cached generated clients. Prefix normalization trims trailing slashes for actual object paths while preserving `url_prefix` for backend URL display.

## Dependencies And Integration Points
Depends on `cloud::blob` contracts/metrics, `kvproto::brpb::Gcs`, `google-cloud-storage`, `google-cloud-gax`, local credential helpers, `tokio`, `futures`, `async-stream`, `bytes`, `url`, and TiKV logging/retry utilities. It re-exports `GcpKms` from `kms.rs`.

## Risks And Edge Cases
- `put_with_client` uses `unsafe transmute` to widen `PutResource` to `'static`; the safety argument depends on `send_buffered()` not detaching the payload in `google-cloud-storage 1.0.0`.
- Forced resumable upload is intentional even for zero-length and small objects; this changes request shape and latency versus legacy `insert_simple`.
- `PutResourceSource::next` allocates a buffer each chunk and clamps zero-length reads to a one-byte buffer; zero-length uploads should still terminate on `Ok(0)`.
- Read streaming retries only the initial `read_object` send, not mid-stream chunk errors after bytes have been yielded.
- Bucket resource conversion treats bucket strings starting with `projects/` as resource names; malformed resource-like strings could pass through.
- Credential JSON is stored in memory and built separately for data/control clients.

## Test Signals
Unit tests cover gRPC error-to-`io::ErrorKind` mapping, prefix trimming, custom endpoint default credential mode, URL formatting, upload metric emission for non-empty and zero-length uploads through a stub client. Integration tests in `tests/metrics.rs` verify real HTTP request shapes for resumable upload, storage class, ACL, and zero-length behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp_v2/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp_v2/tests/metrics.rs -->
# sources/storage-engines/tikv/components/cloud/gcp_v2/tests/metrics.rs

## Purpose
Provides integration-style tests for the `gcp_v2` upload path against a local TCP HTTP server. The tests verify that generated-client uploads use resumable upload flow and preserve requested upload options without depending on live GCP services.

## Important APIs, Types, And Functions
- `start_server` launches a Tokio TCP listener, captures raw HTTP requests, and responds to token, resumable-upload initiation, and final upload requests.
- `response_for_target` returns a token response for `/token`, a `Location` header for `uploadType=resumable`, or a minimal object JSON body.
- `make_cfg` builds `kvproto::brpb::Gcs` test configs.
- `external_account_credentials_blob` creates a JSON external-account credential pointing at the local token endpoint and a subject token file.
- `gcp_v2_put_uses_resumable_upload_with_requested_options` asserts resumable upload, predefined ACL, and storage class are present in captured requests.
- `gcp_v2_zero_length_put_uses_resumable_upload` asserts zero-length upload still uses resumable flow.

## Control Flow
Each test starts the local server, creates a temporary subject token file, injects external-account credentials and custom endpoint into `GcsStorage::from_input`, performs `put`, inspects captured raw request bytes, and sends shutdown. The server reads headers and declared body length before responding so generated client request bodies are captured.

## State And Persistence Behavior
The tests create temporary subject token files and hold captured HTTP requests in `Arc<Mutex<Vec<Vec<u8>>>>`. No repository state is modified.

## Dependencies And Integration Points
Uses `tokio` networking and IO, `tempfile`, `kvproto::brpb::Gcs`, and the public `gcp_v2::GcsStorage`/`cloud::blob::BlobStorage` APIs. It exercises `google-cloud-auth` external-account token exchange through a local endpoint.

## Risks And Edge Cases
- The server is intentionally minimal HTTP/1.1 and only handles the generated-client request patterns required by these tests.
- Tests assert substrings in raw requests; generated client encoding changes could require updates even if semantic behavior remains valid.
- Shutdown is best-effort after assertions; panic before shutdown can leave the spawned task until test runtime teardown.

## Test Signals
These are the primary active tests proving `gcp_v2` does not regress to single-shot upload and keeps storage class/predefined ACL behavior. They also indirectly test external-account credential flow with local token exchange.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/gcp_v2/tests/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/src/blob.rs -->
# sources/storage-engines/tikv/components/cloud/src/blob.rs

## Purpose
Defines shared blob-storage abstractions and helpers used by provider crates. It decouples cloud providers from external storage internals while providing common config URL handling, object listing types, non-empty string validation, and optimized async read-to-end behavior.

## Important APIs, Types, And Functions
- `BlobConfig` exposes provider name and display URL.
- `PutResource<'a>` wraps a boxed async reader for uploads and implements `AsyncRead`.
- `BlobStream<'a>` is a boxed async reader for downloads.
- `BlobStorage` defines async `put`, and streaming `get`/`get_part`.
- `DeletableStorage` and `IterableStorage` define optional delete and prefix iteration contracts.
- `unimplemented` returns an `Unsupported` `io::Error` with the caller location.
- `BlobObject` carries listed object keys and implements `Display`.
- `StringNonEmpty` wraps non-empty strings and provides optional/required constructors.
- `BucketConf` stores endpoint, region, bucket, prefix, and storage class and builds provider URLs.
- `none_to_empty` and `read_to_end` are small utility helpers.

## Control Flow
Provider configs construct `BucketConf` and implement `BlobConfig::url` by delegating to `BucketConf::url`. Storage callers use trait objects for provider-specific implementations. `read_to_end` performs a `futures::io::copy` into a `Cursor<&mut Vec<u8>>`, avoiding repeated initialization behavior in `AsyncReadExt::read_to_end`.

## State And Persistence Behavior
This file has no persistence. Its types describe provider state and data streams. `StringNonEmpty` enforces non-empty config at construction time; `BucketConf::url` percent-encodes path components through `url::Url`.

## Dependencies And Integration Points
Used by Azure, GCP, AWS, and external storage integrations. Depends on `async_trait`, `futures`, `futures_io`, `url`, and standard IO/pin/panic location APIs.

## Risks And Edge Cases
- `StringNonEmpty` treats whitespace-only strings as non-empty.
- `BucketConf::url` overwrites any endpoint path with `bucket/prefix`, which is intended for custom endpoints but can surprise callers expecting endpoint path preservation.
- `unimplemented` reports caller location, useful but potentially exposes source paths in errors.
- `read_to_end` still buffers entire streams; providers using it inherit memory pressure risks.

## Test Signals
Tests cover bucket URL generation with and without endpoints and benchmark `read_to_end` against standard futures behavior using a throttled reader. Benchmarks require the nightly `test` feature and are not ordinary unit assertions except length checks inside benches.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/src/blob.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/src/error.rs -->
# sources/storage-engines/tikv/components/cloud/src/error.rs

## Purpose
Defines shared cloud error types, error codes, and retry classification. It gives provider crates a common way to report IO/protobuf/API/KMS errors to TiKV retry and diagnostics layers.

## Important APIs, Types, And Functions
- `Result<T>` aliases `std::result::Result<T, Error>`.
- `ErrorTrait` combines debug/display/error-code/retry/send/sync bounds.
- `Error` variants cover `Other`, `Io`, `Proto`, API timeout/internal/not-found/authentication, and `KmsError`.
- `KmsError` distinguishes `WrongMasterKey`, `EmptyKey`, and `Other`.
- `OtherError` stores a boxed error plus a retryable flag.
- `ErrorCodeExt` implementations map errors into `error_code::cloud::*`.
- `RetryError` implementations classify retryable cloud and KMS errors.

## Control Flow
Provider-specific errors are converted into `OtherError` or `KmsError` and then into `Error`. `From<Error> for IoError` preserves raw IO errors and stringifies all others. Retry logic calls `is_retryable`; most generic cloud errors are retryable except not-found/authentication and wrong/empty KMS keys.

## State And Persistence Behavior
No persistent state. `OtherError` captures the retryability decision at conversion time.

## Dependencies And Integration Points
Integrates `thiserror`, `error_code`, `protobuf::ProtobufError`, and `tikv_util::stream::RetryError`. Used across cloud blob and KMS providers.

## Risks And Edge Cases
- `Error::Other` is broadly retryable, but `OtherError::from_box` creates non-retryable `KmsError::Other` when providers do not preserve a `RetryError` implementation.
- `From<Error> for IoError` loses structured error codes for non-IO variants.
- The comment in `RetryError for Error` appears stale and says behavior should be refined.
- KMS auth errors must be mapped to `WrongMasterKey` by providers; otherwise they can become retryable/unknown `Other` errors.

## Test Signals
No direct tests in this file. Coverage is indirect through KMS provider tests that assert `WrongMasterKey` mapping and retry-aware custom errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/src/kms.rs -->
# sources/storage-engines/tikv/components/cloud/src/kms.rs

## Purpose
Defines shared KMS configuration, key wrapper types, cryptography key metadata, and the `KmsProvider` trait implemented by cloud provider crates.

## Important APIs, Types, And Functions
- `Location` stores region and endpoint.
- `SubConfigAzure`, `SubConfigGcp`, and `SubConfigAws` hold provider-specific credential/config settings.
- `Config` stores `KeyId`, vendor, location, and optional provider subconfigs.
- `Config::from_proto`, `from_azure_kms_config`, and `from_gcp_kms_config` convert `MasterKeyKms` protobuf data into shared config.
- `KeyId::new` rejects empty IDs.
- `EncryptedKey::new` rejects empty ciphertext and exposes `into_inner`/`as_raw`.
- `CryptographyType` currently supports `Plain` and `AesGcm256`; `target_key_size` enforces size.
- `PlainKey::new` validates key length for the cryptography type and redacts debug output.
- `DataKeyPair` bundles encrypted and plaintext keys.
- `KmsProvider` defines async `generate_data_key`, `decrypt_data_key`, and `name`.

## Control Flow
Provider-specific code receives or constructs `Config`, validates `KeyId`, creates provider clients, and returns `DataKeyPair`s with `PlainKey::new` and `EncryptedKey::new`. The shared constructors centralize empty-key and AES-256 length validation.

## State And Persistence Behavior
The file stores no runtime state. Wrapper types preserve invariants for in-memory key material and prevent accidental plaintext key exposure in debug logs.

## Dependencies And Integration Points
Depends on `kvproto::encryptionpb::MasterKeyKms`, `derive_more::Deref`, `async_trait`, and shared cloud errors. Azure/GCP/AWS KMS implementations all target `KmsProvider`.

## Risks And Edge Cases
- `Config` can contain mismatched `vendor` and subconfig fields; provider constructors must validate their own expected subconfig.
- `PlainKey` derefs to `Vec<u8>`, so callers can still clone/expose plaintext if careless.
- Only `AesGcm256` has a strict size today; adding algorithms requires updating `target_key_size`.
- Empty `Location.endpoint` is meaningful as "default endpoint"; provider code must handle that convention.

## Test Signals
No direct tests in this file. Invariants are exercised indirectly by provider tests that construct `KeyId`, `EncryptedKey`, and `PlainKey`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/src/kms.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/src/lib.rs -->
# sources/storage-engines/tikv/components/cloud/src/lib.rs

## Purpose
Defines the shared `cloud` crate root for TiKV cloud provider integration. It exposes error, KMS, blob, and metrics modules plus common vendor constants.

## Important APIs, Types, And Functions
- Enables nightly features `test` and `min_specialization`.
- Re-exports `Error`, `ErrorTrait`, `Result`, KMS config/key/provider types, and blob `BucketConf`/`StringNonEmpty` helpers.
- Defines `STORAGE_VENDOR_NAME_GCP` and `STORAGE_VENDOR_NAME_GCP_V2`.
- Public modules are `error`, `kms`, `blob`, and `metrics`.

## Control Flow
There is no runtime control flow. The file defines the crate's public API surface.

## State And Persistence Behavior
No state is stored here. Metrics are registered in `metrics.rs` when referenced through lazy statics.

## Dependencies And Integration Points
All provider crates depend on this crate for shared contracts. Downstream TiKV backup/encryption code imports these re-exports to avoid provider-specific dependencies.

## Risks And Edge Cases
Public re-export choices are API commitments inside the workspace. Vendor constants only include GCP/GCP v2 here; Azure has its own crate-level constant.

## Test Signals
No direct tests. Compile coverage of re-exports occurs through provider crates.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/src/metrics.rs -->
# sources/storage-engines/tikv/components/cloud/src/metrics.rs

## Purpose
Registers shared Prometheus metrics for cloud providers.

## Important APIs, Types, And Functions
- `CLOUD_REQUEST_HISTOGRAM_VEC` records cloud request durations with labels `cloud` and `req`.
- `CLOUD_ERROR_VEC` counts cloud errors with labels `cloud` and `error`.
- `AZBLOB_UPLOAD_DURATION` records Azure Blob upload duration with exponential buckets.

## Control Flow
Metrics are registered lazily via `lazy_static!` and Prometheus `register_*` macros. Provider code observes or increments them around cloud operations and retries.

## State And Persistence Behavior
Metrics live in the process-global Prometheus registry. They are not persisted by this module.

## Dependencies And Integration Points
Used by Azure Blob upload, legacy GCP storage/KMS, GCP v2 storage/KMS, and retry helpers. Depends on `lazy_static` and `prometheus`.

## Risks And Edge Cases
- Label values must stay bounded; request method labels should remain from a controlled operation set.
- Registration uses `unwrap()`, so duplicate registration in unusual test/plugin setups can panic.
- `CLOUD_ERROR_VEC` help text mentions "credentail errors from EKS env", which appears stale for a generic cloud metric.

## Test Signals
No direct tests. GCP v2 unit/integration tests assert histogram sample counts for upload and KMS operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/codec/Cargo.toml -->
# sources/storage-engines/tikv/components/codec/Cargo.toml

## Purpose
Defines the TiKV `codec` component crate and its dependencies for byte/number/buffer encoding helpers.

## Important APIs, Types, And Functions
- Package `codec`, version `0.0.1`, edition 2021, unpublished Apache-2.0 crate.
- Runtime dependencies include `byteorder`, `error_code`, `libc`, `static_assertions` with nightly feature, `thiserror`, and workspace `tikv_alloc`.
- Dev dependencies include workspace `bytes`, `panic_hook`, `protobuf`, and `rand`.

## Control Flow
No executable control flow. The manifest selects dependencies used by codec modules and tests.

## State And Persistence Behavior
No state is stored in the manifest.

## Dependencies And Integration Points
The codec crate is a low-level component used by TiKV storage/encoding layers. `static_assertions` nightly feature aligns with the crate's low-level type/layout checks elsewhere.

## Risks And Edge Cases
Codec is a foundational crate; dependency changes can affect serialization compatibility, allocation behavior, or panic/error integration. The manifest itself is minimal and has no feature gating for buffer unsafe APIs.

## Test Signals
Tests live in source modules such as `buffer.rs`; dev dependencies support randomized buffer tests and protobuf codec coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/codec/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/codec/src/buffer.rs -->
# sources/storage-engines/tikv/components/codec/src/buffer.rs

## Purpose
Defines low-level sequential memory buffer read/write traits used by the codec crate. It abstracts over `std::io::Cursor`, byte slices, mutable slices, boxed/delegated buffers, and growable `Vec<u8>` while exposing fast unsafe write access for encoders.

## Important APIs, Types, And Functions
- `BufferReader` exposes `bytes`, `advance`, and `read_bytes`.
- `BufferReader` implementations exist for `Cursor<T: AsRef<[u8]>>`, `&[u8]`, `&mut T`, and `Box<T>`.
- `BufferWriter` exposes unsafe `bytes_mut`, unsafe `advance_mut`, and safe `write_bytes`.
- `BufferWriter` implementations exist for `Cursor<T: AsMut<[u8]>>`, `&mut [u8]`, `Vec<u8>`, `&mut T`, and `Box<T>`.
- Error paths use `ErrorInner::eof().into()` when fixed-size buffers cannot satisfy reads/writes.

## Control Flow
Readers expose the remaining buffer, advance cursors/slices, and return borrowed slices when enough bytes are present. Writers expose writable remaining memory and require callers to advance only after initialization. Fixed-size writers fail on insufficient space; `Vec<u8>` reserves capacity and extends length via unsafe `set_len` after writes.

## State And Persistence Behavior
State is the current cursor position, slice start pointer, or `Vec` length/capacity. No external persistence exists. The traits intentionally mutate their internal position to support sequential encoding/decoding.

## Dependencies And Integration Points
Depends on crate `ErrorInner`/`Result` and nightly `std::intrinsics::unlikely` for branch hints. Higher-level codec modules use these traits to encode/decode bytes and numbers efficiently.

## Risks And Edge Cases
- Cursor `read_bytes` and `write_bytes` use `pos + count >= slice.len()` / `pos + write_len >= slice.len()`, meaning exact-to-end reads/writes fail for non-zero lengths. Tests currently advance to end manually but do not assert exact-to-end `read_bytes`/`write_bytes` success for cursor; this may be intentional historical behavior or an off-by-one risk.
- Unsafe `bytes_mut`/`advance_mut` can expose or commit uninitialized memory if callers advance without writing.
- `Vec<u8>::bytes_mut` returns spare capacity using raw pointer/slice construction; correctness depends on callers not reading uninitialized bytes.
- Slice `advance` and `advance_mut` can panic on over-advance.
- `Vec` reallocation behavior for data written beyond length is explicitly uncertain; the ignored test documents allocator-specific assumptions.

## Test Signals
Tests cover cursor and slice readers, cursor/slice/Vec writers, delegation through direct APIs, zero-length reads/writes, invalid cursor positions, and insufficient fixed-size writes. An ignored `test_vec_reallocate` documents unresolved reliance on unspecified `Vec::reserve` behavior for bytes written past length before `advance_mut`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/codec/src/buffer.rs -->

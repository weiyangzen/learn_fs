# sources/distributed-fs/ceph/src/rgw/rgw_kms.cc

Purpose: Implements RGW server-side encryption key retrieval for SSE-KMS and SSE-S3. It bridges object encryption metadata to configured KMS backends: local testing keys from Ceph config, OpenStack Barbican, HashiCorp Vault KV/transit, and KMIP.

Important APIs and functions: `make_actual_key_from_kms()`, `reconstitute_actual_key_from_kms()`, `make_actual_key_from_sse_s3()`, `reconstitute_actual_key_from_sse_s3()`, `create_sse_s3_bucket_key()`, and `remove_sse_s3_bucket_key()` are the public entry points declared in `rgw_kms.h`. Internal helpers include `ZeroPoolAllocator` for zeroing RapidJSON allocations, `VaultSecretEngine`, `TransitSecretEngine`, `KvSecretEngine`, `KmipSecretEngine`, `get_actual_key_from_barbican()`, `get_actual_key_from_conf()`, and `maybe_cache_kms_fetch()`.

Control flow: KMS calls build a context object (`KMSContext` or `SseS3Context`) around Ceph config, select a backend, then call a backend-specific fetch function. Barbican validates UUID-like key ids, obtains a Keystone token, and fetches `/v1/secrets/<id>/payload`. Vault sends HTTP requests with optional token file auth, namespace, TLS CA/client certificates, and SSL verification settings. Vault KV reads `.data.data.key`; Vault transit either exports old-style keys, creates data keys and stores ciphertext in `RGW_ATTR_CRYPT_DATAKEY`, or decrypts wrapped data keys. KMIP locates by configured key template and then retrieves the unique id. The testing backend decrypts a per-object key selector with an AES-256 master key from config.

State and persistence: The source updates encryption attrs for wrapped Vault transit data keys and consumes attrs such as `RGW_ATTR_CRYPT_KEYID`, `RGW_ATTR_CRYPT_KEYSEL`, `RGW_ATTR_CRYPT_CONTEXT`, and `RGW_ATTR_CRYPT_DATAKEY`. It stores no objects itself, but it may create or delete Vault transit bucket keys for SSE-S3. Sensitive buffers are explicitly zeroed in many paths.

Dependencies and integration points: Depends on RGW crypto helpers, `RGWHTTPTransceiver`, Keystone, KMIP transceiver, RapidJSON, Ceph config, perf counters, and optional `rgw::kms::KMSCache`. It is called by RGW object encryption/decryption paths.

Risks: KMS errors map to object IO failures, so backend availability directly affects reads and writes. Vault transit compatibility mode changes cache identity and attr semantics. Logging must avoid exposing secrets; this file mostly logs ids and status, but error responses may include Vault response text. The testing backend intentionally sleeps for configured delay and should not be confused with production key storage.

Test signals: Unit and integration tests should cover backend selection, invalid key ids, Vault KV/transit JSON parsing, wrapped key reconstitution, cache behavior through `KMSCache`, token file permission checks, KMIP locate edge cases, and secret zeroization-sensitive regressions.

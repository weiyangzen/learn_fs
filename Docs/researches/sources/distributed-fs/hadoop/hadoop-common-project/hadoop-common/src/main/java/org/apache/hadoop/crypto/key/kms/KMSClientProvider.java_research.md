# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/KMSClientProvider.java

## Purpose
`KMSClientProvider` is the HTTP client-side `KeyProvider` and `CryptoExtension` for Hadoop KMS. It translates the key-provider API into KMS REST calls, manages HTTPS/authenticated connections, caches encrypted encryption keys, and implements KMS delegation-token operations.

## Important APIs and types
The scheme is `kms`. `Factory` parses `kms://<proto>@<hosts>/<path>` URIs and returns a `LoadBalancingKMSClientProvider` containing one `KMSClientProvider` per host. Important nested types include `EncryptedQueueRefiller`, `TokenSelector`, `KMSTokenRenewer`, `KMSEncryptedKeyVersion`, `KMSKeyVersion`, and `KMSMetadata`. Public provider methods cover all key operations plus EEK generation/decryption/re-encryption, queue warmup/drain, delegation token select/get/renew/cancel, and close.

## Control flow
Construction unnests the KMS URI into a service URL ending in `/v1/`, computes delegation-token service aliases, initializes SSL for HTTPS, configures connection timeouts, initializes a `ValueQueue` for cached EEKs, and creates an authentication token. `createURL()` appends REST resources/subresources and query parameters. `createConnection()` opens an authenticated connection as the selected UGI, applies HTTP method/output flags, SSL settings, and timeout configuration. `call()` optionally writes JSON, retries once by default on auth failures by resetting the auth token, validates the expected response code, and parses JSON into the requested class.

Key operations map directly to REST endpoints: key versions use `/keyversion/{version}`, current key and metadata/versions use `/key/{name}/_currentversion`, `_metadata`, and `_versions`, create uses `POST /keys`, roll uses `POST /key/{name}`, delete uses `DELETE /key/{name}`, and invalidate uses `POST /key/{name}/_invalidatecache`. EEK generation is served from the local `ValueQueue`; the refiller calls `GET /key/{name}/_eek?eek_op=generate&num_keys=N`. Decrypt and re-encrypt post JSON payloads with base64 IV/material. Batch re-encryption validates same key name, posts a list, and replaces caller list entries from the response.

## State and persistence
Persistent key state lives entirely on the KMS server. Client state includes `kmsUrl`, optional `SSLFactory`, `ConnectionConfigurator`, mutable auth token, EEK `ValueQueue`, token services, and optional client-token-provider override used by load balancing. `flush()` is a no-op. `close()` shuts down queue refill threads and destroys SSL resources.

## Dependencies and integration points
It depends on Hadoop KMS REST constants, `KMSUtil` JSON parsers, `DelegationTokenAuthenticatedURL`, Hadoop security UGI/tokens, Jackson JSON serialization, Apache URIBuilder, Base64, `ValueQueue`, and `LoadBalancingKMSClientProvider`. It is the remote key backend for HDFS encryption zones and command-line key administration.

## Risks
HTTP status handling is security-critical: auth failures reset tokens and retry, while other errors depend on `HttpExceptionUtils`. `call()` has careful handling for output-stream failures to avoid sending empty mutation requests. EEK queueing can return stale encrypted keys after server-side key rotation unless invalidation/drain is called. Delegation-token service aliases must remain compatible with older address-based aliases and newer KMS URI services. Proxy-user `doAs` and UGI fallback to login user are subtle and need security-enabled coverage. Batch re-encryption mutates the caller's list in place.

## Test signals
Tests should cover URI parsing for single and multi-host KMS URIs, REST endpoint/method/payload construction, auth retry on 401/403 invalid signature, JSON parsing for all provider methods, EEK queue warmup/drain/refill, timeout/SSL configurators, delegation token select/get/renew/cancel and token renewer provider creation, proxy-user doAs behavior, batch re-encryption validation, and close cleanup.

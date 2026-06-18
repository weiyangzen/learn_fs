# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMS.java

## Purpose
`KMS.java` is the Jersey REST resource for Hadoop KMS. It exposes the versioned KMS API rooted at `KMSRESTConstants.SERVICE_VERSION` and translates HTTP calls into `KeyProviderCryptoExtension` operations for creating, deleting, rolling, reading, generating encrypted keys, decrypting encrypted keys, and reencryption.

## Important APIs, Types, and Functions
The `KMSOp` enum names auditable server operations: key management, metadata reads, key version reads, encrypted-key generation, decryption, and reencryption. The constructor obtains the process-wide provider and audit service from `KMSWebApp`. Endpoint methods include `createKey`, `deleteKey`, `rolloverKey`, `invalidateCache`, `getKeysMetadata`, `getKeyNames`, `getMetadata`, `getCurrentVersion`, `getKeyVersion`, `generateEncryptedKeys`, `handleEncryptedKeyOp`, `reencryptEncryptedKeys`, and `getKeyVersions`.

## Control Flow
Every endpoint follows a common shape: obtain the authenticated `UserGroupInformation` through `HttpUserGroupInformation`, validate required fields using `KMSUtil.checkNotEmpty` or `checkNotNull`, assert a KMS ACL through `KMSACLs`, run provider calls inside `user.doAs`, update meters from `KMSWebApp`, audit success, and return JSON via `KMSUtil` or `KMSServerJSONUtils`. Mutations call `provider.flush()` after create, delete, roll, and cache invalidation. EEK handling branches by the `eek_op` query parameter: generate returns a list of encrypted key versions, decrypt returns a decrypted key version, and reencrypt returns an updated encrypted key version or batch list.

## State and Persistence
This class stores only references to the static webapp provider and audit service. Persistent state is held by the backing `KeyProvider`; mutation flushes are the main durability boundary. Cache invalidation delegates to the provider wrapper. The class also increments Dropwizard meters, producing process-local metric state.

## Dependencies and Integration Points
It depends on Jersey annotations, Hadoop KMS REST constants, `KeyProviderCryptoExtension`, `KMSWebApp`, `KMSACLs`, `KMSAudit`, `KMSClientProvider` JSON-compatible value types, Base64 decoding for supplied key material and EEK payloads, and `UserGroupInformation` proxy execution. Responses are serialized by `KMSJSONWriter`.

## Risks
Security correctness depends on both the coarse KMS ACL checks here and the optional per-key wrapper configured in `KMSWebApp`. `getKeyVersion` checks only the global GET ACL before provider access, relying on `KeyAuthorizationKeyProvider` for per-key READ enforcement. `reencryptEncryptedKeys` warns but does not reject payloads larger than `MAX_NUM_PER_BATCH`, so protection is observational rather than limiting. User-provided key material is decoded without explicit length validation in this layer. Audit calls generally occur after successful provider operations; failures are handled by `KMSExceptionsProvider`.

## Test Signals
Relevant tests should cover ACL denial, key-material gating with `SET_KEY_MATERIAL`, provider flush after mutation, JSON shape compatibility, EEK op validation, batch reencryption input validation, and interaction with `KeyAuthorizationKeyProvider`. `MiniKMS` exercises this resource through an embedded server, and `KMSBenchmark` stresses generate/decrypt operations through provider APIs.

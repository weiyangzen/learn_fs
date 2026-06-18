# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKeyAuthorizationKeyProvider.java

## Purpose
`TestKeyAuthorizationKeyProvider.java` unit-tests `KeyAuthorizationKeyProvider`, the wrapper that enforces per-key ACLs around a `KeyProviderCryptoExtension`.

## Important APIs, Types, and Functions
- `testCreateKey()` verifies that creating a key requires a configured and authorized `MANAGEMENT` ACL, and denies both missing ACLs and unauthorized users.
- `testOpsWhenACLAttributeExists()` uses a mock `KeyACLs` to grant separate users `MANAGEMENT`, `GENERATE_EEK`, `DECRYPT_EEK`, and `ALL`, then verifies operation-specific permissions.
- `testDecryptWithKeyVersionNameKeyMismatch()` expects `IllegalArgumentException` when an encrypted key is mutated so its encryption key name no longer matches the version information used for decryption.
- `newOptions()` creates AES 128-bit provider options.

## Control Flow and State
The tests use an in-memory `UserProvider`, wrap it in `KeyProviderCryptoExtension`, then wrap that with `KeyAuthorizationKeyProvider`. They run operations under different `UserGroupInformation.doAs()` identities and use Mockito to answer ACL presence and access checks.

## Dependencies and Integration Points
The file integrates `KeyProvider`, `UserProvider`, `KeyProviderCryptoExtension`, `EncryptedKeyVersion`, `KeyAuthorizationKeyProvider.KeyACLs`, `KeyOpType`, `UserGroupInformation`, and Mockito. It protects the lower-level authorization layer used by KMS request handling.

## Risks and Edge Cases
The important risk is incorrectly mapping operations to `KeyOpType`, especially `ALL` bypass behavior and crypto extension methods. The mismatch test protects against decrypting encrypted-key material under a forged key identity.

## Test Signals
The file provides precise unit signals for create, roll, delete, generate encrypted key, decrypt encrypted key, and all-access authorization behavior independent of HTTP/KMS server plumbing.

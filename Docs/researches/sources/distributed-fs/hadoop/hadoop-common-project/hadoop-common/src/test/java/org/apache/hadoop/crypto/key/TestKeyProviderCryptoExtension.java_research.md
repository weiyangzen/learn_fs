# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyProviderCryptoExtension.java

## Purpose
`TestKeyProviderCryptoExtension` validates encrypted-key generation, decryption, re-encryption across key rolls, bulk re-encryption, and extension selection when key providers or caching wrappers implement crypto-extension services.

## Important APIs, Types, and Functions
It uses `UserProvider`, `KeyProviderCryptoExtension.createKeyProviderCryptoExtension`, `generateEncryptedKey`, `decryptEncryptedKey`, `reencryptEncryptedKey`, `reencryptEncryptedKeys`, `rollNewVersion`, `EncryptedKeyVersion.createForDecryption`, and `EncryptedKeyVersion.deriveIV`. Inner classes `DummyCryptoExtensionKeyProvider` and `DummyCachingCryptoExtensionKeyProvider` implement `CryptoExtension` to test selection precedence.

## Control Flow
`setup()` creates a user provider, wraps it in a crypto extension, configures AES-128 options, and creates the encryption key. Generation tests create EEKs, decrypt them, verify deterministic decrypt for the same EEK, and verify different random material/IV for separate EEKs. Manual decrypt tests compare API output to direct JCE AES/CTR decryption using the derived IV. Re-encryption tests roll the encryption key, rewrap older EEKs, verify material changes but decrypted EK material is preserved, and verify no-op behavior for already-current EEKs. Bulk re-encryption mutates a list in place and validates each version path. Extension-selection tests prove direct provider extensions and caching-provider extensions override the default extension.

## State and Persistence
The `UserProvider` stores key material in user credentials for the process. Test state includes generated encryption keys, encrypted-key versions, IVs, and rolled key versions. Bulk re-encryption modifies a list of `EncryptedKeyVersion` instances in place.

## Dependencies and Integration Points
Dependencies include Hadoop key provider classes, Java `Cipher`, `SecretKeySpec`, `IvParameterSpec`, `SecureRandom`, `Configuration`, and JUnit. The tests integrate provider storage, crypto extension wrappers, caching wrappers, and JCE AES/CTR compatibility.

## Risks and Edge Cases
The suite checks randomness, deterministic re-encryption for the same old EEK and target key version, no-op behavior when already current, and extension precedence through wrappers. Incorrect IV derivation or extension selection would break KMS/HDFS encryption-zone behavior.

## Test Signals
Passing tests signal correct EEK/EK naming, encrypted material lengths, manual/API decrypt equivalence, key-roll rewrap semantics, in-place bulk re-encryption, and crypto-extension selection over default fallback.

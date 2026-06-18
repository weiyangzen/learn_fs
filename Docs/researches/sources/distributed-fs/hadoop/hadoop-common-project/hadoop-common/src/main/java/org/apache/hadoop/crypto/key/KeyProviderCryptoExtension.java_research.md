# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderCryptoExtension.java

## Purpose
`KeyProviderCryptoExtension` augments `KeyProvider` with encrypted encryption key operations. It can generate encrypted ephemeral data keys, decrypt them, and re-encrypt them after key rotation, either by delegating to a provider-native implementation or by using a default local crypto implementation.

## Important APIs and types
The extension defines `EEK` and `EK` version-name markers. Nested `EncryptedKeyVersion` stores encryption key name, encryption key version name, encrypted key IV, and the encrypted key material as a `KeyVersion`; it also provides `createForDecryption()` and `deriveIV()` by XORing IV bytes with `0xff`. `CryptoExtension` declares `warmUpEncryptedKeys()`, `drain()`, `generateEncryptedKey()`, `decryptEncryptedKey()`, `reencryptEncryptedKey()`, and batch `reencryptEncryptedKeys()`.

## Control flow
`createKeyProviderCryptoExtension()` chooses a provider-native `CryptoExtension`, an underlying provider inside another `KeyProviderExtension`, or `DefaultCryptoExtension`. The default generator fetches the current encryption key, creates a configured `CryptoCodec`, generates random key material and IV, derives the encryption IV, encrypts the generated key into direct byte buffers, and returns an `EncryptedKeyVersion`. Decrypt does the inverse with the named key version. Re-encrypt fetches the current key, no-ops if already current, decrypts the EEK, and encrypts the plaintext key with the new key version. Batch re-encryption enforces all entries use the same key name and reuses codec/encryptor/decryptor instances.

## State and persistence
The wrapper stores the underlying provider and selected crypto extension. The default extension has no persistent state and does not store generated data keys. Generated EEKs are caller-managed values.

## Dependencies and integration points
It depends on `CryptoCodec`, `Encryptor`, `Decryptor`, `KeyProvider`, and Hadoop preconditions. KMS providers implement `CryptoExtension` natively so EEK plaintext need not leave the server; local providers can use the default implementation.

## Risks
The default extension decrypts EEKs in the client process, so it is less isolated than a KMS-native extension. `deriveIV()` is deliberately simple and must remain compatible across providers. The no-op check in single re-encryption compares the encrypted key version object to the current key version, which is a fragile semantic signal; the batch path compares key versions explicitly. Direct byte buffers are required by some codecs.

## Test signals
Tests should cover default EEK generation/decryption round trips, IV derivation compatibility, validation of EEK marker names, re-encryption no-op and changed-key paths, batch same-key enforcement, provider-native extension selection, and cleanup of `CryptoCodec` resources.

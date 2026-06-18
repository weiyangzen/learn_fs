# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/ReloadingX509KeystoreManager.java

## Purpose

`ReloadingX509KeystoreManager` is an `X509ExtendedKeyManager` wrapper that can atomically replace its delegate when a keystore file is reloaded.

## Important APIs, Types, and Functions

The constructor loads the initial key manager from type/location/passwords. `loadFrom(Path)` reloads and swaps the delegate. All `X509ExtendedKeyManager` alias, chain, and key methods delegate to the current manager held in an `AtomicReference`.

## Control Flow

`loadKeyManager` opens the keystore file, loads it with store password, initializes `KeyManagerFactory`, selects the first `X509ExtendedKeyManager`, and returns it. `loadFrom` wraps checked exceptions in `RuntimeException` for timer callback compatibility.

## State and Persistence Behavior

State is immutable keystore metadata and an atomic reference to the active key manager. It reads keystore files but writes nothing.

## Dependencies and Integration Points

It depends on JSSE `KeyStore`, `KeyManagerFactory`, `X509ExtendedKeyManager`, `SSLFactory.KEY_MANAGER_SSLCERTIFICATE`, and `FileBasedKeyStoresFactory` reload scheduling.

## Risks and Edge Cases

If no `X509ExtendedKeyManager` is produced, the reference can become null and delegate calls fail. Reload exceptions are unchecked and rely on caller failure handling to keep prior state. Store/key password mismatch fails reload.

## Test Signals

Tests should cover initial load, alias/key delegation, successful atomic reload, invalid keystore failure preserving previous manager via scheduler handling, null manager edge cases, and key password defaults.

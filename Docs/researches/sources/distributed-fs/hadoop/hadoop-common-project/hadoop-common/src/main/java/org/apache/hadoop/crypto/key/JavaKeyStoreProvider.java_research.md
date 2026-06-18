# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/JavaKeyStoreProvider.java

## Purpose
`JavaKeyStoreProvider` is a persistent `KeyProvider` backed by Java's JCEKS keystore format stored on any Hadoop `FileSystem`. It provides local or distributed-file key storage for Hadoop encryption while handling keystore passwords, metadata serialization, locking, and crash-tolerant flushes.

## Important APIs and types
The provider's scheme is `jceks`. Key public methods implement the `KeyProvider` contract: `getKeyVersion()`, `getKeys()`, `getKeyVersions()`, `getMetadata()`, `createKey()`, `deleteKey()`, `rollNewVersion()`, `flush()`, password warning methods, and `toString()`. `Factory` creates the provider for `jceks://` URIs. `KeyMetadata` adapts `KeyProvider.Metadata` to a serializable `Key` entry so metadata can live in the same keystore.

## Control flow
Construction unnests the provider URI into a Hadoop `Path`, opens the target filesystem, and calls `locateKeystore()`. Password lookup checks `HADOOP_KEYSTORE_PASSWORD`, then the configured password file, then defaults to `"none"`. Keystore loading handles normal current files, `_OLD` backups, `_NEW` incomplete writes, and corrupt current files. Reads acquire the read lock and fetch aliases from `KeyStore`. Creates and rolls acquire the write lock, validate lowercase names and material length, update metadata/cache, insert `SecretKeySpec` entries, and mark `changed`. `flush()` writes metadata entries, renames current to `_OLD`, writes `_NEW`, renames `_NEW` to current, deletes `_OLD`, and resets state from backup on failure.

## State and persistence
Persistent state is the JCEKS file containing version aliases like `name@0` plus a base alias `name` containing serialized metadata. In-memory state includes `KeyStore`, password, permission snapshot, changed flag, metadata cache, and fair read/write locks. Flush preserves original permissions and uses `_OLD`, `_NEW`, `_CORRUPTED_`, and `_ORPHANED_` paths for recovery.

## Dependencies and integration points
It depends on Hadoop `FileSystem`, `Path`, `FSDataInputStream`, `FSDataOutputStream`, `ProviderUtils`, Java `KeyStore`, `SecretKeySpec`, and the `KeyProviderFactory` service-loader mechanism. It is the primary file-backed provider selected by `hadoop.security.key.provider.path`.

## Risks
JCEKS password handling can silently default to `"none"` unless strict callers check `needsPassword()`. Wrong-password detection is heuristic for some JDK messages. The provider rejects uppercase key names, which can surprise users but avoids case-normalization hazards. Flush correctness depends on filesystem rename semantics; object-store-like filesystems with weak rename behavior may be risky. Metadata is serialized via Java object serialization of `KeyMetadata`, so serial filter compatibility is important.

## Test signals
Tests should cover creation, roll, delete, metadata serialization, lowercase validation, password sources, wrong password errors, recovery from `_OLD`/`_NEW` states, corrupt current fallback, permissions preservation, concurrent reads/writes, and service-loader factory URI unnesting.

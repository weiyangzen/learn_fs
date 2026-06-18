# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProvider.java

## Purpose
`KeyProvider` is Hadoop's stable abstraction for secret key storage and version management. It separates encryption clients from storage backends such as JCEKS files, user credentials, and KMS.

## Important APIs and types
The class implements `Closeable` and defines constants for default cipher/bit length and JCEKS serialization filtering. Nested `KeyVersion` holds key name, version name, and material. Nested `Metadata` holds cipher, bit length, description, attributes, creation time, and version count, with JSON byte serialization. Nested `Options` carries create-key parameters derived from configuration. Abstract methods include `getKeyVersion()`, `getKeys()`, `getKeyVersions()`, `getMetadata()`, `createKey(name, material, options)`, `deleteKey()`, `rollNewVersion(name, material)`, and `flush()`.

## Control flow
Construction copies configuration, installs a JCEKS serial filter system property if absent, and initializes the configured JCE provider via `CryptoUtils`. Convenience `createKey(name, options)` generates material using `KeyGenerator` and delegates to provider-specific creation. `rollNewVersion(name)` gets metadata, generates new material matching metadata cipher/length, and delegates. `getCurrentKey()` computes `name@(versions-1)` from metadata. Static `findProvider()` scans providers for metadata presence.

## State and persistence
The base class stores a defensive copy of configuration only. Persistence is delegated to subclasses. `Metadata.serialize()` writes UTF-8 JSON fields; its byte-array constructor reads the same format. `KeyVersion` exposes raw material byte arrays without defensive copying.

## Dependencies and integration points
It depends on Hadoop configuration keys, Gson streaming JSON, Java crypto `KeyGenerator`, and `CryptoUtils`. It is consumed by `KeyShell`, provider factories, crypto extensions, HDFS encryption-zone code, and KMS clients.

## Risks
`KeyVersion.getMaterial()` returns the underlying byte array, so callers can mutate key material. `Metadata.addVersion()` post-increments the version count, so provider implementations must use it carefully. Algorithm extraction strips text before `/`, which assumes cipher strings follow transformation conventions. The constructor sets a JVM-wide serialization-filter property, making configuration order relevant.

## Test signals
Tests should cover metadata JSON round trips, attributes validation, key generation for configured algorithms/lengths, `getBaseName()` parsing failures, version-name construction, current-key lookup, provider scan behavior, and mutation implications of returned arrays.

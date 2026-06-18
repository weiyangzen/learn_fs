# subset-b-007340 grouped research

This grouped report covers Hadoop common crypto, key provider, KMS client, secure-random, and abortable stream interfaces. Each section is delimited for deterministic source-tree-aligned splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/JceSm4CtrCryptoCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/JceSm4CtrCryptoCodec.java

## Purpose
`JceSm4CtrCryptoCodec` is the JCE-backed implementation of Hadoop's SM4 CTR no-padding crypto codec. It specializes the shared `JceCtrCryptoCodec` base class for the `CipherSuite.SM4_CTR_NOPADDING` suite and creates JCE `Cipher`-based encryptors/decryptors for stream encryption paths that use SM4 instead of AES.

## Important APIs and types
The public class extends `JceCtrCryptoCodec`. Its key overrides are `getLogger()`, `getCipherSuite()`, `calculateIV(byte[], long, byte[])`, `createEncryptor()`, and `createDecryptor()`. `createEncryptor()` constructs `JceCtrCipher` with `Cipher.ENCRYPT_MODE`, the configured provider, the SM4 cipher suite, and algorithm name `"SM4"`. `createDecryptor()` mirrors this with `Cipher.DECRYPT_MODE`.

## Control flow
Construction has no local initialization. During configuration, inherited `JceCtrCryptoCodec.setConf()` selects the JCE provider and random source. Consumers call `calculateIV()`, which delegates to the base CTR IV arithmetic using the suite block size. Encryption/decryption creation delegates to the nested base cipher wrapper, which initializes a JCE `Cipher` and processes `ByteBuffer` data.

## State and persistence
This class has only a static logger. Runtime provider, random generator, and cipher state live in `JceCtrCryptoCodec` and `JceCtrCipher`. It persists no keys or configuration.

## Dependencies and integration points
It depends on Java Cryptography Extension (`javax.crypto.Cipher`) and Hadoop's `CipherSuite`, `Encryptor`, and `Decryptor` abstractions. It is chosen by `CryptoCodec` configuration paths where SM4 CTR is enabled and a suitable JCE provider, commonly Bouncy Castle or another SM4-capable provider, is available.

## Risks
The main compatibility risk is provider support: default JDK providers may not implement `"SM4/CTR/NoPadding"` or algorithm `"SM4"`. Misconfigured provider selection will surface as `GeneralSecurityException` from encryptor/decryptor creation. CTR IV correctness depends on the inherited block-size-specific calculation and caller-provided IV length. This class also assumes SM4 key material length and cipher name are consistent with `CipherSuite.SM4_CTR_NOPADDING`.

## Test signals
Useful tests instantiate the codec with an SM4-capable JCE provider, assert the cipher suite and IV calculation against known vectors, encrypt/decrypt direct and heap-backed stream data through Hadoop crypto streams, and verify missing provider behavior fails clearly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/JceSm4CtrCryptoCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/OpensslAesCtrCryptoCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/OpensslAesCtrCryptoCodec.java

## Purpose
`OpensslAesCtrCryptoCodec` is Hadoop's native OpenSSL-backed AES CTR codec. It exposes the same `CryptoCodec` contract as JCE codecs while routing encryption/decryption through `OpensslCipher` JNI for higher throughput.

## Important APIs and types
The class extends `OpensslCtrCryptoCodec`. It returns `CipherSuite.AES_CTR_NOPADDING`, delegates IV calculation to the base class using the AES block size, and creates `OpensslCtrCipher` instances with `OpensslCipher.ENCRYPT_MODE` or `DECRYPT_MODE`. The constructor checks `OpensslCipher.getLoadingFailureReason()` and throws a runtime exception if the native cipher layer did not initialize.

## Control flow
When Hadoop reflects the codec into existence, the constructor validates native OpenSSL availability. `setConf()` is inherited and configures a `Random` implementation, defaulting to `OpensslSecureRandom`. Consumers request encryptors/decryptors, which build an `OpensslCipher` for the AES CTR transformation and process direct `ByteBuffer` data.

## State and persistence
This class stores no instance state beyond inherited configuration, random source, and optional engine id fields. Native cipher context is per `OpensslCtrCipher`/`OpensslCipher` instance and is cleaned through `OpensslCipher.clean()`/finalization.

## Dependencies and integration points
It depends on Hadoop native code, OpenSSL build support, `NativeCodeLoader`, `OpensslCipher`, `CipherSuite`, and the `CryptoCodec` stream wrappers. It integrates with the configurable codec selection used by HDFS encryption zones and crypto streams.

## Risks
Native library availability is a hard runtime prerequisite; the constructor throws if OpenSSL JNI cannot be initialized. `OpensslCipher.update()` requires direct input/output buffers, so callers must respect `CryptoCodec` buffer contracts. AES support is assumed if OpenSSL loaded; unlike SM4, this class does not call `isSupported()` for the suite.

## Test signals
Tests should cover constructor failure when native OpenSSL is disabled, successful AES CTR round trips with direct buffers, IV calculation parity with JCE AES CTR, and fallback/random-source behavior through inherited `setConf()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/OpensslAesCtrCryptoCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/OpensslCipher.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/OpensslCipher.java

## Purpose
`OpensslCipher` is Hadoop's private JNI wrapper around OpenSSL cipher contexts. It currently supports AES CTR and SM4 CTR with no padding and presents a small cipher-like API to the OpenSSL crypto codecs.

## Important APIs and types
The class exposes `ENCRYPT_MODE`, `DECRYPT_MODE`, `getLoadingFailureReason()`, `getInstance(String)`, `getInstance(String, String)`, `isSupported(CipherSuite)`, `init(int, byte[], byte[])`, `update(ByteBuffer, ByteBuffer)`, `doFinal(ByteBuffer)`, `clean()`, and native `getLibraryName()`. Internal enums `AlgMode` and `Padding` map transformation components to native ordinal identifiers. The nested `Transform` holds parsed algorithm, mode, and padding strings.

## Control flow
The static initializer checks `NativeCodeLoader.buildSupportsOpenssl()` and calls native `initIDs()`. Any failure is retained in `loadingFailureReason`, allowing codec constructors to fail early. `getInstance()` tokenizes transformations like `AES/CTR/NoPadding`, validates algorithm/mode/padding, initializes a native context, optionally initializes an OpenSSL engine, and returns a wrapper. `init()` passes mode, key, IV, algorithm, padding, and engine to native code. `update()` validates direct buffers and initialized context, calls native update with positions/remaining sizes, then advances input to limit and output by returned length. `doFinal()` finalizes/reset native state. `clean()` frees native context and engine handles.

## State and persistence
Instance state is the native `context`, selected `alg` and `padding`, and optional native `engine`. It is memory/resource state only; nothing is persisted. `finalize()` calls `clean()`, but callers should prefer explicit cleanup by owning cipher wrappers where possible.

## Dependencies and integration points
It depends on Hadoop native code, OpenSSL, `NativeCodeLoader`, `PerformanceAdvisory`, and Hadoop `Preconditions`. It is used by `OpensslCtrCryptoCodec.OpensslCtrCipher` and by SM4 support checks in `OpensslSm4CtrCryptoCodec`.

## Risks
Direct buffers are mandatory; heap buffers cause argument failures. Native resource lifecycle relies on `clean()` and finalization, so long-lived leaks are possible if wrappers are abandoned. Transformation parsing is strict and only accepts exactly three slash-separated components. Engine initialization can fail or select unavailable OpenSSL engines. Any native exception behavior must preserve Java buffer position invariants.

## Test signals
Test vectors should validate AES CTR and SM4 CTR transformations, invalid transformation parsing, unsupported suites, non-direct buffer rejection, finalization/cleanup idempotence, engine-id paths, and constructor behavior when native libraries are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/OpensslCipher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/OpensslCtrCryptoCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/OpensslCtrCryptoCodec.java

## Purpose
`OpensslCtrCryptoCodec` is the shared base class for OpenSSL-backed CTR-mode Hadoop codecs. It centralizes IV counter arithmetic, configurable random generation, resource cleanup, and the `Encryptor`/`Decryptor` implementation that delegates to `OpensslCipher`.

## Important APIs and types
The class extends `CryptoCodec` and has configuration/random/engine fields with getters/setters. Important methods are `calculateIV(byte[], long, byte[], int)`, `setConf(Configuration)`, `generateSecureRandom(byte[])`, `close()`, and abstract `getLogger()`. The nested `OpensslCtrCipher` implements both `Encryptor` and `Decryptor`, with constructors accepting mode, `CipherSuite`, and optional engine id.

## Control flow
`setConf()` records configuration, instantiates the configured random class from `HADOOP_SECURITY_SECURE_RANDOM_IMPL_KEY`, defaults to `OpensslSecureRandom`, and falls back to Java `SecureRandom` on failure. `calculateIV()` adds the 64-bit counter to the tail of the initial IV as a big-endian block counter with carry propagation. `OpensslCtrCipher.init()` validates key/IV and initializes the native cipher. `encrypt()` and `decrypt()` both call `process()`, which invokes `OpensslCipher.update()`. If update returns fewer bytes than input, it marks `contextReset` and calls `doFinal()`.

## State and persistence
Codec state is configuration, a random generator, and optional OpenSSL engine id. Cipher state is native OpenSSL context in each nested cipher plus a boolean `contextReset`. There is no persistence; `close()` only closes random generators that implement `Closeable`.

## Dependencies and integration points
It depends on `CryptoCodec`, Hadoop `ReflectionUtils`, `OpensslSecureRandom`, `IOUtils`, `CipherSuite`, and `OpensslCipher`. Concrete subclasses provide AES or SM4 suite selection and logger instances.

## Risks
The IV calculation must exactly match JCE and stream offset logic; off-by-one or endian mistakes corrupt encryption compatibility. `OpensslCipher` requires direct buffers, so integration through `CryptoInputStream`/`CryptoOutputStream` must preserve direct-buffer usage. Random implementation configuration can fail and silently fall back to Java `SecureRandom`, which is correct but may alter performance. `process()` treats short update as unusual; test coverage should confirm context reset behavior.

## Test signals
Tests should compare IV calculation to known counter values, validate AES/SM4 round trips through concrete subclasses, exercise configured random classes and close behavior, assert `isContextReset()` on forced short native updates, and verify no state persists across independent encryptor/decryptor instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/OpensslCtrCryptoCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/OpensslSm4CtrCryptoCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/OpensslSm4CtrCryptoCodec.java

## Purpose
`OpensslSm4CtrCryptoCodec` is the native OpenSSL-backed SM4 CTR codec. It mirrors the AES OpenSSL codec but adds explicit support probing and optional OpenSSL engine selection for SM4 deployments.

## Important APIs and types
It extends `OpensslCtrCryptoCodec`, returns `CipherSuite.SM4_CTR_NOPADDING`, and overrides `setConf(Configuration)` to read `HADOOP_SECURITY_OPENSSL_ENGINE_ID_KEY`. `createEncryptor()` and `createDecryptor()` create `OpensslCtrCipher` instances with the configured engine id. The constructor checks OpenSSL loading and `OpensslCipher.isSupported()` for SM4 CTR.

## Control flow
Construction fails if native OpenSSL did not load or the native library lacks SM4 CTR support. Configuration delegates random setup to the base class and stores the engine id. IV calculation uses inherited CTR arithmetic with the SM4 block size. Encryptor/decryptor creation passes the suite and engine id to the native cipher wrapper.

## State and persistence
The class has only static logging and inherited in-memory codec state. Engine id is configuration-derived state used by future cipher instances. No keys or metadata are persisted.

## Dependencies and integration points
It depends on OpenSSL native support compiled with SM4, `OpensslCipher`, `CipherSuite`, and Hadoop common configuration keys. It integrates with Hadoop codec selection for SM4 encrypted streams.

## Risks
SM4 support varies by OpenSSL version/build, making runtime detection critical. Misconfigured engine ids can prevent cipher initialization. The class throws runtime exceptions during construction, so configuration validation may surface late when a codec is first instantiated.

## Test signals
Tests should cover unsupported SM4 native builds, valid engine-id propagation, SM4 round trips with direct buffers, IV calculation parity with JCE SM4, and constructor behavior when OpenSSL loading fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/OpensslSm4CtrCryptoCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/UnsupportedCodecException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/UnsupportedCodecException.java

## Purpose
`UnsupportedCodecException` is a small unchecked exception used to signal that a requested Hadoop crypto codec is unavailable or unsupported.

## Important APIs and types
The class extends `RuntimeException` and provides four constructors: no-arg, message, message plus cause, and cause. It defines a stable `serialVersionUID`.

## Control flow
There is no custom control flow. Callers throw this exception directly when codec discovery or capability checks cannot satisfy a requested cipher implementation.

## State and persistence
It carries normal exception message/cause state only. It persists nothing.

## Dependencies and integration points
The class lives in `org.apache.hadoop.crypto` and is part of the crypto codec error model. It integrates with `CryptoCodec` selection and stream initialization paths that need to distinguish unsupported codecs from lower-level I/O errors.

## Risks
Because it is unchecked, callers may not be forced to handle codec unavailability. Messages should include enough configuration and cipher context at throw sites; this class itself does not enrich them.

## Test signals
Tests are minimal: serialization compatibility, constructor message/cause propagation, and integration tests asserting unsupported codec selection throws this type where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/UnsupportedCodecException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/CachingKeyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/CachingKeyProvider.java

## Purpose
`CachingKeyProvider` wraps another `KeyProvider` with short-lived Guava caches for key versions, current keys, and metadata. It reduces burst load on backing providers such as KMS while preserving the `KeyProvider` interface.

## Important APIs and types
The class extends `KeyProviderExtension<CacheExtension>`. `CacheExtension` owns three `LoadingCache` instances: `keyVersionCache`, `currentKeyCache`, and `keyMetadataCache`. Public overrides include `getCurrentKey()`, `getKeyVersion()`, `getMetadata()`, `deleteKey()`, `rollNewVersion()`, and `invalidateCache()`.

## Control flow
Cache loaders delegate to the wrapped provider. If the provider returns null, loaders throw internal `KeyNotFoundException`; public getters translate that back to null. Other loader exceptions are unwrapped to `IOException` where possible. Mutating operations delegate to the wrapped provider and then invalidate affected cache entries. Since version-to-base-key mapping is not tracked, version cache invalidation uses `invalidateAll()` on delete and key invalidation.

## State and persistence
State is entirely in-memory cache state. It does not persist key material and relies on the wrapped provider for persistence. Cache expiry is constructor-driven: key versions and metadata expire after access; current keys expire after write.

## Dependencies and integration points
It depends on Hadoop's `KeyProviderExtension` pattern and relocated Guava cache classes. It is useful in front of remote providers where repeated metadata/current-key lookups are expensive.

## Risks
Current-key caching can temporarily return stale key versions until expiry or explicit invalidation. The version cache is coarse-invalidated because it lacks reverse indexes, which is safe but can reduce cache efficiency. Loader null translation relies on wrapping nulls as exceptions because Guava loading caches do not cache null values.

## Test signals
Tests should verify cache hits avoid backing calls, null provider responses return null, `IOException` propagation is preserved, roll/delete/invalidate clear appropriate caches, and expiry semantics differ between current-key and metadata/version caches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/CachingKeyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/JavaKeyStoreProvider.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/JavaKeyStoreProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProvider.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderCryptoExtension.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderCryptoExtension.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderDelegationTokenExtension.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderDelegationTokenExtension.java

## Purpose
`KeyProviderDelegationTokenExtension` adapts a `KeyProvider` to Hadoop's `DelegationTokenIssuer` contract when the provider can issue, select, renew, and cancel delegation tokens. It gives filesystems and clients a uniform way to obtain KMS tokens without hard-coding provider classes.

## Important APIs and types
The class extends `KeyProviderExtension<DelegationTokenExtension>` and implements `DelegationTokenIssuer`. Nested `DelegationTokenExtension` extends both the marker extension interface and `DelegationTokenIssuer`, adding `renewDelegationToken()`, `cancelDelegationToken()`, and a visible-for-testing `selectDelegationToken(Credentials)` method. `DefaultDelegationTokenExtension` returns null or zero for all operations.

## Control flow
`createKeyProviderDelegationTokenExtension()` checks whether the supplied provider implements `DelegationTokenExtension`. If so, it delegates to the provider; otherwise it wraps the provider with the no-op default. `getCanonicalServiceName()` and `getDelegationToken()` simply forward to the selected extension.

## State and persistence
State is the wrapped key provider and extension instance inherited from `KeyProviderExtension`. There is no token cache or persistence in this wrapper.

## Dependencies and integration points
It depends on Hadoop security `Credentials`, `Token`, and `DelegationTokenIssuer`. `KMSClientProvider` and `LoadBalancingKMSClientProvider` implement the extension so KMS delegation tokens can flow through generic key-provider consumers.

## Risks
The default no-op behavior can mask missing token support if callers do not check for null tokens. Renew/cancel methods are present on the extension interface but not publicly forwarded by this wrapper except through the underlying extension type, so callers needing those operations must retain or cast appropriately.

## Test signals
Tests should verify native extension selection, no-op fallback results, forwarding of canonical service and token acquisition, and integration with KMS providers that implement renew/cancel/select methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderDelegationTokenExtension.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderExtension.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderExtension.java

## Purpose
`KeyProviderExtension` is the base decorator for adding capabilities to a `KeyProvider` while preserving the complete provider API. It is used by caching, crypto, and delegation-token extensions.

## Important APIs and types
The abstract class is generic over `E extends Extension`; `Extension` is a marker interface. It stores a `KeyProvider` and extension object, exposes protected `getExtension()` and `getKeyProvider()`, and overrides the full `KeyProvider` contract to delegate to the wrapped provider.

## Control flow
Construction calls `super(keyProvider.getConf())`, then records the provider and extension. Unless a subclass overrides a method, operations such as key lookup, creation, deletion, rolling, cache invalidation, `flush()`, and `isTransient()` are forwarded directly. `toString()` identifies the extension class and wrapped provider string.

## State and persistence
State is only the wrapped provider and extension object. Persistence behavior is exactly the wrapped provider's persistence behavior.

## Dependencies and integration points
It depends on `KeyProvider` and is the foundation for `CachingKeyProvider`, `KeyProviderCryptoExtension`, and `KeyProviderDelegationTokenExtension`. It allows capability wrappers to be stacked without changing provider factory interfaces.

## Risks
Because the constructor creates a new `Configuration` copy via the `KeyProvider` superclass, wrappers may have separate configuration objects from the wrapped provider, though default methods delegate behavior. Subclasses must remember to override close behavior if wrapping should close the underlying provider; this base class does not override `close()`.

## Test signals
Tests should verify transparent delegation for every provider method, `toString()` output, preservation of transient status, and subclass-specific override behavior when wrappers are stacked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderExtension.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderFactory.java

## Purpose
`KeyProviderFactory` discovers and instantiates key providers from URIs configured in Hadoop. It is the service-loader entry point for JCEKS, user, KMS, and other provider implementations.

## Important APIs and types
The class defines `KEY_PROVIDER_PATH` from `hadoop.security.key.provider.path`, abstract `createProvider(URI, Configuration)`, static `getProviders(Configuration)`, and static `get(URI, Configuration)`. A static `ServiceLoader<KeyProviderFactory>` is eagerly iterated to avoid lazy-loading synchronization issues.

## Control flow
`getProviders()` reads all configured provider-path strings, parses each as a URI, calls `get()`, and returns non-null providers. If no factory handles a URI, it throws an `IOException` naming the configuration key. `get()` iterates service-loaded factories until one returns a provider.

## State and persistence
The only state is the static service loader. Created providers own any persistent state.

## Dependencies and integration points
It depends on Java `ServiceLoader`, Hadoop `Configuration`, and provider-specific `Factory` implementations registered through service metadata. `KeyShell`, HDFS encryption-zone setup, and KMS token renewers rely on it.

## Risks
Bad URI syntax fails provider setup at runtime. Service-loader ordering can matter if multiple factories claim the same scheme. Eager static loading can surface provider class initialization errors early.

## Test signals
Tests should cover multiple configured providers, bad URI handling, unknown scheme errors, first-matching factory behavior, and service-loader registration for JCEKS/user/KMS factories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderTokenIssuer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderTokenIssuer.java

## Purpose
`KeyProviderTokenIssuer` is a small interface for filesystems that support encryption zones and need to expose the key provider and key provider URI associated with their delegation-token issuance.

## Important APIs and types
The interface extends Hadoop `DelegationTokenIssuer` and declares `getKeyProvider()` and `getKeyProviderUri()`, both throwing `IOException`.

## Control flow
There is no implementation. Filesystems implement the interface so higher-level token collection code can discover both filesystem tokens and KMS/key-provider tokens.

## State and persistence
No state is defined by the interface. Implementations decide whether providers are cached, lazily constructed, or persisted elsewhere.

## Dependencies and integration points
It depends on `KeyProvider`, `URI`, and Hadoop security token interfaces. HDFS-style encryption-zone filesystems can use it to bridge filesystem operations with KMS credential acquisition.

## Risks
Implementations must avoid returning stale or mismatched provider URIs, especially when logical KMS names or failover groups are configured. Returning a provider with unmanaged lifecycle can leak resources.

## Test signals
Tests belong to implementers: verify URI/provider consistency, token acquisition through `DelegationTokenIssuer`, and behavior when no key provider is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderTokenIssuer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyShell.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyShell.java

## Purpose
`KeyShell` is the `hadoop key` command-line utility for managing Hadoop key providers. It supports key creation, deletion, rolling, listing, metadata display, and cache invalidation.

## Important APIs and types
The class extends `CommandShell`. It parses commands in `init()`, prints detailed usage in `getCommandUsage()`, and defines nested command classes: `ListCommand`, `RollCommand`, `DeleteCommand`, `CreateCommand`, and `InvalidateCacheCommand`. The abstract nested `Command` resolves the active `KeyProvider` via `KeyProviderFactory`.

## Control flow
`init()` walks arguments, creates the appropriate subcommand, mutates `KeyProvider.Options` for `-size`, `-cipher`, `-description`, and `-attr`, sets provider configuration for `-provider`, toggles metadata listing, force deletion, and strict password behavior. Provider selection uses the first configured provider when user supplied `-provider`; otherwise it chooses the first non-transient provider. Commands validate provider and command-specific inputs, warn for transient providers, execute provider operations, call `flush()` for persistent mutations, and print user-facing success/failure messages. Delete prompts unless `-f`/`-force` disables interactivity.

## State and persistence
Shell state includes `interactive`, `strict`, and `userSuppliedProvider`, plus subcommand-local key names/options. Persistence is delegated to the selected provider and usually committed by `flush()`. `invalidateCache` does not call `flush()` because it changes cache state rather than key material.

## Dependencies and integration points
It depends on Hadoop `CommandShell`, `ToolRunner`, `KeyProviderFactory`, and provider implementations. It is the administrative entry point for JCEKS and KMS key operations.

## Risks
Argument parsing for `-attr` assumes an `=` is present; malformed input without it can throw rather than produce a friendly message. Default provider selection intentionally skips transient providers unless explicitly requested, which can surprise tests using `user:///`. Strict password mode only affects create validation, not all commands. CLI output is part of compatibility for scripts.

## Test signals
Tests should cover every command, provider selection with transient and non-transient providers, strict/no-password behavior, delete confirmation and force paths, metadata listing, duplicate/malformed attributes, error prettification, and `flush()` invocation on mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/UserProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/UserProvider.java

## Purpose
`UserProvider` is a transient `KeyProvider` backed by the current user's Hadoop `Credentials`. It lets jobs carry key material in credentials, commonly after copying keys from a persistent provider for task execution.

## Important APIs and types
The provider scheme is `user`. It overrides `isTransient()`, key lookup, metadata lookup, create, delete, roll, `flush()`, `getKeys()`, and `getKeyVersions()`. Nested `Factory` creates the provider for `user://` URIs.

## Control flow
Construction captures `UserGroupInformation.getCurrentUser()` and that user's `Credentials`. Key versions are stored as secret keys under `Text(versionName)`, while metadata is stored under `Text(name)` as serialized `Metadata`. Create validates non-existence and material length, writes metadata and `name@0`. Roll updates metadata version count and adds a new version secret. Delete removes all version secrets and metadata. `flush()` adds the credentials back to the user.

## State and persistence
State is in-memory credentials associated with the current UGI plus a metadata cache. It is explicitly transient: keys are not a long-term persistent store. Synchronization is method-level to protect credentials/cache mutation.

## Dependencies and integration points
It depends on Hadoop `UserGroupInformation`, `Credentials`, and `Text`. It integrates with MapReduce and other job submission flows that distribute secrets through credentials rather than opening persistent providers in tasks.

## Risks
The provider exposes key material in process credentials. Metadata cache must remain coherent with credential updates; this implementation updates/removes cache on mutations. Because it is transient, using it accidentally for administration without explicit `-provider user:///` should be avoided; `KeyShell` warns and normally skips transient providers.

## Test signals
Tests should cover create/get/roll/delete in credentials, `flush()` adding credentials to UGI, transient status, factory scheme matching, synchronization under concurrent access, and correct filtering of base names versus `@` version aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/UserProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/KMSClientProvider.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/KMSClientProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/KMSDelegationToken.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/KMSDelegationToken.java

## Purpose
`KMSDelegationToken` centralizes the token kind and identifier type for Hadoop KMS delegation tokens.

## Important APIs and types
It defines `TOKEN_KIND_STR` as `"kms-dt"` and `TOKEN_KIND` as a `Text`. The nested `KMSDelegationTokenIdentifier` extends `DelegationTokenIdentifier`, initializes the superclass with the KMS token kind, and overrides `getKind()` to return it. The outer class is final with a private constructor.

## Control flow
There is no runtime flow beyond constructing identifiers. KMS client and server token code refer to the constants for selection and renewal.

## State and persistence
No mutable state exists. Token identifier serialization behavior comes from the superclass.

## Dependencies and integration points
It depends on Hadoop `Text` and `DelegationTokenIdentifier`. `KMSClientProvider.TokenSelector`, `KMSTokenRenewer`, and delegation-token auth paths use this token kind.

## Risks
Token-kind string compatibility is externally visible; changing it would break stored credentials and renewal selection. The class intentionally contains no server-side policy.

## Test signals
Tests should assert token kind constants, identifier `getKind()`, and integration with token selector/renewer matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/KMSDelegationToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/KMSRESTConstants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/KMSRESTConstants.java

## Purpose
`KMSRESTConstants` defines shared REST resource, query-parameter, JSON-field, and error-field names for Hadoop KMS client/server communication.

## Important APIs and types
Constants include service version `/v1`, resources such as `key`, `keys`, `keyversion`, subresources like `_metadata`, `_versions`, `_eek`, `_currentversion`, `_invalidatecache`, and `_reencryptbatch`, EEK operations `generate`, `decrypt`, `reencrypt`, JSON fields such as `iv`, `name`, `cipher`, `length`, `material`, `versionName`, and error fields `exception` and `message`.

## Control flow
There are no methods. Client and server code compose URLs and JSON payloads from these constants.

## State and persistence
No state is stored. Constants are API compatibility surface for wire-format persistence in clients and servers.

## Dependencies and integration points
It depends only on Hadoop interface annotations. `KMSClientProvider`, KMS server handlers, and `KMSUtil` JSON conversion code must agree on these values.

## Risks
Any rename is a wire incompatibility. Because constants are simple strings, tests must catch endpoint drift between client and server.

## Test signals
Tests should exercise KMS client/server round trips rather than this class alone, ensuring all constants match accepted REST paths and JSON payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/KMSRESTConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/LoadBalancingKMSClientProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/LoadBalancingKMSClientProvider.java

## Purpose
`LoadBalancingKMSClientProvider` wraps multiple `KMSClientProvider` instances, round-robins requests across them, and fails over on retryable I/O/network failures. It also normalizes delegation-token behavior across a KMS HA group.

## Important APIs and types
The class extends `KeyProvider` and implements `CryptoExtension` and `DelegationTokenExtension`. `ProviderCallable<T>` abstracts an operation on one provider. `WrapperException` transports checked non-IO exceptions through retry code. Key fields are provider array, atomic current index, delegation token service, canonical token alias, and retry policy.

## Control flow
Construction computes token services, optionally shuffles providers, sets each provider's client-token-provider to this load balancer, initializes round-robin index, and builds a failover retry policy from configuration. `doOp()` selects providers from a starting position, invokes the operation, does not retry access-control errors, wraps SSL/socket errors as connect exceptions for retry policy, sleeps after trying all providers in a cycle, and ensures each provider is tried at least once before final failure. Mutating operations such as create/delete/roll use non-idempotent retry flags; reads and EEK operations use idempotent flags where appropriate. Some operations, such as warmup, drain, invalidate, flush, and close, are broadcast to all providers.

## State and persistence
State is in-memory provider list, current index, token service aliases, and retry policy. Persistent key state remains on KMS servers. Mutations that succeed on one KMS are expected to become visible through shared backend/server state.

## Dependencies and integration points
It depends on `KMSClientProvider`, Hadoop retry policies, security tokens, KMS configuration keys, and `KMSUtil`. It is always returned by `KMSClientProvider.Factory` for valid KMS URIs, even with one host.

## Risks
Non-idempotent mutation retry is intentionally constrained but still depends on the retry policy and failure timing. Access-control failures are not retried under the assumption all KMS hosts share ACLs. Canonical token alias handling must balance deterministic token acquisition with backwards-compatible per-host aliases. Provider shuffling improves distribution but tests need deterministic seed paths.

## Test signals
Tests should cover round-robin order, failover on IO/SSL/socket exceptions, no retry on access control, retry limits/sleep behavior, broadcast operations, token selection via canonical and dt services, service rewriting on new tokens, deterministic no-shuffle construction, and close/flush error logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/LoadBalancingKMSClientProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/ValueQueue.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/ValueQueue.java

## Purpose
`ValueQueue<E>` is a generic per-key value cache used by the KMS client to keep encrypted encryption keys pre-generated. It maintains expiring queues, synchronous fallback generation, and asynchronous low-watermark refill.

## Important APIs and types
`QueueRefiller<E>` supplies values for a key. `SyncGenerationPolicy` controls how many values are generated synchronously when a queue is empty: `ATLEAST_ONE`, `LOW_WATERMARK`, or `ALL`. Public APIs include constructors, `initializeQueuesForKeys()`, `getNext()`, `getAtMost()`, `drain()`, visible-for-testing `getSize()`, and `shutdown()`. Internal `UniqueKeyBlockingQueue` ensures only one queued/running refill task per key.

## Control flow
Construction validates parameters, creates striped read/write locks, builds a Guava `LoadingCache` from key name to `LinkedBlockingQueue`, and creates a daemon fixed-size refill executor. Cache load synchronously fills each new queue to the watermark. `getAtMost()` polls up to the requested count under per-key read locks. If insufficient values are present, it synchronously fills according to policy, then schedules an asynchronous refill if the queue is below watermark. `submitRefillTask()` lazily starts core threads and inserts a named runnable directly into the unique queue. `drain()` cancels queued tasks for the key and clears the existing queue under write lock.

## State and persistence
All state is in-memory: expiring per-key queues, striped locks, executor, unique refill queue, refiller callback, target queue size, watermark, and policy. There is no persistence; on restart/warmup queues are regenerated.

## Dependencies and integration points
It depends on relocated Guava `CacheBuilder`/`LoadingCache`, Java concurrent queues/executors, and Hadoop preconditions. `KMSClientProvider` instantiates it for `EncryptedKeyVersion` caching.

## Risks
Refiller exceptions are wrapped as `IOException`, and async refill exceptions become runtime exceptions on executor threads. The striped lock index uses hash masking with fixed array size; collisions serialize unrelated keys. `UniqueKeyBlockingQueue` removes a key from `keysInProgress` when a task is taken, not when it finishes, so a second task can be queued while one is running if timing allows. Queue size checks are approximate around concurrent refills.

## Test signals
Tests should cover parameter validation, cache load fill count, synchronous generation policies, async low-watermark refill, uniqueness/cancellation on drain, expiry behavior, concurrent `getAtMost()` calls for same/different keys, refiller exception propagation, and shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/ValueQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/package-info.java

## Purpose
This package-info file declares the `org.apache.hadoop.crypto.key` package. It provides package-level documentation placeholder for Hadoop key provider classes.

## Important APIs and types
It declares no classes or annotations beyond the package statement.

## Control flow
No runtime control flow exists.

## State and persistence
No state or persistence behavior exists.

## Dependencies and integration points
It groups key-provider abstractions, local providers, CLI, and extension classes under a common package for Javadocs and package metadata.

## Risks
No behavioral risk is present. Documentation could be expanded to describe provider contracts and security expectations.

## Test signals
No direct tests are needed. Javadoc/package generation can verify the package compiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/package-info.java

## Purpose
This package-info file documents the `org.apache.hadoop.crypto` package as containing crypto-related classes.

## Important APIs and types
It declares only the package statement and a short package-level Javadoc comment.

## Control flow
No runtime control flow exists.

## State and persistence
No state or persistence behavior exists.

## Dependencies and integration points
It provides package metadata for Hadoop crypto codecs, streams, cipher suites, and random implementations.

## Risks
No code risk exists. The package documentation is minimal and may not communicate codec/provider configuration expectations to API readers.

## Test signals
No direct tests are needed beyond compilation/Javadoc generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/random/OpensslSecureRandom.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/random/OpensslSecureRandom.java

## Purpose
`OpensslSecureRandom` is a `Random` implementation backed by OpenSSL secure random JNI when available, with Java `SecureRandom` fallback. It supplies random bytes for Hadoop crypto codecs.

## Important APIs and types
The class extends `java.util.Random`. Public APIs are constructor, static `isNativeCodeLoaded()`, `nextBytes(byte[])`, and overridden `setSeed(long)` and protected `next(int)`. Native methods are `initSR()` and `nextRandBytes(byte[])`.

## Control flow
The static initializer checks Hadoop native-code loading and OpenSSL build support, then calls native `initSR()` and sets `nativeEnabled` on success. Construction creates a fallback `SecureRandom` only when native support is unavailable. `nextBytes()` uses native `nextRandBytes()` when enabled and falls back if native generation fails. `next(int)` validates bit count, fills enough random bytes, assembles an integer, and right-shifts to the requested bit width. `setSeed()` is ignored because the generator self-seeds.

## State and persistence
State is static native-enabled status and optional per-instance fallback `SecureRandom`. No random state is persisted by Java code.

## Dependencies and integration points
It depends on `NativeCodeLoader`, `PerformanceAdvisory`, Hadoop preconditions, and native OpenSSL bindings. It is the default random class for `OpensslCtrCryptoCodec`.

## Risks
If native initialization partially fails, fallback must be non-null before `nextBytes()` calls; constructor handles this for new instances. Ignoring `setSeed()` is intentional but differs from deterministic `Random` expectations. Native `nextRandBytes()` failure silently falls back, which is safe but can hide performance degradation.

## Test signals
Tests should cover native unavailable fallback, `isNativeCodeLoaded()`, `nextBytes()` fills arrays, `next(int)` bounds and bit masking, `setSeed()` no-op behavior, and configured use through OpenSSL codecs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/random/OpensslSecureRandom.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/random/OsSecureRandom.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/random/OsSecureRandom.java

## Purpose
`OsSecureRandom` is a configurable `Random` implementation that reads random bytes directly from an operating-system device file such as `/dev/urandom`. It buffers data in an internal reservoir for efficient repeated calls.

## Important APIs and types
The class extends `Random` and implements `Closeable` and `Configurable`. Important methods are `setConf()`, `getConf()`, `nextBytes()`, protected `next(int)`, `close()`, visible-for-testing `isClosed()`, and private `fillReservoir(int)`.

## Control flow
`setConf()` records configuration, reads the random device path from `HADOOP_SECURITY_SECURE_RANDOM_DEVICE_FILE_PATH_KEY` with default fallback, and closes any open stream so the next read uses the new path. `nextBytes()` loops until the output is filled, calling `fillReservoir(0)` and copying from the reservoir. `next(int)` ensures at least four bytes are available, consumes four bytes, and masks to the requested bit count. `fillReservoir()` opens the device lazily and reads a full reservoir when the current position is too close to the end for the requested minimum.

## State and persistence
State is configuration, device path, open input stream, fixed 8192-byte reservoir, and current reservoir position. No random data is persisted. `close()` releases the stream and `finalize()` calls `close()`.

## Dependencies and integration points
It depends on Hadoop configuration keys, `IOUtils`, Java NIO `Files`, and `Random`. It can be selected via `hadoop.security.secure.random.impl`.

## Risks
Device-file reads can block or fail depending on platform/path. `fillReservoir()` converts I/O failures to runtime exceptions, so callers of `Random` APIs do not see checked exceptions. `next(int)` does not validate `nbits`; it assumes `Random` caller conventions. Finalization-based cleanup is best-effort only.

## Test signals
Tests should use a temporary deterministic byte file to validate reservoir refill, `nextBytes()` spanning reservoir boundaries, `next(int)` masking, `setConf()` path switching and stream close, `isClosed()`, and error behavior for missing device paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/random/OsSecureRandom.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/Abortable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/Abortable.java

## Purpose
`Abortable` is a public unstable filesystem interface for output streams that can abandon an active write so that closing the stream does not make partial data visible. It is especially relevant for object-store output streams and is passed through `FSDataOutputStream`.

## Important APIs and types
The interface declares `AbortableResult abort()`. Nested `AbortableResult` exposes `alreadyClosed()` and `anyCleanupException()`.

## Control flow
Implementations define abort semantics. The contract states that after abort, the active write must not become visible. If unsupported, `abort()` may throw `UnsupportedOperationException`. The result allows callers to distinguish first abort from an already closed/aborted stream and inspect cleanup exceptions that do not change abort semantics.

## State and persistence
The interface defines no state. Implementations typically manage upload/session state, temporary objects, multipart uploads, or local buffers. The persistence contract is negative: aborted data must not become visible.

## Dependencies and integration points
It depends only on `IOException` and Hadoop interface annotations. `FSDataOutputStream` can expose/pass through abort support from wrapped streams. Object store connectors implement this to cancel pending writes.

## Risks
The semantic requirement is strong: implementations must ensure close after abort cannot commit data, even under races or cleanup failures. The result's cleanup exception must not be confused with abort failure if data visibility was prevented. Callers need to handle unsupported streams.

## Test signals
Tests should cover abort before close, close after abort, repeated abort idempotence via `alreadyClosed()`, cleanup exception reporting, unsupported implementations, and object-store integration proving aborted data is not listed or readable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/Abortable.java -->

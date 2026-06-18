# subset-b-007386 Hadoop common crypto/key/fs test research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsForLocalFS.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsForLocalFS.java

## Purpose
`TestCryptoStreamsForLocalFS` adapts the shared `CryptoStreamsTestBase` contract to Hadoop's `LocalFileSystem`. It verifies crypto input/output streams over real local filesystem streams while documenting which base tests cannot run through the local checksum wrappers.

## Important APIs, Types, and Functions
The class extends `CryptoStreamsTestBase` and supplies `getOutputStream(int, byte[], byte[])` and `getInputStream(int, byte[], byte[])`. These create a `CryptoOutputStream` around `fileSys.create(file)` and a `CryptoInputStream` around `fileSys.open(file)`. The static `init()` method builds a minimal `Configuration`, binds `fs.file.impl` to `LocalFileSystem`, initializes `fileSys`, and resolves the shared `CryptoCodec`.

## Control Flow
Each test starts by deleting the temp root in `setUp()`, then delegates common key, IV, read, write, seek, and stream-behavior setup to the base class. The overridden stream factories route all data through one temp path. Cleanup makes the root writable, recursively deletes it, and asserts that the directory no longer exists.

## State and Persistence
State is persisted as an encrypted file under `GenericTestUtils.getTempPath("work-dir/testcryptostreamsforlocalfs")`. The static `fileSys` and base-class static `codec` are shared across tests, while each test removes on-disk state before and after execution.

## Dependencies and Integration Points
The test integrates `CryptoInputStream`, `CryptoOutputStream`, `CryptoCodec`, `FileSystem.getLocal`, `LocalFileSystem`, `FileUtil`, and JUnit 5 lifecycle annotations. It also inherits the broader crypto stream contract from `CryptoStreamsTestBase`.

## Risks and Edge Cases
Many inherited interface-specific tests are disabled because the wrapped local checksum streams do not support byte-buffer reads, byte-buffer positioned reads, `Syncable`, enhanced byte-buffer access, `seekToNewSource`, or `unbuffer`. These disabled methods are important compatibility signals: failures in subclasses may reflect missing wrapped-stream capabilities, not crypto logic.

## Test Signals
Passing enabled inherited tests signal correct encryption/decryption over `LocalFileSystem`, temp-file lifecycle cleanup, and ordinary stream semantics. Disabled tests preserve explicit expectations for unsupported local checksum stream features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsForLocalFS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsNormal.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsNormal.java

## Purpose
`TestCryptoStreamsNormal` runs the shared crypto stream tests against plain Java byte-array streams. It isolates crypto stream behavior when the wrapped streams do not implement Hadoop-specific interfaces such as `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `Syncable`, readahead/drop-behind controls, enhanced byte-buffer access, file descriptors, or `unbuffer`.

## Important APIs, Types, and Functions
The class extends `CryptoStreamsTestBase`. `init()` resolves the default `CryptoCodec`. `getOutputStream()` wraps an anonymous `ByteArrayOutputStream` in `CryptoOutputStream`; the anonymous stream snapshots its internal `buf` and `count` into instance fields on `flush()` and `close()`. `getInputStream()` creates a `ByteArrayInputStream` over the captured encrypted bytes and wraps it with `CryptoInputStream`.

## Control Flow
Base tests write through the crypto output stream, causing bytes to be captured on flush or close. Later reads construct a byte-array input stream over the saved bytes. Hadoop-interface tests are overridden as empty disabled JUnit methods so the inherited base suite only exercises generic stream behavior.

## State and Persistence
Encrypted test data is kept in memory in `buffer` and `bufferLen`; there is no filesystem persistence. Because the anonymous output stream exposes its backing array, correctness depends on using `bufferLen` to delimit valid data.

## Dependencies and Integration Points
The file integrates Java `ByteArrayInputStream`/`ByteArrayOutputStream`, Hadoop `CryptoInputStream`/`CryptoOutputStream`, `CryptoCodec`, `Configuration`, and JUnit 5. Its main integration point is the shared base class, not a concrete filesystem.

## Risks and Edge Cases
The test deliberately avoids Hadoop-only capabilities. It guards against accidental assumptions that all crypto stream users can seek, pread, byte-buffer-read, sync, or unbuffer. The buffer capture pattern is also a reminder that the backing array may be larger than the written payload.

## Test Signals
Enabled inherited tests signal that crypto streams work over minimal Java streams. Disabled tests signal expected `UnsupportedOperationException` or absent-interface behavior for seek, readFully, positioned reads, byte-buffer reads, sync, enhanced buffer access, `seekToNewSource`, combined operations, and `unbuffer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsNormal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsWithJceAesCtrCryptoCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsWithJceAesCtrCryptoCodec.java

## Purpose
This class runs the full `TestCryptoStreams` contract with the JCE AES CTR codec selected explicitly through configuration.

## Important APIs, Types, and Functions
It extends `TestCryptoStreams`. `init()` sets `HADOOP_SECURITY_CRYPTO_CODEC_CLASSES_AES_CTR_NOPADDING_KEY` to `JceAesCtrCryptoCodec.class.getName()`, obtains `codec` through `CryptoCodec.getInstance(conf)`, and asserts that the resolved implementation is exactly `JceAesCtrCryptoCodec`.

## Control Flow
The only local control flow is one-time codec selection in `@BeforeAll`; all stream behavior is inherited. The assertion fails early if codec discovery or configuration precedence selects an unexpected implementation.

## State and Persistence
The class mutates the inherited static `codec` field. It does not persist test data itself; inherited tests own file or buffer state.

## Dependencies and Integration Points
Dependencies include `Configuration`, `CommonConfigurationKeysPublic`, `CryptoCodec`, `JceAesCtrCryptoCodec`, AssertJ, and the inherited stream suite. It validates integration between Hadoop crypto configuration keys and JCE-backed AES/CTR implementation loading.

## Risks and Edge Cases
The main risk is configuration drift: if defaults or provider ordering change, this test ensures the configured codec class still wins. It does not test provider-specific JCE failures beyond class selection.

## Test Signals
A passing run signals that the AES CTR codec key resolves to JCE AES and that the inherited crypto stream tests pass with that codec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsWithJceAesCtrCryptoCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsWithJceSm4CtrCryptoCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsWithJceSm4CtrCryptoCodec.java

## Purpose
This subclass runs the shared crypto stream contract using the JCE SM4 CTR codec and the Bouncy Castle provider.

## Important APIs, Types, and Functions
`init()` sets the cipher suite to `SM4/CTR/NoPadding`, configures `HADOOP_SECURITY_CRYPTO_JCE_PROVIDER_KEY` to `BouncyCastleProvider.PROVIDER_NAME`, sets `HADOOP_SECURITY_CRYPTO_CODEC_CLASSES_SM4_CTR_NOPADDING_KEY` to `JceSm4CtrCryptoCodec`, resolves the codec, and asserts the resolved class.

## Control Flow
All test operations come from `TestCryptoStreams`; local setup only establishes provider, suite, and codec class. Failure in setup means SM4 support or provider registration is unavailable before inherited stream tests start.

## State and Persistence
The class writes only configuration state and the inherited static `codec`. Test data persistence is delegated to the parent test suite.

## Dependencies and Integration Points
It integrates Hadoop crypto configuration keys, Bouncy Castle, `JceSm4CtrCryptoCodec`, AssertJ, and the shared crypto stream test suite. It is a key signal for non-AES suite support in the JCE path.

## Risks and Edge Cases
This test depends on Bouncy Castle being available and named as expected. It does not auto-skip on missing provider; provider/class resolution failures surface as setup failures.

## Test Signals
Passing tests signal that SM4/CTR suite configuration, Bouncy Castle provider selection, and inherited crypto stream behavior all work through the JCE SM4 codec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsWithJceSm4CtrCryptoCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsWithOpensslAesCtrCryptoCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsWithOpensslAesCtrCryptoCodec.java

## Purpose
This class executes the common crypto stream tests with the native OpenSSL AES CTR codec and verifies that closing the codec closes its configured random source.

## Important APIs, Types, and Functions
`init()` requires the native profile via `GenericTestUtils.assumeInNativeProfile()`, configures `HADOOP_SECURITY_CRYPTO_CODEC_CLASSES_AES_CTR_NOPADDING_KEY` to `OpensslAesCtrCryptoCodec`, resolves `codec`, and asserts the class. `testCodecClosesRandom()` configures `OsSecureRandom` as the secure random implementation, obtains the codec, pulls the random through `getRandom()`, forces its internal stream to open with `nextBytes`, closes the codec, and verifies `random.isClosed()`.

## Control Flow
The class skips when native support is not expected. Once initialized, inherited stream tests exercise encryption and stream operations through OpenSSL. The local random test follows instantiate, trigger resource creation, assert open, close codec, assert closed.

## State and Persistence
State includes inherited static `codec` and an `OsSecureRandom` with an internal file stream. No durable test data is created locally.

## Dependencies and Integration Points
It integrates native-profile assumptions, OpenSSL-backed `OpensslAesCtrCryptoCodec`, `CryptoCodec`, `OsSecureRandom`, Hadoop crypto config keys, and inherited `TestCryptoStreams` behavior.

## Risks and Edge Cases
The test is environment-sensitive: missing native profile or OpenSSL support skips or fails setup. The resource-closure check guards against file descriptor leaks when codecs own random sources.

## Test Signals
Passing tests signal native AES CTR codec selection, inherited stream correctness, and proper cascade close from codec to `OsSecureRandom`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsWithOpensslAesCtrCryptoCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsWithOpensslSm4CtrCryptoCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsWithOpensslSm4CtrCryptoCodec.java

## Purpose
This class runs the common crypto stream suite with the native OpenSSL SM4 CTR codec and verifies secure-random resource cleanup.

## Important APIs, Types, and Functions
`init()` requires the native profile, assumes `OpensslCipher.isSupported(CipherSuite.SM4_CTR_NOPADDING)`, sets `HADOOP_SECURITY_CRYPTO_CIPHER_SUITE_KEY` to `SM4/CTR/NoPadding`, configures `HADOOP_SECURITY_CRYPTO_CODEC_CLASSES_SM4_CTR_NOPADDING_KEY` to `OpensslSm4CtrCryptoCodec`, resolves the codec, and asserts its class. `testCodecClosesRandom()` repeats this setup with `OsSecureRandom`, opens the random stream by calling `nextBytes`, and verifies `codecWithRandom.close()` closes the random.

## Control Flow
Setup first gates on native build and SM4 OpenSSL support. Inherited tests then run through `TestCryptoStreams`. The local cleanup test follows a direct lifecycle path: configure, instantiate, extract random, use random, close codec, assert closed.

## State and Persistence
The class mutates the inherited static `codec` and temporarily owns an `OsSecureRandom` stream. There is no independent filesystem persistence.

## Dependencies and Integration Points
Dependencies include OpenSSL native bindings, `CipherSuite.SM4_CTR_NOPADDING`, `OpensslSm4CtrCryptoCodec`, `OsSecureRandom`, Hadoop crypto configuration, JUnit assumptions, and the shared crypto stream suite.

## Risks and Edge Cases
SM4 support is optional even in native builds, so the suite uses an assumption before codec resolution. Resource leakage is the main local risk covered by the close test.

## Test Signals
Passing tests signal native SM4 suite support, correct codec discovery, inherited stream behavior, and proper random-source close propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsWithOpensslSm4CtrCryptoCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoUtils.java

## Purpose
`TestCryptoUtils` verifies JCE provider name constants and Bouncy Castle auto-registration behavior used by Hadoop crypto utilities.

## Important APIs, Types, and Functions
The class tests `CryptoUtils.BOUNCY_CASTLE_PROVIDER_NAME`, `CryptoUtils.getJceProvider(Configuration)`, and configuration keys `HADOOP_SECURITY_CRYPTO_JCE_PROVIDER_KEY`, `HADOOP_SECURITY_CRYPTO_JCE_PROVIDER_AUTO_ADD_KEY`, and `HADOOP_SECURITY_CRYPTO_JCE_PROVIDER_AUTO_ADD_DEFAULT`. Helper methods `assertRemoveProvider()` and `assertSetProvider()` manipulate and validate `java.security.Security`.

## Control Flow
The static initializer enables trace logging for `CryptoUtils`. `testProviderName()` checks the Hadoop constant against `BouncyCastleProvider.PROVIDER_NAME`. `testAutoAddDisabled()` removes the provider, disables auto-add, requests the provider name, and asserts Security still lacks Bouncy Castle. `testAutoAddEnabled()` confirms the default auto-add property, requests Bouncy Castle, verifies a real provider instance was added, then removes it.

## State and Persistence
The test mutates JVM-global provider state through `Security.addProvider` indirectly and `Security.removeProvider` directly. It leaves no durable files but must clean provider state to avoid cross-test leakage.

## Dependencies and Integration Points
Dependencies include Bouncy Castle, Java Security provider APIs, Hadoop `Configuration`, crypto config constants, `GenericTestUtils` logging, AssertJ, and JUnit assertions.

## Risks and Edge Cases
The tests are sensitive to JVM-global provider ordering and parallel execution. They explicitly remove Bouncy Castle before and after checks to reduce state bleed. They also guard the default of provider auto-add, which affects deployments that rely on Bouncy Castle without manual registration.

## Test Signals
Passing tests signal that provider constants match Bouncy Castle, disabling auto-add is honored, default auto-add is true, and `CryptoUtils.getJceProvider()` can register Bouncy Castle when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestOpensslCipher.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestOpensslCipher.java

## Purpose
`TestOpensslCipher` validates native OpenSSL cipher construction, input/output buffer preconditions, finalization preconditions, and suite support metadata.

## Important APIs, Types, and Functions
It exercises `OpensslCipher.getLoadingFailureReason()`, `OpensslCipher.getInstance(String)`, `init(int, byte[], byte[])`, `update(ByteBuffer, ByteBuffer)`, `doFinal(ByteBuffer)`, and `OpensslCipher.isSupported(CipherSuite)`. Static AES key and IV fixtures drive initialization.

## Control Flow
Each test assumes OpenSSL loaded successfully. `testGetInstance()` checks valid `AES/CTR/NoPadding`, invalid algorithm (`AES2`), and invalid padding. `testUpdateArguments()` initializes encryption, verifies heap buffers are rejected, then verifies insufficient direct output capacity throws `ShortBufferException`. `testDoFinalArguments()` verifies a heap output buffer is rejected. `testIsSupportedSuite()` checks `UNKNOWN` is false and AES CTR is supported.

## State and Persistence
The tests allocate local heap and direct `ByteBuffer` instances and native cipher state. They do not persist data outside the process.

## Dependencies and Integration Points
Dependencies include OpenSSL native bindings, Java `ByteBuffer`, JCE exception types, `CipherSuite`, `GenericTestUtils.assertExceptionContains`, and JUnit assumptions/assertions.

## Risks and Edge Cases
Native loading makes the suite environment-sensitive. The key edge cases are direct-buffer requirements and output capacity checks, both critical because the native layer cannot safely operate on arbitrary Java buffers.

## Test Signals
Passing tests signal correct error classification for unsupported cipher strings, strict direct-buffer validation, short-buffer handling, and advertised suite support for AES CTR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestOpensslCipher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/FailureInjectingJavaKeyStoreProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/FailureInjectingJavaKeyStoreProvider.java

## Purpose
`FailureInjectingJavaKeyStoreProvider` is a test-only `JavaKeyStoreProvider` wrapper that injects write and backup failures during flush/recovery tests.

## Important APIs, Types, and Functions
It defines scheme `failjceks`, wraps an existing `JavaKeyStoreProvider` via the copy constructor, exposes `setBackupFail(boolean)` and `setWriteFail(boolean)`, overrides `writeToNew(Path)` and `backupToOld(Path)`, and provides a nested `Factory` extending `KeyProviderFactory`.

## Control Flow
The factory recognizes `failjceks` URIs, rewrites them to normal `jceks` URIs, creates a real `JavaKeyStoreProvider`, and wraps it. During flush, `writeToNew()` throws when `writeFail` is true and `backupToOld()` throws when `backupFail` is true; otherwise calls delegate to the superclass.

## State and Persistence
The wrapper controls two boolean failure flags and otherwise uses the underlying keystore provider state. It is designed to perturb persistence steps involving `_NEW`, `_OLD`, and current keystore files.

## Dependencies and Integration Points
It integrates `JavaKeyStoreProvider`, `KeyProviderFactory`, Hadoop `Path`, URI parsing, and tests such as `TestKeyProviderFactory` that validate rollback after failed flushes.

## Risks and Edge Cases
`setWriteFail(boolean)` currently assigns `backupFail = b` rather than `writeFail = b`, which looks like a bug in the test helper and can make intended write-failure injection behave as backup-failure injection. The misspelled backup failure message is harmless but can weaken exact-message assertions.

## Test Signals
When used correctly, this provider should force flush exceptions and allow tests to assert that unflushed keys are rolled back and keystore recovery remains consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/FailureInjectingJavaKeyStoreProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestCachingKeyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestCachingKeyProvider.java

## Purpose
`TestCachingKeyProvider` validates timeout-based caching and cache invalidation for `CachingKeyProvider`.

## Important APIs, Types, and Functions
The tests mock `KeyProvider` methods `getCurrentKey`, `getKeyVersion`, `getMetadata`, `rollNewVersion`, `rollNewVersion(name, material)`, and `deleteKey`. They instantiate `CachingKeyProvider(mockProv, keyTimeoutMillis, currKeyTimeoutMillis)` and use Mockito call counts to prove cache hits and misses.

## Control Flow
`testCurrentKey()` caches a non-null current key, verifies repeat access avoids the provider, sleeps beyond the configured timeout, and verifies refresh. It also verifies null current keys are not cached. `testKeyVersion()` and `testMetadata()` repeat the same pattern for version and metadata lookups. `testRollNewVersion()` and `testDeleteKey()` populate caches, perform a mutation, then assert subsequent lookups hit the underlying provider again.

## State and Persistence
State is entirely in-memory: mock return values, cache entries, TTLs, and call counters. `KMSMetadata` is used in delete tests to describe the number of cached versions to purge.

## Dependencies and Integration Points
Dependencies include `CachingKeyProvider`, `KeyProvider`, `KMSClientProvider.KMSMetadata`, Mockito, `Configuration`, and JUnit. The tests integrate cache behavior with key lifecycle operations that mutate backing provider state.

## Risks and Edge Cases
Timing-based tests depend on sleeps long enough to exceed TTLs. Null values deliberately bypass caching; this avoids hiding newly created keys but increases backend calls for missing keys. Deletion invalidation must clear current-key, key-version, and metadata caches consistently.

## Test Signals
Passing tests signal cache hits for known values, no caching for unknown keys, TTL expiry refresh, and cache purge on roll and delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestCachingKeyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyProvider.java

## Purpose
`TestKeyProvider` verifies core `KeyProvider` value objects, naming helpers, option defaults, URI unnesting, generated key material, unknown-key rollover behavior, and configuration retention.

## Important APIs, Types, and Functions
It exercises `KeyProvider.buildVersionName`, `getBaseName`, `KeyVersion`, `Metadata`, `Options`, `KeyProvider.options(Configuration)`, `ProviderUtils.unnestUri(URI)`, `createKey`, `rollNewVersion`, `generateKey`, and `getConf`. The nested `MyKeyProvider` implements the abstract provider contract and captures generated algorithm, size, and material.

## Control Flow
Naming tests build and parse `name@version` strings and validate invalid/null input. Metadata tests serialize and deserialize metadata with and without descriptions/attributes, then verify `addVersion()` mutates only the deserialized object. Options tests verify config defaults and setters. URI tests validate nested provider URI conversion for HDFS, nested schemes, WASB, ABFS, S3A, file, and HTTPS. Material-generation tests call high-level `createKey`/`rollNewVersion` overloads and assert they delegate to `generateKey`. Unknown rollover expects an `IOException`.

## State and Persistence
State is in Java objects only: serialized metadata bytes/strings, options maps, generated material, and a test configuration. No keystore or credential persistence occurs in this file.

## Dependencies and Integration Points
Dependencies include `Configuration`, `Path`, `ProviderUtils`, `GenericTestUtils`, `LambdaTestUtils.intercept`, Java URI/date APIs, and core `KeyProvider` types.

## Risks and Edge Cases
Version-name parsing requires an `@` with a slash-bearing key path; invalid values must not silently parse. Metadata serialization must preserve optional descriptions, attributes, creation time, and version count. URI unnesting is high-risk because provider paths encode inner filesystems using authority syntax that can include users, ports, and `@` characters.

## Test Signals
Passing tests signal stable key naming, metadata round trips, option defaults, URI unnesting semantics, generated key material delegation, unknown-key rollover failure, and provider configuration retention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyProviderCryptoExtension.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyProviderCryptoExtension.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyProviderDelegationTokenExtension.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyProviderDelegationTokenExtension.java

## Purpose
This test verifies delegation-token extension wrapping for key providers, including the default no-token implementation and provider-supplied token behavior.

## Important APIs, Types, and Functions
It uses `KeyProviderDelegationTokenExtension.createKeyProviderDelegationTokenExtension`, `addDelegationTokens`, `DelegationTokenExtension`, `getCanonicalServiceName`, `getDelegationToken`, `Credentials`, and `Token`. `MockKeyProvider` is an abstract test type that extends `KeyProvider` and implements `DelegationTokenExtension`.

## Control Flow
The test first wraps a normal `UserProvider`, calls `addDelegationTokens`, and verifies an empty non-null token array. It then mocks a provider that returns a canonical service name and a token, wraps it, calls `addDelegationTokens("renewer", credentials)`, and verifies the returned token and credentials entry.

## State and Persistence
State is in-memory `Credentials` plus a mocked token with kind `kind` and service `tservice`. No persistent provider data is created.

## Dependencies and Integration Points
Dependencies include `UserProvider`, Hadoop `Credentials`, `Text`, security `Token`, Mockito, and JUnit. The test validates integration between key providers and Hadoop delegation-token collection.

## Risks and Edge Cases
Default providers must not return null token arrays. Providers with canonical service names must store tokens under that canonical service in `Credentials`, not just return them to the caller.

## Test Signals
Passing tests signal correct default extension creation, empty-token behavior, provider extension delegation, token metadata preservation, and credentials insertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyProviderDelegationTokenExtension.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyProviderFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyProviderFactory.java

## Purpose
`TestKeyProviderFactory` validates provider discovery, provider CRUD semantics, user-provider credential persistence, JCEKS persistence and recovery, keystore permissions, password-file handling, direct URI lookup, and behavior with keytool-created keystores.

## Important APIs, Types, and Functions
The suite exercises `KeyProviderFactory.getProviders`, `KeyProviderFactory.get`, `UserProvider`, `JavaKeyStoreProvider`, `FailureInjectingJavaKeyStoreProvider`, `KeyProvider` CRUD methods, `ProviderUtils.unnestUri`, `FileSystem` status/permissions, and `UserGroupInformation` credentials. `checkSpecificProvider()` is the shared provider contract for missing keys, create/delete/recreate, wrong key lengths, roll, flush, reload, key listing, and version listing.

## Control Flow
Factory tests parse comma-separated provider paths and error on unknown or malformed URIs. `testUserProvider()` runs the shared contract and then verifies secret keys landed in current-user credentials. `testJksProvider()` creates a file-backed JCEKS provider, runs the shared contract, injects flush failures, verifies state rollback, checks file mode, tests recovery from `_OLD` and `_NEW` files, validates conflict handling when current and `_NEW` coexist, tests permission retention, and rejects uppercase key names. Password tests create a keystore with a configured password file and verify bad/missing password settings fail. URI and keytool tests check direct factory lookup and error handling for non-Hadoop keytool entries.

## State and Persistence
The test writes real keystore files under a `FileSystemTestHelper` temp root. It manipulates current, `_OLD`, and `_NEW` keystore files, filesystem permissions, and current-user credentials. Provider flush/reload boundaries are central to the persistence contract.

## Dependencies and Integration Points
Dependencies include local `FileSystem`, `FileStatus`, `FsPermission`, `Path`, `Configuration`, `ProviderUtils`, `UserGroupInformation`, `Credentials`, test keystore resource `hdfs7067.keystore`, and the failure-injecting provider factory.

## Risks and Edge Cases
High-risk behavior includes crash recovery around `_NEW`/`_OLD`, rollback after failed flush, file permission preservation, uppercase key-name rejection, password file discovery, and compatibility with keystores containing non-Hadoop secret-key entries. The write-failure helper has a suspicious setter bug, so failure-injection coverage should be interpreted carefully.

## Test Signals
Passing tests signal provider path parsing, user and JCEKS key lifecycle correctness, durable reload after flush, credential storage, recovery file handling, permission retention, password-file enforcement, direct URI provider lookup, and defensive errors for incompatible keytool entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyProviderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyShell.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyShell.java

## Purpose
`TestKeyShell` validates the command-line key management tool against a temporary JCEKS provider, including lifecycle operations, warnings, strict mode, cipher options, descriptions, and attributes.

## Important APIs, Types, and Functions
It uses `KeyShell.run(String[])`, `KeyShell.NO_VALID_PROVIDERS`, `ProviderUtils` password warning/error strings, and `KeyProviderFactory.KEY_PROVIDER_PATH`. Helpers `deleteKey()` and `listKeys()` execute shell commands and assert return codes/output.

## Control Flow
`setup()` creates a unique temp directory, builds a `jceks://file...` provider URI, and redirects stdout/stderr to byte buffers. Tests run CLI commands for `create`, `list`, `roll`, `invalidateCache`, and `delete`. Negative tests cover invalid key size, invalid cipher, invalid provider, transient-provider-only configuration, strict no-password mode, malformed attributes, and duplicate attributes.

## State and Persistence
The test writes an actual JCEKS keystore in a temp directory. It also mutates JVM-global `System.out` and `System.err` during each test and restores them in `cleanUp()`.

## Dependencies and Integration Points
Dependencies include `KeyShell`, `Configuration`, `Path`, `ProviderUtils`, `GenericTestUtils`, local file-backed JCEKS, and JUnit. It bridges command-line parsing with provider lifecycle operations and user-facing output strings.

## Risks and Edge Cases
Output assertions are sensitive to wording changes. Strict mode and no-password warnings protect users from insecure provider setup. Attribute parsing trims whitespace, allows values containing `=`, rejects missing names/values, and rejects repeated attribute names.

## Test Signals
Passing tests signal successful CLI create/list/roll/invalidate/delete flows, metadata display, description support, invalid-option failures, transient-provider warnings, strict password enforcement, full cipher names, and robust attribute parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestValueQueue.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestValueQueue.java

## Purpose
`TestValueQueue` verifies queue warmup, low-watermark refill, synchronous generation policies, drain behavior, and partial warmup failures for KMS encrypted-key prefetch queues.

## Important APIs, Types, and Functions
It exercises `ValueQueue<T>`, `QueueRefiller<T>`, `SyncGenerationPolicy.ALL`, `ATLEAST_ONE`, and `LOW_WATERMARK`, plus `initializeQueuesForKeys`, `getNext`, `getAtMost`, `getSize`, `drain`, and `shutdown`. `MockFiller` records fill requests in a `LinkedBlockingQueue<FillInfo>` and appends `"test"` values.

## Control Flow
Initial and warmup tests verify first-fill sizes based on queue capacity and low-watermark percentage. Refill tests consume values, wait for asynchronous refill using `GenericTestUtils.waitFor`, and verify exact filler counts. Policy tests drain queues and check how many values are synchronously generated before asynchronous refill starts. Partial warmup uses reflection and a spy `LoadingCache` to force one key lookup to fail, then asserts an `IOException` and only partial fill calls.

## State and Persistence
State is in-memory queues, cache entries, background refill tasks, and recorded fill calls. Tests call `shutdown()` to stop queue workers.

## Dependencies and Integration Points
Dependencies include `ValueQueue`, Guava `LoadingCache` via Hadoop thirdparty shading, Apache Commons `FieldUtils`, Mockito spies, `GenericTestUtils.waitFor`, concurrency utilities, and JUnit timeouts.

## Risks and Edge Cases
The suite is concurrency- and timing-sensitive. It guards low-watermark math, no-refill conditions above the watermark, asynchronous refill after synchronous calls, drained queue behavior, partial warmup failure propagation, and worker shutdown.

## Test Signals
Passing tests signal correct initial fill counts, multi-key warmup, partial-failure handling, async refill thresholds, no unnecessary refill, `getAtMost` policy semantics, and drain suppression of refill.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestValueQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/kms/TestKMSClientProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/kms/TestKMSClientProvider.java

## Purpose
`TestKMSClientProvider` validates delegation-token service selection for a single KMS client, including the newer full provider-URI token service and legacy `host:port` token service.

## Important APIs, Types, and Functions
It exercises `KMSClientProvider.selectDelegationToken(Credentials, Text)`, instance `selectDelegationToken(Credentials)`, `createAuthenticatedURL()`, and `DelegationTokenAuthenticatedURL.selectDelegationToken(URL, Credentials)`. Tokens use `KMSDelegationToken.TOKEN_KIND`.

## Control Flow
`setup()` disables IP-based token services and initializes one token with service `kms://https@host:16000/kms` and one legacy token with service `host:16000`. Tests verify static selection only matches requested service, instance selection accepts legacy service when appropriate, newer URI-format tokens win when both exist, and authenticated URLs can select either service format.

## State and Persistence
State is in-memory credentials and tokens. Each provider is closed in `finally` blocks where instantiated.

## Dependencies and Integration Points
Dependencies include `KMSClientProvider`, `KMSDelegationToken`, Hadoop `Credentials`, `SecurityUtil`, `DelegationTokenAuthenticatedURL`, Java `URI`/`URL`, and JUnit.

## Risks and Edge Cases
Backward compatibility with legacy token service names is critical for existing clients. The newer URI service must take precedence when both tokens exist to avoid selecting stale or less-specific credentials.

## Test Signals
Passing tests signal correct KMS token lookup by service text, legacy fallback, new-format precedence, and authenticated URL token selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/kms/TestKMSClientProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/kms/TestLoadBalancingKMSClientProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/kms/TestLoadBalancingKMSClientProvider.java

## Purpose
`TestLoadBalancingKMSClientProvider` verifies multi-KMS URI parsing, round-robin provider selection, retry/failover policy by operation idempotence and exception class, warmup error handling, token service naming, and current-user credential lookup.

## Important APIs, Types, and Functions
The suite exercises `KMSClientProvider.Factory.createProvider`, `LoadBalancingKMSClientProvider.getProviders`, `getCanonicalServiceName`, `createKey`, `getCurrentKey`, `getKeys`, `getKeyVersions`, `generateEncryptedKey`, `decryptEncryptedKey`, `rollNewVersion`, `warmUpEncryptedKeys`, and provider `getActualUgi`. It uses mocked `KMSClientProvider` instances and config key `KMS_CLIENT_FAILOVER_MAX_RETRIES_KEY`.

## Control Flow
Creation tests parse `kms://http@host...` URIs into one or more backing KMS URLs. Load-balancing tests verify round-robin calls and distinguish retriable `IOException` from non-retriable `NoSuchAlgorithmException`. Retry tests cover all-bad nodes, idempotent versus non-idempotent operations, access-control and runtime exceptions that stop failover, connection/route/host/timeout/socket/SSL exceptions that can fail over or retry, exact configured retry counts, and default retry counts. Warmup tests require all providers to be tried and succeed if at least one succeeds. Token tests compare legacy `host:port` service names with URI-format services. UGI tests run under a test user and verify providers use the current user, not the login user.

## State and Persistence
State is in-memory mocks, credentials, tokens, retry counters, and UGI context. No KMS server or durable key store is used.

## Dependencies and Integration Points
Dependencies include KMS client classes, Hadoop security classes, token kinds, `UserGroupInformation`, `SecurityUtil`, `CommonConfigurationKeysPublic`, Mockito, `LambdaTestUtils.intercept`, and network/SSL exception classes.

## Risks and Edge Cases
This file encodes subtle policy boundaries: non-idempotent mutations should not be blindly replayed on ambiguous IO failures, authorization/runtime failures should not be hidden by failover, transient network and SSL failures may retry, URI token services must coexist with legacy services, and current-user credentials must be honored in Kerberos mode.

## Test Signals
Passing tests signal correct multi-host URL construction, round-robin behavior, failover classification, retry counts, warmup tolerance, exception wrapping preservation, token service naming, and UGI selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/kms/TestLoadBalancingKMSClientProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/random/TestOpensslSecureRandom.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/random/TestOpensslSecureRandom.java

## Purpose
`TestOpensslSecureRandom` smoke-tests that the OpenSSL secure-random implementation returns changing values for byte arrays and primitive random methods.

## Important APIs, Types, and Functions
It constructs `OpensslSecureRandom` and calls `nextBytes`, `nextInt`, `nextLong`, `nextFloat`, and `nextDouble`. `checkRandomBytes()` compares two arrays and loops until values differ.

## Control Flow
Each test obtains two generated values and loops until they are different. The JUnit timeout is the failure mechanism for a broken implementation that returns a constant stream.

## State and Persistence
State is limited to generated byte arrays and primitive values. No explicit close or persistent state appears in this test class.

## Dependencies and Integration Points
Dependencies include `OpensslSecureRandom`, Java array comparison, and JUnit timeouts. It indirectly depends on native OpenSSL random support.

## Risks and Edge Cases
These tests are probabilistic smoke tests, not statistical randomness validation. They can theoretically loop on equal values by chance, but the configured lengths and timeouts make constant-output failures the main target.

## Test Signals
Passing tests signal that OpenSSL random methods do not return a fixed constant for common byte lengths and primitive types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/random/TestOpensslSecureRandom.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/random/TestOsSecureRandom.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/random/TestOsSecureRandom.java

## Purpose
`TestOsSecureRandom` verifies the OS-backed secure-random implementation on Linux, including changing output for bytes/primitives and reservoir refill behavior.

## Important APIs, Types, and Functions
`getOsSecureRandom()` assumes Linux, creates `OsSecureRandom`, and calls `setConf(new Configuration())`. Tests call `nextBytes`, `nextInt`, `nextLong`, `nextFloat`, `nextDouble`, `close`, and the repeated `nextLong` path that refills the internal reservoir.

## Control Flow
Each randomness test creates a configured random source, obtains two values, loops until they differ, then closes the random. `testRefillReservoir()` calls `nextLong()` 8196 times to exceed the reservoir capacity and exercise refill without validating individual values.

## State and Persistence
The implementation owns an OS random stream that must be closed. Test data stays in memory; no durable files are created by the test itself.

## Dependencies and Integration Points
Dependencies include `OsSecureRandom`, Hadoop `Configuration`, Apache Commons `SystemUtils.IS_OS_LINUX`, JUnit assumptions/timeouts, and Java arrays.

## Risks and Edge Cases
The suite only runs on Linux. Like the OpenSSL random tests, it is a constant-output smoke test rather than statistical validation. The refill test guards a long-running internal state path and could reveal stream or reservoir boundary bugs.

## Test Signals
Passing tests signal Linux-only OS random initialization, non-constant byte and primitive output, close behavior after use, and reservoir refill stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/random/TestOsSecureRandom.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FCStatisticsBaseTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FCStatisticsBaseTest.java

## Purpose
`FCStatisticsBaseTest` is an abstract base suite for `FileContext` statistics accounting across filesystem implementations.

## Important APIs, Types, and Functions
It exercises `FileSystem.Statistics`, `FileContext.getStatistics(URI)`, `FileContext.getAllStatistics()`, `FSDataInputStream`, `FileContextTestHelper.createFile`, and abstract hooks `verifyReadBytes`, `verifyWrittenBytes`, and `getFsUri`. `getSchemeAuthorityUri()` normalizes the stats map lookup URI.

## Control Flow
`testStatisticsOperations()` validates counter increments, write-op updates from `SubjectInheritingThread`, copy-constructor behavior, and reset. `testStatistics()` creates a file through `FileContext`, opens and reads it sequentially and positionally, verifies read/write byte counts using subclass-specific hooks, checks the global stats map, and deletes the file. `testStatisticsThreadLocalDataCleanUp()` populates per-thread stats through a fixed thread pool, shuts the pool down, forces GC, and waits until weak thread-local data references are cleaned up while aggregate counts remain.

## State and Persistence
The suite persists a test file through the subclass-provided `FileContext`. Statistics state includes global URI-scoped counters and per-thread data tracked by `Statistics`.

## Dependencies and Integration Points
Dependencies include `FileContext`, `FileSystem.Statistics`, `FileContextTestHelper`, `SubjectInheritingThread`, Guava `Uninterruptibles`, executor services, `GenericTestUtils.waitFor`, and subclass filesystem implementations.

## Risks and Edge Cases
Statistics behavior varies by filesystem, so byte assertions are abstract. Thread-local cleanup relies on GC and weak-reference behavior, making timing important. The stats map key must use scheme/authority normalization.

## Test Signals
Passing subclasses signal correct counter mutation, copy/reset behavior, FileContext read/write accounting, global statistics lookup, and cleanup of stale per-thread statistics data without losing aggregate counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FCStatisticsBaseTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FSMainOperationsBaseTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FSMainOperationsBaseTest.java

## Purpose
`FSMainOperationsBaseTest` is a broad abstract contract suite for `FileSystem` implementations, covering status, working directory, mkdirs, listings, globbing, read/write/delete, rename semantics, stream close idempotence, wrapped streams, and raw-local copy behavior.

## Important APIs, Types, and Functions
It extends `FileSystemTestHelper` and requires subclasses to implement `createFileSystem()`. Important hooks include `renameSupported()` and `unwrapException(IOException)`. It exercises `FileSystem.getStatus`, `setWorkingDirectory`, `mkdirs`, `getFileStatus`, `listStatus`, `globStatus`, `create`, `open`, `delete`, `rename(Path, Path, Options.Rename...)`, permissions, `FSDataInputStream`, `FSDataOutputStream`, `RawLocalFileSystem.copyToLocalFile`, and helper filters `DEFAULT_FILTER` and `TEST_X_FILTER`.

## Control Flow
`setUp()` creates the filesystem and a test root; `tearDown()` deletes it. Early tests validate status and working-directory resolution for `.`, `..`, relative, and absolute paths. Makedir tests verify parent creation and failure under existing files. Listing and glob tests create deterministic directory trees and assert null versus empty-array semantics, wildcard matches, and filter results. Write/read/delete tests cover empty through two-block files. Delete tests cover nonexistent files, nonrecursive directory failure, recursive delete, and empty directory delete. Rename tests cover missing paths, missing parents, parent-as-file, file/directory self-renames, overwrite behavior, non-empty destination constraints, and directory-to-file failures. Stream tests assert double close is harmless and wrapped input streams are exposed. The raw-local copy test verifies `copyToLocalFile(..., useRawLocalFileSystem=true)` avoids CRC sidecar creation.

## State and Persistence
The suite creates and deletes many files and directories under the subclass filesystem's test root. Static data contains deterministic byte content for read/write verification. Working directory state is mutated during tests.

## Dependencies and Integration Points
Dependencies include `FileSystem`, `Path`, `FileStatus`, `PathFilter`, `Options.Rename`, `FsPermission`, `RawLocalFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `Configuration`, and subclass filesystem implementations such as local, HDFS, or object stores.

## Risks and Edge Cases
This is a compatibility baseline, so backend differences around rename support, exception wrapping, permissions, glob null/empty semantics, recursive directory behavior, overwrite rules, and CRC creation are high risk. Some object stores or non-POSIX filesystems may need hook overrides.

## Test Signals
Passing subclasses signal conformance to core `FileSystem` operations: path resolution, metadata, listing/glob filtering, file IO lengths/content, deletion contracts, rename edge cases, close idempotence, wrapped stream access, and raw local copy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FSMainOperationsBaseTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FSTestWrapper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FSTestWrapper.java

## Purpose
`FSTestWrapper` is an abstract test helper that unifies common test operations for both Hadoop `FileSystem` and `FileContext` implementations.

## Important APIs, Types, and Functions
It implements `FSWrapper`, defines default block constants, randomizes a test root under the supplied or default test directory, provides `getFileData`, qualified test-root helpers, absolute-root helpers, and abstract helper methods for local wrapper access, default working directory, file creation, append, existence/type checks, read/write, path containment, and file/link status checks.

## Control Flow
Construction chooses a base test directory and salts it with random alphanumeric text for parallel safety. Root helper methods qualify paths through the wrapped filesystem abstraction. `getAbsoluteTestRootDir()` lazily resolves relative roots against the current working directory to avoid later working-directory changes corrupting cleanup paths.

## State and Persistence
State includes `testRootDir` and cached `absTestRootDir`. Actual file persistence is delegated to concrete wrappers.

## Dependencies and Integration Points
Dependencies include `FSWrapper`, `Path`, `FileStatus`, `Options.CreateOpts`, `GenericTestUtils`, and `RandomStringUtils`. It is the bridge layer used by generic tests that should run against both `FileSystem` and `FileContext`.

## Risks and Edge Cases
Randomized roots reduce parallel-test collisions but make path debugging less deterministic. Relative root handling must be cached carefully because tests may mutate the working directory. Concrete wrappers must keep behavior aligned despite API differences between `FileSystem` and `FileContext`.

## Test Signals
Subclasses using this helper should produce consistent file data, qualified paths, absolute cleanup paths, and type/status assertions across both filesystem abstraction families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FSTestWrapper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FSWrapper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FSWrapper.java

## Purpose
`FSWrapper` defines a common interface for filesystem operations used by generic tests, effectively extracting a `FileContext`-like API that can be implemented over multiple Hadoop filesystem abstractions.

## Important APIs, Types, and Functions
The interface declares working-directory methods, path qualification, create, mkdir, delete, open, replication, rename, permission/owner/time mutation, checksum lookup, file and link status, symlink target, block locations, symlink creation, status iteration, listing, and globbing. It uses `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `FileChecksum`, `BlockLocation`, `RemoteIterator`, `PathFilter`, `Options.CreateOpts`, and `Options.Rename`.

## Control Flow
There is no implementation control flow in this file. It defines the operations that concrete wrappers must route to `FileSystem` or `FileContext`.

## State and Persistence
The interface owns no state. State and persistence are entirely in implementing wrappers and their backing filesystems.

## Dependencies and Integration Points
Dependencies include Hadoop path, permission, checksum, symlink, block-location, and stream types plus security exceptions. It is an integration seam for shared filesystem contract tests.

## Risks and Edge Cases
Because it abstracts two similar but not identical APIs, implementers must preserve exception types, symlink semantics, recursive delete behavior, create flags, rename options, and status/link-status distinctions.

## Test Signals
Any generic test written against `FSWrapper` can validate a concrete wrapper's conformance across creation, mutation, metadata, links, block locations, listing, and globbing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FSWrapper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FileContextCreateMkdirBaseTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FileContextCreateMkdirBaseTest.java

## Purpose
`FileContextCreateMkdirBaseTest` is an abstract contract suite for `FileContext` create and mkdir behavior across filesystem implementations.

## Important APIs, Types, and Functions
It uses a static subclass-provided `FileContext fc`, `FileContextTestHelper`, `fc.mkdir`, `fc.delete`, `fc.rename`, `fc.getFileStatus`, helper methods `createFile` and `createFileNonRecursive`, `ContractTestUtils.assertIsDirectory`, `assertIsFile`, and `LambdaTestUtils.intercept`.

## Control Flow
`setUp()` ensures the test root exists and `tearDown()` deletes it. Mkdir tests cover nonrecursive success with existing parent, nonrecursive failure with missing parent, recursive success with existing or missing parents, creation of all intermediate parents, and recursive mkdir failure when an intermediate path is a file. `testWithRename()` creates a nested tree with files, renames `d1/d2/d3` to `d1/d4`, and verifies directory/file preservation. Create tests cover recursive and nonrecursive file creation with existing and missing parent directories.

## State and Persistence
Tests persist directories and files under the `FileContextTestHelper` root for the configured `FileContext`. Rename tests move actual directory subtrees.

## Dependencies and Integration Points
Dependencies include `FileContext`, `FileContextTestHelper`, `Path`, `FileContext.DEFAULT_PERM`, contract test utilities, `GenericTestUtils` logging, and subclass filesystem implementations.

## Risks and Edge Cases
The key edge cases are recursive versus nonrecursive parent creation, file-as-directory conflicts, intermediate parent status, and subtree preservation during rename. Error assertions are broad `IOException` checks except for the conflict case, which checks the operation context string.

## Test Signals
Passing subclasses signal correct `FileContext` mkdir/create parent semantics, file conflict detection, recursive intermediate directory creation, nonrecursive failure behavior, and rename preservation of nested files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FileContextCreateMkdirBaseTest.java -->

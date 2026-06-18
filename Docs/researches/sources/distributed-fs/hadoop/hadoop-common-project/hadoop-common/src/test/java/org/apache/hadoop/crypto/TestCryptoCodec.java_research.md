# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoCodec.java

## Purpose

`TestCryptoCodec` validates Hadoop crypto codec implementations and interoperability. It tests JCE and OpenSSL AES/CTR codecs, JCE and OpenSSL SM4/CTR codecs where supported, encryption/decryption round trips, cross-codec interoperability, secure-random generation, byte-at-a-time reads, seeked decryption, and IV calculation correctness.

## Important APIs and types

- Codec classes: `JceAesCtrCryptoCodec`, `JceSm4CtrCryptoCodec`, `OpensslAesCtrCryptoCodec`, and `OpensslSm4CtrCryptoCodec`.
- Stream classes: `CryptoOutputStream` and `CryptoInputStream`.
- Configuration keys: cipher-suite key, SM4 codec-class key, and JCE provider key.
- Native/OpenSSL guards: `GenericTestUtils.assumeInNativeProfile`, `NativeCodeLoader.buildSupportsOpenssl`, `OpensslCipher.getLoadingFailureReason`, and `OpensslCipher.isSupported`.
- Test data and buffers: `RandomDatum`, `DataOutputBuffer`, `DataInputBuffer`, `SecureRandom`, and `TestCryptoStreams.FakeInputStream`.
- IV reference calculation uses `BigInteger` and Guava `Longs.toByteArray`.

## Control flow

Each codec test configures assumptions and provider settings, then calls `cryptoCodecTest` with an encryption codec class, a decryption codec class, a record count, and an IV. AES tests verify JCE-to-JCE, JCE-to-OpenSSL, OpenSSL-to-OpenSSL, and OpenSSL-to-JCE paths. SM4 tests set cipher suite/provider configuration and verify JCE/OpenSSL paths when supported. Overflow scenarios set the low eight IV bytes to `0xff` before round trips.

`cryptoCodecTest` reflectively constructs the encryption codec, generates `RandomDatum` records, encrypts them, reflectively constructs the decryption codec, decrypts through buffered `DataInputStream`, and compares every key/value pair plus hash-map lookup semantics. It then re-decrypts byte-by-byte and re-decrypts after seeking one third into the encrypted stream. Finally it calls `testSecureRandom`, which asks the codec for random byte arrays of several lengths and asserts two generated arrays differ.

`testCalculateIV` creates a JCE AES codec and compares `calculateIV(initIV, counter, IV)` against a `BigInteger` reference across overflow, sequential random IV/counter ranges, and random counter values.

## State and persistence behavior

Static `key` and `iv` byte arrays are regenerated before each test. `Configuration conf`, record count, and random seed are instance state. Data is held in memory buffers. Native/OpenSSL availability affects whether tests execute or are skipped.

## Dependencies and integration points

The file integrates codec class loading through Hadoop `ReflectionUtils`, crypto stream read/write paths, OpenSSL native support, BouncyCastle for SM4 JCE provider selection, Hadoop random writable data, and the fake seekable input stream from `TestCryptoStreams`.

## Risks and edge cases

- Native-profile and OpenSSL assumptions mean important interoperability paths may be skipped in non-native test profiles.
- Secure-random tests only assert non-equality between two arrays; they do not provide statistical quality guarantees.
- `testCalculateIV` is expensive because it runs many counters across many random IVs; timeout protects hangs but not necessarily performance drift.
- Cross-codec tests rely on class names as strings; renames or provider changes require test updates.
- Static mutable key/IV arrays are shared within the test class and must be reset before each test.

## Test signals

Strong signals include full record round trips, zero-record behavior, cross-provider interoperability, counter overflow IV handling, byte-at-a-time decryption, seeked decryption, secure-random output shape/non-repeat, and independent IV arithmetic validation.

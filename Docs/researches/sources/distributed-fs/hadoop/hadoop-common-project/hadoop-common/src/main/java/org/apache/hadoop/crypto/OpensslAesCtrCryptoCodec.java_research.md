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

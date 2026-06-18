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

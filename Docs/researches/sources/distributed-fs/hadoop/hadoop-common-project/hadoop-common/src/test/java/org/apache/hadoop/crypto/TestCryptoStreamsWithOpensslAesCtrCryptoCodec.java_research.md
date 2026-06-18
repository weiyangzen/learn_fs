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

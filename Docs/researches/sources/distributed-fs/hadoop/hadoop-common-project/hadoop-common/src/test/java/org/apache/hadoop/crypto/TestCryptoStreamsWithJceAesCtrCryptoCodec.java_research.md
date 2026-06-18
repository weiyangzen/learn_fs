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

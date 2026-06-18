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

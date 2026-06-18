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

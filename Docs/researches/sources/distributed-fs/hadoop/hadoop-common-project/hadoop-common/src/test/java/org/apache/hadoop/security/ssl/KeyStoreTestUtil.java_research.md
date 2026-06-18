<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/KeyStoreTestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/KeyStoreTestUtil.java

## Purpose
Provides reusable SSL test utilities for generating certificates and key pairs, creating JKS key/trust stores, writing Hadoop SSL configuration files, provisioning credential-provider passwords, and relaxing `HttpsURLConnection` trust/hostname checks for tests.

## Important APIs, Types, And Functions
Important helpers include `generateCertificate`, `generateKeyPair`, `createKeyStore`, `createTrustStore`, `bytesToKeyStore`, `setupSSLConfig`, `createClientSSLConfig`, `createServerSSLConfig`, `saveConfig`, `provisionPasswordsToCredentialProvider`, `getSslConfig`, and `setAllowAllSSL`. It also defines default server/client/trust-store passwords.

## Control Flow
`setupSSLConfig` creates optional client credentials, mandatory server credentials, optional truststore, client/server XML configuration files, and mutates the caller's master `Configuration` to point `SSLFactory` at those files. Config creation resolves mode-specific property names through `FileBasedKeyStoresFactory`. `setAllowAllSSL` builds a permissive trust manager and optional client key manager, initializes an `SSLContext`, and installs the socket factory plus `NoopHostnameVerifier`.

## State And Persistence
This utility writes JKS files, XML config files, and a credential-provider JKS under test directories. It deletes known generated files in `cleanupSSLConfig`. Filename generation includes `test.unique.fork.id` to reduce parallel test collisions.

## Dependencies And Integration Points
Depends on Hadoop `Configuration`, `Path`, credential provider APIs, `SSLFactory`, `FileBasedKeyStoresFactory`, Bouncy Castle `X509V1CertificateGenerator`, JSSE key/trust manager APIs, and Apache HTTP's `NoopHostnameVerifier`. Many SSL tests depend on it for consistent stores and config.

## Risks
The generated certificates use 1024-bit RSA and SHA1 signatures, which are acceptable for compatibility tests but weak by modern production standards. File cleanup is best-effort. Permissive SSL helpers intentionally disable certificate and hostname validation and must remain test-only. Shared temp directories and classpath config writing can be sensitive under parallel execution despite fork-id suffixing.

## Test Signals
Downstream tests signal correctness by successfully initializing `SSLFactory`, reloading stores, resolving credential-provider passwords, reading serialized keystores, and completing or deliberately failing TLS handshakes with generated materials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/KeyStoreTestUtil.java -->

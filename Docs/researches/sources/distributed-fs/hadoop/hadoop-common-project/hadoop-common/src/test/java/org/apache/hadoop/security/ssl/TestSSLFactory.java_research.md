<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/TestSSLFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/TestSSLFactory.java

## Purpose
Tests `SSLFactory` configuration loading, client/server mode API restrictions, cipher exclusion, hostname verifier selection, connection configuration, password/key-password combinations, credential-provider lookup, and missing trust/client-cert options.

## Important APIs, Types, And Functions
Core targets are `SSLFactory.readSSLConfiguration`, `init`, `destroy`, `createSSLSocketFactory`, `createSSLServerSocketFactory`, `createSSLEngine`, `getHostnameVerifier`, `configure`, and `isClientCertRequired`. Helpers include `createConfiguration`, `serverMode`, `runDelegatedTasks`, `wrap`, `unwrap`, and `checkSSLFactoryInitWithPasswords`.

## Control Flow
Setup writes generated key/trust stores and SSL XML config into the test classpath. Configuration tests check fallback to the input configuration when XML is missing and classpath precedence when XML exists. Mode tests assert client-only and server-only APIs throw in the wrong mode. The weak-cipher test drives client and server `SSLEngine` instances through buffer-based handshaking after enabling only ciphers excluded by the server, expecting `SSLHandshakeException`. Password tests create stores with explicit or default key passwords and initialize `SSLFactory` in both modes.

## State And Persistence
Writes keystores and XML configs under a temp/classpath directory and cleans them before and after each test. It temporarily changes the JVM security property `ssl.KeyManagerFactory.algorithm` in one test and restores it.

## Dependencies And Integration Points
Depends heavily on `KeyStoreTestUtil`, `FileBasedKeyStoresFactory`, JSSE `SSLEngine`, `HttpsURLConnection`, Hadoop credential providers, `StringUtils.getTrimmedStrings`, and Hadoop test logging utilities. It validates the high-level SSL configuration surface used by Hadoop HTTP/RPC components.

## Risks
Classpath config files and global security properties can interfere with parallel tests if cleanup or restore fails. The weak-cipher test is sensitive to JDK cipher availability and error wording. Hostname-verifier assertions depend on `toString` values. Some tests assert wrong-mode exceptions by wrapping helper calls, so a failure before the intended API call could still satisfy the exception expectation.

## Test Signals
Signals include null/missing config behavior, successful fallback/classpath precedence, `IllegalStateException` for wrong mode APIs, handshake failure with no common ciphers, expected hostname verifier names, successful URL configurator mutation, successful initialization across password variants and credential-provider aliases, and initialization without client certs or truststore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/TestSSLFactory.java -->

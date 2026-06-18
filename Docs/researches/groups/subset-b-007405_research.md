# Research: subset-b-007405

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/http/TestRestCsrfPreventionFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/http/TestRestCsrfPreventionFilter.java

## Purpose
Tests `RestCsrfPreventionFilter` decisions for browser-like requests, non-browser user agents, required CSRF headers, custom header names, and ignored HTTP methods. It is a focused servlet-filter unit test using Mockito mocks rather than a servlet container.

## Important APIs, Types, And Functions
The class exercises `RestCsrfPreventionFilter.init()` and `doFilter()` with mocked `FilterConfig`, `HttpServletRequest`, `HttpServletResponse`, and `FilterChain`. Constants under test include `CUSTOM_HEADER_PARAM`, `CUSTOM_METHODS_TO_IGNORE_PARAM`, `BROWSER_USER_AGENT_PARAM`, `HEADER_DEFAULT`, and `HEADER_USER_AGENT`.

## Control Flow
Each test builds filter init parameters, stubs request headers and methods, initializes a new filter, then calls `doFilter`. Good requests must invoke `FilterChain.doFilter`; blocked requests must avoid the chain and, in several cases, send HTTP 400 with the expected CSRF protection message.

## State And Persistence
State is limited to filter configuration derived during `init`: selected CSRF header name, browser user-agent patterns, and ignored method set. No files or durable state are touched.

## Dependencies And Integration Points
Depends on servlet APIs, JUnit 5, Mockito, Hadoop's `MockitoUtil.verifyZeroInteractions`, and the production `RestCsrfPreventionFilter`. It integrates with Hadoop REST HTTP security behavior by validating filter-level request gating.

## Risks
The tests verify interactions but not full response bodies or servlet-container ordering. Custom user-agent matching and comma-separated method parsing are sensitive to regex and trimming behavior. Some blocked-method tests only assert chain inactivity, so response status regressions could be missed there.

## Test Signals
Signals are `sendError(SC_BAD_REQUEST, EXPECTED_MESSAGE)` for browser requests missing the required header, `doFilter` for non-browser or ignored methods, and zero chain interactions for blocked paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/http/TestRestCsrfPreventionFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/http/TestXFrameOptionsFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/http/TestXFrameOptionsFilter.java

## Purpose
Tests `XFrameOptionsFilter` default and configured `X-Frame-Options` behavior, including whether downstream filters see the header and whether downstream code can override it.

## Important APIs, Types, And Functions
The tests instantiate `XFrameOptionsFilter`, configure `XFrameOptionsFilter.CUSTOM_HEADER_PARAM`, and observe `HttpServletResponse.setHeader`, `containsHeader`, and the wrapper type `XFrameOptionsFilter.XFrameOptionsResponseWrapper`.

## Control Flow
`testDefaultOptionsValue` initializes with no custom value, expects `DENY`, and asserts the header is visible inside the filter chain. `testCustomOptionsValueAndNoOverrides` initializes with `SAMEORIGIN`, has the chain try to set `X-Frame-Options` to another value, and verifies only the configured value reaches the underlying response.

## State And Persistence
Only per-filter configuration and the response wrapper's header state are involved. The test accumulates observed header values in an in-memory collection.

## Dependencies And Integration Points
Uses servlet mocks, Mockito `Answer`, AssertJ, and JUnit assertions. It validates the security response-header contract used by Hadoop HTTP endpoints.

## Risks
The tests cover `setHeader` but not all possible header mutation APIs such as `addHeader` unless the production wrapper maps them internally. They also do not exercise multiple filter invocations on the same response object.

## Test Signals
Successful signals are one observed `X-Frame-Options` value, value `DENY` by default, value `SAMEORIGIN` under custom config, wrapper visibility inside the chain, and no downstream override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/http/TestXFrameOptionsFilter.java -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/TestDelegatingSSLSocketFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/TestDelegatingSSLSocketFactory.java

## Purpose
Tests that `DelegatingSSLSocketFactory` can initialize the OpenSSL-backed default factory when the native Hadoop build and platform support it.

## Important APIs, Types, And Functions
The test uses `NativeCodeLoader.isNativeCodeLoaded`, `NativeCodeLoader.buildSupportsOpenssl`, `DelegatingSSLSocketFactory.initializeDefaultFactory`, `getDefaultFactory`, and `SSLChannelMode.OpenSSL`.

## Control Flow
JUnit assumptions skip the test unless native code and OpenSSL support are available. The test initializes the default factory in OpenSSL mode and expects the provider name to include `openssl`. If initialization fails with a `NoSuchAlgorithmException` cause, it is treated as an environment incompatibility and downgraded to an assumption failure.

## State And Persistence
The test mutates the static default factory inside `DelegatingSSLSocketFactory`; it does not write files.

## Dependencies And Integration Points
Depends on Hadoop native library loading, WildFly/OpenSSL provider availability, AssertJ, and JUnit assumptions. It validates the native TLS provider integration point rather than generic JSSE behavior.

## Risks
Because behavior is environment-dependent, this test can be skipped on many systems. Static factory mutation can leak across tests if the production class does not isolate or reset state.

## Test Signals
The primary signal is a default factory provider name containing `openssl`; skip signals are missing native/OpenSSL support or a known incompatible provider algorithm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/TestDelegatingSSLSocketFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/TestReloadingX509KeyManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/TestReloadingX509KeyManager.java

## Purpose
Tests `ReloadingX509KeystoreManager` load and reload behavior for missing, corrupt, updated, deleted, and corrupted keystore files.

## Important APIs, Types, And Functions
The class exercises `ReloadingX509KeystoreManager`, `FileMonitoringTimerTask`, `Timer`, `KeyStoreTestUtil.generateKeyPair`, `generateCertificate`, `createKeyStore`, `GenericTestUtils.waitFor`, and captured `FileMonitoringTimerTask.LOG` output.

## Control Flow
Initial load tests assert `IOException` for missing and corrupt keystores. Reload tests create a keystore, schedule `FileMonitoringTimerTask` against `tm::loadFrom`, wait past modification-time resolution, alter/delete/corrupt the keystore, and assert manager behavior. Failure reloads must log the process-error marker and retain the previously loaded private key.

## State And Persistence
The tests write JKS files under a temp base directory and manage a daemon timer. The manager keeps the last successfully loaded key material in memory.

## Dependencies And Integration Points
Depends on JSSE keystore loading, Hadoop's file-monitoring reload task, logging capture, generated X.509 material, and JUnit timeouts. It verifies SSL factory support code that keeps key material live while files rotate.

## Risks
Timer-based tests are timing-sensitive and rely on file modification times changing. The reload-success assertion currently waits on the old key equality, so it is a weaker signal for replacement than the analogous trust-manager accepted-issuer count test. Captured logs are stopped in selected tests, which can affect reuse if the same instance is shared unexpectedly.

## Test Signals
Signals include constructor `IOException`, private-key lookup by alias, logged reload failures for deleted/corrupt files, and preservation of the previous private key after failed reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/TestReloadingX509KeyManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/TestReloadingX509TrustManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/TestReloadingX509TrustManager.java

## Purpose
Tests `ReloadingX509TrustManager` initialization and live truststore reload behavior, including preserving the last good trust anchors when reloads fail.

## Important APIs, Types, And Functions
Uses `ReloadingX509TrustManager`, `FileMonitoringTimerTask`, `Timer`, `KeyStoreTestUtil.createTrustStore`, generated certificates, `getAcceptedIssuers`, and `GenericTestUtils.waitFor`.

## Control Flow
Missing and corrupt truststores must throw `IOException` on initial load. Successful reload starts with one certificate, rewrites the truststore with two certificates, and waits until `getAcceptedIssuers()` returns two. Failure tests delete or corrupt the truststore after a successful load, wait for the reload error log, and verify the previous issuer remains active. `testNoPassword` verifies null truststore password support.

## State And Persistence
Writes truststore files under a temp directory and schedules a daemon timer. The trust manager maintains the last valid trust-manager delegate in memory.

## Dependencies And Integration Points
Depends on Hadoop SSL reload support, JSSE trust manager semantics, generated test certificates, and log capture. It is an integration signal for file-backed truststore reloads used by `FileBasedKeyStoresFactory`.

## Risks
The tests depend on sleeps and timer scheduling, making them sensitive to slow CI. They validate accepted issuer counts and object retention but not actual TLS path validation. Reusing filenames between tests can cause interference if cleanup fails.

## Test Signals
Signals are `IOException` on bad initial files, accepted issuer count changing from one to two on successful reload, process-error log entries on failed reloads, preserved issuer after failure, and successful operation with null password.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/TestReloadingX509TrustManager.java -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestDtFetcher.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestDtFetcher.java

## Purpose
Implements a test `DtFetcher` service provider used by `TestDtUtilShell` to simulate delegation-token acquisition without contacting an external service.

## Important APIs, Types, And Functions
Implements `DtFetcher.getServiceName`, `isTokenRequired`, and `addDelegationTokens`. It reuses `TestDtUtilShell.SERVICE_GET` and `TestDtUtilShell.MOCK_TOKEN`.

## Control Flow
When the shell asks for a token matching the service, `addDelegationTokens` inserts the predefined mock token into the supplied `Credentials` and returns it. `isTokenRequired` always returns true.

## State And Persistence
No local state is stored. The only mutation is adding a token to the caller-provided `Credentials` object.

## Dependencies And Integration Points
Depends on Hadoop `Configuration`, `Credentials`, `Token`, `Text`, and the `DtFetcher` plugin contract. It integrates with shell discovery of token fetchers for `dtutil get`.

## Risks
Because it shares static test constants with `TestDtUtilShell`, changes to those constants alter fetcher behavior. It does not validate URL or renewer input, so it is only a deterministic test double.

## Test Signals
`TestDtUtilShell` observes tokens of kind `testTokenKindGet` and service `testTokenServiceGet` in output files after `get` operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestDtFetcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestDtUtilShell.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestDtUtilShell.java

## Purpose
Tests `DtUtilShell` command behavior for printing, editing, appending, removing, fetching, formatting, and importing Hadoop delegation-token files.

## Important APIs, Types, And Functions
Targets `DtUtilShell.run`, `Credentials.writeTokenStorageFile`, `Credentials.readTokenStorageStream`, `Token.encodeToUrlString`, and the test fetcher path. Helper `makeTokenFile` writes either protobuf or legacy writable credential files.

## Control Flow
Each test creates local credential files in setup, runs shell commands with argument arrays, and inspects captured output or resulting files. `print` covers all tokens, legacy files, and alias filtering. `edit`, `append`, and `remove` mutate files then print to verify results. `get` uses `TestDtFetcher`, with optional `-service`, `-alias`, and `-format` flags. `import` decodes a URL token string into a credentials file and optionally rewrites the service alias.

## State And Persistence
The test writes token-storage files under a temporary local filesystem directory and deletes the whole directory after each test. It captures shell output in a `ByteArrayOutputStream`.

## Dependencies And Integration Points
Depends on Hadoop `Credentials`, local `FileSystem`, token serialization formats, Mockito spies, and the `DtFetcher` test provider. It validates the command-line token utility's file and provider integration.

## Risks
Output checks use substring matching, so formatting regressions can slip through if key substrings remain. Static local filesystem setup happens at class load and can fail early. The test depends on provider discovery for the test `DtFetcher`.

## Test Signals
Signals are zero shell return codes, output containing or excluding expected token kind/service/alias strings, Mockito verification of writable vs protobuf read paths, and imported base64 URL strings appearing in printed credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestDtUtilShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestSecretManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestSecretManager.java

## Purpose
Tests static key-generator configuration behavior in `SecretManager`, especially default algorithm/length, configurable stronger settings, unknown algorithm handling, and immutability after manager initialization.

## Important APIs, Types, And Functions
The tests call `SecretManager.update`, `SecretManager.generateSecret`, and a minimal anonymous `SecretManager<TokenIdentifier>` implementation. Configuration keys come from `CommonConfigurationKeysPublic`.

## Control Flow
Setup creates a fresh concrete anonymous manager. `testDefaults` checks default generated key metadata. `testUpdate` changes the global algorithm and length before generation. `testUnknownAlgorithm` updates to an invalid algorithm and expects `IllegalArgumentException`. `testUpdateAfterInitialisation` verifies a manager that already generated a secret continues using its initialized settings even after global update.

## State And Persistence
The important state is static `SecretManager` configuration plus per-instance initialized key generator state. Teardown resets static configuration to defaults.

## Dependencies And Integration Points
Depends on Hadoop configuration keys and Java `SecretKey`. It validates security-token secret generation used by token managers.

## Risks
Static configuration can leak across tests if teardown is skipped. The anonymous manager stubs token password methods, so only key generation is covered, not token password retrieval semantics.

## Test Signals
Signals are expected key algorithm names, encoded key bit lengths, an exception for an unknown algorithm, and unchanged per-manager key settings after a later static update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestSecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestToken.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestToken.java

## Purpose
Tests core `Token` serialization, URL-safe encoding/decoding, argument validation, identifier decoding, and empty-token equality.

## Important APIs, Types, And Functions
Targets `Token.write`, `readFields`, `encodeToUrlString`, `decodeFromUrlString`, `decodeIdentifier`, equality, and constructors. Helpers `checkEqual`, `isEqual`, and `checkUrlSafe` validate field equivalence and URL-safe character sets.

## Control Flow
Serialization writes a token to `DataOutputBuffer` and reads it back. Encoding loops over representative strings, creates tokens using the same bytes/text values, encodes and decodes them, and checks equality plus URL-safe characters. Decode sanity intercepts null input. Identifier decoding creates a delegation token through `TestDelegationTokenSecretManager` and confirms a distinct but equal identifier object is reconstructed.

## State And Persistence
State is in-memory buffers and a started delegation-token secret manager for one test. No files are written.

## Dependencies And Integration Points
Depends on Hadoop IO buffers, `Text`, `HadoopIllegalArgumentException`, delegation token test classes, and `LambdaTestUtils.intercept`. It validates token serialization contracts consumed by credential files, HTTP delegation auth, and secret managers.

## Risks
The secret manager started in `testDecodeIdentifier` is not stopped in the visible test body, so thread cleanup depends on broader test behavior or short-lived intervals. Encoding tests use platform default charset via `String.getBytes()`.

## Test Signals
Signals are round-trip equality, URL-safe encoded strings, null decode rejection, distinct/equal decoded identifiers, and equality of default, zero-length, and null-field empty tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/TestDelegationToken.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/TestDelegationToken.java

## Purpose
Comprehensively tests abstract delegation-token identifiers, selectors, secret-manager lifecycle, renewal/cancellation authorization, master-key rolling, concurrent token creation, serialization limits, equality, empty tokens, and metrics.

## Important APIs, Types, And Functions
Defines `TestDelegationTokenIdentifier`, `TestDelegationTokenSecretManager`, `TestFailureDelegationTokenSecretManager`, and `TokenSelector`. Tests exercise `AbstractDelegationTokenSecretManager` methods including `startThreads`, `stopThreads`, `renewToken`, `cancelToken`, `retrievePassword`, `rollMasterKey`, `verifyToken`, metrics accessors, and token count APIs.

## Control Flow
The file creates real delegation tokens with short lifetimes and validates user reconstruction, store/update/remove hooks, renewal authorization, expiration, max lifetime, cancellation, key rolling, token selection by service, and null-renewer rejection. A concurrency test starts 100 daemon issuers creating 100 tokens each, then verifies every cached password against its key. Metrics tests compare mutable-rate and IO-statistic sample counts before and after successful and failing operations.

## State And Persistence
State is in-memory secret-manager key maps, token maps, sequence numbers, background remover/key-update threads, and metrics registered through Hadoop metrics. No external persistence is used beyond overridden store/remove hook flags.

## Dependencies And Integration Points
Depends on Hadoop UGI, token, secret-manager, metrics2, IOStatistics, `Daemon`, `Time`, and JUnit/AssertJ. It is the central contract test for delegation-token internals used by both filesystem and web token managers.

## Risks
Several tests use real sleeps and short expirations, so slow execution can cause flakiness. The large concurrency test is resource-heavy. Static metrics system initialization can interact with other tests. The failure manager deliberately sleeps before throwing, so failure metrics depend on timing.

## Test Signals
Signals include exact serialized fields, expected UGI authentication methods, token-map counts, access-control and invalid-token exceptions, future renew times, preserved passwords across key roll, 10,000 concurrent tokens verified, overlong identifier serialization failure, metrics sample increments, and failure counters/statistics increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/TestDelegationToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/TestZKDelegationTokenSecretManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/TestZKDelegationTokenSecretManager.java

## Purpose
Tests ZooKeeper-backed delegation-token secret-manager behavior across multiple token-manager instances, startup/restart, cancellation propagation, sequence-number batching, ACLs, namespace creation, concurrent initialization, and shutdown.

## Important APIs, Types, And Functions
Uses Curator `TestingServer`, `CuratorFramework`, `ACLProvider`, `DelegationTokenManager`, `ZKDelegationTokenSecretManager`, and `DelegationTokenIdentifier`. Helpers include `getSecretConf`, `verifyDestroy`, `verifyTokenFail`, `verifyTokenFailWithRetry`, and `verifyACL`.

## Control Flow
Setup starts an in-process ZooKeeper server for each test. Multi-node tests create two or three `DelegationTokenManager` instances sharing the same ZK path, create/verify/renew/cancel tokens across nodes, and retry invalid-token checks to allow watcher propagation. Restart tests ensure cancelled tokens are not reloaded and live tokens are loaded then removed after expiry. Namespace and multiple-init tests exercise Curator parent-container creation and races. ACL tests inject a digest-auth Curator client and verify the working path ACL.

## State And Persistence
Persistent state lives in ZooKeeper znodes under the configured working path, including token records, key records, and sequence counters. Each manager also has in-memory token/key caches and background threads that are destroyed after tests.

## Dependencies And Integration Points
Depends on Apache Curator, ZooKeeper ACL/digest auth, Hadoop web `DelegationTokenManager`, `UserGroupInformation`, token APIs, and Hadoop test wait utilities. It validates distributed token state sharing for HA services.

## Risks
Tests are integration-heavy and timing-sensitive because watcher propagation and cleanup are eventually consistent. Static `ZKDelegationTokenSecretManager.setCurator` must be reset to avoid leaking clients. Method ordering indicates possible historical interdependence or resource sensitivity.

## Test Signals
Signals include cross-node token verification/renew/cancel success, invalid-token failure after cancellation, sequence numbers jumping by configured batch size for a second node, clean destroy, digest ACL equality, cancelled-token absence after restart, expired-token ZK removal, namespace existence, expected `NodeExists` on repeated creation, and successful concurrent init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/TestZKDelegationTokenSecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestDelegationTokenAuthenticationHandlerWithMocks.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestDelegationTokenAuthenticationHandlerWithMocks.java

## Purpose
Unit-tests `DelegationTokenAuthenticationHandler` management and authentication behavior with mocked servlet requests/responses and a mocked underlying authentication handler.

## Important APIs, Types, And Functions
Defines `MockDelegationTokenAuthenticationHandler` wrapping an `AuthenticationHandler` that always challenges. Tests target `managementOperation`, `authenticate`, token-manager creation/verification, JSON response generation, `GETDELEGATIONTOKEN`, `RENEWDELEGATIONTOKEN`, and `CANCELDELEGATIONTOKEN`.

## Control Flow
Setup initializes the handler with token kind `foo`. Management-operation tests cover non-management pass-through, wrong HTTP method, unauthenticated management challenges, get-token JSON responses with optional service, missing token parameters, cancel semantics, and renew responses. Authentication tests provide valid/invalid delegation tokens via query string and header. Additional tests ensure a delegation token cannot be used to obtain or renew a token and that JSON mapper configuration can prevent closing the response writer.

## State And Persistence
State is the handler's in-memory token manager and generated tokens. Responses are mocked, with JSON captured in `StringWriter`.

## Dependencies And Integration Points
Depends on servlet APIs, Hadoop auth client/server classes, Jackson `ObjectMapper`, JAX-RS media type constants, Mockito, and UGI. It validates HTTP delegation-token protocol behavior without Jetty or Kerberos.

## Risks
Mocked servlet behavior can miss container-specific query decoding, writer lifecycle, and header casing issues. Some assertions check substrings in JSON or error text. The underlying authentication handler is intentionally minimal.

## Test Signals
Signals include expected HTTP statuses, `WWW-Authenticate` challenge headers, JSON token labels and URL strings, token kind/service values, invalidation after cancel, renewal output containing a long value, valid authentication tokens from query/header inputs, forbidden invalid-token responses, and writer-not-closed behavior under mapper config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestDelegationTokenAuthenticationHandlerWithMocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestDelegationTokenManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestDelegationTokenManager.java

## Purpose
Parameterized smoke test for web `DelegationTokenManager` create, verify, renew, cancel, and post-cancel invalidation behavior with and without the ZK-key option flag.

## Important APIs, Types, And Functions
Targets `DelegationTokenManager.init`, `createToken`, `verifyToken`, `renewToken`, `cancelToken`, and `destroy`. Config keys include update interval, max lifetime, renew interval, removal scan interval, and `ENABLE_ZK_KEY`.

## Control Flow
The parameterized test initializes manager configuration with day-long intervals, creates a manager for token kind `foo`, creates a token for the current user and renewer `foo`, verifies and renews it, cancels it, and then expects verification to fail with `IOException`.

## State And Persistence
State is the manager's token secret manager and background threads. The test does not create a ZooKeeper server, and the line using `conf.getBoolean` reads rather than sets `ENABLE_ZK_KEY`, so the intended parameter may not actually affect configuration.

## Dependencies And Integration Points
Depends on Hadoop web delegation-token manager, `UserGroupInformation`, JUnit parameterization, and token APIs. It is a quick lifecycle contract for the web token manager.

## Risks
The `ENABLE_ZK_KEY` parameter appears ineffective because it is read from the configuration instead of written into it. This limits coverage of the ZK-enabled path here, leaving that path mostly to `TestZKDelegationTokenSecretManager`.

## Test Signals
Signals are non-null token creation, successful verification, renew time greater than current wall clock, successful cancellation, and verification failure after cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestDelegationTokenManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestWebDelegationToken.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestWebDelegationToken.java

## Purpose
End-to-end Jetty tests for HTTP delegation-token authentication filters and clients, covering raw HTTP operations, `DelegationTokenAuthenticatedURL`, pseudo and Kerberos auth, external secret managers, proxy users, UGI propagation, header vs query-string token transport, and IP-based proxy host checks.

## Important APIs, Types, And Functions
Defines multiple test handlers/filters/servlets: `DummyAuthenticationHandler`, `DummyDelegationTokenAuthenticationHandler`, `AFilter`, `PingServlet`, `NoDTFilter`, `NoDTHandlerDTAFilter`, `PseudoDTAFilter`, `KDTAFilter`, `UserServlet`, `UGIServlet`, and `IpAddressBasedPseudoDTAFilter`. It uses `DelegationTokenAuthenticationFilter`, `DelegationTokenAuthenticatedURL`, `MiniKdc`, `LoginContext`, and `HttpUserGroupInformation`.

## Control Flow
Tests start an embedded Jetty server on localhost, install a filter and servlet, then perform HTTP calls. Raw-call tests verify unauthenticated/authenticated access, get/renew/cancel delegation-token operations, renewer authorization, repeated cancel behavior, and delegation-token access. Client tests use `DelegationTokenAuthenticatedURL` with either header or query transport and verify UGI token pickup. Kerberos tests start `MiniKdc`, create keytabs, login through JAAS, request tokens with optional doAs, inspect token owner/real user, renew/cancel, and verify unauthorized renewal. Proxy tests validate allowed/forbidden doAs and UGI response content.

## State And Persistence
State includes an embedded Jetty server per test, UGI global security configuration reset in setup/cleanup, optional `MiniKdc` work directories and keytabs, in-memory token secret managers, and tokens attached to the current UGI.

## Dependencies And Integration Points
Depends on Jetty, Hadoop auth filters/handlers, Jackson, MiniKdc/Kerberos utilities, servlet APIs, UGI, delegation token secret managers, and HTTP URL connections. It is the broadest integration coverage for Hadoop web delegation-token auth.

## Risks
These tests are environment- and timing-sensitive due to Jetty ports, Kerberos setup, localhost/IP proxy matching, and global UGI state. URL query construction is manual in places, so encoding edge cases are not deeply covered. Token-in-UGI behavior can leak if the current UGI is shared across tests.

## Test Signals
Signals include HTTP 200/401/403/404 responses, JSON token URL strings, expected token kind, header/query marker response headers, external secret-manager token kind, fallback behavior when a filter lacks delegation-token support, Kerberos GSS failure before login and success after login, owner/real-user fields for doAs, proxy authorization outcomes, UGI response strings, and IP-based proxy success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestWebDelegationToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/BreakableService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/BreakableService.java

## Purpose
Provides a controllably failing `AbstractService` implementation for service-lifecycle tests. It can fail during init, start, or stop and tracks how many times each lifecycle state was reached.

## Important APIs, Types, And Functions
Extends `AbstractService` and overrides `serviceInit`, `serviceStart`, and `serviceStop`. Public controls are constructors, `setFailOnInit`, `setFailOnStart`, `setFailOnStop`, `getCount`, and nested exception type `BrokenLifecycleEvent`.

## Control Flow
Each lifecycle override increments the count for the target state, optionally throws `BrokenLifecycleEvent` through `maybeFail`, and otherwise delegates to the superclass implementation. Failure happens before the superclass transition logic, matching the class comment.

## State And Persistence
State is in-memory booleans for failure injection and an integer count array indexed by `Service.STATE.ordinal()`. No external persistence exists.

## Dependencies And Integration Points
Depends on Hadoop `AbstractService`, `Service.STATE`, and `Configuration`. It is a reusable fixture for service lifecycle and listener tests.

## Risks
The count array assumes the enum ordinal range fits four entries; changes to `Service.STATE` ordering or size would break it. Failures are runtime exceptions, which may differ from checked-exception paths in production services.

## Test Signals
Downstream tests can assert state counts, expected thrown `BrokenLifecycleEvent`, and service state after failed or successful lifecycle calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/BreakableService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/BreakableStateChangeListener.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/BreakableStateChangeListener.java

## Purpose
Provides a service-state-change listener fixture that records events and can deliberately fail when a service reaches a configured state.

## Important APIs, Types, And Functions
Implements `ServiceStateChangeListener.stateChanged`. Public methods expose event count, failure count, last service, last state, failing state setter, event-state list, and `toString`.

## Control Flow
On each `stateChanged` callback, the synchronized method increments event count, records the service and state, appends the state to `stateEventList`, and throws `BreakableService.BrokenLifecycleEvent` if the state equals `failingState`.

## State And Persistence
Maintains in-memory listener state: name, counts, last service/state, configured failing state, and a list of observed states. Accessors are mostly synchronized, though `getStateEventList` returns the mutable list directly.

## Dependencies And Integration Points
Depends on Hadoop `Service` and `ServiceStateChangeListener`. It pairs naturally with `BreakableService` in lifecycle tests.

## Risks
Returning the mutable event list can let callers mutate listener internals. The list itself is not synchronized when returned, so concurrent readers could race with callbacks. Failure behavior is tied to exact state equality.

## Test Signals
Tests can observe callback counts, last state/service, failure counts, ordered state events, and thrown `BrokenLifecycleEvent` when the configured failing state is reached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/BreakableStateChangeListener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/ServiceAssert.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/ServiceAssert.java

## Purpose
Provides assertion helpers for Hadoop service lifecycle tests, covering expected service states, `BreakableService` state-count checks, and configuration-key presence.

## Important APIs, Types, And Functions
Extends JUnit `Assertions` and exposes `assertServiceStateCreated`, `assertServiceStateInited`, `assertServiceStateStarted`, `assertServiceStateStopped`, `assertServiceInState`, `assertStateCount`, and `assertServiceConfigurationContains`.

## Control Flow
State helpers delegate to `assertServiceInState`, which compares `service.getServiceState()` to the expected enum and includes the service name in failures. `assertStateCount` compares a `BreakableService` count for a given state. Configuration assertion checks that `service.getConfig().get(key)` is non-null.

## State And Persistence
No state is stored; this is a static assertion utility.

## Dependencies And Integration Points
Depends on Hadoop `Service`, `BreakableService`, and JUnit assertions. It supports the service package's test suite by centralizing common lifecycle assertions.

## Risks
Assertions only check high-level state and configuration presence, not deeper lifecycle side effects. Extending `Assertions` is convenient but not necessary and can make static imports ambiguous.

## Test Signals
Failure messages identify the service name, expected/actual state, count mismatches, and missing configuration keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/ServiceAssert.java -->

# Research Report: subset-b-007414

This grouped report covers the Hadoop KMS, MiniKDC, and NFS source files assigned to subset-b-007414. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMS.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMS.java

## Purpose
`TestKMS.java` is the main integration-style test suite for Hadoop KMS. It validates that the MiniKMS server, KMS client provider, key provider operations, Kerberos/simple authentication, SSL, ACL enforcement, delegation tokens, ZooKeeper-backed shared state, proxy users, JMX, and filter initialization all behave correctly together.

## Important APIs, Types, and Functions
- `TestKMS` is a JUnit 5 class with a 180 second timeout. It owns MiniKdc lifecycle, MiniKMS lifecycle helpers, client provider creation, SSL factory setup, and cleanup.
- `KMSCallable<T>` wraps test logic that runs after one or more MiniKMS instances start. It stores KMS URLs and can produce a load-balancing `kms://http@host,...` provider URI.
- `runServer(...)` starts one or more `MiniKMS` instances, injects their URLs into the callable, executes the callable, and stops all instances in `finally`.
- `createBaseKMSConf(...)`, `writeConf(...)`, `createKMSUri(...)`, and `createKMSHAUri(...)` build test KMS configuration and client URIs.
- The nested `KerberosConfiguration` builds JAAS login entries for keytab-backed Kerberos logins.
- `setUpMiniKdc(...)`, `doAs(...)`, and `tearDown()` manage a real MiniKdc, keytab principals, UGI state, and all created `KeyProvider` instances.

## Control Flow and Behavior
The suite starts by creating a fresh MiniKdc and resetting UGI in `setUp()`. Individual tests create temporary KMS configuration directories, write `kms-site.xml`, `kms-acls.xml`, and an empty `core-site.xml`, start MiniKMS, and use `KMSClientProvider` or `LoadBalancingKMSClientProvider` to exercise server endpoints.

The core `testKMSProvider()` path creates keys, reads versions and metadata, rolls versions, generates/decrypts encrypted keys, re-encrypts individual and batch encrypted keys, deletes keys, validates post-delete failures, verifies default `key.acl.name` metadata behavior, and checks that `invalidateCache()` drains encrypted-key queues after rollover.

Authentication and authorization flows are split across several tests:
- `testStartStop*` covers HTTP/HTTPS and pseudo/Kerberos startup, JMX access, empty key lists, and delegation token acquisition.
- `testKeyACLs()` and `testACLs()` assert separation between global KMS ACLs and per-key ACLs, including management/read/generate/decrypt/whitelist/default ACL behavior.
- `testKMSBlackList()` checks blacklist denial behavior.
- `testServicePrincipalACLs()` verifies that service principals can be scoped correctly.
- `testKMSRestart*()` checks that a client can keep using a provider across a server restart on the same port.
- `testKMSAuthFailureRetry()` validates authentication-token expiry retry behavior and `KMSClientProvider.AUTH_RETRY`.
- `testDelegationTokenAccess()`, `testGetDelegationTokenByProxyUser()`, `testDelegationTokensOps*()`, and `testDelegationTokensUpdatedInUGI()` exercise token retrieval, renewal, cancellation, service binding, and UGI credential mutation.
- `testKMSWithZK*()` and `testKMSHAZooKeeperDelegationToken()` run multiple KMS instances against Curator `TestingServer` to validate ZooKeeper signer secrets, ZooKeeper delegation token secret manager state, and HA token compatibility.
- `testProxyUser*()`, `testWebHDFSProxyUser*()`, and `testTGTRenewal()` verify proxy user impersonation and Kerberos relogin/TGT renewal paths.

## State and Persistence
State lives in temporary directories under `target/<uuid>`, JCEKS keystores, generated XML config files, keytabs, in-memory UGI singleton state, client-side encrypted-key queues, delegation token credentials, and optional ZooKeeper znodes. The tests explicitly reset UGI, stop MiniKdc, stop MiniKMS, destroy SSL factories, and close providers to avoid cross-test leakage.

## Dependencies and Integration Points
This test integrates `MiniKMS`, `MiniKdc`, `KMSClientProvider`, `LoadBalancingKMSClientProvider`, `KeyProviderCryptoExtension`, `KeyProviderDelegationTokenExtension`, `KMSACLs`, `KeyAuthorizationKeyProvider`, `ValueQueue`, Hadoop `UserGroupInformation`, `Credentials`, `Token`, Curator `TestingServer`, SSL test utilities, HTTP/JMX endpoints, and ZooKeeper-backed Hadoop authentication/delegation token components.

## Risks and Edge Cases
The suite is sensitive to global UGI and JAAS state, wall-clock sleeps for token/signature expiry, ephemeral ports, ZooKeeper lifecycle, and Kerberos ticket timing. Reflection into client internals in `testKMSProviderCaching()` is brittle but gives direct cache invalidation coverage. The large number of real server starts makes timeout and cleanup correctness important.

## Test Signals
This file itself is the main signal for KMS server/client integration. It covers positive and negative authorization cases, token lifecycle, restart behavior, HA/ZK interoperability, proxy-user security, JMX availability, SSL setup, and regression checks for special key names and filter initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSACLs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSACLs.java

## Purpose
`TestKMSACLs.java` unit-tests `KMSACLs`, especially default access behavior, configured global ACLs, key ACL parsing, duplicate handling, and hot reload semantics.

## Important APIs, Types, and Functions
- `testDefaults()` verifies that an empty `Configuration(false)` allows every `KMSACLs.Type`.
- `testCustom()` sets each ACL config key to its type name and confirms only the matching user is authorized.
- `testKeyAclConfigurationLoad()` validates key ACL, default key ACL, and whitelist key ACL parsing, including rejection of invalid operations and disallowing `ALL` for default/whitelist key ACL prefixes.
- `testKeyAclDuplicateEntries()` verifies last-write-wins behavior in `Configuration`, wildcard handling, and empty ACL replacement.
- `testKeyAclReload()` calls `setKeyACLs()` repeatedly to ensure hot reload updates, idempotence, wildcard conversion, and clearing old maps when a new configuration omits previous entries.
- Helper methods inspect `KMSACLs.keyAcls`, `defaultKeyAcls`, and `whitelistKeyAcls` maps and compare `AccessControlList` users.

## Control Flow and State
Each test builds an isolated `Configuration`, constructs a `KMSACLs`, and inspects either `hasAccess()` results or the internal ACL maps. Reload tests mutate the same `Configuration`, call `setKeyACLs()`, and assert that old entries are either retained only when still configured or removed on a fresh config.

## Dependencies and Integration Points
The test uses `KMSConfiguration` ACL prefixes, `KeyAuthorizationKeyProvider.KEY_ACL`, `KeyOpType`, Hadoop `AccessControlList`, and `UserGroupInformation`. It validates the config contract consumed by KMS server authorization and `KeyAuthorizationKeyProvider`.

## Risks and Edge Cases
Important security edge cases include invalid operation names, duplicate configuration keys, empty values, wildcard `*`, `ALL` scope restrictions, and reload clearing. Because it directly inspects package-visible maps, changes to `KMSACLs` internals may require test updates even if behavior remains intact.

## Test Signals
The file gives focused unit coverage for ACL parsing and reload behavior, complementing the broader end-to-end authorization tests in `TestKMS.java`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSACLs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSAudit.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSAudit.java

## Purpose
`TestKMSAudit.java` verifies KMS audit logging behavior: aggregation, unauthenticated/unauthorized/error formats, and configured audit logger initialization.

## Important APIs, Types, and Functions
- `setUp()` captures `System.err`, loads `log4j-kmsaudit.properties`, and creates `KMSAudit`.
- `cleanUp()` restores `System.err`, resets Log4j, and shuts down `KMSAudit`.
- `FilterOut` lets the test swap the backing `ByteArrayOutputStream` after each assertion.
- `testAggregation()` checks that selected crypto operations aggregate repeated OK records while management operations remain unaggregated.
- `testAggregationUnauth()` verifies that unauthorized events evict or flush aggregation state, accepting either ordering for asynchronous invalidation.
- `testAuditLogFormat()` validates OK, UNAUTHORIZED, ERROR, and UNAUTHENTICATED log formats.
- `testInitAuditLoggers()` uses reflection to inspect `KMSAudit.auditLoggers`, verifies default `SimpleKMSAuditLogger`, duplicate suppression, and failure when a configured logger class cannot load.

## Control Flow and State
Tests drive `kmsAudit.ok()`, `unauthorized()`, `error()`, `unauthenticated()`, and `evictCacheForTesting()`, then compare captured output against regexes. Aggregation state lives inside `KMSAudit` caches until evicted or invalidated by an unauthorized event.

## Dependencies and Integration Points
The file integrates `KMSAudit`, `KMS.KMSOp`, `KMSAuditLogger`, `SimpleKMSAuditLogger`, Log4j configuration, Hadoop `UserGroupInformation`, and Apache Commons `FieldUtils`. It protects the audit contract expected by operators and downstream log processing.

## Risks and Edge Cases
The tests are regex-heavy and timing-sensitive around asynchronous cache invalidation. They strip a known deprecated config warning from output to reduce noise. Any format change in audit logs is intentionally visible as a test failure.

## Test Signals
The test suite gives direct evidence that audit aggregation preserves counts and intervals for crypto operations, unauthenticated and error events remain structured, and invalid logger configuration fails early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSAudit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSAuthenticationFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSAuthenticationFilter.java

## Purpose
`TestKMSAuthenticationFilter.java` verifies that KMS authentication filter configuration rewrites simple authentication into the delegation-token-aware pseudo handler and sets the KMS delegation token kind.

## Important APIs, Types, and Functions
- `testConfiguration()` sets `hadoop.kms.authentication.type=simple`, calls `new KMSAuthenticationFilter().getKMSConfiguration(conf)`, and inspects returned `Properties`.
- It asserts `KMSAuthenticationFilter.AUTH_TYPE` equals `PseudoDelegationTokenAuthenticationHandler`.
- It asserts `DelegationTokenAuthenticationHandler.TOKEN_KIND` equals `KMSDelegationToken.TOKEN_KIND_STR`.

## Control Flow and State
The test is stateless beyond a local `Configuration` and returned `Properties`. It validates property translation rather than servlet filter execution.

## Dependencies and Integration Points
It links the KMS filter to Hadoop security token web authentication classes and the `KMSDelegationToken` token kind. This property contract is consumed when KMS initializes HTTP authentication.

## Risks and Edge Cases
The test only covers simple mode. Kerberos property conversion and error handling are left to broader KMS integration tests.

## Test Signals
The file gives a narrow regression signal that simple KMS auth still enables delegation token support rather than plain pseudo authentication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSAuthenticationFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSMDCFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSMDCFilter.java

## Purpose
`TestKMSMDCFilter.java` validates request-context lifecycle behavior for `KMSMDCFilter`, ensuring method, URL, remote address, and UGI context are populated during filtering and cleared afterward.

## Important APIs, Types, and Functions
- `setUp()` creates a `KMSMDCFilter`, mocked `HttpServletRequest`/`HttpServletResponse`, and clears the static context.
- `testFilter()` stubs request method, URL, and remote address, then invokes `doFilter()`.
- The inline `FilterChain` asserts that `KMSMDCFilter.getRemoteClientAddress()`, `getMethod()`, and `getURL()` are set while the downstream chain runs.
- `checkMDCValuesAreEmpty()` asserts all context getters, including `getUgi()`, return null before and after filtering.

## Control Flow and State
The filter sets thread-local or static MDC context before invoking the chain and clears it in cleanup logic after the chain returns. The test verifies both sides of that lifecycle.

## Dependencies and Integration Points
The test uses Mockito, servlet `FilterChain`, and KMS MDC accessors. The context is used by KMS request logging, auditing, and diagnostics.

## Risks and Edge Cases
The test does not throw from the chain, so exception-path cleanup should be covered elsewhere or by inspecting filter implementation. Static context reset in setup is important to avoid cross-test contamination.

## Test Signals
This is a focused signal that KMS per-request diagnostic context does not leak across requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSMDCFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSWithZK.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSWithZK.java

## Purpose
`TestKMSWithZK.java` verifies that multiple MiniKMS instances can share ZooKeeper-backed signer secrets so an authentication token issued through one instance is accepted by another.

## Important APIs, Types, and Functions
- `createBaseKMSConf(File)` builds a JCEKS-backed simple-auth KMS configuration with key authorization disabled and `GET_KEYS` limited to user `foo`.
- `testMultipleKMSInstancesWithZKSigner()` starts a Curator `TestingServer`, configures `AuthenticationFilter.SIGNER_SECRET_PROVIDER=zookeeper`, sets ZooKeeper connection string and path, starts two `MiniKMS` instances, and performs HTTP requests through `DelegationTokenAuthenticatedURL`.

## Control Flow and State
The test writes shared KMS config, starts KMS instance 1 and KMS instance 2, obtains an authenticated token as `foo` through the first URL, reuses the same token as `bar` against the second URL, and verifies an empty token as `bar` receives HTTP 403. KMS and ZooKeeper are stopped in `finally`.

## Dependencies and Integration Points
It integrates `MiniKMS`, `KMSAuthenticationFilter`, Hadoop authentication `ZKSignerSecretProvider`, Curator `TestingServer`, `DelegationTokenAuthenticatedURL`, and KMS REST key-name resource paths.

## Risks and Edge Cases
The test relies on shared ZooKeeper state and HTTP authentication cookies/tokens. It intentionally demonstrates that signer-secret sharing is authentication-level state, independent of the current UGI used for the second request.

## Test Signals
This is a targeted HA signal for ZooKeeper signer configuration, complementing the more extensive ZooKeeper delegation token tests in `TestKMS.java`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSWithZK.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKeyAuthorizationKeyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKeyAuthorizationKeyProvider.java

## Purpose
`TestKeyAuthorizationKeyProvider.java` unit-tests `KeyAuthorizationKeyProvider`, the wrapper that enforces per-key ACLs around a `KeyProviderCryptoExtension`.

## Important APIs, Types, and Functions
- `testCreateKey()` verifies that creating a key requires a configured and authorized `MANAGEMENT` ACL, and denies both missing ACLs and unauthorized users.
- `testOpsWhenACLAttributeExists()` uses a mock `KeyACLs` to grant separate users `MANAGEMENT`, `GENERATE_EEK`, `DECRYPT_EEK`, and `ALL`, then verifies operation-specific permissions.
- `testDecryptWithKeyVersionNameKeyMismatch()` expects `IllegalArgumentException` when an encrypted key is mutated so its encryption key name no longer matches the version information used for decryption.
- `newOptions()` creates AES 128-bit provider options.

## Control Flow and State
The tests use an in-memory `UserProvider`, wrap it in `KeyProviderCryptoExtension`, then wrap that with `KeyAuthorizationKeyProvider`. They run operations under different `UserGroupInformation.doAs()` identities and use Mockito to answer ACL presence and access checks.

## Dependencies and Integration Points
The file integrates `KeyProvider`, `UserProvider`, `KeyProviderCryptoExtension`, `EncryptedKeyVersion`, `KeyAuthorizationKeyProvider.KeyACLs`, `KeyOpType`, `UserGroupInformation`, and Mockito. It protects the lower-level authorization layer used by KMS request handling.

## Risks and Edge Cases
The important risk is incorrectly mapping operations to `KeyOpType`, especially `ALL` bypass behavior and crypto extension methods. The mismatch test protects against decrypting encrypted-key material under a forged key identity.

## Test Signals
The file provides precise unit signals for create, roll, delete, generate encrypted key, decrypt encrypted key, and all-access authorization behavior independent of HTTP/KMS server plumbing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKeyAuthorizationKeyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/resources/mini-kms-acls-default.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/resources/mini-kms-acls-default.xml

## Purpose
`mini-kms-acls-default.xml` is a test resource containing permissive default ACLs for MiniKMS test deployments.

## Important Configuration Entries
- Global KMS ACLs allow `*` for `CREATE`, `DELETE`, `ROLLOVER`, `GET`, `GET_KEYS`, `GET_METADATA`, `SET_KEY_MATERIAL`, `GENERATE_EEK`, and `DECRYPT_EEK`.
- Default per-key ACLs allow `*` for `MANAGEMENT`, `GENERATE_EEK`, `DECRYPT_EEK`, and `READ`.
- The file notes that it is hot-reloaded when changed.

## Control Flow and State
This XML is not executable. KMS loads it as `kms-acls.xml` style configuration and interprets property names via `KMSACLs` and `KeyAuthorizationKeyProvider`.

## Dependencies and Integration Points
It is consumed by MiniKMS/KMS test configuration. The property names must align with `KMSConfiguration`, `KMSACLs.Type`, and default key ACL prefixes.

## Risks and Edge Cases
Because all values are wildcard-permissive, this resource is appropriate for tests that need broad access but should not be mistaken for a secure production ACL sample. Hot reload semantics mean test failures can arise if property names drift.

## Test Signals
The file supports integration tests that require permissive defaults while focused tests override ACLs explicitly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/resources/mini-kms-acls-default.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/dev-support/findbugsExcludeFile.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/dev-support/findbugsExcludeFile.xml

## Purpose
This SpotBugs/FindBugs exclude file suppresses one warning for the MiniKDC module.

## Important Entries
- It matches class `org.apache.hadoop.minikdc.MiniKdc`, method `stop`, bug pattern `SWL_SLEEP_WITH_LOCK_HELD`.

## Control Flow and State
The XML is consumed by the module POM's SpotBugs plugin configuration. It has no runtime behavior.

## Dependencies and Integration Points
The path is referenced by `hadoop-minikdc/pom.xml` under `spotbugs-maven-plugin` exclude filter files, along with the global Hadoop exclude file.

## Risks and Edge Cases
The suppressed warning corresponds to `MiniKdc.stop()` sleeping while synchronized. That sleep is intentional in current code due to a Kerby cleanup delay, but it remains a concurrency smell if stop latency or lock contention becomes important.

## Test Signals
Build-time static analysis should ignore this known MiniKdc stop-method warning while still reporting other issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/pom.xml

## Purpose
The MiniKDC POM defines the `hadoop-minikdc` jar module and its dependencies/build configuration.

## Important APIs, Types, and Functions
This is Maven metadata, not Java code. It declares parent `hadoop-project` version `3.6.0-SNAPSHOT`, artifact `hadoop-minikdc`, packaging `jar`, name/description, dependencies, and SpotBugs exclusions.

## Dependencies and Integration Points
Compile/runtime dependencies include `commons-io`, Apache Kerby `kerb-simplekdc`, and `slf4j-reload4j`. Test/provided dependencies include AssertJ and JUnit Jupiter API, params, engine, and platform launcher. The SpotBugs plugin references the module-local `dev-support/findbugsExcludeFile.xml` and the global Hadoop exclude file.

## Control Flow and State
The POM participates in Maven build resolution and static analysis. It does not persist runtime state.

## Risks and Edge Cases
The module depends on Apache Kerby for actual KDC behavior, so API changes there can affect `MiniKdc`. JUnit dependencies are `provided`, reflecting Hadoop's parent/module build conventions; changing scopes can affect downstream test classpath behavior.

## Test Signals
Successful module compilation and tests validate that MiniKdc source and tests have the expected Kerby and JUnit APIs available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/src/main/java/org/apache/hadoop/minikdc/KerberosSecurityTestcase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/src/main/java/org/apache/hadoop/minikdc/KerberosSecurityTestcase.java

## Purpose
`KerberosSecurityTestcase` is a JUnit base class that starts a `MiniKdc` before each test and stops it afterward, giving Kerberos-enabled tests a default embedded KDC.

## Important APIs, Types, and Functions
- Fields store `MiniKdc kdc`, `File workDir`, and `Properties conf`.
- `startMiniKdc()` is annotated `@BeforeEach`; it calls overridable `createTestDir()` and `createMiniKdcConf()`, constructs `MiniKdc`, and starts it.
- `createTestDir()` defaults the work directory to `System.getProperty("test.dir", "target")`.
- `createMiniKdcConf()` defaults to `MiniKdc.createConf()`.
- `stopMiniKdc()` is annotated `@AfterEach` and stops the KDC if present.
- Getters expose KDC, work directory, and properties to subclasses.

## Control Flow and State
Subclasses can override the setup hooks before `MiniKdc` construction. Runtime state includes a generated MiniKdc work subdirectory and system Kerberos properties modified by `MiniKdc`.

## Dependencies and Integration Points
It integrates JUnit 5 lifecycle annotations with `MiniKdc`. `TestMiniKdc` and `TestChangeOrgNameAndDomain` use it directly.

## Risks and Edge Cases
Because `MiniKdc` mutates JVM-wide Kerberos properties, tests inheriting this class should not run multiple KDC instances in parallel in the same JVM. Cleanup relies on `MiniKdc.stop()`.

## Test Signals
Subclasses validate that the base lifecycle successfully starts a KDC, creates keytabs, and supports JAAS login.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/src/main/java/org/apache/hadoop/minikdc/KerberosSecurityTestcase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/src/main/java/org/apache/hadoop/minikdc/MiniKdc.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/src/main/java/org/apache/hadoop/minikdc/MiniKdc.java

## Purpose
`MiniKdc.java` implements an embeddable and command-line Mini KDC backed by Apache Kerby `SimpleKdcServer`. It is used by Hadoop tests that need real Kerberos principals, keytabs, and `krb5.conf` behavior.

## Important APIs, Types, and Functions
- Public configuration keys include `ORG_NAME`, `ORG_DOMAIN`, `KDC_BIND_ADDRESS`, `KDC_PORT`, `INSTANCE`, `MAX_TICKET_LIFETIME`, `MIN_TICKET_LIFETIME`, `MAX_RENEWABLE_LIFETIME`, `TRANSPORT`, and `DEBUG`.
- `createConf()` returns a clone of default properties: localhost, ephemeral port, realm `EXAMPLE.COM`, TCP transport, ticket lifetime defaults, and debug false.
- Constructor validates required properties, creates a timestamped working directory under the supplied build directory, logs config, parses port, and derives upper-case realm from organization name/domain.
- `start()` constructs `SimpleKdcServer`, calls `prepareKdcServer()`, initializes, rewrites default realm in generated `krb5.conf`, and starts the server.
- `prepareKdcServer()` sets work dir, host, realm, TCP/UDP port, transport flags, KDC service name, debug system property, and ticket lifetime config.
- `stop()` stops the Kerby server, restores debug system property, recursively deletes work dir, sleeps for a Kerby cleanup delay, and logs shutdown.
- `createPrincipal(String,password)` and `createPrincipal(File,String...)` create KDC principals and export keytabs.
- `main()` supports standalone usage: work dir, properties file, keytab file, and principals.

## Control Flow and State
MiniKdc owns server state (`SimpleKdcServer`), selected port, realm, work directory, generated `krb5.conf`, transport, and saved Kerberos debug flag. It mutates JVM system properties `java.security.krb5.conf` indirectly through Kerby and `sun.security.krb5.debug` directly. Keytab files are created externally at caller-specified paths; internal work directories are deleted on stop.

## Dependencies and Integration Points
The implementation depends on Apache Kerby `SimpleKdcServer`, `KdcConfigKey`, `NetworkUtil`, `IOUtil`, SLF4J, and Java properties/filesystem APIs. It is used by KMS security tests and MiniKdc tests as an embedded Kerberos authority.

## Risks and Edge Cases
Important risks include global JVM Kerberos property mutation, no parallel KDC safety in one JVM, recursive deletion of the generated work directory, TCP/UDP transport validation, port selection races when port is 0, and the synchronized `stop()` sleep suppressed by SpotBugs. The copy constructor for required property set appears to add `KDC_BIND_ADDRESS` twice and omits `MIN_TICKET_LIFETIME` from required properties, which is intentional or legacy because minimum lifetime is optional.

## Test Signals
`TestMiniKdc` verifies startup, nonzero port selection, keytab generation, and JAAS client/server login. `TestChangeOrgNameAndDomain` verifies realm customization via overridden config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/src/main/java/org/apache/hadoop/minikdc/MiniKdc.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/src/test/java/org/apache/hadoop/minikdc/TestChangeOrgNameAndDomain.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/src/test/java/org/apache/hadoop/minikdc/TestChangeOrgNameAndDomain.java

## Purpose
`TestChangeOrgNameAndDomain.java` verifies that MiniKdc tests still pass when the generated Kerberos realm is changed from the default.

## Important APIs, Types, and Functions
- The class extends `TestMiniKdc`, inheriting all startup, keytab, and login tests.
- It overrides `createMiniKdcConf()`, calls `super`, then sets `MiniKdc.ORG_NAME=APACHE` and `MiniKdc.ORG_DOMAIN=COM`.

## Control Flow and State
The overridden config hook runs before the inherited `KerberosSecurityTestcase.startMiniKdc()` constructs the KDC. This changes the realm to `APACHE.COM` for all inherited tests.

## Dependencies and Integration Points
The file depends on `TestMiniKdc`, `MiniKdc` property keys, and `Properties`. It is a reuse-based test rather than a standalone assertion class.

## Risks and Edge Cases
Because all inherited tests run under the custom realm, failures can indicate realm generation, keytab export, or JAAS login code has hard-coded `EXAMPLE.COM`.

## Test Signals
The inherited `testMiniKdcStart`, `testKeytabGen`, and `testKerberosLogin` provide the actual behavior signal under the customized realm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/src/test/java/org/apache/hadoop/minikdc/TestChangeOrgNameAndDomain.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/src/test/java/org/apache/hadoop/minikdc/TestMiniKdc.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/src/test/java/org/apache/hadoop/minikdc/TestMiniKdc.java

## Purpose
`TestMiniKdc.java` validates the embedded MiniKdc lifecycle, keytab generation, and Kerberos login interoperability.

## Important APIs, Types, and Functions
- The class extends `KerberosSecurityTestcase`, so each test receives a running KDC.
- `shouldUseIbmPackages()` and `isSystemClassAvailable()` detect IBM Java JAAS module differences.
- `testMiniKdcStart()` asserts the KDC binds a nonzero port.
- `testKeytabGen()` creates principals `foo/bar` and `bar/foo`, loads the keytab with Kerby `Keytab`, and verifies realm-qualified principal names.
- Nested `KerberosConfiguration` builds JAAS `AppConfigurationEntry` options for client and server login, with IBM and non-IBM option sets.
- `testKerberosLogin()` creates a `foo` principal/keytab, logs in as client and server, validates the resulting `Subject` contains one `KerberosPrincipal` named `foo@REALM`, and logs out.

## Control Flow and State
MiniKdc is started by the base class. Tests create keytabs in the work directory, then use JAAS `LoginContext` to authenticate. `finally` cleanup logs out if credentials remain.

## Dependencies and Integration Points
The test integrates MiniKdc, Apache Kerby keytab parsing, Java JAAS, `Subject`, `KerberosPrincipal`, and JUnit assertions. It guards compatibility across standard Sun/Oracle/OpenJDK and IBM Java security modules.

## Risks and Edge Cases
JAAS option names differ between IBM and non-IBM runtimes. Environment variable `KRB5CCNAME` is optionally propagated as `ticketCache`, which can affect login behavior. The test assumes generated `krb5.conf` and keytabs are visible to JAAS after MiniKdc startup.

## Test Signals
It provides core smoke coverage that MiniKdc can start, issue principals, export usable keytabs, and authenticate both initiator and acceptor style logins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/src/test/java/org/apache/hadoop/minikdc/TestMiniKdc.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/dev-support/findbugsExcludeFile.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/dev-support/findbugsExcludeFile.xml

## Purpose
This SpotBugs/FindBugs exclude file suppresses a known exposure warning in the Hadoop NFS module.

## Important Entries
- It matches `org.apache.hadoop.oncrpc.security.CredentialsSys#getAuxGIDs()` returning `int[]`.
- It suppresses bug code `EI`, with a comment explaining that callers are not supposed to mutate the returned array and copying would be more expensive.

## Control Flow and State
The file is static build metadata consumed by the module's SpotBugs Maven configuration.

## Dependencies and Integration Points
It is referenced by `hadoop-nfs/pom.xml` together with Hadoop's global SpotBugs exclude file.

## Risks and Edge Cases
Suppressing mutable exposure is a deliberate performance tradeoff. If callers begin mutating the returned auxiliary group IDs, this suppressed issue could become a security or correctness problem.

## Test Signals
Static analysis should suppress only this known warning while continuing to report other NFS module issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/pom.xml

## Purpose
The Hadoop NFS POM defines the `hadoop-nfs` jar module, its dependencies, static analysis exclusions, and distribution assembly profile.

## Important APIs, Types, and Functions
This is Maven metadata. It declares parent `hadoop-project` version `3.6.0-SNAPSHOT`, artifact `hadoop-nfs`, packaging `jar`, module name/description, build timestamp format, and default Kerberos realm property `LOCALHOST`.

## Dependencies and Integration Points
Provided dependencies include Hadoop annotations, `hadoop-common`, Jakarta Servlet API, and JUnit platform launcher. Test dependencies include Hadoop common test jar, Mockito inline, AssertJ, and JUnit Jupiter. Runtime logging uses reload4j and `slf4j-reload4j`; compile logging uses `slf4j-api`; shaded Guava is a regular dependency. The SpotBugs plugin references module-local and global exclude files.

The `dist` profile runs Maven assembly using `hadoop-nfs-dist.xml` from `hadoop-assemblies`, producing a distribution artifact without attaching it.

## Control Flow and State
The POM influences compilation, testing, static analysis, and optional distribution packaging. It has no direct runtime state.

## Risks and Edge Cases
Dependency scopes are important because NFS code integrates Hadoop common RPC/configuration classes and servlet APIs. The commented descriptorRef shows the assembly is path-based rather than descriptor-ref-based; moving assembly resources would break the profile.

## Test Signals
Build success validates dependency availability for NFS protocol, mount daemon, ONCRPC, and tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/mount/MountEntry.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/mount/MountEntry.java

## Purpose
`MountEntry.java` is a small immutable value object representing one NFS mount table entry: client host plus mounted path.

## Important APIs, Types, and Functions
- Constructor `MountEntry(String host, String path)` stores final fields.
- `getHost()` and `getPath()` expose values.
- `equals()` returns true for another `MountEntry` with equal host and path.
- `hashCode()` combines host and path hashes.

## Control Flow and State
There is no mutable state after construction. The object is suitable for lists, sets, and mount response serialization.

## Dependencies and Integration Points
`MountResponse.writeMountList()` consumes `List<MountEntry>` to serialize mountd DUMP responses.

## Risks and Edge Cases
The constructor does not null-check host or path, so `equals()` and `hashCode()` can throw if null values are supplied.

## Test Signals
No direct test is in this subset, but mount response serialization depends on predictable equality and getters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/mount/MountEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/mount/MountInterface.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/mount/MountInterface.java

## Purpose
`MountInterface.java` defines the server-side Java contract for NFS mount protocol procedures described by RFC 1094.

## Important APIs, Types, and Functions
- `MNTPROC` enum maps mount procedure names to ordinal wire values: `NULL`, `MNT`, `DUMP`, `UMNT`, `UMNTALL`, `EXPORT`, `EXPORTALL`, and `PATHCONF`.
- `MNTPROC.getValue()` returns the ordinal.
- `MNTPROC.fromValue(int)` safely maps valid ordinals and returns null for invalid values.
- Interface methods define handlers for `nullOp`, `mnt`, `dump`, `umnt`, and `umntall`, using `XDR`, transaction id, and client `InetAddress`.
- `EXPORT`/`EXPORTALL` and `PATHCONF` handler declarations are present only as commented placeholders.

## Control Flow and State
Implementations decode request XDR where needed, write response XDR, and use client address for authorization or mount tracking. This interface itself holds no state.

## Dependencies and Integration Points
It integrates Hadoop ONCRPC `XDR` with mount daemon implementations. `MountResponse` provides helper serializers for responses to procedures defined here.

## Risks and Edge Cases
Enum ordinal order is wire-protocol significant, so reordering values would break compatibility. Invalid procedure values intentionally map to null and must be handled by dispatchers.

## Test Signals
No direct test in this subset, but protocol dispatch and response helpers rely on this enum contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/mount/MountInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/mount/MountResponse.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/mount/MountResponse.java

## Purpose
`MountResponse.java` serializes XDR responses for NFS mount protocol operations.

## Important APIs, Types, and Functions
- `MNT_OK` is the success status code.
- `writeMNTResponse(int status, XDR xdr, int xid, byte[] handle)` writes an accepted RPC reply, status, and on success the file handle plus supported auth flavor list containing `AUTH_SYS`.
- `writeMountList(XDR xdr, int xid, List<MountEntry> mounts)` writes accepted reply and a linked-list style sequence of mount entries followed by a false terminator.
- `writeExportList(XDR xdr, int xid, List<String> exports, List<NfsExports> hostMatcher)` writes export paths and their allowed host groups, with nested boolean list terminators.

## Control Flow and State
All methods are static and append to the provided `XDR`. RPC accepted headers are written first using `RpcAcceptedReply` and `VerifierNone`. Response lists use ONCRPC boolean "value follows" encoding.

## Dependencies and Integration Points
It integrates mount protocol code with ONCRPC reply types, `AuthFlavor.AUTH_SYS`, `MountEntry`, and `NfsExports.getHostGroupList()`. Mount daemon implementations call these helpers when serving MNT, DUMP, and EXPORT.

## Risks and Edge Cases
`writeExportList()` uses an `assert` for matching list sizes, which is disabled unless assertions are enabled; mismatched lists can still cause runtime index errors. Host groups are encoded as UTF-8 variable opaque values.

## Test Signals
No direct tests in this subset. Protocol correctness depends on byte-accurate XDR serialization and list termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/mount/MountResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/mount/MountdBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/mount/MountdBase.java

## Purpose
`MountdBase.java` is the abstract base for starting and stopping the Hadoop mountd daemon that serves the NFS mount protocol over UDP and TCP.

## Important APIs, Types, and Functions
- Constructor stores the `RpcProgram` that handles mount requests.
- `getRpcProgram()` exposes the program.
- `start(boolean register)` starts UDP and TCP servers, optionally registers both transports with portmap, and installs a shutdown hook.
- `stop()` unregisters bound UDP/TCP ports and shuts down both servers.
- Private `startUDPServer()` and `startTCPServer()` construct `SimpleUdpServer`/`SimpleTcpServer`, start program daemons, run servers, capture bound ports, and terminate the process on startup failure.
- `Unregister` shutdown hook calls `stop()` with priority `10`.

## Control Flow and State
State includes `rpcProgram`, bound UDP/TCP ports, and server instances. Startup begins UDP, then TCP, then registers with portmap if requested. Failure during server startup unregisters any partially registered transport, shuts down the server, and calls `ExitUtil.terminate(1, e)`.

## Dependencies and Integration Points
It depends on Hadoop ONCRPC `RpcProgram`, `SimpleUdpServer`, `SimpleTcpServer`, portmap `PortmapMapping`, `ShutdownHookManager`, SLF4J, and `ExitUtil`. Concrete mount daemons subclass this base with an implementation-specific `RpcProgram`.

## Risks and Edge Cases
`rpcProgram.startDaemons()` is called once for UDP and once for TCP startup; implementations must tolerate that. Startup failure is fatal. `stop()` unregisters regardless of whether `start(register)` was called with registration enabled, but only if bound ports are positive.

## Test Signals
No direct test in this subset. Integration tests should verify port registration/unregistration, dual transport startup, and shutdown hook behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/mount/MountdBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/AccessPrivilege.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/AccessPrivilege.java

## Purpose
`AccessPrivilege.java` defines the access outcomes for NFS export host matching.

## Important APIs, Types, and Functions
- Enum constants: `READ_ONLY`, `READ_WRITE`, and `NONE`.

## Control Flow and State
There is no behavior or mutable state. `NfsExports` assigns these values based on configured host matchers.

## Dependencies and Integration Points
The enum is used by `NfsExports` and downstream NFS server authorization checks to distinguish read-only, read-write, and denied clients.

## Risks and Edge Cases
Semantics depend on callers respecting `READ_ONLY` as a stronger denial of writes than `READ_WRITE`; the enum does not encode ordering itself.

## Test Signals
Behavior is covered indirectly through NFS export access tests outside this subset and through `NfsExports` logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/AccessPrivilege.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/NfsExports.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/NfsExports.java

## Purpose
`NfsExports.java` loads configured NFS export host rules and checks whether a client address/hostname has read-only, read-write, or no access.

## Important APIs, Types, and Functions
- Static singleton `getInstance(Configuration)` reads `nfs.exports.allowed.hosts`, cache size, and cache expiry config and creates one `NfsExports`.
- Constructor splits the host rule string on Hadoop's NFS exports separator and converts each non-empty token into a `Match`.
- `getHostGroupList()` returns configured host matcher strings for mount export responses.
- `getAccessPrivilege(InetAddress)` and package-private `getAccessPrivilege(String address, String hostname)` evaluate and cache access.
- `AccessCacheEntry` implements `LightWeightCache.Entry` keyed by host address with an expiration timestamp.
- `Match` subclasses implement matcher types:
  - `AnonymousMatch` for `*`.
  - `CIDRMatch` for short `ip/prefix` or long `ip/netmask` IPv4 CIDR.
  - `ExactMatch` for exact IP or hostname.
  - `RegexMatch` for wildcard/regex-like host strings containing metacharacters.
- `getMatch(String line)` parses `host [rw]`, defaulting to read-only when no access option is provided.

## Control Flow and State
Access evaluation first checks the cache by IP address. If absent or expired, it scans matchers in configured order. `READ_ONLY` immediately wins and breaks; `READ_WRITE` is recorded but later read-only matches can override. If no matcher includes the client, access remains `NONE`. The result is cached until expiration.

## Dependencies and Integration Points
The class uses Hadoop `Configuration`, `CommonConfigurationKeys`, NFS constants for cache keys, Commons Net `SubnetUtils`, Hadoop `LightWeightCache`, `LightWeightGSet`, `StringUtils`, `Preconditions`, and SLF4J. `MountResponse.writeExportList()` uses `getHostGroupList()`.

## Risks and Edge Cases
The singleton ignores subsequent configuration changes after first initialization. Only IPv4 CIDR patterns are supported. Regex patterns are compiled directly from the host string rather than shell-glob translated, so configured `*` and `?` inside hostnames have Java regex meaning. Invalid host strings throw `IllegalArgumentException`; `getInstance()` logs and returns the existing singleton, which may be null. Cache keys by address ignore hostname changes until expiry.

## Test Signals
Expected tests should cover anonymous, exact, CIDR short/long, regex, invalid hostnames, `rw` option, read-only precedence, and cache expiry. This subset does not include those tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/NfsExports.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/NfsFileType.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/NfsFileType.java

## Purpose
`NfsFileType.java` maps NFS file type names to the numeric values used on the NFS wire.

## Important APIs, Types, and Functions
- Enum constants: `NFSREG(1)`, `NFSDIR(2)`, `NFSBLK(3)`, `NFSCHR(4)`, `NFSLNK(5)`, `NFSSOCK(6)`, and `NFSFIFO(7)`.
- `toValue()` returns the numeric protocol value.

## Control Flow and State
There is no mutable state. Values are assigned at enum construction and returned directly.

## Dependencies and Integration Points
`Nfs3FileAttributes` uses `NfsFileType` to set the serialized `type` field in attributes.

## Risks and Edge Cases
Protocol numeric values must not change. There is no reverse lookup helper in this enum.

## Test Signals
Coverage is indirect through NFS attribute serialization/deserialization and protocol response tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/NfsFileType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/NfsTime.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/NfsTime.java

## Purpose
`NfsTime.java` encapsulates NFS seconds/nanoseconds timestamps and serializes them to XDR.

## Important APIs, Types, and Functions
- Constructors accept `(seconds, nseconds)`, another `NfsTime`, or milliseconds.
- `getSeconds()`, `getNseconds()`, and `getMilliSeconds()` expose time values.
- `serialize(XDR)` writes seconds and nanoseconds as two ints.
- `deserialize(XDR)` reads the same pair.
- `equals()` compares millisecond-equivalent values; `hashCode()` XORs seconds and nanoseconds.
- `toString()` formats a debug representation.

## Control Flow and State
Instances are immutable after construction. The milliseconds constructor splits milliseconds into seconds plus nanoseconds. XDR serialization is straightforward.

## Dependencies and Integration Points
`Nfs3FileAttributes` uses `NfsTime` for access, modification, and change times. `WccAttr` integration uses times derived from attributes.

## Risks and Edge Cases
The copy constructor sets `seconds = other.getNseconds()`, which appears suspicious because it likely intended `other.getSeconds()`. Equality compares only millisecond precision, while `hashCode()` includes raw nanoseconds, so two objects equal by milliseconds but with different sub-millisecond nanoseconds can have different hashes. Seconds are stored as `int`, limiting representable range.

## Test Signals
Protocol tests should verify XDR round-trip, millisecond conversion, equality/hash consistency, and copy-constructor correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/NfsTime.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/FileHandle.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/FileHandle.java

## Purpose
`FileHandle.java` represents the opaque NFS file handle returned to clients and sent back on later operations.

## Important APIs, Types, and Functions
- Default constructor leaves `handle` null for later deserialization.
- `FileHandle(long fileId, int namenodeId)` builds a 32-byte handle with file id in bytes 0-7, namenode id in bytes 8-11, and zeros afterward.
- `FileHandle(long)` defaults namenode id to 0.
- `FileHandle(String)` builds a 32-byte MD5-derived handle with first 16 bytes zero and last 16 bytes digest of the UTF-8 string.
- `serialize(XDR)` writes handle length and fixed opaque bytes.
- `deserialize(XDR)` verifies length, reads fixed opaque bytes, and extracts file id and namenode id.
- `getFileId()`, `getNamenodeId()`, `getContent()`, `toString()`, `equals()`, `hashCode()`, and `dumpFileHandle()` expose and compare handle data.

## Control Flow and State
The object caches decoded `fileId` and `namenodeId` for numeric handles. Deserialization mutates a default instance. String-derived handles do not set meaningful file id/namenode id fields.

## Dependencies and Integration Points
It uses ONCRPC `XDR`, Java `MessageDigest`, `ByteBuffer`, and SLF4J. NFS mount and NFSv3 procedure implementations use file handles as stable references to filesystem objects.

## Risks and Edge Cases
`serialize()` assumes `handle` is non-null. `deserialize()` verifies 32 bytes even though `Nfs3Constant.NFS3_FHSIZE` permits up to 64 bytes, reflecting Hadoop's chosen handle layout. MD5 unavailability leaves `handle` null. `getContent()` protects immutability with a clone.

## Test Signals
Needed tests include numeric handle round-trip, string handle stability, equality/hash behavior, invalid XDR length, and null-handle safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/FileHandle.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Base.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Base.java

## Purpose
`Nfs3Base.java` is the abstract base for starting and stopping an NFSv3 server over TCP.

## Important APIs, Types, and Functions
- Constructor stores `RpcProgram` and logs configured port.
- `getRpcProgram()` exposes the program.
- `start(boolean register)` starts the TCP server and optionally registers the NFSv3 TCP service with portmap and a shutdown hook.
- `startTCPServer()` constructs `SimpleTcpServer`, starts program daemons, runs the server, captures bound port, and terminates on failure.
- `stop()` unregisters the bound TCP port, stops program daemons, and shuts down the TCP server.
- `NfsShutdownHook` calls `stop()` with shutdown hook priority 10.

## Control Flow and State
State includes the `RpcProgram`, bound NFS port, and `SimpleTcpServer`. The server supports TCP only; UDP is deliberately not started.

## Dependencies and Integration Points
It depends on Hadoop ONCRPC server classes, portmap registration, `ShutdownHookManager`, SLF4J, and `ExitUtil`. Concrete NFS daemons subclass it with protocol-specific `RpcProgram` implementations.

## Risks and Edge Cases
Startup failure terminates the process. Registration happens after server startup, so a failure to register leaves a running server only until `terminate()` exits. `stop()` unregisters whenever a positive bound port exists.

## Test Signals
Integration tests should verify TCP binding, portmap registration/unregistration, daemon lifecycle, and no UDP registration for NFSv3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Base.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Constant.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Constant.java

## Purpose
`Nfs3Constant.java` centralizes NFSv3 protocol constants, procedure enums, mode/access bits, write stability options, verifier values, and NFS export cache config keys.

## Important APIs, Types, and Functions
- `SUN_RPCBIND=111`, `PROGRAM=100003`, and `VERSION=3` identify NFS RPC services.
- `NFSPROC3` enum maps NFSv3 procedures to ordinal wire values and marks non-idempotent procedures (`CREATE`, `MKDIR`, `SYMLINK`, `MKNOD`, `REMOVE`, `RMDIR`, `RENAME`, `LINK`) as not idempotent.
- `NFSPROC3.fromValue(int)` safely returns null for invalid ordinals.
- File handle, cookie verifier, create verifier, and write verifier byte sizes are defined.
- Access request/response bit masks and POSIX mode bit masks are defined.
- `WriteStableHow` maps `UNSTABLE`, `DATA_SYNC`, and `FILE_SYNC` to ordinals.
- `WRITE_COMMIT_VERF` is initialized from current time for server-instance write commit verification.
- Filesystem property bits, create options, and `nfs.exports.cache.*` config defaults are defined.

## Control Flow and State
Most fields are immutable constants. `WRITE_COMMIT_VERF` is process-start-time state and changes between server instances. Enum ordinal order is protocol-significant.

## Dependencies and Integration Points
NFSv3 dispatchers, request/response serializers, write handling, access checks, and `NfsExports` use these constants.

## Risks and Edge Cases
`WriteStableHow.fromValue(int)` does not bounds-check and can throw `ArrayIndexOutOfBoundsException` for invalid wire values. `MODE_ALL` contains duplicate OR terms but the result remains effectively a mask of all listed bits. Protocol constants must remain stable.

## Test Signals
Tests should cover ordinal mapping, invalid procedure values, idempotence flags, stable write enum parsing, and config default use in `NfsExports`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Constant.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3FileAttributes.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3FileAttributes.java

## Purpose
`Nfs3FileAttributes.java` models the NFSv3 `fattr3` structure and serializes/deserializes file metadata to XDR.

## Important APIs, Types, and Functions
- Fields include type, mode, nlink, uid, gid, size, used, device `Specdata3`, fsid, fileId, atime, mtime, and ctime.
- Nested `Specdata3` stores major/minor-style special device data.
- Default constructor creates a regular-file-like default.
- Main constructor accepts `NfsFileType`, link count, mode, uid/gid, size, fsid, fileId, mtime, atime, and rdev; `used` defaults to size, `ctime` defaults to mtime, and zero atime falls back to mtime.
- Copy constructor copies scalar fields and wraps times in new `NfsTime` instances.
- `serialize(XDR)` writes fields in NFSv3 attribute order.
- `deserialize(XDR)` reads the same order into a new instance.
- `getWccAttr()` returns weak cache consistency attributes using size, mtime, and ctime.
- Getters and setters expose selected mutable fields (`size`, `used`, `rdev`).

## Control Flow and State
Instances are mutable for size/used/rdev, while most fields are only set by constructors or deserialization. XDR order must match RFC 1813 fattr3 layout.

## Dependencies and Integration Points
It uses `NfsFileType`, `NfsTime`, `WccAttr`, and ONCRPC `XDR`. NFSv3 responses use this type to return object attributes and weak cache consistency data.

## Risks and Edge Cases
The copy constructor relies on `NfsTime` copy behavior, which appears flawed in `NfsTime`. The main constructor initializes `rdev` twice, first to default then to provided value. There are no validation checks for mode, uid/gid ranges, or negative sizes.

## Test Signals
Round-trip XDR serialization/deserialization, WCC conversion, default-atime behavior, and copy-constructor behavior are the key test areas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3FileAttributes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Interface.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Interface.java

## Purpose
`Nfs3Interface.java` defines the Java handler contract for all NFSv3 RPC procedures from RFC 1813.

## Important APIs, Types, and Functions
- `nullProcedure()` returns an NFS null response.
- Methods for all standard NFSv3 operations accept request `XDR` and `RpcInfo` and return `NFS3Response`: `getattr`, `setattr`, `lookup`, `access`, `readlink`, `read`, `write`, `create`, `mkdir`, `symlink`, `mknod`, `remove`, `rmdir`, `rename`, `link`, `readdir`, `readdirplus`, `fsstat`, `fsinfo`, `pathconf`, and `commit`.

## Control Flow and State
The interface has no state. Implementations decode request XDR, use `RpcInfo` for request context/credentials, perform filesystem work, and return typed NFS response objects.

## Dependencies and Integration Points
It integrates `NFS3Response`, ONCRPC `RpcInfo`, and `XDR`. NFSv3 RPC programs dispatch from `Nfs3Constant.NFSPROC3` values to implementations of this interface.

## Risks and Edge Cases
The interface exposes every NFSv3 operation, so implementation consistency is critical for auth, idempotence, write stability, and response status mapping. The API does not declare checked exceptions, implying implementations encode errors into `NFS3Response`.

## Test Signals
Coverage should exist at implementation level for each procedure's XDR decode, authorization, filesystem side effects, and response serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Interface.java -->

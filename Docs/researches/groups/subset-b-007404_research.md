# Research: subset-b-007404

This grouped report covers Hadoop common security test sources. Each section preserves the original source path and is bounded by reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestSecurityUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestSecurityUtil.java

Purpose: exercises `SecurityUtil`, related `NetUtils` token-service helpers, Kerberos principal utilities, ZK auth loading, and host resolver caching. It prevents regressions in principal expansion, lower-casing, wildcard host handling, token service address canonicalization, authentication method configuration, and resolver failure behavior.

Important APIs and types: `SecurityUtil.getServerPrincipal`, `isTGSPrincipal`, `getHostFromPrincipal`, `buildDTServiceName`, `buildTokenService`, `setTokenService`, `getTokenServiceAddr`, `getZKAuthInfos`, `setAuthenticationMethod`, `getAuthenticationMethod`, `StandardHostResolver`, `QualifiedHostResolver`, `CacheableHostResolver`; also `CredentialProviderFactory`, `LocalJavaKeyStoreProvider`, `Token`, `ZKAuthInfo`, `NetUtils`, and mocked `InetAddress`.

Control flow: setup pins Kerberos realm properties so host/principal tests are deterministic. Helper methods validate both string and `InetAddress` principal expansion, then address helpers construct socket addresses, encode token services under `use_ip` true and false, and decode back. Auth tests load ZK auth from literal config, `@file` indirection, and local JCEKS. Resolver tests toggle `HADOOP_SECURITY_TOKEN_SERVICE_USE_IP` and hostname cache duration to assert resolver type and cache presence, then test cached identity reuse, expiry, and invalid host exceptions.

State and persistence: mutates JVM system properties for Kerberos, static `SecurityUtil` configuration and resolver singletons, `NetUtils` static resolutions, temporary auth files, and local JCEKS credential stores. Temp files are deleted in finally blocks, but static configuration can affect neighboring tests if run in the same JVM without reset.

Dependencies and integration points: integrates Hadoop configuration keys, Kerberos Java principal parsing, Hadoop credential providers, token serialization services, `NetUtils` static DNS overrides, Guava file helpers, Mockito, and JUnit 5. It tests the security layer as consumed by RPC token service generation and ZK authentication config.

Risks: DNS and hostname resolution may vary by host environment. Static resolver and config state can bleed across tests. Cache expiry uses `Thread.sleep(1500)`, which is timing-sensitive. The local JCEKS test depends on provider registration and filesystem permissions.

Test signals: strong signal for principal replacement, auth config validation, malformed socket address rejection, service-address round trips, ZK auth source precedence, resolver type selection, resolver cache hit/expiry, and invalid-host exception propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestSecurityUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestShellBasedIdMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestShellBasedIdMapping.java

Purpose: validates `ShellBasedIdMapping` behavior for Unix/NFS user and group ID mapping, including static map parsing, shell command parsing, duplicate resolution, unsigned 32-bit overflow handling, refresh intervals, and incremental lookup updates.

Important APIs and types: `ShellBasedIdMapping`, `ShellBasedIdMapping.StaticMapping`, `ShellBasedIdMapping.PassThroughMap`, `parseStaticMap`, `updateMapInternal`, `getUidNameMap`, `getGidNameMap`, `getUid`, `getGid`, `getUserName`, `getGroupName`, `clearNameMaps`, `IdMappingConstant`, Guava `BiMap`/`HashBiMap`, and `Configuration`.

Control flow: tests create temporary static map files, parse `uid`/`gid` lines with comments, tabs, empty lines, and large unsigned values, then assert pass-through behavior for unmapped IDs. Shell parser tests feed synthetic `echo | cut` commands into `updateMapInternal` to build user/group maps. Refresh tests compare a reference mapper against an incremental mapper, repeatedly clearing maps and changing the static mapping file before `getUid`/`getGid` calls. Duplicate tests verify first/last retained names in the bidirectional map. Update interval tests verify defaults, minimum clamp, and custom timeout.

State and persistence: writes temp static map files and depends on their modification time for refresh behavior; one loop sleeps briefly to avoid same-mtime ambiguity. It also shells out or emulates shell commands and can read real local account/group maps in incremental tests.

Dependencies and integration points: integrates Hadoop NFS ID mapping constants, platform assumptions (`assumeNotWindows`), shell command execution, local OS passwd/group sources, and Guava bidirectional maps.

Risks: non-Windows tests depend on host account database stability. Static map refresh is mtime-sensitive. Duplicate resolution depends on `HashBiMap` replacement semantics and the order of command output. Unsigned ID overflow mapping to signed Java `int` values is intentional but easy to regress.

Test signals: good coverage for parser robustness, static remap precedence, duplicate filtering, 32-bit boundary IDs, timeout configuration, and incremental cache population through individual lookup APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestShellBasedIdMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestShellBasedUnixGroupsMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestShellBasedUnixGroupsMapping.java

Purpose: tests shell-backed Unix group resolution, especially edge cases around nonexistent users, numeric group names versus unresolved group IDs, command timeout configuration, and integration with the higher-level `Groups` framework.

Important APIs and types: `ShellBasedUnixGroupsMapping`, `GroupMappingServiceProvider`, `Groups`, `Shell.ShellCommandExecutor`, `Shell.ExitCodeException`, `CommonConfigurationKeys.HADOOP_SECURITY_GROUP_SHELL_COMMAND_TIMEOUT_KEY`, `ReflectionUtils`, and `GenericTestUtils.LogCapturer`.

Control flow: nested subclasses override `createGroupExecutor` and `createGroupIDExecutor` to return Mockito shell executors with controlled output and exceptions. The tests verify empty results for nonexistent users, filtering of unresolved numeric group IDs when names cannot be resolved, retention of numeric names when the ID command proves they are actual names, and normal group parsing. Timeout tests instantiate a delayed command subclass and assert configured timeout values for seconds, minutes, and millisecond input. `testFiniteGroupResolutionTime` executes sleep/timeout commands, checks log messages, and verifies that direct mapping returns no groups while the `Groups` wrapper raises `IOException`.

State and persistence: captures static logs from `ShellBasedUnixGroupsMapping.LOG`, clears captured output between phases, and uses real sleep/timeout commands. No durable files are written.

Dependencies and integration points: integrates shell command construction, Hadoop configuration duration parsing, the `Groups` cache/service wrapper, Mockito mocks, JUnit timeouts, and platform-specific sleep commands.

Risks: timeout behavior is timing-sensitive and may vary on slow hosts. Windows command semantics differ. Log-message assertions can be brittle if production logging text changes. Mocked executor output must mirror real command output formats to remain meaningful.

Test signals: covers command failure tolerance, ambiguous numeric group handling, timeout propagation to both name and ID executors, direct versus framework-level error behavior, and successful parsing of multi-line shell output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestShellBasedUnixGroupsMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUGILoginFromKeytab.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUGILoginFromKeytab.java

Purpose: integration-tests `UserGroupInformation` keytab login and relogin semantics with `MiniKdc`, including renewal executor configuration, subject-derived UGI behavior, failed relogin recovery, and concurrent relogin synchronization.

Important APIs and types: `MiniKdc`, `UserGroupInformation.loginUserFromKeytab`, `loginUserFromKeytabAndReturnUGI`, `getUGIFromSubject`, `loginUserFromSubject`, `reloginFromKeytab`, `forceReloginFromKeytab`, `isFromKeytab`, `KerberosTicket`, `KerberosPrincipal`, `LoginContext`, `Subject`, `User`, renewal config keys, `CyclicBarrier`, `CountDownLatch`, and executor services.

Control flow: `@BeforeEach` enables Kerberos auth, resets immediate-renew behavior, starts a MiniKdc, and creates a thread pool; `@AfterEach` stops both. Basic tests create principals/keytabs, log in, assert `isFromKeytab`, last-login time, and new `LoginContext` on relogin. Subject tests remove or modify Hadoop `User` principals to distinguish managed keytab logins from external subjects. Renewal tests toggle `HADOOP_KERBEROS_KEYTAB_LOGIN_AUTORENEWAL_ENABLED`. Relogin tests compare ticket identity/auth time across login users and external subject users. Failure recovery renames the keytab to force `KerberosAuthException`, then restores it. The concurrency test blocks logout on a barrier to prove relogins serialize while `getCurrentUser` remains nonblocking.

State and persistence: creates MiniKdc work directories and keytab files under JUnit temp dirs, mutates static UGI configuration/login user, toggles renewal test flags, and starts executor threads. Cleanup shuts down KDC and executor but relies on JUnit temp cleanup for files.

Dependencies and integration points: integrates JAAS login, Java Kerberos credentials, Hadoop UGI internals, MiniKdc, Mockito spies, and concurrent Java primitives.

Risks: Kerberos integration and timing sleeps can be slow/flaky. Static UGI state and global Kerberos config can leak. Concurrency assertions rely on barriers and timeouts. Keytab rename behavior depends on local filesystem semantics.

Test signals: strong integration signal for keytab login, managed versus external subject relogin isolation, renewal executor activation, failure recovery, and credential corruption prevention under concurrent relogin.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUGILoginFromKeytab.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUGIWithExternalKdc.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUGIWithExternalKdc.java

Purpose: verifies UGI keytab login against a user-provided external KDC when explicitly enabled. It is a guarded integration test for deployments that want to validate real Kerberos infrastructure rather than MiniKdc.

Important APIs and types: `SecurityUtilTestHelper.isExternalKdcRunning`, JUnit `assumeTrue`, `UserGroupInformation.loginUserFromKeytabAndReturnUGI`, `AuthenticationMethod.KERBEROS`, `Configuration`, and `CommonConfigurationKeys.HADOOP_SECURITY_AUTHENTICATION`.

Control flow: `@BeforeEach` skips the test unless external KDC support is enabled. The test reads `user.principal` and `user.keytab` system properties, configures Hadoop security authentication to Kerberos, logs in through UGI, and asserts the returned UGI uses Kerberos. It then attempts to log in as a bogus principal using the same keytab and expects failure.

State and persistence: reads JVM system properties for principal, keytab, and external KDC enablement; mutates static UGI configuration. It does not create files and depends entirely on externally provisioned Kerberos files/config.

Dependencies and integration points: integrates with real `java.security.krb5.conf`, real KDC service, external keytab material, and Hadoop UGI Kerberos login. It is intentionally skipped in normal unit-test environments.

Risks: unavailable or misconfigured external KDC causes skip or failure. Printing caught exception stack traces can create noisy logs. Because the keytab is external, failures may indicate environmental drift rather than code regression.

Test signals: when enabled, provides high-value end-to-end proof that UGI can authenticate with real Kerberos and rejects mismatched principals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUGIWithExternalKdc.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUGIWithMiniKdc.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUGIWithMiniKdc.java

Purpose: tests UGI automatic credential renewal failure/retry behavior using a MiniKdc with very short ticket lifetimes and a deliberately bogus `kinit` command.

Important APIs and types: `MiniKdc`, `UserGroupInformation`, `spawnAutoRenewalThreadForUserCreds`, `UserGroupInformation.metrics.getRenewalFailures`, `SecurityUtil.setAuthenticationMethod`, `LambdaTestUtils.await`, and `HADOOP_KERBEROS_MIN_SECONDS_BEFORE_RELOGIN`.

Control flow: setup builds a MiniKdc configuration with two-second ticket lifetimes, starts it under `test.dir`, and creates a principal/keytab. The test configures Kerberos auth, sets `hadoop.kerberos.kinit.command` to a bogus executable to force renewal failures, lowers the relogin interval to one second, logs in from keytab, spawns the auto-renewal thread for user credentials, then waits until the renewal failure metric increments.

State and persistence: static `MiniKdc` is stopped in `@AfterEach`, and `UserGroupInformation.reset()` is called. It writes KDC/keytab data under the test directory and mutates UGI metrics/logging/global config.

Dependencies and integration points: integrates Hadoop MiniKdc, UGI renewal thread logic, retry metrics, test logging, and polling with timeout.

Risks: inherently timing-sensitive; short ticket lifetimes and background threads can be flaky on overloaded CI. Metrics are global and may have prior state if not isolated. The test intentionally avoids real `kinit` to prevent renewing a developer's own TGT.

Test signals: proves the renewal thread retries and records failures for expiring Kerberos credentials. Detailed backoff logic is intentionally delegated to `TestUserGroupInformation#testGetNextRetryTime`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUGIWithMiniKdc.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUserFromEnv.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUserFromEnv.java

Purpose: verifies that the `HADOOP_USER_NAME` system property path is honored by `UserGroupInformation.getLoginUser`.

Important APIs and types: `UserGroupInformation.HADOOP_USER_NAME`, `System.setProperty`, `UserGroupInformation.getLoginUser`, and JUnit assertions.

Control flow: the single test sets the Hadoop user-name system property to `randomUser`, calls `getLoginUser`, and asserts that the login user's name matches the configured value.

State and persistence: mutates a JVM system property and static UGI login state. The test does not clear the property afterward, so isolation depends on the surrounding test framework or a fresh JVM.

Dependencies and integration points: covers the environment/system-property user override used by Hadoop command-line tools and simple-auth deployments.

Risks: property leakage can affect later UGI tests. If a login user was already initialized before the property is set, behavior could differ; the test assumes UGI has not cached a conflicting login user.

Test signals: narrow but important regression signal for simple user override semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUserFromEnv.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUserGroupInformation.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUserGroupInformation.java

Purpose: broad unit/integration coverage for `UserGroupInformation`: login modes, current/login users, proxy users, auth-to-local rules, group lookup metrics, credentials and tokens, subject propagation, Kerberos relogin timing, token import, and concurrency around subjects and credentials.

Important APIs and types: `UserGroupInformation`, `AuthenticationMethod`, `SaslRpcServer.AuthMethod`, `SecurityUtil`, `KerberosName`, `Subject`, `User`, `Credentials`, `Token`, `TokenIdentifier`, `KeyTab`, `KerberosTicket`, `LoginContext`, `SubjectInheritingThread`, `RetryPolicies`, metrics assertions, and Hadoop token config keys.

Control flow: setup installs a dummy JAAS configuration to catch accidental use of the JVM default login config, sets Kerberos realm properties, resets UGI before each test, and clears the login user after each test. Tests validate supported/unsupported login methods, proxy real-auth lookup, `doAs` scoping, OS group parity, constructor short-name rules under simple/Kerberos and Hadoop/MIT mechanisms, Kerberos rule initialization, equality by shared subject, group getters, token add/replace/named-token behavior, credential copy semantics, immutable token collections, token identifiers, auth method propagation, LoginContext preservation, UGI under non-Hadoop `Subject`, `getUGIFromSubject` principal conversion, relogin elapsed-time reflection, `setLoginUser`, private token exclusion, token race prevention, external token files, subject login with keytab private credential, renewal retry-time backoff, concurrent `getCurrentUser`, destroyed-ticket handling, and token import from config or system properties.

State and persistence: heavily mutates static UGI configuration/login user, KerberosName rules, JVM system properties, Hadoop metrics, token files under `target`, and `hadoop.token.files`/`HADOOP_TOKENS` properties. Some cleanup is explicit, but metrics and global state are central risk areas.

Dependencies and integration points: integrates OS `whoami`/`id -Gn` or winutils, Hadoop metrics, token storage files, JAAS, Kerberos principal parsing, Mockito spies/mocks, retry policies, and concurrent execution primitives.

Risks: large global-state surface can cause order-dependent failures. OS group tests are environment-dependent. Reflection against private `hasSufficientTimeElapsed` is brittle. Concurrency tests rely on timeouts and barriers. Token import ignores bad entries/files, so assertions focus on successful valid imports and dedupe behavior.

Test signals: very strong behavioral signal for UGI's core contract: subject identity, auth methods, credentials isolation, token persistence/import, private token filtering, Kerberos retry scheduling, concurrency safety, and global configuration handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUserGroupInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestWhitelistBasedResolver.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestWhitelistBasedResolver.java

Purpose: validates `WhitelistBasedResolver` selection of SASL properties based on fixed whitelist files, optional variable whitelist files, local address treatment, null inputs, and CIDR/IP matching.

Important APIs and types: `WhitelistBasedResolver`, `getSaslProperties`, `getDefaultProperties`, `getServerProperties`, whitelist configuration keys, `TestFileBasedIPList`, `Configuration`, `InetAddress`, and SASL privacy property maps.

Control flow: tests create fixed and variable whitelist files with exact IPs and CIDR ranges, configure resolver options, instantiate the resolver, and compare returned properties. When fixed and variable whitelists are enabled, matching IPs return default properties while nonmatching IPs return SASL privacy properties; localhost is treated as allowed. With variable whitelist disabled, only fixed whitelist and localhost are allowed. Null IP address/string inputs return privacy properties.

State and persistence: writes `fixedwhitelist.txt` and `variablewhitelist.txt` in the working directory through `TestFileBasedIPList`, then removes them. Resolver cache duration is configured but not dynamically refreshed in these tests.

Dependencies and integration points: integrates IP list file parsing, CIDR matching, Hadoop SASL/QOP configuration, and resolver configuration loading.

Risks: file cleanup is manual, so test interruption can leave files. IP string matching and local host assumptions must remain stable. The variable whitelist cache refresh path is only partially covered by configuration, not by modifying files after initialization.

Test signals: good signal for fixed/variable whitelist precedence, CIDR boundaries, localhost default allowance, disabled variable list behavior, and safe null handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestWhitelistBasedResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/alias/TestCredShell.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/alias/TestCredShell.java

Purpose: tests the `CredentialShell` command-line lifecycle and validation behavior for creating, listing, checking, deleting, help output, invalid providers, transient providers, prompting, and strict password enforcement.

Important APIs and types: `CredentialShell`, `CredentialShell.PasswordReader`, `CredentialProviderFactory.CREDENTIAL_PROVIDER_PATH`, `ProviderUtils` warning/error constants, `Configuration`, `Path`, `GenericTestUtils.getTestDir`, and `ByteArrayOutputStream`.

Control flow: setup redirects `System.out` and `System.err` to buffers, deletes the test keystore, and builds a JCEKS provider URI. Lifecycle tests run `create`, `list`, `delete`, and `list` again against the same provider, asserting return codes and output. Invalid/transient provider tests verify no-provider and warning messages. Prompt tests inject `MockPasswordReader` values to simulate mismatched, missing, successful, and failed password checks. Argument tests call `init` directly for empty args, command help, and missing command operands. Strict mode verifies that missing provider password becomes an error rather than a warning. Help tests assert usage output.

State and persistence: writes a JCEKS keystore under `GenericTestUtils.getTestDir("creds")`, redirects global `System.out/err` without restoring them in the test class, and mutates the in-memory user provider for `user:///` cases.

Dependencies and integration points: exercises the CLI facade over credential providers, provider password warning policy, Hadoop configuration, filesystem-backed JCEKS persistence, and interactive password reader abstraction.

Risks: global stream redirection can affect neighboring tests. One password-failure branch appears to create `passwordError` but passes the previous `password` list, so its intended mismatch may be weaker than the assertion suggests. Keystore files persist between tests unless setup deletion is complete.

Test signals: validates user-facing CLI return codes and messages, lifecycle persistence, transient-provider warnings, strict mode enforcement, prompt handling, and basic command parser behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/alias/TestCredShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/alias/TestCredentialProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/alias/TestCredentialProvider.java

Purpose: narrowly tests credential entry value storage and nested provider URI unwrapping.

Important APIs and types: `CredentialProvider.CredentialEntry`, `ProviderUtils.unnestUri`, `Path`, `URI`, and JUnit equality/array assertions.

Control flow: `testCredentialEntry` creates an entry with alias `cred1` and a char-array credential, then asserts alias and array contents. `testUnnestUri` checks that nested provider URIs are converted into the expected Hadoop `Path`, including HDFS authorities, query/fragment retention, nested schemes with multiple `@` separators, and `user:///` handling.

State and persistence: no durable state; all objects are in-memory.

Dependencies and integration points: supports the broader credential provider factory by verifying URI normalization used by keystore-backed provider paths.

Risks: URI unnesting behavior is subtle and can regress with changes to URI parsing around authority, path, query, or fragments. The credential entry test does not check defensive copying of char arrays.

Test signals: focused signal for simple alias/credential accessors and provider URI conversion rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/alias/TestCredentialProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/alias/TestCredentialProviderFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/alias/TestCredentialProviderFactory.java

Purpose: validates provider discovery, error handling, credential CRUD/persistence, password lookup fallback, UGI-backed secret storage, keystore file permissions, and unsupported local BCFKS creation.

Important APIs and types: `CredentialProviderFactory`, `CredentialProvider`, `UserProvider`, `JavaKeyStoreProvider`, `LocalJavaKeyStoreProvider`, `LocalBouncyCastleFipsKeyStoreProvider`, `ProviderUtils.unnestUri`, `Configuration.getPassword`, `CredentialProvider.CLEAR_TEXT_FALLBACK`, `Credentials`, `UserGroupInformation`, `FileSystem`, `FileStatus`, `FsPermission`, and `Path`.

Control flow: `testFactory` configures `user:///` plus JKS provider URIs and asserts provider order, classes, and string forms. Error tests assert precise messages for unknown scheme and malformed URI. `checkSpecificProvider` performs common CRUD: missing credential checks, create, duplicate create failure, delete, missing delete failure, create two credentials, flush, `Configuration.getPassword` lookup through provider, clear-text fallback behavior, reload from provider, and alias list. `testUserProvider` verifies UGI credentials receive secret keys. JKS/local JKS tests assert keystore file creation with `rw-------`, then chmod to `777` and verify permission retention after flush. BCFKS test expects `IOException("Can't create keystore")`.

State and persistence: writes keystore files under `GenericTestUtils.getTestDir("creds")`, changes filesystem permissions, and mutates current user's UGI credentials for user provider tests.

Dependencies and integration points: integrates provider path parsing, filesystem APIs, Hadoop configuration password lookup, local and file-based keystores, permissions, and UGI credential storage.

Risks: random password generation is nondeterministic but only used for equality after round trip. File permission checks may vary on filesystems that do not preserve POSIX permissions. Current-user credentials are global to the test JVM. BCFKS behavior depends on crypto provider availability.

Test signals: strong coverage for provider resolution, persistent keystore semantics, permission creation/retention, config password fallback policy, and UGI secret integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/alias/TestCredentialProviderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authentication/server/TestProxyUserAuthenticationFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authentication/server/TestProxyUserAuthenticationFilter.java

Purpose: verifies that `ProxyUserAuthenticationFilter` honors the `doas` request parameter for a configured proxy user and exposes the proxied user as `HttpServletRequest.getRemoteUser` to downstream filters.

Important APIs and types: `ProxyUserAuthenticationFilter`, `AuthenticationFilter`, `FilterConfig`, `FilterChain`, `HttpServletRequest`, `HttpServletResponse`, servlet context attributes, Mockito, and AssertJ.

Control flow: a dummy `FilterConfig` provides `proxyuser.knox.users=testuser`, `proxyuser.knox.hosts=127.0.0.1`, and `type=simple`, plus a mocked servlet context without a signer secret provider. A custom `FilterChain` records `request.getRemoteUser()`. The mocked request returns remote user `knox`, parameter `doas=testuser`, remote address `127.0.0.1`, and principal `knox@EXAMPLE.COM`. After filter initialization and `doFilter`, the test asserts the chain saw `testuser`.

State and persistence: stores `actualUser` in the test instance. No files are written. Filter initialization may touch static proxy-user configuration through Hadoop auth internals.

Dependencies and integration points: integrates Hadoop auth filter setup, proxy-user authorization configuration, servlet API wrappers, and simple authentication mode.

Risks: test only covers the successful path, not unauthorized `doas`, missing principal, or failed host matching. The response stub is mostly no-op, so error/status behavior is not verified.

Test signals: focused signal that a valid proxy request is wrapped so downstream code sees the effective user rather than the real authenticated proxy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authentication/server/TestProxyUserAuthenticationFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestAccessControlList.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestAccessControlList.java

Purpose: validates `AccessControlList` parsing, string rendering, mutation APIs, wildcard handling, user/group authorization, netgroup integration, and proxied-real-user ACL mode.

Important APIs and types: `AccessControlList`, `UserGroupInformation`, `Groups`, `CommonConfigurationKeysPublic.HADOOP_SECURITY_GROUP_MAPPING`, `NativeCodeLoader`, Mockito spies, and AssertJ/JUnit assertions.

Control flow: the optional netgroup test exits early unless native code and a netgroup-capable group mapping class are configured. It populates ACLs with normal groups and netgroups, validates user group membership and ACL authorization before/after `Groups.refresh`. Core tests assert wildcard parsing for trimmed `*`, human-readable `toString`, round-trip `getAclString`, user/group parsing with spaces and commas, add/remove user/group behavior, illegal wildcard mutation, no-op add/remove on wildcard ACLs, authorization by explicit user and group, and empty ACL avoiding group lookup. The final test checks `USE_REAL_ACLS` so a proxied user's real user can be evaluated.

State and persistence: optional netgroup path depends on host `/etc/netgroup` and native code. Normal tests are in-memory but create UGI test users and may touch group mapping caches.

Dependencies and integration points: integrates ACL grammar, UGI short names/groups, group mapping services, netgroup providers, and proxy-user identity structure.

Risks: manual netgroup test is environment-specific. Empty ACL behavior is verified with a spy to ensure group lookup is skipped, which may be brittle if implementation changes. Wildcard ACL mutation intentionally preserves all-allowed state.

Test signals: strong coverage for ACL syntax, stable rendering/round-trip, mutation semantics, authorization evaluation, wildcard invariants, netgroup support when enabled, and real-user ACL mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestAccessControlList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestDefaultImpersonationProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestDefaultImpersonationProvider.java

Purpose: tests `DefaultImpersonationProvider` handling of proxy-user names that contain dots or spaces, especially successful wildcard authorization and failure messaging for space-containing proxy users.

Important APIs and types: `DefaultImpersonationProvider`, `ProxyUsers.CONF_HADOOP_PROXYUSER`, `UserGroupInformation`, `Configuration`, Mockito mocks, `AuthorizationException`, and `LambdaTestUtils.intercept`.

Control flow: setup creates a provider with proxy entries for `fakeuser`, `test.user`, and `test user2`, all with wildcard groups/hosts, then initializes using the standard proxy-user prefix. Success tests mock a proxy UGI with real users `fakeuser` and `test.user` and authorize from `2.2.2.2`. Failure test uses real user `test user2`, proxied user `dummyUser`, and asserts the authorization exception includes `User: test user2 is not allowed to impersonate dummyUser`.

State and persistence: in-memory configuration/provider only; mocks are nulled after each test.

Dependencies and integration points: integrates proxy-user configuration parsing and `UserGroupInformation.getRealUser`/short-name APIs.

Risks: tests are narrow and use mocks, so they do not validate actual group membership or host list matching. Behavior for spaces is partly a negative case despite wildcard-like setup, reflecting parsing/normalization sensitivity.

Test signals: useful regression signal for proxy user key parsing with special characters and error text from default impersonation authorization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestDefaultImpersonationProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestProxyServers.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestProxyServers.java

Purpose: validates the `ProxyServers` allow-list loaded by `ProxyUsers.refreshSuperUserGroupsConfiguration`.

Important APIs and types: `ProxyServers.isProxyServer`, `ProxyServers.CONF_HADOOP_PROXYSERVERS`, `ProxyUsers.refreshSuperUserGroupsConfiguration`, and `Configuration`.

Control flow: the test first asserts an arbitrary IP is not a proxy server with default state. It then configures `2.2.2.2, 3.3.3.3`, refreshes proxy-user configuration, and asserts the original IP is still false while both configured IPs are true.

State and persistence: mutates static proxy server configuration maintained by `ProxyServers`/`ProxyUsers`. No files are written.

Dependencies and integration points: integrates proxy server list parsing with the global proxy-user refresh path used by Hadoop HTTP and RPC impersonation features.

Risks: static allow-list can leak to other tests if not refreshed. Only exact IP strings are tested; no hostname or whitespace-edge coverage appears here.

Test signals: concise regression signal that configured proxy server IPs are recognized after refresh and unrelated IPs remain denied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestProxyServers.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestProxyUsers.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestProxyUsers.java

Purpose: comprehensive coverage for proxy-user impersonation authorization: group/user allow rules, host allow rules, wildcards, CIDR ranges, null arguments, duplicate normalization, provider override, custom configuration prefixes, missing hosts, optional netgroups, and a manual load-test harness.

Important APIs and types: `ProxyUsers`, `DefaultImpersonationProvider`, `ImpersonationProvider`, `AuthorizationException`, `UserGroupInformation`, `Groups`, `CommonConfigurationKeysPublic.HADOOP_SECURITY_IMPERSONATION_PROVIDER_CLASS`, `StringUtils`, `InetAddress`, and `NativeCodeLoader`.

Control flow: standard tests build configurations using provider helper keys, refresh global proxy settings, construct real/proxy UGIs, then assert both string-host and `InetAddress` authorization paths. Cases cover allowed group from good IP, disallowed IP, disallowed group, explicit user lists, wildcard groups/users/IPs, IP ranges, null UGI/address exceptions, deduped group and host entries, custom provider class that allows only real users in `sudo_<proxied>` groups, values with spaces, null/empty/custom prefixes, and no-hosts denial. Optional netgroup test runs only with native code and configured netgroup mapping. Static `loadTest` and `main` provide manual performance probing for large IP/range lists.

State and persistence: repeatedly mutates static proxy-user configuration and default impersonation provider state. No durable files are written. Optional netgroup path depends on host config and native libraries.

Dependencies and integration points: integrates UGI proxy identity, group mapping, machine/IP list matching, CIDR parsing, provider pluggability, and both hostname string and address overloads.

Risks: global static proxy config can create order dependency if tests run concurrently. Manual netgroup and load-test paths are environment-dependent and not normal automated checks. Fake `InetAddress` construction uses synthetic hostnames from IP strings to test address overloads while preserving address bytes.

Test signals: strong signal for impersonation authorization matrix, dedupe behavior, custom prefixes/providers, input validation, and address matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestProxyUsers.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestServiceAuthorization.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestServiceAuthorization.java

Purpose: validates `ServiceAuthorizationManager` ACL and machine-list authorization for RPC protocols, including default ACLs, blocked ACLs, default blocked ACLs, host allow lists, host block lists, and client-principal lookup in unsecure mode.

Important APIs and types: `ServiceAuthorizationManager`, `PolicyProvider`, `Service`, `AccessControlList`, `UserGroupInformation`, `SecurityUtil.setSecurityInfoProviders`, custom `SecurityInfo`, `KerberosInfo`, `TokenInfo`, `TestRPC.TestProtocol`, `Configuration`, `InetAddress`, and `CommonConfigurationKeys`.

Control flow: a test policy provider maps two protocol interfaces to ACL config keys. A custom security info provider returns a client principal key to ensure authorization works in unsecure mode when client principal metadata exists. ACL tests refresh the manager with different config combinations and authorize a UGI against protocol classes. They verify explicit protocol ACLs override defaults, missing ACLs use wildcard or default ACLs, blocked ACLs deny by user or group, empty blocked ACL resets denial, and default blocked ACL applies to protocols without explicit blocked ACL. Machine-list tests perform the same pattern for allowed hosts, default allowed hosts with CIDR/exact IPs, blocked hosts, and default blocked hosts.

State and persistence: in-memory manager/config only, but `SecurityUtil.setSecurityInfoProviders` mutates static security info providers and is not restored in this file.

Dependencies and integration points: integrates RPC protocol policy metadata, ACL parsing, machine list/CIDR matching, security info principal lookup, and UGI group membership.

Risks: static `SecurityUtil` provider mutation can leak. Tests rely on concrete IPs and exact default config keys. They mostly assert success/failure by catching exceptions, not exception messages.

Test signals: strong authorization matrix coverage for service ACL precedence, blocked ACL precedence, machine allow/block lists, and protocol-specific versus default policy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestServiceAuthorization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/http/TestCrossOriginFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/http/TestCrossOriginFilter.java

Purpose: tests Hadoop's `CrossOriginFilter` CORS handling, including same-origin passthrough, wildcard origins, header encoding against response splitting, wildcard and regex origin matching, disallowed request suppression, successful response headers, and reinitialization after destroy.

Important APIs and types: `CrossOriginFilter`, servlet `FilterConfig`, `FilterChain`, `HttpServletRequest`, `HttpServletResponse`, CORS header constants, Mockito, and `MockitoUtil.verifyZeroInteractions`.

Control flow: tests construct a map-backed `FilterConfigTest`, initialize a filter, and either call `areOriginsAllowed` directly or run `doFilter` with mocked requests/responses. Same-origin and disallowed origin/method/header tests verify no response headers are set while the chain proceeds. Pattern tests cover `*.example.com`, regex entries, complex protocol/port regex, mixed regex and wildcard lists, and origin-list strings where any origin may match. `testEncodeHeaders` confirms newline response-splitting content is truncated/sanitized while valid single or list origins survive. Successful CORS test verifies `Access-Control-Allow-Origin`, credentials, methods, and headers are set. Restart test initializes with one config, destroys, clears config, reinitializes with new values, and verifies new headers/origins.

State and persistence: filter instances are in-memory; no files. Restart test checks that destroy clears state enough for reuse.

Dependencies and integration points: integrates servlet filter lifecycle, Hadoop HTTP security config keys, CORS request/response headers, regex/wildcard matching, and response header encoding.

Risks: no negative regex malformed-pattern test. Disallowed requests are allowed through the chain without CORS headers, so tests do not assert browser-level behavior. Header comparison uses exact string ordering from config.

Test signals: strong signal for CORS origin matching semantics, header sanitation, allowed/disallowed branch behavior, and lifecycle reconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/http/TestCrossOriginFilter.java -->

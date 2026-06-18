# Research Group: subset-b-007432

This grouped report covers Hadoop HDFS HTTPFS test sources under `hadoop-hdfs-httpfs/src/test/java`. Each section is delimited for deterministic split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSServer.java

Purpose: Main HTTPFS integration suite. It starts an embedded Jetty webapp at `/webhdfs`, writes temporary `httpfs-site.xml` and `hdfs-site.xml`, points HTTPFS at the test HDFS cluster, and validates REST behavior against direct `FileSystem`/`DistributedFileSystem` calls.

Important APIs/types/functions: `createHttpFSConf`, `createHttpFSServer`, `delegationTokenCommonTests`, `createWithHttp`, `createDirWithHttp`, `getStatus`, `putCmd`, `putCmdWithReturn`, JSON parsers for permissions/ACLs/xattrs/trash paths, and snapshot helpers. `MockGroups` implements both `Service` and `Groups` so HTTPFS can resolve test users from `HadoopUsersConfTestHelper`. Tests cover `HttpFSServerWebApp`, `HttpFSAuthenticationFilter`, `HttpFSUtils`, `WebHdfsFileSystem`, `JsonUtil`, `JsonUtilClient`, HDFS ACL/xattr/snapshot/EC/storage policy APIs, and delegation token types.

Control flow: setup creates `conf`, `log`, `temp`, a signature secret, a `hadoop-conf` directory, and a Jetty `WebAppContext`. Each test drives HTTP operations through `HttpURLConnection`, then checks response codes, JSON payloads, HDFS side effects, and selected metrics counters. The delegation-token flow first verifies unauthenticated denial, signs an authentication cookie, obtains a token, uses it, renews it only with authenticated credentials, cancels it, and verifies later denial. Snapshot tests create directories, allow snapshots, perform REST snapshot operations, and compare REST JSON with DFS API output.

State and persistence: persistent state is confined to per-test temporary directories, generated XML configs, the signature secret, MiniDFS files, HDFS metadata, snapshots, ACLs, xattrs, and metrics in `HttpFSServerWebApp`. Static `metricsGetter` observes operation counters. Tests rely on `@TestDir`, `@TestJetty`, and `@TestHdfs` extensions to isolate local dirs, Jetty, and MiniDFS.

Dependencies/integration: integrates JUnit 5, Jetty, Hadoop test extensions, WebHDFS/HTTPFS REST contracts, JSON-simple/Jackson-style JSON helpers, authentication/signing classes, HDFS encryption-zone trash behavior, EC policy support, and server-default/block-location serialization. It is the broadest signal that HTTPFS maps WebHDFS operations to HDFS APIs correctly.

Risks and test signals: high-value coverage but environment-sensitive. Risks include brittle hard-coded JSON/checksum strings, timing and static metric state, reliance on default users/groups, manual URL construction without encoding for all parameters, and a likely typo in the block locations query parameter (`offset10` instead of `offset=10`). The suite strongly signals regressions in HTTP status codes, JSON schema, auth handling, ACL/xattr/snapshot feature wiring, no-redirect semantics, and HDFS feature exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSServerNoACLs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSServerNoACLs.java

Purpose: Negative integration suite for HTTPFS when HDFS ACL support is disabled. It proves normal file status/listing operations still work while ACL-specific operations surface HDFS ACL-disabled failures.

Important APIs/types/functions: `startMiniDFS`, `createHttpFSServer`, `getStatus`, `putCmd`, `MiniDFSCluster`, `DFS_NAMENODE_ACLS_ENABLED_KEY`, Jetty `WebAppContext`, `HttpFSAuthenticationFilter`, and `HadoopUsersConfTestHelper`.

Control flow: it builds its own MiniDFS cluster instead of using `TestHdfsHelper` so ACLs remain explicitly disabled. It writes HDFS and HTTPFS configuration files pointing HTTPFS at that cluster, starts Jetty, creates a directory/file directly through `FileSystem`, then calls REST status and ACL operations. `GETFILESTATUS` and `LISTSTATUS` must return OK without `aclBit`; `GETACLSTATUS` and all ACL mutation operations must return HTTP 500 containing `AclException` and the disabled-support message.

State and persistence: state is a per-test MiniDFS cluster plus generated local config/secret files. `miniDfs` and `nnConf` are instance fields; shutdown occurs at the end of the test, so assertion failures before shutdown can leave cleanup to the test framework/process teardown.

Dependencies/integration: exercises HTTPFS with HDFS defaults where ACLs are off and validates error propagation from HDFS through HTTPFS JSON/error streams.

Risks and test signals: strong guard for optional ACL support. Risks are brittle exact error text/status expectations and hand-rolled cluster lifecycle. A regression would show as ACL operations succeeding unexpectedly, status responses leaking `aclBit`, or errors not preserving useful ACL-disabled diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSServerNoACLs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSServerNoXAttrs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSServerNoXAttrs.java

Purpose: Negative integration suite for HTTPFS when HDFS extended attributes are disabled. It verifies xattr REST operations are rejected by HDFS and reported through HTTPFS.

Important APIs/types/functions: `startMiniDFS`, `createHttpFSServer`, `getStatus`, `putCmd`, `MiniDFSCluster`, `DFS_NAMENODE_XATTRS_ENABLED_KEY`, `TestHttpFSServer.setXAttrParam`, `HttpFSAuthenticationFilter`, and Jetty webapp setup.

Control flow: setup mirrors the no-ACL test but explicitly disables `dfs.namenode.xattrs.enabled`. The test creates a file directly in MiniDFS, then sends `GETXATTRS`, `SETXATTR`, and `REMOVEXATTR` requests through HTTPFS. All three must return HTTP 500 and error payloads mentioning `RemoteException`, `XAttr`, and `rejected`.

State and persistence: uses per-test local HTTPFS config/secret files and a per-test MiniDFS cluster. It writes HDFS state for `/noXAttr/file` and uses `nnConf` as the direct cluster client configuration.

Dependencies/integration: integrates HTTPFS request handling, HDFS xattr feature gates, and the shared xattr parameter encoder from the main server test.

Risks and test signals: good signal that optional xattr support does not accidentally appear enabled. It is sensitive to HDFS exception text and HTTP status mapping. The test does not explicitly shut down `miniDfs` at the end, so process/test extension cleanup is important if failures occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSServerNoXAttrs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSServerWebServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSServerWebServer.java

Purpose: Unit/integration tests for `HttpFSServerWebServer` lifecycle and signer secret-provider configuration.

Important APIs/types/functions: `init`, `teardown`, `createWebServer`, `createConfiguration`, `createConfigurationWithRandomSecret`, `createConfigurationWithSecretFile`, `setDeprecatedSecretFile`, `assertServiceRespondsWithOK`, and `assertSignerSecretProviderType`. It inspects the servlet context attribute `SIGNER_SECRET_PROVIDER_ATTRIBUTE` for `FileSignerSecretProvider` or `RandomSignerSecretProvider`.

Control flow: `@BeforeEach` creates a test root, config/log/temp directories, and required system properties; on Windows it copies `winutils` into a local `bin`. Lifecycle tests call start/stop, stop without start, double stop, and double start. Secret tests write or omit the configured secret file, start the web server, hit `LISTSTATUS`, and assert the chosen signer provider class.

State and persistence: writes `httpfs-site.xml` under the configured HTTPFS config dir before constructing the web server. `webServer` is stopped after each test if present. Secret file content is persisted only under the temporary test root.

Dependencies/integration: depends on Hadoop `HttpServer2`, HTTPFS authentication filter configuration keys including deprecated prefix support, Commons IO, `GenericTestUtils`, and the test users helper for HTTP requests.

Risks and test signals: important signal for idempotent lifecycle and secure/compatible secret fallback. Risks include reliance on global system properties and fallback to random secrets for missing/empty files, which is acceptable for tests but security-sensitive in production.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSServerWebServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSWithKerberos.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSWithKerberos.java

Purpose: Kerberos/SPNEGO integration tests for HTTPFS access and delegation tokens.

Important APIs/types/functions: `createHttpFSServer`, `resetUGI`, `testValidHttpFSAccess`, `testInvalidadHttpFSAccess`, `testDelegationTokenHttpFSAccess`, `testDelegationTokenWithFS`, and `testDelegationTokenWithinDoAs`. It uses `KerberosTestUtils`, `AuthenticatedURL`, `DelegationTokenAuthenticator`, `UserGroupInformation`, `HttpFSFileSystem`, and `WebHdfsFileSystem`.

Control flow: setup writes HTTPFS/HDFS config with `httpfs.authentication.type=kerberos`, configures proxyuser entries, starts Jetty, and sets HTTPFS authority. Valid access runs inside a Kerberos client subject and expects OK; invalid unauthenticated access expects unauthorized. Delegation-token tests obtain tokens via SPNEGO, use them for HTTPFS access, require SPNEGO for renew, allow cancel, and verify canceled-token denial. FileSystem tests login or create proxy users, obtain delegation tokens through filesystem implementations, set the token on a renewable filesystem, and list `/`.

State and persistence: global UGI configuration is reset after each test. The helper relies on system properties/keytab defaults for realm, principals, and keytab path; local configs and secrets are written in the test directory.

Dependencies/integration: integrates JAAS/Kerberos, Hadoop UGI, HTTPFS authentication, delegation token JSON, and both HTTPFS and WebHDFS filesystem clients.

Risks and test signals: high-value auth coverage but environment-sensitive because it assumes usable Kerberos test credentials/keytabs. The hard-coded `loginUserFromKeytab("client", "/Users/tucu/tucu.keytab")` path in the doAs helper path is especially brittle unless the test harness intercepts or configures it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSWithKerberos.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/lang/TestRunnableCallable.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/lang/TestRunnableCallable.java

Purpose: Unit tests for `RunnableCallable`, an adapter that exposes a `Runnable` as a `Callable` and a `Callable` as a `Runnable`.

Important APIs/types/functions: nested `R`, `C`, and `CEx` fixtures; tests `runnable`, `callable`, and `callableExRun`; adapter methods `run`, `call`, and `toString`.

Control flow: each positive test constructs a fixture, wraps it, invokes both adapter entry points, and checks the fixture side-effect flag. The exception test wraps a callable that throws and asserts `run()` converts the checked exception into `RuntimeException`.

State and persistence: only in-memory boolean flags; no external persistence.

Dependencies/integration: extends `HTestCase` and uses JUnit assertions. It verifies utility behavior used by scheduler/executor-style services.

Risks and test signals: narrow but useful signal for exception bridging and display names. It uses raw `Callable`, so generic type-safety is not covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/lang/TestRunnableCallable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/lang/TestXException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/lang/TestXException.java

Purpose: Unit tests for `XException` formatting, error identity, and cause wrapping.

Important APIs/types/functions: enum `TestERROR` implements `XException.ERROR` with template `{0}`; test `testXException` exercises constructors with no args, formatted message arg, normal cause, and an existing `XException`.

Control flow: each constructor variant is created and checked for `getError`, message text, and cause. Wrapping an `XException` must preserve the original error and message while using the original exception as the cause.

State and persistence: no persistent state.

Dependencies/integration: depends on `HTestCase`, JUnit, and the common error-template contract used by server/service exceptions.

Risks and test signals: good signal that error codes remain stable and messages include the enum prefix. It does not cover multiple formatting parameters or null templates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/lang/TestXException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/server/TestBaseService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/server/TestBaseService.java

Purpose: Unit test for `BaseService` prefixing, service-specific configuration extraction, dependency defaults, and subclass initialization.

Important APIs/types/functions: nested `MyService` extends `BaseService`, overrides protected `init` and `getInterface`; test `baseService` uses a Mockito `Server` to return a synthetic `Configuration` and prefixed names.

Control flow: it validates the service prefix, dependency list, and null interface before initialization. The mocked server provides keys `server.myservice.foo` and `server.myservice1.bar`; after `init`, only the exact `myservice` prefix should be visible in `getServiceConfig`, and subclass `init` should set a static flag.

State and persistence: in-memory static `MyService.INIT`; no filesystem.

Dependencies/integration: Mockito, Hadoop `Configuration`, and the `Server`/`BaseService` contract.

Risks and test signals: good guard against prefix bleed between similarly named services. Static flag can leak if tests run in unusual orders, but assertions are local and simple.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/server/TestBaseService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/server/TestServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/server/TestServer.java

Purpose: Comprehensive unit suite for the HTTPFS library `Server` container: constructors, directory validation, config loading precedence, lifecycle states, service loading, dependency validation, replacement/addition, and cleanup ordering.

Important APIs/types/functions: `createServer`, `getAbsolutePath`, `LifeCycleService`, `TestService`, `TestServiceExceptionOnStatusChange`, abstract `MyService`, service variants `MyService1` through `MyService7`, and tests for `constructorsGetters`, init failure cases, `lifeCycle`, `changeStatus`, config loading, illegal states, invalid services, missing dependencies, and `services`.

Control flow: tests construct `Server` with explicit or derived home/config/log/temp dirs, validate missing/non-directory paths map to expected `ServerException` codes, and verify default/site/system-property config precedence. Service tests load configured service class lists, record lifecycle ordering in static `ORDER` or `LIFECYCLE`, assert post-init and destroy ordering, force init/destroy/status-change failures, override services using `server.services.ext`, replace/add services using `setService`, and check dependency handling.

State and persistence: creates temporary directories and config/log4j/site XML files under `@TestDir`. Static lists record lifecycle order and are cleared before scenarios. Server state transitions through `UNDEF`, `BOOTING`, `NORMAL`/`ADMIN`, `SHUTTING_DOWN`, and `SHUTDOWN`.

Dependencies/integration: JUnit 5, custom `@TestDir` and `@TestException`, Hadoop `Configuration`, `StringUtils`, and `XException`/`ServiceException` error contracts.

Risks and test signals: central regression signal for service container correctness. Static lifecycle lists and multi-scenario test method are somewhat coupled, but the suite captures many edge cases: invalid classes, no default constructor, wrong interface, missing dependency, init rollback, destroy tolerance, and runtime service mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/server/TestServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/server/TestServerConstructor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/server/TestServerConstructor.java

Purpose: Parameterized validation of `Server` constructor argument checks.

Important APIs/types/functions: `constructorFailParams`, `initTestServerConstructor`, and parameterized `constructorFail`.

Control flow: each row supplies invalid combinations of name, home/config/log/temp directories, and configuration. The test stores them in instance fields and asserts `new Server(...)` throws `IllegalArgumentException`.

State and persistence: no filesystem creation; only parameter fields.

Dependencies/integration: JUnit 5 parameterized tests and Hadoop `Configuration`.

Risks and test signals: compact signal that constructor validation rejects null/empty/non-absolute or incomplete values. It does not include positive constructor cases, which are covered in `TestServer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/server/TestServerConstructor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/service/hadoop/TestFileSystemAccessService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/service/hadoop/TestFileSystemAccessService.java

Purpose: Integration tests for `FileSystemAccessService`, including security mode validation, Hadoop config loading, namenode whitelisting, filesystem creation/execution, exception handling, and cache eviction.

Important APIs/types/functions: `createHadoopConf`, `simpleSecurity`, Kerberos misconfiguration tests, `serviceHadoopConf`, `serviceHadoopConfCustomDir`, `inWhitelists`, `NameNodeNotinWhitelists`, `createFileSystem`, `fileSystemExecutor`, `fileSystemExecutorNoNameNode`, `fileSystemExecutorException`, and `fileSystemCache`.

Control flow: most tests build a `Server` with `InstrumentationService`, `SchedulerService`, and `FileSystemAccessService`. Config tests write `hdfs-site.xml` in the server config dir or custom dir. Security tests assert expected `ServiceException` codes for missing Kerberos keytab/principal, failed Kerberos login, and unknown auth type. Filesystem tests point the service at `TestHdfsHelper`, create/release filesystems, run executor callbacks, verify released filesystems are closed, translate callback exceptions to `H03`, and test cache reuse/purge across sleeps.

State and persistence: writes Hadoop XML config under `@TestDir`, uses MiniDFS for HDFS-backed tests, and relies on server services plus scheduler-driven cache purging. Cache state is time-based and lease-count-based.

Dependencies/integration: HTTPFS server container, instrumentation and scheduler services, HDFS mini-cluster, Hadoop `FileSystem`, UGI/security configuration, and custom exception annotations.

Risks and test signals: strong signal for filesystem access lifecycle and cleanup. Timing in `fileSystemCache` can be flaky on slow machines, and Kerberos failure tests intentionally depend on invalid local paths/principals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/service/hadoop/TestFileSystemAccessService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/service/instrumentation/TestInstrumentationService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/service/instrumentation/TestInstrumentationService.java

Purpose: Unit/integration suite for instrumentation primitives and the `InstrumentationService`.

Important APIs/types/functions: tests `cron`, `timer`, `sampler`, `variableHolder`, `service`, and `sampling`; classes `InstrumentationService.Cron`, `Timer`, `Sampler`, `VariableHolder`; public `Instrumentation` APIs `incr`, `createCron`, `addCron`, `addVariable`, `addSampler`, and `getSnapshot`.

Control flow: `cron` validates start/stop/end timing and illegal states. `timer` adds several cron samples and validates last/average own/total values plus JSON serialization. `sampler` validates rolling average behavior and JSON. `variableHolder` serializes a variable value. `service` boots a server with instrumentation, records counters/timers/variables/samplers, and confirms snapshot sections for OS env, system properties, JVM, counters, timers, variables, and samplers. `sampling` combines instrumentation with `SchedulerService`, registers a sampled variable, sleeps, and verifies scheduled samples occurred.

State and persistence: all metrics are in-memory. Tests use time sleeps and server lifecycle under `@TestDir`.

Dependencies/integration: Hadoop `Time`, JSON-simple, `Server`, scheduler service for periodic sampling, and `HTestCase` wait ratio.

Risks and test signals: good coverage of metric math and serialization. Timing tolerances and sleeps can be platform-sensitive, but `getWaitForRatio` is overridden to 1 for predictable duration expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/service/instrumentation/TestInstrumentationService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/service/scheduler/TestSchedulerService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/service/scheduler/TestSchedulerService.java

Purpose: Minimal service-registration test for `SchedulerService`.

Important APIs/types/functions: single `service` test, `Server`, `InstrumentationService`, `SchedulerService`, and `Scheduler` interface lookup.

Control flow: creates a test server with instrumentation and scheduler services, initializes it, asserts `server.get(Scheduler.class)` is non-null, then destroys the server.

State and persistence: temporary server directories only; scheduler state is in-memory and short-lived.

Dependencies/integration: verifies scheduler service can load through the server container and publish its interface when instrumentation is present.

Risks and test signals: narrow smoke test. It does not verify task execution or shutdown behavior, but catches registration/dependency regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/service/scheduler/TestSchedulerService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/service/security/TestGroupsService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/service/security/TestGroupsService.java

Purpose: Unit/integration tests for `GroupsService` registration and invalid group-mapping configuration.

Important APIs/types/functions: tests `service` and `invalidGroupsMapping`; service classes `GroupsService` and `Groups`.

Control flow: the positive test initializes a server with `GroupsService`, retrieves `Groups`, asks for groups for the current OS user, and asserts the list is not empty. The negative test configures `server.groups.hadoop.security.group.mapping` to `String.class`, initializes the server, and expects a runtime failure.

State and persistence: only temporary server directories; group lookup depends on current user and OS/group mapping.

Dependencies/integration: Hadoop group mapping, server service container, `StringUtils` service-list construction.

Risks and test signals: catches service publication and invalid mapping failures. The positive test is environment-sensitive because current-user group resolution must return at least one group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/service/security/TestGroupsService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/servlet/TestHostnameFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/servlet/TestHostnameFilter.java

Purpose: Unit tests for `HostnameFilter` thread-local remote hostname capture and cleanup.

Important APIs/types/functions: tests `hostname` and `testMissingHostname`; `HostnameFilter.get`, `doFilter`, and servlet `FilterChain`.

Control flow: mocked requests supply either `localhost` or null remote address. During the downstream chain, the test asserts the thread-local hostname resolves to a localhost representation or placeholder `???`; after `doFilter`, it asserts the thread-local is cleared.

State and persistence: uses a thread-local in `HostnameFilter`; no external persistence.

Dependencies/integration: Mockito, servlet API, and JUnit.

Risks and test signals: important cleanup signal for request-scoped logging context. Hostname resolution can vary by OS, so the test accepts `localhost` or `127.0.0.1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/servlet/TestHostnameFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/servlet/TestMDCFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/servlet/TestMDCFilter.java

Purpose: Unit tests for `MDCFilter`, which populates and clears SLF4J MDC fields for request logging.

Important APIs/types/functions: test `mdc`, mocked `HttpServletRequest`, `HostnameFilter.HOSTNAME_TL`, SLF4J `MDC`, and servlet `FilterChain`.

Control flow: first request has no principal and no hostname; chain sees method/path only. Second request adds a principal and chain sees user/method/path. Third sets `HostnameFilter` thread-local and chain sees hostname/user/method/path. After each filter call, key fields are expected to be cleared where checked.

State and persistence: thread-local MDC and hostname state only; `MDC.clear` starts the test.

Dependencies/integration: servlet API, Mockito, SLF4J MDC, and `HostnameFilter`.

Risks and test signals: good request-context cleanup signal. The final hostname thread-local is removed manually, and the test mainly validates in-chain values rather than every post-chain cleanup path after later invocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/servlet/TestMDCFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/servlet/TestServerWebApp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/servlet/TestServerWebApp.java

Purpose: Unit tests for `ServerWebApp` system-property directory resolution, lifecycle, failed init handling, and HTTP authority resolution.

Important APIs/types/functions: tests `getHomeDirNotDef`, `getHomeDir`, `lifecycle`, `failedInit`, and `testResolveAuthority`; `ServerWebApp.getHomeDir`, `getDir`, `contextInitialized`, `contextDestroyed`, and `resolveAuthority`.

Control flow: static directory helpers are checked against required and defaulted system properties. Lifecycle creates an anonymous `ServerWebApp`, sets home/config/log/temp properties, initializes/destroys it, and checks server status transitions. Failed init sets an invalid services property and expects runtime failure. Authority resolution reads configured hostname and port into an `InetSocketAddress`.

State and persistence: mutates JVM system properties and uses temporary directories from `@TestDir`; no cleanup of these properties is visible in the file.

Dependencies/integration: server lifecycle, servlet context listener flow, JUnit, and custom test directory helper.

Risks and test signals: catches global-property contract regressions. Property mutation can leak across tests if names collide, but test-specific prefixes reduce the risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/servlet/TestServerWebApp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/util/TestCheck.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/util/TestCheck.java

Purpose: Unit tests for the `Check` validation utility.

Important APIs/types/functions: `notNull`, `notNullElements`, `notEmptyElements`, `notEmpty`, `validIdentifier`, `gt0`, and `ge0`.

Control flow: positive tests assert valid values are returned unchanged. Negative tests use `assertThrows(IllegalArgumentException.class)` for null values, null/empty collection elements, empty strings, invalid identifiers, too-long identifiers, numeric identifiers, invalid starting characters, zero for `gt0`, and negative values for `gt0`/`ge0`.

State and persistence: none.

Dependencies/integration: `HTestCase`, JUnit assertions, Java collections.

Risks and test signals: broad input-validation guard for shared utility methods used throughout server/config parsing. It does not inspect exception messages, only types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/util/TestCheck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/util/TestConfigurationUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/util/TestConfigurationUtils.java

Purpose: Unit tests for `ConfigurationUtils` loading, copying, default injection, and variable resolution.

Important APIs/types/functions: `ConfigurationUtils.load`, `copy`, `injectDefaults`, and `resolve`; tests also use compact XML resource `test-compact-format-property.xml`.

Control flow: load tests parse standard Hadoop XML and compact `<property name value>` XML from streams/resources. Copy overwrites target keys from source while preserving target-only keys. Inject defaults fills only missing target keys. Resolve creates a new configuration with raw `${a}` references resolved. Variable resolution confirms Hadoop `Configuration.get` resolves config and system properties while raw values remain unresolved until explicit resolve.

State and persistence: in-memory configurations plus a classpath resource stream.

Dependencies/integration: Hadoop `Configuration`, Java streams, and classloader resources.

Risks and test signals: useful signal for config migration/compatibility. It does not test malformed XML, close behavior, or duplicate keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/util/TestConfigurationUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/wsrs/TestInputStreamEntity.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/wsrs/TestInputStreamEntity.java

Purpose: Unit test for `InputStreamEntity` streaming response entity.

Important APIs/types/functions: constructor `InputStreamEntity(InputStream)` and ranged constructor `InputStreamEntity(InputStream, offset, len)`, plus `write(OutputStream)`.

Control flow: first writes a full `ByteArrayInputStream("abc")` and asserts full output. Second writes with offset 1 and length 1 and asserts only byte `b` is emitted.

State and persistence: in-memory streams only.

Dependencies/integration: JUnit and Java IO. It validates behavior used by REST responses that stream file content or ranges.

Risks and test signals: narrow signal for basic full/range streaming. It does not cover zero-length, overrun, close propagation, or large stream behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/wsrs/TestInputStreamEntity.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/wsrs/TestJSONMapProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/wsrs/TestJSONMapProvider.java

Purpose: Unit test for JAX-RS JSON writer provider for `Map` types.

Important APIs/types/functions: `JSONMapProvider.isWriteable`, `getSize`, and `writeTo`.

Control flow: asserts the provider is writable for `Map.class` but not the test class, reports unknown size as `-1`, writes a `JSONObject` containing `a=A`, and checks serialized JSON.

State and persistence: in-memory output stream only.

Dependencies/integration: JSON-simple, JAX-RS provider contract, and JUnit.

Risks and test signals: basic provider serialization guard. It does not verify media type handling, character encoding headers, nested maps, or read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/wsrs/TestJSONMapProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/wsrs/TestJSONProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/wsrs/TestJSONProvider.java

Purpose: Unit test for JAX-RS JSON writer provider for `JSONObject`.

Important APIs/types/functions: `JSONProvider.isWriteable`, `getSize`, and `writeTo`.

Control flow: asserts writability for `JSONObject.class`, non-writability for the test class, unknown size `-1`, and exact serialization of a simple object.

State and persistence: in-memory output stream only.

Dependencies/integration: JSON-simple, JAX-RS provider contract, and JUnit.

Risks and test signals: basic JSON entity writer signal. It does not cover arrays, non-ASCII, media type selection, or error handling during write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/wsrs/TestJSONProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/wsrs/TestParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/wsrs/TestParam.java

Purpose: Unit tests for REST parameter parsing abstractions.

Important APIs/types/functions: generic helper `test`, concrete `BooleanParam`, `ByteParam`, `ShortParam`, `IntegerParam`, `LongParam`, `EnumParam`, `StringParam`, and regex-constrained `StringParam`.

Control flow: the helper validates name/domain/default value, default behavior for null/empty strings, valid parsing, and failure for invalid syntax/out-of-range values. Individual tests cover boolean, byte, short including octal radix constructor, integer, long, enum domain, unconstrained string, and regex-constrained string.

State and persistence: none.

Dependencies/integration: JUnit, Java regex, and the WSRS parameter base classes used by HTTPFS request parsing.

Risks and test signals: strong parsing-contract signal across primitive parameter types. It uses deprecated `new Short(...)` style and checks exceptions by manual try/fail rather than `assertThrows`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/wsrs/TestParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/HFSTestCase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/HFSTestCase.java

Purpose: Base class for tests needing the HTTPFS/HDFS test harness.

Important APIs/types/functions: class `HFSTestCase` extends `HTestCase` and registers `TestHdfsHelper` as a JUnit 5 extension through `@RegisterExtension`.

Control flow: no methods beyond extension registration. Subclasses inherit directory, Jetty, exception, and HDFS helpers.

State and persistence: `TestHdfsHelper` manages MiniDFS state when tests use `@TestHdfs`; this class itself holds an extension instance.

Dependencies/integration: JUnit 5 extension model, `HTestCase`, and `TestHdfsHelper`.

Risks and test signals: foundational test infrastructure. Its behavior is mostly covered indirectly by subclasses and directly by `TestHFSTestCase`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/HFSTestCase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/HTestCase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/HTestCase.java

Purpose: Common base class for HTTPFS tests, providing system-property initialization, JUnit extensions, scaled sleeps, and polling helpers.

Important APIs/types/functions: constants `TEST_WAITFOR_RATIO_PROP`, extensions `TestDirHelper`, `TestJettyHelper`, and `TestExceptionHelper`; `setWaitForRatio`, `getWaitForRatio`, nested `Predicate`, `sleep`, and `waitFor` overloads.

Control flow: static initialization loads test properties. Instance wait ratio defaults from `test.waitfor.ratio`. `sleep` scales time by the ratio. `waitFor` loops until a predicate returns true or timeout expires, logs progress roughly every five seconds, optionally fails on timeout, and wraps predicate exceptions in `RuntimeException`.

State and persistence: process-wide system properties and per-test extension state; no files directly, though registered helpers do.

Dependencies/integration: JUnit 5 extensions, Hadoop `Time`, and `SysPropsForTestsLoader`.

Risks and test signals: central infrastructure for timing-sensitive tests. Polling sleeps fixed 100 ms and console logging can slow very large test runs; exception wrapping may obscure original checked exception types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/HTestCase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/HadoopUsersConfTestHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/HadoopUsersConfTestHelper.java

Purpose: Test helper for user, group, and proxyuser configuration used by MiniDFS and HTTPFS tests.

Important APIs/types/functions: `getHadoopProxyUser`, `getHadoopProxyUserHosts`, `getHadoopProxyUserGroups`, `getHadoopUsers`, `getHadoopUserGroups`, `getBaseConf`, and `addUserConf`.

Control flow: static initialization loads test properties. Getters read system properties with defaults: current user for proxyuser, `*` hosts/groups, and default users `user1`/`user2` with groups `group1`/`supergroup` when no explicit `test.hadoop.user.*` properties exist. `getBaseConf` copies all system properties into a Hadoop `Configuration`. `addUserConf` sets simple authentication/proxyuser keys and creates test UGI users for each configured user.

State and persistence: mutates Hadoop `UserGroupInformation` static test users and reads JVM system properties. No files directly.

Dependencies/integration: Hadoop `Configuration`, UGI, and `SysPropsForTestsLoader`.

Risks and test signals: essential for reproducible HTTPFS proxyuser tests. The identity comparison `getHadoopUsers() == DEFAULT_USERS` works only because the method returns the static array in the default branch; future refactors could break default group detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/HadoopUsersConfTestHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/KerberosTestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/KerberosTestUtils.java

Purpose: Kerberos test utility for constructing principals/keytab paths and running callables under JAAS-authenticated client or server subjects.

Important APIs/types/functions: property constants for realm/client/server/keytab, getters `getRealm`, `getClientPrincipal`, `getServerPrincipal`, `getKeytabFile`, nested `KerberosConfiguration`, and methods `doAs`, `doAsClient`, `doAsServer`.

Control flow: getters read system properties with defaults. `KerberosConfiguration` builds JAAS login-module options for keytab use, ticket cache, renewal, krb5 refresh, initiator mode, and debug. `doAs` creates a subject with a Kerberos principal, logs in via `LoginContext`, executes the callable through `Subject.doAs`, unwraps privileged exceptions, and logs out in `finally`.

State and persistence: depends on keytab and ticket cache files outside the repo; mutates JAAS login session only during invocation.

Dependencies/integration: Java security/JGSS/JAAS, Hadoop `KerberosUtil`, and test Kerberos system properties.

Risks and test signals: powerful but environment-sensitive. Defaults point to `${user.home}/${user.name}.keytab`, so tests require explicit properties or local credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/KerberosTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/SysPropsForTestsLoader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/SysPropsForTestsLoader.java

Purpose: Static test-property loader for HTTPFS tests.

Important APIs/types/functions: constant `TEST_PROPERTIES_PROP`, static initializer, and no-op `init` used to trigger class loading.

Control flow: on class load it resolves the requested `test.properties` file name, searches upward from the current path for the file, loads properties if found, and sets only missing JVM system properties. If the user explicitly set `test.properties` but the file is absent, it prints an error and exits with `System.exit(-1)`. Otherwise it logs that no file exists.

State and persistence: mutates JVM system properties and reads a local properties file. No write operations.

Dependencies/integration: Java `Properties`, file traversal, and helper classes that call `init` in static blocks.

Risks and test signals: centralizes test configuration but has process-global side effects and can terminate the JVM during class loading. Search logic is somewhat complex and path-dependent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/SysPropsForTestsLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestDir.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestDir.java

Purpose: Marker annotation for tests that need an isolated local test directory.

Important APIs/types/functions: annotation `@TestDir` with runtime retention and method target.

Control flow: no executable logic. `TestDirHelper` inspects this annotation before each test and prepares a method-specific directory only when present.

State and persistence: annotation metadata only.

Dependencies/integration: Java annotation model and `HTestCase`/`TestDirHelper`.

Risks and test signals: simple infrastructure contract. Missing the annotation causes `TestDirHelper.getTestDir()` to throw, which is intentionally tested elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestDir.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestDirHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestDirHelper.java

Purpose: JUnit 5 extension that creates and exposes isolated local test directories for methods annotated with `@TestDir`.

Important APIs/types/functions: constants `TEST_DIR_PROP` and `TEST_DIR_ROOT`, static `delete`, `getTestDir`, `resetTestCaseDir`, `beforeEach`, and `afterEach`.

Control flow: static initialization loads properties, validates `test.dir` is absolute and at least four characters, appends `test-dir`, deletes/recreates the root, and stores the resolved property. Before each annotated test it creates a unique directory named from the method and an atomic counter, deletes any prior content, creates the directory, and stores it in an inheritable thread-local. After each test it clears the thread-local.

State and persistence: deletes and creates directories under the configured test root; maintains static counter and thread-local directory reference.

Dependencies/integration: JUnit extension callbacks, Java reflection, and `SysPropsForTestsLoader`.

Risks and test signals: critical infrastructure with destructive delete behavior guarded by minimum path length. It exits the JVM on invalid root configuration and can remove preexisting content under `test.dir/test-dir`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestDirHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestException.java

Purpose: Marker annotation describing an expected exception type and optional message regex for test methods.

Important APIs/types/functions: annotation elements `exception()` and `msgRegExp()` with default `.*`.

Control flow: no executable logic; `TestExceptionHelper` reads the annotation during JUnit exception handling.

State and persistence: annotation metadata only.

Dependencies/integration: Java annotation model and `TestExceptionHelper`.

Risks and test signals: lightweight compatibility layer for older test style. It must be paired with the registered helper extension to have effect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestExceptionHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestExceptionHelper.java

Purpose: JUnit 5 exception handler that implements `@TestException` expectations.

Important APIs/types/functions: `handleTestExecutionException`, `TestExecutionExceptionHandler`, and regex validation with `Pattern`.

Control flow: when a test throws, it reads the method annotation. If present, it verifies the thrown cause is an instance of the expected class and that the message matches the configured regex; otherwise it fails with descriptive assertion messages. If no annotation is present, it rethrows.

State and persistence: no external state.

Dependencies/integration: JUnit extension context and custom `TestException` annotation.

Risks and test signals: allows legacy expected-exception style. The implementation appears flawed: inside the catch it reports `ex.getMessage()` from the assertion failure rather than `cause.getMessage()` for regex mismatch, and tests that do not throw are not handled by this exception handler, so absence of an expected exception may need other lifecycle support or will not fail here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestExceptionHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestHFSTestCase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestHFSTestCase.java

Purpose: Self-tests for the HTTPFS test harness: directory, Jetty, HDFS, wait/sleep helpers, and expected-exception annotation behavior.

Important APIs/types/functions: tests for missing annotations, `testDirAnnotation`, `waitFor`, `waitForTimeOutRatio1/2`, `sleepRatio1/2`, `testHadoopFileSystem`, `MyServlet`, `testJetty`, and `testException0/1`.

Control flow: negative tests call helper getters without annotations and expect `IllegalStateException`. Directory/HDFS/Jetty tests use the relevant annotations to prove helpers are available, create/read a file in MiniDFS, and serve a simple servlet through Jetty. Timing tests validate `waitFor` and `sleep` respect wait ratios. Expected-exception tests throw runtime exceptions matching annotation requirements.

State and persistence: uses extension-provided local dirs, Jetty server, and MiniDFS. The servlet writes simple response content; HDFS test creates a file under the HDFS test dir.

Dependencies/integration: `HFSTestCase`, `TestDirHelper`, `TestJettyHelper`, `TestHdfsHelper`, `TestExceptionHelper`, Jetty servlet APIs, Hadoop `FileSystem`, and `Time`.

Risks and test signals: valuable infrastructure regression coverage. Timing assertions use fixed tolerances and may be sensitive on overloaded machines. The `sleepRatio2` test sets ratio to 1 despite its name, so it does not actually validate a ratio of 2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestHFSTestCase.java -->

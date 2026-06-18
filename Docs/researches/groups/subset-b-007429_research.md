# Research Report: subset-b-007429

Grouped research for Hadoop HDFS client tests and HttpFS implementation/configuration sources. Each section is bounded for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestRequestHedgingProxyProvider.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestRequestHedgingProxyProvider.java

Purpose: this JUnit 5 test validates `RequestHedgingProxyProvider<ClientProtocol>`, the HA client proxy provider that fans an RPC out to multiple NameNode proxies until one succeeds and then prefers the last successful proxy.

Important APIs and types: it builds HA config keys under `HdfsClientConfigKeys`, injects mock `ClientProtocol` instances through a custom `HAProxyFactory`, calls `getProxy().proxy`, `performFailover()`, `getStats()`, and `getBlockLocations()`, and checks `MultiException`, `RemoteException.unwrapRemoteException()`, `StandbyException`, `FileNotFoundException`, `ConnectException`, and `EOFException`.

Control flow: setup creates a unique nameservice with two NameNodes. Tests cover first-call hedging where one proxy is slow or failing, both-proxy failure aggregation, cached use of the winner after success, failover that removes the current proxy from the preferred set, one-proxy exhaustion, and a three-proxy rotation. File-not-found and standby cases verify that terminal active-side exceptions are not hidden by standby errors.

State and persistence: all state is in memory: mock invocation counts, provider current-used proxy state, failover-excluded proxies, and per-test configuration. The helper factory consumes proxies from an iterator in configured address order; no durable state is touched.

Dependencies and integration points: integrates HDFS HA client configuration, dynamic Java proxies/RPC invocation handlers, Hadoop `MultiException`, UGI-aware proxy creation, Mockito answers, and `SubjectInheritingThread` for the multithreaded regression.

Risks: sleeps make winner ordering timing-sensitive, and the iterator-backed factory assumes the provider creates proxies exactly once per configured address. Assertions on exception type/message exercise subtle failover semantics and can break if RPC wrapping changes.

Test signals: verifies hedged fan-out, winner stickiness, failover pruning/reselection, exception aggregation, single-proxy no-valid-proxies behavior, and HDFS-14088 where failover racing an exception path must not dereference a cleared current proxy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestRequestHedgingProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/shortcircuit/TestShortCircuitShm.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/shortcircuit/TestShortCircuitShm.java

Purpose: this test exercises `ShortCircuitShm`, the shared-memory slot table used by HDFS short-circuit reads, including creation, slot allocation, anchoring, invalidation, and cleanup.

Important APIs and types: it uses `SharedFileDescriptorFactory`, `ShortCircuitShm`, `ShortCircuitShm.ShmId`, `ShortCircuitShm.Slot`, `ExtendedBlockId`, `FileUtil.fullyDelete`, and JUnit assumptions/timeouts.

Control flow: `before()` skips tests when native shared-file-descriptor support cannot load. `testStartupShutdown()` creates a descriptor-backed shared memory segment and frees it. `testAllocateSlots()` allocates slots until `isFull()`, iterates them with `slotIterator()`, verifies non-anchorable slots reject anchors, makes each slot anchorable, adds/removes anchors, unregisters each slot, marks it invalid, and frees the segment.

State and persistence: temporary descriptor files live under `GenericTestUtils.getTestDir()` and are deleted at the end. Runtime state is the shared-memory segment, registered slot table, slot indexes, anchor flags, and valid/invalid slot flags.

Dependencies and integration points: depends on native IO shared-file-descriptor support and short-circuit block identity semantics. It directly exercises low-level shared-memory code instead of a DataNode/client integration path.

Risks: native capability and filesystem cleanup make it platform-sensitive. The test assumes a 4096-byte segment yields at least one slot and that slot iteration exposes all allocated slots.

Test signals: confirms shared memory can start and stop, allocation reaches capacity cleanly, slot indexes are sequential, anchors require `makeAnchorable()`, and unregister/invalidate/free complete without leaking temporary files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/shortcircuit/TestShortCircuitShm.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/util/TestByteArrayManager.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/util/TestByteArrayManager.java

Purpose: this test validates `ByteArrayManager`, the client-side byte-array pooling and throttling utility used to reduce allocation pressure while limiting concurrent arrays by size class.

Important APIs and types: it covers `ByteArrayManager.Counter`, `CounterMap`, `ManagerMap`, `FixedLengthManager`, `ByteArrayManager.Conf`, `ByteArrayManager.Impl`, `NewByteArrayWithoutLimit`, and helper classes `Allocator`, `Recycler`, `Runner`, and `NewByteArrayWithLimit`.

Control flow: `testCounter()` increments a resettable counter concurrently and verifies monotonic counts and reset after the configured period. `testAllocateRecycle()` checks the transition from simple allocation under `countThreshold` to pooled management over threshold, release queue sizing, blocking at `countLimit`, unblocking after release, and ignored over-release. `testByteArrayManager()` runs multiple randomized runners with different size classes, while a recycler drains arrays until all producers finish.

State and persistence: state is in memory: per-length counters, fixed-length free queues, outstanding futures, runner queues, and thread counters. There is no durable persistence; the `main()` method is a manual performance harness that measures allocation strategies.

Dependencies and integration points: integrates Hadoop client config defaults, `Time.monotonicNow()`, `SubjectInheritingThread`, `ExecutorService`, futures, and randomized concurrency from `ThreadLocalRandom`.

Risks: concurrency and timing checks can be sensitive to slow machines. The randomized runner can expose races but may be non-deterministic. The helper field `furtures` preserves an existing misspelling and is only test-local.

Test signals: verifies counter thread-safety, auto-reset, threshold-triggered manager creation, capacity blocking and notification, free-queue bounds, rounded size-class allocation, and absence of assertion errors under mixed concurrent allocate/recycle workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/util/TestByteArrayManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/util/TestECPolicyLoader.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/util/TestECPolicyLoader.java

Purpose: this test verifies XML loading and validation for `ECPolicyLoader`, which converts erasure-coding policy configuration files into `ErasureCodingPolicy` instances.

Important APIs and types: it writes XML to `POLICY_FILE`, calls `ECPolicyLoader.loadPolicy()`, and inspects `ErasureCodingPolicy`, `ECSchema`, cell size, codec name, data/parity units, and extra options.

Control flow: each test writes a complete policy XML fixture. The happy path defines two schemas and two policies. Negative tests cover an empty `<option>`, duplicate equivalent schemas, unsupported layout version, non-integer cell size, and invalid negative cell size.

State and persistence: persistent test state is a generated file under `test.build.data` or `/tmp`. The loader produces in-memory schema/policy lists. Tests overwrite the same fixture path and do not include explicit cleanup.

Dependencies and integration points: exercises the HDFS erasure-coding policy XML contract, schema de-duplication, layout-version gate, and policy validation rules shared by NameNode/client configuration.

Risks: assertions depend on exact exception text. Shared fixture path can collide if the class is run concurrently in the same build directory.

Test signals: confirms valid policies parse in order and invalid XML semantics fail with diagnostics for null option values, repeated schemas, bad layout versions, malformed cell sizes, and invalid policy definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/util/TestECPolicyLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestByteRangeInputStream.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestByteRangeInputStream.java

Purpose: this test validates `ByteRangeInputStream`, the WebHDFS input stream that opens HTTP byte-range requests lazily and reopens after seeks.

Important APIs and types: it defines `ByteRangeInputStreamImpl`, mocks `ByteRangeInputStream.URLOpener` and `HttpURLConnection`, uses `InputStreamAndFileLength`, `StreamStatus`, `Whitebox`, and checks `seek()`, `read()`, `available()`, `close()`, and opener `connect(offset, resolved)` calls.

Control flow: `testByteRange()` reads from the original URL, then from the resolved URL after seeking, verifies seek-to-current-position avoids reconnect, and checks missing `Content-Length` fails. `testPropagatedClose()` drives internal stream status so reopen-on-seek closes only the previous stream and closed streams cannot reopen. Availability tests cover known length, unknown length, read/seek position accounting, and closed-stream errors.

State and persistence: state is in-memory stream position (`startPos`, current position), resolved URL, stream status, wrapped input stream, and optional file length. No network or file persistence occurs because connections are mocked.

Dependencies and integration points: integrates WebHDFS HTTP header handling (`Content-Length`), URL resolution after redirect/open, Hadoop test whitebox utilities, and Mockito partial mocks.

Risks: because transport is mocked, the test validates stream state logic more than real HTTP client behavior. It also reads internal fields and status names, so refactors can require test updates.

Test signals: verifies lazy opening, range offsets after seek, no redundant connection on contiguous reads, propagated close semantics, missing content-length diagnostics, and `available()` behavior for known, unknown, and closed streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestByteRangeInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestOffsetUrlInputStream.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestOffsetUrlInputStream.java

Purpose: this small test verifies `WebHdfsFileSystem.removeOffsetParam(URL)`, which removes byte-range offset parameters when building follow-up/resolved URLs.

Important APIs and types: it uses `URL`, `WebHdfsFileSystem.removeOffsetParam()`, and JUnit equality assertions.

Control flow: the test feeds URLs with no query, queries without offset, offset as first/middle/last parameter, mixed-case `OFFset`, and offset as the only parameter. It asserts the resulting URL string preserves all non-offset parameters and removes dangling separators.

State and persistence: no persistent state. The only state is URL parsing and string reconstruction.

Dependencies and integration points: supports WebHDFS/byte-range stream behavior by ensuring an existing offset parameter does not conflict with a newly requested range offset.

Risks: assertions compare exact URL strings, so parameter ordering and encoding behavior are part of the contract.

Test signals: confirms case-insensitive offset removal and correct query cleanup for first, middle, last, and only parameter positions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestOffsetUrlInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestTokenAspect.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestTokenAspect.java

Purpose: this test validates `TokenAspect`, the helper that initializes, caches, selects, renews, and refreshes delegation tokens for WebHDFS-like filesystems.

Important APIs and types: `DummyFs` extends `FileSystem` and implements `DelegationTokenRenewer.Renewable` plus `TokenAspect.TokenManagementDelegator`. Tests inspect `DelegationTokenRenewer.RenewAction`, `UserGroupInformation`, token kind/service matching, `getDelegationToken()`, `setDelegationToken()`, `getRenewToken()`, and internal `dtRenewer`/`action` fields.

Control flow: initialization can emulate security enabled and call `initDelegationToken()`. Tests cover cached remote token acquisition, no-token initialization, using an existing UGI token instead of fetching remotely, propagation of remote fetch failures, and renewal failure causing the next `ensureTokenInitialized()` to fetch and install a replacement token.

State and persistence: state lives in `DummyFs.ugi` token collection and `TokenAspect` internal current token/renewer/action fields. There is no durable persistence. `DelegationTokenRenewer.renewCycle` is shortened for timing.

Dependencies and integration points: integrates Hadoop FS token contracts, UGI token lookup, token service construction via `SecurityUtil.buildTokenService()`, global delegation token renewer scheduling, Mockito spies, and whitebox inspection.

Risks: the renewal test sleeps against a global renew cycle and can be timing-sensitive. Use of whitebox internal field names couples the test to implementation details.

Test signals: verifies token caching, remote acquisition and installation, UGI token preference without renewal, fetch error propagation, renewer/action creation for remote tokens, invalid action detection after renewal failure, and refresh to a new token.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestTokenAspect.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestURLConnectionFactory.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestURLConnectionFactory.java

Purpose: this test covers `URLConnectionFactory` connection customization, SSL initialization failure logging, and SSLFactory monitor thread cleanup when an `swebhdfs` filesystem is closed.

Important APIs and types: it uses `URLConnectionFactory`, `ConnectionConfigurator`, `SSLFactory`, `KeyStoreTestUtil`, `FileSystem.get()`, `FileUtil`, and the SSL reload thread name constant `SSL_MONITORING_THREAD_NAME`.

Control flow: `testConnConfiguratior()` opens an HTTP connection and verifies the configurator sees the expected URL and stores the connection. `testSSLInitFailure()` configures an invalid hostname verifier and asserts the factory logs SSL configuration failure. `testSSLFactoryCleanup()` sets up test keystores, opens an `swebhdfs://localhost` filesystem, finds the SSL monitor thread in the root thread group, closes the filesystem, and waits for the reloader thread to stop.

State and persistence: temporary keystore/config files are created under a test path and removed before setup. Runtime state includes the connection list, captured logs, filesystem instance, and SSL monitoring thread.

Dependencies and integration points: integrates WebHDFS URL connection factory, Hadoop SSL configuration reload support, filesystem scheme registration for `swebhdfs`, and thread lifecycle cleanup on `FileSystem.close()`.

Risks: thread enumeration can be brittle if multiple SSL monitor threads exist or thread names change. Cleanup waits up to ten seconds and is timing-sensitive.

Test signals: verifies configurators are applied, SSL init failures are logged instead of fatal, and SSL reloader resources do not leak after closing the secure WebHDFS filesystem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestURLConnectionFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFSOAuth2.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFSOAuth2.java

Purpose: this integration-style test verifies that WebHDFS OAuth2 support obtains an access token and sends it as an authorization header on a WebHDFS `listStatus` call.

Important APIs and types: it uses `WebHdfsFileSystem`, `ConfCredentialBasedAccessTokenProvider`, `CredentialBasedAccessTokenProvider.OAUTH_CREDENTIAL_KEY`, OAuth config keys, `OAuth2ConnectionConfigurator.HEADER`, MockServer `ClientAndServer`, `MockServerClient`, and JSON `FileStatus` response parsing.

Control flow: `BeforeEach` starts separate MockServer instances for OAuth and WebHDFS. The OAuth server expects a POST to `/refresh` with client credentials form data and returns JSON containing `access_token`, `expires_in`, and token type. The WebHDFS mock expects a GET to `/webhdfs/v1/test1/test2` with the bearer header and returns two file statuses. The test initializes a `WebHdfsFileSystem`, calls `listStatus()`, verifies both expected requests, and checks parsed names.

State and persistence: state is confined to mock server expectations, OAuth config, the filesystem instance, and JSON response bodies. Servers bind fixed ports and are stopped in `AfterEach`.

Dependencies and integration points: integrates WebHDFS filesystem initialization, OAuth2 token provider configuration, HTTP request decoration, MockServer matching, Jackson JSON generation, and WebHDFS JSON-to-`FileStatus` conversion.

Risks: fixed ports 7552/7553 can collide on shared test hosts. Request body matching assumes exact form encoding/order used by the provider.

Test signals: confirms OAuth refresh is performed once, WebHDFS calls include the authorization header, and token-enabled `listStatus()` parses the returned file list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFSOAuth2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsContentLength.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsContentLength.java

Purpose: this socket-level test verifies WebHDFS client HTTP request headers, especially `Content-Length` and `Transfer-Encoding`, for GET/PUT/POST/DELETE operations and redirect upload flows.

Important APIs and types: it uses a raw `ServerSocket`, `FileSystem` for a `webhdfs://` URI, `FSDataOutputStream`, regex extraction of `Content-Length|Transfer-Encoding`, and single-thread executor futures that capture incoming HTTP requests.

Control flow: setup binds a local socket, constructs redirect and error HTTP responses, and opens a WebHDFS filesystem. Each test schedules one or more accept/read tasks, invokes a filesystem operation expected to fail, and inspects the captured request headers. GET/status/open/delete should not send content length; mkdirs and concat send `Content-Length: 0`; redirected create/append first send zero-length control requests then stream data with chunked transfer encoding.

State and persistence: state is local socket binding, captured request strings, configured path, and executor. No HDFS state is persisted because the fake server always errors or redirects.

Dependencies and integration points: integrates Java HTTP client behavior, WebHDFS operation mapping, redirect handling, and upload streaming semantics at the raw HTTP wire level.

Risks: Java HTTP implementation can split chunked headers/body, so the helper consumes the whole socket input to avoid client hangs. The class-level timeout bounds network stalls.

Test signals: verifies correct absence/presence of content length, zero-length control requests for mutating non-upload operations, and chunked transfer for redirected create/append data streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsContentLength.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/oauth2/TestAccessTokenTimer.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/oauth2/TestAccessTokenTimer.java

Purpose: this test validates `AccessTokenTimer`, the small OAuth2 helper that converts token expiry values into a next-refresh timestamp and decides whether a token should be refreshed.

Important APIs and types: it uses `AccessTokenTimer`, injectable Hadoop `Timer`, `setExpiresIn()`, `setExpiresInMSSinceEpoch()`, `getNextRefreshMSSinceEpoch()`, and `shouldRefresh()`.

Control flow: one test fixes timer `now()` at 5 ms, sets `expires_in` to 3 seconds, and verifies the next refresh timestamp is 3005 ms and already considered refreshable under the timer policy. The second sets an absolute expiry and uses sequential mocked `now()` values to verify false before expiry and true at/after expiry.

State and persistence: state is only the timer's stored next-refresh epoch and mocked current time. No persistence exists.

Dependencies and integration points: supports OAuth2 access token providers that need to avoid unnecessary refresh calls while refreshing after expiry.

Risks: exact millisecond arithmetic is part of the contract; policy changes such as refresh skew would require updating tests.

Test signals: confirms seconds-to-milliseconds conversion, absolute epoch handling, and `Timer.now()`-based refresh decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/oauth2/TestAccessTokenTimer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/oauth2/TestClientCredentialTimeBasedTokenRefresher.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/oauth2/TestClientCredentialTimeBasedTokenRefresher.java

Purpose: this test verifies client-credentials OAuth2 refresh behavior for `ConfCredentialBasedAccessTokenProvider`.

Important APIs and types: it builds `Configuration` with credential, `ACCESS_TOKEN_PROVIDER_KEY`, `OAUTH_CLIENT_ID_KEY`, and `OAUTH_REFRESH_URL_KEY`; uses `AccessTokenProvider.getAccessToken()`, `Timer`, MockServer, `ParameterBody`, and OAuth2 constants such as `client_secret`, `grant_type=client_credentials`, and `access_token`.

Control flow: the test selects an available port, configures the token as expired, starts MockServer, expects a POST to `/refresh` with ordered form parameters, returns JSON token metadata, then asserts `getAccessToken()` returns the new token and verifies the expected request occurred exactly once.

State and persistence: state is test configuration, mocked time, MockServer expectation/response, and provider's cached access token/expiry. No durable state is written.

Dependencies and integration points: integrates the OAuth2 provider config contract, OkHttp/form parameter generation, Jackson JSON response generation, and MockServer request verification.

Risks: request body matching is order-sensitive because OkHttp does not sort parameters; the test compensates with `ParameterBody.params`. Server cleanup is manual and must run to free the chosen port.

Test signals: confirms expired client-credential providers POST the correct grant request to the configured refresh URL and parse the returned access token.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/oauth2/TestClientCredentialTimeBasedTokenRefresher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/oauth2/TestRefreshTokenTimeBasedTokenRefresher.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/oauth2/TestRefreshTokenTimeBasedTokenRefresher.java

Purpose: this test verifies refresh-token OAuth2 behavior for `ConfRefreshTokenBasedAccessTokenProvider`.

Important APIs and types: it configures `OAUTH_REFRESH_TOKEN_KEY`, `OAUTH_REFRESH_TOKEN_EXPIRES_KEY`, `OAUTH_CLIENT_ID_KEY`, and `OAUTH_REFRESH_URL_KEY`; uses `AccessTokenProvider`, `Timer`, MockServer form matching, and OAuth2 constants for `grant_type=refresh_token`, `refresh_token`, `client_id`, `token_type=bearer`, and `access_token`.

Control flow: with mocked current time past the configured expiry, the provider calls the refresh endpoint. MockServer expects a POST with client id, grant type, and refresh token parameters, returns JSON token metadata, and the assertion checks the provider returns the new access token.

State and persistence: runtime state is the configuration, provider cache, mocked time, and mock HTTP server expectation. No files are persisted.

Dependencies and integration points: validates the refresh-token provider's HTTP form contract and JSON parsing path used by WebHDFS OAuth2 clients.

Risks: the test uses fixed port 7552, which can collide. Parameter ordering and exact body matching are part of the expected behavior.

Test signals: confirms expired refresh-token credentials trigger exactly one correctly formed refresh request and the response access token is exposed to callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/oauth2/TestRefreshTokenTimeBasedTokenRefresher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/dev-support/findbugsExcludeFile.xml -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/dev-support/findbugsExcludeFile.xml

Purpose: this SpotBugs/FindBugs exclusion file suppresses known warnings for the `hadoop-hdfs-httpfs` module.

Important APIs and types: the XML root is `FindBugsFilter`; each `Match` identifies a class plus method or field and a `Bug pattern`.

Control flow: build tooling reads this file through the HttpFS module's SpotBugs Maven plugin configuration. It suppresses `UL_UNRELEASED_LOCK` for `InstrumentationService.getToAdd`, `ST_WRITE_TO_STATIC_FROM_INSTANCE_METHOD` for `HttpFSServerWebApp.destroy`, `IS2_INCONSISTENT_SYNC` for `ServerWebApp.authority`, and `NP_NULL_ON_SOME_PATH_FROM_RETURN_VALUE` for `FileSystemAccessService.closeFileSystem`.

State and persistence: persistent state is the checked-in filter. It does not execute at runtime, but it affects static-analysis results in builds.

Dependencies and integration points: tied to class/member names in HttpFS/lib server code and referenced by `hadoop-hdfs-httpfs/pom.xml` alongside the global Hadoop exclusion file.

Risks: suppressions can hide real regressions if code changes under the same class/member names. Renames make entries stale and reduce static-analysis signal.

Test signals: build/quality signal is a cleaner SpotBugs run for warnings the project has accepted or deemed false positives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/pom.xml -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/pom.xml

Purpose: this Maven POM defines the `hadoop-hdfs-httpfs` module, its compile/test dependencies, resource filtering, test execution settings, static-analysis exclusions, and distribution profile.

Important APIs and types: artifact `org.apache.hadoop:hadoop-hdfs-httpfs:3.6.0-SNAPSHOT` inherits from `hadoop-project`; compile dependencies include Hadoop auth/common/hdfs, Jersey, servlet API, Jetty, json-simple, shaded Guava, reload4j/slf4j, and provided `hadoop-hdfs-client`; test dependencies include Hadoop test jars, Mockito inline, BouncyCastle, Kotlin stdlib, and JUnit 5.

Control flow: resources filter `httpfs.properties` separately from other resources; test resources filter `krb5.conf`. Surefire runs single-threaded with timeout/listener settings and excludes Kerberos tests by default. Antrun copies the webapp into test classes and generates site HTML from `httpfs-default.xml`. Javadoc groups HttpFS API packages. SpotBugs uses the module and global exclusion files. Profiles enable Kerberos tests or assemble the HttpFS distribution.

State and persistence: persistent build metadata includes source repository/revision placeholders, build timestamp, Kerberos realm, exclusion properties, and resource filtering rules. Build outputs include copied webapp test resources, generated site HTML, test classes, and optional distribution archives.

Dependencies and integration points: integrates HttpFS with Hadoop web/auth/security stacks, Jetty/Jersey servlet runtime, HDFS clients, Maven Surefire, RAT, Javadoc, Antrun, SpotBugs, and Hadoop assembly descriptors.

Risks: explicit dependency exclusions avoid servlet/Jetty conflicts but can become stale as parent dependencies evolve. Default Kerberos exclusion means secure-path tests only run under the `testKerberos` profile.

Test signals: enforces JUnit timeout listener, single-thread test execution, Kerberos profile isolation, SpotBugs suppression scope, RAT exclusions, and generated webapp resources needed by HttpFS tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/conf/httpfs-env.sh -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/conf/httpfs-env.sh

Purpose: this shell configuration template documents HttpFS-specific environment variables layered after `hadoop-env.sh`.

Important APIs and types: commented exports cover `HTTPFS_CONFIG`, `HTTPFS_LOG`, `HTTPFS_TEMP`, `HTTPFS_HTTP_PORT`, `HTTPFS_MAX_THREADS`, `HTTPFS_HTTP_HOSTNAME`, `HTTPFS_MAX_HTTP_HEADER_SIZE`, `HTTPFS_SSL_ENABLED`, `HTTPFS_SSL_KEYSTORE_FILE`, and `HTTPFS_SSL_KEYSTORE_PASS`.

Control flow: there is no active executable logic beyond the shebang and comments. Operators uncomment and set variables to influence the HttpFS daemon launch scripts.

State and persistence: persistent state is a deployable config template. Runtime state arises only when administrators export variables from it.

Dependencies and integration points: integrates with Hadoop distribution startup scripts and inherited `hadoop-env.sh` values such as `HADOOP_CONF_DIR`, `HADOOP_LOG_DIR`, and `HADOOP_HDFS_HOME`.

Risks: defaults are commented, so deployments depend on script defaults elsewhere. Keystore password examples must be replaced for real SSL deployments.

Test signals: no direct tests; correctness is signaled by startup scripts accepting these variables and by operational HttpFS binding/log/temp/SSL behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/conf/httpfs-env.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/conf/httpfs-site.xml -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/conf/httpfs-site.xml

Purpose: this XML configuration file is the site-specific override point for HttpFS.

Important APIs and types: it contains a standard Hadoop `<configuration>` root and no `<property>` entries.

Control flow: Hadoop configuration loading merges this file with HttpFS defaults and other Hadoop config resources. Because it is empty, it changes no settings by itself.

State and persistence: persistent state is an empty site config template intended for operators to customize in deployments.

Dependencies and integration points: consumed by HttpFS server configuration loading and compatible with the normal Hadoop XML configuration schema.

Risks: an empty file is safe, but any deployment-specific behavior must come from defaults, environment variables, or administrator-added properties.

Test signals: no direct runtime test signal; XML well-formedness and packaging presence are the main build/deployment signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/conf/httpfs-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/client/HttpFSFileSystem.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/client/HttpFSFileSystem.java

Purpose: `HttpFSFileSystem` is the HttpFS client-side `FileSystem` implementation for `webhdfs` URIs, translating Hadoop filesystem operations into authenticated HttpFS/WebHDFS-style HTTP requests and JSON response parsing.

Important APIs and types: it extends `FileSystem` and implements `DelegationTokenRenewer.Renewable`. Public surface includes core FS operations (`open`, `create`, `append`, `truncate`, `concat`, `rename`, `delete`, `listStatus`, `listStatusBatch`, `mkdirs`, `getFileStatus`, `getHomeDirectory`, `getTrashRoot`, metadata setters), ACLs, xattrs, storage policies, snapshots, erasure coding, block locations, delegation token methods, `hasPathCapability`, `getServerDefaults`, `access`, `getStatus`, and trash roots. The `Operation` enum maps each HttpFS op to GET/PUT/POST/DELETE.

Control flow: `initialize()` records the scheme/authority URI, selects a `DelegationTokenAuthenticator` class, and builds `DelegationTokenAuthenticatedURL`. `getConnection()` qualifies paths, delegates URL construction to `HttpFSUtils`, runs connection creation as the current UGI, injects auth, sets the HTTP method, and enables output for POST/PUT. Most operations build parameter maps with `op`, call `getConnection()`, validate expected status via `HttpExceptionUtils`, and parse JSON through `HttpFSUtils` or `JsonUtilClient`. `create()` and `append()` first require a 307 redirect, then open the redirect target with `Content-Type: application/octet-stream` and validate final status on stream close.

State and persistence: persistent external state is HDFS state mutated through the remote HttpFS server. Local state includes `authURL`, `authToken`, canonical `uri`, lazy `workingDir`, `realUser`, and inherited statistics. No local filesystem data is persisted. Returned output streams hold the redirect connection until close to validate server response.

Dependencies and integration points: integrates Hadoop FS abstractions, UGI/SPNEGO/delegation-token auth, HttpFS URL layout, JSON-simple and Jackson parsing, HDFS `JsonUtilClient`, ACL/xattr/storage/snapshot/EC protocols, and HTTP status/error utilities.

Risks: seek/positioned reads are unsupported in the nested input stream. Uploads depend on a two-step 307 redirect and a `Location` header. Several methods fall back to superclass behavior on IO errors (`getTrashRoot`, `getTrashRoots`), while most propagate. Token renew/cancel ignores the token parameter and `getRenewToken`/`setDelegationToken` are TODO stubs, limiting renewer integration.

Test signals: covered indirectly by HttpFS/WebHDFS client tests for content length, OAuth, JSON conversion, xattrs, storage policies, snapshots, EC, and block locations. Important behavioral signals are exact op/method mapping, HTTP status validation, JSON field compatibility, upload content type, capability declarations, and fallback behavior for trash roots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/client/HttpFSFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/client/HttpFSUtils.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/client/HttpFSUtils.java

Purpose: `HttpFSUtils` provides private client utilities for constructing HttpFS operation URLs and parsing JSON responses.

Important APIs and types: constants define service prefix `/webhdfs`, version `/v1`, and empty byte array. `createURL(Path, Map)` and `createURL(Path, Map, Map<String,List<String>>)` build HTTP/HTTPS URLs. `jsonParse(HttpURLConnection)` validates JSON content type and parses response streams with JSON-simple.

Control flow: `createURL()` maps `webhdfs` to `http` and `swebhdfs` to `https`, appends `/webhdfs/v1` plus the path, then URL-encodes single-valued and multi-valued query parameters. Invalid schemes throw `IllegalArgumentException`. `jsonParse()` accepts absent content type, rejects non-compatible media types, and wraps JSON parse errors in `IOException`.

State and persistence: stateless utility methods; no persistence or cached state.

Dependencies and integration points: used by `HttpFSFileSystem` for every operation URL and JSON parse path. Integrates `Path`, `HttpURLConnection`, `URLEncoder`, JAX-RS `MediaType`, JSON-simple parser, and UTF-8 stream decoding.

Risks: query parameter order follows map iteration order, so callers should use deterministic maps if exact URL order matters. It uses historical `"UTF8"` encoding labels in some calls. Missing content type is permitted for compatibility, which can defer bad response detection to JSON parsing.

Test signals: expected behavior is visible through HttpFS/WebHDFS request tests and JSON parsing failures: correct scheme translation, service prefix insertion, multi-valued xattr params, content-type compatibility, and parse-error wrapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/client/HttpFSUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/client/HttpsFSFileSystem.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/client/HttpsFSFileSystem.java

Purpose: `HttpsFSFileSystem` is the secure HttpFS client implementation for `swebhdfs` URIs.

Important APIs and types: it extends `HttpFSFileSystem`, defines `SCHEME = "swebhdfs"`, and overrides only `getScheme()`.

Control flow: all filesystem behavior is inherited from `HttpFSFileSystem`; the changed scheme causes `HttpFSUtils.createURL()` to translate requests to `https`.

State and persistence: no additional state beyond the base class. Remote HDFS mutations and authentication state are handled by `HttpFSFileSystem`.

Dependencies and integration points: integrates secure HttpFS scheme registration with the shared HttpFS client implementation and SSL-enabled connection handling.

Risks: because only the scheme changes, secure behavior depends on configuration and lower-level HTTPS/SSL setup rather than class-specific logic.

Test signals: `TestURLConnectionFactory` exercises `swebhdfs://` initialization and SSLFactory monitor cleanup, while inherited HttpFS behavior should match `webhdfs` except for transport scheme.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/client/HttpsFSFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/CheckUploadContentTypeFilter.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/CheckUploadContentTypeFilter.java

Purpose: this servlet filter enforces `application/octet-stream` content type for HttpFS data upload requests.

Important APIs and types: it implements `javax.servlet.Filter`, uses `HttpServletRequest`, `HttpServletResponse`, `FilterChain`, `HttpFSFileSystem.Operation`, `HttpFSFileSystem.OP_PARAM`, `HttpFSFileSystem.UPLOAD_CONTENT_TYPE`, `HttpFSParametersProvider.DataParam.NAME`, and `StringUtils.toUpperCase()`.

Control flow: a static set marks upload operations `APPEND` and `CREATE`. `doFilter()` allows all requests by default, then for PUT/POST requests with an upload operation and `data=true`, compares request content type case-insensitively to `application/octet-stream`. Valid requests continue down the chain; invalid upload requests receive HTTP 400 with a specific message. `init()` and `destroy()` are no-ops.

State and persistence: persistent state is only the static upload-operation set. Runtime state is per-request method/op/data/content-type evaluation. No durable state is touched.

Dependencies and integration points: installed in the HttpFS server servlet chain to guard the second phase of create/append uploads that the client opens after redirect.

Risks: enforcement depends on the `op` and `data` parameters being present and correctly named. Requests with missing `data=true` bypass content-type checking, matching the distinction between control and upload phases.

Test signals: expected signal is server rejection of create/append data requests without the exact upload content type, while non-upload PUT/POST and control-phase requests pass through.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/CheckUploadContentTypeFilter.java -->

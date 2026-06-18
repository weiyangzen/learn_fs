# subset-b-007565 grouped source research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsTokens.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsTokens.java

## Purpose
`TestWebHdfsTokens` validates WebHDFS and SWebHDFS delegation-token behavior across simple, Kerberos-secured, token-only, and expired-token flows. It focuses on when `WebHdfsFileSystem.toUrl` should fetch tokens, which HTTP operations require Kerberos authentication instead of a delegation token, and whether token service/kind values returned by NameNode JSON survive conversion into Hadoop `Token` objects.

## Important APIs, types, and functions
- `initEnv()` sets Kerberos mode on the shared `conf` and installs a testing login user, giving mock WebHDFS instances a secure-client context without starting a cluster.
- `initSecureConf(Configuration)` creates a `MiniKdc`, principal/keytab files, SPNEGO HTTP authentication settings, HDFS Kerberos principals, block tokens, HTTPS keystore resources, and HTTP/HTTPS listener addresses for a secure `MiniDFSCluster`.
- `spyWebhdfsInSecureSetup()` initializes a `WebHdfsFileSystem` against `webhdfs://127.0.0.1:0` and wraps it with Mockito.
- `checkNoTokenForOperation(HttpOpParam.Op)` asserts that token management operations do not recursively fetch or install delegation tokens.
- `validateLazyTokenFetch(UserGroupInformation, Configuration)` is the core integration scenario. It creates WebHDFS clients as a Kerberos UGI, performs token ops and ordinary file ops, cancels/renews tokens, checks replacement of expired tokens, closes file systems, and verifies interaction counts on token methods.
- `getTokenOwner(Token<?>)` clones a WebHDFS token, changes its kind to `HDFS_DELEGATION_KIND`, decodes the identifier, and returns the token owner.

## Control flow
The light tests use a spied `WebHdfsFileSystem` to call `toUrl` for different operation classes and verify token-fetch call counts. The operation-class tests iterate all `GetOpParam`, `PutOpParam`, `PostOpParam`, and `DeleteOpParam` values and assert only delegation-token management operations require auth. `testLazyTokenFetchForWebhdfs` builds a real secure MiniDFSCluster once, logs in via keytab, and runs the same lazy-token lifecycle against both `swebhdfs` and `webhdfs` URIs. `testSetTokenServiceAndKind` starts a mostly simple cluster but enables delegation-token use, injects a custom `URLConnectionFactory` that appends `service=foo&kind=bar`, and verifies both `getDelegationToken` and a lower-level `FsPathResponseRunner` decode token kind/service correctly.

## State and persistence behavior
The class owns static MiniKdc state, keytab/keystore directories, principal strings, and shared `conf`. The secure flow writes temporary KDC/keytab/SSL files under `GenericTestUtils.getTestDir` and classpath SSL config directories, then removes them in `destroy()`. `validateLazyTokenFetch` mutates the active UGI token set and WebHDFS internal renew token; it explicitly resets UGI after the secure cluster test to avoid leaking Kerberos mode into later tests.

## Dependencies and integration points
This test integrates `MiniKdc`, `MiniDFSCluster`, Hadoop HTTP authentication filters, `KeyStoreTestUtil`, `WebHdfsFileSystem`, `JsonUtilClient`, WebHDFS resource parameters, and HDFS delegation-token identifiers. Mockito is used to assert client-internal call order without replacing server-side token logic. It depends on HDFS configs for HTTPS, Kerberos principals, block access tokens, data-transfer protection, and forced NameNode delegation-token use.

## Risks and edge cases
The secure setup is expensive and sensitive to local host naming, Windows localhost behavior, keystore cleanup, and shared static UGI state. The tests intentionally use `127.0.0.1:0` for spy-only URL generation, so those branches do not validate real connectivity. `testSetTokenServiceAndKind` relies on appending query parameters through a custom connection factory; URL or JSON response changes could break the intended coverage. Token replacement assertions are interaction-count-sensitive and may fail if WebHDFS retry internals change while preserving behavior.

## Test signals
Strong signals include coverage for no-recursive-token-fetch on token operations, lazy token acquisition on first non-token op, reuse of renew tokens, expired-token replacement, UGI-provided token reuse/replacement rules, close-time token cancellation semantics, WebHDFS/SWebHDFS parity, and token kind/service parsing. Failures typically indicate regressions in WebHDFS auth query construction, delegation-token caching, expired-token recovery, or secure MiniDFSCluster setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsTokens.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsUrl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsUrl.java

## Purpose
`TestWebHdfsUrl` verifies WebHDFS URL construction, query-parameter selection, and path encoding behavior for simple users, proxy users, secure delegation-token clients, batched listings, access checks, and special-character filenames.

## Important APIs, types, and functions
- `resetUGI()` restores UGI to a fresh simple configuration before each test.
- `getWebHdfsFileSystem(UserGroupInformation, Configuration)` installs a synthetic WebHDFS delegation token in secure mode and returns a `WebHdfsFileSystem` for `webhdfs://127.0.0.1:0`.
- `checkQueryParams(String[], URL)` sorts expected and actual query fragments to assert exact parameter sets independent of order.
- Tests call `WebHdfsFileSystem.toUrl` with `GetOpParam`, `PutOpParam`, `TokenArgumentParam`, `DelegationParam`, `DoAsParam`, `UserParam`, `FsActionParam`, and `StartAfterParam`.

## Control flow
The first group builds URLs without a real cluster and checks that encoded path components and auth parameters round-trip correctly. Simple mode should include `user.name`; simple proxy mode should include real user plus `doas`; secure mode should avoid `user.name`, use delegation tokens for ordinary operations, and include `doas` for proxy token-management operations. Later tests start a `MiniDFSCluster` through `WebHdfsTestUtil.createConf()`, create files with punctuation-heavy names, then verify `getFileStatus` and `listFiles` preserve path names. The final semicolon/plus/percent regression creates files via WebHDFS and validates their names through the direct DFS client.

## State and persistence behavior
Most tests mutate only process UGI state and generated URL objects. The synthetic secure token path creates a `DelegationTokenSecretManager`, starts its threads, and adds a token to the supplied UGI. Cluster-backed tests persist files under MiniDFSCluster namespaces and shut the cluster down in `finally` or try-with-resources.

## Dependencies and integration points
This class integrates WebHDFS resource parameter classes, `SecurityUtil`, `UserGroupInformation`, `DelegationTokenSecretManager`, `FSNamesystem` mocks, `NetUtils`, `DFSTestUtil`, direct `DistributedFileSystem`, and the `WebHdfsTestUtil` helper. It tests a client/server contract between URL encoding in WebHDFS and path decoding in NameNode/DataNode WebHDFS handlers.

## Risks and edge cases
The query tests use an endpoint with port `0` and synthetic tokens, so they validate client URL construction rather than live server acceptance. Path tests are sensitive to encoding rules for `%`, `+`, semicolon, ampersand, comma, braces, quotes, and legacy percent treatment. The helper starts a token secret-manager thread without explicit shutdown in this file, which is acceptable for short tests but is a lifecycle risk.

## Test signals
Useful signals include exact URL query contents for auth/proxy/token cases, preservation of already percent-encoded path text, `CHECKACCESS` action encoding, `LISTSTATUS_BATCH` `startafter` encoding, and MiniDFSCluster proof that special-character paths can be created, listed, and read back without name corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsUrl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsWithAuthenticationFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsWithAuthenticationFilter.java

## Purpose
This test verifies that WebHDFS requests pass through custom HTTP filters configured on the NameNode HTTP server, and that a filter rejection is surfaced to the WebHDFS client as an `IOException`.

## Important APIs, types, and functions
- `CustomizedFilter` implements `javax.servlet.Filter` and either calls `chain.doFilter` or sends HTTP 403 based on the static `authorized` flag.
- `CustomizedFilter.Initializer` extends `FilterInitializer` and registers the filter in the `FilterContainer`.
- `setUp()` configures `HttpServer2.FILTER_INITIALIZER_PROPERTY`, starts a single-node `MiniDFSCluster`, and opens a `webhdfs://host:port` `FileSystem`.
- `testWebHdfsAuthFilter()` toggles `authorized` and calls `fs.getFileStatus("/")`.

## Control flow
The class-level setup starts one cluster and one WebHDFS client. The test first sets `authorized=false`, expects `getFileStatus` to fail, then sets `authorized=true` and expects the same request to succeed. Tear-down closes the file system and cluster.

## State and persistence behavior
The only test control state is static boolean `authorized`; cluster and file system are static per class. No files are created. The cluster stores standard MiniDFS metadata and is shut down after all tests.

## Dependencies and integration points
The test connects HDFS `MiniDFSCluster`, `HttpServer2`, Hadoop `FilterInitializer`, servlet filters, WebHDFS `FileSystem`, and `NetUtils` host:port formatting. It exercises the integration point where NameNode HTTP filters wrap WebHDFS servlet handling.

## Risks and edge cases
The shared static `authorized` flag makes the filter intentionally global, so parallel execution of this exact class would be unsafe. The test validates only a read-only metadata op; redirecting write flows through DataNode filters are covered elsewhere. It catches any `IOException` for the denied request and does not assert the 403 status text.

## Test signals
Passing means a configured custom filter is invoked for WebHDFS and can both block and allow a request. Failure can indicate filter initializer wiring, NameNode HTTP configuration, WebHDFS error propagation, or MiniDFS HTTP address setup regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsWithAuthenticationFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsWithMultipleNameNodes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsWithMultipleNameNodes.java

## Purpose
This test validates WebHDFS create, read, append, and redirect behavior in a federated MiniDFSCluster with multiple independent NameNodes.

## Important APIs, types, and functions
- `setupCluster(int nNameNodes, int nDataNodes)` builds a simple federated topology, waits for activation, and opens one `WebHdfsFileSystem` per NameNode HTTP address.
- `createString` and `createStrings` produce NameNode-specific content with distinct lengths.
- `testRedirect()` writes, reads, appends, and rereads the same path independently through every WebHDFS client.

## Control flow
Class setup raises log levels and starts a four-NameNode, three-DataNode federated cluster. The test loops across `webhdfs[]`, creating `/testRedirect/file` in each namespace with unique content, checks file length for each namespace, reads back exact bytes, appends unique content, then verifies final length and concatenated content in each namespace.

## State and persistence behavior
The test persists the same logical path in each federated namespace. Since each `WebHdfsFileSystem` points to a different NameNode, the content is intentionally different by namespace. Static cluster state is destroyed in `shutdownCluster()`.

## Dependencies and integration points
It integrates `MiniDFSNNTopology.simpleFederatedTopology`, NameNode WebHDFS methods, `FSDataInputStream`, `FSDataOutputStream`, and WebHDFS client redirection from NameNode to DataNode for create/read/append operations.

## Risks and edge cases
The test assumes append is available and that a shared DataNode set can serve all federated namespaces. It validates per-NameNode isolation by content differences but does not explicitly assert block-pool identity. Static cluster and clients are class-scoped, so a setup failure aborts all coverage.

## Test signals
Passing demonstrates that WebHDFS can address multiple NameNodes by HTTP authority, correctly redirect data operations, preserve namespace isolation, and append/read bytes through each federated endpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsWithMultipleNameNodes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsWithRestCsrfPreventionFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsWithRestCsrfPreventionFilter.java

## Purpose
This parameterized test verifies WebHDFS behavior when REST CSRF prevention is independently enabled or disabled on NameNode, DataNode, and client. It distinguishes operations handled only by the NameNode from operations redirected to DataNodes.

## Important APIs, types, and functions
- `data()` returns eight boolean combinations for NameNode CSRF, DataNode CSRF, and client CSRF settings.
- `before()` builds a MiniDFSCluster with NameNode CSRF settings, starts a DataNode with its own CSRF setting and `RestCsrfPreventionFilterHandler`, opens direct DFS and WebHDFS clients.
- `testCreate`, `testDelete`, `testGetFileStatus`, and `testTruncate` encode the expected matrix for PUT, DELETE, GET, and POST operations.

## Control flow
Each parameterized test calls `initTestWebHdfsWithRestCsrfPreventionFilter`, which stores booleans and starts a fresh cluster. Create is expected to fail without client CSRF support if either NameNode or DataNode has the filter because it performs a NameNode-to-DataNode redirected PUT. Delete and truncate fail only when NameNode CSRF is enabled and the client is not configured because they are metadata operations. Get file status always succeeds because GET is not protected by the CSRF filter.

## State and persistence behavior
Each parameter set starts and tears down a MiniDFSCluster. Tests create `/file` where needed through the direct file system before delete/truncate cases. `after()` closes both file systems and shuts down the cluster.

## Dependencies and integration points
The test integrates WebHDFS client CSRF header configuration, NameNode HTTP CSRF filter configuration, DataNode Netty/HTTP filter handler configuration, `CommonPathCapabilities.FS_TRUNCATE`, and `DFSTestUtil.createFile`.

## Risks and edge cases
The browser user-agent regex is set to `.*` so the filter always applies; production behavior may depend on user-agent matching. Assertions check for `"Missing Required Header"` in `IOException` messages, making them sensitive to server error text. The matrix intentionally uses only one DataNode and one file path per case.

## Test signals
Passing confirms client CSRF headers are emitted when enabled, unsafe WebHDFS methods are rejected by protected servers when missing headers, GET remains allowed, and DataNode protection affects redirected create but not NameNode-only metadata operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsWithRestCsrfPreventionFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/WebHdfsTestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/WebHdfsTestUtil.java

## Purpose
`WebHdfsTestUtil` is a small test helper for constructing WebHDFS/SWebHDFS clients, logging generated URLs, opening HTTP connections, parsing JSON responses, and converting WebHDFS delegation-token JSON into Hadoop token objects.

## Important APIs, types, and functions
- `createConf()` returns a new base `Configuration`.
- `getWebHdfsFileSystem(Configuration, String)` builds a URI from `DFS_NAMENODE_HTTP_ADDRESS_KEY` or `DFS_NAMENODE_HTTPS_ADDRESS_KEY` depending on scheme and returns a `WebHdfsFileSystem`.
- `getWebHdfsFileSystemAs(UserGroupInformation, Configuration[, String])` runs client construction inside a UGI `doAs`.
- `toUrl(WebHdfsFileSystem, HttpOpParam.Op, Path, Param...)` delegates to `webhdfs.toUrl` and logs the resulting URL.
- `openConnection`, `sendRequest`, `getAndParseResponse`, and `convertJsonToDelegationToken` wrap lower-level WebHDFS HTTP/JSON APIs.

## Control flow
The helper is stateless. Most methods are single-step factories or adapters: construct URI, call `FileSystem.get`, call `toUrl`, create a default `URLConnectionFactory`, connect, parse JSON, or convert token JSON.

## State and persistence behavior
No persistent state is stored except the static logger. `openConnection` creates a new connection factory with 60-second connect/read timeouts for each call.

## Dependencies and integration points
It sits between WebHDFS tests and `WebHdfsFileSystem`, `URLConnectionFactory`, `JsonUtilClient`, UGI, HDFS config keys, and WebHDFS resource parameter classes.

## Risks and edge cases
The overload `getWebHdfsFileSystemAs(ugi, conf, scheme)` ignores its `scheme` argument and always calls `getWebHdfsFileSystem(conf, WEBHDFS_SCHEME)`. That can mask intended SWebHDFS coverage if callers rely on the overload. `createConf()` is deliberately minimal and does not set NameNode addresses; callers must provide them.

## Test signals
The file itself contains no tests, but downstream tests use it to signal URL construction, live WebHDFS access, HTTP response parsing, and delegation-token JSON conversion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/WebHdfsTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/resources/TestParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/resources/TestParam.java

## Purpose
`TestParam` validates parsing, defaulting, validation bounds, string encoding, and configurable regex behavior for WebHDFS REST parameter classes.

## Important APIs, types, and functions
The test covers scalar params such as `AccessTimeParam`, `ModificationTimeParam`, `BlockSizeParam`, `BufferSizeParam`, `ReplicationParam`, `OverwriteParam`, `RecursiveParam`, quota params, storage policy/type, and EC policy. It covers security and metadata params such as `UserParam`, `AclPermissionParam`, `FsActionParam`, XAttr name/value/encoding/set-flag params, snapshot names, rename options, concatenation source paths, and HTTP op params. `Param.toSortedString` is checked for URI escaping and stable sorted output.

## Control flow
Each JUnit test instantiates one or more parameter objects with default, valid, and invalid values. Invalid values are expected to throw `IllegalArgumentException` or to be caught through explicit `fail()` blocks. Regex override tests save the current domain object, install a new pattern, validate previously invalid users/ACLs, and restore the original domain in a `finally` block for ACLs.

## State and persistence behavior
Most tests are pure object parsing. `UserParam.setUserPattern` and `AclPermissionParam.setAclPermissionPattern` mutate static validation domains; the ACL test restores in `finally`, while the user-pattern test explicitly resets after assertions. No file-system state is created.

## Dependencies and integration points
The class integrates WebHDFS resource param classes with `Configuration`, `DFSConfigKeys`, `CommonConfigurationKeysPublic`, `FsPermission`, `AclEntry`, `XAttrCodec`, `XAttrSetFlag`, `Options.Rename`, `StorageType`, and `StringUtils`.

## Risks and edge cases
This file is a broad regression net for REST API surface syntax. It is sensitive to default HDFS block size, replication, and buffer-size configuration defaults. Static regex mutation can leak to other tests if a future assertion aborts before reset in the user-pattern test. Some invalid-value tests use try/catch rather than `assertThrows`, so a wrong exception type may not always be distinguished.

## Test signals
Passing confirms WebHDFS params reject malformed octal permissions, invalid booleans, bad ACL grammar, invalid FsAction strings, unknown HTTP ops, bad user names under default policy, and incorrectly encoded query strings. It also confirms defaults resolve from configuration where appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/resources/TestParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/metrics2/sink/TestRollingFileSystemSinkWithHdfs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/metrics2/sink/TestRollingFileSystemSinkWithHdfs.java

## Purpose
This class tests `RollingFileSystemSink` against a live non-secure HDFS MiniDFSCluster, covering writes, append/overwrite behavior, error handling when HDFS disappears, flush-thread behavior, and initialization when HDFS is unavailable.

## Important APIs, types, and functions
- `setupHdfs()` starts a four-DataNode cluster and clears `RollingFileSystemSink.hasFlushed`.
- Tests use inherited helpers from `RollingFileSystemSinkTestBase`: `initMetricsSystem`, `doWriteTest`, `doAppendTest`, `assertMetricsContents`, `assertExtraContents`, `findMostRecentLogFile`, and `getLogFilename`.
- `MockSink.errored` and `MockSink.initialized` capture expected sink error behavior.

## Control flow
Basic write/append tests build an `hdfs://namenode/tmp` path, initialize a metrics system, publish metrics through inherited helpers, and assert file contents. Failure tests initialize the sink, optionally publish once, shut down HDFS, then publish or stop the metrics system and assert whether errors are reported according to ignore-errors mode. `testFlushThread` forces the sink flusher thread, publishes twice, waits up to 10 seconds for `hasFlushed`, then checks the current log file length in HDFS.

## State and persistence behavior
Each test gets a fresh MiniDFSCluster and writes metrics files under `/tmp` in HDFS. The metrics system maintains sink state and background flushing. Static test flags on `RollingFileSystemSink` and `MockSink` are mutated and reset where needed. Cluster shutdown is per test.

## Dependencies and integration points
The test integrates Hadoop metrics2 `MetricsSystem`, `RollingFileSystemSink`, HDFS append semantics, MiniDFSCluster availability, HDFS `FileSystem` path resolution, and time-bucketed rolling log paths based on `DATE_FORMAT`.

## Risks and edge cases
Flush-thread validation is timing-sensitive and uses polling. The tests assume four DataNodes are enough for append semantics and replication. Error-path assertions depend on shutdown timing and whether sink operations surface exceptions synchronously or through `MockSink.errored`.

## Test signals
Passing confirms rolling metrics can write to HDFS, append or create new files according to append settings, honor silent error mode, survive missing HDFS during init when configured to ignore errors, and flush buffered metrics to HDFS via the background thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/metrics2/sink/TestRollingFileSystemSinkWithHdfs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/metrics2/sink/TestRollingFileSystemSinkWithSecureHdfs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/metrics2/sink/TestRollingFileSystemSinkWithSecureHdfs.java

## Purpose
This class tests `RollingFileSystemSink` with Kerberos-secured HDFS, HTTPS-only HTTP policy, block tokens, and data-transfer protection. It verifies that a correctly configured sink principal can write metrics and that missing sink principal/keytab settings are reported as initialization errors.

## Important APIs, types, and functions
- `initKdc()` starts a `MiniKdc` and creates sink and HDFS/SPNEGO principals with keytabs.
- `initCluster()` creates a secure HDFS config, installs it into `RollingFileSystemSink.suppliedConf`, starts a four-DataNode MiniDFSCluster, and calls `createDirectoriesSecurely()`.
- `createDirectoriesSecurely()` logs in as HDFS to create `/tmp` with `0777`, logs in as sink to create `/tmp/test`, and supplies the sink-authenticated `FileSystem` to `RollingFileSystemSink`.
- `createSecureConfig(String)` sets Kerberos principals, keytabs, block tokens, data-transfer QOP, HTTPS addresses, SASL retry count, null group mapping, and SSL keystore resources.

## Control flow
Class setup starts KDC once. Per-test setup starts a secure cluster and prepares writable directories. `testWithSecureHDFS` initializes the metrics system with principal/keytab settings and runs the inherited write test inside `sink.doAs`. `testMissingPropertiesWithSecureHDFS` omits required principal/keytab properties and asserts `MockSink.errored`. Per-test cleanup shuts down the cluster and resets UGI and static sink-supplied configuration/filesystem.

## State and persistence behavior
The test writes KDC databases, keytabs, SSL config files, and HDFS directories. Static fields hold principal names and keytab paths. `RollingFileSystemSink.suppliedConf` and `suppliedFilesystem` are global test hooks reset after each test. KDC is stopped after all tests.

## Dependencies and integration points
It integrates MiniKdc, secure MiniDFSCluster, HDFS Kerberos keytab login, SPNEGO configuration, SSL keystore test utilities, metrics2, `NullGroupsMapping`, and `RollingFileSystemSinkTestBase`.

## Risks and edge cases
The test is environment-sensitive because it uses Kerberos, localhost principals, SSL resources, and secure data transfer. Static sink hooks must be reset or they can affect other rolling-sink tests. It covers a basic write as a proxy for more complex sink operations rather than retesting append and failure cases under security.

## Test signals
Passing confirms that the sink can authenticate and write to secure HDFS with supplied config/filesystem, and that secure clusters reject incomplete sink authentication configuration by marking the sink errored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/metrics2/sink/TestRollingFileSystemSinkWithSecureHdfs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/net/TestNetworkTopology.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/net/TestNetworkTopology.java

## Purpose
`TestNetworkTopology` validates Hadoop network topology tree behavior used by HDFS block placement: add/remove, rack counts, distance/weight calculations, sort-by-distance ordering, random node selection with include/exclude scopes, invalid topology handling, non-empty rack counts, and shuffle behavior.

## Important APIs, types, and functions
- `setupDatanodes()` creates twenty `DatanodeDescriptor` instances across data-center/rack paths, adds them to a static `NetworkTopology`, and marks two as decommissioned.
- Tests call `NetworkTopology.contains`, `getNumOfLeaves`, `add`, `remove`, `getNumOfRacks`, `isOnSameRack`, `getWeight`, `getWeightUsingNetworkLocation`, `getDistance`, `getDistanceByPath`, `sortByDistance`, `sortByDistanceUsingNetworkLocation`, `chooseRandom`, `countNumOfAvailableNodes`, `decommissionNode`, `recommissionNode`, and `shuffle`.
- `pickNodesAtRandom` repeatedly calls `chooseRandom` and returns frequency counts; `verifyResults` checks include/exclude outcomes.

## Control flow
Most tests use the shared topology populated in `@BeforeEach`. They assert simple containment/rack/distance behavior, then more complex sort ordering with deterministic seeds and randomization checks. Random-selection tests sample 100-200 choices and assert excluded nodes/racks are never selected while eligible nodes are selected at least once. `testInvalidNetworkTopologiesNotCachedInHdfs` starts a MiniDFSCluster with mismatched rack depths, waits for only one DataNode to register, updates `StaticMapping`, restarts the invalid node, and waits for both nodes to register with matching locations.

## State and persistence behavior
The topology object is static and persists across test methods; setup repeatedly adds the same logical nodes, relying on `NetworkTopology.add` idempotence by node identity/path. `testRemove` removes all nodes and re-adds them before exit. `testInvalidNetworkTopologiesNotCachedInHdfs` mutates static rack mapping and starts a real cluster, then shuts it down.

## Dependencies and integration points
The class integrates `DFSTestUtil` datanode descriptors, HDFS `MiniDFSCluster`, `NamenodeProtocols`, `DatanodeReportType`, `StaticMapping`, `NodeBase`, `DatanodeDescriptor` decommission state, and NetworkTopology logging/random support.

## Risks and edge cases
Sampling-based tests could be flaky if random selection changes or the sample count is insufficient. Static topology state can leak if add/remove semantics or failed tests leave it inconsistent. The invalid-topology cluster test uses sleeps and polling up to 180 seconds and is sensitive to DataNode registration timing.

## Test signals
Passing provides strong evidence that topology paths are validated, distance/weight values match rack depth, reader-local and rack-local sorting is stable with randomized ties, include/exclude scopes work, decommissioned/empty-rack accounting behaves, and invalid HDFS rack topology is not permanently cached after mapping repair.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/net/TestNetworkTopology.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/security/TestPermission.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/security/TestPermission.java

## Purpose
`TestPermission` validates HDFS permission and ownership semantics: umask compatibility, directory/file creation permissions, default permissions, read/write/execute bits, access-control failures, rename checks, and `setOwner` rules for superusers and non-superusers.

## Important APIs, types, and functions
- Static helpers `checkPermission`, `createFile`, `canMkdirs`, `canCreate`, `canOpen`, and `canRename` centralize file creation and expected access-control behavior.
- `testBackwardCompatibility()` checks old/new umask configuration parsing, including invalid umasks.
- `testCreate()` checks mkdir/create permission propagation, inherited parent permissions, umask behavior, and `FileSystem.mkdirs/create` static helpers.
- `testFilePermission()` performs the broader integration scenario using NameNode file system and a non-superuser file system.
- Private ownership tests cover superuser owner/group changes and non-superuser allowed/denied group/owner changes.

## Control flow
`testCreate` starts a MiniDFSCluster with permissions enabled and umask `000`, creates nested directories and files with explicit permissions, switches umask to `022`, and verifies status permissions. `testFilePermission` starts another cluster, validates non-existent file errors, creates files/dirs, writes and reads random bytes, changes permission bits, creates a non-superuser UGI, attempts denied operations, relaxes permissions to permit rename, then runs owner/group subtests.

## State and persistence behavior
Tests persist files under `/data` and root-level helper paths inside MiniDFSCluster. Randomized user names avoid collisions. Instance fields `nnfs` and `userfs` hold superuser and non-superuser file-system handles during `testFilePermission`. Clusters are shut down in `finally` blocks.

## Dependencies and integration points
This class integrates `FsPermission`, HDFS permission enforcement, `MiniDFSCluster`, `DFSTestUtil.getFileSystemAs`, `UserGroupInformation`, `AccessControlException`, and AssertJ/JUnit assertions. It checks both API return behavior and error-message path contents.

## Risks and edge cases
Some assertions use string forms of permissions, so changes in display formatting could break tests. `testNonSuperCannotChangeOwnerForNonExistentFile` accepts either `AccessControlException` or `FileNotFoundException`, reflecting implementation variability. Random user naming is helpful but can make logs non-deterministic.

## Test signals
Passing confirms HDFS permission bits and umasks are applied correctly, permission-denied messages include absolute paths, non-superusers cannot bypass ownership/group restrictions, and superusers retain owner/group mutation powers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/security/TestPermission.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/security/TestPermissionSymlinks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/security/TestPermissionSymlinks.java

## Purpose
This class validates HDFS permission and ACL behavior for symlink operations. It checks that deleting and renaming a link depend on link-parent permissions, reading/accessing a link depends on target permissions, and link status/target inspection does not require target read permission.

## Important APIs, types, and functions
- Static paths define `/symtest1/link` pointing to `/symtest2/target`.
- Class setup enables HDFS permissions and ACLs, starts a MiniDFSCluster, and creates a `FileSystemTestWrapper`.
- Per-test setup creates link and target; per-test teardown deletes both parent directories.
- Helper methods implement repeated checks for delete, read, link-status, and rename behavior through `FileContext` and `FileSystem`.

## Control flow
Each test configures permissions or ACLs, then invokes a helper under a non-superuser `UserGroupInformation.doAs`. Delete tests ensure non-writable link parent blocks link deletion, while non-writable target parent/target does not block deleting only the link. Read tests deny opening the symlink when target read is denied. Link-status tests allow `getFileLinkStatus` and `getLinkTarget` despite target read denial. Rename tests separately cover FileContext `rename(..., Rename.NONE)` and FileSystem `rename`, allowing rename when only target is unwritable and denying when source link parent is unwritable. `testAccess` checks `FileContext.access` through a symlink and validates an error message for a bad child path through a non-directory target.

## State and persistence behavior
The cluster is shared per class. Each test recreates the same symlink and target and removes them afterward. ACL and permission mutations are local to those paths and cleared by directory deletion.

## Dependencies and integration points
The test integrates HDFS symlink implementation, `FileContext`, `FileSystem`, ACL helpers from NameNode tests, `FsPermission`, `FsAction`, `FileSystemTestWrapper`, non-superuser UGI, and `GenericTestUtils.assertExceptionContains`.

## Risks and edge cases
Because it uses a shared static cluster, failed cleanup can affect later tests. ACL tests rely on exact effective permissions for a named user. Error-message assertions in `testAccess` intentionally check that the resolved target path appears and the unresolved bad symlink path does not.

## Test signals
Passing confirms symlink operations enforce permissions on the correct inode/path: link-parent write for delete/rename, target permissions for dereferenced read/access, and non-dereferencing status operations independent of target readability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/security/TestPermissionSymlinks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/security/TestRefreshUserMappings.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/security/TestRefreshUserMappings.java

## Purpose
`TestRefreshUserMappings` verifies administrative refresh of cached user-to-group mappings and proxy-superuser group/host configuration through `DFSAdmin`.

## Important APIs, types, and functions
- `MockUnixGroupsMapping` implements `GroupMappingServiceProvider`; each uncached lookup returns incrementing group names in both list and set forms.
- `setUp()` installs the mock group mapping, sets a one-second cache TTL, starts MiniDFSCluster, and raises group logging.
- `testGroupMappingRefresh()` calls `DFSAdmin -refreshUserToGroupsMappings` and checks cache invalidation before and after timeout.
- `testRefreshSuperUserGroupsConfiguration()` configures proxy-user groups/hosts, mocks UGI real/effective users, calls `ProxyUsers.authorize`, writes a temporary XML resource with changed proxy groups, runs `DFSAdmin -refreshSuperUserGroupsConfiguration`, and validates authorization flips.
- `addNewConfigResource` writes a classpath XML resource and registers it with `Configuration.addDefaultResource`.

## Control flow
Group refresh first proves two immediate group lookups return cached identical values. It runs DFSAdmin refresh and asserts the next lookup differs. It then waits until TTL expiry yields a further changed mapping. Proxy refresh first authorizes only the user whose groups match `gr3,gr4,gr5`, then adds an XML resource changing allowed groups to `gr2`, runs DFSAdmin refresh, and expects the previously denied user to succeed while the previously allowed user fails.

## State and persistence behavior
The class starts a MiniDFSCluster per test and deletes it in teardown. It writes a temporary XML resource beside `hdfs-site.xml` on the classpath and deletes the file afterward. `Configuration.addDefaultResource` is global, so resource registration may outlive file deletion in process state.

## Dependencies and integration points
It integrates `Groups`, `GroupMappingServiceProvider`, `DFSAdmin`, `ProxyUsers`, `DefaultImpersonationProvider`, MiniDFSCluster admin RPCs, mocked `UserGroupInformation`, and classpath configuration loading.

## Risks and edge cases
The cache-timeout test uses polling and a multiplied timeout. The temporary default resource addition is process-global and could affect later tests if keys collide. The mock group mapper increments on both list and set lookups, so new callers can change expected sequences.

## Test signals
Passing confirms DFSAdmin refresh commands reach NameNode-side services, group caches are invalidated on demand and by TTL, and proxy-user authorization reloads group/host rules from refreshed configuration resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/security/TestRefreshUserMappings.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/test/HdfsTestDriver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/test/HdfsTestDriver.java

## Purpose
`HdfsTestDriver` is a command-line program driver for HDFS test utilities that should not depend on MapReduce APIs.

## Important APIs, types, and functions
- Constructor registers `dfsthroughput` mapped to `BenchmarkThroughput` and `minidfscluster` mapped to `MiniDFSClusterManager` in a `ProgramDriver`.
- `run(String[])` delegates to `ProgramDriver.run` and exits the JVM with the returned code.
- `main` constructs the driver and runs it.

## Control flow
Construction registers commands inside a broad `Throwable` catch. `run` initializes exit code to `-1`, tries to run the selected command, catches broad `Throwable`, prints stack traces, and calls `System.exit(exitCode)`.

## State and persistence behavior
The only state is the `ProgramDriver` instance and its command registry. Running commands may start clusters or benchmarks, but this file itself persists no data.

## Dependencies and integration points
It integrates Hadoop `ProgramDriver`, HDFS `BenchmarkThroughput`, and `MiniDFSClusterManager`. It is likely invoked from test jars or command-line HDFS test tooling.

## Risks and edge cases
Broad exception handling prints stack traces rather than structured logs. `System.exit` makes direct unit testing harder unless `ExitUtil` or process isolation is used. Registration failure leaves the driver partially populated.

## Test signals
No local tests are defined here. Functional signals come from invoking registered subcommands and verifying expected exit codes and behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/test/HdfsTestDriver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/test/MiniDFSClusterManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/test/MiniDFSClusterManager.java

## Purpose
`MiniDFSClusterManager` is a command-line utility that starts a local single-process `MiniDFSCluster`, optionally formats it, writes cluster configuration/details to files, and keeps the process alive until the cluster stops or the process is killed.

## Important APIs, types, and functions
- `makeOptions()` defines CLI flags for datanode count, format, command port, NameNode RPC/HTTP ports, NameNode URL, `-D property=value`, `writeConfig`, `writeDetails`, and help.
- `parseArguments(String[])` parses options with Commons CLI, fills member variables, creates `HdfsConfiguration`, and applies `-D` overrides.
- `start()` builds `MiniDFSCluster` with configured ports, datanode count, startup option, and format flag; writes XML config and JSON details if requested.
- `sleepForever()` sleeps in one-minute intervals until `dfs.isClusterUp()` is false.

## Control flow
`run` parses arguments and returns on parse/help errors. On success it starts the cluster, then enters the sleep loop. `main` delegates to `run`. Invalid integer options log errors and fall back to defaults.

## State and persistence behavior
Instance fields hold parsed options and the running `MiniDFSCluster`. Optional `writeConfig` persists Hadoop XML configuration. Optional `writeDetails` persists JSON currently containing the NameNode port. The cluster stores HDFS metadata/data in the MiniDFSCluster configured directories until the process is terminated or cluster shutdown occurs.

## Dependencies and integration points
The class integrates Commons CLI `GnuParser`, `HelpFormatter`, HDFS `MiniDFSCluster.Builder`, `StartupOption`, Hadoop `Configuration` XML serialization, and Jetty JSON serialization.

## Risks and edge cases
The `cmdport` and `namenode` options are defined but not used in startup logic. File streams are closed manually rather than try-with-resources. The process has no explicit shutdown hook; operational shutdown is by killing the process. `sleepForever` ignores interrupts except to continue.

## Test signals
Expected signals are successful CLI parse, cluster activation, valid written XML/JSON files, and continued liveness while `MiniDFSCluster.isClusterUp()` remains true. Invalid args should print help and avoid starting a cluster.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/test/MiniDFSClusterManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/test/PathUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/test/PathUtils.java

## Purpose
`PathUtils` provides test-directory helpers returning either Hadoop `Path`, Java `File`, or absolute path string locations under `GenericTestUtils.getRandomizedTestDir()`.

## Important APIs, types, and functions
- `getTestPath(Class<?>)` and `getTestPath(Class<?>, boolean)` return a Hadoop `Path` for the caller's test directory.
- `getTestDir(Class<?>)` and `getTestDir(Class<?>, boolean)` return a Java `File` directory named after the caller simple class name.
- `getTestDirName(Class<?>)` and overload return the absolute path string.

## Control flow
All public methods delegate to `getTestDir`; if `create` is true, `dir.mkdirs()` is called. The returned path is deterministic for a caller class within the randomized test root.

## State and persistence behavior
The helper creates local filesystem directories when requested. It does not track or clean them up.

## Dependencies and integration points
It integrates Hadoop `Path`, Java `File`, and `GenericTestUtils` randomized test-directory selection.

## Risks and edge cases
`getTestPath(caller, false)` still calls `getTestDir(caller, false)` and returns a path, but no directory is created. `mkdirs()` return value is ignored, so creation failures are not surfaced immediately. Class simple-name collisions can share directories.

## Test signals
No tests are defined here. Consumers should verify returned directories exist when `create=true` and are isolated enough for their test class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/test/PathUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/test/SampleStep.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/test/SampleStep.java

## Purpose
`SampleStep` is a minimal `Step` implementation used by DiskBalancer serialization/deserialization tests.

## Important APIs, types, and functions
It implements `Step` methods for bytes-to-move, source/destination volumes, ideal storage, volume-set ID, formatting, max disk errors, tolerance percent, and bandwidth. Setters are implemented for tolerance, bandwidth, and max disk errors.

## Control flow
The class is a simple data stub. Getters return stored fields for bandwidth/tolerance/max errors, default zero or empty values for other metrics, `null` for source/destination volumes, and `Long.toString(size)` for size formatting.

## State and persistence behavior
Private fields store `bytesToMove`, `bandwidth`, `tolerancePercent`, and `maxDiskErrors`. Only three of those have setters in this class; `bytesToMove` remains default unless serialization/reflection mutates it.

## Dependencies and integration points
It integrates DiskBalancer `Step` and `DiskBalancerVolume` interfaces/classes. Its primary integration point is JSON/XML serde or planner tests that need a concrete `Step` type without real disk volumes.

## Risks and edge cases
Because source/destination volumes are always `null` and volume-set ID is empty, it should not be used for planner logic that expects complete steps. Lack of a setter for `bytesToMove` may require reflection or serde field access.

## Test signals
Serde tests using this class can verify that common `Step` scalar fields survive serialization without constructing a full DiskBalancer plan.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/test/SampleStep.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/tools/FakeRenewer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/tools/FakeRenewer.java

## Purpose
`FakeRenewer` is a test `TokenRenewer` that records the last renewed and canceled token for tests of delegation-token tooling.

## Important APIs, types, and functions
- `KIND` is the token kind handled by this renewer.
- `handleKind(Text)` returns true only for `KIND`.
- `isManaged(Token<?>)` always returns true.
- `renew(Token<?>, Configuration)` records `lastRenewed` and returns `0`.
- `cancel(Token<?>, Configuration)` records `lastCanceled`.
- `reset`, `getLastRenewed`, and `getLastCanceled` expose static test state.

## Control flow
The renewer is invoked by Hadoop token-renewal service discovery. It accepts a test token kind, records side effects on renew/cancel, and otherwise performs no real external operation.

## State and persistence behavior
State is held in static fields `lastRenewed` and `lastCanceled`. `reset()` must be called by tests to avoid cross-test leakage.

## Dependencies and integration points
It integrates Hadoop security token APIs: `TokenRenewer`, `Token`, `Text`, and `Configuration`. It is typically discovered through service-provider configuration in tests.

## Risks and edge cases
The static fields are not synchronized, so parallel tests using this renewer can race. Since `renew` returns zero and `isManaged` always returns true, it is a behavior stub rather than a realistic renewer.

## Test signals
Consumers can assert that command-line token tools or token-management code invoked renew/cancel on the expected token by checking the static recorded values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/tools/FakeRenewer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/tools/TestHdfsConfigFields.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/tools/TestHdfsConfigFields.java

## Purpose
`TestHdfsConfigFields` compares HDFS configuration key constants against `hdfs-default.xml` so missing constants or missing XML properties are detected, with an explicit skip list for deprecated, generated, internal, native, or cross-module properties.

## Important APIs, types, and functions
- The class extends `TestConfigurationFieldsBase`.
- `initializeMemberVariables()` sets `xmlFilename`, `configurationClasses`, error modes, `configurationPropsToSkipCompare`, `xmlPropsToSkipCompare`, and `xmlPrefixToSkipCompare`.
- Configuration classes include `HdfsClientConfigKeys` and nested groups, plus `DFSConfigKeys`.

## Control flow
The base class invokes `initializeMemberVariables`, reflects configuration key fields from listed classes, loads `hdfs-default.xml`, applies exact and prefix skip sets, and fails on missing properties according to enabled error modes.

## State and persistence behavior
The test builds in-memory sets only. It does not persist files.

## Dependencies and integration points
It integrates HDFS client/server config key classes with the default XML resource. It also encodes knowledge of deprecated keys, NFS module ownership, native FUSE keys, HTrace remnants, and dynamically generated NameNode edits-plugin keys.

## Risks and edge cases
Skip lists can become stale and hide missing coverage or produce false positives after config movement. Both `errorIfMissingConfigProps` and `errorIfMissingXmlProps` are true, so adding a key in either Java or XML usually requires updating the other or the skip list.

## Test signals
Passing indicates Java constants and `hdfs-default.xml` are aligned for user-visible HDFS config properties, except for documented skips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/tools/TestHdfsConfigFields.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/tools/TestJMXGet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/tools/TestJMXGet.java

## Purpose
`TestJMXGet` validates the HDFS `JMXGet` tool against live NameNode and DataNode MBeans in a MiniDFSCluster and checks that service MBeans are unregistered after cluster shutdown.

## Important APIs, types, and functions
- `setUp()` creates an `HdfsConfiguration`; `tearDown()` shuts down the cluster and deletes its data directory.
- `testNameNode()` creates a file, initializes `JMXGet` for `NameNode`, prints all values, waits for `NumLiveDataNodes`, compares `CorruptBlocks` to metrics assertions, then checks MBean unregistration.
- `testDataNode()` creates a file, initializes `JMXGet` for `DataNode`, waits for `BytesWritten`, then checks MBean unregistration.
- `checkPrintAllValues(JMXGet)` captures `System.err` through piped streams and looks for the "List of all the available keys:" marker.

## Control flow
Each test starts a two-DataNode cluster, writes an HDFS file to generate metrics, queries metrics through `JMXGet`, falls back to direct value comparison if `DFSTestUtil.waitForMetric` times out, shuts the cluster down, and queries the platform MBean server for remaining Hadoop service MBeans.

## State and persistence behavior
The tests write small files into HDFS and create MiniDFSCluster data directories on local disk. Tear-down removes the HDFS data directory after shutdown. `checkPrintAllValues` temporarily redirects `System.err` and restores it in `finally`.

## Dependencies and integration points
It integrates `JMXGet`, Java platform MBean server, HDFS metrics, `MetricsAsserts`, `DFSTestUtil`, MiniDFSCluster, and local filesystem cleanup via `FileUtil`.

## Risks and edge cases
Metric propagation is asynchronous, so tests use waits and fallback assertions. Capturing `System.err` is process-global and risky under parallel execution. Data-directory cleanup failure is escalated as `IOException` in tear-down.

## Test signals
Passing confirms `JMXGet` can list and read NameNode/DataNode metrics, expected HDFS metrics are exposed with correct values, and service MBeans are removed after cluster shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/tools/TestJMXGet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/tools/TestTools.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/tools/TestTools.java

## Purpose
`TestTools` verifies command-line help, invalid-option output, and exit behavior for HDFS administrative tools: `DelegationTokenFetcher`, `JMXGet`, and `DFSAdmin`.

## Important APIs, types, and functions
- `before()` disables JVM exit through `ExitUtil.disableSystemExit()` and prepares an invalid option array.
- `checkOutput(String[], String, PrintStream, Class<?>)` captures either stdout or stderr, invokes the selected tool, and asserts the captured text contains an expected pattern.
- `expectDelegationTokenFetcherExit`, `expectJMXGetExit`, and `expectDfsAdminPrint` wrap tool invocation and expected `ExitException` handling.
- `testDFSAdminInvalidUsageHelp()` iterates many DFSAdmin commands with an extra invalid option and checks return code `-1`.

## Control flow
Individual tests call `checkOutput` with a command class and pattern. For tools that call `System.exit`, the disabled-exit hook throws `ExitException`, which is consumed and reset. DFSAdmin is invoked through `ToolRunner` or direct helper and expected to print usage for invalid combinations.

## State and persistence behavior
The class mutates global `ExitUtil` state and process stdout/stderr during capture. It does not create files or clusters.

## Dependencies and integration points
It integrates HDFS command-line tools, `ToolRunner`, `ExitUtil`, Guava/thirdparty `ByteStreams` and `ImmutableSet`, and Java piped streams.

## Risks and edge cases
Global stdout/stderr redirection and disabled system exit are not parallel-test-safe. Pipe buffer size is fixed at 5 KiB, so unexpectedly large output could block or truncate behavior. Pattern assertions are broad and may miss formatting regressions outside the checked substring.

## Test signals
Passing confirms common HDFS tools emit expected help/error text and handle invalid argument combinations without terminating the test JVM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/tools/TestTools.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java8/org/apache/hadoop/hdfs/TestDFSClientFailover.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java8/org/apache/hadoop/hdfs/TestDFSClientFailover.java

## Purpose
`TestDFSClientFailover` validates HDFS HA client failover behavior, logical URI handling, connect-timeout failover, DNS avoidance for logical nameservices, legacy failover proxy wrapping, and IP failover proxy logical-URI rules.

## Important APIs, types, and functions
- `setUpCluster()` starts a simple HA MiniDFSCluster and transitions NameNode 0 active.
- `testDfsClientFailover()` writes a file, shuts down active NN0, transitions NN1 active, and verifies the same client can read status after failover.
- `InjectingSocketFactory` spies sockets and throws `ConnectTimeoutException` for a configured NameNode port.
- `spyOnNameService()` reflectively replaces Sun JDK `InetAddress.nameServices[0]` with a Mockito delegate spy, aborting if unsupported.
- DNS tests verify `FileSystem`, `FileContext`, and proxy creation do not resolve logical nameservice hostnames.
- `DummyLegacyFailoverProxyProvider` implements old `FailoverProxyProvider` for wrapping tests.

## Control flow
Each test starts with a fresh HA cluster. Failover tests configure failover file systems, write or create paths, kill/activate NameNodes, and assert behavior. Misconfiguration tests create logical URIs with missing addresses or forbidden ports and assert helpful exceptions. DNS tests install the name-service spy, perform filesystem/proxy operations, and verify no lookup for the logical host. Proxy-provider tests configure legacy or IP providers and assert `HAUtil.useLogicalUri` outcomes.

## State and persistence behavior
The MiniDFSCluster stores `/tmp/failover-test-file` and HA NameNode state per test. `clearConfig()` resets `SecurityUtil.setTokenServiceUseIp(true)` after each test. `spyOnNameService()` mutates JDK-global DNS service list and does not explicitly restore it in this file, which is a notable process-global test hook.

## Dependencies and integration points
It integrates HA MiniDFSCluster topology, `HATestUtil`, `NameNodeProxies`, `NameNodeProxiesClient`, `ConfiguredFailoverProxyProvider`, `IPFailoverProxyProvider`, DFS client config keys, socket factories, Java DNS internals, Mockito, and Java 8 `sun.net.spi.nameservice.NameService`.

## Risks and edge cases
This file lives under `src/test/java8` because it depends on JDK-internal DNS APIs that are not portable across later Java runtimes. DNS spying skips tests on incompatible JDKs but can leak global DNS mock state after success. Connect-timeout failover is sensitive to socket-factory configuration and mocked socket behavior.

## Test signals
Passing confirms HA clients fail over after active NameNode loss and connect timeouts, logical URIs reject explicit ports, misconfigured HA addresses produce actionable errors, logical nameservices are not DNS-resolved, legacy providers still trigger logical-token-service behavior, and IP failover providers do not require logical URIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java8/org/apache/hadoop/hdfs/TestDFSClientFailover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/contract/hdfs.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/contract/hdfs.xml

## Purpose
`hdfs.xml` is a filesystem contract-test resource declaring HDFS capabilities and expected behaviors for Hadoop contract tests.

## Important APIs, types, and functions
The file is an XML `configuration` resource with `property` entries. It enables root tests, sets random seek count, and declares HDFS support for case sensitivity, append, atomic directory delete, atomic rename, block locality, concat, seek, strict exceptions, Unix permissions, setTimes, getFileStatus, file references, content checks, unbuffer, hflush, and hsync. It declares rename return behavior for existing destination or missing source and states `metadata_updated_on_hsync=false`.

## Control flow
There is no executable control flow. Hadoop contract-test loaders read the resource as configuration and parameterize generic filesystem contract tests based on the property values.

## State and persistence behavior
The resource persists no runtime state. Its values influence which contract tests run and what behavior they expect from HDFS.

## Dependencies and integration points
It integrates HDFS with the Hadoop filesystem contract test framework. Property names are part of the contract-test schema used by generic FS tests.

## Risks and edge cases
Incorrect values can either skip meaningful HDFS coverage or cause generic contract tests to expect behavior HDFS does not provide. `metadata_updated_on_hsync=false` is a subtle semantic expectation that can affect durability/metadata tests.

## Test signals
The resource signals that HDFS should pass broad filesystem contract behavior around append, seek, rename, permissions, locality, flush/sync, and error strictness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/contract/hdfs.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/dfs.hosts.json -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/dfs.hosts.json

## Purpose
`dfs.hosts.json` is a host include/exclude manager fixture describing DataNode host entries with optional upgrade domains, admin states, ports, and maintenance expiry.

## Important APIs, types, and functions
The JSON array contains seven objects:
- plain host `host1`
- `host2` with upgrade domain `ud0`
- `host3` decommissioned
- `host4` with upgrade domain `ud2` and decommissioned
- `host5` with port `8090`
- `host6` in maintenance
- `host7` in maintenance with `maintenanceExpireTimeInMS` as a string value

## Control flow
There is no executable control flow. Tests load the JSON into host-entry data structures and verify parser/default behavior.

## State and persistence behavior
The file is static test data. Loaded state should represent host-level administrative membership and maintenance/decommission metadata.

## Dependencies and integration points
It integrates with HDFS hosts-file JSON parsing, DataNode admin-state handling, upgrade-domain support, port-specific entries, and maintenance expiration handling.

## Risks and edge cases
The fixture intentionally mixes absent and present optional fields. The maintenance expiration is encoded as a string, so parsers must handle the expected type. Consumers should preserve port-specific behavior for `host5`.

## Test signals
Useful parser signals include correct defaults for missing fields, correct decommission and maintenance admin states, upgrade-domain extraction, and maintenance expiration parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/dfs.hosts.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/diskBalancer/data-cluster-3node-3disk.json -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/diskBalancer/data-cluster-3node-3disk.json

## Purpose
This JSON fixture describes a three-node DiskBalancer cluster with three storage types and three volumes per storage type per node. It is used to test DiskBalancer data-model parsing, density calculations, and planner behavior over a non-trivial but deterministic cluster shape.

## Important APIs, types, and functions
The top-level object contains `nodes`, empty `exclusionList`, empty `inclusionList`, and `threshold: 0`. Each node has a `dataNodeUUID`, `nodeDataDensity`, and `volumeSets` keyed by `SSD`, `RAM_DISK`, and `DISK`. Each volume entry includes path, capacity, used bytes, reserved bytes, storage type, UUID, failed flag, volume data density, and transient flag.

## Control flow
There is no executable control flow. DiskBalancer tests read the fixture into cluster/node/volume-set/volume model objects and then run validation or planning logic.

## State and persistence behavior
The file is static model state. It encodes mixed capacities, used/reserved values, transient and non-transient storage, and density values that downstream tests treat as expected input data.

## Dependencies and integration points
It integrates with DiskBalancer JSON serde, `DiskBalancerCluster`, node and volume-set models, planner steps, inclusion/exclusion filters, and threshold-based balancing decisions.

## Risks and edge cases
The fixture uses escaped `/tmp/disk/...` paths and large numeric capacities/usage values that must be parsed as long-compatible numbers. All `failed` flags are false and inclusion/exclusion lists are empty, so it does not cover failed-volume or filtered-node behavior. `threshold: 0` can make planners sensitive to any imbalance.

## Test signals
Successful use of this fixture indicates DiskBalancer can parse multi-node, multi-storage-type clusters, preserve transient flags for RAM_DISK, retain UUID/path/capacity/usage metadata, and compute or consume node/volume density information.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/diskBalancer/data-cluster-3node-3disk.json -->

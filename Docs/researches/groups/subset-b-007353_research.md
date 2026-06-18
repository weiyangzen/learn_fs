# Research: subset-b-007353

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/HAServiceProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/HAServiceProtocolServerSideTranslatorPB.java

Purpose: server-side protobuf RPC adapter for `HAServiceProtocolPB`. It receives generated protobuf requests, calls the native `HAServiceProtocol` implementation, and converts Hadoop HA status and transition request metadata back into protobuf responses.

Important APIs, types, and functions: constructor stores the `HAServiceProtocol` delegate. `monitorHealth()`, `transitionToActive()`, `transitionToStandby()`, `transitionToObserver()`, and `getServiceStatus()` implement the protobuf blocking interface. `convert(HAStateChangeRequestInfoProto)` maps protobuf request-source enums into `HAServiceProtocol.RequestSource`. `getProtocolVersion()` and `getProtocolSignature()` expose Hadoop RPC version negotiation.

Control flow: each RPC method catches `IOException` from the HA service and wraps it in protobuf `ServiceException`. State-changing calls convert `reqInfo` before delegating. Status calls translate `HAServiceStatus.State` into `HAServiceStateProto`, set readiness, and include `notReadyReason` only when active transition is not allowed.

State and persistence: the translator has no persisted state. It only caches immutable empty response protobufs and a reference to the live HA service. Persistent HA state changes happen in the wrapped server, not here.

Dependencies and integration points: integrates Hadoop HA service interfaces with protobuf RPC engine types, `RPC` protocol metadata, `ProtocolSignature`, and generated `HAServiceProtocolProtos`.

Risks and test signals: unknown request-source enum values are logged and converted to null, so downstream service handling must tolerate or reject null request info. Tests should cover every HA state, readiness reason propagation, IOException-to-ServiceException wrapping, observer transitions, and protocol-name mismatch failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/HAServiceProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolClientSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolClientSideTranslatorPB.java

Purpose: client-side protobuf translator implementing the native `ZKFCProtocol` API over Hadoop protobuf RPC. It hides request construction and RPC proxy management from callers that need to command a ZooKeeper Failover Controller.

Important APIs, types, and functions: the constructor configures `ProtobufRpcEngine2` for `ZKFCProtocolPB` and obtains an RPC proxy with the current `UserGroupInformation`. `cedeActive(int)` builds `CedeActiveRequestProto`. `gracefulFailover()` sends the default failover request. `close()` stops the proxy, and `getUnderlyingProxyObject()` exposes it for protocol translator plumbing.

Control flow: native method calls build protobuf requests and invoke `rpcProxy` through `ShadedProtobufHelper.ipc`, which converts protobuf service failures into Hadoop `IOException` and `AccessControlException` style errors. There is no retry logic in this class; retry behavior is inherited from the RPC proxy setup.

State and persistence: state is limited to the RPC proxy and a null protobuf controller. It does not persist failover state; it sends commands to the remote ZKFC service.

Dependencies and integration points: depends on Hadoop `RPC`, `ProtobufRpcEngine2`, UGI, socket factory configuration, generated `ZKFCProtocolProtos`, and the public `ZKFCProtocol` interface.

Risks and test signals: lifecycle correctness depends on callers closing the translator. Tests should validate request fields, proxy stop on close, exception conversion, timeout/socket configuration, and compatibility with secure UGI contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolPB.java

Purpose: protobuf RPC protocol interface for the ZK Failover Controller. It binds the generated blocking protobuf service to Hadoop's `VersionedProtocol` and publishes security and protocol metadata.

Important APIs, types, and functions: the interface extends `ZKFCProtocolService.BlockingInterface` and `VersionedProtocol`. `@KerberosInfo` points at `hadoop.security.service.user.name`, while `@ProtocolInfo` declares protocol name `org.apache.hadoop.ha.ZKFCProtocol` and version 1.

Control flow: this file has no executable methods beyond inherited contracts. Hadoop RPC uses its annotations and type identity when creating client proxies and server endpoints.

State and persistence: no runtime or persisted state. Protocol version and name are compatibility contracts for RPC negotiation.

Dependencies and integration points: integrates generated protobuf service code, Hadoop RPC protocol discovery, Kerberos principal lookup, and the ZKFC native protocol translators.

Risks and test signals: changing the protocol name or version breaks wire compatibility. Tests should include RPC proxy construction, secure principal resolution, and server signature negotiation through the translators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolServerSideTranslatorPB.java

Purpose: server-side protobuf adapter for `ZKFCProtocolPB`. It exposes ZKFC administrative operations over protobuf RPC and delegates to the native `ZKFCProtocol` implementation.

Important APIs, types, and functions: constructor stores the `ZKFCProtocol` server. `cedeActive()` extracts `millisToCede`, `gracefulFailover()` delegates directly, and both return default empty protobuf responses. `getProtocolVersion()` and `getProtocolSignature()` support Hadoop RPC compatibility checks.

Control flow: protobuf RPC enters this translator, the translator calls the backing ZKFC server, and `IOException` is wrapped as `ServiceException`. Protocol signature rejects unknown protocol names before returning the negotiated signature.

State and persistence: no persistent state. Runtime state is the delegate reference. HA/failover state changes are owned by the delegate and external coordination systems.

Dependencies and integration points: depends on generated ZKFC protobuf messages, `RPC`, `ProtocolSignature`, and the HA failover controller service implementation.

Risks and test signals: `getProtocolSignature()` passes `HAServiceProtocolPB.class` to `ProtocolSignature.getProtocolSignature()` even though this translator implements `ZKFCProtocolPB`, which is a compatibility-sensitive point worth regression coverage. Tests should cover cede duration propagation, graceful failover delegation, exception wrapping, and protocol mismatch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/AdminAuthorizedServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/AdminAuthorizedServlet.java

Purpose: Jetty default servlet variant that gates static resource access behind Hadoop administrator authorization. It is used for protected HTTP contexts such as `/logs`.

Important APIs, types, and functions: `doGet()` calls `HttpServer2.hasAdministratorAccess()` with the servlet context, request, and response. Only authorized requests are forwarded to `DefaultServlet.doGet()`.

Control flow: requests fail closed when authorization returns false because the helper has already written an HTTP error. Authorized requests continue through Jetty's normal default static-file handling.

State and persistence: the servlet has no local state. Authorization state comes from servlet context attributes populated by `HttpServer2`.

Dependencies and integration points: depends on Jetty `DefaultServlet`, servlet request/response APIs, and `HttpServer2` admin ACL semantics.

Risks and test signals: correctness depends on context attributes `hadoop.conf` and `admins.acl`. Tests should cover authenticated admin access, non-admin rejection, missing remote user, disabled authorization, and static file serving behavior after approval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/AdminAuthorizedServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/FilterContainer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/FilterContainer.java

Purpose: small extension interface for objects that can accept servlet filters. It lets Hadoop filter initializers configure `HttpServer2` without depending on Jetty implementation details.

Important APIs, types, and functions: `addFilter(name, classname, parameters)` installs a filter on user-facing/default filtered contexts. `addGlobalFilter(name, classname, parameters)` installs a filter across all contexts.

Control flow: `FilterInitializer` implementations receive a `FilterContainer` during server initialization and call one of these methods to add authentication, static-user, proxy-user, or custom filters.

State and persistence: no state. Implementations decide how filter definitions and mappings are stored.

Dependencies and integration points: used by `HttpServer2`, security filter initializers, and HTTP libraries that need pluggable servlet filters.

Risks and test signals: the interface does not specify path mappings or ordering, so behavior depends on `HttpServer2`'s implementation. Tests should verify initializer ordering, parameter propagation, and the distinction between filtered and global contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/FilterContainer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/FilterInitializer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/FilterInitializer.java

Purpose: abstract base for Hadoop HTTP filter initializers. It defines the SPI used by `HttpServer2` to configure servlet filters from `hadoop.http.filter.initializers`.

Important APIs, types, and functions: subclasses implement `initFilter(FilterContainer container, Configuration conf)` and call container methods with filter names, class names, and init parameters.

Control flow: `HttpServer2.getFilterInitializers()` instantiates configured classes via reflection, then invokes `initFilter()` during web server setup after adding the safety filter and before default servlets.

State and persistence: no state in the base class. Subclasses may derive runtime filter parameters from `Configuration`.

Dependencies and integration points: depends on Hadoop `Configuration` and the `FilterContainer` abstraction. Security and static-user web filters are typical implementations.

Risks and test signals: initializer code runs during server startup, so misconfiguration can prevent HTTP service creation. Tests should cover reflection construction, configuration cloning with bind address, and expected filter registration side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/FilterInitializer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HtmlQuoting.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HtmlQuoting.java

Purpose: HTML escaping and unescaping utility used by Hadoop servlets and request filters to reduce cross-site scripting exposure in generated text and reflected request parameters.

Important APIs, types, and functions: `needsQuoting(byte[], off, len)` and `needsQuoting(String)` detect active HTML characters. `quoteHtmlChars(OutputStream, byte[], off, len)` and `quoteHtmlChars(String)` replace `&`, `<`, `>`, apostrophe, and quote with entity strings. `quoteOutputStream()` wraps an output stream. `unquoteHtmlChars()` reverses the supported entity set and rejects malformed or unknown entities.

Control flow: string quoting converts to UTF-8 bytes, checks whether work is needed, then writes escaped bytes to a `ByteArrayOutputStream`. Unquoting scans from ampersand to semicolon and throws `IllegalArgumentException` on unexpected entities.

State and persistence: stateless except for cached UTF-8 entity byte arrays. No persistence.

Dependencies and integration points: used by `HttpServer2.QuotingInputFilter` and servlet code that reflects request data. Depends only on standard IO and charset APIs.

Risks and test signals: byte-oriented scanning is safe for ASCII trigger characters but does not perform full HTML sanitization. `unquoteHtmlChars()` intentionally rejects unknown entities, which can turn malformed input into request failures. Tests should cover nulls, all five escaped characters, UTF-8 non-ASCII passthrough, output-stream wrapping, bad entity rejection, and round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HtmlQuoting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpConfig.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpConfig.java

Purpose: HTTP policy holder for Hadoop services that may expose HTTP, HTTPS, or both. It centralizes simple scheme-enable checks.

Important APIs, types, and functions: enum `Policy` has `HTTP_ONLY`, `HTTPS_ONLY`, and `HTTP_AND_HTTPS`. `fromString()` performs case-insensitive lookup and returns null for unknown values. `isHttpEnabled()` and `isHttpsEnabled()` answer whether the policy allows each scheme.

Control flow: callers parse configuration strings into a policy, then use the booleans while building endpoint lists.

State and persistence: no mutable state. The enum names are configuration compatibility values.

Dependencies and integration points: used by Hadoop HTTP service configuration outside this file. It has only annotation dependencies.

Risks and test signals: `fromString()` returning null pushes validation to callers. Tests should cover case-insensitive parsing, unknown value handling, and both enablement predicates for all enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpRequestLog.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpRequestLog.java

Purpose: factory for Jetty request log instances backed by SLF4J. It maps common Hadoop HTTP server names to component-specific request loggers.

Important APIs, types, and functions: static `serverToComponent` maps `cluster` to `resourcemanager`, `hdfs` to `namenode`, and `node` to `nodemanager`. `getRequestLog(name)` creates a `Slf4jRequestLogWriter`, sets logger `http.requests.<component>`, and returns a `CustomRequestLog` with extended NCSA format.

Control flow: `HttpServer2.initializeWebServer()` asks for a request log by server name, then wraps it in Jetty `RequestLogHandler`.

State and persistence: immutable static map only. Actual request log persistence is controlled by the SLF4J/logging backend.

Dependencies and integration points: integrates Jetty request logging with Hadoop component logger names.

Risks and test signals: log volume and privacy are controlled outside this class. Tests should verify server-name mapping, logger naming, and that the returned request log writes extended NCSA-compatible records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpRequestLog.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpServer2.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpServer2.java

Purpose: embedded Jetty HTTP/HTTPS server used by Hadoop daemons for web UIs, instrumentation, static resources, metrics, profiling, filters, and admin-protected endpoints.

Important APIs, types, and functions: `HttpServer2.Builder` configures name, endpoints, SSL stores, SPNEGO, ACLs, filters, ciphers, X-Frame options, SNI checks, port finding, and port ranges. Core methods include `initializeWebServer()`, `addDefaultApps()`, `addDefaultServlets()`, `addServlet()`, `addInternalServlet()`, `addFilter()`, `addGlobalFilter()`, `start()`, `openListeners()`, `stop()`, `isInstrumentationAccessAllowed()`, and `hasAdministratorAccess()`. Nested `StackServlet`, `QuotingInputFilter`, `RequestQuoter`, and `XFrameOption` provide diagnostics, request quoting, headers, and clickjacking policy.

Control flow: builder validation creates a server, optionally initializes SPNEGO, loads SSL configuration if HTTPS endpoints exist, creates one connector per resolved bind address, and loads connectors. Constructor builds the root `WebAppContext`, constructs the authentication signer secret provider, and calls initialization. Initialization configures Jetty thread/session behavior, context collections, request logging, optional metrics, safety headers, configured filters, default servlets, Prometheus, and async-profiler. `start()` binds listeners before starting Jetty and registers optional metrics. Binding either uses a configured port, increments when `findPort` is true, or iterates configured port ranges. `stop()` cancels SSL reload monitoring, closes connectors, destroys the signer provider, clears/stops the web app context, stops Jetty, and unregisters metrics.

State and persistence: runtime state includes Jetty `Server`, `HandlerCollection`, `WebAppContext`, connector list, default-context filter map, filter names, signer secret provider, optional SSL reload timer, Prometheus sink, Jetty statistics handler, and registered metrics source. Persistent effects are indirect: serving files from webapp/log/static/profiler-output directories, opening sockets, writing request logs, and reloading TLS store files when monitored paths change.

Dependencies and integration points: heavily integrates Jetty server, servlet, webapp, request-log, SSL, and statistics APIs with Hadoop configuration, security authentication filters, proxy-user filters, ACLs, UGI, SSLFactory/FileBasedKeyStoresFactory, JMX/conf/logLevel servlets, Prometheus metrics sink, Jersey resources, and static web resources under `webapps/<name>`.

Risks and test signals: security behavior depends on filter ordering, context `isFiltered` flags, admin ACL attributes, SPNEGO parameters, and safety header configuration. TLS reload timers and connector binding have lifecycle risk. `initSpnego()` calls `defineFilter()` with null URL specs, which relies on Jetty/Hadoop expectations for internal auth mapping. `stop()` invokes `webServer.stop()` twice, which should remain harmless but is a lifecycle smell. Tests should cover HTTP and HTTPS connectors, dual-stack address expansion, port conflict/range behavior, no-cache and quoting filters, custom header regex loading, admin and instrumentation access, static/log contexts, servlet replacement, Prometheus registration, profiler enabled/disabled paths, metrics source uniqueness, SSL store reload scheduling, and clean shutdown after partial start failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpServer2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpServer2Metrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpServer2Metrics.java

Purpose: Hadoop metrics2 adapter around Jetty `StatisticsHandler`. It exposes Jetty request, dispatch, async, response, byte, and timing counters as Hadoop metrics.

Important APIs, types, and functions: annotated metric getters delegate to `StatisticsHandler` methods such as `getRequests()`, `getRequestsActive()`, `getRequestTimeMean()`, `getResponses4xx()`, and `getResponsesBytesTotal()`. `create()` registers a source named `HttpServer2-<port>`. `remove()` unregisters that source name.

Control flow: `HttpServer2.start()` creates this object after the server starts and a port is known. Metrics polling calls annotated getters, which read live Jetty counters.

State and persistence: stores the statistics handler and port. Metrics are in process memory and exported through Hadoop metrics sinks.

Dependencies and integration points: depends on Jetty statistics and Hadoop metrics2 default system.

Risks and test signals: duplicate registration is avoided by removing the old source name before registering. Tests should cover repeated server starts on the same port, non-default ports, metric values after sample requests, and unregister on shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpServer2Metrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/IsActiveServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/IsActiveServlet.java

Purpose: abstract load-balancer health servlet for active/standby Hadoop services. It reports success only when subclass-specific HA state is active.

Important APIs, types, and functions: constants define servlet name `isActive`, path `/isActive`, and response text. `doGet()` sets `Connection: close`, calls abstract `isActive()`, writes HTTP 200 with active text, or sends HTTP 405 with not-active text.

Control flow: subclasses implement `isActive()` against NameNode, ResourceManager, Router, or other HA state. Load balancers poll the endpoint and route only to instances returning OK.

State and persistence: no local state; active status comes from subclass implementation.

Dependencies and integration points: integrates servlet APIs with Hadoop HA services through subclassing.

Risks and test signals: HTTP 405 is a deliberate non-OK status but may need load-balancer-specific interpretation. Tests should cover active and inactive statuses, connection-close header, response body, and subclass failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/IsActiveServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/JettyUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/JettyUtils.java

Purpose: tiny Jetty constants holder for Hadoop HTTP code.

Important APIs, types, and functions: `UTF_8` is the content-type charset suffix `charset=utf-8`; `HEADER_SIZE` is 64 KiB.

Control flow: no control flow beyond static constant access.

State and persistence: no mutable or persistent state.

Dependencies and integration points: used by servlet and Jetty setup code that need shared charset/header-size constants.

Risks and test signals: low risk. Compatibility tests should ensure callers relying on 64 KiB header sizing still match the configured defaults in `HttpServer2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/JettyUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/NoCacheFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/NoCacheFilter.java

Purpose: servlet filter that prevents client/proxy caching for Hadoop web responses.

Important APIs, types, and functions: `doFilter()` casts the response to `HttpServletResponse`, sets `Cache-Control: no-cache`, adds current `Expires` and `Date` headers, adds `Pragma: no-cache`, and continues the filter chain. `init()` and `destroy()` are no-ops.

Control flow: installed by `HttpServer2.addNoCacheFilter()` on root, static, logs, and added contexts. It mutates headers before downstream servlets run.

State and persistence: stateless.

Dependencies and integration points: depends on servlet filter APIs and `HttpServer2` context setup.

Risks and test signals: assumes HTTP responses, so non-HTTP servlet responses would fail class cast. Tests should verify headers, chain invocation, and behavior when downstream servlet overwrites cache headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/NoCacheFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfileOutputServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfileOutputServlet.java

Purpose: servlet that serves async-profiler output files and auto-refreshes while a profile result is still being written.

Important APIs, types, and functions: `doGet()` checks `HttpServer2.isInstrumentationAccessAllowed()`, resolves the requested path using servlet context real path, treats files smaller than 100 bytes as incomplete, emits a `Refresh` header, and otherwise delegates to Jetty `DefaultServlet`. `sanitize()` permits only alphanumeric, percent, equals, ampersand, dot, and hyphen characters in query strings.

Control flow: profiler requests first return from `ProfileServlet` with a redirect to `/prof-output-hadoop/<file>`. This servlet then polls the output file until it is large enough and serves it.

State and persistence: no servlet state. It reads files in `ProfileServlet.OUTPUT_DIR`, which are persistent temporary profiler artifacts.

Dependencies and integration points: integrates with `HttpServer2` instrumentation ACLs, `ProfileServlet` response headers, and Jetty static serving.

Risks and test signals: `getRealPath()` and file length checks depend on Jetty context configuration. Query sanitization throws runtime exceptions for unexpected characters. Tests should cover unauthorized access, incomplete-output refresh, query sanitization acceptance/rejection, and final static file serving.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfileOutputServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfileServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfileServlet.java

Purpose: instrumentation servlet that launches async-profiler for a target JVM process and redirects users to the generated profile output.

Important APIs, types, and functions: enums `Event` and `Output` validate profiler event/output parameters. `doGet()` enforces instrumentation access, validates async-profiler home and pid, parses duration/interval/jstackdepth/bufsize/thread/simple/width/height/minwidth/reverse parameters, serializes profiler execution with `profilerLock`, starts `profiler.sh` asynchronously through `ProcessUtils`, writes command details, and sets an auto-refresh to the output URL. Static helpers include `setResponseHeader()`, `getAsyncProfilerHome()`, and test-only `setIsTestRun()`.

Control flow: one profiler process may run per servlet instance. If no profiler is active, the servlet builds a command, creates a unique output file under `java.io.tmpdir/prof-output-hadoop`, optionally starts the process, returns HTTP 202, and points the browser at `ProfileOutputServlet`. Invalid or missing configuration returns HTTP 500. Concurrent profiling returns an error.

State and persistence: mutable state includes a lock, volatile `Process`, configured profiler home, current pid, static output directory, static id generator, and test flag. Persistent artifacts are profiler output files in the temp directory.

Dependencies and integration points: depends on `HttpServer2` instrumentation ACLs, `ProcessUtils`, async-profiler's `profiler.sh`, servlet APIs, and `ProfileOutputServlet`.

Risks and test signals: parameters are parsed leniently, invalid numbers fall back to defaults/null. The command response exposes command text and target pid. Output files can accumulate. Tests should cover access control, missing profiler home, pid fallback, each parameter mapping, invalid event/output defaults, lock contention, already-running process handling, test-run suppression, refresh delay, and output path construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfileServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfilerDisabledServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfilerDisabledServlet.java

Purpose: fallback servlet for `/prof` when async-profiler is not configured at server startup.

Important APIs, types, and functions: `doGet()` sets HTTP 500, applies `ProfileServlet.setResponseHeader()`, and writes a diagnostic message with setup guidance.

Control flow: `HttpServer2.addAsyncProfilerServlet()` installs this servlet when neither `ASYNC_PROFILER_HOME` nor `async.profiler.home` is set.

State and persistence: no state and no persistent effects.

Dependencies and integration points: tied to `ProfileServlet` response-header conventions and `HttpServer2` profiler enablement.

Risks and test signals: this endpoint intentionally exposes setup guidance. Tests should verify disabled installation, HTTP status, CORS/text headers, and message content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfilerDisabledServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/PrometheusServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/PrometheusServlet.java

Purpose: servlet that exports Hadoop metrics in Prometheus text format.

Important APIs, types, and functions: `getPrometheusSink()` retrieves `HttpServer2.PROMETHEUS_SINK` from the servlet context. `doGet()` forces `DefaultMetricsSystem.instance().publishMetricsNow()`, writes metrics via `PrometheusMetricsSink.writeMetrics()`, and flushes the response writer.

Control flow: `HttpServer2.addPrometheusServlet()` creates the sink, stores it in the web context, and maps this servlet at `/prom` when Prometheus support is enabled.

State and persistence: no local state. Metrics state lives in the default metrics system and the sink object.

Dependencies and integration points: integrates Hadoop metrics2 default system, Prometheus sink, and servlet context attributes.

Risks and test signals: a missing or wrong sink context attribute would cause null or class-cast failures. Tests should cover enabled/disabled registration, context attribute presence, publish-before-write behavior, and response content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/PrometheusServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/WebServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/WebServlet.java

Purpose: Hadoop static-content servlet that redirects root webapp requests to `index.html` while preserving safe query strings.

Important APIs, types, and functions: `doGet()` checks whether `request.getRequestURI().equals("/")`. For root, it builds a redirect to `index.html`, appends the query string after removing CR/LF to prevent response splitting, and sends the redirect. Other paths delegate to Jetty `DefaultServlet`.

Control flow: this servlet is the root servlet in the main webapp context and also serves `/static` resources. Root redirects help SPNEGO and impersonation flows reach the actual page asset.

State and persistence: stateless. Static files are served from configured webapp resource bases.

Dependencies and integration points: depends on Jetty default servlet and `HttpServer2` webapp context setup.

Risks and test signals: query strings are not HTML-escaped here, only CR/LF-stripped for redirect safety. Tests should cover root redirect, query preservation/sanitization, non-root static serving, and interaction with authentication filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/WebServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/lib/StaticUserWebFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/lib/StaticUserWebFilter.java

Purpose: filter initializer that supplies a static remote user for web UIs when no authenticated user exists, making secure-cluster web pages usable without full HTTP authentication.

Important APIs, types, and functions: nested `User` implements `Principal` with name-based equality. Nested `StaticUserFilter` wraps unauthenticated `HttpServletRequest`s so `getUserPrincipal()` and `getRemoteUser()` return the configured static user. `initFilter()` registers the filter with the container. `getUsernameFromConf()` reads `hadoop.http.staticuser.user` or deprecated `dfs.web.ugi`.

Control flow: during `HttpServer2` filter initialization, this initializer adds `static_user_filter`. At request time the filter preserves existing authenticated users and only wraps anonymous requests.

State and persistence: filter instance stores immutable username/principal after init. No persistence.

Dependencies and integration points: integrates Hadoop configuration keys, `FilterContainer`, `FilterInitializer`, servlet filters, and downstream admin ACL checks that rely on remote user.

Risks and test signals: static users can grant UI identity in deployments without authentication, so configuration must align with ACL expectations. Deprecated `dfs.web.ugi` parsing uses the first comma-separated field. Tests should cover default user, deprecated key warning/path, preservation of authenticated users, wrapper principal behavior, and ACL interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/lib/StaticUserWebFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/package-info.java

Purpose: package-level metadata for `org.apache.hadoop.http`.

Important APIs, types, and functions: declares the package as support for embedded HTTP services, with audience `LimitedPrivate` for HBase, HDFS, and MapReduce, and stability `Unstable`.

Control flow: no runtime control flow.

State and persistence: no state.

Dependencies and integration points: documents the intended consumers and stability level for the HTTP support package.

Risks and test signals: no direct runtime risk. Compatibility review should treat public-looking classes in this package according to the package stability annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/AbstractMapWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/AbstractMapWritable.java

Purpose: abstract base for `MapWritable` and `SortedMapWritable` class-id serialization. It stores per-instance mappings from writable classes to compact byte identifiers so nested maps can carry their own type tables.

Important APIs, types, and functions: predefined negative IDs cover common Hadoop writables. `addToMap(Class, byte)` and `addToMap(Class)` register classes. `getClass(byte)` and `getId(Class)` resolve mappings. `copy(Writable)` round-trips through `DataOutputBuffer`/`DataInputBuffer`. `write()` serializes new class mappings; `readFields()` loads them with the thread context class loader. It also implements `Configurable`.

Control flow: subclasses write this class table before their map entries, then use ids to encode key/value classes. Reads restore the table before entries are read.

State and persistence: instance state includes concurrent class/id maps, volatile count of new classes, and atomic configuration reference. Serialized persistence is the class table followed by subclass data.

Dependencies and integration points: used by Hadoop writable map implementations, `WritableFactories`, and configuration-aware serializers.

Risks and test signals: only 127 positive dynamic classes are allowed per instance. Loading arbitrary serialized class names depends on classpath and context class loader. Tests should cover duplicate id/class rejection, dynamic class limits, copy constructors, nested maps, missing class failures, and wire compatibility of predefined ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/AbstractMapWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayFile.java

Purpose: dense file-backed array abstraction implemented on top of `MapFile` with monotonically increasing long keys.

Important APIs, types, and functions: `ArrayFile.Writer` extends `MapFile.Writer`, fixes the key class to `LongWritable`, and `append(Writable)` writes at the current count then increments it. `ArrayFile.Reader` extends `MapFile.Reader` and exposes `seek(long)`, `next(Writable)`, `key()`, and `get(long, Writable)` using a reusable `LongWritable` key.

Control flow: writing appends values in order with implicit indexes. Reading seeks or gets by numeric index and delegates to `MapFile` lookup/iteration.

State and persistence: writer state is the current count. reader state is the reusable key holding the most recent index. Persistent data is the underlying MapFile directory with sequence data and index files.

Dependencies and integration points: depends on Hadoop `FileSystem`, `Path`, `MapFile`, `LongWritable`, `SequenceFile.CompressionType`, and progress callbacks.

Risks and test signals: callers must append in dense order; random writes are not supported. Tests should cover compressed and uncompressed writers, seek/next/get semantics, key reporting, empty/missing index behavior, and MapFile compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayPrimitiveWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayPrimitiveWritable.java

Purpose: writable wrapper for primitive Java arrays with a compact per-element binary representation and no object allocation per element.

Important APIs, types, and functions: constructors optionally declare a required component type. `set(Object)` validates non-null primitive arrays and stores the original array without copying. `write()` writes the primitive component type name through deprecated UTF8, writes length, then writes elements using type-specific loops. `readFields()` reads type and length, validates declared type, allocates a primitive array, and fills it. Nested `Internal` is used by `ObjectWritable`.

Control flow: serialization selects the primitive branch once, then loops over array elements. Deserialization mirrors the branch after allocating an array with `Array.newInstance()`.

State and persistence: state includes component type, optional declared component type, length, and the backing primitive array. Serialized form is type name, int length, and raw primitive values.

Dependencies and integration points: used by `ObjectWritable` for primitive array transport and depends on Hadoop exception types and legacy UTF8 string helpers.

Risks and test signals: constructor and `set()` alias the caller's array, so later mutations affect serialized output. Negative lengths are rejected, but very large lengths can allocate large arrays. Tests should cover all primitive types, declared-type enforcement, null/non-array/object-array rejection, negative length rejection, aliasing behavior, and ObjectWritable interop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayPrimitiveWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayWritable.java

Purpose: writable wrapper for homogeneous arrays of `Writable` objects.

Important APIs, types, and functions: constructors set a non-null `valueClass` and optional values. `toStrings()` maps each value to `toString()`. `toArray()` returns a shallow copy of the writable array. `set()` and `get()` manage the value array. `readFields()` reads an int length, instantiates each element with `WritableFactories.newInstance(valueClass)`, and reads it. `write()` writes length and each element.

Control flow: serialization and deserialization are sequential and depend on all elements sharing the declared class.

State and persistence: state is the declared value class and writable array. Serialized form omits the value class, so readers must be constructed with the correct class.

Dependencies and integration points: used by MapReduce and writable serialization APIs; string constructor uses deprecated `UTF8` values under `Text.class`.

Risks and test signals: `values` can be null until set, causing write/toStrings failures. Serialized data cannot self-describe element type. Tests should cover read/write round trips, subclass constructors for reducer use, empty arrays, null value arrays, shallow copy behavior, and factory configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BinaryComparable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BinaryComparable.java

Purpose: abstract comparable base for types whose ordering, equality, and hash code are defined by a byte prefix.

Important APIs, types, and functions: subclasses implement `getLength()` and `getBytes()`. `compareTo(BinaryComparable)` and `compareTo(byte[], off, len)` delegate to `WritableComparator.compareBytes()`. `equals()` checks type and length before comparing bytes. `hashCode()` delegates to `WritableComparator.hashBytes()`.

Control flow: callers compare the valid range `[0, getLength())` of the returned backing byte array.

State and persistence: no state in the base class; subclass backing bytes provide behavior.

Dependencies and integration points: base for byte-oriented writables such as `BytesWritable` and `Text`.

Risks and test signals: subclasses must ensure `getBytes()` has at least `getLength()` valid bytes and stable contents while used as keys. Tests should cover lexicographic ordering, equality/hash consistency, prefix differences, and mutable backing array hazards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BinaryComparable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BloomMapFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BloomMapFile.java

Purpose: MapFile variant with an auxiliary dynamic Bloom filter to avoid expensive lookups for keys that are definitely absent.

Important APIs, types, and functions: `delete()` removes data, index, bloom file, and directory. `Writer` initializes a `DynamicBloomFilter` from configuration, adds each appended serialized key to the filter, and writes `bloom` on close. `Reader` loads the bloom file if present, `probablyHasKey()` tests membership, `get()` skips `MapFile.get()` when membership is false, and `getBloomFilter()` exposes the filter.

Control flow: writes go to the normal MapFile plus in-memory bloom filter; close persists the filter. Reads attempt to load the filter and fall back to normal MapFile behavior if it is unavailable.

State and persistence: writer stores filter parameters, reusable buffers, filesystem and directory. reader stores loaded filter and reusable key serialization buffers. Persistent state is a MapFile directory plus a `bloom` file.

Dependencies and integration points: depends on `MapFile`, `SequenceFile`, Hadoop `FileSystem`, compression codecs, `DynamicBloomFilter`, `Key`, and hash configuration.

Risks and test signals: Bloom filters can have false positives but not false negatives if key serialization is identical. Missing/corrupt bloom files degrade to full MapFile lookup. Tests should cover bloom creation, absent-key short circuit, fallback on missing bloom, compression options, delete cleanup, and configuration of size/error rate/hash type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BloomMapFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BooleanWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BooleanWritable.java

Purpose: writable comparable wrapper for boolean values with an optimized raw comparator.

Important APIs, types, and functions: `set()`, `get()`, `readFields()`, `write()`, `equals()`, `hashCode()`, `compareTo()`, and `toString()` implement boolean value behavior. Nested `Comparator` compares serialized bytes through `compareBytes()`, and the static block registers it.

Control flow: serialized form is one Java boolean. Ordering is false before true.

State and persistence: one boolean field. Persistent form is one byte as written by `DataOutput.writeBoolean()`.

Dependencies and integration points: participates in Hadoop writable sorting via `WritableComparator.define()`.

Risks and test signals: hash code returns 0 for true and 1 for false, which is valid but inverted from some conventions. Tests should cover round trip, sort order, raw comparator behavior, equals/hash consistency, and comparator registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BooleanWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BoundedByteArrayOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BoundedByteArrayOutputStream.java

Purpose: reusable byte-array-backed `OutputStream` that enforces a write limit smaller than or equal to its backing capacity.

Important APIs, types, and functions: constructors allocate or accept a buffer. `resetBuffer()` validates offset/limit and initializes positions. `write(int)` and `write(byte[], off, len)` append while throwing `EOFException` on limit overflow. `reset(int)` and `reset()` reuse the buffer with a new limit. `getLimit()`, `getBuffer()`, `size()`, and `available()` expose buffer state.

Control flow: every write checks bounds before mutating the buffer and advances `currentPointer` on success.

State and persistence: state is the backing byte array, start offset, absolute limit, and current pointer. No external persistence; callers may consume the backing buffer.

Dependencies and integration points: limited-private utility for HDFS/MapReduce serialization paths.

Risks and test signals: `reset(int)` stores `limit` as the provided value rather than `startOffset + newlim`, unlike `resetBuffer()`, which is risky for non-zero start offsets. Tests should cover overflow exceptions, offset-backed buffers, reset semantics, available/size, zero-length writes, and bounds checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BoundedByteArrayOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ByteBufferPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ByteBufferPool.java

Purpose: public interface for pooling heap or direct `ByteBuffer` instances.

Important APIs, types, and functions: `getBuffer(boolean direct, int length)` returns a buffer with at least one byte and generally at least the requested length. `putBuffer(ByteBuffer)` returns a buffer to the pool. Default `release()` is a no-op hook for implementations that can clear resources.

Control flow: users borrow, use, and return buffers. Implementations choose whether to allocate or reuse.

State and persistence: no state in the interface.

Dependencies and integration points: used by Hadoop IO paths that want reusable direct buffers, with `ElasticByteBufferPool` as a simple implementation.

Risks and test signals: the Javadoc says direct in one sentence but the method supports both direct and heap buffers; callers must respect the `direct` flag. Tests for implementations should cover requested length, directness, clearing, reuse, and release semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ByteBufferPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ByteWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ByteWritable.java

Purpose: writable comparable wrapper for a single signed byte with an optimized raw comparator.

Important APIs, types, and functions: `set()`, `get()`, `readFields()`, `write()`, `equals()`, `hashCode()`, `compareTo()`, and `toString()` implement byte value behavior. Nested `Comparator` compares the first serialized byte at each offset and is registered statically.

Control flow: serialized form is one byte. Ordering is signed-byte numeric order.

State and persistence: one byte field, persisted as one byte.

Dependencies and integration points: integrates with Hadoop sort/shuffle via `WritableComparator`.

Risks and test signals: raw comparator ignores lengths and assumes valid one-byte serialized values. Tests should cover negative/positive ordering, round trip, comparator registration, and equals/hash consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ByteWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BytesWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BytesWritable.java

Purpose: resizable byte sequence usable as a Hadoop key or value. It separates logical length from backing-array capacity and orders bytes lexicographically.

Important APIs, types, and functions: constructors can alias an input byte array. `copyBytes()` returns an exact copy, while `getBytes()` exposes backing storage. `getLength()`, `setSize()`, `getCapacity()`, `setCapacity()`, and `set()` manage storage. `readFields()` reads an int length then bytes. `write()` writes length then valid bytes. `toString()` emits hex pairs. Nested `Comparator` skips the four length bytes in serialized form and compares payload bytes.

Control flow: resizing grows capacity to roughly 1.5 times requested size capped at `Integer.MAX_VALUE - 8`. Reads clear old size, allocate/grow, and fill the valid range.

State and persistence: state is logical size and byte array. Serialized form is four-byte length plus payload.

Dependencies and integration points: extends `BinaryComparable` and registers an optimized `WritableComparator`.

Risks and test signals: constructors and `getBytes()` expose mutable backing arrays. `setSize()` lacks explicit negative validation, so negative size paths should be tested. Tests should cover capacity growth/shrink, copy versus alias semantics, serialized comparator, empty values, large sizes, and hex output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BytesWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Closeable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Closeable.java

Purpose: deprecated Hadoop alias for `java.io.Closeable`.

Important APIs, types, and functions: the interface extends `java.io.Closeable` and adds no methods.

Control flow: no control flow.

State and persistence: no state.

Dependencies and integration points: retained for source and binary compatibility with older Hadoop APIs.

Risks and test signals: low runtime risk. Compatibility tests should ensure old code compiling against `org.apache.hadoop.io.Closeable` still works while new code can use `java.io.Closeable` directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Closeable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/CompressedWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/CompressedWritable.java

Purpose: abstract writable base that stores its subclass fields in compressed form and inflates lazily on field access.

Important APIs, types, and functions: final `readFields()` reads compressed bytes. `ensureInflated()` inflates through `InflaterInputStream` and calls subclass `readFieldsCompressed()`. final `write()` compresses current fields through `writeCompressed()` with `Deflater.BEST_SPEED`, caches compressed bytes, and writes length plus bytes.

Control flow: after deserialization, data stays compressed until a subclass method calls `ensureInflated()`. On serialization, uncompressed state is compressed once and then reused until fields are modified by subclass logic.

State and persistence: state is the cached compressed byte array or null when inflated. Serialized form is compressed length and compressed payload.

Dependencies and integration points: used by large writable subclasses that benefit from lazy inflation and fast copying.

Risks and test signals: subclasses must call `ensureInflated()` before reading fields and must clear/update compressed cache if mutating fields. `ensureInflated()` wraps IOExceptions in RuntimeException. Tests should cover lazy read, repeated write cache reuse, mutation invalidation in subclasses, corrupt compressed data, and round-trip compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/CompressedWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataInputBuffer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataInputBuffer.java

Purpose: reusable `DataInputStream` over a byte array without allocating a new `ByteArrayInputStream` for each read.

Important APIs, types, and functions: nested `Buffer` extends `ByteArrayInputStream` and exposes `reset(input,start,length)`, `getData()`, `getPosition()`, and `getLength()`, with optimized `read`, `read(byte[],off,len)`, `skip`, and `available`. Outer `DataInputBuffer` exposes reset and position/length accessors.

Control flow: callers reset the buffer to a byte range and then use normal `DataInput` methods inherited from `DataInputStream`.

State and persistence: state is the referenced byte array, current position, mark, and count. It aliases caller-provided input.

Dependencies and integration points: common utility for writable serialization, comparators, and map writable copy logic.

Risks and test signals: `getLength()` returns the absolute count index, not necessarily the logical length when start is non-zero. Tests should cover non-zero starts, EOF behavior, skip bounds, readFully through `DataInputStream`, and aliasing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataInputBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataInputByteBuffer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataInputByteBuffer.java

Purpose: `DataInputStream` implementation over one or more `ByteBuffer` instances.

Important APIs, types, and functions: nested `Buffer` is an `InputStream` over a `ByteBuffer[]`, tracks current buffer index, position, and total length. `reset(ByteBuffer...)` installs input buffers and computes remaining bytes. `read()` and `read(byte[],off,len)` consume from current buffers. Accessors expose underlying buffers, consumed position, and total length.

Control flow: reads advance the positions of the supplied ByteBuffers. Multi-buffer reads continue into later buffers until requested length is satisfied or buffers are exhausted.

State and persistence: state is the ByteBuffer array and read cursors. It mutates the positions of caller-provided buffers and has no persistence.

Dependencies and integration points: useful for deserializing data already held in NIO buffers.

Risks and test signals: `read(byte[],off,len)` can return 0 if the current buffer has no remaining bytes and len is positive before advancing, which can surprise InputStream users. Tests should cover empty buffers, multi-buffer boundaries, position mutation, readFully behavior, and reset reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataInputByteBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataOutputBuffer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataOutputBuffer.java

Purpose: reusable `DataOutputStream` over an in-memory growing byte array.

Important APIs, types, and functions: nested `Buffer` exposes backing data and length, grows when writing from `DataInput`, and can temporarily set count. Outer methods include `getData()`, `getLength()`, `reset()`, `write(DataInput,int)`, `writeTo(OutputStream)`, and `writeInt(int, offset)` for patching an existing four-byte slot.

Control flow: callers write through normal `DataOutput` methods, then consume the valid prefix of `getData()`. `writeInt(v, offset)` rewinds the internal count to overwrite bytes and restores the old count without increasing `DataOutputStream.written`.

State and persistence: state is the backing byte array, count, and inherited written byte count. No persistence except data copied by callers.

Dependencies and integration points: heavily used by writable serialization, BloomMapFile key encoding, and in-memory copy paths.

Risks and test signals: `getData()` exposes mutable extra-capacity bytes. `writeInt(offset)` can only overwrite existing bytes. Tests should cover growth, reset clearing written count, direct DataInput transfer, offset patching, and backing-array aliasing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataOutputBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataOutputOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataOutputOutputStream.java

Purpose: adapter that presents a `DataOutput` as an `OutputStream`.

Important APIs, types, and functions: static `constructOutputStream(DataOutput)` returns the argument directly if it is already an `OutputStream`, otherwise wraps it in `DataOutputOutputStream`. `write(int)`, `write(byte[],off,len)`, and `write(byte[])` delegate to the underlying `DataOutput`.

Control flow: stream writes become `DataOutput` byte writes, enabling APIs that require `OutputStream` to target `DataOutput` implementations.

State and persistence: state is the wrapped `DataOutput` reference. Persistence depends on the wrapped target.

Dependencies and integration points: useful for serializers and compression streams that accept only `OutputStream`.

Risks and test signals: no flush or close behavior is added when wrapping non-stream `DataOutput`. Tests should cover direct return for existing streams, byte and array writes, and interaction with `DataOutputBuffer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataOutputOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DefaultStringifier.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DefaultStringifier.java

Purpose: default `Stringifier` implementation that converts objects to Base64 strings using Hadoop serialization and restores them from those strings. It also provides configuration storage helpers.

Important APIs, types, and functions: constructor obtains `Serializer` and `Deserializer` from `SerializationFactory` and opens them on reusable buffers. `toString(T)` serializes to `DataOutputBuffer` and Base64 encodes. `fromString(String)` Base64 decodes into `DataInputBuffer` and deserializes. Static `store/load` persist one value in `Configuration`; `storeArray/loadArray` store comma-separated Base64 values.

Control flow: every conversion resets the reusable buffer before serializing/deserializing. Static helpers create a stringifier, use it, and close it in finally paths for load/arrays.

State and persistence: instance state includes serializer, deserializer, and buffers. Persistent state is configuration key strings containing Base64 payloads.

Dependencies and integration points: depends on Hadoop serialization framework, commons-codec Base64, `GenericsUtil`, and configuration.

Risks and test signals: constructor does not validate missing serializer/deserializer before `open()`. `load()` and `loadArray()` fail if the key is missing. `storeArray()` rejects empty arrays and uses the first element's class for all items. Tests should cover writable and custom serializers, missing keys, empty arrays, comma separator safety, close behavior, and mixed-subclass arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DefaultStringifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DoubleWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DoubleWritable.java

Purpose: writable comparable wrapper for double values with an optimized serialized comparator.

Important APIs, types, and functions: `readFields()`/`write()` use `DataInput.readDouble()` and `DataOutput.writeDouble()`. `set()`, `get()`, `equals()`, `hashCode()`, `compareTo()`, and `toString()` implement value behavior. Nested `Comparator` uses `WritableComparator.readDouble()` and `Double.compare()`.

Control flow: serialized form is eight bytes in `DataOutput` double format. Ordering follows `Double.compare`, including NaN and signed-zero semantics for compare.

State and persistence: one double field.

Dependencies and integration points: registered with `WritableComparator` for Hadoop sort/shuffle.

Risks and test signals: `equals()` uses `==`, so NaN is not equal to itself while `Double.compare()` treats NaN consistently for ordering; signed zero equality also differs from compare/hash expectations. Tests should cover NaN, signed zero, raw comparator, round trip, and equals/hash behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DoubleWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ElasticByteBufferPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ElasticByteBufferPool.java

Purpose: simple unbounded heap/direct `ByteBufferPool` that allocates on demand and caches returned buffers by capacity.

Important APIs, types, and functions: nested `Key` orders buffers by capacity and insertion time. `getBuffer(direct,length)` finds the smallest cached buffer with capacity at least length or allocates a new heap/direct buffer. `putBuffer()` clears and inserts by `(capacity, System.nanoTime())`, retrying on duplicate keys. `size(boolean direct)` reports cached buffer count.

Control flow: all pool operations are synchronized. Returned buffers are cleared before use; inserted buffers are cleared before caching.

State and persistence: two `TreeMap<Key, ByteBuffer>` instances store heap and direct buffers. No persistence and no default maximum cache size.

Dependencies and integration points: implements `ByteBufferPool`; used by Hadoop IO paths that want simple buffer reuse.

Risks and test signals: because the cache is unbounded, workloads returning many large buffers can retain memory/direct memory. Tests should cover smallest-sufficient reuse, direct/heap separation, clear semantics, size reporting, duplicate timestamp retry, and memory retention behavior under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ElasticByteBufferPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/EnumSetWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/EnumSetWritable.java

Purpose: writable wrapper around `EnumSet` that preserves enum element type even for null or empty sets.

Important APIs, types, and functions: constructors and `set(EnumSet,EClass)` validate that null/empty values have an element type. Collection methods delegate to the underlying set. `write()` writes -1 for null, 0 for empty with class name, or count plus each enum via `ObjectWritable`. `readFields()` reconstructs null, empty, or populated sets using configuration-aware class loading. It implements `Configurable` and registers a `WritableFactory`.

Control flow: populated reads deserialize the first enum to create `EnumSet.of(first)`, then add remaining elements. Empty reads load the element class name and create `EnumSet.noneOf()`.

State and persistence: state is the enum set, transient element type, and transient configuration. Serialized form includes length and, when needed, element class or serialized enum elements.

Dependencies and integration points: depends on `ObjectWritable`, `WritableUtils`, configuration, and writable factories.

Risks and test signals: `write()` for null assumes `elementType` is non-null; `equals(null)` throws instead of returning false. Tests should cover null set with type, empty set with type, populated sets, config class loading, add-on-null behavior, equals/hash edge cases, and factory instantiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/EnumSetWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/FloatWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/FloatWritable.java

Purpose: writable comparable wrapper for float values with an optimized raw comparator.

Important APIs, types, and functions: `set()`, `get()`, `readFields()`, `write()`, `equals()`, `hashCode()`, `compareTo()`, and `toString()` implement float value behavior. Nested `Comparator` reads serialized floats via `WritableComparator.readFloat()` and compares with `Float.compare()`.

Control flow: serialized form is four bytes in `DataOutput` float format. Ordering follows `Float.compare`.

State and persistence: one float field.

Dependencies and integration points: registered with `WritableComparator` for Hadoop sorting.

Risks and test signals: like `DoubleWritable`, `equals()` uses `==`, so NaN and signed-zero semantics differ from comparator/hash behavior. Tests should cover NaN, signed zero, raw comparator, round trip, and comparator registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/FloatWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/GenericWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/GenericWritable.java

Purpose: compact tagged-union wrapper for a fixed set of `Writable` implementation classes. It avoids writing a class name with every value by serializing a one-byte type index.

Important APIs, types, and functions: subclasses implement `getTypes()` with the allowed writable classes. `set(Writable)` records the instance and matching type index. `get()` returns the wrapped instance. `write()` writes the type byte then delegates to the instance. `readFields()` reads the unsigned type index, instantiates the registered class with `ReflectionUtils.newInstance(clazz, conf)`, and reads its fields. It implements `Configurable` so configuration reaches wrapped instances before deserialization.

Control flow: producers must call `set()` with a registered exact class before writing. Consumers must use the same `getTypes()` order to decode the type byte.

State and persistence: state is the type byte, wrapped instance, and configuration. Serialized form is one type byte plus the wrapped writable payload.

Dependencies and integration points: used when MapReduce sequence files need multiple value types under one declared value class.

Risks and test signals: only exact class equality is accepted, not subclasses. Type indexes are one byte, so practical type count is limited and ordering is a wire contract. `readFields()` does not validate bounds before indexing. Tests should cover each registered type, unregistered set failure, unset write failure, type-order compatibility, configuration propagation, and malformed type bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/GenericWritable.java -->

# Research Report: subset-b-007430

Grouped research for Hadoop HttpFS server and supporting service framework sources. Each section preserves the exact source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/FSOperations.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/FSOperations.java

## Purpose
`FSOperations` is the executor library behind `HttpFSServer`: each nested class adapts one HttpFS/WebHDFS operation into a `FileSystemAccess.FileSystemExecutor<T>` that runs against an authenticated Hadoop `FileSystem`. It also owns the JSON wire-shape helpers for file status, directory listings, ACLs, checksums, xattrs, quota/content summaries, storage policies, block locations, fs status, snapshot data, and erasure-coding responses.

## Important APIs, Types, And Functions
The file is a final utility class with a configurable static `bufferSize` set by `setBufferSize(Configuration)`. Core helpers include `toJson(FileStatus)`, `toJson(FileStatus[], boolean)`, `toJson(FileSystem.DirectoryEntries, boolean)`, `aclStatusToJSON`, `fileChecksumToJSON`, `xAttrsToJSON`, `contentSummaryToJSON`, `quotaUsageToJSON`, `storagePoliciesToJSON`, and `copyBytes`. Nested executors cover create, append, concat, truncate, delete, open, rename, mkdirs, status/listing, batched listing, checksum, content/quota, ACL mutation and lookup, ownership/permission/times/replication, xattr mutation and lookup, trash roots, storage policies, snapshots, block locations, fs status, access checks, and erasure-coding policy/codecs.

## Control Flow
`HttpFSServer` constructs the relevant executor, then `FileSystemAccessService.execute` supplies a per-user `FileSystem` and invokes `execute(FileSystem)`. Most executors are thin one-method wrappers over Hadoop `FileSystem` calls. `FSCreate` and `FSAppend` stream request bodies through `copyBytes`, close both streams, and increment bytes-written metrics. `FSOpen` returns an `InputStream`; the servlet entity owns byte accounting. HDFS-only operations check `fs instanceof DistributedFileSystem` and throw `UnsupportedOperationException` otherwise.

## State And Persistence
State is intentionally transient: each executor stores only parsed constructor arguments such as `Path`, permissions, flags, names, offsets, and lengths. Persistent effects are delegated to HDFS or the configured filesystem. Static mutable state is limited to `bufferSize`, which affects streaming and open/create/append buffer allocation process-wide.

## Dependencies And Integration Points
The class depends heavily on Hadoop `FileSystem`, HDFS protocol classes, `JsonUtil`, `HttpFSFileSystem` JSON constants, ACL/xattr/permission types, and `HttpFSServerWebApp.get().getMetrics()`. It integrates with `FileSystemAccess` by implementing its executor contract and with client compatibility by preserving WebHDFS-compatible JSON key names.

## Risks
HDFS-only features fail at runtime when `fs.defaultFS` is not a `DistributedFileSystem`. `copyBytes` always closes both streams, so callers must not reuse request or output streams after execution. `xAttrNamesToJSON` stores a JSON string under the xattr names key rather than a raw array, which is compatibility-sensitive. `FSCreateSnapshot` uses `HOME_DIR_JSON` as the response key and strips backslashes from JSON, a brittle behavior worth regression testing. `FSSatisyStoragePolicy` contains a misspelled class name but maps to a real operation.

## Test Signals
Useful tests exercise JSON output compatibility for status/listing/quota/xattrs/storage policy, stream close and byte metrics for create/append/open, access-mode behavior via `HttpFSServer`, HDFS-only operation failure on a non-DFS `FileSystem`, and default replication/block-size/umask handling in `FSCreate` and `FSMkdirs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/FSOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSAuthenticationFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSAuthenticationFilter.java

## Purpose
`HttpFSAuthenticationFilter` customizes Hadoop delegation-token authentication for HttpFS. It pulls authentication properties from the active `HttpFSServerWebApp` configuration, loads the signing secret, exposes proxy-user configuration, and selects the WebHDFS or SWebHDFS delegation token kind based on SSL.

## Important APIs, Types, And Functions
The class extends `DelegationTokenAuthenticationFilter`. Constants define accepted configuration prefixes: `httpfs.authentication.` and `hadoop.http.authentication.`. `getConfiguration` uses `HttpServer2.getFilterProperties`, enforces a `signature.secret.file` property, reads the secret unless a random signer provider is already installed, calls `setAuthHandlerClass`, and sets `KerberosDelegationTokenAuthenticationHandler.TOKEN_KIND`. `getProxyuserConfiguration` rewrites `httpfs.proxyuser.*` properties to Hadoop proxyuser keys by removing the `httpfs.` prefix. `isRandomSecret` checks the servlet context's signer secret provider.

## Control Flow
During filter initialization, Hadoop auth calls `getConfiguration`. The method reads server config via the HttpFS singleton, materializes `Properties`, validates/reads the signature secret, configures the auth handler, and returns auth properties to the parent filter. Proxy user data is pulled separately by `getProxyuserConfiguration`.

## State And Persistence
The filter stores no long-lived local state. The signature secret is read from disk at initialization and injected into the returned properties. Proxy-user data remains in Hadoop `Configuration`.

## Dependencies And Integration Points
It integrates with `HttpFSServerWebApp`, `HttpFSServerWebServer.SSL_ENABLED_KEY`, Hadoop auth, delegation-token handlers, servlet context signer providers, and WebHDFS token-kind constants.

## Risks
Missing, unreadable, or empty signature secret files fail initialization. Random secret mode bypasses file reading only when the servlet context provider class is exactly `RandomSignerSecretProvider`. Prefix rewriting for proxy users depends on the `httpfs.` prefix length and should be kept consistent with auth config names.

## Test Signals
Tests should cover secret-file loading, empty secret rejection, random-secret bypass, SSL vs non-SSL token kind, and proxyuser key rewriting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSAuthenticationFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSExceptionProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSExceptionProvider.java

## Purpose
`HttpFSExceptionProvider` is the Jersey exception mapper for HttpFS REST requests. It translates server and filesystem exceptions into HTTP responses and writes audit/server logs with request metadata from MDC.

## Important APIs, Types, And Functions
The class extends `org.apache.hadoop.lib.wsrs.ExceptionProvider` and is annotated with `@Provider`. `toResponse(Throwable)` unwraps `FileSystemAccessException` and Jersey `ContainerException`, then maps `SecurityException` to `401`, `FileNotFoundException` to `404`, `IOException` to `500`, `UnsupportedOperationException` and `IllegalArgumentException` to `400`, and unknown failures to `500`. `log(Response.Status, Throwable)` writes audit and server warnings using `method` and `path` MDC values. `logErrorFully` emits debug-level stack details for selected server-side failures.

## Control Flow
Jersey calls `toResponse` when an endpoint throws. The mapper normalizes wrapper exceptions before choosing a status, calls the inherited `createResponse`, and relies on the inherited provider to invoke logging behavior.

## State And Persistence
There is no persistent state. Side effects are HTTP response construction and log emission.

## Dependencies And Integration Points
It depends on Jersey, the shared `ExceptionProvider`, `FileSystemAccessException`, SLF4J, and MDC values set by HttpFS request filters/endpoints. It is central to how `HttpFSServer` executor failures surface to clients.

## Risks
`SecurityException` maps to unauthorized rather than forbidden, which is externally visible. `FileSystemAccessException` and `ContainerException` unwrapping assumes a meaningful cause; null causes could lead to less specific mapping. Full stack traces for IO/bad-request classes are only debug-level.

## Test Signals
Tests should assert status mappings, wrapper unwrapping, error body format inherited from `ExceptionProvider`, and audit log fields when MDC values are present or absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSExceptionProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSParametersProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSParametersProvider.java

## Purpose
`HttpFSParametersProvider` defines the request parameter schema for every `HttpFSFileSystem.Operation`. It is the validation layer that tells the shared WSRS parameter framework which query parameters are accepted and how they are parsed.

## Important APIs, Types, And Functions
The class extends `ParametersProvider` and initializes `PARAMS_DEF`, mapping each operation to an ordered array of `Param` classes. Nested param types cover booleans (`data`, `noredirect`, `recursive`, `allusers`), longs/integers (`offset`, `length`, times, block size, new length, snapshot diff index), strings (`filter`, owner/group, destination, sources, xattr names/values, storage/snapshot/ec policy names), shorts (`permission`, `unmaskedpermission`, replication), enums (`OperationParam`, `XAttrEncodingParam`), enum sets (`XAttrSetFlagParam`), and validated strings (`FsActionParam`, ACL spec, xattr name).

## Control Flow
`HttpFSServer.getParams(request)` delegates to this provider. The provider reads the `op` query parameter, resolves it to `HttpFSFileSystem.Operation`, then instantiates only the params registered for that operation. Endpoint methods then retrieve typed values by name and class.

## State And Persistence
The static `PARAMS_DEF` map is process-wide immutable after class loading in practice, though it is a mutable `HashMap`. Parameter objects are request-scoped. No persistent state is written.

## Dependencies And Integration Points
It depends on `HttpFSFileSystem` constants and operation enum, `org.apache.hadoop.lib.wsrs` parameter classes, Hadoop xattr enums, HDFS ACL regex config, and `HttpFSServerWebApp.get().get(FileSystemAccess.class)` for the ACL permission pattern.

## Risks
Adding an operation in `HttpFSServer` or `HttpFSFileSystem.Operation` without updating `PARAMS_DEF` breaks request parsing. `AclPermissionParam` consults the singleton webapp at construction time; it requires the `FileSystemAccess` service to be initialized. Some params default to permissive values (`overwrite=true`, default permission, replication/block size `-1`) and endpoint behavior depends on those sentinels. `SnapshotDiffIndexParam` defaults to null while the executor expects an `int`, so invalid missing input would fail during unboxing.

## Test Signals
Tests should validate each operation's accepted parameter set, default values, invalid enum/action/xattr/ACL formats, ACL regex configuration wiring, and parity between switch cases in `HttpFSServer` and `PARAMS_DEF`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSParametersProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSReleaseFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSReleaseFilter.java

## Purpose
`HttpFSReleaseFilter` connects the generic filesystem-release servlet filter to the HttpFS service registry. Its only role is to ensure unmanaged `FileSystem` instances created for request streaming are released at servlet request completion.

## Important APIs, Types, And Functions
The class extends `FileSystemReleaseFilter` and overrides `getFileSystemAccess()` to return `HttpFSServerWebApp.get().get(FileSystemAccess.class)`.

## Control Flow
`HttpFSServer.createFileSystem` creates an unmanaged filesystem for operations like `OPEN`, stores it in `FileSystemReleaseFilter.setFileSystem(fs)`, and the filter later calls the returned `FileSystemAccess` service to release it.

## State And Persistence
The class has no fields. State is maintained by the parent filter, likely request-local/thread-local, and by `FileSystemAccessService`'s cache.

## Dependencies And Integration Points
It depends on `HttpFSServerWebApp`, `FileSystemAccess`, and `FileSystemReleaseFilter`. It is part of the streaming response cleanup path.

## Risks
If the webapp singleton is not initialized or the `FileSystemAccess` service is missing, request cleanup can fail. Correct filter ordering is required so it wraps requests that call `setFileSystem`.

## Test Signals
Tests should verify that a filesystem set during request handling is released exactly once and that open-stream responses do not leak unmanaged filesystem counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSReleaseFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServer.java

## Purpose
`HttpFSServer` is the Jersey REST resource that exposes the HttpFS/WebHDFS API under the service version path. It binds HTTP verbs plus the `op` query parameter to `FSOperations` executors, applies access-mode restrictions, performs user/file-system setup, handles upload/open redirects, and builds HTTP responses.

## Important APIs, Types, And Functions
The class is annotated `@Path(HttpFSFileSystem.SERVICE_VERSION)`. Public endpoints are `getRoot`, `get`, `delete`, `postRoot`, `post`, `putRoot`, and `put`. Helpers include `getHttpUGI`, `getParams`, `fsExecute`, `createFileSystem`, `enforceRootPath`, `makeAbsolute`, `createOpenRedirectionURL`, and `createUploadRedirectionURL`. `AccessMode` supports `READWRITE`, `WRITEONLY`, and `READONLY` via `httpfs.access.mode`.

## Control Flow
Each endpoint parses parameters through `HttpFSParametersProvider`, records MDC fields, normalizes paths, switches on `op.value()`, constructs an `FSOperations` command, and either calls `fsExecute` or uses an unmanaged `FileSystem` for streaming. GET handles read/status/list/instrumentation/snapshot/defaults/ec/block-location operations. DELETE handles delete and delete snapshot. POST handles append, concat, truncate, and unset policy operations. PUT handles create, mkdirs, rename, metadata mutation, ACL/xattr mutation, snapshots, storage policy, and EC policy changes. Upload operations use a two-step redirect/data flow controlled by `data` and `noredirect`; `OPEN` and checksum support `noredirect`.

## State And Persistence
Per-instance state is limited to `accessMode`; request state is held in local variables and MDC. Persistent effects occur through delegated filesystem operations. Streaming `OPEN` stores an unmanaged `FileSystem` in the release filter for cleanup after response completion.

## Dependencies And Integration Points
It integrates with Jersey, servlet requests, `HttpUserGroupInformation`, `UserGroupInformation`, `FileSystemAccess`, `Groups`, `Instrumentation`, `InputStreamEntity`, `HttpFSExceptionProvider`, `HttpFSParametersProvider`, `FSOperations`, audit logging, and the metrics accessed from executors.

## Risks
Some methods call `HttpUserGroupInformation.get()` directly rather than the fallback `getHttpUGI`, so deployments without that filter path need coverage. Access-mode restrictions are verb-level and GET write-only allows only status/list. Streaming `OPEN` catches `InterruptedException` but may continue with a null stream. Operation/parameter mismatches can surface as runtime failures. Admin-only instrumentation depends on group service accuracy.

## Test Signals
Tests should cover every verb switch case, invalid operation errors, read-only/write-only forbiddance, root-only operations, upload redirect/no-redirect/data modes, unmanaged filesystem release for open, admin group enforcement, audit MDC/logging, and JSON/content-type/status-code compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServerWebApp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServerWebApp.java

## Purpose
`HttpFSServerWebApp` is the servlet-context bootstrap object for HttpFS. It extends the generic `ServerWebApp`, installs the global singleton, initializes services/configuration, records the admin group, initializes HttpFS metrics, and tears everything down on webapp destruction.

## Important APIs, Types, And Functions
Constants define server name `httpfs` and `admin.group`. Constructors support production and tests. `init()` enforces a single active instance, calls `super.init()`, reads `httpfs.admin.group` defaulting to `admin`, logs the target NameNode, and calls `setMetrics`. `destroy()` clears the singleton, shuts down metrics, and delegates to the parent. Static `get()` and `getMetrics()` expose singleton state.

## Control Flow
The servlet container creates this listener. Initialization establishes `SERVER` before service initialization so filters/resources can read configuration. Metrics setup creates `HttpFSServerMetrics`, starts a `JvmPauseMonitor`, wires it into JVM metrics, sets `FSOperations` buffer size, and initializes the default metrics system.

## State And Persistence
Static fields hold the active webapp and metrics singleton. Instance state holds `adminGroup`. No persistent data is written, but metrics and pause monitoring are process-wide side effects.

## Dependencies And Integration Points
It depends on `ServerWebApp`, `FileSystemAccess`, `HttpFSServerMetrics`, Hadoop metrics2, `JvmPauseMonitor`, `DefaultMetricsSystem`, and `FSOperations`.

## Risks
Double initialization throws a runtime exception. Metrics initialization and shutdown use static/default metrics systems also touched by `HttpFSServerWebServer`, so lifecycle order matters in tests. `SERVER` is set before `super.init()`, so a failed initialization can leave partial singleton state unless destroyed by the container.

## Test Signals
Tests should cover singleton behavior, admin group default/config override, metrics creation/shutdown, buffer-size propagation, and failure cleanup around repeated initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServerWebApp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServerWebServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServerWebServer.java

## Purpose
`HttpFSServerWebServer` is the standalone HttpFS Jetty/HttpServer2 launcher. It loads HttpFS default/site resources, handles deprecated environment overrides, builds the HTTP or HTTPS endpoint, configures authentication filter prefixes and admin ACLs, and exposes lifecycle methods for start/join/stop.

## Important APIs, Types, And Functions
Constants define config resources, host/port/SSL keys, administrators key, server name `webhdfs`, and servlet path `/webhdfs`. The constructor applies `deprecateEnv` overrides, determines scheme, builds the endpoint URI, removes default auth/proxy filter initializers that HttpFS replaces, and constructs `HttpServer2`. `start`, `join`, `stop`, `getUrl`, `getHttpServer`, `main`, and `addDeprecatedKeys` provide lifecycle and compatibility hooks.

## Control Flow
Static initialization registers deprecated key aliases and default resources. `main` creates a normal Hadoop `Configuration`, reads SSL server configuration, constructs the server, starts it, and blocks in `join`. `start` initializes metrics system `httpfs`; `stop` stops Jetty and shuts metrics down.

## State And Persistence
Instance state is the built `HttpServer2` and selected scheme. Configuration may be mutated by deprecated environment overrides and filter initializer cleanup. No files are written.

## Dependencies And Integration Points
It integrates with `HttpServer2`, `SSLFactory`, Hadoop auth initializers, `HttpFSAuthenticationFilter`, metrics2, ACLs, and Hadoop configuration deprecation APIs.

## Risks
Deprecated environment variables silently override config after logging warnings. Filter initializer filtering only removes exact class names. `getUrl` returns null before connector bind. Metrics shutdown here can interact with webapp metrics lifecycle.

## Test Signals
Tests should validate endpoint URL construction for HTTP/HTTPS, deprecated env override behavior, auth initializer filtering, deprecated key registration, admin ACL propagation, and lifecycle start/stop with metrics cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServerWebServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/metrics/HttpFSServerMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/metrics/HttpFSServerMetrics.java

## Purpose
`HttpFSServerMetrics` is the metrics2 source for HttpFS server activity. It exposes counters for bytes and selected read/write operations and attaches JVM metrics for the server.

## Important APIs, Types, And Functions
The class is annotated `@Metrics(context="httpfs")`. Mutable counters include `bytesWritten`, `bytesRead`, create/append/truncate/delete/rename/mkdir, open/listing/stat/checkAccess/status/allECPolicies/ECCodecs/trashRoots. `create(Configuration, String)` registers a named source in `DefaultMetricsSystem`, creates `JvmMetrics`, and derives a sanitized source name. Increment methods update counters; getters expose a few values for tests; `shutdown` shuts the default metrics system.

## Control Flow
`HttpFSServerWebApp.setMetrics` calls `create`, then `FSOperations` executors increment counters during request execution. JVM pause monitor integration is completed by the webapp via `getJvmMetrics()`.

## State And Persistence
Metrics counters are in memory and exported through Hadoop metrics/JMX. The registry tags `SessionId`. Shutdown affects the process-wide default metrics system.

## Dependencies And Integration Points
It depends on Hadoop metrics2 annotations, `DefaultMetricsSystem`, `MutableCounterLong`, DFS metrics session id config, `JvmMetrics`, and `FSOperations`/`HttpFSServerWebApp` callers.

## Risks
Only some operations are counted; ACL/xattr/storage-policy/snapshot mutations have little direct metric coverage. Calling `shutdown` on the default metrics system may affect other metrics sources in the same JVM. Counter fields are injected by metrics2 registration and should not be used before registration.

## Test Signals
Tests should confirm registration names, session tags, counter increments from representative operations, JVM metrics attachment, and shutdown behavior in isolated metrics systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/metrics/HttpFSServerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/metrics/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/metrics/package-info.java

## Purpose
This package descriptor documents and annotates the HttpFS server metrics package.

## Important APIs, Types, And Functions
It applies `@InterfaceAudience.Public` and `@InterfaceStability.Evolving` to `org.apache.hadoop.fs.http.server.metrics`. It contains no executable functions.

## Control Flow
There is no runtime control flow. The annotations are compile-time/package metadata consumed by documentation and compatibility tooling.

## State And Persistence
No state is created or persisted.

## Dependencies And Integration Points
It imports Hadoop classification annotations and applies them to the metrics package containing `HttpFSServerMetrics`.

## Risks
The package is marked public/evolving even though the metrics class itself is private; changing package-level annotations can affect generated docs or downstream compatibility expectations.

## Test Signals
No behavioral tests are required; source/javadoc checks can verify package annotations remain intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/metrics/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/lang/RunnableCallable.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/lang/RunnableCallable.java

## Purpose
`RunnableCallable` adapts either a `Runnable` or a `Callable<?>` so it can be scheduled or invoked through either Java concurrency interface.

## Important APIs, Types, And Functions
The class implements `Callable<Void>` and `Runnable`. It has two constructors, one accepting a non-null `Runnable` and one accepting a non-null `Callable<?>`, validated by `Check.notNull`. `call()` invokes the wrapped runnable or callable and always returns null. `run()` invokes the runnable directly or calls the callable and wraps checked exceptions in `RuntimeException`. `toString()` returns the wrapped class simple name.

## Control Flow
`SchedulerService.schedule(Runnable, ...)` wraps a runnable in `RunnableCallable`, then treats it as a callable for instrumentation and fixed-delay scheduling.

## State And Persistence
Each instance stores exactly one delegate. There is no persistence or shared state.

## Dependencies And Integration Points
It depends on `java.util.concurrent.Callable` and Hadoop `Check`. It bridges the scheduler service API overloads.

## Risks
Exceptions from callable execution are preserved in `call()` but wrapped in `run()`, so callers may see different exception types depending on invocation path. `toString()` assumes a delegate exists, which constructors enforce.

## Test Signals
Tests should verify runnable and callable invocation, null rejection, checked exception wrapping in `run`, checked exception propagation in `call`, and `toString` delegate naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/lang/RunnableCallable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/lang/XException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/lang/XException.java

## Purpose
`XException` is the base checked exception for this service framework. It standardizes coded errors with `MessageFormat` templates and optional throwable causes.

## Important APIs, Types, And Functions
Nested interface `ERROR` requires `getTemplate()`. Constructors support wrapping another `XException` while preserving its code/message, or building a new exception from an error code and parameters. `getError()` returns the code. Static helpers `format` and `getCause` build the message and treat the final vararg as the cause if it is a `Throwable`.

## Control Flow
Subclasses such as `ServerException`, `ServiceException`, and `FileSystemAccessException` define enums implementing `ERROR`, then delegate construction to `XException`.

## State And Persistence
Instances store the error code and inherited message/cause. No persistence exists.

## Dependencies And Integration Points
It depends on `MessageFormat` and Hadoop `Check`. It is the common error contract for server/service initialization and filesystem access failures.

## Risks
If an error template is null, a positional fallback template is generated from all parameters, including a trailing throwable. `MessageFormat` syntax has quoting rules that can surprise authors of new templates. The wrapped-`XException` constructor uses the cause's formatted message rather than reformating.

## Test Signals
Tests should cover template formatting, null-template fallback, cause extraction only from the last arg, error preservation when wrapping, and subclass enum formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/lang/XException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/BaseService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/BaseService.java

## Purpose
`BaseService` is a convenience superclass for `Service` implementations. It captures the owning `Server`, extracts service-specific configuration by prefix, and supplies default no-op lifecycle/dependency hooks.

## Important APIs, Types, And Functions
The constructor stores a service prefix. Final `init(Server)` records the server, builds a new `Configuration(false)`, copies all resolved server config keys under `serverPrefix.servicePrefix.`, strips that prefix, and delegates to protected abstract `init()`. Defaults for `postInit`, `destroy`, `getServiceDependencies`, and `serverStatusChange` are no-ops/empty. Helpers expose `getPrefix`, `getServer`, `getPrefixedName`, and `getServiceConfig`.

## Control Flow
`Server.initServices` calls `service.init(this)` on each service. Subclasses implement protected `init()` and use the trimmed service config rather than parsing global keys directly.

## State And Persistence
Instance state is prefix, owning server, and a trimmed service configuration snapshot. No persistent data is written.

## Dependencies And Integration Points
It depends on Hadoop `Configuration`, `ConfigurationUtils.resolve`, and the `Service`/`Server` lifecycle. All concrete services in this subset extend it.

## Risks
The final `init(Server)` prevents subclasses from customizing the prefix extraction sequence. Config is copied at initialization; later server config changes are not reflected. Prefix matching is string-based, so malformed prefixes can leak or miss settings.

## Test Signals
Tests should verify prefix stripping, resolved-variable copying, default empty dependencies/status hooks, and subclass initialization seeing only trimmed service config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/BaseService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/Server.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/Server.java

## Purpose
`Server` is the generic runtime container used by HttpFS' `ServerWebApp`. It provides directory validation, configuration loading/overlay, log4j setup, service class loading and de-duplication, dependency-checked lifecycle management, status transitions, and service lookup.

## Important APIs, Types, And Functions
`Status` defines `UNDEF`, `BOOTING`, `HALTED`, `ADMIN`, `NORMAL`, `SHUTTING_DOWN`, and `SHUTDOWN`, with settable/operational flags. Constructors accept home/config/log/temp dirs and optional config. Key methods are `init`, `setStatus`, `ensureOperational`, `initLog`, `initConfig`, `loadServices`, `initServices`, `checkServiceDependencies`, `destroyServices`, `destroy`, `get`, and `setService`. Config constants are `services`, `services.ext`, and `startup.status`.

## Control Flow
`init()` moves from `UNDEF` to `BOOTING`, validates directories, loads build metadata, initializes logging, loads default/site/system-property config, loads service classes from base and extension lists, removes duplicate service interfaces with last implementation winning, initializes services in order, post-initializes all, then sets startup status from config. `destroy()` reverses service order and shuts log4j. `setStatus` notifies services and destroys the server on notification failure.

## State And Persistence
The server stores current status, directory paths, configuration, logger, and a `LinkedHashMap<Class, Service>` keyed by service interface. It reads config/log/build files but does not write state.

## Dependencies And Integration Points
It integrates with Hadoop `Configuration`, `ConfigurationUtils`, log4j, SLF4J, `ConfigRedactor`, service implementations, and classpath resources named after the server.

## Risks
`destroy()` calls `ensureOperational`, so destruction from non-operational states can throw. Service class instantiation uses deprecated no-arg `newInstance`. Missing build metadata resource causes a runtime exception. `getPrefixedName` rejects empty names via `Check.notEmpty`, while callers must pass non-empty suffixes. Programmatic `setService` initializes but does not post-init the replacement.

## Test Signals
Tests should cover config overlay/default injection, redacted system-property override logging, service de-duplication, dependency failure, reverse destroy order, status notifications and failure shutdown, and programmatic service replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/Server.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/ServerException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/ServerException.java

## Purpose
`ServerException` is the coded checked exception for failures in the `Server` lifecycle and service container.

## Important APIs, Types, And Functions
The `ERROR` enum implements `XException.ERROR` with codes `S01` through `S14` for missing directories, non-directories/files, resource/config load failures, invalid service interfaces, instantiation/load errors, programmatic service replacement, dependency failures, status-change failures, service startup failures, missing system properties, and initialization failure. Constructors delegate to `XException`.

## Control Flow
`Server` throws `ServerException` from validation, configuration, service loading, dependency checks, status transitions, and service replacement. `ServiceException` subclasses it for service-specific errors.

## State And Persistence
Each exception stores an error enum, message, and optional cause through `XException`. No persistence.

## Dependencies And Integration Points
It depends on `XException` and is consumed by `Server`, `BaseService` implementations, and `HttpFSServerWebApp.init`.

## Risks
Error messages are public enough to appear in logs and startup failures; spelling mistakes in templates are compatibility noise but not behavior. Protected constructor enables subclasses to pass their own error enums.

## Test Signals
Tests should assert formatting for representative enum values and that wrapped causes are preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/ServerException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/Service.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/Service.java

## Purpose
`Service` defines the managed component contract for the HttpFS service container.

## Important APIs, Types, And Functions
Methods include `init(Server)`, `postInit()`, `destroy()`, `getServiceDependencies()`, `getInterface()`, and `serverStatusChange(Server.Status, Server.Status)`. `getInterface()` is the key used by `Server.get(Class)` and de-duplication.

## Control Flow
`Server` loads configured service classes, validates each implementation against `getInterface`, checks declared dependencies against initialized services, calls `init`, later calls `postInit`, notifies status changes, and finally calls `destroy` in reverse order.

## State And Persistence
The interface itself has no state. Implementations hold service state.

## Dependencies And Integration Points
It depends on `Server` and `ServiceException`. Concrete implementations in this subset include filesystem access, instrumentation, scheduler, and groups.

## Risks
Implementations must return stable interface classes. Dependency arrays are checked only against already initialized services, making configured order significant. Exceptions in status notification can tear down the whole server.

## Test Signals
Container tests should use fake services to verify lifecycle order, dependency ordering, interface validation, and status-change failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/Service.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/ServiceException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/ServiceException.java

## Purpose
`ServiceException` is a thin subclass of `ServerException` used by `Service` implementations to report initialization and lifecycle failures.

## Important APIs, Types, And Functions
It exposes a single public constructor accepting any `XException.ERROR` plus parameters and delegates to `ServerException`.

## Control Flow
Concrete services throw it from `init` or `postInit`. `Server.initServices` catches `ServerException`, destroys already initialized services, and propagates failure.

## State And Persistence
No additional state beyond `ServerException` and `XException`.

## Dependencies And Integration Points
It depends on `ServerException` and `XException.ERROR`; service implementations often pass domain-specific error enums such as `FileSystemAccessException.ERROR`.

## Risks
Because it accepts any error enum, callers must choose meaningful codes. It does not add service identity automatically; callers should include context in parameters.

## Test Signals
Formatting and cause propagation are inherited; service initialization tests should confirm thrown `ServiceException` triggers container cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/ServiceException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/FileSystemAccess.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/FileSystemAccess.java

## Purpose
`FileSystemAccess` is the service interface that mediates all Hadoop `FileSystem` access for HttpFS.

## Important APIs, Types, And Functions
Nested `FileSystemExecutor<T>` defines `T execute(FileSystem fs) throws IOException`. Service methods are `execute(String user, Configuration conf, FileSystemExecutor<T> executor)`, `createFileSystem(String user, Configuration conf)`, `releaseFileSystem(FileSystem fs)`, and `getFileSystemConfiguration()`.

## Control Flow
`HttpFSServer` uses `execute` for short operations and `createFileSystem`/`releaseFileSystem` through the release filter for streaming responses. `FSOperations` supplies concrete executors.

## State And Persistence
The interface has no state. Implementations may cache filesystems and own configuration.

## Dependencies And Integration Points
It depends on Hadoop `Configuration`, `FileSystem`, and `IOException`, and is implemented by `FileSystemAccessService`.

## Risks
Callers must release unmanaged filesystems. Implementations may require the configuration to come from `getFileSystemConfiguration`, as `FileSystemAccessService` does.

## Test Signals
Contract tests should assert executor invocation under the requested user, exception wrapping, unmanaged filesystem release, and configuration validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/FileSystemAccess.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/FileSystemAccessException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/FileSystemAccessException.java

## Purpose
`FileSystemAccessException` is the coded checked exception for filesystem access service failures.

## Important APIs, Types, And Functions
The `ERROR` enum defines `H01` through `H11`: missing service property, Kerberos init failure, executor error, invalid service-created config, NameNode validation failure, missing `fs.defaultFS`, unhealthy namenode, generic message, invalid auth mode, missing Hadoop config directory, and Hadoop config load failure. Constructor delegates to `XException`.

## Control Flow
`FileSystemAccessService` throws this exception from initialization, validation, and execution paths. `HttpFSExceptionProvider` unwraps it to map the cause when possible.

## State And Persistence
Each instance stores the error code/message/cause through `XException`; no persistent state.

## Dependencies And Integration Points
It depends on `XException` and is part of the `FileSystemAccess` service contract and HttpFS exception mapping.

## Risks
Some errors wrap causes, but mapper unwrapping can hide the service-specific code from HTTP responses. The H04 template has a typo but its semantics are important: callers must use service-created configurations.

## Test Signals
Tests should cover each major error path in `FileSystemAccessService`, especially invalid config marker, missing default FS, whitelist rejection, and executor exception wrapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/FileSystemAccessException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Groups.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Groups.java

## Purpose
`Groups` is the service interface for resolving a user to Hadoop groups, used by HttpFS authorization decisions.

## Important APIs, Types, And Functions
It exposes `List<String> getGroups(String user)` and `Set<String> getGroupsSet(String user)`, both throwing `IOException`. The set form is used by admin group checks.

## Control Flow
`HttpFSServer` calls `getGroupsSet` during `INSTRUMENTATION` requests to require membership in the configured admin group. `GroupsService` implements this interface using Hadoop security groups.

## State And Persistence
The interface has no state. Implementation state is in Hadoop group mapping/cache.

## Dependencies And Integration Points
It depends on Java collections and `IOException`, and integrates with `GroupsService` and authorization logic.

## Risks
Group lookup failures surface as request failures. Set/list consistency depends on the implementation.

## Test Signals
Tests should cover admin membership checks, lookup failure propagation, and expected group cache behavior in `GroupsService`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Groups.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Instrumentation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Instrumentation.java

## Purpose
`Instrumentation` is the internal service interface for counters, timing samples, variables, samplers, and snapshot export used by HttpFS services.

## Important APIs, Types, And Functions
Nested `Cron` supports `start()` and `stop()` timing. Nested `Variable<T>` supplies dynamic values. Methods create crons, increment counters, add completed crons, add variables, add one-second samplers, and return `Map<String, Map<String, ?>> getSnapshot()`.

## Control Flow
`FileSystemAccessService` creates a cron around executor calls and registers unmanaged filesystem variables/samplers. `SchedulerService` instruments scheduled task executions/failures/skips. `HttpFSServer` exposes snapshots through the admin-only `INSTRUMENTATION` operation.

## State And Persistence
The interface has no state; implementation stores in-memory metrics. Snapshots are live maps, not persisted.

## Dependencies And Integration Points
Implemented by `InstrumentationService` and depended on by scheduler/filesystem services and the REST instrumentation endpoint.

## Risks
Snapshot value types are heterogeneous and JSON serialization depends on implementation wrappers. Callers must stop crons before adding them.

## Test Signals
Tests should assert counter increments, cron timings, variable sampling, scheduler integration, and snapshot serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Instrumentation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Scheduler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Scheduler.java

## Purpose
`Scheduler` is the service interface for running repeated background tasks inside the HttpFS server.

## Important APIs, Types, And Functions
It declares two overloads: `schedule(Callable<?> callable, long delay, long interval, TimeUnit unit)` and `schedule(Runnable runnable, long delay, long interval, TimeUnit unit)`.

## Control Flow
Services use it in `postInit` after dependencies exist. `FileSystemAccessService` schedules cache purging; `InstrumentationService` schedules one-second sampler updates. `SchedulerService` implements fixed-delay execution with instrumentation.

## State And Persistence
The interface has no state. Scheduled task state is implementation-owned and in memory.

## Dependencies And Integration Points
It depends on Java concurrency types and is implemented by `SchedulerService`.

## Risks
Fixed-delay semantics and shutdown behavior are implementation choices. Callers need idempotent tasks because failures are logged/instrumented but scheduling continues.

## Test Signals
Tests should verify callable/runnable scheduling, delay/interval forwarding, behavior under halted server status, and shutdown rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Scheduler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/hadoop/FileSystemAccessService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/hadoop/FileSystemAccessService.java

## Purpose
`FileSystemAccessService` is the concrete `FileSystemAccess` implementation. It initializes Hadoop authentication/configuration, validates allowed NameNodes, impersonates request users, caches per-user filesystems, instruments executor timings, and provides managed and unmanaged filesystem access paths.

## Important APIs, Types, And Functions
Configuration keys cover auth mode/keytab/principal, filesystem cache purge frequency/timeout, NameNode whitelist, and Hadoop config directory. `CachedFileSystem` tracks a cached `FileSystem`, use count, idle timestamp, timeout, release, and purge behavior. Main methods include `init`, `postInit`, `loadHadoopConf`, `getNewFileSystemConfiguration`, `createFileSystem`, `closeFileSystem`, `validateNamenode`, `execute`, `createFileSystemInternal`, public `createFileSystem`, `releaseFileSystem`, and `getFileSystemConfiguration`.

## Control Flow
Initialization configures UGI for kerberos or simple auth, loads `core-site.xml`/`hdfs-site.xml`, marks service-created filesystem config, clears server-side umask to `000`, disables HDFS FS cache, and loads the whitelist. Post-init registers instrumentation and schedules idle cache purging if enabled. `execute` validates user/config/defaultFS/whitelist, creates a proxy UGI, obtains a cached filesystem under `doAs`, checks health, starts a cron, invokes the executor, records timing, and releases the cache reference.

## State And Persistence
State includes Hadoop service config, service-created filesystem config, whitelist, purge timeout, unmanaged filesystem count, and a concurrent map of user to `CachedFileSystem`. Filesystem instances may be closed immediately or after idle timeout; cache entries remain indefinitely.

## Dependencies And Integration Points
It depends on Hadoop `FileSystem`, `UserGroupInformation`, Hadoop config files, `Instrumentation`, `Scheduler`, `ConfigurationUtils`, and `FSOperations` through the executor interface.

## Risks
Cache entries are never removed, only their filesystem is reopened/closed, so a very large user population grows the map. Whitelist validation uses only URI authority and lower-case matching. Public unmanaged filesystem users must call `releaseFileSystem` or metrics/cache counts leak. Kerberos login uses configured keytab/principal and fails service startup on errors.

## Test Signals
Tests should cover simple and kerberos config validation, missing Hadoop config dir/files, service-created config marker enforcement, defaultFS missing, whitelist accept/reject, executor exception wrapping, cron recording, cache reference counting/purge, umask clearing, and unmanaged count release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/hadoop/FileSystemAccessService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/instrumentation/InstrumentationService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/instrumentation/InstrumentationService.java

## Purpose
`InstrumentationService` is the in-memory implementation of the instrumentation interface. It tracks counters, timer rings, dynamic variables, rolling samplers, JVM/process information, and returns a snapshot map for the admin endpoint.

## Important APIs, Types, And Functions
It extends `BaseService` with prefix `instrumentation`; `timers.size` controls timer ring length. Internal maps are grouped by metric group/name. `getToAdd` lazily creates group maps and metric holders under locks. Nested `Cron` tracks own and total elapsed time. `Timer` stores ring buffers for own/total durations and exports last/average values as JSON. `VariableHolder` and `Sampler` implement JSON-aware wrappers. `SamplersRunnable` samples registered variables every second.

## Control Flow
`init` creates locks/maps, installs OS env, system properties, JVM memory variables, and exposes all categories in a linked snapshot map. `postInit` schedules the sampler runnable if a scheduler service is available. Callers use `incr`, `createCron`/`addCron`, `addVariable`, and `addSampler`; snapshots are returned directly to `HttpFSServer` instrumentation responses.

## State And Persistence
All state is process-local memory. The snapshot includes live environment and system property maps, counters, timers, variables, and samplers. Sampler windows roll in arrays and maintain an atomic sum.

## Dependencies And Integration Points
It depends on `Scheduler`, JSON-simple interfaces, Hadoop `Time`, and the service framework. It is consumed by `FileSystemAccessService`, `SchedulerService`, and the admin REST endpoint.

## Risks
`Timer.getValues` assumes at least one cron has been added; with `last == -1`, direct serialization could index invalid arrays. `addSampler` can add the same sampler object multiple times if called repeatedly for the same group/name. Snapshot exposes environment and system properties, so the admin endpoint must remain restricted. Variable callbacks can throw during JSON serialization.

## Test Signals
Tests should cover counter creation, cron start/stop reuse rejection, timer averages, snapshot JSON serialization before and after metrics exist, sampler rolling average, duplicate sampler behavior, and admin endpoint access control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/instrumentation/InstrumentationService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/scheduler/SchedulerService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/scheduler/SchedulerService.java

## Purpose
`SchedulerService` implements the background scheduler used by HttpFS services. It wraps scheduled work with server-status checks, instrumentation counters, timing, and error logging.

## Important APIs, Types, And Functions
It extends `BaseService` with prefix `scheduler`, depends on `Instrumentation`, and uses `threads` config defaulting to 5. `init` creates a `ScheduledThreadPoolExecutor`. `destroy` calls `shutdownNow` and waits up to about 30 seconds. `schedule(Callable, ...)` wraps callable execution in a `Runnable` and uses `scheduleWithFixedDelay`. `schedule(Runnable, ...)` adapts via `RunnableCallable`.

## Control Flow
For each scheduled tick, the wrapper retrieves `Instrumentation`, skips execution and increments `.skips` if server status is `HALTED`, otherwise increments `.execs`, starts a cron, calls the task, increments `.fails` on exception, and records timing in `finally`.

## State And Persistence
State is the scheduled executor service and queued tasks. Metrics are in instrumentation memory. No persistent state is written.

## Dependencies And Integration Points
It integrates with `InstrumentationService`, `RunnableCallable`, service lifecycle, and callers such as filesystem cache purging and instrumentation sampling.

## Risks
Tasks are scheduled with fixed delay, not fixed rate. Exceptions are swallowed after logging, so failing tasks continue to be rescheduled. `destroy` logs but does not restore interrupt status after catching `InterruptedException`. Scheduling after shutdown throws `IllegalStateException`.

## Test Signals
Tests should cover thread-count config, callable/runnable adaptation, halted-skip counters, execution/failure counters, cron recording, fixed-delay scheduling, and destroy timeout/shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/scheduler/SchedulerService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/security/GroupsService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/security/GroupsService.java

## Purpose
`GroupsService` is the concrete group lookup service for HttpFS. It adapts Hadoop's `org.apache.hadoop.security.Groups` to the local `Groups` service interface.

## Important APIs, Types, And Functions
It extends `BaseService` with prefix `groups`. `init` copies the trimmed service config into a Hadoop `Configuration(false)` and constructs `org.apache.hadoop.security.Groups`. `getInterface` returns `Groups.class`. `getGroups` delegates to Hadoop's list-returning method and is deprecated in favor of `getGroupsSet`, which delegates to the set-returning method.

## Control Flow
`Server` initializes this service from `httpfs.groups.*` properties. `HttpFSServer` uses it to check whether the requester belongs to the configured admin group before exposing instrumentation.

## State And Persistence
The service stores a Hadoop `Groups` instance, which may maintain its own in-memory cache according to Hadoop configuration. No state is persisted here.

## Dependencies And Integration Points
It depends on `BaseService`, `ConfigurationUtils`, local `Groups`, and Hadoop security group mapping.

## Risks
Group provider misconfiguration can deny admin access or allow stale membership until Hadoop cache refresh. The deprecated list method remains for compatibility. IOException propagates to REST error handling.

## Test Signals
Tests should cover service-config copying, delegate invocation for list and set forms, IOException propagation, and integration with the instrumentation admin group check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/security/GroupsService.java -->

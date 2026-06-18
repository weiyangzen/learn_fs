# subset-b-007431 Research

Grouped research for Hadoop HttpFS servlet, wsrs, deployment, and compatibility-test sources. Each section preserves the source path and is intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/servlet/FileSystemReleaseFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/servlet/FileSystemReleaseFilter.java

## Purpose
`FileSystemReleaseFilter` is an abstract servlet `Filter` that guarantees an HDFS `FileSystem` borrowed from `FileSystemAccess` is released after a servlet request finishes. It is aimed at streaming responses where the filesystem must remain open until response body streaming completes.

## Important APIs, Types, and Functions
The class implements `javax.servlet.Filter` and exposes static `setFileSystem(FileSystem fs)` for downstream request handlers to register the request-associated filesystem. `doFilter(ServletRequest, ServletResponse, FilterChain)` delegates to the chain and releases the registered filesystem in a `finally` block. Subclasses must implement `protected abstract FileSystemAccess getFileSystemAccess()`.

## Control Flow
`init` and `destroy` are no-ops. During `doFilter`, the request always enters `filterChain.doFilter`; after completion or exception, the filter checks a static `ThreadLocal<FileSystem>`, removes it if present, and calls `FileSystemAccess.releaseFileSystem(fs)`.

## State and Persistence
State is request-thread local only. No persistent storage is touched. Correct cleanup depends on servlet request processing staying on the same thread that called `setFileSystem`.

## Dependencies and Integration Points
It depends on Hadoop `FileSystem` and HttpFS/lib `FileSystemAccess`. The concrete HttpFS integration is `HttpFSReleaseFilter`, which binds `getFileSystemAccess()` to the running `HttpFSServerWebApp` service registry. Web descriptors map this filter around all requests so server operations that set the ThreadLocal are cleaned up after streaming.

## Risks
If an async servlet or streaming framework changes threads after `setFileSystem`, the ThreadLocal may not be visible to this filter and resources may leak. If code calls `setFileSystem` more than once in the same request, the last value wins. Release exceptions in the `finally` path can mask an earlier servlet exception.

## Test Signals
The listed subset does not include a direct unit test for this abstract filter, but the client compatibility tests exercise create/open/append/content streaming paths through the webapp and the mapped `fsReleaseFilter`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/servlet/FileSystemReleaseFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/servlet/HostnameFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/servlet/HostnameFilter.java

## Purpose
`HostnameFilter` resolves the remote client address for the current servlet request and exposes the canonical hostname to later code through a request-thread `ThreadLocal`.

## Important APIs, Types, and Functions
The class implements `Filter`, uses `InetAddress.getByName(request.getRemoteAddr()).getCanonicalHostName()`, and exposes `public static String get()` to retrieve the hostname. Unknown or null addresses become the sentinel string `"???"` and are logged with SLF4J.

## Control Flow
`doFilter` resolves the hostname before invoking the downstream chain, stores it in `HOSTNAME_TL`, delegates to `chain.doFilter`, and always removes the ThreadLocal in `finally`.

## State and Persistence
Only per-thread transient state is stored. No filesystem or configuration persistence occurs.

## Dependencies and Integration Points
`MDCFilter` can read `HostnameFilter.get()` to add `hostname` to logging MDC. The HttpFS `web.xml` files register both filters. In the descriptors read here, `MDCFilter` is mapped before `hostnameFilter`, so the hostname value will only be visible to MDC if container ordering or another mapping causes hostname to run first; otherwise MDC will omit the hostname.

## Risks
Reverse DNS lookup can block request handling or produce environment-dependent names. The SLF4J warning for `UnknownHostException` uses a `{0}` token rather than the usual `{}`, which may reduce message clarity. The ThreadLocal model has the same async-thread limitation as other servlet filters in this package.

## Test Signals
Direct tests outside this subset (`TestHostnameFilter`) assert resolution for localhost, fallback to `"???"`, and cleanup after request completion. In this subset, `MDCFilter` and web descriptors are the primary integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/servlet/HostnameFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/servlet/MDCFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/servlet/MDCFilter.java

## Purpose
`MDCFilter` populates SLF4J mapped diagnostic context for HttpFS request logs with request hostname, authenticated user, HTTP method, and path.

## Important APIs, Types, and Functions
The class implements `Filter` and uses `org.slf4j.MDC`. It casts the generic `ServletRequest` to `HttpServletRequest`, reads `getUserPrincipal()`, `getMethod()`, and `getPathInfo()`, and consults `HostnameFilter.get()`.

## Control Flow
Before the downstream chain runs, `doFilter` clears any stale MDC entries, conditionally adds `hostname` and `user`, always adds `method`, conditionally adds `path`, and delegates. The `finally` block clears MDC again.

## State and Persistence
State is log-context state scoped to the current request thread. Nothing is persisted directly, but downstream log lines can include the MDC values if the logging pattern is configured to do so.

## Dependencies and Integration Points
It depends on servlet HTTP requests, `HostnameFilter`, and SLF4J. It is registered in both HttpFS web descriptors and sits in the same filter chain as authentication, upload content checking, and filesystem release.

## Risks
The filter assumes every request is an `HttpServletRequest`; a non-HTTP request would throw `ClassCastException`. Since web descriptors map `MDCFilter` before `hostnameFilter`, the `hostname` field may be absent despite the Javadoc saying it appears if `HostnameFilter` is configured before this filter. Clearing all MDC state can erase context set by earlier filters in the same request.

## Test Signals
Direct tests outside this subset (`TestMDCFilter`) validate MDC population and cleanup. The subset web descriptors confirm the production registration and filter order risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/servlet/MDCFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/servlet/ServerWebApp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/servlet/ServerWebApp.java

## Purpose
`ServerWebApp` bridges Hadoop's internal `Server` lifecycle into a servlet container. It starts the server during `ServletContextListener.contextInitialized`, stops it during `contextDestroyed`, and resolves servlet-deployment directories and authority from Java system properties.

## Important APIs, Types, and Functions
The class extends `org.apache.hadoop.lib.server.Server` and implements `ServletContextListener`. It defines property suffixes such as `.home.dir`, `.config.dir`, `.log.dir`, `.temp.dir`, `.http.hostname`, `.http.port`, and public `.ssl.enabled`. Public and protected APIs include `setHomeDirForCurrentThread`, constructor variants for tests, static `getHomeDir`, static `getDir`, `resolveAuthority`, `getAuthority`, `setAuthority`, and `isSslEnabled`.

## Control Flow
The default constructor resolves home/config/log/temp directories from `#name#.home.dir` and related properties, defaulting config/log/temp under the home directory. `contextInitialized` calls `init()` and wraps `ServerException` as `RuntimeException` after logging to the servlet context. `getAuthority` lazily caches the address returned by `resolveAuthority`, which requires hostname and port system properties and resolves the hostname with `InetAddress.getByName`.

## State and Persistence
The main mutable state is the cached `InetSocketAddress authority` and a static test-only `ThreadLocal<String>` for overriding home directory. It reads Java system properties but does not persist changes. The inherited `Server` owns service lifecycle and configuration state.

## Dependencies and Integration Points
Concrete subclasses such as `HttpFSServerWebApp` provide the server name and services. The deployment `web.xml` files install that subclass as a listener. Shell launchers set `-Dhttpfs.home.dir`, `-Dhttpfs.config.dir`, `-Dhttpfs.log.dir`, and `-Dhttpfs.temp.dir`; the embedded web server path also relies on `httpfs.http.hostname`, `httpfs.http.port`, and `httpfs.ssl.enabled`.

## Risks
Missing required system properties fail startup. `resolveAuthority` catches `UnknownHostException` but not invalid integer ports, so malformed ports can propagate as `NumberFormatException`. Cached `authority` means system property changes after first access are ignored unless tests call `setAuthority`.

## Test Signals
The client and access-control tests call `HttpFSServerWebApp.setHomeDirForCurrentThread` before starting Jetty, exercising the test override path and servlet listener lifecycle. SSL subclasses depend on `isSslEnabled` via the web server integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/servlet/ServerWebApp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/util/Check.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/util/Check.java

## Purpose
`Check` is a small precondition utility for internal HttpFS/lib code. It centralizes argument validation for nulls, empty strings/lists, identifiers, and non-negative/positive numeric values.

## Important APIs, Types, and Functions
Static APIs are `notNull`, `notNullElements`, `notEmpty`, `notEmptyElements`, `validIdentifier`, `gt0(int)`, `gt0(long)`, `ge0(int)`, and `ge0(long)`. `validIdentifier` enforces `[a-zA-Z_][a-zA-Z0-9_\\-]*` and a caller-supplied maximum length.

## Control Flow
Each method validates inputs synchronously and either returns the original value or throws `IllegalArgumentException` with a formatted message. List methods iterate all elements and produce index-specific error text.

## State and Persistence
The class is stateless except for a compiled static `Pattern`. It has no persistence or I/O behavior.

## Dependencies and Integration Points
`ConfigurationUtils` uses `Check.notNull`. Other HttpFS server and service classes use this style to fail fast on invalid configuration or parameters.

## Risks
The methods do not trim strings, so whitespace-only input passes `notEmpty`. Javadoc for `ge0` says "if the integer is greater or equal to zero" in the thrown case, but the implementation correctly rejects negative values. Exceptions expose parameter names and values, which is useful internally but should be considered for externally sourced values.

## Test Signals
No direct tests are in this subset. Indirect coverage comes from components that use these preconditions during HttpFS server setup and parameter handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/util/Check.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/util/ConfigurationUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/util/ConfigurationUtils.java

## Purpose
`ConfigurationUtils` provides internal helpers for copying, default-injecting, resolving, and loading Hadoop `Configuration` objects.

## Important APIs, Types, and Functions
Static APIs are `copy(Configuration source, Configuration target)`, `injectDefaults(Configuration source, Configuration target)`, `resolve(Configuration conf)`, and `load(Configuration conf, InputStream is)`.

## Control Flow
`copy` iterates all source entries and overwrites the target. `injectDefaults` iterates source entries and writes only keys absent from target. `resolve` builds a new `Configuration(false)` and writes each key with `conf.get(key)` so inline variable references are expanded. `load` delegates to `Configuration.addResource(InputStream)`.

## State and Persistence
No class state is kept. Methods mutate caller-provided `Configuration` instances and read input streams, but do not write files.

## Dependencies and Integration Points
It depends on Hadoop `Configuration` and local `Check`. It supports HttpFS configuration loading, default composition, and variable resolution used by server/service startup.

## Risks
`resolve` silently drops metadata beyond key/value pairs and can realize sensitive interpolation into plain values. `load` leaves stream ownership to the caller and does not close the input stream. `copy` and `injectDefaults` iterate effective configuration entries, not necessarily only explicitly declared resources.

## Test Signals
No direct tests are listed, but `BaseTestHttpFSWith` and `TestHttpFSAccessControlled` create temporary `httpfs-site.xml` and `hdfs-site.xml` files that exercise configuration loading through the server path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/util/ConfigurationUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/BooleanParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/BooleanParam.java

## Purpose
`BooleanParam` is a base JAX-RS query parameter parser for boolean HttpFS parameters.

## Important APIs, Types, and Functions
It extends `Param<Boolean>`. The constructor passes the parameter name and default value to `Param`. `parse(String)` accepts case-insensitive `"true"` and `"false"` only. `getDomain()` returns `"a boolean"` for validation messages.

## Control Flow
`Param.parseParam` handles default retention for blank or null input; nonblank values reach `BooleanParam.parse`, which returns a boxed Boolean or throws `IllegalArgumentException`.

## State and Persistence
State is the inherited per-instance `value`. Instances are request parameter objects and are not persisted.

## Dependencies and Integration Points
Subclasses in `HttpFSParametersProvider` use this parser for options such as upload-data flags, overwrite, recursive, no-redirect, and all-users style parameters. `ParametersProvider` creates a fresh instance for each query value.

## Risks
Values like `1`, `0`, `yes`, or `no` are rejected. That is strict and predictable, but compatibility depends on WebHDFS clients sending true/false strings.

## Test Signals
`TestCheckUploadContentTypeFilter` uses `HttpFSParametersProvider.DataParam.NAME` and true/false strings around upload requests, indirectly signaling expected boolean query values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/BooleanParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/ByteParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/ByteParam.java

## Purpose
`ByteParam` is a base parser for signed byte-valued HttpFS/JAX-RS request parameters.

## Important APIs, Types, and Functions
It extends `Param<Byte>`, parses with `Byte.parseByte(str)`, and identifies its validation domain as `"a byte"`.

## Control Flow
Blank or absent input keeps the default through `Param.parseParam`; nonblank input is parsed as a decimal Java byte, with exceptions wrapped by the base class into a parameter-domain error.

## State and Persistence
Only the inherited mutable `value` field is used per request parameter instance.

## Dependencies and Integration Points
This belongs to the generic `org.apache.hadoop.lib.wsrs` parser family used by `ParametersProvider`. It is available for concrete HttpFS parameter definitions that need byte values.

## Risks
Only Java's standard byte range is accepted. There is no radix option or unsigned support. Reusing one instance across requests would be unsafe, but `ParametersProvider` instantiates new objects.

## Test Signals
No direct tests in this subset target `ByteParam`; parser behavior is covered by the same parameter provider mechanics used throughout the HttpFS operation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/ByteParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/EnumParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/EnumParam.java

## Purpose
`EnumParam` parses a single enum-valued query parameter while accepting lower or mixed case input.

## Important APIs, Types, and Functions
It extends `Param<E>` for `E extends Enum<E>`. The constructor stores the enum `Class<E>`. `parse(String)` uses `Enum.valueOf(klass, StringUtils.toUpperCase(str))`. `getDomain()` returns the comma-joined enum constants.

## Control Flow
The base `Param.parseParam` controls default retention and error wrapping. `EnumParam` transforms input to uppercase before Java enum lookup, matching WebHDFS's case-insensitive operation style.

## State and Persistence
State is per parser instance: the enum class and inherited parsed value.

## Dependencies and Integration Points
It depends on `org.apache.hadoop.util.StringUtils` and is used by concrete HttpFS parameter classes for operation names, xattr encodings, set flags, filesystem actions, and storage-related enum parameters.

## Risks
It only supports enum constants whose canonical name is uppercase-equivalent to the user input. Localized case rules are avoided by Hadoop `StringUtils`, but any enum with nonstandard naming would need a custom parser.

## Test Signals
`BaseTestHttpFSWith` sends many operation names through `HttpFSFileSystem` and WebHDFS clients, indirectly testing enum operation parsing through the server.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/EnumParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/EnumSetParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/EnumSetParam.java

## Purpose
`EnumSetParam` parses comma-separated enum lists into `EnumSet` values and provides stable string conversion for outbound or diagnostic use.

## Important APIs, Types, and Functions
It extends `Param<EnumSet<E>>`. `parse(String)` returns an empty `EnumSet` for an empty string or parses comma-separated, trimmed enum names after uppercase normalization. `getDomain()` returns available constants. Static `toString(EnumSet<E>)` emits comma-separated values, and instance `toString()` returns `name=value-list`.

## Control Flow
For each nonempty token, parsing calls `Enum.valueOf`; any invalid token bubbles to `Param.parseParam` as a validation error. The static string converter iterates the set in enum natural order.

## State and Persistence
Per-instance state includes the enum class and parsed set. There is no persistence.

## Dependencies and Integration Points
Concrete HttpFS parameter definitions can use it for flags such as xattr set flags or other multi-valued enum query options. It integrates with `ParametersProvider` as a normal `Param`.

## Risks
The parser does not ignore empty sub-tokens inside a nonempty string, so trailing commas can produce enum lookup failures. The inherited mutable value should not be shared across requests.

## Test Signals
The xattr tests in `BaseTestHttpFSWith` exercise flags and xattr operations through higher-level clients, which are the likely production users of this parser family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/EnumSetParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/ExceptionProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/ExceptionProvider.java

## Purpose
`ExceptionProvider` is a JAX-RS exception mapper that converts uncaught throwables into HTTP error responses for HttpFS REST endpoints.

## Important APIs, Types, and Functions
It implements `ExceptionMapper<Throwable>`. `toResponse(Throwable)` returns a BAD_REQUEST response by default. `createResponse(Response.Status, Throwable)` delegates to `HttpExceptionUtils.createJerseyExceptionResponse`. `getOneLineMessage` truncates messages at the first platform line separator. `log` emits debug-level exception details.

## Control Flow
Jersey calls `toResponse` when endpoint dispatch throws. The default implementation maps every throwable to HTTP 400, relying on subclasses or other mappers for more specific status mapping if present.

## State and Persistence
No mutable request state is stored. Logging is the only side effect.

## Dependencies and Integration Points
The web descriptors include `org.apache.hadoop.lib.wsrs` in Jersey provider package scanning, making this mapper available to HttpFS resources. It depends on Hadoop `HttpExceptionUtils` to produce the JSON/HTTP response shape expected by Hadoop clients.

## Risks
The broad `Throwable` mapping can hide server-side faults as client BAD_REQUEST unless a more specific mapper intercepts them. `getOneLineMessage` is unused in this class, suggesting either legacy behavior or subclass hooks. Debug-only logging may make production diagnosis dependent on client-visible JSON.

## Test Signals
`BaseTestHttpFSWith` has negative paths for invalid create overwrite, invalid working directory, xattr names, and snapshot diff parameters; these exercise exception conversion through client-visible failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/ExceptionProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/InputStreamEntity.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/InputStreamEntity.java

## Purpose
`InputStreamEntity` is a JAX-RS `StreamingOutput` wrapper for returning bytes from an `InputStream` with a configurable copy buffer.

## Important APIs, Types, and Functions
The class stores an `InputStream is` and `int offset`. `write(OutputStream os)` allocates a byte buffer of `offset` length, loops on `is.read(buffer)`, and writes each block to the response output stream.

## Control Flow
When Jersey writes the response, `write` streams all bytes from the source input to the servlet output. It closes the input stream in a `finally` block after copying completes or fails.

## State and Persistence
State is the source stream and buffer size. The class does not persist data; it performs transient network/file stream copying.

## Dependencies and Integration Points
HttpFS server operations that return file contents use this kind of `StreamingOutput`. It complements `FileSystemReleaseFilter`: the filesystem must remain open through streaming and be released after response completion.

## Risks
The field name `offset` is misleading because it is used as buffer size. A zero or negative buffer size would fail at runtime. The output stream is not closed, which is correct for servlet containers, but callers must understand ownership. Copying is blocking and unthrottled.

## Test Signals
`BaseTestHttpFSWith.testOpen` writes a byte through the proxied filesystem and reads it through HttpFS, validating the streaming response path at a high level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/InputStreamEntity.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/IntegerParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/IntegerParam.java

## Purpose
`IntegerParam` is the base parser for integer query parameters in HttpFS REST resources.

## Important APIs, Types, and Functions
It extends `Param<Integer>`, implements `parse(String)` with `Integer.parseInt`, and reports the domain `"an integer"`.

## Control Flow
Default handling and exception wrapping are inherited from `Param`. Concrete subclasses define names and defaults, while this base class supplies conversion.

## State and Persistence
Only per-instance parsed value is stored.

## Dependencies and Integration Points
HttpFS parameter definitions use integer values for options such as list limits, snapshot diff indices, and numeric request modifiers.

## Risks
No range checks are applied here. Domain-specific minimums, maximums, or sentinel values must be validated by concrete parameter users or filesystem APIs.

## Test Signals
`BaseTestHttpFSWith` exercises integer-like parameters through snapshot diff listing index values and filesystem operation options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/IntegerParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/JSONMapProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/JSONMapProvider.java

## Purpose
`JSONMapProvider` is a Jersey `MessageBodyWriter` that serializes Java `Map` responses as UTF-8 JSON.

## Important APIs, Types, and Functions
It is annotated with `@Provider` and `@Produces(MediaType.APPLICATION_JSON + "; " + JettyUtils.UTF_8)`. `isWriteable` accepts classes assignable to `Map`. `getSize` returns `-1`. `writeTo` serializes with `JSONObject.toJSONString(map)`, appends the platform newline, and writes UTF-8 bytes.

## Control Flow
During response writing, Jersey selects the provider for map entities, serializes the complete map into a string, and writes it to the output stream.

## State and Persistence
The provider is stateless. It has no persistence; its side effect is writing HTTP response bytes.

## Dependencies and Integration Points
It depends on Jersey, `org.json.simple.JSONObject`, Hadoop `JettyUtils.UTF_8`, and HttpFS resource methods that return `Map` objects for JSON APIs.

## Risks
The provider materializes the entire JSON string before writing, which is fine for small metadata maps but not for large responses. Raw `Map` typing means generic type validation is absent. Platform-specific newline is appended to every JSON response.

## Test Signals
`BaseTestHttpFSWith` compares JSON-derived filesystem metadata for block locations, snapshots, server defaults, quotas, and erasure coding; those flows depend on consistent JSON response serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/JSONMapProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/JSONProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/JSONProvider.java

## Purpose
`JSONProvider` is a Jersey `MessageBodyWriter` for `JSONStreamAware` response entities.

## Important APIs, Types, and Functions
It is annotated with `@Provider` and JSON UTF-8 `@Produces`. `isWriteable` accepts classes assignable to `JSONStreamAware`. `writeTo` wraps the output in an `OutputStreamWriter` using UTF-8, calls `writeJSONString`, appends a newline, and flushes.

## Control Flow
Jersey invokes this provider for JSON-simple streaming objects. The provider writes through the entity's own JSON streaming method, then flushes but does not close the servlet output stream.

## State and Persistence
The provider is stateless and only writes response bytes.

## Dependencies and Integration Points
It depends on `org.json.simple.JSONStreamAware`, Jersey, and Hadoop Jetty UTF-8 constants. HttpFS resources can return JSON-simple objects directly and rely on provider package scanning in `web.xml`.

## Risks
The provider flushes the writer, which is usually safe but can affect response buffering. Like `JSONMapProvider`, it appends a platform newline. Any exception during `writeJSONString` becomes a response write failure.

## Test Signals
Metadata-heavy operations in `BaseTestHttpFSWith`, including snapshot and erasure-coding comparisons, provide high-level coverage for JSON response compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/JSONProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/LongParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/LongParam.java

## Purpose
`LongParam` parses long integer query parameters for HttpFS REST operations.

## Important APIs, Types, and Functions
It extends `Param<Long>`, parses with `Long.parseLong(str)`, and describes its domain as `"a long"`.

## Control Flow
Blank and absent values keep defaults through the base parser. Nonblank values must be valid Java decimal long values.

## State and Persistence
Only per-instance parsed value is kept; no persistence occurs.

## Dependencies and Integration Points
Concrete HttpFS parameters use long values for offsets, lengths, block sizes, timestamps, and new truncate lengths. These values are then passed to Hadoop `FileSystem` or HDFS APIs.

## Risks
No range, unit, or sentinel validation is done in this base class. Negative values may be valid for some APIs and invalid for others, so endpoint logic must enforce semantics.

## Test Signals
`BaseTestHttpFSWith` exercises long-valued paths such as create block size, setTimes timestamps, truncate length, block-location offsets/lengths, and snapshot diff listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/LongParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/Param.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/Param.java

## Purpose
`Param<T>` is the generic base class for typed query parameter parsing in HttpFS's JAX-RS layer.

## Important APIs, Types, and Functions
It stores a parameter `name` and protected mutable `value`. Public APIs are `getName()`, `parseParam(String)`, `value()`, and `toString()`. Subclasses must implement `getDomain()` and `parse(String)`.

## Control Flow
`parseParam` only calls subclass parsing when the input string is non-null and nonblank after trimming. Otherwise it keeps the existing default. Parse exceptions are converted to `IllegalArgumentException` with the parameter name, invalid value, and expected domain.

## State and Persistence
Each instance is mutable and holds the current parsed/default value. No persistence occurs. Correct usage requires request-local instances.

## Dependencies and Integration Points
`ParametersProvider` instantiates `Param` subclasses reflectively, fills them from the servlet parameter map, and wraps them in `Parameters` for HttpFS resource methods.

## Risks
Because `parseParam` retains the previous value for blank input, defaults are sticky and instances must not be reused across requests or values unless intentionally reset. The wrapper exception drops the original cause, making detailed parse failures less visible. Subclasses like `StringParam` override this method to trim before validation.

## Test Signals
Every operation in `BaseTestHttpFSWith` passes through the concrete HttpFS parameter provider, indirectly exercising default retention, type conversion, and error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/Param.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/Parameters.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/Parameters.java

## Purpose
`Parameters` is a request-scoped container for parsed query parameters created by `ParametersProvider`.

## Important APIs, Types, and Functions
The constructor accepts `Map<String, List<Param<?>>>`. `get(String name, Class<T> klass)` returns the first parsed value cast to the requested `Param` subclass. `getValues(String name, Class<T> klass)` returns all non-null values for multi-valued parameters.

## Control Flow
Lookup is by parameter name. Single-value lookup returns null for missing or empty lists. Multi-value lookup creates a new list, casts each `Param`, and skips null values.

## State and Persistence
It holds the request parameter map only. It does not persist or mutate external state after construction.

## Dependencies and Integration Points
HttpFS resource methods use `Parameters` to read typed values by concrete parameter class. It depends on Hadoop `Lists` for list construction.

## Risks
The `klass` argument is used only for unchecked casts; it does not validate that the stored parameter class matches. Missing parameters return null even if a default object was not registered. Multi-valued lookup silently drops null defaults, which may be correct for optional lists but important for callers.

## Test Signals
The broad operation matrix in `BaseTestHttpFSWith` covers single and multi-value retrieval through operations such as xattr names, ACL entries, concat sources, and snapshot parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/Parameters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/ParametersProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/ParametersProvider.java

## Purpose
`ParametersProvider` turns a servlet request parameter map into a typed `Parameters` object based on an operation-dispatched parameter definition table.

## Important APIs, Types, and Functions
The constructor takes the operation/driver parameter name, an enum class for operations, and a `Map<Enum, Class<Param<?>>[]>` defining expected parameter classes per operation. `get(HttpServletRequest)` performs parsing. `newParam` reflectively calls default constructors on parameter classes.

## Control Flow
`get` reads `request.getParameterMap()`, extracts the first value of the driver parameter, uppercases it, converts it to the operation enum, checks support in `paramsDef`, and then iterates every parameter class for that operation. For each class it creates a parameter instance; if request values exist, each value is parsed into a fresh instance and appended to the list. If absent, one default instance is added. The result map is wrapped in `Parameters`.

## State and Persistence
The provider stores immutable-ish definition references but no request state after `get` returns. The returned `Parameters` owns the per-request objects.

## Dependencies and Integration Points
`HttpFSParametersProvider` subclasses/configures this class for WebHDFS operation parameters. `HttpFSServer` holds a static provider and calls it for each request.

## Risks
Reflective construction requires every concrete `Param` class to have a public/default constructor. If the servlet parameter map contains a key with an empty array, `queryString.get(driverParam)[0]` can throw. Wrapped parse errors become `IllegalArgumentException(ex.toString(), ex)`, so clients receive generic bad-request responses through `ExceptionProvider`.

## Test Signals
`BaseTestHttpFSWith` tests every declared client operation against the server, and negative cases for invalid operations/values depend on this parser rejecting malformed or missing parameters. `TestCheckUploadContentTypeFilter` references provider-defined `DataParam` names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/ParametersProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/ShortParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/ShortParam.java

## Purpose
`ShortParam` parses short integer query parameters, optionally in a caller-supplied radix.

## Important APIs, Types, and Functions
It extends `Param<Short>`. Constructors accept name/default/radix or name/default with radix 10. `parse(String)` calls `Short.parseShort(str, radix)`. `getDomain()` reports `"a short"`.

## Control Flow
Base default handling is used. Nonblank strings are parsed under the configured radix.

## State and Persistence
Each instance stores its radix and inherited parsed value. No persistence or I/O occurs.

## Dependencies and Integration Points
HttpFS parameter definitions use short values for HDFS settings such as replication and octal permissions when concrete subclasses choose the appropriate radix.

## Risks
The validation message does not mention radix, so octal/decimal failures may be unclear. No semantic range beyond Java `short` is enforced.

## Test Signals
`BaseTestHttpFSWith` exercises replication and permissions through create, setReplication, and setPermission operations, indirectly covering short-valued parameter parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/ShortParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/StringParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/StringParam.java

## Purpose
`StringParam` parses and optionally regex-validates string query parameters.

## Important APIs, Types, and Functions
It extends `Param<String>`, stores an optional `Pattern`, and overrides `parseParam` to trim non-null input before parsing. The constructor calls `parseParam(defaultValue)` so defaults are validated. `parse(String)` checks the pattern if present and returns the trimmed string.

## Control Flow
Null, empty, or whitespace-only inputs leave the existing default value unchanged. Nonblank values are trimmed, optionally matched with `Pattern.matches`, and stored as the parsed value. Errors become `IllegalArgumentException` with the pattern or `"a string"` as the domain.

## State and Persistence
State is per parameter instance: pattern plus inherited value.

## Dependencies and Integration Points
Concrete HttpFS parameters use it for paths, users/groups, ACL specs, xattr names/values, snapshot names, storage policy names, and filters. The constructor-time default validation catches invalid defaults at provider instantiation.

## Risks
Blank user input can silently select the default rather than an empty string, which matters for operations where empty strings have semantics. Pattern validation is all-or-nothing and the error does not include the underlying reason.

## Test Signals
`BaseTestHttpFSWith` covers many string parameters, including custom ACL user/group patterns, snapshot names, invalid working directories, invalid xattr names, storage policies, and snapshot diff parameter failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/StringParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/libexec/shellprofile.d/hadoop-httpfs.sh -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/libexec/shellprofile.d/hadoop-httpfs.sh

## Purpose
`hadoop-httpfs.sh` integrates HttpFS into the modern Hadoop shell command framework as the `hdfs httpfs` daemon subcommand.

## Important APIs, Types, and Functions
When `HADOOP_SHELL_EXECNAME` is `hdfs`, it registers `httpfs` via `hadoop_add_subcommand`. Function `hdfs_subcommand_httpfs` sources optional `httpfs-env.sh`, marks daemonization support, sets `HADOOP_CLASSNAME` to `org.apache.hadoop.fs.http.server.HttpFSServerWebServer`, and appends Java system properties for HttpFS home/config/log/temp directories.

## Control Flow
On command execution, the function reads optional environment overrides (`HTTPFS_CONFIG`, `HTTPFS_HOME`, `HTTPFS_LOG`, `HTTPFS_TEMP`), falls back to Hadoop defaults, adds `-Dhttpfs.*.dir` options, and creates the temp directory for `start` or default daemon modes.

## State and Persistence
It mutates shell variables used by Hadoop launcher scripts and creates the temp directory. It does not persist configuration files.

## Dependencies and Integration Points
It depends on Hadoop shell helper functions such as `hadoop_add_subcommand`, `hadoop_add_param`, and `hadoop_mkdir`. The Java system properties it sets are consumed by `ServerWebApp` and `HttpFSServerWebServer`.

## Risks
Incorrect environment overrides can point HttpFS at the wrong config or log directory. Temp directory creation only occurs in start/default modes, so custom run modes must still have valid paths. The script assumes it is sourced in the Hadoop shell framework.

## Test Signals
No shell tests are in this subset. The Java tests simulate the same property contract by calling `HttpFSServerWebApp.setHomeDirForCurrentThread` and writing temporary `conf`, `log`, and `temp` directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/libexec/shellprofile.d/hadoop-httpfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/resources/httpfs-default.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/resources/httpfs-default.xml

## Purpose
`httpfs-default.xml` provides default HttpFS server configuration: listener address, SSL, Hadoop HTTP server settings, service list, authentication, proxy-user examples, delegation-token timing, Hadoop backend authentication, filesystem cache purge, and access-mode defaults.

## Important APIs, Types, and Functions
Key properties include `httpfs.http.port` (`14000`), `httpfs.http.hostname` (`0.0.0.0`), `httpfs.http.administrators`, `httpfs.ssl.enabled`, Hadoop HTTP thread/header/temp settings, `httpfs.buffer.size`, `httpfs.services`, Kerberos principal/keytab properties, proxy-user property examples, delegation token intervals, `httpfs.hadoop.authentication.*`, filesystem cache purge frequency/timeout, and `httpfs.access.mode`.

## Control Flow
The file is loaded into Hadoop `Configuration` during HttpFS startup. Variable interpolation links properties such as `httpfs.hostname` to `httpfs.http.hostname`, Kerberos principals to realm/host values, and secret/temp paths to config/tmp directories.

## State and Persistence
This is static configuration shipped with the application. Runtime state is created by services that consume the settings, such as secret files, Kerberos logins, filesystem cache entries, and delegation token managers.

## Dependencies and Integration Points
`ServerWebApp` and `HttpFSServerWebServer` consume listener and SSL properties. `HttpFSAuthenticationFilter` consumes Hadoop HTTP authentication settings. `FileSystemAccessService` consumes backend auth/cache settings. `TestHttpFSAccessControlled` mutates `httpfs.access.mode` at runtime to verify read-write, write-only, and read-only behavior.

## Risks
Defaults are simple-auth and non-SSL, which are suitable for test/dev but insecure for production unless overridden. The typo `FORBIDDED` appears in the description only. Default wildcard examples for proxy users are comments, not active settings. Secret-file handling must be secured by deployment permissions.

## Test Signals
`TestHttpFSAccessControlled` directly verifies `httpfs.access.mode` semantics. `BaseTestHttpFSWith` writes `httpfs-site.xml` with proxy-user and signature-secret overrides and runs the full operation matrix through the server.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/resources/httpfs-default.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/resources/webapps/webhdfs/WEB-INF/web.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/resources/webapps/webhdfs/WEB-INF/web.xml

## Purpose
This deployment descriptor packages the HttpFS web application under a `/webhdfs/*` servlet mapping for the resource-style webapp layout.

## Important APIs, Types, and Functions
It declares listener `org.apache.hadoop.fs.http.server.HttpFSServerWebApp`, Jersey servlet `org.glassfish.jersey.servlet.ServletContainer`, provider packages `org.apache.hadoop.fs.http.server, org.apache.hadoop.lib.wsrs`, servlet mapping `/webhdfs/*`, and filters `HttpFSAuthenticationFilter`, `MDCFilter`, `HostnameFilter`, `CheckUploadContentTypeFilter`, and `HttpFSReleaseFilter`.

## Control Flow
On webapp startup the listener initializes HttpFS services. Requests under `/webhdfs/*` are routed to Jersey after passing through all mapped filters in descriptor order: auth, MDC, hostname, upload content-type check, filesystem release.

## State and Persistence
The descriptor itself is static. It causes servlet container state to include one listener, one Jersey servlet, and filter instances.

## Dependencies and Integration Points
It integrates HttpFS server resources with the generic lib wsrs providers. The filter chain connects authentication, logging context, upload validation, and filesystem lifecycle cleanup. Tests create Jetty `WebAppContext(url.getPath(), "/webhdfs")`, matching this path style.

## Risks
`MDCFilter` is declared before `HostnameFilter`, so MDC hostname population may not occur despite the filter's documented dependency. `url-pattern>*</url-pattern>` is used for filters under a Servlet 2.4 descriptor; deployment behavior should be verified across containers. Provider package scanning must include both server resources and generic JSON/exception providers.

## Test Signals
`BaseTestHttpFSWith.createHttpFSServer` and `TestHttpFSAccessControlled.createHttpFSServer` load the `webapp` resource into Jetty at context `/webhdfs`, exercising this descriptor's listener, servlet, and filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/resources/webapps/webhdfs/WEB-INF/web.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/sbin/httpfs.sh -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/sbin/httpfs.sh

## Purpose
`httpfs.sh` is a deprecated compatibility wrapper for managing HttpFS, forwarding legacy `httpfs.sh run|start|status|stop` commands to the modern `hdfs httpfs` subcommand.

## Important APIs, Types, and Functions
It defines `print_usage`, emits a deprecation warning, maps `run` to `hdfs httpfs`, maps `start|stop|status` to `hdfs --daemon <mode> httpfs`, locates `${HADOOP_HOME}/bin` or derives `../bin` relative to the script directory, and `exec`s `hdfs`.

## Control Flow
The script validates at least one argument, branches on the first command, computes the Hadoop bin directory, and replaces the current process with the delegated `hdfs` command.

## State and Persistence
No persistent state is created. It only emits stderr/stdout and delegates to another process.

## Dependencies and Integration Points
It depends on the Hadoop `hdfs` command and on the shellprofile subcommand implementation for actual HttpFS launch behavior.

## Risks
Additional arguments beyond the first are ignored, so legacy callers cannot pass extra options through this wrapper. Missing `HADOOP_HOME` and unusual installation layouts can cause incorrect bin resolution. The script exits with status 0 on no arguments after printing usage because it calls plain `exit`.

## Test Signals
No shell tests are in this subset. Its behavior is operational compatibility rather than Java request behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/sbin/httpfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/webapp/WEB-INF/web.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/webapp/WEB-INF/web.xml

## Purpose
This is the main HttpFS WAR deployment descriptor. It maps Jersey to the whole webapp path (`/*`) rather than the nested `/webhdfs/*` pattern used by the alternate resources descriptor.

## Important APIs, Types, and Functions
It declares `HttpFSServerWebApp` as listener, Jersey `ServletContainer` with provider packages `org.apache.hadoop.fs.http.server, org.apache.hadoop.lib.wsrs`, servlet mapping `/*`, and the same auth, MDC, hostname, upload-content-type, and filesystem-release filters.

## Control Flow
Servlet startup initializes the server listener and eagerly loads the Jersey servlet. All requests routed to the webapp run through the filter chain and then Jersey resource dispatch.

## State and Persistence
The descriptor creates container-managed listener/servlet/filter instances. It persists nothing directly.

## Dependencies and Integration Points
It is the production-style webapp descriptor for the HttpFS WAR. It binds the generic servlet filters and wsrs providers to the server resources scanned by Jersey.

## Risks
The same filter-order issue exists as in the alternate descriptor: `MDCFilter` precedes `HostnameFilter`. Mapping Jersey to `/*` means static resources or default servlet behavior must be considered if added later. Filter URL pattern syntax should be validated for target containers.

## Test Signals
The tests load `webapp` from the classpath into Jetty; depending on build resource layout this descriptor is the active one for the compatibility matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/webapp/WEB-INF/web.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/site/site.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/site/site.xml

## Purpose
`site.xml` configures the Maven site for the HttpFS module.

## Important APIs, Types, and Functions
It declares project name `HttpFS`, uses `org.apache.maven.skins:maven-stylus-skin` with version property `${maven-stylus-skin.version}`, and adds a site link to Apache Hadoop.

## Control Flow
Maven site generation reads this descriptor to choose skin and navigation links. It is not loaded by HttpFS runtime code.

## State and Persistence
Static build metadata only. Generated site output is produced by Maven outside this file.

## Dependencies and Integration Points
It depends on the Maven site plugin ecosystem and the stylus skin version property from the parent build.

## Risks
The external link uses `http://hadoop.apache.org/` rather than HTTPS. Runtime risk is none; build/site risk appears if the skin version property is missing.

## Test Signals
No runtime or unit tests target this file. Its validation is through Maven site generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/site/site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/BaseTestHttpFSWith.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/BaseTestHttpFSWith.java

## Purpose
`BaseTestHttpFSWith` is the central parameterized compatibility harness for HttpFS, WebHDFS, and SWebHDFS client behavior against an embedded HttpFS server and proxied filesystem.

## Important APIs, Types, and Functions
Subclasses provide `getProxiedFSTestDir`, `getProxiedFSURI`, and `getProxiedFSConf`; optional overrides choose filesystem class and scheme. `createHttpFSServer` builds a temporary home with `conf`, `log`, `temp`, writes `hdfs-site.xml` and `httpfs-site.xml`, configures proxy users and auth secret, and starts Jetty with the webapp resource. `getHttpFSFileSystem` registers the chosen implementation and returns a Hadoop `FileSystem`.

## Control Flow
The `Operation` enum lists the test matrix. `operations()` returns every enum value. `testOperation` and `testOperationDoAs` are JUnit 5 parameterized tests that start the server and dispatch the selected operation normally and under a proxy `UserGroupInformation.doAs`. The large `operation` switch routes to focused private test methods.

## State and Persistence
Each test creates temporary directories/files, writes XML configuration and secret files, creates data in the proxied filesystem, and starts/stops resources through test helpers. Persistent state is isolated under JUnit test directories and MiniDFSCluster storage.

## Dependencies and Integration Points
The class integrates Hadoop `FileSystem`, MiniDFSCluster helpers, Jetty, HttpFS server webapp, HttpFS/WebHDFS/SWebHDFS clients, ACL/xattr/snapshot/erasure-coding/storage-policy APIs, JSON utilities, and security user helpers. It is the strongest integration signal for the wsrs parameter providers, JSON providers, filters, and web descriptors.

## Covered Behavior
The test matrix covers get/open/create/append/truncate/concat/rename/delete/listing/batched listing/working directory/trash roots/mkdirs/times/permission/owner/replication/checksum/content summary/quota usage/xattrs/ACLs/encryption/storage policy/erasure coding/snapshots/snapshot diffs/server defaults/access checks/storage policy satisfier/block locations/link status/status/EC policies/EC codecs/trash root listing. Many assertions compare HttpFS/WebHDFS results with direct `DistributedFileSystem` results.

## Risks
The file is very broad and can be expensive because each operation starts an embedded HttpFS server and runs both direct and doAs variants. Some operations are skipped for local filesystems, so local subclass coverage is intentionally narrower. Several exception tests accept multiple exception types, which improves compatibility but may hide overly broad error mapping.

## Test Signals
This file is itself the main signal. It validates request parsing, operation dispatch, response JSON, filesystem side effects, proxy-user handling, and advanced HDFS metadata compatibility across different client implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/BaseTestHttpFSWith.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/TestHttpFSFWithSWebhdfsFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/TestHttpFSFWithSWebhdfsFileSystem.java

## Purpose
This subclass runs the base HttpFS compatibility matrix using Hadoop's secure WebHDFS client (`SWebHdfsFileSystem`) and `swebhdfs` scheme.

## Important APIs, Types, and Functions
It extends `TestHttpFSWithHttpFSFileSystem`, sets up SSL test keystores with `KeyStoreTestUtil.setupSSLConfig`, replaces `jettyTestHelper` with an HTTPS-enabled `TestJettyHelper`, overrides `getFileSystemClass` to `SWebHdfsFileSystem`, overrides `getScheme` to `swebhdfs`, and overrides `getHttpFSFileSystem` to use SSL configuration plus `fs.swebhdfs.impl`.

## Control Flow
An instance initializer locates the test classpath directory via `classutils.txt`, creates a temporary keystore directory, writes client/server SSL configs, and configures Jetty. `@AfterAll cleanUp` deletes generated SSL files and keystore config. The inherited parameterized tests then execute every operation over HTTPS.

## State and Persistence
Temporary SSL keystores and `ssl-client.xml`/`ssl-server.xml` files are created under test directories/classpath and cleaned after all tests.

## Dependencies and Integration Points
It depends on Hadoop SSL test utilities, SWebHDFS, the inherited HttpFS server setup, and Jetty HTTPS support.

## Risks
The instance initializer throws runtime exceptions if classpath resource discovery fails or SSL config setup fails, which can fail test construction before JUnit method execution. Cleanup assumes generated SSL files live in `classpathDir`.

## Test Signals
It extends the complete operation matrix to TLS transport and secure scheme URI handling, proving that HttpFS behavior is not limited to plain WebHDFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/TestHttpFSFWithSWebhdfsFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/TestHttpFSFWithWebhdfsFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/TestHttpFSFWithWebhdfsFileSystem.java

## Purpose
This subclass runs the base compatibility matrix using Hadoop's standard `WebHdfsFileSystem` client implementation against the HttpFS server.

## Important APIs, Types, and Functions
It extends `TestHttpFSWithHttpFSFileSystem` and overrides only `getFileSystemClass()` to return `WebHdfsFileSystem.class`.

## Control Flow
All setup, operation dispatch, and assertions are inherited. The overridden class causes `BaseTestHttpFSWith.getHttpFSFileSystem(Configuration)` to register `fs.webhdfs.impl` as `WebHdfsFileSystem` and use the inherited `webhdfs` scheme.

## State and Persistence
State is inherited from the base test: temporary configs, Jetty server, and filesystem test data.

## Dependencies and Integration Points
It verifies compatibility between the HttpFS server endpoint and Hadoop's built-in WebHDFS client stack.

## Risks
Because behavior is entirely inherited, failures are attributable to client implementation differences or server compatibility rather than local logic. This is intentional but can make test triage broad.

## Test Signals
The full `Operation` matrix runs with `WebHdfsFileSystem`, checking that HttpFS honors WebHDFS client expectations and response formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/TestHttpFSFWithWebhdfsFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/TestHttpFSFileSystemLocalFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/TestHttpFSFileSystemLocalFileSystem.java

## Purpose
This subclass runs the base HttpFS client tests with a local filesystem backend (`file:///`) rather than HDFS.

## Important APIs, Types, and Functions
It extends `BaseTestHttpFSWith`. Static initialization creates a local test root and stores `PATH_PREFIX`. It returns prefixed test directories, `file:///` as the proxied URI, and a minimal configuration with `fs.defaultFS`. `addPrefix` uses `Path.mergePaths`. `testSetPermission` is overridden for Windows to skip sticky-bit checks unsupported by local FS.

## Control Flow
Inherited operations run, but many base methods early-return when `isLocalFS()` is true. Paths are prefixed to keep local file operations under the test root.

## State and Persistence
Creates local test directories and files under Hadoop test temp locations. No HDFS cluster state is used.

## Dependencies and Integration Points
It validates HttpFS behavior when `FileSystemAccessService` proxies a local filesystem, giving coverage for operations shared between local and HDFS backends.

## Risks
Coverage is intentionally incomplete because HDFS-only features are skipped. Local filesystem checksum side files are called out by the base batched-listing test and can make direct listing comparisons invalid.

## Test Signals
This class signals which parts of HttpFS are backend-independent and guards Windows-specific permission behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/TestHttpFSFileSystemLocalFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/TestHttpFSWithHttpFSFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/TestHttpFSWithHttpFSFileSystem.java

## Purpose
This concrete subclass runs the base compatibility matrix with the HttpFS-specific client implementation, `HttpFSFileSystem`, against a MiniDFSCluster-backed HttpFS server.

## Important APIs, Types, and Functions
It overrides `getFileSystemClass` to return `HttpFSFileSystem.class`, `getProxiedFSTestDir` to return `TestHdfsHelper.getHdfsTestDir()`, `getProxiedFSURI` to read `fs.defaultFS` from `TestHdfsHelper.getHdfsConf()`, and `getProxiedFSConf` to return that HDFS configuration.

## Control Flow
All test execution is inherited from `BaseTestHttpFSWith`; this class supplies the canonical HttpFS client/backend pairing.

## State and Persistence
State is MiniDFSCluster and HttpFS test state managed by inherited test helpers.

## Dependencies and Integration Points
It ties the HttpFS client, HttpFS server webapp, and HDFS test cluster together. Other subclasses for WebHDFS and SWebHDFS extend this class and alter only client transport details.

## Risks
The subclass is thin, so correctness depends on `TestHdfsHelper` configuring the HDFS cluster with the capabilities required by the full operation matrix.

## Test Signals
This is the direct end-to-end signal for the HttpFS client/server pair and is the baseline for comparing WebHDFS and SWebHDFS client behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/TestHttpFSWithHttpFSFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/HttpFSKerberosAuthenticationHandlerForTesting.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/HttpFSKerberosAuthenticationHandlerForTesting.java

## Purpose
This test authentication handler avoids real Kerberos initialization while preserving delegation-token manager setup for HttpFS tests.

## Important APIs, Types, and Functions
It extends `KerberosDelegationTokenAuthenticationHandler`. `init(Properties config)` overrides the parent to call only `initTokenManager(config)`. `destroy()` is a no-op.

## Control Flow
When configured in tests, servlet authentication initialization skips Kerberos principal/keytab login and initializes only the token manager portions needed for token-related behavior.

## State and Persistence
It may initialize token manager state through the inherited helper. It does not create Kerberos login state and does not clean token manager state in `destroy`.

## Dependencies and Integration Points
It depends on Hadoop security's delegation-token web authentication handler and is intended for HttpFS server tests that need Kerberos-mode code paths without a KDC.

## Risks
Because `destroy` is a no-op, inherited cleanup is skipped; this is acceptable in short-lived tests but would not be suitable for production. It can mask bugs in real Kerberos initialization.

## Test Signals
The class is test-only infrastructure. It signals that HttpFS authentication tests distinguish token-manager behavior from real Kerberos login behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/HttpFSKerberosAuthenticationHandlerForTesting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestCheckUploadContentTypeFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestCheckUploadContentTypeFilter.java

## Purpose
This unit test verifies `CheckUploadContentTypeFilter` accepts data-upload requests only when upload semantics and content type are consistent.

## Important APIs, Types, and Functions
JUnit tests call helper `test(method, operation, contentType, upload, error)`. The helper uses Mockito `HttpServletRequest`, `HttpServletResponse`, and `FilterChain`, sets method, operation, data parameter, and content type, invokes `new CheckUploadContentTypeFilter().doFilter`, and verifies either `chain.doFilter` or `response.sendError(SC_BAD_REQUEST, contains("Data upload"))`.

## Control Flow
`putUpload` and `postUpload` assert valid `PUT CREATE` and `POST APPEND` uploads with `application/octet-stream` are allowed, including uppercase content type. `putUploadWrong` and `postUploadWrong` distinguish bad content type with and without `data=true`: bad type only errors when upload data is expected. `getOther` and `putOther` assert non-upload operations pass through.

## State and Persistence
The test is stateless and uses mocks only.

## Dependencies and Integration Points
It depends on `HttpFSFileSystem.Operation` names and `HttpFSParametersProvider.DataParam.NAME`, making it sensitive to client/server operation naming contracts. It verifies the filter registered in both web descriptors.

## Risks
The tests do not cover missing content type, multipart variants, charset parameters, or request bodies. They focus on the key create/append upload gate.

## Test Signals
The file directly signals that create/append two-step upload requests must use octet-stream content type only when the `data` flag marks the upload leg.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestCheckUploadContentTypeFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSAccessControlled.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSAccessControlled.java

## Purpose
`TestHttpFSAccessControlled` verifies the `httpfs.access.mode` server setting gates read and write HTTP operations as intended.

## Important APIs, Types, and Functions
`startMiniDFS` creates a hand-rolled `MiniDFSCluster` with permissions enabled and ACL support intentionally not enabled. `createHttpFSServer` writes separate HDFS and HttpFS config files, including `httpfs.hadoop.config.dir`, proxy-user settings, and auth secret, then starts Jetty with the webapp. Helper methods `getCmd`, `putCmd`, `postCmd`, and `deleteCmd` build raw `/webhdfs/v1/...` URLs and assert HTTP 200 or 403.

## Control Flow
The single test `testAcessControlledFS` creates three files, retrieves the running `HttpFSServerWebApp` config, and mutates `httpfs.access.mode` through `read-write`, `write-only`, and `read-only`. It then verifies GETFILESTATUS/LISTSTATUS always pass, GETXATTRS is forbidden in write-only, and SETPERMISSION/UNSETSTORAGEPOLICY/DELETE are forbidden in read-only but allowed in write-capable modes.

## State and Persistence
The test starts a MiniDFSCluster, writes temporary XML configuration and secret files, creates HDFS files, mutates live HttpFS configuration, and shuts down the cluster at the end.

## Dependencies and Integration Points
It integrates access-control mode configuration from `httpfs-default.xml`, the running `HttpFSServerWebApp` service/config registry, raw HttpURLConnection behavior, authentication with simple `user.name`, and HTTP method/operation dispatch.

## Risks
The test mutates global live config and resets access mode to read-write before shutdown; failures before reset could affect later tests if the same server survived. The method name has a typo (`testAcessControlledFS`). It verifies a representative operation set rather than every operation in each mode.

## Test Signals
This is the direct regression signal for read-write, write-only, and read-only enforcement. It confirms the documented exception that write-only still permits `GETFILESTATUS` and `LISTSTATUS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSAccessControlled.java -->

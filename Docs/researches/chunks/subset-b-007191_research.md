# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.1.2.xml

Chunk: `subset-b-007191`
Lines researched: 30508-35695 of generated JDiff XML for `Apache Hadoop Common 3.1.2`.

## Purpose

This chunk is a line-bounded slice of Hadoop Common 3.1.2's generated JDiff API description. It is not implementation source; it is a public API snapshot used by Hadoop release tooling to compare package/type/member compatibility across versions. The XML records public and protected API shape: packages, classes, interfaces, constructors, methods, fields, inheritance, implemented interfaces, visibility, abstract/static/final/synchronized flags, deprecation metadata, checked exceptions, parameter types, and Javadoc text.

The chunk starts inside the tail of `org.apache.hadoop.security.authorize.ImpersonationProvider`, then covers security HTTP filters, security token APIs, web delegation token clients/authenticators, the service lifecycle model, service launcher contracts and exit codes, tracing administration protocol types, general utilities, shell execution helpers, shutdown-hook management, build-version metadata, and Bloom filter data structures. It ends with empty package markers for `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash`, followed by the XML document close.

## XML Structure And Coverage

The slice contains complete `<package>` sections for:

- `org.apache.hadoop.security.http`
- `org.apache.hadoop.security.protocolPB` and `org.apache.hadoop.security.ssl` as empty API package markers
- `org.apache.hadoop.security.token`
- `org.apache.hadoop.security.token.delegation.web`
- `org.apache.hadoop.service`
- `org.apache.hadoop.service.launcher`
- `org.apache.hadoop.tools` and `org.apache.hadoop.tools.protocolPB` as empty API package markers
- `org.apache.hadoop.tracing`
- `org.apache.hadoop.util`
- `org.apache.hadoop.util.bloom`
- `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash` as empty API package markers

The first lines complete `ImpersonationProvider`, whose API was opened earlier in the XML. The visible tail confirms it implements `Configurable` and exposes `init(String configurationPrefix)` plus `authorize(UserGroupInformation user, String remoteAddress)`, with `AuthorizationException` on rejected proxy-user impersonation. Whole-file reconciliation should merge this with the previous chunk before summarizing the full type.

## APIs And Types Covered

`org.apache.hadoop.security.http.RestCsrfPreventionFilter` is a servlet `Filter` for REST CSRF protection. It exposes `init`, `doFilter`, `destroy`, protected `isBrowser(String)`, public `handleHttpInteraction(RestCsrfPreventionFilter.HttpInteraction)`, and static `getFilterParams(Configuration, String)`. Public constants identify the user-agent header, browser user-agent regex parameter, custom header parameter, methods-to-ignore parameter, and default header name. Its contract is browser-sensitive: browser-like user agents must supply the configured CSRF header, while non-browser user agents are not forced through that check.

`org.apache.hadoop.security.http.XFrameOptionsFilter` is a servlet `Filter` for clickjacking protection. It initializes from filter config, adds X-Frame-Options behavior during `doFilter`, and exposes `getFilterParams(Configuration, String)` plus constants for the X-Frame-Options header and custom header parameter.

`org.apache.hadoop.security.token.SecretManager<T>` is the server-side abstraction for token secrets. Implementations create token passwords, retrieve passwords while validating expiration/revocation, and create empty identifiers. It also exposes `retriableRetrievePassword` for failover/retry-aware callers, `checkAvailableForRead()` for standby-state gating, `generateSecret()`, static HMAC password creation from identifier bytes and a `SecretKey`, and `createSecretKey(byte[])`.

`org.apache.hadoop.security.token.Token<T>` is the client-side token value and implements `Writable`. It can be constructed from an identifier plus `SecretManager`, raw identifier/password/kind/service components, another token, a protobuf `SecurityProtos.TokenProto`, or an empty default constructor. Its public API covers cloning, protobuf conversion, identifier/password/kind/service access, service mutation, private clone checks and creation, Writable serialization, URL-safe encode/decode, equality/hash/string/cache-key behavior, and delegation-token management through `isManaged`, `renew(Configuration)`, and `cancel(Configuration)`.

`Token.TrivialRenewer` is a static public `TokenRenewer` subclass for token kinds that are not managed. Subclasses provide `getKind`; it implements kind matching, unmanaged status, no-op/unsupported renewal semantics, and cancellation behavior.

`TokenIdentifier` is the abstract, writable identifier side of a token. Implementations provide `getKind()` and `getUser()`. The base API serializes itself through `getBytes()` and exposes `getTrackingId()`, documented as an MD5-derived cross-session tracking identifier.

`TokenInfo` is a public annotation type marker for token-related metadata. `TokenRenewer` is the plugin interface for token kind support, managed-token checks, renewal, and cancellation. `TokenSelector<T>` selects a token for a named `Text` service from a collection.

`DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` with Hadoop delegation-token support. It has constructors for default, explicit authenticator, connection configurator, and both together. Public behavior includes global default authenticator selection, optional query-string token transport for WebHDFS compatibility, authenticated connection opening, delegation-token acquisition, renewal, and cancellation, with overloads supporting `doAs` proxy-user parameters. Its nested `Token` extends `AuthenticatedURL.Token` and stores an optional Hadoop delegation `Token`.

`DelegationTokenAuthenticator` wraps an underlying `Authenticator` and implements `Authenticator` itself. It accepts a `ConnectionConfigurator`, performs authentication, and drives remote delegation-token operations through URL endpoints. Public constants define operation/query/header names and JSON field names such as delegation token header, delegation parameter, token parameter, renewer parameter, service parameter, token JSON, URL-string JSON, and renew-expiration JSON. `KerberosDelegationTokenAuthenticator` and `PseudoDelegationTokenAuthenticator` are concrete simple constructors for SPNEGO-backed and pseudo-auth-backed delegation flows.

`org.apache.hadoop.service.Service` is the public lifecycle contract. It extends `Closeable` and defines `init(Configuration)`, `start()`, `stop()`, `close()`, listener registration, name/config/state/start-time queries, state checks, failure cause/state access, `waitForServiceToStop(long)`, lifecycle history snapshots, and blocker snapshots. The documented state model is `NOTINITED -> INITED -> STARTED -> STOPPED`, with failures expected to trigger stop and move to `STOPPED`.

`AbstractService` is the base implementation for `Service`. It exposes lifecycle entry points, protected overridable `serviceInit`, `serviceStart`, and `serviceStop`, failure recording via `noteFailure`, per-service and global state listener registration, lifecycle history, start time, configuration, state, blocker management, and service-stop waiting.

`CompositeService` manages child `Service` instances. It can add/remove children, add objects only if they implement `Service`, return a cloned service list, and cascades init/start/stop across children. The protected `STOP_ONLY_STARTED_SERVICES` field documents shutdown policy around stopping all children versus only started children, while still stopping children that failed during init/start.

`LifecycleEvent` is a serializable value object with public `time` and `state` fields. `LoggingStateChangeListener` logs service state changes. `ServiceOperations` provides static stop helpers, including quiet variants that catch and return exceptions while logging warnings. `ServiceStateChangeListener` receives callbacks after state changes and its docs warn that callbacks execute inside synchronized service transition paths, so slow listeners or reentrant service calls can deadlock.

`ServiceStateException` is a runtime exception that implements `ExitCodeProvider`; it records or derives a service lifecycle exit code and offers static `convert` helpers that wrap arbitrary throwables. `ServiceStateModel` is a small state-machine helper with current-state checks, synchronized `enterState`, static transition validation, and string rendering.

`org.apache.hadoop.service.launcher.LaunchableService` extends `Service` for process-launch-managed services. `bindArgs(Configuration, List)` is invoked before service init and can return a replacement configuration; `execute()` runs after service start and returns the process exit code. `AbstractLaunchableService` supplies defaults that return the input configuration and success exit code.

`HadoopUncaughtExceptionHandler` implements the JVM uncaught-exception hook policy for Hadoop launcher entry points. It logs ordinary exceptions outside shutdown but exits on `Error` because process state may be unsafe. `LauncherExitCodes` is a constants interface defining success, generic failure, client shutdown, task launch failure, interruption, command argument/config/auth/HTTP-like error categories, exception, unimplemented, service unavailable, unsupported version, service creation failure, and service lifecycle exception codes. `ServiceLaunchException` extends `ExitUtil.ExitException` and carries launcher exit codes, including formatted English-locale message construction.

`org.apache.hadoop.tracing.SpanReceiverInfo` exposes span receiver id and class name. `SpanReceiverInfoBuilder` builds receiver descriptions from a class name plus configuration pairs. `TraceAdminProtocol` lists, adds, and removes span receivers over an IOException-throwing protocol with a public `versionID`; `TraceAdminProtocolPB` bridges to the protobuf blocking interface and `VersionedProtocol`.

`org.apache.hadoop.util.ApplicationClassLoader` is a `URLClassLoader` for application isolation. It supports URL-array and classpath-string constructors, resource lookup, public/protected class loading, and static `isSystemClass(String, List)` pattern matching. `SYSTEM_CLASSES_DEFAULT` marks JDK, Hadoop, resource, and selected third-party classes that should stay parent/system loaded.

`IPList` is a one-method inclusion test for IP addresses. `Progressable` is a callback interface for long-running operations to report progress to Hadoop framework code and avoid timeout assumptions.

`PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum`. Both expose construction, `getValue`, `reset`, byte-array update, and single-byte update. `PureJavaCrc32` targets the same polynomial as native CRC32 to avoid JNI overhead for many small checksum operations; `PureJavaCrc32C` targets CRC32-C/iSCSI/SSE4.2-compatible polynomial behavior.

`ReflectionUtils` provides static helpers for configuration injection, reflective new instance creation, contention tracing, thread dump printing/logging through commons-logging or SLF4J, runtime class lookup for a typed object, Writable copy/clone through serialization, and declared field/method collection across inheritance.

`Shell` is an abstract base class for shell command execution and OS-specific command construction. It exposes static OS/JDK checks, Windows command-line length validation, groups/user/netgroup/permission/owner/symlink/readlink/process-signal command builders, environment variable regex, script extension helpers, Hadoop home/bin/winutils discovery, bash support checks, environment and working-directory setters, protected `run()`, abstract `getExecString()` and `parseExecResult(BufferedReader)`, process/exit/waiting-thread/timeout accessors, static `execCommand` overloads, global process destruction/listing, and memory-lock-limit parsing. Public fields capture Hadoop home env/system property names, Windows command-length constants including a deprecated misspelled alias, OS booleans, command constants, timeout/inherit-env state, deprecated `WINUTILS`, setsid availability, and token separator regex.

`ShutdownHookManager` is a singleton deterministic shutdown-hook registry. It registers hooks by priority, supports optional per-hook timeout and time unit, removal, presence checks, shutdown-in-progress checks, and clearing. Public constants define minimum timeout and default time unit. The class centralizes hooks behind one JVM shutdown hook so higher-priority hooks run earlier.

`StringInterner` exposes strong and weak string interning and in-place array interning. `SysInfo` is the abstract system-resource plugin surface for memory, processor/core counts, CPU frequency/time/usage, virtual cores used, network IO, and storage IO, with `newInstance()` selecting a default OS implementation.

`Tool` extends `Configurable` and defines `run(String[])` as Hadoop's generic CLI tool contract. `ToolRunner` parses generic Hadoop command-line options, injects the resulting `Configuration` into a `Tool`, invokes it, prints generic usage, and provides an interactive confirmation prompt. `VersionInfo` exposes protected instance getters and public static getters for Hadoop version, git revision, branch, build date, build user, source URL, source checksum, build version, protoc version, plus `main`.

`org.apache.hadoop.util.bloom.BloomFilter` is a standard Bloom filter extending `Filter`, with constructors for serialization and vector/hash setup, `add`, logical `and`/`or`/`xor`/`not`, membership tests, string rendering, vector-size access, and Writable serialization.

`CountingBloomFilter` is a final counting Bloom filter supporting add, delete, membership, approximate count, logical operations, string rendering, and Writable serialization. Its docs highlight 4-bit bucket-style overflow risk: adding the same key more than 15 times can overflow positions and raise error rates; delete can underflow and introduce false negatives.

`DynamicBloomFilter` supports a matrix of Bloom-filter rows that grows when the active row reaches its key threshold. It exposes add, membership, logical operations, string rendering, and Writable serialization. `HashFunction` maps a `Key` to multiple hash positions using configured max value, hash count, and hash type. `RemoveScheme` defines retouched Bloom filter clearing strategies: `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`. `RetouchedBloomFilter` extends `BloomFilter`, records known false positives through single key, collection, list, or array overloads, and applies `selectiveClearing(Key, short)` to trade selected false positive removal against possible false negatives.

## Control Flow And Behavioral Contracts

The XML itself has no executable control flow; behavior is inferred from method contracts, signatures, exceptions, and Javadoc.

Security HTTP request flow is filter-based. `RestCsrfPreventionFilter` initializes from servlet/configuration parameters, classifies the `User-Agent` through regexes, and rejects browser-originated REST requests that lack the configured custom header unless the method is ignored. `XFrameOptionsFilter` initializes header configuration and applies the clickjacking header before passing the request down the filter chain.

Token flow separates server and client responsibilities. `SecretManager` creates and validates token passwords and can signal invalid, standby, retriable, or IO states. `Token` carries the serialized identity/password/kind/service payload across RPC or HTTP boundaries, can be encoded for URLs or protobuf, and delegates renew/cancel/isManaged to registered `TokenRenewer` plugins. `TokenSelector` resolves service-specific tokens from collections.

Web delegation-token flow builds on `AuthenticatedURL`. Connections authenticate normally unless the URL token wrapper already carries a delegation token, in which case that token takes precedence. Acquisition and renewal require configured authentication, while cancellation is explicitly documented as not requiring authentication. Optional `doAs` parameters integrate with proxy-user flows, and optional query-string transport exists for WebHDFS compatibility despite header transport being the default.

Service lifecycle flow is explicit and guarded: services are initialized with a `Configuration`, started, stopped, and closed through `stop()`. On init/start failures, the documented contract is to stop and enter `STOPPED`. `AbstractService` records history and failures, notifies local/global listeners during transitions, and exposes blockers. `CompositeService` recursively initializes/starts/stops children. `ServiceStateModel` enforces valid transitions and throws `ServiceStateException` for illegal movement.

Launcher flow calls `LaunchableService.bindArgs()` before init, then starts the service, then calls `execute()`, using the returned value or thrown exception to produce a process exit code. `ServiceLaunchException`, `ExitCodeProvider`, and `LauncherExitCodes` form the process-exit mapping layer.

Utility control flow centers on adapters and helpers. `ApplicationClassLoader` applies child-first loading except for configured system-class patterns. `ReflectionUtils.newInstance()` constructs and config-injects objects. `Shell.run()` gates command execution by interval, constructs command arrays through subclass `getExecString()`, executes the process, and lets subclasses parse output. `ShutdownHookManager` orders registered hooks by priority and enforces configured timeouts.

Bloom filter control flow follows probabilistic set operations. Keys are hashed into positions through `HashFunction`; Bloom filters set/test bit vectors; counting filters increment/decrement counters and derive approximate counts; dynamic filters add rows when a row's record threshold is reached; retouched filters record false positives and selectively clear positions using one of the configured schemes.

## State And Persistence Behavior

The JDiff XML is persistent release metadata. Its primary durable state is the API description in the source tree; it should be preserved byte-for-byte except when the API snapshot is regenerated intentionally.

Runtime state described by the APIs includes servlet filter configuration, CSRF browser regex/header/method-ignore settings, X-Frame-Options header settings, token identifiers/passwords/kinds/services, delegation-token transport choices, authentication tokens, token renewal/cancellation state, and server-side token secret material. Secret material is not itself shown in the XML, but `SecretManager` APIs imply persistent or replicated backing state in concrete implementations.

Service APIs maintain mutable lifecycle state: current state, configuration, start time, failure cause/state, lifecycle event history, listeners, global listeners, blockers, and child service lists. State changes are synchronized in the model/base implementation, but listener callbacks can observe transient multi-threaded states.

Launcher and tracing state includes process exit-code decisions, uncaught exception handling policy, span receiver descriptions, span receiver ids, and configuration key/value pairs for receiver creation.

Utility state includes classloader URL/classpath and system-class patterns, CRC accumulator values, reflection/thread-dump throttling state, shell environment/working directory/current process/exit code/timeout/global shell registry, shutdown-hook registry and shutdown-in-progress flag, intern pools, system metrics snapshots, and version metadata loaded from build properties.

Bloom filters persist their probabilistic structures through `write(DataOutput)` and `readFields(DataInput)`. Standard filters persist bit vectors; counting filters persist counters; dynamic filters persist row matrices and thresholds; retouched filters persist false-positive metadata and adjusted filter state. Default constructors are explicitly present for deserialization.

## Dependencies And Integration Points

This generated XML integrates with JDiff/Javadoc compatibility tooling. Consumers compare it with other Hadoop Common API XML files to detect public API additions, removals, signature changes, deprecations, and documentation shifts.

Runtime APIs described here integrate with:

- Java Servlet API for REST CSRF and X-Frame-Options filters.
- Hadoop `Configuration`, `UserGroupInformation`, security authorization, authentication client classes, `AuthenticatedURL`, `Authenticator`, and `ConnectionConfigurator`.
- Hadoop `Writable`, `Text`, security protobufs, token identifiers, token renewer plugins, and secret-manager implementations.
- HTTP/S delegation-token services, WebHDFS compatibility behavior, Kerberos SPNEGO, pseudo authentication, proxy-user `doAs` flows, and JSON delegation-token responses.
- Hadoop service framework classes, SLF4J and commons-logging, launcher exit-code handling, JVM uncaught exception hooks, and `ExitUtil`.
- Hadoop IPC/protobuf tracing administration through `VersionedProtocol` and `TraceAdminPB`.
- Java class loading, reflection, management/thread diagnostics, process execution, OS-specific shell commands, shutdown hooks, checksums, and system-resource probes.
- Hadoop CLI conventions through `Tool`, `ToolRunner`, `GenericOptionsParser`, and configuration injection.
- Hadoop Bloom filter support classes such as `Filter`, `Key`, and hash implementations under `org.apache.hadoop.util.hash.Hash`.

## Risks And Compatibility Notes

- The chunk begins mid-`ImpersonationProvider`, so any whole-type report must merge with the preceding chunk. This chunk should only claim the visible tail for that interface.
- Empty packages are still compatibility-relevant package markers in the XML, but they do not expose public types in this slice.
- Generated API XML can drift if regenerated with a different doclet classpath, JDK, annotations, or source set. Compatibility checks should treat the source as generated metadata, not hand-authored API truth.
- `RestCsrfPreventionFilter.isBrowser` is protected and overrideable; subclasses can weaken or alter CSRF enforcement. Tests should cover default regex behavior and configured overrides.
- Header/query-string delegation-token transport affects security posture. Query-string tokens are present for compatibility and may leak through logs or caches if used carelessly.
- `AuthenticatedURL` instances are documented as not thread-safe; delegation-token URL wrappers should not be shared across concurrent client operations without external synchronization.
- `Token` exposes byte-array identifier/password accessors and URL encoders; callers must avoid accidental logging or mutation of sensitive token material.
- `TokenIdentifier.getTrackingId()` is documented as MD5-derived; this is a tracking identifier, not a modern cryptographic guarantee.
- `ServiceStateChangeListener` callbacks run during synchronized state transitions. Slow callbacks or callbacks that reenter service methods can block transitions or deadlock.
- `ServiceOperations.stop(Service)` is explicitly not thread-safe because it checks state before stopping; concurrent lifecycle operations need external coordination.
- `Shell` is OS-sensitive and has deprecated compatibility fields/methods, including `isJava7OrAbove`, misspelled `WINDOWS_MAX_SHELL_LENGHT`, and nullable deprecated `WINUTILS`. Command construction and Windows command-line limits need platform coverage.
- `Shell.execCommand` and global process destruction are high-impact APIs; tests and callers should handle timeouts, stderr behavior, environment inheritance, and process cleanup.
- Shutdown hook ordering is deterministic only within `ShutdownHookManager`; JVM-level hook ordering remains centralized through its single registered hook and can be affected by shutdown already being in progress.
- Bloom filter APIs are probabilistic and mutable. Counting filter overflow beyond 15 repeated inserts and delete underflow can increase false positives or introduce false negatives.

## Test Signals

Useful validation signals for this chunk include:

- XML well-formedness from line 30508 through the closing `</api>`, with matching start/end class and interface comments for all complete types in this slice.
- JDiff comparisons against adjacent Hadoop Common releases should flag public API changes in servlet filters, token/delegation-token APIs, service lifecycle APIs, launcher exit codes, shell utilities, and Bloom filters.
- Security filter tests should cover CSRF header enforcement for browser and non-browser user agents, custom browser regexes, custom header names, ignored HTTP methods, filter parameter extraction from `Configuration`, and X-Frame-Options header initialization/application.
- Token tests should cover SecretManager password creation/retrieval, invalid/retriable/standby behavior, Token Writable and protobuf round trips, URL-safe encode/decode, private clones, service mutation, renewer plugin discovery, renew/cancel/isManaged paths, and selector behavior.
- Delegation-token HTTP tests should cover default Kerberos authenticator selection, pseudo fallback where applicable, connection configurator propagation, header versus query-string token transport, `doAs` handling, get/renew/cancel operations, JSON parsing fields, and cancellation without authentication.
- Service lifecycle tests should cover valid and invalid state transitions, failure recording, listener/global-listener notification ordering, listener deadlock avoidance expectations, lifecycle history snapshots, blocker add/remove snapshots, wait-for-stop timeouts, CompositeService child ordering, and quiet stop exception capture.
- Launcher tests should cover `bindArgs` configuration replacement, execute return-code propagation, exception-to-exit-code wrapping, uncaught `Error` versus ordinary exception handling, and stability of every `LauncherExitCodes` constant.
- Tracing tests should cover span receiver builder configuration pairs, list/add/remove protocol behavior, receiver id returns, and protobuf protocol bridge compatibility.
- Utility tests should cover ApplicationClassLoader child-first/system-class matching, CRC32/CRC32C vectors, ReflectionUtils configuration injection and Writable copy, Shell command builders across Linux/Mac/Windows/Solaris/FreeBSD branches, command timeout cleanup, winutils discovery failures, shutdown-hook priority/timeout/removal behavior, string interning null/array cases, SysInfo unsupported OS handling, ToolRunner generic option parsing, and VersionInfo property loading.
- Bloom filter tests should cover add/membership, logical operations, serialization round trips, counting delete/underflow/overflow behavior, approximate counts, dynamic row growth at `nr`, hash position bounds, retouched false-positive recording overloads, and selective clearing schemes.

## Cross-Chunk Continuations

Previous chunk context is required for the beginning of `org.apache.hadoop.security.authorize.ImpersonationProvider`. This chunk reaches the end of the XML document after `org.apache.hadoop.util.hash`, so the merge lane should treat it as the terminal chunk for this JDiff file while still reconciling earlier chunks for packages and types not covered here.

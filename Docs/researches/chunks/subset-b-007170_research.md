# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.0.xml lines 30694-36789

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 2.8.0. It starts in the tail of the deprecated generated record compiler parser `org.apache.hadoop.record.compiler.generated.Rcc`, covers the rest of generated record compiler support, the deprecated `org.apache.hadoop.record.meta` type metadata package, large parts of Hadoop security and token APIs, the service lifecycle framework, tracing admin protocol types, and utility APIs through most of `org.apache.hadoop.util.Shell`.

Because the source is generated API metadata rather than executable Java source, the research surface is the compatibility contract: packages, class/interface names, inheritance, implemented interfaces, constructors, method signatures, public/protected fields, checked exceptions, deprecation markers, and embedded Javadocs. The chunk begins and ends inside classes, so adjacent chunks own the opening of `Rcc` and the remainder of `Shell`.

## Purpose

The record compiler and `record.meta` APIs preserve the legacy Hadoop Record I/O compiler and type-description model. They are all deprecated in favor of Avro, but they still define parser tokens, lexer streams, token objects, lexer errors, and record schema metadata classes that older generated record code may reference.

The security APIs define Hadoop's process and RPC identity model: access-control exceptions, credentials storage, user/group/id mapping, Kerberos and token utility methods, UGI login/proxy/doAs behavior, credential-provider abstraction, ACL parsing/serialization, and proxy-user impersonation checks. The HTTP and token packages add web request protections, X-Frame headers, secret manager and token contracts, token renewal/selection, and HTTP delegation-token client flows.

The service APIs define a reusable lifecycle model for Hadoop daemons and components. `Service`, `AbstractService`, `CompositeService`, `ServiceStateModel`, lifecycle events, listeners, and helper operations provide a common NOTINITED/INITED/STARTED/STOPPED state machine with failure recording, listener notification, blockers, and orderly child-service shutdown.

The tracing and utility APIs expose span-receiver administration, application classloading isolation, progress callbacks, IP-list matching, pure-Java CRC implementations, reflection helpers, and platform-specific shell command construction/execution.

## Important APIs, Types, and Functions

### Deprecated record compiler and metadata

- `RccConstants` enumerates parser token kinds for the deprecated record compiler grammar: module, record, include, primitive types, string/buffer/vector/map tokens, punctuation, string/identifier tokens, lexical states, and `tokenImage`.
- `RccTokenManager` implements `RccConstants` and exposes JavaCC-style lexer lifecycle: constructors over `SimpleCharStream`, `setDebugStream(PrintStream)`, `ReInit(...)`, `SwitchTo(int)`, protected `jjFillToken()`, and `getNextToken()`.
- `SimpleCharStream` wraps `Reader` or `InputStream` inputs, including encoding-aware constructors and `ReInit` overloads. It tracks buffer positions, line/column arrays, CR/LF state, tab width, backup count, and exposes `BeginToken()`, `readChar()`, `backup()`, `GetImage()`, `GetSuffix()`, `Done()`, and `adjustBeginLineColumn()`.
- Generated `Token` stores token kind, begin/end line and column, string image, next regular token, and preceding special token. `newToken(int)` is the customization hook for token subclasses.
- `TokenMgrError` extends `Error`, formats lexical errors, escapes unprintable characters, and exposes `getMessage()`.
- `TypeID` and constants such as `BoolTypeID`, `BufferTypeID`, `ByteTypeID`, `DoubleTypeID`, `FloatTypeID`, `IntTypeID`, `LongTypeID`, and `StringTypeID` describe base record types. `VectorTypeID`, `MapTypeID`, and `StructTypeID` add element/key/value/record-type composition.
- `FieldTypeInfo` couples a field id/name with a `TypeID`; `RecordTypeInfo` is a writable record schema with name, fields, nested-struct lookup, `serialize(RecordOutput, String)`, `deserialize(RecordInput, String)`, and a `compareTo` that is explicitly not intended for sorting.
- `Utils.skip(RecordInput, String, TypeID)` reads and discards data based on a type descriptor.

### Security identity, credentials, and mapping

- `AccessControlException` extends the filesystem permission exception and keeps constructors needed for IPC `RemoteException` unwrapping.
- `Credentials` implements `Writable` for in-memory and persisted token/secret-key storage. It supports token lookup/add/enumeration/counting, secret-key lookup/add/remove/enumeration/counting, token-storage file/stream read/write, `write(DataOutput)`, `readFields(DataInput)`, `addAll()` with overwrite, and `mergeAll()` without overwrite.
- `GroupMappingServiceProvider` is the user-to-groups provider interface used by `Groups`, with `getGroups(String)`, `cacheGroupsRefresh()`, `cacheGroupsAdd(List)`, and `GROUP_MAPPING_CONFIG_PREFIX`.
- `IdMappingServiceProvider` maps users/groups to numeric IDs and back, with strict `getUid()`/`getGid()` that can throw `IOException` and permissive `getUidAllowingUnknown()`/`getGidAllowingUnknown()` variants.
- `SecurityUtil` centralizes Kerberos and token helpers: original-TGT detection, server-principal host substitution, keytab login overloads, delegation-token service-name construction, host extraction from principals, Kerberos/token annotation lookup, token service address extraction and setting, login/current-user `doAs` wrappers, authentication-method mapping, and privileged-port detection.
- `UserGroupInformation` wraps JAAS `Subject` identity. It exposes global configuration/security state, current/login/ticket-cache/subject UGI resolution, keytab and ticket-cache login/relogin/logout flows, remote/proxy/test user construction, real-user access, short and full names, primary group, group lists, token identifier/token/credential management, authentication method state, subject equality/hash, privileged `doAs` execution, diagnostics, and `HADOOP_TOKEN_FILE_LOCATION`.
- `UserGroupInformation.AuthenticationMethod` bridges UGI authentication methods to `SaslRpcServer.AuthMethod`.

### Credential providers, authorization, and HTTP filters

- `CredentialProvider` is the abstract password/secret store contract. It distinguishes transient stores, requires `flush()` for persistence, supports alias lookup/list/create/delete, password-needed diagnostics, and clear-text fallback configuration.
- `CredentialProviderFactory` creates providers from URI paths in `Configuration` using a service-loader interface and the `CREDENTIAL_PROVIDER_PATH` key.
- `AccessControlList` implements `Writable` for configured user/group ACLs. Constructors accept a combined ACL string or separate comma-separated user/group lists; methods add/remove users and groups, expose unmodifiable user/group collections, test direct membership and effective allowance against `UserGroupInformation`, stringify for display or exact reconstruction, and serialize/deserialize. `WILDCARD_ACL_VALUE` marks all-access ACLs.
- `AuthorizationException` extends `AccessControlException` but intentionally suppresses stack traces for security purposes.
- `DefaultImpersonationProvider` implements `ImpersonationProvider` and `Configurable`, initializes proxy-user configuration from a prefix, authorizes proxy users by effective user and remote address, and exposes generated superuser user/group/IP config keys plus proxy group/host maps.
- `RestCsrfPreventionFilter` is a servlet `Filter` that treats browser user agents as needing a custom CSRF header unless configured methods are ignored. It exposes constants for `User-Agent`, browser regex, custom header, and ignored methods, plus `handleHttpInteraction()` for servlet-independent filtering.
- `XFrameOptionsFilter` is a servlet `Filter` that sets an X-Frame-Options-style header using configurable header/value parameters.

### Tokens and web delegation-token clients

- `SecretManager<T extends TokenIdentifier>` creates and retrieves passwords, has a retriable retrieval path, creates identifiers, checks read availability, and provides static helpers for generating secrets, creating passwords, and wrapping secret keys.
- `org.apache.hadoop.security.token.Token<T>` implements the writable token payload: identifier bytes, password bytes, kind, service, URL-string encode/decode, identifier decoding through the token identifier class, equality/hash/string/cache-key helpers, and renew/cancel/isManaged operations through registered renewers.
- `Token.TrivialRenewer` is a default no-op renewer implementation; `TokenRenewer` is the abstract renew/cancel contract keyed by token kind; `TokenSelector<T>` selects a token from a collection for a service.
- `TokenIdentifier` is the writable identity payload contract with `getKind()`, `getUser()`, byte serialization through `getBytes()`, and tracking id support.
- `TokenInfo` is an annotation-like type that identifies the renewer class associated with a token-using protocol.
- `DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` with Hadoop delegation-token operations. It supports configurable default authenticator class, optional query-string token transport, connection opening with delegation tokens and optional `doAs`, token fetch, renew, and cancel overloads. Its nested `Token` holds both HTTP authentication state and a Hadoop delegation token.
- `DelegationTokenAuthenticator` wraps another `Authenticator` and adds HTTP/S delegation-token request, renew, and cancel flows with JSON/header/parameter constants for operation, delegation token, token, renewer, and response keys.
- `KerberosDelegationTokenAuthenticator` adds SPNEGO delegation-token support and falls back to pseudo authentication when the endpoint does not trigger SPNEGO. `PseudoDelegationTokenAuthenticator` models simple authentication by trusting the current UGI user as a query-string user.

### Service lifecycle framework

- `Service` is the lifecycle interface with `init(Configuration)`, `start()`, `stop()`, `close()`, listener registration, name/config/state/start-time/failure/history/blocker accessors, and `waitForServiceToStop(long)`.
- `AbstractService` implements `Service`. It enforces state transitions, records first failure cause and failure state, stores configuration and start time, supports global and local listeners, records lifecycle history, tracks blocker name/details, exposes protected hooks `serviceInit()`, `serviceStart()`, and `serviceStop()`, and makes `close()` relay to `stop()`.
- `CompositeService` extends `AbstractService` for child-service management. It clones the service list for callers, adds/removes services, adds arbitrary objects only if they implement `Service`, and initializes/starts/stops children according to `STOP_ONLY_STARTED_SERVICES`.
- `LifecycleEvent` is a serializable record of transition time and new state; `LoggingStateChangeListener` logs service state changes.
- `ServiceOperations` stops services safely or quietly, returning caught exceptions for cleanup paths.
- `ServiceStateChangeListener` callbacks run on the initiating thread while the service is synchronized, making long-running listener work and reentrant service calls a documented deadlock risk.
- `ServiceStateException` converts arbitrary throwables into runtime service-state failures. `ServiceStateModel` stores the current lifecycle state, validates transitions, enters states thread-safely, and exposes static transition checks.

### Tracing and utility APIs

- `SpanReceiverInfo` exposes span receiver id and class name; `SpanReceiverInfoBuilder` collects class name and configuration pairs; `TraceAdminProtocol` lists/adds/removes span receivers and declares `versionID`; `TraceAdminProtocolPB` bridges protobuf RPC and `VersionedProtocol`.
- `ApplicationClassLoader` extends `URLClassLoader` to isolate application classes from system classes. It can be built from URL arrays or classpath strings, overrides resource and class loading, and exposes `isSystemClass()` plus `SYSTEM_CLASSES_DEFAULT`.
- `IPList.isIn(String)` tests whether an address is included in an IP list, and `Progressable.progress()` is the classic Hadoop progress callback.
- `PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum` with `getValue()`, `reset()`, and byte-array/int `update()` methods.
- `ReflectionUtils` handles `Configurable` injection, configuration-aware instance construction, contention tracing, thread dumps to streams/logs with throttling, typed class lookup, writable copy/clone through serialization, and retrieval of declared fields/methods including inherited members.
- `Shell` constructs and executes platform-specific shell commands. Static helpers cover Windows command-line length checks, group/user/netgroup commands, permission/owner/symlink/readlink/process/signal commands, environment-variable regexes, platform script extensions and interpreters, Hadoop home and qualified binary discovery, winutils detection, bash support checks, and simple `execCommand()` overloads. Subclasses implement `getExecString()` and `parseExecResult(BufferedReader)`, while the base class manages environment, working directory, process, exit code, timeout flag, and re-execution interval.

## Control Flow

The XML file has no runtime control flow, but the documented APIs imply several important flows:

- Record compiler lexing flows from `SimpleCharStream` through `RccTokenManager.getNextToken()` into linked `Token` objects, with `TokenMgrError` used for lexical failures. Parser tracing is toggled on `Rcc` through the tail methods visible at the start of the chunk.
- Record metadata flows build a `RecordTypeInfo` from named `FieldTypeInfo` entries and nested `TypeID` structures, then serialize/deserialize that schema through Hadoop Record I/O `RecordOutput` and `RecordInput`. `Utils.skip()` uses the same `TypeID` graph to consume data without materializing it.
- Credentials are populated in memory, optionally loaded from a token storage file or stream, merged into another credentials object, and written back through `Writable` or token-storage methods. `addAll()` overwrites aliases; `mergeAll()` preserves existing ones.
- UGI setup starts with `setConfiguration()`, resolves current/login users from JAAS subjects, ticket cache, or keytab, renews/relogs Kerberos credentials as needed, then runs code under a user identity through `doAs(PrivilegedAction)` or `doAs(PrivilegedExceptionAction)`. Proxy users carry a real user whose authentication method is consulted by helper APIs.
- Authorization flows parse ACL strings or proxy-user configuration, map users to groups/hosts, and test an incoming `UserGroupInformation` plus remote address. `AuthorizationException` intentionally avoids revealing stack traces.
- HTTP delegation-token flows authenticate a connection with an underlying authenticator, request a delegation token over HTTP/S, store it in a `DelegationTokenAuthenticatedURL.Token`, attach the token to subsequent connections either in headers or query strings, and later renew or cancel it. Kerberos-backed flows can fall back to pseudo authentication.
- Service lifecycle flows are state-machine driven: `init()` invokes `serviceInit()`, `start()` invokes `serviceStart()`, `stop()` invokes `serviceStop()`, all while recording lifecycle events, failures, listeners, blockers, and child-service behavior for composites.
- Shell execution flows through subclass-provided command arrays and parse callbacks. `run()` checks the minimum interval, starts a process with configured environment and working directory, captures output for parsing, records exit/timeout state, and exposes the live process and exit code.

## State and Persistence Behavior

The JDiff file itself persists API metadata for compatibility checks and release documentation. It does not store application data.

Several APIs in this chunk are persistence-sensitive:

- `Credentials`, `AccessControlList`, `Token`, `TokenIdentifier`, and record metadata types implement Hadoop `Writable` or record serialization contracts. Their binary and textual encodings are compatibility surfaces for job tokens, delegation tokens, ACL configuration, and older Record I/O users.
- `CredentialProvider` separates transient credential stores from persistent providers and requires explicit `flush()` to push changes to backing storage.
- UGI stores identity state in JAAS `Subject` instances, including authentication method, token identifiers, tokens, credentials, and real-user/proxy relationships. Keytab and ticket-cache login state is process-global enough that relogin and logout paths have broad side effects.
- Service objects keep lifecycle state, configuration, start time, failure cause/state, lifecycle history snapshots, listeners, and blocker maps. `CompositeService` adds child-service lists and shutdown policy state.
- Shell instances keep environment overrides, working directory, process handle, last exit code, timeout flag, redirect-error-stream setting, and re-execution interval state. Static Hadoop home/winutils helpers depend on environment variables, system properties, and file existence.
- `ApplicationClassLoader` stores classpath URLs and system-class patterns, which directly affect runtime class/resource resolution.

## Dependencies and Integration Points

The chunk depends heavily on Java standard APIs: `Reader`, `InputStream`, `PrintStream`, `DataInput`, `DataOutput`, `DataInputStream`, `DataOutputStream`, `File`, `URI`, `URL`, `HttpURLConnection`, servlet `Filter` APIs, JAAS `Subject`, privileged actions, collections, `Checksum`, `URLClassLoader`, `Process`, `BufferedReader`, crypto `SecretKey`, and checked exceptions such as `IOException`, `UnsupportedEncodingException`, `FileNotFoundException`, `ServletException`, and authentication exceptions.

Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration` and `Configurable` for UGI/security configuration, impersonation providers, credential-provider discovery, service initialization, and reflection-based object configuration.
- `org.apache.hadoop.io.Writable`, `Text`, `WritableUtils`, and token/credential serialization used by RPC, MapReduce jobs, filesystem clients, and delegation-token files.
- `org.apache.hadoop.fs.Path`, filesystem permission exceptions, and Hadoop home/bin utilities used by command execution and security setup.
- `org.apache.hadoop.security.authentication.client.AuthenticatedURL`, `Authenticator`, `ConnectionConfigurator`, and `AuthenticationException` for HTTP authentication and delegation-token clients.
- `org.apache.hadoop.ipc.VersionedProtocol` and generated protobuf blocking interfaces for tracing admin RPC.
- `org.apache.hadoop.record.RecordInput`, `RecordOutput`, and legacy record compiler generated code.
- Commons Logging and SLF4J logging used by service listeners, reflection thread dumps, shell diagnostics, and security utilities.

## Risks and Edge Cases

- The chunk starts and ends inside classes. The merge lane must combine this with adjacent chunks before making complete-file claims about `Rcc` and `Shell`.
- JDiff gives signatures and Javadocs, not implementation bodies. Exact synchronization, timeout handling, command arrays, binary encodings, and exception text require source-code validation.
- The record compiler APIs are deprecated but still public. Removing or changing them can break old generated record code even though Avro is the recommended replacement.
- `SimpleCharStream` exposes mutable lexer buffer state and many reinitialization paths. Off-by-one line/column handling, CR/LF normalization, backup counts, tab widths, and encoding constructors are compatibility-sensitive.
- `Credentials` stores byte arrays and tokens by aliases. Aliasing, mutation of returned arrays/tokens, overwrite-vs-merge semantics, and token-storage format compatibility are high-risk areas.
- UGI methods mix process-global login state, subject-local credentials, Kerberos keytab/ticket-cache renewal, proxy users, and privileged execution. Misordered configuration or relogin calls can affect unrelated callers in the same JVM.
- `AuthorizationException` suppresses stack traces. This is deliberate for security, but it can hide operational diagnostics if callers do not log enough context.
- ACL and proxy-user authorization depend on string parsing of users, groups, hosts, wildcard values, and remote addresses. Empty lists, wildcard ACLs, unknown users, and group lookup failures need explicit coverage.
- HTTP CSRF filtering depends on user-agent regexes and ignored methods. Browser misclassification or missing custom headers can either block legitimate clients or permit unsafe browser-originated requests.
- Delegation-token URL handling has both header and query-string modes. Query-string token transport risks token leakage through logs, browser history, proxies, and referrers if enabled casually.
- `AuthenticatedURL` instances are documented as not thread-safe; callers sharing `DelegationTokenAuthenticatedURL` or its token objects across threads need synchronization.
- Service listeners run synchronously during state changes and are warned against long-running or reentrant service calls. Listener misuse can block lifecycle transitions or deadlock.
- `CompositeService` shutdown policy and partial init/start failures are subtle: child services may be stopped even if not fully started, depending on failure path and `STOP_ONLY_STARTED_SERVICES`.
- `ApplicationClassLoader` class/resource ordering and system-class pattern matching can cause class shadowing or dependency leakage between application and Hadoop runtime classes.
- Shell helpers are platform-specific. Windows command-line length, winutils discovery, Hadoop home resolution, environment regexes, script suffixes, and group/id command behavior all vary by OS and configuration.

## Test Signals

Useful validation for this API surface should include:

- Golden API compatibility checks for all public/protected classes, interfaces, fields, constructors, methods, checked exceptions, deprecation markers, and package boundaries in this chunk.
- Lexer/parser compatibility tests for `SimpleCharStream`, `RccTokenManager`, `Token`, and `TokenMgrError`, including encoded input streams, CR/LF/tab line-column accounting, token backup, special tokens, EOF handling, tracing toggles, and lexical-error messages.
- Record metadata round trips for base, vector, map, struct, nested-record, and field type info, plus `Utils.skip()` coverage for each supported type.
- `Credentials` tests for token and secret-key add/get/remove/enumeration/counting, stream/file read/write, `Writable` round trips, alias overwrite in `addAll()`, alias preservation in `mergeAll()`, and mutation/copy behavior of byte-array secrets.
- Group/id mapping tests for known and unknown users/groups, cache refresh/add behavior, strict vs allowing-unknown ID methods, and empty-list handling for missing users.
- UGI tests covering simple and Kerberos modes, ticket-cache and keytab login, relogin throttling/immediate-renewal test hooks, proxy users and real users, token/credential propagation, authentication method mapping, group lookups, and `doAs` exception propagation.
- Security utility tests for principal host substitution, token service address build/parse/set, privileged port detection, annotation lookup, and fatal/nonfatal login-user `doAs` wrappers.
- Credential-provider tests for service-loader discovery from `CREDENTIAL_PROVIDER_PATH`, transient vs persistent providers, duplicate alias creation, delete, password-needed warning/error paths, clear-text fallback, and required `flush()`.
- ACL and impersonation tests for wildcard ACLs, empty users/groups, add/remove operations, exact ACL string reconstruction, writable serialization, stack-trace suppression in authorization failures, proxy-user user/group/IP config keys, and remote-address authorization.
- Servlet filter tests for CSRF browser regex defaults and customizations, custom header names, ignored methods, non-browser user agents, missing/invalid headers, X-Frame header configuration, and filter lifecycle.
- Token tests for password creation/retrieval, retriable failures, identifier decoding, URL-string encode/decode, service mutation, renewer selection, trivial renewer behavior, cancellation, managed/unmanaged token handling, and cache-key stability.
- HTTP delegation-token tests for Kerberos and pseudo authenticators, fallback behavior, `doAs` owner handling, header vs query-string transport, JSON response parsing, renew/cancel with and without authentication, unsupported non-HTTP URLs, and thread-safety assumptions.
- Service lifecycle tests for valid and invalid transitions, null configuration rejection, first failure capture, listener notification order and deadlock-safe expectations, blocker map snapshots, lifecycle history snapshots, wait-for-stop timing, `ServiceOperations.stopQuietly()`, and composite child init/start/stop ordering under partial failure.
- Tracing admin tests for span receiver list/add/remove RPC contracts and protobuf bridge compatibility.
- Utility tests for application classloader class/resource precedence, system-class pattern matching, CRC32/CRC32C values against known vectors, reflection configuration injection and inherited field/method discovery, writable copy/clone behavior, throttled thread logging, and platform shell command construction/execution on Unix and Windows.

## Cross-Chunk Notes

`subset-b-007169` should own the earlier portion of `org.apache.hadoop.record.compiler.generated.Rcc` and any package context before line 30694. `subset-b-007171` should complete `org.apache.hadoop.util.Shell` and subsequent utility APIs. The reconciliation lane should merge those adjacent chunks before producing a final report for `Apache_Hadoop_Common_2.8.0.xml`.

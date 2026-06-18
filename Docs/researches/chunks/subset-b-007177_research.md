# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.2.xml lines 30699-36765

## Scope

This chunk is a JDiff API descriptor slice for Apache Hadoop Common 2.8.2. It begins inside the deprecated generated record compiler parser `org.apache.hadoop.record.compiler.generated.Rcc`, continues through generated parser support classes and deprecated record metadata types, then covers Hadoop security, credential providers, authorization, HTTP security filters, security tokens, web delegation token helpers, service lifecycle APIs, tracing administration, and utility classes through the beginning of `org.apache.hadoop.util.Shell`.

The file is generated API metadata rather than executable Java implementation. It records public and protected classes, interfaces, constructors, methods, fields, inheritance, implemented interfaces, checked exceptions, synchronization flags, deprecation state, and selected Javadoc. Its primary purpose is compatibility checking: downstream code, tests, and release tooling can compare this snapshot against another Hadoop Common release to detect public API drift.

## Purpose

The chunk preserves the Hadoop Common 2.8.2 public contract for several compatibility-sensitive subsystems:

- The deprecated Hadoop record compiler/runtime metadata APIs that remain public for old generated record code even though they are replaced by Avro.
- Security identity and credential handling through `Credentials`, `UserGroupInformation`, Kerberos helper functions, group/id mapping providers, and token storage.
- Credential-provider and authorization extension points used by secure clusters to externalize secrets and enforce proxy-user/ACL rules.
- Servlet filters for REST CSRF protection and clickjacking protection.
- Token creation, serialization, renewal, selection, and web delegation-token operations.
- The generic service lifecycle model used by Hadoop daemons and composed subsystems.
- Trace administration protocol surfaces and utility classes for class loading, checksums, reflection, progress callbacks, and platform shell commands.

Because this is a JDiff descriptor, behavior is visible only through signatures and documentation. The runtime implementation is elsewhere in the Hadoop source tree, but the compatibility promise represented here is the external API shape of Hadoop Common 2.8.2.

## Important APIs and Types

### Deprecated record compiler and metadata

The chunk starts at the tail of `org.apache.hadoop.record.compiler.generated.Rcc`. The visible parser methods include `main(String[])`, `usage()`, `driver(String[])`, grammar productions such as `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`, parser reset overloads `ReInit(...)`, token accessors `getNextToken()` and `getToken(int)`, and `generateParseException()`. Public fields `token_source`, `token`, and `jj_nt` expose JavaCC parser state.

`RccConstants` publishes token-kind integers for the record compiler grammar: module, record, include, primitive types, string/buffer/vector/map, braces, angle brackets, semicolon, comma, dot, C string, identifier, lexer states, and `tokenImage`.

`RccTokenManager` implements `RccConstants` and exposes JavaCC lexer lifecycle methods: constructors from `SimpleCharStream`, optional lexical state construction, `setDebugStream(PrintStream)`, `ReInit`, `SwitchTo`, protected `jjFillToken()`, and `getNextToken()`. It exposes lexer fields such as `debugStream`, literal images, lexical state names, `jjnewLexState`, `input_stream`, and `curChar`.

`SimpleCharStream` is the generated character stream supporting constructors from `Reader` or `InputStream` with optional encoding, initial line/column, and buffer size. It exposes buffer management and token-position APIs: `setTabSize`, `getTabSize`, `ExpandBuff`, `FillBuff`, `BeginToken`, `UpdateLineColumn`, `readChar`, begin/end line/column getters, `backup`, many `ReInit` overloads, `GetImage`, `GetSuffix`, `Done`, and `adjustBeginLineColumn`. Its public fields reveal mutable stream state including buffer positions, line/column arrays, CR/LF flags, backing `Reader`, char buffer, and tab size.

`Token` models JavaCC tokens with `kind`, `beginLine`, `beginColumn`, `endLine`, `endColumn`, `image`, `next`, and `specialToken`, plus `toString()` and static `newToken` factories. `TokenMgrError` extends `Error` with lexical error constructors and helpers `addEscapes`, `LexicalError`, and `getMessage`.

The `org.apache.hadoop.record.meta` classes describe deprecated record schemas. `FieldTypeInfo` exposes field id/type metadata and equality/hash behavior. `TypeID` publishes singleton primitive type identifiers (`BoolTypeID`, `BufferTypeID`, `ByteTypeID`, `DoubleTypeID`, `FloatTypeID`, `IntTypeID`, `LongTypeID`, `StringTypeID`) and a `typeVal`. `MapTypeID`, `VectorTypeID`, and `StructTypeID` extend `TypeID` for nested collection and record schemas. `RecordTypeInfo` extends deprecated `org.apache.hadoop.record.Record`, carries a record name, field list, nested struct lookup, and `serialize`, `deserialize`, and `compareTo`. `Utils.skip(RecordInput, String, TypeID)` supports skipping fields based on schema type.

All of these record APIs are explicitly deprecated in favor of Avro but remain part of the public API snapshot.

### Security identity, credentials, and Kerberos helpers

`AccessControlException` in `org.apache.hadoop.security` extends the filesystem permission access-control exception and provides empty, message, and cause constructors.

`Credentials` implements `Writable` and is the in-memory and persisted container for tokens and secret keys. It provides constructors for empty and copy instances; token APIs `getToken(Text)`, `addToken(Text, Token)`, `getAllTokens()`, and `numberOfTokens()`; secret-key APIs `getSecretKey(Text)`, `addSecretKey(Text, byte[])`, `removeSecretKey(Text)`, `getAllSecretKeys()`, and `numberOfSecretKeys()`; token-storage file and stream methods for `Path`, `File`, `DataInputStream`, and `DataOutputStream`; `write`/`readFields`; and merge methods `addAll` and `mergeAll`. `addAll` overwrites existing entries, while `mergeAll` preserves existing entries.

`GroupMappingServiceProvider` defines user-to-groups lookup and cache operations: `getGroups(String)`, `cacheGroupsRefresh()`, `cacheGroupsAdd(List)`, and `GROUP_MAPPING_CONFIG_PREFIX`. `IdMappingServiceProvider` defines numeric UID/GID and name translation, including allowing-unknown variants for user and group names.

`SecurityUtil` is a final static utility class for secure Hadoop RPC and Kerberos integration. Visible APIs include original TGT detection, Kerberos server-principal substitution by hostname or `InetAddress`, configuration-based keytab login, delegation-token service-name construction, extracting hostnames from principals, looking up `KerberosInfo` and `TokenInfo` annotations/providers, token service address and service text construction, token service mutation, privileged execution as login or current user, mapping SASL auth methods into `UserGroupInformation.AuthenticationMethod`, and privileged-port detection. Public constants include `LOG`, `HOSTNAME_PATTERN`, and `FAILED_TO_GET_UGI_MSG_HEADER`.

`UserGroupInformation` is the central identity wrapper around a JAAS `Subject`. The API exposes static configuration and test hooks, security-enabled and Kerberos-credential checks, current/best/login user discovery, ticket-cache and subject construction, keytab and ticket-cache login/relogin/logout operations, remote and proxy user creation, testing users, short/full user names, primary group and group lists, token identifier and token management, credentials extraction/addition, authentication method getters/setters, equality/hash, protected `getSubject`, `doAs` privileged execution overloads, diagnostic logging, and a test `main`. Several login and token methods are synchronized, reflecting shared login/subject state. `HADOOP_TOKEN_FILE_LOCATION` names the environment variable for token cache files.

`UserGroupInformation.AuthenticationMethod` is a public enum-like nested class with `values`, `valueOf(String)`, `valueOf(SaslRpcServer.AuthMethod)`, and `getAuthMethod()`.

### Credential providers and authorization

`CredentialProvider` is an abstract provider of passwords/credentials. It exposes `isTransient()`, mandatory persistence `flush()`, lookup `getCredentialEntry(String)`, alias enumeration `getAliases()`, creation and deletion methods, password-requirement reporting, no-password warning/error text, and `CLEAR_TEXT_FALLBACK`. Its documentation makes the storage abstraction explicit: providers may be transient or backed by external long-term stores.

`CredentialProviderFactory` is an abstract factory with `createProvider(URI, Configuration)`, static `getProviders(Configuration)`, and `CREDENTIAL_PROVIDER_PATH`. The descriptor documents service-loader based discovery of provider implementations and URI path parsing from configuration.

`AccessControlList` implements `Writable` and models user/group ACL strings. It has constructors for a serialized ACL string or separate user/group lists, supports wildcard all-allowed checks, user/group add/remove operations, immutable views through `getUsers()` and `getGroups()`, `isUserInList(UserGroupInformation)`, `isUserAllowed(UserGroupInformation)`, descriptive `toString()`, exact `getAclString()`, and writable serialization. `WILDCARD_ACL_VALUE` is the public wildcard marker.

`AuthorizationException` extends `AccessControlException` but suppresses stack-trace exposure for security purposes by overriding stack-trace access and print methods.

`DefaultImpersonationProvider` implements `ImpersonationProvider` and `Configurable` behavior. It exposes synchronized `getTestProvider()`, configuration setters/getters, `init(String configurationPrefix)`, `authorize(UserGroupInformation, String)`, proxy-superuser key builders for users, groups, and IP addresses, and maps of proxy groups/hosts. `ImpersonationProvider` itself defines initialization by configuration prefix and proxy-user authorization.

### HTTP security filters

`RestCsrfPreventionFilter` implements `javax.servlet.Filter`. It exposes servlet `init`, `doFilter`, and `destroy`; protected `isBrowser(String)` using configurable user-agent regexes; `handleHttpInteraction(HttpInteraction)` for applying the filtering logic independent of servlet plumbing; static `getFilterParams(Configuration, String)` for translating prefixed Hadoop configuration into filter init parameters; and constants for `HEADER_USER_AGENT`, `BROWSER_USER_AGENT_PARAM`, `CUSTOM_HEADER_PARAM`, and `CUSTOM_METHODS_TO_IGNORE_PARAM`. The documented behavior rejects browser-origin REST requests missing a configurable custom header, while allowing non-browser or ignored-method traffic depending on configuration.

`XFrameOptionsFilter` also implements `Filter` and adds a configurable `X-Frame-Options` header to protect Hadoop webapps from clickjacking. It exposes `init`, `doFilter`, `destroy`, `getFilterParams(Configuration, String)`, and constants `X_FRAME_OPTIONS` and `CUSTOM_HEADER_PARAM`.

### Token and delegation-token APIs

`SecretManager<T extends TokenIdentifier>` is the server-side abstract token secret manager. It requires subclasses to implement protected `createPassword(T)`, public `retrievePassword(T)`, and `createIdentifier()`. It also exposes `retriableRetrievePassword(T)` for HA/retry-aware failures (`InvalidToken`, `StandbyException`, `RetriableException`, `IOException`), `checkAvailableForRead()`, protected random `generateSecret()`, and static HMAC/password helper methods from identifier bytes and secret keys.

`Token<T extends TokenIdentifier>` implements `Writable` and is the client-side token form. Constructors cover identifier plus secret manager, raw identifier/password/kind/service components, default construction, and copy construction. It exposes raw identifier and password access, `decodeIdentifier()`, synchronized `getKind()`, service get/set, public/private token cloning checks, writable serialization, URL-safe encode/decode, equality/hash/string/cache-key behavior, and managed token operations `isManaged`, `renew(Configuration)`, and `cancel(Configuration)`. `Token.TrivialRenewer` extends `TokenRenewer` for token kinds that are not managed.

`TokenIdentifier` is an abstract `Writable` with required `getKind()` and `getUser()`, plus byte serialization through `getBytes()` and `getTrackingId()` derived from identifier bytes. `TokenInfo` is an annotation interface for declaring token metadata on protocols. `TokenRenewer` is the abstract renewal/cancel extension point with `handleKind(Text)`, `isManaged(Token)`, `renew(Token, Configuration)`, and `cancel(Token, Configuration)`. `TokenSelector<T>` selects a token of a kind/service from a collection.

`DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` with Hadoop delegation token support. Constructors allow default, explicit `DelegationTokenAuthenticator`, connection configurator, or both. Static controls configure the default authenticator class and whether delegation tokens are carried in query strings. Connection-opening overloads accept a URL, token wrapper, optional `doAsUser`, and optional HTTP method. It also exposes delegation token get, renew, and cancel methods with overloads for `doAsUser`. Its nested `Token` extends `AuthenticatedURL.Token` and stores a Hadoop `Token`.

`DelegationTokenAuthenticator` wraps another `Authenticator` and adds delegation-token operations. It exposes `setConnectionConfigurator`, `authenticate`, get/renew/cancel methods with optional `doAsUser`, and HTTP/JSON parameter constants such as `OP_PARAM`, `DELEGATION_TOKEN_HEADER`, `DELEGATION_PARAM`, `TOKEN_PARAM`, `RENEWER_PARAM`, `DELEGATION_TOKEN_JSON`, `DELEGATION_TOKEN_URL_STRING_JSON`, and `RENEW_DELEGATION_TOKEN_JSON`. `KerberosDelegationTokenAuthenticator` provides SPNEGO with pseudo-auth fallback, and `PseudoDelegationTokenAuthenticator` models simple authentication based on current UGI/query-string user.

### Service lifecycle APIs

`Service` is the public lifecycle interface and extends `Closeable`. It defines `init(Configuration)`, `start()`, `stop()`, `close()`, listener registration/unregistration, name/config/state/start-time accessors, `isInState(STATE)`, failure cause/state accessors, `waitForServiceToStop(long)`, lifecycle history, and blocker reporting. The documentation defines state transitions from `NOTINITED` to `INITED` to `STARTED` to `STOPPED`, with failed init/start requiring stop.

`AbstractService` implements `Service` and provides the base state-machine implementation. Public and protected APIs include final state/failure accessors, protected `setConfig`, lifecycle entry points `init`, `start`, `stop`, final `close`, failure recording, stop waiting, protected hooks `serviceInit`, `serviceStart`, and `serviceStop`, instance and global listener registration, identity/config/start-time/history accessors, state predicate, blockers, and `toString`. Javadoc notes that hook methods are called at most once per service instance and that `serviceStop` must be robust even after partial initialization or failures.

`CompositeService` extends `AbstractService` to manage child services. It exposes cloned child-service list access, protected `addService`, `addIfService`, synchronized `removeService`, and hook overrides for init/start/stop propagation. `STOP_ONLY_STARTED_SERVICES` controls whether shutdown attempts all children or only started children, with special handling after init/start failures.

`LifecycleEvent` is a serializable public event with public fields `time` and `state`. `LoggingStateChangeListener` implements `ServiceStateChangeListener` and logs state changes. `ServiceOperations` exposes static `stop(Service)` and `stopQuietly(...)` helpers. `ServiceStateChangeListener` defines the `stateChanged(Service)` callback. `ServiceStateException` wraps lifecycle failures and converts checked exceptions to runtime exceptions. `ServiceStateModel` is the explicit state-transition helper with constructors, `getState`, `isInState`, `ensureCurrentState`, `enterState`, `checkStateTransition`, `isValidStateTransition`, and `toString`.

### Tracing and utility APIs

`SpanReceiverInfo` exposes tracing span receiver id and class name. `SpanReceiverInfoBuilder` builds receiver info from a class name and configuration key/value pairs. `TraceAdminProtocol` defines administrative RPCs to list, add, and remove span receivers and publishes `versionID`. `TraceAdminProtocolPB` combines the protobuf blocking interface with `VersionedProtocol`.

`ApplicationClassLoader` extends `URLClassLoader` and exposes constructors from URL arrays or classpath strings, `getResource`, `loadClass` overloads, static `isSystemClass(String, List)`, and `SYSTEM_CLASSES_DEFAULT`. It is the application-first/system-class-aware classloader used by Hadoop applications.

`IPList` defines `isIn(String)` for IP/range membership checks. `Progressable` defines the single `progress()` callback used by long-running operations.

`PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum`, exposing constructors, `getValue`, `reset`, `update(byte[], int, int)`, and `update(int)`. `PureJavaCrc32C` documents use of the CRC32-C/iSCSI polynomial.

`ReflectionUtils` provides public static helpers for configurable object initialization and reflective utilities: `setConf`, generic `newInstance(Class, Configuration)`, contention tracing toggling, synchronized `printThreadInfo`, interval-limited `logThreadInfo`, type-safe `getClass(T)`, writable copy/clone through serialization, and inherited-field/method enumeration.

The chunk ends inside `Shell`, an abstract command-execution helper. Visible constructors configure optional minimum run interval and stderr redirection. Static APIs include deprecated `isJava7OrAbove()`, Windows command-line length checking, OS-specific commands for group and netgroup lookup, permission/owner/symlink/readlink/process/signal operations, environment-variable regex generation, script extension and run-command construction, Hadoop home lookup, Hadoop bin qualification, and winutils discovery through `hasWinutilsPath`, `getWinUtilsPath`, and the start of `getWinUtilsFile()`. The remainder of `Shell` continues in the next chunk.

## Control Flow

The XML itself has no runtime control flow. It does, however, expose the intended runtime flow of the APIs:

- Record compiler flow is JavaCC parser flow: `SimpleCharStream` feeds `RccTokenManager`, the token manager yields `Token` instances, and `Rcc` grammar methods build compiler model objects such as `JFile`, `JRecord`, `JField`, `JType`, `JMap`, and `JVector`.
- Record metadata flow uses `TypeID` values to describe field schemas, collection nesting, and record structures; `RecordTypeInfo` can serialize/deserialize schema metadata and `Utils.skip` can skip unknown fields based on type.
- Credential flow stores tokens and secret keys in `Credentials`, reads or writes token storage files/streams, and merges credentials into `UserGroupInformation`.
- Kerberos login flow passes configuration keys to `SecurityUtil.login`, substitutes hostnames into principals, and updates global or returned `UserGroupInformation` instances via keytab or ticket-cache login paths.
- Proxy authorization flow constructs a proxy UGI, initializes an `ImpersonationProvider` with a configuration prefix, then checks real/effective users plus remote address against configured ACLs and host rules.
- CSRF/clickjacking filter flow initializes servlet filters from prefixed Hadoop configuration, then applies header or frame protections in `doFilter` before continuing the servlet chain.
- Token flow creates a `TokenIdentifier`, uses `SecretManager` to compute or validate passwords, serializes client-side `Token` values, selects matching tokens for services, and delegates renew/cancel to registered `TokenRenewer` implementations.
- Web delegation token flow authenticates an HTTP connection through an underlying authenticator, then sends get/renew/cancel operations with URL parameters or headers and parses returned token JSON.
- Service lifecycle flow moves services through `NOTINITED`, `INITED`, `STARTED`, and `STOPPED`, dispatches listener callbacks, records lifecycle history and failures, and cascades child service state changes in `CompositeService`.
- Utility flow includes reflective instance construction plus configuration injection, writable copying via serialization buffers, checksum state updates, classloader system-class filtering, and OS-specific shell command array generation.

## State and Persistence Behavior

This chunk is static generated metadata, but the represented APIs expose substantial mutable and persistent state:

- JavaCC record compiler classes maintain mutable parser, token, character buffer, line/column, lexical state, and debug stream state. These classes are deprecated but still part of binary/source compatibility.
- Record metadata classes persist schema descriptions, type identifiers, field names, nested struct definitions, and serialized record type information.
- `Credentials` persists token and secret-key maps through Hadoop `Writable` serialization and token storage files. `addAll` and `mergeAll` have different overwrite semantics that affect credential propagation.
- `UserGroupInformation` wraps a mutable JAAS `Subject`, login method state, keytab/ticket-cache credentials, token identifiers, tokens, and credentials. Several APIs are synchronized because login state and subject contents are process/global or shared.
- Credential providers may be transient or persistent. `flush()` is the explicit persistence boundary for provider-backed credential changes; password-required reporting affects whether a provider can safely operate.
- ACL and impersonation objects hold parsed user/group/host rules and are serialized or initialized from configuration.
- HTTP filters hold initialized filter parameters such as required header names, ignored methods, browser user-agent regexes, and X-Frame-Options header values.
- Tokens persist identifier bytes, password bytes, kind, service, and optional private-clone relationships. URL string encoding is another stable external representation.
- Secret managers own secret keys and token-validation policy, including HA availability/read checks and retryable failure signaling.
- Service objects store lifecycle state, start time, failure cause/state, lifecycle history, listener registrations, global listeners, and blocker maps. Composite services additionally store child services.
- Tracing administration state is external to the descriptor but exposed through span receiver ids, class names, and configuration pairs.
- Checksums keep incremental CRC accumulator state. Reflection utility copy operations use serialization buffers, and `Shell` state includes minimum execution interval and stdout/stderr merge behavior in constructors.

## Dependencies and Integration Points

The APIs in this chunk integrate with Java IO, Java security, JAAS `Subject`, Kerberos tickets, servlet filters, Hadoop `Configuration`, Hadoop `Writable`, filesystem `Path`, IPC exceptions and protocols, protobuf RPC, HTTP authentication client classes, Commons Logging, Java cryptography, Java networking, Java classloading, and `java.util.zip.Checksum`.

Important Hadoop integration points include:

- Deprecated record compiler/runtime compatibility for old generated record classes and build tools.
- Token cache loading via `HADOOP_TOKEN_FILE_LOCATION` and token storage files used by MapReduce/YARN/HDFS clients.
- Group and id mapping providers used by authorization, filesystems, NFS gateways, and identity-aware services.
- `SecurityUtil` principal substitution, keytab login, token-service construction, and protocol annotation lookup used by secure RPC clients and servers.
- `UserGroupInformation` as the central identity object used by RPC, filesystem access, proxy users, delegation tokens, and privileged execution.
- Credential provider paths configured through `CredentialProviderFactory.CREDENTIAL_PROVIDER_PATH`, allowing JCEKS, user, or third-party credential stores.
- `AccessControlList` and `DefaultImpersonationProvider` for service authorization and proxy-user `doAs` checks.
- Hadoop HTTP servers that install `RestCsrfPreventionFilter` and `XFrameOptionsFilter`.
- Delegation token web endpoints that support SPNEGO/pseudo authentication and token lifecycle operations over HTTP/S.
- Hadoop daemon and client subsystems based on `Service`, `AbstractService`, and `CompositeService`.
- Trace admin RPC clients/servers that manage span receivers through protocol and protobuf interfaces.
- MapReduce/YARN classloader isolation through `ApplicationClassLoader`.
- Long-running filesystem and job operations that accept `Progressable`.
- Data checksum paths using pure-Java CRC32/CRC32C when native or JDK-specific alternatives are unavailable.
- Platform-specific shell helpers for permissions, process signaling, Hadoop bin resolution, Windows `winutils`, and group lookup.

## Risks and Edge Cases

- This is a compatibility artifact. Changing public signatures, inheritance, exceptions, deprecation markers, visibility, synchronization, or fields can break downstream code or JDiff compatibility even when behavior remains equivalent.
- The chunk starts inside `Rcc` and ends inside `Shell`; final whole-class research must reconcile adjacent chunks before making complete class-surface claims.
- Deprecated record APIs are still public. Removing them or altering generated JavaCC fields/methods can break old generated record code even though new code should use Avro.
- JavaCC parser classes expose mutable public fields and are not designed as robust general-purpose thread-safe APIs.
- Credential and token serialization is security-sensitive and compatibility-sensitive. Incorrect alias overwrite/merge behavior, token service text, or URL encoding can make jobs unable to authenticate.
- `Credentials.getSecretKey` returns `byte[]`; callers must avoid leaking, mutating, or retaining sensitive bytes longer than necessary.
- Kerberos principal hostname substitution depends on DNS and FQDN behavior. Mis-substitution can cause login failures or service principal mismatch during secure RPC.
- `UserGroupInformation` has shared login state, synchronized relogin paths, and token/subject mutation. Tests and services can become order-dependent if they mutate global login configuration or current login user.
- Proxy-user authorization combines real user, effective user, groups, and remote address. Configuration prefix mistakes or stale group caches can either deny legitimate traffic or allow unintended impersonation.
- `AuthorizationException` deliberately hides stack traces. Debugging must preserve the security property while still providing enough audit context elsewhere.
- CSRF filter browser detection is regex-driven and custom-header based. Too broad ignored-method configuration or too narrow browser detection can weaken protection; too broad detection can break non-browser clients.
- Delegation token HTTP APIs are documented as not thread-safe through `AuthenticatedURL`; shared instances can race authentication or token state.
- Token renewal/cancel depends on discoverable `TokenRenewer` implementations and correct token kind/service metadata. Unmanaged tokens should follow trivial renewer semantics.
- `SecretManager.retriableRetrievePassword` is HA-sensitive: wrong exception mapping can prevent client retry/failover or cause retries of permanently invalid tokens.
- Service lifecycle implementations must handle partial initialization and failed start/stop paths. `serviceStop` must be resilient to null fields and should not prevent cleanup of later components.
- Global service listeners can leak references or receive events from all services in a JVM, which matters for tests and long-lived daemons.
- `CompositeService` stop ordering and `STOP_ONLY_STARTED_SERVICES` policy can affect resource cleanup after child init/start failures.
- `ApplicationClassLoader` system-class filtering is security and compatibility sensitive; wrong patterns can load Hadoop/JDK classes from user jars or hide application classes.
- Pure Java CRC implementations are persistent data-integrity dependencies; checksum polynomial or update-order drift can corrupt interoperability.
- `ReflectionUtils.copy` destroys the destination contents before replacing them through serialization, so exceptions can leave `dst` unusable.
- `Shell` command construction is OS-sensitive. Windows command-line limits, `winutils` resolution, shell extension inference, and process signaling differ across environments and must be tested on target platforms.

## Test and Validation Signals

Validation for this API slice should include:

- JDiff or equivalent API compatibility checks against the intended Hadoop Common 2.8.2 baseline, covering public/protected signatures, fields, checked exceptions, inheritance, implemented interfaces, synchronization, and deprecation text.
- Deprecated record compiler tests that parse representative `.jr` record specifications, include files, primitive/vector/map/record field declarations, parser reinitialization, lexical errors, and token position reporting.
- Record metadata round-trip tests for primitive `TypeID`, `MapTypeID`, `VectorTypeID`, `StructTypeID`, `FieldTypeInfo`, and `RecordTypeInfo` serialization/deserialization and equality/hash behavior.
- `Credentials` tests for token/secret-key add/get/remove, `addAll` overwrite behavior, `mergeAll` non-overwrite behavior, writable serialization, file/stream token storage, and sensitive byte handling.
- Group and id mapping provider tests for existing, missing, and cache-refresh cases, including unknown UID/GID fallback methods.
- Kerberos/security utility tests for principal host substitution, `0.0.0.0`/null/default host behavior, reverse-DNS behavior, keytab login failure modes, token service construction, protocol annotation lookup, and privileged execution wrappers.
- `UserGroupInformation` tests for secure and simple modes, current/login/best user resolution, ticket-cache and keytab login/relogin/logout, remote/proxy users, testing users, group lookup, token and credentials attachment, authentication method mapping, equality/hash, and `doAs` exception mapping.
- Credential provider tests for transient versus persistent providers, service-loader discovery, URI path parsing, create/get/delete/list aliases, `flush`, password-needed warning/error behavior, and clear-text fallback policy.
- ACL and impersonation tests for wildcard ACLs, empty users/groups, exact ACL string serialization, writable round trips, user/group membership checks, hidden stack traces in `AuthorizationException`, proxy user/group/host configuration keys, and authorize pass/fail paths.
- HTTP filter tests for CSRF custom header enforcement, browser regex configuration, ignored methods, non-browser clients, servlet-chain continuation/rejection, filter parameter extraction, and X-Frame-Options header configuration.
- Token tests for secret-manager password creation/retrieval, retryable and standby exceptions, identifier byte serialization, tracking IDs, token writable and URL-safe round trips, service/kind matching, private clone semantics, renewer discovery, trivial renewer behavior, and selector behavior over mixed token collections.
- Web delegation token tests for SPNEGO and pseudo-auth flows, fallback behavior, query-string versus header delegation token transport, get/renew/cancel operations, `doAsUser` overloads, JSON field parsing, and non-thread-safe token isolation.
- Service lifecycle tests for legal and illegal state transitions, failed init/start stop behavior, listener/global-listener notifications, lifecycle history, blocker maps, failure cause/state recording, stop waiting, quiet stop helpers, `ServiceStateException.convert`, and composite child ordering/cleanup after failures.
- Tracing protocol tests for list/add/remove span receivers, builder configuration pairs, protobuf protocol versioning, and invalid receiver removal.
- Utility tests for `ApplicationClassLoader` resource/class lookup and system-class filtering, `IPList` membership, `Progressable` invocation in long operations, CRC32 and CRC32C known vectors, `ReflectionUtils` configuration injection/new instance/copy/thread-info logging, and `Shell` command arrays on Unix and Windows including command length, script extensions, Hadoop home/bin lookup, and winutils resolution.

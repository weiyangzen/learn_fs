# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml lines 42862-48966

## Scope

This chunk is a Hadoop Common 3.5.0 JDiff public API slice. It begins inside `org.apache.hadoop.security.alias.CredentialProvider`, then covers security authorization, HTTP security filters, token and delegation-token APIs, the service lifecycle and service launcher contracts, and the first part of `org.apache.hadoop.util` utility APIs through `StringInterner`. The source is an API XML snapshot rather than Java implementation source, so the research is based on exposed classes, method contracts, state fields, documented control flow, persistence hooks, and compatibility signals.

## Purpose

The chunk documents infrastructure APIs used across Hadoop daemons, clients, command-line tools, and HTTP endpoints:

- Credential provider and ACL APIs abstract credential persistence, ACL string parsing, Writable serialization, and proxy-user authorization.
- HTTP security filters add CSRF prevention and `X-Frame-Options` response hardening for servlet deployments.
- Token APIs define client-side token encoding, token identifiers, selectors, renewer plugins, shared-secret generation, and delegation-token state management.
- Delegation-token web APIs extend `AuthenticatedURL` so HTTP clients can acquire, send, renew, and cancel Hadoop delegation tokens over HTTP/S.
- Service APIs define the shared lifecycle model for Hadoop services, composite service ordering, listener notification, failure recording, lifecycle history, and standardized service-launch exit codes.
- Utility APIs cover application classloader isolation, duration logging, IP-list membership, CRC implementations, reflection helpers, shell command execution, shutdown-hook ordering, and string interning.

## Important APIs, Types, And Functions

### Credential Providers

The visible tail of `org.apache.hadoop.security.alias.CredentialProvider` exposes the provider contract for credential storage. Implementations must be thread safe. Key methods are `flush()`, `getCredentialEntry(String)`, `getAliases()`, `createCredentialEntry(String, char[])`, and `deleteCredentialEntry(String)`, all IO-bearing where storage access may fail. The non-abstract password helpers `needsPassword()`, `noPasswordWarning()`, and `noPasswordError()` model providers whose backing store requires a password not found through normal mechanisms. `isTransient()` is documented for providers intended for temporary job access rather than long-term storage, such as user-backed providers. `CLEAR_TEXT_FALLBACK` is a public configuration-related constant.

`CredentialProviderFactory` is a service-loader based factory. `createProvider(URI, Configuration)` is the factory method implemented by concrete factories; `getProviders(Configuration)` resolves the configured provider path from `CREDENTIAL_PROVIDER_PATH` and returns the matching provider list.

### Authorization And Impersonation

`AccessControlList` represents a configured ACL and implements `Writable`. It can be built from a single ACL string of comma-separated users followed by comma-separated groups, or separate user and group strings. It exposes `addUser`, `addGroup`, `removeUser`, `removeGroup`, `getUsers`, `getGroups`, `isAllAllowed`, `isUserInList(UserGroupInformation)`, `isUserAllowed(UserGroupInformation)`, `getAclString`, `toString`, `write(DataOutput)`, and `readFields(DataInput)`. `WILDCARD_ACL_VALUE` models all-access ACLs. `USE_REAL_ACLS` is significant for proxied users: `isUserInList` treats `USE_REAL_ACLS + realUser` as a match for a proxied user.

`AuthorizationException` extends `AccessControlException` and deliberately suppresses stack-trace visibility for security. It overrides `getStackTrace()` and all `printStackTrace` variants, which is an API-level signal that callers should not rely on stack details for this exception.

`DefaultImpersonationProvider` implements `ImpersonationProvider` and `Configurable`. It reads proxy-user configuration with a configurable prefix, authorizes a `UserGroupInformation` plus remote `InetAddress`, and exposes helper methods for user, group, and IP configuration keys: `getProxySuperuserUserConfKey`, `getProxySuperuserGroupConfKey`, and `getProxySuperuserIpConfKey`. It also exposes current proxy group and host maps for inspection. `getTestProvider()` returns a synchronized singleton-style test provider.

`ImpersonationProvider` is the extension point. Implementations receive `init(String configurationPrefix)`, then authorize either `(UserGroupInformation, String remoteAddress)` or `(UserGroupInformation, InetAddress remoteAddress)`, and inherit `Configurable` setup through `setConf`/`getConf`.

### HTTP Security Filters

`RestCsrfPreventionFilter` implements `javax.servlet.Filter`. Its public surface includes `init(FilterConfig)`, `doFilter(ServletRequest, ServletResponse, FilterChain)`, `destroy()`, `getFilterParams(Configuration, String)`, `isBrowser(String userAgent)`, and `handleHttpInteraction(HttpServletRequest, HttpServletResponse, FilterChain)`. Constants define the user-agent header, browser-user-agent parameter, custom CSRF header parameter, methods-to-ignore parameter, and default header name. The intended flow is: detect browser-like requests, require the configured custom header on unsafe methods, and let configured ignored methods through.

`XFrameOptionsFilter` is another servlet `Filter`. It initializes from filter config, sets the `X-Frame-Options` response header in `doFilter`, exposes `getFilterParams(Configuration, String)`, and publishes `X_FRAME_OPTIONS` and `CUSTOM_HEADER_PARAM`.

`org.apache.hadoop.security.ssl.SSLChannelMode` is an enum-style public nested type from `DelegatingSSLSocketFactory`, exposed here with `values()` and `valueOf(String)`.

### Token Core

`SecretManager<T extends TokenIdentifier>` is the abstract base for issuing and validating token passwords. Implementations provide `createPassword(T)`, `retrievePassword(T)`, and `createIdentifier()`. The visible concrete helpers include `retriableRetrievePassword(T)`, `checkAvailableForRead()`, static `generateSecret()`, `validateSecretKeyLength(byte[])`, static password generation from identifier bytes and a `SecretKey`, and `createSecretKey(byte[])`. It depends on JCE `SecretKey` and logs through SLF4J. The nested `InvalidToken` exception is referenced by retrieval and verification APIs.

`Token<T extends TokenIdentifier>` is the client-side token representation and implements `Writable`. Constructors cover creating from an identifier plus `SecretManager`, raw identifier/password/kind/service fields, default deserialization, and copy construction. Core fields are exposed through `getIdentifier`, `getPassword`, synchronized `getKind`/`setKind`, `getService`/`setService`, and token cloning helpers. `privateClone(Text)` creates a token tied to a private service, while `isPrivate()` and `isPrivateCloneOf(Text)` differentiate public and private forms. Serialization and transport surfaces are `readFields`, `write`, `encodeToUrlString`, and `decodeFromUrlString`. Runtime operations `isManaged`, `renew(Configuration)`, and `cancel(Configuration)` delegate to token renewers and can raise IO or interruption.

`TokenIdentifier` is a `Writable` identifier contract. Implementations provide `getKind()` and `getUser()`. Base methods serialize to bytes with `getBytes()` and provide a cross-session tracking ID, documented as an MD5 of the identifier bytes.

`TokenInfo` is an annotation-style interface whose `value()` names the `TokenSelector` class for a token family. `TokenSelector<T>` chooses a token for a service from a token collection. `TokenRenewer` is the plugin contract for renew/cancel support: `handleKind(Text)`, `isManaged(Token<?>)`, `renew(Token<?>, Configuration)`, and `cancel(Token<?>, Configuration)`. `TrivialRenewer` is a base class for unmanaged token kinds; subclasses implement `getKind()`, while `isManaged` is false and renew/cancel are trivial.

### Delegation Token Manager

`AbstractDelegationTokenIdentifier` extends `TokenIdentifier` with delegation-token metadata: owner, renewer, real user, issue date, max date, sequence number, and master key ID. It provides setters/getters, equality/hash behavior, Writable serialization, `toString()`, and `toStringStable()`. `getUser()` resolves the encoded user or owner into a `UserGroupInformation`.

`AbstractDelegationTokenSecretManager<TokenIdent>` extends `SecretManager<TokenIdent>` and is the central stateful delegation-token manager. Its constructor takes intervals for key rolling, maximum token lifetime, renew interval, and expired-token scan interval. Public lifecycle and recovery APIs include `startThreads()`, `stopThreads()`, `reset()`, `isRunning()`, `addKey(DelegationKey)`, `getAllKeys()`, `getCurrentTokensSize()`, and `addPersistedDelegationToken(TokenIdent, long)`. The recovery method must be called before activation and marks tokens with unknown `DelegationKey`s as expired for cleanup.

The class exposes many protected hooks for durable storage and HA/externalized state, especially ZooKeeper-backed implementations: `storeNewMasterKey`, `removeStoredMasterKey`, `storeDelegationKey`, `updateDelegationKey`, `storeNewToken`, `removeStoredToken`, `updateStoredToken`, `storeToken`, `updateToken`, `removeExpiredStoredToken`, `logUpdateMasterKey`, `logExpireToken`, and `logExpireTokens`. It also exposes protected/current-id helpers for external storage: `getCurrentKeyId`, `incrementCurrentKeyId`, `setCurrentKeyId`, `getDelegationTokenSeqNum`, `incrementDelegationTokenSeqNum`, and `setDelegationTokenSeqNum`.

Validation and mutation APIs include `rollMasterKey()`, protected `createPassword(TokenIdent)`, `checkToken(TokenIdent)`, public `retrievePassword(TokenIdent)`, `verifyToken(TokenIdent, byte[])`, `renewToken(Token<TokenIdent>, String)`, `cancelToken(Token<TokenIdent>, String)`, `decodeTokenIdentifier(Token<TokenIdent>)`, and token tracking helpers `getTrackingIdIfEnabled` and `getTokenTrackingId`. Metrics support is exposed through `getTopTokenRealOwners(int)`, `addTokenForOwnerStats(TokenIdent)`, `syncTokenOwnerStats()`, and `getMetrics()`.

State fields are explicitly documented: `currentTokens` maps token identifiers to token information and is protected by the manager monitor; `allKeys`, `currentId`, and `delegationTokenSequenceNumber` are also monitor-protected; `tokenOwnerStats` tracks real-owner counts for metrics; `storeTokenTrackingId` controls whether tracking IDs are stored in token information; `running` is volatile; and `noInterruptsLock` prevents interruption of the update thread while held.

### Delegation Tokens Over HTTP

`DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` and is explicitly not thread safe. It uses `KerberosDelegationTokenAuthenticator` by default, with fallback to pseudo authentication. Constructors accept an optional `DelegationTokenAuthenticator` and/or `ConnectionConfigurator`. Static methods `setDefaultDelegationTokenAuthenticator` and `getDefaultDelegationTokenAuthenticator` change or read the default authenticator class. `setUseQueryStringForDelegationToken(boolean)` exists for WebHDFS backwards compatibility; otherwise delegation tokens are sent in the `DelegationTokenAuthenticator.DELEGATION_TOKEN_HEADER` header.

Its `openConnection` overloads authenticate a URL using either an embedded delegation token, an `AuthenticatedURL.Token`, or a `doAs` user. If a delegation token is present in the nested `Token`, that token takes precedence over the configured authenticator. It can select a delegation token from `Credentials` based on URL, obtain a new token with `getDelegationToken`, renew with `renewDelegationToken`, and cancel with `cancelDelegationToken`. Cancel operations are documented as not requiring authentication by the configured authenticator.

`DelegationTokenAuthenticator` wraps another `Authenticator`. It supports `setConnectionConfigurator`, `authenticate`, token acquisition, token renewal, and token cancellation, with overloads that include a `doAsUser`. Public constants define HTTP query and JSON field names: `OP_PARAM`, `DELEGATION_TOKEN_HEADER`, `DELEGATION_PARAM`, `TOKEN_PARAM`, `RENEWER_PARAM`, `SERVICE_PARAM`, `DELEGATION_TOKEN_JSON`, `DELEGATION_TOKEN_URL_STRING_JSON`, and `RENEW_DELEGATION_TOKEN_JSON`.

`KerberosDelegationTokenAuthenticator` adds SPNEGO plus delegation-token operations and falls back to `PseudoDelegationTokenAuthenticator` if the endpoint does not trigger SPNEGO. `PseudoDelegationTokenAuthenticator` accepts the user name from a query parameter, matching Hadoop Simple authentication's trust in `UserGroupInformation.getCurrentUser()`. The nested web `Token` extends `AuthenticatedURL.Token` and stores a Hadoop delegation token through `getDelegationToken()` and `setDelegationToken(...)`.

### Service Lifecycle

`Service` is the core lifecycle interface and extends `Closeable`. Its state machine is `NOTINITED -> INITED -> STARTED -> STOPPED`, exposed through enum `Service.STATE`, whose `getValue()` returns a numeric code. `init(Configuration)` must move from `NOTINITED` to `INITED`, or call `stop()` and enter `STOPPED` on failure. `start()` must move from `INITED` to `STARTED`, or stop on failure. `stop()` must be a no-op if already stopped and should be robust regardless of partially initialized fields. `close()` must relay to `stop()` and is documented to never throw `IOException`. Read APIs include name, config, state, start time, failure cause/state, lifecycle history, blockers, and `waitForServiceToStop(long)`.

`AbstractService` is the base implementation. It manages state transitions, failure recording via `noteFailure(Exception)`, listener registration, global listener registration, start time, lifecycle history snapshots, blockers, and `close()` relay. Subclasses implement or override `serviceInit(Configuration)`, `serviceStart()`, and `serviceStop()`, each called once per instance lifecycle by the base transition logic. The docs emphasize non-reentrancy guarantees around these hooks and require `serviceStop()` to tolerate failures and null internal fields.

`CompositeService` extends `AbstractService` and manages child services. It exposes a cloned snapshot from `getServices()`, protected `addService`, `addIfService(Object)`, `removeService`, and lifecycle hooks that initialize, start, and stop children. `STOP_ONLY_STARTED_SERVICES` documents a shutdown policy tradeoff: close everything or only services that reached started state, while still stopping children that fail during init/start.

`LifecycleEvent` is a serializable record with public `time` and `state` fields. `LoggingStateChangeListener` logs state changes at INFO level. `ServiceStateChangeListener` is called after state changes, on the thread that initiated the transition, while the service is in a synchronized section; the docs warn that long-lived listener work can block transitions and listener-spawned calls back into the service can deadlock.

`ServiceOperations` is a final static helper with `stop(Service)` and `stopQuietly` overloads. It catches and logs exceptions for cleanup paths but not `Throwable`s. The `commons-logging` overload is deprecated in favor of the SLF4J `Logger` overload. `ServiceStateException` is a runtime exception implementing `ExitCodeProvider`; it can derive an exit code from a cause or use `EXIT_SERVICE_LIFECYCLE_EXCEPTION`, and its `convert` helpers wrap arbitrary failures as runtime exceptions.

`ServiceStateModel` is the standalone thread-safe state-machine helper. It exposes `getState`, `isInState`, `ensureCurrentState`, synchronized `enterState(STATE)`, static `checkStateTransition`, static `isValidStateTransition`, and `toString`.

### Service Launcher

`AbstractLaunchableService` extends `AbstractService` and implements `LaunchableService`. Its base `bindArgs(Configuration, List<String>)` logs arguments at debug and returns the same configuration, while `execute()` returns success (`0`).

`LaunchableService` extends `Service` for command-line managed services. `bindArgs(Configuration, List<String>)` is called before `init(Configuration)` and may mutate or replace the configuration, often to instantiate `YarnConfiguration` or another subclass that loads default resources. `execute()` is called after `start()` and its return value becomes the process exit code unless an exception overrides it.

`HadoopUncaughtExceptionHandler` is intended for installation through `Thread.setDefaultUncaughtExceptionHandler`. Standard exceptions are logged or delegated; `Error` causes process shutdown because the system state is considered unknown.

`LauncherExitCodes` standardizes exit codes. It includes success, generic failure, client-initiated shutdown, launch failure, interrupted, argument/usage/configuration errors, unauthorized/forbidden/not-found style client errors, connectivity and service-side failures, unsupported version, service creation failure, and lifecycle exception. The docs map many codes loosely to HTTP status classes while preserving Unix `0` for success.

`ServiceLaunchException` extends `ExitUtil.ExitException` and implements both `ExitCodeProvider` and `LauncherExitCodes`. Constructors support exit-code plus cause, message, `String.format` style varargs in English locale, and explicit cause plus format. The package-level launcher docs describe the broader flow: instantiate a service with a no-arg or string constructor, load `--conf <file>` local configuration files, call `bindArgs` for launchable services, initialize, start, execute or wait for stop, stop on completion, convert exceptions or exit-code-providing exceptions to `ExitException`, and terminate through `ExitUtil`. Interrupt handling uses an escalator that tries service shutdown on first signal and halts on a repeated signal.

### Tools And Utility Classes

`org.apache.hadoop.tools.TableListing.Justification` appears as an enum-style nested public type with `values()` and `valueOf(String)`. Empty package declarations for `tools.protocolPB` and `tracing` are present in the snapshot.

`ApplicationClassLoader` extends `URLClassLoader` for application isolation. It prefers application JARs over the parent loader except for system classes. Constructors accept URLs or a classpath string, parent loader, and system-class patterns. `getResource`, `loadClass`, protected synchronized `loadClass(String, boolean)`, and static `isSystemClass(String, List<String>)` define loading behavior. `SYSTEM_CLASSES_DEFAULT` lists JDK, Hadoop, resources, and selected third-party classes that should remain parent/system loaded.

`OperationDuration` records start and finished times. It exposes `finished()`, `value()` in milliseconds, `asDuration()`, `getDurationString()`, `humanTime(long)`, and `toString()`. `DurationInfo` extends it and implements `AutoCloseable`, logging the formatted operation text at construction and the final duration on `close()`, which makes it a try-with-resources timing helper.

`IPList` is a simple membership interface with `isIn(String ipAddress)`. `Shell.OSType` is exposed as an enum-style nested type with `values()` and `valueOf(String)`. `Progressable` is a callback interface with `progress()`.

`PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum`. Each has `getValue`, `reset`, `update(int)`, `update(byte[], int, int)`, and protected `mod(int)`. They are pure Java checksum implementations used where native or JDK alternatives are not desired.

`ReflectionUtils` provides common reflection helpers: `setConf(Object, Configuration)`, overloaded `newInstance(Class<T>, Configuration)` and `newInstance(Class<T>, Configuration, Class<?>[])`, contention tracing toggles, thread-info printing/logging, class lookup by name, deep copy through serialization, `cloneWritableInto`, and inherited field/method collection. The `commons-logging` `logThreadInfo` overload is deprecated in favor of the SLF4J overload.

`Shell` is an abstract base for running native commands. It provides constructors with timeout and parent-environment inheritance, Java version checks, Windows command-line length checks, `bashQuote`, group/user command builders, permission/owner/symlink/readlink/process/signal command builders, environment variable regex access, script extension helpers, run-script command construction, Hadoop home and qualified bin discovery, and Windows `winutils` discovery. Protected instance setup includes `setEnvironment(Map)`, `setWorkingDirectory(File)`, `run()`, abstract `getExecString()`, and abstract `parseExecResult(BufferedReader)`. Runtime inspection APIs expose environment values, current process, exit code, waiting thread, and timeout state. Static `execCommand` overloads cover common one-shot command execution with optional environment and timeout. Static process registry helpers `destroyAllShellProcesses()` and `getAllShells()` support global cleanup. Constants expose OS booleans, command strings, Hadoop home property/env names, Windows launch lock, `ENV_NAME_REGEX`, `TOKEN_SEPARATOR_REGEX`, deprecated misspelled `WINDOWS_MAX_SHELL_LENGHT`, deprecated nullable `WINUTILS`, and `isSetsidAvailable`.

`ShutdownHookManager` is a final singleton that registers a single JVM shutdown hook and then runs Hadoop-registered hooks in priority order. `addShutdownHook` overloads accept priority and optional timeout, `removeShutdownHook`, `hasShutdownHook`, `isShutdownInProgress`, and `clearShutdownHooks` manage/query the registry. `TIMEOUT_MINIMUM` and `TIME_UNIT_DEFAULT` define timeout policy, and default hook timeout comes from `CommonConfigurationKeysPublic.SERVICE_SHUTDOWN_TIMEOUT`.

`StringInterner` begins at the end of the chunk. The visible `strongIntern(String)` method returns the representative instance for equal strings; later methods continue outside this chunk.

## Control Flow

Credential-provider control flow is provider-path resolution followed by provider-specific CRUD. `CredentialProviderFactory.getProviders(conf)` reads configured URIs, locates factories with a service-loader mechanism, and asks them to create providers. Mutating credential operations are not durable until `flush()` succeeds.

Authorization flow starts with ACL string parsing, then membership checks against explicit users/groups, wildcard ACLs, and special real-user ACL entries for proxied users. Proxy authorization loads prefix-scoped proxy-user rules, then validates both effective user/group authorization and source host/IP authorization before allowing impersonation.

HTTP filter flow is servlet-chain mediation. `RestCsrfPreventionFilter.doFilter` delegates to `handleHttpInteraction`, classifies the user agent, skips configured methods, requires the custom header for browser-originating state-changing requests, and either rejects or continues the chain. `XFrameOptionsFilter.doFilter` sets the configured frame-options header before continuing the chain.

Token flow has a clear separation of public identifier, private password, and service/kind metadata. A `SecretManager` creates a token password from an identifier and secret key; clients serialize or URL-encode `Token` instances; renew/cancel operations are routed by token kind to a `TokenRenewer`. `TokenIdentifier.getTrackingId()` gives a stable correlation key without exposing the password.

Delegation-token manager flow is stateful and time driven. Before service activation, previously persisted keys and tokens are loaded through `addKey` and `addPersistedDelegationToken`. `startThreads()` activates key rolling and expired-token cleanup. New token creation increments sequence state, signs identifiers with the current master key, stores token information, and optionally stores tracking IDs. Renewal verifies the token and renewer, extends renew time within max lifetime, and updates persistent storage. Cancellation removes active and stored token state. Expiry scanning removes expired tokens and calls storage/logging hooks.

HTTP delegation-token flow layers token operations over `AuthenticatedURL`. A connection first prefers an already stored delegation token; otherwise it authenticates with the configured authenticator. Token acquisition and renewal require authentication; cancellation is explicitly unauthenticated by the configured authenticator. `doAs` overloads propagate proxy-user intent to the server endpoint.

Service lifecycle flow is strict. `init` transitions from `NOTINITED` to `INITED` and calls `serviceInit`; `start` transitions from `INITED` to `STARTED` and calls `serviceStart`; `stop` transitions to `STOPPED` and calls `serviceStop` once. Failures are recorded with the state in which they occurred and may trigger stop. Listeners are invoked synchronously in the transition path. `waitForServiceToStop(0)` waits indefinitely.

Composite-service flow applies the same lifecycle to child services and handles partial failures by stopping children that failed during init or start. Launcher flow builds configuration, strips and applies `--conf <file>` arguments, optionally binds command arguments through `LaunchableService.bindArgs`, initializes and starts the service, then either waits for a regular service to stop or calls `execute()` for a launchable service. Return codes and exceptions are normalized through `ExitCodeProvider`, `ExitUtil.ExitException`, and `ServiceLaunchException`.

Utility control flow is mostly wrapper/template based. `ApplicationClassLoader` tests system-class patterns before deciding parent versus application loading. `DurationInfo` starts logging at construction and emits elapsed time on `close()`. `ReflectionUtils.newInstance` creates and configures objects. `Shell` subclasses provide command vector and parse stdout while the base class manages process launch, timeout, environment, working directory, and process registry. `ShutdownHookManager` sorts registered hooks by priority and applies per-hook timeout policy.

## State And Persistence Behavior

Credential providers may be persistent or transient. The API explicitly separates in-memory mutation from durable storage by requiring `flush()`. Providers may also require an external password; `needsPassword()` and the warning/error text are part of the user-facing state surface.

`AccessControlList` persists through Hadoop `Writable` serialization. Its user/group collections are returned as unmodifiable snapshots by contract. ACL state also has a special wildcard all-allowed mode and real-user proxy matching behavior.

Token persistence is split across several layers. `Token` and `TokenIdentifier` are `Writable`, plus `Token` has URL-safe string encoding for transport. Delegation-token identifiers carry owner, renewer, real user, issue/max dates, sequence number, and master key ID in serialized form. `AbstractDelegationTokenSecretManager` maintains in-memory maps for active tokens and keys, but provides protected hooks for edit logs, ZooKeeper, or other durable stores. Recovery APIs must run before activation. Unknown-key persisted tokens are marked expired and later cleaned up.

Service state is in-memory but observable: current state, lifecycle history, start time, blockers, first failure cause, and failure state. `LifecycleEvent` is serializable, but the lifecycle history API returns a snapshot and is not itself a persistence layer. `CompositeService` holds child service references and exposes cloned lists to avoid callers mutating live state.

Launcher configuration state is assembled before service initialization. The package docs state that `--conf <file>` pairs are read from local files, merged in command-line order with later files applied later, and removed from the argument list passed to services. Launchable services may mutate or replace the configuration before `init`.

`Shell` has both per-instance mutable process state and process-wide static state. Per-instance state includes environment, working directory, process, exit code, waiting thread, timeout interval, timeout flag, and parent-environment inheritance. Static state includes OS detection, command constants, winutils discovery, setsid availability, and the global live-shell registry. `ShutdownHookManager` owns a process-wide hook registry and shutdown-in-progress flag. `OperationDuration` stores start and finish timestamps; `DurationInfo` adds logging side effects.

## Dependencies And Integration Points

This chunk depends heavily on Hadoop Common core types: `Configuration`, `UserGroupInformation`, `Credentials`, `Text`, `Writable`, `DelegationKey`, `Metrics2Util.NameValuePair`, `ExitUtil`, and `ExitCodeProvider`. It also integrates with Java platform APIs: servlet filters, `HttpURLConnection`, `URLClassLoader`, JCE `SecretKey`, `DataInput`/`DataOutput`, `Closeable`, `Thread.UncaughtExceptionHandler`, `Process`, `TimeUnit`, `Checksum`, reflection APIs, and SLF4J logging.

Security integration points include credential-provider service loading, proxy-user configuration keys, servlet container filter configuration, SPNEGO/pseudo HTTP authentication, token-renewer plugins, token selectors registered through `TokenInfo`, and delegation-token secret-manager persistence hooks for HA stores such as ZooKeeper.

Service integration points include global state-change listeners, shutdown hooks, command-line service launching, signal/interrupt escalation, `--conf` local file loading, and exception-to-exit-code conversion. Utility integration points include application classpath isolation, shell command execution for platform-specific operations, and JVM shutdown ordering.

## Risks And Compatibility Notes

- `AuthorizationException` intentionally hides stack traces; diagnostics must rely on messages and surrounding logs.
- ACL parsing and proxy-user real-user matching are security sensitive. Regressions can either block legitimate proxy use or allow unintended impersonation.
- `RestCsrfPreventionFilter` security depends on accurate browser detection, ignored-method configuration, and consistent custom-header enforcement.
- `DelegationTokenAuthenticatedURL` is documented as not thread safe; sharing instances across callers can corrupt authentication/delegation-token state.
- Sending delegation tokens in query strings exists for WebHDFS compatibility but increases exposure through URLs, logs, and caches compared with headers.
- Delegation-token manager methods document monitor-protected state. Implementations or subclasses that bypass locking around `currentTokens`, `allKeys`, `currentId`, or sequence state risk duplicate sequence numbers, stale keys, failed renewals, or accepting expired tokens.
- Persistent token recovery must occur before `startThreads()`. Loading persisted tokens after activation can race with key rolling and cleanup.
- `TokenIdentifier.getTrackingId()` is documented as MD5 of identifier bytes; it is for correlation, not cryptographic proof.
- Service listeners run synchronously during state transitions. Slow listeners or callbacks into the same service can delay startup/shutdown or deadlock.
- `Service.stop()` must tolerate partially initialized state. Many lifecycle failures route through stop, so null-sensitive cleanup code can mask the original failure.
- Launcher exit-code conversion gives priority to exceptions over normal return codes. Tests should cover both `ExitException` and generic exception paths.
- `Shell.WINUTILS` is deprecated because it may be null; callers should use exception-raising getters. Windows command length and process launch locking remain platform-sensitive.
- Deprecated APIs in this chunk include the `ServiceOperations.stopQuietly(org.apache.commons.logging.Log, Service)` overload, `ReflectionUtils.logThreadInfo` with commons logging, `Shell.isJava7OrAbove`, the misspelled `WINDOWS_MAX_SHELL_LENGHT`, and nullable `Shell.WINUTILS`.

## Test Signals

Relevant tests should assert API behavior rather than XML shape:

- Credential provider tests should cover provider-path resolution, transient versus persistent providers, password-required warnings/errors, create/delete/list/get behavior, duplicate alias rejection, and durability only after `flush()`.
- ACL and impersonation tests should cover wildcard ACLs, separate and combined user/group ACL parsing, Writable round trips, proxied real-user entries with `USE_REAL_ACLS`, host/IP constraints, and negative authorization cases.
- HTTP filter tests should cover browser versus non-browser user agents, ignored HTTP methods, missing/valid custom CSRF headers, custom filter parameters, and `X-Frame-Options` header injection.
- Token tests should cover Writable and URL-string round trips, kind/service mutation, private clone semantics, token selector lookup, renewer dispatch, unmanaged `TrivialRenewer` behavior, and missing token class decode behavior.
- Delegation-token secret-manager tests should cover key rolling, token issue/renew/cancel, expired-token cleanup, persisted key/token recovery before activation, unknown-key recovery cleanup, token owner metrics, tracking ID storage, and concurrent access around monitor-protected maps.
- Delegation-token HTTP tests should cover default Kerberos authenticator selection, pseudo fallback, header versus query-string token transmission, `doAs` propagation, credential token selection by URL, and unauthenticated cancel semantics.
- Service lifecycle tests should cover valid and invalid state transitions, idempotent stop, failure cause/state recording, listener registration/unregistration, listener deadlock avoidance by design, lifecycle history snapshots, blockers, `waitForServiceToStop`, `CompositeService` child ordering, and cleanup after child init/start failure.
- Launcher tests should cover `--conf` local file loading and stripping, `bindArgs` replacing configuration, `execute()` return-code propagation, exception-to-exit-code conversion, signal/shutdown hook behavior, and uncaught `Error` handling.
- Utility tests should cover classloader system-class inclusion/exclusion patterns, duration value before and after `finished()`, CRC known vectors, reflection configuration injection and inherited member discovery, shell command timeout/exit-code/environment behavior, Windows-specific winutils failures, shutdown-hook priority/timeout ordering, and string interning identity.

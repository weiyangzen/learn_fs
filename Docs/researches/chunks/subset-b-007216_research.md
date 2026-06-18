# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.4.xml lines 30893-37013

## Scope

This chunk is a JDiff public API slice for Hadoop Common 3.3.4. It begins in the tail of `org.apache.hadoop.net.AbstractDNSToSwitchMapping` and ends in the middle of `org.apache.hadoop.util.Shell.getQualifiedBinPath`; the complete `Shell` class continues in the next chunk. Because this is generated JDiff XML, the source exposes API signatures, inheritance, visibility, deprecation state, exceptions, fields, and embedded Javadoc, but not implementation bodies.

The covered APIs are grouped around Hadoop's shared runtime infrastructure: network/rack resolution, security identity and token handling, HTTP security filters, service lifecycle management, service launcher exits, and low-level utility classes.

## Network Topology And Socket APIs

Lines 30893-31412 cover `org.apache.hadoop.net` APIs:

- `AbstractDNSToSwitchMapping` tail exposes `setConf(Configuration)`, `isSingleSwitch()`, `getSwitchMap()`, `dumpTopology()`, protected `isSingleSwitchByScriptPolicy()`, and static `isMappingSingleSwitch(DNSToSwitchMapping)`. The class is documented as a preferred base for pluggable DNS-to-switch mappings and deliberately does not extend `Configured` because superclass construction would call subclass `setConf()` too early.
- `CachedDNSToSwitchMapping` wraps a protected final `DNSToSwitchMapping rawMapping`, implements `resolve(List)`, exposes a diagnostic copy of host-to-rack cache via `getSwitchMap()`, delegates `isSingleSwitch()` to `AbstractDNSToSwitchMapping.isMappingSingleSwitch`, and supports `reloadCachedMappings()` for all or selected names.
- `DNSToSwitchMapping` is the core interface: `resolve(List)` must return a same-sized list of network paths, and cache reload methods either clear all mappings or specific nodes. The Javadoc says unresolved names should conventionally map to `NetworkTopology.DEFAULT_RACK`.
- `ScriptBasedMapping` extends `CachedDNSToSwitchMapping`, with constructors for default config, raw mapping, or `Configuration`. Its configuration is driven by `CommonConfigurationKeys.NET_TOPOLOGY_SCRIPT_FILE_NAME_KEY`; the outer class caches results while an inner raw script mapping executes configured scripts.
- `TableMapping` also extends `CachedDNSToSwitchMapping` and offers `getConf()`, `setConf(Configuration)`, and `reloadCachedMappings()`, indicating a config-driven static mapping source.
- `SocksSocketFactory` and `StandardSocketFactory` both extend `javax.net.SocketFactory` and expose the usual five `createSocket` overloads. `SocksSocketFactory` is also `Configurable`, supports a `Proxy` constructor, and defines `equals`/`hashCode`; `StandardSocketFactory` is the direct socket implementation.
- `ConnectTimeoutException` extends `SocketTimeoutException` and is thrown by `NetUtils.connect(...)` when a socket connect times out.

Control flow is mostly contract based: callers resolve host names through a `DNSToSwitchMapping`, often a cached wrapper, then Hadoop placement/topology logic can query whether the mapping is single-switch. Socket factories are reflection-friendly via default constructors and integrate with Hadoop configuration where proxies are needed.

State is in-memory: cached DNS-to-rack entries, table/script configuration, and proxy configuration. The key risk is stale topology data unless reload APIs are invoked after script/table changes. Another risk is return-list cardinality from `resolve(List)`: consumers expect one returned path per input name.

## Core Security APIs

Lines 31417-32931 cover `org.apache.hadoop.security`:

- `AccessControlException` is the base `IOException` for access-denied failures with default, message, and cause constructors.
- `Credentials` is `Writable` storage for delegation tokens and secret keys. It supports token CRUD by `Text` alias, unmodifiable token/secret maps, token count and secret count, static `readTokenStorageFile(Path|File, Configuration)`, stream/file writers with optional `Credentials.SerializedFormat`, `write(DataOutput)`, `readFields(DataInput)`, and merge/copy helpers. `addAll()` overwrites existing entries; `mergeAll()` preserves existing entries.
- `GroupMappingServiceProvider` defines user-to-groups lookup plus cache refresh and cache injection. `IdMappingServiceProvider` maps users/groups to UID/GID and supports "allowing unknown" variants.
- `KerberosAuthException` captures unrecoverable Kerberos login/logout or invalid-subject failures. It carries optional user, principal, keytab, ticket-cache, and initial-message fields, and customizes `getMessage()`.
- `SecurityUtil` is a final static utility class. It configures security state, checks original TGTs, expands server principals with host substitution, logs in from keytab/principal config, builds delegation-token service names from URIs or socket addresses, looks up `KerberosInfo`/client principal/`TokenInfo` through security providers, manipulates token service fields, runs privileged actions as login/current user, reads authentication method from configuration, checks privileged ports, and parses ZK auth info.
- `UserGroupInformation` is the central identity abstraction. It has static initialization/configuration and metrics hooks, security-enabled checks, current/login-user lookup, ticket-cache and subject construction, keytab login/logout/relogin flows, ticket-cache relogin, remote/proxy/testing user factories, user and group accessors, token and token-identifier attachment, credentials aggregation, authentication method getters/setters, equality/hash, subject exposure, `doAs` privileged execution, logging, and a `main` helper. Public fields identify token-file environment/property names: `HADOOP_TOKEN_FILE_LOCATION` and `HADOOP_TOKEN`.
- `UserGroupInformation.AuthenticationMethod` is an enum bridge to `SaslRpcServer.AuthMethod`, with `values()`, string `valueOf`, `getAuthMethod()`, and reverse `valueOf(AuthMethod)`.

The security flow is centered on UGI: configuration selects simple or Kerberos authentication, login material may come from local user, keytab, ticket cache, or subject, and downstream code executes via `doAs`. `SecurityUtil` adapts protocol metadata, principals, and delegation-token service strings for RPC and filesystem clients. `Credentials` is the persistence container used to carry tokens and secret material across process and job boundaries.

Persistence behavior is explicit in `Credentials`: token/secret state can be serialized through Hadoop `Writable` streams or token storage files in a chosen serialized format. UGI itself exposes process/static login state and subject-held credentials, not durable storage. Kerberos and token validity depend on external KDC/token secret-manager state.

Risks include leakage of credential maps or byte arrays, confusion between `addAll()` overwrite and `mergeAll()` non-overwrite semantics, stale group/ID caches, principal substitution against unexpected hostnames, and relogin code paths that must avoid retrying unrecoverable `KerberosAuthException`s.

## Credential Provider APIs

Lines 32934-33102 cover `org.apache.hadoop.security.alias`:

- `CredentialProvider` is an abstract, thread-safe credential/password store. It defines `flush()` for durable writes, alias lookup/list/create/delete, `needsPassword()`, warning/error text for missing provider passwords, and `CLEAR_TEXT_FALLBACK`.
- `CredentialProviderFactory` creates providers from URI names and resolves the configured provider list from `CREDENTIAL_PROVIDER_PATH` using service-loader style discovery.

The control flow is configuration-driven: callers ask the factory for providers, then call provider CRUD methods and `flush()` to persist changes. The main integration points are Hadoop `Configuration`, provider URI schemes, and implementations discovered through Java service loading. Risks are missing provider passwords, fallback to clear text when enabled, and implementations that violate the documented thread-safety expectation.

## Authorization And HTTP Filters

Lines 33107-33674 cover authorization and servlet filters:

- `AccessControlList` is a `Writable` ACL value with constructors from combined ACL string or separate users/groups. It supports wildcard ACLs, mutable add/remove methods, immutable user/group views, `isUserInList(UserGroupInformation)`, `isUserAllowed(UserGroupInformation)`, a parseable `getAclString()`, and `write/readFields`. `USE_REAL_ACLS` enables real-user ACL handling for proxied users.
- `AuthorizationException` extends `AccessControlException`, but intentionally suppresses stack trace exposure for security-sensitive authorization failures.
- `DefaultImpersonationProvider` implements `ImpersonationProvider`, is configurable, initializes from a configuration prefix, authorizes proxy users by effective user and remote `InetAddress`, provides config-key builders for proxy users/groups/IPs, and exposes proxy group/host maps.
- `ImpersonationProvider` extends `Configurable`, defines `init(prefix)`, keeps a string-address `authorize` convenience method, and prefers the `InetAddress` overload to avoid redundant DNS resolution.
- `RestCsrfPreventionFilter` is a servlet `Filter` that requires a configurable custom header for browser-originated REST calls. It exposes browser-agent detection, a testable `handleHttpInteraction(...)` path, servlet `doFilter`, and a static `getFilterParams(Configuration, prefix)` helper. Public constants define user-agent, browser-regex, custom-header, ignored-method, and default-header parameter names.
- `XFrameOptionsFilter` is a servlet `Filter` that adds clickjacking protection through an X-Frame-Options-style header. It has `init`, `doFilter`, `destroy`, `getFilterParams`, and constants for `X_FRAME_OPTIONS` and custom header parameter naming.

The authorization flow combines identity from UGI, ACL membership, proxy-user configuration, and remote client address. The HTTP filters are initialized from prefixed `Configuration` values converted to servlet init parameters, then enforce request headers during `doFilter`.

State persists only when ACLs are serialized as `Writable`s or when proxy/filter settings live in configuration. Runtime maps in impersonation providers and filter params are derived state. Test signals should include wildcard ACL parsing, real-user proxy ACL behavior, stack-trace suppression in `AuthorizationException`, browser/non-browser CSRF branches, ignored HTTP methods, custom header names, and X-Frame-Options header emission.

## Token And Delegation Token APIs

Lines 33681-34844 cover `org.apache.hadoop.security.token` and `org.apache.hadoop.security.token.delegation.web`:

- `SecretManager<T extends TokenIdentifier>` is the token-password authority. Subclasses implement `createPassword(T)`, `retrievePassword(T)`, and `createIdentifier()`. The base API adds `retriableRetrievePassword(...)` for standby/retriable server states, `checkAvailableForRead()`, secret-key generation, HMAC password creation from identifier bytes plus `SecretKey`, and secret-key reconstruction.
- `Token<T extends TokenIdentifier>` is `Writable` token state with constructors from identifier/secret manager, raw byte arrays, empty, and copy. It exposes ID/password setters, identifier/password/kind/service getters, private clone support, read/write serialization, URL-safe encode/decode, equality/hash/string/cache-key helpers, and lifecycle methods `isManaged()`, `renew(Configuration)`, and `cancel(Configuration)`.
- `Token.TrivialRenewer` is a `TokenRenewer` implementation for unmanaged/simple token kinds.
- `TokenIdentifier` is `Writable`, with `getKind()`, `getUser()`, serialized bytes, and optional tracking ID.
- `TokenInfo` is an annotation type for binding protocols to token selectors.
- `TokenRenewer` is the service-provider API for token kind handling, managed-state checks, renewal, and cancellation.
- `TokenSelector<T extends TokenIdentifier>` selects a token by service from a collection.
- `DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` with delegation-token operations. It has constructors taking authenticators/configurators, static default authenticator configuration, query-string behavior toggles, `openConnection` overloads, token get/renew/cancel operations with optional doAs user, and a nested `Token` that holds a Hadoop delegation token alongside the HTTP auth token.
- `DelegationTokenAuthenticator` wraps an `Authenticator` and adds delegation-token REST operations. It has constants for operation, delegation header/parameter names, token/renewer/service params, and JSON fields. `KerberosDelegationTokenAuthenticator` supports SPNEGO with fallback to pseudo auth; `PseudoDelegationTokenAuthenticator` models simple auth through current UGI/query user.

Token control flow starts with an identifier and secret manager producing a password, persists token bytes through `Writable` or URL encoding, and uses `TokenRenewer` implementations for managed renew/cancel. HTTP delegation-token flow authenticates with an `AuthenticatedURL.Token`, calls remote endpoints for get/renew/cancel, and stores the resulting Hadoop token in the nested URL token holder.

Persistent state includes token identifier/password/kind/service bytes, URL-encoded token strings, and credential stores that carry tokens. Secret-manager key material and token validity are server-side authority state. Risks include using `TrivialRenewer` for managed tokens, relying on client-side token fields without server validation, failing to handle standby/retriable exceptions, placing delegation tokens in query strings when headers are safer, and inconsistent service text construction across RPC and web clients.

## Service Lifecycle And Launcher APIs

Lines 34847-36232 cover `org.apache.hadoop.service` and `org.apache.hadoop.service.launcher`:

- `AbstractService` implements `Service` and provides the lifecycle template: `init(Configuration)` invokes `serviceInit`, `start()` invokes `serviceStart`, `stop()` invokes `serviceStop`, `close()` relays to `stop()`, and `noteFailure(Exception)` records failure cause/state. It also tracks service name, config, start time, lifecycle history, blockers, local listeners, and global listeners.
- `CompositeService` extends `AbstractService` to own child services. It adds protected `addService`, `addIfService`, `removeService`, cloned `getServices()`, and overrides service init/start/stop to cascade lifecycle operations. `STOP_ONLY_STARTED_SERVICES` documents shutdown policy.
- `LifecycleEvent` is serializable event state with public `time` and `state`.
- `LoggingStateChangeListener` logs service state changes.
- `Service` extends `Closeable` and defines the service state machine contract: `init`, `start`, `stop`, `close`, listener registration, name/config/state/start-time/failure/history/blocker accessors, `isInState`, and `waitForServiceToStop`. The Javadoc is strict that failed init/start should invoke stop and enter `STOPPED`; stop must be robust even for partially initialized internals.
- `ServiceOperations` supplies static `stop` and several `stopQuietly` overloads for safe service cleanup.
- `ServiceStateChangeListener` is the callback interface.
- `ServiceStateException` is a runtime exception with `ExitCodeProvider` support and conversion helpers.
- `ServiceStateModel` is the explicit state-transition engine with current-state access, `ensureCurrentState`, `enterState`, transition validation, and `isValidStateTransition`.
- `AbstractLaunchableService` extends `AbstractService` and implements `LaunchableService` with default `bindArgs` and `execute` behavior.
- `HadoopUncaughtExceptionHandler` is intended for process entry points; it exits for `Error`s and logs ordinary exceptions, with optional delegation for simple cases.
- `LaunchableService` extends `Service` and adds `bindArgs(Configuration, List)` before init and `execute()` after start. Its exception policy maps `ExitException`, `ExitCodeProvider`, and generic exceptions into process exit behavior.
- `LauncherExitCodes` defines common process exit constants, deliberately mapped near HTTP-like categories.
- `ServiceLaunchException` extends `ExitUtil.ExitException`, implements `ExitCodeProvider` and `LauncherExitCodes`, and supports formatted messages with explicit exit codes and causes.

The lifecycle flow is a template method pattern plus state model: configure, initialize, start, execute if launchable, then stop/close. Failure is recorded and converted into lifecycle or launcher exceptions with exit codes. Composite services apply this flow recursively to child services.

State is in-memory lifecycle metadata: current state, start time, failure cause/state, history, blockers, listeners, and child-service lists. `LifecycleEvent` is serializable but the service framework itself is not a persistence layer. Risks include invalid state transitions, non-idempotent stop logic, failing to stop after partial init/start failure, listener side effects during state changes, and child services that cannot tolerate stop unless fully started.

## Utility APIs

Lines 36241-37013 cover the beginning of `org.apache.hadoop.util`:

- `ApplicationClassLoader` extends `URLClassLoader` for application isolation. It supports URL-array and classpath-string constructors, child-first `getResource`/`loadClass` behavior except for system classes, static `isSystemClass(name, patterns)`, and `SYSTEM_CLASSES_DEFAULT` for JDK, Hadoop, resource, and selected third-party exclusions.
- `DurationInfo` extends `OperationDuration` and implements `AutoCloseable`; constructors format/log a duration message at info or debug, and `close()` logs the final state for try-with-resources usage.
- `IPList` defines a single membership check for IP address strings.
- `OperationDuration` tracks start and finish times, exposes `finished()`, printable duration, static `humanTime(long)`, raw millisecond value, and `java.time.Duration` conversion.
- `Progressable` is the callback for long operations to report progress to Hadoop frameworks.
- `PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum`, with `getValue`, `reset`, byte-array `update`, and int `update`. The first matches the standard CRC32 polynomial and avoids JNI overhead for small repeated checksum operations; the second uses CRC32-C/iSCSI polynomial.
- `ReflectionUtils` provides configuration injection, reflective construction with configuration, contention tracing toggle, synchronized thread-info printing, commons-logging and slf4j thread-stack logging with minimum interval, typed class lookup, `Writable` copy/clone using serialization, and inherited declared field/method enumeration.
- `Shell` begins here as an abstract base for platform command execution. The covered part includes constructors with optional minimum interval and stderr redirection, deprecated `isJava7OrAbove()` which always returns true, Java major-version checks, Windows command-line length validation, platform-specific group/user/netgroup/permission/owner/symlink/readlink/process/signal command builders, environment-variable regex generation, script-extension helpers, run-script command generation, Hadoop home lookup, and qualified Hadoop bin lookup/path methods. The XML chunk stops inside the Javadoc for `getQualifiedBinPath`.

Control flow is utility specific: class loading decides parent/system versus application lookup, duration classes record and later finish/log elapsed time, CRC implementations mutate internal checksum state across updates, reflection helpers create/configure objects and copy `Writable`s through serialization, and `Shell` builds platform-specific command arrays before execution in later methods outside this chunk.

State is local and mutable for timers, checksum accumulators, shell interval/output settings, and loaded classpath URLs. Risks include classloader isolation mistakes from incorrect system-class patterns, checksum offset/length bounds, thread-dump throttling correctness, reflection constructor/configuration failures, platform-specific command quoting and Windows length limits, and expensive qualified-bin existence checks that Javadoc says callers should cache.

## Dependencies And Integration Points

Major dependencies visible in this API slice include Hadoop `Configuration`, `Writable`, `Text`, `Path`, RPC/security annotations, servlet `Filter` APIs, Java JAAS/Kerberos classes, Java networking/socket APIs, Java crypto `SecretKey`, logging through slf4j and commons-logging, and Java classloading/reflection/serialization primitives.

The integration surface is broad:

- HDFS/YARN block placement and topology code consume `DNSToSwitchMapping` and rack paths.
- RPC, filesystem, and HTTP clients consume `SecurityUtil`, `UserGroupInformation`, `Credentials`, `Token`, and delegation-token URL helpers.
- Daemons and launchers use `Service`, `AbstractService`, `CompositeService`, `LaunchableService`, and launcher exit codes.
- Web UIs and REST endpoints use CSRF and X-Frame filters.
- Configuration and service-provider discovery connect credential providers, token renewers/selectors, security-info providers, socket factories, and classloader policies.

## Test Signals

Useful tests for this chunk should validate API contracts rather than implementation internals:

- DNS mapping returns same-sized result lists, caches and reloads correctly, dumps topology diagnostics, and respects single-switch policy.
- Script/table mappings re-read configuration and handle missing or failing mapping inputs without corrupting cached state.
- Socket factories create equivalent sockets and proxy-backed sockets, and `ConnectTimeoutException` is surfaced from timeout paths.
- `Credentials` read/write round trips tokens and secrets across stream/file formats; `addAll` overwrites while `mergeAll` preserves.
- UGI covers simple, keytab, ticket-cache, subject, remote, proxy, and testing users; relogin and `doAs` behavior should propagate exceptions and authentication methods correctly.
- ACL and impersonation tests cover wildcard, user/group, real-user proxy, host/IP matching, and stack-trace suppression for authorization failures.
- Servlet filter tests cover browser detection, custom CSRF headers, ignored methods, missing headers, and X-Frame header configuration.
- Token tests cover `Writable` and URL encode/decode round trips, service/kind matching, private clones, renew/cancel delegation, and retriable/standby secret-manager exceptions.
- Service tests cover all valid and invalid state transitions, failure recording, listener notification, blocker maps, wait-for-stop, composite child ordering, and launch exception exit-code mapping.
- Utility tests cover application classloader positive/negative system patterns, duration finalization, CRC32/CRC32C known vectors, `ReflectionUtils.copy` for `Writable`s, thread-info throttling, and `Shell` command construction across Unix/Windows branches.

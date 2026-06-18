# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.6.xml lines 31094-37159

## Scope

This chunk is a large portion of the Hadoop Common 3.3.6 JDiff public API XML. It starts inside `org.apache.hadoop.metrics2.lib.MetricsRegistry`, covers mutable metrics, metrics sinks and utilities, network mapping/socket APIs, security identity and token APIs, HTTP security filters, delegation-token web clients, and service lifecycle classes. It ends inside the `org.apache.hadoop.service.Service.waitForServiceToStop(long)` documentation; `Service.getLifecycleHistory()`, `Service.getBlockers()`, and following `ServiceOperations` APIs are outside this chunk.

Because the source is JDiff XML rather than executable Java, the research below focuses on exposed API contracts, state surfaces implied by public fields/methods, control-flow contracts documented in Javadocs, integration points, compatibility risks, and likely test signals.

## Purpose

The chunk captures public contracts for several Hadoop Common cross-cutting subsystems:

- Metrics production and export: mutable counters, gauges, rates, quantiles, rolling averages, metric registries, JMX MBean helpers, cache utilities, and sinks for files, rolling filesystems, Graphite, and StatsD.
- Network topology and sockets: DNS-to-rack/switch mappings, cache wrappers, script/table based mapping, and standard/SOCKS socket factories.
- Security primitives: credentials, user/group identity, Kerberos helpers, ACLs, impersonation providers, credential providers, token identifiers, token renewal, and delegation-token HTTP clients.
- HTTP hardening filters: REST CSRF prevention and X-Frame-Options insertion for servlet filters.
- Service lifecycle management: abstract service state transitions, composite child service coordination, lifecycle events, state-change logging, and the core `Service` interface up to stop-waiting semantics.

The common theme is public framework API. These types are intended to be used by HDFS, YARN, MapReduce, command-line tools, RPC clients/servers, web services, and pluggable Hadoop deployments rather than by a single feature.

## Important APIs, Types, And Functions

### Metrics Registry And Mutable Metrics

The chunk begins with the tail of `MetricsRegistry`, whose methods create and manage mutable metrics and tags:

- `newRate(name)`, `newRate(name, description)`, and `newRate(name, desc, extended)` create `MutableRate` metrics; the extended flag requests additional statistics such as min/max/stdev.
- `newRatesWithAggregation(name)` and `newMutableRollingAverages(name, valueName)` create aggregate rate/rolling-average helpers.
- `add(name, value)` adds a sample to a stat metric by metric name.
- `setContext(name)` writes the metrics context tag and returns the registry for chaining.
- `tag(...)` overloads add string tags by name/description/value or by `MetricsInfo`, with optional override behavior.
- `snapshot(MetricsRecordBuilder, boolean all)` emits all contained mutable metrics to a record builder, optionally including unchanged values.

The mutable metric family is centered on `MutableMetric`, an abstract base with `snapshot(builder, all)`, convenience `snapshot(builder)`, protected `setChanged()`/`clearChanged()`, and `changed()`. This establishes the common changed-since-last-snapshot contract.

Counter and gauge APIs split by monotonic-vs-arbitrary and int-vs-long storage:

- `MutableCounter` is abstract, stores `MetricsInfo`, and requires `incr()`.
- `MutableCounterInt` and `MutableCounterLong` provide `incr()`, delta overloads, `value()`, and `snapshot(...)`. `MutableCounterLong` has a public `(MetricsInfo, long)` constructor.
- `MutableGauge` is abstract, stores `MetricsInfo`, and requires `incr()` plus `decr()`.
- `MutableGaugeInt` and `MutableGaugeLong` provide `value()`, increment/decrement delta overloads, `set(value)`, `snapshot(...)`, and `toString()`.

Statistical metrics include:

- `MutableStat`, constructed from metric name/description/sample name/value name and optional extended flag. It supports `setExtended(boolean)`, `setUpdateTimeStamp(boolean)`, sample addition through `add(numSamples, sum)` and `add(value)`, `snapshot(...)`, `lastStat()`, `resetMinMax()`, `getSnapshotTimeStamp()`, and `toString()`.
- `MutableRate extends MutableStat` and exposes the rate-metric specialization.
- `MutableQuantiles`, constructed with name/description/sample name/value name/interval, supports `add(long)`, `snapshot(...)`, `getInterval()`, `stop()`, `getEstimator()`, and `setEstimator(...)`. It publishes protected `quantiles` and `previousSnapshot` fields.
- `MutableRates` and `MutableRatesWithAggregation` dynamically manage rate metrics by operation or method name. Their `init(...)`, `add(name, elapsed)`, and `snapshot(...)` APIs support reflective initialization and aggregation.
- `MutableRollingAverages implements Closeable`; it supports `add(name, value)`, `snapshot(...)`, `collectThreadLocalStates()`, `getStats(long minSamples)`, `setRecordValidityMs(long)`, and `close()`.

### Metrics Sinks And Utilities

The sink classes implement `MetricsSink` and generally `Closeable`:

- `FileSink` initializes from `SubsetConfiguration`, writes metrics records with `putMetrics(MetricsRecord)`, supports `flush()`, and closes resources.
- `GraphiteSink` has the same sink lifecycle and writes records to a Graphite endpoint.
- `StatsDSink` initializes, writes records, has a protected/public `writeMetric(String, String, String, String)` style helper in the API, flushes, and closes.
- `RollingFileSystemSink` writes metrics to rolling files under a Hadoop `Path`. It exposes default and `(long, long)` constructors, `init(...)`, `getRollInterval()`, `updateFlushTime(Calendar)`, `setInitialFlushTime(Date)`, `putMetrics(...)`, `flush()`, and `close()`.

`RollingFileSystemSink` has a broad state surface in protected/public fields: `source`, `ignoreError`, `allowAppend`, `basePath`, `rollIntervalMillis`, `rollOffsetIntervalMillis`, `nextFlush`, `forceFlush`, `hasFlushed`, `suppliedConf`, and `suppliedFilesystem`. That makes subclass or test behavior sensitive to field naming and type compatibility.

Metrics utility APIs include:

- `MBeans.register(serviceName, nameName, mbean)` and an overload with an additional `Map<String,String>` of properties; `getMbeanNameService(ObjectName)`, `getMbeanNameName(ObjectName)`, and `unregister(ObjectName)`.
- `MetricsCache`, with default and size-limited constructors, `update(MetricsRecord, boolean includingTags)`, `update(MetricsRecord)`, and `get(String name, Collection<MetricsTag> tags)`. It exposes cached `Record` objects through API signatures.
- `Servers.parse(String specs, int defaultPort)` returns a list of server socket addresses from a comma-delimited host/port-like spec.

### Network Mapping And Socket APIs

`DNSToSwitchMapping` is the rack/switch resolution interface. It defines `resolve(List<String> names)`, `reloadCachedMappings()`, and `reloadCachedMappings(List<String> names)`.

`AbstractDNSToSwitchMapping implements DNSToSwitchMapping, Configurable` and adds configuration handling plus topology inspection helpers:

- constructors with no args or `Configuration`;
- `getConf()` / `setConf(Configuration)`;
- `isSingleSwitch()`;
- `getSwitchMap()`;
- `dumpTopology()`;
- static/utility style policy helpers `isSingleSwitchByScriptPolicy()` and `isMappingSingleSwitch(DNSToSwitchMapping)`.

Concrete wrappers and implementations:

- `CachedDNSToSwitchMapping` wraps a raw `DNSToSwitchMapping`, caches name-to-switch results, supports cache reloads for all or selected names, exposes `getSwitchMap()`, `isSingleSwitch()`, `toString()`, and a protected `rawMapping` field.
- `ScriptBasedMapping` extends the cached wrapper, provides constructors from no args, raw mapping, or configuration, exposes `NO_SCRIPT`, and updates the underlying script mapping through `setConf`.
- `TableMapping` extends the cached wrapper and is configuration-driven; `reloadCachedMappings()` refreshes table-derived mappings.
- `ConnectTimeoutException extends SocketTimeoutException` gives Hadoop a named connect-timeout exception type.

Socket factories:

- `SocksSocketFactory extends SocketFactory implements Configurable` supports creation from no args or a `Proxy`, all five `SocketFactory.createSocket(...)` overloads, equality/hash code, and configuration handling. Its configuration determines the SOCKS proxy.
- `StandardSocketFactory extends SocketFactory` exposes the same five `createSocket(...)` overloads plus equality/hash code for ordinary sockets.

### Credentials, Group/ID Mapping, And Kerberos Helpers

`AccessControlException extends IOException` provides empty, message, and throwable constructors for authorization/access failures.

`Credentials implements Writable` stores token aliases and secret keys in memory and serializes them:

- construction from empty state or copy;
- token access through `getToken(Text)`, `addToken(Text, Token)`, `getAllTokens()`, `getTokenMap()`, and `numberOfTokens()`;
- secret-key access through `getSecretKey(Text)`, `numberOfSecretKeys()`, `addSecretKey(Text, byte[])`, `removeSecretKey(Text)`, `getAllSecretKeys()`, and `getSecretKeyMap()`;
- token-storage IO through `readTokenStorageFile(Path, Configuration)`, `readTokenStorageFile(File, Configuration)`, `readTokenStorageStream(DataInputStream)`, `writeTokenStorageToStream(DataOutputStream)`, `writeTokenStorageToStream(DataOutputStream, SerializedFormat)`, `writeTokenStorageFile(Path, Configuration)`, and `writeTokenStorageFile(Path, Configuration, SerializedFormat)`;
- `write(DataOutput)`, `readFields(DataInput)`, `addAll(Credentials)`, and `mergeAll(Credentials)`.

`GroupMappingServiceProvider` defines pluggable group lookup with `getGroups(String user)`, `cacheGroupsRefresh()`, `cacheGroupsAdd(List<String>)`, and `GROUP_MAPPING_CONFIG_PREFIX`.

`IdMappingServiceProvider` defines user/group ID mapping: `getUid(user)`, `getGid(group)`, `getUserName(uid, unknown)`, `getGroupName(gid, unknown)`, `getUidAllowingUnknown(user)`, and `getGidAllowingUnknown(group)`.

`KerberosAuthException extends IOException` enriches authentication failures with optional user, principal, keytab, ticket cache, and initial message. It has setters, getters, and an overridden `getMessage()` to include context.

`SecurityUtil` is a static helper surface for Kerberos, token service names, privileged execution, protocol annotations, and ZooKeeper auth:

- global setup: `setConfiguration(Configuration)`;
- Kerberos principal helpers: `isOriginalTGT(KerberosTicket)`, `getServerPrincipal(String, String)`, `getServerPrincipal(String, InetAddress)`, and `getHostFromPrincipal(String)`;
- login helpers: `login(Configuration, keytabKey, userNameKey)` and overload with explicit hostname;
- delegation-token service helpers: `buildDTServiceName(URI, int)`, `getTokenServiceAddr(Token)`, `setTokenService(Token, InetSocketAddress)`, and `buildTokenService(...)` overloads for address and URI;
- protocol metadata: `getKerberosInfo(Class, Configuration)`, `getClientPrincipal(Class, Configuration)`, and `getTokenInfo(Class, Configuration)`;
- privileged execution: `doAsLoginUserOrFatal(PrivilegedAction<T>)`, `doAsLoginUser(PrivilegedExceptionAction<T>)`, and `doAsCurrentUser(PrivilegedExceptionAction<T>)`;
- auth-method config: `getAuthenticationMethod(Configuration)`, `setAuthenticationMethod(AuthenticationMethod, Configuration)`;
- utility checks: `isPrivilegedPort(int)` and `getZKAuthInfos(Configuration, String)`;
- fields include `LOG`, `HOSTNAME_PATTERN`, and `FAILED_TO_GET_UGI_MSG_HEADER`.

### UserGroupInformation

`UserGroupInformation` is the public identity and subject wrapper for Hadoop. The XML exposes static process configuration, login state, user creation, token/credential management, group lookup, authentication method state, and privileged execution:

- test and metrics hooks: `setShouldRenewImmediatelyForTests(boolean)` and `reattachMetrics()`;
- global configuration and status: `isInitialized()`, `setConfiguration(Configuration)`, `isSecurityEnabled()`, and `hasKerberosCredentials()`;
- user discovery: `getCurrentUser()`, `getBestUGI(ticketCachePath, user)`, `getUGIFromTicketCache(ticketCache, user)`, `getUGIFromSubject(Subject)`, `getLoginUser()`, and `trimLoginMethod(String)`;
- login lifecycle: `loginUserFromSubject(Subject)`, `isFromKeytab()`, `loginUserFromKeytab(user, path)`, `logoutUserFromKeytab()`, `checkTGTAndReloginFromKeytab()`, `reloginFromKeytab()`, `forceReloginFromKeytab()`, `reloginFromTicketCache()`, `loginUserFromKeytabAndReturnUGI(user, path)`, `isLoginKeytabBased()`, and `isLoginTicketBased()`;
- identity creation: `createRemoteUser(user)`, `createRemoteUser(user, AuthMethod)`, `createProxyUser(user, realUser)`, `createUserForTesting(user, groups)`, and `createProxyUserForTesting(user, realUser, groups)`;
- proxy identity inspection: `getRealUser()` and `getRealUserOrSelf(UserGroupInformation)`;
- names and groups: `getShortUserName()`, `getPrimaryGroupName()`, `getUserName()`, `getGroupNames()`, and `getGroups()`;
- token and credential handling: `addTokenIdentifier(TokenIdentifier)`, `getTokenIdentifiers()`, `addToken(Token)`, `addToken(Text, Token)`, `getTokens()`, `getCredentials()`, and `addCredentials(Credentials)`;
- auth method state: `setAuthenticationMethod(AuthenticationMethod)`, `setAuthenticationMethod(SaslRpcServer.AuthMethod)`, `getAuthenticationMethod()`, `getRealAuthenticationMethod()`, and static `getRealAuthenticationMethod(ugi)`;
- subject behavior: `equals(Object)`, `hashCode()`, `getSubject()`, `doAs(PrivilegedAction<T>)`, `doAs(PrivilegedExceptionAction<T>)`, `logAllUserInfo(ugi)`, and `main(String[])`.

`UserGroupInformation.AuthenticationMethod` is an enum-like nested type with `values()`, `valueOf(String)`, `getAuthMethod()`, and `valueOf(SaslRpcServer.AuthMethod)`. `HADOOP_TOKEN_FILE_LOCATION` and `HADOOP_TOKEN` are public environment variable names for token-file and base64-token ingestion.

### Credential Providers And Authorization

`CredentialProvider` is the abstract credential-store contract. It exposes `isTransient()`, `flush()`, `getCredentialEntry(alias)`, `getAliases()`, `createCredentialEntry(alias, credential)`, `deleteCredentialEntry(alias)`, `needsPassword()`, `noPasswordWarning()`, and `noPasswordError()`. The `CLEAR_TEXT_FALLBACK` field names the clear-text fallback behavior/config key.

`CredentialProviderFactory` constructs providers from a URI-like provider path. It exposes `createProvider(URI, Configuration)`, `getProviders(Configuration)`, and `CREDENTIAL_PROVIDER_PATH`.

`AccessControlList implements Writable` models user/group ACL strings:

- constructors from no args, ACL string, or user/group strings;
- mutation and inspection: `isAllAllowed()`, `addUser()`, `addGroup()`, `removeUser()`, `removeGroup()`, `getUsers()`, `getGroups()`, `isUserInList()`, `isUserAllowed(UserGroupInformation)`, `toString()`, and `getAclString()`;
- serialization: `write(DataOutput)` and `readFields(DataInput)`;
- public constants: `WILDCARD_ACL_VALUE` and `USE_REAL_ACLS`.

`AuthorizationException extends AccessControlException` has constructors matching message/throwable use cases and overrides stack-trace access/printing methods. That API suggests a lightweight or intentionally stackless authorization failure surface.

`ImpersonationProvider extends Configurable` authorizes proxy users through `init(String configurationPrefix)`, `authorize(UserGroupInformation user, InetAddress remoteAddress)`, and an overload accepting a `String` remote address. `DefaultImpersonationProvider` implements it with config-backed proxy group/host maps and helper methods for derived config keys:

- `getTestProvider()`;
- `setConf()` / `getConf()`;
- `init(prefix)`;
- `authorize(...)`;
- `getProxySuperuserUserConfKey(user)`, `getProxySuperuserGroupConfKey(user)`, and `getProxySuperuserIpConfKey(user)`;
- `getProxyGroups()` and `getProxyHosts()`.

### HTTP Security Filters

`RestCsrfPreventionFilter implements javax.servlet.Filter` and exposes:

- servlet lifecycle: `init(FilterConfig)`, `doFilter(ServletRequest, ServletResponse, FilterChain)`, and `destroy()`;
- policy hooks: `isBrowser(String userAgent)` and `handleHttpInteraction(HttpInteraction)`;
- `getFilterParams(Configuration, String prefix)` for extracting filter configuration;
- public field names for headers and parameters: `HEADER_USER_AGENT`, `BROWSER_USER_AGENT_PARAM`, `CUSTOM_HEADER_PARAM`, `CUSTOM_METHODS_TO_IGNORE_PARAM`, and `HEADER_DEFAULT`.

`XFrameOptionsFilter implements Filter` and exposes `init`, `doFilter`, `destroy`, `getFilterParams(Configuration, String prefix)`, and fields `X_FRAME_OPTIONS` plus `CUSTOM_HEADER_PARAM`.

### Tokens And Secret Managers

`SecretManager<T extends TokenIdentifier>` is the server-side token-secret abstraction:

- abstract/overridable token methods: `createPassword(T identifier)`, `retrievePassword(T identifier)`, `retriableRetrievePassword(T identifier)`, `createIdentifier()`, and `checkAvailableForRead()`;
- cryptographic helpers: `generateSecret()`, static-like `createPassword(byte[] identifier, SecretKey key)`, and `createSecretKey(byte[] key)`;
- failure modes include `SecretManager.InvalidToken`, `StandbyException`, `RetriableException`, and `IOException`.

`Token<T extends TokenIdentifier> implements Writable` is the client-side token form:

- constructors from `(identifier, secretManager)`, raw components `(identifier bytes, password bytes, kind, service)`, empty state, or copy;
- mutators/accessors: `setID(byte[])`, `setPassword(byte[])`, `copyToken()`, `getIdentifier()`, `decodeIdentifier()`, `getPassword()`, `getKind()`, `getService()`, and `setService(Text)`;
- privacy/aliasing: `isPrivate()`, `isPrivateCloneOf(Text publicService)`, and `privateClone(Text newService)`;
- serialization and string encoding: `readFields(DataInput)`, `write(DataOutput)`, `encodeToUrlString()`, and `decodeFromUrlString(String)`;
- identity and cache behavior: `equals(Object)`, `hashCode()`, `toString()`, and `buildCacheKey()`;
- lifecycle through renewers: `isManaged()`, `renew(Configuration)`, and `cancel(Configuration)`;
- public `LOG`.

`Token.TrivialRenewer extends TokenRenewer` is for token kinds that are not managed. It exposes `getKind()`, `handleKind(Text)`, `isManaged(Token)`, `renew(Token, Configuration)`, and `cancel(Token, Configuration)`.

`TokenIdentifier implements Writable` is the public identifier contract with `getKind()`, `getUser()`, `getBytes()`, and `getTrackingId()`.

`TokenInfo` is an annotation type marking protocol token metadata. `TokenRenewer` is the plugin interface for token kinds with `handleKind(Text)`, `isManaged(Token)`, `renew(Token, Configuration)`, and `cancel(Token, Configuration)`. `TokenSelector<T extends TokenIdentifier>` selects an appropriate token from a collection by service.

### Delegation-Token Web Client APIs

`DelegationTokenAuthenticatedURL extends AuthenticatedURL` wraps HTTP authentication with delegation-token operations:

- constructors accept defaults, a `DelegationTokenAuthenticator`, a `ConnectionConfigurator`, or both.
- static/default behavior: `setDefaultDelegationTokenAuthenticator(Class)`, `getDefaultDelegationTokenAuthenticator()`, `setUseQueryStringForDelegationToken(boolean)`, and `useQueryStringForDelegationToken()`.
- authenticated connections: `openConnection(URL, AuthenticatedURL.Token)`, `openConnection(URL, DelegationTokenAuthenticatedURL.Token)`, and overload with `doAs`.
- token operations: `getDelegationToken(URL, Token, renewer)`, overload with `doAsUser`, `renewDelegationToken(URL, Token)`, overload with `doAsUser`, `cancelDelegationToken(URL, Token)`, and overload with `doAsUser`.

`DelegationTokenAuthenticatedURL.Token extends AuthenticatedURL.Token` stores an optional Hadoop delegation `Token` via `getDelegationToken()` and `setDelegationToken(Token)`.

`DelegationTokenAuthenticator implements Authenticator` wraps another authenticator and adds REST-style delegation token operations:

- constructor from an underlying `Authenticator`;
- `setConnectionConfigurator(ConnectionConfigurator)`;
- `authenticate(URL, AuthenticatedURL.Token)`;
- `getDelegationToken(...)`, `renewDelegationToken(...)`, and `cancelDelegationToken(...)` overloads with optional `doAsUser`;
- protocol constant fields including `OP_PARAM`, `DELEGATION_TOKEN_HEADER`, `DELEGATION_PARAM`, `TOKEN_PARAM`, `RENEWER_PARAM`, `SERVICE_PARAM`, `DELEGATION_TOKEN_JSON`, `DELEGATION_TOKEN_URL_STRING_JSON`, and `RENEW_DELEGATION_TOKEN_JSON`.

`KerberosDelegationTokenAuthenticator` and `PseudoDelegationTokenAuthenticator` are concrete specializations for Kerberos-backed and pseudo-authenticated web endpoints.

### Service Lifecycle APIs

`AbstractService implements Service` is the base service implementation. It exposes:

- lifecycle state and failure inspection: `getServiceState()`, `getFailureCause()`, `getFailureState()`, `getStartTime()`, `getLifecycleHistory()`, `isInState(STATE)`, and `toString()`;
- mutable config: protected/public `setConfig(Configuration)` and `getConfig()`;
- lifecycle operations: `init(Configuration)`, `start()`, `stop()`, `close()`, and protected hooks `serviceInit(Configuration)`, `serviceStart()`, and `serviceStop()`;
- failure and synchronization: `noteFailure(Exception)` and `waitForServiceToStop(long timeout)`;
- listeners: per-service `registerServiceListener(...)` / `unregisterServiceListener(...)` and static global `registerGlobalListener(...)` / `unregisterGlobalListener(...)`;
- liveness blockers: protected `putBlocker(name, details)`, public `removeBlocker(name)`, and `getBlockers()`.

The hook documentation is explicit: `serviceInit`, `serviceStart`, and `serviceStop` are called once per lifecycle transition, do not need extra synchronization because the base lifecycle methods prevent re-entry, and failures are caught/wrapped to trigger service stop. `serviceStop` implementations must be robust against partially initialized internal fields and continue shutdown work even after one subcomponent fails.

`CompositeService extends AbstractService` manages child `Service` instances:

- `getServices()` returns a cloned snapshot of children;
- protected `addService(Service)`, `addIfService(Object)`, and `removeService(Service)` manage children;
- lifecycle hooks `serviceInit`, `serviceStart`, and `serviceStop` initialize/start/stop children;
- `STOP_ONLY_STARTED_SERVICES` controls whether shutdown tries all children or only those that started, with documentation noting failed init/start children still receive `stop()`.

`LifecycleEvent implements Serializable` publishes mutable/public fields `time` and `state`. `LoggingStateChangeListener implements ServiceStateChangeListener` logs state changes to either a supplied `Logger` or a static class logger through `stateChanged(Service)`.

The chunk includes the start of `Service extends Closeable`. Methods within the assigned line range include `init(Configuration)`, `start()`, `stop()`, `close()`, listener registration/unregistration, `getName()`, `getConfig()`, `getServiceState()`, `getStartTime()`, `isInState(STATE)`, `getFailureCause()`, `getFailureState()`, and `waitForServiceToStop(long)`. The documented lifecycle contract requires `NOTINITED -> INITED -> STARTED -> STOPPED` transitions, invokes `stop()` on init/start failure, makes repeated `stop()` on already stopped services a no-op, and defines `close()` as a direct relay to `stop()`.

## Control Flow

Metrics control flow is producer/snapshot oriented. A metric source updates mutable metrics (`incr`, `decr`, `set`, `add`) and marks them changed through `MutableMetric`; a metrics system calls `snapshot(builder, all)` on registries and metrics to emit values. `all=false` can suppress unchanged values, while `all=true` forces a full record. `MutableStat`, `MutableRate`, `MutableQuantiles`, and rolling-average metrics accumulate samples between snapshots; quantiles and rolling averages introduce periodic rollover/state collection.

Metrics sink control flow follows the `MetricsSink` lifecycle: `init(SubsetConfiguration)`, repeated `putMetrics(MetricsRecord)`, optional `flush()`, and `close()`. `RollingFileSystemSink` adds time-based control flow: records are written until `nextFlush`/roll interval boundaries require file rotation or flushing. `ignoreError` likely controls whether sink write failures are swallowed or surfaced, while `allowAppend` changes file creation behavior.

Network mapping control flow starts with `resolve(names)`. Cache wrappers consult cached name-to-switch entries, delegate misses to `rawMapping`, and expose reload methods to clear all or selected cache entries. Script and table mappings populate the raw mapping from external command/configuration or mapping files; `isSingleSwitch()` allows callers to short-circuit topology-aware behavior when all nodes map to a default/single rack.

Security login control flow is centered on global configuration and JAAS/Kerberos subject state. `SecurityUtil.login(...)` reads configured keytab/principal keys, substitutes host names in principal patterns, and delegates identity setup to UGI. UGI exposes separate flows for login-user discovery, keytab login, ticket-cache login, re-login when TGTs expire, forced re-login, logout, and subject-scoped `doAs` execution. Proxy-user creation binds an effective user to a real user, and impersonation providers later authorize that binding against configured users/groups/hosts.

Credential and token control flow separates persistent credentials from runtime identities. `Credentials` reads token storage from `Path`, `File`, or `DataInputStream`, stores tokens and secret keys by `Text` alias, and writes them back in a selected serialized format. `UserGroupInformation` can ingest `Credentials`, expose them as token collections, or add token identifiers to its underlying `Subject`. `Token` can decode its identifier, serialize as binary Writable data, or encode/decode URL-safe strings for HTTP transport.

Token renewal control flow is plugin-based. A `Token` asks its matching `TokenRenewer` whether the token kind is managed, then renews or cancels via configuration. `SecretManager` is the server-side counterpart: it creates passwords, retrieves existing passwords, checks read availability, and can signal invalid, standby, retriable, or IO failures.

Delegation-token web control flow wraps HTTP authentication. `DelegationTokenAuthenticatedURL.openConnection(...)` authenticates with an `AuthenticatedURL.Token`; when a delegation token is present, it can be sent in a header or query string depending on global setting. `getDelegationToken`, `renewDelegationToken`, and `cancelDelegationToken` call server endpoints using well-known operation/token/renewer/service parameters. `doAs` overloads layer proxy-user semantics onto those HTTP requests.

Service lifecycle control flow is a strict state machine. `Service.init(conf)` moves from `NOTINITED` to `INITED`, `start()` moves to `STARTED`, and `stop()` moves to `STOPPED`; init/start failures must trigger `stop()`. `AbstractService` wraps subclass hooks and listener notifications, records lifecycle history, tracks first failure cause/state, updates start time, and wakes waiters for `waitForServiceToStop(timeout)`. `CompositeService` cascades init/start/stop to child services using snapshots of registered children.

## State And Persistence Behavior

Mutable metrics keep in-memory counters, gauges, sample statistics, changed flags, quantile estimators, previous snapshots, and thread-local or rolling windows. Their persistence is observational rather than durable: values are emitted through `MetricsRecordBuilder` or sinks, not stored by the metric objects beyond process lifetime. `MutableQuantiles.stop()` and `MutableRollingAverages.close()` indicate background schedulers/resources may need explicit cleanup.

Metrics sinks hold runtime IO state. `FileSink`, `GraphiteSink`, and `StatsDSink` hold output destinations and buffers/connections. `RollingFileSystemSink` keeps Hadoop `Configuration`, `FileSystem`, output `Path`, source name, roll intervals, flush calendar, and error/append policy. Its file output is durable state; correctness depends on roll time calculation, append compatibility, and close/flush behavior.

`MetricsCache` is in-memory cache state keyed by record identity and tags. `MBeans` registers process-wide JVM MBean state under `ObjectName`s and must unregister to avoid leaks or duplicate registration errors.

Network mapping caches are in-memory and reloadable. Table/script mappings depend on external configuration, files, and scripts, so their effective topology state can diverge from the cluster until reload methods are called. Socket factories hold configuration/proxy state; equality and hash code matter when factories are cached or compared.

`Credentials` has both in-memory sensitive state and serialized token-storage state. Token aliases map to `Token` objects; secret-key aliases map to raw byte arrays. `getTokenMap()` and `getSecretKeyMap()` return unmodifiable maps, but the values themselves can still be mutable (`Token`, `byte[]`) unless implementation defensively copies. Writable and token-storage methods persist credentials to streams/files.

`UserGroupInformation` has significant process-global state: static configuration, login user, security enabled flag, keytab/ticket-cache login mode, metrics, and test renewal behavior. Per-UGI state is in a JAAS `Subject`, including principals, credentials, tokens, token identifiers, auth method, and real/effective user relationship. UGI group results depend on configured group mapping providers and their caches.

`AccessControlList` persists ACL content through Writable serialization and ACL strings. `DefaultImpersonationProvider` persists only in memory but derives proxy host/group/user rules from configuration prefixes.

`CredentialProvider` implementations may be transient or durable. The abstract API's `flush()` is the durability boundary; callers that create/delete credentials without flushing risk losing changes for persistent providers.

`Token` persists identifier/password/kind/service through Writable and URL-safe encodings. Private-token clone state changes service identity while preserving linkage to the public service. `TokenIdentifier.getTrackingId()` supplies audit correlation without exposing token secrets. `SecretManager` state is implementation-specific and often durable or replicated in concrete managers outside this chunk.

HTTP filters store servlet init parameters and per-request derived policy. They do not persist data but affect response/request authorization behavior across all matching web endpoints.

Service classes keep lifecycle state, configuration, start time, lifecycle history, failure cause/state, listener registries, blocker maps, and wait/termination notification state. `LifecycleEvent` is serializable and carries transition time plus state. `CompositeService` keeps an ordered child-service list; `getServices()` returns a clone to prevent accidental direct mutation.

## Dependencies And Integration Points

Key dependencies surfaced by the API signatures include:

- Hadoop metrics core: `MetricsInfo`, `MetricsRecord`, `MetricsRecordBuilder`, `MetricsSink`, `MetricsTag`, `MutableMetric`, `SampleStat`, `Quantile`, `QuantileEstimator`, and `SubsetConfiguration`.
- Hadoop configuration/filesystem: `Configuration`, `Configurable`, `FileSystem`, `Path`, and configuration keys consumed by metrics, network mapping, security, and service setup.
- Java platform APIs: `Closeable`, `IOException`, `DataInput`, `DataOutput`, `DataInputStream`, `DataOutputStream`, `File`, `URI`, `URL`, `HttpURLConnection`, `InetAddress`, `InetSocketAddress`, `Socket`, `SocketFactory`, `Proxy`, `Calendar`, `Date`, `Map`, `List`, `Collection`, `Set`, `Serializable`, JAAS `Subject`, `PrivilegedAction`, `PrivilegedExceptionAction`, Kerberos tickets, servlet `Filter`, and JMX `ObjectName`.
- Hadoop network topology: `DNSToSwitchMapping` implementations feed rack awareness used by HDFS block placement, YARN scheduling, and other locality decisions.
- Hadoop security/RPC: `KerberosInfo`, `SaslRpcServer.AuthMethod`, `TokenInfo`, `Token`, `TokenIdentifier`, `TokenRenewer`, `UserGroupInformation`, and impersonation authorization are shared by RPC clients, RPC servers, web authentication, filesystem clients, and service daemons.
- Hadoop web authentication client: `AuthenticatedURL`, `AuthenticatedURL.Token`, `Authenticator`, `AuthenticationException`, and `ConnectionConfigurator`.
- Logging and observability: `org.slf4j.Logger`, metrics sinks, JMX registration, and service state-change listeners.

## Risks And Compatibility Concerns

This JDiff snapshot is a compatibility surface. Removing or changing signatures here can break downstream Hadoop integrations, custom metrics sources/sinks, network mapping plugins, credential providers, token renewers/selectors, servlet filters, service implementations, and security tooling.

Metrics risks:

- Changed-flag semantics affect metrics visibility. If `snapshot(..., all=false)` does not clear or honor changed flags consistently, counters/gauges may disappear or be repeatedly emitted.
- Numeric overflow is possible for long-running counters, gauges, sample counts, and rolling aggregates.
- Quantile and rolling-average APIs imply background state; missing `stop()`/`close()` can leak scheduled tasks or thread-local state.
- Public/protected `RollingFileSystemSink` fields are subclass-visible compatibility constraints. Renaming or changing them breaks subclasses/tests.
- Sink errors are operationally sensitive: ignoring errors hides telemetry loss, but surfacing them can destabilize daemons if not contained by the metrics system.

Network risks:

- DNS-to-switch mappings are security and availability adjacent. Wrong rack mapping changes replica placement, locality scheduling, and fault-domain assumptions.
- Cache invalidation is explicit; stale cached topology can persist until reload.
- Script/table mappings depend on external files/scripts and can block or fail at runtime.
- SOCKS socket configuration equality/hash behavior matters if socket factories are reused in connection caches.

Security risks:

- `Credentials`, `Token`, and `UserGroupInformation` carry secrets. APIs exposing raw `byte[]`, mutable tokens, maps, and subjects require defensive usage and careful logging.
- UGI has global static state. Tests or embedded applications that call `setConfiguration`, test renewal controls, or login methods can affect unrelated code in the same JVM.
- Keytab and ticket-cache re-login flows are race-prone if multiple threads use a UGI while credentials are refreshed.
- Kerberos principal host substitution must be exact. Incorrect canonicalization or `_HOST` handling breaks authentication or can produce cross-host principals.
- Token service construction must match RPC/HTTP service naming. Mismatches make otherwise valid tokens unusable.
- `AuthorizationException` overriding stack-trace methods can reduce diagnostics; callers should preserve context in messages.
- ACL string parsing and wildcard handling are compatibility-sensitive because ACLs are persisted and often configured by operators.
- Impersonation provider config prefixes and host/group maps are critical authorization boundaries. Incorrect prefix handling can authorize or deny proxy users unexpectedly.
- Delegation-token query-string mode risks token disclosure through logs, proxies, browser history, or referrers; header mode is safer when supported.

HTTP filter risks:

- CSRF browser detection depends on user-agent matching and ignored method lists; mistakes can block legitimate clients or allow unsafe browser requests.
- X-Frame-Options config affects clickjacking protections and UI embedding compatibility.

Service lifecycle risks:

- Service hooks must tolerate partial initialization and repeated stop attempts. Violating this contract causes shutdown failures after init/start errors.
- Listener notification and global listener registries can leak objects or introduce unexpected side effects across services in the JVM.
- `waitForServiceToStop(0)` means wait forever by contract; callers must avoid deadlocks by using bounded waits where appropriate.
- `CompositeService` stop policy affects cleanup during failures. Stopping only started services assumes child implementations cannot handle early `stop()`, while stopping all services assumes robust stop implementations.

## Test Signals

Useful test coverage suggested by this API surface:

- Metrics mutable tests: counter/gauge value changes, delta handling, `changed()` behavior, `snapshot(all=false)` vs `snapshot(all=true)`, stat min/max reset, extended stat output, quantile rollover, rolling-average close/state collection, and registry duplicate/tag override behavior.
- Metrics sink tests: sink `init`/`putMetrics`/`flush`/`close` lifecycle, Graphite/StatsD formatting, FileSink write formatting, RollingFileSystemSink roll interval computation, append/no-append behavior, forced flush, error handling with `ignoreError`, and use of supplied `Configuration`/`FileSystem`.
- JMX/cache utility tests: MBean register/unregister idempotence and name construction, `MetricsCache` updates with and without tags, cache size eviction, and `Servers.parse` default-port parsing.
- Network tests: cached mapping hits/misses, reload all vs selected names, single-switch detection, script/table mapping missing-config behavior, topology dump content, and socket factory proxy configuration/equality.
- Credentials tests: token/secret-key add/remove/count, map immutability, copy constructor, `addAll` vs `mergeAll` overwrite semantics, Writable round trip, token storage file/stream round trip in each serialized format, and secret byte-array mutation expectations.
- UGI/SecurityUtil tests: secure/simple auth configuration, `_HOST` principal substitution, login from keytab/ticket cache, forced and conditional relogin, proxy-user real/effective identity, group lookup, auth-method conversion, token/credential addition, `doAs` subject scoping, and environment token ingestion.
- Authorization tests: ACL wildcard/user/group parsing, writable round trip, real-user ACL behavior, stackless `AuthorizationException` behavior, proxy superuser config-key derivation, host/group authorization success/failure, and string-vs-address authorize overload equivalence.
- HTTP filter tests: default and custom CSRF header names, browser user-agent matching, ignored methods, rejection/allowance paths, X-Frame-Options default/custom header insertion, and servlet lifecycle cleanup.
- Token tests: token construction from identifier/secret manager, identifier decode failure behavior, binary and URL-safe round trips, private clone semantics, cache key stability, renewer selection, managed/unmanaged renew/cancel behavior, `SecretManager` invalid/standby/retriable failure paths, and tracking ID exposure.
- Delegation-token web tests: authenticator wrapping, connection configurator propagation, header vs query-string token transmission, get/renew/cancel request parameter names, JSON response parsing keys, `doAs` parameter handling, and Kerberos vs pseudo authenticator construction.
- Service lifecycle tests: valid and invalid state transitions, init/start failure triggering stop, close relaying to stop, idempotent stop, lifecycle history contents, failure cause/state recording, blocker map snapshot behavior, listener/global-listener notification ordering and unregister behavior, `waitForServiceToStop` timeout and forever-wait behavior, composite child init/start/stop ordering, child failure cleanup, and `STOP_ONLY_STARTED_SERVICES` policy.

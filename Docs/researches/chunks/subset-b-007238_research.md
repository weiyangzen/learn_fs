# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml lines 36702-42861

## Scope

This chunk is a JDiff public API snapshot for Hadoop Common 3.5.0. It starts in the tail of `org.apache.hadoop.metrics2.AbstractMetric`, covers the rest of the public Metrics2 API and several Metrics2 subpackages, then moves through network mapping/socket APIs, ONC RPC enum surfaces, Hadoop security credential/authentication APIs, and ends at the beginning of `org.apache.hadoop.security.alias.CredentialProvider`. Because the source is generated XML rather than implementation code, the research focuses on exposed contracts, API shape, state surfaces, integration behavior implied by signatures/docs, compatibility risks, and tests that should protect users of these contracts.

## Purpose

The chunk documents several cross-cutting Hadoop Common subsystems:

- Metrics2 core interfaces and helpers define how Hadoop components expose metrics, build records, filter sources/sinks, publish to sinks, register with a metrics system, expose JMX controls, and represent immutable metric/tag values.
- Metrics2 annotations, filters, libraries, sinks, Ganglia enums, and utilities provide the higher-level instrumentation layer used by Hadoop daemons and tests: registries, mutable counters/gauges/stats/quantiles, default singleton metrics system management, file/network metrics sinks, MBean registration, and sink-side cache helpers.
- Network APIs define DNS-to-rack mapping contracts, cached/script/table mapping implementations, socket factories, and connect-timeout exception typing used by Hadoop RPC/filesystem clients and daemons.
- ONC RPC APIs expose enum conversions for RPC message/reply/auth states used by Hadoop's NFS/portmap-style services.
- Security APIs expose access-control exceptions, SASL/authentication enum mapping, credentials token/secret-key storage and serialization, group/id mapping providers, Kerberos exception diagnostics, security utility methods, and `UserGroupInformation` login/proxy/doAs/token/group behavior.
- The final `CredentialProvider` fragment marks the start of the credential alias provider API, but this chunk only includes its constructor and the beginning of `isTransient()`.

## Important APIs, Types, And Functions

### Metrics2 Core

The tail of `AbstractMetric` exposes `type()`, `visit(MetricsVisitor)`, and object identity methods. It is the immutable metric value abstraction paired with visitor callbacks for gauges and counters.

`MetricStringBuilder` and `MetricsJsonBuilder` both extend `MetricsRecordBuilder` and collect metric records into diagnostic renderings. `MetricStringBuilder` formats entries as `prefix + name + separator + value + suffix`, supports arbitrary `tuple(key, value)`, and implements the tag/counter/gauge/add paths. `MetricsJsonBuilder` exposes the same builder-style record API and serializes collected values as JSON; it also exposes a public `LOG`.

`MetricType` is the public enum for metric kind. `MetricsInfo` carries immutable metric/tag metadata through `name()` and `description()`. `MetricsTag` combines `MetricsInfo` and a string value and exposes name, description, info, value, equality, hash, and string conversion.

`MetricsCollector` starts records via `addRecord(String)` or `addRecord(MetricsInfo)`. `MetricsRecordBuilder` is the fluent builder contract for `tag`, `add(MetricsTag)`, `add(AbstractMetric)`, `setContext`, overloaded `addCounter`, overloaded `addGauge`, `parent()`, and `endRecord()`. `MetricsRecord` is the immutable snapshot interface exposing timestamp, name, description, context, tags, and metric iterable.

`MetricsSource.getMetrics(MetricsCollector, boolean)` is the pull side of the framework. `MetricsSink.putMetrics(MetricsRecord)` and `flush()` are the sink side. `MetricsFilter` can accept or reject by name, tag, tag collection, or whole record and implements `MetricsPlugin`; `MetricsPlugin.init(SubsetConfiguration)` is the common configuration hook. `MetricsException` is the runtime wrapper used by the framework.

`MetricsSystem` is the daemon-facing registration and lifecycle abstraction: `init(prefix)`, `register(source)`, `register(name, desc, source)`, `unregisterSource(name)`, `getSource(name)`, callback registration, immediate publication, and `shutdown()`. `MetricsSystemMXBean` exposes JMX lifecycle operations for starting/stopping the system and Metrics MBeans plus `currentConfig()`. `MetricsVisitor` defines overloaded gauge/counter callbacks for `int`, `long`, `float`, and `double`.

### Metrics2 Annotation, Filter, Library, Sink, And Utility APIs

`org.apache.hadoop.metrics2.annotation.Metric` annotates fields or methods with optional value/name/description, sample/value names for stats, `always`, type, and quantile rollover interval. `Metrics` annotates metric groups with record name, description, and context. The nested `Metric.Type` enum is represented in this XML as `Type`.

`GlobFilter` and `RegexFilter` extend the metrics pattern filter base and compile strings to `com.google.re2j.Pattern`. They are intended for metrics configuration files.

`DefaultMetricsSystem` is an enum singleton facade for the process-wide default metrics system. It initializes or returns the current `MetricsSystem`, shuts it down, swaps the instance, toggles mini-cluster mode, manages MBean/source-name uniqueness, and returns `ObjectName` values. Name collision behavior is visible through `sourceName(name, dupOK)`.

`Interns` creates interned `MetricsInfo` and `MetricsTag` instances to reduce allocation and provide canonical metadata/tag objects.

`MetricsRegistry` is the main mutable source-side registry. It exposes registry info, metric/tag lookup, factory methods for int/long counters, int/long/float gauges, quantiles, inverse quantiles, stats, rates, aggregated rates, and rolling averages. It also supports adding samples by name, context/tag creation with override controls, snapshotting all metrics into a `MetricsRecordBuilder`, and string conversion.

The mutable metric hierarchy includes:

- `MutableMetric`: abstract base with `snapshot(builder, all)`, convenience `snapshot(builder)`, changed-flag management, and `changed()`.
- `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong`: monotonically increasing counters with increment/value/snapshot behavior.
- `MutableGauge`, `MutableGaugeInt`, and `MutableGaugeLong`: gauges with increment/decrement/set/value/snapshot behavior.
- `MutableQuantiles` and `MutableInverseQuantiles`: online quantile estimators with interval rollover, quantile metadata arrays, estimator access, add, snapshot, stop, and previous snapshot state. They expose `QUANTILES`, `INVERSE_QUANTILES`, and `previousSnapshot`.
- `MutableRate`, `MutableRates`, and `MutableRatesWithAggregation`: throughput/rate metrics, protocol-method initialization, named elapsed-time sample updates, and snapshots.
- `MutableRollingAverages`: rolling aggregate collection with thread-local state collection, named sample add, close, test-only record-validity control, and stats retrieval.
- `MutableStat`: sample count/sum/stat tracking with optional extended stats, timestamp control, reset of min/max, last-stat access, snapshot timestamp, and string conversion.

Metrics sinks in this chunk include `FileSink`, `GraphiteSink`, `RollingFileSystemSink`, and `StatsDSink`. They implement the standard `init(SubsetConfiguration)`, `putMetrics(MetricsRecord)`, `flush()`, and close/write paths where applicable. `RollingFileSystemSink` has the richest public surface: test constructor with roll intervals, roll interval parsing, next-flush computation, initial flush time setup, and public fields for source, error handling, append behavior, base path, roll intervals, next flush calendar, force/has-flushed flags, supplied configuration, and supplied filesystem. `StatsDSink.writeMetric(String)` exposes the line-writing path.

Ganglia-related enum surfaces expose `GangliaConfType` and `GangliaSlope`. `org.apache.hadoop.metrics2.source` has no concrete public types in this chunk. `MBeans` provides standard Hadoop MBean registration/unregistration and name parsing. `MetricsCache` caches `MetricsRecord` values for sinks that cannot handle sparse updates. `Servers.parse(specs, defaultPort)` parses comma/space-separated server endpoint strings.

### Network And ONC RPC APIs

`DNSToSwitchMapping` is the rack-resolution interface: `resolve(List<String>)`, `reloadCachedMappings()`, and targeted reload by node list. `AbstractDNSToSwitchMapping` adds `Configurable` behavior, default single-switch/topology diagnostics, switch-map access, and helper `isMappingSingleSwitch(mapping)`.

`CachedDNSToSwitchMapping` wraps a raw mapping, caches results, exposes the raw mapping field, resolves names, dumps its switch map, delegates single-switch queries, and reloads all or selected cached mappings. `ScriptBasedMapping` is a cached mapping using a configured external script and exposes `NO_SCRIPT`, configuration access, and `toString()`. `TableMapping` is a cached mapping backed by a table file and supports configuration and cache reload.

`ConnectTimeoutException` specializes `SocketTimeoutException` for `NetUtils.connect`. `SocksSocketFactory` and `StandardSocketFactory` implement the overloaded `SocketFactory.createSocket` variants. `SocksSocketFactory` also implements Hadoop configuration access and equality/hash behavior around its proxy; `StandardSocketFactory` provides equality/hash behavior for default sockets.

ONC RPC enum surfaces include accepted reply state (`AcceptState` with integer value conversion), denied reply state (`RejectState`), reply state (`ReplyState` with `fromValue`), XDR state (`State`), RPC message type (`Type` with `getValue()` and `fromValue()`), and security auth flavor (`AuthFlavor` with numeric RFC 1831 value).

### Security APIs

`AccessControlException` is the checked access-control failure type. `AuthMethod` is the SASL RPC auth enum surface with mechanism name, binary read/write, and public `code`. `AuthenticationMethod` maps UGI authentication modes to/from `SaslRpcServer.AuthMethod`.

`Credentials` stores tokens and secret keys in memory and serializes them. Public operations include token lookup/add/remove, unmodifiable token map access, token count, secret key lookup/add/remove, secret-key alias listing, unmodifiable secret-key map access, reading token storage files from `Path` or `File`, stream read/write, token storage file write with optional serialized format, `Writable`-style `write`/`readFields`, and combining credentials through `addAll` and `mergeAll`.

`GroupMappingServiceProvider` resolves a user to groups, refreshes/augments caches, exposes a set-returning alternative, and publishes `GROUP_MAPPING_CONFIG_PREFIX`. `IdMappingServiceProvider` maps users/groups to numeric ids and ids back to names, with "allowing unknown" variants.

`KerberosAuthException` carries diagnostic context around failed Kerberos authentication. It can be constructed from message, cause, or both, then enriched with user, principal, keytab file, and ticket cache file. Accessors and `getMessage()` expose the enriched details. `QualityOfProtection` exposes the SASL QOP string through `getSaslQop()` and public `saslQop`.

`SecurityUtil` is the public utility surface for security configuration and protocol metadata. It includes static configuration and token-service-IP controls, Kerberos TGT inspection, server principal expansion from hostname/address, keytab login helpers, delegation-token service-name construction, principal host extraction, security-info provider registration, Kerberos/token info lookup for RPC protocols, token service address/set/build helpers, privileged `doAs` helpers for login/current user, secure DNS resolution, authentication-method config get/set, privileged-port checks, ZooKeeper auth info parsing, and ZooKeeper SSL configuration validation/application. Its public fields include `LOG`, `HOSTNAME_PATTERN`, and `FAILED_TO_GET_UGI_MSG_HEADER`.

`SerializedFormat` is the credentials serialized-format enum with `valueOf(String)` and `valueOf(int)`.

`UserGroupInformation` is the central Hadoop user identity surface. This chunk exposes static initialization/configuration/reset methods, security status checks, login success and Kerberos credential checks, current/login/best UGI selection, ticket-cache and `Subject` login helpers, setting login user, keytab/ticket relogin flows, remote/proxy/testing user creation, real-user lookup, short/full username and primary group access, token identifier/token/credential mutation and access, group retrieval, authentication method get/set including real-authentication handling, subject identity equality/hash, protected subject access, `doAs` wrappers for privileged actions, user-info logging helpers, a diagnostic `main`, and token environment variable names `HADOOP_TOKEN_FILE_LOCATION` and `HADOOP_TOKEN`. `getGroups()` is explicitly deprecated in favor of `getGroupsSet()`.

The final `org.apache.hadoop.security.alias.CredentialProvider` fragment shows an abstract provider class with a public constructor and `isTransient()` returning whether the provider represents a transient store. The rest of that class belongs to a later chunk.

## Control Flow

Metrics source flow is pull-oriented. A registered `MetricsSource` receives a `MetricsCollector`, opens a record through `addRecord`, populates tags/counters/gauges/metrics through a `MetricsRecordBuilder`, and the `MetricsSystem` publishes snapshots to configured `MetricsSink` instances. Filters may run at source or sink boundaries by name/tag/record. Builder helpers such as `MetricStringBuilder` and `MetricsJsonBuilder` use the same builder methods but terminate in a diagnostic `toString()` representation.

Mutable metrics use a changed-flag/snapshot flow. Counter/gauge/stat/quantile objects mutate in source code paths, set changed state, and later write a snapshot into a record builder. The `all` flag controls whether unchanged metrics are emitted. Quantile and rolling-average APIs add extra rollover/estimator collection behavior, and `stop()`/`close()` are lifecycle hooks for background or retained state.

Metrics sink flow begins with `init(SubsetConfiguration)`, then repeated `putMetrics(record)` calls, periodic `flush()`, and optional `close()`. Rolling filesystem sink flow includes deriving roll intervals from configuration, computing initial and next flush times, writing metrics to a filesystem path, and rolling/forcing flushes based on clock state.

Rack mapping flow calls `resolve(names)` on a raw or cached mapper. Cached mapping resolves misses through the raw mapper and preserves results until full or targeted reload. Script/table mappings feed raw results from external configuration or data files. Socket factories create configured sockets through Java `SocketFactory` overloads.

ONC RPC enum flow is value conversion: wire integer values map to enum constants through `fromValue`, while outbound paths use `getValue()`.

Security flow is layered. `SecurityUtil` interprets configuration, expands principals, configures protocol security metadata, performs keytab login, constructs token service names, and wraps privileged execution. `UserGroupInformation` holds or locates the active identity, manages relogin, creates remote/proxy/test users, attaches token credentials, exposes groups, and runs actions through `Subject.doAs` semantics. `Credentials` is the portable container for tokens and secret keys that UGI can absorb or expose.

## State And Persistence Behavior

Metrics state is mostly process-local and in memory. `DefaultMetricsSystem` maintains singleton process state, source/MBean names, and mini-cluster mode. `MetricsRegistry` owns a mutable map of metrics and tags. Mutable metrics hold counters, gauges, sample stats, quantile estimators, rolling average windows, previous snapshots, changed flags, and in some cases thread-local state.

Metrics persistence occurs mainly through sinks. `FileSink` and `RollingFileSystemSink` write metrics to files or Hadoop filesystems; the rolling sink carries public scheduling and filesystem state. `GraphiteSink` and `StatsDSink` persist by sending metrics to external daemons over the network. `MetricsCache` keeps sink-side record state so sinks that need complete records can handle sparse updates.

Network mapping state is cached in `CachedDNSToSwitchMapping` and subclasses. It can become stale until reloaded, and diagnostics can expose a copy of host-to-switch mappings. Script and table mappings depend on configuration and external command/file state outside the Java heap.

Credentials persist in two forms: in-memory maps keyed by `Text` aliases, and serialized token storage streams/files using `Credentials.SerializedFormat`. Returned token/secret maps are documented as unmodifiable views, but byte arrays remain sensitive mutable data at the API boundary.

UGI state is both global and per-subject. Global state includes static configuration, initialized/security flags, login user, relogin scheduling, and metrics attachment. Per-user state is represented by a JAAS `Subject`, principals, token identifiers, tokens/credentials, authentication method, real-user relation for proxies, and group resolution results. The token-related environment variables indicate integration with external credential files or base64 token payloads.

## Dependencies And Integration Points

This API surface integrates with Java core APIs (`DataInput`, `DataOutput`, `IOException`, `InterruptedException`, `RuntimeException`, `Socket`, `SocketFactory`, `InetAddress`, `InetSocketAddress`, `URI`, `Subject`, privileged actions, JMX `ObjectName`, `Date`, `Calendar`, collections, and concurrency/lifecycle close hooks).

Hadoop dependencies include `Configuration`, `Configurable`, `Path`, `FileSystem`, `Text`, `MetricsInfo`, token and token identifier classes, security annotations/providers, `ZKUtil.ZKAuthInfo`, RPC/SASL classes, and Writable-style serialization. External dependencies include Apache Commons Configuration `SubsetConfiguration`, RE2/J regex patterns, ZooKeeper client SSL classes, SLF4J logging, Kerberos/JGSS JAAS concepts, and external metrics services such as Graphite, StatsD, Ganglia, and filesystem-backed logs.

Operational integration points are broad: daemon startup initializes metrics and UGI; RPC setup uses `SecurityUtil` and UGI authentication state; HDFS/YARN rack awareness uses `DNSToSwitchMapping`; token files move credentials between clients and services; metrics sinks ship operational data to local files and monitoring backends; MBeans expose metrics lifecycle controls to JMX.

## Risks And Edge Cases

- This is generated API XML, so implementation details such as synchronization, exact map types, serialization field order, retry behavior, and background thread management must be confirmed in Java sources when changing behavior.
- Metrics names, tag names, source names, and MBean names are compatibility-sensitive. Changes can break dashboards, alerts, JMX consumers, and sink parsers.
- `DefaultMetricsSystem` is process-global. Tests and embedded mini-clusters can interfere unless singleton state and source-name registries are reset carefully.
- Mutable metric snapshot semantics depend on changed flags and the `all` parameter. Missed `setChanged()` calls or overuse of `all=false` can hide metrics.
- Quantile, inverse quantile, and rolling average classes retain estimator/window state and expose lifecycle methods. Missing `stop()` or `close()` risks retained background resources or stale observations.
- Rolling file metrics output depends on clock calculations, filesystem append support, configured paths, and flush/roll intervals. Public mutable fields increase the risk of inconsistent test or subclass state.
- Pattern filters use RE2/J. Regex/glob compatibility and invalid patterns need explicit validation in configuration tests.
- Cached rack mappings can become stale after DNS, script, or table changes. Reload behavior, partial reload behavior, and single-switch optimizations must be covered.
- Script-based mapping depends on external process execution and configuration. Missing scripts, slow scripts, malformed output, and differing host/IP canonicalization can affect placement.
- Socket factory equality/hash behavior matters for connection pooling. Proxy configuration changes must be reflected consistently.
- ONC RPC enum `fromValue` methods must reject or handle unknown wire values predictably.
- Credentials expose sensitive tokens and secret-key byte arrays. Copying, map immutability, alias collisions, serialization format compatibility, and accidental logging are high-risk areas.
- `Credentials.addAll` and `mergeAll` likely differ on overwrite behavior; callers need tests that protect expected token/secret collision semantics.
- `GroupMappingServiceProvider.getGroups()` can fail with `IOException`; callers must tolerate empty/failing group providers and cache refresh races.
- `KerberosAuthException` carries keytab/ticket-cache details. Diagnostics are useful but can leak sensitive deployment paths if logged broadly.
- `SecurityUtil.setTokenServiceUseIp`, DNS resolution, and principal host expansion affect token identity and Kerberos service names. Behavior can change across IP/hostname, HA, proxy, and secure DNS environments.
- ZooKeeper SSL configuration must validate complete truststore/keystore inputs; partial configuration should fail early and clearly.
- UGI has substantial static global state. `setConfiguration`, `reset`, `setLoginUser`, relogin methods, and test hooks can affect every caller in the JVM.
- UGI proxy users must preserve real-user and real-authentication semantics. Incorrect handling can weaken authorization/audit trails.
- `getGroups()` is deprecated in favor of `getGroupsSet()`; new code should avoid list conversion unless primary-group ordering is required.
- Token and credential mutation on UGI has synchronization-sensitive APIs (`addTokenIdentifier`, auth method getters/setters are synchronized in the XML). Concurrency tests should cover simultaneous token additions and `doAs` usage.
- The `CredentialProvider` class is incomplete in this chunk; any conclusions about its full behavior must be deferred to later chunk research.

## Test Signals

Useful validation for code touching APIs in this chunk:

- Metrics core: source registration/unregistration, duplicate source naming, record builder chaining, context tag insertion, all counter/gauge numeric overloads, metric visitor dispatch, filter acceptance by name/tag/record, JSON/string builder output, and MXBean lifecycle methods.
- Metrics registry/mutable metrics: counter/gauge increment/decrement/set, changed-flag behavior, snapshot with `all=true` and `all=false`, stat min/max/stdev and timestamp behavior, rate sample aggregation, protocol-based rate initialization, quantile rollover, inverse quantile outputs, rolling average collection/close, and concurrent metric updates.
- Metrics sinks: configuration parsing, malformed configs, flush/close idempotence, file append support, rolling interval and next-flush calculations, StatsD/Graphite line formatting, network failure handling, and filesystem error behavior under `ignoreError`.
- MBeans/cache/server utilities: JMX object name construction including extra properties, unregister idempotence, cache update/get with and without tags, sparse metric update behavior, and parsing of server specs with default ports and malformed entries.
- Network mapping: raw and cached `resolve`, cache hit/miss behavior, full and targeted reloads, script/table configuration changes, unknown hosts, single-switch detection, topology dump content, and socket factory behavior with local bind addresses and SOCKS proxy settings.
- ONC RPC: enum round-trip for every known wire value and explicit tests for unknown values.
- Credentials: token and secret-key add/remove/count/map immutability, alias collision behavior, byte-array handling, read/write stream round trips, `Path` and `File` token-storage file round trips, all serialized formats, `addAll` versus `mergeAll`, and invalid/corrupt token-storage files.
- Group/id mapping: IOException propagation, cache refresh/add behavior, set/list consistency, unknown uid/gid behavior, and provider configuration prefix use.
- Kerberos/security utilities: principal expansion for `_HOST`, keytab login failure diagnostics, TGT original-ticket detection, token service build/parse with IP and hostname modes, security info provider lookup, `doAsLoginUser` and `doAsCurrentUser` exception propagation, secure DNS failure modes, privileged port boundary values, ZooKeeper auth parsing, and SSL configuration validation.
- UGI: static initialization/reset isolation, security-enabled mode selection, current/login user behavior, ticket-cache and keytab login/relogin flows, forced relogin throttling bypass, remote/proxy/test user creation, real-user and real-authentication results, token identifier and token mutation, credentials import/export, group retrieval including deprecated `getGroups`, equality/hash by subject, `doAs` checked/unchecked exception propagation, and logging helpers with token redaction expectations.

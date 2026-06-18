# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.2.xml lines 24460-30682

## Scope

This chunk is a generated JDiff API snapshot for Apache Hadoop Common 3.2.2. It begins inside the tail of `org.apache.hadoop.io.file.tfile.Utils`, covers serializer, Avro serializer, log metrics, metrics2 core/filter/lib/sink/util APIs, network topology and socket factory APIs, the main security and authorization APIs, HTTP security filters, and ends inside `org.apache.hadoop.security.token.Token`.

The source is API metadata rather than executable implementation. The research therefore treats method signatures, visibility, inheritance, implemented interfaces, checked exceptions, static/final/synchronized markers, fields, and embedded Javadocs as the compatibility contract. Runtime behavior below is inferred from those public contracts and docs.

## Purpose

The opening `tfile.Utils` tail exposes sorted-list binary-search helpers used by TFile and its users. `lowerBound(List, T)` returns the first element greater than or equal to a key, while `upperBound(List, T)` returns the first element greater than a key.

The serialization packages define Hadoop pluggable serialization entry points. `JavaSerialization` is an experimental `Serialization` for Java `Serializable` classes, `JavaSerializationComparator` deserializes and compares objects through `Comparable`, and `WritableSerialization` delegates to Hadoop `Writable.write` and `Writable.readFields`. The Avro subpackage adds `AvroSerialization` as a configured abstract base plus specific and reflect variants selected by generated Avro classes, configured package names, or the `AvroReflectSerializable` marker.

The metrics packages are the largest surface. They describe immutable metric values and tags, record builders, sources, sinks, metrics-system lifecycle and JMX control, mutable counters/gauges/stats/quantiles/rates/rolling averages, sink implementations for files, Graphite, rolling filesystem output, and StatsD, plus MBean, cache, and server-address utilities.

The network package provides rack-awareness and socket-factory APIs. DNS/IP names are mapped to network locations by pluggable `DNSToSwitchMapping` implementations, optionally cached, script-backed, or table-backed. Socket factories create standard or SOCKS-proxied sockets.

The security packages cover credential and token storage, group and id mapping, Kerberos login utilities, user identity/proxy-user management, credential-provider abstraction, ACLs, impersonation checks, CSRF/clickjacking servlet filters, and the beginning of token secret-manager/token APIs.

## Important APIs, Types, and Functions

### Serialization

- `org.apache.hadoop.io.serializer.JavaSerialization` implements `Serialization` for Java `Serializable` classes.
- `JavaSerializationComparator<T>` extends `DeserializerComparator` and can throw `IOException` during construction; it compares deserialized objects via `Comparable`.
- `WritableSerialization` extends `Configured` and implements `Serialization`, delegating object state to the `Writable` protocol.
- Package configuration is through the `io.serializations` property, whose values name `Serialization` implementations able to create serializers and deserializers.
- `AvroSerialization` extends `Configured`, implements `Serialization`, and exposes `AVRO_SCHEMA_KEY`.
- `AvroSpecificSerialization` handles Avro generated "specific" classes.
- `AvroReflectSerialization` handles classes either in configured comma-separated `AVRO_REFLECT_PACKAGES` (`avro.reflect.pkgs`) or implementing the marker `AvroReflectSerializable`.

### Log Metrics

- `EventCounter` extends log4j `AppenderSkeleton`.
- Its public appender contract includes `append(LoggingEvent)`, `close()`, and `requiresLayout()`.
- It counts fatal, error, and warn events and is wired by class name from `log4j.properties`.

### Metrics2 Core

- `AbstractMetric` implements `MetricsInfo` and represents immutable metric metadata plus abstract `value()`, `type()`, and `visit(MetricsVisitor)` methods. It also supplies name, description, equality, hash, and string behavior.
- `MetricsInfo` supplies immutable `name()` and `description()` metadata; annotation docs tie names/descriptions to `@Metric` values or class names.
- `MetricsTag` implements `MetricsInfo` and adds immutable tag `value()`.
- `MetricsCollector.addRecord(String|MetricsInfo)` creates a `MetricsRecordBuilder`.
- `MetricsRecord` is an immutable timestamped snapshot with `name`, `description`, `context`, unmodifiable tags, and immutable metric iteration.
- `MetricsRecordBuilder` is the fluent writer API for tags, existing tags, existing immutable metrics, context, int/long counters, int/long/float/double gauges, `parent()`, and `endRecord()`.
- `MetricsJsonBuilder` and `MetricStringBuilder` implement record-building APIs that render collected data to JSON or custom delimited strings. `MetricsJsonBuilder.LOG` is a public static logger.
- `MetricsPlugin.init(SubsetConfiguration)` is the common plugin initialization hook.
- `MetricsSource.getMetrics(MetricsCollector, boolean all)` snapshots source state; `MetricsSink.putMetrics(MetricsRecord)` and `flush()` consume records.
- `MetricsSystem` registers/unregisters sources, registers JMX callbacks, requests best-effort immediate publication with `publishMetricsNow()`, and shuts down via `shutdown()`.
- `MetricsSystemMXBean` exposes JMX lifecycle and diagnostics: `start`, `stop`, `startMetricsMBeans`, `stopMetricsMBeans`, and `currentConfig`.
- `MetricsVisitor` receives typed gauge/counter callbacks for int, long, float, and double gauge values and int/long counters.

### Metrics2 Filters and Mutable Metrics

- `GlobFilter` and `RegexFilter` compile configured expressions to `com.google.re2j.Pattern` for metrics filtering.
- `DefaultMetricsSystem` is the default singleton with `initialize`, `instance`, `shutdown`, `setMiniClusterMode`, and `inMiniClusterMode`.
- `Interns` creates interned `MetricsInfo` and `MetricsTag` instances.
- `MetricsRegistry` creates and owns mutable metrics: int/long counters, int/long/float gauges, quantiles, stats, rates, aggregated rates, rolling averages, tags, context, named sample additions, and snapshots into a builder. Several mutating methods are synchronized, marking it as a shared source-side state container.
- `MutableMetric` tracks change state with `setChanged`, `clearChanged`, `changed`, and `snapshot(builder, all)`/`snapshot(builder)`.
- `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong` model monotonically increasing metrics.
- `MutableGauge`, `MutableGaugeInt`, and `MutableGaugeLong` model values that can increase, decrease, or be set.
- `MutableQuantiles` maintains online estimates for fixed quantiles, rolls over at a configured interval, exposes `quantiles`, `previousSnapshot`, an estimator getter/setter, `add(long)`, `snapshot`, and `stop`.
- `MutableStat` stores sample statistics, optional extended stats, Welford-based variance data, `lastStat`, and min/max reset. Its docs warn that adding many samples as a single `(numSamples, sum)` preserves mean but may reduce variance accuracy.
- `MutableRate`, `MutableRates`, and `MutableRatesWithAggregation` cover throughput/rate tracking. `MutableRates` synchronizes all accesses and is documented as poor for high contention; `MutableRatesWithAggregation` uses per-thread local counts aggregated on snapshot and can lose samples produced between the last snapshot and thread death.
- `MutableRollingAverages` implements `Closeable`, keeps sliding-window average state, can collect thread-local states, add named samples, snapshot, close, and return stats filtered by minimum sample count.

### Metrics Sinks and Utilities

- `FileSink`, `GraphiteSink`, and `StatsDSink` implement sink lifecycle with `init`, `putMetrics`, `flush`, and `close`; `StatsDSink` also exposes `writeMetric`.
- `RollingFileSystemSink` writes metrics to a filesystem-backed rolling sink. It has a reflection constructor and a testing constructor, `init`, roll interval extraction, flush scheduling (`updateFlushTime`, `setInitialFlushTime`), `putMetrics`, `flush`, and `close`.
- `RollingFileSystemSink` exposes protected state for source name, error policy, append policy, base path, roll/offset intervals, next flush calendar, force/has-flushed booleans, and supplied test configuration/filesystem.
- Empty package markers exist for `org.apache.hadoop.metrics2.sink.ganglia` and `org.apache.hadoop.metrics2.source` in this slice.
- `MBeans` registers/unregisters MBeans and parses service/name parts from Hadoop's standard MBean name format.
- `MetricsCache` keeps dense cached records for sinks that do not support sparse updates.
- `Servers.parse(String, int)` parses comma and/or space separated server specifications with default ports.

### Network

- `AbstractDNSToSwitchMapping` implements common `DNSToSwitchMapping` support without extending `Configured`, explicitly to avoid superclass-constructor calls into subclass `setConf`. It tracks configuration, reports single-switch status, returns switch maps, dumps known topology, and exposes `isMappingSingleSwitch(DNSToSwitchMapping)`.
- `DNSToSwitchMapping.resolve(List)` maps hostnames/IPs one-to-one to rack paths such as `/foo/rack`; implementations should return `NetworkTopology.DEFAULT_RACK` for unknown names. It also defines cache reload methods for all or selected names.
- `CachedDNSToSwitchMapping` wraps a raw mapper, caches resolved host-to-rack mappings, exposes a copied switch map, delegates single-switch checks to the raw mapping, and can reload all or selected cached mappings.
- `ScriptBasedMapping` is a cached wrapper around a script-backed raw mapper configured by `CommonConfigurationKeys.NET_TOPOLOGY_SCRIPT_FILE_NAME_KEY`; it also exposes `NO_SCRIPT`, constructors for default/raw/conf inputs, and `Configurable` methods.
- `TableMapping` is a cached mapper backed by a two-column whitespace-separated table configured via `net.topology.table.file.name`; unresolved entries map to `/default-rack`.
- `ConnectTimeoutException` extends `SocketTimeoutException` for `NetUtils.connect` connection timeouts.
- `SocksSocketFactory` extends `javax.net.SocketFactory`, implements `Configurable`, and creates sockets through a configured or supplied SOCKS `Proxy`.
- `StandardSocketFactory` exposes the same `createSocket` overload family without `Configurable` and represents normal socket creation.

### Security, Credentials, and UGI

- `AccessControlException` extends `IOException` and includes a default constructor for unwrapping `RemoteException`.
- `Credentials` implements `Writable` and stores tokens plus secret keys in memory. It supports token/key get/add/remove/list/count maps, static token-storage file reads from `Path` or local `File`, stream read/write, file write with optional `SerializedFormat`, `Writable` read/write, `addAll` overwrite merge, and `mergeAll` non-overwrite merge.
- `GroupMappingServiceProvider` returns groups for users, refreshes group caches, and pre-adds group cache entries. `GROUP_MAPPING_CONFIG_PREFIX` is public.
- `IdMappingServiceProvider` maps user/group names and numeric ids in both directions, including unknown-tolerant uid/gid methods.
- `KerberosAuthException` carries contextual fields for user, principal, keytab file, and ticket cache file, with setters/getters and a composed message.
- `SecurityUtil` exposes global security helpers: configuration setup, original TGT checks, server principal substitution, keytab/ticket-cache login helpers, delegation-token service-name construction, Kerberos/token annotation discovery, token-service address/text conversion, login/current-user `doAs` helpers, auth-method configuration, privileged-port checks, and ZooKeeper auth-info loading. Public constants include `LOG`, `HOSTNAME_PATTERN`, and `FAILED_TO_GET_UGI_MSG_HEADER`.
- `UserGroupInformation` wraps a JAAS `Subject` and supports simple, Windows/Unix, and Kerberos identity flows. Static APIs manage global configuration, initialization checks, metrics reattachment, security-enabled state, login/current/best UGI discovery, ticket-cache/subject/keytab logins, keytab logout/relogin/force-relogin, remote/proxy/test user construction, login-method checks, and debug logging.
- UGI instances expose Kerberos-credential checks, real/effective user data, short/full user name, primary group, group arrays/lists, token identifiers, tokens, credentials, auth-method setters/getters, equality/hash by subject, protected subject access, and `doAs` wrappers for privileged actions.
- `UserGroupInformation.AuthenticationMethod` is an enum-compatible nested class with `values`, `valueOf(String)`, conversion to/from `SaslRpcServer.AuthMethod`, and docs naming existing authentication method types.

### Security Alias, Authorization, HTTP, and Tokens

- `CredentialProvider` is an abstract, thread-safe credential/password store API. It differentiates transient stores from durable ones, flushes changes, retrieves aliases and entries, creates/deletes entries, reports missing-password state, and exposes `CLEAR_TEXT_FALLBACK`.
- `CredentialProviderFactory` loads provider implementations by service loader and configuration path (`CREDENTIAL_PROVIDER_PATH`), with abstract `createProvider(URI, Configuration)` and static `getProviders(Configuration)`.
- `AccessControlList` implements `Writable`, parses user/group ACL strings, supports wildcard all-allowed state, add/remove users/groups, user and group collection access, membership checks against `UserGroupInformation`, ACL string rendering, and serialization.
- `AuthorizationException` extends `AccessControlException` but suppresses stack trace access/printing for security.
- `DefaultImpersonationProvider` implements `ImpersonationProvider`, is configurable, initializes from a proxy-user configuration prefix, authorizes proxy UGI plus remote address, builds proxy superuser config keys, exposes configured proxy groups/hosts, and has synchronized `getTestProvider`.
- `ImpersonationProvider` extends `Configurable`, initializes by configuration prefix, and authorizes proxy users by `InetAddress`; the string-address overload is a default compatibility path that is documented as less preferred because it may re-resolve addresses.
- `RestCsrfPreventionFilter` implements `javax.servlet.Filter`, classifies browser user agents with configurable regex defaults (`^Mozilla.*`, `^Opera.*`), enforces a configurable custom header unless ignored by method/user-agent rules, exposes `handleHttpInteraction`, and converts prefixed Hadoop `Configuration` keys into filter init parameters.
- `XFrameOptionsFilter` implements `Filter`, adds clickjacking protection through `X_FRAME_OPTIONS`, and also exposes configuration-prefix-to-filter-params conversion.
- Empty package markers exist for `org.apache.hadoop.security.protocolPB` and `org.apache.hadoop.security.ssl`.
- `SecretManager<T>` is the server-side token secret manager. It creates/retrieves token passwords, provides a retriable retrieval path with `StandbyException`, `RetriableException`, and `IOException`, creates empty identifiers, checks read availability, generates random secrets, computes HMAC passwords, and converts raw bytes into `SecretKey`.
- The chunk ends in the middle of `Token<T>`. Visible APIs construct tokens from identifiers plus secret managers, raw components, default state, another token, or `SecurityProtos.TokenProto`; mutate identifier/password/service; copy tokens; convert to protobuf; expose identifier, decoded identifier, password, kind, and service; and define public/private clone predicates where base tokens are non-private.

## Control Flow

The XML has no runtime control flow, but the API contracts imply these operational paths:

- Serialization selection starts from `io.serializations`; Hadoop code asks configured `Serialization` implementations whether they support a class, then obtains matching serializers/deserializers. Writable serialization delegates to each object's `write`/`readFields`; Java comparator deserializes both inputs and invokes `Comparable`.
- Avro reflect serialization accepts a class when it either implements the marker interface or belongs to a configured package. Specific serialization is intended for generated Avro classes.
- Metrics collection flows from mutable source-side state to immutable records: a `MetricsSource` snapshots into a `MetricsCollector`, builder calls add tags/metrics/gauges/counters, `MetricsSystem` periodically polls sources, then pushes records to `MetricsSink` implementations and flushes them. `publishMetricsNow()` is documented as best-effort synchronous snapshot and sink publication.
- Mutable metrics update local state and mark themselves changed. Snapshot calls emit either all metrics or only changed metrics depending on the `all` flag, then clear changed state as appropriate. Registry-level snapshots aggregate all registered mutables.
- Quantile/stat/rate/rolling-average metrics add samples during operation and publish derived snapshots later. Quantiles roll over by interval; rolling averages rotate windows; aggregated rates collect thread-local data at snapshot time.
- Sink control flow is lifecycle based: `init(SubsetConfiguration)` configures external destination and buffering, `putMetrics` writes records, `flush` forces buffered data, and `close` releases resources. Rolling filesystem output also advances `nextFlush` according to roll and offset intervals.
- Rack mapping starts with `resolve(List)` and requires output list position correspondence with input hosts. Cached mapping resolves misses through a raw mapping and serves repeated lookups from memory until all or selected mappings are reloaded. Script and table mappings derive their raw data from configuration.
- Security credential flow keeps tokens and secret keys in memory, can serialize them through `Writable`, stream, or token-storage files, and can merge credential sets either overwriting or preserving existing entries.
- UGI flow initializes global security configuration, discovers or performs a login, creates current/login/proxy/remote users, attaches tokens/credentials to a subject-backed identity, and executes actions under that identity with `doAs`.
- Impersonation flow initializes provider state from proxy-user configuration, receives an effective/proxy UGI plus remote address, and throws `AuthorizationException` if the real user, allowed groups/users, or allowed host constraints fail.
- HTTP filter flow initializes servlet filters from prefixed configuration, classifies browser requests, enforces CSRF headers for browser-like clients and non-ignored methods, or injects X-Frame-Options before delegating through the filter chain.
- Token flow constructs identifiers and passwords through `SecretManager`, stores token bytes/kind/service in `Token`, decodes identifiers for consumers, and uses retriable password retrieval to signal invalid, standby, or temporary server-side token validation failures.

## State and Persistence Behavior

The JDiff file itself is persisted API metadata for compatibility checking. It does not store Hadoop runtime state.

Serializer classes are mostly stateless factories, but they consume `Configuration` through `Configured`. The durable compatibility concern is serialized data format: Java serialization, Avro schema/key use, and Writable byte layout must remain readable by corresponding deserializers.

Metrics APIs split state into mutable and immutable layers. `MetricsInfo`, `MetricsTag`, `AbstractMetric`, and `MetricsRecord` are immutable snapshots. `MutableMetric` subclasses hold process-local counters, gauges, sample statistics, quantile estimators, per-thread rate accumulators, rolling windows, change flags, and previous snapshots. `MetricsRegistry` stores the named collection of mutable metrics and tags. `DefaultMetricsSystem` is a process singleton and has mini-cluster mode state.

Metrics sinks persist or transmit data externally. File and rolling filesystem sinks write durable metrics output; Graphite and StatsD sinks send metrics over network protocols. `MetricsCache` stores in-memory dense records for sinks that cannot process sparse updates. MBeans register process-local JMX objects under stable ObjectNames.

Network mapping state is in-memory cache plus external configuration or mapping files/scripts. `CachedDNSToSwitchMapping` stores host-to-rack results and exposes copies for diagnostics. `TableMapping` persists mapping data in the configured two-column file; `ScriptBasedMapping` depends on the configured script and cache invalidation.

Security state includes both in-memory identity state and durable credential material. `Credentials` stores token and secret-key maps, writes/reads token storage files and streams, and implements `Writable`. `CredentialProvider` implementations may be transient or durable; durable providers require `flush()` to persist changes. ACLs are serializable through `Writable`.

UGI maintains global static security configuration, login user state, metrics attachment, and per-instance JAAS subjects with principals, groups, token identifiers, tokens, credentials, and auth method markers. Kerberos login/relogin updates the subject's credentials in place. Keytab and ticket-cache paths appear in exception context and login flows but are not themselves persisted by UGI.

Token state visible in this chunk is byte arrays for identifier/password plus `Text` kind/service, with conversion to/from protobuf and `Writable` hooks continuing past the chunk boundary. `SecretManager` state is implementation-specific, but the contract requires secret keys and registries sufficient to create/retrieve passwords and detect expiry/revocation/standby availability.

## Dependencies and Integration Points

Key Java dependencies include `Serializable`, `Comparable`, collections, `Closeable`, `IOException`, `DataInput/DataOutput`, `DataInputStream/DataOutputStream`, `File`, `URI`, `InetAddress`, `Socket`, `SocketTimeoutException`, `UnknownHostException`, `Proxy`, `Calendar`, `PrintStream/PrintWriter`, JAAS `Subject`, privileged action interfaces, JMX `ObjectName`, servlet `Filter` APIs, and crypto `SecretKey`.

External library integrations include log4j `AppenderSkeleton` and `LoggingEvent`, SLF4J `Logger`, Apache Commons Configuration2 `SubsetConfiguration`, Avro specific/reflect serialization concepts, RE2/J `Pattern`, and servlet containers.

Hadoop integration points include `Configuration`, `Configured`, `Configurable`, `Writable`, `Text`, `Path`, `FileSystem`, `SecurityProtos.TokenProto`, `RemoteException`, `StandbyException`, `RetriableException`, `NetworkTopology`, `NetUtils`, `CommonConfigurationKeys`, `SaslRpcServer.AuthMethod`, `KerberosInfo`, `TokenInfo`, `TokenIdentifier`, token secret-manager subclasses, ZooKeeper auth utilities, and metrics annotation packages.

The empty package markers indicate API namespace presence but no public types in this line window for `org.apache.hadoop.ipc.protocolPB`, `org.apache.hadoop.log`, `org.apache.hadoop.metrics2.sink.ganglia`, `org.apache.hadoop.metrics2.source`, `org.apache.hadoop.net.unix`, `org.apache.hadoop.security.protocolPB`, and `org.apache.hadoop.security.ssl`.

## Risks and Edge Cases

- This chunk begins mid-class and ends mid-class. Complete reports for `tfile.Utils` and `Token` require adjacent chunks.
- JDiff omits method bodies. Exact JSON rendering, string escaping, socket proxy configuration keys, file formats, Kerberos timing policy, token byte-copy behavior, and synchronization internals need implementation-source validation.
- `JavaSerialization` is explicitly experimental and relies on Java serialization, which carries compatibility and security risks for untrusted streams.
- `JavaSerializationComparator` assumes deserialized objects implement compatible `Comparable` semantics; class mismatches or malicious serialized data can fail at runtime.
- Avro reflect package configuration is broad. Over-including packages may serialize unintended classes; under-including packages silently rejects classes unless they implement the marker.
- Metrics mutable classes mix synchronized and unsynchronized methods. Consumers should not assume all value reads are atomic or globally ordered unless the concrete implementation provides it.
- `MutableRates` warns about high contention. `MutableRatesWithAggregation` improves concurrency but can lose per-thread samples when short-lived threads die before collection.
- `MutableStat.add(numSamples, sum)` can preserve mean while degrading variance accuracy for large `numSamples`.
- Quantile and rolling-average metrics keep estimators/windows in memory; missing `stop()` or `close()` can leak scheduled work or buffers in long-running daemons.
- `publishMetricsNow()` is best effort and may return before every source/sink completes under time pressure.
- Rolling filesystem sinks expose multiple protected fields and depend on clock/roll interval math, append support, and filesystem behavior; rollover boundaries and error-ignore settings are likely failure points.
- Rack mapping requires one output per input. Returning null, wrong-sized lists, or malformed paths can break scheduler/topology assumptions.
- `AbstractDNSToSwitchMapping.isMappingSingleSwitch` documentation is internally surprising: it says mappings not derived from this class are assumed multi-switch, while the `@return` line says true if not derived. Implementation should be checked before relying on the text.
- Script-based mapping depends on external scripts and can fail due to missing executables, slow scripts, malformed output, or command injection if host inputs are not handled carefully.
- Table mapping returns `/default-rack` for misses, which can hide configuration drift by clustering unknown hosts together.
- Socket factories expose equality/hash behavior, which can affect connection-pool reuse; SOCKS proxy configuration must be included consistently.
- `Credentials` stores secret keys and token passwords in memory as byte arrays. Returned arrays may expose mutable secret material depending on implementation.
- Credential-provider implementations must be thread safe; factories using service loading and URI lists need deterministic error handling for unknown schemes or missing passwords.
- `AuthorizationException` intentionally hides stack traces, improving information hiding but reducing diagnostics.
- UGI has significant global static state. Tests that call `setConfiguration`, `setShouldRenewImmediatelyForTests`, login APIs, or mini-cluster metrics hooks can affect later tests in the same JVM.
- `doAsLoginUserOrFatal` can terminate the JVM if login user lookup fails; it is unsafe in libraries or tests unless failure is truly fatal.
- Kerberos relogin methods mutate the subject credentials and depend on keytab/ticket-cache availability and timing windows.
- HTTP CSRF browser detection is regex-based and user-agent controlled. Non-browser clients that look browser-like must send the header; browser user agents that do not match configured patterns may bypass enforcement.
- X-Frame-Options only addresses frame embedding; it does not replace broader content-security policies.
- `SecretManager.retriableRetrievePassword` broadens failure modes. Clients must distinguish invalid-token terminal failures from standby/retriable temporary failures.
- Base `Token.isPrivate()` and `isPrivateCloneOf()` are documented as false for non-private tokens; private clone behavior may depend on subclass or continuation beyond this chunk.

## Test Signals

Useful validation for this API surface should include:

- API compatibility checks ensuring all public classes, fields, constructors, overloads, checked exceptions, and deprecated markers in this JDiff slice remain present.
- Serialization tests for Java/Writable/Avro specific/Avro reflect selection, configured `io.serializations`, reflect package inclusion, marker-interface inclusion, schema key handling, comparator construction failures, and round-trip byte compatibility.
- Log metrics tests for `EventCounter` counting fatal/error/warn events, ignoring lower levels if intended, appender lifecycle, and layout requirement.
- Metrics core tests for immutable equality/hash/string behavior, builder chaining, context/tag/gauge/counter output, JSON/string rendering, visitor dispatch by metric type, record tag immutability, and source-to-sink collection through `MetricsSystem`.
- Metrics system lifecycle tests for source registration uniqueness, unregister behavior, callback registration, JMX start/stop, `currentConfig`, `publishMetricsNow` flushing, complete shutdown, and default singleton mini-cluster mode.
- Mutable metrics tests for changed-flag behavior, `all` snapshots, int/long counter increments, gauge increments/decrements/sets, registry lookup/tag override behavior, synchronized paths under concurrency, and duplicate metric/tag names.
- Statistical metric tests for quantile rollover and estimator replacement, `MutableStat` mean/min/max/stdev and variance degradation case, rate initialization from protocol classes, per-thread aggregation collection, rolling-average window eviction, `getStats(minSamples)`, and close/stop cleanup.
- Sink tests for file, Graphite, rolling filesystem, and StatsD initialization, record formatting, flush/close idempotence, connection failures, ignored versus fatal errors, rolling interval parsing, offset scheduling, append behavior, and filesystem injection for tests.
- MBeans and cache tests for ObjectName format parsing, duplicate registration/unregistration, sparse-to-dense cache updates, record eviction limits, and server specification parsing with default ports.
- Network tests for one-to-one rack mapping, empty input, unknown-host default rack, cache hits/misses/reloads, copied switch maps, topology dump content, script absent/present behavior, malformed script/table output, table reload, socket factory overloads, SOCKS proxy configuration, and equality/hash consistency.
- Security credentials tests for token/secret-key add/get/remove/count/map immutability, stream/file/Writable/protobuf round trips, overwrite versus non-overwrite merge semantics, malformed token storage, and secret byte defensive copying.
- Group/id mapping tests for nonexistent users returning empty groups, cache refresh/add behavior, unknown uid/gid handling, and IOException propagation.
- Kerberos/SecurityUtil/UGI tests for principal host substitution, keytab and ticket-cache login paths, subject-based UGI creation, current/login/proxy/remote/test users, token and credential attachment, group lookup failure behavior, auth method conversions, relogin and logout errors, `doAs` exception mapping, static configuration isolation, and debug logging.
- Credential-provider tests for service-loader provider discovery, URI scheme handling, transient versus persistent stores, missing-password warnings/errors, create duplicate alias failure, delete missing alias behavior, flush durability, and thread safety.
- Authorization tests for ACL parsing/rendering, wildcard semantics, user/group add/remove, serialization, suppressed stack traces, proxy superuser key generation, group/host allow and deny cases, string-address authorization compatibility, and remote address resolution avoidance.
- HTTP filter tests for prefixed configuration extraction, browser regex matching including null user agent, custom header enforcement, ignored HTTP methods, servlet chain continuation/rejection status, X-Frame-Options header value, and filter lifecycle.
- Token tests for HMAC password determinism with a fixed key, random secret generation shape, invalid/standby/retriable retrieval exceptions, read-availability checks, token constructor defensive copies, protobuf conversion, service mutation, identifier decoding failure paths, and private clone base behavior.

## Cross-Chunk Notes

The previous chunk is required to complete `org.apache.hadoop.io.file.tfile.Utils`; this one only includes `lowerBound`, `upperBound`, and the closing class/package docs. A later chunk is required to complete `org.apache.hadoop.security.token.Token`; this chunk stops at the opening of `readFields`.

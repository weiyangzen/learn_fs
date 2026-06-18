# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.4.xml lines 24454-30679

## Scope And Purpose

This chunk is part of Hadoop Common 3.2.4's JDiff API descriptor. It is generated XML that records the public/protected Java API surface, inheritance, visibility, synchronization flags, exceptions, fields, and Javadoc for a slice of Hadoop Common. It does not contain implementation bodies, so control flow and persistence behavior below are derived from the API contracts and comments visible in this chunk.

The slice starts at the end of `org.apache.hadoop.io.file.tfile.Utils` binary-search helpers, then covers serialization packages, Log4J event counting, the core `metrics2` API, metrics mutable registries and sinks, metrics/JMX utilities, network topology/socket factories, security credentials and Kerberos/UGI utilities, credential-provider APIs, authorization/proxy-user and servlet security filters, and the beginning of token secret management.

## Important APIs, Types, And Functions

- `org.apache.hadoop.io.file.tfile.Utils` ends with static `lowerBound` and `upperBound` overloads over `java.util.List`, with optional `java.util.Comparator`, used by TFile consumers to locate sorted-list insertion/search boundaries.
- `org.apache.hadoop.io.serializer` defines Hadoop serialization integration points: `JavaSerialization`, `JavaSerializationComparator`, and `WritableSerialization`. `WritableSerialization` delegates to `Writable.write(DataOutput)` and `Writable.readFields(DataInput)`, while `JavaSerializationComparator` deserializes Java-serialized objects and compares via `Comparable`.
- `org.apache.hadoop.io.serializer.avro` exposes `AvroSerialization`, `AvroSpecificSerialization`, `AvroReflectSerialization`, and marker interface `AvroReflectSerializable`. Key configuration fields include `AVRO_SCHEMA_KEY` and `AVRO_REFLECT_PACKAGES`.
- `org.apache.hadoop.log.metrics.EventCounter` is a Log4J `AppenderSkeleton` with `append`, `close`, and `requiresLayout`; its documented purpose is counting fatal, error, and warn events.
- `org.apache.hadoop.metrics2` provides the core metrics contracts: immutable `AbstractMetric`, `MetricsInfo`, `MetricsTag`, `MetricsRecord`, `MetricsCollector`, `MetricsRecordBuilder`, `MetricsVisitor`, `MetricsFilter`, `MetricsSource`, `MetricsSink`, `MetricsPlugin`, `MetricsSystem`, and `MetricsSystemMXBean`. Builders support tags, context, counters, and gauges across int/long/float/double variants.
- `MetricsJsonBuilder` and `MetricStringBuilder` are concrete `MetricsRecordBuilder` implementations for JSON and string dump representations. They collect tags/metrics and expose `toString()`.
- `DefaultMetricsSystem` is a singleton-style enum facade for initializing, accessing, shutting down, and setting mini-cluster mode on the default daemon metrics system.
- `Interns` creates interned `MetricsInfo` and `MetricsTag` instances.
- `MetricsRegistry` holds mutable metrics and tags for a metrics source. It creates counters, gauges, rates, stats, quantiles, rates-with-aggregation, and rolling averages, and snapshots all registered mutable metrics into a `MetricsRecordBuilder`.
- Mutable metrics include `MutableMetric`, `MutableCounter`, `MutableCounterInt`, `MutableCounterLong`, `MutableGauge`, `MutableGaugeInt`, `MutableGaugeLong`, `MutableQuantiles`, `MutableRate`, `MutableRates`, `MutableRatesWithAggregation`, `MutableRollingAverages`, and `MutableStat`.
- Metrics sinks in this chunk include `FileSink`, `GraphiteSink`, `RollingFileSystemSink`, and `StatsDSink`. Each implements `MetricsSink`; most also implement `Closeable`.
- `RollingFileSystemSink` is the most stateful sink here, with protected fields for `source`, `ignoreError`, `allowAppend`, `basePath`, roll intervals, next flush time, forced flush flags, and supplied test filesystem/configuration hooks.
- `MBeans` standardizes JMX object-name registration as `hadoop:service=<serviceName>,name=<nameName>` with optional properties. `MetricsCache` stores sparse metric updates for sinks that need complete records. `Servers.parse` turns comma/space separated host specs into `InetSocketAddress` values.
- `org.apache.hadoop.net` covers rack/topology mapping and socket factories: `DNSToSwitchMapping`, `AbstractDNSToSwitchMapping`, `CachedDNSToSwitchMapping`, `ScriptBasedMapping`, `TableMapping`, `ConnectTimeoutException`, `SocksSocketFactory`, and `StandardSocketFactory`.
- `Credentials` stores Hadoop tokens and secret keys in memory and supports `Writable` serialization, token-storage file/stream read/write, `addAll`, and `mergeAll`.
- `GroupMappingServiceProvider` and `IdMappingServiceProvider` are pluggable OS/security mapping interfaces for users to groups and numeric IDs.
- `KerberosAuthException` enriches unrecoverable Kerberos login failures with user, principal, keytab, and ticket-cache context.
- `SecurityUtil` centralizes Kerberos principal expansion, login from configuration, token service construction, token-service decoding, `doAs` helpers, authentication-method configuration, privileged-port checks, and ZooKeeper auth loading.
- `UserGroupInformation` wraps a JAAS `Subject` and exposes static process-wide security initialization, current/login user discovery, keytab/ticket-cache login and relogin, remote/proxy/test user construction, token/credential attachment, group lookup, authentication-method handling, and `doAs` execution.
- `UserGroupInformation.AuthenticationMethod` maps UGI auth methods to `SaslRpcServer.AuthMethod`.
- `CredentialProvider` and `CredentialProviderFactory` define thread-safe password/credential storage abstraction, persistent `flush`, alias enumeration, create/delete operations, password-needed warnings/errors, and provider discovery through configured URI paths.
- `AccessControlList`, `AuthorizationException`, `DefaultImpersonationProvider`, and `ImpersonationProvider` cover ACL parsing/serialization and proxy-user authorization against configured groups/users/hosts.
- `RestCsrfPreventionFilter` and `XFrameOptionsFilter` are servlet filters for REST CSRF and clickjacking protection. Both expose static `getFilterParams(Configuration, prefix)` helpers for translating Hadoop configuration prefixes into filter init parameters.
- `SecretManager<T>` and the start of `Token<T>` define delegation-token password creation/retrieval, standby/retriable read paths, HMAC password generation, secret-key conversion, token construction from identifiers/components/protobuf, token copy, token protobuf conversion, identifier decode, and accessors for identifier/password/kind/service.

## Control Flow And Lifecycle

The metrics path is a publish/collect/sink pipeline. A daemon initializes `DefaultMetricsSystem`, registers `MetricsSource` instances with `MetricsSystem.register`, and sources populate records through `MetricsCollector.addRecord`. `MetricsRegistry` simplifies source implementations by owning mutable metrics and tags; source code mutates counters/gauges/stats over time, then `snapshot(builder, all)` emits changed or all values to a `MetricsRecordBuilder`. Sinks receive `MetricsRecord` objects via `putMetrics`, then flush/close according to their implementation.

Mutable metrics distinguish change tracking from collection. `MutableMetric.snapshot(builder)` emits only changed metrics, while `snapshot(builder, all)` can force unchanged values too. Counters are monotonic increments, gauges can increment/decrement/set, stats collect sample counts/sums and optionally extended statistics, quantiles maintain online estimates over periodic rollover intervals, and rolling averages keep sliding-window aggregate state.

`MutableRatesWithAggregation` changes the rate-update flow for high-contention scenarios: each long-running thread keeps local rate counts, and `snapshot` aggregates thread-local state into a global rate. The Javadoc explicitly warns that values produced after the last snapshot and before thread death can be lost, which is a lifecycle risk for short-lived threads.

`RollingFileSystemSink` rolls output directories/files on a schedule. `init` reads metrics2 properties, `setInitialFlushTime` picks an initial roll time with a random offset, `updateFlushTime` advances to the next interval preserving that offset, and `putMetrics`/`flush`/`close` write metrics through Hadoop `FileSystem`. It can append where supported or create sequence-suffixed files; secure deployments require configured keytab and principal keys.

Network topology resolution flows through `DNSToSwitchMapping.resolve(List)`, returning a one-to-one list of rack paths. `CachedDNSToSwitchMapping` delegates misses to a raw mapping and stores host-to-rack results until `reloadCachedMappings` clears all or selected entries. `ScriptBasedMapping` wraps a raw script-based resolver configured from `net.topology.script.file.name`; `TableMapping` reads a two-column mapping file configured by `net.topology.table.file.name`.

Security flows center on static UGI process state and per-user `Subject` state. `UserGroupInformation.setConfiguration` initializes authentication mode and group lookup. `getCurrentUser` returns the current subject, including nested `doAs` scopes. Keytab and ticket-cache login methods create or refresh login credentials; relogin methods update the UGI subject. `doAs` executes privileged actions as a selected UGI and propagates checked or unchecked failures per method contract.

Delegation token flow starts with a token identifier and `SecretManager`. `SecretManager.createPassword(T)` creates token passwords for issued identifiers; `retrievePassword(T)` validates tokens, including expiry/revocation checks supplied by subclasses. `retriableRetrievePassword` can signal standby or temporary retriable failure so clients can fail over or retry. `Token` stores identifier bytes, password, kind, and service, can be serialized as Writable/protobuf, and can decode its identifier through token kind metadata.

Proxy-user authorization flows through `ImpersonationProvider.init(prefix)`, then `authorize(proxyUgi, remoteAddress)`. `DefaultImpersonationProvider` derives configuration keys for allowed effective users, groups, and IPs for a real superuser and throws `AuthorizationException` on denial. The exception suppresses stack traces for security.

HTTP filter flow is standard servlet lifecycle: `init` consumes filter params, `doFilter` applies policy, and `destroy` releases state. `RestCsrfPreventionFilter.handleHttpInteraction` enforces a configurable header for browser-originating requests, while `isBrowser` defaults to user-agent regex matching. `XFrameOptionsFilter` injects the configured frame-options response header before continuing the chain.

## State And Persistence Behavior

The JDiff file itself is static generated metadata. The APIs it describes manage several important state surfaces:

- Metrics state is held in mutable metric objects, `MetricsRegistry` maps, tags, and singleton `DefaultMetricsSystem` process state. Snapshot behavior clears or observes changed flags depending on implementation.
- `MetricsCache` persists sparse metric updates only in memory for sink-side reconstruction of complete records.
- `RollingFileSystemSink` persists metrics records to a Hadoop `FileSystem` under a time-rolled base path. It may append to existing files or create new numbered files, and has explicit error-handling behavior controlled by `ignore-error`.
- `Credentials` persists tokens and secret keys through Hadoop Writable/token-storage file formats and maintains in-memory alias maps for tokens and secret keys.
- `CredentialProvider` implementations are required to be thread safe and may represent persistent stores or transient stores. `flush()` is the contract for writing changes to backing storage.
- UGI maintains static process configuration/login state and per-UGI subject credentials. The `HADOOP_TOKEN_FILE_LOCATION` environment variable points to a token cache file.
- ACLs are `Writable` and can round-trip through `write/readFields`; they also expose a canonical `getAclString()` for configuration persistence.
- Secret-manager implementations own server-side token key/registry state outside this XML chunk; the exposed contract requires validation of expiry and revocation during password retrieval.

## Dependencies And Integration Points

This chunk ties Hadoop Common to Java core libraries (`java.io`, `java.net`, `java.security`, `javax.crypto`, `javax.management`, `javax.security.auth`, servlet APIs), Hadoop contracts (`Configuration`, `Configured`, `Writable`, `Text`, `Path`, `FileSystem`, IPC exceptions, SASL auth methods, token identifiers, security protobufs), Apache Commons Configuration `SubsetConfiguration`, Avro serialization, Log4J, SLF4J, RE2/J patterns, and JMX.

Metrics integration is broad: daemon code registers sources in `DefaultMetricsSystem`, sources use annotations/registries/builders, and sinks integrate with files, Graphite, StatsD, and JMX consumers. Configuration is through `hadoop-metrics2.properties`-style prefixes and sink properties.

Network integration affects HDFS block placement and rack awareness. The `isSingleSwitch` predicate is explicitly used by policies that behave differently on single-rack versus multi-rack systems.

Security integration spans Kerberos principal substitution, keytabs, ticket caches, token service strings, ZooKeeper ACL auth files, JAAS Subjects, RPC remote/proxy users, servlet filters, and credential provider service loading. Misconfiguration in these integration points can surface as authentication failures, authorization denials, or silently ineffective protection.

## Risks And Edge Cases

- Because this is JDiff metadata, method bodies and actual invariants are not visible. Research consumers should verify implementation details in the corresponding `.java` sources before changing behavior.
- Serialization APIs are compatibility-sensitive. Changing `WritableSerialization`, `Credentials`, `Token`, or ACL Writable formats would affect persisted token files and wire compatibility.
- `JavaSerialization` is documented as experimental; using Java object serialization can carry performance, compatibility, and security concerns.
- Metrics naming/tagging APIs are public contracts. Duplicate metric or tag names, incorrect context tags, or misuse of `all=false` snapshots can make metrics disappear or become misleading.
- `MutableRates` is documented as synchronized and unsuitable for high contention. `MutableRatesWithAggregation` improves concurrency but can lose samples from short-lived threads.
- `MutableStat.add(numSamples, sum)` warns that large `numSamples` can produce inaccurate variance due to one-step Welford variance calculation.
- `RollingFileSystemSink` has operational pitfalls: default base path may resolve to `/tmp` on the default filesystem, append support varies by filesystem, HDFS append requires enough DataNodes, HDFS file size may not update until close, and simultaneous cluster-wide rolls can overload HDFS unless roll offset is configured.
- Rack mapping must preserve one-to-one input/output ordering. Unknown hosts should map to default rack in bundled implementations; bad scripts or stale table files can degrade placement locality.
- `AbstractDNSToSwitchMapping` intentionally avoids extending `Configured` because constructor-time `setConf` dispatch can call subclass methods before construction completes.
- `SecurityUtil.doAsLoginUserOrFatal` can terminate the JVM if login user cannot be determined.
- Kerberos login/relogin depends on correct hostname substitution, reverse DNS, keytab path, principal, and ticket-cache state. `KerberosAuthException` is marked unrecoverable and callers should not retry it blindly.
- `AccessControlList.isUserInList` has special behavior for proxied users and `USE_REAL_ACLS`; ACL reviews need to consider both effective and real users.
- `AuthorizationException` intentionally hides stack traces, which is good for security but can reduce diagnosability in tests/logs.
- CSRF protection depends on browser user-agent detection and required custom headers. Non-browser clients may bypass header enforcement by design; user-agent regex changes are security-sensitive.
- `CredentialProvider.needsPassword` and clear-text fallback behavior require careful error handling so callers do not silently fall back to insecure or unavailable credentials.
- `Token.decodeIdentifier` may return null if the identifier class is unavailable and may throw runtime exceptions if instantiation fails; callers must handle both.
- `SecretManager.retriableRetrievePassword` explicitly adds standby/retry exceptions to the authentication path; clients and tests must preserve failover semantics.

## Test Signals

Useful validation signals for this API slice include:

- JDiff/API compatibility tests ensuring public classes, methods, fields, visibility, synchronization, and exceptions remain stable across Hadoop Common releases.
- Serialization round-trip tests for `WritableSerialization`, Avro specific/reflect serializations, `Credentials`, `Token`, and `AccessControlList`.
- Metrics tests that register sources, mutate counters/gauges/stats/quantiles/rates, snapshot with `all=true/false`, validate JSON/string builders, and confirm MBean registration names.
- Concurrency tests for `MetricsRegistry`, mutable metric updates, `MutableRatesWithAggregation`, `MutableRollingAverages.collectThreadLocalStates`, and thread-safe `CredentialProvider` implementations.
- Sink integration tests for `FileSink`, `GraphiteSink`, `StatsDSink`, and especially `RollingFileSystemSink` across local FS/HDFS, append/no-append, roll interval parsing, random roll offset, secure keytab/principal configuration, and error-ignore behavior.
- Rack mapping tests for empty input, unresolved hosts, cache reload, script absence/failure, table-file reload, one-to-one output ordering, and single-switch predicates.
- Socket factory tests for standard and SOCKS proxy socket creation, equality/hashCode, and configuration loading.
- Security tests for UGI initialization, current/login/proxy/test users, keytab/ticket-cache login and relogin, token/credential attachment, `doAs` exception propagation, auth-method mapping, and `HADOOP_TOKEN_FILE_LOCATION` loading.
- Authorization tests for wildcard ACLs, user/group add/remove, proxied real-user ACL behavior, Writable round trips, hidden stack traces, and proxy-user group/host config enforcement.
- Servlet filter tests for CSRF browser detection, custom header/method-ignore configuration, bad-request rejection, config-prefix parameter extraction, and X-Frame-Options header insertion.
- Token/secret-manager tests for password HMAC generation, secret-key conversion, invalid/expired/revoked token handling, standby/retriable failure propagation, protobuf conversion, and identifier decode failure handling.

## Unresolved Cross-Chunk References

The chunk begins mid-class after earlier `Utils` methods and ends mid-`Token` class at `getService`; additional token mutators, Writable methods, equality/string helpers, token renewer/canceler classes, and token identifier classes likely appear in later lines. Some metrics types referenced here, such as `MutableGaugeFloat`, `MetricType`, concrete metric implementations, `AbstractPatternFilter`, quantile utility classes, and nested helper records, are outside the visible range. The source Java implementation files should be used by the merge lane to reconcile exact implementation details.

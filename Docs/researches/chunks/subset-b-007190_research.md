# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.1.2.xml lines 24253-30507

## Scope

This chunk is part 5 of 6 for the Apache Hadoop Common 3.1.2 JDiff API snapshot. It starts inside the tail of `org.apache.hadoop.io.compress.SplitCompressionInputStream`, covers the full public API records for erasure-code schema, TFile helpers, serializers, metrics, network-topology mapping, core security identity/credential utilities, and ends at the start of `org.apache.hadoop.security.authorize.ImpersonationProvider`.

The source is generated JDiff XML rather than implementation code. Its research value is the compatibility surface: public/protected type names, inheritance, implemented interfaces, method signatures, checked exceptions, static/final/abstract/synchronized flags, deprecation markers, public fields, and embedded Javadocs. Runtime control flow below is inferred from those contracts and must be reconciled with Java implementation sources before changing behavior.

## Purpose

The compression tail documents split-aware compressed-input contracts. `SplitCompressionInputStream` exposes adjusted start/end offsets after a codec aligns a requested byte range, and `SplittableCompressionCodec` lets codecs create positioned decompression streams for parallel reads of compressed data.

`org.apache.hadoop.io.erasurecode.ECSchema` records erasure-code schema metadata: codec name, data-unit count, parity-unit count, and extra codec-specific options. The empty `coder.util` and `grouper` package elements indicate package presence but no public types in this line range.

`org.apache.hadoop.io.file.tfile` exposes the public TFile container surface. TFile is a byte-oriented key/value container with block compression, named metadata blocks, sorted or unsorted keys, key/file-offset seeking, compression/comparator constants, binary-search utilities, variable-length integer/string encoding helpers, and meta-block exception types.

The serializer packages expose Hadoop serialization implementations and Avro integration markers. `JavaSerialization`, `WritableSerialization`, `AvroSerialization`, `AvroReflectSerialization`, and `AvroSpecificSerialization` are API entries for plugging Java, Writable, and Avro formats into Hadoop's `Serialization` framework.

The metrics packages are the largest part of the chunk. They define immutable metric/tag metadata, collector/record/builder/source/sink/plugin/system contracts, mutable counters/gauges/stats/rates/quantiles, annotation markers, filters, singleton system accessors, sink implementations, JMX helpers, metrics caches, and address parsing helpers.

The network package documents rack/topology mapping and socket factory contracts. It includes configurable DNS-to-switch mapping abstractions, cached/script/table implementations, a connect-timeout exception, and standard/SOCKS socket factories.

The security packages define access-control exceptions, in-memory and serialized credentials, group/id mapping provider interfaces, Kerberos authentication exception context, security utility helpers, `UserGroupInformation`, credential-provider abstractions, and the opening authorization APIs for ACLs, authorization exceptions, and proxy-user impersonation.

## Important APIs, Types, and Functions

### Compression and Erasure Coding

- `SplitCompressionInputStream.getAdjustedStart()` and `getAdjustedEnd()` return codec-adjusted compressed-range offsets after stream creation.
- `SplittableCompressionCodec` extends `CompressionCodec` and adds `createInputStream(InputStream seekableIn, Decompressor decompressor, long start, long end, READ_MODE readMode) throws IOException`, returning a `SplitCompressionInputStream`.
- `SplittableCompressionCodec.READ_MODE` is referenced as the read-position reporting mode; the enum body is outside this chunk.
- `ECSchema` is final and `Serializable`. Constructors accept either an all-options `Map`, `(String codecName, int numDataUnits, int numParityUnits)`, or those key parameters plus extra options.
- `ECSchema` getters expose `getCodecName()`, `getExtraOptions()`, `getNumDataUnits()`, and `getNumParityUnits()`, with `toString()`, `equals(Object)`, and `hashCode()` for logging and value semantics.
- Public schema keys are `NUM_DATA_UNITS_KEY`, `NUM_PARITY_UNITS_KEY`, and `CODEC_NAME_KEY`.

### TFile and Serialization

- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are `IOException` subclasses for named TFile metadata block operations.
- `RawComparable` exposes `buffer()`, `offset()`, and `size()` so external `RawComparator` instances can compare a byte range without copying.
- `TFile` exposes compression constants `COMPRESSION_GZ`, `COMPRESSION_LZO`, `COMPRESSION_NONE` and comparator constants `COMPARATOR_MEMCMP`, `COMPARATOR_JCLASS`.
- `TFile.makeComparator(String)` builds a raw comparator from a configured comparator name; `getSupportedCompressionAlgorithms()` returns writer-accepted compression names; `main(String[])` dumps TFile information for paths.
- `TFile` Javadocs define the container contract: type-less byte keys/values, 64KB key limit, block compression, named metadata blocks, sorted/unsorted modes, seek by key or offset, configurable chunk and filesystem buffer sizes, and performance tradeoffs around block size, compression, and buffering.
- `Utils` writes and reads variable-length ints/longs and Text-format strings through `writeVInt`, `writeVLong`, `readVInt`, `readVLong`, `writeString`, and `readString`.
- `Utils.lowerBound`/`upperBound` overloads implement binary-search boundary lookups over `List` values with either natural comparison or a supplied `Comparator`.
- `JavaSerialization` and `WritableSerialization` implement `Serialization`; `WritableSerialization` delegates to `Writable.write`/`readFields`.
- `JavaSerializationComparator` provides a comparator path for Java-serialized objects.
- `AvroReflectSerializable` is a marker interface; `AvroReflectSerialization` is configured by `AVRO_REFLECT_PACKAGES`; `AvroSerialization` implements `Serialization` and carries `AVRO_SCHEMA_KEY`; `AvroSpecificSerialization` handles Avro specific records.

### Metrics Core

- `EventCounter` is a Log4J appender that counts logging events at fatal/error/warn/info levels via `append`, `close`, and `requiresLayout`.
- `AbstractMetric` implements `MetricsInfo` and exposes immutable metric metadata and value through `name`, `description`, `info`, `value`, `type`, `visit`, equality, hash, and string rendering.
- `MetricsCollector` creates `MetricsRecordBuilder` instances by record name or `MetricsInfo`.
- `MetricsRecordBuilder` is the fluent mutable assembly surface for metrics records: `tag`, `add`, `setContext`, `addCounter`, `addGauge`, `parent`, and `endRecord`.
- `MetricsRecord` is the immutable snapshot surface: `timestamp`, `name`, `description`, `context`, `tags`, and `metrics`.
- `MetricsSource.getMetrics(MetricsCollector, boolean all)` emits updated metrics; `MetricsSink.putMetrics(MetricsRecord)` and `flush()` consume them; `MetricsPlugin.init(SubsetConfiguration)` initializes plugins.
- `MetricsSystem` registers/unregisters sources, registers JMX callbacks, publishes metrics immediately, and shuts down. `MetricsSystemMXBean` exposes start/stop of the system and MBeans plus `currentConfig()`.
- `MetricsJsonBuilder` and `MetricStringBuilder` implement `MetricsRecordBuilder`-style output builders for JSON/string dumps.
- `MetricsFilter` accepts/rejects metric names, tags, tag collections, and records. `GlobFilter` and `RegexFilter` compile filters to `com.google.re2j.Pattern`.
- `MetricsInfo` supplies immutable name/description metadata; `MetricsTag` implements `MetricsInfo` and adds a tag value.
- `MetricsVisitor` receives typed gauge and counter callbacks for int, long, float, and double metrics.
- Annotation types `Metric` and `Metrics` mark individual metric members and grouped metric sources.

### Metrics Library and Sinks

- `DefaultMetricsSystem` is the singleton enum facade for daemon metrics systems: `initialize`, `instance`, `shutdown`, `setMiniClusterMode`, and `inMiniClusterMode`.
- `Interns.info` and `Interns.tag` create interned `MetricsInfo` and `MetricsTag` objects to reduce repeated metadata allocation.
- `MetricsRegistry` creates and tracks mutable metrics and tags. It has constructors by record name or `MetricsInfo`, lookup methods `get`/`getTag`, factories for counters, gauges, quantiles, stats, rates, aggregate rates, and rolling averages, plus `add`, `setContext`, `tag`, and `snapshot`.
- `MutableMetric` defines changed-state-aware snapshot behavior through `snapshot(builder, all)`, `snapshot(builder)`, `setChanged`, `clearChanged`, and `changed`.
- `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong` expose monotonic incrementing counters with typed `value()` and `snapshot`.
- `MutableGauge`, `MutableGaugeInt`, and `MutableGaugeLong` expose increment/decrement/set gauges with typed `value()`, `snapshot`, and string rendering.
- `MutableQuantiles` maintains online quantile estimates over a rolling interval, with `add`, `snapshot`, `getInterval`, `stop`, `getEstimator`, `setEstimator`, and exposed `quantiles`/`previousSnapshot` fields.
- `MutableStat` accumulates sample statistics, supports extended statistics toggling, adding counts/sums or samples, `lastStat`, `resetMinMax`, and snapshotting.
- `MutableRate`, `MutableRates`, `MutableRatesWithAggregation`, and `MutableRollingAverages` provide throughput/rate and rolling-average helpers, including protocol-method initialization, per-name sample addition, thread-local state collection, closing, and stats retrieval.
- `FileSink`, `GraphiteSink`, `StatsDSink`, and `RollingFileSystemSink` implement configured metrics output. Rolling HDFS/file-system sink state includes source, ignore/append flags, base path, roll and offset intervals, next flush time, force/has-flushed flags, supplied configuration, and supplied filesystem.
- `MBeans` registers/unregisters standard Hadoop MBeans and can extract service/name components from an MBean name.
- `MetricsCache` updates and retrieves cached sparse metrics records for sinks that need complete records.
- `Servers.parse(String, int)` parses comma/space-separated host specifications into `InetSocketAddress` values.

### Network

- `AbstractDNSToSwitchMapping` implements `Configurable` support for topology mappers and provides `isSingleSwitch`, `getSwitchMap`, `dumpTopology`, `isSingleSwitchByScriptPolicy`, and static `isMappingSingleSwitch`.
- `DNSToSwitchMapping` defines `resolve(List<String>)`, `reloadCachedMappings()`, and `reloadCachedMappings(List<String>)` for pluggable host-to-rack mapping.
- `CachedDNSToSwitchMapping` wraps a raw mapping, caches host-to-switch results, exposes `rawMapping`, and supports targeted/full cache reload.
- `ScriptBasedMapping` uses configured scripts for host topology resolution and exposes `NO_SCRIPT`; constructors accept default config, raw mapping, or `Configuration`.
- `TableMapping` provides table-backed mapping configuration and cache reload.
- `SocksSocketFactory` and `StandardSocketFactory` provide multiple `createSocket` overloads plus equality/hash behavior; the SOCKS variant also implements `Configurable`.
- `ConnectTimeoutException` is thrown by NetUtils connection paths on connect timeout.

### Security and Credentials

- `AccessControlException` is the base access-control exception with default, message, and cause constructors.
- `Credentials` stores tokens and secret keys in memory and serializes token-storage files/streams. Important methods include token lookup/add/list/count, secret-key lookup/add/remove/list/count, static `readTokenStorageFile` overloads, `readTokenStorageStream`, `writeTokenStorageToStream` overloads, `writeTokenStorageFile` overloads, `write`, `readFields`, `addAll`, and `mergeAll`.
- `GroupMappingServiceProvider` maps users to groups and supports cache refresh/addition. It exposes `GROUP_MAPPING_CONFIG_PREFIX`.
- `IdMappingServiceProvider` maps UID/GID to names and back, including allowing-unknown variants for UID/GID lookup.
- `KerberosAuthException` records context for unrecoverable UGI failures: user, principal, keytab file, ticket cache file, initial message, and contextual `getMessage`.
- `SecurityUtil` configures security behavior and provides helpers for Kerberos principals, logins, delegation-token service names, Kerberos/TokenInfo annotation lookup, token service encode/decode, privileged-port checks, ZK auth extraction, and `doAsLoginUser`/`doAsCurrentUser` execution helpers.
- `UserGroupInformation` is the central identity object. Static APIs configure UGI, determine security status, get current/login users, select the best UGI from ticket cache/user, create UGIs from ticket caches or subjects, login/logout/relogin from keytab or ticket cache, create remote/proxy/testing users, and reattach metrics.
- UGI instance APIs expose real/effective user relationships, short/full user names, primary/group names, token identifiers, tokens, credentials, authentication methods, the underlying JAAS `Subject`, equality/hash, string rendering, debug logging, and `doAs` execution for `PrivilegedAction`/`PrivilegedExceptionAction`.
- `UserGroupInformation.AuthenticationMethod` enumerates authentication methods and maps to/from `SaslRpcServer.AuthMethod`.
- `CredentialProvider` is a thread-safe credential-store abstraction. It exposes transient-store detection, `flush`, credential lookup/list/create/delete, password-needed checks, no-password warning/error text, and `CLEAR_TEXT_FALLBACK`.
- `CredentialProviderFactory` creates providers from configured URI paths via service loading. `CREDENTIAL_PROVIDER_PATH` is the configuration key; `getProviders(Configuration)` returns the provider list.

### Authorization

- `AccessControlList` implements `Writable`, can be built from a combined ACL string or separate user/group strings, and supports wildcard ACLs through `WILDCARD_ACL_VALUE`.
- ACL methods include `isAllAllowed`, user/group add/remove, immutable user/group collection accessors, `isUserInList`, `isUserAllowed`, descriptive `toString`, exact `getAclString`, and `write`/`readFields`.
- `AuthorizationException` extends `AccessControlException` and deliberately suppresses stack trace access/printing for security-sensitive authorization failures.
- `DefaultImpersonationProvider` implements `ImpersonationProvider`, has a synchronized test-provider getter, accepts configuration, initializes with a proxy-user configuration prefix, authorizes a real user and remote address, generates proxy-user config keys, and exposes proxy group/host maps.
- This chunk stops at the opening of `ImpersonationProvider`; its method details continue in the next chunk.

## Control Flow

The XML has no executable flow, but the APIs imply these runtime paths:

- Split-compression readers call the codec-specific `createInputStream` with a seekable compressed stream and requested range. The codec may adjust start/end to compression block boundaries; callers then read the adjusted range from `SplitCompressionInputStream`.
- TFile writes group key/value data into compressed blocks and optional named metadata blocks, while readers load indexes and seek by key or file offset. Utility encoding methods serialize primitive/string metadata to `DataOutput` and recover it from `DataInput`.
- Serializer selection is framework-driven: Hadoop asks configured `Serialization` implementations whether they accept a class, then uses the serializer/deserializer provided by Java, Writable, Avro reflect, or Avro specific implementations.
- Metrics sources register with a `MetricsSystem`; sources fill `MetricsRecordBuilder` instances when polled, mutable metrics snapshot changed values into builders, filters can accept/reject names/tags/records, and sinks publish records to files, Graphite, StatsD, rolling filesystem paths, JSON, strings, JMX, or caches.
- Mutable metrics generally mutate local counters/gauges/stats on application events, mark themselves changed, and clear that changed flag during snapshot unless a full snapshot is requested.
- Rolling metrics and quantiles accept stream samples over time, maintain in-memory estimators/windows, and publish snapshots periodically or when requested.
- Network topology resolution flows from host lists to configured `DNSToSwitchMapping` implementations. Cached wrappers first return stored mappings, miss through to raw/script/table providers, and can be invalidated globally or for selected hosts.
- Security setup flows through `UserGroupInformation.setConfiguration` and `SecurityUtil.setConfiguration`, then identities are created from the current subject, Kerberos keytabs, ticket caches, remote usernames, or proxy relationships. `doAs` runs work under the selected subject.
- Token and secret-key flows use `Credentials` as the in-memory carrier and `writeTokenStorage*`/`readTokenStorage*` for persistence through streams or files.
- Credential providers are discovered from URI paths in configuration, created through factory service loading, mutated via create/delete, and committed to backing stores only when `flush()` succeeds.
- Authorization flows parse ACL strings into user/group sets or wildcard state, then test `UserGroupInformation` users/groups. Proxy authorization uses `DefaultImpersonationProvider` configuration maps of allowed effective users/groups and remote hosts.

## State and Persistence Behavior

This JDiff file persists API metadata for release compatibility checks. It does not store Hadoop runtime data.

`ECSchema` is value-like schema metadata. Its durable relevance is in configuration and serialized consumers that rely on the public option-key strings and equality/hash behavior.

TFile state is durable file content: data blocks, compressed block indexes, metadata block indexes, comparator/compression names, value chunking, and encoded primitive/string metadata. Public constants and variable-length encodings are compatibility-sensitive because existing TFiles and clients depend on them.

Metrics state is mostly in-memory and process-local. Immutable records/tags/metrics are snapshots; mutable counters/gauges/stats/rates/quantiles hold live process measurements; registries own metric instances and tags; `DefaultMetricsSystem` owns singleton lifecycle state; caches retain recent records for sparse sinks. Sinks persist or transmit metrics to files, filesystems, Graphite, StatsD, JMX, or logs depending on configuration.

Network mapping state is configuration plus optional caches. `CachedDNSToSwitchMapping` stores host-to-rack results in memory; script/table providers depend on external script or table configuration; reload calls invalidate or refresh cached mappings.

Security state includes in-memory JAAS subjects, authentication methods, token identifiers, delegation tokens, credentials, Kerberos login context, ticket/keytab paths, and group/id mapping caches. `Credentials` has explicit Writable/token-storage persistence through `DataInput`, `DataOutput`, streams, and files.

Credential-provider state may be transient or backed by persistent stores. `isTransient()` distinguishes non-durable stores; `flush()` is the durability boundary for persisted credential mutations. Password-needed methods report whether provider access is blocked by missing password material.

Authorization ACLs are serializable through `Writable` and preserve user/group/wildcard state. `AuthorizationException` suppresses stack traces as part of its externally visible security behavior.

## Dependencies and Integration Points

- Java dependencies include `InputStream`, `IOException`, `DataInput`, `DataOutput`, `DataInputStream`, `File`, `PrintStream`, `Comparator`, collections, `InetSocketAddress`, `Socket`, `Proxy`, `SocketFactory`, JAAS `Subject`, privileged actions, JMX `ObjectName`, and primitive arrays.
- Hadoop dependencies include `CompressionCodec`, `Decompressor`, `Configuration`, `Configurable`, `Writable`, `RawComparator`, `Text`, `Path`, `FileSystem`, token classes, Kerberos/Token annotation classes, SASL RPC auth methods, `UserGroupInformation`, and `SubsetConfiguration`.
- Metrics integrates with Log4J (`EventCounter`), SLF4J logger fields, Apache Commons Configuration for plugin init, RE2/J pattern compilation for filters, JMX MBean registration, and external metrics systems such as Graphite and StatsD.
- TFile integrates with Hadoop filesystem streams, Hadoop compression codecs, Text-compatible string encoding, raw comparators, and `Writable`-style serialization.
- Network mapping integrates with Hadoop configuration keys, external rack-resolution scripts or table files, and Java socket creation used by RPC/client layers.
- Security APIs integrate with Kerberos principals/keytabs/ticket caches, delegation-token service naming, ZooKeeper auth configuration, service-loaded credential providers, group mapping providers, id mapping providers, RPC impersonation, and Hadoop authorization checks.

## Risks and Edge Cases

- The chunk begins mid-class and ends mid-interface. Full reports must merge previous chunk data for `SplitCompressionInputStream` and next chunk data for `ImpersonationProvider`.
- JDiff omits implementation bodies. Thread safety, synchronization details, cache eviction, serialization wire layout, and error-message behavior require implementation-source validation.
- Split-compression correctness depends on codecs consistently adjusting start/end and reporting positions according to `READ_MODE`. Misaligned offsets can lose records or duplicate records in split processing.
- TFile public docs mention LZO support, comparator class loading, sorted/unsorted behavior, filesystem buffering, and block-size tuning; all can have performance or compatibility impact. Existing files depend on varint/string encodings and comparator/compression names.
- `RawComparable` exposes a mutable backing byte array plus offset/size. Callers must honor range boundaries and avoid mutating bytes while comparisons are in progress.
- Strong interning is not in this chunk, but metrics `Interns` performs object interning; high-cardinality metric names/tags can still cause memory retention.
- Mutable metrics can be lost or duplicated in snapshots if changed flags, full snapshots, and concurrent updates are mishandled. Rolling/quantile metrics have lifecycle risk if `stop()`/`close()` is not called.
- `DefaultMetricsSystem` singleton and mini-cluster mode are global process state. Tests must isolate initialization and shutdown to avoid cross-test contamination.
- File, rolling filesystem, Graphite, and StatsD sinks depend on external IO endpoints. `ignoreError`, append support, flush scheduling, and roll intervals are behaviorally important under failures.
- DNS-to-switch mapping can return nulls, stale caches, incomplete host lists, or single-switch defaults. Incorrect topology mapping degrades block placement and scheduler locality.
- Script-based topology mapping depends on external scripts and configuration; reload behavior must handle script changes and missing scripts cleanly.
- Socket factories must preserve equality/hash behavior because they may be used as configurable connection-factory keys.
- Security and credential APIs are high risk: token storage files contain sensitive material; credentials are mutable in memory; provider flush is the only persistence guarantee; missing passwords may force clear-text fallback depending on configuration.
- `Credentials.addAll` and `mergeAll` have different overwrite/merge semantics in implementation; callers need tests around alias collisions.
- Kerberos principal expansion with host substitution, ticket-cache/keytab relogin, and `doAs` execution are sensitive to configuration, DNS, clock skew, and exception propagation.
- `AuthorizationException` suppresses stack traces by contract; debugging tools should not assume stack details are available.
- ACL string parsing must handle wildcard, empty users/groups, whitespace, duplicate entries, and group resolution correctly. Proxy-user authorization must validate both user/group and remote host dimensions.

## Test Signals

- API compatibility checks should assert public classes, interfaces, fields, constructors, method signatures, checked exceptions, deprecation status, and partial-boundary merge correctness for this chunk.
- Split-compression tests should cover adjusted start/end reporting, read-mode behavior, block-boundary alignment, and split processing with compressed inputs.
- `ECSchema` tests should cover constructor variants, required option keys, extra options preservation, invalid/missing options if enforced by implementation, equality/hash consistency, serialization compatibility where used, and stable `toString`.
- TFile tests should cover compression constant acceptance, comparator creation, sorted and unsorted reads, named meta-block duplicate/missing errors, seek by key/offset, varint/string round trips, lower/upper-bound behavior, and compatibility with existing TFile fixtures.
- Serializer tests should cover Java, Writable, Avro reflect, and Avro specific class acceptance, schema-key configuration, round-trip serialization, and comparator behavior.
- Metrics tests should cover collector/builder fluent behavior, immutable record/tag/metric equality and rendering, visitor dispatch for all numeric types, filter accept/reject behavior, source registration, immediate publish, shutdown lifecycle, JMX callbacks, and MXBean config output.
- Mutable metrics tests should cover counter monotonicity, gauge set/incr/decr including negative values if allowed, changed-flag semantics, full versus changed-only snapshots, stat min/max/stddev behavior, rate aggregation, rolling-average state collection, quantile intervals, estimator replacement, and close/stop cleanup.
- Sink tests should cover file output, rolling interval/offset calculation, append/no-append behavior, flush scheduling, error handling, Graphite formatting, StatsD metric writing, cache updates, and server address parsing.
- Network tests should cover cache hits/misses/reloads, script/table configuration, single-switch detection, null or partial mapping responses, topology dump text, socket factory creation overloads, proxy configuration, and connection timeout exception handling.
- Security tests should cover credential token/secret-key add/get/remove/list/count, token-storage file and stream round trips, alias collision behavior for `addAll` and `mergeAll`, group/id mapping cache operations, Kerberos exception contextual messages, principal host substitution, token service encode/decode, ZK auth extraction, privileged-port checks, and doAs exception propagation.
- UGI tests should cover configuration initialization, current/login/best user selection, subject and ticket-cache creation, keytab login/logout/relogin, ticket-cache relogin, remote/proxy/testing user creation, real/effective user relationships, group lookup, authentication method mapping, token and credential attachment, equality/hash, and debug logging.
- Credential-provider tests should cover provider path parsing, service-loader factory selection, transient versus persistent providers, create/get/delete/list aliases, password-needed warning/error paths, clear-text fallback configuration, and flush durability.
- Authorization tests should cover ACL parsing from combined and split strings, wildcard behavior, user/group add/remove, immutable returned collections, Writable serialization, user membership checks against UGI groups, suppressed stack traces, proxy-user config-key generation, and authorize success/failure for user/group/host combinations.

## Cross-Chunk Notes

The previous chunk is needed for the complete `SplitCompressionInputStream` class declaration and constructor/mutator context. The next chunk is needed for the complete `ImpersonationProvider` interface and the remaining authorization/security APIs in this JDiff file. This chunk should be merged into the final per-file research document for `Apache_Hadoop_Common_3.1.2.xml` only after all six chunk documents are available.

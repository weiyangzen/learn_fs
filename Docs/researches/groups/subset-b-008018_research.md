# Research: subset-b-008018

Grouped research for Apache Ozone HDDS utility and RocksDB support files. Each section preserves the source path and is bounded by reconciliation markers for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/HAUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/HAUtils.java

## Purpose
`HAUtils` is a stateless helper class used by SCM and OM high-availability paths. It builds SCM protocol clients, reads transaction state from RocksDB checkpoints, replaces local DB directories with downloaded checkpoints, scans existing SST files for incremental snapshot transfer, and fetches SCM CA certificates in HA deployments.

## Important APIs and Types
The main client APIs are `getScmInfo`, `addSCM`, `getScmBlockClient`, and the three `getScmContainerClient` variants. DB/checkpoint APIs include `replaceDBWithCheckpoint`, `getTrxnInfoFromCheckpoint`, `getTransactionInfoTable`, `verifyTransactionInfo`, `getExistingFiles`, and `getExistingSstFilesRelativeToDbDir`. Certificate bootstrapping is handled by `buildCAX509List`, backed by `getCAListWithRetry` and `waitForCACerts`.

## Control Flow and State
SCM calls construct failover proxy providers and wrap translators with `TracingUtil`. `getScmInfo` adjusts retry count based on a configured wait duration before asking the block client for SCM info. Checkpoint installation first moves the old DB aside, creates a transient marker, copies the candidate checkpoint into the live DB path, then deletes the marker. On copy failure it deletes the partial live DB, moves the backup back, and terminates if rollback fails.

## Persistence, Dependencies, and Integration
The class depends on Ozone configuration keys, SCM proxy providers, Ratis retry utilities, Hadoop `FileUtil`, Ratis `FileUtils`, `DBStoreBuilder`, `DBDefinition`, and `TransactionInfo`. It integrates with HA bootstrapping, snapshot installation, OM/SCM metadata DB layouts, and SCM security certificate retrieval.

## Risks and Test Signals
`getTransactionInfoTable` assumes exactly one column family has `TransactionInfo` value type and calls `findFirst().get()`, so malformed DB definitions fail abruptly. `replaceDBWithCheckpoint` protects startup with `DB_TRANSIENT_MARKER`, but copy semantics mean partial directories must be cleaned reliably. CA-list retry intentionally fails fast on `AccessControlException`; tests should cover retry, auth-failure, leader checkpoint index regression, rollback failure, and SST path scanning for nested snapshot directories.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/HAUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/HddsServerUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/HddsServerUtil.java

## Purpose
`HddsServerUtil` is a broad server-side utility class for Ozone/HDDS daemons. It centralizes RPC protocol registration, SCM/Recon bind address resolution, heartbeat/dead-node timing validation, datanode storage directory handling, security/secret-key client creation, metrics initialization, DB checkpoint streaming, startup/shutdown logging, thread-pool resizing, and SCM address discovery.

## Important APIs and Types
Important methods include `addPBProtocol`, `getValidInetsForCurrentHost`, `isScopedOrMaskingIPv6Address`, `getScm*BindAddress`, `getReconDataNodeBindAddress`, heartbeat interval helpers, `getStaleNodeInterval`, `getDeadNodeInterval`, `getDatanodeStorageDirs`, `getDatanodeIdFilePath`, `getScmSecurityClient*`, `getSecretKeyClient*`, `initializeMetrics`, `writeDBCheckpointToStream`, `includeRatisSnapshotCompleteFlag`, `startupShutdownMessage`, `setPoolSize`, and `getSCMAddressForDatanodes`.

## Control Flow and State
Address helpers combine host and port config keys with defaults and return Hadoop `NetUtils` socket addresses. Timing helpers read durations and run them through `sanitizeUserArgs` to maintain minimum relationships between heartbeat, stale, and dead intervals. Checkpoint streaming lists the checkpoint directory, excludes requested filenames, tars each remaining file, and appends the Ratis completion flag. Startup logging also registers UNIX signal handlers and a shutdown hook.

## Persistence, Dependencies, and Integration
The class uses Hadoop RPC, Protobuf services, `DefaultMetricsSystem`, `JvmMetrics`, `CpuMetrics`, SCM HA node metadata, security failover providers, archive helpers, and `DBCheckpoint`. It is a key integration layer between server configuration, RPC endpoints, datanode/SCM/Recon discovery, certificate/secret-key services, and snapshot transfer.

## Risks and Test Signals
Network enumeration must not include loopback, wildcard, scoped IPv6, or prefix-length IPv6 addresses in certificate SANs. `getDatanodeStorageDirs` deliberately throws when required data dirs are absent, while DB dirs are optional. `setPoolSize` updates maximum/core pool sizes in different orders to preserve executor invariants. Tests should verify HA and legacy SCM address parsing, malformed host handling, checkpoint tar exclusion and completion flag inclusion, secret/security client UGI selection, and timing sanitation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/HddsServerUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/HttpServletUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/HttpServletUtils.java

## Purpose
`HttpServletUtils` provides shared servlet response helpers for Ozone HTTP endpoints. It chooses JSON/XML response formats from the `Accept` header, writes formatted error bodies, writes generic formatted content through a checked callback, and exposes a small `ResponseFormat` enum.

## Important APIs and Types
`getResponseFormat(HttpServletRequest)` returns `JSON`, `XML`, or `UNSPECIFIED`. `writeErrorResponse` sets status and emits either a JSON `{"error": ...}` object or secure XML `<error>` document. `writeResponse` sets content type and invokes a `CheckedConsumer<Writer>`, rethrowing caller-declared exception types. `ResponseFormat.getContentType` maps JSON/XML to UTF-8 media types.

## Control Flow and State
The class is stateless except for a memoized secure `DocumentBuilderFactory` supplier. XML error creation builds a DOM document and transforms it with Hadoop secure XML utilities. Format detection treats any accept header containing `json` as JSON and otherwise defaults to XML for compatibility.

## Persistence, Dependencies, and Integration
There is no persistence. Dependencies include servlet APIs, JAX-RS media/header constants, Ozone `JsonUtils`, Hadoop `XMLUtils`, and Ratis memoized checked suppliers. This class is intended for web UI and REST-like endpoint handlers that need consistent response formatting.

## Risks and Test Signals
`UNSPECIFIED` has no content type and is not supported by `writeErrorResponse`, so callers must normalize or handle unspecified formats before writing errors. Accept-header parsing is substring-based rather than full content negotiation. Tests should cover null/mixed accept headers, secure XML escaping, callback exception propagation, content types, and unsupported format behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/HttpServletUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/LogLevel.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/LogLevel.java

## Purpose
`LogLevel` implements Hadoop-compatible runtime log-level inspection and mutation over HTTP/HTTPS. It contains a CLI that sends authenticated requests to `/logLevel` and a servlet that renders a small admin UI and applies log4j level changes.

## Important APIs and Types
The top-level `main` delegates to `CLI`, an internal `Tool`. `CLI.parseArguments` supports `-getlevel`, `-setlevel`, and `-protocol`. `CLI.connect` uses `AuthenticatedURL` with `KerberosAuthenticator` and optional `SSLFactory`. `Servlet.doGet` checks `HttpServer2.hasAdministratorAccess`, reads `log` and `level` parameters, and calls `process(Logger, level, out)`.

## Control Flow and State
The CLI validates a single operation, builds an HTTP(S) URL, connects, and prints only servlet output lines beginning with the marker `<!-- OUTPUT -->` after stripping HTML tags. The servlet displays submitted class/logger details, checks whether the SLF4J logger is backed by reload4j/log4j, validates the requested level using `Level.toLevel`, sets it when valid, and prints the effective level.

## Persistence, Dependencies, and Integration
State is runtime-only: log levels are changed in the active JVM logger hierarchy. Dependencies include Hadoop `ToolRunner`, servlet utilities, SPNEGO authentication, SSL client config, `HttpServer2` admin access, SLF4J, and log4j/reload4j classes.

## Risks and Test Signals
The servlet is operationally sensitive because it mutates logging dynamically; admin access enforcement is the key guard. Query parameters are concatenated directly by the CLI and should be tested for class names/levels requiring encoding. `IS_LOG4J_LOGGER` permanently disables adapter lookup after class-not-found. Tests should cover argument parser edge cases, protocol validation, HTTPS SSL setup, admin denial, invalid levels, non-log4j logger behavior, and marker parsing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/LogLevel.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/MetaStoreIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/MetaStoreIterator.java

## Purpose
`MetaStoreIterator<T>` is a minimal iterator extension for metadata-store backends. It adds bidirectional positioning primitives to Java `Iterator<T>` so callers can seek to the first or last entry.

## Important APIs and Types
The interface extends `Iterator<T>` and declares `seekToFirst()` and `seekToLast()`. It does not define close semantics, prefix seeking, or typed key/value access.

## Control Flow and State
The interface itself has no control flow or state. Implementations are expected to maintain backend cursor state and move that cursor to the first or last record when requested.

## Persistence, Dependencies, and Integration
The only direct dependency is `java.util.Iterator`. It acts as a common contract for metadata database iterators, including RocksDB-backed table iterators elsewhere in the HDDS utility DB package.

## Risks and Test Signals
Because this interface does not extend `Closeable`, resource-owning implementations need their own cleanup contract or wrapper. Tests should verify implementation-specific cursor movement, empty-store behavior, `next`/`hasNext` semantics after seeking, and how `seekToLast` behaves for prefix-limited iterators.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/MetaStoreIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/MetadataKeyFilters.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/MetadataKeyFilters.java

## Purpose
`MetadataKeyFilters` provides byte-prefix filtering for metadata DB keys. Its primary built-in helper, `getUnprefixedKeyFilter`, returns a negative filter that hides keys beginning with `#`, following the convention that special key prefixes are surrounded by `#`.

## Important APIs and Types
`KeyPrefixFilter` exposes `filterKey(byte[])`, counters `getKeysScannedNum` and `getKeysHintedNum`, and factories `newFilter(String)` and `newFilter(String, boolean negative)`. A null positive prefix returns a singleton pass-through filter; a null negative prefix is rejected.

## Control Flow and State
Each `filterKey` call increments `keysScanned`; null keys return false. A null prefix returns true. Otherwise `prefixMatch` compares byte-by-byte and the positive/negative flag decides whether matches pass or fail. Passing keys increment `keysHinted`.

## Persistence, Dependencies, and Integration
There is no persistence. It depends on `org.apache.hadoop.hdds.StringUtils` for string-to-byte conversion and is intended for LevelDB/RocksDB metadata scans and prefix-aware table iteration.

## Risks and Test Signals
The source contains a TODO noting two known issues: string conversion can replace unsupported characters with `?`, and the encoding may differ from the key codec. Tests should cover positive and negative filters, null/short keys, counter accuracy, null prefix behavior, and non-ASCII prefixes once codec-aligned filtering is implemented.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/MetadataKeyFilters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/NettyMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/NettyMetrics.java

## Purpose
`NettyMetrics` is a Hadoop metrics source that exports Netty direct-memory usage for HDDS services using Ratis-shaded Netty internals.

## Important APIs and Types
`create()` registers a `NettyMetrics` instance under `NettyMetrics.SOURCE_NAME` with `DefaultMetricsSystem`. `getMetrics` emits gauges for `USED_DIRECT_MEM` and `MAX_DIRECT_MEM`. `unregister()` removes the source.

## Control Flow and State
The class is stateless. On metrics collection, it reads `PlatformDependent.usedDirectMemory()` and `maxDirectMemory()` and writes them into one metrics record with context `Netty metrics`.

## Persistence, Dependencies, and Integration
No persistence exists. It depends on Hadoop Metrics2 and Ratis third-party Netty internals. It integrates with daemon metrics initialization where Netty memory pressure needs visibility.

## Risks and Test Signals
Metric values depend on Netty's direct-memory accounting being enabled and meaningful for the runtime. Duplicate registration can fail through the metrics system. Tests should cover registration/unregistration, metric names/descriptions, and behavior when Netty reports unavailable or sentinel values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/NettyMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/PrometheusMetricsSinkUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/PrometheusMetricsSinkUtil.java

## Purpose
`PrometheusMetricsSinkUtil` adapts Hadoop Metrics2 record/metric names and tags for Ozone's Prometheus sink. It normalizes names to Prometheus-friendly lowercase underscore form, handles special RocksDB metrics, and augments tags for RPC scheduler and UGI metrics.

## Important APIs and Types
`addTags` copies an input tag collection and conditionally adds username and servername tags. `prometheusName` combines record and metric names, with a RocksDB-specific path that keeps metric names already delimited by underscores. `getMetricName` and `getUsername` delegate split logic to `DecayRpcSchedulerUtil`.

## Control Flow and State
Name normalization uses a Guava `LoadingCache` capped at 100,000 entries. The normalizer splits camel-case and acronym boundaries, lowercases parts, and replaces non-alphanumeric runs with underscores. Cache load failures are logged and fall back to direct normalization.

## Persistence, Dependencies, and Integration
There is no persistence. Dependencies include Guava cache, Hadoop `MetricsTag`, Apache `StringUtils`, `RocksDBStoreMetrics.ROCKSDB_CONTEXT_PREFIX`, `DecayRpcSchedulerUtil`, and `UgiMetricsUtil`. It is part of HTTP metrics exposition.

## Risks and Test Signals
The cache can hold many unique metric names; its size cap should be validated under high-cardinality inputs. Name splitting can subtly change acronym-heavy names. Tests should cover RocksDB record names containing dots, camel-case/acronym normalization, illegal character replacement, tag preservation/order, username/servername tag injection, and cache fallback.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/PrometheusMetricsSinkUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/ProtocolMessageMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/ProtocolMessageMetrics.java

## Purpose
`ProtocolMessageMetrics<KEY>` collects per-message-type count and total duration metrics for enum-keyed protocol operations. It also tracks current concurrency using an auto-closeable measurement scope.

## Important APIs and Types
`create` and the constructor initialize a `Stats` entry for every enum constant. `increment(KEY, duration)` adds an observed duration. `measure(KEY)` increments concurrency, captures monotonic start time, and returns an `UncheckedAutoCloseable` that decrements concurrency and records elapsed time on close. `register`, `unregister`, and `getMetrics` integrate with Metrics2.

## Control Flow and State
The state is an immutable enum-to-`Stats` map and atomic counters. `getMetrics` emits a record for each key tagged with `type`, plus a separate record for concurrency. `Stats` uses `AtomicLong` counters for call count and cumulative time.

## Persistence, Dependencies, and Integration
No persistent state exists. Dependencies include Hadoop Metrics2, `DefaultMetricsSystem`, `Interns`, `Time.monotonicNow`, and Ratis `UncheckedAutoCloseable`. Callers typically wrap protocol handler bodies in try-with-resources using `measure`.

## Risks and Test Signals
If callers do not close the returned scope, concurrency remains inflated and duration is lost. Passing a null or foreign enum key will fail through the map lookup. Tests should cover all enum constants exported, duration accumulation, concurrent measurements, unregister behavior, and try-with-resources correctness on exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/ProtocolMessageMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/RDBSnapshotProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/RDBSnapshotProvider.java

## Purpose
`RDBSnapshotProvider` is an abstract RocksDB snapshot downloader for OM/SCM HA state transfer. It supports full and incremental snapshot flows by downloading tar parts from the current leader, untarring them into a candidate directory, and returning a `DBCheckpoint` when the Ratis snapshot completion flag appears.

## Important APIs and Types
Key APIs are the constructor, synchronized `init`, `downloadDBSnapshotFromLeader`, `checkLeaderConsistency`, `getSnapshotFileName`, `getCheckpointFromUntarredDb`, and abstract `downloadSnapshot`. Test hooks include `FaultInjector`, `getSnapshotDir`, `getCandidateDir`, `setInjector`, `getNumDownloaded`, and `getInitCount`.

## Control Flow and State
Construction creates `snapshotDir`, derives `candidateDir`, initializes atomics, and calls `init`. `init` ensures the parent exists, clears or creates the candidate dir, resets last leader, and increments init count. Downloads loop until a tar extraction contains `OZONE_RATIS_SNAPSHOT_COMPLETE`. Leader changes or unexpected candidate contents trigger cleanup and reset.

## Persistence, Dependencies, and Integration
The provider mutates filesystem directories under the configured snapshot directory, writes temporary tar files, deletes tar files after extraction, and returns `RocksDBCheckpoint` by default. It depends on `HAUtils.getExistingFiles`, `HddsServerUtil.ratisSnapshotComplete`, Hadoop `FileUtil`, and HDDS directory creation utilities. Subclasses provide the transport.

## Risks and Test Signals
The download loop is unbounded until a completion flag appears, so transport implementations and tests must simulate multipart termination. Candidate cleanup is leader-sensitive and critical for incremental correctness. Tests should cover leader change reset, stale candidate dir cleanup, snapshot filename uniqueness, tar deletion, incomplete multipart loops, injected pause, and subclass download failure propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/RDBSnapshotProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/RocksDBStoreMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/RocksDBStoreMetrics.java

## Purpose
`RocksDBStoreMetrics` exports RocksDB statistics, properties, SST layout, and sequence metrics through Hadoop Metrics2. It supports both per-column-family metrics and aggregated counters for selected RocksDB properties.

## Important APIs and Types
`create` registers or reuses a metrics source named with `ROCKSDB_CONTEXT_PREFIX + dbName`. `getMetrics` delegates to `getHistogramData`, `getTickerTypeData`, `getDBPropertyData`, and `getLatestSequenceNumber`. Helpers compute live SST file counts/sizes per level and export them as metrics.

## Control Flow and State
Constructor stores `Statistics`, `RocksDatabase`, context name, known histogram attributes, and precomputes Prometheus-style property suffixes. Histogram collection reflects over `HistogramData` getters for average/median/p95/p99/stddev/max while skipping BLOB DB metrics. Property collection iterates extra column families, reads `rocksdb.*` properties, and aggregates selected values.

## Persistence, Dependencies, and Integration
No persistence is created, but it reads live RocksDB state. Dependencies include RocksDB `Statistics`, `TickerType`, `HistogramType`, `LiveFileMetaData`, HDDS `RocksDatabase`, and Metrics2. It is registered by `RDBStore` when RocksDB metrics are enabled.

## Risks and Test Signals
Reflection can log noisy errors if RocksDB changes histogram accessors. Property values are parsed as longs and can fail for unavailable properties. Raw `HashMap` use is unchecked. Tests should cover duplicate registration reuse, BLOB metric exclusion, null statistics, per-CF and aggregate property emission, SST level aggregation, and latest sequence error handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/RocksDBStoreMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/SignalLogger.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/SignalLogger.java

## Purpose
`SignalLogger` logs UNIX termination-related signals before delegating to the previous signal handler. It helps operators distinguish normal shutdowns from signals such as SIGHUP, SIGINT, and SIGTERM.

## Important APIs and Types
The enum singleton `INSTANCE` exposes `register(Logger)`. Internal `Handler` implements `jnr.posix.SignalHandler`, installs itself with `POSIX.signal`, stores the previous handler or a default `System.exit` handler, and logs before delegation.

## Control Flow and State
`register` is one-shot: it throws if called more than once. It iterates the configured signal set, installs handlers, logs per-signal installation failures at info, and logs the final registered set. On signal receipt, `Handler.handle` logs the numeric signal and symbolic name, then invokes the previous handler.

## Persistence, Dependencies, and Integration
There is no persistence. It depends on JNR POSIX and HDDS audience/stability annotations. `HddsServerUtil.startupShutdownMessage` registers it for UNIX platforms during daemon startup.

## Risks and Test Signals
Because handler registration is process-global and one-shot, tests must isolate or reset process state carefully. Delegating to prior handlers is essential for normal shutdown behavior. Tests should cover repeated registration failure, handler installation failures, logging content, and non-UNIX startup paths that skip registration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/SignalLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/TableCacheMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/TableCacheMetrics.java

## Purpose
`TableCacheMetrics` exports cache size and hit/miss/iteration counters for a single HDDS table cache through Hadoop Metrics2.

## Important APIs and Types
`create(TableCache, tableName)` registers a metrics source named `<tableName>Cache`. `getMetrics` emits one `TableCacheMetrics` record tagged with the table name and gauges for size, hit count, miss count, and iteration count. `unregister` removes the source by the per-table name.

## Control Flow and State
The object stores references to the cache and table name. Metrics collection asks the cache for `CacheStats` and current size each time, so exported values reflect live cache state.

## Persistence, Dependencies, and Integration
No persistence exists. Dependencies include `TableCache`, `CacheStats`, `DefaultMetricsSystem`, and Metrics2. It integrates with typed table/cache implementations that want table-local cache observability.

## Risks and Test Signals
The registered source name differs from the record name (`SOURCE_NAME`), so consumers should validate both. Duplicate table names can collide in the metrics system. Tests should cover registration/unregistration, metric values from a fake cache, record tags, zero-counter state, and repeated registration behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/TableCacheMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/TransactionInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/TransactionInfo.java

## Purpose
`TransactionInfo` is an immutable persisted representation of a Ratis term and transaction index. It is stored in Ozone metadata DBs and can also be exposed as Ratis `SnapshotInfo`.

## Important APIs and Types
Static constructors include `valueOf(String)`, `valueOf(long, long)`, `valueOf(TermIndex)`, and non-Ratis `getTermIndex(long)`. `getCodec` returns a `DelegatedCodec` over `StringCodec`. Accessors include `getTerm`, `getTransactionIndex`, `getTermIndex`, `toByteString`, `fromByteString`, `toSnapshotInfo`, and `readTransactionInfo(DBStoreHAManager)`.

## Control Flow and State
The persisted string is `term + TRANSACTION_INFO_SPLIT_KEY + index`. Parsing validates exactly two fields and converts both to longs. The constructor creates an anonymous `SnapshotInfo` whose term-index and `toString` mirror the immutable transaction string; `getFiles` returns null.

## Persistence, Dependencies, and Integration
This is directly persisted under `TRANSACTION_INFO_KEY` in HA metadata tables and read by HA checkpoint validation. Dependencies include Guava preconditions, Protobuf `ByteString`, HDDS codecs, Ratis `TermIndex`, `SnapshotInfo`, and DB HA manager interfaces.

## Risks and Test Signals
Malformed transaction strings throw `IllegalArgumentException`. The anonymous `SnapshotInfo.getFiles` returning null may surprise generic snapshot code. Ordering delegates to `TermIndex.compareTo`. Tests should cover codec round trips, byte-string conversion, default value semantics, non-Ratis term handling, compare/equality/hash consistency, malformed strings, and DB read skip-cache behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/TransactionInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/UgiMetricsUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/UgiMetricsUtil.java

## Purpose
`UgiMetricsUtil` adds Ozone-specific servername tagging for Hadoop UGI metrics so Prometheus output can distinguish the server associated with user/group metrics.

## Important APIs and Types
`createServernameTag(String key, String servername)` returns `Optional.empty()` unless the metric key contains `ugi_metrics`; otherwise it creates a `MetricsTag` whose info name is `servername` and value is the supplied server name.

## Control Flow and State
The class is stateless. It performs a substring check on the metric key and constructs an inline `MetricsInfo` instance when a tag is needed.

## Persistence, Dependencies, and Integration
No persistence exists. Dependencies are Hadoop `MetricsInfo` and `MetricsTag`. `PrometheusMetricsSinkUtil.addTags` calls this helper while adapting metrics records for Prometheus.

## Risks and Test Signals
The substring match is broad; unrelated keys containing `ugi_metrics` will be tagged. Null keys would throw. Tests should cover matching and non-matching keys, null/empty server names if allowed by callers, metrics info name/description, and integration with `PrometheusMetricsSinkUtil.addTags`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/UgiMetricsUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/AutoCloseSupplier.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/AutoCloseSupplier.java

## Purpose
`AutoCloseSupplier<RAW>` is a package-private functional interface combining `Supplier<RAW>` and `AutoCloseable`. It lets code pass suppliers that may own resources while defaulting to no-op cleanup.

## Important APIs and Types
The interface extends `AutoCloseable` and `Supplier<RAW>` and overrides `close()` with a default no-op implementation. Because it is annotated as a functional interface, the abstract method remains `Supplier.get()`.

## Control Flow and State
There is no state or control flow. Implementations can be lambdas for simple suppliers or classes overriding `close` when cleanup is needed.

## Persistence, Dependencies, and Integration
No persistence exists. The only dependency is `java.util.function.Supplier`. It is scoped to the DB package and can be used around codec/raw-value APIs where optional resource cleanup is useful.

## Risks and Test Signals
The no-op default can hide forgotten cleanup if implementers assume close is mandatory. Tests are only needed where concrete implementations allocate resources; they should verify both `get` behavior and idempotent close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/AutoCloseSupplier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/BatchOperation.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/BatchOperation.java

## Purpose
`BatchOperation` is the generic handle for collecting multiple metadata DB operations before committing them atomically through a `BatchOperationHandler`.

## Important APIs and Types
The interface extends `AutoCloseable` and redeclares `close()` without checked exceptions. Concrete implementations, notably `RDBBatchOperation`, hold backend-specific batch resources.

## Control Flow and State
No behavior is implemented here. The lifecycle is: create through a handler/store, add operations through backend-specific table methods, commit through `commitBatchOperation`, then close.

## Persistence, Dependencies, and Integration
No direct persistence. It is part of the HDDS DB abstraction and is implemented by RocksDB-backed batch operations.

## Risks and Test Signals
The abstraction does not itself expose put/delete methods, so callers rely on table/store-specific APIs and casts. Tests should focus on concrete implementations: close releases resources, uncommitted operations are discarded, and committed batches are atomic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/BatchOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/BatchOperationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/BatchOperationHandler.java

## Purpose
`BatchOperationHandler` defines the store-level contract for creating and committing database batch operations.

## Important APIs and Types
`initBatchOperation()` returns a `BatchOperation` container. `commitBatchOperation(BatchOperation)` persists its collected operations and may throw `RocksDatabaseException`.

## Control Flow and State
The interface has no internal state. Implementations decide whether commits are synchronous, which write options apply, and how invalid operation types are handled.

## Persistence, Dependencies, and Integration
This interface is implemented by `DBStore`, with `RDBStore` returning `RDBBatchOperation` and committing through RocksDB write batches. It connects higher-level metadata tables to backend atomic writes.

## Risks and Test Signals
The generic signature accepts any `BatchOperation`; `RDBStore` casts to `RDBBatchOperation`, so wrong implementation types fail at runtime. Tests should cover commit success, exception propagation, close-after-commit, and invalid operation type handling if exposed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/BatchOperationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/ByteArrayCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/ByteArrayCodec.java

## Purpose
`ByteArrayCodec` is a singleton no-op codec for byte arrays. It allows raw byte keys or values to pass through typed table APIs without serialization overhead.

## Important APIs and Types
`get()` returns the singleton `Codec<byte[]>`. `getTypeClass` returns `byte[].class`. `toPersistedFormat`, `fromPersistedFormat`, and `copyObject` all return the same array reference.

## Control Flow and State
The class is immutable and stateless. There is no null handling beyond returning whatever reference is passed.

## Persistence, Dependencies, and Integration
It implements the HDDS `Codec` interface and is registered by default in `CodecRegistry`. It is used by raw RocksDB tables and byte-array typed metadata tables.

## Risks and Test Signals
Returning the same mutable array is efficient but can leak mutations between caller, cache, and persistence layers. Tests should verify pass-through behavior and document aliasing expectations; callers needing defensive copies must use a different codec or copy externally.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/ByteArrayCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/ByteStringCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/ByteStringCodec.java

## Purpose
`ByteStringCodec` serializes and deserializes protobuf `ByteString` values for HDDS metadata tables, including optimized `CodecBuffer` support.

## Important APIs and Types
`get()` returns the singleton. `supportCodecBuffer` returns true. `toCodecBuffer` wraps existing `ByteString` data or copies into a direct buffer when requested. `fromCodecBuffer` returns the wrapped `ByteString` when possible or copies from a read-only byte buffer. Byte-array conversion maps null inputs to empty values.

## Control Flow and State
The class is stateless. It tries to avoid copies when buffer/directness constraints allow, while preserving compatibility with direct allocators.

## Persistence, Dependencies, and Integration
It depends on protobuf `ByteString`, `jakarta.annotation.Nonnull`, and HDDS `CodecBuffer`. It integrates with typed table values storing protobuf blobs and with code paths using direct buffers for RocksDB writes.

## Risks and Test Signals
Null object serialization returns an empty byte array, which differs from codecs that reject null persistence. Direct allocator behavior should be tested carefully to avoid heap/direct mismatches. Tests should cover nulls, empty values, direct and heap `CodecBuffer` round trips, wrapped-object preservation, and immutability assumptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/ByteStringCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/CodecBufferCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/CodecBufferCodec.java

## Purpose
`CodecBufferCodec` persists `CodecBuffer` objects directly, preserving direct-vs-heap allocation mode and avoiding unnecessary copies for buffer-native table operations.

## Important APIs and Types
`get(boolean direct)` returns either the direct or heap singleton. `supportCodecBuffer` returns true. `toCodecBuffer` requires the provided allocator to match the object's directness and returns the same object. `fromPersistedFormat` allocates a new buffer of the configured type and fills it from a byte array. `copyObject` also returns the same buffer.

## Control Flow and State
Each singleton stores a `CodecBuffer.Allocator`. Serialization reads `buffer.getArray()`, while deserialization wraps the input bytes in a `ByteBuffer` and puts them into a newly allocated `CodecBuffer`.

## Persistence, Dependencies, and Integration
It depends on `CodecBuffer`, `ByteBuffer`, and Jakarta `Nonnull`. It is useful for RocksDB paths that already operate on direct buffers.

## Risks and Test Signals
The class intentionally does not copy in `copyObject` or `toCodecBuffer`, so ownership/lifecycle is caller-sensitive. `getArray()` may imply heap accessibility depending on `CodecBuffer` implementation. Tests should cover direct/heap mismatch exceptions, round trips, close ownership expectations, and mutation/aliasing behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/CodecBufferCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/CodecRegistry.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/CodecRegistry.java

## Purpose
`CodecRegistry` is an immutable lookup table for converting typed keys/values to and from persisted byte arrays in HDDS metadata tables.

## Important APIs and Types
`newBuilder` pre-registers codecs for `String`, `Long`, `Integer`, `byte[]`, and `Boolean`. `Builder.addCodec` adds or replaces mappings. `asObject`, `copyObject`, and `asRawData` perform conversion. `getCodec(object)` searches exact class, all superclasses, then all interfaces. `getCodecFromClass` requires an exact registered class.

## Control Flow and State
The registry copies builder mappings into an unmodifiable map. Object lookup allows subclass/interface codecs, while class lookup is stricter. `asRawData` rejects null persisted values with `Objects.requireNonNull`.

## Persistence, Dependencies, and Integration
It has no persistence, but is foundational for typed table persistence. Dependencies include HDDS codec implementations and Apache Commons `ClassUtils`.

## Risks and Test Signals
Subclass/interface search order can pick an unexpected codec when multiple supertypes are registered. `asObject` returns null for null raw data, but `asRawData` rejects null objects. Tests should cover default registry codecs, custom codec overrides, subclass/interface resolution, missing codec errors, null raw/object behavior, and copy semantics for mutable types.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/CodecRegistry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBCheckpoint.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBCheckpoint.java

## Purpose
`DBCheckpoint` is the generic contract for filesystem-backed snapshots of an HDDS database.

## Important APIs and Types
It exposes checkpoint location, creation timestamp, latest sequence number, checkpoint creation duration, and `cleanupCheckpoint()`.

## Control Flow and State
The interface has no implementation. Implementations such as RocksDB checkpoints own the snapshot directory and cleanup behavior.

## Persistence, Dependencies, and Integration
It represents persisted checkpoint artifacts on local disk and is used by checkpoint managers, snapshot providers, and checkpoint streaming utilities.

## Risks and Test Signals
Implementations must define whether cleanup is destructive, idempotent, and safe under concurrent readers. Tests should verify timestamp/sequence accuracy, cleanup behavior, missing-path handling, and integration with tar streaming and HA installation flows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBCheckpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBColumnFamilyDefinition.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBColumnFamilyDefinition.java

## Purpose
`DBColumnFamilyDefinition<KEY, VALUE>` describes one logical table/column family, including its table name, key codec, value codec, optional RocksDB column-family options, and typed table accessors.

## Important APIs and Types
Constructors require table name and codecs. Static helpers build unmodifiable maps or multimaps keyed by table name. `getTable(DBStore)` and `getTable(DBStore, CacheType)` return typed tables. Accessors expose codecs, key/value classes, table name, and mutable `ManagedColumnFamilyOptions`.

## Control Flow and State
Definitions are mostly immutable except for volatile `cfOptions`. `toString` stores a readable `<table>-def: Key -> Value` name. Map helpers delegate to `CollectionUtils` and preserve uniqueness or multi-value semantics depending on helper used.

## Persistence, Dependencies, and Integration
No direct persistence occurs, but definitions drive `DBStoreBuilder` column-family creation and typed table conversion. Dependencies include HDDS codecs, table cache types, collection utilities, and managed RocksDB options.

## Risks and Test Signals
`cfOptions` mutability means shared definitions can leak option changes across builders/tests. Duplicate names in unmodifiable maps should be validated. Tests should cover typed table retrieval, cache type propagation, map helper duplicate behavior, null constructor validation, and options override precedence in `DBStoreBuilder`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBColumnFamilyDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBConfigFromFile.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBConfigFromFile.java

## Purpose
`DBConfigFromFile` loads developer-oriented RocksDB DB and column-family options from `.ini` files. It supports direct paths and fallback lookup under `OZONE_CONF_DIR`.

## Important APIs and Types
`getConfigLocation` reads `OZONE_CONF_DIR` from environment or JVM property. `getOptionsFileNameFromDB` appends `.ini` to a DB filename. `readDBOptionsFromFile` loads `ManagedDBOptions`; `readCFOptionsFromFile` selects a `ColumnFamilyDescriptor` matching a requested CF and wraps its options in `ManagedColumnFamilyOptions`.

## Control Flow and State
`generateDBPath` returns the given path if it exists; otherwise it builds a fallback path from config location and `<dbPath>.ini`; otherwise it returns an empty path. Option loaders return null for empty or missing paths, close temporary descriptors in finally blocks, and propagate RocksDB parsing errors where appropriate.

## Persistence, Dependencies, and Integration
It does not persist state but reads local option files. Dependencies include RocksDB `OptionsUtil`, column-family descriptors, managed option wrappers, Apache `StringUtils`, and `OZONE_CONF_DIR`. `DBStoreBuilder` calls this before falling back to profile defaults.

## Risks and Test Signals
This is explicitly for developers/performance testing, not end-user tuning. The fallback uses `path.toString()` when constructing an options filename, which can include path separators. Tests should cover env/property lookup, direct vs fallback paths, missing files returning null, descriptor cleanup, default column family naming, invalid RocksDB option files, and CF lookup misses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBConfigFromFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBDefinition.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBDefinition.java

## Purpose
`DBDefinition` describes a logical HDDS metadata database: its name, configuration key for location, options path, and column-family definitions.

## Important APIs and Types
Core methods are `getName`, `getLocationConfigKey`, `getDBLocation`, `getOptionsPath`, `getColumnFamilies`, `getColumnFamilies(String)`, and `getColumnFamily(String)`. Static `getColumnFamilyNames` builds immutable name lists. Nested `WithMapInterface` and `WithMap` implement map-backed definitions with memoized column-family names.

## Control Flow and State
Default `getDBLocation` delegates to `ServerUtils.getDirectoryFromConfig`. `getColumnFamily` returns null for missing names and throws if a name maps to multiple definitions. `WithMap` stores the provided map and memoizes the derived names through Ratis `MemoizedSupplier`.

## Persistence, Dependencies, and Integration
The interface does not persist data but controls DB creation by `DBStoreBuilder` and HA utilities. It depends on HDDS `ConfigurationSource`, `ServerUtils`, and DB column-family definitions.

## Risks and Test Signals
Multi-map definitions need care because default `getColumnFamily` rejects ambiguous names. Memoization means changes to the underlying map after construction may not be reflected in names. Tests should cover location fallback behavior, options path overrides, missing and duplicate column families, map-backed iteration, and builder integration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBProfile.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBProfile.java

## Purpose
`DBProfile` provides predefined RocksDB tuning profiles for HDDS metadata stores: `SSD`, `DISK`, and `TEST`.

## Important APIs and Types
Each enum implements `getDBOptions`, `getColumnFamilyOptions`, and `getBlockBasedTableConfig`. `SSD` configures write buffer size, dynamic level bytes, block cache, block size, pinned filters/indexes, bloom filter, parallelism, background compactions/flushes, bytes-per-sync, and create-if-missing flags. `DISK` adds compaction readahead and level compaction. `TEST` disables auto compactions.

## Control Flow and State
Every call creates new managed RocksDB option/config objects. `DISK` and `TEST` start from `SSD` options and mutate profile-specific fields. `toLong` converts storage-size doubles via `BigDecimal`.

## Persistence, Dependencies, and Integration
No persistence occurs directly. Dependencies include Hadoop `StorageUnit`, managed RocksDB option wrappers, LRU cache, bloom filter, and RocksDB `CompactionStyle`. `DBStoreBuilder` selects a default profile from `HDDS_DB_PROFILE`.

## Risks and Test Signals
Managed options contain native resources and must be closed by the owning store/build path. Profiles encode operational defaults, so changes affect memory and compaction behavior broadly. Tests should cover independent object creation, key option values, TEST compaction disabling, DISK readahead, and resource cleanup by builder/store paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBProfile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBStore.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBStore.java

## Purpose
`DBStore` is the main abstraction for HDDS metadata databases that expose named tables, typed table access, batch operations, flush/compact/checkpoint operations, WAL delta reads, and lifecycle management.

## Important APIs and Types
Key methods include raw and typed `getTable`, `listTables`, `flushDB`, `flushLog`, `compactDB`, `compactTable`, `getEstimatedKeyCount`, `getCheckpoint`, `getDbLocation`, `getTableNames`, `dropTable`, `getUpdatesSince`, `isClosed`, `getSnapshotsParentDir`, and `getRocksDBCheckpointDiffer`.

## Control Flow and State
The interface extends `UncheckedAutoCloseable` and `BatchOperationHandler`. Default typed `getTable` uses `CacheType.PARTIAL_CACHE`, while implementations provide actual backend behavior.

## Persistence, Dependencies, and Integration
This interface represents persistent metadata stores and integrates with RocksDB-specific classes, table cache types, compaction options, checkpoint diffing, and Recon delta update flows.

## Risks and Test Signals
Some methods are RocksDB-specific despite the generic name, such as checkpoint differ and RocksDB exceptions. `dropTable` is destructive. Tests should use implementation suites to verify table typing, checkpoint creation, WAL delta limits, compaction, read-only close behavior, and lifecycle after close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBStoreBuilder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBStoreBuilder.java

## Purpose
`DBStoreBuilder` constructs `RDBStore` instances by combining DB definitions, metadata paths, RocksDB profile defaults, optional `.ini` configuration, metrics/statistics settings, WAL/log settings, read-only mode, checkpoint directory behavior, and optional compaction-DAG differ support.

## Important APIs and Types
Static entry points are `createDBStore` and several `newBuilder` overloads. Builder methods include `setName`, `setPath`, `setOptionsPath`, `addTable`, `setDBOptions`, `setDefaultCFOptions`, `setOpenReadOnly`, `setEnableCompactionDag`, `setCreateCheckpointDirs`, `setEnableRocksDbMetrics`, `setProfile`, `setMaxNumberOfOpenFiles`, and `disableDefaultCFAutoCompaction`. `build` returns an `RDBStore`.

## Control Flow and State
Construction reads config for statistics, CF write buffer size, default DB profile, RocksDB configuration, and max DB update size. Applying a `DBDefinition` sets name/path/options path and adds all column families, preferring file-based CF options, then definition-level options. `build` validates required fields, creates table configs, selects DB options, applies statistics and write options, checks parent directory, and constructs `RDBStore`.

## Persistence, Dependencies, and Integration
The builder creates/open RocksDB stores and thus controls persistent DB layout. It depends on HDDS config keys, `DBConfigFromFile`, `DBProfile`, managed RocksDB options/statistics/write options/loggers, `RocksDBConfiguration`, and `RDBStore`.

## Risks and Test Signals
Native option ownership is delicate: `tableConfigs` are closed in `finally`, while DB options/statistics/write options transfer to `RDBStore` on success and are closed on failure. The default CF is always added. Tests should cover missing name/path, nonexistent parent directory, read-only builds, `.ini` precedence, profile fallback, statistics off/on, logger settings, max open files, compaction DAG lock requirements, metrics disabling, and cleanup on constructor failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBStoreBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBUpdatesWrapper.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBUpdatesWrapper.java

## Purpose
`DBUpdatesWrapper` is a simple mutable carrier for RocksDB WAL update batches returned by `DBStore.getUpdatesSince`.

## Important APIs and Types
It stores a `List<byte[]>` of write batch data, `currentSequenceNumber`, `latestSequenceNumber`, and a success flag. `addWriteBatch` appends data and advances current sequence number when the input sequence is newer.

## Control Flow and State
The wrapper starts with sequence numbers `-1` and success true. Callers add batches, set latest/current sequence values, and mark DB update success false on partial/failure cases.

## Persistence, Dependencies, and Integration
It does not persist state itself but transports persisted WAL bytes to Recon or other consumers. It is populated by `RDBStore.getUpdatesSince`.

## Risks and Test Signals
The returned data list is mutable and directly exposed. Sequence semantics rely on callers passing monotonically meaningful sequence numbers. Tests should cover empty wrapper defaults, add/update sequence behavior, success flag propagation, latest sequence setting, and external list mutation expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBUpdatesWrapper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/FixedLengthStringCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/FixedLengthStringCodec.java

## Purpose
`FixedLengthStringCodec` serializes strings with ISO-8859-1 so serialized byte length equals Java string length for supported characters. It is useful for fixed-width key schemas.

## Important APIs and Types
`get()` returns the singleton. Static helpers `string2Bytes` and `bytes2String` delegate to the codec. The class extends `StringCodecBase.WithFallback` with `StandardCharsets.ISO_8859_1`.

## Control Flow and State
The codec is stateless. Encoding errors in `string2Bytes` are converted to `IllegalStateException` through the provided exception factory.

## Persistence, Dependencies, and Integration
It participates in typed DB persistence where fixed byte length matters. Dependencies include `StringCodecBase` and Java charset APIs.

## Risks and Test Signals
Characters outside ISO-8859-1 can trigger fallback/error behavior depending on the base class. Tests should cover ASCII and high Latin-1 round trips, unsupported character behavior, byte-length equality, null handling inherited from the base codec, and ordering implications for keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/FixedLengthStringCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/InodeMetadataRocksDBCheckpoint.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/InodeMetadataRocksDBCheckpoint.java

## Purpose
`InodeMetadataRocksDBCheckpoint` represents a RocksDB checkpoint layout that reconstructs inode-based metadata snapshots using hardlinks described by a `hardLinkFile`. It optimizes disk use and normalizes v1/v2 checkpoint layouts.

## Important APIs and Types
Constructors accept a checkpoint path and optional `deleteSourceFiles` flag. `installHardLinks` reads hardlink mappings and creates links. `moveActiveDbFilesToOmDbIfNeeded` moves root-level active DB files into `om.db` for v1 format. `cleanupCheckpoint` deletes the checkpoint directory.

## Control Flow and State
Construction stores the location/timestamp, installs hardlinks, then normalizes active DB file placement. `installHardLinks` reads lines split by `OzoneConsts.HARDLINK_SEPARATOR`, creates parent directories, creates hardlinks from source to target inside the checkpoint tree, deletes the hardlink file, and optionally deletes source files. Malformed lines are skipped with warnings.

## Persistence, Dependencies, and Integration
This class mutates checkpoint directories and uses filesystem hardlinks. It depends on Apache Commons IO `FileUtils`, Java NIO `Files`, `HddsServerUtil.OZONE_RATIS_SNAPSHOT_COMPLETE_FLAG_NAME`, and Ozone constants. It implements `DBCheckpoint` for snapshot install flows.

## Risks and Test Signals
Hardlink creation can fail across filesystems or if targets already exist. Deleting source files in v2 mode is destructive but intended after links exist. Tests should cover missing hardlink file, malformed mappings, parent directory creation, v1 active-file movement, completion flag preservation, source deletion failures, cleanup deletion, and latest sequence returning `-1`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/InodeMetadataRocksDBCheckpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBBatchOperation.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBBatchOperation.java

## Purpose
`RDBBatchOperation` is the RocksDB `BatchOperation` implementation. It collects put/delete operations by column family, deduplicates operations on the same key, then applies the final operations to a managed RocksDB write batch for atomic commit.

## Important APIs and Types
Factories `newAtomicOperation()` and `newAtomicOperation(ManagedWriteBatch)` create batches. Public operations include `put`, `delete`, `commit(RocksDatabase)`, `commit(RocksDatabase, ManagedWriteOptions)`, and `close`. Internal `Bytes` wraps heap or direct key data with content equality. Internal `Op`, `SingleKeyOp`, `PutOp`, `DeleteOp`, and `OpCache` manage lifecycle and deduplication.

## Control Flow and State
`OpCache` groups operations by column-family name. Adding a new op removes and closes any previous op for the same key, tracks discarded size/count, and stores the latest op. Commit prepares each family cache once, applies ops to the write batch, writes the batch to RocksDB, and clears temporary resources through try-with-resources. Closing closes the write batch and any cached operations.

## Persistence, Dependencies, and Integration
Persistence occurs only on commit via `RocksDatabase.batchWrite`. The class depends on managed write batches, managed direct/heap slices, `CodecBufferCodec`, `ColumnFamily`, `ManagedWriteOptions`, and HDDS `IOUtils`. It is created and committed by `RDBStore`.

## Risks and Test Signals
The class is explicitly not thread-safe and is single-use after commit. Deduplication relies on stable byte content and proper closure of slices/buffers. `delete(byte[])` and `put(byte[], byte[])` allocate direct codec buffers. Tests should cover overwrite deduplication, delete-after-put, put-after-delete, multi-CF batches, commit once, close without commit warning/discard, direct and heap key equality, write options commit, and resource closure on exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBBatchOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBCheckpointManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBCheckpointManager.java

## Purpose
`RDBCheckpointManager` wraps RocksDB checkpoint creation and translates it into HDDS `RocksDBCheckpoint` objects with metadata such as creation time and latest sequence number.

## Important APIs and Types
The constructor stores a `RocksDatabase`, checkpoint name prefix, and `RocksCheckpoint`. `createCheckpoint(parentDir, name)` creates a named or timestamped checkpoint. `createCheckpoint(parentDir)` uses the default timestamp naming scheme. `close` closes the underlying Rocks checkpoint object.

## Control Flow and State
Checkpoint creation builds a directory name from optional prefix and supplied name or `checkpoint_<time>`, flushes WAL and memtables, calls RocksDB checkpoint creation, reads latest sequence number, measures elapsed time, waits for the directory to exist, and returns a `RocksDBCheckpoint`. IO failures are logged and return null.

## Persistence, Dependencies, and Integration
It writes checkpoint directories under the supplied parent path and depends on `RocksDatabase.RocksCheckpoint`, `RocksDBCheckpoint`, and `RDBCheckpointUtils`. It is owned by `RDBStore`.

## Risks and Test Signals
Returning null on `IOException` rather than throwing can push failure handling to callers. Directory existence waiting is best-effort. Tests should cover naming, explicit names, flush ordering, latest sequence propagation, creation duration, missing parent behavior, null return on IO failure, and close lifecycle.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBCheckpointManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBCheckpointUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBCheckpointUtils.java

## Purpose
`RDBCheckpointUtils` contains polling helpers for waiting until a checkpoint directory appears after RocksDB checkpoint creation.

## Important APIs and Types
`waitForCheckpointDirectoryExist(File, Duration)` polls `file.exists()` every 100 ms until the supplied timeout. The overload without timeout uses a 20 second maximum.

## Control Flow and State
The utility delegates polling to `RatisHelper.attemptUntilTrue`. If the directory is not observed before timeout, it logs an informational message and returns false.

## Persistence, Dependencies, and Integration
There is no persistence. It depends on Java `File`, `Duration`, Ratis helper polling, and SLF4J. `RDBCheckpointManager` calls it after checkpoint creation.

## Risks and Test Signals
The no-timeout overload declares `IOException` but does not throw directly. A false result is not propagated as an exception by the manager. Tests should cover immediate success, delayed success, timeout logging, custom timeout, and interrupted/polling behavior through `RatisHelper`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBCheckpointUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBMetrics.java

## Purpose
`RDBMetrics` is a singleton Metrics2 source for generic RocksDB table operation and WAL delta-update counters.

## Important APIs and Types
`create` registers or returns the singleton. Counters track key may-exist checks/misses, key gets, get-if-exist checks/misses/gets, WAL update data size, and WAL update sequence count. `unRegister` clears the singleton and unregisters the source.

## Control Flow and State
The metrics system injects `MutableCounterLong` fields annotated with `@Metric`. Increment/get methods update or read counters. Singleton creation and unregistration are synchronized.

## Persistence, Dependencies, and Integration
No persistent state exists. Dependencies include Hadoop Metrics2 annotations and `DefaultMetricsSystem`. `RDBStore` creates it and `RDBTable`/WAL update code increment it.

## Risks and Test Signals
Because it is a global singleton, multiple stores share counters and one store close unregisters the source. Tests should isolate metrics system state and cover singleton reuse, increments, WAL counters, unregister/reset, and interaction with multiple `RDBStore` instances.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBSstFileLoader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBSstFileLoader.java

## Purpose
`RDBSstFileLoader` ingests external RocksDB SST files into a target column family.

## Important APIs and Types
The package-private `load(RocksDatabase db, ColumnFamily family, File externalFile)` method skips empty files and otherwise creates `ManagedIngestExternalFileOptions`, sets `ingestBehind(false)`, and calls `db.ingestExternalFile`.

## Control Flow and State
The class is stateless. Ingest options are created and closed with try-with-resources for each load operation.

## Persistence, Dependencies, and Integration
It mutates RocksDB persistent state by ingesting SST contents. Dependencies include `RocksDatabase`, `ColumnFamily`, `ManagedIngestExternalFileOptions`, and Java `File`. It is a low-level helper for bulk-load/import paths.

## Risks and Test Signals
Skipping zero-length SSTs avoids RocksDB exceptions but may hide upstream empty-file generation. Tests should cover empty-file no-op, successful ingest path, option setting, exception propagation from RocksDB, and target column-family selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBSstFileLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBStore.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBStore.java

## Purpose
`RDBStore` is the concrete RocksDB-backed implementation of `DBStore`. It opens RocksDB with configured column families, exposes raw and typed tables, manages checkpoints/snapshots, flush/compact/drop operations, Metrics2 registration, optional compaction-DAG checkpoint differ integration, and WAL delta retrieval for Recon.

## Important APIs and Types
Constructor parameters include DB file, DB options/statistics/write options, table configs, read-only flag, metrics name, compaction DAG settings, delta size threshold, checkpoint dir flag, configuration, and metrics enable flag. Public APIs implement table access, compaction, close, `getCheckpoint`, `getSnapshot`, `getUpdatesSince`, property reads, metrics access, and checkpoint differ access.

## Control Flow and State
Construction optionally initializes `RocksDBCheckpointDiffer`, opens `RocksDatabase`, registers `RocksDBStoreMetrics`, creates checkpoint/snapshot parent directories, wires differ column-family handles, loads compaction logs, creates `RDBCheckpointManager`, and registers `RDBMetrics`. `close` unregisters metrics, closes checkpoint/differ/statistics resources, flushes non-read-only DBs, and closes RocksDB. `getUpdatesSince` validates WAL availability, skips old batches, enforces count and cumulative size limits, closes each write batch, updates metrics, and throws `SequenceNumberNotFoundException` when full deltas are unavailable.

## Persistence, Dependencies, and Integration
This class owns the live RocksDB database, checkpoint directories, snapshot directories, WAL reads, table handles, metrics, and compaction differ state. It depends on `RocksDatabase`, managed RocksDB options/statistics/write options, `RDBCheckpointManager`, `RDBMetrics`, `RocksDBStoreMetrics`, Ozone snapshot constants, and `RocksDBCheckpointDiffer`.

## Risks and Test Signals
Constructor failure calls `close`, but final fields such as `checkPointManager` may be uninitialized on early failures depending on Java initialization path. `dropTable` permanently removes column families. Global `RDBMetrics.unRegister` on close can affect other stores. WAL delta logic must handle sequence gaps accurately to trigger full snapshot fallback. Tests should cover open/close success and failure cleanup, read-only close no-flush, checkpoint/snapshot dirs disabled, metrics enable/disable, compaction DAG required CFs, table not found, batch commit, flush/compact/drop, getUpdatesSince sequence gaps/limits/size threshold/latest sequence, and multiple-store metrics interactions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBStoreAbstractIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBStoreAbstractIterator.java

## Purpose
`RDBStoreAbstractIterator<RAW>` is the shared base for raw RocksDB table iterators. It implements `Table.KeyValueIterator<RAW, RAW>` over a managed Rocks iterator, with optional prefix restriction and delete-current-entry support.

## Important APIs and Types
Subclasses provide `key`, `getKeyValue`, `seek0`, `delete`, and `startsWithPrefix`. Implemented methods include `hasNext`, `next`, `seekToFirst`, `seekToLast`, `seek`, `removeFromDB`, `forEachRemaining`, and `close`.

## Control Flow and State
The iterator stores the managed Rocks iterator, optional table reference, optional prefix, iterator type, current entry, and an atomic close flag. `hasNext` returns false if the table DB is closed or Rocks iterator is invalid or prefix no longer matches. `next` captures current key/value, advances the Rocks iterator, and returns the captured entry. Prefix-limited `seekToFirst` seeks to the prefix; prefix-limited `seekToLast` is unsupported.

## Persistence, Dependencies, and Integration
Iteration reads persistent RocksDB data. `removeFromDB` mutates the table by deleting the current entry key. Dependencies include `ManagedRocksIterator`, `RDBTable`, table iterator contracts, and RocksDB exceptions.

## Risks and Test Signals
Callers must close iterators to maintain accurate resource/refcounting. `removeFromDB` depends on `currentEntry`, which is set by `next`/seek methods, not merely `hasNext`. Tests should cover empty iteration, prefix boundaries, DB-closed behavior, seek/seekToFirst/seekToLast, remove before/after next, double close idempotency, and iterator type key/value read flags.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBStoreAbstractIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBStoreByteArrayIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBStoreByteArrayIterator.java

## Purpose
`RDBStoreByteArrayIterator` is the byte-array concrete implementation of `RDBStoreAbstractIterator`. It adapts RocksDB raw byte keys and values into `Table.KeyValue<byte[], byte[]>` records.

## Important APIs and Types
The constructor copies a non-empty prefix, stores the table/iterator/type through the superclass, and immediately seeks to the first matching entry. Implementations provide `key`, `getKeyValue`, `seek0`, `delete`, and `startsWithPrefix`.

## Control Flow and State
`getKeyValue` reads key and/or value depending on `IteratorType` flags, allowing key-only or value-only iteration. `startsWithPrefix` compares prefix bytes manually and treats null prefix as unrestricted.

## Persistence, Dependencies, and Integration
It reads from and can delete entries in a RocksDB-backed `RDBTable`. It depends on `ManagedRocksIterator`, `IteratorType`, and table key/value helpers.

## Risks and Test Signals
RocksDB byte arrays are exposed directly for current iterator values; callers should not assume long-lived defensive copies unless Rocks iterator semantics guarantee them. Tests should cover prefix copying isolation, empty prefix treated as no prefix, key/value read flags, seek behavior, delete behavior, short key mismatch, null key handling in prefix checks, and close through the superclass.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBStoreByteArrayIterator.java -->

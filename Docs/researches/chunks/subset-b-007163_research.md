# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.7.2.xml lines 24377-30557

## Scope

This chunk is a JDiff API-description slice for Hadoop Common 2.7.2. It starts at the tail of the `org.apache.hadoop.metrics2.lib.MutableQuantiles` documentation, covers metrics helper/sink/util APIs, network topology and socket factory APIs, the deprecated Hadoop Record I/O runtime and compiler surface, selected security mapping and credential-provider APIs, HTTP delegation-token authentication APIs, and ends inside the beginning of `org.apache.hadoop.service.AbstractService`.

Because the source is generated XML API metadata rather than executable Java source, control-flow and state notes are inferred from public method contracts, inheritance, synchronization flags, exceptions, and documentation text. The slice is still operationally useful: it captures the public compatibility contract that Hadoop clients, services, metrics sinks, network topology providers, record-compiler tools, and security-token integrations were expected to preserve in the 2.7.2 common module.

## Purpose

The metrics portion defines mutable rate/statistic primitives and sinks used by Hadoop daemons to publish operational measurements. `MutableRate`, `MutableRates`, and `MutableStat` accumulate latency/throughput samples and snapshot them into `MetricsRecordBuilder`; `FileSink` and `GraphiteSink` export records to local files or Graphite; `MBeans`, `MetricsCache`, and `Servers` help expose, cache, and address metrics.

The network portion defines pluggable host-to-rack resolution and socket creation. `DNSToSwitchMapping` is the contract used by block placement and other topology-aware code. `AbstractDNSToSwitchMapping`, `CachedDNSToSwitchMapping`, `ScriptBasedMapping`, and `TableMapping` provide common mapping, caching, script-based, and file/table-based behavior. `StandardSocketFactory` and `SocksSocketFactory` are `javax.net.SocketFactory` implementations used by client networking, with the SOCKS variant configurable through Hadoop `Configuration`.

The Record I/O portion documents Hadoop's older serialization system, explicitly deprecated in favor of Avro across many classes. It includes binary, CSV, and XML `RecordInput`/`RecordOutput` implementations, `Buffer`, `Record`, `RecordComparator`, low-level varint helpers, type metadata classes, compiler AST/type classes, an Ant task, and JavaCC-generated parser/lexer classes.

The security portion defines group and ID mapping provider contracts, an authentication-method enum entry point, credential-provider abstractions for secret storage, and web delegation-token clients/authenticators. These APIs integrate Hadoop identity, alias-backed credentials, HTTP authentication, Kerberos/SPNEGO fallback, pseudo authentication, proxy-user `doAs`, and delegation-token lifecycle operations.

The final service portion begins `AbstractService`, Hadoop's base class for lifecycle-managed components. In this chunk it exposes service construction, state/failure accessors, configuration setting, `init`, `start`, `stop`, `close`, failure recording, and the beginning of stop-wait behavior.

## Important APIs, Types, and Functions

- `org.apache.hadoop.metrics2.lib.MutableRate` extends `MutableStat` as a convenience metric for throughput measurement.
- `MutableRates` extends `MutableMetric` and provides `init(Class protocol)`, `add(String name, long elapsed)`, and `snapshot(MetricsRecordBuilder rb, boolean all)`. Its `init` method pre-registers protocol methods so JMX output includes all rates in the first snapshot.
- `MutableStat` extends `MutableMetric`, has constructors with metric name/description/sample/value labels and optional extended statistics, synchronized `setExtended(boolean)`, synchronized `add(long numSamples, long sum)`, synchronized `add(long value)`, synchronized `snapshot(...)`, and `resetMinMax()`.
- `FileSink` and `GraphiteSink` both implement `MetricsSink` and `Closeable` with `init(SubsetConfiguration)`, `putMetrics(MetricsRecord)`, `flush()`, and `close()`.
- `MBeans.register(String serviceName, String nameName, Object theMbean)` registers an MBean under the standard `hadoop:service=<serviceName>,name=<nameName>` naming convention and returns the `ObjectName`; `unregister(ObjectName)` removes it.
- `MetricsCache` has default and max-record constructors, `update(MetricsRecord, boolean includingTags)`, `update(MetricsRecord)`, and `get(String name, Collection tags)` for sinks that need dense records rather than sparse metric deltas.
- `Servers.parse(String specs, int defaultPort)` parses space/comma-separated `hostname` or `hostname:port` specifications, defaulting to localhost at the supplied port when specs are null.
- `DNSToSwitchMapping` defines `resolve(List names)`, `reloadCachedMappings()`, and `reloadCachedMappings(List names)` for pluggable rack/switch lookup.
- `AbstractDNSToSwitchMapping` implements `DNSToSwitchMapping` and `Configurable`; it stores configuration, reports whether a mapping is single-switch, exposes diagnostics through `getSwitchMap()` and `dumpTopology()`, and provides `isMappingSingleSwitch(DNSToSwitchMapping)`.
- `CachedDNSToSwitchMapping` wraps a raw `DNSToSwitchMapping`, caches host-to-switch answers, exposes its `rawMapping` field, delegates unresolved names, and can reload all or selected cached mappings.
- `ScriptBasedMapping` extends the cached mapping with script-backed topology lookup. It has constructors for default configuration, raw mapping, and explicit `Configuration`, plus `setConf`, `getConf`, `toString`, and `NO_SCRIPT`.
- `TableMapping` extends `CachedDNSToSwitchMapping` and supports configuration-driven, reloadable host/rack mappings from a table file.
- `ConnectTimeoutException` extends `SocketTimeoutException` for `NetUtils.connect(...)` timeout failures.
- `SocksSocketFactory` and `StandardSocketFactory` provide the five standard `createSocket` overloads plus equality/hash behavior; `SocksSocketFactory` also implements `Configurable` and can be built from a supplied `Proxy`.
- `RecordInput` and `RecordOutput` define the serialization contract: primitive read/write methods, `Buffer` support, and start/end markers for records, vectors, and maps.
- `BinaryRecordInput`, `CsvRecordInput`, and `XmlRecordInput` implement `RecordInput`; `BinaryRecordOutput`, `CsvRecordOutput`, and `XmlRecordOutput` implement `RecordOutput`.
- `BinaryRecordInput.get(DataInput)` and `BinaryRecordOutput.get(DataOutput)` are documented as thread-local helpers, so caller code may reuse per-thread wrappers over changing underlying data streams.
- `Buffer` is a comparable, cloneable byte-sequence type with constructors over empty storage, full byte arrays, and byte ranges; mutation/access methods include `set`, `copy`, `get`, `getCount`, `getCapacity`, `setCapacity`, `reset`, `truncate`, and two `append` overloads.
- `Record` is an abstract generated-record base class implementing `WritableComparable` and `Cloneable`, with tagged and untagged `serialize`/`deserialize`, plus Hadoop `write(DataOutput)` and `readFields(DataInput)`.
- `RecordComparator` extends `WritableComparator` and registers optimized comparators for `Record` implementations through `define(Class, RecordComparator)`.
- `org.apache.hadoop.record.Utils` provides float/double parsing from byte arrays, zero-compressed variable-length integer and long read/write helpers, encoded-length calculation, and lexicographic byte comparison.
- `org.apache.hadoop.record.compiler` includes `CodeBuffer`, `Consts`, primitive/composite `JType` classes (`JBoolean`, `JBuffer`, `JByte`, `JDouble`, `JFloat`, `JInt`, `JLong`, `JMap`, `JRecord`, `JString`, `JVector`), `JField`, and `JFile.genCode(String language, String destDir)` for record DDL code generation.
- `RccTask` is an Ant `Task` with setters for language, file, fail-on-error, destination directory, file sets, and `execute()` to run the record compiler.
- `org.apache.hadoop.record.compiler.generated.Rcc` is the JavaCC parser driver with constructors over input streams, readers, and token managers; parsing methods include `Input`, `Include`, `Module`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`.
- Generated compiler support includes `RccConstants` token IDs and lexical states, `RccTokenManager`, `SimpleCharStream`, `Token`, `ParseException`, and `TokenMgrError`.
- `org.apache.hadoop.record.meta` provides `TypeID` constants for primitive record types, `MapTypeID`, `VectorTypeID`, `StructTypeID`, `FieldTypeInfo`, `RecordTypeInfo`, and metadata `Utils.skip(DataInput, byte)` for skipping serialized values by type.
- `GroupMappingServiceProvider` defines group lookup plus cache refresh/add methods and `GROUP_MAPPING_CONFIG_PREFIX`.
- `IdMappingServiceProvider` maps user/group names to numeric IDs and back, with strict and unknown-tolerant variants: `getUid`, `getGid`, `getUserName`, `getGroupName`, `getUidAllowingUnknown`, and `getGidAllowingUnknown`.
- `UserGroupInformation.AuthenticationMethod` is an enum surface with `values`, `valueOf(String)`, and `getAuthMethod()` returning `SaslRpcServer.AuthMethod`.
- `CredentialProvider` defines transient-vs-persistent provider detection, `flush()`, alias listing, credential retrieval/creation/deletion, and `CLEAR_TEXT_FALLBACK`.
- `CredentialProviderFactory` creates providers from a configuration path via `createProvider(URI, Configuration)` and `getProviders(Configuration)`, keyed by `CREDENTIAL_PROVIDER_PATH`.
- `DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` and adds default-authenticator configuration, query-string delegation-token mode, authenticated `HttpURLConnection` creation, and delegation-token get/renew/cancel overloads with optional `doAsUser`.
- `DelegationTokenAuthenticatedURL.Token` extends `AuthenticatedURL.Token` and stores a Hadoop `Token` delegation token through `getDelegationToken()` and `setDelegationToken(Token)`.
- `DelegationTokenAuthenticator` wraps an `Authenticator` and exposes connection configurator propagation, `authenticate`, token get/renew/cancel overloads, and public parameter/header/JSON field constants such as `OP_PARAM`, `DELEGATION_TOKEN_HEADER`, `DELEGATION_PARAM`, `TOKEN_PARAM`, and `RENEWER_PARAM`.
- `KerberosDelegationTokenAuthenticator` provides Kerberos SPNEGO plus delegation-token operations and falls back to `PseudoDelegationTokenAuthenticator` when the HTTP endpoint does not trigger SPNEGO.
- `PseudoDelegationTokenAuthenticator` provides Hadoop pseudo/simple authentication using a query-string user name based on `UserGroupInformation.getCurrentUser()`.
- `AbstractService` implements `Service` and begins the lifecycle API with constructor `AbstractService(String name)`, `getServiceState`, synchronized failure accessors, protected `setConfig`, `init(Configuration)`, `start()`, `stop()`, final `close()`, final protected `noteFailure(Exception)`, and `waitForServiceToStop(long)`.

## Control Flow

Metrics control flow is sample accumulation followed by snapshot/export. Producers call `MutableRate` or `MutableStat.add(...)`; synchronized `MutableStat` mutators serialize updates to current sample state and extended-stat toggles. A metrics system later calls `snapshot(MetricsRecordBuilder, boolean)`, which emits counters/gauges into the record builder. `MutableRates.init(protocol)` pre-populates metrics from a protocol class before samples arrive so first-snapshot/JMX consumers see stable names. Sinks receive configured state through `init(SubsetConfiguration)`, consume records in `putMetrics`, and flush or close their outputs.

Metrics cache control flow fills gaps for sinks that do not handle sparse updates. Each incoming `MetricsRecord` updates a cached record keyed by name and tags; callers can choose whether tag values are included for later lookup. Sinks such as file or Graphite exporters can then emit complete records using cached data rather than only the fields present in an individual update.

Network topology resolution flows through `DNSToSwitchMapping.resolve(List)`. Hadoop topology-aware code supplies hostnames or IP addresses and expects a returned list in the same order and size, with `null` indicating failure. `CachedDNSToSwitchMapping` filters out names already present in cache, delegates misses to the raw mapping, then serves future lookups from memory. Reload methods either invalidate all cached mappings or selected nodes. `AbstractDNSToSwitchMapping.dumpTopology()` provides diagnostic flow by collecting known mappings and switch counts.

Script/table topology providers layer configuration over the same contract. `ScriptBasedMapping.setConf(Configuration)` configures the script-backed raw resolver; if no script is configured, `NO_SCRIPT` appears in string diagnostics and the mapping behaves as a default/single-policy resolver depending on implementation. `TableMapping.reloadCachedMappings()` refreshes its table-backed raw map and invalidates cached entries so subsequent `resolve` calls see updated rack assignments.

Socket factory flow is the standard Java networking path. Hadoop clients obtain a `SocketFactory`, call one of the overloaded `createSocket` methods, and either get direct sockets from `StandardSocketFactory` or proxy-routed sockets from `SocksSocketFactory`. The configurable SOCKS factory reads Hadoop configuration to construct or update its proxy settings; equality/hash behavior allows factories to be compared or cached.

Record I/O runtime flow is serializer-implementation dependent but contractually uniform. Generated `Record` classes call `RecordOutput.startRecord`, primitive/vector/map write methods, and `endRecord`; deserialization mirrors that through `RecordInput.startRecord`, primitive reads, index-based vector/map loops, and end markers. Binary implementations use compact binary and zero-compressed integer utilities; CSV and XML implementations add format-specific escaping and structural markers. `Record.write/readFields` bridge generated records to Hadoop `Writable` APIs.

Record compiler flow starts from `.jr` record definitions. The generated `Rcc` parser reads input through `SimpleCharStream` and `RccTokenManager`, builds compiler model objects such as `JFile`, `JRecord`, `JField`, and `JType`, and `JFile.genCode` emits source for the selected language into a destination directory. `RccTask.execute()` wraps that driver for Ant builds, applying language, destination, file, file-set, and fail-on-error settings.

Record metadata flow lets code describe and skip serialized records without binding to a generated Java class. `RecordTypeInfo` stores a record name and ordered field type information, can serialize/deserialize itself, and can find nested struct type info by name. `TypeID` subclasses encode primitive, map, vector, and struct shapes; metadata `Utils.skip` uses type IDs to consume serialized data from a stream.

Security mapping flow is provider-driven. Group mapping services receive a user name, return group memberships, and expose cache refresh/add hooks for administrative updates. ID mapping providers translate between user/group names and integer IDs, with unknown-tolerant methods for protocols such as NFS that may encounter unmapped principals.

Credential-provider flow is path/configuration based. `CredentialProviderFactory.getProviders(conf)` reads configured provider URIs and creates provider instances. Applications call provider methods to list aliases, retrieve credential entries, create new entries, delete entries, and call `flush()` so durable providers write changes to their backing store. `isTransient()` differentiates in-memory/non-persistent providers from persistent stores.

Web delegation-token flow layers token operations on top of `AuthenticatedURL`. `DelegationTokenAuthenticatedURL.openConnection(...)` authenticates using either an existing delegation token in its nested `Token` object or the configured authenticator. Token acquisition authenticates the user and stores/returns a Hadoop delegation token; renewal authenticates with the configured authenticator and returns a new expiration time; cancellation sends the token to the server endpoint and intentionally does not require authenticator-based login. Overloads carrying `doAsUser` propagate proxy-user identity to server-side token ownership/operation semantics.

`DelegationTokenAuthenticator` control flow is wrapper-oriented: it delegates base HTTP authentication to an inner `Authenticator`, applies any `ConnectionConfigurator`, and then performs delegation-token operations using documented query parameters, headers, and JSON response field names. The Kerberos subclass first attempts SPNEGO-capable behavior and can fall back to pseudo authentication; the pseudo subclass trusts the current Hadoop user identity and serializes it as an HTTP query parameter.

`AbstractService` lifecycle flow begins with `init(conf)`, moves through `start()`, and ends at `stop()` or `close()`. The public methods enforce service-state transitions and delegate implementation work to lifecycle hooks outside this chunk (`serviceInit`, `serviceStart`, `serviceStop` are referenced but not fully visible here). Failures are recorded through `noteFailure`, and callers can inspect both the throwable cause and the service state in which failure happened.

## State and Persistence Behavior

The XML file itself is generated API metadata and has no runtime persistence behavior. Runtime state and durability are implied by the public contracts it describes.

Metrics classes are in-memory mutable state holders until a snapshot is taken. `MutableStat` keeps running sample counts, sums, min/max, and optional extended statistics; synchronized methods imply concurrency-sensitive in-memory state. `resetMinMax()` explicitly clears all-time min/max state. `FileSink` persists emitted metrics to a file, while `GraphiteSink` sends them to an external Graphite endpoint; both need `flush()` and `close()` handling to avoid losing buffered data. `MetricsCache` stores the latest metric/tag values in memory and may evict or reject records based on the configured max-records-per-name limit.

Network topology mappings are local cached state over external or configurable sources. `CachedDNSToSwitchMapping` maintains host-to-switch memory state and exposes a copy for diagnostics. `ScriptBasedMapping` depends on configured script path/arguments and process execution outside this XML surface. `TableMapping` persists its authoritative mapping in a configuration-specified table file and refreshes in-memory state on reload. Stale mappings directly affect rack-aware scheduling and block placement decisions until refreshed.

Socket factories hold little durable state, but `SocksSocketFactory` keeps configuration/proxy state. Equality and hash code behavior matter if factories are used as keys or cached by RPC/client code.

Record I/O persists application data to binary, CSV, or XML streams through `RecordOutput` and restores it through `RecordInput`. `Buffer` owns mutable byte-array storage with distinct count and capacity, so `get()` exposes underlying storage rather than necessarily a right-sized copy. `RecordTypeInfo` is itself a serializable `Record`, so schema/type metadata can travel in files or RPC streams with record data. The compiler and generated parser hold transient parse/token buffers and write generated source files as their durable output.

Security providers model both transient and durable state. Group and ID mapping providers typically cache OS, LDAP, shell, or service-backed identity data; cache refresh/add methods are part of the public contract. `CredentialProvider` implementations may be transient or persistent; persistent stores require `flush()` to write changes. Credential aliases and entries represent sensitive state and must preserve delete/create semantics and clear-text fallback policy.

Delegation-token classes hold authentication cookies and Hadoop delegation tokens client-side. The nested `DelegationTokenAuthenticatedURL.Token` combines the base authenticated URL token state with a Hadoop delegation token. Server-side token acquisition, renewal, and cancellation mutate remote token-manager state even though the client API only exposes HTTP calls and returned expiration timestamps. Query-string transmission mode persists sensitive token material into URLs and potentially logs, caches, or proxies, so its state exposure differs from header transmission.

`AbstractService` holds lifecycle state, configuration, failure cause, and failure state. `getFailureCause()` and `getFailureState()` are synchronized, implying cross-thread visibility requirements after lifecycle failures. `close()` is final and delegates to `stop()`, so service implementations cannot bypass the common close/stop contract.

## Dependencies and Integration Points

The metrics APIs integrate with `org.apache.hadoop.metrics2` core interfaces: `MutableMetric`, `MetricsRecordBuilder`, `MetricsRecord`, `MetricsSink`, and Apache Commons Configuration `SubsetConfiguration`. Export paths integrate with JMX (`MBeans` and `javax.management.ObjectName`), local I/O (`FileSink`), Graphite's plaintext network protocol (`GraphiteSink`), and Java networking (`InetSocketAddress` through `Servers.parse`).

Network APIs integrate with Hadoop configuration (`Configurable`, `Configuration`), topology-aware HDFS policies, `NetUtils`, Java sockets, `SocketTimeoutException`, `SocketFactory`, `Proxy`, `InetAddress`, `SocketAddress`, and external mapping sources such as scripts and table files. The `isSingleSwitch` and `isMappingSingleSwitch` contracts are direct integration points for block placement and scheduling policies that distinguish single-rack from multi-rack clusters.

Record I/O integrates with Hadoop `WritableComparable`, `WritableComparator`, Java `DataInput`/`DataOutput`, `InputStream`/`OutputStream`, JavaCC-generated parser infrastructure, Ant task execution, and generated application record classes. Many classes explicitly document Avro as the replacement, so compatibility work must consider both legacy support and migration paths.

Record compiler APIs integrate with source generation pipelines, build tooling, JavaCC parser/token classes, language-specific code generators, and destination directories. The Ant task bridges Hadoop's record compiler into legacy build files through `org.apache.tools.ant.Task` and `FileSet`.

Security mapping integrates with `UserGroupInformation`, SASL RPC auth methods, OS/directory-service identity providers, cache management commands, and NFS-style numeric identity mapping. Credential providers integrate with `Configuration`, URI-based provider paths, keystores or other secret stores, and applications that resolve aliases instead of embedding passwords in clear text.

Delegation-token web APIs integrate with `org.apache.hadoop.security.authentication.client.AuthenticatedURL`, `Authenticator`, `ConnectionConfigurator`, `AuthenticationException`, `HttpURLConnection`, `URL`, Hadoop `Token`, Kerberos SPNEGO, pseudo authentication, proxy-user `doAs`, and server endpoints that implement the delegation-token HTTP protocol and JSON field names exposed as constants.

`AbstractService` integrates with `org.apache.hadoop.service.Service`, `Service.STATE`, `ServiceStateException`, `Configuration`, Java `Closeable`, and any Hadoop daemon/component that follows the common init/start/stop lifecycle.

## Risks and Edge Cases

Metrics update and snapshot semantics are concurrency-sensitive. `MutableStat` synchronizes important mutators, but `MutableRates` methods in this XML are not marked synchronized; implementations must still protect dynamic metric registration and per-name stat lookup when multiple RPC/client threads add samples. `resetMinMax()` is not marked synchronized in this metadata, which is a potential race area if reset can run concurrently with updates/snapshots.

Metrics sinks can lose data or block daemon progress. `FileSink` depends on file permissions, path validity, and flush/close discipline. `GraphiteSink` depends on network reachability and Graphite formatting; failure handling must avoid unbounded memory growth or service disruption. `MetricsCache` can produce misleading output if tags are excluded when a sink later expects tag-qualified records.

Topology mapping contracts require strict output alignment. `DNSToSwitchMapping.resolve` must return a list with one element per input in the same order; returning fewer, more, or reordered elements can corrupt rack placement. Stale caches after host moves or table/script changes can degrade HDFS placement until reload. `AbstractDNSToSwitchMapping.isMappingSingleSwitch` documentation is subtle: code must verify actual implementation behavior because the text describes special treatment for mappings not derived from the base class.

Script-based mapping is operationally fragile. Missing scripts, slow scripts, script output parse errors, and command-injection risks from hostnames can affect topology resolution. Table mappings risk stale or malformed files. Diagnostics from `dumpTopology()` and `getSwitchMap()` are snapshots and should not be treated as authoritative in concurrent reload scenarios.

SOCKS socket configuration can silently change network routing and security posture. Equality/hash behavior must include proxy-relevant state; otherwise caches may reuse incompatible factories. `ConnectTimeoutException` distinguishes connect timeout from other socket failures and should be preserved by callers that implement retry/backoff logic.

Record I/O is deprecated but still compatibility-sensitive. Binary/CSV/XML encodings must remain readable for legacy data. `Buffer.get()` exposing backing storage can leak mutable internal state if callers modify the returned array. Capacity/count mismatches, truncation, append bounds, clone/copy semantics, and lexicographic byte comparison are common edge cases. CSV/XML string and buffer escaping must round-trip delimiters, non-ASCII, binary data, and empty values.

Generated record comparison and serialization need stable ordering. `RecordComparator.define` changes comparator dispatch globally for a record class; wrong registration can corrupt sort/shuffle behavior. `Record.compareTo` and raw byte comparators must agree. Variable-length integer utilities must handle negative values, boundary values, malformed encodings, and EOF without truncation bugs.

Record compiler/parser classes are generated and easy to break with manual edits. `SimpleCharStream` manages line/column state, buffer expansion, backup, tab size, and begin/end token positions; off-by-one errors affect parse diagnostics. `ParseException` and `TokenMgrError` construct human-facing messages and escaped text; malformed or huge inputs can stress token buffers. Compiler deprecation reduces active coverage but does not remove public API compatibility obligations.

Credential-provider APIs handle sensitive material. Providers must reject duplicate alias creation, handle missing deletes, avoid leaking credential char arrays/entries, and ensure `flush()` is called for persistent stores. `CLEAR_TEXT_FALLBACK` can weaken security if enabled unexpectedly. URI parsing in `CredentialProviderFactory` must avoid accepting unsupported or malicious provider schemes.

Group and ID mapping providers can create authorization and ownership bugs. Cache refresh/add must be visible to subsequent lookups. Unknown-tolerant UID/GID methods need deterministic behavior for unmapped principals. Group membership ordering and duplicates can affect policy checks or tests.

Delegation-token URL handling is security-critical. Sending tokens in query strings can expose secrets through logs, browser/proxy caches, referrers, and monitoring systems; header mode is safer where supported. Token get/renew methods require authentication and can throw both `IOException` and `AuthenticationException`; cancellation intentionally does not require configured authenticator login, so the token itself must be sufficient proof. `doAsUser` propagation must be encoded and authorized consistently to avoid proxy-user escalation.

Kerberos-to-pseudo fallback improves interoperability but can mask server misconfiguration. Clients expecting strong SPNEGO authentication may accidentally proceed with pseudo auth if endpoint negotiation fails. Tests and deployments need explicit coverage of fallback enablement and failure behavior.

`AuthenticatedURL` instances are documented as not thread-safe, and `DelegationTokenAuthenticatedURL` inherits that warning. Sharing one instance or nested token object across threads can corrupt cookie/delegation-token state.

`AbstractService` lifecycle transitions are failure-prone under concurrency. `init` requires non-null configuration and valid state transitions; `start` and `stop` must reject illegal states. Failure cause should be recorded only once according to the doc for `noteFailure`. Since `close()` is final and relays to `stop()`, code must avoid assuming `close()` can throw implementation-specific cleanup exceptions beyond the `IOException` signature and stop behavior.

## Test Signals

Useful validation for this chunk should focus on API contract behavior across legacy and integration boundaries:

- Metrics tests for `MutableStat` constructors, synchronized sample addition, extended-stat toggling, snapshot contents with `all=true/false`, min/max reset, and concurrent add/snapshot/reset behavior.
- `MutableRates` tests that `init(protocol)` pre-creates method-rate metrics, `add(name, elapsed)` creates or updates the expected rate, and snapshots expose stable names for JMX consumers.
- `FileSink` and `GraphiteSink` tests for configuration parsing, put/flush/close behavior, output formatting, close idempotence, IO failures, and network failures without daemon crashes.
- `MetricsCache` tests for sparse update merging, tag-inclusive vs tag-exclusive lookup, max-records-per-name handling, record eviction/error behavior, and sinks that require dense output.
- `MBeans` tests for exact Hadoop object-name format, duplicate registration handling, unregister behavior, and invalid service/name inputs.
- `Servers.parse` tests for null specs, whitespace/comma combinations, host-only default ports, explicit ports, IPv6 or unusual host strings if supported, and malformed specifications.
- `DNSToSwitchMapping` implementation tests verifying output list size/order, null handling, failed resolutions, full and selective cache reload, `getSwitchMap` copy semantics, `dumpTopology` diagnostics, and `isSingleSwitch`/`isMappingSingleSwitch` policy results.
- `ScriptBasedMapping` tests for configured script execution, no-script fallback string, malformed output, timeout/slow script behavior, duplicate hosts, and configuration replacement through `setConf`.
- `TableMapping` tests for table-file parsing, reload after file changes, missing/malformed entries, cache invalidation, and default rack behavior.
- Socket factory tests for every `createSocket` overload, SOCKS proxy configuration, equality/hash differences between proxy settings, invalid proxy config, and connect timeout propagation through `ConnectTimeoutException`.
- Record I/O round-trip tests across binary, CSV, and XML for every primitive, strings with escapes/non-ASCII, empty and large `Buffer` values, nested records, vectors, maps, and malformed/EOF inputs.
- `Buffer` tests for count/capacity invariants, `set` vs `copy` aliasing, append growth, truncation, reset, clone independence, lexicographic `compareTo`, encoding-specific `toString`, equality, and hash code stability.
- `Record` and `RecordComparator` tests ensuring generated records serialize/deserialize through tagged and untagged APIs, `Writable` methods round-trip, raw comparators agree with object comparison, and comparator registration applies only to the intended class.
- `org.apache.hadoop.record.Utils` tests for variable-length integer/long boundary values, negative numbers, encoded sizes, byte-array and stream readers, malformed varints, float/double parsing, and byte comparison ordering.
- Record compiler tests for `Rcc.driver`, parser productions, include/module/record/type parsing, generated source output paths, invalid syntax diagnostics, JavaCC token positions, and Ant `RccTask` fail-on-error behavior.
- Record metadata tests for `TypeID` equality/hash behavior, map/vector/struct nested types, `RecordTypeInfo` serialize/deserialize, nested struct lookup, field ordering, and `meta.Utils.skip` consuming exactly the expected bytes.
- Group and ID mapping provider tests for cache refresh/add semantics, duplicate and unknown groups/users, unknown-tolerant UID/GID behavior, and integration with `UserGroupInformation`.
- Credential provider tests for provider discovery from `CREDENTIAL_PROVIDER_PATH`, URI scheme validation, transient vs persistent providers, create/get/list/delete aliases, duplicate alias rejection, missing alias behavior, `flush()` durability, and clear-text fallback policy.
- Delegation-token URL tests for default authenticator get/set, header vs query-string token transmission, authenticated open connection with and without an existing delegation token, get/renew/cancel with and without `doAsUser`, IO/authentication exception surfaces, JSON parsing, and token storage in the nested token object.
- Kerberos and pseudo authenticator tests for SPNEGO success, SPNEGO fallback to pseudo when appropriate, pseudo user parameter construction from current UGI, connection configurator propagation, and no accidental fallback when strong authentication is required.
- `AbstractService` tests for legal state transitions, null configuration rejection, failure recording, failure-cause visibility across threads, `close()` calling `stop()`, stop wait behavior, and subclass hook invocation order.

## Cross-Chunk Notes

This chunk begins in the middle of `MutableQuantiles` documentation and ends before the full `AbstractService` API entry is complete. Adjacent chunks should supply the preceding metrics classes and the remainder of `org.apache.hadoop.service`. The merge lane should keep this document tied to the JDiff XML source and distinguish API compatibility metadata from implementation details that need confirmation in the corresponding Java classes under Hadoop Common.

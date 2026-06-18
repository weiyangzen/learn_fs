# Research Report: subset-b-008438

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/PartitionedLogIterator.h -->
# sources/storage-engines/foundationdb/fdbclient/PartitionedLogIterator.h

## Purpose
`PartitionedLogIterator.h` defines the minimal reference-counted interface used to iterate partitioned mutation logs. It also defines `VersionedMutation`, the value object returned by the iterator, combining a database `Version`, a per-version `subsequence`, and a `MutationRef`.

## Important APIs, Types, and Functions
- `VersionedMutation` stores one mutation plus ordering metadata. Its arena-copy constructor deep-copies the `MutationRef` into the supplied `Arena`, while preserving version and subsequence.
- `PartitionedLogIterator` derives from `ReferenceCounted<PartitionedLogIterator>`, so callers generally hold it through `Reference<>`.
- `hasNext()` is a synchronous availability check.
- `peekNextVersion()` asynchronously exposes the next available version without consuming it.
- `getNext()` asynchronously returns a `Standalone<VectorRef<VersionedMutation>>`, making returned mutation batches self-owned through the standalone arena.

## Control Flow and State
This header contains no concrete iteration logic. Implementations are expected to maintain cursor state, answer `hasNext`, support version peeking, and advance on `getNext`. The interface separates cheap local availability from asynchronous storage or network reads.

## State and Persistence Behavior
The interface itself is in-memory only. Persistence belongs to the backing mutation-log implementation. `VersionedMutation`'s arena-aware copy is important because mutation refs are arena-backed and must remain valid after a batch crosses actor boundaries.

## Dependencies and Integration Points
The file depends on `fdbclient/FDBTypes.h` for `Version`, `MutationRef`, `Arena`, `VectorRef`, `Standalone`, `Future`, and reference counting. Consumers likely include backup, restore, or mutation-log readers that need ordered mutation replay across partitioned logs.

## Risks and Edge Cases
- Implementations must preserve ordering by `(version, subsequence)` across partitions, because this type exposes both fields but does not enforce ordering.
- `hasNext()` can race with asynchronous source changes unless implementers define stable cursor semantics.
- Returning refs without copying into the returned standalone arena would create lifetime bugs.

## Test Signals
Useful tests should cover empty logs, `peekNextVersion()` not consuming entries, arena lifetime of returned mutations, multi-mutation batches at the same version, and cross-partition ordering around subsequence boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/PartitionedLogIterator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/Printable.cpp -->
# sources/storage-engines/foundationdb/fdbclient/Printable.cpp

## Purpose
`Printable.cpp` centralizes human-readable formatting and reverse parsing helpers for FDB key/value types. It is mainly diagnostic infrastructure used by tests, trace details, and debug output.

## Important APIs, Types, and Functions
- `printable(VectorRef<KeyValueRef>)` renders each key using key escaping and appends the value size.
- `printable(KeyValueRef)` renders a single key/value size pair.
- `printable(VectorRef<StringRef>)`, `printable(StringRef)`, and `printable(std::string)` all route through `StringRef::printable()`.
- `printable(KeyRangeRef)` and `printable(VectorRef<KeyRangeRef>)` render begin/end bounds.
- `unhex(char)` decodes one hex digit and asserts unreachable for invalid input.
- `unprintable(std::string const&)` reverses the `StringRef::printable()` escaping subset it expects: escaped backslash and `\xNN` bytes.

## Control Flow and State
All helpers are stateless and allocate a fresh `std::string` result. Vector overloads iterate in order and concatenate with spaces. `unprintable` scans byte by byte, switches on backslash escapes, and asserts on malformed trailing or unknown escapes.

## State and Persistence Behavior
There is no persistent state. The functions intentionally expose only value sizes for `KeyValueRef` values, avoiding dumping potentially large or sensitive value bytes in common debug paths.

## Dependencies and Integration Points
The file includes `fdbclient/FDBTypes.h` for FoundationDB ref types, `format`, assertions, and `StringRef::printable()`. It is integrated with tests such as `RYWIterator.cpp` and debugging routines that need stable escaped byte strings.

## Risks and Edge Cases
- `unprintable` uses assertions rather than returning errors, so it is appropriate for trusted/debug input, not user-facing parsing.
- `unhex` treats invalid characters as unreachable, making malformed `\x` escapes fatal in assertion-enabled builds.
- The vector formatting has trailing spaces; downstream comparisons should account for that existing behavior.

## Test Signals
Round-trip tests should include empty strings, backslashes, embedded zero bytes, high-bit bytes, malformed escapes under assertion builds, and range/vector formatting stability.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/Printable.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ProxyLoadBalance.h -->
# sources/storage-engines/foundationdb/fdbclient/ProxyLoadBalance.h

## Purpose
`ProxyLoadBalance.h` provides coroutine helpers for sending requests to commit proxies and GRV proxies while retrying if the database proxy set changes before a reply arrives. It wraps `basicLoadBalance` with proxy-change awareness.

## Important APIs, Types, and Functions
- `ReqBuilder<Req, Args...>` stores constructor arguments and rebuilds a fresh request for every retry.
- `makeReqBuilder<Req>(Args&&...)` decays and validates constructor argument types with `std::is_constructible_v`.
- `commitProxyLoadBalance` takes a commit-proxy channel pointer, optional provisional proxy selection, task priority, and `AtMostOnce` setting.
- The overload without explicit provisional/task parameters uses non-provisional proxies and `cx->taskID`.
- `grvProxyLoadBalance` mirrors the pattern for `GrvProxyInterface`.

## Control Flow and State
Each load-balancer function loops forever until a reply wins a `race` against `cx->onProxiesChanged()`. If the reply wins, it returns the reply. If the proxy-change future wins, it discards the in-flight result and rebuilds the request for the new proxy set.

## State and Persistence Behavior
The helpers keep only local request-builder state. They do not persist or mutate database state directly. `AtMostOnce` is passed through to `basicLoadBalance`, so callers must choose retry semantics suitable for idempotent or non-idempotent requests.

## Dependencies and Integration Points
The file depends on commit/GRV proxy interfaces, `NativeAPI.actor.h` for `Database`, and `fdbrpc/LoadBalance.actor.h` for `basicLoadBalance`. It is a template header so callers get strongly typed request and reply inference through `REPLY_TYPE(Req)`.

## Risks and Edge Cases
- Retrying on proxy changes can duplicate requests unless the channel semantics and `AtMostOnce` choice are correct.
- The request builder assumes constructor arguments are safe to store and reuse. Mutable references should be avoided because arguments are decayed and captured by value.
- A constantly changing proxy set can starve the reply path.

## Test Signals
Tests should simulate proxy-change races, request reconstruction on retry, provisional commit proxy selection, GRV proxy calls, and `AtMostOnce` behavior for requests where duplicate delivery would be harmful.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ProxyLoadBalance.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/RESTClient.cpp -->
# sources/storage-engines/foundationdb/fdbclient/RESTClient.cpp

## Purpose
`RESTClient.cpp` implements a generic asynchronous REST client on top of FoundationDB Flow networking and `fdbrpc/HTTP`. It parses URLs through `RESTUrl`, obtains pooled TCP/TLS connections, sends HTTP requests, retries selected failures, and records per-host statistics.

## Important APIs, Types, and Functions
- `RESTClient::Stats::getJSON`, `operator-`, and `clear` expose per `host:service` counters for successes, failures, and bytes sent.
- Constructors initialize a `RESTConnectionPool` with knob-derived pool size and optionally apply knob overrides.
- `setKnobs` and `getKnobs` delegate to `RESTClientKnobs`.
- `isErrorRetryable` decides which Flow errors should be retried by this client. The current implementation returns false for timeout and connection failure.
- `doRequest_impl` builds `HTTP::OutgoingRequest`, fills host/resource/body, obtains a pooled connection, performs `HTTP::doRequest`, handles connection reuse, classifies errors/status codes, backs off, and throws typed HTTP/connection errors.
- Public verb helpers are `doGet`, `doHead`, `doDelete`, `doTrace`, `doPut`, and `doPost`.

## Control Flow and State
For each request, `doRequest_impl` creates one request object and loops until success, non-retryable failure, or tries are exhausted. It checks out a `ReusableConnection`, applies connect and request timeouts separately, returns healthy keep-alive connections unless the response says `Connection: close`, and closes checked-out connections on exceptions to satisfy simulation connection assertions. Failures increment stats, emit throttled trace events, optionally honor `Retry-After`, and use exponential retry delay capped at 60 seconds.

## State and Persistence Behavior
State is process-local: knobs, connection pool, and `statsMap`. It does not persist request state. Reused connections are keyed by `host:service` and expire according to `max_connection_life`.

## Dependencies and Integration Points
The implementation depends on `RESTUtils` for URL parsing, knobs, and connection pooling; `fdbrpc/HTTP` for wire protocol; Flow actors, packet queues, rate controls, tracing, and unit tests. Higher-level clients, including blob-store code, can reuse this client pattern or its utilities.

## Risks and Edge Cases
- `doGetHeadDeleteOrTrace` accepts a `verb` argument but calls `doRequest_impl` with `HTTP::HTTP_VERB_GET`, so `HEAD`, `DELETE`, and `TRACE` requests appear to be sent as GET. This is a high-value regression test target.
- The retry classification comment says unreachable or timed-out servers should bubble to callers, and the implementation does not retry timeout/connection_failed even though the variable name can be confusing.
- `HTTP_STATUS_CODE_BAD_GATEWAY` is listed twice in retryable status checks.
- `TOO_MANY_REQUESTS` does not increment `thisTry`, so persistent 429s can continue beyond the nominal try count, bounded mainly by actor cancellation or external timeouts.
- Request body content is written once before retries; this is safe only because the request owns an `UnsentPacketQueue` that remains valid for the loop.

## Test Signals
The file includes a unit test for knob defaults, mutation, and invalid knob errors. Additional important tests should cover verb preservation for HEAD/DELETE/TRACE, `Retry-After`, 429 retry behavior, connection reuse/drop on `Connection: close`, timeout mapping to `connection_failed`, and stats counter updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/RESTClient.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/RESTClient.h -->
# sources/storage-engines/foundationdb/fdbclient/RESTClient.h

## Purpose
`RESTClient.h` declares the `RESTClient` interface for sending common HTTP REST verbs to a URL-backed resource with connection pooling, knobs, and statistics.

## Important APIs, Types, and Functions
- `RESTClient::Stats` is the externally visible stats record for one `host:service`.
- `RESTClientKnobs knobs` stores connection and request retry/timeout settings.
- `Reference<RESTConnectionPool> conectionPool` owns reusable network connections. The member name is misspelled as `conectionPool` and consumers must use that spelling.
- `statsMap` maps `host:service` strings to `Stats`.
- Public methods cover GET, HEAD, DELETE, TRACE, PUT, and POST. PUT/POST accept request bodies.
- `getStatsKey(host, service)` standardizes map keys.
- Private helpers split bodyless verbs and body verbs.

## Control Flow and State
The header defines asynchronous APIs returning `Future<Reference<HTTP::IncomingResponse>>`. Callers pass optional headers; methods parse full URLs internally and then dispatch through shared implementation helpers in the `.cpp` file.

## State and Persistence Behavior
All state is in-memory and scoped to the `RESTClient` instance. Stats accumulate until `clear` or object destruction. Connections are held in the pool and reused across requests to the same endpoint.

## Dependencies and Integration Points
The header depends on `JSONDoc`, `fdbrpc/HTTP`, `RESTUtils`, Flow arenas/ref counting, and packet types. It provides a generic REST layer used by code that does not need S3-specific signing or blob-store behavior.

## Risks and Edge Cases
- The public API exposes raw HTTP response objects, so callers must validate response bodies and headers themselves.
- Knob changes after construction update `knobs` but do not resize or rebuild existing connection-pool state immediately.
- The private helper split makes it easy for verb dispatch bugs to affect multiple public methods.

## Test Signals
Tests should instantiate default and override knob configurations, validate per-verb status-code acceptance, check optional header propagation, and verify stats JSON/delta behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/RESTClient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/RESTUtils.cpp -->
# sources/storage-engines/foundationdb/fdbclient/RESTUtils.cpp

## Purpose
`RESTUtils.cpp` implements REST connection pooling, supported protocol handling, REST client knob mapping, URL parsing, and a small continuous-time decay utility.

## Important APIs, Types, and Functions
- `RESTConnectionPool::~RESTConnectionPool` explicitly closes pooled connections in simulation.
- `RESTConnectionType::supportedConnTypes`, `getConnectionType`, `isProtocolSupported`, and `isSecure` support `http` and `https`.
- `RESTClientKnobs` initializes from Flow knobs and maps full names plus aliases such as `pz`, `ct`, `cto`, `mcl`, `rt`, and `rtom`.
- `connect_impl` reuses unexpired connections or creates a new connection with `INetworkConnections::net()->connect` and `connectHandshake`.
- `RESTConnectionPool::returnConnection` returns non-expired connections up to the per-key capacity.
- `RESTUrl::parseUrl` splits protocol, host, optional service, resource path, and query parameters.
- `continuousTimeDecay` computes `initialValue * exp(-decayRate * time)`.

## Control Flow and State
Connection acquisition first checks the queue for a matching `(host, service)` key, discarding expired entries. If no reusable connection exists, it connects and records an expiration timestamp. Return logic pushes the connection back only if it remains unexpired and the queue is under capacity.

URL parsing uses `StringRef::eat` and `eatAny` to parse `<protocol>://<host>[:service][/resource][?params]`, defaulting the resource to `/`. Unsupported protocols and empty hosts become FoundationDB REST errors.

## State and Persistence Behavior
The connection pool is in-memory and keyed by host/service. Expiration is wall-clock/runtime state based on `now()`. Knobs are copied into the `RESTClientKnobs` object and are not persisted.

## Dependencies and Integration Points
The file integrates Flow networking, `IConnection`, Flow knobs, tracing, boost string utilities, and Flow unit tests. It is the utility backend for `RESTClient.cpp`.

## Risks and Edge Cases
- `RESTClientKnobs::set` asserts that the input key equals the stored map key. Alias keys satisfy this because the map key is the alias, but any future normalization must preserve that invariant.
- URL parsing is intentionally simple and does not fully implement RFC URL syntax, userinfo, IPv6 literals, or percent-decoding.
- Service can be empty, which depends on lower networking layers to choose defaults or fail clearly.
- Expired connections are popped but not explicitly closed outside the simulation destructor path.

## Test Signals
The file includes unit tests for invalid protocol, missing host, valid URI with/without service, extra slash paths, and query parameters. Additional coverage should check HTTP protocol security false, aliases in `RESTClientKnobs`, connection reuse capacity, expiration, and empty service handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/RESTUtils.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/RESTUtils.h -->
# sources/storage-engines/foundationdb/fdbclient/RESTUtils.h

## Purpose
`RESTUtils.h` declares the utility types that make the REST client work: connection-pool keys, reusable connections, supported protocols, REST knobs, parsed URLs, and a decay helper.

## Important APIs, Types, and Functions
- `RESTConnectionPoolKey` is `(host, service)`.
- `RESTLogSeverity` defines `INFO`, `DEBUG`, and `VERBOSE` levels checked against Flow REST logging knobs.
- `RESTConnectionPool::ReusableConnection` bundles `Reference<IConnection>` with an expiration time.
- `RESTConnectionPool` owns `connectionPoolMap`, connects, returns connections, and builds keys with `getConnectionPoolKey`.
- `RESTConnectionType` stores protocol plus secure flag and exposes supported protocol queries.
- `RESTClientKnobs` stores pool, connect, and request retry/timeout values, with `set`, `get`, and descriptions.
- `RESTUrl` exposes parsed `host`, `service`, `resource`, `reqParameters`, `body`, and `connType`.

## Control Flow and State
The declarations establish an explicit checkout/return connection lifecycle. `RESTUrl` construction immediately parses and validates a full URL. `RESTClientKnobs` is mutable, letting clients adjust request behavior at runtime.

## State and Persistence Behavior
All state is local to objects using this header. `connectionPoolMap` queues reusable connections by endpoint. `RESTUrl` stores a copy of parsed URL data and request body.

## Dependencies and Integration Points
The header depends on Flow futures/ref counting/packet types, boost pair hashing for unordered map keys, and fmt formatting. It is included by both REST client implementation and likely any code constructing REST URLs or knobs.

## Risks and Edge Cases
- `max_connection_life` is documented as not fully implemented in `RESTClientKnobs`, although the pool uses a max-life value when creating expiration timestamps.
- `RESTUrl::toString` includes the request body, so verbose trace logging can expose payload data.
- `RESTConnectionType::secure` is an `int` rather than bool, reflecting existing serialization/logging conventions but requiring care in boolean contexts.

## Test Signals
Header-level behavior is covered through `RESTUtils.cpp` and `RESTClient.cpp` tests. Compile-time tests should ensure connection pool keys hash correctly and knob descriptions stay in sync with accepted knob names.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/RESTUtils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/RYWIterator.cpp -->
# sources/storage-engines/foundationdb/fdbclient/RYWIterator.cpp

## Purpose
`RYWIterator.cpp` implements the iterator that overlays a transaction's local `WriteMap` on top of its `SnapshotCache`. It is the low-level mechanism used by read-your-writes transactions to see local mutations, clears, dependent atomic operations, and cached snapshot reads as one ordered keyspace.

## Important APIs, Types, and Functions
- `RYWIterator::typeMap` maps the cartesian product of write segment type and cache segment type to `UNKNOWN_RANGE`, `EMPTY_RANGE`, or `KV`.
- `type`, `is_kv`, `is_unknown_range`, `is_empty_range`, `is_dependent`, and `is_unreadable` classify the current overlay segment.
- `beginKey` and `endKey` compute the current segment bounds from the write/cache boundary comparisons.
- `kv(Arena&)` returns the visible key/value, coalescing local write operations over cached values when needed, and returns `nullptr` for deletes produced by operations such as compare-and-clear.
- `operator++` and `operator--` advance both underlying iterators when segment boundaries are reached.
- `skip`, `skipContiguous`, and `skipContiguousBack` support positioning and efficient contiguous cache traversal.
- `extractWriteMapIterator` gives higher-level code access to the underlying write iterator for conflict tracking.

## Control Flow and State
The iterator maintains a `SnapshotCache::iterator`, a `WriteMap::iterator`, and cached comparison results between their begin/end keys. Movement advances whichever iterator owns the current boundary, then flips/recomputes comparisons. Reads first enforce unreadable protection unless bypassed, then either return cached data, local independent writes, or coalesced dependent writes over cached values.

## State and Persistence Behavior
State is transient and points into the transaction-owned arena/cache/write map. There is no persistence. The `temp` key/value is used to return a stable coalesced result until the iterator advances or another `kv` call overwrites it.

## Dependencies and Integration Points
The file depends on `fdbclient/RYWIterator.h`, `KeyRangeMap`, and Flow unit tests. It is tightly coupled to `ReadYourWrites.actor.cpp`, `SnapshotCache`, `WriteMap`, `OperationStack`, and mutation coalescing semantics.

## Risks and Edge Cases
- Unreadable versionstamp-related ranges must throw unless bypassed; bypass is used in targeted tests and internal paths.
- `kv` can return `nullptr` for logically deleted keys even when `is_kv()` is true, so callers must check.
- Correctness depends on `begin_key_cmp` and `end_key_cmp` staying in sync after every skip or movement.
- Coalescing dependent atomic operations over absent cached values is subtle and must match storage-server mutation semantics.

## Test Signals
This file contains extensive unit tests for `WriteMap` emptiness, clears, versionstamped key/value unreadability, atomic add coalescing, random mutation ranges, conflict map behavior, and debug-only snapshot cache iteration. Important additional signals are reverse iteration parity, contiguous skip correctness, and compare-and-clear deletion results.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/RYWIterator.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/RandomKeyValueUtils.cpp -->
# sources/storage-engines/foundationdb/fdbclient/RandomKeyValueUtils.cpp

## Purpose
`RandomKeyValueUtils.cpp` is a unit-test translation unit for random key/value generator helpers. It force-links tests and demonstrates generator grammar for integers, strings, key sets, tuple key sets, and values.

## Important APIs, Types, and Functions
- `printNextN` is a small templated diagnostic helper that prints generated values from any generator exposing `toString()` and `next()`.
- The `/randomKeyValueUtils/generate` test constructs `RandomIntGenerator`, `RandomStringGenerator`, `RandomKeySetGenerator`, `RandomKeyTupleGenerator`, `RandomKeyTupleSetGenerator`, and `RandomValueGenerator` from direct arguments and compact string specifications.
- `forceLinkRandomKeyValueUtilsTests` ensures the unit tests are linked into the test binary.

## Control Flow and State
The test repeatedly constructs generators and prints samples. It covers fixed ranges, reverse ranges, skew markers using `^`, fixed values, string length/character specs, indexed key sets, and multi-part tuple sets.

## State and Persistence Behavior
There is no persistent state. Generator state is local to each object and advances as `next()` is called. The test writes to stdout through `fmt::print`.

## Dependencies and Integration Points
The file includes `fdbclient/RandomKeyValueUtils.h` and Flow unit tests. These generators are useful for simulation workloads and randomized testing of keyspace behavior.

## Risks and Edge Cases
- The test is mostly observational; it prints generated samples but does not assert distribution or parser invariants.
- String grammar changes could silently alter output without failing this test.
- Randomness depends on the generator implementations and deterministic random state outside this file.

## Test Signals
Current coverage confirms the generator APIs compile and run for representative specs. Stronger tests should assert bounds, fixed-value behavior, reverse ranges, skew direction, tuple part counts, and generated key ordering/uniqueness guarantees where promised by the generator types.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/RandomKeyValueUtils.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ReadYourWrites.actor.cpp -->
# sources/storage-engines/foundationdb/fdbclient/ReadYourWrites.actor.cpp

## Purpose
`ReadYourWrites.actor.cpp` implements `ReadYourWritesTransaction`, the client-side transaction wrapper that provides FoundationDB read-your-writes semantics. It merges local mutations with cached snapshot reads, tracks conflict ranges, integrates special keyspace behavior, manages watches, options, retries, timeouts, and materializes buffered writes into the underlying native transaction at commit.

## Important APIs, Types, and Functions
- `RYWImpl` is an internal helper class containing request structs (`GetValueReq`, `GetKeyReq`, `GetRangeReq`, `GetMappedRangeReq`) and most read/commit actors.
- `read` overloads implement get, getKey, forward/reverse getRange, and limited getMappedRange behavior over either `SnapshotCache::iterator` or `RYWIterator`.
- `readThrough` bypasses the RYW overlay when `READ_YOUR_WRITES_DISABLE` is set and clips inaccessible system keys.
- `addConflictRange` and `updateConflictMap` derive read conflict ranges from resolved reads and local write-map state.
- `resolveKeySelectorFromCache`, `getKnownKeyRange`, `skipUncached`, `countUncached`, and their reverse variants drive incremental range reads and cache population.
- `triggerWatches`, `watch`, `commit`, `onError`, and `getReadVersion` implement transaction lifecycle behavior.
- Public `ReadYourWritesTransaction` methods wrap get/getRange/getMappedRange, conflict range APIs, mutations, atomic ops, commit, reset, cancel, options, debug logging, and special conflict-range introspection.

## Control Flow and State
Reads choose one of three paths: direct native transaction reads if RYW is disabled, snapshot-cache reads if snapshot RYW is disabled, or full RYW overlay reads through `RYWIterator`. Unknown cache ranges trigger native snapshot reads, insert known ranges into `SnapshotCache`, then re-resolve selectors. Serializable reads add conflicts only for unmodified or dependent-write segments where server-side state can affect the result.

Writes are buffered in `WriteMap` unless RYW is disabled. `set`, `clear`, and `atomicOp` validate key/value limits, update approximate transaction size, add conflict metadata unless disabled for the next write, and trigger local watches. At commit, the wrapper waits for outstanding reads, optionally commits special keyspace configuration changes, writes buffered clears before sets/atomic ops into the native transaction, forwards read conflicts, and commits the native transaction.

`onError` delegates retry policy to the native transaction, enforces retry limits, logs debug information, and resets the RYW cache/write/conflict/watch state for retry.

## State and Persistence Behavior
The durable commit is performed only by the underlying `Transaction`. Before commit, all RYW state is in memory: `arena`, `SnapshotCache`, `WriteMap`, `readConflicts`, `watchMap`, `nativeReadRanges`, `nativeWriteRanges`, versionstamp key tracking, special keyspace write map, timeout actor, retry counters, and persistent option vectors. `resetRyow` cancels old in-flight work through `resetPromise` and rebuilds all transient state.

## Dependencies and Integration Points
The file integrates `ReadYourWrites.h`, `NativeAPI.actor.h`, atomic mutation helpers, `DatabaseContext`, `SpecialKeySpace`, `StatusClient`, leader monitoring, Flow coroutine utilities, and actor compiler support. It is central to the FDB C/API transaction behavior and must preserve compatibility across API versions, especially for special keys, versionstamps, and option semantics.

## Risks and Edge Cases
- Range selector resolution is complex in both directions and must handle unknown ranges, single-key clears, row/byte limits, `readToBegin`, `readThroughEnd`, and inaccessible system-key boundaries.
- `getMappedRange` intentionally does not fully implement RYW; it performs native reads and throws `get_mapped_range_reads_your_writes` if relevant ranges were locally modified.
- Versionstamped key/value operations create unreadable ranges and special write-conflict behavior until the versionstamp is known.
- Using a transaction during commit sets `resetPromise` unless protection is disabled.
- API-version conditionals change reset-after-commit behavior, special key handling, mutation suffix compatibility, and cancellation semantics.
- Watch handling has to reconcile local writes racing with initial read and native watch registration.

## Test Signals
Direct tests live heavily in related iterator/write-map files, while this file exposes many simulation-code probes. High-value tests include forward/reverse range parity, conflict range special-key introspection, retries after `onError`, timeout behavior, special keyspace reads/writes by API version, versionstamp conflict keys before/after commit, watch triggering by local writes, disabled RYW direct-through behavior, and getMappedRange modified-range rejection.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ReadYourWrites.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/RestoreInterface.cpp -->
# sources/storage-engines/foundationdb/fdbclient/RestoreInterface.cpp

## Purpose
`RestoreInterface.cpp` defines the system keys and serialization helpers used to store and trigger restore requests in FoundationDB system keyspace.

## Important APIs, Types, and Functions
- `restoreRequestDoneKey` marks restore request completion state.
- `restoreRequestTriggerKey` stores the trigger value for restore workers.
- `restoreRequestKeys` is the range containing indexed restore request records.
- `restoreRequestTriggerValue(UID randomID, int numRequests)` serializes request count and random ID with `ProtocolVersion::withRestoreRequestTriggerValue()`.
- `decodeRestoreRequestTriggerValue(ValueRef const&)` reads the request count and random ID, returning only the count.
- `restoreRequestKeyFor(int index)` appends a binary index to the restore request key prefix.
- `restoreRequestValue(RestoreRequest const&)` serializes the full request with `ProtocolVersion::withRestoreRequestValue()`.

## Control Flow and State
The helpers are straight-line serialization/deserialization routines. Key construction uses an unversioned writer for the binary key suffix, while values include explicit protocol versions for compatibility.

## State and Persistence Behavior
The persistent state is the system keyspace data under `\xff\x02/restoreRequest...`. This file defines how restore requests and triggers are encoded into keys/values that other restore components consume.

## Dependencies and Integration Points
The file includes `RestoreInterface.h` and `flow/serialize.h`. It integrates with restore orchestration code that writes trigger keys and individual indexed requests, and with workers that read/decode them.

## Risks and Edge Cases
- The header declares `decodeRequestRequestTriggerValue`, but the implementation defines `decodeRestoreRequestTriggerValue`; that name mismatch should be checked against callers and build coverage.
- Serialization format changes require protocol-version updates and downgrade planning, as noted in the request type.
- Binary key encoding must remain stable because restore workers locate requests by index.

## Test Signals
Useful tests should round-trip trigger values and `RestoreRequest` values across protocol versions, validate indexed key ordering, check the declared/defined decode function name, and verify system key range boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/RestoreInterface.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/RestoreInterface.h -->
# sources/storage-engines/foundationdb/fdbclient/RestoreInterface.h

## Purpose
`RestoreInterface.h` declares the wire/storage contract for restore requests and replies. It defines serializable request/reply types plus system keys used to coordinate restore work.

## Important APIs, Types, and Functions
- `RestoreCommonReply` carries the replying server `UID` and an `isDuplicated` flag.
- `RestoreRequest` carries request index, backup tag, URL, optional proxy, target version, key range, random UID, prefix rewrite fields, and a reply promise.
- Both structs define `file_identifier` constants and Flow `serialize` methods.
- `toString` methods provide diagnostic output for tracing or logs.
- Extern keys identify done, trigger, and request ranges.
- Helper declarations cover trigger value encode/decode, per-index request keys, and request value serialization.

## Control Flow and State
This header is declarative. Restore clients construct `RestoreRequest` values, serialize them into system keyspace, and receive `RestoreCommonReply` asynchronously through `ReplyPromise`.

## State and Persistence Behavior
`RestoreRequest` values are persisted as serialized values under the restore request system-key prefix. Fields such as `targetVersion`, `range`, `addPrefix`, and `removePrefix` define how restored backup keys are transformed and bounded.

## Dependencies and Integration Points
The header depends on `FDBTypes.h` for keys, ranges, versions, and UIDs, and `fdbrpc/fdbrpc.h` for reply promises. It is part of the interface between restore coordinators and restore-capable server actors.

## Risks and Edge Cases
- The constructor takes `Key& addPrefix` non-const while storing by value, which is unnecessarily restrictive for callers.
- Comments warn that serialization changes require `ProtocolVersion::RestoreRequestValue` updates and downgrade consideration.
- Prefix rewrite semantics with both add and remove prefixes are not fully covered by simulation according to the inline comment.
- The declared decode helper name appears inconsistent with the `.cpp` implementation.

## Test Signals
Tests should cover serialization compatibility, duplicate reply formatting, prefix rewrite combinations, optional proxy handling, request key generation, and declaration/definition linkage for the decode helper.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/RestoreInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/S3BlobStore.cpp -->
# sources/storage-engines/foundationdb/fdbclient/S3BlobStore.cpp

## Purpose
`S3BlobStore.cpp` implements the S3-compatible `IBlobStoreEndpoint` backend used by backup/restore and blob operations. It handles bucket/object APIs, S3 URL/resource construction, credentials, AWS v2/v4 signing, request retry support for expiring tokens, listing, multipart upload, object integrity checks, tags, and unit tests.

## Important APIs, Types, and Functions
- `guessRegionFromDomain` infers regions from common S3-compatible host patterns and special-cases localhost.
- `parseS3Credentials`, `updateSecret`, `extractCredentialFields`, `credentialFileKey`, and `lookupSecretOnEachRequest` manage inline, file-backed, and optional AWS SDK credentials.
- `constructResourcePath` supports virtual-hosted and path-style bucket addressing and strips leading slashes from object keys.
- Bucket/object operations include `bucketExists`, `objectExists`, `deleteObject`, `createBucket`, `objectSize`, `readEntireFile`, `writeEntireFileFromBuffer`, and `readObject`.
- Listing APIs include `listObjectsStream` using ListObjectsV2 pagination and recursive common-prefix handling, plus `listBuckets`.
- Signing helpers include `awsCanonicalURI`, `hmac_sha1`, SHA256 helpers, `setV4AuthHeaders`, and `setAuthHeaders`.
- Multipart APIs include begin, upload part, finish, and abort.
- Tag APIs include `putObjectTags` with verify/retry and `getObjectTags`.
- `parseErrorCodeFromS3`, `isS3TokenError`, `processRequestFailure`, and `preRetryCheck` support token-error retry handling.

## Control Flow and State
Each public method wraps a reference-counted actor implementation. Operations acquire rate-limiter allowance, build a resource path, set headers, and call `doRequest` inherited from the blob-store base. Write operations also use upload concurrency locks. Listing loops over truncated responses with continuation tokens and sends parsed `ListResult` pages to a promise stream; recursive listing queues sub-list futures.

Signing builds canonical resource/query/header data. V4 signing adds `x-amz-content-sha256`, `x-amz-date`, signed headers, credential scope, and HMAC-SHA256 authorization. Legacy signing builds the AWS string-to-sign with date, content headers, x-amz/x-icloud headers, and canonical resource.

Token retry support parses S3 XML error codes, treats `InvalidToken` and `ExpiredToken` 400 responses specially, and for write retries can perform a dry-run bucket request before resending a large write.

## State and Persistence Behavior
Persistent state lives in S3 buckets and objects, object tags, multipart upload sessions, and remote bucket metadata. Local state includes endpoint credentials, region, request knobs, rate limiters/locks inherited from the base class, and `simulatedTokenError` for simulation fault injection. Object integrity can persist checksum metadata through S3 headers.

## Dependencies and Integration Points
The file depends on `S3BlobStore.h`, `fdbrpc/HTTP`, blob/client knobs, Flow networking/tracing/actors, OpenSSL SHA/HMAC, MD5, SHA1, base64, Boost string algorithms, RapidXML, async file interfaces, host parsing, and optional `FDBAWSCredentialsProvider` under `WITH_AWS_BACKUP`. It integrates directly with backup and restore blob-store URL handling.

## Risks and Edge Cases
- V4 signing requires a non-empty region; region inference may fail for uncommon S3-compatible domains unless explicitly configured.
- URL/resource canonicalization is security- and compatibility-sensitive, especially query sorting, path encoding, virtual hosting, and object keys with leading slashes.
- XML parsing with RapidXML mutates buffers and can throw on malformed or non-XML responses; most paths convert these to HTTP errors, but diagnostics depend on response shape.
- Multipart completion after a client-side timeout is acknowledged as ambiguous; retry may see a removed upload ID.
- `putObjectTags` builds XML by string concatenation without escaping tag keys/values.
- Token dry-run retry applies only to write requests when enabled and depends on parsing a bucket from path-style resources.
- The SHA256 integrity path relies on S3 returning `x-amz-checksum-sha256` on GET after uploads.

## Test Signals
The file includes unit tests for AWS V4 authorization headers, region guessing and invalid URL overflow, virtual-hosted list path construction, resource path normalization, and S3 error-code parsing for XML, HTML, empty, and malformed responses. Additional high-value tests should cover multipart checksum manifests, tag XML escaping, recursive listing with continuation tokens, token retry dry-run paths, virtual-hosted write retries, and integrity-check read failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/S3BlobStore.cpp -->

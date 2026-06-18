# Research Report: subset-b-008449

Grouped research for FoundationDB `fdbrpc` files in subset B. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FlowTransport.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/FlowTransport.cpp

### Purpose
`FlowTransport.cpp` implements FoundationDB's Flow RPC transport over `IConnection`. It owns endpoint registration, message framing, reliable/unreliable packet queues, peer connection lifecycle, protocol compatibility tracking, public-key lookup for authorization, ping/failure monitoring, and listener setup.

### Important APIs, Types, And Functions
The central private state is `TransportData`, which stores local addresses, listeners, `Peer` objects, endpoint maps, metrics, allow-list state, health monitor data, incompatible peer maps, multiversion connection IDs, connection history logging, and loaded public keys. `EndpointMap` packs endpoint token indexes and task priorities into a dense table for well-known and dynamically allocated endpoints. Built-in receivers handle endpoint-not-found, ping, and unauthorized-endpoint messages. `ConnectPacket` is the connection prelude containing protocol version, canonical remote address, and multiversion connection ID. Public `FlowTransport` methods expose `bind`, `sendReliable`, `sendUnreliable`, endpoint add/remove methods, peer protocol lookup, reset, degraded state, public-key file loading/watching, and current delivery peer metadata.

### Control Flow
`bind()` records a public address and starts a listener. `listenImpl()` accepts connections and launches `connectionIncoming()`, which performs TLS/connection handshakes and starts `connectionReader()`. Outgoing sends call `getOrOpenPeer()`, enqueue framed messages with `sendPacket()`, and trigger `connectionKeeper()` to connect, exchange a `ConnectPacket`, then run `connectionWriter`, `connectionReader`, and `connectionMonitor` together. `connectionReader()` grows an arena-backed read buffer, parses the connect packet, establishes compatibility, then calls `scanPackets()` to validate lengths/checksums, deserialize endpoint tokens, and schedule `deliver()`. `deliver()` switches to the endpoint priority, validates endpoint visibility and peer compatibility, sets global current-delivery metadata, and invokes `NetworkMessageReceiver::receive`.

### State And Persistence Behavior
Most state is in-memory and actor-lifetime scoped. Reliable packets remain linked in the peer's reliable set until cancelled or sent; unreliable queued packets are discarded on reconnect. Failure and health state feeds `IFailureMonitor` and `HealthMonitor`. Connection attempt history can be persisted as rolling CSV files through a thread-pool writer when `LOG_CONNECTION_ATTEMPTS_ENABLED` is set. Public keys are loaded from a JWKS file and can be refreshed by a file watcher.

### Dependencies And Integration Points
This file integrates `FlowTransport.h`, `fdbrpc`, `FailureMonitor`, `HealthMonitor`, `IPAllowList`, `JsonWebKeySet`, Flow actors, `IConnection`, `INetworkConnections`, `Net2Packet`, object serializers, `WatchFile`, TD metrics, simulator hooks, and xxHash checksums. It is the transport implementation registered by `FlowTransport::createInstance()` in `g_network`.

### Risks And Edge Cases
The framing path uses unaligned integer loads and manually managed `PacketBuffer` chains. Packet length limits log but outbound oversize packets do not currently throw. Global current-delivery state relies on strict single-delivery discipline. Compatibility handling has special multiversion-client cases and may keep incompatible connections alive for ping behavior. Private endpoint exposure depends on allow-list plus `hasTrustedPeer`; mistakes can either reject valid internal RPCs or leak private endpoints. Public-key refresh errors are logged and leave previous keys in place.

### Test Signals
There are no direct unit tests in this file, but it contains simulator buggify probes for partial/corrupt packets, counters for connection lifecycle events, checksum failure handling, and TraceEvents for large packets, incompatible peers, unauthorized endpoints, connection churn, and key loading. Transport behavior is indirectly exercised across fdbrpc, simulation, HTTP, and cluster tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FlowTransport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/HTTP.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/HTTP.cpp

### Purpose
`HTTP.cpp` provides a small asynchronous HTTP/1.1 client/server utility layer for FoundationDB components that need REST-style transport, proxy CONNECT, or simulation HTTP services.

### Important APIs, Types, And Functions
Encoding helpers include `awsV4URIEncode`, `urlEncode`, and `urlDecode`. `ResponseBase<T>::getCodeDescription()` maps supported status codes to reason phrases. `computeMD5Sum()` and `verifyMD5()` implement `Content-MD5` support. Request/response formatting is handled by `writeHeaders`, `writeRequestHeader`, `writeResponseHeader`, and `writeResponse`. Read helpers are `read_into_string`, `read_delimited_into_string`, `read_fixed_into_string`, `read_http_response_headers`, and `readHTTPData`. Public actors include `IncomingRequest::read`, `OutgoingResponse::write/reset`, `IncomingResponse::read`, `doRequest`, `sendProxyConnectRequest`, and `proxyConnect`.

### Control Flow
Writers prepend serialized HTTP headers to an `UnsentPacketQueue` and then loop on `IConnection::write()` with optional simulated partial writes. Readers accumulate bytes in strings, parse CRLF-delimited start lines and headers, then read either fixed `Content-Length` content or chunked transfer encoding. `doRequestActor()` starts response reading before finishing the request body so early server responses can close the connection cleanly. It injects optional request IDs, rate-limits sends, validates response IDs, logs verbose details, and returns `IncomingResponse`. Proxy support sends a CONNECT request with retries/backoff before wrapping the socket into the remote TLS endpoint connection.

### State And Persistence Behavior
The module has no persisted state. State lives in request/response objects, packet queues, local read buffers, counters passed by pointer, and Flow knob-driven behavior. A request body queue is consumed as it is sent.

### Dependencies And Integration Points
It depends on `fdbrpc/HTTP.h`, `IConnection`, Flow actors, `Net2Packet`, knobs, simulator buggify, `IRateControl`, MD5, and libb64. It is used by REST clients, blob/S3 paths, proxy connection setup, and `HTTPServer.cpp` simulation tests.

### Risks And Edge Cases
Parsing is intentionally narrow: multiline headers are unsupported, status/request parsing is simple, and unknown content schemes throw `http_bad_response`. `urlEncode` preserves characters that are not generally safe for every HTTP context. `awsV4URIEncode` uses `char` with `isalnum`, so signed-char inputs require care. Fixed-length content rejects trailing bytes. Chunked parsing strips chunk metadata in-place and expects clean post-chunk headers. MD5 verification is skipped for partial content when a knob allows it.

### Test Signals
`HTTPServer.cpp` exercises success, server-error conversion, and bad-MD5 behavior. Simulation buggify changes read/write sizes to cover partial I/O. TraceEvents cover malformed headers, parse failures, content-length mismatch, MD5 mismatch, request ID mismatch, and proxy retry outcomes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/HTTP.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/HTTPServer.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/HTTPServer.cpp

### Purpose
`HTTPServer.cpp` implements a simulated HTTP server framework and colocated tests for the `HTTP.cpp` request/response path.

### Important APIs, Types, And Functions
`callbackHandler()` runs a parsed request through an `HTTP::IRequestHandler` and writes the response. `connectionHandler()` accepts a connection handshake and loops reading pipelined requests. `listenActor()` initializes a handler and accepts incoming sockets. `HTTP::SimServerContext::registerNewServer()` binds listeners. `HTTP::SimRegisteredHandlerContext` updates mock DNS records for registered simulation endpoints. Test handlers include `AlwaysFailRequestHandler`, `HelloWorldRequestHandler`, `HelloErrorRequestHandler`, and `HelloBadMD5RequestHandler`.

### Control Flow
A simulator server registers listen addresses and starts `listenActor`. Each accepted connection gets a `connectionHandler` that serializes response writes with `FlowMutex` while request reads and callbacks can overlap. `callbackHandler` converts request parse or handler errors into either retryable connection termination or HTTP 500 responses, then writes the response. DNS helper methods add/remove advertised mock endpoint addresses.

### State And Persistence Behavior
State is in-memory in `SimServerContext` actor collections, listener lists, registered handler contexts, and per-connection mutex/request futures. There is no disk persistence.

### Dependencies And Integration Points
The file integrates `fdbrpc/HTTP.h`, `INetworkConnections`, simulator mock DNS, Flow actors, `IConnection`, and FoundationDB unit test registration. It provides the simulated HTTP endpoint implementation used by REST-like tests.

### Risks And Edge Cases
The connection loop assumes HTTP/1.1 style reuse but has a TODO questioning multiple requests per connection. Response writes are mutexed to avoid concurrent writers. Some handler errors are normalized to 500 while unexpected errors propagate. Bad MD5 tests depend on client-side checksum validation in `HTTP.cpp`.

### Test Signals
Three `TEST_CASE`s register simulated servers and verify normal POST/response content, handler errors becoming 500, and mismatched `Content-MD5` throwing `http_bad_response`. The tests require `g_network->isSimulated()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/HTTPServer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/HealthMonitor.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/HealthMonitor.cpp

### Purpose
`HealthMonitor.cpp` tracks recent closed peer connections and reports when a peer has crossed the configured instability threshold.

### Important APIs, Types, And Functions
`reportPeerClosed()` appends a `(time, NetworkAddress)` entry and increments the peer count. `purgeOutdatedHistory()` removes entries older than `HEALTH_MONITOR_CLIENT_REQUEST_INTERVAL_SECS` and maintains the count map. `tooManyConnectionsClosed()`, `closedConnectionsCount()`, and `getRecentClosedPeers()` expose threshold and recent-peer views.

### Control Flow
Every public read/write path first purges expired history. Counts are derived from a deque plus map so old entries can be removed in time order while current peer counts stay O(1) for lookup.

### State And Persistence Behavior
The monitor is purely in-memory. It stores a rolling deque of closure events and an address-to-count map. State resets with the owning `TransportData`.

### Dependencies And Integration Points
The implementation depends on `fdbrpc/HealthMonitor.h`, `NetworkAddress`, Flow `now()`, and Flow knobs. `FlowTransport` calls it when public connections close and uses its threshold to mark unstable peers failed or later available.

### Risks And Edge Cases
Correctness depends on monotonic event ordering and regular purging. The threshold comparison is strict greater-than, so exactly the knob value is still acceptable. High churn can grow the deque until the time window rolls forward.

### Test Signals
No direct unit test is present. Indirect signals come from `FlowTransport` TraceEvents `TooManyConnectionsClosedMarkFailed`, `TooManyConnectionsClosedMarkAvailable`, and closed-count details.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/HealthMonitor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/IPAllowList.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/IPAllowList.cpp

### Purpose
`IPAllowList.cpp` parses trusted IPv4/IPv6 CIDR subnets and validates whether peer IP addresses are allowed for trusted fdbrpc operations.

### Important APIs, Types, And Functions
`AuthAllowedSubnet` stores a base address and mask. `fromString()` parses `address/prefix` syntax through Boost.Asio, builds a mask with `createBitMask()`, and normalizes the base. `netmask()`, `netmaskWeight()`, and `printIP()` expose derived subnet information. Test helpers generate random addresses and assert expected allow-list behavior.

### Control Flow
CIDR parsing splits at `/`, parses the prefix width, creates a byte mask, applies it to the parsed address, and constructs an `AuthAllowedSubnet`. Membership is implemented in the header/operator side by comparing masked address values. The unit test validates deterministic examples, all-address corner cases, single-host `/32` and `/128` cases, and randomized subnet inclusion/exclusion.

### State And Persistence Behavior
Allow-list state is in-memory as a vector of trusted subnets owned by `IPAllowList`; `FlowTransport` copies it into `TransportData`.

### Dependencies And Integration Points
The file depends on Boost.Asio IP parsing, `flow/UnitTest`, `flow/Error`, `fdbrpc/IPAllowList.h`, fmt, bitset, and deterministic random. `FlowTransport` combines allow-list membership with `IConnection::hasTrustedPeer()` to decide whether private endpoints can be reached.

### Risks And Edge Cases
`fromString()` uses `std::stoi` and Boost parsing, so malformed input throws. Prefix width validation is not explicit in this file and depends on bit-mask construction and caller/test coverage. Mixed IPv4/IPv6 checks must reject different address families. A bad allow-list can either block legitimate internal RPCs or permit unauthorized private endpoint traffic.

### Test Signals
The `/fdbrpc/allow_list` test covers prefix weight calculation for IPv4/IPv6, representative fixed subnets, `/0` and full-host masks, cross-family rejection, and randomized subnet membership.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/IPAllowList.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/JsonWebKeySet.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/JsonWebKeySet.cpp

### Purpose
`JsonWebKeySet.cpp` parses and emits a restricted JSON Web Key Set format for FoundationDB public/private key handling.

### Important APIs, Types, And Functions
Helper templates read required/optional string members and base64url big-number members. `parseEcP256Key()` accepts ES256/P-256 JWK coordinates and optional private `d`. `parseRsaKey()` accepts RS256 modulus/exponent and either no private members or all six private CRT members. `parseKey()` dispatches by `kty`. `encodeEcKey()`, `encodeRsaKey()`, and `encodeKey()` serialize supported `PublicKey`/`PrivateKey` values. Public entry points are `JsonWebKeySet::parse()` and `JsonWebKeySet::toStringRef()`.

### Control Flow
Parsing uses RapidJSON to require an object with a `keys` array, then validates each key object, optional `use`, unique `kid`, algorithm/type consistency, and required cryptographic parameters. Big-number fields are base64url-decoded into OpenSSL `BIGNUM`s and converted into `EVP_PKEY` structures. Serialization walks the key map, extracts OpenSSL parameters, base64url-encodes them, and writes a JWKS object. The implementation has separate OpenSSL 3 provider APIs and older OpenSSL/BoringSSL paths.

### State And Persistence Behavior
The function returns an in-memory `JsonWebKeySet` map. Temporary decode/encode allocations use `Arena` and `AutoCPointer` for OpenSSL ownership. No disk I/O occurs here; `FlowTransport` performs file loading and watching around this API.

### Dependencies And Integration Points
It depends on Flow `Arena`, `PKey`, `MkCert`, `Error`, base64 helpers, RapidJSON, OpenSSL EC/RSA/EVP APIs, and unit tests. `FlowTransport::applyPublicKeySet()` uses `parse()` and retains only public keys for authorization lookup.

### Risks And Edge Cases
The supported JWKS surface is intentionally narrow: only EC P-256 ES256 and RSA RS256 are accepted. RSA private keys must include all CRT parameters. Duplicate `kid`s reject the whole set. OpenSSL API differences create portability risk. Logging suppresses repeated parse/write failures. Private keys in a public-key file are parsed but later ignored with a warning by `FlowTransport`.

### Test Signals
Tests round-trip EC public/private and RSA public/private keys generated by `mkcert`, then verify signatures against cloned keys. An empty key set is also accepted. These tests check cryptographic usability, not malformed JWKS fuzz coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/JsonWebKeySet.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/JsonWebKeySet.h -->
## sources/storage-engines/foundationdb/fdbrpc/JsonWebKeySet.h

### Purpose
`JsonWebKeySet.h` declares the restricted JWKS model used by fdbrpc authorization and key loading.

### Important APIs, Types, And Functions
`PublicOrPrivateKey` wraps either `PublicKey` or `PrivateKey` in a `std::variant` and exposes `isPublic()`, `isPrivate()`, `getPublic()`, and `getPrivate()`. `JsonWebKeySet` defines `KeyMap` from `Standalone<StringRef>` key IDs to wrapped keys, plus static `parse(StringRef, VectorRef<StringRef>)` and instance `toStringRef(Arena&)`.

### Control Flow
The header defines the public contract only. `parse()` is expected to validate JWKS JSON and optional allowed `use` members. `toStringRef()` is the inverse for supported keys.

### State And Persistence Behavior
`JsonWebKeySet` is an in-memory container. Key names are arena-backed standalone strings. Serialization writes into a caller-provided `Arena`.

### Dependencies And Integration Points
The header depends on Flow `Arena`, `PKey`, `StringRef`, STL `map`, and `variant`. It is consumed by `JsonWebKeySet.cpp` and `FlowTransport.cpp`.

### Risks And Edge Cases
The getters assume the caller checks the active variant type; wrong getter use throws `std::bad_variant_access`. The comments document that shared keys are unsupported and only EC P-256/ES256 and RSA/RS256 are allowed by the implementation.

### Test Signals
Tests live in `JsonWebKeySet.cpp` and exercise the declared parse/serialize API for supported key types.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/JsonWebKeySet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/LinkTest.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/LinkTest.cpp

### Purpose
`LinkTest.cpp` provides a dummy executable entry point so module link tests fail on unresolved symbols instead of allowing static/shared library builds to ignore them.

### Important APIs, Types, And Functions
The only function is `int main()`, returning zero.

### Control Flow
There is no runtime control flow beyond process entry and successful exit.

### State And Persistence Behavior
No state or persistence.

### Dependencies And Integration Points
It intentionally has no includes. Its value is in the build system: producing an executable forces the linker to resolve module symbols.

### Risks And Edge Cases
The file should remain minimal. Adding dependencies would weaken its role as a generic link sentinel and could create unrelated build failures.

### Test Signals
The signal is build/link success or failure, not a unit test assertion.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/LinkTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/LoadBalance.actor.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/LoadBalance.actor.cpp

### Purpose
`LoadBalance.actor.cpp` implements throttling for repeated `all_alternatives_failed` errors so clients do not flood proxies with location refresh requests.

### Important APIs, Types, And Functions
The file exports `allAlternativesFailedDelay(Future<Void> okFuture)`. It uses `g_network->networkInfo` timestamps and Flow knobs controlling reset time, minimum delay, skip-delay interval, delay ratios, and maximum delays.

### Control Flow
On each call, the actor resets the oldest failure timestamp after a quiet period, computes a jittered delay based on elapsed failure-window time unless a skip-delay window allows immediate behavior, records the newest failure time, then races `okFuture` against the delay. If the delay wins, it throws `all_alternatives_failed`; if `okFuture` wins, it returns successfully.

### State And Persistence Behavior
State is transient process-global network info timestamps. There is no disk persistence.

### Dependencies And Integration Points
It depends on `fdbrpc/LoadBalance.actor.h`, Flow actors, `CoroUtils`, `g_network`, and Flow knobs. Higher-level load-balanced request code uses the thrown error to trigger `GetKeyLocationRequest` refreshes.

### Risks And Edge Cases
The actor modifies shared network info timestamps, so delay behavior is process-wide. Too-small delays can overload proxies; too-large delays can slow recovery from stale location metadata. Correct behavior depends on `okFuture` cancellation/completion semantics.

### Test Signals
No direct tests are in this file. Behavior is indirectly covered by load-balancing and client simulation workloads that observe proxy request rates and recovery from failed alternatives.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/LoadBalance.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Locality.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/Locality.cpp

### Purpose
`Locality.cpp` implements locality constants, process-class parsing/formatting, role fitness scoring, and load-balance distance classification.

### Important APIs, Types, And Functions
Static `LocalityData` keys define process, zone, data-center, machine, and data-hall identifiers. `ProcessClass` constructors parse class/source strings, `toString()` and `sourceString()` serialize them, and `machineClassFitness(ClusterRole)` ranks each process class for cluster roles. `loadBalanceDistance()` returns `SAME_MACHINE`, `SAME_DC`, or `DISTANT` based on locality knobs and IDs.

### Control Flow
Class parsing is a string-to-enum cascade with deprecated `proxy` mapped to `commit_proxy` and `fast_restore` asserted as deprecated. Fitness is a role-indexed switch with role-specific best/good/okay/worst/never outcomes. Load-balance distance first checks zone-id locality, then data-center locality, then falls back to distant.

### State And Persistence Behavior
The file stores only static constants. Parsed `ProcessClass` values are plain in-memory objects used by cluster configuration and recruitment logic.

### Dependencies And Integration Points
It depends on `fdbrpc/Locality.h` and Flow knobs. The fitness table informs recruitment for storage, TLogs, proxies, resolvers, controllers, data distribution, ratekeeper, consistency scan, blob roles, backup, and encryption key proxy. Distance is consumed by load-balancing code.

### Risks And Edge Cases
The fitness matrix is policy-heavy and easy to regress when new roles/classes are added. Unknown strings become invalid. Deprecated classes can assert. Locality distance ignores host-local checks for now and is knob-gated for zone/DC matching.

### Test Signals
No direct tests in this file. Coverage is indirect through configuration parsing, role recruitment, simulation role placement, and load-balancing behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Locality.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Net2FileSystem.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/Net2FileSystem.cpp

### Purpose
`Net2FileSystem.cpp` implements the `IAsyncFileSystem` backend for the Net2 networking runtime, selecting cached, kernel-AIO, EIO/ASIO, write-checker, and chaos wrappers as appropriate.

### Important APIs, Types, And Functions
`Net2FileSystem::open()` validates optional filesystem-device constraints, enforces exclusive/create expectations, chooses `AsyncFileCached` for buffered files, `AsyncFileKAIO` for Linux unbuffered AIO when enabled, or `Net2AsyncFile` otherwise, then wraps with `AsyncFileWriteChecker` or `AsyncFileChaos` based on knobs. Other APIs are `deleteFile`, `lastWriteTime`, `renameFile`, `stop`, and static `newFileSystem` overloads. Linux-only `runAsyncFileKAIOTestOps()` and `/fdbrpc/AsyncFileKAIO/RequestList` test KAIO request timeouts.

### Control Flow
Construction initializes Net2 async file support and, on Linux, KAIO eventfd support. If filesystem paths are provided, it verifies each is a mount point and stores allowed device IDs. `open()` compares the target file's device ID with this allow-list before dispatching to the selected async-file implementation.

### State And Persistence Behavior
The object stores allowed filesystem device IDs and a `checkFileSystem` flag. It performs real filesystem operations through underlying async file classes. The KAIO test creates and deletes `/tmp/__KAIO_TEST_FILE__`.

### Dependencies And Integration Points
It depends on `Net2FileSystem.h`, async file implementations, `AsioReactor`, platform filesystem helpers, Flow knobs, unit tests, and the global network `enFileSystem` slot. Storage and log subsystems use this through `IAsyncFileSystem`.

### Risks And Edge Cases
Device-ID enforcement can reject valid paths if mount configuration is wrong. Kernel AIO support varies by platform and flags. Chaos/write-check wrappers intentionally perturb or validate I/O. Tests write large temporary files and skip KAIO in simulation.

### Test Signals
The Linux KAIO test checks normal timeout settings and forced tiny timeouts, asserting request failure state. Broader filesystem behavior is covered in `Net2FileSystemTests.cpp`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Net2FileSystem.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Net2FileSystemTests.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/Net2FileSystemTests.cpp

### Purpose
`Net2FileSystemTests.cpp` contains unit tests for asynchronous file-system semantics required by FoundationDB.

### Important APIs, Types, And Functions
`forceLinkNet2FileSystemTests()` ensures test linkage. `writeRangeWithByte()` writes a repeated byte pattern over a file range. Test cases cover `/fileio/zero`, `/fileio/incrementalDelete`, `/fileio/rename`, and `/fileio/truncateAndRead`.

### Control Flow
Tests open temporary files through `IAsyncFileSystem::filesystem()`, perform async writes, zeroing, truncate, sync, rename, readback, listing, and deletion. They use `co_await` for each operation and assert expected bytes or filesystem state.

### State And Persistence Behavior
Tests create real temporary files under `/tmp`, including large 5 GB and 100 MB files. They explicitly clear file references before delete/rename where needed and call durable delete or incremental delete for cleanup.

### Dependencies And Integration Points
The tests depend on `IAsyncFile`, deterministic random, platform helpers, aligned allocation, and the active filesystem backend registered by Net2.

### Risks And Edge Cases
Large temporary file sizes can stress disk space or sparse-file behavior depending on platform. File names such as `/tmp/__JUNK__` are shared across tests, so parallel execution could conflict if the harness does not isolate. The tests assume truncate extension reads as zero and rename preserves data.

### Test Signals
Assertions validate zero-range growth and clearing, incremental deletion completion, rename visibility plus data preservation, and zero-filled truncate extension.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Net2FileSystemTests.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/QueueModel.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/QueueModel.cpp

### Purpose
`QueueModel.cpp` maintains per-endpoint queue measurements used by load-balanced request selection and future-version backoff.

### Important APIs, Types, And Functions
`QueueModel::addRequest()` adds the endpoint penalty to smoothed outstanding work and returns it. `endRequest()` removes the outstanding delta, updates latency and penalty, and adjusts future-version backoff state. `getMeasurement()` returns `QueueData`. TSS helpers are `updateTssEndpoint`, `removeTssEndpoint`, and `getTssData`. Overloads of `getLoadBalancedReply` and `getBasicLoadBalancedReply` adapt typed reply pointers into optional load-balance metadata.

### Control Flow
Requests add a penalty before dispatch and remove it on completion. Clean completions replace latency and reset future-version backoff. Unclean completions keep the max latency. Future-version errors exponentially increase endpoint backoff, capped by knobs, and set `failedUntil`.

### State And Persistence Behavior
State is in-memory in the model's endpoint-ID map. Each `QueueData` tracks latency, penalty, smoothed outstanding work, future-version backoff timing, failed-until time, and optional TSS endpoint data.

### Dependencies And Integration Points
It depends on `fdbrpc/QueueModel.h`, `LoadBalance.h`, Flow time and knobs. It is consumed by load-balanced RPC selection and TSS routing metadata.

### Risks And Edge Cases
Accessing `data[id]` creates default entries, so probing unknown IDs mutates state. Future-version backoff depends on wall-clock `now()` and can temporarily exclude endpoints. Penalty updates only apply when positive. Old commented-out measurement code is inactive.

### Test Signals
No direct tests are present. Behavior is indirectly covered by load-balanced request tests and simulation scenarios involving endpoint latency, penalties, and future-version responses.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/QueueModel.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Replication.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/Replication.cpp

### Purpose
`Replication.cpp` is a minimal translation unit for the replication API declared in `fdbrpc/Replication.h`.

### Important APIs, Types, And Functions
This file only includes `fdbrpc/Replication.h`; implementation is header-based or in related files such as `ReplicationPolicy.cpp` and `ReplicationTypes.cpp`.

### Control Flow
No runtime control flow is implemented here.

### State And Persistence Behavior
No state or persistence in this file.

### Dependencies And Integration Points
It ensures the replication header participates as a compiled source unit in the fdbrpc build.

### Risks And Edge Cases
The file can appear empty but may be needed for build-system structure, link behavior, or future non-inline replication code.

### Test Signals
No direct test. Replication behavior is tested through policy serialization and higher-level data-placement tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Replication.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/ReplicationPolicy.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/ReplicationPolicy.cpp

### Purpose
`ReplicationPolicy.cpp` implements replica-selection policy composition over locality sets.

### Important APIs, Types, And Functions
`IReplicationPolicy` provides convenience `selectReplicas`, `validate`, `validateFull`, and locality tracing helpers. `PolicyOne` selects or validates one available entry. `PolicyAcross` enforces selection across a configured locality attribute such as data center, rack, or data hall, delegating within each group to a child policy. `PolicyAnd` composes multiple policies in sequence. Tests use `serializeReplicationPolicy()`.

### Control Flow
`validateFull()` checks solved/unsolved outcomes and minimality by removing each selected server. `PolicyAcross::selectReplicas()` first accounts for already-selected `alsoServers`, caches locality key lookups for the simple across-one pattern, sorts candidate additions by fewest added entries, then randomly scans remaining mutable entries by unused locality value. If it cannot satisfy `_count`, it rolls results back. `PolicyAnd::selectReplicas()` threads a growing result set through sorted child policies and appends only newly selected entries.

### State And Persistence Behavior
Selection uses temporary member vectors/arenas such as `_usedValues`, `_newResults`, and `_addedResults`; policy objects persist configured counts, attribute keys, and child policies. There is no disk persistence, but policies serialize through Flow binary serialization.

### Dependencies And Integration Points
The file depends on `ReplicationPolicy.h`, `Replication.h`, `ReplicationTypes`, `LocalitySet`, deterministic random, TraceEvents, and unit tests. Data distribution and team-building code use these policies for failure-domain placement.

### Risks And Edge Cases
Policy correctness is subtle: rollback on failure, minimality validation, locality-key caching, group-key mapping, and random mutable-entry swapping must stay consistent with `LocalitySet`. Debug tracing depends on `g_replicationdebug`. New locality attributes or policy shapes may bypass the cache or expose validation gaps.

### Test Signals
`/ReplicationPolicy/Serialization` round-trips a simple `PolicyAcross` and a nested `PolicyAnd` with data-center/rack/data-hall constraints, asserting `info()` equality after serialization. It does not exhaustively test selection correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/ReplicationPolicy.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/ReplicationTypes.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/ReplicationTypes.cpp

### Purpose
`ReplicationTypes.cpp` defines shared globals for replication locality types.

### Important APIs, Types, And Functions
It defines `const std::vector<LocalityEntry> emptyEntryArray` and `int g_replicationdebug`.

### Control Flow
No active control flow; the globals are referenced by replication policy code.

### State And Persistence Behavior
`emptyEntryArray` is immutable. `g_replicationdebug` is mutable process-global debug state and affects tracing/display behavior in replication policy selection.

### Dependencies And Integration Points
The file depends on `fdbrpc/ReplicationTypes.h`. `ReplicationPolicy.cpp` uses `emptyEntryArray` when selecting without preselected servers and checks `g_replicationdebug` for verbose locality display.

### Risks And Edge Cases
Global debug state can change logging behavior process-wide. `emptyEntryArray` avoids repeated temporary allocation but should remain read-only.

### Test Signals
No direct tests. The globals are indirectly touched by replication policy serialization and selection tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/ReplicationTypes.cpp -->

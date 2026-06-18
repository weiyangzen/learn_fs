# subset-b-007597 research

Grouped research for Kubo core HTTP gateway/routing helpers, CoreAPI interface contracts and option builders, CoreAPI conformance tests, repo GC/stat helpers, UnixFS add/metadata paths, mock node construction, and node Bitswap/build configuration. Each source file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/gateway.go -->
# sources/distributed-fs/ipfs-kubo/core/corehttp/gateway.go

## Purpose
Builds Kubo HTTP gateway serve options, including path-based gateways, hostname/subdomain gateways, version reporting, and the libp2p gateway endpoint. It adapts `core.IpfsNode` block, namesys, routing, resolver, and config state into Boxo gateway handlers.

## Important APIs, Types, and Functions
Key entry points are `GatewayOption`, `HostnameOption`, `VersionOption`, `Libp2pGatewayOption`, `newGatewayBackend`, `getGatewayConfig`, `withMetricLabels`, `newServerDomainAttrFn`, and `offlineGatewayErrWrapper`. Constants include `defaultPaths`, `subdomainGatewaySpec`, and `defaultKnownGateways`.

## Control Flow and State
Serve options read repo config, build a gateway backend, wrap it with configured headers/CORS, add bounded OTel `server.domain` labels, then mount handlers on the mux. `newGatewayBackend` switches to offline blockservice, offline value store, a rebuilt namesys, and offline path resolver when `Gateway.NoFetch` is true. `getGatewayConfig` fills Boxo defaults, copies implicit localhost subdomain gateway config, and applies per-host public gateway overrides.

## Dependencies and Integration Points
Depends on Boxo gateway, blockservice, namesys, path resolver, Kubo config defaults, `core.IpfsNode`, libp2p routing, and OTel HTTP instrumentation. It is used by daemon HTTP setup and coordinates with API/WebUI/routing handlers through the shared serve option pattern.

## Risks and Test Signals
Risks include accidentally fetching in `NoFetch` mode, high-cardinality metrics labels, incorrect public gateway inheritance, disabled localhost defaults not being removed, and offline errors mapping to the wrong HTTP status. Tests cover version output and `DeserializedResponses` inheritance; integration coverage should exercise path gateway, hostname gateway, libp2p trustless mode, DNSLink/no-fetch behavior, and configured headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/gateway.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/gateway_test.go -->
# sources/distributed-fs/ipfs-kubo/core/corehttp/gateway_test.go

## Purpose
Tests selected gateway behavior with a mock namesystem and httptest server, focusing on version endpoint output and public gateway deserialized-response configuration inheritance.

## Important APIs, Types, and Functions
Defines `mockNamesys`, `newNodeWithMockNamesys`, `delegatedHandler`, `doWithoutRedirect`, `newTestServerAndNode`, `TestVersion`, and `TestDeserializedResponsesInheritance`.

## Control Flow and State
`mockNamesys.Resolve` follows chained `/ipns/` names with a depth counter and appends unresolved suffix segments. Test servers build real core nodes over an in-memory mock repo and mount `HostnameOption`, `GatewayOption`, and `VersionOption`. The inheritance test constructs configs directly and inspects `getGatewayConfig`.

## Dependencies and Integration Points
Depends on Kubo core node construction, coreapi, repo mocks, datastore, Boxo namesys/path, HTTP test utilities, and testify assertions. It validates gateway code through the same serve-option API used by daemon setup.

## Risks and Test Signals
The mock resolver is intentionally partial and does not test publishing. The tests signal regressions in `/version` formatting and `Gateway.PublicGateways[*].DeserializedResponses` defaulting, but leave path gateway fetching, hostname routing, CORS headers, NoFetch behavior, and metrics labeling to other coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/gateway_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/logs.go -->
# sources/distributed-fs/ipfs-kubo/core/corehttp/logs.go

## Purpose
Adds a `/logs` HTTP endpoint that streams live go-log output to connected clients.

## Important APIs, Types, and Functions
The only entry point is `LogOption`, which registers an HTTP handler using `logging.NewPipeReader`, `bufio.Reader`, response writes, and optional flushing.

## Control Flow and State
On each request, the handler creates a log pipe reader, starts a cancellation goroutine watching request cancellation, node shutdown, or reader completion, then streams newline-delimited log messages to the response until read/write fails. It closes the pipe reader to unblock reads when the client disconnects.

## Dependencies and Integration Points
Depends on `go-log/v2`, `core.IpfsNode.Context`, and the core HTTP serve option interface. It integrates with API HTTP serving and exposes process log state to remote API clients.

## Risks and Test Signals
Risks include long-lived goroutines on stalled clients, writing an HTTP error after partial streaming, leaking log readers, and exposing sensitive logs if the API endpoint is reachable broadly. Test signals should cover client cancellation, node shutdown, flushing behavior, and authorization/binding assumptions at the HTTP API layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/logs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/metrics.go -->
# sources/distributed-fs/ipfs-kubo/core/corehttp/metrics.go

## Purpose
Provides HTTP serve options for Prometheus scraping, OpenCensus export/zpages, HTTP request instrumentation, and a custom libp2p connected-peer collector.

## Important APIs, Types, and Functions
Exports `MetricsScrapingOption`, `MetricsOpenCensusCollectionOption`, `MetricsOpenCensusDefaultPrometheusRegistry`, `MetricsCollectionOption`, `IpfsNodeCollector`, `PeersTotalValues`, and `peersTotalMetric`.

## Control Flow and State
Scraping mounts `promhttp.HandlerFor` using the default gatherer. OpenCensus options register Prometheus exporters and optional zpages. `MetricsCollectionOption` registers or reuses four Prometheus collectors, wraps a child mux with request/response size, duration, and counter middleware, and returns that child mux for downstream handlers. `PeersTotalValues` iterates current peer host connections and groups peers by the first connection's transport protocol stack.

## Dependencies and Integration Points
Depends on Prometheus, OpenCensus exporters, zpages, `core.IpfsNode.PeerHost`, and net/http. It wraps the same mux used by gateway/API handlers and contributes `ipfs_http_*` and `ipfs_p2p_peers_total` telemetry.

## Risks and Test Signals
Risks include global collector registration collisions, type assertions on already-registered collectors, nondeterministic transport selection for peers with multiple connections, and nil `PeerHost` handling. `metrics_test.go` covers peer counting over libp2p test swarms; additional signals include duplicate initialization and scrape output validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/metrics_test.go -->
# sources/distributed-fs/ipfs-kubo/core/corehttp/metrics_test.go

## Purpose
Tests the peer-count aggregation used by `IpfsNodeCollector`.

## Important APIs, Types, and Functions
Defines `TestPeersTotal`, which builds four basic libp2p hosts over generated swarms, dials three peers from the center host, and inspects `PeersTotalValues`.

## Control Flow and State
The test connects host 0 to hosts 1-3, waits briefly for swarm state, wraps host 0 in an `IpfsNode`, and sums `/ip4/tcp` plus `/ip4/udp/quic-v1` counts. It tolerates at most two transport buckets.

## Dependencies and Integration Points
Depends on libp2p basic host and swarm testing packages. It exercises the collector without a Prometheus registry.

## Risks and Test Signals
The sleep is timing-sensitive and the transport bucket set depends on libp2p defaults. It is a useful regression signal for peer counting semantics but not for full metric registration or scrape formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/mutex_profile.go -->
# sources/distributed-fs/ipfs-kubo/core/corehttp/mutex_profile.go

## Purpose
Adds API endpoints for changing Go runtime mutex and block profiling rates at runtime.

## Important APIs, Types, and Functions
Exports `MutexFractionOption` and `BlockProfileRateOption`, each registering a POST-only handler that parses form values and calls `runtime.SetMutexProfileFraction` or `runtime.SetBlockProfileRate`.

## Control Flow and State
Handlers reject non-POST requests, parse form data, require `fraction` or `rate`, convert it to an integer, log the change, and mutate global runtime profiling state. No persistent repo state is touched.

## Dependencies and Integration Points
Depends on Go `runtime`, net/http, Kubo logging, and the serve option pattern. It is intended for debugging endpoints mounted by daemon/API configuration.

## Risks and Test Signals
Risks include exposing expensive profiling toggles without adequate API binding controls, accepting negative values according to runtime semantics, and global side effects across all handlers. Tests should cover method rejection, missing/invalid parameters, and successful runtime setting changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/mutex_profile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/option_test.go -->
# sources/distributed-fs/ipfs-kubo/core/corehttp/option_test.go

## Purpose
Tests the API version checking serve option behavior.

## Important APIs, Types, and Functions
Defines `testcasecheckversion`, its `body` helper, and `TestCheckVersionOption`.

## Control Flow and State
Each case builds a request with a `User-Agent`, wraps a child mux via `CheckVersionOption`, records whether the downstream handler ran, and compares response code/body. API version mismatches are rejected for normal API paths but bypassed for `/api/v0/version` and `/webui`.

## Dependencies and Integration Points
Depends on Kubo version constants and httptest. It validates a serve option implemented outside this subset but mounted in the same corehttp option chain.

## Risks and Test Signals
The test signals API compatibility enforcement regressions, especially false rejection of browser/WebUI/version requests. It does not cover all user-agent variants or interaction with CORS/auth middleware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/option_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/p2p_proxy.go -->
# sources/distributed-fs/ipfs-kubo/core/corehttp/p2p_proxy.go

## Purpose
Exposes `/p2p/` HTTP reverse proxying to HTTP services advertised over libp2p peers.

## Important APIs, Types, and Functions
Exports `P2PProxyOption`; internal pieces are `proxyRequest`, `parseRequest`, and `handleError`.

## Control Flow and State
The handler parses paths of the form `/p2p/$peer/http/$path` or `/p2p/$peer/x/$protocol/http/$path`, validates the peer ID, rewrites the request path, builds a `libp2p://$peer` target, creates a go-libp2p-http transport with the selected protocol ID, and delegates to `httputil.ReverseProxy`.

## Dependencies and Integration Points
Depends on `core.IpfsNode.PeerHost`, libp2p peer/protocol types, go-libp2p-http, net/http reverse proxy, and URL parsing. It integrates with API HTTP serving as a proxy bridge from HTTP clients to libp2p services.

## Risks and Test Signals
Risks include path parsing edge cases, per-request transport/proxy allocation, forwarding headers to untrusted peers, and broad protocol exposure. Tests cover valid/invalid parser cases; integration coverage should verify proxy transport behavior, forwarded path/query semantics, and cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/p2p_proxy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/p2p_proxy_test.go -->
# sources/distributed-fs/ipfs-kubo/core/corehttp/p2p_proxy_test.go

## Purpose
Tests URL path parsing for the p2p HTTP proxy.

## Important APIs, Types, and Functions
Defines `TestCase`, `validtestCases`, `invalidtestCases`, `TestParseRequest`, and `TestParseRequestInvalidPath`.

## Control Flow and State
Valid cases build URLs for default `/http` and namespaced `/x/custom/http` protocols, then assert target peer, protocol ID, and proxied path. Invalid cases assert parser errors for missing/incorrect protocol path segments.

## Dependencies and Integration Points
Depends on net/http request construction, libp2p protocol IDs, and testify `require`. It validates the parsing helper used by `P2PProxyOption`.

## Risks and Test Signals
The test does not instantiate a libp2p HTTP transport or reverse proxy. It is a parser regression signal for path structure and PeerID validation only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/p2p_proxy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/redirect.go -->
# sources/distributed-fs/ipfs-kubo/core/corehttp/redirect.go

## Purpose
Provides a simple serve option that redirects an HTTP path while applying configured API headers.

## Important APIs, Types, and Functions
Exports `RedirectOption` and defines `redirectHandler`.

## Control Flow and State
The serve option reads repo config, builds a handler with redirect target and `API.HTTPHeaders`, and mounts it either at `/$path/` or `/`. Requests copy configured headers into the response and issue HTTP 302 to the target path.

## Dependencies and Integration Points
Depends on `core.IpfsNode.Repo.Config`, net/http, and the corehttp serve option pattern. It is used for root or alias endpoint behavior in daemon HTTP setup.

## Risks and Test Signals
Risks include unexpected broad root matching, header exposure, and permanent-vs-temporary redirect expectations. Tests should verify configured headers, mounted path behavior, and exact redirect status/location.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/redirect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/routing.go -->
# sources/distributed-fs/ipfs-kubo/core/corehttp/routing.go

## Purpose
Serves the HTTP delegated routing v1 API backed by the node's routing, peerstore, and DHT client.

## Important APIs, Types, and Functions
Exports `RoutingOption`; implements `contentRouter` methods `FindProviders`, `ProvideBitswap`, `FindPeers`, `GetIPNS`, `PutIPNS`, and `GetClosestPeers`; defines `peerChanIter`.

## Control Flow and State
`RoutingOption` wraps the Boxo routing HTTP server with gateway headers/CORS and mounts `/routing/v1/`. Provider lookup converts the async libp2p provider channel into a result iterator with cancellation. Peer/IPNS methods call routing interfaces directly. Closest-peer lookup rejects undefined CIDs, chooses WAN DHT for dual DHT, supports fullrt and IpfsDHT, then maps peerstore addresses into HTTP records.

## Dependencies and Integration Points
Depends on Boxo routing HTTP server/types, gateway headers, Kubo node routing/DHT fields, libp2p DHT implementations, peerstore, CIDs, and IPNS records. It is a public delegated-routing surface.

## Risks and Test Signals
Risks include exposing LAN peers from the wrong DHT, stale peerstore addresses, unsupported DHT types, iterator cancellation leaks, and lack of Bitswap write-provide support. Tests should cover HTTP routing endpoints, WAN-only selection, IPNS marshal/unmarshal errors, and provider iterator cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/routing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/webui.go -->
# sources/distributed-fs/ipfs-kubo/core/corehttp/webui.go

## Purpose
Provides the `/webui/` API handler and records the current and historical WebUI IPFS paths.

## Important APIs, Types, and Functions
Exports `WebUIPath`, `WebUIPaths`, and `WebUIOption`; internal type `webUIHandler` implements `ServeHTTP`, `writeIncompatibleError`, and `writeNotAvailableError`.

## Control Flow and State
`WebUIOption` reads API headers and gateway flags from config, then mounts `/webui/`. Requests copy API headers, reject if deserialized gateway responses are disabled, optionally check the hardcoded WebUI CID is locally present when `Gateway.NoFetch` is true, and otherwise redirect to `WebUIPath`.

## Dependencies and Integration Points
Depends on Kubo config, node blockstore, CIDs, net/http, and gateway deserialized response semantics. It integrates API endpoint behavior with gateway content retrieval.

## Risks and Test Signals
Risks include stale `WebUIPath`, NoFetch availability checks only checking the root block, config combinations that make WebUI unusable, and user-facing error text drift. Tests should verify redirect, headers, incompatible deserialization mode, NoFetch missing/present block behavior, and path list maintenance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/webui.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/block.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/block.go

## Purpose
Defines the CoreAPI block-layer interface for raw block import, retrieval, removal, and stat operations.

## Important APIs, Types, and Functions
Declares `BlockStat` with `Size` and `Path`, and `BlockAPI` with `Put`, `Get`, `Rm`, and `Stat`.

## Control Flow and State
This file has no implementation flow. It describes contracts over blockstore state: `Put` hashes and stores block data, optional pinning may affect pin state, `Get` resolves a path to block bytes, `Rm` removes local blocks subject to pinning/force semantics, and `Stat` returns size/path metadata.

## Dependencies and Integration Points
Depends on context, `io.Reader`, Boxo path types, and block options. Implementations live in coreapi and are tested by `coreiface/tests/block.go`.

## Risks and Test Signals
Risks are contract ambiguity around pinned block removal, path resolution, and CID option semantics. Test signals include raw/dag-pb/dag-cbor CID generation, forced removal, stat size, and pin-on-put behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/coreapi.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/coreapi.go

## Purpose
Defines the top-level Go CoreAPI interface for interacting with an IPFS node.

## Important APIs, Types, and Functions
The `CoreAPI` interface exposes sub-APIs `Unixfs`, `Block`, `Dag`, `Name`, `Key`, `Pin`, `Object`, `Swarm`, `PubSub`, and `Routing`, plus `ResolvePath`, `ResolveNode`, and `WithOptions`.

## Control Flow and State
There is no implementation here. The contract partitions node behavior into sub-interfaces while allowing option-derived API views, such as offline or no-fetch views, over the same underlying node state.

## Dependencies and Integration Points
Depends on Boxo path, IPLD nodes, context, and global API options. It is consumed by commands, tests, and embedders using Kubo as a Go library.

## Risks and Test Signals
Risks include API implementations returning nil sub-APIs, inconsistent option behavior across sub-APIs, and path resolution differences between IPLD and UnixFS. `tests/api.go` orchestrates conformance coverage across all sub-APIs and checks context cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/coreapi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/dag.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/dag.go

## Purpose
Defines the DAG service exposed through CoreAPI.

## Important APIs, Types, and Functions
Declares `APIDagService`, embedding `ipld.DAGService` and adding `Pinning() ipld.NodeAdder`.

## Control Flow and State
No runtime flow is present. The interface requires normal DAG get/add/batch operations and a special node adder that recursively pins added nodes.

## Dependencies and Integration Points
Depends on `go-ipld-format`. It is used by CoreAPI implementations and conformance tests for DAG add/get/tree/batch behavior.

## Risks and Test Signals
Risks include divergence between normal DAG additions and pinning additions, and preserving custom CID builders/hashes. Tests in `tests/dag.go` cover dag-cbor CIDs, path traversal, tree output, and batch add.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/dag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/errors.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/errors.go

## Purpose
Centralizes common CoreAPI sentinel errors.

## Important APIs, Types, and Functions
Defines `ErrIsDir`, `ErrNotFile`, `ErrOffline`, and `ErrNotSupported`.

## Control Flow and State
There is no control flow or persistence. These values are shared error identities for API implementations and wrappers.

## Dependencies and Integration Points
Depends only on Go `errors`. Gateway code maps `ErrOffline` to service-unavailable behavior, and API implementations use these sentinels for mode/type failures.

## Risks and Test Signals
Risks are string/API compatibility and wrapping behavior. Tests should use `errors.Is` where possible and verify offline-mode callers surface `ErrOffline` consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/idfmt.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/idfmt.go

## Purpose
Formats IPNS key identifiers in a canonical CIDv1 base36 form.

## Important APIs, Types, and Functions
Provides `FormatKeyID(peer.ID) string` and `FormatKey(Key) string`.

## Control Flow and State
`FormatKeyID` converts a peer ID to a CID and encodes it with multibase base36, panicking only if base encoding unexpectedly fails. `FormatKey` delegates to `Key.ID`.

## Dependencies and Integration Points
Depends on libp2p peer IDs and multibase. Key and name APIs use this formatting for `/ipns/` paths and conformance tests validate base36 paths.

## Risks and Test Signals
Risks are canonical format drift and panic assumptions if upstream peer/CID conversion changes. Tests in key conformance verify generated/listed keys use `/ipns/` base36 CID strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/idfmt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/key.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/key.go

## Purpose
Defines CoreAPI keystore and key identity operations.

## Important APIs, Types, and Functions
Declares `Key` with `Name`, `Path`, and `ID`, and `KeyAPI` with `Generate`, `Rename`, `List`, `Self`, `Remove`, `Sign`, and `Verify`.

## Control Flow and State
No implementation flow is in this file. The contract controls persistent keystore entries, the immutable self key, signing with named keys, and verification by key name or encoded key identity.

## Dependencies and Integration Points
Depends on context, Boxo path, key options, and libp2p peer IDs. It integrates with IPNS names and is tested by key conformance tests.

## Risks and Test Signals
Risks include accidental mutation of `self`, overwrite semantics, signature domain separation, and accepting multiple key formats during verify. Tests cover generate/list/rename/remove restrictions, overwrite force behavior, signing, and verification across PeerID/CID/IPNS path encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/key.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/name.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/name.go

## Purpose
Defines CoreAPI IPNS publishing and resolution contracts.

## Important APIs, Types, and Functions
Defines `ErrResolveFailed`, `IpnsResult`, and `NameAPI` methods `Publish` and `Resolve`.

## Control Flow and State
No implementation appears here. The interface requires publishing signed paths under self or selected keys and resolving mutable names back to paths with options controlling cache/depth/validity behavior.

## Dependencies and Integration Points
Depends on context, Boxo IPNS/path, and name options. It integrates with KeyAPI identities, routing value stores, and namesys.

## Risks and Test Signals
Risks include expired records resolving from cache, path suffix preservation, offline/delegated publish semantics, and key selection. Tests cover publish/resolve with self and generated keys, suffix resolution, cache off, and record expiry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/name.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/object.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/object.go

## Purpose
Defines dag-pb object mutation and diff contracts for CoreAPI.

## Important APIs, Types, and Functions
Defines `ChangeType` constants `DiffAdd`, `DiffRemove`, and `DiffMod`; `ObjectChange`; and `ObjectAPI` methods `New`, `Put`, `Get`, `Data`, `Links`, `Stat`, `AddLink`, `RmLink`, `AppendData`, `SetData`, and `Diff`.

## Control Flow and State
No implementation flow is present. The interface describes DAG object state transformations that create new immutable paths rather than mutating existing CIDs.

## Dependencies and Integration Points
Depends on Boxo path, IPLD links, context, readers, and object options. It is tied to dag-pb and UnixFS validation behavior in implementations.

## Risks and Test Signals
Risks include corrupting UnixFS file or HAMT shard nodes through low-level link mutation, link ordering, and diff correctness. Tests cover add/rm link validation, explicit non-UnixFS bypass, create-parent behavior, and modification diffs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/block.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/options/block.go

## Purpose
Builds option structs for block put and remove operations, including CID codec/hash settings and pin/force flags.

## Important APIs, Types, and Functions
Defines `BlockPutSettings`, `BlockRmSettings`, option function types, `BlockPutOptions`, `BlockRmOptions`, `Block` option namespace, and option methods `CidCodec`, `Format`, `Hash`, `Pin`, and `Force`.

## Control Flow and State
Defaults are CIDv1 raw with sha2-256 and no pinning. Options apply in order. `Format` preserves legacy names by mapping `v0`/`protobuf` to dag-pb and `cbor` to dag-cbor, and validates CIDv0 compatibility with dag-pb plus sha2-256-32.

## Dependencies and Integration Points
Depends on go-cid, go-multicodec, and go-multihash. Consumed by BlockAPI implementations and tested by block conformance cases.

## Risks and Test Signals
Risks include typo in error text (`sha2-255-32`), legacy format compatibility, option order interactions, and invalid CIDv0 combinations. Tests cover raw defaults, dag-cbor/dag-pb aliases, CIDv0, custom hash, pin, and force remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/dht.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/options/dht.go

## Purpose
Maintains deprecated DHT option aliases for the routing option API.

## Important APIs, Types, and Functions
Aliases `DhtProvideSettings`, `DhtFindProvidersSettings`, option function types, `DhtProvideOptions`, `DhtFindProvidersOptions`, and `Dht` to their routing equivalents.

## Control Flow and State
There is no runtime flow. Alias declarations keep old import paths source-compatible without duplicating state.

## Dependencies and Integration Points
Depends on `options/routing.go` definitions in the same package. It supports older callers while the CoreAPI exposes `Routing`.

## Risks and Test Signals
Risks include alias drift if routing option types change and deprecated docs falling out of sync. Compile coverage of old DHT option users is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/dht.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/global.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/options/global.go

## Purpose
Defines global CoreAPI view options for offline mode and block fetching.

## Important APIs, Types, and Functions
Defines `ApiSettings`, `ApiOption`, `ApiOptions`, `ApiOptionsTo`, `Api` option namespace, and methods `Offline` and `FetchBlocks`.

## Control Flow and State
Defaults are online API mode with block fetching enabled. Option functions mutate a settings struct in order. These settings are later interpreted by CoreAPI implementations to select offline/no-fetch behavior.

## Dependencies and Integration Points
No external dependencies. Used by `CoreAPI.WithOptions` and conformance tests for offline add/routing behavior.

## Risks and Test Signals
Risks include confusion between fully offline mode and fetch-blocks-disabled mode, and incomplete propagation to sub-APIs. Tests use `Api.Offline(true)` for local UnixFS add and offline routing put behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/global.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/key.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/options/key.go

## Purpose
Builds settings for key generation and key rename operations.

## Important APIs, Types, and Functions
Defines key algorithm constants `RSAKey`, `Ed25519Key`, `DefaultRSALen`, settings structs, option function types, `KeyGenerateOptions`, `KeyRenameOptions`, `Key` namespace, and option methods `Type`, `Size`, and `Force`.

## Control Flow and State
Generate defaults to RSA with implementation-selected size (`-1`). Rename defaults to no overwrite. Option functions simply mutate settings; validation is expected in the implementation.

## Dependencies and Integration Points
No external package dependencies. Consumed by KeyAPI implementations and conformance tests.

## Risks and Test Signals
Risks include accepting unsupported algorithms/sizes too late, self-key overwrite/remove protection, and force semantics. Tests cover size, type, existing-name errors, rename overwrite, and self restrictions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/key.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/name.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/options/name.go

## Purpose
Builds IPNS publish and resolve option settings.

## Important APIs, Types, and Functions
Defines `DefaultNameValidTime`, `NamePublishSettings`, `NameResolveSettings`, option types, `NamePublishOptions`, `NameResolveOptions`, `Name` namespace, and methods for valid time, key, offline/delegated publishing, TTL, sequence, v1 compatibility, cache, and raw namesys resolve options.

## Control Flow and State
Publish defaults to 24h validity, key `self`, and no offline/delegated publishing. Resolve defaults to cache enabled. Options append or override fields; implementations consume TTL/sequence pointers to distinguish unset from zero.

## Dependencies and Integration Points
Depends on time and Boxo namesys options. It connects NameAPI to KeyAPI and routing/namesys implementations.

## Risks and Test Signals
Risks include zero TTL/sequence pointer semantics, cache use after expiry, and differences between offline and delegated publishing. Tests cover custom keys, cache disabled, suffix resolution, and expiry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/name.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/object.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/options/object.go

## Purpose
Builds settings for object link addition/removal, including UnixFS validation bypass controls.

## Important APIs, Types, and Functions
Defines `ObjectAddLinkSettings`, `ObjectRmLinkSettings`, option types, `ObjectAddLinkOptions`, `ObjectRmLinkOptions`, `Object` namespace, and methods `Create`, `SkipUnixFSValidation`, and `RmLinkSkipUnixFSValidation`.

## Control Flow and State
Add-link defaults to no parent creation and validation enabled. Remove-link defaults to validation enabled. Options flip booleans; implementations enforce directory/HAMT/raw dag-pb safety unless bypassed.

## Dependencies and Integration Points
No external dependencies. Consumed by ObjectAPI and its conformance tests.

## Risks and Test Signals
Risks include exposing validation bypass too broadly and inconsistent add/remove bypass names. Tests explicitly cover UnixFS directory/file/HAMT/raw dag-pb validation and bypass behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/pin.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/options/pin.go

## Purpose
Builds settings for pin add, list, status, remove, and update operations.

## Important APIs, Types, and Functions
Defines `PinAddSettings`, `PinLsSettings`, `PinIsPinnedSettings`, `PinRmSettings`, `PinUpdateSettings`, option types, settings builders, `Pin` namespace, nested `Ls`/`IsPinned` namespaces, type filters, `Detailed`, `Name`, `Recursive`, `RmRecursive`, and `Unpin`.

## Control Flow and State
Defaults are recursive add/remove, list all, is-pinned all, update unpins old target. Type methods validate allowed pin types and return option functions. Detailed listing controls whether pin names are populated.

## Dependencies and Integration Points
Depends only on fmt. Consumed by PinAPI implementations and conformance tests around recursive/direct/indirect pin state.

## Risks and Test Signals
Risks include invalid type strings, precedence between recursive/direct/indirect pins, preserving pin names on update, and detailed-vs-nondetailed name exposure. Tests cover pin add/rm/list/is-pinned/verify, precedence, indirect listing, and names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/pin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/pubsub.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/options/pubsub.go

## Purpose
Builds settings for pubsub peer listing and subscriptions.

## Important APIs, Types, and Functions
Defines `PubSubPeersSettings`, `PubSubSubscribeSettings`, option types, `PubSubPeersOptions`, `PubSubSubscribeOptions`, `PubSub` namespace, and methods `Topic` and `Discover`.

## Control Flow and State
Peer listing defaults to no topic filter. Subscribe defaults to discovery disabled. Options mutate simple settings fields consumed by PubSubAPI implementations.

## Dependencies and Integration Points
No external dependencies. Used by PubSubAPI tests for topic-scoped peers.

## Risks and Test Signals
Risks include empty topic semantics and discovery behavior varying by router. Tests cover publish/subscribe delivery, topic peer filtering, and local topic listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/pubsub.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/routing.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/options/routing.go

## Purpose
Builds settings for routing put/provide/find-provider operations.

## Important APIs, Types, and Functions
Defines `RoutingPutSettings`, `RoutingProvideSettings`, `RoutingFindProvidersSettings`, option types, builder functions, deprecated `Put` alias, `Routing` namespace, and methods `Recursive`, `NumProviders`, and `AllowOffline`.

## Control Flow and State
Routing put defaults to disallow offline writes, provide defaults to non-recursive, and find-providers defaults to 20 providers. Option functions update these values.

## Dependencies and Integration Points
No external dependencies except same-package deprecated DHT aliases. Consumed by RoutingAPI and routing tests.

## Risks and Test Signals
Risks include type aliases still named `DhtProvideSettings`, offline put bypass, and provider count bounds left to implementations. Tests cover offline put requiring `AllowOffline`, provider search counts, and explicit provide.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/routing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/unixfs.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/options/unixfs.go

## Purpose
Builds UnixFS add/list settings and derives the CID prefix used by UnixFS imports.

## Important APIs, Types, and Functions
Defines `Layout`, `BalancedLayout`, `TrickleLayout`, `UnixfsAddSettings`, `UnixfsLsSettings`, `UnixfsAddOptions`, `UnixfsLsOptions`, `Unixfs` namespace, and many add/list option methods including CID/hash/raw leaves, chunker, layout, pin, hash-only, events, no-copy, HAMT limits, metadata preservation, and empty-directory inclusion.

## Control Flow and State
Defaults are CID version auto, sha2-256, balanced layout, size-262144 chunker, no pin, no hash-only, no-copy off, raw leaves off unless CIDv1, and include empty dirs. Normalization enforces no-copy implies raw leaves, non-sha2 implies CIDv1, CIDv0 only with sha2-256, explicit mtime/mode disables preserve flags, and HAMT fanout must be a power of two from 8 to 1024.

## Dependencies and Integration Points
Depends on Boxo UnixFS importer helpers/io, merkledag CID prefix helpers, go-cid, multihash, os, and time. Used by CoreAPI UnixFS add/list implementations and tests.

## Risks and Test Signals
Risks include option order interactions, CID default changes, invalid mtime nanoseconds, no-copy/raw-leaf compatibility, HAMT fanout validation, and empty-directory default semantics. Tests cover fanout validation and extensive UnixFS add/get/list behavior in conformance tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/unixfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/unixfs_test.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/options/unixfs_test.go

## Purpose
Tests validation of UnixFS HAMT fanout option values.

## Important APIs, Types, and Functions
Defines `TestMaxHAMTFanoutValidation`.

## Control Flow and State
The test calls `UnixfsAddOptions(Unixfs.MaxHAMTFanout(v))` for valid powers of two from 8 through 1024 and for invalid negative, small, non-power-of-two, and oversized values. Invalid cases must include the expected error text.

## Dependencies and Integration Points
Depends on testify `require` and the UnixFS options builder.

## Risks and Test Signals
This is a narrow validation signal for sharding settings. It does not test downstream MFS/HAMT construction, but catches regressions in the option-level guardrail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/options/unixfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/pin.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/pin.go

## Purpose
Defines CoreAPI pinning interfaces and pin verification result contracts.

## Important APIs, Types, and Functions
Declares `Pin`, `PinStatus`, `BadPinNode`, and `PinAPI` methods `Add`, `Ls`, `IsPinned`, `Rm`, `Update`, and `Verify`.

## Control Flow and State
No implementation flow is present. The contract represents recursive, direct, and indirect pin state, optional pin names, update semantics, and streamed verification results.

## Dependencies and Integration Points
Depends on context, Boxo path, CIDs, and pin options. Implementations wrap the node pinner and are exercised by pin conformance tests.

## Risks and Test Signals
Risks include channel close/error ordering in `Ls`/`Verify`, pin type precedence, indirect reason reporting, and name preservation. Tests cover simple/recursive/direct/indirect pins, list consistency, is-pinned reasons, verification, and named pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/pin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/pubsub.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/pubsub.go

## Purpose
Defines CoreAPI pubsub subscription, message, and control interfaces.

## Important APIs, Types, and Functions
Declares `PubSubSubscription`, `PubSubMessage`, and `PubSubAPI` with `Ls`, `Peers`, `Publish`, and `Subscribe`.

## Control Flow and State
There is no implementation here. The contract exposes streaming subscription state via `Next`, message metadata such as sender/sequence/topic/signature/key, and topic-peer queries.

## Dependencies and Integration Points
Depends on context, pubsub options, and libp2p peer IDs. Implementations integrate with the node pubsub router.

## Risks and Test Signals
Risks include subscription cancellation, message authenticity fields, peer discovery semantics, and topic-local vs remote state. Tests cover basic two-node publish/subscribe, sender identity, topic peer listing, and topic listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/pubsub.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/routing.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/routing.go

## Purpose
Defines CoreAPI routing operations over value records, peers, and providers.

## Important APIs, Types, and Functions
Declares `RoutingAPI` with `Get`, `Put`, `FindPeer`, `FindProviders`, and `Provide`.

## Control Flow and State
No implementation flow is present. The contract covers DHT/delegated routing state: value records, peer address discovery, provider records, and explicit provider announcements.

## Dependencies and Integration Points
Depends on context, Boxo path, routing options, and libp2p peer address info. Implementations use node routing/DHT subsystems.

## Risks and Test Signals
Risks include offline write semantics, provider channel closure, stale addresses, and recursive provide behavior. Tests cover IPNS record get/put, offline put option, peer finding, provider finding, and explicit provide propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/routing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/swarm.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/swarm.go

## Purpose
Defines CoreAPI swarm networking operations and connection metadata.

## Important APIs, Types, and Functions
Defines `ErrNotConnected`, `ErrConnNotFound`, `ConnectionInfo`, and `SwarmAPI` methods `Connect`, `Connectedness`, `Peers`, `KnownAddrs`, `LocalAddrs`, `ListenAddrs`, and `Disconnect`.

## Control Flow and State
No implementation is present. The interface describes live libp2p connection state, peerstore-known addresses, local/listen addresses, and connect/disconnect operations.

## Dependencies and Integration Points
Depends on context, multiaddr, libp2p network/peer types. Routing and pubsub tests use swarm APIs for local address and peer identity checks.

## Risks and Test Signals
Risks include confusing known vs connected addresses, stale connection info, and disconnect races. Conformance in this subset is indirect through routing/pubsub tests; dedicated swarm tests should cover connection lifecycle and error sentinels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/swarm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/api.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/api.go

## Purpose
Defines the shared CoreAPI conformance test harness.

## Important APIs, Types, and Functions
Declares `Provider`, `TestSuite`, helper methods `makeAPISwarm`, `makeAPI`, `makeAPIWithIdentityAndOffline`, `MakeAPISwarm`, `hasApi`, and `TestApi`.

## Control Flow and State
Providers create swarms with requested identity/online settings. `TestApi` runs subtests for every CoreAPI domain, tracks live API swarms through a channel, cancels contexts, and verifies all spawned swarms terminate by the final `TestsCancelCtx` subtest.

## Dependencies and Integration Points
Depends on testing, context, and the CoreAPI interface. Implementations plug in by providing `MakeAPISwarm`.

## Risks and Test Signals
Risks include shared running counter races, providers ignoring full-identity/offline flags, and test contexts leaking resources. The final cleanup subtest is the main signal for context cancellation discipline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/block.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/block.go

## Purpose
Conformance tests for BlockAPI CID creation, retrieval, removal, stat, and pin-on-put behavior.

## Important APIs, Types, and Functions
Defines known CIDs, fixture readers `pbBlock`/`cborBlock`, and tests `TestBlock*` for put formats/codecs/hash, get, remove, stat, and pin.

## Control Flow and State
Tests create offline APIs, put fixture blocks with different options, compare exact CIDs, read data back, resolve paths, remove blocks with and without force, and inspect pin lists after `Block.Pin(true)`.

## Dependencies and Integration Points
Depends on BlockAPI, PinAPI, ResolvePath, multihash, IPLD not-found checks, and block options.

## Risks and Test Signals
Strong signals cover default raw CIDv1, legacy `Format` compatibility, custom hash/CID codec, not-found handling, force removal, stat sizes, and recursive pin creation. It does not cover concurrent remove or pinned block removal edge cases deeply.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/dag.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/dag.go

## Purpose
Conformance tests for DAG service add/get/path/tree/batch behavior.

## Important APIs, Types, and Functions
Defines `treeExpected` and tests `TestPut`, `TestPutWithHash`, `TestDagPath`, `TestTree`, and `TestBatch`.

## Control Flow and State
Tests create dag-cbor nodes with default and custom hashes, add them, compare exact CIDs, resolve links through `ResolvePath`, inspect `Tree` output, and verify `AddMany` makes a previously missing node retrievable.

## Dependencies and Integration Points
Depends on dag-cbor, Boxo path, CoreAPI DAG service, and `ResolvePath`.

## Risks and Test Signals
Signals include CID stability, custom multihash support, IPLD link traversal, tree enumeration, and batch commit behavior. It does not exercise pinning node adder or large DAG streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/dag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/key.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/key.go

## Purpose
Conformance tests for KeyAPI generation, listing, renaming, removal, signing, and verification.

## Important APIs, Types, and Functions
Includes `TestKey`, `verifyIPNSPath`, and tests for self handling, generate size/type/existing, list, rename variants, remove, sign, and verify across key encodings.

## Control Flow and State
Tests create APIs, inspect the default `self` key, generate named keys, validate `/ipns/` base36 CID paths, enforce self immutability, exercise force/no-force rename overwrite paths, remove keys, sign with domain-separated libp2p key data, and verify signatures by name, empty self selector, base58 PeerID, CIDv1 PeerID, IPNS name, and prefixed IPNS path.

## Dependencies and Integration Points
Depends on KeyAPI, key options, libp2p peer/IPNS formatting, multibase, and testify.

## Risks and Test Signals
Signals are broad for keystore semantics and signature compatibility. The Ed25519 generate-type path is skipped for a linked upstream issue, so supported key algorithm validation still needs implementation-specific coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/key.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/name.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/name.go

## Purpose
Conformance tests for IPNS publish and resolve behavior.

## Important APIs, Types, and Functions
Defines deterministic random source `rnd`, helper `addTestObject`, and tests `TestPublishResolve`, `TestBasicPublishResolveKey`, and `TestBasicPublishResolveTimeout`.

## Control Flow and State
Tests create online swarms, add UnixFS objects, publish under self or a generated key, resolve direct and suffixed names with cache on/off, and verify record expiry by publishing with one-second validity then resolving after a delay.

## Dependencies and Integration Points
Depends on Unixfs, Name, Key, IPNS, path options, and multi-node provider setup.

## Risks and Test Signals
Signals include self-key mapping, generated-key publishing, suffix preservation, cache disabled resolution, and expiry. Timing sleeps make expiry tests slow and somewhat timing-sensitive; routing propagation relies on provider setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/name.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/object.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/object.go

## Purpose
Conformance tests for ObjectAPI dag-pb link mutation, UnixFS validation, and diffs.

## Important APIs, Types, and Functions
Defines helper `putDagPbNode` and tests `TestObjectAddLink`, `TestObjectAddLinkCreate`, `TestObjectAddLinkValidation`, `TestObjectRmLink`, `TestObjectRmLinkValidation`, and `TestDiffTest`.

## Control Flow and State
Tests build raw dag-pb, UnixFS directory/file, and HAMT shard nodes; attempt add/remove link operations with and without validation bypass; check expected errors; inspect resulting link lists; and compare object diffs.

## Dependencies and Integration Points
Depends on DAG service, ObjectAPI, UnixFS protobuf metadata, IPLD links, and object options.

## Risks and Test Signals
This file directly guards against data-loss/corruption risks from dag-pb-level mutation of UnixFS files and HAMT shards. It also signals bypass semantics and link-create behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/path.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/path.go

## Purpose
Conformance tests for path mutability, joins, root resolution, and unresolved remainder reporting.

## Important APIs, Types, and Functions
Defines `newIPLDPath` and tests `TestMutablePath`, `TestPathRemainder`, `TestEmptyPathRemainder`, `TestInvalidPathRemainder`, `TestPathRoot`, and `TestPathJoin`.

## Control Flow and State
Tests create raw blocks and dag-cbor nodes, resolve paths through `CoreAPI.ResolvePath`, assert mutable status for key paths versus block paths, compare unresolved remainder slices, verify invalid traversal errors, and validate `path.Join`.

## Dependencies and Integration Points
Depends on BlockAPI, DagAPI, KeyAPI, path utilities, dag-cbor, and UnixFS/IPLD path namespaces.

## Risks and Test Signals
Signals include correct root CID extraction after IPLD traversal and remainder behavior. It does not cover IPNS mutable resolution depth or UnixFS path traversal extensively.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/path.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/pin.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/pin.go

## Purpose
Conformance tests for pin add/list/remove/update/verify/is-pinned behavior and pin-name handling.

## Important APIs, Types, and Functions
Defines many `TestPin*` tests, helpers `getThreeChainedNodes`, `assertPinTypes`, `assertPinCids`, `assertPinLsAllConsistency`, `assertIsPinned`, `assertNotPinned`, and `accPins`.

## Control Flow and State
Tests add UnixFS/IPLD objects, create recursive and direct pins, inspect all/direct/recursive/indirect listings, verify precedence rules, check is-pinned reasons, stream verification results, add/list/update/re-pin named pins, and ensure nondetailed lists omit names.

## Dependencies and Integration Points
Depends on Unixfs, Dag, PinAPI, pin options, CIDs, dag-cbor, and path helpers.

## Risks and Test Signals
Strong signals cover pin state precedence, indirect listing even with direct parents, duplicate handling, detailed name exposure, update name preservation, and direct pin naming. Missing-block verify failure is left as TODO because it requires lower-level node access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/pin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/pubsub.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/pubsub.go

## Purpose
Conformance tests for basic PubSubAPI messaging and topic peer discovery.

## Important APIs, Types, and Functions
Defines `TestPubSub` and `TestBasicPubSub`.

## Control Flow and State
Creates a two-node online swarm, subscribes node 0 to `testch`, repeatedly publishes from node 1 until a message is received, checks data and sender identity, verifies topic-scoped peers, and checks topic listings on subscribed versus publishing-only nodes.

## Dependencies and Integration Points
Depends on PubSubAPI, KeyAPI self identity, pubsub topic options, and multi-node provider setup.

## Risks and Test Signals
Signals cover end-to-end publish/subscribe, sender metadata, and peer/topic queries. The publish retry loop is timing-sensitive and does not cover discovery-enabled subscribe, signatures, or sequence fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/pubsub.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/routing.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/routing.go

## Purpose
Conformance tests for routing value, peer, provider, and provide operations.

## Important APIs, Types, and Functions
Defines helper `testRoutingPublishKey` and tests `TestRoutingGet`, `TestRoutingPut`, `TestRoutingPutOffline`, `TestRoutingFindPeer`, `TestRoutingFindProviders`, and `TestRoutingProvide`.

## Control Flow and State
Tests create online swarms, publish IPNS records, retrieve and put routing values, enforce offline put failure unless `AllowOffline`, find peers and compare swarm local addresses, find providers for pinned content, and explicitly provide content added through an offline API view.

## Dependencies and Integration Points
Depends on Name, Routing, Unixfs, Pin, Swarm, Key APIs, IPNS record marshaling, and routing options.

## Risks and Test Signals
Signals cover DHT propagation and provider discovery but use sleeps/retries because routing is asynchronous. Risks include timing flakes, provider strategy assumptions, and only checking first provider/address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/routing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/unixfs.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/unixfs.go

## Purpose
Large CoreAPI conformance suite for UnixFS add, get, list, seek, read-at, pinning, hash-only, no-copy, events, progress, and close behavior.

## Important APIs, Types, and Functions
Defines fixtures `hello`, `emptyFile`, helpers `strFile`, `twoLevelDir`, `flatDir`, `wrapped`, close-test types, and tests `TestAdd`, `TestAddPinned`, `TestAddHashOnly`, `TestGetEmptyFile`, `TestGetDir`, `TestGetNonUnixfs`, `TestLs`, `TestEntriesExpired`, `TestLsEmptyDir`, `TestLsNonUnixfs`, `TestAddCloses`, `TestGetSeek`, and `TestGetReadAt`.

## Control Flow and State
`TestAdd` table-drives content through UnixFS add with CIDv1/raw leaves, alternate hash, inline, chunker/layout, offline, hash-only, directories/wrapping, hidden files, no-copy, events, silent, and progress options, then compares exact paths and round-trips content via `Get`. Later tests verify pin creation, hash-only non-storage, empty file read, directory retrieval, non-UnixFS errors, listing symlinks/files, canceled directory iterators, empty/non-UnixFS listing, input node closure, seek, and optional `ReaderAt`.

## Dependencies and Integration Points
Depends on Unixfs, Block, Pin, Dag APIs, options, Boxo files, UnixFS importer helpers, dag-cbor, CIDs, multihash, and random data.

## Risks and Test Signals
This is the main regression signal for UnixFS behavior: CID stability, option normalization, event ordering, no-copy path requirements, hash-only persistence, file closure, iterator cancellation, and random-access reads. It is large and exact-CID-heavy, so upstream UnixFS encoding changes require deliberate test updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/tests/unixfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/unixfs.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/unixfs.go

## Purpose
Defines CoreAPI UnixFS file/directory operations and listing event types.

## Important APIs, Types, and Functions
Declares `AddEvent`, `DirEntryType` constants `TUnknown`, `TFile`, `TDirectory`, `TSymlink`, `DirEntry`, and `UnixfsAPI` methods `Add`, `Get`, and `Ls`.

## Control Flow and State
There is no implementation flow. The interface describes importing files to content-addressed paths, retrieving paths as Boxo file nodes, and streaming directory entries through channels.

## Dependencies and Integration Points
Depends on context, Boxo files/path, CIDs, and UnixFS options. Implementations use `coreunix.Adder` and DAG/path resolvers.

## Risks and Test Signals
Risks include event channel ordering, directory entry close/error semantics, symlink targets, and random-access file support. Tests in `tests/unixfs.go` provide broad conformance coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/unixfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/util.go -->
# sources/distributed-fs/ipfs-kubo/core/coreiface/util.go

## Purpose
Provides a small helper for canonical empty path handling.

## Important APIs, Types, and Functions
Exports `Path(nil) path.Path`, a package-level variable initialized from `path.NewPath("/")`.

## Control Flow and State
Initialization parses `/` and panics if it fails. The exported variable is immutable path state shared by callers.

## Dependencies and Integration Points
Depends on Boxo path. It is a convenience constant for CoreAPI callers and implementations needing the root path.

## Risks and Test Signals
Risk is minimal; panic would only happen if Boxo path parsing of `/` broke. Compile and package init tests are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreiface/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corerepo/gc.go -->
# sources/distributed-fs/ipfs-kubo/core/corerepo/gc.go

## Purpose
Implements repository garbage collection orchestration, storage watermark checks, and result aggregation.

## Important APIs, Types, and Functions
Defines `ErrMaxStorageExceeded`, `GC`, `NewGC`, `BestEffortRoots`, `GarbageCollect`, `CollectResult`, `MultiError`, `GarbageCollectAsync`, `PeriodicGC`, `ConditionalGC`, and `(*GC).maybeGC`.

## Control Flow and State
`NewGC` reads repo config, initializes missing storage defaults in the repo config, parses storage max and watermark, and computes slack. GC roots are derived from MFS root. `GarbageCollect` and async variant call `gc.GC` over blockstore/datastore/pinner. `CollectResult` drains result channels, calls removal callbacks, and aggregates errors. Periodic/conditional GC compares storage usage plus offset to the GC watermark and runs GC when exceeded.

## Dependencies and Integration Points
Depends on Kubo core node, repo config/storage usage, Kubo `gc`, Boxo MFS, CIDs, humanize byte parsing, and logging. It interacts with add paths through blockstore GC locks and pin roots.

## Risks and Test Signals
Risks include mutating config defaults unexpectedly, best-effort root failures, multi-error construction assuming at least one error, GC running too often/late, and context cancellation while draining. Tests should cover watermark thresholds, config defaulting, result aggregation, and add-vs-GC concurrency; `coreunix/add_test.go` exercises live add safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corerepo/gc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corerepo/stat.go -->
# sources/distributed-fs/ipfs-kubo/core/corerepo/stat.go

## Purpose
Computes repository size and object-count statistics for repo stat APIs.

## Important APIs, Types, and Functions
Defines `SizeStat`, `Stat`, `NoLimit`, `RepoStat`, and `RepoSize`.

## Control Flow and State
`RepoSize` reads config, asks repo for storage usage, parses `Datastore.StorageMax` when configured, or returns `NoLimit`. `RepoStat` calls `RepoSize`, counts every blockstore key from `AllKeysChan`, obtains the best-known fsrepo path, and returns fs-repo version metadata.

## Dependencies and Integration Points
Depends on core node repo/blockstore, fsrepo path/version, humanize byte parsing, and context. Used by repo stat commands/APIs.

## Risks and Test Signals
Risks include expensive full blockstore scans, context cancellation during count, stale best-known repo path, and parse failures for storage max. Tests should cover no-limit, configured limit, storage usage errors, and object count accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corerepo/stat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreunix/add.go -->
# sources/distributed-fs/ipfs-kubo/core/coreunix/add.go

## Purpose
Implements the lower-level UnixFS adder used to import file trees into DAG/MFS, emit add/progress events, and optionally pin the resulting root safely with concurrent GC.

## Important APIs, Types, and Functions
Defines `Link`, `NewAdder`, `Adder`, `mfsRoot`, `SetMfsRoot`, `mkdirOpts`, `add`, `curRootNode`, `PinRoot`, `outputDirs`, `addNode`, `AddAllAndPin`, `addFileNode`, `addSymlink`, `addFile`, `addDir`, `maybePauseForGC`, `outputDagnode`, `getOutput`, `progressReader`, and `progressReader2`.

## Control Flow and State
`NewAdder` creates a buffered DAG and defaults. `AddAllAndPin` takes a pin lock when pinning, recursively adds nodes into an MFS root, flushes/closes the root, emits directory events, syncs async DAG services, and pins the final root. File adds chunk input, build balanced/trickle UnixFS DAGs, commit buffered blocks, and patch nodes into MFS. Directory adds peek for emptiness, optionally skip empty dirs, preserve root metadata, and recurse. During GC requests, `maybePauseForGC` pins the current root, releases/reacquires the pin lock, and tracks a temporary root.

## Dependencies and Integration Points
Depends on Boxo blockstore GC locks, files, chunker, filestore posinfo, merkledag, UnixFS importer, MFS, pinner, CIDs, Kubo config defaults, CoreAPI add events, and tracing. CoreAPI UnixFS add implementations configure and call this adder.

## Risks and Test Signals
Risks include GC races during long adds, MFS memory growth, event ordering, path/name handling for single files vs directories, no-copy posinfo propagation, metadata preservation drift, empty-directory semantics, and progress channel blocking. Tests cover GC live safety, no-copy posinfo, and CoreAPI UnixFS add/get/list behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreunix/add.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreunix/add_test.go -->
# sources/distributed-fs/ipfs-kubo/core/coreunix/add_test.go

## Purpose
Tests UnixFS adder safety around concurrent GC and filestore position metadata.

## Important APIs, Types, and Functions
Defines `TestAddMultipleGCLive`, `TestAddGCLive`, `testAddWPosInfo`, `TestAddWPosInfo`, `TestAddWPosInfoAndRawLeafs`, `testBlockstore`, `CheckForPosInfo`, and `dummyFileInfo`.

## Control Flow and State
GC live tests construct mock nodes, use pipe-backed files to pause adds mid-stream, start GC concurrently, assert GC waits for add lock handoff, then ensure newly added hashes are not collected. PosInfo tests wrap blockstore puts and count filestore nodes at offset zero/nonzero for no-copy adds with and without raw leaves.

## Dependencies and Integration Points
Depends on core node/repo mocks, Kubo GC, blockstore, Boxo files/filestore/merkledag, datastore, and add events.

## Risks and Test Signals
Strong signals cover add/GC lock choreography and filestore metadata propagation. The tests use sleeps/timeouts and pipe timing, so failures may indicate either real deadlocks or scheduling sensitivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreunix/add_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreunix/metadata.go -->
# sources/distributed-fs/ipfs-kubo/core/coreunix/metadata.go

## Purpose
Adds and reads UnixFS metadata wrapper nodes around existing DAG content.

## Important APIs, Types, and Functions
Exports `AddMetadataTo` and `Metadata`.

## Control Flow and State
`AddMetadataTo` decodes a CID string, loads the target DAG node, serializes UnixFS metadata, creates a new dag-pb node with metadata data and a `file` link to the target, adds it to the DAG, and returns the wrapper CID string. `Metadata` decodes and loads a CID, requires a dag-pb node, and parses metadata bytes from its data.

## Dependencies and Integration Points
Depends on Kubo core node DAG service, Boxo merkledag and UnixFS metadata, and CIDs. It supports legacy metadata wrapping around UnixFS file data.

## Risks and Test Signals
Risks include assuming the loaded metadata node is dag-pb, invalid metadata bytes, and hardcoded `file` link semantics. Tests verify adding metadata and reading the original file through the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreunix/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreunix/metadata_test.go -->
# sources/distributed-fs/ipfs-kubo/core/coreunix/metadata_test.go

## Purpose
Tests UnixFS metadata wrapping and retrieval.

## Important APIs, Types, and Functions
Defines helper `getDagserv` and `TestMetadata`.

## Control Flow and State
The test builds an in-memory DAG service, imports random data into a UnixFS DAG, wraps it with metadata, reads metadata back, loads the wrapper node, creates a DAG reader, and verifies the original bytes are still readable through the wrapper.

## Dependencies and Integration Points
Depends on blockservice, merkledag, UnixFS importer/io, offline exchange, blockstore, datastore, random data, and a minimal `IpfsNode{DAG: ds}`.

## Risks and Test Signals
Signals include metadata serialization, dag-pb wrapper shape, and content readability through the `file` link. It does not test malformed metadata, non-protobuf nodes, or missing target CIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreunix/metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/mock/mock.go -->
# sources/distributed-fs/ipfs-kubo/core/mock/mock.go

## Purpose
Provides helpers for constructing mock Kubo nodes and command contexts in tests.

## Important APIs, Types, and Functions
Exports `NewMockNode`, `MockHostOption`, `MockCmdsCtx`, and `MockPublicNode`.

## Control Flow and State
`NewMockNode` creates an online node using a mocknet host. `MockHostOption` adapts mocknet to Kubo's libp2p host option, applying listen addresses to the peerstore because mocknet does not consume libp2p options. `MockCmdsCtx` builds a mock repo/node and returns a command context. `MockPublicNode` initializes config, assigns deterministic public-looking swarm addresses based on mocknet peer count, and creates an online DHT server node.

## Dependencies and Integration Points
Depends on Kubo core/build config, repo mocks, command context, datastore, config initialization, libp2p mocknet/testing identity, peerstore, and host options. Used by tests needing lightweight nodes.

## Risks and Test Signals
Risks include mocknet behavior diverging from real libp2p, missing private key in some mock configs, address collisions from peer-count mapping, and tests accidentally depending on public-looking addresses. Signals are compile/test use across command/core tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/mock/mock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/bitswap.go -->
# sources/distributed-fs/ipfs-kubo/core/node/bitswap.go

## Purpose
Constructs Kubo Bitswap options, the Bitswap service, and the online exchange wrapper used by the node dependency graph.

## Important APIs, Types, and Functions
Defines Bitswap default constants, `bitswapOptionsOut`, `BitswapOptions`, `bitswapIn`, `Bitswap`, `OnlineExchange`, and `noopExchange`.

## Control Flow and State
`BitswapOptions` reads internal config defaults for workers, delays, outstanding bytes, and want-have replacement. `Bitswap` builds libp2p and/or HTTP retrieval networks, rejects configurations with both disabled, configures HTTP retrieval limits/allowlist/denylist, appends Kubo-specific provider query manager and broadcast-control options, decodes ignored providers, builds the provider query manager, enables/disables serving, creates Bitswap, and registers lifecycle close hooks. `OnlineExchange` returns either Bitswap or a no-op exchange that always reports not found.

## Dependencies and Integration Points
Depends on Boxo bitswap/client/network/httpnet, blockstore, exchange interface, provider query manager, Kubo config/version/helpers/shutdown, libp2p host/routing/peer, CIDs, and Uber Fx. It is part of node construction.

## Risks and Test Signals
Risks include config shadowing of the `libp2pEnabled` parameter, invalid ignored provider IDs aborting startup, HTTP retrieval security lists, broadcast-control default typo (`disabled` branch sets disposition to enabled), close hook ownership, and no-op exchange semantics when Bitswap inactive. Tests should cover network selection, config parsing, ignored providers, lifecycle close, and disabled exchange behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/bitswap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/builder.go -->
# sources/distributed-fs/ipfs-kubo/core/node/builder.go

## Purpose
Defines node build configuration defaults and Fx option provisioning for Kubo node construction.

## Important APIs, Types, and Functions
Defines `BuildCfg`, methods `getOpt`, `fillDefaults`, `options`, and helper `defaultRepo`.

## Control Flow and State
`fillDefaults` supplies an in-memory mock repo, DHT routing option, and default host option when omitted. `options` installs repo, host, routing, and metrics context providers into Fx, registers repo close on lifecycle stop, and reads the repo config. `defaultRepo` generates an RSA identity, peer ID, base64 private key, fallback bootstrap list, default swarm addresses, and returns a mock repo over the provided datastore.

## Dependencies and Integration Points
Depends on datastore, Kubo config/repo, autoconf bootstrap peers, libp2p routing/host option types, crypto identity generation, peer IDs, shutdown helpers, and Uber Fx. Used by `core.NewNode`.

## Risks and Test Signals
Risks include default repo identity generation cost, mock repo use when callers expected persistent state, repo close lifecycle errors, shutdown timeout behavior handled elsewhere, and default swarm addresses in tests. Tests should cover nil/default build configs, injected repo/host/routing, config read failures, and lifecycle stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/builder.go -->

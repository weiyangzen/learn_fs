# Research group subset-b-008169

Grouped research for Garage net, RPC, layout, and table replication files. Each section preserves the source path and is intended to be split into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/net/server.rs -->
# sources/object-store/garage/src/net/server.rs

Purpose: server-side NetApp connection handling. It authenticates inbound TCP sockets with `kuska_handshake`, wraps them in encrypted `BoxStream`s, sends the Garage version tag, and then runs receive/send loops for request/response streams.

Important APIs and types: `ServerConn` stores the remote socket address, authenticated peer `NodeID`, parent `NetApp`, an `ArcSwapOption` response channel, and a `Mutex<HashMap<RequestID, JoinHandle<()>>>` of running request handlers. `ServerConn::run` is the lifecycle entry point. `recv_handler_aux` resolves a request path into a registered endpoint and invokes the endpoint handler. The `RecvLoop` implementation spawns one task per request and `cancel_handler` aborts outstanding tasks.

Control flow: after handshake and version-tag write, `run` registers the connection as server-side with `NetApp`, starts `recv_loop` under `select!` with `await_exit`, starts `send_loop`, and tears down sender state when receive finishes. Each decoded `ReqEnc` carries priority, path, body, and optional telemetry context; responses are converted with `RespEnc::encode` and sent through `SendItem::Stream`.

State and persistence: no disk persistence. Runtime state is the response channel and in-flight handler map. Cancellation removes the join handle and sends `SendItem::Cancel` so the send loop can suppress the response.

Dependencies and integration: integrates with `netapp`, `endpoint` handlers, stream/message encoding, `tokio` tasks/channels, `arc-swap`, `futures`, and optional OpenTelemetry trace propagation.

Risks and test signals: per-request task spawning makes cancellation correctness important. A dropped response channel silently discards late work. Handler map locking must remain short. Telemetry is feature-gated. Network behavior is indirectly covered by ignored flaky peering tests in `net/test.rs`.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/net/server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/net/stream.rs -->
# sources/object-store/garage/src/net/stream.rs

Purpose: common byte stream abstraction used by Garage NetApp message and RPC layers. It converts packetized stream bodies to fixed-size reads and bridges between `ByteStream` and Tokio `AsyncRead`.

Important APIs and types: `ByteStream` is a pinned boxed `Stream<Item = Result<Bytes, io::Error>>`; `Packet` names each stream item. `ByteStreamReader` maintains an internal `BytesBuf`, end-of-stream flag, and deferred stream error. It exposes `read_exact`, `read_exact_or_eos`, `read_u8/u16/u32`, `fill_buffer`, `take_buffer`, `into_stream`, and `eos`. `ReadExactError` separates unexpected EOF from underlying IO failure. `ByteStreamReadExact` implements `Future`.

Control flow: `ByteStreamReadExact::poll` loops until the internal buffer can satisfy the requested byte count, an error arrives, EOF is reached, or the underlying stream yields another packet. `read_exact_or_eos` returns the remaining buffered bytes at EOF, whereas `read_exact` treats early EOF as an error. `into_stream` reconstructs a stream from unread buffered slices, a stored error, and the unconsumed stream tail.

State and persistence: all state is in-memory per reader. The module does not persist data or mutate global state.

Dependencies and integration: uses `bytes::Bytes`, `futures::{Stream, StreamExt, Future}`, Garage `BytesBuf`, and `tokio_util` adapters. `asyncread_stream`, `stream_asyncread`, and `read_stream_to_end` are integration shims for RPC body encoding, client/server connections, and streaming endpoints.

Risks and test signals: subtle behavior centers on preserving packet order and error-as-terminal semantics. `into_stream` must not drop already-read-but-unconsumed buffered bytes. No direct tests in this file; coverage comes through net protocol tests and all RPC streaming paths.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/net/stream.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/net/test.rs -->
# sources/object-store/garage/src/net/test.rs

Purpose: integration tests for the Garage NetApp peering layer under single-threaded and multi-threaded Tokio schedulers.

Important APIs and functions: `test_with_basic_scheduler` and `test_with_threaded_scheduler` are ignored `tokio::test`s that call `run_test`. `run_test` wraps `run_test_inner` in a 20 second timeout. `run_test_inner` creates three keypairs, three loopback addresses, starts three NetApps with a shared network key, and asserts peer-list convergence. `run_netapp` constructs `NetApp`, `PeeringManager`, and a spawned task running `listen` and `peering.run`.

Control flow: node 1 starts alone, node 2 bootstraps from node 1, the tests wait for gossip/peering convergence, and both peer managers should report two peers. Node 3 then bootstraps from node 2, waits again, and all three peer managers should report three peers. A watch channel broadcasts shutdown and the spawned tasks are awaited.

State and persistence: no persistent state. Runtime state consists of generated sodiumoxide auth/signing keys, socket listeners, peering state, and the stop watch channel.

Dependencies and integration: covers `NetApp::new`, `NetApp::listen`, `PeeringManager::new`, `PeeringManager::run`, `get_peer_list`, network handshakes, and connection propagation. It uses loopback TCP ports based at `19980` and `19990`.

Risks and test signals: both tests are marked `#[ignore = "flaky"]`, which is itself a strong signal that timing and port reuse are fragile. The fixed sleeps make tests scheduler/load dependent. They are still valuable as manual smoke tests for authenticated peering and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/net/test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/net/util.rs -->
# sources/object-store/garage/src/net/util.rs

Purpose: small utilities for NetApp serialization, shutdown signaling, and peer address parsing/resolution.

Important APIs and functions: `rmp_to_vec_all_named` serializes arbitrary Serde values to MessagePack with struct-map field names. `await_exit` blocks until a `watch::Receiver<bool>` observes `true` or the sender closes. `watch_ctrl_c` returns a cancellation receiver driven by `tokio::signal::ctrl_c`. `parse_peer_addr`, `parse_and_resolve_peer_addr`, and `parse_and_resolve_peer_addr_async` parse `<public key hex>@<host>:<port>` forms into `NodeID` plus socket addresses.

Control flow: `await_exit` repeatedly checks `borrow_and_update` and awaits `changed`. The parsers split at `@`, hex-decode the full public key, convert it to `NodeID`, then parse or resolve the host suffix. The async resolver delegates to `tokio::net::lookup_host`; the sync resolver uses `ToSocketAddrs`.

State and persistence: no persistence. `watch_ctrl_c` spawns one task and owns the sending side of a watch channel.

Dependencies and integration: used by client/server loops, system bootstrap peer resolution, endpoint serialization, and command-line peer specs. It depends on `rmp-serde`, `hex`, Tokio watch/signal, and Garage `NodeID`.

Risks and test signals: parser errors collapse to `None`, so callers need good diagnostics. Host resolution can return multiple addresses and callers decide retry order. `watch_ctrl_c` unwraps send and signal setup, appropriate for process-level shutdown but not for library isolation. No direct unit tests here.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/net/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/rpc/Cargo.toml -->
# sources/object-store/garage/src/rpc/Cargo.toml

Purpose: crate manifest for `garage_rpc`, the Garage cluster membership and RPC support crate.

Important configuration: the package is version `2.3.0`, edition 2018, AGPL-3.0, with `lib.rs` as the crate root. The description identifies it as "Cluster membership management and RPC protocol for the Garage object store".

Dependencies: internal workspace crates are `garage_util` and `garage_net`; external workspace dependencies include `arc-swap`, `bytesize`, `gethostname`, `hex`, `ipnet`, `tracing`, `rand`, `itertools`, `sodiumoxide`, `nix`, `async-trait`, `serde`, `serde_bytes`, `serde_json`, `utoipa`, `pnet_datalink`, `futures`, `tokio`, and `opentelemetry`. Optional dependencies support discovery: `reqwest` and `thiserror` for Consul, `kube`, `k8s-openapi`, and `schemars` for Kubernetes.

Features and integration: `kubernetes-discovery` enables Kubernetes CRD/client dependencies; `consul-discovery` enables HTTP/TLS Consul discovery; `system-libs` forwards `sodiumoxide/use-pkg-config`. Workspace lints are inherited.

State and persistence behavior: no runtime state itself, but the selected features control whether `system.rs` can advertise/discover peers via Consul or Kubernetes.

Risks and test signals: feature combinations must stay aligned with conditional modules in `lib.rs` and `system.rs`. The manifest note says newer `kube` requires Rust 2021, so dependency upgrades can be constrained by the crate's edition/toolchain support. Optional dependency drift can break discovery builds while core RPC still compiles.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/rpc/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/rpc/consul.rs -->
# sources/object-store/garage/src/rpc/consul.rs

Purpose: optional Consul service discovery integration for Garage RPC peers. It can query registered Garage nodes and publish the local node into either the Consul catalog API or local agent service API.

Important APIs and types: `ConsulDiscovery` holds `ConsulDiscoveryConfig` and a configured `reqwest::Client`. `new` builds TLS roots, optional client certificate identity for catalog API, optional invalid-cert acceptance, and token headers. `get_consul_nodes` returns `(NodeID, SocketAddr)` pairs. `publish_consul_service` registers the local node. `ConsulError` wraps IO, reqwest, invalid TLS config, and token-header errors. Internal structs model Consul's JSON shapes and use `META_PREFIX` for Garage metadata keys.

Control flow: reads query one or more configured datacenters, fetch `/v1/catalog/service/<service>`, deserializes entries, parses IP and Garage public key metadata, and skips malformed entries with warnings. Publishing constructs a deterministic service ID from the node key prefix, merges configured tags/meta, stores pubkey and hostname metadata, then PUTs to `catalog/register` or `agent/service/register?replace-existing-checks`.

State and persistence: no local persistent state. It reads certificate/key files at initialization and writes discovery state only into Consul.

Dependencies and integration: used by `System::discovery_loop` and `advertise_to_consul` behind `consul-discovery`. Relies on `garage_util::config`, `garage_net::NodeID`, `reqwest` rustls, and Consul HTTP API behavior.

Risks and test signals: malformed Consul metadata reduces discovery without failing the whole query. Catalog API requires cert/key pair consistency. Datacenter aggregation does not deduplicate nodes. No in-repo tests here; integration depends on external Consul availability and feature builds.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/rpc/consul.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/rpc/kubernetes.rs -->
# sources/object-store/garage/src/rpc/kubernetes.rs

Purpose: optional Kubernetes peer discovery and advertisement through a `GarageNode` custom resource.

Important APIs and types: `Node` is the spec for the generated `GarageNode` CRD, with hostname, IP address, and RPC port. `create_kubernetes_crd` applies the CRD cluster-wide. `get_kubernetes_nodes` lists namespaced `GarageNode`s by service label and returns `(NodeID, SocketAddr)`. `publish_kubernetes_node` creates or replaces the object named by the hex node ID.

Control flow: CRD creation uses server-side apply with field manager `garage.deuxfleurs.fr`. Listing builds a label selector `garage.deuxfleurs.fr/service=<service>`, logs found object names, decodes each object name as a Garage public key, and returns only valid IDs. Publishing builds a `GarageNode`, inserts the same service label, then performs `get`; if the object exists, it preserves `resource_version` and calls `replace`, otherwise it calls `create`.

State and persistence: no local persistence. Cluster-visible state is the CRD and one custom resource per advertised node in the configured namespace.

Dependencies and integration: feature-gated through `kubernetes-discovery`, called by `System::discovery_loop` and `advertise_to_kubernetes`. Depends on `kube`, `k8s-openapi`, `schemars`, Serde, and `garage_util::config::KubernetesDiscoveryConfig`.

Risks and test signals: requires Kubernetes credentials and RBAC for CRDs and namespaced resources. Object name equals node public key hex, so invalid names are silently ignored on read. Replace can race with other writers if resource versions change. No direct tests; validation is mainly compile/feature and live-cluster integration.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/rpc/kubernetes.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/rpc/layout/graph_algo.rs -->
# sources/object-store/garage/src/rpc/layout/graph_algo.rs

Purpose: graph primitives and algorithms used by layout computation to assign partitions to nodes under replication, capacity, zone, and rebalance constraints.

Important APIs and types: `Vertex` models source/sink, partition upper/lower vertices, partition-zone vertices, and node vertices. `FlowEdge` and `WeightedEdge` back `Graph<FlowEdge>` and `Graph<WeightedEdge>`. `CostFunction` maps directed vertex pairs to costs. Public flow APIs include `add_edge`, `get_positive_flow_from`, `get_outflow`, `flow_upper_bound`, `compute_maximal_flow`, and `optimize_flow_with_cost`.

Control flow: `compute_maximal_flow` implements Dinic's algorithm over adjacency lists, first shuffling edges with deterministic seeded randomness to distribute assignments consistently across runs. It builds BFS levels, then iterative DFS paths, updating forward/reverse residual flows. `optimize_flow_with_cost` converts residual capacity into a weighted graph, finds negative cycles with bounded Bellman-Ford, and pushes one unit around each cycle until no improving cycle remains. `cycles_of_1_forest` extracts cycles from predecessor links.

State and persistence: graphs are in-memory only. Deterministic shuffle is important state behavior because `garage layout show` and actual application must agree.

Dependencies and integration: used from `layout/version.rs` for optimal partition size, candidate assignment, and rebalance minimization. Depends only on standard collections and `rand` seeded RNG.

Risks and test signals: correctness is algorithmic and error-prone: reverse-edge indices must stay valid after shuffling, capacities are `u64` but flows are `i64`, and bounded negative-cycle search assumes layout graph structure. Coverage comes through layout assignment tests rather than unit tests of graph internals.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/rpc/layout/graph_algo.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/rpc/layout/helper.rs -->
# sources/object-store/garage/src/rpc/layout/helper.rs

Purpose: cached, validated wrapper around persisted `LayoutHistory`. It computes fast-read layout views, synchronization digests, and local update tracker changes.

Important APIs and types: `RpcLayoutDigest` advertises current layout version, active version count, tracker hash, and staging hash. `SyncLayoutDigest` tracks fields relevant to table sync. `LayoutHelper` owns an optional `LayoutHistory`, consistency mode, cached ack/sync minima, all nodes, storage nodes, hashes, validity flag, and `ack_lock` counters keyed by layout version.

Control flow: `new` optionally collapses history to the current version for non-consistent modes, prunes old versions, computes all node sets, clamps update trackers, calculates `ack_map_min` and quorum-aware `sync_map_min`, hashes trackers/staging, retains active ack locks, and records whether `layout.check()` passed. `update` is the only mutation wrapper: it applies a closure to `LayoutHistory` and rebuilds all caches if changed. `current`, `versions`, `read_version`, `all_nodes`, and `all_nongateway_nodes` refuse access when layout checks fail.

State and persistence: no direct disk IO, but it wraps the state persisted by `LayoutManager`. The ack lock blocks acknowledging a newer layout while local writes still use an older version.

Dependencies and integration: central to `LayoutManager`, table replication read/write sets, system status exchange, and sync scheduling. Uses Garage CRDT/data/error types and replication consistency modes.

Risks and test signals: `update_ack_to_max_free` is subtle because a wrong ack can let the cluster prune an old layout while writes are still in flight. Read-version selection depends on sync trackers and quorums. Tests are indirect through layout/history/table sync behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/rpc/layout/helper.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/rpc/layout/history.rs -->
# sources/object-store/garage/src/rpc/layout/history.rs

Purpose: layout history lifecycle and CRDT merge logic for active, old, and staged cluster layouts.

Important APIs and functions: `LayoutHistory::new`, `current`, `min_stored`, `get_all_nodes`, `get_all_nongateway_nodes`, `keep_current_version_only`, `cleanup_old_versions`, `clamp_update_trackers`, `calculate_sync_map_min_with_quorum`, `calculate_trackers_hash`, `calculate_staging_hash`, `merge`, `apply_staged_changes`, `revert_staged_changes`, and `check`.

Control flow: cleanup removes invalid leading versions when a later current layout is valid, moves active versions to `old_versions` once current nodes have sync-acked beyond them, and caps `old_versions` at `OLD_VERSION_COUNT`. Sync-map calculation returns the current version for single-version histories, uses the global min when writes require all replicas, and otherwise evaluates write sets by partition to find a safe read version under quorum rules. `merge` appends next versions, checks conflicting same-version layouts, merges update trackers, and merges staged CRDT changes. `apply_staged_changes` computes the next `LayoutVersion`, pushes it, cleans up, and clears staged role changes while preserving parameters.

State and persistence: `LayoutHistory` is the persisted object saved as `cluster_layout` by `LayoutManager`. Trackers determine when old versions are safe to retire.

Dependencies and integration: uses CRDT `Lww`/`LwwMap`, nonversioned encoding for hashes, replication factors, and `ComputationStat` from `version.rs`. Table sync reports progress back into these trackers.

Risks and test signals: history merge assumes linear version increments and logs conflicts instead of resolving divergent same-version layouts. Wrong tracker math can break read-after-write consistency. Assignment tests exercise staged changes; broader tracker behavior is mostly integration-tested by cluster operation.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/rpc/layout/history.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/rpc/layout/manager.rs -->
# sources/object-store/garage/src/rpc/layout/manager.rs

Purpose: runtime owner of cluster layout state. It loads and saves layout history, merges advertised layouts and trackers, broadcasts updates, and provides write locks that coordinate layout acknowledgments with table writes.

Important APIs and types: `LayoutManager::new`, `layout`, `update_cluster_layout`, `add_table`, `sync_table_until`, `write_lock_with`, `handle_advertise_status`, pull/advertise handlers, and `WriteLock<T>`. Fields include local node ID, replication factor, `Persister<LayoutHistory>`, `RwLock<LayoutHelper>`, change `Notify`, per-table sync versions, `RpcHelper`, and system endpoint.

Control flow: initialization loads `cluster_layout`, validates replication factor compatibility, or creates a fresh history. It wraps it in `LayoutHelper`, updates local trackers, and builds `RpcHelper`. Advertised status digests trigger async pulls for full layouts or tracker-only updates. Merge functions write-lock the helper, merge valid incoming state, update local trackers, notify waiters, broadcast the new state, and save asynchronously. `sync_table_until` computes the minimum sync version across registered tables and advertises tracker progress.

State and persistence: persists `cluster_layout` under the metadata directory. Runtime state includes table sync progress and ack-lock counters. `WriteLock` increments the current layout's lock count; its `Drop` decrements and may advance local ack when all older writes finish.

Dependencies and integration: connects `SystemRpc`, `RpcHelper`, `PeeringManager`, `Persister`, `LayoutHelper`, and table replication write sets.

Risks and test signals: replication-factor mismatch aborts layout reuse for safety. `WriteLock::drop` unwraps `current`, so layout invalidity during drop would be serious. Async broadcast/save errors are logged. Tests are indirect through layout and table write/sync paths.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/rpc/layout/manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/rpc/layout/mod.rs -->
# sources/object-store/garage/src/rpc/layout/mod.rs

Purpose: layout module root. It defines persisted layout data types, migration formats, constants, re-exports, and CRDT helpers.

Important APIs and types: re-exports `LayoutHelper`, `RpcLayoutDigest`, `SyncLayoutDigest`, `WriteLock`, and all current version types. Constants include `PARTITION_BITS = 8`, `NB_PARTITIONS = 256`, `CompactNodeType = u8`, and `MAX_NODE_NUMBER = 256`. Current `v010` types are `LayoutHistory`, `LayoutVersion`, `LayoutStaging`, `UpdateTrackers`, and `UpdateTracker`; older `v08` and `v09` modules define migration inputs.

Control flow and migrations: `v09::ClusterLayout::migrate` converts old arbitrary capacity units to bytes, derives partition size from old assignment data, introduces `LayoutParameters`, and creates staging fields. `v010::LayoutHistory::migrate` wraps the old cluster layout into a one-version history and initializes ack/sync/sync-ack trackers for storage nodes. Utility CRDT implementations make layout parameters and node roles warn on divergence, while `LayoutStaging::merge` merges parameters and roles.

State and persistence: the current data structures are serialized to disk by `Persister<LayoutHistory>`. `node_id_vec` ordering deliberately places storage nodes before gateways so compact assignment bytes can index storage nodes efficiently.

Dependencies and integration: consumed by RPC layout manager, table replication, system metrics, and admin layout commands. Uses `garage_util` CRDT/data migration facilities.

Risks and test signals: compact node IDs cap non-gateway storage nodes at 256. Migration capacity scaling is explicitly arbitrary and may be inaccurate for old deployments. A duplicated `versions` field appears in the shown `v010::LayoutHistory` block and would be a compile concern if present in the active source. Layout tests validate assignment behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/rpc/layout/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/rpc/layout/test.rs -->
# sources/object-store/garage/src/rpc/layout/test.rs

Purpose: unit tests and helper routines for partition assignment quality across changing cluster topologies.

Important functions: `check_against_naive` attempts a naive token-based assignment with partition size `S + 1` and returns whether the optimized algorithm beats that baseline. `show_stat` prints `ComputationStat`. `update_layout` stages node roles and zone redundancy. `test_assignment` applies four successive layout configurations and verifies consistency and baseline quality.

Control flow: the test creates a replication factor 3 history, stages roles/capacities/zones, applies staged changes, prints stats, checks `LayoutHistory::check`, and asserts that the partition size is not worse than the naive model. It then modifies capacities, zones, and redundancy, applying several more versions to exercise rebalance and reassignment behavior.

State and persistence: all layout state is in-memory. Node IDs are deterministic fixed-byte values derived from the loop index, making results reproducible.

Dependencies and integration: directly exercises `LayoutHistory::apply_staged_changes`, `LayoutVersion` assignment computation, CRDT staging updates, zone redundancy parameters, and `ComputationStat`.

Risks and test signals: the naive check is not a proof of optimality; comments document a counterexample for the naive algorithm. The test mainly guards gross regressions in assignment validity and capacity usage. It does not test layout-manager persistence, tracker propagation, or multi-node sync behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/rpc/layout/test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/rpc/layout/version.rs -->
# sources/object-store/garage/src/rpc/layout/version.rs

Purpose: implements the active layout version behavior: node/partition accessors, consistency checks, next-version computation, capacity-optimal assignment, rebalance minimization, and computation reporting.

Important APIs and types: `LayoutVersion::new`, `all_nodes`, `nongateway_nodes`, `node_role`, `partition_of`, `partitions`, `nodes_of`, quorum helpers, `check`, `calculate_next_version`, `calculate_partition_assignment`, `generate_nongateway_zone_ids`, and `ComputationStat` with zone/node stat structs.

Control flow: `calculate_next_version` merges staged roles, prunes removed roles, applies parameters, and calls `calculate_partition_assignment`. Assignment updates node IDs, determines effective zone redundancy, validates enough storage nodes/zones, computes maximal feasible partition size by binary search with max flow, computes a candidate assignment biased toward previous edges, optimizes rebalance with negative-cycle cost improvements, emits stats, writes `ring_assignment_data`, and rechecks invariants. `check` validates assignment length, node sets, no gateway assignments, distinct replicas per partition, zone redundancy, capacity limits, and optimal partition size.

State and persistence: `LayoutVersion` is part of persisted `LayoutHistory`. `ring_assignment_data` stores compact node indices for each partition replica; `partition_size` is persisted for checks and reporting.

Dependencies and integration: uses graph algorithms, CRDT maps, `bytesize`, `itertools`, `utoipa`, and replication-mode quorum logic. Table sharded replication relies on `nodes_of` and partition iteration.

Risks and test signals: this file carries the highest algorithmic risk. Capacity math uses integer division and requires viable capacities; small partition sizes trigger warnings. Any change to `PARTITION_BITS`, compact node type, or assignment ordering affects data placement. `layout/test.rs` exercises several reassignment scenarios but not all edge cases.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/rpc/layout/version.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/rpc/lib.rs -->
# sources/object-store/garage/src/rpc/lib.rs

Purpose: crate root for `garage_rpc`.

Important exports: imports `tracing` macros, declares private `metrics` and `system_metrics`, conditionally declares `consul` and `kubernetes`, and publicly exposes `layout`, `replication_mode`, `system`, and `rpc_helper`. It also re-exports `rpc_helper::*`, making common RPC types and helpers available through the crate root.

Control flow: no runtime control flow; this is module wiring.

State and persistence: none directly. Persistence is implemented in the submodules, particularly `layout::manager` and `system`.

Dependencies and integration: ties together the public surface used by `garage_table`, block management, API/admin layers, and cluster startup. Feature gates here must match manifest features and conditional uses in `system.rs`.

Risks and test signals: overly broad `pub use rpc_helper::*` makes helper API changes externally visible. Feature-gated modules must stay synchronized with `Cargo.toml`. No tests in this file; compile coverage across feature combinations is the main signal.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/rpc/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/rpc/metrics.rs -->
# sources/object-store/garage/src/rpc/metrics.rs

Purpose: OpenTelemetry metrics for outbound RPC behavior.

Important APIs and types: `RpcMetrics` owns counters for emitted RPCs, timeouts, NetApp communication errors, Garage handler errors, and a duration recorder. `RpcMetrics::new` registers instruments under meter `garage_rpc`.

Control flow: construction initializes instruments. Recording happens in `rpc_helper.rs`, where each call increments `rpc_counter`, records duration, and increments timeout/network/Garage error counters according to outcome.

State and persistence: metric instruments are runtime observers/counters only; no persistence.

Dependencies and integration: depends on `opentelemetry::{global, metrics::*}`. `RpcHelperInner` stores one `RpcMetrics` instance and attaches endpoint/from/to tags while recording.

Risks and test signals: metric naming and cardinality matter. Tags include node IDs and endpoints, which are useful but can grow with cluster size. The file comment incorrectly says `TableMetrics`, a naming drift risk. No direct tests; observability is validated by runtime metrics export.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/rpc/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/rpc/replication_mode.rs -->
# sources/object-store/garage/src/rpc/replication_mode.rs

Purpose: parses and represents cluster replication factor and consistency mode configuration.

Important APIs and types: `ReplicationFactor(usize)` guarantees factor >= 1 through `new`; `ConsistencyMode` has `Dangerous`, `Degraded`, and default `Consistent`. Methods compute read and write quorums. `parse_replication_mode` converts `Config` fields into `(ReplicationFactor, ConsistencyMode)`.

Control flow: quorum behavior is mode-dependent. `Dangerous` reads and writes with quorum 1. `Degraded` reads with 1 but writes enough to satisfy the consistent write quorum. `Consistent` uses `ceil(replication_factor / 2)` read quorum and complementary write quorum. Parsing rejects the legacy `replication_mode`, requires `replication_factor`, validates factor and consistency string, and returns configuration errors.

State and persistence: values are serialized/deserialized and embedded in layout/history/status, but this file has no IO.

Dependencies and integration: used by layout creation/checks, table replication, system status validation, and config parsing. Implements `AutoCrdt` for `ConsistencyMode` with divergence warnings.

Risks and test signals: `Dangerous` can sacrifice consistency by design. Config mismatch between nodes is checked in `System::handle_advertise_status`; a higher remote replication factor forces process exit for safety. No direct tests here.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/rpc/replication_mode.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/rpc/rpc_helper.rs -->
# sources/object-store/garage/src/rpc/rpc_helper.rs

Purpose: high-level RPC orchestration: single calls, broadcasts, quorum reads, write-set quorum writes, request ordering, block read node ordering, and quorum result tracking.

Important APIs and types: `RequestStrategy` configures quorum, send-all behavior, priority, timeout, and drop-on-complete payload. `RpcHelper` wraps peer manager, layout, metrics, local node ID, and timeout. Public methods include `call`, `call_many`, `broadcast`, `try_call_many`, `try_write_many_sets`, and `block_read_nodes_of`. `QuorumSetResultTracker` tracks successes/failures across overlapping quorum sets.

Control flow: `call` performs a streaming endpoint call under OpenTelemetry context and a selectable timeout, translating NetApp and Garage errors into metrics. `try_call_many` orders nodes by locality/latency, sends only enough requests to reach quorum unless `send_all_at_once`, and stops once quorum succeeds or becomes impossible. `try_write_many_sets` sends to every unique node immediately, waits for quorum in every write set, and moves unfinished requests to a background task after success so broadcast writes can still complete on lagging replicas.

State and persistence: no persistence. Runtime state is per-call futures and metric counters.

Dependencies and integration: core dependency for `System`, layout manager, table GC/sync, and higher storage layers. Uses Garage NetApp endpoint abstractions, layout versions, peering ping state, OpenTelemetry, and `RecordDuration`.

Risks and test signals: dropping read-style futures cancels remote handlers, which is intentional but unsuitable for writes. `try_write_many_sets` relies on tracker correctness for overlapping layout versions. Node ordering assumes current layout has zone data. No direct tests in file; exercised by table/system integration.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/rpc/rpc_helper.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/rpc/system.rs -->
# sources/object-store/garage/src/rpc/system.rs

Purpose: cluster membership manager. It owns node identity, NetApp RPC listener, full-mesh peering, discovery, status exchange, layout manager, health reporting, and system RPC handling.

Important APIs and types: `SystemRpc` includes connect, status, known-node, and layout pull/advertisement messages. `System` stores local ID, persisted peer list, local/remote statuses, NetApp, peering manager, endpoint, listen/public addresses, optional discovery configs, layout manager, metrics, replication factor, and data/metadata paths. Functions include `read_node_id`, `gen_node_key`, `System::new`, `run`, `get_known_nodes`, `connect`, `health`, discovery/status loops, and `EndpointHandler<SystemRpc>`.

Control flow: startup reads or generates an ed25519 node key, creates `NetApp`, endpoint, peering manager, peer-list persister, layout manager, local status, optional discovery clients, and metrics. `run` joins listener, peering, discovery, and status loops. Discovery resolves bootstrap peers, reloads persisted peers, optionally queries Consul/Kubernetes, filters to layout nodes when appropriate, tries connections asynchronously, saves peers, and advertises itself. Status exchange broadcasts local status every 10 seconds. RPC handling delegates layout messages to `LayoutManager`.

State and persistence: persists `node_key`, `node_key.pub`, and `peer_list`; layout persistence is delegated. Local and remote node statuses are in `RwLock`s.

Dependencies and integration: integrates config, NetApp, peering, discovery modules, layout, RPC helper, metrics, disk usage, and node health.

Risks and test signals: replication-factor mismatch can terminate the process for safety. Public address autodetection can be wrong on complex networks. Discovery loops spawn connection attempts without awaiting them. Health depends on current layout validity. Tests are mostly external/integration.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/rpc/system.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/rpc/system_metrics.rs -->
# sources/object-store/garage/src/rpc/system_metrics.rs

Purpose: OpenTelemetry observers for Garage system, disk, cluster health, and per-layout-node status.

Important APIs and types: `SystemMetrics` owns value observers for build info, replication factor, local disk availability/total, cluster healthy/available flags, node/partition counts, per-node connected status, and disconnected time. `SystemMetrics::new` registers instruments under `garage_system`.

Control flow: construction creates a one-second cached closure around `System::health` to avoid recomputing expensive partition health for every observer. Observers read `System::local_status`, `cluster_layout`, and `get_known_nodes`, attach role labels when available, and observe current values.

State and persistence: no persistence. The only mutable state is the short-lived `RwLock` health cache captured by observers. `System::cleanup` drops metrics to break reference cycles.

Dependencies and integration: depends on OpenTelemetry, `System`, `ClusterHealthStatus`, and Garage version helpers. Created during `System::new` and held in an `ArcSwapOption`.

Risks and test signals: observer closures capture `Arc<System>`, so cleanup is needed to avoid cycles. Labels include node IDs and role properties; cardinality grows with cluster size and role churn. Some comments note omitted hostname/address labels because OpenTelemetry aggregation would duplicate metrics. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/rpc/system_metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/Cargo.toml -->
# sources/object-store/garage/src/table/Cargo.toml

Purpose: crate manifest for `garage_table`, Garage's table sharding and replication engine.

Important configuration: package version `2.3.0`, edition 2018, AGPL-3.0, `lib.rs` as root. The description says it is a "Table sharding and replication engine (DynamoDB-like) for the Garage object store".

Dependencies: internal crates are `garage_db`, `garage_rpc`, and `garage_util`. External workspace dependencies include OpenTelemetry, `async-trait`, `arc-swap`, `hex`, `hexdump`, `tracing`, `rand`, `serde`, `serde_bytes`, `futures`, `futures-util`, and Tokio. Workspace lints apply.

State and persistence behavior: the manifest itself has none, but dependency choices show the crate owns DB-backed table persistence, RPC sync/GC, background workers, metrics, and async coordination.

Integration points: consumed by Garage table definitions and storage subsystems. It depends on RPC layout and system crates, so table consistency is tightly coupled to cluster membership and layout history.

Risks and test signals: no feature flags here; it always compiles table sync, GC, Merkle, and replication support. API compatibility with `garage_db`, `garage_rpc`, and `garage_util` is critical. Workspace lint changes can affect this crate broadly.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/data.rs -->
# sources/object-store/garage/src/table/data.rs

Purpose: local persistent data engine for one logical Garage table. It owns DB trees, read helpers, transactional mutation logic, insert queueing, Merkle todo updates, schema hooks, and GC todo scheduling.

Important APIs and types: `TableData<F, R>` stores `System`, schema instance, replication policy, main `store`, `merkle_tree`, `merkle_todo`, `insert_queue`, `gc_todo`, notifications, and metrics. Key methods include `new`, `read_entry`, `read_range`, `update_many`, `update_entry`, `update_entry_with`, `delete_if_equal`, `delete_if_equal_hash`, `queue_insert`, `tree_key`, and `decode_entry`.

Control flow: reads use `partition_key.hash() + sort_key` DB keys and range scans constrained by the partition hash prefix. Mutations run in DB transactions: decode old value, compute merged/new value, encode/migration-normalize it, write `merkle_todo`, write store, and call schema `updated`. After commit, changed tombstones may be inserted into `gc_todo` only if this node is first replica for the partition. Deletes are compare-and-delete operations that also enqueue empty Merkle todos and call schema hooks.

State and persistence: opens five persistent trees per table: `<table>:table`, `:merkle_tree`, `:merkle_todo`, `:insert_queue`, and `:gc_todo_v2`. Notifications wake background workers after commits.

Dependencies and integration: used by `Table`, `MerkleUpdater`, `InsertQueueWorker`, `TableGc`, and `TableSyncer`. Depends on CRDT merge, schema migration, replication node selection, and Garage DB transactions.

Risks and test signals: transaction boundaries are critical; missing Merkle todo or schema hook would corrupt sync/index behavior. The tombstone leader comment notes layout changes may break GC leadership assumptions. Decode failures are hexdumped. Tests are indirect via table users.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/data.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/gc.rs -->
# sources/object-store/garage/src/table/gc.rs

Purpose: garbage collection for table tombstones. It waits a delay, ensures all replica nodes have observed a tombstone, then deletes the tombstone locally and remotely if still equal.

Important APIs and types: `TableGc<F, R>` owns `System`, `TableData`, and a `GcRpc` endpoint. `GcRpc` has `Update`, `DeleteIfEqualHash`, and `Ok`. `GcWorker` drives background work. `GcTodoEntry` encodes todo keys as tombstone timestamp plus table key and stores the tombstone value hash.

Control flow: `gc_loop_iter` scans `gc_todo` by timestamp, waits until the earliest deletion time, filters candidates whose current table value still hashes to the tombstone hash, removes stale todos, groups live tombstones by remote storage-node set, and runs `try_send_and_delete`. That method sends tombstone values to every other replica with quorum equal to all nodes, then asks them to delete if their value hash still matches, then deletes locally and removes todos. RPC handlers apply updates or compare-delete hashes.

State and persistence: persistent state is the `gc_todo_v2` DB tree and main table rows. GC does not delete unless all target nodes respond, so failures leave todos for retry.

Dependencies and integration: depends on table replication, RPC helper quorum calls, background worker API, table update/delete primitives, and wall-clock `now_msec`.

Risks and test signals: GC correctness is safety-critical because premature deletion can resurrect old CRDT values. It intentionally requires all remote nodes, trading liveness for safety. Layout changes during GC can alter storage sets. No direct tests here; behavior is integration-level.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/gc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/lib.rs -->
# sources/object-store/garage/src/table/lib.rs

Purpose: crate root for `garage_table`.

Important exports: declares public modules `schema`, `util`, `data`, `replication`, and `table`; private modules `gc`, `merkle`, `metrics`, `queue`, and `sync`; re-exports schema, table, and util APIs; and re-exports Garage CRDT utilities under `garage_table::crdt`.

Control flow: no runtime logic. The root also sets `recursion_limit = "1024"` and allows `clippy::comparison_chain`, likely for generated/complex generic code and existing style.

State and persistence: none directly. Persistence is implemented by `data`, `merkle`, `gc`, and workers in submodules.

Dependencies and integration: this is the public boundary consumed by Garage model tables and service crates. Private modules are still wired through `table.rs` and `data.rs` to provide replication, sync, GC, and metrics.

Risks and test signals: public re-exports shape downstream API compatibility. Keeping worker modules private limits direct external coupling. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/merkle.rs -->
# sources/object-store/garage/src/table/merkle.rs

Purpose: maintains per-table Merkle trees used by anti-entropy synchronization. Data is split into 2^16 Merkle partitions based on partition-key hash prefixes.

Important APIs and types: `MerkleUpdater<F, R>` owns `TableData` and the empty-node hash. `MerkleNodeKey` identifies a partition and hash prefix. `MerkleNode` is `Empty`, `Intermediate(Vec<(u8, Hash)>)`, or `Leaf(key, value_hash)`. Methods include `new`, `spawn_workers`, `update_item`, recursive `update_item_rec`, `read_node`, and approximate length helpers.

Control flow: the worker reads the first `merkle_todo` entry, computes the full table-key hash, maps the partition through replication, recursively updates the tree, then removes the todo only if it still equals the processed value hash. Recursion collapses empty/single-child intermediates, splits leaf collisions into deeper prefixes, and stores non-empty nodes as nonversioned-encoded blobs whose hashes form parent entries. Work is batched in `spawn_blocking` for up to 100 updates per iteration.

State and persistence: persistent trees are `merkle_tree` and `merkle_todo`. Empty nodes are implicit by missing DB entries. A todo value is either a value hash or empty bytes for deletion.

Dependencies and integration: used by `TableSyncer` for root/node comparisons and by `TableData` mutations through Merkle todos. Depends on Garage DB transactions, layout partitions, nonversioned encoding, background workers, and Tokio notifications.

Risks and test signals: Merkle lag is tolerated and logged during sync. Recursive collision handling and ordered intermediate children are correctness-sensitive. There is a direct unit test for intermediate child insert/remove ordering, but full tree update behavior is integration-tested.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/merkle.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/metrics.rs -->
# sources/object-store/garage/src/table/metrics.rs

Purpose: OpenTelemetry metrics for per-table storage size, queues, operations, and sync traffic.

Important APIs and types: `TableMetrics` owns value observers for table size, Merkle tree size, Merkle todo length, insert queue length, and GC todo length; bound counters/recorders for get and put requests; counters for internal updates/deletes; and counters for sync items sent/received. `TableMetrics::new` binds instruments to a table name.

Control flow: observers call `approximate_len` on the relevant DB trees when scraped. Request/update/delete counters are incremented by table operations elsewhere. Sync counters are recorded by `sync.rs`.

State and persistence: no persistent state in the metrics object. It keeps cloned DB tree handles so observers can query live approximate lengths.

Dependencies and integration: constructed by `TableData::new`, used in data mutation, table API, sync sending/receiving, and background status.

Risks and test signals: observer closures must not panic if DB length calls fail; the code ignores errors. The GC observer block shows indentation drift, but behavior is simple. Bound table-name labels keep per-table metrics stable; sync counters add `to`/`from` labels with node IDs. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/queue.rs -->
# sources/object-store/garage/src/table/queue.rs

Purpose: background worker that drains the local insert queue and republishes queued entries through normal table replication.

Important APIs and types: `InsertQueueWorker<F, R>(Arc<Table<F, R>>)` implements `garage_util::background::Worker`. `BATCH_SIZE` is 1024.

Control flow: `work` scans up to slightly over `BATCH_SIZE` entries from `data.insert_queue`, decodes them, calls `Table::insert_many` to replicate/apply them, and then removes queue rows only if their stored value still equals the processed value. `wait_for_work` wakes on either a 600 second timer or `insert_queue_notify`.

State and persistence: persistent state is the `insert_queue` DB tree. Compare-before-remove prevents losing a newer merged queued value that arrived while the batch was being processed.

Dependencies and integration: `TableData::queue_insert` writes this queue inside transactions and notifies after commit. The worker depends on table replication APIs, schema decoding, background worker status, Tokio select/watch, and queue approximate length for status.

Risks and test signals: if `insert_many` repeatedly fails, the queue remains and retries later. Decoding failures stop the worker iteration. Batching condition uses `> BATCH_SIZE`, so it may process 1025 entries. No direct tests; behavior depends on table insertion tests/integration.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/queue.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/replication/fullcopy.rs -->
# sources/object-store/garage/src/table/replication/fullcopy.rs

Purpose: `TableReplication` implementation for small fully replicated tables, where every layout node stores every entry.

Important APIs and types: `TableFullReplication` stores `Arc<System>` and `ConsistencyMode`. It implements storage/read nodes, read/write quorum calculation, write sets, partition mapping, and sync partition enumeration.

Control flow: `storage_nodes` returns all layout nodes across the current cluster layout. `read_nodes` uses the layout's `read_version` all nodes. In consistent mode, read quorum is majority of read-version nodes; dangerous/degraded reads need one. `write_sets` returns one all-node set for each active layout version under a layout write lock. Write quorum is majority-like across active versions, with a warning and fallback if active layouts have very different node counts. Sync treats the entire table as partition `0` over the full hash range.

State and persistence: no persistence here. It reads layout state from `System` and participates in ack-locking through `WriteLock`.

Dependencies and integration: used by tables that are small enough to store on gateways and storage nodes. Tightly coupled to `System::cluster_layout` and layout history.

Risks and test signals: comments note layout tracking is harder because gateway nodes store this data but are not storage nodes for sharded data. If writes fail, nodes can read outdated data. The warning path for mismatched active layout sizes indicates possible quorum degradation. No direct tests in file.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/replication/fullcopy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/replication/mod.rs -->
# sources/object-store/garage/src/table/replication/mod.rs

Purpose: module root for table replication strategies.

Important exports: declares private `parameters`, `fullcopy`, and `sharded` modules, and re-exports `TableFullReplication`, all parameter traits/types, and `TableShardedReplication`.

Control flow: no runtime logic. It centralizes the replication public API for `garage_table`.

State and persistence: none directly.

Dependencies and integration: consumed by `data`, `table`, `sync`, `gc`, and Garage table definitions. The split keeps the trait contract separate from concrete full-copy and sharded implementations.

Risks and test signals: public re-export changes affect downstream imports. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/replication/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/replication/parameters.rs -->
# sources/object-store/garage/src/table/replication/parameters.rs

Purpose: defines the replication strategy contract used by all table operations and synchronization workers.

Important APIs and types: `TableReplication` trait defines associated `WriteSets`, anti-entropy interval, storage nodes, read nodes/quorum, write sets/quorum, partition lookup, and sync partition listing. `SyncPartitions` packages a layout version and list of `SyncPartition`s. `SyncPartition` contains the partition ID, first/last hash bounds, and storage node sets.

Control flow: concrete implementations use the trait to direct reads, writes, Merkle partitioning, offload, anti-entropy, and layout sync progress. `WriteSets` must be both `AsRef` and `AsMut` over `Vec<Vec<Uuid>>` and is usually a layout `WriteLock`, ensuring writes delay layout acknowledgment until complete.

State and persistence: no state; this is a contract. Implementations read layout state and persistent table workers use the results.

Dependencies and integration: bridges `garage_rpc::layout` with table data/sync/GC. All table replication modes must provide partition ranges for `TableSyncer`.

Risks and test signals: trait semantics are stronger than type signatures: write sets must include all active layout versions when needed, and quorums must match the consistency model. Incorrect implementations can silently corrupt replication. No tests here; fullcopy/sharded and table integration validate behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/replication/parameters.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/replication/sharded.rs -->
# sources/object-store/garage/src/table/replication/sharded.rs

Purpose: `TableReplication` implementation for ring-sharded tables, where each partition is stored on the nodes assigned by the current and active layout versions.

Important APIs and types: `TableShardedReplication` holds a `LayoutManager` and `ConsistencyMode`. It implements storage/read nodes, quorums, write sets, partition mapping, and sync partition generation.

Control flow: `storage_nodes` unions nodes for the hash across all active versions, deduplicating for layout transitions. `read_nodes` uses the `read_version` selected by layout sync trackers. `read_quorum` and `write_quorum` delegate to read/current layout version quorum methods. `write_sets` obtains a layout `WriteLock` over one node set per active layout version. `sync_partitions` enumerates current layout partitions, sets hash ranges by adjacent partition starts, and attaches write sets for each partition.

State and persistence: no local persistence. Runtime access to layout state is protected by `LayoutManager`; write operations hold `WriteLock` to delay ack advancement.

Dependencies and integration: used by large Garage metadata/data tables where ownership follows the layout ring. Depends on layout version partition and node assignment functions.

Risks and test signals: during layout transitions, all active write sets must be written to avoid losing data. `partition_of` uses current layout, which is correct for Merkle partitioning but sensitive during transitions. Tests are indirect through layout assignment and table sync/offload.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/replication/sharded.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/schema.rs -->
# sources/object-store/garage/src/table/schema.rs

Purpose: generic schema traits for Garage replicated tables.

Important APIs and types: `PartitionKey` hashes a partition key to `Hash`; implemented for `String` via Blake2 and `FixedBytes32` as identity. `SortKey` exposes sortable bytes; implemented for `String` and `FixedBytes32`. `Entry<P, S>` requires CRDT merge, equality, clone, migration support, and key accessors, with optional `is_tombstone`. `TableSchema` defines table name, key types, entry type, filter type, schema-level `updated` hook, and `matches_filter`.

Control flow: table reads build DB keys from partition hash plus sort key and apply `matches_filter` during scans. Mutations call `Entry::merge` for CRDT updates and invoke `TableSchema::updated` inside the same DB transaction as the table update, allowing secondary local DB changes to remain atomic.

State and persistence: trait implementors define the serialized entries stored by `TableData`. Migration support lets decoded entries be normalized on rewrite.

Dependencies and integration: central contract for all Garage table definitions, `TableData`, queue, sync, GC, and public table API. Uses `garage_db::Transaction` for hooks.

Risks and test signals: schema implementors must make `partition_key`/`sort_key` stable and ensure CRDT/tombstone semantics are correct. A bad `updated` hook can abort mutations or break secondary indexes. No direct tests in this file; each table schema should test its own behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/schema.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/sync.rs -->
# sources/object-store/garage/src/table/sync.rs

Purpose: table anti-entropy and layout-transition synchronization. It compares Merkle trees with peers, pushes missing/different items, offloads partitions the local node no longer owns, and reports table sync progress to the layout manager.

Important APIs and types: `TableSyncer<F, R>` owns `System`, `TableData`, `MerkleUpdater`, an optional full-sync trigger channel, and `SyncRpc` endpoint. `SyncRpc` includes root checksum, node fetch, item transfer, and OK messages. `SyncWorker` tracks layout digest, full-sync scheduling, and partition todo list.

Control flow: workers add full syncs on manual trigger, layout digest changes, or `R::ANTI_ENTROPY_INTERVAL`. `sync_partition` checks whether this node is in any storage set. If yes, it syncs with every node in the partition's write sets and validates quorum through `QuorumSetResultTracker`; if no, it offloads all local items in the hash range to current storage nodes and compare-deletes local copies. Driver-side sync checks remote root Merkle hash, walks differing intermediate nodes, queues leaf values, and sends items in batches. Receiver-side RPCs compare root hashes, return Merkle nodes, and merge received items into `TableData`.

State and persistence: persistent state lives in table store and Merkle trees. Worker state is in-memory. Completing all partitions calls `layout_manager.sync_table_until` with the sync partition layout version.

Dependencies and integration: combines table replication, Merkle updater, RPC helper, system layout notifications, metrics, background workers, and Tokio channels.

Risks and test signals: Merkle trees may lag writes; code logs and tolerates missing/mismatched values. Offload requires all target nodes and can retry changed rows. Layout digest changes reset sync work. No direct unit tests; correctness is integration-level and central to safe layout changes.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/sync.rs -->

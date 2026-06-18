# subset-b-000534 Research

Grouped research for the exact source files assigned to `subset-b-000534`. Each section preserves the source path in the title and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg/buddy_group.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/bee_msg/buddy_group.rs

### Purpose
Defines BeeGFS wire message types for mirror buddy-group discovery, creation/removal, metadata mirroring enablement, target state aggregation, and storage/meta resynchronization statistics. These types are Rust protocol counterparts for BeeGFS C/C++ management, storage, metadata, client, fsck, and ctl interactions.

### Important APIs, Types, and Functions
- `GetMirrorBuddyGroups` / `GetMirrorBuddyGroupsResp` use message IDs `1047` and `1048` to query buddy groups for a `NodeType`; the response carries parallel vectors of group IDs, primary targets, and secondary targets.
- `CombinedTargetState` combines `TargetReachabilityState` from `target.rs` with `TargetConsistencyState` from shared `types.rs`.
- `BuddyGroup` stores primary and secondary `TargetId` values.
- `GetStatesAndBuddyGroups` / `GetStatesAndBuddyGroupsResp` use IDs `1053` and `1054` and return `HashMap<BuddyGroupId, BuddyGroup>` plus `HashMap<TargetId, CombinedTargetState>`.
- `RemoveBuddyGroup`, `SetMetadataMirroring`, `SetMirrorBuddyGroup`, and their responses model mutation operations and return `OpsErr` status.
- `SetMirrorBuddyGroupResp` has manual `Serializable` and `Deserializable` implementations because the BeeGFS wire format includes two trailing padding bytes after `group_id`.
- `SetLastBuddyCommOverride` and `GetStorageResyncStats` / `GetMetaResyncStats` expose mirror resync control and reporting.
- `BuddyResyncJobState` is converted with `impl_enum_bee_msg_traits!` using BeeGFS numeric values `0..5`.

### Control Flow and State
The file is declarative protocol glue: runtime control flow is in the serializer, deserializer, and connection dispatcher. Message handlers elsewhere deserialize these structs based on `Msg::ID`, execute cluster state changes or queries, and serialize the response. State represented here includes buddy group mapping, target state, metadata mirroring enablement, last buddy-communication override, and resync job counters, but the file itself persists none of it.

### Dependencies and Integration Points
Depends on `super::*` for `Msg`, `MsgId`, `OpsErr`, BeeSerde helpers, and shared BeeGFS type aliases. It imports `TargetReachabilityState` from `target.rs` and uses `TargetConsistencyState`, `NodeType`, `NodeId`, `TargetId`, and `BuddyGroupId` from `types.rs`. Integration is through `bee_msg::serialize` / `deserialize_body` and the network layers under `conn/`.

### Risks and Edge Cases
Parallel-vector response formats require consumers to verify equal lengths before zipping. The manual padding in `SetMirrorBuddyGroupResp` must remain exact for compatibility. Several integer enum fields are serialized as different raw widths (`u32`, `i32`), so changing helper annotations can break wire compatibility. Mutation messages carry `u8` boolean-ish fields (`check_only`, `force`, `allow_update`, `abort_resync`) without local validation.

### Test Signals
No local tests in this file. Coverage is indirect through BeeSerde tests, message round-trip tests elsewhere if present, and integration tests against BeeGFS peers. Useful additional tests would round-trip `SetMirrorBuddyGroupResp` padding and assert all map/sequence response formats decode correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg/buddy_group.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg/misc.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/bee_msg/misc.rs

### Purpose
Defines miscellaneous BeeGFS control messages: generic error responses, UDP acknowledgements, stream authentication, peer identity, channel-direct hints, and capacity-pool refresh/query messages.

### Important APIs, Types, and Functions
- `GenericResponseCode` aliases `i32`; constants `TRY_AGAIN`, `INDIRECT_COMM_ERR`, and `NEW_SEQ_NO_BASE` define known generic response codes.
- `GenericResponse` (`MsgId 4009`) carries a response code and C-string description.
- `Ack` (`4003`) models UDP acknowledgement IDs.
- `AuthenticateChannel` (`4007`) carries `AuthSecret` and is used by `conn::incoming` as the only allowed pre-authentication TCP message when authentication is required.
- `PeerInfo` (`4011`) reports a `NodeType` and `NodeId`.
- `SetChannelDirect` (`4001`) carries a direct-worker hint but is documented as ignored in Rust.
- `RefreshCapacityPools` (`1035`) is a UDP invalidation/request-refresh signal.
- `GetNodeCapacityPools` (`1021`) and `GetNodeCapacityPoolsResp` (`1022`) query node capacity pools.
- `GetNodeCapacityPoolsResp` implements custom serialization for nested map/sequence data: `HashMap<PoolId, Vec<Vec<u16>>>`.
- `CapacityPoolQueryType` maps `Meta`, `Storage`, `MetaMirrored`, and `StorageMirrored` to BeeGFS integers `0..3`.

### Control Flow and State
The file itself has no mutable state. `AuthenticateChannel` affects connection state because a handler may call `Request::authenticate_connection()` after validating it, changing a `Stream`'s authenticated flag. Refresh messages trigger other nodes to request fresh state rather than embedding the state directly.

### Dependencies and Integration Points
Uses `AuthSecret`, `NodeType`, `NodeId`, and `PoolId` from shared types, and BeeSerde helpers for C strings and enum integer conversion. Integrates with TCP authentication checks in `conn/incoming.rs`, request handling in `conn/msg_dispatch.rs`, and capacity-pool state in management/meta handlers.

### Risks and Edge Cases
`GetNodeCapacityPoolsResp` uses raw `u16` inner IDs instead of typed IDs, so target/group interpretation depends on `CapacityPoolQueryType`. Nested collection serialization is manual because the derive macro does not support nested collections; drift from BeeGFS C++ layouts would be easy to miss. `Ack` can be ignored by current nodes, so callers must not rely on it as a strong delivery guarantee.

### Test Signals
No direct tests. BeeSerde nested sequence/map tests partially exercise the same serializer primitives. Targeted tests should round-trip `GetNodeCapacityPoolsResp` with multiple pools and empty inner vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg/misc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg/node.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/bee_msg/node.rs

### Purpose
Defines BeeGFS node discovery, heartbeat, registration, removal, and NIC wire representations. It is the protocol bridge for management, client, metadata, storage, fsck, ctl, and monitor node identity flows.

### Important APIs, Types, and Functions
- `GetNodes` (`1017`) and `GetNodesResp` (`1018`) fetch nodes by `NodeType`, with metadata-root ownership fields `root_num_id` and `is_root_mirrored`.
- `Node` is a BeeSerde struct containing alias, NIC list, numeric ID, port, unused TCP port, and node type.
- `Nic` manually serializes IPv4/IPv6 addresses, truncates interface names to 15 bytes plus a null/ignored byte, serializes `NicType`, and includes two padding bytes.
- `HeartbeatRequest` (`1019`) asks a node to send heartbeat data.
- `Heartbeat` (`1020`) and `RegisterNode` (`1039`) publish node details, ports, NICs, machine UUID, and root metadata ownership.
- `RegisterNodeResp` (`1040`) returns assigned numeric ID, gRPC port, and filesystem UUID.
- `RemoveNode` / `RemoveNodeResp` (`1013` / `1014`) remove a node and return `OpsErr`.

### Control Flow and State
The file defines state snapshots used in registration and liveness updates. The custom `Nic` deserializer validates protocol byte `4` or `6`, reads little-endian address integers, strips null bytes from names, and decodes `NicType`. Actual state insertion, heartbeat handling, and removal occur in node stores or message handlers outside this file.

### Dependencies and Integration Points
Depends on `anyhow::bail`, `std::net::{IpAddr, Ipv4Addr}`, BeeSerde primitives, and shared types. It integrates with local NIC discovery in `nic.rs`, connection address management in `conn/outgoing.rs` via `Pool::replace_node_addrs`, and BeeGFS management registration workflows.

### Risks and Edge Cases
NIC name truncation can collapse distinct interface names beyond 15 bytes. The 16th name byte is ignored on deserialization to match C/C++ behavior; changing that would create compatibility mismatches. IPv6 serialization uses little-endian conversion through `u128`, so tests should protect byte order. `Heartbeat` and `RegisterNode` have similar but not identical field order, which is a wire-compatibility trap.

### Test Signals
No tests in this file. Good test signals would include round-tripping IPv4/IPv6 `Nic`, verifying name truncation/null stripping, and rejecting invalid protocol bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg/node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg/publish_capacities.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/bee_msg/publish_capacities.rs

### Purpose
Defines `PublishCapacities`, a BeeGFS message asking metadata or storage nodes to publish capacity information, normally by sending target-info updates. The comment notes that nodes already publish periodically, so this is only for on-demand freshness.

### Important APIs, Types, and Functions
- `PublishCapacities` contains an `ack_id` encoded as `CStr<0>`.
- `impl Msg for PublishCapacities` assigns message ID `1059`.

### Control Flow and State
The file is protocol-only and has no state. When sent, the receiver should respond by publishing capacity information through the existing target-info path; the message itself only carries an acknowledgement identifier.

### Dependencies and Integration Points
Uses `super::*` for BeeSerde, C-string helper, and `Msg`. It should integrate with UDP acknowledgement and target-info update flows near `SetStorageTargetInfo` in `target.rs`.

### Risks and Edge Cases
The implementation uses `const ID: MsgID = 1059;` while the rest of the crate defines `MsgId` in `bee_msg.rs`. Unless a `MsgID` alias exists elsewhere, this is a compile-time typo. The module is also not listed in `bee_msg.rs`'s visible `pub mod` set in the inspected root, so it may currently be dead or excluded code.

### Test Signals
No tests. A simple compile check or targeted message round-trip would catch the `MsgID`/`MsgId` issue and module export status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg/publish_capacities.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg/quota.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/bee_msg/quota.rs

### Purpose
Defines quota query, response, exceeded-quota publication, and exceeded-quota request messages for BeeGFS user/group quota handling across ctl, management, metadata, and storage roles.

### Important APIs, Types, and Functions
- `GetQuotaInfo` (`2097`) models quota query type, quota ID type, range/list/single fields, transfer method, target ID, and pool ID.
- `GetQuotaInfo::with_group_ids` and `with_user_ids` build list-mode queries from `HashSet<QuotaId>`, target, and pool.
- `GetQuotaInfo` implements custom serialization/deserialization because body layout depends on `query_type`.
- `GetQuotaInfoResp` (`2098`) returns `QuotaInodeSupport` and a sequence of `QuotaEntry`.
- `SetExceededQuota` (`2077`) and `SetExceededQuotaResp` (`2078`) publish exceeded quota IDs.
- `RequestExceededQuota` (`2079`) and `RequestExceededQuotaResp` (`2080`) query and return exceeded quota state.
- Enums `GetQuotaInfoTransferMethod`, `QuotaInodeSupport`, and `QuotaQueryType` map to BeeGFS numeric constants.
- `QuotaEntry` stores space, inode count, quota ID, ID type, and a `valid` flag.

### Control Flow and State
`GetQuotaInfo::serialize` emits different fields for `Range`, `List`, and `Single`, then always serializes transfer method, target ID, and pool ID. `deserialize` mirrors that layout and fills irrelevant fields with zero or empty vectors. The file represents quota state in transit but persists none locally.

### Dependencies and Integration Points
Uses `HashSet` through `super::*`, `QuotaIdType` and `QuotaType` from shared types, BeeSerde collection helpers, and `OpsErr` for responses. Integrates with management quota commands and storage/meta quota scanners.

### Risks and Edge Cases
`HashSet::drain().collect()` produces nondeterministic ID ordering; protocol consumers should treat lists as sets. `QuotaQueryType::None` and `All` serialize no ID selector fields, so handlers must interpret omitted data correctly. The `valid` field is a raw `u8`, not a Rust `bool`. Conditional serialization makes round-trip tests more important than for derive-only messages.

### Test Signals
No local tests. Needed coverage includes all `QuotaQueryType` variants, transfer-method conversions, and response sequences with both user and group quota entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg/quota.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg/storage_pool.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/bee_msg/storage_pool.rs

### Purpose
Defines storage-pool discovery and refresh messages plus nested capacity-pool structures for targets and buddy groups.

### Important APIs, Types, and Functions
- `GetStoragePools` (`1066`) and `GetStoragePoolsResp` (`1067`) query all storage pools.
- `StoragePool` contains pool ID, alias, target IDs, buddy group IDs, target capacity pools, and buddy-group capacity pools.
- `TargetCapacityPools` manually serializes nested `Vec<Vec<TargetId>>`, grouped target pools `Vec<HashMap<NodeId, Vec<TargetId>>>`, and a target-to-node map.
- `BuddyGroupCapacityPools` manually serializes nested `Vec<Vec<BuddyGroupId>>`.
- `RefreshStoragePools` (`1070`) is a UDP-style invalidation/request-refresh message carrying an `ack_id`.

### Control Flow and State
The file provides wire representations of management's storage-pool state. Deserialization reconstructs nested vectors/maps, while state ownership and mutation live in management/storage/meta handlers. Refresh messages notify nodes to fetch current pool state rather than embedding it.

### Dependencies and Integration Points
Uses typed BeeGFS IDs from `types.rs`, `HashMap` from `super::*`, and BeeSerde sequence/map primitives. It integrates with capacity-pool query messages in `misc.rs`, target mapping in `target.rs`, and buddy-group mapping in `buddy_group.rs`.

### Risks and Edge Cases
Nested collection serialization is manual and shape-sensitive. The comment on `BuddyGroupCapacityPools` notes BeeGFS deserializes these as target numeric IDs even though they are buddy group IDs; changing underlying ID widths must be coordinated carefully. Empty pool vectors and missing target-map entries need handler-level validation.

### Test Signals
No local tests. Round-trip tests should cover multiple capacity pools, grouped target maps, empty groups, and buddy-group IDs at type width boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg/storage_pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg/target.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/bee_msg/target.rs

### Purpose
Defines target mapping, target state, target registration, consistency-state updates, target usage reporting, and target-state refresh messages.

### Important APIs, Types, and Functions
- `GetTargetMappings` (`1025`) / `GetTargetMappingsResp` (`1026`) fetch target-to-node mappings. The response has custom serialization writing node IDs as raw `u32`.
- `GetTargetStates` (`1049`) / `GetTargetStatesResp` (`1050`) fetch parallel lists of target IDs, reachability states, and consistency states.
- `TargetReachabilityState` maps `Online`, `ProbablyOffline`, and `Offline` to `0`, `1`, and `2` and serializes as `u8`.
- `RegisterTarget` (`1041`) / `RegisterTargetResp` (`1042`) register storage targets.
- `MapTargets` (`1023`) / `MapTargetsResp` (`1024`) map target IDs to pools and owning node.
- `ChangeTargetConsistencyStates` (`1057`) and `SetTargetConsistencyStates` (`1055`) update target consistency, with corresponding `OpsErr` responses.
- `SetStorageTargetInfo` (`2099`) / response (`2100`) publish usage information for storage or metadata targets.
- `TargetInfo` includes path, total/free space, total/free inodes, and consistency state.
- `RefreshTargetStates` (`1051`) is a UDP refresh trigger.

### Control Flow and State
All state is represented in message payloads. Parallel-vector responses require consumers to combine positions into logical records. Consistency-state changes include old/new state lists for compare-and-change semantics, while set-state messages replace with provided states and may optionally set reachability online via `set_online`.

### Dependencies and Integration Points
Uses BeeSerde helpers, `OpsErr`, `NodeType`, ID aliases, `PoolId`, and `TargetConsistencyState`. It integrates with buddy-group state in `buddy_group.rs`, storage-pool mapping in `storage_pool.rs`, and management/storage message handlers.

### Risks and Edge Cases
Parallel vectors can desynchronize by length. `GetTargetMappingsResp` currently implements serialization but not an explicit custom deserializer in this file; if `BeeSerde` derive is not present, inbound decoding of this response may not compile or may be intentionally unused. `TargetInfo.path` uses aligned C-string encoding (`CStr<4>`), which must match C/C++ message definitions. Raw `u8` flags and unchecked state transition lists need handler validation.

### Test Signals
No local tests. Useful tests include target-state response vector length validation in handlers, enum conversion rejection for invalid values, and round-trip of `TargetInfo` path alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg/target.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_serde.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/bee_serde.rs

### Purpose
Implements the core BeeGFS serialization/deserialization framework used for network messages and some on-disk data. It provides primitive encoding, C-string handling, sequence/map layouts, derive-macro helper traits, and enum conversion support.

### Important APIs, Types, and Functions
- `Serializable` and `Deserializable` are the central traits implemented by protocol types.
- `Serializer` writes little-endian primitives into a fixed mutable slice and tracks `write_pos`; it also carries a `bee_msg::Header` for message-specific metadata.
- `Deserializer` reads from a source slice and carries a borrowed or owned `Header` for conditional deserialization.
- `Serializer::bytes`, `cstr`, `seq`, `map`, `zeroes`, and `bytes_written` implement BeeGFS wire primitives.
- `Deserializer::bytes`, `cstr`, `seq`, `map`, `skip`, `finish`, and `take` mirror the read side with bounds checks.
- `BeeSerdeConversion<S>` converts enums and other values to/from raw BeeGFS integer encodings.
- `BeeSerdeHelper<In>` plus helpers `Int`, `Seq`, `Map`, and `CStr` drive the `#[derive(BeeSerde)]` field annotations.
- Primitive integer types implement both serialization traits.

### Control Flow and State
Serialization writes fields sequentially into a caller-owned buffer. Sequence and map serialization reserve count/size placeholders, serialize elements, then patch the placeholders in-place. Deserialization advances the source slice by splitting off consumed bytes; `finish` reports trailing bytes. No persistent state exists beyond each serializer/deserializer instance.

### Dependencies and Integration Points
Coupled to `bee_msg::Header` because some BeeGFS messages depend on header metadata. Uses `anyhow` for error propagation, `Cow` for header ownership, and `HashMap` for map deserialization. All `bee_msg` modules, `conn` send/receive paths, and derive macros depend on this file.

### Risks and Edge Cases
`seq` and `map` trust decoded length values enough to `try_reserve`, so malformed inputs can request large allocations before element reads fail. `cstr` writes length as `u32` using `v.len() as u32`; extremely large inputs would truncate before buffer writes fail. Included sequence total size is skipped but not validated on decode. Arithmetic like `self.write_pos + v.len()` in `bytes` can overflow for pathological values, although normal fixed buffers make this unlikely. Header coupling keeps the generic serializer less reusable.

### Test Signals
Includes unit tests for primitive round-trips, byte blocks, C-string alignment, nested collections, and buffer-length errors. Additional hardening tests should cover malicious sequence lengths, invalid C-string terminators, and mismatched included total sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_serde.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/conn.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/conn.rs

### Purpose
Declares the connection module tree and shared TCP/UDP buffer-size constants for BeeGFS network communication.

### Important APIs, Types, and Functions
- Public modules: `incoming`, `msg_dispatch`, and `outgoing`.
- Private modules: `async_queue`, `store`, and `stream`.
- `TCP_BUF_LEN` is `4 * 1024 * 1024`, matching BeeGFS C++ worker buffer sizes.
- `UDP_BUF_LEN` is `65536`, matching BeeGFS datagram buffer sizes and kept below the TCP size.

### Control Flow and State
No runtime control flow beyond module organization. Constants shape allocation size in incoming/outgoing TCP buffers, UDP datagram buffers, and pooled message buffers.

### Dependencies and Integration Points
The submodules use these constants for socket reads/writes, pooled buffers, and datagram handling. The values must stay aligned with the C/C++ BeeGFS codebase for protocol compatibility and expected maximum message size.

### Risks and Edge Cases
If BeeGFS upstream changes buffer sizes, this crate can reject or truncate valid traffic or allocate more than needed. Fixed 4 MiB buffers per stream/request can create memory pressure under high concurrency.

### Test Signals
No local tests. Integration tests with large messages near TCP/UDP boundaries would exercise these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/conn.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/conn/async_queue.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/conn/async_queue.rs

### Purpose
Provides a small async-safe FIFO queue built from `Mutex<VecDeque<T>>` and `tokio::sync::Notify`, used by the connection store to wait for reusable streams.

### Important APIs, Types, and Functions
- `AsyncQueue<T>` holds `queue: Mutex<VecDeque<T>>` and `notification: Notify`.
- `new()` constructs an empty queue.
- `push(item)` appends to the back and notifies one waiter.
- `try_pop()` pops the front immediately; if more items remain, it notifies one waiter to preserve availability.
- `pop().await` waits for notification and loops until `try_pop()` returns an item.

### Control Flow and State
The queue state is in-memory only. `pop` can awaken spuriously or lose a race to `try_pop`, so it loops. After a successful pop, `try_pop` re-notifies when the queue is still non-empty, avoiding stranded items when multiple waiters exist.

### Dependencies and Integration Points
Uses standard `Mutex` and `VecDeque`, plus Tokio `Notify`. It is used by `conn/store.rs` for per-node stored-stream queues.

### Risks and Edge Cases
`Mutex::lock().unwrap()` panics on poison. Notifications are not tied to exact items, so consumers must tolerate wakeups where another consumer won the item. There is no close/shutdown signal; a `pop` waiter can wait forever if no producer arrives and caller does not wrap it in timeout or select.

### Test Signals
Includes unit tests for `push`/`try_pop`, async `push`/`pop`, and a 16-worker concurrent drain. Tests validate queue ordering and notify behavior under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/conn/async_queue.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/conn/incoming.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/conn/incoming.rs

### Purpose
Implements incoming BeeGFS TCP listener and UDP receiver loops. It reads message headers/bodies into fixed buffers and forwards requests to a generic dispatcher.

### Important APIs, Types, and Functions
- `listen_tcp(listen_addr, dispatch, stream_authentication_required, run_state)` binds a `TcpListener`, spawns an accept loop, and spawns `stream_loop` per accepted connection.
- `stream_loop` owns a `Stream`, allocates one TCP buffer, waits for readability or shutdown, and calls `read_stream`.
- `read_stream` reads a BeeGFS header, validates authentication state if required, reads the body, and dispatches a `StreamRequest`.
- `recv_udp(sock, dispatch, run_state)` spawns a datagram receive loop.
- `recv_datagram` allocates a UDP buffer, receives a packet, and spawns per-datagram dispatch through `SocketRequest`.

### Control Flow and State
TCP handling is one task per connection, with request-response semantics on a single stream. UDP handling allocates a new buffer per received datagram and handles dispatch in a separate task so the receive loop can continue. Shutdown is coordinated through `RunStateHandle`. Authentication state is stored on the `Stream`.

### Dependencies and Integration Points
Depends on `conn::stream::Stream`, `conn::msg_dispatch`, `bee_msg::{Header, deserialize_header}`, `AuthenticateChannel`, Tokio networking, and `run_state`. The dispatcher owns message deserialization, handler selection, and response writing.

### Risks and Edge Cases
After `deserialize_header`, `read_stream` indexes `buf[Header::LEN..header.msg_len()]` without checking `header.msg_len() <= TCP_BUF_LEN`; a malformed header can panic before `read_exact` returns an error. Similarly, UDP dispatch deserializes only the header and passes the full 64 KiB buffer to the dispatcher, so body length validation relies on later deserialization. Incoming TCP has no connection limit. Per-datagram allocation can be costly under high UDP load.

### Test Signals
No local tests. Important integration tests should cover invalid headers, overlarge `msg_len`, authentication-required behavior, graceful shutdown, and UDP datagram parsing with short packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/conn/incoming.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/conn/msg_dispatch.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/conn/msg_dispatch.rs

### Purpose
Defines transport-agnostic request dispatch traits and concrete request wrappers for TCP streams and UDP sockets.

### Important APIs, Types, and Functions
- `DispatchRequest` is implemented by dispatchers that can handle any `Request` asynchronously.
- `Request` abstracts response writing, connection authentication, peer address access, header access, and body deserialization.
- `StreamRequest<'a>` wraps a mutable `Stream`, shared buffer, and header reference.
- `SocketRequest<'a>` wraps an `Arc<UdpSocket>`, peer address, buffer, and header reference.
- `Request::respond` serializes a response into the same buffer and writes it to the stream or UDP peer.
- `deserialize_msg<M>` calls `bee_msg::deserialize_body`.
- `test::TestRequest` is a lightweight request double.

### Control Flow and State
Dispatchers receive a request wrapper and decide how to deserialize and handle it. `StreamRequest::authenticate_connection` mutates the underlying stream's `authenticated` flag. UDP authentication is a no-op.

### Dependencies and Integration Points
Depends on `bee_msg::{serialize, deserialize_body, Header, Msg}`, `bee_serde`, `conn::stream::Stream`, Tokio `UdpSocket`, and `SocketAddr`. Used by both incoming TCP and UDP paths.

### Risks and Edge Cases
Responses reuse the request buffer; large responses can fail serialization if they exceed buffer size. UDP responses may exceed practical MTU even if under `UDP_BUF_LEN`. Generic associated async functions are convenient but can make trait-object use difficult. Authentication is transport-specific and silently ignored for UDP.

### Test Signals
Contains a test helper but no direct assertions. Dispatcher-level tests can use `TestRequest` to verify authentication and handler selection without sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/conn/msg_dispatch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/conn/outgoing.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/conn/outgoing.rs

### Purpose
Implements outgoing BeeGFS communication through a reusable connection/buffer pool. It supports request-response TCP messages, fire-and-forget TCP sends, UDP datagram broadcasts, optional stream authentication, address management, and IPv6 filtering.

### Important APIs, Types, and Functions
- `Pool` owns a `Store<Uid>`, UDP socket, optional `AuthSecret`, and `use_ipv6` flag.
- `Pool::new` configures connection limit, auth, and IPv6 usage.
- `request<M, R>` serializes a message, communicates over a stream expecting a response, deserializes the response, and returns `R`.
- `send<M>` serializes and writes a stream message without reading a response.
- `comm_stream` tries reusable streams, then opens a new stream with a permit, then waits up to two seconds for an existing stream.
- `write_and_read_stream` writes the serialized message and optionally reads response header/body.
- `broadcast_datagram` serializes once and sends to all known addresses for each peer.
- `replace_node_addrs` updates the address store for a node UID.

### Control Flow and State
Buffers and streams are pooled in `Store`. New streams are authenticated by sending `AuthenticateChannel` before the real message if `auth_secret` is configured. Failed reused streams are discarded by dropping them. Successful streams are pushed back into the pool.

### Dependencies and Integration Points
Depends on `bee_msg` serialization/deserialization, `conn::store`, `conn::stream`, `AuthSecret`, `Uid`, Tokio UDP, and `timeout`. It is the main client-side transport API for higher-level BeeGFS components.

### Risks and Edge Cases
On early errors in `request`/`send`, buffers may not be returned to the buffer pool because `push_buf` is after fallible awaits. This is not memory unsafe but can reduce pooling efficiency. Header `msg_len` is used to slice into fixed buffers without explicit upper-bound checks, so malformed responses can panic. Authentication writes do not read an auth response, assuming one is unnecessary. If all addresses are IPv6 and `use_ipv6` is false, connection attempts are skipped and the final error still lists all known addresses. UDP broadcast treats send success as socket-level only, not delivery.

### Test Signals
No local tests. Needed coverage includes buffer return on error, connection-limit behavior, authentication prelude, overlarge response headers, IPv6 filtering, and datagram broadcast partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/conn/outgoing.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/conn/store.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/conn/store.rs

### Purpose
Provides in-memory storage for reusable TCP streams, fixed-size message buffers, peer address lists, and per-peer connection permits.

### Important APIs, Types, and Functions
- `Store<T>` holds per-key `(AsyncQueue<StoredStream<T>>, Semaphore)` pairs, a buffer deque, address map, and connection limit.
- `new(connection_limit)` constructs the store.
- `try_pop_stream`, `try_acquire_permit`, `pop_stream`, and `push_stream` implement stream reuse and connection limiting.
- `pop_buf`, `pop_buf_or_create`, and `push_buf` manage reusable `Vec<u8>` buffers sized to `TCP_BUF_LEN`.
- `get_node_addrs` and `replace_node_addrs` manage peer address snapshots.
- `StoredStreamPermit<T>` owns a Tokio semaphore permit for one open stream.
- `StoredStream<T>` wraps `Stream` plus its permit and implements `AsRef` / `AsMut`.

### Control Flow and State
All state is in memory and protected by `Mutex`/`RwLock`. A permit is acquired before opening a new connection and held by the `StoredStream`; dropping the stream releases the permit. Existing streams are queued by peer key. Buffers are pooled globally.

### Dependencies and Integration Points
Uses `AsyncQueue`, `Stream`, Tokio `Semaphore`, and `SocketAddr`. It is used by `conn/outgoing.rs` to implement `Pool`.

### Risks and Edge Cases
`connection_limit == 0` means no new connection permits can be acquired and callers may later wait for a stream that can never exist. Mutex/RwLock poison causes panics through `unwrap`. The buffer pool is unbounded and can retain many 4 MiB buffers after spikes. Address replacement is all-or-nothing; there is no merge or staleness tracking.

### Test Signals
No direct tests. Behavior is partly exercised through `AsyncQueue` tests. Store tests should cover permit release on drop, zero-limit behavior, address replacement, and buffer reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/conn/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/conn/stream.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/conn/stream.rs

### Purpose
Wraps Tokio TCP streams behind a BeeGFS-oriented `Stream` type with authentication state, peer address access, readability waits, and timeout-bound reads/writes.

### Important APIs, Types, and Functions
- `TIMEOUT` is two seconds for connect/read/write operations.
- `Stream` stores `InnerStream` and public `authenticated` flag.
- `InnerStream` currently supports only `Tcp(TcpStream)`.
- `From<TcpStream>` creates an unauthenticated `Stream`.
- `connect_tcp(addr)` connects with timeout.
- `readable()` waits until the socket is readable and uses a zero-length `try_read` probe to handle readiness races.
- `read_exact` and `write_all` wrap Tokio I/O in two-second timeouts and warn they are not cancel-safe.
- `addr()` returns the peer address.

### Control Flow and State
The wrapper is a thin stateful transport object. Authentication is an external flag set by request handling. Read/write operations time out but may leave stream contents partially consumed or written, so callers should discard streams after such errors.

### Dependencies and Integration Points
Uses Tokio `TcpStream`, `AsyncReadExt`, `AsyncWriteExt`, and `timeout`; integrated with incoming TCP, outgoing connection pooling, and dispatcher request wrappers.

### Risks and Edge Cases
`addr()` unwraps `peer_addr` and can panic if the OS call fails. `read_exact`/`write_all` are explicitly not cancel-safe. The two-second timeout is fixed and may be too aggressive for slow networks or large 4 MiB messages. The zero-byte readability probe depends on Tokio/socket behavior and may not detect all closure cases uniformly.

### Test Signals
No direct tests. Socket integration tests should cover timeouts, closed-peer detection, address retrieval, and non-reuse after partial I/O errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/conn/stream.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/grpc.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/grpc.rs

### Purpose
Provides shared gRPC helper macros and utilities for BeeGFS Rust services using tonic: handler forwarding, response streams, error-to-status mapping, and required-field validation.

### Important APIs, Types, and Functions
- `impl_grpc_handler!` generates tonic service methods for unary and server-streaming RPCs by forwarding to a handler module/function with `self.app`.
- `StreamSender<Msg>` wraps an `mpsc::Sender<Result<Msg, Status>>` and exposes async `send`.
- `RespStream<T>` aliases a pinned boxed Tokio stream of tonic results.
- `resp_stream(buf_size, source_fn)` creates a channel-backed response stream and maps source errors to gRPC statuses.
- `AnyhowContextStatus` stores a tonic `Code` plus optional source error.
- `AnyhowErrorStatusExt::status_code` wraps errors with a desired gRPC status code.
- `process_grpc_handler_error` walks an anyhow error chain, extracts the last status-code wrapper, logs, and returns `tonic::Status`.
- `required_field` converts `Option<T>` protobuf fields into `anyhow::Result<T>`.

### Control Flow and State
Generated handlers call the real handler asynchronously, convert `Ok` values to tonic responses, and convert errors through `process_grpc_handler_error`. `resp_stream` spawns a producer task; source errors are sent as a final stream error unless the receiver closed early.

### Dependencies and Integration Points
Uses tonic `Status`/`Code`, Tokio `mpsc`, `tokio_stream`, and anyhow. It is gated by the `grpc` feature in `lib.rs`, and depends on consuming service structs having an `app` field.

### Risks and Edge Cases
The macro is not fully generic despite being shared; it assumes `self.app` and handler module naming. Error responses include the full stringified error chain, which may leak internal detail. `process_grpc_handler_error` defaults to `Code::Unknown` despite comments mentioning generic internal status. Stream producer tasks can outlive request context until channel closure or source completion.

### Test Signals
No local tests. Tests should assert status-code extraction, required-field errors, receiver-cancel behavior, and generated handler behavior in a minimal tonic service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/grpc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/impl_macros.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/impl_macros.rs

### Purpose
Defines internal convenience macros for enum conversions, user-facing enum strings, and optional protobuf conversions.

### Important APIs, Types, and Functions
- `impl_enum_bee_msg_traits!` implements `BeeSerdeConversion` for a target enum across integer types `u8`, `u16`, `i16`, `u32`, `i32`, `u64`, `i64`, `usize`, and `isize`.
- `impl_enum_user_str!` adds `user_str()` and `Display` for enum variants.
- `impl_enum_protobuf_traits!` is compiled with feature `grpc` and implements `TryFrom<proto>` plus `From<domain>` and `into_proto_i32`.

### Control Flow and State
Macros expand at compile time. Runtime behavior is simple matching: valid numeric/protobuf values map to enum variants and unknown values return anyhow errors.

### Dependencies and Integration Points
Used heavily by `types.rs`, target/buddy/quota message enums, and gRPC conversion code. Requires `crate::bee_serde::BeeSerdeConversion`, `anyhow`, and optional generated protobuf modules in call sites.

### Risks and Edge Cases
The macro implements many integer conversions, so accidental use of the wrong raw width may compile even when wire definitions require a narrower type. `impl_enum_protobuf_traits!` treats the protobuf unspecified variant as an error on inbound conversion, which is generally correct but must match API semantics. Duplicate numeric values would compile into unreachable or conflicting match arms depending on expansion.

### Test Signals
No direct tests. Enum round-trip tests in message/type modules would exercise expansions. Compile tests are useful for protobuf feature builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/impl_macros.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/journald_logger.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/journald_logger.rs

### Purpose
Implements a `log` crate backend that sends structured log records directly to the systemd journal socket.

### Important APIs, Types, and Functions
- `JournaldLogger` stores a connected Unix datagram socket and a `LevelFilter`.
- `init(level_filter)` connects to `/run/systemd/journal/socket`, installs the boxed logger, and sets the max log level.
- `impl Log for JournaldLogger` filters records, formats journald fields, encodes `MESSAGE` as a binary field with little-endian length, and sends via Unix datagram.
- `level_to_priority` maps Rust log levels to syslog priorities: error `3`, warn `4`, info `5`, debug `6`, trace `7`.

### Control Flow and State
After initialization, logging is synchronous per record: build a buffer and send it through the socket. State is only the socket and max level.

### Dependencies and Integration Points
Uses `log`, `std::os::unix::net::UnixDatagram`, and systemd journald's native socket protocol. Exposed by `lib.rs` for BeeGFS Rust daemons.

### Risks and Edge Cases
Hard-coded `SYSLOG_IDENTIFIER=beegfs-mgmtd` makes the logger less reusable for non-management binaries. Send failures are printed to stderr, which may be unavailable or noisy in daemon contexts. `init` fails on non-systemd systems or if journald socket is absent. Message size is not capped locally.

### Test Signals
No tests. Unit tests could cover priority mapping; integration tests would need a fake Unix datagram receiver or journald socket abstraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/journald_logger.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/lib.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/lib.rs

### Purpose
Defines the public module surface for the shared BeeGFS Rust crate.

### Important APIs, Types, and Functions
- Imports `impl_macros` with `#[macro_use]`.
- Exposes `bee_msg`, `bee_serde`, `conn`, `journald_logger`, `nic`, `parser`, `run_state`, and `types`.
- Exposes `grpc` only when the `grpc` feature is enabled.

### Control Flow and State
No runtime control flow or state. This file controls compilation visibility and feature-gated API availability.

### Dependencies and Integration Points
All downstream Rust crates use this root to access protocol messages, serialization, connection handling, logging, NIC discovery, parsers, run-state coordination, and shared type definitions.

### Risks and Edge Cases
Modules not listed here are inaccessible from downstream crates. In the inspected tree, `bee_msg/publish_capacities.rs` exists but is not exported by `bee_msg.rs`, so it may be orphaned even though `lib.rs` exposes `bee_msg` as a whole. Feature-gated `grpc` consumers must compile with matching protobuf dependencies.

### Test Signals
No tests. Compile checks with default and `grpc` features validate module exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/nic.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/nic.rs

### Purpose
Parses NIC filters, discovers local network interfaces, prioritizes matching addresses, and checks whether IPv6 dual-stack sockets are usable on the host.

### Important APIs, Types, and Functions
- `Protocol` parses `"4"` and `"6"` into IPv4/IPv6 selectors.
- `NicFilter` contains optional name, address, protocol, NIC type, and invert flag.
- `NicFilter::parse_optional` and `parse` parse filters in the form `[!] [name|*] [addr|*] [4|6|*] [tcp|rdma|*]`.
- `serde::Deserialize for NicFilter` parses string config entries through `NicFilterVisitor`.
- `nic_priority` matches a discovered `(name, ip)` against filters, rejects link-local addresses, and handles inverted entries.
- `Nic` stores address, `NicType`, interface name, priority, interface index, and address index; `Ord` sorts by filter priority, non-loopback, IPv4 preference, RDMA, interface index, and address index.
- `query_nics(filter, use_ipv6)` uses `pnet_datalink::interfaces()` and returns sorted matching TCP NICs.
- `check_ipv6(port, use_ipv6)` uses libc socket/connect/getsockopt to require IPv6 availability and dual-stack behavior.

### Control Flow and State
Filter parsing is stateless. NIC discovery walks OS interfaces, filters each address, and sorts the result. IPv6 checking creates a temporary nonblocking AF_INET6 socket, probes localhost connect behavior for `EADDRNOTAVAIL`, and checks `IPV6_V6ONLY`.

### Dependencies and Integration Points
Depends on shared `NicType`, `serde`, `regex`, `pnet_datalink`, `libc`, and standard networking/FD APIs. Integrates with node registration and connection address selection by producing local NIC lists and deciding IPv4/IPv6 mode.

### Risks and Edge Cases
RDMA detection is not implemented; RDMA filter entries currently do not match discovered interfaces in `nic_priority`. `check_ipv6` ignores errors from `fcntl` and treats many connect failures as acceptable unless specifically `EADDRNOTAVAIL`. `NicFilter::parse_optional` accepts extra fields after the expected five because it does not reject leftovers. Sorting currently puts RDMA before TCP based on `NicType` ordering, but discovered NICs are always TCP.

### Test Signals
Includes tests for filter parsing, matching/inversion behavior, and NIC sorting. Host-dependent `query_nics` and `check_ipv6` are not covered by deterministic tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/nic.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/parser.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/parser.rs

### Purpose
Top-level module for custom parsers used by configuration and command-line deserialization.

### Important APIs, Types, and Functions
- Public submodules: `duration`, `integer_range`, and `integer_unit`.

### Control Flow and State
No runtime logic in this file beyond module exposure.

### Dependencies and Integration Points
Downstream config structs can import `parser::duration::deserialize`, `parser::integer_range::deserialize`, and `parser::integer_unit::deserialize` for serde fields.

### Risks and Edge Cases
Only exposes submodules; parser correctness and risks live in the child files.

### Test Signals
No tests in this module; child modules contain parser-specific tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/parser.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/parser/duration.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/parser/duration.rs

### Purpose
Parses positive duration values from strings or integer serde inputs for config/CLI use.

### Important APIs, Types, and Functions
- Regex accepts digits plus optional unit among `ns`, `us`, `ms`, `s`, `m`, `h`, and `d`, with optional spaces.
- `parse_optional(input)` returns `Option<Duration>`.
- `parse(input)` returns `anyhow::Result<Duration>` with a descriptive expectation string.
- Serde `Visitor` accepts strings, unsigned seconds, and signed nonnegative seconds.
- `deserialize(de)` invokes `de.deserialize_str(Visitor::default())`.

### Control Flow and State
Parsing trims input, captures number and suffix, converts the number to `u64`, and constructs a `Duration`. Minute/hour/day conversions use `saturating_mul`, so very large valid numbers saturate rather than error after parsing.

### Dependencies and Integration Points
Uses `regex`, `serde`, `anyhow`, `LazyLock`, and `std::time::Duration`. Intended for serde annotations on configuration fields.

### Risks and Edge Cases
`deserialize` calls `deserialize_str`, so despite the visitor implementing numeric visits, some serde formats may not drive numeric values through this function unless they coerce to string. Saturation can hide overflow-like configuration mistakes. Negative values and malformed units fail.

### Test Signals
Unit tests cover plain seconds, whitespace, several units, invalid negative/malformed values, and too-large parse failure for number parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/parser/duration.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/parser/integer_range.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/parser/integer_range.rs

### Purpose
Parses a single positive integer or inclusive integer range from strings for serde config/CLI fields.

### Important APIs, Types, and Functions
- Regex accepts `lower` or `lower-upper` with optional spaces around `-`.
- `parse_optional<T>` returns `Option<RangeInclusive<T>>` for `T: FromStr + Copy + Ord`.
- `parse<T>` returns `anyhow::Result<RangeInclusive<T>>`.
- Generic serde `Visitor<T>` parses string input.
- `deserialize` exposes the serde hook.

### Control Flow and State
The parser captures the lower bound and optional upper bound. If no upper bound is present, it returns `lower..=lower`. If `upper < lower`, parsing fails. No persistent state exists.

### Dependencies and Integration Points
Uses `regex`, `serde`, `anyhow`, `RangeInclusive`, and generic `FromStr`. Useful for numeric config ranges.

### Risks and Edge Cases
The regex accepts only unsigned decimal syntax, so signed numeric types cannot parse negative ranges. It does not support open-ended ranges. `deserialize` uses string deserialization only. Type-specific overflow is handled by `FromStr` failure.

### Test Signals
Unit tests cover single values, whitespace, valid ranges, invalid strings, missing upper bounds, negative syntax, descending ranges, and empty input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/parser/integer_range.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/parser/integer_unit.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/parser/integer_unit.rs

### Purpose
Parses unsigned integers with optional SI or IEC unit prefixes from config/CLI strings.

### Important APIs, Types, and Functions
- Regex accepts a positive integer, optional prefix among `k`, `M`, `G`, `T`, `P`, `E` with optional `i`, and arbitrary alphabetic unit suffix.
- `parse_optional(input)` returns `Option<u64>`.
- `parse(input)` returns `anyhow::Result<u64>`.
- Serde `Visitor` accepts string, unsigned integer, and nonnegative signed integer inputs.
- `deserialize(de)` invokes string deserialization.

### Control Flow and State
Parsing trims input, extracts the number and prefix, parses `u64`, multiplies by base-10 or base-2 factor, and returns the result. Multiplication is saturating.

### Dependencies and Integration Points
Uses `regex`, `serde`, `anyhow`, and `LazyLock`. Used for byte/count-like configuration values where unit labels are syntactic convenience and the trailing unit word is ignored.

### Risks and Edge Cases
Saturating multiplication may silently turn too-large values into `u64::MAX`. Lowercase `m` is not megascale because only uppercase `M` is accepted. Arbitrary alphabetic trailing units are ignored, so typos after a valid prefix can still parse. `deserialize` uses string deserialization, so numeric visitor methods may not be used by all deserializers.

### Test Signals
Unit tests cover base values, SI prefixes, IEC prefixes, whitespace, invalid missing numbers, invalid `i` suffix alone, negative values, garbage, and empty strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/parser/integer_unit.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/run_state.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/run_state.rs

### Purpose
Implements shared application run-state signaling for graceful asynchronous shutdown and pre-shutdown notification.

### Important APIs, Types, and Functions
- Internal `RunState` enum has `Running`, `PreShutdown`, and `Shutdown`.
- `WeakRunStateHandle` can observe state without blocking shutdown completion.
- `RunStateHandle` observes state and holds a count receiver that keeps shutdown waiting until strong handles are dropped.
- `RunStateControl` sends state changes and waits for strong handles to close.
- `new()` creates a connected `RunStateHandle` and `RunStateControl`.
- `wait_for_shutdown` completes only on `Shutdown`.
- `wait_for_pre_shutdown` completes on `PreShutdown` or `Shutdown`.
- `pre_shutdown()` reports whether pre-shutdown has begun.
- `RunStateHandle::clone_weak()` creates a non-blocking observer.
- `RunStateControl::pre_shutdown()` sends the preparatory state; `shutdown(self)` sends final shutdown and awaits handle drop.

### Control Flow and State
State is broadcast through Tokio watch channels. Tasks select on wait futures and exit when signaled. Strong run-state handles keep `count_tx.closed().await` pending until dropped, while weak handles do not.

### Dependencies and Integration Points
Used by `conn/incoming.rs` listener/receiver loops and likely other async components. Depends on Tokio `watch` and standard `Deref`/`DerefMut` forwarding.

### Risks and Edge Cases
If a task keeps a `RunStateHandle` after receiving shutdown, `RunStateControl::shutdown` waits forever. `pre_shutdown` is one-way and cannot return to running. Watch receiver closure breaks wait loops, effectively treating sender drop as shutdown.

### Test Signals
Includes a Tokio test verifying pre-shutdown state, weak handle behavior, and shutdown completion after dropping the strong handle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/run_state.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/types.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/types.rs

### Purpose
Defines shared BeeGFS domain types, ID aliases, enums, display strings, gRPC conversions, quota/target states, and authentication-secret handling.

### Important APIs, Types, and Functions
- Re-exports `entity::*`.
- Type aliases include `Uid`, `TargetId`, `BuddyGroupId`, `Port`, `NodeId`, `PoolId`, and `QuotaId`.
- Constants include `MGMTD_ID`, `MGMTD_UID`, and `DEFAULT_STORAGE_POOL`.
- `NodeType` models meta, storage, client, and management nodes with BeeGFS integer values and user strings.
- `NodeTypeServer` restricts to meta/storage and converts to/from `NodeType`.
- `NicType` parses `tcp`/`rdma`, maps to BeeGFS integers, displays user strings, and optionally maps to protobuf NIC types.
- `CapacityPool` models normal/low/emergency and provides `bee_msg_vec_index`.
- `TargetConsistencyState` serializes/deserializes as `u8`.
- `QuotaIdType` and `QuotaType` model user/group and space/inode quota dimensions.
- `AuthSecret` is a BeeSerde wrapper over `u64`, with `hash_from_bytes`, `try_from_bytes`, and `FromStr`.

### Control Flow and State
The file is mostly type-level. Runtime behavior is validation/conversion: enum numeric conversions reject invalid values, `NodeTypeServer` rejects client/management, `NicType::from_str` rejects unknown names, and `AuthSecret` either hashes bytes with SHA-256 first eight bytes or parses a stringified integer.

### Dependencies and Integration Points
Uses `bee_serde`, `bee_serde_derive`, `anyhow`, `ring::digest`, optional protobuf modules, macros from `impl_macros.rs`, and `entity.rs`. These types are used throughout messages, connection addressing, gRPC APIs, and configuration.

### Risks and Edge Cases
Many IDs are aliases rather than newtypes, so accidental cross-use of target, buddy group, pool, and node IDs can compile. `AuthSecret::hash_from_bytes` keeps only the first eight SHA-256 bytes as little-endian `u64`, matching BeeGFS behavior but lowering entropy to 64 bits. `AuthSecret::try_from_bytes` says it expects a stringified `i64` in comments but parses into `u64` through the wrapper field type.

### Test Signals
No direct tests here. Enum conversion tests, auth-secret known vectors, and protobuf feature compile/tests would improve confidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/types/entity.rs -->
## sources/distributed-fs/beegfs-rust/shared/src/types/entity.rs

### Purpose
Defines entity identity abstractions: entity type, validated aliases, legacy numeric IDs, flexible entity ID selectors, and complete entity ID sets.

### Important APIs, Types, and Functions
- `EntityType` distinguishes node, target, buddy group, and pool, with display strings and optional protobuf conversion.
- `Alias` wraps `String` and validates aliases with regex `^[a-zA-Z][a-zA-Z0-9-_.]+$` and max length 32.
- `TryFrom<String>` and `TryFrom<&str>` construct aliases; `AsRef<str>`, `From<Alias> for String`, and `Display` expose values.
- `LegacyId` stores `NodeType` plus numeric ID and displays as `type:num`.
- Optional protobuf conversions validate `LegacyId` node type and nonzero numeric ID.
- `EntityId` is a selector enum: alias, legacy ID, or UID, with display and optional protobuf conversion from `EntityIdSet`.
- `EntityIdSet` contains all three identifiers and provides `node_type()` and `num_id()` accessors plus display formatting.

### Control Flow and State
No persistent state. Validation occurs during alias and protobuf conversions. Ambiguous protobuf `EntityIdSet` conversion to `EntityId` prefers UID, then alias, then legacy ID if multiple fields are present.

### Dependencies and Integration Points
Uses shared `NodeType`/`Uid`, `regex::Regex` with `LazyLock`, `anyhow`, display traits, and optional protobuf types. Used by management APIs, gRPC request parsing, and entity lookup logic.

### Risks and Edge Cases
Alias regex requires at least two characters because it has one leading character plus `+` for the remainder; a single-letter alias is rejected. Protobuf `EntityIdSet` to `EntityId` precedence can hide conflicting fields rather than rejecting them. `EntityIdSet` itself assumes a node-style legacy ID, which may not fit target/pool/buddy-group entities without higher-level context.

### Test Signals
No local tests. Needed tests include alias boundary lengths, single-character alias behavior, invalid characters, protobuf conflict handling, and display output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/types/entity.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/sqlite/Cargo.toml -->
## sources/distributed-fs/beegfs-rust/sqlite/Cargo.toml

### Purpose
Declares the `sqlite` helper crate used by BeeGFS Rust components for SQLite connection pooling, migrations, and transaction utilities.

### Important APIs, Types, and Functions
- Package metadata uses workspace edition/authors/docs/homepage/publish settings.
- Dependencies: `anyhow`, `log`, `tokio`, and `rusqlite` with the `backup` feature.

### Control Flow and State
No runtime control flow. The manifest enables features needed by source files, especially database backup support in `migration.rs`.

### Dependencies and Integration Points
The crate is consumed by management/database code and by the `sqlite_check` proc-macro crate. It relies on workspace dependency versions.

### Risks and Edge Cases
Workspace dependency changes can alter SQLite behavior globally. Only `backup` is explicitly enabled here; other rusqlite features such as bundled SQLite or array support must come from workspace configuration if needed.

### Test Signals
Build and test of the `sqlite` crate validate manifest dependency consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/sqlite/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/sqlite/src/connection.rs -->
## sources/distributed-fs/beegfs-rust/sqlite/src/connection.rs

### Purpose
Provides SQLite connection setup and an async-friendly connection pool wrapper around blocking `rusqlite` operations.

### Important APIs, Types, and Functions
- `setup_connection` loads the `carray` virtual table module, enables foreign keys/triggers, sets a 30-second busy timeout, enables WAL mode, and sets `synchronous=full`.
- `open(db_file)` opens an existing DB read/write without creating it and applies setup.
- `open_in_memory()` creates an in-memory DB and applies setup.
- `Connections` is a cloneable wrapper around `Arc<InnerConnections>`.
- `SyncMode` selects `Full` or temporary `Normal` sync behavior.
- `Connections::new` and `new_in_memory` create file-backed and shared-cache in-memory pools.
- `write_tx`, `write_tx_no_sync`, `read_tx`, and `conn` run closures on a connection through `run_op`.
- `run_op` uses `tokio::task::spawn_blocking`, pops or opens a rusqlite connection, runs the closure, resets sync mode if needed, and returns the connection to the pool.

### Control Flow and State
The pool stores idle `rusqlite::Connection` objects in a `Mutex<Vec<Connection>>`. Operations execute in Tokio's blocking thread pool. Write transactions use `Immediate` behavior so the busy timeout applies before write locks are needed. In-memory pools use distinct shared-cache URI names generated by an atomic counter.

### Dependencies and Integration Points
Uses `rusqlite`, Tokio blocking tasks, `anyhow`, `log`, and standard path/sync types. Higher-level database code calls these methods to avoid blocking async workers directly.

### Risks and Edge Cases
If `op` returns an error, the connection is still returned to the pool; this assumes rusqlite connection state remains usable after all errors. `write_tx_no_sync` drops the connection if resetting sync mode fails, but the comment has a typo only. There is no explicit maximum number of pooled/open connections beyond Tokio blocking-thread limits. `open` refuses to create missing DB files, so callers must create/migrate before pooling.

### Test Signals
No tests in this file. Integration tests should cover WAL setup, in-memory isolation, immediate write contention, `write_tx_no_sync` sync reset, and connection reuse after closure errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/sqlite/src/connection.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/sqlite/src/lib.rs -->
## sources/distributed-fs/beegfs-rust/sqlite/src/lib.rs

### Purpose
Crate root for the SQLite helper crate.

### Important APIs, Types, and Functions
- Private modules: `connection`, `migration`, and `transaction`.
- Publicly re-exports all items from those modules with `pub use`.

### Control Flow and State
No runtime behavior. It defines the public API surface.

### Dependencies and Integration Points
Consumers import connection pooling, migration, and transaction extension helpers from this crate root.

### Risks and Edge Cases
Glob re-exports make all helper names part of the public API and can create name collisions as modules grow.

### Test Signals
Compile checks validate exports; behavior tests live in child modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/sqlite/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/sqlite/src/migration.rs -->
## sources/distributed-fs/beegfs-rust/sqlite/src/migration.rs

### Purpose
Provides build-time and runtime SQLite migration utilities: reading numbered SQL files, generating Rust migration slices, flattening schemas, checking DB versions, applying migrations, and backing up DB files.

### Important APIs, Types, and Functions
- `Migration` stores static versioned SQL for runtime use.
- `OwnedMigration` stores owned SQL read from files at build time.
- `read_migrations(src_dir)` reads `n.sql` files, sorts by version, rejects empty/non-contiguous sets, and returns owned migrations.
- `migrations_slice_code` emits Rust code for a `&[::sqlite::Migration]` literal.
- `flatten_migrations` applies migrations to an in-memory database and extracts ordered SQL from `sqlite_schema`.
- `check_schema(tx, migrations)` compares `PRAGMA user_version` to migration base/latest and reports whether migration is needed.
- `migrate_schema(tx, migrations)` applies pending migrations and updates `user_version`.
- `backup_db(conn)` copies the current database to `<db_file>.v<version>`.
- `check_migration_versions` validates contiguity and returns `(base, latest)`.

### Control Flow and State
Build-time functions read SQL files and generate code/schema snapshots. Runtime migration reads `user_version`, normalizes new DB version `0` to `base - 1`, skips already-applied migrations by index, executes remaining SQL batches, and updates `user_version`. Backup uses rusqlite's backup API.

### Dependencies and Integration Points
Uses `rusqlite`, `anyhow`, filesystem APIs, and `std::fmt::Write`. Integrated into build scripts and runtime database startup paths. `sqlite_check` depends on flattened schema output.

### Risks and Edge Cases
If the first remaining migration has version `0`, `base - 1` underflows, but migration versions are expected to start at positive integers. `migrations_slice_code` embeds SQL in a raw string using `r#"... "#`; SQL containing the delimiter sequence could break generated Rust. `flatten_migrations` emits schema SQL ordered by type/name, which may still miss dependencies beyond the chosen order in unusual schemas. `check_schema` treats database version `0` as invalid unless latest is also zero; runtime callers should use `migrate_schema` for new DBs.

### Test Signals
Unit tests cover migration application across contiguous versions, dropping early migrations after a new base, failure when up-to-date, non-contiguous migration failure, and schema flattening order for tables/indexes/views.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/sqlite/src/migration.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/sqlite/src/transaction.rs -->
## sources/distributed-fs/beegfs-rust/sqlite/src/transaction.rs

### Purpose
Adds convenience methods for rusqlite transactions and helper functions for array parameters and affected-row validation.

### Important APIs, Types, and Functions
- `TransactionExt` defines `execute_cached`, `query_row_cached`, and `query_map_collect`.
- Implementation for `Transaction<'_>` wraps `prepare_cached` plus execute/query helpers.
- `rarray_param(iter)` converts an iterator into `Rc<Vec<rusqlite::types::Value>>` for use with `rarray(?n)` and the loaded carray/array module.
- `check_affected_rows(affected, allowed)` returns success only if `affected` is in the allowed set; otherwise it maps to `rusqlite::Error::StatementChangedRows`.

### Control Flow and State
All helpers are synchronous transaction utilities. Cached statement preparation is delegated to rusqlite's transaction cache. `rarray_param` materializes values into an `Rc` for rusqlite parameter binding.

### Dependencies and Integration Points
Depends on `rusqlite`, `anyhow`, and `Rc`. Used by database access layers to reduce boilerplate and validate mutations.

### Risks and Edge Cases
`rarray_param` allocates the entire iterator, so huge arrays can be memory-heavy. `check_affected_rows` converts a rusqlite error through anyhow and back to `Result<()>`; callers get generic anyhow context unless they inspect the source. Statement caching effectiveness depends on stable SQL strings.

### Test Signals
No local tests. Useful tests should exercise cached query helpers, `rarray_param` with the loaded array module, and affected-row validation for zero/one/many rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/sqlite/src/transaction.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/sqlite_check/Cargo.toml -->
## sources/distributed-fs/beegfs-rust/sqlite_check/Cargo.toml

### Purpose
Declares the `sqlite_check` procedural macro crate for compile-time validation of literal SQL statements against the BeeGFS management SQLite schema.

### Important APIs, Types, and Functions
- Package metadata uses workspace settings.
- `[lib] proc-macro = true` enables procedural macro export.
- Dependencies: local `sqlite` crate, `syn` with `parsing`, and workspace `rusqlite`.

### Control Flow and State
No runtime behavior in the manifest. It configures the crate as a proc macro and wires dependencies needed by `src/lib.rs`.

### Dependencies and Integration Points
Consumed by crates that invoke the `sql!` macro. Depends on build scripts producing a schema file under `OUT_DIR`.

### Risks and Edge Cases
Proc-macro crates run at compile time; dependency or schema generation failures become build failures. The local path dependency requires workspace layout consistency.

### Test Signals
Builds of consumers using `sql!` validate the manifest. Dedicated compile-fail tests would be useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/sqlite_check/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/sqlite_check/src/lib.rs -->
## sources/distributed-fs/beegfs-rust/sqlite_check/src/lib.rs

### Purpose
Implements the `sql!` procedural macro, which validates literal SQL at compile time by preparing it against an in-memory SQLite database loaded with the generated management schema.

### Important APIs, Types, and Functions
- Global `DB_CONN: OnceLock<Arc<Mutex<rusqlite::Connection>>>` caches one schema-loaded in-memory connection per compiler process.
- `sql(input)` parses a string literal with `syn::LitStr`, prepares it on the cached connection, panics on invalid SQL, and returns the original token stream unchanged.
- `open_db()` opens an in-memory SQLite DB through the helper crate, reads `OUT_DIR/current.sql`, executes the schema, and returns the locked connection wrapper.

### Control Flow and State
The first macro invocation initializes the database from `OUT_DIR/current.sql`; later invocations reuse it. Each macro call prepares but does not execute the statement, so it validates syntax and referenced schema names without needing data.

### Dependencies and Integration Points
Depends on `sqlite::open_in_memory`, `rusqlite`, `syn`, environment variable `OUT_DIR`, and a build-script-generated `current.sql`. Used in management code to catch invalid literal queries at compile time.

### Risks and Edge Cases
Invalid SQL panics during macro expansion, which is acceptable for compile-time validation but can produce terse errors. Only string literals are supported; dynamic SQL cannot be checked. It only prepares statements, so runtime-only constraints, parameter types, and data-dependent errors are not validated. Missing `OUT_DIR` or `current.sql` causes unwrap panics.

### Test Signals
No local tests. Compile-pass/fail tests should cover valid statements, invalid table/column names, non-literal inputs, and missing schema setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/sqlite_check/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/CMakeLists.txt -->
## sources/distributed-fs/beegfs/client_module/CMakeLists.txt

### Purpose
Integrates the BeeGFS client kernel module into the CMake packaging/build flow, including DKMS source installation, default config installation, and Debian/RPM package metadata.

### Important APIs, Types, and Functions
- If `BEEGFS_SKIP_CLIENT` is not set, `ExternalProject_Add(client-module)` builds in source using `make -C build -j $(nproc)` with `KDIR` and `OFED_INCLUDE_PATH`.
- `configure_file` produces DKMS and package maintainer scripts from build templates.
- Installs the client module source tree to `usr/src/beegfs-${BEEGFS_VERSION}` and compat source tree to `usr/src/beegfs-compat-${BEEGFS_VERSION}`.
- Installs generated `dkms.conf` and default `etc/beegfs/beegfs-client.conf`.
- Sets package dependencies/requires on `dkms` and package script hooks for Debian/RPM.

### Control Flow and State
CMake configure time generates files; build time invokes the kernel-module make flow; install/package time copies source trees and scripts. No runtime application state.

### Dependencies and Integration Points
Depends on CMake `ExternalProject`, Makefile targets under `client_module/build`, kernel directory variable `BEEGFS_KERNELDIR`, optional OFED include directory `BEEGFS_OFEDDIR`, and CPACK variables.

### Risks and Edge Cases
`BUILD_COMMAND` uses `$(nproc)`, which is shell/make-specific inside CMake and may be nonportable. Installing `DIRECTORY ""` copies a broad source tree and relies on exclusion patterns to avoid unwanted files. Compat DKMS packaging appears commented as currently unsupported. Missing kernel headers or OFED path failures surface during external build.

### Test Signals
Build/package tests should exercise normal client build, `BEEGFS_SKIP_CLIENT`, Debian/RPM package metadata, and DKMS install paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/dkms.conf.in -->
## sources/distributed-fs/beegfs/client_module/dkms.conf.in

### Purpose
Template for DKMS configuration of the BeeGFS client kernel module.

### Important APIs, Types, and Functions
- Template variables: `__NAME__`, `__VERSION__`, and `__MODNAME__`.
- `BUILT_MODULE_NAME[0]`, `BUILT_MODULE_LOCATION[0]`, and `DEST_MODULE_LOCATION[0]` describe the built module.
- `MAKE[0]` runs `make -C build module` with `KDIR=$kernel_source_dir`, target module name, and version.
- `CLEAN` invokes `make -C build clean`.
- `AUTOINSTALL="yes"` requests automatic rebuild/install for new kernels.

### Control Flow and State
DKMS substitutes variables and executes the configured make/clean commands when building or removing modules. State is managed by DKMS outside this file.

### Dependencies and Integration Points
Used by CMake/package scripts to generate installable DKMS metadata. Depends on the client module `build` Makefile supporting `module` and `clean` targets.

### Risks and Edge Cases
Quoting in `MAKE[0]` must survive DKMS shell handling. Kernel source directory correctness is delegated to DKMS. Template mismatch with actual module target names breaks DKMS builds.

### Test Signals
DKMS add/build/install tests on supported distributions validate the template.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/dkms.conf.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/include/uapi/beegfs_client.h -->
## sources/distributed-fs/beegfs/client_module/include/uapi/beegfs_client.h

### Purpose
Defines the BeeGFS client kernel module user-space ABI: ioctl request numbers, constants, and argument structures for file creation, mount/config queries, stripe info, inode/entry info, ping, and file-state changes.

### Important APIs, Types, and Functions
- Buffer and protocol constants define maximum config path, mount ID, node alias/type, filename, entry ID, ping counts, and stripe pattern values.
- `BEEGFS_IOCTYPE_ID` is `'f'`; `BEEGFS_IOCNUM_*` enumerate ioctl command numbers.
- `BEEGFS_IOC_*` macros use `_IOR` and `_IOW` to define ioctl request codes and associated structs.
- File creation structs: `BeegfsIoctl_MkFile_Arg`, `MkFileV2`, and `MkFileV3`, with increasing support for 32-bit owner/group IDs, buddy-mirrored parent flag, and storage pool override.
- Query structs: `GetCfgFile`, `GetStripeInfo`, `GetStripeTarget`, `GetStripeTargetV2`, `GetInodeID`, `GetEntryInfo`, and `PingNode`.
- `BeegfsIoctl_SetFileState_Arg` updates access/data state for a named file.

### Control Flow and State
No control flow. This header fixes memory layouts exchanged between user space and the kernel through ioctl calls. Kernel handlers copy in/out these structs and perform corresponding filesystem operations.

### Dependencies and Integration Points
Included by user-space tools and kernel module code. Relies on Linux ioctl macros and types such as `uid_t`, `gid_t`, `uint16_t`, and `uint32_t` from surrounding includes. Must stay ABI-compatible with existing BeeGFS tools.

### Risks and Edge Cases
ABI changes are high risk: struct field order, sizes, and ioctl numbers must not change unintentionally. `BEEGFS_IOCTL_TEST_BUFLEN` is documented as wrong for the exchanged string but retained for compatibility. Several structs contain user pointers and lengths; kernel handlers must validate copy lengths and nullability. Mixed 16-bit and 32-bit IDs reflect legacy compatibility and can truncate if misused.

### Test Signals
ABI tests should compare ioctl numbers and struct sizes across architectures, and integration tests should exercise each ioctl through user-space tooling against the client module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/include/uapi/beegfs_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/Makefile -->
## sources/distributed-fs/beegfs/client_module/source/Makefile

### Purpose
Kernel-build Makefile for the BeeGFS client module source tree. It runs feature detection, sets compiler flags, declares the module object, and lists all C sources compiled into the module.

### Important APIs, Types, and Functions
- `BEEGFS_CLIENT_BUILDDIR` locates the adjacent build directory.
- `BEEGFS_FEATURE_DETECTION` invokes `feature-detect-cacher.sh` and `feature-detect.sh` with kernel build flags.
- Fails the build unless feature detection ends with `--~~success~~--`.
- Adds feature-detection output and `BEEGFS_CFLAGS` to `ccflags-y`.
- Helper variables/functions compute kernel version and conditionally add flags.
- `obj-m += ${TARGET}.o` declares the module.
- `SOURCES` enumerates all C files for networking, messages, filesystem ops, threading, node stores, caches, components, and app/config/logging.
- `${TARGET}-y` maps sources to objects.
- `BEEGFS_NO_RDMA` adds a compile define.
- `OFED_INCLUDE_PATH` adds OFED include paths and compatibility include flags; kernel >= 4.18 gets `HAVE_BITS_H`.

### Control Flow and State
This is evaluated by Kbuild. Feature detection happens at make evaluation time. The object list controls module composition. Optional RDMA/OFED branches adjust compilation based on environment.

### Dependencies and Integration Points
Depends on Linux kernel Kbuild variables, BeeGFS feature-detection scripts, OFED headers when configured, and the full client source tree. Invoked by DKMS, CMake external build, and direct make flows.

### Risks and Edge Cases
Feature-detection output is injected into compiler flags; incorrect shell quoting can break builds, which the header comment says was a known issue. The source list is manual and can omit new files. Kernel-version helper only uses major/patchlevel formatting and may be too coarse for distro backports. OFED compatibility includes can conflict with kernel headers.

### Test Signals
Build matrix tests across supported kernels, with/without RDMA and OFED, are the primary signal. Feature-detect script output should be cached and validated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/app/App.c -->
## sources/distributed-fs/beegfs/client_module/source/app/App.c

### Purpose
Implements the BeeGFS client kernel module application lifecycle: configuration loading, network/interface setup, local node identity, buffer/store allocation, inode-operation table setup, component construction/start/stop/join, mount sanity checks, and runtime update helpers.

### Important APIs, Types, and Functions
- `__App_probe_sockDomain` checks IPv6 socket/connect behavior and falls back to `AF_INET` when IPv6 is unavailable.
- `App_init` initializes all `App` fields to safe defaults, initializes lists/mutexes/counters, and records the owned `MountConfig`.
- `App_uninit` destructs components/stores/nodes/filters/config in reverse-ish order, disables logging before tearing down dependencies, frees inode op tables and fsUUID, and uninitializes locks/lists.
- `App_run` initializes data objects, inode operations, components, logs startup info, starts threads, waits briefly for management initialization, and performs mount sanity checks.
- `App_stop` stops components, optionally disables connection retries for unmount, joins components, and logs completion.
- `__App_initDataObjects` builds config, validates management host, decides socket domain, loads net/TCP-only/interface/RDMA/preferred-node filters, creates stores/mappers/state stores/node stores/local node, preallocates buffer stores, and creates ack/inode/statfs stores.
- `__App_initInodeOperations` allocates per-app Linux `inode_operations` tables and populates callbacks based on kernel feature macros and config flags for xattrs/ACLs.
- `App_updateLocalInterfaces`, `App_cloneLocalNicList`, `App_cloneLocalRDMANicList`, `App_findAllowedInterfaces`, and `App_findAllowedRDMAInterfaces` manage NIC discovery and propagation to node objects.
- `App_cloneFsUUID` and `App_updateFsUUID` manage filesystem UUID with a mutex.
- `__App_initLocalNodeInfo` discovers NICs, generates a client alias from PID/time/hostname truncated to 32 chars, and constructs the local node.
- `__App_initComponents`, `__App_startComponents`, `__App_stopComponents`, `__App_joinComponents`, and `__App_waitForComponentTermination` manage `DatagramListener`, `InternodeSyncer`, `AckManager`, and optional `Flusher`.
- `__App_logInfos` logs version, client ID, NICs, filters, preferred nodes, and ACL/xattr warnings.
- `__App_mountServerCheck` temporarily disables retries, waits for management init, stats root metadata and storage free space, then restores retry setting.
- `App_getVersionStr` returns compile-time `BEEGFS_VERSION`.

### Control Flow and State
Lifecycle is staged: `App_init` zeroes/initializes fields; `App_run` calls data setup, inode op setup, component setup/start, and mount verification; `App_stop` terminates and joins background threads; `App_uninit` frees resources. The `App` object owns most client-module runtime state: config/logger, filters, preferred node lists, local node, node stores, target/buddy mappers, target state stores, buffer stores, ack/inode/statfs caches, components, inode operation tables, lock counters, retry flags, benchmark mode, socket domain, RDMA NIC list, and fsUUID.

### Dependencies and Integration Points
Includes many kernel BeeGFS components: config/logging, sockets/NIC filters, target/buddy mappers, target state stores, node stores, ack manager, datagram listener, internode syncer, flusher, filesystem operations, remoting, inode ref store, buffer store, statfs cache, and kernel xattr APIs. It is the central integration point between mount configuration, networking, protocol state, and Linux VFS operation tables.

### Risks and Edge Cases
`App_updateFsUUID` overwrites `this->fsUUID` without freeing the previous value, so repeated updates can leak. `__App_logInfos` builds an extended NIC string in a fixed 1024-byte buffer with repeated `snprintf`/`strcpy`; many NICs can truncate and possibly produce confusing logs, though `snprintf` bounds the temporary. Initialization has many early returns; cleanup relies on `App_uninit` tolerating partially initialized state. `__App_initLocalNodeInfo` allocates `alias` without checking for allocation failure before `strncpy`. Component stop/join assumes thread self-termination proceeds; blocking join can hang unmount if a component never exits. `connRetriesEnabled` is `volatile bool` but not otherwise synchronized.

### Test Signals
Primary signals are kernel-module build/load/mount/unmount tests, mount sanity check failures, config parser tests, and VFS operation integration tests. Focused tests should exercise partial-initialization cleanup, IPv6 fallback, interface filtering, xattr/ACL feature combinations, repeated fsUUID updates, and component termination timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/app/App.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/app/App.h -->
## sources/distributed-fs/beegfs/client_module/source/app/App.h

### Purpose
Declares the BeeGFS client kernel module `App` object, lifecycle functions, helper functions, runtime state fields, and inline accessors used throughout the client module.

### Important APIs, Types, and Functions
- Return codes: `APPCODE_NO_ERROR`, `APPCODE_PROGRAM_ERROR`, `APPCODE_INVALID_CONFIG`, `APPCODE_INITIALIZATION_ERROR`, and `APPCODE_RUNTIME_ERROR`.
- Forward declarations cover config, logger, components, node stores, mappers, state stores, buffer stores, ack store, filters, inode ref store, and statfs cache.
- Lifecycle declarations: `App_init`, `App_uninit`, `App_run`, `App_stop`.
- Internal setup declarations: `__App_initDataObjects`, inode ops, local node info, components, start/stop/join, logging, mount check, and interface discovery.
- External helpers: version string, local interface update/clone, fsUUID clone/update, local/RDMA NIC clone.
- `struct App` stores configuration, logger, fsUUID mutex, filters, preferred lists, RDMA NIC list and mutex, local and remote node stores, target/buddy mappers, state stores, buffer stores, ack/inode/statfs stores, components, lock ack counter, retry/benchmark flags, inode operation tables, socket domain, and debug counters under `BEEGFS_DEBUG`.
- Inline getters expose nearly all internal fields, plus setters for retry and benchmark flags.
- Debug inline functions increment counters under a mutex; in non-debug builds increments compile to no-ops.

### Control Flow and State
The header centralizes ownership and access patterns for the `App` state object. Most modules obtain dependencies through inline getters rather than receiving narrower interfaces. `App_lockNicList` and `App_unlockNicList` define a manual lock protocol for direct RDMA NIC list access.

### Dependencies and Integration Points
Includes mount config, list iterators, NIC address list, atomic/mutex/thread abstractions, common definitions, and bit store headers. It is included by most client module subsystems that need application context or shared stores.

### Risks and Edge Cases
The broad `App` struct and many inline getters create tight coupling across the client module. Manual NIC-list locking is error-prone because callers must pair lock/unlock. `connRetriesEnabled` is volatile but not a full synchronization primitive. Inline non-static function definitions in a header can be risky in C unless compiler/linkage expectations are controlled; declarations are `static inline` prototypes but definitions omit `static inline` text in the shown file, relying on prior declarations style and compiler behavior.

### Test Signals
Compile tests across supported kernels are essential because struct members and inode operation fields depend on feature macros. Runtime mount/unmount tests exercise getter wiring and state ownership. Debug builds should exercise counter increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/app/App.h -->

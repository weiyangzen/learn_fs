# subset-b-006290 Research

Grouped code research for TIPC message formatting, name distribution/name table management, network identity/netlink configuration, legacy netlink compatibility, and peer node/link lifecycle files under the Ceph client source tree. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/msg.c -->
# sources/distributed-fs/ceph-client/net/tipc/msg.c

## Purpose
`msg.c` implements the allocation, initialization, validation, construction, fragmentation, bundling, extraction, reversal, cloning, destination lookup, and reassembly helpers for TIPC packets carried in Linux `sk_buff` objects. It is the concrete implementation behind the protocol header accessors in `msg.h` and is used by sockets, links, broadcast, name distribution, connection management, and rejection paths.

## Important APIs, Types, And Functions
Important exported functions include `tipc_buf_acquire()`, `tipc_msg_init()`, `tipc_msg_create()`, `tipc_buf_append()`, `tipc_msg_append()`, `tipc_msg_validate()`, `tipc_msg_fragment()`, `tipc_msg_build()`, `tipc_msg_try_bundle()`, `tipc_msg_extract()`, `tipc_msg_reverse()`, `tipc_msg_skb_clone()`, `tipc_msg_lookup_dest()`, `tipc_msg_assemble()`, `tipc_msg_reassemble()`, `tipc_msg_pskb_copy()`, `__tipc_skb_queue_sorted()`, and `tipc_skb_reject()`. File-level constants compute crypto-aware headroom and the exported `one_page_mtu` fallback.

## Control Flow
Outbound message construction starts by allocating an skb with reserved link-layer/crypto headroom, initializing the TIPC header, and either copying data directly or splitting it into `MSG_FRAGMENTER` packets when the message exceeds the selected MTU. `tipc_msg_build()` can fall back from `MAX_MSG_SIZE` to `one_page_mtu`, then immediately reassemble the resulting local fragment list when the large allocation failed. `tipc_msg_append()` supports stream-like appending into a queue of MSS-sized buffers and updates block accounting. Bundling checks that the new message is not already a fragment, tunnel, or broadcast message, optionally pushes an outer `MSG_BUNDLER` header onto the previous skb, appends aligned inner messages, and consumes the appended skb on success.

Receive-side validation first mitigates extreme `skb->truesize` versus rounded payload length by copying into a right-sized skb, then enforces minimum pullability, header size bounds, protocol version, message size consistency, maximum user payload size, and actual skb length. Fragment reassembly uses `tipc_buf_append()` to linearize the first fragment, coalesce or chain later fragments, validate the completed packet, and carefully repair ownership when validation replaces the skb. Bundled extraction linearizes the outer skb, copies one inner message by `pos`, validates it, and frees the outer skb on exhaustion or error. Reversal builds a new reply buffer, avoids returning droppable or already errored traffic, caps returned payload at `MAX_FORWARD_SIZE`, expands short headers to basic headers, swaps ports/nodes, and sets the requested error code.

## State And Persistence
This file owns no global persistent table, but it mutates skb-local state. `TIPC_SKB_CB(skb)->validated` caches header validation; `TIPC_SKB_CB(head)->tail` tracks fragment-chain tail during reassembly; message header words carry sequence numbers, sizes, user/type fields, reroute count, destination ports/nodes, and error codes. Queue order and skb ownership are part of the state contract: many helpers consume input buffers on both success and failure.

## Dependencies And Integration Points
The file depends on Linux skb primitives, iterator copying from userspace, endian conversion through `msg.h`, `name_table.h` for named-service anycast lookup, `addr.h` scope helpers, and optional crypto headroom/tag sizing from `crypto.h`. Link code calls fragmentation, validation, clone/copy, sorted queueing, and reassembly helpers. Socket and transport code use build/append/reverse/reject paths. Name lookup reroutes named data messages via `tipc_nametbl_lookup_anycast()`.

## Risks And Edge Cases
The highest risk is skb lifetime confusion: several functions consume, replace, or null caller pointers, and error paths must not double free partially assembled chains. Header validation is a security boundary for untrusted network input. Fragment reassembly must keep `truesize`, `data_len`, and `len` consistent after coalescing. Bundling relies on 4-byte alignment and sufficient tailroom. `tipc_msg_lookup_dest()` deliberately rejects repeated reroutes to avoid loops. `tipc_msg_reverse()` must not amplify traffic by returning large payloads or SYN overload data.

## Test Signals
Useful tests include malformed header fuzzing, non-linear skb validation, `truesize` stress, fragmentation/reassembly across MTU boundaries, first/middle/last fragment loss or duplication, bundle extraction with padding, user iterator short-copy faults, named-message reroute success/failure, rejection path behavior for droppable and already errored packets, skb clone/copy allocation failures, sorted sequence queue insertion including duplicates, and crypto-enabled versus crypto-disabled headroom builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/msg.h -->
# sources/distributed-fs/ceph-client/net/tipc/msg.h

## Purpose
`msg.h` is the internal TIPC wire-format contract. It defines message users, message types, header sizes, the skb control block layout, packed TIPC header structures, gap-ACK records, inline header bitfield accessors, protocol constants for internal users, and prototypes for the skb/message helpers implemented in `msg.c`.

## Important APIs, Types, And Functions
Important constants include `TIPC_VERSION`, payload types such as `TIPC_CONN_MSG`, `TIPC_NAMED_MSG`, and group message types, internal users such as `BCAST_PROTOCOL`, `LINK_PROTOCOL`, `NAME_DISTRIBUTOR`, `MSG_FRAGMENTER`, `TUNNEL_PROTOCOL`, and `MSG_CRYPTO`, plus header sizes from `SHORT_H_SIZE` through `MAX_H_SIZE`. Important types are `struct tipc_skb_cb`, `struct tipc_msg`, `struct tipc_gap_ack`, and `struct tipc_gap_ack_blks`. Inline APIs read and write every significant header field: size, user/type, errors, sequence/ack, broadcast ACKs/gaps, ports, nodes, service ranges, fragmentation metadata, link state, tunnel sync, group broadcast state, crypto/discovery node IDs, and skb queue operations.

## Control Flow
The header has no standalone runtime loop, but its inlines are on the hot path for nearly all TIPC send and receive logic. `buf_msg()` casts skb data to the wire header; `msg_word()`, `msg_set_word()`, `msg_bits()`, and `msg_set_bits()` centralize endian-aware bitfield access. Higher-level helpers then interpret the same header words differently depending on user/type, for example word 1 bits serve payload type/error/legacy flags, name-distribution bulk markers, or link activation session state. Queue helpers wrap locked or lockless skb list access used by links, sockets, and receive queues.

## State And Persistence
Persistent protocol state is encoded in skb headers and the skb control block. `struct tipc_skb_cb` stores reassembly tail pointers, retransmission metadata, bytes read, chain importance, ackers, retransmit count, validation and optional crypto flags/context. `struct tipc_msg` is a fixed 15-word big-endian header that supports the largest internal layouts. Gap ACK structures persist selective acknowledgement records in message payloads for unicast and broadcast loss reporting.

## Dependencies And Integration Points
The header includes `<linux/tipc.h>` and `core.h`, and is included throughout the TIPC subsystem. It underpins `msg.c`, `link.c`, `bcast.c`, `node.c`, `name_distr.c`, socket receive/transmit code, crypto handling, discovery, group communication, and netlink-facing diagnostics that inspect link/node state. Public prototypes expose the message helper surface used by those modules.

## Risks And Edge Cases
Field overlap is intentional and context-sensitive, so changing one accessor can corrupt unrelated protocol users. Size accessors assume headers have already been validated or pulled into linear data. Several fields are only valid for internal message users, and some helpers transparently descend into an inner header for fragments. `TIPC_SKB_CB` must fit within `skb->cb`, remain packed as expected, and keep crypto fields conditional. Queue helpers mix lock-protected and caller-lock-required forms, so misuse can race list mutation.

## Test Signals
Compile coverage across `CONFIG_TIPC_CRYPTO` variants is important. Runtime signals include protocol header encode/decode tests, endian correctness, max/min header size validation, fragment inner-header access, gap ACK serialization, queue helper behavior under lockdep, payload/internal user importance mapping, legacy/non-legacy name distributor bits, and fuzzing that exercises all accessors through `tipc_msg_validate()` and receive paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/name_distr.c -->
# sources/distributed-fs/ceph-client/net/tipc/name_distr.c

## Purpose
`name_distr.c` distributes cluster-scope TIPC service publications between nodes and consumes remote publication updates into the local name table. It turns local `struct publication` objects into `NAME_DISTRIBUTOR` messages, bulk-sends all current cluster publications to newly reachable peers, orders received updates by sequence number, and purges remote publications when a node is lost.

## Important APIs, Types, And Functions
The file exports `sysctl_tipc_named_timeout`, `tipc_named_publish()`, `tipc_named_withdraw()`, `tipc_named_node_up()`, `tipc_publ_notify()`, `tipc_named_rcv()`, and `tipc_named_reinit()`. Internal helpers include `publ_to_item()`, `named_prepare_buf()`, `named_distribute()`, `tipc_publ_purge()`, `tipc_update_nametbl()`, and `tipc_named_dequeue()`.

## Control Flow
Local publish inserts node-scope publications into `name_table.node_scope` without sending anything, while cluster-scope publications are appended to `name_table.cluster_scope`, encoded as a one-item `PUBLICATION` message, assigned `snd_nxt`, marked non-legacy, and returned for broadcast. Withdraw removes the publication from the scope list and, for cluster scope, returns a one-item `WITHDRAWAL` message. When a node comes up, `tipc_named_node_up()` adjusts the replicast destination count for peers lacking `TIPC_NAMED_BCAST`, snapshots the sequence number, walks `cluster_scope`, packs as many `distr_item` entries per MTU-sized message as possible, marks bulk and final-bulk flags, and unicasts the chain to the new peer.

Receive processing dequeues messages from the node broadcast/name queue. Legacy and bulk messages bypass sequence gating; non-legacy single updates wait until the stream is opened by the last bulk message and `rcv_nxt` matches the message sequence. Publications call `tipc_nametbl_insert_publ()` and then subscribe the publication to the source node for later purge. Withdrawals call `tipc_nametbl_remove_publ()`, unsubscribe, and free the publication via RCU. Node-loss notification walks the node publication list, purges each remote publication, and decrements `rc_dests` for peers that required replicast.

## State And Persistence
Name distribution state lives mostly in `struct name_table`: `node_scope`, `cluster_scope`, `cluster_scope_lock`, `snd_nxt`, and `rc_dests`. Per-peer receive state is stored by `node.c` in `bc_entry.namedq`, `named_rcv_nxt`, and `named_open`. Remote publications are linked into each node's `publ_list` via `publication.binding_node` so they can be withdrawn on node failure. `tipc_named_reinit()` rewrites local publication node addresses after network address changes and resets `rc_dests`.

## Dependencies And Integration Points
The file depends on `msg.h` wire helpers, `name_table.h` publication insertion/removal, `node.h` subscription and transmit helpers, link MTU lookup through `tipc_node_get_mtu()`, and broadcast/receive integration in `node.c`. It is called from socket bind/unbind paths indirectly through `tipc_nametbl_publish()`/`withdraw()`, from node-up/link-up handling, and from broadcast receive processing.

## Risks And Edge Cases
Bulk distribution assumes at least one message is queued before setting the final-bulk sequence; empty cluster-scope lists rely on callers tolerating no payload. Sequence gating must handle wraparound and avoid processing updates before the initial bulk snapshot completes. `rc_dests` accounting must match peer capability changes and node-loss cleanup. Publication purge holds the global name-table lock while removing from service structures, and lifetime relies on RCU freeing after unlinking from node subscriptions.

## Test Signals
Tests should cover node-scope versus cluster-scope publish/withdraw, bulk sync to a newly reachable node, MTU-limited multi-message bulk distribution, legacy peer handling, sequence wrap/reorder/drop behavior in `tipc_named_dequeue()`, remote publication purge on node down, `TIPC_NAMED_BCAST` capability toggling and `rc_dests` accounting, address reinitialization, duplicate withdraw warnings, and lockdep/RCU validation during concurrent publish and node failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/name_distr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/name_distr.h -->
# sources/distributed-fs/ceph-client/net/tipc/name_distr.h

## Purpose
`name_distr.h` defines the compact on-wire item used by TIPC name distribution and declares the publication distribution API used by the name table and node receive paths. It is the contract between local publication storage and `NAME_DISTRIBUTOR` protocol messages.

## Important APIs, Types, And Functions
The header defines `ITEM_SIZE` as `sizeof(struct distr_item)` and `struct distr_item`, whose network-byte-order fields are `type`, `lower`, `upper`, `port`, and `key`. Public prototypes are `tipc_named_publish()`, `tipc_named_withdraw()`, `tipc_named_node_up()`, `tipc_named_rcv()`, `tipc_named_reinit()`, and `tipc_publ_notify()`.

## Control Flow
The header itself has no executable flow. Callers publish or withdraw a local `struct publication`, pass the returned skb to broadcast/replicast as needed, invoke `tipc_named_node_up()` when a peer link becomes reachable, feed queued received distributor messages through `tipc_named_rcv()`, and call `tipc_publ_notify()` when a peer is lost.

## State And Persistence
No state is allocated by the header. The persistent state it describes is encoded as `distr_item` records inside `NAME_DISTRIBUTOR` message payloads. The comments explicitly define that all fields are network byte order and that the publishing node is not stored per item because it is inferred from the enclosing message.

## Dependencies And Integration Points
The header includes `name_table.h` for `struct publication` and publication-related types. It is included by `name_distr.c`, `name_table.c`, `net.c`, and `node.c`, tying together socket publication changes, node up/down events, and receive-side name table updates.

## Risks And Edge Cases
Any layout or byte-order change is wire-protocol visible. Because node identity is implicit in the containing message, callers must not process a `distr_item` without a validated `msg_orignode()`. `ITEM_SIZE` is used for MTU packing and receive item counts, so padding or struct layout changes would affect compatibility.

## Test Signals
Compile-time ABI checks, publication encode/decode tests, mixed-endian interoperability, MTU packing tests using `ITEM_SIZE`, receive validation of item counts, and compatibility tests with legacy and non-legacy name distribution all exercise this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/name_distr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/name_table.c -->
# sources/distributed-fs/ceph-client/net/tipc/name_table.c

## Purpose
`name_table.c` implements TIPC service name publication storage, service-range lookup, subscription notification, multicast/group destination expansion, local publish/withdraw orchestration, netlink dumping of publications, and helper lists of destination socket/node pairs. It is the authoritative runtime table mapping service types/ranges to publishing sockets.

## Important APIs, Types, And Functions
Internal structures are `struct service_range`, an augmented RB-tree node keyed by lower/upper instance ranges with `max` for overlap search, and `struct tipc_service`, a hash-bucket entry for one service type with its range tree, subscriptions, publication counter, and spinlock. Important exported functions include `tipc_nametbl_lookup_anycast()`, `tipc_nametbl_lookup_group()`, `tipc_nametbl_lookup_mcast_sockets()`, `tipc_nametbl_lookup_mcast_nodes()`, `tipc_nametbl_build_group()`, `tipc_nametbl_publish()`, `tipc_nametbl_withdraw()`, `tipc_nametbl_insert_publ()`, `tipc_nametbl_remove_publ()`, `tipc_nametbl_subscribe()`, `tipc_nametbl_unsubscribe()`, `tipc_nametbl_init()`, `tipc_nametbl_stop()`, `tipc_nl_name_table_dump()`, and the `tipc_dest_*()` list helpers.

## Control Flow
Insertion allocates a `publication`, finds or creates the hash-bucket `tipc_service`, creates or finds an exact `service_range`, rejects duplicate key/socket/node publications, links local publications into `local_publ`, links all publications into `all_publ`, assigns a monotonic id, and reports `TIPC_PUBLISHED` to overlapping subscriptions. Removal finds the service and exact range, unlinks the publication, reports `TIPC_WITHDRAWN`, erases the range if empty, and deletes the service when it has neither ranges nor subscriptions.

Anycast lookup first checks whether a remote lookup should be deferred by scope. It then searches overlapping ranges for the requested instance and chooses local-only, legacy closest-first, or round-robin `all_publ` selection, moving the selected publication to the tail. Multicast and group lookup functions walk matching ranges to build destination lists, local socket lists, node lists, or communication-group members. Subscribe creates the service if needed, attaches a subscription, optionally reports existing matching publications in publication-id order, and holds a reference until unsubscribe.

`tipc_nametbl_publish()` enforces `TIPC_MAX_PUBL`, inserts the publication, delegates distribution message creation to `name_distr.c`, and broadcasts the returned skb after dropping the table lock. Withdraw mirrors this flow and frees the publication with RCU. Netlink dumping walks hash buckets, services, ranges, and publication lists with callback cursor state for service type, lower bound, key, and done status.

## State And Persistence
Persistent state is the per-net `struct name_table`: hash buckets, node/cluster scope publication lists, cluster-scope rwlock, local publication count, replicast destination count, and outgoing name-distribution sequence. Each `tipc_service` owns its RB tree and subscription list. Each `publication` is linked simultaneously into socket, node/scope, local-publication, all-publication, and temporary reporting lists, with RCU lifetime.

## Dependencies And Integration Points
The file depends on `netlink.h`, `name_distr.h`, subscription reporting, broadcast distribution, address/scope helpers, node subscription cleanup, and group membership construction. Socket bind/unbind paths publish and withdraw here; `msg.c` uses anycast lookup for named-message rerouting; broadcast and group code use multicast/group lookup helpers; legacy and modern netlink paths use the dump API.

## Risks And Edge Cases
The locking hierarchy combines the global per-net `nametbl_lock`, per-service spinlocks, RCU traversal, and the cluster-scope lock in `name_distr.c`; lock-order regressions can deadlock. Publication objects live on many lists, so partial unlinking can corrupt later cleanup. Overlap search depends on correct augmented RB-tree `max` maintenance. Round-robin list movement mutates lookup state. Netlink dump cursors can become stale if publications are removed mid-dump, and the code signals interrupted dumps via `prev_seq`.

## Test Signals
Tests should cover exact and overlapping ranges, duplicate publication rejection, max-publication enforcement, local/node/cluster scope semantics, anycast local-first/round-robin/legacy behavior, multicast socket and node expansion, group member construction, subscription initial reports and withdrawal reports, service/range deletion, netlink dump pagination under concurrent updates, destination list duplicate suppression, and lockdep/RCU/KASAN during bind/unbind/node-failure races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/name_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/name_table.h -->
# sources/distributed-fs/ceph-client/net/tipc/name_table.h

## Purpose
`name_table.h` exposes the TIPC name table data structures and lookup/publish/subscribe API to sockets, message rerouting, name distribution, groups, broadcast, node cleanup, and netlink dump code.

## Important APIs, Types, And Functions
Key constants include `TIPC_ZM_SRV`, `TIPC_PUBL_SCOPE_NUM`, `TIPC_NAMETBL_SIZE`, and `TIPC_ANY_SCOPE`. `struct publication` records the service range, publishing socket address, scope, key, id, several list memberships, and RCU callback. `struct name_table` records service hash buckets, local node-scope and cluster-scope publication lists, locks, local publication count, replicast destination count, and sequence number. `struct tipc_dest` is a small node/port destination list item. The header declares the lookup, multicast, group-build, publish/withdraw, insert/remove, subscribe/unsubscribe, init/stop, netlink dump, and destination-list helper functions.

## Control Flow
The header has no direct control flow, but it defines how callers interact with the name table: bind paths publish, unbind paths withdraw, receive/reroute paths query anycast or multicast destinations, group creation builds members from publications, node failure removes remote publications, subscriptions attach to service types, and netlink dumps enumerate the table.

## State And Persistence
The persistent objects described here are per-net and RCU-managed. Publications may be reachable from socket binding lists, node cleanup lists, scope distribution lists, local/all publication lists, and temporary notification lists. The name table itself is stored under `tipc_net(net)->nametbl` and freed through RCU during namespace teardown.

## Dependencies And Integration Points
The header forward-declares subscription, plist/nlist, group, and user-address types to keep dependencies light. It is included by `name_table.c`, `name_distr.c`, `msg.c`, `netlink.c`, `netlink_compat.c`, `net.c`, and group/socket/broadcast code. Its constants and struct layout are shared with distribution and cleanup paths.

## Risks And Edge Cases
Because `struct publication` participates in many lists, every user must understand which list head it owns and when RCU freeing is safe. `TIPC_NAMETBL_SIZE` must remain a power of two for the hash function. Scope constants affect lookup semantics across legacy and non-legacy address modes. Destination list helpers allocate with atomic GFP in hot paths and can silently fail, so callers must handle incomplete destination sets.

## Test Signals
Compile-time coverage for all users, publication lifetime tests, socket bind/unbind cleanup, remote node purge, destination-list add/pop/delete duplicate behavior, scope matching, hash distribution, and RCU/list debug checks validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/name_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/net.c -->
# sources/distributed-fs/ceph-client/net/tipc/net.c

## Purpose
`net.c` manages TIPC network identity and network-mode lifecycle for a namespace. It initializes node identity or legacy node address, finalizes the node address, reinitializes dependent subsystems after address assignment, stops bearers/nodes on exit from network mode, and implements modern netlink get/set operations for network id, node id, legacy address, and legacy-address status.

## Important APIs, Types, And Functions
The exported functions are `tipc_net_init()`, `tipc_net_finalize_work()`, `tipc_net_stop()`, `tipc_nl_net_dump()`, `__tipc_nl_net_set()`, `tipc_nl_net_set()`, and `tipc_nl_net_addr_legacy_get()`. Internal helpers are `tipc_net_finalize()`, `__tipc_nl_add_net()`, and `__tipc_nl_addr_legacy_get()`.

## Control Flow
Initialization rejects a second configured node identity, logs entry into network mode, stores a supplied 128-bit node id, and optionally finalizes a supplied 32-bit legacy address. Finalization uses `cmpxchg()` to set `tipc_net.node_addr` only once, updates the node address, reinitializes local name publications, sockets, and self-monitor state, then publishes the node-state service for the new address. Deferred finalization runs under RTNL from work queued by address trial/discovery code.

Stopping checks whether an identity exists, then under RTNL stops bearers and all nodes before logging that network mode was left. Netlink dump emits the namespace `net_id` and two 64-bit halves of the 128-bit node id. Netlink set requires a nested `TIPC_NLA_NET`, rejects changes after a node address exists, validates net id range 1..9999, supports legacy address assignment through `TIPC_NLA_NET_ADDR`, and supports node-id assignment only when both halves are present.

## State And Persistence
State lives in `struct tipc_net`: node id, node address, trial address, net id, legacy address flag, broadcast link pointer, work item, and subsystem state reinitialized by finalization. The code publishes a `TIPC_NODE_STATE` service binding as persistent visible state once an address is finalized.

## Dependencies And Integration Points
The file depends on name distribution/table reinitialization, socket reinitialization, node and bearer shutdown, broadcast/link state, monitor self state, and generic netlink helpers. It is called by netlink configuration, discovery/address trial logic, namespace lifecycle, and the legacy netlink compatibility layer.

## Risks And Edge Cases
Identity and address are intended to be one-time configuration values; allowing changes after joining a network would invalidate publications, sockets, links, monitors, and peer state. `tipc_net_finalize()` is guarded with `cmpxchg()` to avoid double finalization from concurrent work paths. The netlink dump treats the node id as two `u64` words, so alignment and endian expectations matter for user space. Legacy address mode changes lookup semantics elsewhere in the name table.

## Test Signals
Tests should cover setting net id before and after join, invalid net ids, legacy address assignment, 128-bit node-id assignment with missing second half, duplicate initialization rejection, deferred finalization under RTNL, publication of `TIPC_NODE_STATE`, network stop teardown order, netlink dump/reply fields, and legacy-address get behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/net.h -->
# sources/distributed-fs/ceph-client/net/tipc/net.h

## Purpose
`net.h` declares the TIPC network identity/lifecycle API and the netlink policy used to configure it. It is the small public contract for `net.c`.

## Important APIs, Types, And Functions
The header includes generic netlink definitions, exports `tipc_nl_net_policy[]`, and declares `tipc_net_init()`, `tipc_net_finalize_work()`, `tipc_net_stop()`, `tipc_nl_net_dump()`, `tipc_nl_net_set()`, `__tipc_nl_net_set()`, and `tipc_nl_net_addr_legacy_get()`.

## Control Flow
There is no executable flow in the header. Callers use `tipc_net_init()` to set node identity/address, `tipc_net_finalize_work()` as a workqueue callback for deferred address finalization, `tipc_net_stop()` for namespace shutdown, and the netlink functions as generic-netlink command handlers or compatibility-layer targets.

## State And Persistence
The header owns no storage. It exposes functions that mutate per-net `struct tipc_net` identity fields, legacy-address mode, and network-mode subsystem state.

## Dependencies And Integration Points
It is included by `net.c`, `node.c`, `netlink.c`, `netlink_compat.c`, and other TIPC modules that need lifecycle or configuration entry points. `__tipc_nl_net_set()` is intentionally exported for the legacy compatibility layer, while `tipc_nl_net_set()` wraps it in RTNL locking for normal netlink operation.

## Risks And Edge Cases
The split between locked and unlocked netlink setters is easy to misuse; callers of the double-underscore form must provide required serialization. Policy declarations must stay aligned with `netlink.c` and user-visible TIPC attributes. Network identity changes have broad side effects and should remain centralized in `net.c`.

## Test Signals
Compile coverage for all netlink handlers, lockdep checks around compatibility calls to `__tipc_nl_net_set()`, and netlink API tests for get/set/legacy status validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/netlink.c -->
# sources/distributed-fs/ceph-client/net/tipc/netlink.c

## Purpose
`netlink.c` registers the modern TIPC generic netlink family, defines the top-level and nested attribute policies, and maps each TIPC netlink command to its subsystem handler. It is the central user-space configuration and dump surface for bearers, sockets, publications, links, media, nodes, network identity, name tables, monitors, peer removal, optional UDP media, and optional crypto keys.

## Important APIs, Types, And Functions
The file defines `tipc_nl_policy[]` and exported nested policies including `tipc_nl_name_table_policy`, `tipc_nl_monitor_policy`, `tipc_nl_sock_policy`, `tipc_nl_net_policy`, `tipc_nl_link_policy`, `tipc_nl_node_policy`, `tipc_nl_prop_policy`, `tipc_nl_bearer_policy`, `tipc_nl_media_policy`, and `tipc_nl_udp_policy`. It defines the `tipc_genl_v2_ops[]` command table, the exported `tipc_genl_family`, and lifecycle functions `tipc_netlink_start()` and `tipc_netlink_stop()`.

## Control Flow
Module startup calls `tipc_netlink_start()`, which registers `tipc_genl_family`. User commands arrive through generic netlink, are validated according to the family policy and per-op relaxed validation flags, and dispatch to the corresponding subsystem handler. Dump commands use handlers such as `tipc_nl_bearer_dump()`, `tipc_nl_sk_dump()`, `tipc_nl_node_dump()`, `tipc_nl_net_dump()`, and `tipc_nl_name_table_dump()`. Shutdown unregisters the family.

## State And Persistence
The main persistent object is `tipc_genl_family`, marked `__ro_after_init`, with family name/version, max attribute, policy pointer, namespace support, module owner, operation table, and reserved operation start. Attribute policy arrays are global const state used by both modern netlink and compatibility transcoding.

## Dependencies And Integration Points
The file includes and dispatches into `socket`, `name_table`, `bearer`, `link`, `node`, `net`, and optionally `udp_media` and crypto functionality. `netlink.h` exposes the family and policies. `netlink_compat.c` uses the same policies and subsystem handlers to translate legacy TLV commands into modern nested attributes.

## Risks And Edge Cases
The operation table is user-space ABI. Adding, removing, or reassigning commands can break `tipc` tooling and the legacy compatibility layer. Many ops use `GENL_DONT_VALIDATE_STRICT` to preserve older behavior, so individual handlers must validate required nested attributes. Policy lengths for names, node IDs, and keys are security boundaries. Conditional UDP/crypto operations must compile and reserve consistent command space across configs.

## Test Signals
Generic netlink registration failure injection, `tipc` command-line get/set coverage for every op, malformed attribute fuzzing, namespace isolation, dump pagination, conditional builds with UDP media and crypto enabled/disabled, legacy compatibility command parity, and ABI regression tests for family name/version/commands validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/netlink.h -->
# sources/distributed-fs/ceph-client/net/tipc/netlink.h

## Purpose
`netlink.h` declares the shared TIPC generic netlink family, a small message-building context, nested attribute policy arrays, and lifecycle functions for modern and legacy netlink registration.

## Important APIs, Types, And Functions
The header exports `struct genl_family tipc_genl_family`, defines `struct tipc_nl_msg` with `skb`, `portid`, and `seq`, declares policy arrays for name table, socket, network, link, node, properties, bearer, media, UDP, and monitor attributes, and declares `tipc_netlink_start()`, `tipc_netlink_compat_start()`, `tipc_netlink_stop()`, and `tipc_netlink_compat_stop()`.

## Control Flow
The header has no executable flow. Subsystem dump helpers receive `struct tipc_nl_msg` to emit generic-netlink replies with the correct sender port and sequence. Module init/exit code calls the start/stop functions for both modern and compatibility families.

## State And Persistence
The header owns no storage beyond declarations. It describes global netlink registration state and immutable policy arrays defined in `netlink.c`, plus the transient `tipc_nl_msg` context used while constructing replies.

## Dependencies And Integration Points
It includes `<net/netlink.h>` and is included by netlink handlers across bearer, media, node, net, name table, socket, and compatibility code. Keeping policies declared here lets compatibility translation reuse the modern validation contract.

## Risks And Edge Cases
Any policy declaration mismatch with definitions in `netlink.c` causes compile or ABI errors. `tipc_nl_msg` assumes callers set all fields before nested `nla_put()`/`genlmsg_put()` operations. Start/stop ordering matters because compatibility code references the modern family id and policies.

## Test Signals
Build tests across optional TIPC configs, generic netlink family registration/unregistration tests, dump helper tests that verify `portid` and `seq` propagation, and malformed-attribute validation through declared policy arrays exercise this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/netlink_compat.c -->
# sources/distributed-fs/ceph-client/net/tipc/netlink_compat.c

## Purpose
`netlink_compat.c` implements the legacy `TIPC_GENL_NAME` TLV-based configuration ABI on top of the modern nested generic-netlink handlers. It allocates legacy TLV replies, translates legacy request structures into modern attributes for mutating commands, runs modern dump handlers and formats their nested attributes back into legacy TLV or text output, and registers/unregisters a separate compatibility generic-netlink family.

## Important APIs, Types, And Functions
Key structures are `struct tipc_nl_compat_msg`, `struct tipc_nl_compat_cmd_dump`, and `struct tipc_nl_compat_cmd_doit`. Core helpers include `tipc_skb_tailroom()`, `tipc_add_tlv()`, `tipc_tlv_init()`, `tipc_tlv_sprintf()`, `tipc_tlv_alloc()`, `tipc_get_err_tlv()`, `tipc_nl_compat_dumpit()`, `__tipc_nl_compat_dumpit()`, `tipc_nl_compat_doit()`, and `__tipc_nl_compat_doit()`. Command-specific translation/formatting covers bearer names/enable/disable, link stats and properties, media/bearer/link property set, name-table display, socket/port display, media names, node list, net id/address get/set, and show-stats. The exported lifecycle functions are `tipc_netlink_compat_start()` and `tipc_netlink_compat_stop()`.

## Control Flow
`tipc_nl_compat_recv()` parses the legacy command header, checks `CAP_NET_ADMIN` for mutating command ranges, validates the incoming TLV when present, dispatches through `tipc_nl_compat_handle()`, maps common errors to legacy error TLVs, prepends a generic-netlink header copied from the request, and unicasts the reply. Dump commands allocate a TLV reply, optionally write a text header, build a synthetic modern dump request, call the modern dump handler repeatedly with a fake `netlink_callback`, parse each emitted modern netlink message, and call a formatter to append TLV/text output. Doit commands allocate an attribute buffer, call a transcoder under RTNL to build modern nested attributes from the legacy TLV, parse attributes into `genl_info`, call the modern handler, and return an empty success TLV.

## State And Persistence
Compatibility state is transient per request in `tipc_nl_compat_msg`. Persistent global state is the `tipc_genl_compat_family` with one `TIPC_GENL_CMD` operation. Reply size is capped by the legacy `ULTRA_STRING_MAX_LEN`/`TIPC_SKB_MAX` behavior, and truncation is represented by appending a textual `<truncated>` marker when the legacy string buffer is full.

## Dependencies And Integration Points
The file depends on modern netlink policies and handlers from bearer, media, link, node, net, name table, and socket code. It uses legacy definitions from `<linux/tipc_config.h>`, string termination helpers, generic netlink dump helpers, and RTNL serialization for translated mutating operations. It is registered separately from `tipc_genl_family` but translates through that family's id, maxattr, and policy.

## Risks And Edge Cases
This is an ABI-preservation layer, so behavior must match old `tipc-config` expectations even when modern netlink semantics differ. String TLVs are manually length-checked and must be NUL-terminated before conversion. `tipc_tlv_sprintf()` writes directly into skb tailroom and relies on the legacy cap. Dump callbacks reuse attribute buffers and fake callback state; stale cursor or parse errors can truncate or interrupt output. Some formatting, such as link TX profile percentages, divides by modern stat counters and depends on handlers providing nonzero expected attributes.

## Test Signals
Legacy `tipc-config` command coverage, CAP_NET_ADMIN denial tests, malformed TLV type/length/string tests, bearer enable/disable translation, link property set/reset stats, name-table depth filters, port publication display, net id/address get/set, large dump truncation behavior, namespace-specific requests, modern/legacy parity tests, and registration/unregistration failure tests validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/netlink_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/node.c -->
# sources/distributed-fs/ceph-client/net/tipc/node.c

## Purpose
`node.c` manages TIPC peer-node objects and the unicast/broadcast links attached to each peer. It owns node creation, address conflict handling, peer capability aggregation, link up/down selection, failover/synchronization state machines, keepalive timers, local-container fast transmit, receive dispatch, broadcast/name-distribution delivery, connected-socket failure notification, peer removal, link/monitor/key netlink handlers, diagnostics, and namespace cleanup of peer references.

## Important APIs, Types, And Functions
The central private type is `struct tipc_node`, containing node address/id, kref/RCU/list/hash membership, active link slots, per-bearer `tipc_link_entry`, broadcast `tipc_bclink_entry`, action flags, FSM state, publication and connected-socket lists, timer, peer namespace pointer, capabilities, and optional crypto RX state. Important exported functions include `tipc_node_create()`, `tipc_node_try_addr()`, `tipc_node_check_dest()`, `tipc_node_xmit()`, `tipc_node_xmit_skb()`, `tipc_node_distr_xmit()`, `tipc_node_broadcast()`, `tipc_rcv()`, `tipc_node_stop()`, `tipc_node_delete_links()`, `tipc_node_apply_property()`, `tipc_node_subscribe()`, `tipc_node_unsubscribe()`, connection tracking helpers, MTU/id/capability accessors, many netlink handlers, `tipc_node_dump()`, and `tipc_node_pre_cleanup_net()`.

## Control Flow
Node creation is serialized by `node_list_lock`, finds existing nodes by address or 128-bit id, upgrades preliminary crypto/key nodes into real nodes, creates a broadcast receive link, inserts the node into hash and sorted lists, starts a keepalive timer, initializes crypto if enabled, recalculates cluster-wide capability intersection, and toggles broadcast replicast mode. Destination discovery calls `tipc_node_check_dest()`, which evaluates peer signature, media address, and link-up state across eight cases to decide whether to respond, accept a new media address, reset an existing link, or flag duplicate address risk. New unicast links are created with bearer properties and attached to the selected node.

Link-up handling establishes the link FSM, updates working link count, MTU, bearer destination counts, active link slots, monitor/name-table notifications, broadcast peer state, and optional tunnel synchronization when a second link appears. Link-down handling removes bearer destinations, selects replacement active links, resets and notifies full node loss when no links remain, or starts failover through the remaining active link. The node FSM tracks self/peer contact, peer leaving/coming states, failover, and synchronization.

Receive flow validates/decrypts skb data, dispatches discovery and broadcast packets specially, locates the sending node/link, updates broadcast ACK state, uses a fast path for fully up non-tunnel traffic, otherwise checks node state and tunnel/failover rules before passing packets to `tipc_link_rcv()`. It then processes link-up/down events, name distribution queues, multicast queues, socket input queues, and queued outbound state messages. Transmit selects loopback, local-container peer namespace delivery, or an active link by selector, then calls `tipc_link_xmit()` and bearer transmit.

## State And Persistence
Persistent per-net node state lives in `tipc_net.node_list` and `node_htable`, with RCU read access and kref lifetime. Each node stores per-bearer links, input queues, media addresses, link MTUs, active link slot selection, broadcast receive queues, name-distribution receive cursors, action flags deferred to unlock, connection/publication cleanup lists, keepalive interval/timer, peer capabilities, peer namespace/hash, and optional crypto state. Down nodes remain for `NODE_CLEANUP_AFTER` before timer-driven cleanup.

## Dependencies And Integration Points
The file integrates with link creation/state/data transfer, bearer destination management and transmit, broadcast reliable link handling, monitor peer events, discovery, name distribution, name table publication of link state, sockets and multicast receive, crypto key distribution/receive, tracing, generic netlink, net namespace iteration, and network identity helpers from `net.c`.

## Risks And Edge Cases
This is highly concurrency-sensitive: node list lock, node rwlock, per-link spinlocks, skb queue locks, RCU, timers, RTNL, and krefs all interact. Deferred action flags are executed after releasing the node lock to avoid calling monitor/name-table code while locked. Address conflict handling must distinguish peer reboot, interface address change, duplicate/malicious peer, and preliminary key-only nodes. Failover/synch state must prevent message reordering while not wedging active links. Local-container peer delivery depends on `check_net()` and clearing `peer_net` before namespace exit. Timer cleanup must not free a node with live references.

## Test Signals
High-value tests include peer discovery/reboot/address-conflict matrices, one-link and two-link establishment, priority-based active/standby selection, failover and synchronization under packet loss/reorder, node-loss socket error delivery, remote publication purge, broadcast ACK/NACK and name-distribution receive queues, local namespace/container fast delivery, bearer deletion, peer removal while down versus busy, link property netlink set/get/reset, monitor dump/set, crypto key set/flush builds, timer cleanup after prolonged down state, and lockdep/KASAN/RCU stress under concurrent receive/transmit/teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/node.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/node.h -->
# sources/distributed-fs/ceph-client/net/tipc/node.h

## Purpose
`node.h` exposes TIPC peer-node capability bits and the node/link management API used by bearer, discovery, link, broadcast, name distribution, socket, crypto, netlink, and namespace cleanup code.

## Important APIs, Types, And Functions
The header defines capability bits such as `TIPC_SYN_BIT`, `TIPC_BCAST_SYNCH`, `TIPC_BCAST_STATE_NACK`, `TIPC_BLOCK_FLOWCTL`, `TIPC_BCAST_RCAST`, `TIPC_NODE_ID128`, `TIPC_LINK_PROTO_SEQNO`, `TIPC_MCAST_RBCTL`, `TIPC_GAP_ACK_BLOCK`, `TIPC_TUNNEL_ENHANCED`, `TIPC_NAGLE`, and `TIPC_NAMED_BCAST`, then combines them as `TIPC_NODE_CAPABILITIES`. It declares node lifecycle, lookup/accessor, creation, address trial, discovery validation, link deletion/property/name lookup, transmit/broadcast, publication subscription, connection tracking, MTU/up/capability queries, netlink node/link/monitor/peer/key handlers, optional crypto accessors, and `tipc_node_pre_cleanup_net()`.

## Control Flow
The header has no executable flow. It defines how callers progress from discovery (`tipc_node_try_addr()`, `tipc_node_check_dest()`), to link establishment and data movement (`tipc_node_xmit*()`, `tipc_rcv()` through `node.c`), to cleanup (`tipc_node_delete_links()`, `tipc_node_stop()`, `tipc_node_pre_cleanup_net()`), and to user-space control through netlink handlers.

## State And Persistence
The private `struct tipc_node` is intentionally opaque here. Persistent state is managed in `node.c`, while this header exposes only references and APIs for obtaining IDs, addresses, capabilities, crypto handles, link names, and status.

## Dependencies And Integration Points
The header includes `addr.h`, `net.h`, `bearer.h`, and `msg.h`, reflecting that node logic sits between addressing/network identity, bearer media, and message/link protocol. Optional crypto declarations are gated by `CONFIG_TIPC_CRYPTO`. Netlink prototypes connect `node.c` to the operation table in `netlink.c`.

## Risks And Edge Cases
Capability bit definitions are wire-visible negotiation state; changing `TIPC_NODE_CAPABILITIES` affects cluster feature decisions such as broadcast mode, named broadcast, tunnel behavior, and gap ACK support. The API mixes reference-counted node pointers, RCU traversal assumptions, RTNL-locked netlink calls, and optional crypto pointers, so callers must respect locking/lifetime rules documented in implementations.

## Test Signals
Compile tests across crypto and non-crypto builds, capability negotiation tests with mixed-version peers, discovery/link setup tests, node transmit/receive API coverage, netlink operation table coverage, and namespace cleanup tests validate the exported contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/node.h -->

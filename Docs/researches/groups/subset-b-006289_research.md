# subset-b-006289 TIPC Crypto, Discovery, Media, Group, Link, and Monitor Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/crypto.c -->
# sources/distributed-fs/ceph-client/net/tipc/crypto.c

## Purpose

`crypto.c` implements TIPC packet confidentiality/integrity, key lifecycle, session-key distribution, and crypto diagnostics for `CONFIG_TIPC_CRYPTO`. It wraps TIPC v2 packets in the encrypted header defined by `crypto.h`, encrypts/decrypts them with AEAD `gcm(aes)`, manages per-net TX crypto state and per-peer RX crypto state, and coordinates cluster-key and per-node-key operation.

## Important APIs, Types, and Functions

The key internal objects are `struct tipc_key`, `struct tipc_tfm`, `struct tipc_aead`, `struct tipc_crypto_stats`, and `struct tipc_crypto`. `struct tipc_crypto` owns RCU-protected AEAD slots `aead[0..3]`, pending/active/passive key state, key generation, delayed work, per-CPU stats, per-peer TX sequence state, peer RX active-key tracking, and flags such as `working`, `key_master`, `legacy_user`, and `nokey`. Public entry points include `tipc_crypto_start()`, `tipc_crypto_stop()`, `tipc_crypto_timeout()`, `tipc_crypto_xmit()`, `tipc_crypto_rcv()`, `tipc_crypto_key_init()`, `tipc_crypto_key_flush()`, `tipc_crypto_key_distr()`, `tipc_crypto_msg_rcv()`, `tipc_crypto_rekeying_sched()`, `tipc_aead_key_validate()`, and `tipc_ehdr_validate()`.

AEAD helpers validate `gcm(aes)` keys, allocate one or more crypto transforms up to `sysctl_tipc_max_tfms`, rotate per-CPU transform selection, build IVs from salt plus sequence number, and handle synchronous or async crypto callbacks. Key helpers attach, flush, align, pick, clone, revoke, distribute, receive, and activate keys.

## Control Flow

Transmit starts in `tipc_crypto_xmit()`. If TX crypto is inactive the skb is left unchanged. Otherwise it selects a key in pending/master/active preference order, optionally clones probing or grace-period messages, builds `struct tipc_ehdr`, encrypts the original TIPC header and payload, and returns either an encrypted skb or async ownership. `tipc_aead_encrypt_done()` sends or frees the skb after async completion.

Receive starts in `tipc_crypto_rcv()`. It reads the encrypted header's TX key, finds a matching per-peer RX key, attempts RX key slot alignment when a peer rejoined with a shifted key index, or falls back to local TX cluster keys for bootstrap/decryption of unknown peers. `tipc_crypto_rcv_complete()` strips the encryption header and tag, validates the inner TIPC message, marks the skb decrypted, and calls `tipc_crypto_key_synch()` to update peer RX-active tracking and key-distribution needs.

Key distribution uses `MSG_CRYPTO/KEY_DISTR_MSG`. TX delayed work generates a fresh session key from the current template, attaches it as pending, distributes it via unicast or broadcast, and reschedules rekeying. RX delayed work sends a key to a peer that lacks one and attaches a received session key when possible.

## State and Persistence Behavior

State is in memory only: per-net TX crypto hangs off `tipc_net`, while per-peer RX crypto hangs off `tipc_node`. AEAD slots are RCU-protected and refcounted; key material is duplicated with sensitive allocation and freed with `kfree_sensitive()`. Key state persists across packets as pending/active/passive slots, generation counters, sequence counters, user counts, and timers. `tipc_crypto_timeout()` advances pending keys to active, retires passive keys, clears legacy grace state, and handles debug command dispatch through the `max_tfms` sysctl escape path.

## Dependencies and Integration Points

The file depends on Linux crypto AEAD/RNG APIs, skb scatter-gather helpers, RCU/refcounting, delayed workqueues, per-CPU stats, TIPC node/bearer/message helpers, broadcast transmit, and net namespace lifetime management. It integrates with link receive in `link.c` for `MSG_CRYPTO`, with netlink/sysctl configuration for keys and rekeying, with `tipc_node` for per-peer RX crypto, and with bearer media send callbacks for async encryption completion.

## Risks and Edge Cases

This is security-sensitive code. Risks include nonce reuse on sequence wrap, incorrect key slot activation, RCU/refcount lifetime mistakes, failure to clear sensitive key material, peer bootstrap using TX cluster-key fallback, and async completion racing bearer/net namespace teardown. The pending/active/passive state machine depends on user counts and jiffies thresholds; small ordering mistakes can keep dead keys alive or revoke live ones. `sysctl_tipc_max_tfms` has a dual role as TFM limit and debug command trigger above `TIPC_MAX_TFMS_LIM`, which is easy to misuse.

## Test Signals

Useful signals include builds with `CONFIG_TIPC_CRYPTO`, netlink key validation failures for wrong algorithm/key length, packet traces showing `MSG_CRYPTO` distribution and encrypted LINK_CONFIG/LINK_PROTOCOL traffic, per-CPU crypto stats printed by debug command `0xfff1`, rekey interval tests, peer restart tests that force key-slot alignment, and namespace teardown tests while async crypto operations are outstanding.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/crypto.h -->
# sources/distributed-fs/ceph-client/net/tipc/crypto.h

## Purpose

`crypto.h` declares the public TIPC crypto interface and the wire-format encryption header used by `crypto.c` and link/bearer paths. It is compiled only under `CONFIG_TIPC_CRYPTO`, so it defines the contract for encrypted TIPC packets without burdening non-crypto builds.

## Important APIs, Types, and Functions

The header defines encryption version `TIPC_EVERSION`, AES-GCM key/salt/IV/tag sizes, crypto modes `CLUSTER_KEY` and `PER_NODE_KEY`, and the exported sysctls `sysctl_tipc_max_tfms` and `sysctl_tipc_key_exchange_enabled`. The central type is packed `struct tipc_ehdr`, whose first word carries version, user, destination-known bit, TX key, peer RX-active key, keepalive, master-key, and no-RX-key indications. It also stores a 64-bit sequence number and either a node address or 128-bit node ID for LINK_CONFIG.

Public prototypes cover crypto object lifecycle, timeouts, transmit/receive, key initialization/flushing/distribution, MSG_CRYPTO receive, rekey scheduling, user-key validation, and encrypted-header validation. Inline helpers `msg_key_gen()`, `msg_set_key_gen()`, `msg_key_mode()`, and `msg_set_key_mode()` reserve bits in message word 4 for key distribution metadata.

## Control Flow

Callers use this header by creating TX/RX crypto objects with `tipc_crypto_start()`, feeding outgoing skbs through `tipc_crypto_xmit()`, validating encrypted headers with `tipc_ehdr_validate()`, and decrypting inbound skbs through `tipc_crypto_rcv()`. Key-management control flows through `tipc_crypto_key_init()`, `tipc_crypto_key_distr()`, `tipc_crypto_msg_rcv()`, and `tipc_crypto_rekeying_sched()`.

## State and Persistence Behavior

The header itself has no storage other than external sysctl declarations. It defines persistent on-wire state encoded in `struct tipc_ehdr`: key index, sequence number, peer key status, and source address or node ID. Header sizes `EHDR_SIZE`, `EHDR_CFG_SIZE`, and `EMSG_OVERHEAD` are used to size skb headroom/tailroom and link MSS calculations.

## Dependencies and Integration Points

It includes `core.h`, `node.h`, `msg.h`, and `bearer.h`, tying crypto to TIPC message layout, node identity, and media bearer abstractions. `link.c` uses `EMSG_OVERHEAD` to reduce MSS when crypto is enabled and dispatches decrypted `MSG_CRYPTO` messages. Netlink and sysctl code use validation and rekey/key APIs declared here.

## Risks and Edge Cases

The packed bitfield layout is endian-sensitive and part of the wire protocol. Any change to bit positions, header sizing, or `TIPC_EVERSION` handling affects interoperability. `EMSG_OVERHEAD` must stay aligned with the actual encryption tag and header size or link fragmentation and MTU checks become wrong.

## Test Signals

Build both little-endian and big-endian configurations if available, compile with and without `CONFIG_TIPC_CRYPTO`, verify encrypted packet sizes against `EHDR_*` constants, and exercise key distribution metadata through `MSG_CRYPTO/KEY_DISTR_MSG` packet captures.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/diag.c -->
# sources/distributed-fs/ceph-client/net/tipc/diag.c

## Purpose

`diag.c` implements the SOCK_DIAG handler for TIPC sockets. It lets userspace request AF_TIPC socket diagnostic dumps through `NETLINK_SOCK_DIAG`, producing per-socket information via the existing TIPC socket diag filler.

## Important APIs, Types, and Functions

`__tipc_diag_gen_cookie()` converts the generic socket diag cookie into a `u64` for TIPC reporting. `__tipc_add_sock_diag()` creates a netlink answer message and delegates body population to `tipc_sk_fill_sock_diag()`. `tipc_diag_dump()` walks sockets through `tipc_nl_sk_walk()`. `tipc_sock_diag_handler_dump()` validates request size and starts a netlink dump using `tipc_dump_start`, `tipc_diag_dump`, and `tipc_dump_done`. Module init/exit register and unregister `tipc_sock_diag_handler`.

## Control Flow

Userspace sends a `tipc_sock_diag_req`. The handler rejects undersized requests and supports only dump requests (`NLM_F_DUMP`). The generic netlink dump framework then repeatedly calls `tipc_diag_dump()`, which walks TIPC sockets and calls `__tipc_add_sock_diag()` for each matching socket. Each result is a multipart `SOCK_DIAG_BY_FAMILY` response.

## State and Persistence Behavior

The module maintains no persistent per-socket state. It registers one static `sock_diag_handler` for `AF_TIPC` and reads socket state while walking. The cookie is derived from the socket's saved diag cookie and is stable enough for diag consumers within normal socket lifetime constraints.

## Dependencies and Integration Points

The file depends on `core.h`, `socket.h`, Linux `sock_diag`, and `linux/tipc_sockets_diag.h`. It integrates with TIPC socket walking/filling helpers and the global SOCK_DIAG registry. The module metadata exposes a netlink alias for AF_TIPC diagnostic support.

## Risks and Edge Cases

The main risks are netlink sizing and dump iteration correctness. `nlmsg_put_answer()` or `tipc_sk_fill_sock_diag()` failures must return `-EMSGSIZE` or the underlying error so dump replay can continue correctly. Only dump mode is supported; point queries return `-EOPNOTSUPP`.

## Test Signals

Run `ss` or a SOCK_DIAG client against AF_TIPC sockets, including many sockets to force multipart dumps. Validate short request rejection, module load/unload registration, and group socket diagnostics when `group.c` contributes nested group attributes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/discover.c -->
# sources/distributed-fs/ceph-client/net/tipc/discover.c

## Purpose

`discover.c` drives TIPC bearer peer discovery and link setup request/response exchange. It periodically sends discovery messages on a bearer, performs initial node-address uniqueness trials when the local node has no assigned address, validates incoming discovery traffic, detects duplicate node addresses, and asks `node.c` to create or check peer destinations.

## Important APIs, Types, and Functions

`struct tipc_discoverer` stores bearer identity, destination media address, net namespace, discovery domain, discovered-node count, a reusable discovery skb, timer interval, timer, and spinlock. Public functions are `tipc_disc_create()`, `tipc_disc_delete()`, `tipc_disc_reset()`, `tipc_disc_add_dest()`, `tipc_disc_remove_dest()`, and `tipc_disc_rcv()`. Internal helpers build discovery messages (`tipc_disc_init_msg()`), transmit one-shot messages (`tipc_disc_msg_xmit()`), report duplicate addresses, handle trial address messages, and run the periodic timer.

## Control Flow

Creation allocates the discoverer and reusable request skb, initializes it as `DSC_REQ_MSG`, optionally changes it to `DSC_TRIAL_MSG` for a one-second address trial, starts the timer at `TIPC_DISC_INIT`, attaches the discoverer to the bearer, and returns an initial clone. Timer expiry doubles the interval until fast or slow limits depending on whether links exist, stops when a specific destination node is found, handles trial-period exit by scheduling `tipc_net` work, clones the reusable skb, and transmits it through the bearer.

Receive linearizes the skb, extracts peer capabilities, node ID, suggested address, node signature, network ID, media address, and message type. It rejects corrupt/broadcast media addresses, own-media messages, wrong net IDs, trial-only messages, duplicate own address usage, and out-of-domain peers. Valid candidates are passed to `tipc_node_check_dest()`, which decides whether to respond and whether a duplicate alert is needed. Discovery requests that require a response produce `DSC_RESP_MSG`.

## State and Persistence Behavior

The discoverer persists per bearer while discovery is active. Its reusable skb is mutated for trial and normal phases, `num_nodes` tracks active destinations, and `timer_intv` backs off or resets. Per-net address trial state lives in `tipc_net`: `trial_addr`, `addr_trial_end`, `random`, `net_id`, and legacy address format flags. No state is written to disk.

## Dependencies and Integration Points

The file depends on TIPC core, node, bearer/media address conversion, timers, skbs, and domain helpers. It integrates directly with media adapters via `b->media->addr2msg()` and `msg2addr()`, with bearer transmit via `tipc_bearer_xmit_skb()`, with node identity/address assignment via `tipc_node_try_addr()` and `tipc_node_check_dest()`, and with net work scheduling when a trial address becomes usable.

## Risks and Edge Cases

Discovery is exposed to untrusted LAN/bearer traffic. It must reject malformed media addresses, wrong net IDs, self-originated messages, and duplicate node addresses. Timer and lock ordering matters because delete shuts down the timer while bearer teardown may race receive/reset. Address trial handling is subtle: accepting normal link setup before trial end risks duplicate addresses; failing to switch from trial to request can stall cluster formation.

## Test Signals

Exercise bearer enable/disable, peer appearance/removal, duplicate address injection, network ID mismatch, trial fail messages with new suggestions, and discovery reset after bearer reconfiguration. Packet traces should show `DSC_TRIAL_MSG`, `DSC_TRIAL_FAIL_MSG`, `DSC_REQ_MSG`, and `DSC_RESP_MSG` transitions and interval backoff.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/discover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/discover.h -->
# sources/distributed-fs/ceph-client/net/tipc/discover.h

## Purpose

`discover.h` exposes the small discovery subsystem contract to bearer and node management code. It keeps `struct tipc_discoverer` opaque and declares lifecycle, destination-count, reset, and receive entry points for link setup discovery.

## Important APIs, Types, and Functions

The header forward-declares `struct tipc_discoverer`. `tipc_disc_create()` initializes per-bearer discovery and returns an initial discovery skb. `tipc_disc_delete()` tears it down. `tipc_disc_reset()` reinitializes the reusable request after bearer changes. `tipc_disc_add_dest()` and `tipc_disc_remove_dest()` update discovered peer count for timer behavior. `tipc_disc_rcv()` is the inbound discovery message handler.

## Control Flow

Bearer activation calls create, then later passes inbound LINK_CONFIG discovery skbs to `tipc_disc_rcv()`. Link/node up/down paths call add/remove destination to adjust discovery polling. Bearer reset calls `tipc_disc_reset()` to rebuild request metadata, and bearer teardown calls delete.

## State and Persistence Behavior

The header owns no state but enforces opacity of the discoverer internals. Persistent runtime state lives in `discover.c` and `struct tipc_bearer->disc`.

## Dependencies and Integration Points

The declarations integrate with `struct net`, `struct tipc_bearer`, `struct tipc_media_addr`, and `struct sk_buff` users without including their full definitions here. It is included by bearer/node setup code and `discover.c`.

## Risks and Edge Cases

Because the type is opaque, callers must respect lifecycle ordering: no receive/reset/add/remove calls after delete and no delete while uncoordinated timer or bearer users still reference the object. API misuse would become use-after-free in `discover.c`.

## Test Signals

Compile coverage should catch declaration drift. Runtime signals are bearer enable/delete cycles, discovery reset after media changes, and correct timer behavior when destination count moves between zero and nonzero.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/discover.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/eth_media.c -->
# sources/distributed-fs/ceph-client/net/tipc/eth_media.c

## Purpose

`eth_media.c` registers the Ethernet media adapter for TIPC bearers. It converts Ethernet MAC addresses between TIPC media-address structures, discovery message payloads, raw L2 addresses, and printable strings, and supplies default link properties for Ethernet bearers.

## Important APIs, Types, and Functions

Internal functions are `tipc_eth_addr2str()`, `tipc_eth_addr2msg()`, `tipc_eth_raw2addr()`, and `tipc_eth_msg2addr()`. The exported object is `struct tipc_media eth_media_info`, which binds these converters to common L2 send/enable/disable helpers and sets priority, tolerance, window bounds, media type, hardware address length, and name `"eth"`.

## Control Flow

Bearer/media registration consumes `eth_media_info`. When discovery is sent, `addr2msg()` writes media type plus MAC address into the TIPC media info area. When discovery is received, `msg2addr()` skips the discovery preamble and calls `raw2addr()`. Raw address conversion stores the MAC, sets `TIPC_MEDIA_TYPE_ETH`, and marks broadcast via `is_broadcast_ether_addr()`. Printable diagnostics use `%pM`.

## State and Persistence Behavior

The file has no mutable persistent state. `eth_media_info` is static global registration data. Runtime address state is carried in `struct tipc_media_addr` and bearers.

## Dependencies and Integration Points

It depends on TIPC bearer abstractions and Ethernet address helpers. It integrates with generic L2 bearer operations `tipc_l2_send_msg()`, `tipc_enable_l2_media()`, and `tipc_disable_l2_media()`, plus discovery code that serializes/deserializes media addresses.

## Risks and Edge Cases

The string buffer must be at least 18 bytes. Discovery format correctness depends on writing `TIPC_MEDIA_TYPE_ETH` at the media type offset and copying exactly `ETH_ALEN` bytes at the address offset. Broadcast detection controls rejection/handling of discovery messages and bearer destination behavior.

## Test Signals

Enable an Ethernet bearer, inspect discovery packets for media type and MAC placement, verify broadcast media address detection, check `tipc media`/link diagnostics for printable MACs, and compile with Ethernet/L2 bearer support.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/eth_media.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/group.c -->
# sources/distributed-fs/ceph-client/net/tipc/group.c

## Purpose

`group.c` implements TIPC socket group membership, group unicast/multicast/broadcast filtering, member events, receive-window flow control, broadcast sequence handling, and group diagnostics. It lets group sockets discover members through topology subscriptions, exchange group protocol messages, and prevent any one member from exhausting receive buffers.

## Important APIs, Types, and Functions

`struct tipc_member` tracks a member in an RB tree keyed by node/port, list membership for active/pending/small-window queues, deferred receive queue, state, advertised/window credits, and broadcast sequence/ack state. `struct tipc_group` owns member RB tree/lists, destination nlist, net/type/instance/scope/port metadata, member counts, active limits, broadcast send/ack state, and flags for loopback/events/open.

Public APIs include `tipc_group_create()`, `tipc_group_join()`, `tipc_group_delete()`, `tipc_group_add_member()`, `tipc_group_dests()`, `tipc_group_self()`, `tipc_group_exclude()`, `tipc_group_filter_msg()`, `tipc_group_member_evt()`, `tipc_group_proto_rcv()`, `tipc_group_update_bc_members()`, `tipc_group_cong()`, `tipc_group_bc_cong()`, `tipc_group_update_rcv_win()`, `tipc_group_bc_snd_nxt()`, `tipc_group_update_member()`, and `tipc_group_fill_sock_diag()`.

## Control Flow

Creation initializes lists/RB tree, destination list, flags, and a kernel topology subscription. Join sends `GRP_JOIN_MSG` to known members and initializes advertised windows. Topology publish/withdraw events flow through `tipc_group_member_evt()`, creating or retiring members and emitting optional user events. Group protocol messages flow through `tipc_group_proto_rcv()`, which handles joins, leaves, advertisements, broadcast ACKs, reclaim/remit exchange, and wakeup decisions.

Data receive enters `tipc_group_filter_msg()`. It validates group membership and sender state, sorts multicast/broadcast messages by group broadcast sequence into the member deferred queue, delivers in-order messages to the socket input queue, sends ACKs when requested, drops mismatched multicast instances, and updates receive windows. Send-side congestion checks use `tipc_group_cong()` and `tipc_group_bc_cong()` to compare requested length against member windows and to send extra advertisements when needed.

## State and Persistence Behavior

All state is per group socket and in memory. Member state transitions include joining, published, joined, pending, active, reclaiming, remitted, and leaving. The group maintains active receiver admission control using `max_active`, `active_cnt`, active/pending lists, and `ADV_IDLE`/`ADV_ACTIVE` windows. Broadcast persistence is sequence based: `bc_snd_nxt`, per-member `bc_rcv_nxt`, `bc_syncpt`, `bc_acked`, and group `bc_ackers`.

## Dependencies and Integration Points

The file depends on TIPC address, broadcast, topology server, socket, node, name table, subscription, message, skb queue, RB tree, and netlink attribute helpers. It integrates with socket send/receive paths for congestion and filtering, with topology server kernel subscriptions for membership, with `tipc_node_distr_xmit()` for protocol messages, and with socket diagnostics via `tipc_group_fill_sock_diag()`.

## Risks and Edge Cases

Ordering and flow control are the main risks. Broadcast/multicast messages can be bypassed by unicasts, so deferred sorting and sequence comparisons must be correct. Window arithmetic uses `u16` and credit blocks; underflow or stale advertisement can deadlock senders or overrun receivers. Reclaim/remit transitions are subtle under active-member churn. Member deletion must clean all lists and deferred queues and update `dests` only when the last member on a node leaves.

## Test Signals

Test group join/leave with and without loopback, node-scope versus cluster-scope groups, many members to trigger active/pending/reclaim logic, broadcast requiring ACKs, multicast instance mismatch, member withdraw while messages are deferred, and socket diag output for group attributes. Congestion tests should observe `open` flag transitions and SOCK_WAKEUP behavior in socket code.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/group.h -->
# sources/distributed-fs/ceph-client/net/tipc/group.h

## Purpose

`group.h` declares the socket-facing TIPC group API and keeps `struct tipc_group` and `struct tipc_member` opaque. It is the contract between group implementation, sockets, node distribution, and diagnostics.

## Important APIs, Types, and Functions

The header declares creation/join/delete, member addition, destination-list access, self service-range lookup, loopback exclusion, receive filtering, member event processing, protocol receive processing, broadcast member/window updates, unicast and broadcast congestion checks, receive-window updates, broadcast send sequence lookup, member credit update, and socket diag filling.

## Control Flow

Sockets create a group from `struct tipc_group_req`, join it after binding/publishing, call congestion helpers before sending, pass inbound data/protocol/member events to the relevant handlers, update broadcast member state after sends, and delete the group on socket teardown. Diagnostics call the fill helper when dumping a grouped socket.

## State and Persistence Behavior

The header has no storage, but its opaque pointers protect the per-socket group and member state owned by `group.c`. The `bool *group_is_open` pointer passed to create is intentionally shared back to socket state so flow-control changes can wake or block users.

## Dependencies and Integration Points

It includes `core.h` and references TIPC service ranges, group requests, skb queues, messages, net namespaces, and netlink/socket diag skb output. It is included by socket code and the group implementation.

## Risks and Edge Cases

The API assumes callers serialize access with the owning socket/node locks used by the TIPC stack. Passing null groups is tolerated by some implementation functions but not all helpers. The shared `group_is_open` pointer must outlive the group.

## Test Signals

Compile tests catch signature drift. Runtime coverage comes from grouped socket send/receive, member publish/withdraw events, congestion wakeups, and SOCK_DIAG dumps that include group fields.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/group.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/ib_media.c -->
# sources/distributed-fs/ceph-client/net/tipc/ib_media.c

## Purpose

`ib_media.c` registers the InfiniBand media adapter for TIPC bearers. It mirrors the Ethernet adapter pattern but uses InfiniBand hardware address size, broadcast comparison, formatting, and a smaller maximum link window.

## Important APIs, Types, and Functions

Internal converters are `tipc_ib_addr2str()`, `tipc_ib_addr2msg()`, `tipc_ib_raw2addr()`, and `tipc_ib_msg2addr()`. The exported `struct tipc_media ib_media_info` binds those converters to common L2 media send/enable/disable helpers and sets type `TIPC_MEDIA_TYPE_IB`, hardware address length `INFINIBAND_ALEN`, name `"ib"`, default priority/tolerance/window, and `TIPC_MAX_IB_LINK_WIN` as max window.

## Control Flow

Discovery and bearer code call `addr2msg()` to copy an InfiniBand address into the media info payload and `msg2addr()`/`raw2addr()` to build a `struct tipc_media_addr` from inbound data. `raw2addr()` marks broadcast by comparing the raw address with the bearer broadcast address. Diagnostics use `%20phC` formatting when the caller supplies at least 60 bytes.

## State and Persistence Behavior

The file has no mutable persistent state. Registration data is static, and runtime addresses are stored in bearer/media address objects.

## Dependencies and Integration Points

It depends on `<linux/if_infiniband.h>`, TIPC core, bearer abstractions, and common L2 media helpers. It integrates with discovery serialization and bearer media registration like the Ethernet media module.

## Risks and Edge Cases

Buffer sizing for printable addresses is larger than Ethernet. Discovery format differs from Ethernet because it copies from offset zero rather than setting the Ethernet media preamble fields; any shared discovery assumptions must account for media-specific conversion. Broadcast detection depends on a valid bearer broadcast address.

## Test Signals

Enable an InfiniBand TIPC bearer, verify address formatting, confirm discovery address round trips, test broadcast address detection, and ensure max window defaults differ from Ethernet as expected.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/ib_media.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/link.c -->
# sources/distributed-fs/ceph-client/net/tipc/link.c

## Purpose

`link.c` is the core TIPC link reliability layer. It creates unicast and broadcast links, runs the link finite-state machine, sequences outgoing packets, manages transmit/backlog/deferred queues, handles acknowledgements/NACKs/retransmission, fragments/reassembles input, supports failover/synchronization tunneling, exchanges link protocol state, integrates monitor domain records, and exports link netlink diagnostics.

## Important APIs, Types, and Functions

`struct tipc_link` is the main state object: peer/session/bearer identity, tolerance/abort limits, FSM state, capabilities, monitor state, MTU, transmit queue, backlog by importance, receive sequencing, input/name queues, wakeup queue, reassembly state, congestion window state, broadcast send/receive fields, failover queues, and `struct tipc_stats`. Public APIs include link creation, state predicates, reset, xmit/receive, timeout, state/reset message builders, failover/tunnel preparation, broadcast peer add/remove/sync/ack/nack helpers, property setters, netlink dump helpers, and `tipc_link_dump()`.

Key internal routines include `tipc_link_fsm_evt()`, `tipc_link_update_cwin()`, `tipc_link_advance_backlog()`, `tipc_link_advance_transmq()`, `tipc_link_proto_rcv()`, `tipc_link_build_proto_msg()`, `tipc_data_input()`, `tipc_link_input()`, and `tipc_link_tnl_rcv()`.

## Control Flow

Transmit starts in `tipc_link_xmit()`. It validates MTU, checks per-importance backlog limits, schedules SOCK_WAKEUP pseudo messages on congestion, assigns sequence/ACK/broadcast-ACK fields to packets that fit the congestion window, clones packets into the caller xmit queue, stores originals in `transmq`, and queues or bundles overflow into `backlogq`. ACK processing through data packets, STATE messages, or broadcast ACKs calls `tipc_link_advance_transmq()` to release acked packets and retransmit missing ranges, then updates congestion window and advances backlog.

Receive starts in `tipc_link_rcv()`. LINK_PROTOCOL packets go to `tipc_link_proto_rcv()`. Data packets reset silence counters, validate link state and receive window, release acked transmit packets, defer out-of-order packets with NACK generation, deliver in-order packets upward, and drain deferred packets when gaps close. `tipc_data_input()` routes normal data, connection manager, group protocol, name distributor, crypto, bundler, fragmenter, tunnel, and broadcast protocol users. Fragmented and bundled messages are unpacked before delivery.

Timeout builds RESET, ACTIVATE, or STATE/probe messages depending on FSM state, silence count, monitor probing, unacked receive data, broadcast ACK needs, and transmit queue pressure. Link protocol receive validates sessions and capabilities, handles RESET/ACTIVATE establishment, updates MTU/tolerance/priority, ingests monitor domain data, replies to probes, and processes gap ACK blocks.

## State and Persistence Behavior

All state is in memory per link. The FSM moves among RESETTING, RESET, PEER_RESET, FAILINGOVER, ESTABLISHING, ESTABLISHED, and SYNCHING. Sequence state persists in `snd_nxt`, `rcv_nxt`, state-message sequence numbers, broadcast acked/receive state, and failover drop points. Queue state persists in `transmq`, `backlogq`, `deferdq`, `wakeupq`, and reassembly buffers. Congestion state persists in `window`, `ssthresh`, `cong_acks`, `checkpoint`, and per-importance backlog limits.

## Dependencies and Integration Points

The file depends on TIPC core, subscriptions, broadcast, sockets, name distribution, discovery, netlink, monitor, trace, optional crypto, Linux skb and traffic priority helpers. It integrates with node code for locking and xmit scheduling, bearer code for packet transmission, group/socket receive queues, broadcast global locks, monitor domain gossip in STATE messages, crypto `MSG_CRYPTO` handling, and generic netlink link/stat reporting.

## Risks and Edge Cases

This is a dense reliability state machine. Risks include illegal FSM transitions, sequence wrap mistakes, retransmission storms, stale gap ACK block state, wakeup starvation, memory leaks in reassembly/failover queues, MTU mismatch during tunneling, and broadcast ACK/NACK storms. Broadcast sender and per-peer receiver links share state but have different semantics. Optional crypto reduces MSS; missing that adjustment causes oversize encrypted packets.

## Test Signals

Exercise link establishment/reset, silent peer timeout, priority/tolerance changes, congestion/backlog wakeups, fragmentation and bundling, out-of-order receive with NACK/retransmit, broadcast peer add/remove, gap ACK blocks with broadcast and unicast gaps, failover and synchronization tunneling, monitor threshold changes, crypto-enabled MSS, and netlink link/stat dumps.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/link.h -->
# sources/distributed-fs/ceph-client/net/tipc/link.h

## Purpose

`link.h` declares the public interface and constants for the TIPC link layer. It lets node, bearer, broadcast, netlink, monitor, and socket paths create links, drive their FSM, enqueue traffic, receive packets, manage broadcast synchronization, and inspect link properties without exposing `struct tipc_link` internals.

## Important APIs, Types, and Functions

The header defines `ELINKCONG`, external FSM event constants, receive/timeout return event bits, and `MAX_PKT_DEFAULT`. Prototypes cover unicast and broadcast link creation, tunnel/failover preparation, reset/state message generation, FSM events, state predicates, active flag, reset/stats reset, transmit/receive, queue accessors, sequence and identity accessors, property getters/setters, netlink property parsing and dump, timeout handling, broadcast peer management, MTU/MSS, gap ACK parsing, broadcast init/sync/ack/nack, silence checking, and namespace lookup.

## Control Flow

Node and bearer code create links, pass outbound skbs to `tipc_link_xmit()`, pass inbound skbs to `tipc_link_rcv()`, call `tipc_link_timeout()` from node timers, and react to returned event bits such as `TIPC_LINK_UP_EVT`, `TIPC_LINK_DOWN_EVT`, and `TIPC_LINK_SND_STATE`. Broadcast code uses the broadcast-specific helpers to synchronize send and receive links.

## State and Persistence Behavior

The header has no storage and keeps `struct tipc_link` opaque. Persistent runtime state is owned by `link.c`, while callers observe it through accessors such as `tipc_link_state()`, `tipc_link_rcv_nxt()`, `tipc_link_acked()`, `tipc_link_mtu()`, `tipc_link_prio()`, and `tipc_link_tolerance()`.

## Dependencies and Integration Points

It includes generic netlink plus TIPC `msg.h` and `node.h`. It is a central integration point for TIPC node management, broadcast, netlink control plane, bearer media setup, monitor, and socket data paths.

## Risks and Edge Cases

The event constants are magic values used for diagnostics and FSM dispatch; accidental changes break callers. Return event bits are combinable and must be handled as flags. Callers must hold the correct node/broadcast locks around mutable link operations because the opaque type does not enforce synchronization.

## Test Signals

Compile coverage catches API drift. Runtime signals include link up/down events from timeout and receive paths, netlink property parsing validation, broadcast helper behavior, and caller handling of `ELINKCONG` from `tipc_link_xmit()`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/link.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/monitor.c -->
# sources/distributed-fs/ceph-client/net/tipc/monitor.c

## Purpose

`monitor.c` implements TIPC's scalable peer monitoring. Instead of every node actively probing every peer in large clusters, it maintains a circular monitor list, assigns domain heads, exchanges compact domain records in link STATE messages, detects suspected lost members from peer reports, and tells links when to monitor, probe, or reset.

## Important APIs, Types, and Functions

`struct tipc_mon_domain` is the on-wire/local domain record containing length, generation, acknowledged generation, member count, up bitmap, and member addresses. `struct tipc_peer` tracks a peer's address, domain, hash/list links, applied domain count, down count, and role flags. `struct tipc_monitor` owns peer hash buckets, peer count, self peer, rwlock, cached outgoing domain record, list/domain generations, net namespace, and timer.

Public functions include `tipc_mon_create()`, `tipc_mon_delete()`, `tipc_mon_peer_up()`, `tipc_mon_peer_down()`, `tipc_mon_remove_peer()`, `tipc_mon_prep()`, `tipc_mon_rcv()`, `tipc_mon_get_state()`, `tipc_mon_reinit_self()`, and netlink threshold/dump helpers. Internal helpers handle endian conversion, domain sizing, peer lookup/list traversal, domain application, lost-member identification, local-domain updates, neighbor updates, and role assignment.

## Control Flow

Creation allocates a monitor per bearer, creates the self peer/domain, starts a randomized periodic timer, and stores the monitor in `tipc_net->monitors[bearer_id]`. Peer up inserts or finds a peer, marks it up, updates local domain if the affected head is self, and reassigns roles. Peer down removes domain state, marks the peer down, identifies potentially lost members if the peer was a head, updates affected domains, and reassigns roles. Removal deletes the peer and may revert all domains when cluster size falls below threshold.

STATE-message send calls `tipc_mon_prep()`. If monitoring is inactive it sends an invalid zero-length record. If the peer has acked the current domain generation it sends a dummy ack-only record; otherwise it copies the cached full domain and sets `ack_gen`. STATE-message receive calls `tipc_mon_rcv()`, validates record length/count/generation, synchronizes per-link monitor state, stores the peer's domain, applies it to the local monitor list, identifies lost members, and reassigns roles. Links call `tipc_mon_get_state()` to decide whether to monitor, probe, or reset.

## State and Persistence Behavior

All state is per net namespace and bearer in memory. The monitor list is a circular ascending list anchored at self plus hash buckets for lookup. Generations `list_gen` and `dom_gen` let link-local `struct tipc_mon_state` cache decisions. Peer `down_cnt` accumulates reports until `MAX_PEER_DOWN_EVENTS` triggers reset. The timer periodically corrects self domain size when peer count changes.

## Dependencies and Integration Points

The file depends on generic netlink, TIPC core/address/bearer/netlink helpers, timers, rwlocks, hlist/list APIs, and link STATE-message storage. It integrates tightly with `link.c`: link protocol embeds monitor records via `tipc_mon_prep()`, consumes peer records via `tipc_mon_rcv()`, and queries state through `tipc_mon_get_state()`. Netlink monitor commands expose threshold, monitor, and peer details.

## Risks and Edge Cases

Domain record validation is critical because records arrive from peers. Role assignment depends on sorted circular list invariants; insertion/removal bugs can misassign heads or skip local monitoring. Endian conversion must match the on-wire record. Threshold transitions between full-mesh and active monitoring must free or recreate peer domains carefully. `down_cnt` false positives can reset healthy links if duplicate/stale domain records are mishandled.

## Test Signals

Test clusters below and above monitor threshold, peer up/down churn, bearer deletion, node address reinitialization, malformed domain lengths/counts, generation duplicate handling, probe/reset escalation after repeated down reports, and netlink monitor/peer dumps. STATE packet captures should show dummy ack-only records after peer acknowledgement and full records on generation changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/monitor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/monitor.h -->
# sources/distributed-fs/ceph-client/net/tipc/monitor.h

## Purpose

`monitor.h` declares the TIPC monitor API and the per-link monitor cache structure used by `link.c`. It is the interface between bearer/node peer events, link protocol STATE-message preparation/receive, and netlink monitor reporting.

## Important APIs, Types, and Functions

`struct tipc_mon_state` stores a link endpoint's cached monitor list generation, peer domain generation, acked self-domain generation, and flags for monitoring, probing, reset, and synchronization. Prototypes cover monitor create/delete, peer up/down/remove, STATE-message prepare/receive, cached state lookup, threshold set/get, netlink monitor and peer dump, self-address reinitialization, and exported `tipc_max_domain_size`.

## Control Flow

Bearer setup creates a monitor per bearer. Node/link up/down events update peers. Link protocol send calls `tipc_mon_prep()` with its `tipc_mon_state`; receive calls `tipc_mon_rcv()`; timeout calls `tipc_mon_get_state()` to decide whether to probe or reset. Control-plane netlink uses threshold and dump functions.

## State and Persistence Behavior

The header has no global mutable state except the external size constant. `struct tipc_mon_state` persists inside each link and caches monitor decisions across STATE messages. The `synched` flag gates initial generation synchronization after link reset.

## Dependencies and Integration Points

It includes `netlink.h` and references `struct net`, `struct tipc_nl_msg`, and link protocol buffers. It integrates with link state messages, bearer lifecycle, node peer events, and generic netlink monitor commands.

## Risks and Edge Cases

`tipc_mon_state` fields are part of link behavior but not wire format. Resetting the structure at the wrong time can cause missed generation acks or unnecessary probes; failing to reset after link reset can ignore a peer's first domain record. `tipc_max_domain_size` must match the actual maximum record size in `monitor.c`.

## Test Signals

Compile coverage catches API drift. Runtime validation should observe monitor flags changing during peer churn, threshold netlink set/get behavior, link reset clearing monitor state, and STATE-message payload sizing using `tipc_max_domain_size`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tipc/monitor.h -->

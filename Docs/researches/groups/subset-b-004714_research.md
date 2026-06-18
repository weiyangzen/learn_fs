# Research: subset-b-004714

Grouped research for WireGuard netdev/control-plane files and ADMtek wireless driver files. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/device.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/device.c

Purpose: Implements the WireGuard virtual network device lifecycle: RTNL link creation/destruction, netdev open/stop/xmit callbacks, module-level PM/vmfork/netns notifications, workqueue and queue allocation, socket bring-up, and teardown of peers, key material, and lookup tables.

Important APIs and functions: `wg_open()` disables IPv4 redirects and IPv6 address generation, opens UDP sockets, then drains staged peer packets and emits persistent keepalives. `wg_stop()` purges staged traffic, stops timers, clears handshakes/keypairs, drains handshake queue, and closes sockets. `wg_xmit()` validates inner IP packets, routes them to peers by allowed destination IP, handles GSO segmentation, stages packets, and triggers encryption. `wg_newlink()` allocates peer/index hash tables, workqueues, crypt queues, ratelimiter state, registers the netdev, and adds it to the global `device_list`. `wg_destruct()` is the private destructor and performs full device cleanup. `wg_device_init()`/`wg_device_uninit()` register RTNL link ops, per-netns exit ops, and PM/vmfork notifiers.

Control flow: New RTNL links run `wg_setup()` for static netdev attributes, then `wg_newlink()` for dynamic resources. Open initializes sockets and kicks peers; transmit looks up a peer via `wg_allowedips_lookup_dst()`, validates endpoint family, segments GSO packets, stores MTU metadata in `PACKET_CB`, queues to the peer staged queue, and calls `wg_packet_send_staged_packets()`. Stop and destruct run in reverse: stop disables live datapath state; destruct removes the global list entry, clears sockets, removes peers, destroys workqueues, frees queues/hash tables, zeroes identity, and waits for RCU peer release.

State and persistence: Owns global `device_list`; per-device sockets, static identity, allowedips trie, peer/index hash tables, workqueues, crypt queues, handshake queue length, incoming port, fwmark, peer count, and update generation. No durable state is stored, but netdev registration, UDP sockets, per-peer timers, queued skbs, and RCU/kref references must be unwound in strict order.

Dependencies and integration points: Integrates with Linux netdev/RTNL, per-netns operations, PM and random-vmfork notifiers, UDP socket helpers, allowedips, Noise, peer lifecycle, packet queueing, timers, and ratelimiter. It provides the `wireguard` rtnl-link kind and uses `ip_tunnel_header_ops` and tunnel headroom/tailroom conventions.

Risks: `wg_xmit()` returns negative errno cast as `netdev_tx_t` on errors rather than `NETDEV_TX_OK`, so callers rely on this existing driver convention. Teardown ordering is sensitive: peers reference queues/workqueues/NAPI/timers and keypairs via RCU. Device-private key material and sockets must be cleared on suspend, vmfork, namespace exit, stop, and destroy. GSO segmentation and staged queue trimming must avoid skb leaks and keep TX drop counters accurate.

Test signals: Create/delete WireGuard links, open/stop with IPv4 and IPv6 configured, transmit to missing peer and missing endpoint, GSO and non-GSO xmit, staged queue overflow, persistent keepalive on open, suspend/vmfork key clearing, netns exit socket/source clearing, and destructor leak checks under active peers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/device.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/device.h

Purpose: Defines the central WireGuard device state and queue worker structures shared by device, packet, peer, socket, netlink, and timer code.

Important APIs and types: `struct multicore_worker` pairs a work item with a queue pointer for per-CPU crypto/handshake workers. `struct crypt_queue` wraps a `ptr_ring`, per-CPU workers, and last CPU cursor. `struct prev_queue` is the ordered per-peer queue used to preserve packet order after parallel crypto. `struct wg_device` aggregates netdev pointer, encrypt/decrypt/handshake queues, RCU sockets, creating netns, static identity, workqueues, cookie checker, lookup tables, allowedips trie, locks, peer/device lists, handshake queue length, peer count, update generation, fwmark, and incoming port. Exports `wg_device_init()` and `wg_device_uninit()`.

Control flow: The header has no executable flow, but it is the state contract used by `device.c` allocation/teardown, `send.c`/`receive.c` queueing, `netlink.c` control changes, `socket.c` RCU socket replacement, and `peer.c` peer insertion/removal.

State and persistence: Declares all volatile per-interface runtime state. `sock4`, `sock6`, and `creating_net` are RCU-protected; `device_update_lock` serializes control-plane mutations; `socket_update_lock` serializes socket replacement. No durable persistence exists.

Dependencies and integration points: Includes Noise, allowedips, peerlookup, cookie, netdevice, workqueue, mutex, ptr_ring, and socket types. It is high fanout and creates circular dependency pressure with `peer.h` and queueing headers.

Risks: Any field lifetime change affects multiple asynchronous paths. `prev_queue.empty` must match the first two members of `struct sk_buff`, enforced in queue code. Locking semantics are implicit in the struct and must remain consistent across callers.

Test signals: Build coverage across all WireGuard C files, RTNL link create/destroy, socket replacement, queue init/free, and peer removal while queues and work items are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/generated/netlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/generated/netlink.c

Purpose: Auto-generated Generic Netlink policy and split-op table for the WireGuard control API, generated from `Documentation/netlink/specs/wireguard.yaml`.

Important APIs and definitions: Defines exported policy arrays `wireguard_wgallowedip_nl_policy` and `wireguard_wgpeer_nl_policy`, plus command-specific `wireguard_get_device_nl_policy` and `wireguard_set_device_nl_policy`. Exports `wireguard_nl_ops[2]`, mapping `WG_CMD_GET_DEVICE` to `wg_get_device_start()`, `wg_get_device_dumpit()`, and `wg_get_device_done()`, and `WG_CMD_SET_DEVICE` to `wg_set_device_doit()`.

Control flow: Generic Netlink validates request attributes against these policies before invoking the handwritten handlers in `netlink.c`. The dump op permits admin dump capability; the set op permits admin doit capability. Nested peers and allowed IPs use nested array policies.

State and persistence: Owns no mutable runtime state. The arrays are kernel ABI validation data and must match UAPI `linux/wireguard.h` and the generated header.

Dependencies and integration points: Includes netlink/genetlink headers, `generated/netlink.h`, UAPI WireGuard definitions, and time types. Integrated by `netlink.c` through the `genl_family.split_ops` pointer.

Risks: Because this is generated, manual edits can be lost or drift from YAML/UAPI. Policy length/mask mistakes could either reject valid userspace configurations or admit malformed keys, flags, endpoints, or nested allowed IPs.

Test signals: Generic netlink get/set smoke tests, malformed attribute length tests, invalid flag mask tests, nested peer/allowedip parsing, and regeneration diff against the YAML spec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/generated/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/generated/netlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/generated/netlink.h

Purpose: Auto-generated declaration header for WireGuard Generic Netlink policy arrays, split operations, and handler prototypes.

Important APIs and types: Declares `wireguard_wgallowedip_nl_policy`, `wireguard_wgpeer_nl_policy`, `wireguard_nl_ops[2]`, and the handwritten callbacks `wg_get_device_start()`, `wg_get_device_done()`, `wg_get_device_dumpit()`, and `wg_set_device_doit()`.

Control flow: This header binds generated validation/dispatch tables to the handwritten implementation that registers the Generic Netlink family. It has no executable flow.

State and persistence: No state. It preserves the generated source contract derived from `Documentation/netlink/specs/wireguard.yaml`.

Dependencies and integration points: Includes netlink/genetlink headers, UAPI WireGuard definitions, and `linux/time_types.h`. Consumed by generated `netlink.c` and handwritten `netlink.c`.

Risks: Prototype or array-size drift breaks Generic Netlink registration. Hand editing the generated header risks divergence from the YAML schema.

Test signals: Compile WireGuard netlink registration, run get/set Generic Netlink commands, and compare regenerated output from `tools/net/ynl/ynl-regen.sh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/generated/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/main.c

Purpose: Provides WireGuard module initialization and exit sequencing plus module metadata and aliases.

Important APIs and functions: `wg_mod_init()` initializes allowedips slab state, optional DEBUG selftests, Noise constants, peer kmem cache, device RTNL/pernet/notifier plumbing, and Generic Netlink family. `wg_mod_exit()` unregisters Generic Netlink, device plumbing, peer cache, and allowedips slab state. Module macros expose license, description, author, version, RTNL link alias, and Generic Netlink family alias.

Control flow: Initialization proceeds from low-level data structures to externally visible APIs; each error branch unwinds only resources already initialized. In DEBUG builds, allowedips, packet counter, and ratelimiter selftests run before peer/device/netlink registration. Exit unwinds in reverse external-to-internal order.

State and persistence: Module load creates global slab caches, precomputed Noise initialization constants, notifier registrations, RTNL link kind, and Generic Netlink family. These persist until module unload.

Dependencies and integration points: Integrates with `allowedips`, `noise`, `peer`, `device`, `netlink`, and optional DEBUG selftest sources included elsewhere. Uses `WG_GENL_NAME` and `WIREGUARD_VERSION`.

Risks: Error labels must remain aligned with initialization order. DEBUG selftests can make module load fail. Netlink/device registration order affects userspace visibility of partially initialized functionality.

Test signals: Module load/unload, failure injection for each init step, DEBUG selftest pass/fail behavior, RTNL link autoload alias, and Generic Netlink family autoload alias.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/messages.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/messages.h

Purpose: Defines WireGuard cryptographic sizes, protocol limits, message type IDs, wire-format structures, skb headroom/tailroom constants, and handshake DSCP marking.

Important APIs and types: Enumerates Noise key/hash/tag/timestamp sizes, cookie sizes, anti-replay window sizes, protocol limits such as rekey/reject times and message counts, queue limits, and message types. Defines packed-by-layout C structs for handshake initiation, response, cookie, and data messages. `noise_encrypted_len()` and `message_data_len()` calculate authenticated ciphertext sizes. `DATA_PACKET_HEAD_ROOM`, `SKB_HEADER_LEN`, and `MESSAGE_PADDING_MULTIPLE` are used by send/receive and netdev setup.

Control flow: Header-only constants drive validation in `receive.c`, encryption layout in `send.c`, handshake construction in `noise.c`, MTU setup in `device.c`, and cookie handling. No executable flow exists.

State and persistence: No runtime state. The values encode stable protocol ABI and security limits.

Dependencies and integration points: Pulls Curve25519, ChaCha20-Poly1305, BLAKE2s, kernel, params, and skb definitions. Integrates with UAPI key length checks in `netlink.c`.

Risks: Size or alignment changes are wire-protocol breaking. Queue and timing constants affect DoS resistance, latency, and rekey behavior. Data headroom/tailroom must match encapsulation and authentication tag needs.

Test signals: Compile-time size checks, handshake interop, encrypted data length tests, MTU/headroom behavior, anti-replay counter selftest, and netlink key length `BUILD_BUG_ON()` checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/netlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/netlink.c

Purpose: Implements the handwritten WireGuard Generic Netlink control plane for dumping and setting interface, peer, endpoint, key, fwmark, listen-port, persistent-keepalive, and allowedips configuration.

Important APIs and functions: `wg_get_device_start()`, `wg_get_device_dumpit()`, and `wg_get_device_done()` implement multipart dumps with peer/allowedips cursors. `wg_set_device_doit()` applies device-level and nested peer changes. Helpers include `lookup_interface()`, `get_peer()`, `get_allowedips()`, `set_port()`, `set_allowedip()`, and `set_peer()`. `wg_genetlink_init()` registers the family and checks UAPI key sizes; `wg_genetlink_uninit()` unregisters it.

Control flow: Dump start resolves the WireGuard netdev by ifindex or ifname. Dumpit locks RTNL and `device_update_lock`, emits device attributes and private/public keys, then walks peers and their allowedips, saving cursors when the skb fills. Set operations resolve the device, take RTNL plus `device_update_lock`, check namespace capability for listen-port/fwmark changes, bump `device_update_gen`, apply fwmark/listen-port/private-key updates, optionally replace all peers, then process nested peer operations. Peer set creates or finds a peer, handles remove/update-only/replace-allowedips flags, updates preshared key, endpoint, allowedips, keepalive interval, and sends staged packets on running devices.

State and persistence: Mutates `wg_device` incoming port, fwmark, static identity, cookie precomputed keys, peer list, peer allowedips, peer endpoint, preshared keys, keepalive intervals, staged packets, and update generation. Private and preshared key netlink buffers are explicitly zeroed after use. State is runtime-only but visible to userspace via netlink dumps.

Dependencies and integration points: Depends on generated netlink policies, UAPI WireGuard attributes, Generic Netlink, RTNL, peer lookup/lifecycle, allowedips trie, Noise identity/keypair invalidation, socket reinitialization, cookie precomputation, and queueing.

Risks: Dumps include private key material in skbs and note missing zero-on-free support. Multipart dump consistency depends on `device_update_gen`, peer references, and allowedips sequence checks. Private-key replacement removes a peer with matching new public key before updating identity. Capability checks are tied to the creating namespace, which can disappear. Attribute parsing must keep key material lengths and flags strict.

Test signals: `wg show` and `wg set` equivalents by ifname/ifindex, multipart dumps with many peers/allowedips, concurrent peer removal during dump, private-key replacement removing self peer, listen-port socket rebind, fwmark clearing endpoint source cache, replace-peers/replace-allowedips flags, invalid protocol version, and malformed nested attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/netlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/netlink.h

Purpose: Declares WireGuard Generic Netlink module lifecycle functions.

Important APIs: `wg_genetlink_init()` registers the Generic Netlink family; `wg_genetlink_uninit()` unregisters it.

Control flow: Used by `main.c` after device initialization and before device uninitialization. The header has no executable flow.

State and persistence: No direct state; declared functions manage global Generic Netlink family registration.

Dependencies and integration points: Consumed by `main.c` and implemented in `netlink.c`.

Risks: Minimal, but init/uninit order matters because userspace can configure devices through the family once registered.

Test signals: Module load/unload and Generic Netlink family visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/noise.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/noise.c

Purpose: Implements WireGuard's Noise_IKpsk2 handshake, HKDF/BLAKE2s chaining, Curve25519 DH mixes, ChaCha20-Poly1305 handshake encryption, static-static precomputation, keypair lifecycle, key rotation slots, replay-relevant key invalidation, and session derivation.

Important APIs and functions: `wg_noise_init()` precomputes initial chaining key/hash. `wg_noise_handshake_init()`, `wg_noise_handshake_clear()`, and `wg_noise_precompute_static_static()` manage per-peer handshake state. `wg_noise_handshake_create_initiation()`, `wg_noise_handshake_consume_initiation()`, `wg_noise_handshake_create_response()`, `wg_noise_handshake_consume_response()`, and `wg_noise_handshake_begin_session()` implement the protocol transcript. `wg_noise_keypair_get()`, `wg_noise_keypair_put()`, `wg_noise_keypairs_clear()`, `wg_noise_received_with_keypair()`, and `wg_noise_expire_current_peer_keypairs()` manage current/previous/next keypairs. Internal helpers implement HMAC, HKDF, DH mixing, hash mixing, PSK mixing, message encrypt/decrypt, ephemeral handling, and rounded TAI64N timestamps.

Control flow: Initiators create an initiation from static identity and remote static key, generate an ephemeral, mix `es`, encrypt static key, mix precomputed `ss`, encrypt timestamp, and insert a handshake index. Responders consume initiation by decrypting peer static key, looking up the peer, validating `ss`, decrypting timestamp, rejecting replay/flood attempts, and storing transcript state. Responses add responder ephemeral, mix `ee`, `se`, PSK, encrypt an empty payload, and insert a response index. Consuming a response validates the saved initiation transcript and marks handshake consumed. Beginning a session derives directional sending/receiving keys, zeroes handshake state, installs current or next keypair depending on initiator/responder role, and replaces the handshake index with a keypair index.

State and persistence: Mutates per-peer handshake state, latest timestamp, last initiation consumption time, static-static precomputation, current/previous/next keypairs, key validity flags, sending counters, receiving replay counters, random index hash entries, and keypair refcounts. Sensitive stack and heap material is zeroed with `memzero_explicit()` or `kfree_sensitive()`.

Dependencies and integration points: Uses Curve25519, BLAKE2s, ChaCha20-Poly1305, kernel random APIs, RCU, krefs, index/pubkey peer lookup, device index table, timers through callers, and message formats. The receive/send paths call into this file for handshake parsing and data-key validity.

Risks: Cryptographic transcript ordering and hash/chaining-key updates are correctness- and security-critical. Locking mixes static identity rwsem, handshake rwsem, RCU, krefs, and keypair spinlock. Timestamp replay and initiation flood checks must remain monotonic despite races. The initiator keypair transition comment notes a possible KCI robustness tradeoff around demoting `next_keypair`. Index replacement failure during peer death must not leak keypairs.

Test signals: Interoperability with WireGuard userspace/kernel peers, initiation replay rejection, initiation flood throttling, invalid DH/public key handling, response to stale/missing index, PSK/no-PSK sessions, key rotation current/next/previous transitions, suspend/vmfork key expiry, RCU/kref leak detection, and static identity change invalidating peer keypairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/noise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/noise.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/noise.h

Purpose: Defines WireGuard Noise state types and declares the cryptographic handshake/keypair APIs.

Important APIs and types: `struct noise_replay_counter` stores anti-replay bitmap state. `struct noise_symmetric_key` stores key bytes, birthdate, and validity. `struct noise_keypair` stores index-table entry, sending/receiving keys, send counter, receive replay counter, remote index, initiator flag, kref/RCU, and debug ID. `struct noise_keypairs` stores current/previous/next RCU keypairs. `struct noise_static_identity` stores device public/private static key under rwsem. `enum noise_handshake_state` and `struct noise_handshake` capture the in-progress protocol transcript, remote static/ephemeral keys, preshared key, hash/chaining key, latest timestamp, and remote index. Declares all Noise lifecycle, keypair, identity, precompute, handshake create/consume, and session-begin functions.

Control flow: The header defines state transitions used by `noise.c`, with callers in send/receive/netlink/device/peer. `wg_noise_reset_last_sent_handshake()` sets a timestamp far enough in the past to allow immediate initiation.

State and persistence: Header declares sensitive volatile key material that must be zeroed on clear, stop, peer destroy, suspend, vmfork, or static identity change. Keypairs and handshakes are indexed in runtime lookup tables.

Dependencies and integration points: Includes message constants and peerlookup entry types plus kernel locks, atomics, krefs, and rwsem types. Consumed throughout WireGuard datapath and control plane.

Risks: Struct layout and locking comments define cross-file invariants. Callers must hold the right locks when accessing private key, handshake transcript, or RCU keypair pointers. Exposing raw key buffers increases risk of missed zeroization.

Test signals: Compile coverage, static identity setting, handshake state-machine tests, keypair RCU/kref lifetime tests, and anti-replay counter selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/noise.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/peer.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/peer.c

Purpose: Implements WireGuard peer allocation, initialization, lookup reference helpers, removal, full teardown, and peer slab cache lifecycle.

Important APIs and functions: `wg_peer_create()` allocates a peer, initializes endpoint cache, Noise handshake, cookie state, timers, keypair lock, work items, per-peer TX/RX ordered queues, endpoint lock, staged packet queue, NAPI, allowedips list, pubkey hash entry, and peer counters. `wg_peer_get_maybe_zero()` safely references peers under RCU. `wg_peer_remove()` and `wg_peer_remove_all()` remove peers from configuration lookup structures and complete asynchronous teardown. `wg_peer_put()` releases krefs. `wg_peer_init()`/`wg_peer_uninit()` manage the peer kmem cache.

Control flow: Creation requires `device_update_lock`, checks `MAX_PEERS_PER_DEVICE`, initializes all peer subsystems, adds the peer to the device list and pubkey hashtable, and enables NAPI. Removal first calls `peer_make_dead()` to remove config-time reachability and set `is_dead`, then `synchronize_net()`, then `peer_remove_after_dead()` to clear keypairs, stop timers, flush crypto work twice, disable/delete NAPI, flush handshake send work, decrement peer count, and drop the owning reference. Final kref release removes handshake index, purges staged packets, and schedules RCU memory zero/free.

State and persistence: Mutates `wg->peer_list`, `wg->num_peers`, peer allowedips list, pubkey hash, index hash entries, NAPI state, keypairs, timers, staged packets, endpoint cache, and peer kref/RCU lifetime. No durable state exists.

Dependencies and integration points: Depends on device state, queueing, timers, peerlookup, Noise, cookie, allowedips, dst cache, NAPI, workqueues, RCU, and krefs. Netlink creates/removes peers; datapath holds peer references during TX/RX and handshake processing.

Risks: Removal ordering is delicate because packets can move from global crypto queues to per-peer serial/NAPI queues while references are in flight. The double workqueue flush and `synchronize_net()` are part of the lifetime proof. Any new peer context must honor `is_dead` or removal can race into freed state. Final zeroing wipes sensitive material but requires all references gone.

Test signals: Create up to limit, remove single/all peers under traffic, remove during handshake and data receive, NAPI disable/delete correctness, queued packet cleanup, staged packet drop accounting, RCU stall/leak detection, and peer cache init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/peer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/peer.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/peer.h

Purpose: Defines endpoint and peer runtime state plus peer lifecycle APIs.

Important APIs and types: `struct endpoint` stores remote IPv4/IPv6 sockaddr plus discovered source address/interface information for route symmetry. `struct wg_peer` contains device pointer, ordered TX/RX queues, staged packet queue, serial work CPU, death flag, keypairs, endpoint/cache/lock, handshake, last handshake timestamp, work items, cookie, pubkey hash node, byte counters, timers, persistent keepalive fields, last handshake walltime, kref/RCU, peer and allowedips lists, NAPI, and internal ID. Declares create/get/put/remove/all and peer cache init/uninit APIs.

Control flow: Header shapes how netlink, device, socket, send, receive, timers, and lookup code share peer state. Inline `wg_peer_get()` increments the kref without zero check for known-live references.

State and persistence: Declares volatile per-peer runtime state. Endpoint cache and byte counters persist only while the peer object lives; key material is sensitive and must be cleared.

Dependencies and integration points: Includes device, Noise, cookie, netfilter, spinlock, kref, and dst-cache types. The endpoint type is consumed by socket and debug helpers.

Risks: Peer state is accessed from softirq, workqueue, timer, NAPI, and netlink contexts. Fields require different locks: endpoint rwlock, keypair spinlock, handshake rwsem, kref/RCU, and device update mutex. Misuse of `wg_peer_get()` on maybe-dead peers can resurrect invalid objects.

Test signals: Build coverage, peer creation/removal, endpoint update and source clearing, timer callbacks, NAPI receive, kref underflow checks, and RCU lifetime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/peer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/peerlookup.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/peerlookup.c

Purpose: Implements WireGuard peer lookup tables: public-key-to-peer for configuration/handshake identity and random-index-to-handshake/keypair for incoming response/data packet dispatch.

Important APIs and functions: `wg_pubkey_hashtable_alloc()`, `wg_pubkey_hashtable_add()`, `wg_pubkey_hashtable_remove()`, and `wg_pubkey_hashtable_lookup()` manage siphash-keyed public key buckets. `wg_index_hashtable_alloc()`, `wg_index_hashtable_insert()`, `wg_index_hashtable_replace()`, `wg_index_hashtable_remove()`, and `wg_index_hashtable_lookup()` manage random 32-bit index entries for handshakes and keypairs.

Control flow: Public-key lookup hashes remote static keys under RCU and returns a strong peer reference. Index insertion removes any old entry, picks a random unused 32-bit index with unlocked search and locked double-check, then inserts under RCU. Session establishment replaces a handshake index with a keypair index. Lookup filters by type mask and returns the indexed entry plus a strong peer reference.

State and persistence: Maintains per-device hash arrays, random siphash keys, mutex/spinlock protection, RCU hlist nodes, and index values. State is runtime-only and rebuilt on device/peer creation.

Dependencies and integration points: Used by netlink peer lookup, Noise handshake consume/session begin, receive data packet dispatch, cookie consume paths, and peer teardown. Depends on siphash, hashtable macros, RCU BH read sections, and peer krefs.

Risks: Index uniqueness search is intentionally not constant time and relies on low occupancy. Replacement initializes the old hlist node, with comments acknowledging benign RCU lookup races that drop packets. Lookups must not return peers whose kref reached zero. Public-key hash access must stay synchronized with peer removal and static key updates.

Test signals: Many peer insertion/removal cycles, index collision stress, response/data lookup by index, stale index after peer removal, RCU/kref race tests, and public-key lookup after peer replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/peerlookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/peerlookup.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/peerlookup.h

Purpose: Declares WireGuard public-key and index lookup table structures and operations.

Important APIs and types: `struct pubkey_hashtable` contains an 11-bit hlist hash table, siphash key, and mutex. `struct index_hashtable` contains a 13-bit hlist hash table and spinlock. `enum index_hashtable_type` distinguishes handshake and keypair entries. `struct index_hashtable_entry` stores peer pointer, hlist node, type mask, and index. Declares alloc/add/remove/lookup/insert/replace functions.

Control flow: Header has no executable flow but defines the lookup entry embedded in Noise handshakes and keypairs.

State and persistence: Declares runtime lookup state only. Hash table size and entry type masks are protocol performance/lifetime parameters.

Dependencies and integration points: Includes message key sizes, kernel hashtable, mutex, and siphash headers. Used by device allocation, peer creation/removal, Noise, and receive.

Risks: Type masks must match lookup callers; table sizes and random indexes affect collision behavior; embedded entries require careful lifetime management.

Test signals: Compile coverage, public key lookup, index insert/replace/remove, and RCU lifetime tests under data/handshake traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/peerlookup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/queueing.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/queueing.c

Purpose: Implements WireGuard queue primitives used to run crypto in parallel while preserving per-peer packet order.

Important APIs and functions: `wg_packet_percpu_multicore_worker_alloc()` allocates and initializes a per-CPU `multicore_worker` array. `wg_packet_queue_init()` initializes a bounded `ptr_ring` and per-CPU workers for a crypt queue. `wg_packet_queue_free()` frees workers and cleans the ring. `wg_prev_queue_init()`, `wg_prev_queue_enqueue()`, and `wg_prev_queue_dequeue()` implement a multi-producer/single-consumer ordered queue using `skb->prev` as next pointer and a stub node.

Control flow: Device queues receive skbs/lists for parallel encryption/decryption. Per-peer queues receive the same items first so the serial consumer can wait until worker state changes from uncrypted to crypted/dead, preserving order even if crypto finishes out of order.

State and persistence: Mutates `crypt_queue.ring`, per-CPU worker pointers, `last_cpu`, and `prev_queue` head/tail/peek/count state. Queue contents are volatile skbs.

Dependencies and integration points: Used by device setup/teardown, send encryption worker, receive decryption worker, per-peer TX worker, and NAPI RX polling. Depends on ptr_ring, per-CPU workqueues, skb layout, atomics, and memory barriers.

Risks: The queue relies on `struct sk_buff` `next`/`prev` offsets and release/acquire ordering. `wg_packet_queue_free()` warns if non-purge cleanup sees pending entries. Failed global queue insertion after per-peer insertion returns `-EPIPE` and callers must mark peer queue entries dead.

Test signals: Queue capacity limits, multi-producer ordering, crypto completion out of order, queue free with and without purge, CPU hotplug/online selection behavior, and skb leak tests on `-EPIPE` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/queueing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/queueing.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/queueing.h

Purpose: Declares WireGuard packet queue APIs and defines inline helpers for protocol validation, skb scrubbing, CPU selection, and enqueueing between per-device crypto queues and per-peer serial queues.

Important APIs and types: Declares queue init/free/per-CPU worker alloc, receive entry points/workers, send entry points/workers, `enum packet_state`, `struct packet_cb`, `PACKET_CB`, and `PACKET_PEER`. Inline helpers include `wg_check_packet_protocol()`, `wg_reset_packet()`, CPU selection helpers, `wg_prev_queue_peek()`, `wg_prev_queue_drop_peeked()`, `wg_queue_enqueue_per_device_and_peer()`, `wg_queue_enqueue_per_peer_tx()`, and `wg_queue_enqueue_per_peer_rx()`.

Control flow: `wg_queue_enqueue_per_device_and_peer()` marks an skb/list uncrypted, enqueues it first to the per-peer ordered queue, then to the per-device `ptr_ring`, and schedules a per-CPU crypto worker. Crypto workers later call TX or RX enqueue helpers, which take a temporary peer reference, publish final state with release semantics, then schedule the peer serial worker or NAPI.

State and persistence: Stores transient packet metadata in skb control buffer: nonce, keypair pointer, atomic state, MTU, and DS field. Manipulates peer references and queue state but owns no durable state.

Dependencies and integration points: Shared by `device.c`, `send.c`, `receive.c`, `peer.c`, and DEBUG selftests. Uses skb, IP/IPv6 tunnel helpers, NAPI, workqueues, atomics, and peer krefs.

Risks: `PACKET_CB` consumes skb control buffer, so callers must not need prior control metadata after enqueue. Release/acquire semantics are required to avoid serial consumers seeing incomplete crypto writes. `wg_reset_packet()` scrubs metadata differently for encapsulation to preserve hash values. Queue insertion partial failure must be handled by caller.

Test signals: TX/RX ordering under parallel crypto, skb control buffer correctness, GSO segmentation metadata, NAPI scheduling after decrypt, peer serial CPU choice, and DEBUG packet counter selftest declaration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/queueing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/ratelimiter.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/ratelimiter.c

Purpose: Implements a global token-bucket ratelimiter for WireGuard handshake initiation packets, keyed by network namespace and source IPv4 address or IPv6 /64.

Important APIs and functions: `wg_ratelimiter_allow()` checks or creates a per-source entry and consumes tokens. `wg_ratelimiter_init()` reference-counts global initialization, creates the entry cache, sizes IPv4/IPv6 hash tables based on RAM, schedules garbage collection, and seeds siphash key. `wg_ratelimiter_uninit()` decrements init refcount, cancels GC, removes all entries, waits for RCU, and frees tables/cache. `wg_ratelimiter_gc_entries()` prunes entries idle for over one second or removes all entries on shutdown. DEBUG builds include `selftest/ratelimiter.c`.

Control flow: On packet check, the code hashes the net namespace pointer and source address into the relevant table. Existing entries update tokens according to elapsed coarse boottime and allow if at least one packet cost is available. Missing entries allocate a new bucket entry up to `max_entries`, initialize it with burst budget minus one packet, and insert under RCU.

State and persistence: Global static state includes kmem cache, siphash key, table lock, init mutex/refcount, total entry count, max entries, table size, delayed GC work, and IPv4/IPv6 hash tables. Entries store last time, tokens, IP, net pointer, spinlock, hlist node, and RCU head.

Dependencies and integration points: Used by WireGuard handshake receive/cookie path to rate-limit unauthenticated initiations. Depends on siphash, coarse boottime, RCU, delayed work, memory sizing, IPv4/IPv6 headers, and DEBUG selftests.

Risks: Global refcounting must match per-device init/uninit. IPv6 intentionally ratelimits by /64, which is security policy. `net_word` truncates the net pointer to 32 bits by design. Table insertion after RCU lookup can race duplicate entries for the same IP under concurrency, affecting strictness but bounded by max entries. GC and shutdown must not free entries still under RCU readers.

Test signals: DEBUG ratelimiter selftest, burst/rate timing behavior, IPv4 and IPv6 /64 keys, max-entry capacity behavior, repeated device create/destroy refcounting, GC expiry, and concurrent handshake flood tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/ratelimiter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/ratelimiter.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/ratelimiter.h

Purpose: Declares the WireGuard handshake ratelimiter lifecycle and allow-check API.

Important APIs: `wg_ratelimiter_init()`, `wg_ratelimiter_uninit()`, and `wg_ratelimiter_allow()`. DEBUG builds also declare `wg_ratelimiter_selftest()`.

Control flow: Header-only declarations are used by device initialization/destruction and receive/cookie handling.

State and persistence: No state in the header; implementation owns global refcounted tables.

Dependencies and integration points: Includes skb type declarations and is consumed by `device.c`, `receive.c`/cookie paths, `main.c` DEBUG selftests, and `ratelimiter.c`.

Risks: Callers must initialize before allow checks and balance uninit calls across devices.

Test signals: Compile in DEBUG and non-DEBUG builds, module load selftest, and device create/destroy cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/ratelimiter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/receive.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/receive.c

Purpose: Implements WireGuard UDP receive path for handshake, cookie, and encrypted data packets, including header validation, cookie/MAC handling under load, data decryption dispatch, anti-replay validation, inner packet validation, allowed source enforcement, NAPI delivery, and RX statistics.

Important APIs and functions: `wg_packet_receive()` is the socket entry point. `wg_packet_handshake_receive_worker()` drains queued handshakes. `wg_packet_decrypt_worker()` decrypts data packets in parallel. `wg_packet_rx_poll()` serially consumes per-peer decrypted packets under NAPI. Key helpers include `prepare_skb_header()`, `validate_header_len()`, `wg_receive_handshake_packet()`, `decrypt_packet()`, `counter_validate()`, `wg_packet_consume_data()`, and `wg_packet_consume_data_done()`. DEBUG builds include the packet counter selftest.

Control flow: Socket receive trims/pulls the skb to the UDP payload and validates exact WireGuard message sizes. Handshake/cookie packets enter a bounded handshake queue and are processed on per-CPU workers. Under load, MAC/cookie validation may demand a cookie reply before handshake consumption. Valid initiations update endpoint, send a response, and record timers/stats; valid responses derive a session and send keepalive or staged data. Data packets look up a keypair by index, take keypair/peer refs, enqueue for decrypt, then per-peer NAPI validates crypto state, replay counter, endpoint, inner IP header, ECN, inner length, and allowed source peer before GRO delivery.

State and persistence: Updates device handshake queue length, per-peer endpoint, keypair next/current transition, replay counter bitmap, timers, byte counters, netdev stats, skb packet metadata, and staged packets. All state is runtime-only.

Dependencies and integration points: Depends on queueing, Noise, cookie, timers, socket endpoint helpers, allowedips source lookup, ip tunnel helpers, NAPI/GRO, ChaCha20-Poly1305 scatter-gather crypto, skb cow/trim/pull APIs, and ratelimited debug logging.

Risks: Header preparation must defend against malformed IP/UDP lengths. Anti-replay `counter_validate()` is security-critical. Decryption temporarily pushes/pulls headers to preserve endpoint metadata. The allowed-source check prevents peer spoofing and must match allowedips semantics. Queue overload paths can drop handshakes; cookie under-load state is global and racy by design. NAPI completion must not lose remaining crypted/dead packets.

Test signals: Malformed UDP/IP lengths, each message type size, cookie response under queue load, invalid MAC, valid initiation/response session derivation, data decrypt success/failure, replayed counters, keepalive zero-length data, invalid inner IP/version/length, allowedips source mismatch, IPv4/IPv6 ECN decapsulation, GRO delivery, and queue overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/receive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/selftest/allowedips.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/selftest/allowedips.c

Purpose: Provides DEBUG-only init-time tests for the WireGuard allowedips trie, including deterministic IPv4/IPv6 route cases, removal behavior, list iteration normalization, optional Graphviz dumping, and optional randomized comparison against a simple reference implementation.

Important APIs and functions: `wg_allowedips_selftest()` is the public DEBUG selftest. Helpers build fake peers, insert/remove/test IPv4 and IPv6 prefixes, print trie nodes, and optionally run `randomized_test()`. The "horrible" reference table implements ordered CIDR match with simple hlist nodes for cross-checking. Macros `insert`, `remove`, `test`, `test_negative`, and `test_boolean` structure the deterministic cases.

Control flow: The deterministic test initializes an allowedips trie, creates fake peers, inserts overlapping routes, validates longest-prefix lookups, removes by peer and exact prefix, checks invalid CIDR handling, stresses deep IPv6 free paths, validates peer allowedips list normalization, optionally runs random tests, then frees all structures. Random testing inserts many random/mutated IPv4 and IPv6 routes into both implementations, compares lookup results over many queries, then removes peers one by one.

State and persistence: Allocates temporary fake peers, allowedips trie nodes, and reference hlist nodes during module init in DEBUG builds. No state persists after the test, except printk output.

Dependencies and integration points: Included by the allowedips implementation in DEBUG builds and invoked from `main.c` before module registration. Depends on allowedips internal functions such as `lookup()` and `wg_allowedips_read_node()`, peer krefs/lists, mutex locking, siphash for graph colors, and random APIs.

Risks: It reaches into internal allowedips details and can become stale when trie internals change. Optional random mode is intentionally very expensive. Static `ip4()`/`ip6()` helpers reuse storage, so tests rely on immediate consumption. DEBUG-only coverage means production builds do not run it.

Test signals: DEBUG module load should print allowedips self-tests pass. Failures indicate lookup, prefix normalization, replacement, exact removal, invalid CIDR handling, peer removal, list iteration, or trie free-depth regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/selftest/allowedips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/selftest/counter.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/selftest/counter.c

Purpose: Provides DEBUG-only init-time tests for the WireGuard data packet anti-replay counter window implemented in `receive.c`.

Important APIs and functions: `wg_packet_counter_selftest()` allocates a `noise_replay_counter`, repeatedly initializes it, and uses macro `T(n, expected)` to assert `counter_validate()` behavior over duplicates, out-of-order counters, window boundaries, and reject-after limits.

Control flow: Test sequences first check simple increasing, duplicate, and near-window values, then fill entire windows in ascending and descending patterns, then checks boundary behavior near `REJECT_AFTER_MESSAGES`. It prints pass/fail and frees the counter.

State and persistence: Allocates one temporary replay counter and mutates its bitmap/counter state. No persistent state remains.

Dependencies and integration points: Included inside `receive.c` after `counter_validate()` so it can call the static function. Invoked from `main.c` in DEBUG builds.

Risks: Because it includes the static implementation, compile placement matters. It verifies algorithmic cases but not concurrent locking behavior under real RX load.

Test signals: DEBUG module load should print nonce counter self-tests pass; failure pinpoints anti-replay window or reject-limit regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/selftest/counter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/selftest/ratelimiter.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/selftest/ratelimiter.c

Purpose: Provides DEBUG-only init-time tests for the WireGuard handshake ratelimiter.

Important APIs and functions: `wg_ratelimiter_selftest()` drives initialization reference-count checks, skb construction, optional timing tests, capacity tests, and extra uninit underflow tolerance. Helpers include `maximum_jiffies_at_index()`, `timings_test()`, and `capacity_test()`.

Control flow: The selftest initializes the ratelimiter three times, creates IPv4 and optional IPv6 skbs, optionally runs rate timing expectations against token refill intervals, then fills entries up to `max_entries` to verify capacity rejection. It frees skbs and calls uninit four times to check balanced and extra uninit behavior. KASAN/UBSAN builds skip the test as timing-sensitive.

State and persistence: Mutates the global ratelimiter tables, GC state, total entry count, and init refcount during testing, then clears them. No intended persistent state remains.

Dependencies and integration points: Included by `ratelimiter.c` in DEBUG builds and invoked from `main.c`. Uses internal ratelimiter globals and functions, jiffies, msleep, IPv4/IPv6 headers, and init_net.

Risks: Timing tests are disabled unless `DEBUG_RATELIMITER_TIMINGS` because scheduler delays can cause false failures. Capacity test can be expensive on large tables. It does not simulate real handshake/cookie integration.

Test signals: DEBUG module load should print ratelimiter self-tests pass; failures indicate init refcount, token bucket, IPv4/IPv6 keying, GC cleanup, or max-entry regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/selftest/ratelimiter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/send.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/send.c

Purpose: Implements WireGuard send path for handshake initiations/responses/cookies, keepalives, staged data packet encryption, nonce assignment, key freshness rekeying, per-peer ordered TX completion, and UDP socket transmission.

Important APIs and functions: `wg_packet_send_queued_handshake_initiation()`, `wg_packet_handshake_send_worker()`, `wg_packet_send_handshake_response()`, `wg_packet_send_handshake_cookie()`, `wg_packet_send_keepalive()`, `wg_packet_send_staged_packets()`, `wg_packet_encrypt_worker()`, `wg_packet_tx_worker()`, and `wg_packet_purge_staged_packets()`. Helpers include `wg_packet_send_handshake_initiation()`, `keep_key_fresh()`, `calculate_skb_padding()`, `encrypt_packet()`, `wg_packet_create_data()`, and `wg_packet_create_data_done()`.

Control flow: Handshake initiation is rate-limited by `last_sent_handshake`, builds a Noise initiation, adds cookie MACs, sends by socket, and starts timers. Responses derive a session before sending. Data send steals the staged queue, grabs a valid current keypair, assigns ECN DS and monotonically increasing nonces to every skb, enqueues the list for parallel encryption, then serial TX worker sends successfully encrypted skbs to the peer endpoint and drops dead lists. If no usable key exists, packets are orphaned, returned to the staged queue, and a handshake is queued. Keepalive creates an empty data skb only when no staged data exists.

State and persistence: Mutates peer staged queue, keypair sending counter and validity, packet metadata, tx byte counters via socket path, timers, last sent handshake timestamp, handshake attempts, and netdev TX drop stats. State is runtime-only but sensitive to key age/message limits.

Dependencies and integration points: Depends on Noise, cookie MACs, timers, queueing, socket send helpers, ip tunnel ECN, skb scatter-gather encryption, checksum helpers, and workqueues.

Risks: Nonce assignment must never exceed `REJECT_AFTER_MESSAGES` or reuse with a key. Encryption mutates skb head/tail and must handle checksum completion before padding/header insertion. Returning packets to staged queue on missing key can reorder slightly by design. Handshake queueing must balance peer references if work is already pending. `PACKET_CB(first)->keypair` represents an entire skb list.

Test signals: Handshake initiation rate limit, response send and session derivation, cookie replies, keepalive with and without staged data, data send with valid/expired/missing key, nonce overflow invalidation, padding at MTU boundaries, checksum-partial skb encryption, parallel encryption failure, ordered TX completion, and staged queue purge stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/send.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/socket.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/socket.c

Purpose: Implements WireGuard UDP socket creation/replacement, IPv4/IPv6 encapsulated send helpers, endpoint extraction/update, reply sends, receive callback dispatch, route caching, source address validation, and socket cleanup.

Important APIs and functions: `wg_socket_init()` creates IPv4 and optional IPv6 UDP tunnel sockets for the WireGuard device. `wg_socket_reinit()` atomically swaps RCU socket pointers and frees old sockets after `synchronize_net()`. `wg_socket_send_skb_to_peer()`, `wg_socket_send_buffer_to_peer()`, and `wg_socket_send_buffer_as_reply_to_skb()` transmit data/handshake/cookie packets. `wg_socket_endpoint_from_skb()`, `wg_socket_set_peer_endpoint()`, `wg_socket_set_peer_endpoint_from_skb()`, and `wg_socket_clear_peer_endpoint_src()` manage peer endpoints. Internal `send4()`, `send6()`, `wg_receive()`, `sock_free()`, and `set_sock_opts()` do low-level routing and socket handling.

Control flow: Send path reads peer endpoint under `endpoint_lock`, routes through cached dst or fresh IPv4/IPv6 lookup using fwmark and discovered source, resets invalid source constraints, then calls UDP tunnel transmit. Reply sends derive an endpoint from the incoming skb and send without peer cache. Socket init pins the creating netns, opens IPv4 first, reuses its port for IPv6 if enabled, configures UDP tunnel callbacks, then swaps sockets into the device. Receive callback pulls `wg` from `sk_user_data` and passes skb to `wg_packet_receive()`.

State and persistence: Mutates RCU `wg->sock4/sock6`, `wg->incoming_port`, peer endpoints, peer dst caches, endpoint source fields, skb marks/devs, and peer TX byte counters. UDP sockets persist while the interface is running or until reinit/stop/destruct.

Dependencies and integration points: Uses Linux UDP tunnel APIs, IPv4/IPv6 route lookup, dst cache, LSM flow classification, RCU BH socket access, endpoint locks, netns lifetime, fwmark, and packet receive path.

Risks: Socket replacement requires `synchronize_net()` before freeing old sockets. Endpoint source address/interface can become stale and must be cleared on route errors, fwmark/port change, namespace exit, and handshake retry. IPv6 socket creation retries on ephemeral port collisions when no port is specified. Peer TX bytes are counted by skb length before socket send consumes/frees the skb.

Test signals: IPv4 and IPv6 sends, no socket error, route failure, stale source address reset, fwmark routing, endpoint update from skb, cookie reply to incoming skb, listen-port rebinding, IPv6 disabled builds, netns teardown, and concurrent sends during socket reinit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/socket.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/socket.h

Purpose: Declares WireGuard socket send/init/reinit and endpoint helper APIs, plus debug logging wrappers that resolve skb endpoints.

Important APIs: Exports socket lifecycle functions, peer send helpers, reply send helper, endpoint extraction/update/source-clear helpers, and `net_dbg_skb_ratelimited()` for dynamic debug/DEBUG builds.

Control flow: Header declarations are used by device open/stop/destruct, send/receive handshake/data paths, timers, and netlink endpoint updates.

State and persistence: No header-owned state. Declared functions mutate device sockets and peer endpoints/caches.

Dependencies and integration points: Includes netdevice, UDP, VLAN, and Ethernet headers and relies on `struct wg_device`, `struct wg_peer`, and `struct endpoint` from peer/device headers.

Risks: The non-debug `net_dbg_skb_ratelimited` macro has a shorter apparent parameter list than debug form, so call sites must match the macro definitions exactly. Endpoint helpers require skb protocol/network/UDP headers to be valid.

Test signals: Compile with and without dynamic debug/DEBUG, endpoint debug logging, socket send paths, and endpoint update paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/timers.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/timers.c

Purpose: Implements per-peer WireGuard timers for handshake retransmission, delayed keepalive, new-handshake retry after silence, zeroing stale key material, and persistent keepalives.

Important APIs and functions: `wg_timers_init()` and `wg_timers_stop()` initialize and synchronously stop all timers/work. Event hooks include `wg_timers_data_sent()`, `wg_timers_data_received()`, `wg_timers_any_authenticated_packet_sent()`, `wg_timers_any_authenticated_packet_received()`, `wg_timers_handshake_initiated()`, `wg_timers_handshake_complete()`, `wg_timers_session_derived()`, and `wg_timers_any_authenticated_packet_traversal()`. Expiry handlers include retransmit, send keepalive, new handshake, zero key material, queued zero-key work, and persistent keepalive.

Control flow: Authenticated data sent starts a new-handshake watchdog. Data received schedules a keepalive unless one is already pending, in which case it marks the need for another. Any authenticated send/receive cancels opposing timers. Handshake initiation schedules retransmit with jitter. Handshake completion cancels retransmit and records walltime. Session derivation schedules key zeroing after three reject windows. Retransmit expiry either retries and clears endpoint source or gives up, purges staged packets, and schedules key zeroing. Zero-key expiry queues work on the handshake send workqueue with a peer ref.

State and persistence: Mutates per-peer timer pending state, handshake attempt count, `timer_need_another_keepalive`, `sent_lastminute_handshake`, walltime last handshake, staged packet queue, endpoint source cache, and key material. Runtime-only.

Dependencies and integration points: Depends on peer/device state, send queueing, socket source clearing, Noise key clearing, workqueues, timers, random jitter, and netdev running state.

Risks: Timer callbacks run asynchronously against peer removal; `mod_peer_timer()` checks `netif_running()` and `is_dead` under RCU. `wg_timers_stop()` must delete timers synchronously and flush clear-peer work. Retry limits and jitter affect both liveness and network noise.

Test signals: Handshake retry/give-up, endpoint source clearing on retry, staged packet purge after max attempts, data receive keepalive behavior, data sent new-handshake watchdog, persistent keepalive interval, key zeroing after session age, peer removal while timers pending, and walltime last-handshake reporting via netlink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/timers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/timers.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/timers.h

Purpose: Declares WireGuard per-peer timer lifecycle/event hooks and provides a coarse-boottime expiration helper.

Important APIs: Declares timer init/stop plus event notification functions for data sent/received, authenticated packet sent/received/traversal, handshake initiation/completion, and session derivation. `wg_birthdate_has_expired()` compares a nanosecond birthdate plus seconds to coarse boottime.

Control flow: Send, receive, device stop, peer create/remove, and Noise session derivation use these hooks to drive rekey/keepalive behavior.

State and persistence: No header-owned state; declared functions mutate peer timers and related peer fields.

Dependencies and integration points: Includes `linux/ktime.h` and forward-declares `struct wg_peer`.

Risks: Expiration helper casts to signed 64-bit for wrap-safe comparison; callers must pass coarse-boottime-compatible birthdates. Event hooks must be called in the right datapath places or rekey/keepalive behavior changes.

Test signals: Compile coverage and send/receive timer behavior around key age, keepalive, and retry boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/timers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/version.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/version.h

Purpose: Defines the WireGuard module version string.

Important APIs and definitions: `WIREGUARD_VERSION` is set to `"1.0.0"` and consumed by `main.c` for `MODULE_VERSION()` and load-time `pr_info()`.

Control flow: No executable flow.

State and persistence: No runtime state. The macro contributes to module metadata and logs.

Dependencies and integration points: Included by `main.c`.

Risks: Version drift can mislead userspace/log readers if code changes without updating the macro.

Test signals: Module metadata inspection and load log should report the expected version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/Kconfig

Purpose: Defines the top-level Linux Wireless LAN driver Kconfig menu and includes vendor-specific wireless driver Kconfig files.

Important APIs and definitions: `menuconfig WLAN` is a bool menu enabled by default, depends on `!S390` and `NET`, and selects `WIRELESS`. Inside `if WLAN`, it sources vendor Kconfig files for ADMtek, Atheros, Atmel, Broadcom, Intel, Intersil, Marvell, MediaTek, Microchip, pureLiFi, Ralink, Realtek, RSI, Silicon Labs, ST, TI, Zydas, Quantenna, and virtual wireless drivers.

Control flow: Kconfig evaluation exposes the WLAN menu only when dependencies are satisfied. Vendor submenus and virtual drivers are included only when `WLAN` is enabled.

State and persistence: Build-time configuration only; no runtime state.

Dependencies and integration points: Integrates with the kernel Kconfig system and `drivers/net/wireless/Makefile` object selection. Vendor files define concrete driver symbols such as `ADM8211`.

Risks: Missing or reordered `source` lines hide entire vendor driver families. `default y` makes WLAN options broadly visible, increasing config surface. Dependency changes can affect many wireless drivers.

Test signals: `make menuconfig`/`oldconfig` visibility, all sourced vendor Kconfig paths existing, and build matrix with `CONFIG_WLAN=y/n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/Makefile

Purpose: Selects wireless vendor subdirectories for compilation based on Kconfig symbols.

Important APIs and definitions: Adds vendor directories to `obj-y`/`obj-m` through `obj-$(CONFIG_WLAN_VENDOR_*) += <vendor>/`, including `admtek/`, `ath/`, `broadcom/`, `intel/`, and others. Adds `virtual/` when `CONFIG_WLAN` is enabled.

Control flow: Kbuild descends into each enabled vendor directory and into virtual wireless drivers when WLAN is enabled.

State and persistence: Build-time only; no runtime state.

Dependencies and integration points: Mirrors the top-level wireless Kconfig vendor list and relies on each subdirectory Makefile to map concrete driver symbols to objects.

Risks: Kconfig/Makefile drift can expose a config option that never builds, or build a directory with no visible config. Vendor ordering can affect link order for built-in objects.

Test signals: Build with representative vendor symbols enabled/disabled, `make drivers/net/wireless/`, and consistency check against Kconfig sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/admtek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/admtek/Kconfig

Purpose: Defines ADMtek wireless vendor selection and the ADM8211 PCI 802.11b driver configuration option.

Important APIs and definitions: `config WLAN_VENDOR_ADMTEK` is a bool vendor gate, default y. Under it, `config ADM8211` is a tristate depending on `MAC80211 && PCI`, selecting `CRC32` and `EEPROM_93CX6`. Help text lists supported ADM8211A/B/C cards and notes some model-number chip substitutions.

Control flow: The ADM8211 option is visible only when the vendor gate is enabled. Selecting ADM8211 pulls required CRC and EEPROM helpers and allows built-in or module builds.

State and persistence: Build-time configuration only.

Dependencies and integration points: Controls `drivers/net/wireless/admtek/Makefile`, which builds `adm8211.o`. Runtime driver integrates with PCI and mac80211.

Risks: Missing dependencies would cause link/build failures; inaccurate help text could lead users to select the wrong driver for rebranded cards. Vendor gate set to `n` hides the driver entirely.

Test signals: Kconfig visibility with `MAC80211`/`PCI` on and off, module and built-in builds, and dependency auto-selection for `CRC32` and `EEPROM_93CX6`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/admtek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/admtek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/admtek/Makefile

Purpose: Builds the ADMtek ADM8211 wireless driver object when its Kconfig symbol is enabled.

Important APIs and definitions: `obj-$(CONFIG_ADM8211) += adm8211.o`.

Control flow: Kbuild compiles and links `adm8211.c` into the kernel or module when `CONFIG_ADM8211=y/m`.

State and persistence: Build-time only.

Dependencies and integration points: Driven by `admtek/Kconfig` and reached via the top-level wireless Makefile.

Risks: Minimal; filename or symbol drift would silently break builds for this driver.

Test signals: `CONFIG_ADM8211=m` produces `adm8211.ko`; `CONFIG_ADM8211=y` links built-in object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/admtek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/admtek/adm8211.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/admtek/adm8211.c

Purpose: Implements a PCI/mac80211 driver for ADMtek ADM8211 802.11b wireless chips, covering PCI probe/remove, EEPROM parsing, RF/BBP programming, DMA ring setup, interrupt-driven RX/TX, mac80211 callbacks, filtering, channel/rate setup, and transmit header construction.

Important APIs and functions: PCI/module entry uses `adm8211_driver` and `module_pci_driver()`. Probe/remove are `adm8211_probe()` and `adm8211_remove()`. mac80211 ops include `adm8211_start()`, `adm8211_stop()`, `adm8211_tx()`, `adm8211_add_interface()`, `adm8211_remove_interface()`, `adm8211_config()`, `adm8211_bss_info_changed()`, `adm8211_prepare_multicast()`, `adm8211_configure_filter()`, `adm8211_get_stats()`, and `adm8211_get_tsft()`. Hardware helpers cover EEPROM access, SRAM writes, ring alloc/init/free, interrupt service, BBP writes, RF synthesizer writes, RF channel setting, mode updates, rate/beacon setup, hardware reset/init, duration/PLCP calculation, and raw TX descriptor submission.

Control flow: Probe enables PCI, validates resources/signature, requests regions, sets DMA mask/mastering, allocates `ieee80211_hw`, maps BARs, allocates coherent RX/TX descriptors and buffer metadata, reads permanent MAC and EEPROM-derived RF/BBP/channel/power data, configures mac80211 capabilities, and registers hardware. Start resets hardware, initializes rings, programs MAC/RF/BBP and channel, requests IRQ, enables interrupts, enters monitor mode, starts RX, and sets beacon/listen interval. Interrupt handler acknowledges status, services RX completions by recycling or replacing DMA buffers and passing skbs to mac80211, and services TX completions by unmapping DMA, restoring 802.11 headers, setting ACK status, and waking queues. TX builds ADM8211 extended headers from mac80211 skb metadata, calculates PLCP/duration, maps DMA, fills descriptors, and kicks hardware. Stop disables RX/TX/interrupts, frees IRQ, and frees rings. Remove unregisters mac80211 and releases DMA, EEPROM, mappings, regions, and PCI device.

State and persistence: Per-device private state includes PCI device, MMIO/IO mapping, EEPROM contents/length, RF/BBP/transceiver selections, channel table/band, current channel/mode/NAR bits, BSSID, soft RX CRC mode, stats, ring sizes, coherent descriptor rings, DMA addresses, RX/TX buffer arrays, ring cursors `cur_rx`, `cur_tx`, `dirty_tx`, power/calibration defaults, retry limits, and spinlock. Runtime hardware state persists in ADM8211 registers/SRAM until reset/stop.

Dependencies and integration points: Integrates with PCI core, DMA API, mac80211, EEPROM 93cx6 helper, CRC32 multicast filtering, ADM8211 register/header definitions in `adm8211.h`, RF transceiver-specific programming tables, and kernel IRQ/skb APIs.

Risks: DMA ring ownership and cursor arithmetic are central; incorrect descriptor flags can wedge RX/TX. RX buffer replacement handles DMA mapping failure by dropping and may leave descriptor state sensitive. TX queue stop threshold uses `tx_ring_size - 2`; small module-param ring sizes could break assumptions if not validated elsewhere. RF/BBP programming is revision/transceiver-specific and has many magic constants. Probe error unwind has many stages and one `pci_request_regions()` failure returns without disabling the PCI device. Suspend/resume are NULL. Several TODOs note missing RX error/drop stats and uncertain hardware behavior.

Test signals: PCI probe/remove on ADM8211A/B/C IDs, invalid signature/resource failures, EEPROM 93C46/93C66 parsing and unknown RF/BBP fallback, start/stop cycles, IRQ RX/TX completion, DMA mapping failure injection, channel changes across 1-14 for all supported transceivers, station interface add/remove, multicast filter and promisc/FCS modes, BSSID updates, TX ACK status, queue stop/wake, hardware reset timeout, and module-param ring size edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/admtek/adm8211.c -->

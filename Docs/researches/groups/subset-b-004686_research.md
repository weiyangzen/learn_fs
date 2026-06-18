# subset-b-004686 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/netlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/netlink.c

Purpose: Implements the OpenVPN data-channel generic-netlink control plane. It maps userspace requests onto `ovpn_priv` devices, peers, sockets, endpoint bindings, and crypto key slots, and emits multicast notifications for peer deletion, endpoint floating, and key-renewal needs.

Important APIs, types, and functions: `ovpn_nl_pre_doit()`/`ovpn_nl_post_doit()` acquire and release the target ovpn netdev reference through `OVPN_A_IFINDEX`. Peer commands are handled by `ovpn_nl_peer_new_doit()`, `ovpn_nl_peer_set_doit()`, `ovpn_nl_peer_get_doit()`, `ovpn_nl_peer_get_dumpit()`, and `ovpn_nl_peer_del_doit()`. Key commands are handled by `ovpn_nl_key_new_doit()`, `ovpn_nl_key_get_doit()`, `ovpn_nl_key_swap_doit()`, and `ovpn_nl_key_del_doit()`. Notification helpers are `ovpn_nl_peer_del_notify()`, `ovpn_nl_peer_float_notify()`, and `ovpn_nl_key_swap_notify()`. `ovpn_nl_register()`/`ovpn_nl_unregister()` register the generated `ovpn_nl_family`.

Control flow: Requests first validate the netdev and nested attributes, then convert netlink sockaddr/key attributes into kernel objects. New peers allocate `ovpn_peer`, look up a userspace socket fd, enforce UDP endpoint presence and TCP endpoint absence, wrap the socket with `ovpn_socket_new()`, apply mutable attributes, and finally hash the peer through `ovpn_peer_add()`. Set commands reject socket replacement, update endpoint/TX ID/VPN IP/keepalive state, and rehash VPN addresses when needed. Get and dump commands serialize peers and stats into nested attributes. Key install parses cipher directions, installs a crypto slot, and key swap/delete delegates to crypto helpers.

State and persistence behavior: This file persists no storage itself; it mutates in-memory peer tables, `peer->bind`, `peer->tx_id`, VPN address fields, keepalive timers, socket references, and `peer->crypto`. Netdev references are held across doit handlers via `netdevice_tracker`. Peer and socket references are paired on error paths so half-created peers are released before they become visible.

Dependencies and integration points: It depends on the generated netlink policies/family in `netlink-gen.[ch]`, UAPI `linux/ovpn.h`, `ovpn_dev_is_valid()`, peer/socket/bind/crypto helpers, and generic-netlink extack reporting. It integrates with network namespaces for socket netns IDs and multicasts events in the namespace owning the peer socket.

Risks and edge cases: Address family normalization includes IPv4-mapped IPv6 handling and must stay consistent between local and remote attributes. TCP and UDP transport semantics differ sharply; accepting a remote endpoint for TCP or missing one for UDP is rejected. `ovpn_nl_send_peer()` reads socket and bind state under RCU in separate windows, so serialization must tolerate endpoint changes. Error paths after socket wrapping must release both peer and socket once. GET commands open-code unexpected-attribute rejection because policy alone cannot express the exact command shape.

Test signals: Exercise peer create/set/get/dump/delete in P2P and MP modes; UDP create without remote endpoint; TCP create with remote endpoint; IPv4, IPv6, and v4-mapped-v6 endpoint/local combinations; VPN IP rehash after set; keepalive pair validation; socket fd lookup failures; cross-netns socket reporting; key install/get/swap/delete for both slots; multicast peer delete/float/key notifications; and forced allocation/EMSGSIZE failures during reply generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/netlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/netlink.h

Purpose: Declares the ovpn module's public netlink hooks used outside `netlink.c`.

Important APIs, types, and functions: The header exposes `ovpn_nl_register()` and `ovpn_nl_unregister()` for module initialization/cleanup, plus notification helpers `ovpn_nl_peer_del_notify()`, `ovpn_nl_peer_float_notify()`, and `ovpn_nl_key_swap_notify()`. It forward-relies on `struct ovpn_peer`, `struct sockaddr_storage`, and `u8` being visible through includers.

Control flow: Main module setup calls the register/unregister pair around generic-netlink family lifetime. Peer-management code calls delete and float notifications after state changes. Crypto/data-path code can call key-swap notification when a primary key becomes unusable.

State and persistence behavior: No state is defined here. The declarations are entry points into netlink multicast and registration code that acts on runtime peer/socket state.

Dependencies and integration points: This header ties peer lifetime and crypto state transitions to the generic-netlink userspace ABI in `linux/ovpn.h`. It is included by peer and module code that must report kernel-side events to OpenVPN userspace.

Risks and edge cases: Callers must hold or otherwise own a valid peer reference while notifying because the implementation reads peer fields and RCU-protected socket state. Notification failures are non-fatal but should be visible to tests because userspace may rely on them to clean up or rekey.

Test signals: Build tests should catch missing type includes in includers. Runtime signals are successful generic-netlink family registration, teardown without stale family objects, and multicast notifications for peer expiry, userspace deletion, transport disconnect, floating, and key renewal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/ovpnpriv.h -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/ovpnpriv.h

Purpose: Defines the private per-interface OpenVPN state and the multi-peer hash-table container used by the driver.

Important APIs, types, and functions: `struct ovpn_peer_collection` contains the MP-mode lookup tables: `by_id`, `by_vpn_addr4`, `by_vpn_addr6`, and `by_transp_addr`. `struct ovpn_priv` stores the netdev pointer, `enum ovpn_mode`, a spinlock protecting writes, MP-mode peer collection, P2P single-peer RCU pointer, GRO cells, and global delayed keepalive work.

Control flow: Netdev creation initializes `ovpn_priv`, P2P mode uses `ovpn->peer`, and MP mode allocates `ovpn->peers`. Peer add/delete, packet RX/TX lookup, netlink dump, and keepalive scans use these members to locate peers or iterate all peers.

State and persistence behavior: All fields are runtime-only and rebuilt with the netdev. `ovpn->lock` protects table mutations and P2P peer replacement. Peer pointers are RCU-protected so data path readers can operate without taking the writer lock.

Dependencies and integration points: It depends on kernel workqueues, GRO cells, link UAPI mode enums, and ovpn UAPI definitions. It is the shared state contract among netlink, peer, socket, transport, I/O, and main netdev code.

Risks and edge cases: The MP hash arrays have fixed size and include nulls-list heads for address tables, so lookup/restart logic must preserve nulls values during rehash. Callers must honor the mode distinction: using `peers` in P2P or `peer` in MP will break lookups and teardown. Keepalive work must not rearm after netdev teardown.

Test signals: Verify P2P and MP netdev creation, MP hash initialization, peer replacement in P2P, concurrent peer lookup during delete, GRO receive delivery, delayed keepalive scheduling/cancellation, and teardown with non-empty peer tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/ovpnpriv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/peer.c -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/peer.c

Purpose: Implements ovpn peer allocation, reference lifetime, P2P/MP peer tables, endpoint binding and floating, destination/source peer selection, teardown, and keepalive timeout/transmit scheduling.

Important APIs, types, and functions: Creation and lifetime are `ovpn_peer_new()`, `ovpn_peer_release()`, and `ovpn_peer_release_kref()`. Mutable endpoint state is handled by `ovpn_peer_reset_sockaddr()` and `ovpn_peer_endpoints_update()`. Lookup APIs include `ovpn_peer_get_by_transp_addr()`, `ovpn_peer_get_by_id()`, `ovpn_peer_get_by_dst()`, and `ovpn_peer_check_by_src()`. Table operations are `ovpn_peer_add()`, `ovpn_peer_del()`, `ovpn_peers_free()`, and `ovpn_peer_hash_vpn_ip()`. Keepalive is configured and run by `ovpn_peer_keepalive_set()` and `ovpn_peer_keepalive_work()`.

Control flow: New peers initialize IDs, crypto, stats, locks, dst cache, dev reference, and keepalive work. MP add inserts by peer ID, transport address, and VPN IP; P2P add replaces the old single peer and toggles carrier. RX endpoint update learns local addresses and detects UDP peer floating, resets bind/dst cache, emits a netlink float event, and rehashes transport address in MP mode. TX lookup uses the single P2P peer or MP VPN next-hop hashes; source checks perform reverse-route lookup. Delete removes visible table entries, sends delete notification, then defers socket release/ref drops until after `ovpn->lock` is released.

State and persistence behavior: Peer state is in memory and protected by a mix of `ovpn->lock`, `peer->lock`, RCU, kref, and delayed work. `peer->bind` and `peer->sock` are RCU pointers. The dst cache is destroyed only after an RCU grace period. Keepalive tracks `last_sent`, `last_recv`, future expiry timestamps, and removes expired peers.

Dependencies and integration points: This file depends on bind, crypto, pktid, netlink, socket, route lookup, IPv6 route support, workqueues, netdev carrier, and I/O keepalive transmit helpers. Packet paths in UDP/TCP and tunnel TX call these lookup/update helpers.

Risks and edge cases: Lock ordering between ovpn and peer locks is important during floating and rehash. Releasing sockets while holding table locks could sleep, so the release list is essential. Nulls-list lookup must restart when entries move. P2P replacement deletes the old peer with a teardown reason and may race readers. Keepalive scheduling uses wall-clock seconds and must avoid negative delays if time moves unexpectedly. A likely bug signal is `memset(dt_val, ..., sizeof(*dt_val))`-style mistakes elsewhere; here allocations are explicit and peer tables rely on initialized hash/nulls nodes from zero allocation.

Test signals: Cover MP duplicate peer IDs, TCP peers without bind, UDP transport lookup by peer ID and by undefined peer ID/source address, IPv4/IPv6 VPN destination lookup with gateways, source reverse-path checks, endpoint floating and rehash, P2P carrier on/off, concurrent delete/lookup, device teardown filtering by socket, keepalive send and expiry, and RCU/kref leak detection under stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/peer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/peer.h -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/peer.h

Purpose: Defines the main ovpn peer object and exports peer-management APIs used by netlink, transport, crypto, and packet I/O code.

Important APIs, types, and functions: `struct ovpn_peer` carries the owning `ovpn_priv`, peer/TX IDs, VPN IPv4/IPv6 addresses, hash nodes, RCU socket and bind pointers, TCP-specific parser/queues/callback backups, crypto state, dst cache, keepalive timers, stats, delete reason, spinlock, kref, RCU head, release-list node, and keepalive work. Inline `ovpn_peer_hold()` and `ovpn_peer_put()` manage references. Public functions cover create/add/delete/free, lookups by transport/ID/destination, VPN-IP rehash, source validation, keepalive, endpoint update, and sockaddr reset.

Control flow: Callers allocate a peer through `ovpn_peer_new()`, attach a socket and bind through netlink/socket helpers, add it to the appropriate P2P or MP table, then use reference-taking lookup APIs from data paths. Delete removes the peer from visible state; final freeing happens after refs and RCU readers drain.

State and persistence behavior: The struct is the central runtime persistence unit for a remote OpenVPN peer. It is not durable across device teardown. Several members are only meaningful for TCP, but share storage inside every peer so TCP transport can override socket callbacks and buffer in-flight stream data.

Dependencies and integration points: It depends on dst cache, stream parser, crypto, socket, stats, netdev reference tracking, bind definitions via users of the pointer, and UAPI delete reasons. It integrates directly with phasing in `netlink.c`, transport send/receive, and keepalive work.

Risks and edge cases: Users must not dereference `sock` or `bind` without RCU or protected locks. `peer->lock` protects bind and keepalive fields, while `ovpn->lock` protects global visibility and hashes; mixing them incorrectly can deadlock or expose stale hash entries. TCP callback backup fields must be restored exactly once.

Test signals: Compile with TCP and UDP paths, create/release peers under KASAN/KCSAN, validate refcount behavior on lookup/delete races, ensure TCP queues are purged on detach, and check keepalive/delete reason propagation through netlink notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/peer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/pktid.c -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/pktid.c

Purpose: Implements transmit packet-ID initialization and receive replay-window validation for OpenVPN AEAD packet IDs.

Important APIs, types, and functions: `ovpn_pktid_xmit_init()` initializes transmit sequence numbers to 1. `ovpn_pktid_recv_init()` clears receive state and initializes its spinlock. `ovpn_pktid_recv()` validates a `(pkt_id, pkt_time)` pair against monotonic time, zero-ID rejection, a sliding replay bitmap, and an expiry-driven floor.

Control flow: Receive validation locks the packet-ID state, expires old backtrack acceptance by raising `id_floor`, resets the replay window when packet time moves forward, rejects time rollback, accepts strict next IDs, handles forward jumps by clearing skipped bitmap positions, and handles backtracks only if inside the retained window, above `id_floor`, and not already seen.

State and persistence behavior: State lives in `struct ovpn_pktid_recv` inside a crypto key slot and is runtime-only. `expire` uses jiffies to narrow the acceptable backtrack range after `PKTID_RECV_EXPIRE`. `max_backtrack` records observed replay depth for diagnostics even though it is not exported here.

Dependencies and integration points: It depends on atomic/jiffies/spinlock primitives and protocol nonce sizing from `pktid.h`/`proto.h`. Crypto decrypt paths use this to prevent replay before accepting data-channel packets.

Risks and edge cases: Sequence ID zero is invalid and transmit wrap must force key renewal elsewhere. Time rollback is rejected, so userspace/key time generation must be monotonic per key. The bitmap math relies on power-of-two `REPLAY_WINDOW_SIZE`. Expiry updates `id_floor` only when validation runs, not by timer.

Test signals: Unit-style tests should cover zero ID, in-order sequences, forward jumps smaller/larger than the window, duplicate backtracks, backtracks below the floor after expiry, packet-time advance reset, packet-time rollback rejection, and concurrent receive validation under softirq context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/pktid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/pktid.h -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/pktid.h

Purpose: Defines OpenVPN packet-ID transmit/receive state, replay-window constants, and nonce construction helpers.

Important APIs, types, and functions: `struct ovpn_pktid_xmit` contains an atomic sequence number. `struct ovpn_pktid_recv` contains the replay bitmap, base/extent, expiry, highest ID/time, floor, max backtrack, and lock. `ovpn_pktid_xmit_next()` atomically allocates the next ID and rejects wrap to zero. `ovpn_pktid_aead_write()` writes the 12-byte AEAD IV as 4-byte packet ID plus 8-byte nonce tail. `PKTID_RECV_EXPIRE`, `REPLAY_WINDOW_ORDER`, `REPLAY_WINDOW_BYTES`, `REPLAY_WINDOW_SIZE`, and `REPLAY_INDEX()` describe replay tracking.

Control flow: TX callers request an ID before encryption and use it to build nonce material. RX callers initialize per-key replay state and call `ovpn_pktid_recv()` after parsing/decrypting packet ID/time material.

State and persistence behavior: Packet-ID state is per key slot and runtime-only. It must reset on key install to avoid nonce reuse or replay-state bleed between key generations.

Dependencies and integration points: It depends on `proto.h` for nonce size constants and kernel bitmap/atomic/spinlock APIs through included headers. Crypto AEAD code depends on the IV layout matching OpenVPN's wire format.

Risks and edge cases: Reusing a TX packet ID with the same nonce tail and key is catastrophic for AEAD, so `-ERANGE` on wrap must trigger key rotation/drop. `ovpn_pktid_aead_write()` assumes destination space is at least `OVPN_NONCE_SIZE`. The replay window size and index mask require power-of-two sizing.

Test signals: Validate nonce byte order, packet-ID wrap behavior, per-key reset, replay-window macros, and AEAD encryption/decryption interoperability with userspace OpenVPN test vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/pktid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/proto.h -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/proto.h

Purpose: Captures OpenVPN data-channel wire constants and inline helpers for opcode, key ID, peer ID, and AEAD nonce formatting.

Important APIs, types, and functions: Constants include `OVPN_NONCE_SIZE`, `OVPN_NONCE_TAIL_SIZE`, `OVPN_NONCE_WIRE_SIZE`, `OVPN_OPCODE_SIZE`, opcode field masks, `OVPN_DATA_V1`, `OVPN_DATA_V2`, and `OVPN_PEER_ID_UNDEF`. Inline helpers are `ovpn_opcode_from_skb()`, `ovpn_peer_id_from_skb()`, `ovpn_key_id_from_skb()`, and `ovpn_opcode_compose()`.

Control flow: UDP/TCP receive paths pull enough bytes, use `ovpn_opcode_from_skb()` to accept kernel-handled `DATA_V2`, reject `DATA_V1`, or forward control packets to userspace. Decrypt paths use key ID extraction. TX paths compose a 32-bit opcode word containing packet type, key ID, and peer ID.

State and persistence behavior: No mutable state. This header defines a stable in-kernel representation of the OpenVPN wire bit layout.

Dependencies and integration points: It depends on bitfield helpers and skbuff access. It is shared by packet I/O, transports, crypto, and packet-ID nonce helpers.

Risks and edge cases: The inline readers assume the caller has already pulled at least four bytes into linear skb data. Misaligned direct `__be32` casts rely on kernel architectures tolerating the access pattern used elsewhere. Field masks must match UAPI/wire protocol; changing them breaks interoperability.

Test signals: Use packet fixtures for DATA_V1, DATA_V2, undefined peer ID, multiple key IDs, and peer-ID boundaries. Verify compose/extract round trips and non-linear skb paths that first call the expected pull helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/skb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/skb.h

Purpose: Defines ovpn-specific skbuff control-block state and an IP-version validation helper.

Important APIs, types, and functions: `struct ovpn_cb` overlays `skb->cb` with `peer`, `ks`, `crypto_tmp`, `payload_offset`, and TCP `nosignal` metadata. `ovpn_skb_cb()` returns the overlay and enforces size at build time. `ovpn_ip_check_protocol()` pulls enough network header data and returns `ETH_P_IP`, `ETH_P_IPV6`, or zero.

Control flow: Crypto and transport paths stash peer/key/temp state in the skb control block while packets move asynchronously through encryption/decryption and TCP send. TX/RX logic uses `ovpn_ip_check_protocol()` before routing or accepting inner packets.

State and persistence behavior: Control-block data is per skb and transient. It must be cleared or not assumed once packets are handed to userspace or foreign networking layers.

Dependencies and integration points: It depends on skbuff, IPv4/IPv6 header helpers, socket types, and ovpn peer/crypto types through pointers. TCP receive explicitly clears `skb->cb` before queuing non-data packets to userspace.

Risks and edge cases: Any other subsystem reusing `skb->cb` can clobber ovpn metadata; handoff boundaries must be clear. Non-linear skbs require the pull checks in `ovpn_ip_check_protocol()`. The helper checks `ip_hdr(skb)->version`, so callers must have set the network header first.

Test signals: Check nonlinear IPv4/IPv6 skbs, too-short headers, unknown IP versions, control-block size build checks, async crypto completion preserving metadata, and userspace-forwarded TCP control packets not leaking ovpn private cb contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/skb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/socket.c -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/socket.c

Purpose: Wraps user-provided TCP/UDP sockets in `struct ovpn_socket`, attaches transport-specific callbacks, and manages shared socket lifetime.

Important APIs, types, and functions: `ovpn_socket_new()` validates ownership and attaches sockets. `ovpn_socket_release()` detaches a peer from its socket, drops references, waits for TCP work, and frees the wrapper when the kref reaches zero. Internal helpers include `ovpn_socket_release_kref()`, `ovpn_socket_put()`, `ovpn_socket_hold()`, and `ovpn_socket_attach()`.

Control flow: Netlink passes a looked-up socket to `ovpn_socket_new()`. TCP sockets must be unowned and become unique to one peer. UDP sockets may already be owned by the same ovpn instance, in which case the wrapper kref is incremented for sharing. A new wrapper stores either the peer (TCP) or ovpn instance and dev tracker (UDP), takes a sock reference, and calls `ovpn_tcp_socket_attach()` or `ovpn_udp_socket_attach()`. Release swaps `peer->sock` to NULL, drops wrapper kref under the socket lock, synchronizes RCU readers, then performs transport-specific final cleanup.

State and persistence behavior: `struct ovpn_socket` is runtime state anchored in `sk_user_data` and peer RCU pointers. UDP wrappers hold a netdev reference while shared; TCP wrappers hold a peer reference and work item.

Dependencies and integration points: It depends on UDP and TCP transport attach/detach implementations, socket locks, RCU `sk_user_data`, netdev reference tracking, and krefs. Netlink owns socket fd lookup; this layer owns encapsulation state.

Risks and edge cases: UDP `ovpn_udp_socket_attach()` can return `-EALREADY` when the same instance already owns the socket; the caller treats an already-held wrapper as success before attach. Release must avoid racing a new attach against a partially detached socket, hence the socket lock and RCU sync. TCP cleanup can sleep and therefore is intentionally outside global peer locks.

Test signals: Test TCP double-attach `-EBUSY`, UDP sharing across peers in one instance, UDP sharing across instances rejected, unknown protocols rejected, release after transport-side detach, concurrent new/release on same socket, TCP work cancellation, and sock/netdev/peer refcount balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/socket.h -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/socket.h

Purpose: Defines the ovpn socket wrapper shared by peer management and TCP/UDP transport code.

Important APIs, types, and functions: `struct ovpn_socket` contains either UDP owner state (`ovpn_priv *ovpn` plus netdev tracker) or TCP owner state (`ovpn_peer *peer`), the underlying `struct sock *sk`, a kref, a generic work item, and a TCP TX work item. The public APIs are `ovpn_socket_new()` and `ovpn_socket_release()`.

Control flow: Netlink creates wrappers from socket fds during peer creation. Peer deletion calls `ovpn_socket_release()` exactly once for the peer. TCP/UDP detach functions are selected from the socket protocol.

State and persistence behavior: The wrapper persists while at least one peer references a UDP socket or while a TCP peer owns a connected socket. It is freed after detach, RCU reader synchronization, and reference drops.

Dependencies and integration points: It depends on kernel socket, kref, and sock APIs. It is included by peer and transport headers, making it the bridge between peer lifetime and socket callback ownership.

Risks and edge cases: The union means callers must branch on `sk_protocol` before interpreting `ovpn` versus `peer`. `work` is documented but not actively used in this subset, while `tcp_tx_work` is transport-specific. Releasing a wrapper twice would corrupt socket ownership, so peer deletion must be idempotent.

Test signals: Build tests for both transports, static analysis for union misuse, runtime refcount checks for UDP multi-peer sharing and TCP single-peer ownership, and teardown while TX work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/stats.c -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/stats.c

Purpose: Provides initialization for per-peer ovpn packet/byte counters.

Important APIs, types, and functions: `ovpn_peer_stats_init()` sets RX/TX byte and packet atomic64 counters to zero for a `struct ovpn_peer_stats`.

Control flow: Peer allocation calls this initializer for VPN and link stats before the peer becomes visible. Data paths later increment counters through inline helpers in `stats.h`; netlink serializes their current values in peer get/dump responses.

State and persistence behavior: The counters are per-peer runtime state and reset with peer recreation or key/session reconfiguration that allocates a new peer.

Dependencies and integration points: It depends on Linux atomic64 and the declarations in `stats.h`. It integrates with netlink telemetry and data-path accounting.

Risks and edge cases: Counters are atomic but not snapshot-consistent across multiple fields, so netlink can report bytes/packets from slightly different moments. Initialization must run before any packet path can increment.

Test signals: Create peers and verify zeroed stats; send/receive data and validate increments; dump stats during concurrent traffic; and run on 32-bit builds where atomic64 support is more sensitive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/stats.h -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/stats.h

Purpose: Defines per-peer ovpn statistics structures and inline counter update helpers.

Important APIs, types, and functions: `struct ovpn_peer_stat` stores atomic64 `bytes` and `packets`. `struct ovpn_peer_stats` groups RX and TX stats. `ovpn_peer_stats_increment()`, `ovpn_peer_stats_increment_rx()`, and `ovpn_peer_stats_increment_tx()` update byte and packet counters.

Control flow: Data paths call the inline helpers after successful VPN or link RX/TX operations. Netlink reads counters for peer reports.

State and persistence behavior: Stats are in-memory per-peer counters. They are monotonic for the peer lifetime and reset on peer recreation.

Dependencies and integration points: It relies on atomic64 operations and is embedded in `struct ovpn_peer` for both inner VPN accounting and outer transport accounting.

Risks and edge cases: Packet and byte increments are not a single atomic transaction. Callers must pass the correct length category to avoid mixing encrypted transport bytes with decrypted VPN bytes. Drops are accounted through netdev dstats elsewhere, not here.

Test signals: Validate RX/TX counters under UDP/TCP traffic, confirm no increment on failed decrypt or failed transmit, and compare netlink stats with expected packet sizes in both VPN and link layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/tcp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/tcp.c

Purpose: Implements OpenVPN-over-TCP socket integration, including stream framing, userspace control packet delivery, kernel data packet receive, TCP send buffering, callback replacement, and transport-error peer deletion.

Important APIs, types, and functions: `ovpn_tcp_init()` builds cloned IPv4/IPv6 proto/proto_ops tables. `ovpn_tcp_socket_attach()`, `ovpn_tcp_socket_detach()`, and `ovpn_tcp_socket_wait_finish()` own socket callback lifetime. RX framing uses `ovpn_tcp_parse()` and `ovpn_tcp_rcv()` with `strparser`. Userspace I/O is `ovpn_tcp_recvmsg()` and `ovpn_tcp_sendmsg()`. Kernel TX uses `ovpn_tcp_send_skb()`, `ovpn_tcp_tx_work()`, and `ovpn_tcp_release()`. Close/poll/write callbacks are `ovpn_tcp_close()`, `ovpn_tcp_poll()`, `ovpn_tcp_data_ready()`, and `ovpn_tcp_write_space()`.

Control flow: Attach requires an established, unowned TCP socket, installs `sk_user_data`, initializes strparser, saves original callbacks/proto/ops, then replaces them with ovpn variants. Incoming stream data is parsed by a 16-bit length prefix. `DATA_V2` frames are handed to `ovpn_recv()` with a peer reference; other non-`DATA_V1` frames are re-prefixed and queued for userspace `recvmsg()`. Outgoing packets are prefixed with length and either sent immediately under socket lock, queued while userspace owns the socket, or retried by write-space/TX work.

State and persistence behavior: TCP peer state includes strparser, userspace queue, deferred out queue, current partially sent skb and offset/length, callback backups, and a deferred-delete work item. This state lasts for the peer/socket lifetime and is purged on detach.

Dependencies and integration points: It depends on TCP internals, `strparser`, cloned proto tables, socket callbacks, `ovpn_recv()`, `ovpn_peer_del()`, and netdev dynamic stats. It is selected by `socket.c` for `IPPROTO_TCP`.

Risks and edge cases: TCP is a stream, so malformed length fields or too-small frames require peer deletion. Partial sends must not duplicate or lose bytes. Callback replacement must be restored even if close races detach. `release_cb` and nested socket locks need the custom lockdep subclass. Userspace `sendmsg()` supports only `MSG_DONTWAIT` and `MSG_NOSIGNAL`. Transport errors intentionally kill the peer because the stream cannot be resynchronized.

Test signals: Test established-state requirement, length framing across fragmented TCP receives, control packet forwarding to userspace, DATA_V1 rejection, partial send and `EAGAIN` retry, out_queue backlog limit, close/disconnect behavior, poll over user_queue, IPv6 build path, callback restoration on detach, and race tests for close/write_space/release_cb/delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/tcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/tcp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/tcp.h

Purpose: Declares the ovpn TCP transport API used by socket wrapping and packet transmit code.

Important APIs, types, and functions: The header declares `ovpn_tcp_init()`, `ovpn_tcp_socket_attach()`, `ovpn_tcp_socket_detach()`, `ovpn_tcp_socket_wait_finish()`, `ovpn_tcp_send_skb()`, and `ovpn_tcp_tx_work()`. It includes peer, skb, and socket definitions because TCP state is embedded in `struct ovpn_peer` and work is embedded in `struct ovpn_socket`.

Control flow: Module initialization calls `ovpn_tcp_init()` before TCP sockets can be attached. `socket.c` calls attach/detach/wait during socket lifetime. Crypto/TX completion calls `ovpn_tcp_send_skb()` to prepend the OpenVPN stream length and send/enqueue the skb. Socket write-space schedules `ovpn_tcp_tx_work()`.

State and persistence behavior: No state is defined here directly; declarations operate on per-peer TCP queues and per-socket TX work.

Dependencies and integration points: It integrates ovpn with Linux TCP proto/proto_ops replacement and the shared skbuff control block.

Risks and edge cases: `ovpn_tcp_send_skb()` expects enough headroom for the 2-byte length prefix. Attach/detach must be paired once per TCP wrapper. Header include cycles are possible because `peer.h` includes `socket.h`; build coverage catches ordering issues.

Test signals: Build TCP-enabled ovpn, validate headroom assumptions in encrypted TX, and test attach/detach/send under both IPv4 and IPv6 sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/udp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/udp.c

Purpose: Implements OpenVPN-over-UDP socket encapsulation receive, peer lookup, UDP tunnel transmit, endpoint route caching, and UDP socket attach/detach.

Important APIs, types, and functions: `ovpn_udp_socket_attach()` installs `setup_udp_tunnel_sock()` callbacks, `ovpn_udp_socket_detach()` clears them, and `ovpn_udp_send_skb()` sends encrypted skbs. RX starts in `ovpn_udp_encap_recv()`. TX helpers are `ovpn_udp_output()`, `ovpn_udp4_output()`, and IPv6-only `ovpn_udp6_output()`. `ovpn_udp_encap_destroy()` removes peers using a closing socket.

Control flow: UDP receive verifies the socket is owned by ovpn, pulls UDP header plus opcode, drops unsupported DATA_V1, passes non-DATA_V2 packets to userspace, and for DATA_V2 looks up the peer by embedded peer ID or by source transport address when the peer ID is undefined. It then strips the outer UDP header and calls `ovpn_recv()`. TX sets skb device/mark/checksum state, reads the peer bind under RCU, obtains or refreshes a cached route, and uses UDP tunnel helpers to emit IPv4/IPv6 packets.

State and persistence behavior: UDP socket ownership is stored in `sk_user_data` and UDP encap fields. Per-peer `dst_cache` stores route and source address. `bind->local` can be reset when cached local addresses become invalid. UDP socket wrappers may be shared by multiple peers in the same ovpn instance.

Dependencies and integration points: It depends on UDP tunnel infrastructure, route lookup, IPv6 address validation when enabled, bind matching, peer lookup/update, and ovpn receive code. Netlink provides the initial UDP endpoint binding.

Risks and edge cases: DATA_V2 packets with undefined peer IDs rely entirely on transport address lookup, so floating/rehash correctness matters. Route cache source addresses can become invalid and must be reset. IPv6 scoped addresses feed `flowi6_oif`. Detach must restore UDP socket state, including multicast loopback and checksum conversion. `ovpn_udp_socket_attach()` returning `-EALREADY` is meaningful to wrapper sharing logic.

Test signals: Cover DATA_V2 receive by ID and by transport address, DATA_V1 drop, control packet userspace pass-through, short skb drop, IPv4/IPv6 TX route cache hits/misses, local address invalidation, peer floating, socket close removing only peers using that socket, shared UDP socket across peers, and detach restoring UDP fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/udp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/udp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/udp.h

Purpose: Declares the ovpn UDP transport API used by socket wrapping and packet transmit code.

Important APIs, types, and functions: `ovpn_udp_socket_attach()` links an ovpn socket wrapper and kernel socket to an ovpn instance. `ovpn_udp_socket_detach()` removes UDP tunnel callbacks. `ovpn_udp_send_skb()` transmits an encrypted skb to a peer over the associated UDP socket.

Control flow: `socket.c` calls attach/detach according to `sk_protocol`. The crypto/TX path calls `ovpn_udp_send_skb()` after encryption has produced an outer OpenVPN packet.

State and persistence behavior: No state is defined here; functions operate on `struct ovpn_socket`, `struct ovpn_priv`, `struct ovpn_peer`, and `struct sock` runtime objects.

Dependencies and integration points: It depends on the kernel socket layer and the ovpn peer/socket types. It is the UDP-specific boundary between generic socket wrapping and transport implementation.

Risks and edge cases: Callers must only pass UDP sockets. Send requires a valid peer bind; otherwise the implementation drops the skb. Attach may find the socket already owned by the same ovpn instance or a different user.

Test signals: Build inclusion with socket/peer declarations, UDP attach/detach lifecycle, send without bind, send after route cache reset, and shared socket refcount behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/udp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/pcs/Kconfig

Purpose: Defines Kconfig entries for PCS-layer drivers in this directory.

Important APIs, types, and functions: `PCS_XPCS` is a tristate for Synopsys DesignWare Ethernet XPCS and selects `PHYLINK`. `PCS_LYNX` is a tristate helper library for NXP Layerscape/QorIQ Lynx PCS. `PCS_MTK_LYNXI` is a tristate helper selecting `PHY_COMMON_PROPS` and `REGMAP`. `PCS_RZN1_MIIC` is a user-visible tristate for Renesas RZ/N1, RZ/N2H, and RZ/T2H MII converter PCS, depending on OF and Renesas architecture or compile-test.

Control flow: These symbols control which object files the PCS Makefile builds and which phylink helper providers are available to MAC drivers.

State and persistence behavior: No runtime state; this is build configuration.

Dependencies and integration points: It integrates with the kernel networking driver menu, phylink, regmap, OF, architecture symbols, and compile-test coverage.

Risks and edge cases: Library-style symbols such as `PCS_LYNX` and `PCS_MTK_LYNXI` are not prompt-visible here, so consumers must select them. Missing `PHYLINK`/`REGMAP` selections would surface as link errors. The Renesas driver is OF-only.

Test signals: Kconfig matrix builds for each symbol as built-in/module, allmodconfig, allyesconfig, compile-test without Renesas hardware, and consumer drivers selecting hidden library symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/pcs/Makefile

Purpose: Lists PCS driver objects and composes the multi-file XPCS module.

Important APIs, types, and functions: `pcs_xpcs-$(CONFIG_PCS_XPCS)` combines `pcs-xpcs.o`, `pcs-xpcs-plat.o`, `pcs-xpcs-nxp.o`, and `pcs-xpcs-wx.o`. `obj-$(CONFIG_PCS_XPCS)`, `obj-$(CONFIG_PCS_LYNX)`, `obj-$(CONFIG_PCS_MTK_LYNXI)`, and `obj-$(CONFIG_PCS_RZN1_MIIC)` select the final objects.

Control flow: Kbuild compiles helper libraries and platform drivers according to Kconfig symbols. The XPCS module links core, platform MDIO/MMIO frontend, and vendor PMA helpers together.

State and persistence behavior: No runtime state; build artifact composition only.

Dependencies and integration points: It integrates PCS objects into `drivers/net/pcs` and ensures vendor helpers are available for core XPCS compatibility tables.

Risks and edge cases: Removing a helper from `pcs_xpcs` would leave unresolved symbols for NXP/WangXun PMA callbacks. Hidden helper configs require consumers to select them correctly.

Test signals: Module and built-in builds for each PCS config, modpost unresolved-symbol checks, and verifying `pcs_xpcs.ko` includes platform and vendor helper code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-lynx.c -->
# sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-lynx.c

Purpose: Provides an NXP Lynx PCS phylink helper library for MDIO-backed PCS blocks in Layerscape/QorIQ Ethernet SerDes.

Important APIs, types, and functions: `struct lynx_pcs` wraps `phylink_pcs` and an `mdio_device`. `lynx_pcs_phylink_ops` implements in-band capabilities, state read, config, autoneg restart, and link-up. Exported constructors/destructor are `lynx_pcs_create_mdiodev()`, `lynx_pcs_create_fwnode()`, and `lynx_pcs_destroy()`.

Control flow: Consumers create a PCS from an MDIO bus/address or firmware node. Config chooses C22 helpers for SGMII/QSGMII/1000BASE-X/2500BASE-X, C45 helpers for 10GBASE-R state, and vendor MMD reads for USXGMII/10G-QXGMII. Link timers are programmed for gigabit modes. Non-inband SGMII link-up forces speed/duplex in `IF_MODE`.

State and persistence behavior: The object holds an MDIO device reference and marks supported interfaces. `pcs.poll = true`, so phylink polls state instead of relying on interrupts. No persistent hardware state beyond programmed PCS registers.

Dependencies and integration points: It depends on phylink MII PCS helpers, MDIO device management, firmware-node MDIO lookup, and `linux/pcs-lynx.h` consumer API.

Risks and edge cases: USXGMII currently requires in-band autoneg and returns `-EOPNOTSUPP` otherwise. Link timer programming must match interface mode. Constructor reference handling intentionally drops the caller-created MDIO reference after taking its own. Unsupported speeds in forced SGMII link-up are rejected.

Test signals: Test all supported interfaces, in-band and forced SGMII, USXGMII autoneg-only behavior, fwnode unavailable/defer paths, MDIO read/write failures, state decode for C22/C45/vendor paths, and create/destroy refcount balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-lynx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-mtk-lynxi.c -->
# sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-mtk-lynxi.c

Purpose: Implements a MediaTek LynxI SGMII/BASE-X PCS phylink helper using regmap-backed SGMII subsystem registers.

Important APIs, types, and functions: `struct mtk_pcs_lynxi` stores regmap, ANA_RGC3 offset, current interface, phylink PCS, flags, and fwnode. `mtk_pcs_lynxi_ops` implements in-band caps, state read, config, autoneg restart, link-up, and disable. Exported APIs are `mtk_pcs_lynxi_create()` and `mtk_pcs_lynxi_destroy()`.

Control flow: Creation verifies device ID and version, allocates a PCS object, stores fwnode/regmap, and advertises SGMII/1000BASE-X/2500BASE-X. Config encodes advertisement, selects SGMII versus BASE-X mode, powers down and resets QPHY on interface change, applies RX/TX polarity from properties, programs analog speed and link timer, updates advertisement/BMCR/mode bits, then powers QPHY back up after a short sleep. Link-up forces speed/duplex when not using in-band negotiation.

State and persistence behavior: `mpcs->interface` caches the active interface to avoid disruptive analog reprogramming. Register programming persists in the PCS hardware until reconfigured or reset. Fwnode reference is held for polarity parsing.

Dependencies and integration points: It depends on regmap, phylink C22 encode/decode helpers, PHY common polarity properties, firmware child node `"pcs"`, and MediaTek consumer headers.

Risks and edge cases: Interface changes intentionally reset/power-cycle QPHY and can interrupt traffic. Polarity defaults can be inverted by legacy `mediatek,pnswap` or per-direction properties. QPHY power-up has a race-sensitive sleep and full-register write to clear problematic states. Creation returns NULL rather than ERR_PTR on ID/version/read failures, so consumers must handle that convention.

Test signals: Verify ID/version rejection, SGMII and BASE-X config, 2500BASE-X analog speed, polarity properties, forced speed/duplex, disable/reconfigure, link timer values, regmap failure injection, and traffic after QPHY power-cycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-mtk-lynxi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-rzn1-miic.c -->
# sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-rzn1-miic.c

Purpose: Implements the Renesas RZ/N1, RZ/N2H, and RZ/T2H MII converter PCS driver. It configures SoC Ethernet mux/converter registers and provides per-port `phylink_pcs` objects for MAC drivers.

Important APIs, types, and functions: `struct miic` stores MMIO base, device, lock, reset controls, OF data, and PHY_LINK config. `struct miic_port` is the per-port PCS wrapper. Exported APIs are `miic_create()` and `miic_destroy()`. Phylink ops are `miic_config()`, `miic_link_up()`, and `miic_pre_init()`. Platform lifecycle is `miic_probe()`/`miic_remove()`. OF data tables describe RZ/N1 and RZ/T2H mux match tables, port ranges, reset IDs, write-lock behavior, and switch-mode masks.

Control flow: Probe allocates `miic`, parses device tree requested converter inputs into `dt_val`, validates them against SoC match tables, maps registers, deasserts resets, enables runtime PM, writes MODCTRL, disables converters and switch speed/duplex overrides, programs PHY_LINK polarity bits, and finally publishes driver data. `miic_create()` finds the parent platform device, validates the port number, device-links the consumer, allocates a port PCS, and advertises MII/RMII/RGMII modes. Config sets converter mode and initial speed, enables the converter, and link-up updates speed/duplex.

State and persistence behavior: Hardware mux mode and PHY_LINK bits persist in MIIC registers. Per-port interface cache avoids changing speed while an interface is already active. Runtime PM remains active while the platform driver is bound.

Dependencies and integration points: It depends on OF bindings, Renesas dt-bindings constants, reset controller, runtime PM, platform devices, phylink, and consumer MAC drivers calling `miic_create()` from child PCS nodes.

Risks and edge cases: Device-tree mux combinations must match fixed tables; invalid combinations print the requested configuration. RZ/N1 and RZ/T2H differ in port numbering, lock/unlock sequence, resets, and active polarity rules. `miic_parse_dt()` allocates `dt_val` for multiple entries but clears only `sizeof(*dt_val)`, which is a suspicious bug because uninitialized entries can affect match results. `miic_create()` uses driver-data presence as readiness and returns `-EPROBE_DEFER` before probe completion.

Test signals: Validate all documented mux table combinations, invalid DT diagnostics, RZ/N1 register unlock and RZ/T2H locked writes, reset deassert/assert actions, PHY_LINK active-high/low mapping, per-port create/destroy, MII/RMII/RGMII config and link-up speeds, `rxc_always_on` pre-init, runtime PM error paths, and KASAN/UBSAN around DT parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-rzn1-miic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs-nxp.c -->
# sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs-nxp.c

Purpose: Provides NXP-specific PMA programming callbacks for DesignWare XPCS instances embedded in SJA1105/SJA1110 devices.

Important APIs, types, and functions: Exported-to-core functions are `nxp_sja1105_sgmii_pma_config()`, `nxp_sja1110_sgmii_pma_config()`, and `nxp_sja1110_2500basex_pma_config()`. Shared helper `nxp_sja1110_pma_config()` writes PLL dividers, transmitter amplitude/trim, lane termination, datapath, receiver PLL, signal detector, power/reset bits, and CTLE settings.

Control flow: The XPCS core calls these callbacks after mode-specific PCS configuration when a compatibility entry has `pma_config`. SJA1105 SGMII simply inverts TX polarity. SJA1110 variants program different PLL divider/CTLE values for SGMII versus 2500BASE-X, then release PMA power/reset.

State and persistence behavior: Register writes persist in vendor MMD PMA/PCS hardware until reset or reprogramming. No software state is stored here.

Dependencies and integration points: It depends on `struct dw_xpcs` accessors from `pcs-xpcs.h` and MDIO MMD vendor registers. It is linked into the XPCS module and referenced by compatibility tables in `pcs-xpcs.c`.

Risks and edge cases: Hard-coded analog values are silicon-specific and order-sensitive. Any write failure aborts later programming, potentially leaving a partially configured PMA. SJA1105 polarity inversion encodes a board/device assumption. Register field macros use wide constants for trim values and must remain correct on 16-bit writes.

Test signals: Hardware bring-up for SJA1105 SGMII and SJA1110 SGMII/2500BASE-X, MDIO failure injection at each write, link BER/eye validation, polarity tests, and regression after PCS reset or mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs-nxp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs-plat.c -->
# sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs-plat.c

Purpose: Implements a platform driver that exposes memory-mapped Synopsys DesignWare XPCS registers as an MDIO bus/device for the XPCS core.

Important APIs, types, and functions: `struct dw_xpcs_plat` stores platform device, synthetic MDIO bus, direct/indirect register mode, register width, MMIO base, and CSR clock. MMIO accessors implement C22/C45 read/write through direct or viewport-indirect addressing. Probe helpers are `xpcs_plat_init_res()`, `xpcs_plat_init_clk()`, `xpcs_plat_init_bus()`, and `xpcs_plat_init_dev()`. Runtime PM callbacks gate the optional CSR clock.

Control flow: Probe allocates data, parses `reg-io-width`, selects a resource named `"direct"` or `"indirect"`, validates address-space size, maps MMIO, enables runtime PM, registers a synthetic MDIO bus, creates a single MDIO device at address 0, attaches the firmware node and match data, and registers the MDIO device so the XPCS driver core can bind to it. MMIO MDIO operations resume runtime PM around each register access.

State and persistence behavior: Software state is devm-managed and persists for the platform device lifetime. The MDIO bus/device abstracts XPCS CSR access; hardware register state is owned by the XPCS core and PMA helpers.

Dependencies and integration points: It depends on platform resources, OF match data, clocks, runtime PM, MDIO bus/device APIs, and `DW_XPCS_INFO_DECLARE()` entries for compatible PMA IDs. It bridges device-tree `"snps,dw-xpcs*"` nodes to the generic XPCS library.

Risks and edge cases: Direct access requires a large 2 MiB-like window while indirect access uses a 256-register viewport; resource naming and size validation must match bindings. Address formatting combines MMD and register into MMIO offsets and can break if register width is wrong. Each MDIO op resumes/suspends PM, so high-frequency polling can churn clocks. Only MDIO address 0 is valid.

Test signals: Probe with direct and indirect resources, reg-io-width 2 and 4, invalid resource names/sizes, optional clock absent/present, runtime PM suspend/resume around reads, C22 and C45 access correctness, fwnode reuse, and all supported OF compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs-plat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs-wx.c -->
# sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs-wx.c

Purpose: Provides WangXun TXGBE-specific PMA/PCS mode switching for DesignWare XPCS hardware.

Important APIs, types, and functions: `txgbe_xpcs_switch_mode()` is called by the XPCS core when selecting 10GBASE-R, SGMII, or 1000BASE-X. Helpers program PMA registers for 10G (`txgbe_pma_config_10gbaser()`) or 1G/SGMII (`txgbe_pma_config_1g()`), poll PCS power-up (`txgbe_pcs_poll_power_up()`), wait for PMA init reset completion (`txgbe_pma_init_done()`), and detect LAN-reset mode quirks (`txgbe_xpcs_mode_quirk()`).

Control flow: If the target interface is supported and either differs from cached mode or hardware appears reset to 10G, the function polls PCS power-up, programs PCS/PMA MDIO control registers for 10G or 1G mode, applies a sequence of analog PMA tuning writes, triggers vendor PCS reset with VSMMD enabled, then waits for reset deassertion.

State and persistence behavior: `xpcs->interface` caches the selected mode, but hardware can revert during LAN reset, so mode quirk detection rereads PCS type. PMA register state persists until reset or mode change.

Dependencies and integration points: It depends on XPCS MDIO accessors, WangXun PMA register layout, and is invoked from `xpcs_switch_interface_mode()` for `WX_TXGBE_XPCS_PMA_10G_ID`.

Risks and edge cases: Poll timeouts are long and indicate hardware bring-up failure. The mode quirk path must catch external resets or phylink may believe the PCS is configured when it is not. Analog values are device-specific. Errors from many configuration writes are mostly ignored in the tuning helpers, so final poll/reset failures may be the first visible symptom.

Test signals: Mode switching 10GBASE-R to SGMII/1000BASE-X and back, LAN reset recovery, timeout paths for power-up and PMA init, MDIO error injection, link stability/BER at both speeds, and interrupt-driven non-polled XPCS operation with TXGBE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs-wx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs.c -->
# sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs.c

Purpose: Implements the generic Synopsys DesignWare XPCS phylink library, including identification, supported interface validation, autonegotiation setup/status, link state resolution, EEE control, clock handling, and public constructors/destructors.

Important APIs, types, and functions: Public APIs include `xpcs_to_phylink_pcs()`, `xpcs_get_an_mode()`, `xpcs_config_eee_mult_fact()`, `xpcs_create_mdiodev()`, `xpcs_create_pcs_mdiodev()`, `xpcs_create_fwnode()`, `xpcs_destroy()`, and `xpcs_destroy_pcs()`. MDIO accessors are `xpcs_read()`, `xpcs_write()`, `xpcs_modify()`, `xpcs_read_vpcs()`, and `xpcs_write_vpcs()`. `xpcs_phylink_ops` provides validate, in-band caps, pre-config, config, get-state, AN restart, link-up, and EEE hooks. Compatibility tables map PCS IDs/interfaces to supported link modes, AN modes, and PMA callbacks.

Control flow: Creation allocates `dw_xpcs`, gets optional clocks, reads or accepts platform-provided PCS/PMA IDs, selects a descriptor, populates supported interfaces, and sets polling/reset behavior. Phylink validation intersects supported link modes with the selected interface. Pre-config switches interface mode, possibly soft-resets. Config dispatches to Clause 73, Clause 37 SGMII, Clause 37 1000BASE-X, 2500BASE-X, 10GBASE-R no-op, and optional vendor PMA callbacks. State reading decodes C73/C37/2500/10G paths, handles faults and resets, and resolves speed/duplex/pause.

State and persistence behavior: `struct dw_xpcs` caches descriptor, IDs, interface, reset need, clocks, phylink PCS, and EEE multiplier. Hardware autoneg/PCS/PMA registers persist until reset/reconfiguration. Some PMA IDs disable polling and reset behavior for interrupt-driven or special hardware.

Dependencies and integration points: It depends on MDIO C45/C22 helpers, phylink, ethtool link modes, clocks, firmware MDIO lookup, and vendor helper files for NXP and WangXun. Platform and MAC drivers use its constructors to obtain `phylink_pcs`.

Risks and edge cases: Link-status bits can be latching-low, so unnecessary rereads can miss down events. Fault handling resets and reconfigures C73 links. SGMII MAC-side/PHY-side differences and TXGBE quirks affect register programming. Autoneg advertisement support is per-compat table, and unsupported interfaces return `-ENODEV`/`-EINVAL`. Clock preparation must unwind on ID failure. EEE multiplier must be configured appropriately by consumers.

Test signals: Probe all descriptor IDs, validate supported interfaces/link modes, C73 advertisement/LPA resolution, C37 SGMII and 1000BASE-X forced/in-band paths, 2500BASE-X fixed link, USXGMII speed programming, fault/reset recovery, PMA-specific TXGBE and NXP callbacks, EEE enable/disable, clock failure unwind, fwnode and MDIO constructors, and destroy after partial create failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs.h -->
# sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs.h

Purpose: Provides private DesignWare XPCS register definitions, data structures, and helper prototypes shared by the XPCS core, platform frontend, and vendor PMA files.

Important APIs, types, and functions: The header defines vendor-register access marker `DW_VENDOR`, VR PCS/MII register offsets and bit fields, USXGMII speed encodings, Clause 73 advertisement bits, Clause 37 mode bits, EEE controls, and polarity bits. `DW_XPCS_INFO_DECLARE()` creates static `dw_xpcs_info` match data. `enum dw_xpcs_clock` names core/pad clocks. `struct dw_xpcs` stores IDs, descriptor, MDIO device, clocks, phylink PCS, current interface, reset flag, and EEE multiplier. It declares XPCS MDIO accessors and vendor PMA callbacks.

Control flow: Core code uses these constants to program autoneg, link-up, reset, EEE, and vendor registers. Platform code uses `DW_XPCS_INFO_DECLARE()` for OF match data. Vendor files call `xpcs_read/write/modify()` against PMA/PCS registers.

State and persistence behavior: The only mutable software state defined is `struct dw_xpcs`, which persists for the XPCS object lifetime. Register macros describe hardware state persisted in the PCS/PMA.

Dependencies and integration points: It includes kernel bit helpers and the public `linux/pcs/pcs-xpcs.h` UAPI/internal interface. It is private to `drivers/net/pcs` implementation files.

Risks and edge cases: Register offsets combine standard and vendor MMD spaces; using the wrong MMD or forgetting `DW_VENDOR` writes the wrong hardware location. Bit-field encodings for SGMII/USXGMII speeds are reused across mode paths. Private struct layout is shared across module objects, so all XPCS object files must be built together.

Test signals: Compile all XPCS objects together, verify register writes against hardware documentation, test each speed encoding, and run sparse/build checks for prototype drift between core and vendor helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pfcp.c -->
# sources/distributed-fs/ceph-client/drivers/net/pfcp.c

Purpose: Implements an rtnetlink-created PFCP virtual interface that receives PFCP UDP packets on the standard PFCP port, strips the PFCP header, attaches tunnel metadata, and injects payloads through GRO cells.

Important APIs, types, and functions: `struct pfcp_dev` stores list linkage, UDP socket, netdev, net namespace, and GRO cells. `struct pfcp_net` stores per-netns device list. RX functions are `pfcp_encap_recv()`, `pfcp_session_recv()`, and `pfcp_node_recv()`. Netdev lifecycle is `pfcp_link_setup()`, `pfcp_dev_init()`, `pfcp_dev_uninit()`, `pfcp_newlink()`, and `pfcp_dellink()`. Socket setup is `pfcp_create_sock()`, `pfcp_add_sock()`, and `pfcp_del_sock()`. Namespace/module lifecycle is `pfcp_net_init()`, `pfcp_net_exit_rtnl()`, `pfcp_init()`, and `pfcp_exit()`.

Control flow: Module init registers pernet ops and rtnl link kind `"pfcp"`. Newlink creates a UDP IPv4 socket bound to `PFCP_PORT`, installs a UDP tunnel receive callback with `sk_user_data = pfcp`, registers the netdev, and links it into the namespace list. RX validates minimum PFCP header, allocates tunnel metadata, records node/session type and SEID when present, marks PFCP tunnel options, pulls the PFCP header, sets skb dst/dev/headers, and delivers via GRO cells.

State and persistence behavior: One `pfcp_dev` exists per PFCP netdev, owning its UDP socket and GRO cells. `pfcp_net` tracks devices per namespace for exit cleanup. There is no persistent storage beyond netdev/socket lifetime.

Dependencies and integration points: It depends on rtnl link ops, pernet operations, UDP tunnel socket helpers, `net/pfcp.h` header parsing and metadata definitions, ip tunnel metadata, GRO cells, and netdev stats helpers.

Risks and edge cases: Only an IPv4 wildcard UDP socket is created, so IPv6 PFCP is not handled here. `pfcp_encap_recv()` drops all malformed packets and always consumes the skb. Metadata allocation and `iptunnel_pull_header()` failures must free skb and avoid leaking `metadata_dst`; ownership transfers through `skb_dst_set()` on success. Namespace exit must unregister queued netdevs under rtnl. Binding to PFCP_PORT can fail if unavailable in the namespace.

Test signals: Create/delete PFCP links in multiple netns, port bind failure, receive node and session PFCP packets with SEID metadata, too-short packet drops, metadata allocation failure injection, GRO delivery, namespace teardown with live devices, stats reads, module unload, and verification that PFCP tunnel option bits are visible to consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pfcp.c -->

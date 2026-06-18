# sources/distributed-fs/ceph-client/drivers/net/wireguard/peer.h

Purpose: Defines endpoint and peer runtime state plus peer lifecycle APIs.

Important APIs and types: `struct endpoint` stores remote IPv4/IPv6 sockaddr plus discovered source address/interface information for route symmetry. `struct wg_peer` contains device pointer, ordered TX/RX queues, staged packet queue, serial work CPU, death flag, keypairs, endpoint/cache/lock, handshake, last handshake timestamp, work items, cookie, pubkey hash node, byte counters, timers, persistent keepalive fields, last handshake walltime, kref/RCU, peer and allowedips lists, NAPI, and internal ID. Declares create/get/put/remove/all and peer cache init/uninit APIs.

Control flow: Header shapes how netlink, device, socket, send, receive, timers, and lookup code share peer state. Inline `wg_peer_get()` increments the kref without zero check for known-live references.

State and persistence: Declares volatile per-peer runtime state. Endpoint cache and byte counters persist only while the peer object lives; key material is sensitive and must be cleared.

Dependencies and integration points: Includes device, Noise, cookie, netfilter, spinlock, kref, and dst-cache types. The endpoint type is consumed by socket and debug helpers.

Risks: Peer state is accessed from softirq, workqueue, timer, NAPI, and netlink contexts. Fields require different locks: endpoint rwlock, keypair spinlock, handshake rwsem, kref/RCU, and device update mutex. Misuse of `wg_peer_get()` on maybe-dead peers can resurrect invalid objects.

Test signals: Build coverage, peer creation/removal, endpoint update and source clearing, timer callbacks, NAPI receive, kref underflow checks, and RCU lifetime tests.

# sources/distributed-fs/ceph-client/drivers/net/ovpn/peer.h

Purpose: Defines the main ovpn peer object and exports peer-management APIs used by netlink, transport, crypto, and packet I/O code.

Important APIs, types, and functions: `struct ovpn_peer` carries the owning `ovpn_priv`, peer/TX IDs, VPN IPv4/IPv6 addresses, hash nodes, RCU socket and bind pointers, TCP-specific parser/queues/callback backups, crypto state, dst cache, keepalive timers, stats, delete reason, spinlock, kref, RCU head, release-list node, and keepalive work. Inline `ovpn_peer_hold()` and `ovpn_peer_put()` manage references. Public functions cover create/add/delete/free, lookups by transport/ID/destination, VPN-IP rehash, source validation, keepalive, endpoint update, and sockaddr reset.

Control flow: Callers allocate a peer through `ovpn_peer_new()`, attach a socket and bind through netlink/socket helpers, add it to the appropriate P2P or MP table, then use reference-taking lookup APIs from data paths. Delete removes the peer from visible state; final freeing happens after refs and RCU readers drain.

State and persistence behavior: The struct is the central runtime persistence unit for a remote OpenVPN peer. It is not durable across device teardown. Several members are only meaningful for TCP, but share storage inside every peer so TCP transport can override socket callbacks and buffer in-flight stream data.

Dependencies and integration points: It depends on dst cache, stream parser, crypto, socket, stats, netdev reference tracking, bind definitions via users of the pointer, and UAPI delete reasons. It integrates directly with phasing in `netlink.c`, transport send/receive, and keepalive work.

Risks and edge cases: Users must not dereference `sock` or `bind` without RCU or protected locks. `peer->lock` protects bind and keepalive fields, while `ovpn->lock` protects global visibility and hashes; mixing them incorrectly can deadlock or expose stale hash entries. TCP callback backup fields must be restored exactly once.

Test signals: Compile with TCP and UDP paths, create/release peers under KASAN/KCSAN, validate refcount behavior on lookup/delete races, ensure TCP queues are purged on detach, and check keepalive/delete reason propagation through netlink notifications.

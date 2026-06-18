# sources/distributed-fs/ceph-client/drivers/net/ovpn/bind.c

Purpose: implements allocation and replacement of OpenVPN peer transport bindings, which record remote endpoint addresses.

Important APIs/types/functions: `ovpn_bind_from_sockaddr()` allocates an `ovpn_bind` from IPv4 or IPv6 `sockaddr_storage`. `ovpn_bind_reset()` replaces a peer's binding under the peer lock and frees the old binding with RCU.

Control flow: binding creation validates address family, chooses sockaddr length, allocates with `GFP_ATOMIC`, copies the remote address, and returns either a pointer or `ERR_PTR`. Reset asserts the caller holds `peer->lock`, uses `rcu_replace_pointer()` to publish the new binding, and schedules the old object through `kfree_rcu()`.

State and persistence: a binding stores remote sockaddr, local IP union fields populated elsewhere, and an RCU head. It is volatile per peer.

Dependencies and integration: depends on `ovpn_peer`, RCU pointer discipline, socket address types, and the receive-side matching helpers in `bind.h`.

Risks: only AF_INET and AF_INET6 are accepted. Allocation uses atomic context, so callers must handle `-ENOMEM`. Reset must be called under the correct peer lock; otherwise RCU replacement lockdep assumptions are invalid.

Test signals: create IPv4 and IPv6 bindings, reject unsupported families, replace peer binding under lock, verify old binding is safe for RCU readers, and run endpoint-floating tests that reset bindings.

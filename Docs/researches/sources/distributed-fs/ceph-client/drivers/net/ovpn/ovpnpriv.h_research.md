# sources/distributed-fs/ceph-client/drivers/net/ovpn/ovpnpriv.h

Purpose: Defines the private per-interface OpenVPN state and the multi-peer hash-table container used by the driver.

Important APIs, types, and functions: `struct ovpn_peer_collection` contains the MP-mode lookup tables: `by_id`, `by_vpn_addr4`, `by_vpn_addr6`, and `by_transp_addr`. `struct ovpn_priv` stores the netdev pointer, `enum ovpn_mode`, a spinlock protecting writes, MP-mode peer collection, P2P single-peer RCU pointer, GRO cells, and global delayed keepalive work.

Control flow: Netdev creation initializes `ovpn_priv`, P2P mode uses `ovpn->peer`, and MP mode allocates `ovpn->peers`. Peer add/delete, packet RX/TX lookup, netlink dump, and keepalive scans use these members to locate peers or iterate all peers.

State and persistence behavior: All fields are runtime-only and rebuilt with the netdev. `ovpn->lock` protects table mutations and P2P peer replacement. Peer pointers are RCU-protected so data path readers can operate without taking the writer lock.

Dependencies and integration points: It depends on kernel workqueues, GRO cells, link UAPI mode enums, and ovpn UAPI definitions. It is the shared state contract among netlink, peer, socket, transport, I/O, and main netdev code.

Risks and edge cases: The MP hash arrays have fixed size and include nulls-list heads for address tables, so lookup/restart logic must preserve nulls values during rehash. Callers must honor the mode distinction: using `peers` in P2P or `peer` in MP will break lookups and teardown. Keepalive work must not rearm after netdev teardown.

Test signals: Verify P2P and MP netdev creation, MP hash initialization, peer replacement in P2P, concurrent peer lookup during delete, GRO receive delivery, delayed keepalive scheduling/cancellation, and teardown with non-empty peer tables.

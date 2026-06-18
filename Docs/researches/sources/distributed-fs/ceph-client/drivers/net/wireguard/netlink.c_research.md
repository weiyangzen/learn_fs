# sources/distributed-fs/ceph-client/drivers/net/wireguard/netlink.c

Purpose: Implements the handwritten WireGuard Generic Netlink control plane for dumping and setting interface, peer, endpoint, key, fwmark, listen-port, persistent-keepalive, and allowedips configuration.

Important APIs and functions: `wg_get_device_start()`, `wg_get_device_dumpit()`, and `wg_get_device_done()` implement multipart dumps with peer/allowedips cursors. `wg_set_device_doit()` applies device-level and nested peer changes. Helpers include `lookup_interface()`, `get_peer()`, `get_allowedips()`, `set_port()`, `set_allowedip()`, and `set_peer()`. `wg_genetlink_init()` registers the family and checks UAPI key sizes; `wg_genetlink_uninit()` unregisters it.

Control flow: Dump start resolves the WireGuard netdev by ifindex or ifname. Dumpit locks RTNL and `device_update_lock`, emits device attributes and private/public keys, then walks peers and their allowedips, saving cursors when the skb fills. Set operations resolve the device, take RTNL plus `device_update_lock`, check namespace capability for listen-port/fwmark changes, bump `device_update_gen`, apply fwmark/listen-port/private-key updates, optionally replace all peers, then process nested peer operations. Peer set creates or finds a peer, handles remove/update-only/replace-allowedips flags, updates preshared key, endpoint, allowedips, keepalive interval, and sends staged packets on running devices.

State and persistence: Mutates `wg_device` incoming port, fwmark, static identity, cookie precomputed keys, peer list, peer allowedips, peer endpoint, preshared keys, keepalive intervals, staged packets, and update generation. Private and preshared key netlink buffers are explicitly zeroed after use. State is runtime-only but visible to userspace via netlink dumps.

Dependencies and integration points: Depends on generated netlink policies, UAPI WireGuard attributes, Generic Netlink, RTNL, peer lookup/lifecycle, allowedips trie, Noise identity/keypair invalidation, socket reinitialization, cookie precomputation, and queueing.

Risks: Dumps include private key material in skbs and note missing zero-on-free support. Multipart dump consistency depends on `device_update_gen`, peer references, and allowedips sequence checks. Private-key replacement removes a peer with matching new public key before updating identity. Capability checks are tied to the creating namespace, which can disappear. Attribute parsing must keep key material lengths and flags strict.

Test signals: `wg show` and `wg set` equivalents by ifname/ifindex, multipart dumps with many peers/allowedips, concurrent peer removal during dump, private-key replacement removing self peer, listen-port socket rebind, fwmark clearing endpoint source cache, replace-peers/replace-allowedips flags, invalid protocol version, and malformed nested attributes.

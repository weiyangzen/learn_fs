# sources/distributed-fs/ceph-client/drivers/net/ovpn/udp.c

Purpose: Implements OpenVPN-over-UDP socket encapsulation receive, peer lookup, UDP tunnel transmit, endpoint route caching, and UDP socket attach/detach.

Important APIs, types, and functions: `ovpn_udp_socket_attach()` installs `setup_udp_tunnel_sock()` callbacks, `ovpn_udp_socket_detach()` clears them, and `ovpn_udp_send_skb()` sends encrypted skbs. RX starts in `ovpn_udp_encap_recv()`. TX helpers are `ovpn_udp_output()`, `ovpn_udp4_output()`, and IPv6-only `ovpn_udp6_output()`. `ovpn_udp_encap_destroy()` removes peers using a closing socket.

Control flow: UDP receive verifies the socket is owned by ovpn, pulls UDP header plus opcode, drops unsupported DATA_V1, passes non-DATA_V2 packets to userspace, and for DATA_V2 looks up the peer by embedded peer ID or by source transport address when the peer ID is undefined. It then strips the outer UDP header and calls `ovpn_recv()`. TX sets skb device/mark/checksum state, reads the peer bind under RCU, obtains or refreshes a cached route, and uses UDP tunnel helpers to emit IPv4/IPv6 packets.

State and persistence behavior: UDP socket ownership is stored in `sk_user_data` and UDP encap fields. Per-peer `dst_cache` stores route and source address. `bind->local` can be reset when cached local addresses become invalid. UDP socket wrappers may be shared by multiple peers in the same ovpn instance.

Dependencies and integration points: It depends on UDP tunnel infrastructure, route lookup, IPv6 address validation when enabled, bind matching, peer lookup/update, and ovpn receive code. Netlink provides the initial UDP endpoint binding.

Risks and edge cases: DATA_V2 packets with undefined peer IDs rely entirely on transport address lookup, so floating/rehash correctness matters. Route cache source addresses can become invalid and must be reset. IPv6 scoped addresses feed `flowi6_oif`. Detach must restore UDP socket state, including multicast loopback and checksum conversion. `ovpn_udp_socket_attach()` returning `-EALREADY` is meaningful to wrapper sharing logic.

Test signals: Cover DATA_V2 receive by ID and by transport address, DATA_V1 drop, control packet userspace pass-through, short skb drop, IPv4/IPv6 TX route cache hits/misses, local address invalidation, peer floating, socket close removing only peers using that socket, shared UDP socket across peers, and detach restoring UDP fields.

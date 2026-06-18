# sources/distributed-fs/ceph-client/net/ieee802154/socket.c

## Purpose
`socket.c` implements the AF_IEEE802154 socket family for IEEE 802.15.4 devices. It exposes two socket personalities: `SOCK_RAW` sockets that send and receive complete 802.15.4 frames, and `SOCK_DGRAM` sockets that build data-frame headers, maintain source/destination 802.15.4 addresses, and expose WPAN-specific socket options.

## Important APIs, types, and functions
The file registers `ieee802154_family_ops` through `sock_register()` and attaches `ieee802154_packet_type` to `ETH_P_IEEE802154`. `ieee802154_create()` selects `ieee802154_raw_prot`/`ieee802154_raw_ops` or `ieee802154_dgram_prot`/`ieee802154_dgram_ops`. Shared socket wrappers include `ieee802154_sock_release()`, `ieee802154_sock_sendmsg()`, `ieee802154_sock_bind()`, `ieee802154_sock_connect()`, and `ieee802154_sock_ioctl()`. Raw-socket state is tracked in `raw_head` under `raw_lock`; datagram state uses `struct dgram_sock`, `dgram_head`, and `dgram_lock`. Address resolution is centralized in `ieee802154_get_dev()`, which maps long or short IEEE 802.15.4 addresses to netdevices.

## Control flow
Module init registers both protocol objects, registers the socket family, then adds the packet handler. Socket creation rejects non-init network namespaces, requires `CAP_NET_RAW` for raw sockets, allocates a `struct sock`, installs protocol ops, hashes the socket, and runs per-protocol init. Raw sends pick a bound device or the first IEEE802154 device, copy user payload into an skb, set `ETH_P_IEEE802154`, and transmit with `dev_queue_xmit()`. Datagram sends resolve either an explicit send address or a connected destination, select the bound source device if present, fill `ieee802154_mac_cb` flags, build the MAC header via `wpan_dev_hard_header()`, append payload, and transmit. Receive flow enters `ieee802154_rcv()`, drops frames from stopped devices or non-init namespaces, clones to matching raw sockets, then delivers non-`PACKET_OTHERHOST` frames to matching datagram sockets.

## State and persistence
Socket state is volatile in-kernel state only. Raw sockets persist only their bound device index. Datagram sockets persist source and destination `struct ieee802154_addr`, bound/connected bits, ack and LQI preferences, and security override bits/levels. Global socket lists are protected by rwlocks and protocol in-use counters. No durable storage is written.

## Dependencies and integration points
The implementation depends on core socket/proto registration, netdevice lookup, `dev_add_pack()`, IEEE802154 address conversion helpers, `wpan_dev_hard_header()`, skbuff datagram helpers, capability checks, and netdevice ioctls for `SIOCGIFADDR`/`SIOCSIFADDR`. It integrates with userspace through AF_IEEE802154 socket calls and `SOL_IEEE802154` options such as `WPAN_WANTACK`, `WPAN_WANTLQI`, `WPAN_SECURITY`, and `WPAN_SECURITY_LEVEL`.

## Risks and invariants
`ieee802154_get_dev()` assumes matching `ieee802154_ptr` state on ARPHRD_IEEE802154 devices and deliberately rejects broadcast/undefined short addresses for binding. Datagram delivery queues the original skb to the last matching socket and clones for earlier matches, so clone allocation failures silently reduce fan-out. Security socket options require either `CAP_NET_ADMIN` or `CAP_NET_RAW`; regressions here affect link-layer security policy. Namespace support is intentionally limited to `init_net`, which is a functional limitation and a test boundary.

## Test signals
Useful tests include creating raw and datagram AF_IEEE802154 sockets, verifying raw capability gating, binding by long and short addresses, sending oversized payloads to observe `-EMSGSIZE`, receiving fan-out across multiple raw/datagram sockets, checking `WPAN_WANTLQI` control messages, testing security option permission failures, and loading/unloading the module to confirm protocol and packet handler registration unwind cleanly.

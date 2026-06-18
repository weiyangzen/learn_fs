# sources/distributed-fs/ceph-client/drivers/net/wireguard/socket.h

Purpose: Declares WireGuard socket send/init/reinit and endpoint helper APIs, plus debug logging wrappers that resolve skb endpoints.

Important APIs: Exports socket lifecycle functions, peer send helpers, reply send helper, endpoint extraction/update/source-clear helpers, and `net_dbg_skb_ratelimited()` for dynamic debug/DEBUG builds.

Control flow: Header declarations are used by device open/stop/destruct, send/receive handshake/data paths, timers, and netlink endpoint updates.

State and persistence: No header-owned state. Declared functions mutate device sockets and peer endpoints/caches.

Dependencies and integration points: Includes netdevice, UDP, VLAN, and Ethernet headers and relies on `struct wg_device`, `struct wg_peer`, and `struct endpoint` from peer/device headers.

Risks: The non-debug `net_dbg_skb_ratelimited` macro has a shorter apparent parameter list than debug form, so call sites must match the macro definitions exactly. Endpoint helpers require skb protocol/network/UDP headers to be valid.

Test signals: Compile with and without dynamic debug/DEBUG, endpoint debug logging, socket send paths, and endpoint update paths.

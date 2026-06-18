# sources/distributed-fs/ceph-client/drivers/net/wireguard/socket.c

Purpose: Implements WireGuard UDP socket creation/replacement, IPv4/IPv6 encapsulated send helpers, endpoint extraction/update, reply sends, receive callback dispatch, route caching, source address validation, and socket cleanup.

Important APIs and functions: `wg_socket_init()` creates IPv4 and optional IPv6 UDP tunnel sockets for the WireGuard device. `wg_socket_reinit()` atomically swaps RCU socket pointers and frees old sockets after `synchronize_net()`. `wg_socket_send_skb_to_peer()`, `wg_socket_send_buffer_to_peer()`, and `wg_socket_send_buffer_as_reply_to_skb()` transmit data/handshake/cookie packets. `wg_socket_endpoint_from_skb()`, `wg_socket_set_peer_endpoint()`, `wg_socket_set_peer_endpoint_from_skb()`, and `wg_socket_clear_peer_endpoint_src()` manage peer endpoints. Internal `send4()`, `send6()`, `wg_receive()`, `sock_free()`, and `set_sock_opts()` do low-level routing and socket handling.

Control flow: Send path reads peer endpoint under `endpoint_lock`, routes through cached dst or fresh IPv4/IPv6 lookup using fwmark and discovered source, resets invalid source constraints, then calls UDP tunnel transmit. Reply sends derive an endpoint from the incoming skb and send without peer cache. Socket init pins the creating netns, opens IPv4 first, reuses its port for IPv6 if enabled, configures UDP tunnel callbacks, then swaps sockets into the device. Receive callback pulls `wg` from `sk_user_data` and passes skb to `wg_packet_receive()`.

State and persistence: Mutates RCU `wg->sock4/sock6`, `wg->incoming_port`, peer endpoints, peer dst caches, endpoint source fields, skb marks/devs, and peer TX byte counters. UDP sockets persist while the interface is running or until reinit/stop/destruct.

Dependencies and integration points: Uses Linux UDP tunnel APIs, IPv4/IPv6 route lookup, dst cache, LSM flow classification, RCU BH socket access, endpoint locks, netns lifetime, fwmark, and packet receive path.

Risks: Socket replacement requires `synchronize_net()` before freeing old sockets. Endpoint source address/interface can become stale and must be cleared on route errors, fwmark/port change, namespace exit, and handshake retry. IPv6 socket creation retries on ephemeral port collisions when no port is specified. Peer TX bytes are counted by skb length before socket send consumes/frees the skb.

Test signals: IPv4 and IPv6 sends, no socket error, route failure, stale source address reset, fwmark routing, endpoint update from skb, cookie reply to incoming skb, listen-port rebinding, IPv6 disabled builds, netns teardown, and concurrent sends during socket reinit.

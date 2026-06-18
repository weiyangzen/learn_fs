# sources/distributed-fs/ceph-client/drivers/net/ovpn/io.c

Purpose: implements ovpn packet I/O: netdev transmit, peer receive, AEAD completion handling, keepalive detection/sending, GSO segmentation, peer selection, stats, and transport handoff.

Important APIs/types/functions: `ovpn_net_xmit()` is the net_device transmit entry. `ovpn_recv()` starts decrypt for received transport packets. `ovpn_encrypt_post()` and `ovpn_decrypt_post()` complete async crypto. `ovpn_xmit_special()` sends keepalive or other out-of-band payloads. `ovpn_netdev_write()` injects decrypted IP packets into the ovpn interface.

Control flow: transmit resets conntrack, validates IP protocol, finds the peer by destination, drops dst, segments GSO skbs, share-checks each segment, updates VPN tx stats, then encrypts each segment with the peer primary key. Encrypt completion frees crypto temp data, handles nonce exhaustion by killing the key and notifying userspace, sends encrypted skb via UDP or TCP socket, updates link tx stats and `last_sent`, and drops on failure. Receive records link rx stats, selects a key by packet key id, starts AEAD decrypt, validates replay packet ID in completion, updates endpoints for UDP floating, strips ovpn header/tag, detects keepalive/null packets, validates encapsulated IP and RPF, then injects into GRO cells and updates VPN/device rx stats.

State and persistence: uses peer crypto, stats, last send/receive timestamps, skb control block crypto temp/peer/key references, and ovpn GRO cells. State is volatile.

Dependencies and integration: integrates with ovpn peer lookup, bind endpoint updates, AEAD crypto, packet ID replay, TCP/UDP transport senders, generic segmentation, GRO cells, device dstats, netfilter conntrack reset, and netlink key-swap notification.

Risks: async crypto makes reference balancing crucial: peer and key refs are released in completion callbacks. Early decrypt/encrypt failures must free temp buffers only when allocated. RPF and keepalive classification happen after successful authentication. GSO segmentation errors and share-check failures must avoid double-freeing skb lists.

Test signals: send IPv4/IPv6 payloads in P2P and MP modes, no-peer drops, GSO segmentation, key-missing receive, replay rejection, keepalive receive, endpoint floating, RPF drops, TCP/UDP transport send, nonce exhaustion key kill notification, and async crypto completion cleanup.

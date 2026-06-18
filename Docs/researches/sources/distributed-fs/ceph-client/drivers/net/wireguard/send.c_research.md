# sources/distributed-fs/ceph-client/drivers/net/wireguard/send.c

Purpose: Implements WireGuard send path for handshake initiations/responses/cookies, keepalives, staged data packet encryption, nonce assignment, key freshness rekeying, per-peer ordered TX completion, and UDP socket transmission.

Important APIs and functions: `wg_packet_send_queued_handshake_initiation()`, `wg_packet_handshake_send_worker()`, `wg_packet_send_handshake_response()`, `wg_packet_send_handshake_cookie()`, `wg_packet_send_keepalive()`, `wg_packet_send_staged_packets()`, `wg_packet_encrypt_worker()`, `wg_packet_tx_worker()`, and `wg_packet_purge_staged_packets()`. Helpers include `wg_packet_send_handshake_initiation()`, `keep_key_fresh()`, `calculate_skb_padding()`, `encrypt_packet()`, `wg_packet_create_data()`, and `wg_packet_create_data_done()`.

Control flow: Handshake initiation is rate-limited by `last_sent_handshake`, builds a Noise initiation, adds cookie MACs, sends by socket, and starts timers. Responses derive a session before sending. Data send steals the staged queue, grabs a valid current keypair, assigns ECN DS and monotonically increasing nonces to every skb, enqueues the list for parallel encryption, then serial TX worker sends successfully encrypted skbs to the peer endpoint and drops dead lists. If no usable key exists, packets are orphaned, returned to the staged queue, and a handshake is queued. Keepalive creates an empty data skb only when no staged data exists.

State and persistence: Mutates peer staged queue, keypair sending counter and validity, packet metadata, tx byte counters via socket path, timers, last sent handshake timestamp, handshake attempts, and netdev TX drop stats. State is runtime-only but sensitive to key age/message limits.

Dependencies and integration points: Depends on Noise, cookie MACs, timers, queueing, socket send helpers, ip tunnel ECN, skb scatter-gather encryption, checksum helpers, and workqueues.

Risks: Nonce assignment must never exceed `REJECT_AFTER_MESSAGES` or reuse with a key. Encryption mutates skb head/tail and must handle checksum completion before padding/header insertion. Returning packets to staged queue on missing key can reorder slightly by design. Handshake queueing must balance peer references if work is already pending. `PACKET_CB(first)->keypair` represents an entire skb list.

Test signals: Handshake initiation rate limit, response send and session derivation, cookie replies, keepalive with and without staged data, data send with valid/expired/missing key, nonce overflow invalidation, padding at MTU boundaries, checksum-partial skb encryption, parallel encryption failure, ordered TX completion, and staged queue purge stats.

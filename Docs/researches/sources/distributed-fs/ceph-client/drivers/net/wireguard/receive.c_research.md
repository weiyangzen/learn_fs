# sources/distributed-fs/ceph-client/drivers/net/wireguard/receive.c

Purpose: Implements WireGuard UDP receive path for handshake, cookie, and encrypted data packets, including header validation, cookie/MAC handling under load, data decryption dispatch, anti-replay validation, inner packet validation, allowed source enforcement, NAPI delivery, and RX statistics.

Important APIs and functions: `wg_packet_receive()` is the socket entry point. `wg_packet_handshake_receive_worker()` drains queued handshakes. `wg_packet_decrypt_worker()` decrypts data packets in parallel. `wg_packet_rx_poll()` serially consumes per-peer decrypted packets under NAPI. Key helpers include `prepare_skb_header()`, `validate_header_len()`, `wg_receive_handshake_packet()`, `decrypt_packet()`, `counter_validate()`, `wg_packet_consume_data()`, and `wg_packet_consume_data_done()`. DEBUG builds include the packet counter selftest.

Control flow: Socket receive trims/pulls the skb to the UDP payload and validates exact WireGuard message sizes. Handshake/cookie packets enter a bounded handshake queue and are processed on per-CPU workers. Under load, MAC/cookie validation may demand a cookie reply before handshake consumption. Valid initiations update endpoint, send a response, and record timers/stats; valid responses derive a session and send keepalive or staged data. Data packets look up a keypair by index, take keypair/peer refs, enqueue for decrypt, then per-peer NAPI validates crypto state, replay counter, endpoint, inner IP header, ECN, inner length, and allowed source peer before GRO delivery.

State and persistence: Updates device handshake queue length, per-peer endpoint, keypair next/current transition, replay counter bitmap, timers, byte counters, netdev stats, skb packet metadata, and staged packets. All state is runtime-only.

Dependencies and integration points: Depends on queueing, Noise, cookie, timers, socket endpoint helpers, allowedips source lookup, ip tunnel helpers, NAPI/GRO, ChaCha20-Poly1305 scatter-gather crypto, skb cow/trim/pull APIs, and ratelimited debug logging.

Risks: Header preparation must defend against malformed IP/UDP lengths. Anti-replay `counter_validate()` is security-critical. Decryption temporarily pushes/pulls headers to preserve endpoint metadata. The allowed-source check prevents peer spoofing and must match allowedips semantics. Queue overload paths can drop handshakes; cookie under-load state is global and racy by design. NAPI completion must not lose remaining crypted/dead packets.

Test signals: Malformed UDP/IP lengths, each message type size, cookie response under queue load, invalid MAC, valid initiation/response session derivation, data decrypt success/failure, replayed counters, keepalive zero-length data, invalid inner IP/version/length, allowedips source mismatch, IPv4/IPv6 ECN decapsulation, GRO delivery, and queue overflow.

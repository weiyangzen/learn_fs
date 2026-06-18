# sources/distributed-fs/ceph-client/drivers/net/wireguard/messages.h

Purpose: Defines WireGuard cryptographic sizes, protocol limits, message type IDs, wire-format structures, skb headroom/tailroom constants, and handshake DSCP marking.

Important APIs and types: Enumerates Noise key/hash/tag/timestamp sizes, cookie sizes, anti-replay window sizes, protocol limits such as rekey/reject times and message counts, queue limits, and message types. Defines packed-by-layout C structs for handshake initiation, response, cookie, and data messages. `noise_encrypted_len()` and `message_data_len()` calculate authenticated ciphertext sizes. `DATA_PACKET_HEAD_ROOM`, `SKB_HEADER_LEN`, and `MESSAGE_PADDING_MULTIPLE` are used by send/receive and netdev setup.

Control flow: Header-only constants drive validation in `receive.c`, encryption layout in `send.c`, handshake construction in `noise.c`, MTU setup in `device.c`, and cookie handling. No executable flow exists.

State and persistence: No runtime state. The values encode stable protocol ABI and security limits.

Dependencies and integration points: Pulls Curve25519, ChaCha20-Poly1305, BLAKE2s, kernel, params, and skb definitions. Integrates with UAPI key length checks in `netlink.c`.

Risks: Size or alignment changes are wire-protocol breaking. Queue and timing constants affect DoS resistance, latency, and rekey behavior. Data headroom/tailroom must match encapsulation and authentication tag needs.

Test signals: Compile-time size checks, handshake interop, encrypted data length tests, MTU/headroom behavior, anti-replay counter selftest, and netlink key length `BUILD_BUG_ON()` checks.

# sources/distributed-fs/ceph-client/drivers/net/wireguard/queueing.h

Purpose: Declares WireGuard packet queue APIs and defines inline helpers for protocol validation, skb scrubbing, CPU selection, and enqueueing between per-device crypto queues and per-peer serial queues.

Important APIs and types: Declares queue init/free/per-CPU worker alloc, receive entry points/workers, send entry points/workers, `enum packet_state`, `struct packet_cb`, `PACKET_CB`, and `PACKET_PEER`. Inline helpers include `wg_check_packet_protocol()`, `wg_reset_packet()`, CPU selection helpers, `wg_prev_queue_peek()`, `wg_prev_queue_drop_peeked()`, `wg_queue_enqueue_per_device_and_peer()`, `wg_queue_enqueue_per_peer_tx()`, and `wg_queue_enqueue_per_peer_rx()`.

Control flow: `wg_queue_enqueue_per_device_and_peer()` marks an skb/list uncrypted, enqueues it first to the per-peer ordered queue, then to the per-device `ptr_ring`, and schedules a per-CPU crypto worker. Crypto workers later call TX or RX enqueue helpers, which take a temporary peer reference, publish final state with release semantics, then schedule the peer serial worker or NAPI.

State and persistence: Stores transient packet metadata in skb control buffer: nonce, keypair pointer, atomic state, MTU, and DS field. Manipulates peer references and queue state but owns no durable state.

Dependencies and integration points: Shared by `device.c`, `send.c`, `receive.c`, `peer.c`, and DEBUG selftests. Uses skb, IP/IPv6 tunnel helpers, NAPI, workqueues, atomics, and peer krefs.

Risks: `PACKET_CB` consumes skb control buffer, so callers must not need prior control metadata after enqueue. Release/acquire semantics are required to avoid serial consumers seeing incomplete crypto writes. `wg_reset_packet()` scrubs metadata differently for encapsulation to preserve hash values. Queue insertion partial failure must be handled by caller.

Test signals: TX/RX ordering under parallel crypto, skb control buffer correctness, GSO segmentation metadata, NAPI scheduling after decrypt, peer serial CPU choice, and DEBUG packet counter selftest declaration coverage.

# sources/distributed-fs/ceph-client/net/vmw_vsock/virtio_transport_common.c

## Purpose
`virtio_transport_common.c` implements the shared virtio/vhost/loopback vsock packet protocol. It builds and parses virtio-vsock headers, manages stream and seqpacket receive queues, implements credit-based flow control, handles connection state packets, shutdown/reset/close timeouts, packet tapping, zerocopy skb construction, and exports callback implementations used by concrete virtio-style transports.

## Important APIs, Types, And Functions
Key APIs include `virtio_transport_do_socket_init()`, `virtio_transport_connect()`, `virtio_transport_shutdown()`, `virtio_transport_stream_enqueue()`, `virtio_transport_seqpacket_enqueue()`, `virtio_transport_stream_dequeue()`, `virtio_transport_seqpacket_dequeue()`, `virtio_transport_recv_pkt()`, `virtio_transport_release()`, `virtio_transport_destruct()`, `virtio_transport_read_skb()`, and credit helpers `virtio_transport_get_credit()`, `virtio_transport_put_credit()`, and `virtio_transport_inc_tx_pkt()`.

## Control Flow
Sending starts in `virtio_transport_send_pkt_info()`: resolve local and remote CIDs/ports, reserve credit from the per-socket TX window, choose zerocopy when allowed, split payload into `VIRTIO_VSOCK_MAX_PKT_BUF_SIZE` packets, initialize headers with current buffer allocation and forward count, and hand packets to the concrete transport's `send_pkt()`. Receive enters `virtio_transport_recv_pkt()`, validates type, locates a connected or bound socket with optional namespace context, updates peer credit state, and dispatches by socket state. Listening sockets create connected children and respond; connecting sockets accept `OP_RESPONSE` or reset; established sockets enqueue RW payloads, process credit updates/requests, or process shutdown/reset.

## State And Persistence
Per-socket state is `struct virtio_vsock_sock`: TX counters `tx_cnt`, `peer_fwd_cnt`, `peer_buf_alloc`, `bytes_unsent`, and RX counters `fwd_cnt`, `last_fwd_cnt`, `rx_bytes`, `buf_alloc`, `buf_used`, `rx_queue`, and `msg_count`. Close uses `vsk->close_work` and `close_work_scheduled`. Receive queues persist skbs until userspace dequeues or `read_skb()` consumes them.

## Dependencies And Integration Points
The file depends on AF_VSOCK core callbacks, `linux/virtio_vsock.h`, skbuff APIs, zero-copy message infrastructure, tracepoints, vsockmon tap delivery, and concrete `struct virtio_transport` providers such as virtio, vhost, and loopback. It exports many symbols consumed by those providers.

## Risks And Edge Cases
Credit accounting is the highest-risk area: reserved credits must be returned on partial send, peer buffer shrink must not underflow, RX queue accounting must match skb lifetimes, and credit updates must avoid stalls without spamming control packets. Connection handling must avoid replying to RST with RST, must remove sockets after full peer shutdown so port reuse works, and must handle sockets closed or reassigned before `lock_sock()`. Seqpacket message boundaries rely on `SEQ_EOM` and `msg_count`; small-packet coalescing must not cross message boundaries.

## Test Signals
Important tests include stream and seqpacket transfers with fragmentation, MSG_PEEK, MSG_TRUNC, MSG_EOR, `SO_RCVLOWAT`, large sends beyond peer credit, buffer-size updates, zero-copy completion and fallback copy, malformed type/op/length packets, reset-no-socket paths, close timeout, simultaneous shutdown, `read_skb()` consumers, vsockmon output, and KCSAN/lockdep around RX/TX locks.

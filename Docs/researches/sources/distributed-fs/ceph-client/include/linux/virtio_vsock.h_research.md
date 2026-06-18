# sources/distributed-fs/ceph-client/include/linux/virtio_vsock.h

## Purpose
`virtio_vsock.h` defines the in-kernel virtio transport contract for AF_VSOCK sockets. It supplies skb layout helpers, per-socket virtio transport state, virtqueue identifiers, packet metadata, and the transport callback prototypes used by host/guest virtio-vsock drivers and the generic vsock core. In this Ceph-client source tree it is infrastructure, not Ceph-specific logic.

## Important APIs, Types, and Functions
Important definitions include `VIRTIO_VSOCK_SKB_HEADROOM`, `struct virtio_vsock_skb_cb`, `VIRTIO_VSOCK_SKB_CB()`, `virtio_vsock_hdr()`, skb reply and tap-delivery flag helpers, `virtio_vsock_skb_put()`, `virtio_vsock_alloc_skb()`, and queue helpers wrapping `sk_buff_head` operations under `spin_lock_bh()`. Buffer constants include `VIRTIO_VSOCK_DEFAULT_RX_BUF_SIZE`, `VIRTIO_VSOCK_MAX_BUF_SIZE`, and `VIRTIO_VSOCK_MAX_PKT_BUF_SIZE`. `enum { VSOCK_VQ_RX, VSOCK_VQ_TX, VSOCK_VQ_EVENT }` names the virtqueues. `struct virtio_vsock_sock` stores tx/rx credit state, buffer accounting, RX queue, and message count. `struct virtio_vsock_pkt_info` describes enqueue/dequeue packet parameters. `struct virtio_transport` embeds `struct vsock_transport` and adds `send_pkt()` plus optional `can_msgzerocopy()`. Declared APIs cover stream, datagram, and seqpacket enqueue/dequeue, credit get/put, socket initialization, poll notifications, buffer-size notification, connect/shutdown/release/destruct, receive packet dispatch, tap delivery, skb purging, and `read_skb`.

## Control Flow
Transmit paths allocate an skb with room for `struct virtio_vsock_hdr`, fill packet metadata from a `virtio_vsock_pkt_info`, charge credits in `virtio_vsock_sock`, and hand ownership to the transport `send_pkt()` callback. Large payloads can be stored as skb frags when `virtio_vsock_alloc_skb()` exceeds a costly-page linear allocation. Receive paths use the RX virtqueue to obtain skbs, decode the header with `virtio_vsock_hdr()`, enqueue payload into `vvs->rx_queue`, update `fwd_cnt`, and wake poll/read waiters through the notify hooks. Credit accounting is bidirectional: local buffer consumption updates forward counts and peer buffer fields determine whether writers may continue.

## State and Persistence
State is volatile kernel socket state. `struct virtio_vsock_sock` is attached through `vsock_sock->trans`; `tx_lock` protects transmit counters and unsent byte accounting, while `rx_lock` protects receive counters, queue state, and buffer usage. Skb control block fields are transient per-packet flags. No durable persistence exists; state lasts for socket, skb, and transport-device lifetimes.

## Dependencies and Integration Points
The header depends on uapi virtio-vsock ABI, skb/socket primitives, `net/af_vsock.h`, virtio queue users, net namespaces, and generic vsock notification structures. Integration points include the AF_VSOCK core, virtio device drivers, packet tap delivery, zerocopy send validation, datagram bind/allow policy, and poll/read/write paths exposed to user sockets.

## Risks
Credit and buffer accounting mistakes can deadlock streams or overrun peer buffers. `skb->cb` use must not conflict with other skb consumers. Header-room assumptions depend on the skb data pointer being reserved correctly. Queue helpers disable BH while taking the skb queue lock, so callers must avoid incompatible locking. Zerocopy capability checks must match the transport's descriptor limits. Nonlinear skb length manipulation in `virtio_vsock_skb_put()` is sensitive to skb layout.

## Test Signals
Useful signals include stream/datagram/seqpacket loopback tests, guest-host connect/shutdown races, RX/TX credit exhaustion and recovery, large payload fragmentation, zerocopy send paths, packet tap delivery, poll readiness transitions, socket teardown with queued skbs, and lockdep/KASAN coverage under concurrent read/write.

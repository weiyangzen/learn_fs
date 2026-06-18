# sources/distributed-fs/ceph-client/net/vmw_vsock/virtio_transport.c

## Purpose
`virtio_transport.c` is the virtio-vsock device driver and concrete guest-to-host transport. It owns virtqueue setup, transmit and receive workqueues, event handling, guest CID discovery, zero-copy capability checks, and registration of the virtio transport callbacks with the AF_VSOCK core.

## Important APIs, Types, And Functions
The central device object is `struct virtio_vsock`, containing RX/TX/event virtqueues, locks, work items, queued reply accounting, guest CID, seqpacket feature state, and scatterlist storage for TX. Important functions include `virtio_transport_send_pkt()`, `virtio_transport_send_pkt_work()`, `virtio_transport_rx_work()`, `virtio_vsock_vqs_init()`, `virtio_vsock_vqs_start()`, `virtio_vsock_vqs_del()`, `virtio_vsock_probe()`, `virtio_vsock_remove()`, and PM freeze/restore paths.

## Control Flow
Module init creates a percpu workqueue, registers the transport as `VSOCK_TRANSPORT_F_G2H`, and registers a virtio driver for `VIRTIO_ID_VSOCK`. Probe enforces one device per guest, allocates `struct virtio_vsock`, initializes queues and workers, discovers features such as `VIRTIO_VSOCK_F_SEQPACKET`, initializes virtqueues, assigns the RCU global `the_virtio_vsock`, fills RX/event queues, and enables TX processing.

Sends use a fast path that tries to lock the TX virtqueue and enqueue immediately; otherwise packets go to `send_pkt_queue` and `send_pkt_work`. TX completion consumes skbs and restarts queued sends. RX work drains RX buffers, validates packet and payload lengths, taps packets for monitoring, and calls `virtio_transport_recv_pkt()` in global namespace mode. Event work handles transport reset by refreshing guest CID and resetting connected sockets.

## State And Persistence
Global state is the RCU pointer `the_virtio_vsock` protected by `the_virtio_vsock_mutex`. Device state persists until removal or PM freeze, including queued replies used to throttle RX so reply packets do not exhaust the TX ring. Socket-specific state is mostly in `virtio_transport_common.c`.

## Dependencies And Integration Points
The driver depends on virtio core APIs, virtqueue callbacks, DMA-safe event buffers, workqueues, RCU, AF_VSOCK core registration, and shared virtio transport common helpers. It integrates with vsock taps and with connected-socket reset iteration on transport reset or device removal.

## Risks And Edge Cases
Important risks include global device replacement races, workqueue callbacks after virtqueue deletion, RX starvation when queued replies fill the ring, packet length validation before exposing payload, zero-copy packets larger than virtqueue capacity, and freeze/restore ordering. Virtio currently forces global namespace mode on receive because this transport path does not provide per-net context.

## Test Signals
Use virtio-vsock connect/send/recv tests, seqpacket feature negotiation, guest CID reset events, suspend/resume, hot remove, module unload, vsockmon packet capture, zero-copy send with large fragmented iovecs, queue pressure tests that force slow-path send, and lockdep/KASAN around device removal with active sockets.

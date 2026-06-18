# sources/distributed-fs/ceph-client/drivers/vhost/net.c

## Purpose

`net.c` implements the `/dev/vhost-net` misc device, a kernel vhost backend for virtio-net. It binds guest TX and RX virtqueues to host networking endpoints, primarily TAP/TUN and AF_PACKET raw sockets, and uses the shared vhost core to translate virtqueue descriptors, poll eventfds, log dirty memory, and signal completions. The file contains both the normal copy path and optional experimental TX zerocopy path, plus an XDP batching path for high-throughput TAP/TUN transmission.

## Important APIs, Types, and Functions

The main state is `struct vhost_net`, which embeds `struct vhost_dev`, two `struct vhost_net_virtqueue` instances, backend socket polls, TX zerocopy counters, and a page-frag cache. `struct vhost_net_virtqueue` extends `struct vhost_virtqueue` with virtio-net header lengths, zerocopy state (`upend_idx`, `done_idx`, `ubuf_info`, `ubufs`), an RX `ptr_ring`, a small batched RX queue, and a batched XDP buffer array. `struct vhost_net_ubuf_ref` is the reference-counted completion object used by zerocopy TX.

The device surface is `vhost_net_fops`, especially `vhost_net_open()`, `vhost_net_release()`, `vhost_net_ioctl()`, `vhost_net_chr_read_iter()`, `vhost_net_chr_write_iter()`, and `vhost_net_chr_poll()`. Frontend-specific ioctls are handled by `vhost_net_set_backend()`, `vhost_net_set_features()`, `vhost_net_set_owner()`, and `vhost_net_reset_owner()`. Data-path workers are `handle_tx()`, `handle_tx_copy()`, `handle_tx_zerocopy()`, `handle_rx()`, and the kick/socket-poll trampolines `handle_tx_kick()`, `handle_rx_kick()`, `handle_tx_net()`, and `handle_rx_net()`.

Backend helpers include `get_raw_socket()`, `get_tap_socket()`, `get_tap_ptr_ring()`, and `get_socket()`. Zerocopy helpers include `vhost_net_ubuf_alloc()`, `vhost_zerocopy_complete()`, `vhost_zerocopy_signal_used()`, and `vhost_net_flush()`. RX/TX descriptor helpers include `get_tx_bufs()`, `get_rx_bufs()`, `init_iov_iter()`, `vhost_net_build_xdp()`, `vhost_tx_batch()`, and `vhost_net_signal_used()`.

## Control Flow

Open allocates the device, the vq pointer array, RX batching queue, TX XDP batch buffer, initializes both virtqueues and socket polls, and stores the device in `file->private_data`. Userspace first sets owner through the shared vhost ioctl path, configures memory and vring state, negotiates features, and then uses `VHOST_NET_SET_BACKEND` to attach each virtqueue to a socket fd. Backend setup validates owner and ring access, resolves the fd to a supported socket, disables old polling, installs the new backend, initializes vq access, starts polling, and records the TAP/TUN RX `ptr_ring` when available.

TX starts from a guest kick or socket writable poll. `handle_tx()` locks the TX vq, checks backend and metadata access, disables guest notifications and socket polling, then selects zerocopy only when the socket has `SOCK_ZEROCOPY` and the module parameter enabled it. The copy path repeatedly obtains one descriptor chain with `vhost_get_vq_desc_n()`, rejects input descriptors on TX, skips the virtio header, and sends the payload through `sock->ops->sendmsg()`. If batching is possible, it converts packet data to XDP buffers and flushes them with a `TUN_MSG_PTR` control message through `vhost_tx_batch()`. Otherwise it uses `MSG_MORE` according to total length and ring availability. On transient send pressure it discards the descriptor cursor with `vhost_discard_vq_desc()`, re-enables socket polling, and exits.

The zerocopy path records the descriptor in `vq->heads[upend_idx]`, attaches a `ubuf_info_msgzc` with `vhost_ubuf_ops`, increments the ubuf reference, and sends the packet with `TUN_MSG_UBUF`. Completion arrives in `vhost_zerocopy_complete()`, marks the corresponding head as done or failed, drops the ubuf ref, and queues vhost work periodically or when the count drains. `vhost_zerocopy_signal_used()` advances contiguous completed heads and publishes them to the used ring.

RX starts from a guest kick or socket readable poll. `handle_rx()` locks the RX vq, checks metadata, disables notifications and socket polling, peeks the next packet length either from TAP/TUN `ptr_ring` or socket receive queue, and optionally busy-polls the paired TX queue. It then collects enough guest input descriptors through `get_rx_bufs()`, receives the socket packet into the guest iovecs, supplies or patches the virtio-net header and `num_buffers`, logs dirty writes when requested, batches used-ring entries, and re-enables polling or notifications when no packet or no descriptors are available.

## State and Persistence Behavior

All state is per-open file and lives in memory. There is no disk persistence. Persistent-for-open state includes negotiated feature bits on each vq, derived header lengths (`vhost_hlen` and `sock_hlen`), backend socket references, RX ring pointers, XDP batch buffers, zerocopy completion arrays, and the shared vhost memory/IOTLB state. `vhost_net_stop()` clears backends and stops polling. `vhost_net_flush()` drains vhost workers and zerocopy DMA completions. `vhost_net_release()` stops backends, flushes twice to cover self-requeued work, drops socket refs, drains RCU, frees buffers, and releases the vhost core state.

## Dependencies and Integration Points

The file depends on `vhost.c` and `vhost.h` for virtqueue parsing, eventfd polling, worker execution, IOTLB miss handling, dirty logging, and owner/memory ioctls. It integrates with Linux socket operations, TAP/TUN helpers (`tun_get_socket()`, `tun_get_tx_ring()`, `tun_ptr_free()`), TAP helpers, AF_PACKET raw sockets, XDP buffer APIs, skb queue inspection, page-frag allocation, eventfd, miscdevice registration, and virtio-net feature definitions. Userspace components such as QEMU configure this device through vhost ioctls and pass the TAP/TUN fd as backend.

## Risks and Edge Cases

Descriptor parsing is security-sensitive because guest-provided vring state controls iovec translation and used-ring writes. RX must avoid overrun when one packet spans more than `UIO_MAXIOV` segments and must discard cleanly when userspace races by consuming socket data. TX must correctly rewind descriptor cursors on transient send failures, especially with `VIRTIO_F_IN_ORDER`, XDP batching, and zerocopy outstanding completions. Zerocopy state is subtle because completions can arrive out of order and are coordinated with RCU, a refcount, vq locks, and device flush. In this source snapshot, `vhost_net_ubuf_put()` visibly contains two consecutive `rcu_read_unlock()` calls after one `rcu_read_lock()`, which is a high-risk imbalance if not corrected elsewhere in the source history. Backend replacement must stop polling before dropping socket refs and must flush old work after the swap. Busy polling uses `mutex_trylock()` to avoid lock-order inversion but can miss opportunities under contention.

## Test Signals

Useful signals include building with `CONFIG_VHOST_NET`, boot tests that create `/dev/vhost-net`, QEMU virtio-net traffic over TAP/TUN, migration or dirty-log tests with `VHOST_F_LOG_ALL`, IOTLB tests with `VIRTIO_F_ACCESS_PLATFORM`, stress tests that repeatedly set/unset backends, traffic tests with mergeable RX buffers and `VIRTIO_F_IN_ORDER`, and fault injection around `sendmsg()`, `recvmsg()`, descriptor translation, and zerocopy completions. The optional zerocopy module parameter should be tested separately because it activates paths not used by default.

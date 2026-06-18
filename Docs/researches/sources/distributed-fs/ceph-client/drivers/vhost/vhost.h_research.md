# sources/distributed-fs/ceph-client/drivers/vhost/vhost.h

## Purpose
`vhost.h` is the private shared interface for Linux vhost device implementations. It defines the in-kernel representation of vhost devices, virtqueues, workers, polling hooks, logging state, IOTLB metadata, and feature helpers used by concrete backends such as vhost-vsock, vhost-net, and vhost-scsi.

## Important APIs, types, and functions
Key types are `struct vhost_dev`, `struct vhost_virtqueue`, `struct vhost_worker`, `struct vhost_poll`, `struct vhost_work`, `struct vhost_vring_call`, and `struct vhost_msg_node`. The header declares lifecycle APIs (`vhost_dev_init`, `vhost_dev_set_owner`, `vhost_dev_stop`, `vhost_dev_cleanup`, `vhost_dev_reset_owner`), ioctl dispatch (`vhost_dev_ioctl`, `vhost_vring_ioctl`, `vhost_worker_ioctl`), queue traversal/completion (`vhost_get_vq_desc`, `vhost_get_vq_desc_n`, `vhost_add_used*`, `vhost_signal`), polling (`vhost_poll_*`), IOTLB setup (`vhost_init_device_iotlb`), and character-device helpers (`vhost_chr_*`). Inline helpers cover backend private data, negotiated features, endian conversion, and feature-array construction.

## Control flow
Backends allocate `vhost_virtqueue` arrays, call `vhost_dev_init`, set ownership from userspace, configure rings through ioctls, then start queue processing. Queue kicks enter `vhost_poll`, enqueue `vhost_work`, parse descriptors, copy data, publish used elements, and signal eventfds. Device shutdown clears backend pointers, flushes queued work, tears down IOTLB/logging state, and releases owner resources.

## State and persistence
State is entirely kernel runtime state: owner `mm`, queue ring pointers, eventfd contexts, per-vq indices, feature bits, IOTLB pointers, logging buffers, worker xarray, pending/read message lists, and backend-private pointers. Nothing persists across device close. Synchronization is explicit through device/vq mutexes, spinlocks for IOTLB, RCU worker pointers, and wait queues.

## Dependencies and integration points
The header depends on eventfd, poll, uio, virtio ring/config, xarray, irq bypass, vhost IOTLB, and Linux feature-bit helpers. It integrates with userspace vhost ioctls, virtio feature negotiation, eventfd notifications, dirty-page logging, memory translation, and backend-specific transport drivers.

## Risks and test signals
Risks concentrate around user-provided ring pointers, descriptor bounds, endian mode, feature mismatch, worker swaps, IOTLB permissions, and eventfd lifetime. Test signals include vhost ioctl coverage, malformed descriptor chains, feature negotiation matrices, cross-endian legacy tests, IOTLB map/unmap races, dirty logging, worker attach/detach, and backend teardown while work is pending.

# sources/distributed-fs/ceph-client/include/linux/virtio.h

## Purpose
This header defines the core virtio device and virtqueue API used by all Linux virtio drivers and transports.

## Important APIs, types, and functions
Key types are `virtqueue`, `virtio_map`, `virtio_admin_cmd`, `virtio_device`, and `virtio_driver`. APIs add in/out buffers and scatterlists, kick/notify queues, get completed buffers, manage callbacks, detach unused buffers, query/reset/resize vrings, register/unregister devices and drivers, signal config changes, freeze/restore/reset devices, iterate queues, map/unmap DMA buffers, and initialize optional debugfs filtering.

## Control flow, state, and persistence
Transports create `virtio_device` objects with config/map ops; drivers match by ID, negotiate features, find virtqueues, add buffers, kick devices, and handle callbacks/config changes. Core state includes device status flags, config-change locks, queue lists, negotiated feature arrays, mapping token, private driver data, and optional debug state. Persistence is not defined; virtio state is runtime and renegotiated after reset.

## Dependencies and integration points
It depends on scatterlists, device model, DMA mapping, completions, spinlocks, mod device tables, and virtio feature helpers. It integrates all virtio transports, virtio-net/block/scsi/console/etc. drivers, vDPA/VDUSE mapping, PM, and debugfs.

## Risks and test signals
Risks include queue callback races, broken-device state after reset, DMA mapping mismatches, feature-table omissions, and improper callback enable/disable loops. Tests should cover buffer enqueue/dequeue, notification suppression, reset/resize, DMA map/unmap, feature negotiation, PM freeze/restore, config change gating, and driver registration lifecycle.

# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_virtio.c

## Purpose
Implements the remoteproc virtio transport. It turns `RSC_VDEV` resource-table entries into Linux virtio devices, allocates and wires vrings, exposes config/status/features through the resource table, and routes mailbox kicks between processors and virtqueues.

## Important APIs, Types, And Functions
Exports `rproc_vq_interrupt()`. `rproc_virtio_config_ops` implements virtio callbacks for features, status, vq discovery/removal, reset, and config access. `rproc_virtio_probe()` consumes `struct rproc_vdev_data`, parses vrings, allocates notify IDs, adds an rvdev subdevice, and holds an rproc reference. `rproc_add_virtio_dev()` registers the child `struct virtio_device` when the subdevice starts.

## Control Flow
Core registers a `rproc-virtio` platform device for each vdev resource. Probe copies DMA range information from the remoteproc parent, sets DMA ops/mask, parses each vring, allocates vring resources, and registers subdevice start/stop callbacks. Subdevice start associates dedicated or fallback reserved memory, allocates a virtio device, and registers it. Virtio drivers call `find_vqs()`, which creates vrings on preallocated memory and writes assigned addresses back to the resource table.

Outbound notifications call platform `ops->kick(rproc, notifyid)`. Inbound platform interrupts call `rproc_vq_interrupt()`, which looks up the notify ID in `rproc->notifyids` and dispatches `vring_interrupt()`. Stop removes child virtio devices and remove frees vring IDs and drops references.

## State And Persistence Behavior
State spans the resource table, `struct rproc_vdev`, `struct rproc_vring`, notify IDR, vring carveouts, platform devices, and child virtio devices. Virtio status, guest features, config data, vring addresses, and notify IDs are stored in `rproc->table_ptr`, which may be cached or loaded table memory depending on lifecycle stage.

## Dependencies And Integration Points
Integrates with core resource parsing, reserved-memory helpers, DMA coherent memory pools, Linux virtio, `virtio_ring`, platform driver registration, and platform mailbox/doorbell `kick` callbacks. Supports standard remoteproc vdev layout with at most two vrings per vdev.

## Risks
Packed rings are disabled because preallocated vring memory is used. Feature negotiation asserts that features fit in 32 bits. Config access logs and returns on bounds errors without reporting to virtio callers. Cleanup depends on device-release ordering because virtio devices hold platform-device and remoteproc references. Reserved-memory fallback to parent index 0 is best-effort and may fall back silently.

## Test Signals
Boot firmware with vdevs, verify virtio/rpmsg registration, notify ID assignment, resource-table status/features/vring updates, inbound and outbound kicks, stop/restart cleanup, missing `kick` rejection, reserved-memory vdev buffer assignment, and malformed vring counts, sizes, or alignments.

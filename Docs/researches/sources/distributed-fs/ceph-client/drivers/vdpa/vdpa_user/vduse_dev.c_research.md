# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/vduse_dev.c

## Purpose

`vduse_dev.c` implements VDUSE, the kernel side of userspace-backed vDPA devices. It exposes `/dev/vduse/control` for creating and destroying device instances, `/dev/vduse/$name` for the userspace device process to exchange control messages and eventfds, and a vDPA management device named `vduse` so the vDPA bus can instantiate the prepared device. The implementation is a bridge between virtio/vdpa configuration operations, userspace request/response messages, eventfd kicks/interrupts, and VDUSE IOVA domains with optional bounce-buffer backed user memory.

## Important APIs, Types, and Functions

Core state lives in `struct vduse_dev`, which owns the device identity, feature bits, config space copy, status/generation, virtqueue array, address-space array, vq groups, message queues, work items, and locks. `struct vduse_virtqueue` tracks per-vq addresses, queue size, split/packed state, readiness, kickfd, callback, irq affinity, and sysfs kobject. `struct vduse_as` wraps a `vduse_iova_domain`, optional pinned user bounce memory, and `mem_lock`; `struct vduse_vq_group` maps a vq group to an address space under an rwlock.

The userspace protocol is centered on `vduse_dev_msg_sync()`, `vduse_dev_read_iter()`, and `vduse_dev_write_iter()`. The vDPA surface is `vduse_vdpa_config_ops`, with queue address/kick/callback/ready/state, feature/status/config, reset, map, group-asid, and map-token callbacks. DMA mapping for virtio uses `vduse_map_ops`, which forwards map/unmap/sync/coherent allocation operations to the group's current IOVA domain. Control ioctls include `VDUSE_GET_API_VERSION`, `VDUSE_SET_API_VERSION`, `VDUSE_CREATE_DEV`, and `VDUSE_DESTROY_DEV`; device ioctls include IOTLB fd/info queries, config update, vq setup/info/kickfd/irq injection, and UMEM registration.

## Control Flow

Module init registers the VDUSE class, allocates a char-device major, installs the control cdev at minor 0, installs per-device cdev coverage for remaining minors, creates high-priority IRQ workqueues, initializes the VDUSE IOVA subsystem, and registers a vDPA management device. Userspace opens `/dev/vduse/control`, negotiates API version, and calls `VDUSE_CREATE_DEV`. Creation validates reserved fields, feature constraints, device type, group/as counts, queue count, and config size, allocates the `vduse_dev`, IDR minor, config copy, vq groups, address spaces, `/dev/vduse/$name`, and per-vq sysfs objects.

Userspace then opens `/dev/vduse/$name`. vDPA device creation occurs later through the management-device `dev_add` callback: the named VDUSE device must exist and every virtqueue must have a nonzero `num_max`; domains are created, split across `bounce_size / nas`, and `_vdpa_register_device()` publishes the device. vDPA operations enqueue synchronous messages when userspace must perform work, for example status changes, IOTLB updates, and vq state reads. Userspace reads a request from `send_list`, which moves it to `recv_list`, writes a matching response by request id, and wakes the waiting kernel caller.

Data movement maps through the vDPA map token. Each virtqueue resolves to a group, a group resolves to an address space, and the address space owns the IOVA domain. API v0 has one group/asid; API v1 supports multiple groups and address spaces and can rebind a group via `VDUSE_SET_VQ_GROUP_ASID`. UMEM registration pins user pages for the full bounce-map range, enforces `RLIMIT_MEMLOCK`, charges `mm->pinned_vm`, and installs those pages into the domain's bounce map. Deregistration removes the bounce pages, dirties/unpins them, drops the mm reference, and frees the page array.

## State and Persistence Behavior

State is in-kernel and per-module, not file backed. The global `vduse_idr` maps minors to live `vduse_dev` objects under `vduse_lock`. Each device persists until `VDUSE_DESTROY_DEV`, which refuses busy devices with a registered vDPA instance or connected userspace endpoint, resets queues, destroys the class device, removes the IDR entry, frees config/vqs/domains/name/groups, and drops the module reference.

Reset clears driver status/features, increments config generation, removes config and queue callbacks, flushes IRQ/kick work, resets queue addresses/state/ready flags, drops kickfds, and resets bounce maps while preserving coherent mappings that are later freed through the coherent free callback. A message timeout marks the device broken, fails all queued messages, wakes poll/read waiters, and prevents further device ioctls. Releasing `/dev/vduse/$name` deregisters all UMEM, moves in-flight `recv_list` messages back to `send_list` so a reconnecting process can answer them, and marks the endpoint disconnected.

## Dependencies and Integration Points

The file integrates with the vDPA core (`vdpa_alloc_device`, `_vdpa_register_device`, `vdpa_mgmtdev_register`), virtio config and ring state, eventfd, character devices, sysfs/kobjects, workqueues, IDR, UIO iterators, pinned user pages, and the local `iova_domain.h` helpers. It depends on VDUSE UAPI structs from `uapi/linux/vduse.h`, vhost IOTLB maps, and virtio feature definitions for block, net, and fs devices. The only allowed device ids are block, net, and fs; net additionally requires `CAP_NET_ADMIN` at creation.

## Risks and Edge Cases

The message protocol has several ordering-sensitive lists under `msg_lock`. Partial `copy_to_iter()` requeues a message, while a timeout removes it and marks the whole device broken; tests need races between timeout, userspace response, release, and poll. UMEM registration increments `pinned_vm` by requested `npages` after `pin_user_pages()` returns `pinned`; this assumes the full pin succeeded and relies on prior equality checks. `vduse_vq_update_effective_cpu()` loops until it finds an online CPU or resets to `IRQ_UNBOUND`; affinity masks are validated through sysfs, but unexpected CPU hotplug behavior deserves coverage.

Feature validation is intentionally restrictive because config space is read-only to the vDPA driver: block WCE and net CTRL_VQ are rejected, net requires modern virtio, and every device must advertise `VIRTIO_F_ACCESS_PLATFORM`. API-version compatibility is another risk: v0 callers must not set groups/asids, while v1 callers must provide valid nonzero group/as counts and zero reserved fields.

## Test Signals

Useful tests include API version negotiation, create/destroy validation, duplicate names, busy destroy, open exclusivity, message request/response, timeout-to-broken behavior, reconnect with `recv_list` requeue, vq setup for API v0/v1, kickfd assignment/deassignment and queued kicks, config IRQ and vq IRQ injection, sysfs irq affinity parsing, bounce-size changes before and after domain allocation, UMEM pin/deregistration, IOTLB fd/info queries, multiple ASID group rebinding, reset cleanup, and module init/exit failure unwinds. vDPA integration should verify a created device can be registered only after all queues are configured and that DMA map/unmap/sync callbacks use the active group address space.

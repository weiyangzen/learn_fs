# sources/distributed-fs/ceph-client/include/uapi/linux/vhost.h

Purpose: defines vhost ioctl numbers for userspace hypervisors configuring in-kernel virtio accelerators such as vhost-net, vhost-scsi, vhost-vsock, and vhost-vDPA.

Important APIs/types/functions: core ioctls include `VHOST_GET_FEATURES`, `VHOST_SET_FEATURES`, `VHOST_SET_OWNER`, `VHOST_RESET_OWNER`, `VHOST_SET_MEM_TABLE`, log base/fd setup, worker creation/freeing, virtqueue setup (`VHOST_SET_VRING_NUM`, `ADDR`, `BASE`, `GET_VRING_BASE`, endian, worker attach/get), eventfd binding (`KICK`, `CALL`, `ERR`), busy-loop timeout, and backend feature get/set. Device-family ioctls include `VHOST_NET_SET_BACKEND`, vhost-scsi endpoint/events ABI, vhost-vsock guest CID/running, and a large vhost-vDPA surface for device id/status/config, vring enable/count/size/group/ASID, config callbacks, IOVA range, suspend/resume, feature arrays, and fork-owner control.

Control flow: userspace normally opens a vhost device, optionally configures fork-owner mode before ownership, calls `VHOST_SET_OWNER`, negotiates features, installs guest memory, configures each virtqueue's size/base/address/endian/eventfds, attaches a backend, then starts the emulated virtio device. Migration and reset flows query vring bases, stop or unbind backends, log writes, and for vDPA call suspend/resume or status/config ioctls. Worker ioctls let one device create extra vhost workers and bind selected virtqueues to them.

State and persistence: state lives in the vhost kernel device fd: exclusive owner, memory table, log settings, feature masks, worker pool, per-vring geometry/base/eventfds/worker/endian/busy-loop settings, backend bindings, and vDPA status/config/group/ASID state. `VHOST_RESET_OWNER` and fd close discard most state; vDPA suspend requires preserving enough device-specific state for resume.

Dependencies and integration: includes `linux/vhost_types.h`, `linux/types.h`, and `linux/ioctl.h`. It integrates with virtio rings, eventfd, tap/raw sockets, target core for vhost-scsi, AF_VSOCK, vDPA hardware/software devices, QEMU, and userspace memory slots.

Risks: `VHOST_SET_OWNER` ordering is mandatory and many ioctls fail before ownership. Memory regions and vring addresses must match guest mappings and alignment requirements from `vhost_types.h`. Incorrect eventfd binding can hang guest I/O or lose interrupts. vDPA ASID/group ioctls affect DMA isolation, and suspend/resume support must be feature-checked. Feature-array and extended feature ioctls share command numbers with feature masks in ways userspace must call with the exact expected struct.

Test signals: QEMU vhost-net/scsi/vsock smoke tests, virtqueue setup/teardown tests, live migration tests verifying vring base and logging, vDPA conformance tests for config/status/IOVA/group APIs, eventfd kick/call tests, worker attach/free tests, and UAPI ioctl-number/layout checks.

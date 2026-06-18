# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/vhost.h

## Purpose

`vhost.h` defines the userspace ioctl ABI for in-kernel virtio accelerators such as vhost-net, vhost-scsi, vhost-vsock, and vhost-vDPA. Perf trace beauty uses it to decode ownership/setup sequencing, feature negotiation, vring/eventfd controls, worker controls, backend commands, vDPA management, feature arrays, and fork-owner controls.

## Important APIs, Types, and Constants

Important definitions include `VHOST_FILE_UNBIND`, ioctl type `VHOST_VIRTIO`, feature get/set ioctls, owner reset/set, memory table, log base/fd, worker creation/free/attach/get, vring num/addr/base/endian/eventfd/busyloop commands, backend feature commands, `VHOST_NET_SET_BACKEND`, vhost-scsi endpoint/events, vhost-vsock CID/running, many vhost-vDPA device/status/config/vring/group/ASID/suspend/resume/query commands, feature array commands, and `VHOST_SET/GET_FORK_FROM_OWNER`. Most struct types come from `linux/vhost_types.h`.

## Control Flow and Integration

Typical setup opens a vhost fd, calls `VHOST_SET_OWNER`, negotiates features, sets the guest memory table, configures dirty logging if needed, sets each vring's size/address/base/endian/eventfds, binds backend resources, optionally creates and attaches workers, then uses get-base/suspend/resume/unbind/reset operations for migration or teardown. Perf decodes these ioctl commands and associated struct namespaces.

## State and Persistence Behavior

Most commands mutate kernel device state tied to the fd: ownership, memory tables, logging, features, backend fds, vring configuration, eventfd bindings, worker allocation, vDPA status/config/groups/ASIDs, and running/suspended state. vDPA suspend requires preserving restore state. Workers are freed explicitly when unattached or implicitly on close.

## Dependencies and Integration Points

The header includes `linux/vhost_types.h`, `linux/types.h`, and `linux/ioctl.h`. It integrates with virtio, eventfd, tap/raw sockets, SCSI target infrastructure, vsock, vDPA, IOMMU/address spaces, dirty logging, worker threads, cgroups/namespaces, and config gates such as `CONFIG_VHOST_ENABLE_FORK_OWNER_CONTROL`.

## Risks

Commands are order-dependent; a decoded name does not imply the operation was valid. Some ioctl directions contain read-index/write-result semantics inside the struct. Worker controls create kernel execution resources constrained by ownership and limits. vDPA suspend/resume and vring/group queries are migration-critical. Fork-owner controls are config-gated. `VHOST_FILE_UNBIND` is signed `-1` and should be displayed distinctly.

## Test Signals

Decode vhost-net startup traces showing set owner, features, memory table, vrings, eventfds, and backend bind. Decode net/scsi/vsock/vDPA commands without conflating struct types. Unit-check worker, busyloop, feature-array, suspend/resume, group/ASID, fork-owner commands, and signed unbind fd display.

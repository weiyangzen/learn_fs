# sources/distributed-fs/ceph-client/include/uapi/linux/vdpa.h

## Purpose
Defines the generic netlink userspace ABI for vDPA device management.

## Important APIs, Types, And Constants
`VDPA_GENL_NAME` is `"vdpa"` and `VDPA_GENL_VERSION` is `0x1`. `enum vdpa_command` covers management-device discovery, vDPA device create/delete/get, configuration dump, virtqueue stats, and device attribute setting. `enum vdpa_attr` defines netlink attributes for management device bus/name/supported classes; vDPA device name, id, vendor id, queue counts and sizes; virtio-net config (MAC, status, queue pairs, MTU); negotiated/supported/provisioned features; per-queue index; vendor attributes; and virtio-blk configuration fields including capacity, block size, segments, queue count, discard/write-zeroes limits, read-only, and flush flags.

## Control Flow, State, And Persistence
Userspace sends generic netlink commands to list management devices, create vDPA devices under a management device, inspect config/stats, set selected attributes, and delete devices. Persistent state is kernel vDPA device registration and driver-backed configuration; netlink messages are transient.

## Dependencies And Integration Points
This header has no includes because it is constants-only. It integrates with the kernel vDPA subsystem, virtio device classes, vdpa tooling, management drivers such as hardware accelerators or software backends, and netlink libraries.

## Risks And Test Signals
Risks include attribute type/width mismatches, missing 64-bit alignment padding for u64 attributes, feature negotiation inconsistencies, and tool/kernel skew when new attributes are added before `VDPA_ATTR_MAX`. Tests should exercise netlink policy validation, dump/create/delete flows, feature provisioning, queue stats, and virtio-net/blk config reporting.

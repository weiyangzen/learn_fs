
# sources/distributed-fs/ceph-client/include/uapi/linux/if_tun.h

## Purpose

`if_tun.h` defines the user-space ioctl and data-structure ABI for Universal TUN/TAP devices, including device creation/configuration, queue management, offload flags, BPF filters, carrier, netns access, packet-info headers, and TAP multicast filters. The complete 127-line file was read.

## Important APIs, Types, and Functions

Important ioctls include `TUNSETIFF`, `TUNSETPERSIST`, `TUNSETOWNER`, `TUNSETGROUP`, `TUNGETFEATURES`, `TUNSETOFFLOAD`, `TUNATTACHFILTER`, `TUNSETVNETHDRSZ`, `TUNSETQUEUE`, `TUNSETVNETLE/BE`, `TUNSETSTEERINGEBPF`, `TUNSETFILTEREBPF`, `TUNSETCARRIER`, and `TUNGETDEVNETNS`. Flags include `IFF_TUN`, `IFF_TAP`, `IFF_NO_PI`, `IFF_VNET_HDR`, `IFF_MULTI_QUEUE`, `IFF_ATTACH_QUEUE`, `IFF_DETACH_QUEUE`, `IFF_PERSIST`, and offloads `TUN_F_*`. Structs are `tun_pi` and flexible `tun_filter`.

## Control Flow

User space opens `/dev/net/tun`, issues `TUNSETIFF` and other ioctls, then reads/writes packets. Kernel TUN/TAP code prepends or strips `tun_pi` depending on `IFF_NO_PI`, manages queues, applies optional filters, and advertises or consumes offload metadata.

## State and Persistence Behavior

Per-device state includes owner/group, persistence, queue attachment, vnet header size and endian mode, offload capabilities, BPF/filter settings, and carrier. Persistent devices survive fd close when `TUNSETPERSIST` is enabled.

## Dependencies and Integration Points

It includes `linux/types.h`, `linux/if_ether.h`, and `linux/filter.h`. It integrates with character-device ioctls, netdevices, virtio-style vnet headers, BPF filters, network namespaces, and virtual networking stacks.

## Risks and Edge Cases

`IFF_NO_PI` and `IFF_NOFILTER` share the same numeric value in different contexts, so callers must interpret flags by ioctl path. Other risks are multi-queue attach/detach races, endian mode support, offload feature mismatch, flexible filter sizing, and persistent-device ownership mistakes.

## Test Signals

TUN/TAP selftests should cover device creation, persistence, ownership, queue attach/detach, packet-info present/absent modes, vnet header sizing/endian, BPF filters, carrier toggles, and offload negotiation.

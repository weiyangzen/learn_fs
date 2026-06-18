# sources/distributed-fs/ceph-client/tools/include/uapi/linux/if_tun.h

Purpose: defines the userspace ioctl and packet-header ABI for `/dev/net/tun` TUN/TAP virtual network devices.

Important APIs/types: ioctl constants configure device creation, persistence, ownership/group, link type, offloads, filters, queue attach/detach, ifindex, virtio-net header size/endian, steering/filter eBPF programs, carrier, and device netns fd. `TUNSETIFF` flags include `IFF_TUN`, `IFF_TAP`, `IFF_NO_PI`, `IFF_VNET_HDR`, `IFF_TUN_EXCL`, `IFF_MULTI_QUEUE`, and read-only persistence state. Feature flags include checksum, TSO4/6, ECN, and UFO. `struct tun_pi` is the optional per-packet protocol header, and `struct tun_filter` configures TAP multicast filtering.

Control flow, state, and persistence: userspace opens the tun device, issues `TUNSETIFF`, optionally sets queues/offloads/filters/persistence, then reads/writes packets. Device and queue state persists while file descriptors are open; `TUNSETPERSIST` can keep the netdev beyond fd lifetime.

Dependencies and integration points: depends on Ethernet and socket-filter headers. It integrates VPNs, containers, emulators, virtual switches, eBPF steering, and virtio-net compatible packet paths.

Risks and test signals: risks include flag aliasing (`IFF_NO_PI` and `IFF_NOFILTER` share a value in different contexts), multi-queue attach/detach races, wrong virtio header size/endian, and unsupported offload claims. Tests should create TUN and TAP devices, send/receive packets with and without PI/VNET headers, attach filters/eBPF, exercise multi-queue, and verify persistence/ownership permissions.

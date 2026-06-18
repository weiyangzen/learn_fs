
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bpqether.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/bpqether.h

## Purpose
Defines the legacy BPQ Ethernet UAPI used by AX.25-over-Ethernet drivers and tools. It exposes private socket ioctl numbers and small request structures for configuring BPQ Ethernet addresses and level-1 parameters.

## APIs, Control Flow, and State
Important exports are `SIOCSBPQETHOPT`, `SIOCSBPQETHADDR`, `SIOCGBPQETHPARAM`, `SIOCSBPQETHPARAM`, `struct bpq_ethaddr`, and `struct bpq_req`. `bpq_ethaddr` carries a destination Ethernet address, accepted source address, and an AX.25 address string sized by `AX25_ADDR_LEN`. `bpq_req` carries command, speed, clock mode, and persistence-style link parameters. The header contains no executable logic; control flow is in the BPQ Ethernet netdevice ioctl handlers, and state is persisted by the driver/device configuration.

## Dependencies, Integration, Risks, and Tests
Depends on `<linux/if_ether.h>` and AX.25 sizing conventions. Integration points include amateur-radio AX.25 networking, netdevice private ioctl dispatch, and legacy BPQ configuration tools. Risks are ioctl-number collisions in private ranges, fixed-size address/name assumptions, lack of modern netlink-style extensibility, and tools depending on obsolete driver behavior. Test signals include ioctl compatibility tests with BPQ devices, address length validation, and regression tests for 32/64-bit userspace structure layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bpqether.h -->

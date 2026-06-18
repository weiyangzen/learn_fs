<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_infiniband.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_infiniband.h

## Purpose
`if_infiniband.h` defines the Linux UAPI hardware address length for IP over InfiniBand interfaces.

## Important APIs, types, and functions
The single exported constant is `INFINIBAND_ALEN`, set to 20 octets for IPoIB hardware addresses.

## Control flow
There is no control flow. Network code and userspace tools use the constant when sizing link-layer address buffers for ARPHRD_INFINIBAND/IPoIB devices.

## State and persistence behavior
The header carries no state. IPoIB hardware addresses are per-interface/per-neighbor live network state managed by the InfiniBand and netdevice stacks.

## Dependencies and integration points
It integrates with IPoIB netdevices, ARP/neighbor tables, rtnetlink address dumps, packet sockets, and tools displaying link-layer addresses.

## Risks and test signals
Risks include assuming Ethernet-length addresses for IPoIB, truncating rtnetlink or neighbor addresses, and inconsistent libc/kernel header use. Test signals include IPoIB link dumps, neighbor entry formatting, address buffer size tests, and packet socket sockaddr_ll handling for 20-byte addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_infiniband.h -->

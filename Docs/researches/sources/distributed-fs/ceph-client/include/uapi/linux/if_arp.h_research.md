<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_arp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_arp.h

## Purpose
`if_arp.h` defines ARP hardware type constants, ARP operation codes, flags, and request structures used by neighbor/ARP ioctls and packet parsers.

## Important APIs, types, and functions
It exports many `ARPHRD_*` link-layer identifiers, including Ethernet, loopback, tunnel, IEEE 802 variants, CAN, Infiniband, Phonet, MCTP, and special `ARPHRD_NONE`/`VOID`. Operation codes include `ARPOP_REQUEST`, `REPLY`, `RREQUEST`, `RREPLY`, `InREQUEST`, `InREPLY`, and `NAK`. `struct arphdr` defines wire ARP header fields. `struct arpreq` and `struct arpreq_old` carry ioctl requests for protocol address, hardware address, flags, netmask, and device name. Flags include `ATF_COM`, `ATF_PERM`, `ATF_PUBL`, `ATF_USETRAILERS`, `ATF_NETMASK`, and `ATF_DONTPUB`.

## Control flow
ARP packets use `arphdr` followed by variable address fields. User space manages ARP cache entries through socket ioctls using `arpreq`; the kernel resolves, inserts, updates, deletes, or exposes entries based on flags.

## State and persistence behavior
Neighbor table entries, permanent/public flags, netmask proxy entries, and device-scoped ARP state are live network-namespace state. Wire headers are transient packets.

## Dependencies and integration points
It depends on `<linux/netdevice.h>`-compatible sizes and socket address types. It integrates with Ethernet/IP ARP, neighbor tables, netdevice hardware types, packet sockets, and legacy net-tools.

## Risks and test signals
Risks include hardware-type mismatches, ioctl struct compatibility, proxy ARP netmask misuse, stale permanent entries, and new link types requiring stable IDs. Test signals include ARP request/reply captures, `arp`/`ip neigh` interoperability, add/delete/proxy entries, namespace isolation, and packet parser tests for hardware lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_arp.h -->

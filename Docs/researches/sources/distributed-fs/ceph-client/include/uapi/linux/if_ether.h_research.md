<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_ether.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_ether.h

## Purpose
`if_ether.h` defines Ethernet frame sizes, MTU limits, EtherType/protocol constants, pseudo protocol IDs used by packet sockets, and the Ethernet header layout.

## Important APIs, types, and functions
Constants include `ETH_ALEN`, `ETH_TLEN`, `ETH_HLEN`, `ETH_ZLEN`, `ETH_DATA_LEN`, `ETH_FRAME_LEN`, `ETH_FCS_LEN`, `ETH_MIN_MTU`, `ETH_MAX_MTU`, many `ETH_P_*` protocol identifiers for IP, ARP, VLANs, IPv6, MPLS, PPPoE, LLDP, MACsec, FCoE, HSR, MCTP, DSA tags, and internal pseudo types, plus `ETH_P_802_3_MIN`. `struct ethhdr` contains destination/source MAC addresses and big-endian protocol field, guarded by `__UAPI_DEF_ETHHDR`.

## Control flow
Network drivers and packet sockets classify Ethernet frames by the protocol field when it is at least `ETH_P_802_3_MIN`, or by 802.3/LLC logic for length-coded frames. User space uses the constants for socket protocol selection and packet decoding.

## State and persistence behavior
The header defines packet-local frame layout and stable numeric protocol IDs. Interface MTU/MAC state is managed elsewhere.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with almost all Ethernet netdevices, AF_PACKET, bridge/VLAN/DSA/tunnel code, BPF programs, and packet analyzers.

## Risks and test signals
Risks include using host byte order for EtherTypes, frame-size off-by-FCS errors, non-official protocol collisions, DSA tag confusion, and libc header guard conflicts. Test signals include packet socket bind tests, Ethernet header parsing, VLAN/MPLS/IPv6 captures, MTU validation, BPF protocol matching, and compile tests with glibc/musl.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_ether.h -->

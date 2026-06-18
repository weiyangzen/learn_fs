<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/filter.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/filter.h

## Purpose
Defines the generic SFC hardware filter specification used by RX/TX filtering, RFS steering, default unicast/multicast filters, virtual ports, and tunnel encapsulation matching.

## Important APIs, types, and functions
- Enums: `efx_filter_match_flags`, `efx_filter_priority`, `efx_filter_flags`, and `efx_encap_type`.
- Main data type: `struct efx_filter_spec`, a compact match/action target structure carrying priority, flags, queue ID, RSS context, vport ID, VLANs, MACs, EtherType, IP protocol, hosts, ports, and encap type.
- Initializers: `efx_filter_init_rx` and `efx_filter_init_tx`.
- Match setters: IPv4/IPv6 local/full helpers, Ethernet local/default unicast/default multicast helpers, vport setter, and encap type getter/setter.

## Control flow
All code is inline initialization and field-setting. Callers zero the spec through the init helpers, then OR match flags and set associated fields through typed setters. Invalid Ethernet local filters with neither VID nor MAC return `-EINVAL`.

## State and persistence behavior
Filter specs are caller-owned transient values submitted to NIC-specific filter tables. The header stores no global state and performs no hardware I/O.

## Dependencies and integration points
Depends on Linux Ethernet, IPv6 address, byte-order types, and is consumed by driver filter implementations plus Falcon RFS code. Encapsulation values connect legacy filter handling with EF100 tunnel offload capability checks.

## Risks and test signals
Risks include unsupported match flag combinations per NIC type, bitfield size limits (`match_flags`, `flags`, `dmaq_id`, `encap_type`), and host/network byte-order mistakes. Test signals include filter insertion/removal tests for IPv4, IPv6, MAC/VLAN, default UC/MC, vport, encap filters, and RFS steering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/filter.h -->

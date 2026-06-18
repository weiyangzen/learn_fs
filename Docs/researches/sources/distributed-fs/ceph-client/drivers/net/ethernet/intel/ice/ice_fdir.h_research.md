# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fdir.h

## Purpose

`ice_fdir.h` defines the shared Flow Director data structures, packet offsets, descriptor context types, and function prototypes used by ICE Flow Director implementation files. It is the contract between ethtool Flow Director translation, raw packet/descriptor construction, and the rest of the ICE driver.

## Important APIs, Types, and Constants

Packet offset macros define where `ice_fdir.c` inserts match data into synthetic programming packets. They cover Ethernet ethertype/VLAN offsets, IPv4/IPv6 source and destination addresses, TCP/UDP/SCTP ports, IPv4 protocol/TOS/TTL, IPv6 next-header/traffic-class/hop-limit, GTP-U TEID/QFI, L2TPv3 session ID, ESP/AH SPI, and NAT-T ESP SPI. `ICE_FDIR_TUN_PKT_OFF` marks the inner packet offset for tunnel templates, and `ICE_FDIR_MAX_RAW_PKT_SIZE` bounds raw programming packet buffers.

`ICE_FDIR_MAX_FLTRS` defines a 16384 filter upper bound, while `ICE_FDIR_NO_QUEUE_IDX` represents no queue target. `ICE_FDIR_IPV4_PKT_FLAG_MF` is the IPv4 "more fragments" bit used for fragment template generation.

`enum ice_fltr_prgm_desc_dest` defines descriptor destination behavior: drop, direct to queue index, direct to queue group, or direct to other. `enum ice_fltr_prgm_desc_fd_status` defines whether the descriptor reports no status or FD ID status.

`struct ice_fd_fltr_desc_ctx` is an unpacked software representation of the hardware Flow Director programming descriptor fields. `ice_fdir_get_prgm_desc()` fills this and packs it into `struct ice_fltr_desc`.

`struct ice_rx_flow_userdef` holds parsed ethtool `FLOW_EXT` user-defined flex filter data: flex word, offset, and enabled flag. `struct ice_fdir_v4`, `struct ice_fdir_v6`, `struct ice_fdir_udp_gtp`, `struct ice_fdir_l2tpv3`, and `struct ice_fdir_extra` hold protocol-specific match data and masks. `struct ice_fdir_fltr` is the central software filter object: list node, flow type, Ethernet/IP/tunnel/extra data and masks, flex fields, queue/destination controls, counter data, filter ID, priority, and completion reporting.

`struct ice_fdir_base_pkt` maps a flow type to raw non-tunnel and tunnel packet templates. The prototypes export resource allocation, descriptor generation, packet generation, capacity, duplicate detection, fragment support, list lookup, counter updates, and list insertion.

## Control Flow and Integration

The header is included by `ice_ethtool_fdir.c` and used indirectly by `ice_fdir.c`. Ettool parsing fills `struct ice_fdir_fltr` and `struct ice_rx_flow_userdef`; low-level programming reads the same filter object to generate descriptors and packets. The fixed packet offset macros are the bridge between high-level protocol fields and byte-level packet templates.

Resource helpers (`ice_alloc_fd_res_cntr()`, `ice_free_fd_res_cntr()`, `ice_alloc_fd_guar_item()`, `ice_alloc_fd_shrd_item()`) integrate with ICE admin queue resource counters. Programming helpers (`ice_fdir_get_prgm_desc()`, `ice_fdir_get_gen_prgm_pkt()`) integrate with control VSI transmit programming. List helpers (`ice_fdir_find_fltr_by_idx()`, `ice_fdir_list_add_fltr()`, `ice_fdir_is_dup_fltr()`, `ice_fdir_update_cntrs()`) integrate with ethtool rule add/delete/list/replay behavior.

## State and Persistence Behavior

The header does not allocate state itself, but it defines the shape of persistent runtime Flow Director state. `struct ice_fdir_fltr` instances are stored in `hw->fdir_list_head`, survive across normal ethtool operations, and are used for reset replay. Counter fields and destination fields in the structure determine hardware programming, ethtool reporting, and per-flow accounting.

The packet offset constants are compile-time persistent assumptions. They must remain aligned with the packet byte templates in `ice_fdir.c`; otherwise the driver will persist and replay filters with wrong keys.

## Dependencies and Integration Points

This header depends on Linux networking types (`struct ethhdr`, `ETH_ALEN`, byte-order integer types, `struct list_head`) and ICE-internal enums/types such as `enum ice_fltr_ptype`, `struct ice_hw`, `struct ice_vsi`, and `struct ice_fltr_desc`. It is part of the ICE Flow Director API surface used by ethtool, reset replay, ADQ interaction, and hardware programming.

## Risks and Edge Cases

Adding new flow types requires coordinated updates in several places: packet offsets and data structures here, packet templates and insertion logic in `ice_fdir.c`, ethtool mask parsing and profile setup in `ice_ethtool_fdir.c`, duplicate comparison, and reporting back to ethtool. A mismatch in any layer can create filters that program successfully but do not match traffic.

Bitfield layout in `struct ice_fdir_udp_gtp` is compiler and endian sensitive if used directly as wire layout; current code mostly uses explicit fields such as TEID and QFI insertion. Descriptor context fields must match hardware descriptor masks and shifts used by `ice_fdir.c`.

## Test Signals

Build coverage should catch missing prototypes and type drift. Runtime tests should focus on every macro offset family: Ethernet/VLAN, IPv4/IPv6 L3 fields, L4 ports, GTP-U, L2TPv3, ESP/AH/NAT-T ESP, PFCP, flex-word insertion, drop/direct destination modes, queue-group fields, counter enablement, duplicate/list behavior, and reset replay of stored `struct ice_fdir_fltr` entries.

# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fdir.c

## Purpose

`ice_fdir.c` provides the low-level Flow Director data-plane construction helpers for the ICE driver. It defines static no-op/training packet templates for supported filter protocol types, builds Flow Director programming descriptors, allocates Flow Director hardware resources, generates raw packets from `struct ice_fdir_fltr` match data, maintains the sorted software filter list, updates Flow Director counters, and detects duplicate filters.

This file is lower level than `ice_ethtool_fdir.c`: it does not parse ethtool flow specs. Instead, it consumes already-normalized `struct ice_fdir_fltr` objects and turns them into descriptor plus packet data suitable for `ice_prgm_fdir_fltr()`.

## Important APIs, Types, and Functions

The large static packet-template section defines raw Ethernet/IP/L4/tunnel packet byte arrays for many ICE filter packet types: non-fragmented Ethernet, IPv4 TCP/UDP/SCTP/other, IPv6 TCP/UDP/SCTP/other, GTP-U inner IPv4 variants, L2TPv3, ESP, AH, NAT-T ESP, PFCP node/session, non-IP L2, and tunnel templates. `ice_fdir_pkt[]` maps each `enum ice_fltr_ptype` to its non-tunnel and tunnel template and length.

Descriptor programming starts with `ice_set_dflt_val_fd_desc()`, which fills default descriptor context values such as completion queue/reporting, Flow Director space, counter enablement, eviction, destination behavior, flex metadata, descriptor type, profile priority, swap behavior, and FDID metadata. `ice_set_fd_desc_val()` packs the context into `struct ice_fltr_desc` qwords with `FIELD_PREP()`. `ice_fdir_get_prgm_desc()` applies per-filter add/delete command, drop/direct destination, queue, VSI, counter, FDID, priority, and completion report before packing.

Resource helpers `ice_alloc_fd_res_cntr()`, `ice_free_fd_res_cntr()`, `ice_alloc_fd_guar_item()`, `ice_alloc_fd_shrd_item()`, and `ice_get_fdir_cnt_all()` wrap ICE admin queue resource allocation for Flow Director counters and guaranteed/shared filter entries.

Packet synthesis uses insertion helpers `ice_pkt_insert_ipv6_addr()`, `ice_pkt_insert_u6_qfi()`, `ice_pkt_insert_u8()`, `ice_pkt_insert_u8_tc()`, `ice_pkt_insert_u16()`, `ice_pkt_insert_u32()`, and `ice_pkt_insert_mac_addr()`. The main function `ice_fdir_get_gen_prgm_pkt()` selects the correct base template, optionally switches IPv4/IPv6 "other" flows to TCP/UDP/SCTP templates based on protocol, optionally fills tunnel destination port and inner packet offset, then writes filter fields into the packet. It reverses source and destination because user input is from RX perspective while hardware programming expects TX perspective.

List and duplicate helpers include `ice_fdir_find_fltr_by_idx()`, `ice_fdir_list_add_fltr()`, `ice_fdir_update_cntrs()`, `ice_fdir_has_frag()`, `ice_fdir_is_dup_fltr()`, and local comparison helpers. The list is ordered by `fltr_id`, which makes location lookup and ordered listing deterministic.

## Control Flow

The normal add/delete path is orchestrated by `ice_ethtool_fdir.c`, which calls `ice_fdir_get_prgm_desc()` and `ice_fdir_get_gen_prgm_pkt()` through `ice_fdir_write_fltr()`. Descriptor construction and packet construction are independent: the descriptor tells hardware what to do with a matched packet and the synthetic packet tells hardware what exact key to program.

`ice_fdir_get_gen_prgm_pkt()` first resolves the effective flow type. For `ICE_FLTR_PTYPE_NONF_IPV4_OTHER` or IPv6 other, it inspects `input->ip.v4.proto` or `input->ip.v6.proto` and may use TCP, UDP, or SCTP templates. It then finds the template in `ice_fdir_pkt[]`. For tunnel programming, it requires an open tunnel port, copies the tunnel template, writes the outer UDP destination tunnel port, and points `loc` to the inner packet offset. For non-tunnel programming, it copies the base template and points `loc` to the packet start.

The switch over flow type writes fields at fixed offsets defined in `ice_fdir.h`. IPv4/IPv6 address and port fields are reversed relative to RX input, ToS/TTL or TC/hop-limit are inserted where supported, destination MACs are inserted for several flows, GTP-U TEID and QFI fields are inserted, L2TPv3 session IDs and IPsec SPI fields are inserted, PFCP ports are inserted, and optional flex-word data is written at `input->flex_offset`. IPv4 "other" may generate an additional fragment packet through `ice_fdir_has_frag()`.

The software list path is simple but important. `ice_fdir_list_add_fltr()` inserts by ascending `fltr_id`; `ice_fdir_find_fltr_by_idx()` stops once it passes the requested ID; `ice_fdir_update_cntrs()` increments or decrements total and per-flow counters. `ice_fdir_is_dup_fltr()` walks same-flow entries and compares relevant key fields, with a special case allowing same filter ID with a different queue to be treated as an update rather than a duplicate.

## State and Persistence Behavior

This file manipulates in-memory driver state, not persistent storage. `hw->fdir_list_head` stores active software filter definitions. `hw->fdir_active_fltr` and `hw->fdir_fltr_cnt[]` track total and per-flow active filters. Hardware resource counters are allocated/freed through admin queue resource helpers. The packet template arrays are immutable static data.

The generated programming packets and descriptors are transient per hardware programming operation. The software list is the durable driver copy used for ethtool reporting and replay by higher layers after reset. Incorrect list or counter updates can therefore cause both observability and replay errors.

## Dependencies and Integration Points

The file includes `ice_common.h` and relies on definitions from `ice_fdir.h`, ICE admin queue resource APIs, ICE flow/filter descriptor field macros, ICE register/resource definitions, Linux Ethernet helpers, and net byte-order types. Its exported functions are consumed by `ice_ethtool_fdir.c` and other Flow Director setup/replay paths.

It integrates directly with hardware programming semantics: descriptor bit layout, packet offsets, fixed tunnel offset `ICE_FDIR_TUN_PKT_OFF`, open tunnel port discovery, and ICE flow packet type enums. Any change in hardware parser expectations must be reflected in both templates and offsets.

## Risks and Edge Cases

The largest risk is offset/template mismatch. The fixed offsets in `ice_fdir.h` must match the byte arrays in this file. A wrong packet length, protocol byte, or offset would silently program filters that do not match traffic. The source/destination reversal is required by hardware perspective and is easy to break when adding a new flow.

Tunnel programming depends on an open tunnel port and uses a fixed inner offset. Unsupported tunnel templates return errors or skip tunnel writes at higher layers. Fragment support is currently only reported for IPv4 other flows, so new fragmented flow support needs explicit updates.

Duplicate detection is incomplete for newer specialty flows such as GTP-U, L2TPv3, ESP/AH, NAT-T ESP, PFCP, and non-IP L2 unless their compared fields are added. This can allow semantically duplicate filters or reject too little, depending on higher-level constraints.

## Test Signals

Low-level validation should exercise add/delete for each packet template family, then verify hardware match behavior with real packets where possible. Useful tests include IPv4/IPv6 TCP/UDP/SCTP source/destination reversal, IPv4 other fragment programming, tunnel and non-tunnel programming, GTP-U TEID/QFI insertion, L2TPv3 session ID, IPsec SPI flows, PFCP node/session, non-IP L2 ethertype, flex-word offsets, sorted rule locations, duplicate detection, counter increments/decrements, and reset replay from the software list.

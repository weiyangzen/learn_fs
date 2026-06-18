# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_tc_lib.h

Purpose: declares the TC flower offload contract used by the ice driver. It defines the bit flags, parsed header containers, action representation, filter lifetime object, and exported helper prototypes consumed by the TC implementation and other driver modules.

Important APIs and types: `ICE_TC_FLWR_FIELD_*` flags describe every supported match dimension, including L2/L3/L4, tunnel key ID, encap addresses and ports, GTP/PFCP options, VLAN priority/TPID, PPPoE, and L2TPv3. `struct ice_tc_flower_action` stores either hardware traffic class or queue forwarding target plus `enum ice_sw_fwd_act_type`. `struct ice_tc_flower_lyr_2_4_hdrs` contains key and mask storage for MAC, VLAN, CVLAN, PPPoE, L2TPv3, IP, and ports. `struct ice_tc_flower_fltr` is the persistent filter node linked into the PF list. Exported functions include add/delete, replay, queue-to-VSI lookup, tunnel support checks, and LLDP pass/drop helpers.

Control flow role: this header does not implement the parser, but its fields determine how `ice_tc_lib.c` moves from flow dissector input to hardware lookup elements. `ice_is_chnl_fltr()` classifies ADQ channel filters after the implementation has resolved destination VSI or traffic class. `ice_is_forward_action()` centralizes the action categories that need destination validation.

State and persistence: `struct ice_tc_flower_fltr` is the main persistence unit. It stores netlink cookie, rule and recipe IDs returned by firmware, destination VSI handle and pointer, source VSI, direction, parsed outer/inner headers, tenant ID, GTP/PFCP metadata, tunnel type, flags, action, and extack pointer. The extack pointer is transient and is reset during replay.

Dependencies and integration: pulls in Linux bit helpers and PFCP metadata plus driver-specific `struct ice_vsi`, `struct ice_pf`, `struct ice_netdev_priv`, switch forwarding action enums, and ADQ constants from other ice headers. Kernel networking consumers reach these functions through TC setup hooks.

Risks: the field-bit namespace is nearly full at bit 30; adding fields requires compatible count/fill/parser changes in the C file. Header aliases for IPv4/IPv6 fields use macros inside `struct ice_tc_l3_hdr`, so careless names can obscure actual storage. `ice_is_chnl_fltr()` depends on `dest_vsi` being populated before it is called for queue actions.

Test signals: compile coverage should catch missing prototypes and struct drift, but behavioral tests need to verify that each flag has parser, lookup-count, and lookup-fill support. ADQ tests should confirm `ice_is_chnl_fltr()` for class and queue modes, and tunnel tests should validate PFCP/GTP metadata layout.

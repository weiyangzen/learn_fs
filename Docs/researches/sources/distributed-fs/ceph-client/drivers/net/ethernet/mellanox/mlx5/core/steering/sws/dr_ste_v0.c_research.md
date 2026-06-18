# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v0.c

## Purpose
`dr_ste_v0.c` implements the ConnectX-5 (`MLX5_STEERING_FORMAT_CONNECTX_5`) STE format. It provides the v0 `mlx5dr_ste_ctx` callbacks for STE initialization, hit/miss address encoding, match builder initialization/tag encoding, RX/TX action encoding, modify-header action encoding, and decap-L3 action-list generation.

## Important APIs, Types, And Functions
The public output is `mlx5dr_ste_get_ctx_v0()`, returning `ste_ctx_v0`. The file defines v0 entry types, tunnel/action encodings, lookup-type constants, modify-header hardware field mappings, and many builder callbacks. Core setters include `dr_ste_v0_set_miss_addr()`, `dr_ste_v0_get_miss_addr()`, `dr_ste_v0_set_hit_addr()`, `dr_ste_v0_set_next_lu_type()`, `dr_ste_v0_set_byte_mask()`, and `dr_ste_v0_init()`. Action encoders include `dr_ste_v0_set_actions_tx()`, `dr_ste_v0_set_actions_rx()`, `dr_ste_v0_set_action_set()`, `dr_ste_v0_set_action_add()`, `dr_ste_v0_set_action_copy()`, and `dr_ste_v0_set_action_decap_l3_list()`.

## Control Flow
Each match builder has an init function that encodes the matcher mask into `sb->bit_mask`, computes `sb->byte_mask`, sets a v0 lookup type, and installs a tag-build function. At rule insertion, the tag-build function encodes concrete values and clears consumed fields. Builders cover L2 source/destination, tunnel L2, IPv4 5-tuple and misc, IPv6 L3/L4, MPLS, GRE, MPLS-over-GRE/UDP via flex parsers, ICMP via parser IDs, metadata/registers, source GVMI/QPN, programmable flex parsers, Geneve/VXLAN-GPE/GTPU tunnel headers, GTPU flex parser fields, and tunnel header words 0/1.

Action flow differs for TX and RX. TX orders modify-header before encapsulation, handles push VLANs, emits extra STEs when modify/push/encap cannot share one STE, sets counters, and finally points to the final ICM address. RX handles counters, L3/L2 decap, pop VLAN, modify header, and flow tags, adding extra STEs when entry-type conflicts require it.

## State And Persistence
The static `ste_ctx_v0` vtable is the long-lived state. Runtime state is encoded into hardware STE byte arrays: entry type, lookup type, next lookup type, byte mask, hit/miss addresses, GVMI, counters, flow tags, tunnel actions, rewrite action indexes, reformat IDs, and flex parser values. Modify-field metadata maps software action fields to v0 hardware modify fields with bit ranges and optional L3/L4 type constraints.

## Dependencies And Integration Points
The file depends on `dr_ste.h`, Linux types/CRC headers, mlx5 IFC layouts, domain capabilities for parser IDs and `prio_tag_required`, and generic action attributes built outside this file. It is selected by `mlx5dr_ste_get_ctx()` for ConnectX-5 and is called by matcher/rule/action code only through the context interface.

## Risks
This file is dense with hardware layout assumptions. Lookup-type selection must match RX/TX/inner direction; flex parser IDs must map to FLEX_PARSER_0 or FLEX_PARSER_1 correctly; source GVMI/QPN lookup depends on vport capabilities and peer domains; and action splitting must respect v0 entry-type limitations. Many builders consume fields by clearing them, so missing a clear yields false unsupported-field errors, while clearing too much hides invalid input.

## Test Signals
Test signals include v0 matcher creation for each builder family, concrete rule tags for IPv4/IPv6/L2/tunnel/register/flex-parser cases, source-port matching across local and peer domains, TX action combinations of modify/push/encap/counter, RX combinations of decap/pop/modify/tag/counter, decap-L3 with and without VLAN, and parser-ID boundary cases around `DR_STE_MAX_FLEX_0_ID`. Hardware integration should verify packets hit expected rules on ConnectX-5 format devices.

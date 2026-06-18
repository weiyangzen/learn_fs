# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v1.c

## Purpose
This file implements the software-steering STE context for steering format v1. It converts high-level direct-rule match/action objects into 64-byte hardware STE records, action words, lookup type identifiers, byte masks, and modify-header pattern/argument objects. The file ends by publishing `ste_ctx_v1`, a `struct mlx5dr_ste_ctx` function table consumed by the generic STE/rule/action code.

## Important APIs, Types, And Functions
The exported entry point is `mlx5dr_ste_get_ctx_v1()`, which returns `ste_ctx_v1`. That context wires v1 implementations into generic operations for STE initialization, miss/hit address programming, byte-mask handling, RX/TX action assembly, action encoding, modify-header chunk allocation, and pre-send formatting.

Core STE field helpers include `dr_ste_v1_init()`, `dr_ste_v1_set_miss_addr()`, `dr_ste_v1_get_miss_addr()`, `dr_ste_v1_set_hit_addr()`, `dr_ste_v1_set_next_lu_type()`, `dr_ste_v1_get_next_lu_type()`, `dr_ste_v1_set_byte_mask()`, and `dr_ste_v1_prepare_for_postsend()`. Address helpers encode ICM addresses as shifted indices; hit addresses use `icm_addr >> 5` plus hash table size, while miss addresses use `miss_addr >> 6`.

Action encoders include VLAN push/pop, encapsulation, L3 encapsulation, RX decapsulation, insert/remove header, flow tag, counter, ASO flow meter, modify-list, accelerated modify-list, set/add/copy modify actions, and special L3 decap action-list construction. `dr_ste_v1_set_actions_tx()` and `dr_ste_v1_set_actions_rx()` are the control points that lay out action words across one or more STEs.

Match builders are numerous and follow the same pattern: build a bit mask from a mask `mlx5dr_match_param`, select the v1 lookup type, compute the byte mask with `mlx5dr_ste_conv_bit_to_byte_mask()`, and install a tag-building callback. Builders cover L2 source/destination, IPv4/IPv6 5-tuple pieces, tunnel L2, GRE, MPLS, MPLS-over-UDP/GRE flex parsers, ICMP, metadata registers, source GVMI/QPN, Geneve, VXLAN-GPE, GTP-U, programmable flex parsers, and tunnel header words.

## Control Flow
For normal rule construction, generic code selects builder functions through `ste_ctx_v1`, calls each builder init with a mask, and later calls the stored `ste_build_tag_func()` with a rule value. Many tag builders intentionally zero fields they consume from the input `mlx5dr_match_param`; this is a consumed-field accounting convention used elsewhere to detect unsupported or unconsumed match bits.

TX action assembly starts with a double-action capacity in the original STE. It may append additional MATCH STEs with `dr_ste_v1_arr_init_next_match()` when a requested action does not fit or when capability/order rules require separation. TX ordering is pop VLAN, modify header, push VLAN, encap/insert/remove, ASO flow meter, range, counter. RX ordering handles decap first, then tag, pop VLAN, modify header, push VLAN, counter, encap/insert/remove, ASO, and range. The final STE gets the hit GVMI and final hit ICM address.

Range matching is special: `DR_ACTION_TYP_RANGE` always appends a `DR_STE_V1_TYPE_MATCH_RANGES` STE, programs the range miss address, and encodes packet length min/max using the range definer. Range STEs do not carry normal actions.

## State And Persistence
The file does not persist Linux state directly; it mutates caller-owned byte buffers that are later posted to ICM hardware memory. It also allocates and releases modify-header pattern and argument objects through domain managers in `dr_ste_v1_alloc_modify_hdr_ptrn_arg()` and `dr_ste_v1_free_modify_hdr_ptrn_arg()`. Runtime persistence is therefore in device ICM, modify action objects, cached pattern objects, and argument objects referenced by `struct mlx5dr_action_rewrite`.

## Dependencies And Integration Points
The code depends on `mlx5_ifc_dr_ste_v1.h` hardware layout definitions, `dr_ste_v1.h` constants, generic `dr_types.h` structures, `MLX5_SET`/`MLX5_GET` accessors, `mlx5dr_ste_conv_bit_to_byte_mask()`, `mlx5dr_domain_get_vport_cap()`, flex-parser capability fields, and pattern/argument managers. It integrates with `dr_ste.c` through the `mlx5dr_ste_ctx` dispatch table and with action creation through modify-field conversion arrays.

## Risks
Risks are mostly hardware ABI risks: a wrong field code, shift, lookup type, or byte mask can silently steer traffic incorrectly. RX/TX action ordering is fragile because some actions must be split across STEs. `prepare_for_postsend()` swaps tag and mask for full STEs; the range STE workaround deliberately writes min/max in locations that survive that generic swapping path. Builders mutate match parameters, so callers must pass scratch copies, not shared immutable masks. Source GVMI/QPN matching depends on peer-domain xarray state and vport capability lookup, returning `-EINVAL` when unavailable.

## Test Signals
Useful tests include compile coverage for all `MLX5_SET` fields, rule creation with combinations of VLAN pop/push, modify header, decap/encap, counters, ASO meters, and range matching, plus traffic tests for inner/outer IPv4/IPv6, tunnel protocols, metadata registers, and peer vport source matching. Negative tests should verify invalid IP version, invalid peer GVMI, unavailable vport caps, undersized L3 decap action buffers, and missing pattern/argument managers.

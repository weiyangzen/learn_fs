# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v3.c

## Purpose
This file defines the steering format v3 context. It reuses v1 builders and most generic action assembly, uses v2 modify-header field codes, and overrides packet-reformat/VLAN action encoders whose bit layouts changed in v3.

## Important APIs, Types, And Functions
The exported entry point is `mlx5dr_ste_get_ctx_v3()`. V3-specific setters include `dr_ste_v3_set_encap()`, `dr_ste_v3_set_push_vlan()`, `dr_ste_v3_set_pop_vlan()`, `dr_ste_v3_set_encap_l3()`, `dr_ste_v3_set_rx_decap()`, `dr_ste_v3_set_insert_hdr()`, `dr_ste_v3_set_remove_hdr()`, and `dr_ste_v3_set_action_decap_l3_list()`.

## Control Flow
Generic code selects `ste_ctx_v3` by steering format version. Match building still calls v1 builder functions. RX/TX action assembly still calls the v1 packers, but those packers dispatch through the context for encap, VLAN, decap, insert, and remove actions, so the v3 bitfield setters are used at the actual action-write points.

## State And Persistence
The file only owns a static function table and writes caller-provided action buffers. Persistent effects occur when the generic send path posts those buffers to hardware ICM/action memory.

## Dependencies And Integration Points
It includes `dr_ste_v1.h` for shared action IDs, anchors, sizes, builders, and v1 helpers, and `dr_ste_v2.h` for modify-field mappings. It depends on v3 layout structures defined in `mlx5_ifc_dr.h` for action bitfields.

## Risks
The v3 context is a hybrid: v1 matching plus v3 action layouts plus v2 modify fields. A reviewer must verify all three ABI families when changing it. The L3 decap inline-list algorithm mirrors v1 but uses v3 structures; any future change to padding or inline data width must update both. As with v2, `DR_STE_CTX_ACTION_CAP_POP_MDFY` is not advertised.

## Test Signals
Traffic tests should emphasize packet reformat operations on v3 hardware: L2-to-tunnel, L3 tunnel, insert/remove header, VLAN push/pop, and decap-L3 action-list creation. Modify-header tests should match v2 expectations.

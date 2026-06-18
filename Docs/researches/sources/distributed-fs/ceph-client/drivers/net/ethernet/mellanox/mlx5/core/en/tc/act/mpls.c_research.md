# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/mpls.c

Purpose: Parses MPLS push/pop TC actions for FDB offload, mainly with BareUDP and L3-to-L2 decap flows.

Important APIs: `mlx5e_tc_act_mpls_push` validates `reformat_l2_to_l3_tunnel` support and MPLS unicast protocol, then records MPLS fields in parse state. `mlx5e_tc_act_mpls_pop` validates action position and BareUDP filter device, then sets packet reformat and `L3_TO_L2_DECAP`.

Control flow and state: Push only stores transient `parse_state->mpls_push` and `mpls_info`; `mirred` later consumes it. Pop mutates `attr->esw_attr->eth.h_proto`, action flags, and flow flags.

Dependencies and integration: Depends on BareUDP device recognition, eswitch firmware caps, `tc_priv` flow flags, and later VLAN/mirred parsing for Ethernet push requirements.

Risks and tests: MPLS support is action-order constrained. Tests should cover push with non-MPLS_UC, missing firmware cap, pop not first or not after decap, non-BareUDP filter device, pop plus VLAN eth push, and mirred after MPLS push.

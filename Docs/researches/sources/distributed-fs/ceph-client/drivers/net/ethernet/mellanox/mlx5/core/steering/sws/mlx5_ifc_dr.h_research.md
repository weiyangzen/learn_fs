# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/mlx5_ifc_dr.h

## Purpose
This header declares hardware interface bit layouts for direct-rule STE tags, legacy STE formats, modify-header actions, ASO flow-meter actions, and v3 packet-reformat action layouts. These structures are used by `MLX5_SET`, `MLX5_GET`, and `MLX5_ADDR_OF` macros, not as normal C data structures.

## Important APIs, Types, And Functions
It defines `MLX5DR_STE_LU_TYPE_DONT_CARE` and many `mlx5_ifc_ste_*_bits` structures for general STE control, SX transmit, RX steering multicast, packet modify STEs, L2/L3/L4 tags, IPv6 addresses, tunnel tags, MPLS, metadata registers, GRE, flex parsers, tunnel headers, general purpose lookup, source GVMI/QP, L2 headers, set/copy modify actions, ASO flow meters, and v3 insert/remove action formats.

## Control Flow
There is no executable flow. The field names are referenced by STE builders and action setters. For example, v1 builders set tag fields such as `ste_eth_l2_tnl_v1`, while v3 action setters use `ste_double_action_insert_with_ptr_v3` and related structures from this header.

## State And Persistence
No runtime state is stored. The definitions describe byte/bit positions in hardware command or STE buffers that are later posted to device memory.

## Dependencies And Integration Points
This header is included through `dr_types.h` and directly/indirectly by STE code. It must stay synchronized with firmware PRM definitions and with the action/match builders in `dr_ste_v*.c`.

## Risks
Field names and widths are hardware ABI. A single width or ordering mistake changes how `MLX5_SET` packs bytes and can cause traffic missteering. Some structures are older direct-rule layouts while v1-specific layouts live in `mlx5_ifc_dr_ste_v1.h`, so callers must use the correct family.

## Test Signals
Compile tests catch missing field names; only hardware/traffic tests catch most semantic layout mistakes. Exercise L2/L3/L4, tunnel, flex parser, ASO, and v3 reformat actions on devices that support the corresponding steering formats.

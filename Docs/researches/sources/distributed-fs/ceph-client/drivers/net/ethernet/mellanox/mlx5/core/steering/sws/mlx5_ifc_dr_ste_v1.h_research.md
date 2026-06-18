# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/mlx5_ifc_dr_ste_v1.h

## Purpose
This header declares steering format v1 hardware bit layouts for single/double actions, v1 STE control formats, match range STEs, and v1 tag layouts. It is the direct layout companion for `dr_ste_v1.c`.

## Important APIs, Types, And Functions
Important definitions include `MLX5_MODIFY_HEADER_V1_QW_OFFSET`, v1 action layouts for flow tag, modify list, remove header, remove-by-size, copy, set, add, insert inline, insert pointer, accelerated modify action list, and v1 STE layouts `ste_match_bwc_v1`, `ste_mask_and_match_v1`, and `ste_match_ranges_v1`.

Tag layouts cover v1 L2 source/destination/source-destination, IPv4 5-tuple, L2 tunnel, IPv4 misc, L4, L4 misc, MPLS, GRE, source GVMI/QP, and ICMP fields.

## Control Flow
There is no executable flow. `dr_ste_v1.c` uses these names in `MLX5_SET`, `MLX5_GET`, and `MLX5_ADDR_OF` calls to encode match tags, masks, actions, hit/miss addresses, range min/max values, and reparse/counter state.

## State And Persistence
No state is stored in the header. It defines the binary contract for the hardware buffers that become persistent in ICM when posted.

## Dependencies And Integration Points
It is included by `dr_ste_v1.c`. V2 reuses v1 functions for many operations, so these v1 layouts also indirectly affect v2 for the shared action/match parts that did not change.

## Risks
The v1 action layouts have small fields and non-byte-aligned anchors/offsets. Mistakes in reserved-field placement or field width break all generated hardware STEs. `MLX5_MODIFY_HEADER_V1_QW_OFFSET` is applied by modify-action setters; changing it would shift all modify-header fields.

## Test Signals
Run traffic tests for all v1 match builders and action encoders, plus modify-header set/add/copy and match-range packet length. Compile tests should include v1, v2, and v3 users because v2/v3 reuse v1 functions.

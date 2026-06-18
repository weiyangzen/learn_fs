# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v1.h

## Purpose
This header defines the public v1 STE constants and function prototypes used by v1, v2, and v3 STE contexts. It names v1 entry formats, lookup types, header anchors, action sizes, action IDs, modify-header hardware field codes, and ASO context types.

## Important APIs, Types, And Functions
Important constants include `DR_STE_DECAP_L3_ACTION_NUM`, `DR_STE_L2_HDR_MAX_SZ`, `DR_STE_CALC_DFNR_TYPE()`, `DR_STE_V1_TYPE_*`, `DR_STE_V1_LU_TYPE_*`, `DR_STE_HEADER_ANCHOR_*`, `DR_STE_ACTION_*_SZ`, `DR_STE_V1_ACTION_ID_*`, and v1 modify field offsets. Function prototypes expose all v1 STE utilities, action encoders, match-builder init routines, and modify-header pattern/argument allocation helpers.

## Control Flow
The header itself has no runtime flow, but it defines the dispatch surface for `ste_ctx_v1` and reused v1 behavior in v2/v3. The lookup type constants are combined by `DR_STE_CALC_DFNR_TYPE()` to choose inner or outer definer types during builder initialization.

## State And Persistence
No state is stored here. The values are part of the driver/hardware ABI and must remain synchronized with the STE layout headers and firmware-supported steering format.

## Dependencies And Integration Points
It includes `dr_types.h` and `dr_ste.h`, so all prototypes are expressed in generic direct-rule types such as `mlx5dr_ste_ctx`, `mlx5dr_domain`, `mlx5dr_ste_build`, `mlx5dr_match_param`, and `mlx5dr_action`. It is included by `dr_ste_v1.c`, `dr_ste_v2.c`, and `dr_ste_v3.c`.

## Risks
Changing numeric constants breaks hardware encoding. The header is reused by newer contexts, so v1-looking constants such as action IDs and anchors are not v1-only in practice. Prototype changes can cascade through v2/v3 because they intentionally call v1 implementations.

## Test Signals
Build tests should compile all STE versions. Runtime tests should cover every action ID and lookup type that has a public builder or encoder, especially fields reused by v2/v3.

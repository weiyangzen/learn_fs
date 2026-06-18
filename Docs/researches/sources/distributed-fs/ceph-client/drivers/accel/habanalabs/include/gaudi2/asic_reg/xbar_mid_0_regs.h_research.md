# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/xbar_mid_0_regs.h

## Purpose
`xbar_mid_0_regs.h` defines the generated register address map for Gaudi2 XBAR mid instance 0. It has the same functional register families as the edge XBAR block but at the mid-instance base address.

## Important APIs, Types, And Functions
The exported macros include LBW/DBG base and mask windows for HIF, HMMU, EDMA, HBM, and XBAR peers; internal routing registers; EMEM bit-location controls; HIF response channel placement; HBW arbitration weight; MMU page-cache index mapping and low-latency arbiter controls; HBM response overrides; read/write rate limiter banks; end-to-end credit registers; and upscale/down-conversion LFSR controls.

## Control Flow
The header contains no logic. Initialization and security paths program routing windows and conversion settings, while performance/debug paths inspect or adjust arbitration, rate limiting, and credit state.

## State, Persistence, And Dependencies
State is persistent XBAR hardware configuration. The register map depends on the broader fabric topology and on correct alignment with edge XBAR instances and duplicated XBAR blocks counted in `gaudi2.h`.

## Integration Points
Gaudi2 security code references `mmXBAR_MID_0_*` ranges. The map integrates with MMU/HIF/HBM routing, fabric protection, bandwidth management, and low-level debug.

## Risks
The mid and edge maps are structurally similar, so instance mixups are a realistic risk. Wrong base/mask or conversion settings can break routing across a central fabric segment and affect multiple engines. Rate-limit changes can create global performance artifacts.

## Test Signals
Test signals include register readback for mid instance 0, successful memory traffic through expected routes, security allow/deny behavior, bandwidth under load, no XBAR ECC/fatal async events, and comparison with edge-instance programming where symmetry is expected.

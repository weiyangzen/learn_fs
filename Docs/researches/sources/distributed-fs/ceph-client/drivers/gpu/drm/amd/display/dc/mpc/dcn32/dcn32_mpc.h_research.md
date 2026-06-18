# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.h

## Purpose
This header declares the DCN3.2 MPC register list and helper prototypes. It extends DCN3 with per-MPCC movable color-management registers for shaper LUT, 3D LUT, post-1D LUT, and their memory power controls.

## Important APIs, types, and functions
`MPC_REG_LIST_DCN3_2` adds `MPCC_MOVABLE_CM_LOCATION_CONTROL`, `MPCC_MCM_SHAPER_*`, `MPCC_MCM_3DLUT_*`, `MPCC_MCM_1DLUT_*`, and `MPCC_MCM_MEM_PWR_CTRL` registers. `MPC_COMMON_MASK_SH_LIST_DCN32` maps fields for blend, denorm, OGAM, MCM shaper, MCM 3D LUT, MCM 1D LUT, and memory power state. `struct dcn32_mpc_registers` reuses `MPC_REG_VARIABLE_LIST_DCN3_0` and `MPC_REG_VARIABLE_LIST_DCN32`. Prototypes expose DCN3.2 construction, init, shaper, 3D LUT, post-1D LUT, memory power, configuration, and low-level LUT RAM writers.

## Control flow and state
The header does not implement behavior, but it defines the state topology used by `dcn32_mpc.c`: each MPCC owns its MCM shaper, 3D LUT, and 1D LUT state. This contrasts with DCN3 RMU mux state and simplifies per-plane color programming at the cost of a much larger per-MPCC register surface.

## Dependencies and integration points
It includes both DCN20 and DCN30 MPC headers and is consumed by DCN32 implementation plus later DCN401 code that reuses DCN32 MCM programming helpers. The exposed functions are also referenced through `struct mpc_funcs` callbacks for generic display color management.

## State and persistence behavior
All register lists describe volatile hardware state. Bank selection, mode current, LUT indices, LUT data, and memory power fields are held in hardware. The software side is inherited from `struct dcn30_mpc`; no durable persistence exists.

## Risks
This header is highly sensitive to register macro coverage. Missing one channel-specific field can break only one color component, making failures visually subtle. Several helpers are declared for reuse by later files, so signature changes have broad impact. The DCN32 register structure type is effectively a DCN30-compatible layout with extra variables, which requires careful casting and constructor use.

## Test signals
Compile and link tests should cover all declared helpers. Runtime signals include valid register table generation for every MCM block, successful banked post-1D/shaper/3D LUT programming, memory power state transitions, and absence of RMU dependencies in DCN3.2 color-management paths.

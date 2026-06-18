# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h

## Purpose
This header declares the DCN3 MPC register schema and public interface. It builds on DCN2, adds DWB mux registers, RMU global and per-RMU registers, shaper LUT registers, 3D LUT registers, gamut remap controls, output rate/flow-control fields, and DCN3.2-compatible movable color-management register variables.

## Important APIs, types, and functions
`struct dcn30_mpc` embeds `struct mpc` and carries MPCC/RMU counts plus register, shift, and mask tables. `MAX_RMU` is defined as 3. `MPC_REG_LIST_DCN3_0`, `MPC_RMU_REG_LIST_DCN3AG`, `MPC_REG_VARIABLE_LIST_DCN3_0`, `MPC_REG_VARIABLE_LIST_DCN32`, `MPC_COMMON_MASK_SH_LIST_DCN3_0`, and variant lists for DCN30/DCN303 generate ASIC register bindings. Declared APIs include construction, MPC init, shaper and 3D LUT programming, RMU mux acquisition/status, denorm, output CSC, output gamma, gamut remap set/get, DWB mux, rate control, OGAM power, and register-state readback.

## Control flow and state
The header defines the shape consumed by `dcn30_mpc.c`; actual control flow is table-driven through `struct mpc_funcs`. The register lists describe three major state domains: MPCC plane composition, OPP output formatting, and color-management LUT/matrix hardware. RMU state is separate from MPCC state and is multiplexed to an MPCC through `MPC_RMU_CONTROL`.

## Dependencies and integration points
It includes `dcn20/dcn20_mpc.h` and depends on AMD register-generation macros and common display color types. Later DCN32, DCN401, and DCN42 code reuse the DCN30 structure layout and many function prototypes, so this header is a compatibility hinge between shared DCN3 behavior and later per-MPCC MCM implementations.

## State and persistence behavior
State is either software bookkeeping in `struct dcn30_mpc` or volatile hardware register contents. The large register variable and mask lists are compile-time descriptions, not runtime storage for values. No file or firmware persistence is provided by this layer.

## Risks
The header has multiple similar mask-list variants for DCN3.0 and DCN3.03, with some fields intentionally commented out in one variant; picking the wrong list can expose unavailable status fields. `SRII_MPC_RMU` is conditionally redefined, so macro conflicts can break register addresses. The register variable list includes DCN32 additions, making structure consumers sensitive to assumed layout. RMU count and `MAX_RMU` must match the actual ASIC tables.

## Test signals
Compile-time signals are successful register table construction for each ASIC include path. Runtime signals include correct function-table hookup, valid DWB and RMU mux fields, gamut remap mode current reads, memory power status fields, and successful color-management operations on both DCN3.0 and DCN3.03 variants.

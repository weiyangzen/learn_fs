# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn401/dcn401_mpc.h

## Purpose
This header defines the DCN4.01 MPC register schema and public API. It extends DCN30/DCN32 register coverage with two MCM gamut-remap blocks, fast-load controls for MCM 3D LUT, and DCN4.01-specific shift/mask/register structures.

## Important APIs, types, and functions
`MPC_REG_VARIABLE_LIST_DCN4_01` combines DCN3.0 and DCN3.2 variables with first and second MCM gamut-remap coefficient registers and 3D LUT fast-load select/status registers. `MPC_COMMON_MASK_SH_LIST_DCN4_01` maps fields for MCM gamut-remap modes/current modes, coefficient components, and fast-load done and underflow flags. `struct dcn401_mpc_registers`, `struct dcn401_mpc_shift`, `struct dcn401_mpc_mask`, and `struct dcn401_mpc` define the concrete DCN4.01 object. Public prototypes cover construction, movable CM location, LUT population, LUT mode/read-write controls, gamut remap set/get/read/program, and fast-load status/select.

## Control flow and state
The header declares a more command-oriented interface than DCN32: callers can separately populate a LUT bank, configure read/write control, program active mode, and query mode. It also exposes block-specific gamut remap operations so color-management code can target OGAM, first MCM, or second MCM remap stages.

## Dependencies and integration points
It includes `dcn30/dcn30_mpc.h` and `dcn32/dcn32_mpc.h`, making DCN4.01 a layered extension rather than a separate MPC implementation. It depends on shared enums such as `MCM_LUT_ID`, `dc_cm_lut_size`, `mpcc_gamut_remap_id`, and `mpcc_movable_cm_location`, plus generic `struct mpc`.

## State and persistence behavior
State is volatile register state for coefficient sets, modes, fast-load status, LUT banks, and MPCC bookkeeping. The structure mirrors earlier MPC state with `mpcc_in_use_mask`, `num_mpcc`, `num_rmu`, and register metadata pointers.

## Risks
The register list adds many paired A/B coefficient registers; mapping only C11/C12 and C33/C34 into helper structs may hide assumptions about helper support for full 3x4 matrices. Duplicate prototype declaration for `mpc401_update_3dlut_fast_load_select` is harmless but noisy. Type compatibility with DCN32 helper functions depends on shared leading structure layout and matching register variable lists.

## Test signals
Compile-time tests should validate register table generation for all new fields. Runtime signals include mode/current readback for both MCM gamut-remap blocks, fast-load status flag reads, LUT bank population and activation, and construction of a `dcn401_mpc` with correct callback coverage.

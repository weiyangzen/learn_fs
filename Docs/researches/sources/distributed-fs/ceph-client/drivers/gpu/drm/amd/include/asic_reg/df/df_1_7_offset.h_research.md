# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_1_7_offset.h

## Purpose
`df_1_7_offset.h` maps AMD Data Fabric 1.7 register names to SOC15 MMIO offsets and base-index selectors. It gives the v1.7 DF driver stable symbolic names for fabric access control, medium-grain clock gating, DRAM base decoding, and coherent slave mode control.

## Important APIs, Types, And Functions
The public surface is a set of macros: `mmFabricConfigAccessControl`, `mmDF_PIE_AON0_DfGlobalClkGater`, `mmDF_CS_AON0_DramBaseAddress0`, and `mmDF_CS_AON0_CoherentSlaveModeCtrlA0`, each paired with a `_BASE_IDX` macro. There are no functions or types.

## Control Flow
The header has no direct control flow. It supplies the register identifiers used by `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_FIELD15` in `df_v1_7.c`: broadcast-mode toggling reads/writes `FabricConfigAccessControl`, clock-gating updates read/modify/write `DfGlobalClkGater`, channel discovery reads `DramBaseAddress0`, and ECC RMW forcing writes a field in `CoherentSlaveModeCtrlA0`.

## State, Persistence, And Dependencies
The macros are compile-time constants. Hardware state lives in the registers they address and persists until changed by the driver, firmware, reset, or power transitions. These offsets depend on the SOC15 DF register accessor convention and on the matching shift/mask header for field extraction and modification.

## Integration Points
`df_v1_7.c` is the direct consumer. The exported `amdgpu_df_funcs` methods use these addresses for DF broadcast mode, HBM channel discovery, DF medium-grain clock gating, clock-gating state reporting, and ECC force-parallel-write read-modify-write behavior.

## Risks
Incorrect offsets or base indices can redirect writes to unrelated DF registers, with high impact because these paths affect global fabric access, memory interleaving interpretation, clock gating, and ECC behavior. Generated headers also expose no type safety, so cross-generation macro mixups may compile.

## Test Signals
Signals include successful compilation of `df_v1_7.c`, correct HBM channel counts from known `DramBaseAddress0` encodings, clock-gating enable/disable register traces, and ECC feature tests that verify `ForceParWrRMW` changes only the intended bit.

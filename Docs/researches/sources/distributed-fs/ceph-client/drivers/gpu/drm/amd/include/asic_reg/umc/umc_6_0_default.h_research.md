# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_0_default.h

## Purpose
This generated header records reset/default values for a small UMC 6.0 register subset: ECC control, UMC configuration, and local capability. It is reference metadata for code or diagnostics comparing runtime UMC state with expected defaults.

## Important APIs, Types, and Functions
The exported macros are `mmUMCCH0_0_EccCtrl_DEFAULT` set to `0x00000000`, `mmUMCCH0_0_UMC_CONFIG_DEFAULT` set to `0x00000203`, and `mmUMCCH0_0_UmcLocalCap_DEFAULT` set to `0x00000000`. There are no functions or types.

## Control Flow
There is no control flow. The defaults are passive constants. In this source snapshot, direct references to these exact default macros are not present in nearby AMDGPU code, but the companion UMC 6.0 mask header is included by `gmc_v9_0.c`, and generated default headers are commonly used for register bring-up, reset comparison, or debug table generation.

## State and Persistence Behavior
The header stores no state. It documents reset-like expected values for hardware state. Runtime UMC registers can diverge from these defaults after firmware memory training, ECC enablement, memory initialization, or driver RAS setup.

## Dependencies and Integration Points
It pairs with `umc_6_0_offset.h` and `umc_6_0_sh_mask.h`. Any consumer comparing register values would also need SOC15 address mapping and register read helpers. The constants map only channel 0 names; per-channel equivalence is inferred through companion offset patterns.

## Risks
Treating defaults as runtime invariants is risky because firmware and driver initialization legitimately change UMC state. `UMC_CONFIG_DEFAULT` includes nonzero bits, so code that assumes zeroed UMC configuration would be wrong. Defaults should not be used to overwrite live registers unless the hardware reset sequence explicitly requires it.

## Test Signals
Compile tests are enough for macro syntax. Runtime validation would compare early boot register dumps against these defaults only at a known reset point, then verify later ECC and DRAM-ready state through the companion mask macros after firmware and driver initialization.

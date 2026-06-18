# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/cz_ppsmc.h

## Purpose
`cz_ppsmc.h` defines Carrizo/Stoney-era PowerPlay SMC protocol constants: fan-control modes, DPM array IDs, return codes, message IDs, and feature masks. It provides the numeric firmware command ABI for older ASIC/APU SMU communication.

## Important APIs, Types, and Functions
The header defines `PPSMC_Result_*` return values and `PPSMC_isERROR()`, a large set of `PPSMC_MSG_*` command IDs for feature enablement, clock limits, power gating, DRAM/logging setup, display/watermark control, and legacy jobs, plus feature masks such as `NB_DPM_MASK`, `VDDGFX_MASK`, `VCE_DPM_MASK`, `ACP_DPM_MASK`, `UVD_DPM_MASK`, and `SCLK_DPM_MASK`. It also defines fan-control and DPM-array enums.

## Control Flow
There is no executable flow. Other source files use these constants when composing commands for the SMC messaging layer.

## State and Persistence
No state is declared. The constants describe firmware-visible state transitions and commands.

## Dependencies and Integration Points
The file uses packed layout guards for firmware/shared-code compatibility and is part of the PowerPlay include set used by ASIC-specific SMU managers. Although the researched Vega20 hwmgr uses `vega20_ppsmc.h`, this header is relevant to the same generic SMC message infrastructure for older hardware paths.

## Risks
Numeric message IDs are firmware ABI. Renumbering or reusing IDs incorrectly would send wrong commands. Some names overlap with other ASIC-specific `*_ppsmc.h` headers, so include ordering and ASIC-specific compilation boundaries matter.

## Test Signals
Build coverage in Carrizo/Stoney PM code and runtime SMC command success on those ASICs are the practical tests. Failures would appear as unknown command, failed SMC result, or broken DPM/power-gating behavior.

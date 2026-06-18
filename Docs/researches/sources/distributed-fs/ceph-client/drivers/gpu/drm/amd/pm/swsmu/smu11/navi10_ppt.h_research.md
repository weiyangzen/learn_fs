# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.h Research

## Purpose
`navi10_ppt.h` is the small public header for the Navi10/Navi12/Navi14 SMU11 PowerPlay table implementation. It publishes ASIC-specific UMD pstate clock constants, the voltage scaling factor used by Navi10 OverDrive voltage curves, and the `navi10_set_ppt_funcs()` registration entry point.

## Important APIs, Types, And Functions
The header defines peak GFX clock constants for Navi10 XTX/XT/XL, Navi14 XT/XTM/XLM/XTX/XL, and Navi12. It also defines profiling pstate clocks for Navi10 and Navi14 across GFXCLK, SOCCLK, MEMCLK, VCLK, and DCLK. `NAVI10_VOLTAGE_SCALE` is used by `navi10_ppt.c` when converting between firmware OD curve voltage units and millivolts. The only function declaration is `extern void navi10_set_ppt_funcs(struct smu_context *smu);`.

## Control Flow
There is no executable control flow in the header. Its constants are consumed when `navi10_populate_umd_state_clk()` derives standard and peak UMD pstates, and the exported function is called by higher-level SMU ASIC-selection code to install Navi10 PPT behavior into `struct smu_context`.

## State, Persistence, And Dependencies
The header stores no state. Its values become part of runtime pstate and OD behavior through the C implementation. It depends on the caller including or forward-declaring `struct smu_context` in the include chain; the header itself only carries include guards and macro definitions.

## Integration Points
`navi10_ppt.c` includes this header for pstate and voltage constants. Platform dispatch code includes or references the header to call `navi10_set_ppt_funcs()` for MP1 IP versions handled by the Navi10 PPT module.

## Risks
The constants are board/ASIC policy values rather than values queried at runtime. If a future SKU uses a different UMD profiling or peak clock policy but reuses this path, user-visible pstate reporting can be misleading. The voltage scale must continue to match the firmware OD table encoding; a mismatch would display or program VDDC curve values incorrectly.

## Test Signals
Validation is mostly indirect: confirm `pp_dpm_*` and UMD pstate reporting on Navi10, Navi12, and Navi14 SKUs; verify OD VDDC curve display and writes round-trip in millivolts; and check that the ASIC dispatch path calls `navi10_set_ppt_funcs()` only for compatible SMU11 IP versions.

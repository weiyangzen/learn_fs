# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.h

## Purpose

`vangogh_ppt.h` is the public header for the Vangogh SMU11.5 PPT policy implementation. It exposes the policy installation function and Vangogh-specific UMD P-state frequency constants used by `vangogh_ppt.c`.

## Important APIs, Types, and Macros

The only function declaration is `void vangogh_set_ppt_funcs(struct smu_context *smu);`.

Macros define standard, peak, minimum-SCLK, and minimum-MCLK UMD P-state frequencies for GFXCLK, SOCCLK, FCLK, VCLK, and DCLK. It also defines RLC power status message parameters `RLC_STATUS_OFF` and `RLC_STATUS_NORMAL`.

## Control Flow

The header has no executable control flow. Consumers include it to call `vangogh_set_ppt_funcs` during ASIC selection and to use the P-state constants while programming performance profiles.

## State and Persistence Behavior

The header stores no state. Its constants influence persistent firmware state indirectly when `vangogh_ppt.c` sends SMU messages using the defined frequencies or RLC status values.

## Dependencies

The header assumes `struct smu_context` is declared by the including translation unit. It has only an include guard and C preprocessor constants.

## Integration Points

`vangogh_ppt.c` includes this header and uses the UMD P-state macros for performance profile mode, clock level emission, and peak/standard/min profile programming. AMDGPU SMU ASIC setup code can include the header to call `vangogh_set_ppt_funcs`.

## Risks and Edge Cases

These constants encode platform policy. Wrong frequencies can overconstrain clocks, reduce performance, or send unsupported requests to firmware. The min-SCLK and min-MCLK profiles deliberately constrain different clock domains, so swapping constants would change user-visible `power_dpm_force_performance_level` behavior.

## Test Signals

Build coverage catches declaration and macro name drift. Runtime DPM sysfs profile tests should confirm standard, peak, min-SCLK, and min-MCLK modes apply the frequencies expected for Vangogh.

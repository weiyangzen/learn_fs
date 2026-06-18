# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu12/renoir_ppt.h

## Purpose

`renoir_ppt.h` is the public header for the Renoir SMU12 PPT policy implementation. It exposes the callback installation function and the fixed Renoir UMD P-state constants used by performance-profile handling.

## Important APIs, Types, and Macros

The header declares `void renoir_set_ppt_funcs(struct smu_context *smu);`.

It defines `RENOIR_UMD_PSTATE_GFXCLK`, `RENOIR_UMD_PSTATE_SOCCLK`, `RENOIR_UMD_PSTATE_FCLK`, and packed `RENOIR_UMD_PSTATE_VCNCLK`.

## Control Flow

There is no executable control flow. `renoir_ppt.c` includes this header to publish its install function and to program standard profile clocks.

## State and Persistence Behavior

The header has no storage. Its constants affect firmware state indirectly when Renoir profile callbacks send SMU clock-limit messages.

## Dependencies

The declaration assumes `struct smu_context` is visible at include sites. The file otherwise depends only on the C preprocessor and its include guard.

## Integration Points

AMDGPU SMU ASIC setup calls `renoir_set_ppt_funcs` for Renoir-class devices. `renoir_ppt.c` uses the macros in DPM profile and clock emission code.

## Risks and Edge Cases

The packed VCN clock value carries both VCLK and DCLK policy in a single firmware parameter; wrong packing would affect video clock constraints. Updating Renoir performance policy requires keeping these constants consistent with PMFW expectations.

## Test Signals

Build coverage catches declaration drift. Runtime profile tests should confirm Renoir standard profile applies the expected GFX, SOC, FCLK, and VCN frequencies.

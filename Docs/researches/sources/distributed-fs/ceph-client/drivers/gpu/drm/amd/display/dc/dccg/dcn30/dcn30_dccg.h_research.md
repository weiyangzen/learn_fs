# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn30/dcn30_dccg.h

## Purpose
`dcn30_dccg.h` extends the DCN2 DCCG register and mask/shift lists for DCN3.0 and declares DCN3 create functions.

## Important APIs, Types, And Macros
`DCCG_REG_LIST_DCN30` extends `DCCG_REG_LIST_DCN2` with `HDMICHARCLK0_CLOCK_CNTL`, extra OTG pixel rate entries, and PHY A/B/C symbol clock control registers. `DCCG_MASK_SH_LIST_DCN3` extends DCN2 field mapping with HDMI character clock enable/source and PHY symbol force enable/source fields.

The header declares `dccg3_create` and `dccg30_create`.

## Control Flow And State
The macros are used by resource files to instantiate concrete register tables. There is no direct flow in the header.

## Dependencies And Integration Points
It includes `dcn20/dcn20_dccg.h`, sharing the object layout and base function declarations. It integrates with DCN3 resource initialization and hardware clock programming.

## Risks
The register list duplicates OTG entries already in `DCCG_REG_LIST_DCN2`, so correctness depends on macro expansion matching the intended generated table. Missing PHY D/E fields here reflects DCN3.0 hardware limits and must align with ASIC register headers.

## Test Signals
Compile-time macro expansion for DCN30 resources and runtime HDMI/DP clock programming on DCN3.0 are key.

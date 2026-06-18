# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn303/dcn303_dccg.h

## Purpose
`dcn303_dccg.h` defines a compact DCN 3.0.3 DCCG register and mask/shift list for a smaller pipe configuration.

## Important APIs And Macros
`DCCG_REG_LIST_DCN3_03` includes DPP DTO control/params for DPP0-1, refclk, dispclk frequency change control, and OTG pixel rate control for OTG0-1. `DCCG_MASK_SH_LIST_DCN3_03` maps DPP0-1 DTO enable/DB fields, DTO phase/modulo, refclk fields, dispclk change/error fields, and OTG0-1 add/drop pixel fields.

## Control Flow And State
There is no runtime logic in this header. It supplies concrete register-table macros consumed by DCN303 resource construction with a shared DCCG implementation.

## Dependencies And Integration Points
It includes `dcn30/dcn30_dccg.h`, sharing DCN3/DCN2 infrastructure. It integrates with DCN303 resource initialization and DCCG hardware sequencing.

## Risks
The table only covers two DPP/OTG instances. Any caller using indices above one with this table would access uninitialized register slots. The header has an SPDX line plus the standard MIT text; licensing is consistent but duplicated style differs from neighboring files.

## Test Signals
Compile coverage for DCN303 resources, two-pipe DPP DTO programming, OTG add/drop on OTG0-1, and no out-of-range DCCG calls on DCN303 are key.

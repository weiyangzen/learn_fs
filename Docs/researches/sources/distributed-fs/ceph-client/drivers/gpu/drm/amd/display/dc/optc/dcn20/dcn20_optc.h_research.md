# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn20/dcn20_optc.h

## Purpose
`dcn20_optc.h` defines the DCN2.0 OPTC register additions and function prototypes. It extends DCN10 with global control, GSL windows, vupdate keepout, DSC start, CRC mode, ODM data format/width/memory, DWB source, manual flow control, DRR status, and pipe update status.

## Important APIs, types, and functions
Important macros are `TG_COMMON_REG_LIST_DCN2_0()` and `TG_COMMON_MASK_SH_LIST_DCN2_0()`. Prototypes expose DCN20 initialization, CRTC enable, GSL programming, DSC configuration/status, ODM bypass/combine/source readback, triplebuffer and doublebuffer locks, manual trigger setup/programming, CRC configuration, and last-used DRR vtotal readback.

## Control flow
The header has no executable control flow. It describes the extra register fields needed by `dcn20_optc.c` and later users.

## State and persistence behavior
The register and bitfield tables are runtime metadata. Hardware state is volatile OTG/OPTC state.

## Dependencies and integration points
It includes `dcn10/dcn10_optc.h` and integrates with DCN20 timing-generator construction, ODM, DSC, DWB, GSL, DRR, and CRC flows.

## Risks and edge cases
The header must stay synchronized with generated register names. DWB source fields include both DWB0 and DWB1; incorrect field mapping misroutes writeback. The mask list adds pipe-update and vupdate-keepout fields used for locking, so omissions can lead to unsafe update timing.

## Test signals
Compile coverage, register-table instantiation, ODM/DSC/GSL/DWB mode tests, and lock/update-pending tests validate this header.

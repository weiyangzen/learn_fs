# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn401/dcn401_optc.h

## Purpose
Defines the DCN401 OPTC field list and declares the generation-specific functions implemented in `dcn401_optc.c`. It captures the expanded DCN4 register surface used for ODM 3:1, FAMS/FAMS2 DRR, P-state keepout, and update-lock handling.

## Important APIs, Types, and Macros
`OPTC_COMMON_MASK_SH_LIST_DCN401(mask_sh)` maps standard OTG timing/update-lock/status fields plus `OPTC_DOUBLE_BUFFER_PENDING`, ODM segment 0-3 selection, `OPTC_WIDTH_CONTROL2.OPTC_SEGMENT_WIDTH_LAST`, `OTG_H_TIMING_DIV_MODE_MANUAL`, `OTG_PSTATE_REGISTER` fields, pipe-update status, and interrupt destination. Prototypes cover init, DRR/min-max/manual-trigger, global sync, CRTC/phantom enable/disable, ODM bypass/combine, out mux, update-lock wait, and vupdate keepout.

## Control Flow and State
No runtime flow is present. The macro controls register-table state for DCN401 and determines which fields shared helpers can access. The function prototypes allow DCN42 and resource modules to reuse DCN401 logic without duplicating declarations.

## Dependencies and Integration Points
Includes `dcn10/dcn10_optc.h`. DCN401 resources instantiate these tables; DCN42 includes and calls this API for most base behavior. The fields must match the generated ASIC headers consumed by `reg_helper`.

## Risks and Test Signals
Risks are missing or incorrect masks for new DCN4 functionality, especially `OPTC_SEGMENT_WIDTH_LAST`, P-state fields, and update-lock status. Build coverage and DCN401/DCN42 hardware mode-set tests are the best signals.

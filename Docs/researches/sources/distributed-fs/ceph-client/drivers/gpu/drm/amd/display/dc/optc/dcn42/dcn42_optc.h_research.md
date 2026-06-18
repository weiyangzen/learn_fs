# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn42/dcn42_optc.h

## Purpose
Defines the DCN42 OPTC field list and public function declarations for DCN42 timing-generator behavior. It combines DCN4 timing/ODM/P-state concepts with DCN42-only RSMU underflow, split CRC result registers, PWA frame-sync fields, and FGC clock-gating control.

## Important APIs, Types, and Macros
`OPTC_COMMON_MASK_SH_LIST_DCN42(mask_sh)` enumerates standard OTG timing, update lock, VTG, GSL, ODM, DSC, DRR, P-state, pipe update, and interrupt fields. DCN42 additions include `OPTC_RSMU_UNDERFLOW_*`, split CRC0/CRC1 R/G/B registers, `OTG_DRR_TIMING_DBUF_UPDATE_PENDING`, PWA frame-sync fields, and `OPTC_FGCG_REP_DIS`. Prototypes expose init, PWA, TG init, underflow, disable, and lock-doublebuffer helpers.

## Control Flow and State
The header is declarative. It defines the field state that DCN42 implementation can read/write and that reused DCN35/DCN401 helpers expect to find in the `struct optc` masks.

## Dependencies and Integration Points
Includes `dcn10/dcn10_optc.h`. Resource construction uses this macro to build the generation-specific register table, while the implementation includes DCN35/DCN401 headers for behavior reuse.

## Risks and Test Signals
Risk areas are incorrect RSMU or PWA field mappings and CRC engine field mismatches. Build tests catch missing symbols; hardware tests should verify PWA frame sync, underflow reporting, CRC readback, double-buffer pending, and inherited ODM/DRR behavior.

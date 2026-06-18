# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn30/dcn30_optc.h

## Purpose
`dcn30_optc.h` defines DCN3.0 OPTC register lists, mask/shift fields, and prototypes. It refactors DCN3 base register metadata around new global-control lock fields, extended blank color, DTO, DRR trigger/change registers, four-segment ODM selection, and update-pending status fields.

## Important APIs, types, and functions
Important macros include `OPTC_COMMON_REG_LIST_DCN3_BASE()`, `OPTC_COMMON_REG_LIST_DCN3_0()`, `OPTC_COMMON_MASK_SH_LIST_DCN3_BASE()`, `OPTC_COMMON_MASK_SH_LIST_DCN3_0()`, and `OPTC_COMMON_MASK_SH_LIST_DCN30()`. Prototypes expose DCN30 initialization, output mux, locks, DRR trigger/change controls, triplebuffer lock, blank color, DSC config, ODM bypass/combine, DRR pending wait, TG init, vtotal min/max, and update-pending queries.

## Control flow
The header has no runtime flow. It gives `dcn30_optc.c` register coverage for the DCN3 lock model, ODM segment routing, and DRR/pipe-update status.

## State and persistence behavior
It defines volatile register metadata only. Runtime state is in `struct optc` and hardware registers.

## Dependencies and integration points
It includes `dcn20/dcn20_optc.h` and integrates with DCN30 timing-generator resource construction, ODM, DSC, DRR, lock, CRC, GSL, and pending-status paths.

## Risks and edge cases
The header declares `optc3_set_timing_db_mode()` but this file set does not provide a matching non-static implementation in `dcn30_optc.c`, so users must avoid relying on that symbol unless implemented elsewhere. DCN3.0 has both `OTG_H_TIMING_DIV_BY2` and `OTG_H_TIMING_DIV_MODE` variants in mask macros, requiring correct generation selection.

## Test signals
Compile/link coverage, register-table initialization, ODM four-segment programming, lock-window programming, DRR trigger/change, pending-status reads, and DSC/CRC mode tests validate this header.

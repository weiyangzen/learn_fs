# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn35/dcn35_dwb.c

## Purpose

`dcn35_dwb.c` adapts the DCN30 Display Writeback Controller for DCN3.5. It delegates construction to the DCN30 constructor with extended shift/mask structs and adds fine-grain clock-gating control.

## Important APIs, Types, And Functions

The exported functions are `dcn35_dwbc_construct` and `dcn35_dwbc_set_fgcg`. The file defines DCN35-specific `FN` access casting but otherwise reuses the DCN30 DWB implementation.

## Control Flow

Construction calls `dcn30_dwbc_construct`, casting DCN35 shift/mask tables to DCN30-compatible base types. FGCg control updates `DWB_FGCG_REP_DIS` to the inverse of the requested enable flag.

## State, Dependencies, Risks, And Test Signals

No private software state is added. Runtime effects are inherited DWB object initialization and the DWB enable-clock-control register field for FGCg. It depends on `reg_helper` and `dcn35_dwb.h`. Risks include layout assumptions in casted shift/mask structs and FGCg toggling interfering with enable state. Build and runtime tests should verify inherited DCN30 operations plus FGCg enable/disable.

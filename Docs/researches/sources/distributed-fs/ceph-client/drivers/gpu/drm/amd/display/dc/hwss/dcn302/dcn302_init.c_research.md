# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn302/dcn302_init.c

## Purpose
Constructs DCN302 HWSS behavior by calling the DCN30 constructor and then overriding private power-gating hooks for DPP, HUBP, and DSC.

## Important APIs, Types, and Functions
Exports `dcn302_hw_sequencer_construct(struct dc *dc)`. It calls `dcn30_hw_sequencer_construct(dc)` then assigns `dc->hwseq->funcs.dpp_pg_control`, `hubp_pg_control`, and `dsc_pg_control`.

## Control Flow
Linear inheritance-and-patch pattern. The DCN30 public/private tables are installed first; only three private functions are changed.

## State and Persistence Behavior
Persists inherited DCN30 table state with DCN302 PG overrides in `dc->hwseq->funcs`.

## Dependencies and Integration Points
Includes `dcn302_hwseq.h`, `dcn30_init.h`, and `dc.h`. Integrated by ASIC resource construction for DCN302.

## Risks and Test Signals
Risk is forgetting to call the base constructor or overriding the wrong function fields. Test boot and power-gating behavior to confirm DCN302 register mappings are used while all DCN30 behavior remains intact.

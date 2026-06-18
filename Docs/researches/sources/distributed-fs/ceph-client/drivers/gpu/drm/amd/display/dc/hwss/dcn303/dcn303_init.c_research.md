# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn303/dcn303_init.c

## Purpose
Constructs DCN303 HWSS behavior by inheriting DCN30 tables and overriding all plane-related PG hooks with DCN303 no-op implementations.

## Important APIs, Types, and Functions
Exports `dcn303_hw_sequencer_construct(struct dc *dc)`. It calls `dcn30_hw_sequencer_construct(dc)` and then patches `dpp_pg_control`, `hubp_pg_control`, `dsc_pg_control`, and `enable_power_gating_plane`.

## Control Flow
Linear base-constructor call followed by hook replacement.

## State and Persistence Behavior
Persists DCN30 behavior plus DCN303 no-op PG overrides in the DC function tables.

## Dependencies and Integration Points
Includes `dcn303_hwseq.h`, `dcn30_init.h`, and `dc.h`. Selected by DCN303 resource construction.

## Risks and Test Signals
Risk is accidental inherited register access if any PG hook is missed. Test boot, suspend/resume, plane disable, and DSC paths on DCN303 to ensure no PG register programming occurs.

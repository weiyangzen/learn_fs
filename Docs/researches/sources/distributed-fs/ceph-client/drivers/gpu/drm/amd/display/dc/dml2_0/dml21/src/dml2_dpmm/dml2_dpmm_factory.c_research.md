# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_dpmm/dml2_dpmm_factory.c

## Purpose
Builds a `dml2_dpmm_instance` by project id and wires mode-to-DPM and watermark callbacks for the power-management mapping layer.

## Important APIs, types, and functions
- `dml2_dpmm_create()` is the exported factory.
- Dummy callbacks return true without mutating inputs and are used for stage1 and for projects where watermark mapping is intentionally inactive.
- DCN40 and DCN4 stage2 use `dpmm_dcn3_map_mode_to_soc_dpm()` plus dummy watermarks.
- DCN4 stage2 auto-DRR/SVP uses `dpmm_dcn4_map_mode_to_soc_dpm()` and `dpmm_dcn4_map_watermarks()`.
- DCN42 uses `dpmm_dcn4_map_mode_to_soc_dpm()` and `dpmm_dcn42_map_watermarks()`.

## Control flow and integration
The function validates `out`, clears it, switches on project id, assigns callbacks, and returns success. Top-level DML creation later invokes these callbacks through `dml2_dpmm_instance`.

## State and persistence behavior
Only the callback table inside caller-provided `out` persists. The factory does not store project id in the instance in this implementation.

## Dependencies
Includes the factory header, DCN4 DPMM declarations, and external library dependencies for `memset`.

## Risks and edge cases
Stage1 succeeds with dummy callbacks, unlike the core factory where stage1 fails. DCN40/stage2 mode mapping uses the DCN3 policy path but has no real watermark mapping. Callers must tolerate dummy watermarks for those projects or explicitly skip watermark programming.

## Test signals
Factory tests should assert callback identity for each project id, null-output failure, invalid-id failure, and that dummy callbacks return true. Integration tests should confirm projects expecting real watermark programming receive non-dummy callbacks.

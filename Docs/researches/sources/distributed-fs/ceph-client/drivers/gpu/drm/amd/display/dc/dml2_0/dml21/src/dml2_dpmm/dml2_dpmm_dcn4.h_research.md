# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_dpmm/dml2_dpmm_dcn4.h

## Purpose
Declares the DCN3/DCN4/DCN42 DPMM mapping functions used by the DPMM factory and top-level display programming.

## Important APIs, types, and functions
- `dpmm_dcn3_map_mode_to_soc_dpm()`
- `dpmm_dcn4_map_mode_to_soc_dpm()`
- `dpmm_dcn4_map_watermarks()`
- `dpmm_dcn42_map_watermarks()`
All functions operate on in/out parameter bundles from `dml2_internal_shared_types.h`.

## Control flow and integration
The factory assigns these functions into `dml2_dpmm_instance` callbacks by project id. Mode-to-DPM mapping is called after core mode-support/programming has produced bandwidth, clock, and latency data; watermark mapping is called when programming global DCHUB registers.

## State and persistence behavior
The functions declared here mutate caller-owned programming structures and do not own storage.

## Dependencies
Includes `dml2_internal_shared_types.h` for `dml2_dpmm_map_mode_to_soc_dpm_params_in_out` and `dml2_dpmm_map_watermarks_params_in_out`.

## Risks and edge cases
DCN3 and DCN4 function names coexist in a DCN4 header because DCN40/stage2 projects reuse the DCN3 policy path while later projects use DCN4 policy. Callers should not infer ASIC generation solely from the header name.

## Test signals
Factory wiring tests should verify the intended function is selected for each project id, and DPMM integration tests should confirm both DPM and watermark callbacks are non-null for supported projects.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_utils.c

## Purpose
`dml21_utils.c` contains DML2.1 wrapper utilities that resolve DML-to-DC mappings, program DC pipe contexts from DML outputs, create SubVP phantom streams/planes, accumulate MALL allocation sizes, detect DP2.0, and build FAMS2 firmware programming payloads.

## Important APIs, types, and functions
Lookup helpers include `dml21_helper_find_dml_pipe_idx_by_stream_id()`, `dml21_find_dml_pipe_idx_by_plane_id()`, `dml21_get_plane_id()`, `dml21_get_dc_plane_idx_from_plane_id()`, `find_valid_pipe_idx_for_stream_index()`, and `find_pipe_regs_idx()`. Programming helpers include `dml21_find_dc_pipes_for_plane()`, `dml21_pipe_populate_global_sync()`, `dml21_populate_mall_allocation_size()`, `dml21_program_dc_pipe()`, `dml21_handle_phantom_streams_planes()`, `dml21_build_fams2_programming()`, and `dml21_is_plane1_enabled()`.

## Control flow
Pipe resolution uses DML mapping tables to find the DC stream, plane index, real DPP pipes, and optional paired phantom pipes. Pipe programming copies global sync, selects pipe-register slice by ODM/MPC indices, copies normal or phantom HUBP register sets, updates unbounded request and DET sizes, records max DPP clock, accumulates MALL usage, and sets DC p-state type. Phantom handling creates paired streams and planes for DML-programmed SubVP, then remaps DC pipes. FAMS2 building resets firmware payloads, skips blank/phantom streams, copies DML static state, fills DC pipe masks and OTG IDs, and adds SubVP phantom mask details.

## State and persistence behavior
The file mutates only in-memory `dc_state` and `pipe_ctx` state: global sync, hubp registers, mcache/MALL accounting, FAMS2 payloads, pipe masks, and p-state type. Phantom streams/planes are created through callback-owned DC state mechanisms and removed by wrapper validation before subsequent runs.

## Dependencies and integration points
It depends on DML2 internal types, DML core DCN4 calculations, translation helpers, DC resource management, and callback tables in `dml2_context->config`. It integrates directly with `dml21_wrapper_fpu.c` after DML mode programming succeeds.

## Risks and edge cases
Several functions assume mapping tables and `plane_descriptor` pointers are valid. `find_valid_pipe_idx_for_stream_index()` dereferences `plane_descriptor` without checking null. Phantom plane creation duplicates many main-plane fields but adjusts only clip height. FAMS2 bit masks assume pipe indices fit in the mask width. `is_sub_vp_enabled()` scans all pipes and relies on paired-stream callbacks. Plane1 enablement uses a broad enum range that includes more than classic 420 formats.

## Test signals
Validation should cover multi-DPP/ODM/MPC pipe-register indexing, blank streams, SubVP phantom creation/removal/remapping, real and phantom MALL accounting, DP2.0 encoder detection with missing HPO link encoders, FAMS2 vblank/vactive/DRR/SubVP payloads, pipe mask correctness, p-state type assignment, and null/invalid mapping resilience.

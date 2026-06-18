# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn3.c

## Purpose
Implements the DCN3-style PMO optimizer used by DCN40/DCN4 stage2 projects in this tree. It adjusts display configurations for DCC/MCACHE admissibility, dynamic ODM voltage-minimum optimization, and UCLK p-state support through reserved vblank time and min-clock latency index search.

## Important APIs, types, and functions
- `pmo_dcn3_initialize()` stores SoC/IP/options pointers, combine limits, and MCG table size in the PMO instance.
- `pmo_dcn3_optimize_dcc_mcache()` increases MPC combine or ODM combine factors when planes fail DCC/MCACHE support and free pipes are available.
- `pmo_dcn3_init_for_vmin()`, `pmo_dcn3_test_for_vmin()`, and `pmo_dcn3_optimize_for_vmin()` implement dynamic ODM optimization to reduce DISPCLK below vmin limits.
- `pmo_dcn3_init_for_pstate_support()`, `pmo_dcn3_test_for_pstate_support()`, and `pmo_dcn3_optimize_for_pstate_support()` build and iterate reserved-vblank-time/min-latency candidates for p-state support.
- Helpers include sorting/deduplicating candidate times, getting/setting reserved vblank time per stream, increasing MPC/ODM combine factors, testing horizontal timing divisibility, DP encoder eligibility, synchronizability, and highest ODM load selection.

## Control flow and integration
Initialization is first. DCC/MCACHE optimization copies the display config when needed, counts used/free pipes, then either applies no-ODM MPC expansion or single-stream ODM expansion depending on stream/ODM state. Vmin init marks unoptimizable streams based on disable options, existing MPC combine, SVP, horizontal divisibility, and non-DP encoders; optimization then chooses the stream with highest pixel-clock-per-ODM load and tries the next legal ODM combine mode. P-state init builds per-stream candidate reserved times from existing reservations and optional FCLK/UCLK/stutter requirements, then optimization iterates latency index upward first and falls back to lower reserved-time candidate combinations.

## State and persistence behavior
Persistent PMO state lives in `dml2_pmo_instance`: SoC/IP/options pointers, combine limits, MCG table size, and `scratch.pmo_dcn3` search state (`min_latency_index`, `max_latency_index`, `cur_latency_index`, stream mask, reserved-time candidates/counts, current candidate indices). Optimizers mutate copied `display_configuation_with_meta` or `dml2_display_cfg` outputs, especially stage3/stage4 metadata, `reserved_vblank_time_ns`, `odm_mode`, and `mpcc_combine_factor`.

## Dependencies
Includes PMO factory and DCN3 PMO header. Uses internal shared structures for display configs, stage3/stage4 metadata, SoC power-management blackout times, mode-support result, cfg support info, stream/plane descriptors, PMO options, and IP pipe counts.

## Risks and edge cases
The code assumes fixed stream/plane masks fit in small integer masks (`0xF`). `optimize_dcc_mcache()` has single-stream ODM logic that indexes `stream_descriptors[i]` while iterating planes, which is only safe when plane and stream indices align in the intended single-stream case. Dynamic ODM legality depends on horizontal timing divisibility and DSC slice divisibility; missing a case can cause unsupported transitions. Candidate iteration spelling aside, the search order can reduce reserved time only after exhausting latency indices. Stage3 `performed` is set during p-state init, so downstream code sees optimization as active even before a successful final candidate.

## Test signals
Tests should cover no free pipes, MPC combine limit, ODM combine limit, multi-stream no-ODM optimization, single-stream ODM expansion, vmin disabled options, non-DP encoder rejection, horizontal divisibility by 2/4, DSC slice divisibility by 3/4, vmin DISPCLK threshold, p-state candidate sorting/deduplication, latency-index iteration, and reserved-vblank propagation to all planes on a stream.

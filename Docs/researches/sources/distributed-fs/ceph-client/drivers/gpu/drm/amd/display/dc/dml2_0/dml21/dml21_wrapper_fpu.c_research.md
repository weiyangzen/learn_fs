# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_wrapper_fpu.c

## Purpose
`dml21_wrapper_fpu.c` implements the FPU-protected DML2.1 initialization, validation, mode-programming, DC hardware-state mapping, clock/watermark/register copy-out, FAMS2 generation, and mcache programming preparation.

## Important APIs, types, and functions
Public APIs are `dml21_init()`, `dml21_reinit()`, `dml21_validate()`, and `dml21_prepare_mcache_programming()`. Internal helpers include `dml21_populate_configuration_options()`, `dml21_check_mode_support()`, `dml21_mode_check_and_programming()`, `dml21_calculate_rq_and_dlg_params()`, and `dml21_prepare_mcache_params()`.

## Control flow
Initialization copies configuration, applies debug-forced p-state options, populates DML init parameters, and initializes the DML2 instance. Non-programming validation scrubs prior phantom streams/planes, maps DC state into DML display config, and calls `dml2_check_mode_supported()`. Programming validation clears state, handles empty stream lists with minimum clocks and FAMS2 reset, removes phantoms, maps display config, calls `dml2_build_mode_programming()`, maps DC pipes, creates SubVP phantoms, optionally allocates mcache, copies per-pipe DCHUB/HUBP registers, clocks, watermarks, and FAMS2 payloads. Mcache preparation builds per-plane/per-pipe descriptors, calls `dml2_build_mcache_programming()`, then copies generated mcache registers into main and phantom pipes.

## State and persistence behavior
The file mutates `dml2_context->v21` scratch, display config, mode support, mode programming, and `dc_state->bw_ctx` plus pipe fields. Phantom streams/planes are transient runtime DC state. No persistent storage is used.

## Dependencies and integration points
It depends on DML top-level APIs, DML2 DC resource management, translation helpers, utility helpers, resource-pool callbacks, SVP/FAMS callbacks, and DC bandwidth context structures. It is the main integration point called by DC validation paths.

## Risks and edge cases
The programming path is sensitive to stale phantom state, so callback ordering matters. `dml21_calculate_rq_and_dlg_params()` appears to index max supported dispclk/dppclk with `num_clk_values`, which is one past the last valid element if the count is a conventional length. Empty-stream handling skips full DML mode programming but still seeds clocks and FAMS2 state. Mcache phantom indexing must stay aligned with DML's main-plane count. Skipping hardware-state mapping suppresses pipe/register copy-out.

## Test signals
Critical signals include validate-only and validate-and-programming modes, empty state, allocation of SubVP phantoms, mcache allocation/programming with and without phantom planes, skip-hw-state-mapping behavior, clock/watermark copy correctness, max clock table bounds, FAMS2 required and legacy-pstate paths, and repeated validation after phantom cleanup.

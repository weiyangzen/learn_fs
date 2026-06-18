# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce100/dce100_hwseq.c

Purpose: implements DCE 10.0 hardware sequencer specialization. It customizes display power gating, bandwidth preparation/optimization, construction, and DCC/tiling reset behavior on top of DCE 11.0 shared sequencing.

Important APIs and functions: `dce100_enable_display_power_gating()` maps generic pipe gating control to BIOS command table actions, calls `dc_bios->enable_disp_power_gating()`, and resets `MASTER_UPDATE_MODE` to 0 because BIOS sets it to 2. `dce100_prepare_bandwidth()` and `dce100_optimize_bandwidth()` set safe display marks then update clocks with optimize false or true. `dce100_hw_sequencer_construct()` starts from `dce110_hw_sequencer_construct()` and overrides function pointers. `dce100_reset_surface_dcc_and_tiling()` clears mem-input tiling when requested and forces an immediate surface flip/address program.

Control flow: power gating skips BIOS calls for `PIPE_GATING_CONTROL_INIT` on nonzero controllers, otherwise calls BIOS with controller id plus one and the mapped action. Bandwidth functions delegate to DCE110 watermark logic then clock manager. Reset surface flow exits if no mem input, optionally clears tiling through `mem_input_clear_tiling`, then calls `mem_input_program_surface_flip_and_addr()` with immediate flip.

State and persistence: persists BIOS-programmed pipe power state, CRTC `MASTER_UPDATE_MODE`, display watermark/clock state through delegated helpers, mem-input tiling state, and surface address latches. It mutates `dc->hwseq->funcs` and `dc->hwss` function tables during construction.

Dependencies and integration points: includes Display Core services/types, clock manager, resource definitions, `dce100_hwseq.h`, DCE110 HWSS, and DCE10 register headers. It integrates with BIOS command tables, clock manager, mem-input/HUBP-style plane resources, and the DCE110 base sequencer.

Risks and test signals: BIOS command table side effects require the explicit `MASTER_UPDATE_MODE` repair; removing it can break update sequencing. Immediate flips after clearing tiling are necessary to avoid stale framebuffer interpretation but can be visible if called at the wrong time. Signals include DCE10 modeset, suspend/resume and power-gating tests, bandwidth/clock transition validation, tiling clear with immediate flip, and BIOS table failure-path coverage.

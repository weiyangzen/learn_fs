# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce100/dce100_hwseq.h

Purpose: declares the public DCE 10.0 hardware sequencer entry points used by resource construction and HWSS function tables.

Important APIs: declares `dce100_hw_sequencer_construct()`, `dce100_prepare_bandwidth()`, `dce100_optimize_bandwidth()`, `dce100_enable_display_power_gating()`, and `dce100_reset_surface_dcc_and_tiling()`. It forward declares `struct dc` and `struct dc_state` and includes `core_types.h` plus `hw_sequencer_private.h` for `pipe_ctx`, `dc_plane_state`, and pipe gating types.

Control flow: declaration-only. The implementation in `dce100_hwseq.c` installs these functions into `dc->hwseq->funcs` and `dc->hwss` after constructing the DCE110 base sequencer.

State and persistence: no local state. Declared functions mutate hardware power gating, clocks/watermarks, mem-input tiling, and surface address state when called.

Dependencies and integration points: used by DCE10 resource construction and by code that needs DCE100-specific HWSS overrides. It sits between shared DCE110 behavior, BIOS command tables, clock manager, and plane mem-input resources.

Risks and test signals: prototype drift breaks function table assignment or hides ABI changes in common HWSS code. Because the declared functions touch power and immediate flips, validation should include DCE10 build coverage, power-gating paths, bandwidth transitions, and clear-DCC/tiling behavior.

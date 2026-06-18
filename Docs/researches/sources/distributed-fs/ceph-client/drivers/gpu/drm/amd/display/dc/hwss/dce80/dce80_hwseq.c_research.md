# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce80/dce80_hwseq.c

Purpose: DCE8 hardware sequencer shim. It reuses the DCE110 base sequencer but overrides a small set of hooks to match DCE8/DCE100-era power gating, bandwidth, pipe locking, and surface DCC/tiling behavior.

Important APIs, types, and functions: exported `dce80_hw_sequencer_construct()` is the only implementation function. It calls `dce110_hw_sequencer_construct()` and then assigns `dce100_enable_display_power_gating`, `dce_pipe_control_lock`, `dce100_prepare_bandwidth`, `dce100_optimize_bandwidth`, and `dce100_reset_surface_dcc_and_tiling` into the relevant private/public HWSS slots.

Control flow: all normal mode-set, stream, audio, eDP, link, and front-end flows continue through DCE110 handlers unless one of the overridden hooks is invoked. DCE80 does not define additional runtime sequencing of its own.

State and persistence: no local state is maintained. State effects come from the inherited DCE110 logic and the DCE100 helper hooks that program hardware power, clock, bandwidth, DCC, and tiling state.

Dependencies and integration points: depends on DCE110 HWSS, DCE100 HWSS helpers, DCE common pipe-control locking, and DCE8 register headers. It integrates with DCE8 resource construction as a compatibility layer over the DCE110 function table.

Risks and test signals: the main risk is relying on the DCE110 default table for behavior that may differ subtly on DCE8. Test signals include DCE8 boot/mode-set, pipe power transitions, bandwidth changes, DCC/tiling reset paths, and lock behavior around updates.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn201/dcn201_init.c

## Purpose
Installs the DCN 2.0.1 HWSS dispatch tables. It mostly reuses DCN10/DCN20/DCE110 behavior but swaps in DCN201 functions for UMA-aware plane address updates, initialization, unblank, MPCC update/disconnect, pipe locking, cursor attributes, and DMData attributes.

## Important APIs, Types, and Functions
Exports `dcn201_hw_sequencer_construct(struct dc *dc)`. Static tables are `dcn201_funcs` and `dcn201_private_funcs`. Public table differences include `init_hw = dcn201_init_hw`, `power_down_on_boot = NULL`, `update_plane_addr = dcn201_update_plane_addr`, `unblank_stream = dcn201_unblank_stream`, `pipe_control_lock = dcn201_pipe_control_lock`, `set_dmdata_attributes = dcn201_set_dmdata_attributes`, and `set_cursor_attribute = dcn201_set_cursor_attribute`. Private differences include `init_pipes = NULL`, `plane_atomic_disconnect = dcn201_plane_atomic_disconnect`, `update_mpcc = dcn201_update_mpcc`, `init_blank = dcn201_init_blank`, and no DSC PG hook.

## Control Flow
Construction assigns both tables to the DC object. Runtime control is indirect through those tables. Compared with DCN20, this table disables some inherited hooks and uses a simpler post-unlock path, reflecting ASIC-specific constraints.

## State and Persistence Behavior
Persists function pointer selection in `dc->hwss` and `dc->hwseq->funcs`. No independent state is stored in this file.

## Dependencies and Integration Points
Includes DCE110, DCN10, DCN20, and DCN201 HWSEQ headers. It is selected by DCN201 resource construction and is the integration point for `dcn201_hwseq.c`.

## Risks and Test Signals
The `NULL` hooks are important risk points: callers must tolerate absent `init_pipes`, stream gating, and DSC PG behavior on this generation. Test with mode-set, boot, resume, plane update, cursor, DMData, and power-down paths on DCN201 hardware.

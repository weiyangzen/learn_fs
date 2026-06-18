# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.c

## Purpose
This implementation provides the DCN3 MPC function table and the programming sequences for output gamma, denorm, output CSC, gamut remap, DWB muxing, output rate control disablement, RMU shaper LUTs, and RMU 3D LUTs. It composes older DCN1 plane topology helpers and DCN2 blending helpers with DCN3 color-management hardware.

## Important APIs, types, and functions
Constructor `dcn30_mpc_construct` initializes `struct dcn30_mpc`, assigns `dcn30_mpc_funcs`, stores register tables, records `num_mpcc` and `num_rmu`, and initializes every `mpcc` with `mpc3_init_mpcc`. Exported operations include `mpc3_mpc_init`, `mpc3_mpc_init_single_inst`, `mpc3_set_output_gamma`, `mpc3_program_shaper`, `mpc3_program_3dlut`, `mpcc3_acquire_rmu`, `mpc3_set_gamut_remap`, `mpc3_get_gamut_remap`, `mpc3_set_output_csc`, `mpc3_set_ocsc_default`, DWB helpers, and `mpc3_read_reg_state`.

## Control flow and state
Initialization first calls DCN1 MPC init, then disables MPC output rate and flow control for each valid OPP mux. OGAM programming checks debug color-management bypass, disables on `NULL` params, otherwise enables OGAM, chooses the inactive RAM bank from current hardware status, powers memory, writes region metadata and LUT samples, then switches bank select. Shaper and 3D LUT programming follow the same double-buffering pattern for RMU resources. 3D LUT data is split across four tetrahedral RAM masks and can be programmed as 12-bit paired values or packed 30-bit values. RMU acquisition reads mux status, returns an already-connected RMU, connects an idle one, or returns `-1`.

## Dependencies and integration points
The file depends on `reg_helper.h`, `dcn30_cm_common.h`, `dcn10_cm_common.h`, `basics/conversion.h`, `dc.h`, inherited MPC helpers (`mpc1_*`, `mpc2_*`), color helpers (`cm_helper_program_gamcor_xfer_func`, `cm_helper_program_color_matrices`, `cm_helper_read_color_matrices`), and matrix conversion helpers. It plugs into `struct mpc_funcs`, which higher display core code calls through the generic MPC interface.

## State and persistence behavior
Software state is held in `base.mpcc_array`, `num_mpcc`, `num_rmu`, and register table pointers. Hardware state lives in MPCC, OPP, DWB, OGAM, RMU mux, shaper, and 3D LUT registers. There is no durable persistence. Low-power state is controlled by debug flags and memory power registers; programming sequences temporarily force memory active and may restore low-power allowance afterward.

## Risks
RMU handling only explicitly covers RMU 0 and 1 in several helpers despite `MAX_RMU` being 3. Some invalid inputs trigger `BREAK_TO_DEBUGGER` rather than clean error propagation. LUT programming assumes entry counts and array layouts match hardware expectations, including even counts for 12-bit paired writes. Register waits have bounded retries, so power sequencing failures can leave partially programmed color blocks. Gamut remap double-buffering depends on correct `*_MODE_CURRENT` reads.

## Test signals
Important signals include no underflow or blanking during init, DWB mux idle status returning `0xf` when disabled, output gamma bank flips without visible artifacts, shaper and 3D LUT enable/disable paths with low-power enabled and disabled, RMU acquisition/release under multi-plane use, CSC defaults for multiple color spaces, gamut remap readback matching programmed matrices, and register-state dumps showing expected MPCC topology and color block modes.

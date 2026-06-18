# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn20/dcn20_mpc.c

Purpose: extends the DCN10 MPC implementation for DCN2.0 with richer blending controls, output denorm/clamp, output CSC, output gamma LUT programming, MPCC disabled-state handling, and updated function table behavior.

Important APIs/functions: `dcn20_mpc_construct` installs `dcn20_mpc_funcs`. Exports include `mpc2_update_blending`, `mpc2_set_denorm`, `mpc2_set_denorm_clamp`, `mpc2_set_output_csc`, `mpc2_set_ocsc_default`, `mpc20_power_on_ogam_lut`, and `mpc2_set_output_gamma`. It reuses DCN10 insert/remove/init/cursor/mux/bg-color helpers.

Control flow: blending programs alpha, global gains, background BPC, bottom gain mode, and top/bottom gain registers. Denorm maps output color depth to hardware denorm mode and clamp registers. CSC selects the inactive A/B coefficient bank based on current mode, programs matrices, then flips mode for frame-boundary update. Gamma reads current RAM A/B/bypass state, powers OGAM memory, selects the alternate RAM, programs transfer-function regions and PWL data through sequenced register writes, applies the DEDCN20-305 workaround when needed, and switches OGAM mode.

State/persistence: tracks inherited `mpcc_in_use_mask`, `num_mpcc`, and `mpcc_array`; updates persistent MPCC control, gain, denorm, CSC, OGAM RAM, LUT, and status registers. `mpc2_read_mpcc_state` also reports gamma mode.

Dependencies/integration: includes `dcn20_mpc.h`, `reg_helper`, `dc`, `mem_input`, and color-management helper code from `dcn10_cm_common`. It is used by DCN2 resource construction and later derived MPC implementations.

Risks: double-buffered CSC/gamma bank selection must match current hardware status or visible glitches occur. Gamma programming assumes valid `pwl_params` and point counts. Workaround behavior depends on debug/workaround flags and OTG locking assumptions. Idle assertions differ from DCN10 because disabled state is explicit.

Test signals: plane blending with global/top/bottom gains, output CSC changes across color spaces, denorm/clamp by bit depth, gamma LUT enable/bypass/A-B switching, DEDCN20-305 workaround, MPCC idle/disabled assertions, and inherited tree insert/remove coverage.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c

## Purpose
This file constructs and manages the DCN 3.1 resource pool for Yellow Carp-class APUs. It extends DCN30-style resources with DP 2.0/HPO encoders, DPIA/USB4 support, DMUB PSR and Replay objects, DCN31 DML population and validation wrappers, DET-buffer policy, and encoder-switch state updates.

## Important APIs, Types, And Functions
`res_cap_dcn31` declares 4 OTGs/OPPs/planes, 5 audio/stream/dig-link/DDC resources, 4 HPO DP stream encoders, 2 HPO DP link encoders, 5 PLLs, 1 DWB, 16 VMIDs, 2 3D LUTs, and 3 DSCs. Public functions include `dcn31_validate_bandwidth()`, `dcn31_calculate_wm_and_dlg()`, `dcn31_populate_dml_pipes_from_context()`, `dcn31_populate_dml_writeback_from_context()`, `dcn31_set_mcif_arb_params()`, `dcn31_get_det_buffer_size()`, `dcn31_create_resource_pool()`, and `dcn31_update_dc_state_for_encoder_switch()`. Static factories create DCN31 HUBP/Hubbub/TG/DCCG/DIO/link/HPO/audio/VPG/AFMT/APG/HWSEQ objects.

## Control Flow
`dcn31_create_resource_pool()` allocates `struct dcn31_resource_pool` and calls `dcn31_resource_construct()`. Construction sets BIOS registers, caps/functions, APU and DP2/HPO capabilities, color caps, host-router/DPIA counts, LTTPR defaults, debug/config defaults, VM helpers, five pixel PLL sources with B0-specific PLL remapping, a DP DTO source, DCCG, IRQ, Hubbub, DIO, per-pipe HUBP/DPP, OPP, TG, PSR, Replay, ABM, MPC, DSC, DWB/MMHUBBUB, AUX/I2C, optional USB4 DPIA counts for Yellow Carp B0 and GC 11.0.1, common resources, HW sequencer, plane caps, and `dc->dcn_ip->max_num_dpp`.

## State And Persistence
State lives in the resource pool arrays, HPO encoder arrays, `dc->caps`, `dc->config`, `dc->debug`, `dc->dml`, `dc->cap_funcs`, and `dc->dcn_ip`. `dcn31_populate_dml_pipes_from_context()` mutates DML pipe parameters: GPUVM/hostVM flags, immediate flip, unbounded request mode, vfront porch, DCC rate, DSC input bpc, and DET buffer size. It adjusts DET size for single non-video planes, CRB allocation policy, and multi-stream upscale cases. No filesystem persistence exists.

## Dependencies And Integration Points
The file depends on Yellow Carp/DCN312/NBIO/DPCS/MMHUB register headers, DCN31 DCCG/Hubbub/HUBP/OPTC/HPO/APG/link/panel code, DCN30 base blocks, DCN31 FPU code, link encoder configuration, DMUB PSR/Replay/ABM, DML, and common DC resource helpers. `dcn31_res_pool_funcs` wires the pool to DP2 encoder assignment/unassignment, bandwidth validation, DML population, writeback/MCIF wrappers, DET query, encoder-switch update, tiling defaults, and pipe pixel-clock parameter building.

## Risks
The constructor has many hardware-revision branches, especially PLL remapping and DPIA count assignment, so ASIC ID drift is risky. HPO stream encoder VPG/APG mapping must match register block numbering. `dcn31_validate_bandwidth()` allocates a pipe array and depends on FPU sections around validation; non-FPU builds only warn/assert for encoder-switch updates. Destruction handles many nested objects, including HPO VPG/APG children, and relies on pointer nulling. DET policy affects underflow risk and is sensitive to format/upscale decisions.

## Test Signals
Signals include probe on Yellow Carp A0/B0, DP1 to DP2 retraining with audio rebuilt, HPO stream/link encoder allocation, DPIA/USB4 displays, PSR and Replay object creation, DML validation under multi-stream/upscaled/immediate-flip cases, expected DET buffer size changes, DSC on eDP/DP, and clean unload. KASAN/KMEMLEAK and mode-validation tracing are valuable for constructor/destructor and bandwidth paths.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn201/dcn201_hwseq.c

## Purpose
Implements DCN 2.0.1-specific sequencing for UMA address translation, initialization, plane disconnect/connect, cursor programming, DMData setup, pipe locking, blanking, and DP/eDP unblank.

## Important APIs, Types, and Functions
Exported functions are `dcn201_update_plane_addr`, `dcn201_init_blank`, `dcn201_init_hw`, `dcn201_plane_atomic_disconnect`, `dcn201_update_mpcc`, `dcn201_pipe_control_lock`, `dcn201_set_cursor_attribute`, `dcn201_set_dmdata_attributes`, and `dcn201_unblank_stream`. Important internal helpers are `patch_address_for_sbs_tb_stereo`, `gpu_addr_to_uma`, `plane_address_in_gpu_space_to_uma`, and `read_mmhub_vm_setup`. Core types include `struct dc`, `struct dce_hwseq`, `struct pipe_ctx`, `struct dc_plane_state`, `struct hubp`, `struct dpp`, `struct mpc`, `struct output_pixel_processor`, `struct timing_generator`, and `PHYSICAL_ADDRESS_LOC`.

## Control Flow
Plane address updates optionally patch side-by-side/top-bottom stereo secondary pipes, copy the plane address, translate GPU FB addresses into UMA offsets, program HUBP flip/address registers, and restore the patched stereo address. Initialization starts clocks and DCCG, performs BIOS golden init, derives reference clocks from BIOS, initializes link encoders, reads MMHUB VM setup if not cached, blanks active TGs with OPP display pattern generator, locks active TGs, resets DPPs and MPC, initializes OPP MPC tree state, wires temporary pipe/HUBP/DPP/OPP resources, disconnects planes, maps DWB to MCIF_WB, unlocks TGs, disables planes, initializes TG/audio/DIO, and enables clock gating. MPCC disconnect removes secondary and primary MPCC entries, marks disconnect pending, requests optimization, and disconnects HUBP. MPCC update builds blend config, fast-updates blending on non-full updates, otherwise removes existing MPCC links and inserts a plane using a fixed `mpcc_id == dpp_id` policy.

## State and Persistence Behavior
The file caches FB/UMA aperture values in `hws->fb_base`, `fb_top`, `fb_offset`, and `uma_top`. It mutates plane status requested/current addresses, HUBP `mpcc_id`, `opp_id`, `power_gated`, OPP `mpc_tree_params`, `mpcc_disconnect_pending`, `dc->optimized_required`, pipe resource pointers, and stream DMData/cursor addresses. It also touches hardware registers through MMHUB, DCFCLK, DIO, TG, MPC, HUBP, DPP, OPP, and audio functions.

## Dependencies and Integration Points
Depends on DC resource objects and HW blocks from HUBP, DCHUBBUB, TG, OPP, IPP, MPC, DCCG, CLK manager, DIO, and link encoder implementations. Integrated by `dcn201_init.c` through public/private HWSS table entries.

## Risks and Test Signals
Address translation is high risk: incorrect FB aperture math can flip to wrong UMA addresses or trigger debugger breaks for non-UMA addresses. Init order is sensitive because TG lock/unlock, MPC reset, plane disable, audio, DIO, and clock gating must match hardware expectations. Test signals include S3/S4 resume, UMA systems, stereo surfaces, cursor updates, DMData on HDMI/DP, plane enable/disable, MPC blending, writeback resource pointer setup, and sanity-check/pstate validation.

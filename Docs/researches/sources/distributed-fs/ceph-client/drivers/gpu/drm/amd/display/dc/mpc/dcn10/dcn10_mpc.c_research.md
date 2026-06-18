# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn10/dcn10_mpc.c

Purpose: implements the DCN1.0 Multiple Pipe/Plane Combiner (MPC/MPCC) base behavior for composing DPP planes into OPP outputs.

Important APIs/functions: `dcn10_mpc_construct` installs the DCN10 `mpc_funcs`. Key operations include `mpc1_insert_plane`, `mpc1_remove_mpcc`, `mpc1_mpc_init`, `mpc1_mpc_init_single_inst`, `mpc1_init_mpcc_list_from_hw`, `mpc1_set_bg_color`, `mpc1_update_stereo_mix`, `mpc1_read_mpcc_state`, `mpc1_cursor_lock`, and `mpc1_get_mpc_out_mux`.

Control flow: insertion validates MPCC availability, links the new MPCC into the in-memory tree above a requested node or at the bottom, programs top/bottom selectors, OPP ID, update-lock mapping, output mux, blending, stereo mix, and in-use mask. Removal unlinks top/middle/bottom nodes, updates mux/selectors/mode, clears hardware selectors, and clears in-memory `dpp_id`/`mpcc_bot`. Init disconnects every MPCC and output mux. Hardware reconstruction reads mux/top/bottom/OPP registers to rebuild `tree->opp_list`.

State/persistence: tracks `mpcc_in_use_mask`, `num_mpcc`, and `mpc->mpcc_array` linked-list state; persistent hardware state lives in MPCC selector/control/status and MUX registers.

Dependencies/integration: uses `reg_helper` and generic `mpc.h` types. DCN20 reuses many DCN10 tree functions while overriding blending, color, gamma, and idle behavior.

Risks: linked-list corruption can create cycles; assertions guard some but not all traversal cases. In-memory tree and hardware mux state must stay synchronized across insert/remove/resume. Background color writes target the bottommost MPCC.

Test signals: multi-plane composition ordering, insert/remove top/middle/bottom, resume reconstruction from hardware, idle wait/assert paths, stereo mix programming, cursor lock, and mux readback.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/dcn35_init.c

## Purpose
`dcn35_init.c` constructs the DCN35 public and private hw sequencer callback tables. It binds DCN35-specific power, plane, idle, cursor offload, and timing behavior while retaining inherited DCE/DCN helpers for stable functionality.

## Important APIs, types, and functions
The file defines `dcn35_funcs`, `dcn35_private_funcs`, and `dcn35_hw_sequencer_construct`. Notable public bindings include `dcn35_init_hw`, `dcn35_power_down_on_boot`, `dcn35_disable_plane`, `dcn35_prepare_bandwidth`, `dcn35_optimize_bandwidth`, `dcn35_set_drr`, `dcn35_set_static_screen_control`, cursor offload callbacks, `dcn35_disable_link_output`, `dcn35_z10_restore`, `dcn35_apply_idle_power_optimizations`, block gate/ungate callbacks, root-clock control, long-vblank, hardware release, and pipe change detection. Private bindings include `dcn35_init_pipes`, `dcn35_plane_atomic_disable`, root-clock controls, `dcn35_update_odm`, DCN32 color helpers, DCN314 FIFO resync, DCN35 DP pixel-rate policy, and DCN35 plane enable.

## Control flow
`dcn35_hw_sequencer_construct` installs the two static tables onto `dc->hwss` and `dc->hwseq->funcs`. After construction, common DC code dispatches through those tables for init, modeset, plane updates, bandwidth transitions, idle power, cursor updates, and release.

## State and persistence behavior
This file sets long-lived function-pointer state on `dc`. Those assignments decide all later hardware sequencing behavior for the DCN35 device instance.

## Dependencies and integration points
The table composes functions from DCE110, DCN10/20/21/30/301/31/314/32/35. It integrates DCN35 into the common Display Core without duplicating common sequence code.

## Risks and edge cases
Callback selection is hardware-critical. For example, DCN35 uses `dcn10_lock_all_pipes` instead of DCN32's SubVP-specific interdependent lock, DCN35 bandwidth power gating instead of DCN20-only behavior, and DCN35 link disable instead of DCN32 for TMDS/SYMCLK handling. `enable_plane` in the public table points to `dcn20_enable_plane` while the private table has `dcn35_enable_plane`, so call-site choice matters.

## Test signals
Probe/init on DCN35 hardware, full modeset, plane disable/enable, bandwidth optimize/prepare, cursor offload, DRR/static screen control, link disable, and hardware release should all demonstrate that the installed callback table is coherent.

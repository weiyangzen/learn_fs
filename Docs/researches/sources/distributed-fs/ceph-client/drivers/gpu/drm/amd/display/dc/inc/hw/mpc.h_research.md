# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/mpc.h

## Purpose

`mpc.h` defines the Multiple Pipe/Plane Combiner abstraction. MPC blends DPP outputs into OPP outputs, supports flexible M-input to N-output composition, programs background color, stereo mixing, DWB routing, output CSC/gamma, gamut remap, and newer movable color-management LUT blocks.

## Important APIs, Types, And Functions

Constants define `MAX_MPCC`, `MAX_OPP`, and `MAX_DWB`. Blend and color enums include `mpc_output_csc_mode`, `mpcc_blend_mode`, `mpcc_alpha_blend_mode`, movable CM location, and `MCM_LUT_ID`. Configuration structs cover 3D LUT fast-load (`mpc_fl_3dlut_config`), LUT parameters (`mcm_lut_params`), blending (`mpcc_blnd_cfg`), gamut adjustment, RMCM register snapshots, stereo mix, denorm clamp, and DWB flow control.

`struct mpcc` is the node for an MPC tree and stores MPCC ID, DPP ID, bottom link, blend/stereo config, and shared-bottom state. `struct mpc_tree` associates a tree with an OPP and the top MPCC list. `struct mpc` owns the vtable, context, MPCC array, blender PWL params, and CM bypass flag. `mpc_funcs` is large: it reads state, inserts/removes planes in OPP or DWB trees, initializes MPCCs, updates blending, locks cursors, waits/asserts idle, initializes from hardware, programs denorm/output CSC/output gamma, controls MPC memory power, sets DWB muxes, programs output rate control, gamut remap, 1D/shaper/3D LUTs, RMU acquire/release, background color, low-power mode, movable CM location, fast-load status, and RMCM sequential programming.

## Control Flow

Composition control flows through tree mutation: allocate/select MPCC, insert it into an OPP or DWB tree, program blend/stereo/background settings, and wait for idle before reconnecting. Color programming either uses classic output gamma/CSC hooks or newer RMU/RMCM hooks for shaper and 3D LUT operation. DWB capture routes through MPC muxes. Removal detaches MPCCs and returns them to idle.

## State And Persistence Behavior

MPC state is both software topology and hardware mux state. The `mpcc_array` mirrors physical MPCC nodes, while hardware registers define active links, LUT RAM banks, RMU ownership, DWB muxes, and memory power. LUT programming is persistent and banked; RMU acquire/release must remain synchronized with MPCC ownership.

## Dependencies And Integration Points

The file depends on `dc_hw_types.h`, `hw_shared.h`, `transform.h`, and `dc_types.h`. It integrates with resource pipe topology code, OPP/OPTC timing paths, DPP/transform output, DWB, color management, cursor locking, and debug state dump paths.

## Risks And Test Signals

Risks include MPCC tree corruption, idle wait failures, incorrect blend order, shared-bottom DWB/OPP mistakes, RMU ownership leaks, LUT bank mismatches, and underflow during reconnect. Test signals include multi-plane blending, ODM/MPC slice composition, DWB capture, cursor locking across planes, color-management PWL/3D LUT tests, RMCM fast-load status, and underflow register dumps.

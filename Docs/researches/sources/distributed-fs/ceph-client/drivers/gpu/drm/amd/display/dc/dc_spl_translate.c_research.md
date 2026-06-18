# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_spl_translate.c

## Purpose
`dc_spl_translate.c` translates between DC pipe context structures and SPL scaler library input/output structures. It lets DC reuse SPL calculations while preserving DC-native structs for resource and hardware programming.

## Important APIs, Types, And Functions
Static helpers copy `rect` to/from `spl_rect`, map `scaling_taps` to/from `spl_taps`, convert SPL fixed-point ratio/init outputs to DC `fixed31_32`, and convert `dc_pixel_format` to `spl_pixel_format`.

`translate_SPL_in_params_from_pipe_ctx` fills `struct spl_in` from `struct pipe_ctx`. It chooses line-buffer partition callbacks based on `plane_state->ctx->dce_version`: DCN2, DCN3.2, DCN4.01/4.2, or DCN2 default. It maps plane clip/source/destination, stream source/destination, rotation, mirror, MPC slice count/index, ODM slice rect/index, output size including DSC hactive padding, scaler taps, EASF/debug settings, adaptive sharpening, linear-light scaling, cositing, transfer function, h/v active size, sharpness policy, fullscreen/HDR flags, and SDR white level.

`translate_SPL_out_params_to_pipe_ctx` copies SPL scaler program output back into `pipe_ctx->plane_res.scl_data`: recout, ratios, viewport, chroma viewport, taps, and scaler inits.

## Control Flow And State
Input translation is mostly field copying with policy branches for DCN generation and debug overrides. Output translation mutates the pipe context scaler data based on SPL results. No persistent storage is allocated here; state is transferred between caller-owned `pipe_ctx`, `spl_in`, and `spl_out`.

## Dependencies And Integration Points
It includes `dc_spl_translate.h`, DPP headers for generation-specific `dscl*_spl_calc_lb_num_partitions` callbacks, and uses resource helpers such as `resource_get_odm_slice_src_rect`, `resource_get_mpc_slice_count`, and `resource_get_mpc_slice_index`. It also calls `dm_helpers_is_hdr_on`. It integrates with scaler programming, adaptive sharpening, EASF, ODM/MPC slicing, and DC debug policy.

## Risks
The function assumes `pipe_ctx`, `plane_state`, `stream`, and stream timing/resource pointers are valid. Enum casts between DC and SPL types rely on aligned enum values; only pixel format has an invalid guard. Tap output adds one to SPL tap values, which is a subtle convention that can create off-by-one scaler programming if SPL changes. Fixed-point conversion right-shifts SPL fractional values by five bits; this must match SPL format. Debug override precedence can mask plane settings.

## Test Signals
Tests should compare translated SPL inputs/outputs for scaling, rotation, chroma formats, side-by-side 3D, ODM/MPC split cases, DSC padding, DCN2/DCN3.2/DCN4 callback selection, EASF force modes, adaptive sharpening modes, HDR detection, and tap/ratio fixed-point conversions.

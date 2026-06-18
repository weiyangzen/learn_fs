# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.c

## Purpose
`dcn10_opp.c` implements the DCN1.0 output pixel processor. It programs FMT bit-depth reduction, spatial dithering, clamping, pixel encoding, dynamic expansion, stereo OPP buffer parameters, pipe clock control, and basic register-state readback.

## Important APIs, types, and functions
Public functions wired into `struct opp_funcs` are `opp1_set_dyn_expansion()`, `opp1_program_fmt()`, `opp1_program_bit_depth_reduction()`, `opp1_program_stereo()`, `opp1_pipe_clock_control()`, `opp1_destroy()`, and `opp1_read_reg_state()`. Internal helpers include `opp1_set_truncation()`, `opp1_set_spatial_dither()`, `opp1_set_pixel_encoding()`, `opp1_set_clamping()`, and `opp1_program_clamping_and_pixel_encoding()`. `dcn10_opp_construct()` binds context, instance, register tables, masks, shifts, and the function table.

## Control flow
`opp1_program_fmt()` optionally releases 4:2:0 map memory from forced power mode, then programs bit-depth reduction before clamping and pixel encoding because dithering depends on the CRTC source selection. Bit-depth reduction first writes truncation controls, then disables old dither state, configures frame-random counters and seeds, and enables requested spatial-dither fields. Pixel encoding maps RGB/YCbCr444 to 4:4:4, YCbCr422 to subsampling mode 2, and YCbCr420 to pixel encoding 2 with CbCr bit reduction bypass, unless the debug option forces 1-tap chroma subsampling. Dynamic expansion only enables 8-to-12 or 10-to-12 expansion for HDMI, DP, MST, and virtual signals when `opp->dyn_expansion` permits it.

## State and persistence behavior
The implementation stores no durable state. `struct dcn10_opp` keeps pointers to immutable register metadata and a base `output_pixel_processor`. Runtime state is hardware register state in FMT, OPPBUF, and OPP_PIPE blocks. `opp1_destroy()` frees the allocated OPP object.

## Dependencies and integration points
The file depends on AMD DC core types, `dm_services`, `reg_helper`, OPP interface types from `opp.h`, color/depth/timing enums, and debug flags under `dc->debug`. It is constructed by resource code and called by pipe/mode programming code before data reaches OPTC/stream encoder blocks.

## Risks and edge cases
Dither programming has depth-specific frame-counter settings and silently returns for unsupported depth. Clamping has an unimplemented programmable case. Stereo active width subtracts `h_border_right` twice, which may be intentional or legacy but is a maintenance risk. Dynamic expansion is signal-type gated. Debug-forced 1-tap chroma subsampling can override normal 4:2:2/4:2:0 setup.

## Test signals
Mode-set tests across RGB, YCbCr444, YCbCr422, and YCbCr420; 6/8/10/12 bpc output; dither/truncation enable combinations; debug forced chroma subsampling; dynamic-expansion signal coverage; stereo timing formats; and register readback through `opp_read_reg_state()` are key signals.

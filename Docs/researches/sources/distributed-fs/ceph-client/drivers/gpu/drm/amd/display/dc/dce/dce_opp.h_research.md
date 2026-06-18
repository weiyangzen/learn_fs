# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_opp.h

## Purpose
This header declares the DCE output pixel processor object and formatter register metadata. It supports DCE6 through DCE12 register-list variants for FMT bit-depth, dither, dynamic expansion, clamp, pixel encoding, and 4:2:0 memory control.

## Important APIs, Types, and Macros
`FROM_DCE11_OPP()` and `TO_DCE110_OPP()` cast from the abstract OPP type. `enum dce110_opp_reg_type` names DCP/DCFE/FMT register spaces. Register list macros include `OPP_COMMON_REG_LIST_BASE()`, DCE80/100/110/112/120 variants, and optional DCE60. Mask/shift macros cover dynamic expansion, truncation, spatial/temporal dithering, random seeds, frame counter control, stereo sync override, 4:2:0 memory, clamp components, pixel encoding/subsampling, and CbCr bit-reduction bypass. Public prototypes declare constructors, destructor, formatter programming, bit-depth reduction, dynamic expansion, and clamping.

## Control Flow and State
The header has no runtime control flow but defines which fields the implementation can program. `struct dce110_opp` stores the base `output_pixel_processor` plus register, shift, and mask metadata.

## Dependencies and Integration Points
It depends on `dc_types.h`, `opp.h`, and `core_types.h`, plus generated register macros from generation-specific files. It is consumed by resource builders and `dce_opp.c`.

## Risks and Test Signals
Register availability changes by generation: DCE112 adds FMT memory, DCE120 uses prefixed FMT0 fields, and DCE60 lacks several fields. Compile coverage and mode-set tests with RGB, YCbCr422, YCbCr420, clamp, and dither options are the main signals. Header macro skew can produce subtle runtime formatting errors even when builds pass.

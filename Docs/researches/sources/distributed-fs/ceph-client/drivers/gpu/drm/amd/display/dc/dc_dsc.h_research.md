# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_dsc.h

## Purpose
`dc_dsc.h` declares the public Display Stream Compression helper interface used by DC to parse DSC DPCD data, compute bandwidth ranges, select encoder configuration, and tune DSC policy for a timing. It is an interface header; implementation is elsewhere.

## Important APIs, Types, And Data Contracts
`struct dc_dsc_bw_range` reports min/max compressed bandwidth and target bpp in x16 fixed units plus uncompressed stream bandwidth. `struct display_stream_compressor` is the hardware/service object containing `dsc_funcs`, `dc_context`, and instance id. `struct dc_dsc_policy` captures policy choices such as slice preference, target bpp limits, forced DSC, and YCbCr422-simple handling. `struct dc_dsc_config_options` carries per-call overrides for slice height, target bpp cap, ODM h-slice, and force-DSC behavior.

The key functions are `dc_dsc_parse_dsc_dpcd`, `dc_dsc_compute_bandwidth_range`, `dc_dsc_compute_config`, `dc_dsc_stream_bandwidth_in_kbps`, `dc_dsc_stream_bandwidth_overhead_in_kbps`, `dc_dsc_get_policy_for_timing`, and policy setters for max target bpp, forced DSC, and stream overhead. Dump helpers expose decoder/encoder capabilities to logs.

## Control Flow And State
The header declares stateless computation functions plus global policy setters. The policy setters imply module-level mutable policy in the implementation, so tests must account for cross-test state and reset policy between cases. Compute flow is DPCD parse, policy/default option selection, bandwidth range calculation, then specific DSC config selection for target bandwidth and link encoding.

## Dependencies And Integration Points
It defines temporary DP extended DSC DPCD addresses and includes `dc_types.h`, using `struct dc`, `struct dc_crtc_timing`, `struct dc_dsc_config`, `struct dsc_dec_dpcd_caps`, and `enum dc_link_encoding_format`. It integrates with DP/eDP/HDMI FRL link validation, MST bandwidth calculation, timing validation, stream resource programming, and debug logging.

## Risks
Target bpp uses x16 fixed-point units while some policy fields are plain `uint32_t`, so unit confusion can over- or under-compress streams. Global policy setters can make behavior order-dependent. `dsc_min_slice_height_override` and slice granularity must remain aligned with hardware restrictions. HDMI FRL and DP overhead differ, making `is_dp` and link encoding selection important for bandwidth math.

## Test Signals
Use known DSC DPCD byte fixtures, eDP and DP sink variants, HDMI FRL DSC cases, MST hub branch throughput limits, min/max target bpp clamp tests, disabled-overhead policy tests, and mode validation for timings near link bandwidth boundaries.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dc_dsc.c

## Purpose

`dc_dsc.c` is the shared AMD Display Core Display Stream Compression policy and negotiation layer. It parses sink DSC DPCD capability blocks, derives encoder capabilities from the active DSC object and clock/resource limits, intersects source and sink capabilities, selects slice geometry and target bits-per-pixel, and computes bandwidth ranges used by link validation.

## Important APIs, Types, And Functions

Public entry points include `dc_bandwidth_in_kbps_from_timing`, `dc_dsc_parse_dsc_dpcd`, `dc_dsc_compute_bandwidth_range`, `dc_dsc_compute_config`, `dc_dsc_stream_bandwidth_in_kbps`, `dc_dsc_stream_bandwidth_overhead_in_kbps`, `dc_dsc_get_policy_for_timing`, the policy setter functions, and `dc_dsc_get_default_config_option`. Internal helpers convert DPCD encodings, build multi-DSC slice caps, intersect `struct dsc_dec_dpcd_caps` with `struct dsc_enc_caps`, choose slice counts, and compute target BPP from a link bandwidth budget.

## Control Flow

DSC setup flows from sink DPCD parsing to encoder cap collection to `setup_dsc_config`. `setup_dsc_config` rejects unsupported branch line width, missing DSC support, incompatible color format/depth, throughput limits, invalid slice divisibility, and impossible slice height. It applies policy defaults and debug/options overrides, chooses horizontal/vertical slice counts, optionally computes target BPP from bandwidth, and fills `struct dc_dsc_config`.

## State, Dependencies, Risks, And Test Signals

There is no disk persistence. The file owns process-global DSC policy toggles and mutates caller-provided capability/range/config structures. It depends on DRM DP/DSC helpers, AMD fixed-point math, clock manager, resource pool, `display_stream_compressor` function tables, and DC timing/color enums. Risks include global policy side effects, malformed timing math, slice loops relying on valid caps, and broad debug overrides. Tests should cover DPCD parsing, RGB/YUV policy, eDP max BPP, branch limits, forced ODM slices, overhead math, and zeroed failure configs.

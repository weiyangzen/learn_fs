# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/hw_shared.h

## Purpose

`hw_shared.h` is the common AMD Display Core hardware type header used by multiple virtual hardware blocks. It centralizes hardware topology limits, color/gamma lookup-table data shapes, shared pixel-processing enums, DisplayPort test-pattern enums, and compact audio-channel bit layout. It does not implement algorithms; it publishes stable data contracts used by IPP, DPP/transform, OPP, MPC, stream/timing encoders, and resource code.

## Important APIs, Types, And Functions

The header defines global sizing constants such as `MAX_PIPES`, `MAX_LINKS`, `MAX_DIG_LINK_ENCODERS`, `MAX_DWB_PIPES`, and HPO DP encoder limits. `pipe_topology_line`, `pipe_topology_snapshot`, and `pipe_topology_history` describe recorded pipe layout snapshots with phantom-pipe, plane, slice, stream, DPP, OPP, and TG identifiers. Color-management structures include `gamma_curve`, `curve_points`, `curve_points3`, `pwl_result_data`, `dc_rgb`, `tetrahedral_*`, `tetrahedral_params`, and `pwl_params`.

Shared enums cover line-buffer pixel depth, CSC adjustment type, IPP degamma/gamcor/output-format modes, expansion mode, gamut remap, OPP regamma, OPTC DSC mode, DP/controller test patterns, DP color space, test-pattern component depth, and LUT RAM selection. `default_adjustment`, `out_csc_color_matrix`, and `dc_bias_and_scale` carry color-conversion setup. `union audio_cea_channels` maps CEA speaker bits onto named channel flags.

## Control Flow

There is no runtime control flow. Include-time behavior is limited to the header guard and type publication. The key behavioral contract is that consumers can use the same enums and structures when programming different hardware blocks, avoiding divergent definitions for LUT layout, color-space setup, test patterns, and display topology logging.

## State And Persistence Behavior

The file creates no runtime state. Its persistent effect is ABI-like source compatibility inside DC: array sizes, enum numeric values, bit-vector encodings, and large LUT structures must remain consistent with hardware programming code and any state snapshots stored in DC state objects. `lb_pixel_depth` explicitly states that values are used as bit vectors, so numeric changes are behavioral.

## Dependencies And Integration Points

It depends on `os_types.h`, `fixed31_32.h`, and `dc_hw_types.h`. It is included by multiple hardware abstraction headers in this group, especially IPP, OPP, MPC, transform, stream encoder, and timing generator paths. Resource and debug code consume the topology snapshot structures when logging pipe layout changes.

## Risks And Test Signals

Risks are mostly compatibility risks: changing `MAX_*` constants can under-size or over-size arrays in resource pools; changing enum values can misprogram hardware registers; and large tetrahedral LUT arrays are memory-heavy and sensitive to dimension assumptions. Good test signals are clean AMDGPU display builds across DCE/DCN variants, color-management validation with PWL/3D LUT programming, DSC/test-pattern CTS paths, pipe topology logging, and audio speaker-channel mapping tests.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dsc.c

## Purpose
Implements the original DPU DSC hardware wrapper for display stream compression. It programs DSC encoder registers from DRM DSC config, writes rate-control thresholds and range parameters, disables DSC, and optionally binds DSC output to a pingpong block on DPU5+.

## Important APIs, Types, and Functions
The public constructor is `dpu_hw_dsc_init`. Exposed ops are `dpu_hw_dsc_disable`, `dpu_hw_dsc_config`, `dpu_hw_dsc_config_thresh`, and `dpu_hw_dsc_bind_pingpong_blk`. The config path writes common mode, encoder flags, picture/slice size, chunk size, HRD delay, scale intervals, BPG offsets, flatness thresholds, model size, and RC config. Threshold programming iterates DRM DSC buffer threshold and `rc_range_params` arrays.

## Control Flow and State
The wrapper is stateless apart from register map, index, caps, and ops. `dsc_config` derives command/video initial-line adjustment, slice last group size, input bit depth, and flatness threshold through DRM helpers, then writes registers. `dsc_config_thresh` writes contiguous threshold/minQP/maxQP/BPG register ranges. Binding computes a DSC-specific CTL mux offset and writes either a PP index or disabled value.

## Dependencies and Integration Points
Consumes `struct drm_dsc_config`, DRM DSC helper calculations, catalog DSC config, DPU register helpers, and CTL/encoder DSC topology. Encoders call DSC ops while CTL flushes DSC blocks.

## Risks and Test Signals
Risks include bitfield packing mistakes, command-mode initial-line off-by-one, mismatch with DSC v1.2 wrapper selection, and binding wrong pingpong. Tests should cover RGB/DSI DSC, video vs command mode, split/multiplex flags where supported, threshold table programming, disable, PP bind/unbind, and comparison against panel DSC PPS expectations.

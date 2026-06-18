# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dsc.h

## Purpose
Declares the DSC hardware wrapper API shared by both legacy and v1.2 implementations.

## Important APIs, Types, and Functions
Mode flags are `DSC_MODE_SPLIT_PANEL`, `DSC_MODE_MULTIPLEX`, and `DSC_MODE_VIDEO`. `struct dpu_hw_dsc_ops` exposes `dsc_disable`, `dsc_config`, `dsc_config_thresh`, and `dsc_bind_pingpong_blk`. `struct dpu_hw_dsc` stores generic block, register map, DSC index, catalog caps, and ops. Constructors are `dpu_hw_dsc_init` and `dpu_hw_dsc_init_1_2`; `to_dpu_hw_dsc` casts from generic hardware block.

## Control Flow and State
The header makes DSC programming a two-step operation: base config and threshold config. Callers must select the correct constructor for the catalog/hardware revision, then invoke ops after clocks are enabled and before CTL flush.

## Dependencies and Integration Points
Includes DRM DSC config definitions and references DPU catalog DSC structures and pingpong IDs. Encoders and topology helpers use this API to program DSC blocks and route compressed output.

## Risks and Test Signals
Risks include callers assuming `dsc_bind_pingpong_blk` exists on all hardware, using legacy constructor on v1.2 hardware, or omitting threshold programming. Tests should verify constructor selection, op presence, mode flag combinations, and DSC + CTL flush integration.

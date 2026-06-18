# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dsc_1_2.c

## Purpose
Implements DSC hardware programming for DPU DSC 1.2-style register layout. It supports newer wrapper/control offsets, native 4:2:0 and 4:2:2 encoding flags, packed threshold registers, and pingpong binding through catalog sub-block offsets.

## Important APIs, Types, and Functions
The public constructor is `dpu_hw_dsc_init_1_2`. Ops are installed by `_setup_dcs_ops_1_2`: `dpu_hw_dsc_disable_1_2`, `dpu_hw_dsc_config_1_2`, `dpu_hw_dsc_config_thresh_1_2`, and `dpu_hw_dsc_bind_pingpong_blk_1_2`. `_dsc_calc_output_buf_max_addr` derives output buffer max address from number of active soft slices and native 42x support.

## Control Flow and State
`dsc_config_1_2` writes common main config for split/multiplex topology, computes active slices per encoder, sets video/command and output-buffer fields, programs DSC version minor, native 420/422, bpp doubling for native 42x, block prediction, RGB conversion, line buffer depth, picture/slice sizes, HRD delays, scale intervals, first/second-line offsets, BPG offsets, flatness, RC model/config, and wrapper enable bits. Threshold programming packs 14 buffer thresholds into four registers and 15 min-QP/max-QP/BPG entries into three registers each. Disable clears wrapper and encoder enable/control registers.

## Dependencies and Integration Points
Uses DRM DSC helpers, catalog `dpu_dsc_sub_blks` offsets, feature bit `DPU_DSC_NATIVE_42x_EN`, DPU register helpers, and the same `dpu_hw_dsc_ops` API as legacy DSC.

## Risks and Test Signals
Native 420/422 bpp scaling and slice multiplex math are high-risk. Tests should include DSC 1.2 panels, native 420/422 when catalog supports it, split-panel and multiplex topologies, command/video mode differences, packed threshold register validation, disable path, and PP bind/unbind through `sblk->ctl.base`.

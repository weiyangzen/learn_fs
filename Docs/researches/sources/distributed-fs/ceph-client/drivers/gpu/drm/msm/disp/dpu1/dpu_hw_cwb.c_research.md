# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_cwb.c

## Purpose
Implements the concurrent writeback mux wrapper. CWB selects a real-time pingpong source and an input tap point so display output can be captured while scanout continues.

## Important APIs, Types, and Functions
The public constructor is `dpu_hw_cwb_init`. The only op is `dpu_hw_cwb_config`, exposed as `config_cwb`, which programs `CWB_MUX` and `CWB_MODE` using `dpu_hw_cwb_setup_cfg`. `CWB_MUX_MASK` and `CWB_MODE_MASK` define the low-bit fields.

## Control Flow and State
The wrapper stores register base, log mask, index, and ops. Config validates non-null config and input enum range. It defaults mux to disabled `0xf`; if `pp_idx` is a real pingpong, it writes the zero-based PP index into the mux field. It writes the input mode into `CWB_MODE`.

## Dependencies and Integration Points
Uses catalog `dpu_cwb_cfg`, DPU pingpong IDs, and register helpers. Encoder helper CWB setup and writeback setup call this block, while CTL tracks CWB active/flush masks.

## Risks and Test Signals
Risks include accepting an invalid pingpong range, wrong tap point, or failing to disable mux when CWB is not active. Tests should cover LM output and DSPP output input modes, PP_NONE disable behavior, each valid PP index, CWB + WB commit, CWB teardown, and CTL CWB active/flush register pairing.

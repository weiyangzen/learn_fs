# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_cwb.h

## Purpose
Declares the concurrent writeback hardware wrapper, setup payload, input-mode enum, and init/cast helpers.

## Important APIs, Types, and Functions
`enum cwb_mode_input` defines `INPUT_MODE_LM_OUT` and `INPUT_MODE_DSPP_OUT`. `struct dpu_hw_cwb_setup_cfg` carries the real-time pingpong index and input tap point. `struct dpu_hw_cwb_ops` exposes `config_cwb`. `struct dpu_hw_cwb` stores the generic hardware block, register map, CWB index, and ops. `to_dpu_hw_cwb` converts from generic block and `dpu_hw_cwb_init` creates the wrapper.

## Control Flow and State
The header defines only transient configuration and wrapper state. Runtime persistence is limited to the allocated hardware object; CWB mux choices live in registers and are usually coordinated by encoder helper and CTL flush state.

## Dependencies and Integration Points
Includes DPU hardware utility definitions and references `enum dpu_pingpong`, `enum dpu_cwb`, and catalog `dpu_cwb_cfg`. It integrates with writeback and concurrent capture paths.

## Risks and Test Signals
The enum-to-register mapping must remain synchronized with hardware documentation. Tests should check both input modes, invalid input rejection in implementation, PP_NONE behavior, and that callers pair CWB config with CTL CWB active and flush updates.

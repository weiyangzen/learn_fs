# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_ctl.h

## Purpose
Declares the CTL hardware wrapper interface and data structures used to configure display/writeback topology, pending flushes, resets, blend stages, and active block bitmaps.

## Important APIs, Types, and Functions
`enum dpu_ctl_mode_sel` distinguishes video and command interface mode. `struct dpu_hw_stage_cfg` maps DPU stages and multirect indexes to SSPP pipes. `struct dpu_hw_intf_cfg` describes CTL output topology: INTF, master INTF, WB, 3D mode, merge-3D, mode select, CDM, stream select, DSC mask, and CWB mask. `struct dpu_hw_ctl_ops` is the main vtable with start/pending/flush/reset/topology/blend/active-pipe operations. `struct dpu_hw_ctl` stores catalog caps, mixer caps, MDSS version, cached pending masks, and ops. `dpu_hw_ctl_init` constructs the wrapper.

## Control Flow and State
The header explicitly separates software-cached pending masks from hardware side effects: most `update_pending_flush*` ops have no immediate hardware effect until `trigger_flush`. This contract matters for encoders that accumulate all flush bits before kickoff. Reset and active topology ops are immediate hardware operations in the implementation.

## Dependencies and Integration Points
Includes DPU MDSS, util, catalog, and SSPP definitions. It is a central dependency for encoders, planes, mixers, DSPP, DSC/CDM/WB/CWB, resource manager, and hardware init code.

## Risks and Test Signals
Caller misuse is the key risk: forgetting `trigger_flush`, using a null generation-gated op, passing enum values outside catalog ranges, or failing to clear pending masks after a failed commit. Tests should assert ops availability for each core major version and verify topology structs are populated consistently for video, command, writeback, DSC merge, and CWB commits.

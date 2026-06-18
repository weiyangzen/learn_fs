# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-m2m.h

## Purpose
This header defines the MDP3 mem2mem context and its small public interface to the rest of the driver.

## Important APIs, Types, And Functions
`MDP_MAX_CTRLS` sizes the V4L2 control handler. The queue-role enum maps source and destination frame counters. `struct mdp_m2m_ctrls` stores hflip, vflip, and rotate controls. `struct mdp_m2m_ctx` contains a V4L2 file handle, control handler, mem2mem context, frame counters, current MDP frame parameters, and a context mutex. Public functions are `mdp_m2m_device_register()`, `mdp_m2m_device_unregister()`, and `mdp_m2m_job_finish()`.

## Control Flow
The header itself has no execution. It defines the object created by `mdp_m2m_open()` and consumed by queue callbacks, VPU/CMDQ submission, and completion.

## State, Persistence, And Dependencies
State is per-open-file and in memory only. `curr_param` is the key mutable processing state. The header depends on V4L2 controls, MDP core state, VPU types, and register/format definitions.

## Integration Points
Core probe registers the M2M device. CMDQ completion calls `mdp_m2m_job_finish()` to return queued vb2 buffers. Register helpers rely on the context's `mdp_frameparam`.

## Risks
The context state bits are stored in `curr_param.state`, not directly in this header, so callers must use the M2M state helpers in the C file. `MDP_M2M_MAX` must match the frame counter array.

## Test Signals
Open/close leaks, control lifetime, frame counter sequencing, and job completion ordering validate this contract.

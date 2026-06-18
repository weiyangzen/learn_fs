# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_drv.h

## Purpose
Central MSM DRM private header declaring shared driver state, feature glue, subsystem entry points, helpers, and configuration stubs.

## Important APIs, types, and functions
- `struct msm_drm_private` holds DRM device, KMS/GPU pointers, GEM object/LRU/shrinker state, debug handles, hangcheck/devfreq config, and fault-stall fields.
- Controller enums define DP and DSI controller IDs and `MSM_GPU_MAX_RINGS`.
- Declares atomic, MMU, GEM, PRIME, framebuffer, fbdev, HDMI, DSI, DP, MDP, DPU, MDSS, debugfs, IO remap, ICC, hrtimer work, probe, and shutdown APIs.
- Helpers include `msm_rmw()`, `align_pitch()`, `timeout_to_jiffies()`, `UERR`, `DBG`, `FIELD`, and `COND`.
- Conditional stubs compile out disabled subsystems.

## Control flow
Mostly declarative. Inline helpers perform read-modify-write, pitch alignment to 32 pixels, absolute timeout conversion to jiffies, and disabled-subsystem no-op/error behavior.

## State and persistence
The main persistent state definition is `struct msm_drm_private`, owned by `msm_drv.c` and shared by GPU/KMS/GEM/debugfs code. No storage is allocated by the header.

## Dependencies and integration points
Pulls together Linux platform/component/PM/IOMMU/devfreq headers, DRM atomic/probe/DSC/GEM/UAPI headers, and internal subsystem declarations. Almost every MSM DRM file depends on it.

## Risks
Because this is a broad private ABI, structure changes can affect many modules. Conditional stubs must match real signatures. `timeout_to_jiffies()` treats expired deadlines as zero, influencing wait IOCTL behavior. Global helper macros like `FIELD()` depend on generated mask/shift names.

## Test signals
Build coverage across configurations with HDMI/DSI/DP/MDP/DPU/MDSS/debugfs/fbdev enabled and disabled, plus runtime checks of timeout and pitch helper behavior.

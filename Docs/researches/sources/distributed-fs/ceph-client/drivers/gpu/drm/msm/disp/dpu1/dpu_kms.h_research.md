# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_kms.h

## Purpose
Declares the DPU KMS core object, global atomic state, logging helpers, KMS utility APIs, vblank hooks, and shared constants used by DPU CRTC/encoder/plane/hardware modules.

## Important APIs, types, and functions
- `struct dpu_kms` embeds `struct msm_kms` and owns device, catalog, UBWC data, MMIO bases, regulators, interrupts, perf, global private state, resource manager, VBIF/MDP wrappers, platform device, clocks, bandwidth refs, and ICC paths.
- `struct dpu_global_state` tracks shared hardware block ownership by CRTC ID for pingpong, mixer, CTL, DSPP, DSC, CDM, SSPP, and CWB resources.
- Helpers/macros include `to_dpu_kms()`, `to_dpu_global_state()`, `DRMID()`, DPU logging macros, `ktime_compare_safe()`, timeout constants, and `DPU_KMS_INFO_MAX_SIZE`.
- Declares `dpu_kms_get_global_state()`, `dpu_kms_get_existing_global_state()`, debugfs regset helper, vblank wrappers, and `dpu_kms_get_clk_rate()`.

## Control flow
The header has no runtime flow except macros. It defines the shared object model that implementation files use to access KMS state and atomic resource allocations.

## State and persistence
The structs declared here are central persistent in-memory state for the DPU driver. `dpu_global_state` is duplicated per atomic transaction and becomes persistent after atomic swap; `dpu_kms` persists for the platform device lifetime.

## Dependencies and integration points
Includes Linux interconnect, DRM driver, MSM KMS/MMU/GEM, DPU catalog, CTL, LM, interrupts, TOP, RM, and perf headers. Nearly all DPU modules include it for access to driver state and logging.

## Risks
Resource ownership arrays depend on enum ranges and offsets. Direct access to `global_state` is discouraged; callers must use getter helpers to satisfy DRM locking. Changes to `dpu_kms` affect initialization, runtime PM, debugfs, and plane/CRTC/encoder modules.

## Test signals
Build coverage is broad. Runtime validation includes atomic resource allocation consistency, state printouts, vblank operations, clock-rate queries, debugfs register reads, and suspend/resume behavior.

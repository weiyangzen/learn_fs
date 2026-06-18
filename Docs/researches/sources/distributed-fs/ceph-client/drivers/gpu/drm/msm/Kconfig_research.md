# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/Kconfig

## Purpose
Defines build-time configuration for the Qualcomm MSM/Snapdragon DRM driver, including core GPU support, KMS display blocks, DisplayPort, DSI PHY variants, HDMI, HDCP, debug-oriented GPU state, and developer-only options.

## Important APIs, types, and functions
- `DRM_MSM` is the root tristate depending on DRM, OF, PM, IOMMU support, common clocks, and Qualcomm optional subsystems, and selecting GPUVM/scheduler/exec/shmem/tmpfs/SCM/UBWC and other helpers.
- `DRM_MSM_GPU_STATE`, `DRM_MSM_GPU_SUDO`, and `DRM_MSM_VALIDATE_XML` configure diagnostics, privileged submit behavior, and XML schema validation.
- `DRM_MSM_KMS`, `DRM_MSM_KMS_FBDEV`, and `DRM_MSM_MDSS` provide display core selections.
- `DRM_MSM_MDP4`, `DRM_MSM_MDP5`, and `DRM_MSM_DPU` enable display controller generations.
- `DRM_MSM_DP`, `DRM_MSM_DSI`, DSI PHY options, `DRM_MSM_HDMI`, and `DRM_MSM_HDMI_HDCP` gate external display blocks.

## Control flow
This file is build-time Kconfig control flow. Selecting display controller or connector options pulls in KMS and required DRM display helpers. DSI and DP options gate include paths and object lists in the Makefile.

## State and persistence
No runtime state. Configuration choices persist in the kernel build and determine which objects, generated headers, and feature paths are compiled.

## Dependencies and integration points
Integrates MSM DRM with DRM core, scheduler, GPUVM, display helpers, panel/bridge helpers, MIPI DSI, DisplayPort AUX/helper code, HDMI helpers, power domains, OPP, NVMEM, and Qualcomm firmware/platform services.

## Risks
The root driver has broad dependency/select impact. `DRM_MSM_GPU_SUDO` intentionally grants CAP_SYS_RAWIO users kernel-level GPU command capability and is unsafe for production. XML validation depends on Python/lxml availability. Default-y display options can increase build surface.

## Test signals
Kconfig dependency resolution across ARCH_QCOM, COMPILE_TEST, and non-Qualcomm builds; minimal GPU-only builds; all display combinations; and validation of developer-only options are useful signals.

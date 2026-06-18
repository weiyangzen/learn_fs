# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.c

## Purpose
This file provides the GFXHUB 1.1 XGMI topology query helper for Vega20, Arcturus, and Aldebaran-class devices. It reads the GFX hub XGMI local-frame-buffer registers and records node count, node id, and segment size in `adev->gmc.xgmi`.

## Important APIs, Types, and Functions
`gfxhub_v1_1_get_xgmi_info(struct amdgpu_device *adev)` is the sole exported function. It uses `RREG32_SOC15`, `REG_GET_FIELD`, and local Aldebaran-specific register/mask definitions for `MC_VM_XGMI_LFB_CNTL` and `MC_VM_XGMI_LFB_SIZE`. The output state is `adev->gmc.xgmi.num_physical_nodes`, `physical_node_id`, and `node_segment_size`.

## Control Flow and State
The function first selects Aldebaran-specific register addresses and masks when `adev->asic_type == CHIP_ALDEBARAN`; otherwise it uses the standard GC 9.2.1 register definitions. It derives `seg_size` by shifting the hardware PF LFB size field by 24, derives `max_region`, then constrains expected physical-node limits by ASIC: 4 nodes for Vega20, 8 for Arcturus, and 16 for Aldebaran. When XGMI appears enabled (`max_region` nonzero) or the GPU is connected to the CPU over XGMI, it writes the derived GMC XGMI fields and returns `-EINVAL` if either the number of nodes or local node id exceeds the generation limit.

## Dependencies and Integration Points
This helper is declared by `gfxhub_v1_1.h` and is used by GMC initialization paths that need XGMI-aware VRAM/GART placement. It depends on `amdgpu.h`, GC 9.2.1 offset/mask headers, and SOC15 register access helpers.

## Risks and Test Signals
The risk is topology mis-detection: an incorrect `node_segment_size` or `physical_node_id` shifts VRAM base calculations and can corrupt multi-GPU address placement. Test signals include XGMI multi-node boot, KFD peer-memory workloads, GPU reset/resume on Vega20/Arcturus/Aldebaran, and validation that unsupported ASICs return `-EINVAL` instead of silently programming invalid topology.

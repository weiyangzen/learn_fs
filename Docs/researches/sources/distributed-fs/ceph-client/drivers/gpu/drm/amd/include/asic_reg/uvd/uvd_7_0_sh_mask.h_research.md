# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_7_0_sh_mask.h

### Purpose
`uvd_7_0_sh_mask.h` is the UVD 7.0 bit-field contract for AMDGPU's Unified Video Decoder MMIO programming. It contains 705 preprocessor constants that describe shifts and masks for power-gating, dynamic power-gating ring-buffer control, JPEG and UDEC address tiling, command mailboxes, LMI cache and VMID registers, ring-buffer controller registers, clock-gating controls, soft reset status, semaphore timeout handling, context IDs, and firmware-authentication status.

### Important APIs, Types, And Functions
There are no C functions or types. The API surface is macro-only: `UVD_*__SHIFT` and `UVD_*_MASK` constants consumed with register read/modify/write helpers. Important groups include `UVD_POWER_STATUS`, `UVD_DPG_RBC_*`, `UVD_JPEG_ADDR_CONFIG`, `UVD_UDEC_*_ADDR_CONFIG`, `UVD_GPCOM_VCPU_*`, `UVD_LMI_*_64BIT_BAR_*`, `UVD_RBC_*`, `UVD_STATUS`, `UVD_SEMA_*`, `UVD_CONTEXT_ID*`, and `UVD_FW_STATUS`.

### Control Flow
This header has no executable control flow. Runtime flow is created in `amdgpu/uvd_v7_0.c`, which includes this file along with the UVD 7.0 offset header and VCE 4.0 register headers. Driver paths use these masks to compose MMIO values for block bring-up, ring setup, command submission, interrupt/status polling, power-gating transitions, reset sequencing, and firmware status checks.

### State, Persistence, And Dependencies
The header persists no state by itself. Its constants define how software interprets persistent hardware state in UVD registers: ring read/write pointers, VMID and 64-bit BAR programming, firmware status bits, semaphore timeout latches, soft-reset bits, power-gating acknowledgement bits, and scratch/context fields. Correct use depends on the matching UVD 7.0 offset header, AMDGPU register access macros, firmware layout, GPU memory-manager address configuration, interrupt handling, and ASIC-specific clock/power sequencing.

### Integration Points
Primary integration is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v7_0.c`. It also intersects with the shared AMDGPU UVD firmware loader, ring scheduler, MMU/GART address tiling setup, power-management code, interrupt sources under `ivsrcid/uvd`, and JPEG/UVD command paths that rely on common register naming.

### Risks
The largest risk is silent hardware misprogramming: a one-bit shift or mask drift can make the driver poll the wrong busy bit, leave the block in reset, corrupt ring pointers, misprogram 64-bit memory addresses, acknowledge the wrong interrupt, or mis-handle firmware authentication failure. Address-configuration masks are especially sensitive because they encode GPU memory tiling topology. Reset and power-gating bits are also risky because they affect ordering and recovery from hangs.

### Test Signals
Useful signals include successful UVD 7.0 firmware load, clean `dmesg` during block init/resume, video decode workloads, JPEG paths when routed through UVD-era blocks, ring write/read pointer progress, GPU reset recovery, runtime suspend/resume, power-gating enable/disable testing, semaphore timeout handling, and checks that firmware `DONE`, `PASS`, `FAIL`, and invalid-image status bits are decoded as expected.

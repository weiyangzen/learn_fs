# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_4_0_default.h

### Purpose
`vce_4_0_default.h` records reset/default values for the VCE 4.0 register map. Its 82 `*_DEFAULT` macros document the expected initial state for VCE decoder, UENC control, LMI/cache, MMSCH virtual-function mailbox, and hardware-version register blocks.

### Important APIs, Types, And Functions
There are no functions or types. The interface is a set of `mmVCE_*_DEFAULT` constants. Most registers default to zero, while notable nonzero defaults include `mmVCE_VCPU_CNTL_DEFAULT` (`ONE_CACHE_SURFACE_EN` set), `mmVCE_SOFT_RESET_DEFAULT`, `mmVCE_RB_ARB_CTRL_DEFAULT`, clock-gating defaults such as `mmVCE_CLOCK_GATING_A_DEFAULT`, `mmVCE_CLOCK_GATING_B_DEFAULT`, `mmVCE_UENC_CLOCK_GATING_DEFAULT`, `mmVCE_UENC_REG_CLOCK_GATING_DEFAULT`, `mmVCE_UENC_CLOCK_GATING_2_DEFAULT`, `mmVCE_LMI_CTRL_DEFAULT`, and `mmVCE_LMI_STATUS_DEFAULT`.

### Control Flow
This file has no control flow. `amdgpu/vce_v4_0.c` and `amdgpu/uvd_v7_0.c` include it with the VCE 4.0 offset and mask headers so code can compare, initialize, or document expected register reset state during block setup and recovery.

### State, Persistence, And Dependencies
The header does not persist software state. It describes hardware reset state and therefore depends on the ASIC specification matching actual silicon. Its usefulness depends on `vce_4_0_offset.h` for register identity and `vce_4_0_sh_mask.h` for field meaning. Defaults that set reset or clock-gating fields are particularly important because init code must clear or override them in the correct order.

### Integration Points
Direct integration is `amdgpu/vce_v4_0.c`, with secondary inclusion in `amdgpu/uvd_v7_0.c` because that generation shares VCE 4.0 encode-related register definitions. It supports diagnostics, initialization assumptions, and reset sequencing in the AMDGPU multimedia stack.

### Risks
Default-value drift can mislead recovery code and debugging even when register addresses are correct. Assuming a documented default after partial reset, runtime power-gating, virtualization, or firmware activity may be wrong. Nonzero clock-gating and soft-reset defaults are high-risk because they affect whether the block is accessible before explicit initialization.

### Test Signals
Useful tests include register dumps immediately after cold boot and after GPU reset, comparison of documented defaults with observed hardware, VCE 4.0 firmware boot, encode workloads, runtime PM transitions, and validation that reset paths do not depend on defaults that firmware or power management may have changed.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_3_0_d.h

### Purpose
`vce_3_0_d.h` maps VCE 3.0 register names to MMIO indices. It extends the VCE 2.x address model with a third ring-buffer register set and VCE 3.0-specific UENC clock-gating and LMI address placement.

### Important APIs, Types, And Functions
This is a macro-only header. Its 46 `mmVCE_*` constants cover `mmVCE_STATUS`, VCPU control/cache registers, soft reset, ring-buffer sets 1, 2, and 3, `mmVCE_RB_ARB_CTRL`, clock-gating registers, UENC DMA/clock controls including `mmVCE_UENC_CLOCK_GATING_2`, system interrupt registers, LMI cache/bar/control/status/VM/swap/misc registers, and LMI cache control.

### Control Flow
No executable control flow exists here. `amdgpu/vce_v3_0.c` and ASIC setup code include the header to perform VCE 3.0 init: reset sequencing, firmware cache setup, multi-ring programming, trap interrupt configuration, clock-gating setup, and status polling.

### State, Persistence, And Dependencies
The file contains no runtime state. It defines addresses for hardware state in VCE registers, especially multi-ring command queues and LMI/VCPU control state. It depends on `vce_3_0_sh_mask.h` for field layout, common AMDGPU MMIO accessors, VCE firmware, and ASIC family code that chooses VCE 3.0 only for compatible chips.

### Integration Points
Direct consumers are `amdgpu/vce_v3_0.c` and platform setup paths such as `vi.c`, which include both the VCE 3.0 address and shift/mask headers. It integrates with the common AMDGPU VCE scheduler, firmware loading, interrupts, clock-gating, and GPU reset paths.

### Risks
VCE 3.0 adds a third ring at offsets `mmVCE_RB_BASE_LO3` through `mmVCE_RB_WPTR3`; omitting or misaddressing it can break multi-session encode scheduling. Address differences in `SYS_INT_*` and LMI registers versus VCE 2.0 can cause lost interrupts or invalid cache/coherency programming if headers are mixed.

### Test Signals
Build VCE 3.0 support, boot supported VI-era hardware, confirm firmware load, run single and multi-ring encode submissions, check all enabled rings advance, verify trap interrupts, and exercise suspend/resume and GPU reset recovery with clock gating enabled.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_1_0_sh_mask.h

### Purpose
`vce_1_0_sh_mask.h` defines the VCE 1.0 field layout for the register addresses in `vce_1_0_d.h`. Its 83 macros provide masks and shifts for VCE status, VCPU control, VCPU cache offset/size windows, two ring-buffer register sets, soft-reset bits, trap interrupts, UENC DMA clock forcing, LMI cache/coherency/swap behavior, dynamic clock mode, and firmware status bits.

### Important APIs, Types, And Functions
The interface is macro-only. Important fields include `VCE_STATUS__JOB_BUSY`, `VCE_STATUS__VCPU_REPORT`, `VCE_STATUS__UENC_BUSY`, `VCE_VCPU_CNTL__CLK_EN`, `VCE_VCPU_CNTL__RBBM_SOFT_RESET`, `VCE_RB_*__RB_*`, `VCE_SOFT_RESET__ECPU_SOFT_RESET`, `VCE_SOFT_RESET__FME_SOFT_RESET`, `VCE_SYS_INT_*__VCE_SYS_INT_TRAP_INTERRUPT_*`, `VCE_LMI_CTRL__VCPU_DATA_COHERENCY_EN`, and `VCE_FW_REG_STATUS__BUSY/PASS/DONE`.

### Control Flow
There is no executable flow. VCE 1.0 driver paths use the masks when building read/modify/write values: enable the VCPU clock, configure cache offsets and sizes, place ring buffers on aligned addresses, enable or acknowledge trap interrupts, poll busy and firmware status fields, and toggle reset or clock-gating fields.

### State, Persistence, And Dependencies
The header itself is stateless, but it defines interpretation of persistent hardware register state. It depends on the address macros in `vce_1_0_d.h` and the AMDGPU register helpers that apply masks and shifts. The suffix convention is mostly `__FIELD_MASK` and `__FIELD__SHIFT`, with one `VCE_CLOCK_GATING_A__CGC_DYN_CLOCK_MODE_SHIFT` spelling that lacks the double underscore before `SHIFT`, so consumers must use exact macro names rather than generated assumptions.

### Integration Points
The direct integration point is `amdgpu/vce_v1_0.c`. It indirectly participates in firmware boot, ring scheduling, GPU reset, power management, and interrupt processing through common AMDGPU VCE helpers.

### Risks
Field drift can be hard to diagnose because the driver may still compile but write invalid bit patterns. Ring pointer masks require aligned low-address bits to be zero; cache offset and size masks constrain firmware memory layout; interrupt bit mistakes can lose completions; and incorrect firmware status bits can report failed authentication as success or keep the driver waiting indefinitely.

### Test Signals
Signals include VCE firmware reaching `DONE` and `PASS`, encode ring submission completing without timeout, trap interrupts being acknowledged exactly once, reset paths clearing busy bits, clock-gating changes not hanging the encoder, and register traces showing ring base/size/pointer values masked to expected alignment.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_2_0_d.h

### Purpose
`vce_2_0_d.h` is the VCE 2.0 register-address map. It keeps the same broad programming model as VCE 1.0 but updates the register indices for the second-generation block and adds VCE 2.x-specific controls such as `mmVCE_CGTT_CLK_OVERRIDE`, `mmVCE_LMI_SWAP_CNTL2`, and `mmVCE_LMI_SWAP_CNTL3`.

### Important APIs, Types, And Functions
There are no functions or types. The public surface is 41 `mmVCE_*` address macros for status, VCPU control, three VCPU cache segments, soft reset, two ring-buffer register sets, ring arbitration, clock gating, UENC DMA/clock-gating control, system interrupt registers, LMI cache/bar/control/status/VM/swap registers, and miscellaneous LMI control.

### Control Flow
No code executes in this header. `amdgpu/vce_v2_0.c` includes it and performs the runtime sequencing: firmware load, VCPU cache setup, ring base and pointer programming, interrupt enable/acknowledge, reset, clock-gating setup, and LMI coherency/swap configuration.

### State, Persistence, And Dependencies
The constants identify hardware registers but store no software state. They depend on matching VCE 2.0 field macros in `vce_2_0_sh_mask.h`, the AMDGPU MMIO accessor layer, the VCE firmware image, and GPU family setup that selects VCE 2.0 for the correct ASICs. Several VCE 2.0 LMI and interrupt addresses differ from VCE 1.0, so cross-generation reuse is unsafe unless gated by the correct header.

### Integration Points
Direct consumer: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v2_0.c`. The header integrates with common VCE ring management, firmware loading, IRQ handling, power/clock gating, and older ASIC initialization that selects the VCE 2.0 IP implementation.

### Risks
The main risk is address skew between VCE generations. Accidentally using VCE 1.0 or VCE 3.0 addresses against VCE 2.0 hardware can corrupt unrelated registers, especially for interrupt and LMI blocks whose offsets moved substantially. Ring-buffer addresses and reset registers are high-impact because mistakes can hang GPU scheduling or make reset recovery ineffective.

### Test Signals
Compile coverage for `vce_v2_0.c`, successful firmware load on VCE 2.0 hardware, ring tests that advance read/write pointers, encode workloads, trap interrupt delivery, clock-gating toggles, and reset/suspend/resume tests are the best validation signals.

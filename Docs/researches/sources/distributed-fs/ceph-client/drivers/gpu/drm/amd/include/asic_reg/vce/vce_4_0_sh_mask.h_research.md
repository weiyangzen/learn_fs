# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_4_0_sh_mask.h

### Purpose
`vce_4_0_sh_mask.h` is the VCE 4.0 field-layout definition. It contains 369 shift and mask macros for status, VCPU control, nine cache windows, soft-reset fanout, ring buffers, arbitration, clock-gating, interrupts, UENC sub-block clock controls, LMI/cache/coherency/swap policy, 64-bit and 40-bit cache BAR arrays, MMSCH virtual-function registers, and hardware-version reporting.

### Important APIs, Types, And Functions
The interface is macro-only. Important field groups include `VCE_STATUS__*`, `VCE_VCPU_CNTL__CLK_EN/ED_ENABLE/RBBM_SOFT_RESET/ONE_CACHE_SURFACE_EN`, `VCE_VCPU_CACHE_OFFSET0..8`, `VCE_VCPU_CACHE_SIZE0..8`, extensive `VCE_SOFT_RESET__*` bits, `VCE_RB_*` and `VCE_RB_*3`, `VCE_CLOCK_GATING_A/B__*`, `VCE_UENC_CLOCK_GATING*__*`, `VCE_LMI_CTRL*__*`, `VCE_LMI_SWAP_CNTL*__*`, `VCE_LMI_VCPU_CACHE_{64,40}BIT_BAR*`, `VCE_MMSCH_VF_*`, and `VCE_HW_VERSION__*`.

### Control Flow
The header has no executable control flow. VCE 4.0 runtime flow uses it to build read/modify/write values for block reset, VCPU enablement, firmware cache aperture setup, ring setup, clock-gating policy, interrupt enable/ack/status handling, LMI coherency and urgent-traffic policy, virtual-function mailbox setup, and hardware version decoding.

### State, Persistence, And Dependencies
No state is stored in the header. It defines interpretation of VCE 4.0 hardware state and must match `vce_4_0_offset.h`. The field definitions also depend on reset defaults in `vce_4_0_default.h`, AMDGPU SOC15 register helpers, firmware expectations, and power-management sequencing. Several fields have full-width masks, so callers must still enforce semantic ranges such as address alignment, VMID limits, and valid clock-gating combinations.

### Integration Points
The direct consumer is `amdgpu/vce_v4_0.c`; `amdgpu/uvd_v7_0.c` also includes it for shared multimedia register programming. Integration crosses common VCE firmware/ring code, SOC15 IP discovery, interrupt source headers, GPU reset, runtime PM, and SR-IOV/MMSCH command paths.

### Risks
This is a high-blast-radius hardware contract. Incorrect soft-reset bits can reset the wrong sub-block or fail to recover a hung encoder. Clock-gating masks span many submodules and can create hangs if force-on/off bits are wrong. LMI swap and coherency bits affect memory ordering and byte interpretation. MMSCH VF address/size/mailbox fields affect virtualization. Cache BAR masks and low-address shifts impose alignment requirements that the header cannot enforce.

### Test Signals
Test VCE 4.0 firmware boot, encode workloads, multi-ring scheduling, reset recovery, clock-gating on/off paths, runtime suspend/resume, register dumps of cache BAR and ring alignment, interrupt status/ack tests, SR-IOV or MMSCH mailbox operation where available, and hardware-version decoding.

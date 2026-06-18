# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_4_0_offset.h

### Purpose
`vce_4_0_offset.h` is the VCE 4.0 register-address and base-index map. It defines 163 macros: one `mmVCE_*` offset and one `mmVCE_*_BASE_IDX` companion for each register. The map is organized by address blocks `vce0_vce_dec`, `vce0_ctl_dec`, `vce0_vce_sclk_dec`, `vce0_mmsch_dec`, and `vce0_vce_rb_pg_dec`.

### Important APIs, Types, And Functions
The macro API covers status, VCPU control, nine VCPU cache offset/size slots, soft reset, ring-buffer sets 1/2/3, ring arbitration, clock-gating registers, system interrupt registers, UENC clock-gating registers, LMI cache/bar/control/status/VM/swap registers, 64-bit and 40-bit VCPU cache BAR arrays, MMSCH virtual-function VMID/context/GPCOM/mailbox registers, and `mmVCE_HW_VERSION`.

### Control Flow
There is no executable flow. Runtime code pairs each `mmVCE_*` offset with the base index when using SOC15-style register helpers. VCE 4.0 driver flow uses this map to initialize firmware cache apertures, program rings, set clock/reset/LMI state, configure interrupts, communicate with MMSCH virtual-function paths, and read hardware identity.

### State, Persistence, And Dependencies
The header is stateless. It defines where hardware state lives in the MMIO aperture and depends on `vce_4_0_sh_mask.h` for field layout and `vce_4_0_default.h` for reset-state documentation. All registers use base index 0 in this file, so consumers relying on base-index-aware accessors should preserve that pairing.

### Integration Points
Direct consumer: `amdgpu/vce_v4_0.c`. It is also included by `amdgpu/uvd_v7_0.c`, and VCE 4.0 IP discovery can be selected through `soc15.c` or `amdgpu_discovery.c`. The map integrates with SOC15 register access macros, firmware loading, multimedia scheduler rings, IRQ source definitions, power management, and virtualization/MMSCH support.

### Risks
VCE 4.0 offsets are not numerically compatible with older VCE 1/2/3 `*_d.h` maps; mixing generations would target the wrong MMIO pages. The cache-slot expansion from three to nine slots and the additional 64-bit BAR arrays increase the chance of off-by-one programming. MMSCH mailbox and VF context registers are high-risk in virtualized setups because wrong addresses can break guest/host command handoff.

### Test Signals
Validate by compiling SOC15 VCE 4.0 paths, booting matching hardware, checking register reads through base-index macros, loading firmware, submitting encode rings, exercising power gating and reset, testing SR-IOV/MMSCH mailbox paths when available, and comparing hardware-version reads with expected ASIC data.

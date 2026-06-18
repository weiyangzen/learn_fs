# subset-b-003441 Research

Grouped source research for subset B work item `subset-b-003441`. Each source file section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_7_0_sh_mask.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_7_0_sh_mask.h

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_7_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_1_0_d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_1_0_d.h

### Purpose
`vce_1_0_d.h` maps VCE 1.0 register names to MMIO register indices. It is the address half of the VCE 1.0 register contract used by the early AMD video encode driver code. The 42 macros cover status, VCPU control and cache windows, ring-buffer base/size/read/write pointers for two rings, arbitration, clock gating, soft reset, interrupt status/acknowledge/enable, local-memory-interface control, swap controls, and firmware status/start-key registers.

### Important APIs, Types, And Functions
There are no functions or C types. The exported interface is the `mmVCE_*` macro set, including `mmVCE_STATUS`, `mmVCE_VCPU_CNTL`, `mmVCE_VCPU_CACHE_OFFSET*`, `mmVCE_VCPU_CACHE_SIZE*`, `mmVCE_RB_BASE_LO*`, `mmVCE_RB_BASE_HI*`, `mmVCE_RB_SIZE*`, `mmVCE_RB_RPTR*`, `mmVCE_RB_WPTR*`, `mmVCE_SYS_INT_*`, `mmVCE_LMI_*`, `mmVCE_FW_REG_STATUS`, `mmVCE_LMI_FW_PERIODIC_CTRL`, and `mmVCE_LMI_FW_START_KEYSEL`.

### Control Flow
The header has no runtime flow. `amdgpu/vce_v1_0.c` includes it and uses the addresses with AMDGPU MMIO helpers during VCE firmware setup, cache programming, ring initialization, interrupt handling, clock-gating configuration, and reset/status polling.

### State, Persistence, And Dependencies
No software state is stored here. The constants identify hardware state owned by the VCE block: VCPU firmware state, ring buffers, interrupt latches, LMI cache behavior, memory byte-lane swap policy, and clock/reset controls. Correctness depends on matching `vce_1_0_sh_mask.h`, VCE firmware expectations, ASIC register aperture routing, and the AMDGPU ring and IRQ frameworks.

### Integration Points
The direct consumer is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v1_0.c`, with higher-level selection from older ASIC setup files such as `si.c`. It integrates with the common AMDGPU VCE code that allocates firmware buffers and rings, emits commands, and handles trap interrupts.

### Risks
Wrong register indices can write valid-looking values into unrelated MMIO locations. High-risk addresses are ring base pointers, interrupt ack/status aliases, soft reset, VCPU cache configuration, and firmware status registers because errors here can cause hangs, lost interrupts, or failed firmware boot. VCE 1.0 also has generation-specific firmware registers that do not appear in the same form in later VCE 2.x/3.x headers.

### Test Signals
Test by building legacy VCE 1.0 support, booting a matching SI-era GPU, loading VCE firmware, submitting encode rings, checking interrupt delivery, exercising reset recovery, and verifying suspend/resume leaves ring pointers, cache programming, and firmware status sane.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_1_0_d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_1_0_sh_mask.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_1_0_sh_mask.h

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_1_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_2_0_d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_2_0_d.h

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_2_0_d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_2_0_sh_mask.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_2_0_sh_mask.h

### Purpose
`vce_2_0_sh_mask.h` is the VCE 2.0 field-definition companion to `vce_2_0_d.h`. It defines 77 masks and shifts used to program status, VCPU clock/reset, firmware cache segments, two ring buffers, UENC DMA clocks, trap interrupts, LMI cache/coherency, and memory-client byte-swap behavior.

### Important APIs, Types, And Functions
The exported API is preprocessor constants only. Important fields include `VCE_STATUS__JOB_BUSY`, `VCE_STATUS__VCPU_REPORT`, `VCE_STATUS__UENC_BUSY`, `VCE_VCPU_CNTL__CLK_EN`, `VCE_VCPU_CNTL__RBBM_SOFT_RESET`, `VCE_RB_BASE_*`, `VCE_RB_SIZE*`, `VCE_RB_RPTR*`, `VCE_RB_WPTR*`, `VCE_SYS_INT_*__VCE_SYS_INT_TRAP_INTERRUPT_*`, `VCE_LMI_SWAP_CNTL{,1,2,3}`, `VCE_LMI_CTRL__VCPU_DATA_COHERENCY_EN`, and `VCE_LMI_CACHE_CTRL__VCPU_EN`.

### Control Flow
This header has no direct flow. Runtime code uses these masks while bringing the encoder up: configure cache windows, set ring addresses and sizes, enable VCPU and LMI cache access, set swap/coherency policy, force DMA clocks when needed, enable trap interrupts, and poll busy fields.

### State, Persistence, And Dependencies
No data persists in the header. The hardware state it describes includes ring-buffer state, interrupt latches, VCPU state, LMI cache enablement, and byte-swapping modes. It depends on exact pairing with the VCE 2.0 address header and on common AMDGPU helpers for masked register writes. Compared with VCE 1.0, this file adds `LMI_SWAP_CNTL2/3` fields, so generation-aware code must not assume identical swap-register layouts.

### Integration Points
The main consumer is `amdgpu/vce_v2_0.c`, with indirect participation in firmware loading, ring scheduling, interrupt handling, clock gating, memory coherency, and GPU reset paths.

### Risks
Mask errors can cause malformed ring programming, incorrect endian/byte-swap behavior, lost trap interrupts, or stale VCPU cache contents. Since the ring base low fields mask off low six bits and pointers/sizes use low-nibble alignment, callers must pass correctly aligned GPU addresses and sizes before applying these fields.

### Test Signals
Validate with VCE 2.0 firmware boot, encode command submission, ring pointer progress, interrupt enable/ack/clear behavior, endian/swap-sensitive buffer tests, runtime PM, and GPU reset recovery. Register dumps before and after init should show fields limited to the documented masks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_2_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_3_0_d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_3_0_d.h

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_3_0_d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_3_0_sh_mask.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_3_0_sh_mask.h

### Purpose
`vce_3_0_sh_mask.h` defines VCE 3.0 bit fields for the address map in `vce_3_0_d.h`. It carries forward the VCE 2.0 programming model and adds fields for VCE configuration/instance reporting, ring arbitration clock override, and the third ring-buffer register set.

### Important APIs, Types, And Functions
The header exports 93 mask/shift macros. Important groups are `VCE_STATUS__JOB_BUSY/VCPU_REPORT/UENC_BUSY/VCE_CONFIGURATION/VCE_INSTANCE_ID`, `VCE_VCPU_CNTL__CLK_EN/RBBM_SOFT_RESET`, cache offset/size fields, `VCE_RB_*`, `VCE_RB_*3`, `VCE_RB_ARB_CTRL__VCE_CGTT_OVERRIDE`, `VCE_UENC_DMA_DCLK_CTRL`, trap interrupt fields, `VCE_LMI_SWAP_CNTL{,1,2,3}`, `VCE_LMI_CTRL__VCPU_DATA_COHERENCY_EN`, and `VCE_LMI_CACHE_CTRL__VCPU_EN`.

### Control Flow
The header is declarative. Driver code uses the macros during VCE 3.0 bring-up and operation: decode status/configuration fields, program up to three rings, enable VCPU and cache access, set LMI swap/coherency, control clock-gating override, enable/acknowledge trap interrupts, and poll busy state.

### State, Persistence, And Dependencies
There is no state in the file. The described hardware state includes status/configuration identifiers, ring pointers, cache aperture layout, clock-gating override state, interrupt latches, and LMI coherency behavior. It depends on the matching VCE 3.0 address map and AMDGPU helpers that apply masks consistently.

### Integration Points
Direct consumers are `amdgpu/vce_v3_0.c` and `vi.c`. The fields also support common VCE firmware loading, scheduler ring control, IRQ handling, clock/power management, and reset recovery.

### Risks
The main risks are multi-ring misprogramming, incorrect status interpretation for VCE instance/configuration, stale cache or coherency programming, and trap interrupt mishandling. Because the masks for base and pointer fields encode alignment constraints, callers must not assume arbitrary byte granularity.

### Test Signals
Good validation includes VCE 3.0 firmware boot, concurrent encode-session tests that exercise ring 1/2/3 paths, IRQ tests, reset recovery, clock-gating override toggles, and register dumps confirming `VCE_CONFIGURATION` and `VCE_INSTANCE_ID` decode correctly.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_3_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_4_0_default.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_4_0_default.h

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_4_0_default.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_4_0_offset.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_4_0_offset.h

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_4_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_4_0_sh_mask.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_4_0_sh_mask.h

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_4_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_1_0_offset.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_1_0_offset.h

### Purpose
`vcn_1_0_offset.h` maps VCN 1.0/UVD-style multimedia registers to offsets and base indices. It defines 381 macros across UVD power-gating, dynamic power gating, scratch, JPEG, command/semaphore, SUVD clock-gating, LMI cache/BAR, ring-buffer, context, status, and semaphore-timeout registers. It is the address companion to VCN 1.0 shift/mask definitions.

### Important APIs, Types, And Functions
There are no functions or C types. The macro API includes `mmUVD_PGFSM_*`, `mmUVD_POWER_STATUS`, `mmCC_UVD_HARVESTING`, `mmUVD_DPG_*`, scratch registers, MIF address-config registers, JPEG ring and GPCOM registers, semaphore and VCPU command registers, UDEC address-config registers, SUVD/JPEG/UVD clock-gating registers, 64-bit BAR registers, multiple ring-buffer sets, context IDs, RBC control/status registers, and base-index companions for each address. Most entries use `BASE_IDX` 1.

### Control Flow
The file is declarative. `amdgpu/vcn_v1_0.c` and `amdgpu/jpeg_v1_0.c` use these offsets with SOC15-style MMIO helpers during VCN/JPEG initialization, firmware setup, ring-buffer programming, power-gating, command submission, interrupt/status polling, semaphore timeout control, and reset recovery.

### State, Persistence, And Dependencies
No state is persisted in the header. The constants point to hardware state in the VCN 1.0 block: firmware scratch and command registers, ring-buffer pointers, VMID and BAR programming, power-gating state, JPEG ring state, semaphore timeout latches, context identifiers, and clock-gating status. It depends on `vcn_1_0_sh_mask.h`, AMDGPU SOC15 register accessors, firmware layout, memory address-configuration helpers, and interrupt source definitions.

### Integration Points
Direct consumers are `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v1_0.c` and `amdgpu/jpeg_v1_0.c`. It integrates with common VCN firmware handling, JPEG ring support, power management, GPU reset, scheduler rings, VMID/GART setup, and IP discovery.

### Risks
Wrong offsets or base indices can misroute MMIO accesses. Base-index mismatches are especially risky because the same numeric offset can mean different physical register blocks. Ring and BAR addresses control DMA-visible memory, so errors can corrupt command streams or firmware cache mappings. JPEG and VCN share many UVD-prefixed names, making accidental use of older UVD headers a realistic maintenance risk.

### Test Signals
Validate with VCN 1.0 firmware load, video decode, JPEG decode/encode paths supported by the driver, ring pointer progress for all active rings, power-gating and DPG pause/resume, semaphore timeout behavior, GPU reset, runtime suspend/resume, and register traces confirming `BASE_IDX` 1 accessors reach expected hardware.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_1_0_offset.h -->

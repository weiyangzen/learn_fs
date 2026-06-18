# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_3_0_sh_mask.h

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

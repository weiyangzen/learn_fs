# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vce/vce_2_0_sh_mask.h

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

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_1_0_offset.h

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

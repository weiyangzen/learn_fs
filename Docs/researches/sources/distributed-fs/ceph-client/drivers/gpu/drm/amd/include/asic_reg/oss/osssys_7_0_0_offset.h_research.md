# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_7_0_0_offset.h

## Purpose

`osssys_7_0_0_offset.h` is a generated AMDGPU ASIC register offset map for the OSSSYS 7.0.0 block, specifically the `osssys_osssysdec` address block with documented base address `0x4280`. It does not implement executable logic. Its job is to export stable preprocessor symbols named `reg...` plus matching `..._BASE_IDX` constants so driver code can compute MMIO register addresses with SOC15 helpers.

The covered hardware surface is the OSS interrupt handler and related OSS/SEM control window. The register families include per-VMID PASID lookup tables, interrupt cookie registers, IH ring buffer controls and pointers, write-pointer writeback addresses, doorbell read-pointer controls, retry CAM and interrupt-rate controls, status and performance counters, DSM match controls, SR-IOV/VF status and violation logging, MSI storm controls, SEM mailbox registers, active-function and virtualization controls, client configuration/remapping, interrupt drop filtering, and MMHUB control.

## Important APIs, Types, And Macros

This header exports only macros. The important exported groups are:

- `regIH_VMID_0_LUT` through `regIH_VMID_15_LUT` at offsets `0x0000` through `0x000f`, and `regIH_VMID_0_LUT_MM` through `regIH_VMID_15_LUT_MM` at `0x0010` through `0x001f`. These are contiguous arrays used by GMC/KFD code to map VMIDs to PASIDs for GFXHUB and MMHUB paths.
- `regIH_COOKIE_0` through `regIH_COOKIE_7` at `0x0020` through `0x0027`, defining the interrupt vector metadata layout together with the sibling mask header.
- Ring 0 registers `regIH_RB_CNTL`, `regIH_RB_RPTR`, `regIH_RB_WPTR`, `regIH_RB_BASE`, `regIH_RB_BASE_HI`, `regIH_RB_WPTR_ADDR_HI`, `regIH_RB_WPTR_ADDR_LO`, and `regIH_DOORBELL_RPTR` in the `0x0080` range.
- Ring 1 equivalents `regIH_RB_CNTL_RING1`, `regIH_RB_RPTR_RING1`, `regIH_RB_WPTR_RING1`, `regIH_RB_BASE_RING1`, `regIH_RB_BASE_HI_RING1`, and `regIH_DOORBELL_RPTR_RING1` in the `0x008c` range.
- Global IH control/status registers such as `regIH_CNTL`, `regIH_CLK_CTRL`, `regIH_LIMIT_INT_RATE_CNTL`, `regIH_RETRY_INT_CAM_CNTL`, `regIH_MEM_POWER_CTRL`, `regIH_MEM_POWER_CTRL2`, `regIH_CNTL2`, `regIH_STATUS`, and performance counter registers.
- Diagnostics and virtualization registers such as `regIH_VF_RB_STATUS*`, `regIH_RB_STATUS`, `regIH_INT_FLOOD_*`, `regIH_INT_FLAGS`, `regIH_CLIENT_CREDIT_ERROR`, `regIH_GPU_IOV_VIOLATION_LOG*`, `regIH_COOKIE_REC_VIOLATION_LOG`, `regIH_CREDIT_STATUS`, and `regIH_MMHUB_ERROR`.
- SEM mailbox symbols `regSEM_MAILBOX`, `regSEM_MAILBOX_CLEAR`, and `regSEM_REGISTER_LAST_PART2`.
- Client and virtualization configuration symbols in the `0x0180` to `0x01a8` range, including `regIH_ACTIVE_FCN_ID`, `regIH_VIRT_RESET_REQ`, `regIH_CLIENT_CFG*`, `regIH_RING1_CLIENT_CFG_*`, `regIH_CID_REMAP_*`, `regIH_CHICKEN`, interrupt drop match registers, and `regIH_MMHUB_CNTL`.

Every register has a matching `*_BASE_IDX` macro set to `0`. That value is consumed by the SOC15 register-address macro layer to select the register-instance base index.

## Control Flow And Runtime Use

There is no C control flow in the file. Runtime flow is introduced by consumers that include it and pass its offsets to register access helpers. Direct consumers found in this tree include:

- `amdgpu/ih_v7_0.c`, which includes this header and `osssys_7_0_0_sh_mask.h`. It initializes `struct amdgpu_ih_regs` with `SOC15_REG_OFFSET(OSSSYS, 0, regIH_RB_...)`, configures ring buffer base/pointer/control registers, toggles interrupt enable fields, sets doorbell read-pointer registers, and programs `regIH_MSI_STORM_CTRL`.
- `amdgpu/gmc_v12_0.c`, which includes this header and uses `regIH_VMID_0_LUT + vmid` and `regIH_VMID_0_LUT_MM + vmid` to read and emit VMID-to-PASID mappings during TLB invalidation paths.

The typical flow is: include the generated offset header, compute an absolute register address with `SOC15_REG_OFFSET(OSSSYS, instance, regNAME)`, then access it with `RREG32`, `WREG32`, `RREG32_SOC15`, `WREG32_SOC15`, or ring-emitted write helpers. Bit-level values are formed with the matching `osssys_7_0_0_sh_mask.h` field macros and generic helpers such as `REG_SET_FIELD`.

## State And Persistence Behavior

The header itself is stateless and has no persistence. The symbols refer to hardware registers that hold live device state:

- IH ring buffer state persists in GPU-visible memory and MMIO registers until reprogrammed, reset, or power-managed by the device.
- VMID/PASID LUT entries are mutable runtime mappings used by GPUVM and KFD/HSA paths.
- Doorbell and write-pointer writeback registers link CPU/GPU memory addresses and doorbell indices to interrupt-ring consumption.
- Status, overflow, flood, violation, credit, and last-interrupt registers expose transient or sticky diagnostic state that driver code may clear or re-arm through the paired control fields.

Because these are raw offsets, persistence semantics are determined by the hardware block and by callers such as IH/GMC initialization, suspend/resume, reset, and SR-IOV virtualization paths.

## Dependencies And Integration Points

This generated header depends on the AMDGPU register macro conventions rather than C types. Integration points include:

- `soc15_common.h` and the SOC15 address-construction macros that combine the OSSSYS hardware block, instance, register offset, and base index.
- `amdgpu_ih` code that maps ring register offsets into `struct amdgpu_ih_regs` and programs the interrupt handler.
- GMC/KFD VM code that depends on the VMID LUT offsets being contiguous so `regIH_VMID_0_LUT + vmid` is valid for VMIDs 0-15.
- SR-IOV PSP-mediated paths where some IH register writes are routed through PSP register IDs instead of direct MMIO writes; the same offsets still define which logical register is being manipulated.
- The sibling mask header, which defines the field layout for the offset names exported here.

## Risks

The main risk is version drift. These offsets are a hardware ABI, so a wrong generated value can send the driver to the wrong MMIO location. That is especially risky for IH ring base, pointer, doorbell, and enable registers because mistakes can disable interrupts, corrupt interrupt-ring state, or break resume/reset.

The VMID LUT arrays rely on contiguous offsets. If future hardware adds indirection or changes layout without matching caller changes, expressions such as `regIH_VMID_0_LUT + vmid` can read or write the wrong mapping. This is visible in OSSSYS 7.1.0, where a new `regIH_VMID_LUT_INDEX` register is introduced in the offset header and `gmc_v12_1.c` selects a LUT slice before reading the VMID table.

Another risk is sharing this 7.0.0 header with 7.1.0 paths. `ih_v7_0.c` uses this header but carries local `*_V7_1` offset defines for a few moved registers, showing that the register window changed between versions. New 7.1-specific usage should prefer the 7.1 offset header or be very explicit about compatibility.

## Test Signals

Useful validation signals include:

- Build coverage of `amdgpu/ih_v7_0.c` and `amdgpu/gmc_v12_0.c`, proving the generated macro names match call-site expectations.
- Boot/probe logs showing IH ring initialization succeeds, no `PSP program IH_RB_CNTL failed` errors occur, and interrupts are delivered after enabling ring 0/ring 1.
- Runtime checks that VMID/PASID mappings can be written and read back for VMIDs 1-15 via the GMC paths.
- Suspend/resume and GPU reset tests that verify IH ring bases, writeback addresses, pointers, and doorbells are restored correctly.
- SR-IOV VF tests covering indirect IH register programming through PSP and checking VF ring status/overflow diagnostics.
- Interrupt storm/drop tests or fault-injection traces that exercise `regIH_MSI_STORM_CTRL`, flood status, and drop-match diagnostics without unexpected interrupt loss.

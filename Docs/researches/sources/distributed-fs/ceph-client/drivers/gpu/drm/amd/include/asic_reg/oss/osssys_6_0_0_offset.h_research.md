# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_6_0_0_offset.h

## Purpose

`osssys_6_0_0_offset.h` is a generated AMDGPU ASIC register address contract for the OSSSYS 6.0.0 block. It maps symbolic register names to register offsets relative to the OSSSYS base address noted in the file (`0x4280`) and gives every listed register a `BASE_IDX` value of `0`.

This header is the address-side partner to `oss/osssys_6_0_0_sh_mask.h`. Runtime code combines `reg...` macros from this file with field masks/shifts from the sh/mask file through SOC15 helpers. It is used by GFX11-era and later AMDGPU paths such as `amdgpu/ih_v6_0.c`, `amdgpu/ih_v7_0.c`, `amdgpu/gmc_v11_0.c`, and `amdgpu/amdgpu_amdkfd_gfx_v11.c`.

## Important APIs, Types, and Definitions

The file exports only preprocessor macros:

- `regIH_VMID_0_LUT` through `regIH_VMID_15_LUT`, contiguous offsets `0x0000` through `0x000f`, and matching `regIH_VMID_*_LUT_MM` offsets `0x0010` through `0x001f`.
- `regIH_COOKIE_0` through `regIH_COOKIE_7`, offsets `0x0020` through `0x0027`, plus `regIH_REGISTER_LAST_PART0` at `0x003f`.
- Primary IH ring registers: `regIH_RB_CNTL`, `regIH_RB_BASE`, `regIH_RB_BASE_HI`, `regIH_RB_RPTR`, `regIH_RB_WPTR`, `regIH_RB_WPTR_ADDR_HI`, `regIH_RB_WPTR_ADDR_LO`, `regIH_DOORBELL_RPTR`, and `regIH_DOORBELL_RETRY_CAM`.
- Ring1 IH registers: `regIH_RB_CNTL_RING1`, `regIH_RB_BASE_RING1`, `regIH_RB_BASE_HI_RING1`, `regIH_RB_RPTR_RING1`, `regIH_RB_WPTR_RING1`, and `regIH_DOORBELL_RPTR_RING1`.
- Global IH control/status/perf/diagnostic registers: `regIH_RETRY_CAM_ACK`, `regIH_VERSION`, `regIH_CNTL`, `regIH_CNTL2`, `regIH_STATUS`, `regIH_PERFMON_CNTL`, `regIH_PERFCOUNTER*_RESULT`, DSM match registers, limit-rate control, VF ring status, ring status, flood/storm controls, clock control, interrupt flags, last interrupt info, scratch, credit/error/status, MMHUB error, cookie-recognition violation log, memory power controls, retry CAM control, MSI storm index/data, and register-last sentinels.
- SEM-facing registers are much smaller in this 6.0.0 offset file than in older mask files: `regSEM_MAILBOX`, `regSEM_MAILBOX_CLEAR`, and `regSEM_REGISTER_LAST_PART2`.
- IH client configuration/remap/drop registers: `regIH_CLIENT_CFG`, `regIH_RING1_CLIENT_CFG_INDEX`, `regIH_RING1_CLIENT_CFG_DATA`, `regIH_CLIENT_CFG_INDEX`, `regIH_CLIENT_CFG_DATA`, `regIH_CID_REMAP_INDEX`, `regIH_CID_REMAP_DATA`, `regIH_CHICKEN`, `regIH_INT_DROP_CNTL`, `regIH_INT_DROP_MATCH_VALUE*`, `regIH_INT_DROP_MATCH_MASK*`, and `regIH_REGISTER_LAST_PART1`.

Every register also has a matching `reg..._BASE_IDX` macro, always `0`, indicating the base index passed to SOC15 address construction for this block.

## Control Flow

This header has no executable control flow. In consumers it controls which MMIO address is touched:

- `ih_v6_0_init_register_offset()` maps `adev->irq.ih` and `adev->irq.ih1` register slots to `SOC15_REG_OFFSET(OSSSYS, 0, regIH_...)` values. Unlike OSSSYS 5.0.0/Navi10, the comment states ring2 is removed and only ring0/ring1 are available.
- `ih_v6_0_enable_ring()` writes ring base, base high, read/write pointers, writeback address, and doorbell register addresses selected from this header.
- `ih_v6_0_irq_init()` uses `regIH_STORM_CLIENT_LIST_CNTL`, `regIH_INT_FLOOD_CNTL`, `regIH_MSI_STORM_CTRL`, `regIH_RING1_CLIENT_CFG_INDEX`, and `regIH_RING1_CLIENT_CFG_DATA` to configure storm handling and dGPU ring1 redirection.
- `force_update_wptr_for_self_int()` reads/writes `regIH_CNTL2` and `regIH_RB_CNTL_RING1` to force write pointer propagation for self interrupts.
- `gmc_v11_0.c` reads or writes `regIH_VMID_0_LUT + vmid` and `regIH_VMID_0_LUT_MM + vmid` for PASID lookup and VMID mapping.
- `amdgpu_amdkfd_gfx_v11.c` writes the `regIH_VMID_0_LUT + vmid` address when KFD maps a process PASID to an interrupt VMID.

Since the file supplies constants, the build has no branching here; the runtime branch decisions live in the IH/GMC/KFD source that selects which register macro to use.

## State and Persistence Behavior

The header itself is stateless. The state represented by these offsets lives in GPU registers and is re-established during device load, resume, reset, and interrupt subsystem initialization.

Important state domains addressed by the file are:

- VMID/PASID attribution tables for both regular and MMHUB-related interrupt paths.
- IH ring0 and ring1 buffer base addresses, write/read pointers, write pointer writeback addresses, control words, and doorbell read-pointer controls.
- IH global control, status, retry-CAM, performance counter, clock, memory-power, flood, storm, drop, and diagnostic registers.
- Ring1 client redirection state used to steer selected interrupts to the second IH ring on dGPU configurations.
- Client configuration and client-ID remap tables used by firmware/driver integration paths.
- Minimal SEM mailbox offsets used for OSSSYS 6.0.0 semaphore mailbox interaction.

Register state can persist until explicitly overwritten by the driver or reset by hardware. Consumers must pair these offsets with correct field definitions from the same IP generation; using the right address with the wrong field mask can still corrupt state.

## Dependencies and Integration Points

This file has no `#include` dependencies. Its effective dependencies are:

- `oss/osssys_6_0_0_sh_mask.h` for field layouts of the registers named here.
- SOC15 address helpers such as `SOC15_REG_OFFSET(OSSSYS, instance, reg...)`.
- MMIO helpers `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, and related no-KIQ variants after offsets are stored in `amdgpu_ih_regs`.
- IH v6/v7 driver code that assigns offsets into `amdgpu_ih_regs`, programs ring buffers, acknowledges overflow, and configures storm controls.
- KFD PASID mapping for GFX11, which uses the VMID LUT offsets to keep IH attribution aligned with process VMIDs.
- GMC v11 fault handling, which reads the same LUT offsets to recover PASIDs for VM fault processing.
- PSP/SR-IOV register programming paths, because some addresses are written indirectly through PSP register IDs rather than direct MMIO when running as a virtual function.

The file is also implicitly tied to the generated register namespace. OSSSYS 6.0.0 uses the `reg...` prefix rather than the `mm...` prefix used by many older offset headers; consumers for this generation must include and reference the right naming style.

## Risks and Edge Cases

- Address drift across IP revisions is the largest risk. If an OSSSYS 6.0.0 offset is used on 5.x, 6.0.1, or another block revision without checking compatibility, the driver may write a valid field value to the wrong register.
- Ring topology differs from earlier generations. `ih_v6_0.c` explicitly treats ring2 as removed; adding ring2 logic using old 5.0.0 assumptions would require new offsets that are not present here.
- VMID LUTs are contiguous and consumers add `vmid` to `regIH_VMID_0_LUT` or `_MM`. That relies on the contiguous layout remaining true and on caller-side VMID bounds checks.
- Every `BASE_IDX` is `0`. If future block instances or base-index selection change, blindly copying this file's pattern would address the wrong SOC15 base.
- Register families in the sh/mask file may include fields for registers omitted from this offset file, or vice versa, depending on generated package scope. Code must compile against the matching offset and mask pair for the target ASIC.
- Storm/flood and interrupt-drop offsets affect interrupt throttling. Wrong addresses here can produce missing interrupts, interrupt floods, or inability to diagnose the first dropped interrupt.
- The `reg...` namespace can coexist with older `mm...` headers in nearby code. Accidental cross-generation inclusion may compile if names overlap through other headers but touch incompatible addresses.

## Test Signals

Validation should focus on both compile-time symbol coverage and hardware behavior:

- Build GFX11/OSSSYS 6.0.0 users including `ih_v6_0.c`, `ih_v7_0.c`, `gmc_v11_0.c`, and `amdgpu_amdkfd_gfx_v11.c` to verify all referenced `reg...` symbols exist.
- Device load and resume on GFX11 hardware should initialize IH ring0/ring1 without MMIO faults, PSP programming timeouts, or missing interrupt-enable state.
- Interrupt smoke tests should confirm ring write pointers advance, read pointers are acknowledged through MMIO or doorbells, and no unexpected ring2 access occurs.
- KFD process creation and teardown should update `regIH_VMID_0_LUT + vmid` and produce correct PASID attribution in VM faults and interrupts.
- VM fault tests in `gmc_v11_0` should recover the expected PASID from the IH LUT and handle retry/write fault flags consistently.
- Page-fault storm scenarios can exercise `regIH_STORM_CLIENT_LIST_CNTL`, `regIH_INT_FLOOD_CNTL`, and `regIH_MSI_STORM_CTRL` programming.
- Suspend/resume and GPU reset should reprogram all ring base/pointer/control registers selected from this offset table and restore interrupt delivery.
- Mechanical generation checks should compare offsets and `BASE_IDX` values against vendor register XML or the authoritative generated source for OSSSYS 6.0.0.

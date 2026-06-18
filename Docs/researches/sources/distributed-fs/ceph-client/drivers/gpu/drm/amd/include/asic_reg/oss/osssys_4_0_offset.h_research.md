# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_0_offset.h

## Purpose
This generated AMDGPU ASIC register-offset header defines the OSSSYS 4.0 register address map for the `osssys_osssysdec` block. The block comment gives base address `0x4280`; every `mm*` macro is an offset within that block, and each is paired with a `*_BASE_IDX` selector. In this file all base indices are `0`.

The offsets cover the interrupt handler (IH) and semaphore/SEM portions of OSSSYS: VMID/PASID LUTs, interrupt-cookie records, interrupt ring buffers, ring status and diagnostics, interrupt filtering/drop/flood controls, virtualization state, client configuration/remapping, SEM clock/UTCL2/mailbox/status/response controls, and register-range sentinels.

## Important APIs, Types, And Constants
The file exports preprocessor constants only. It contains no functions, types, storage, inline helpers, or runtime logic. Consumers combine these `mm*` offsets with SOC15 IP base tables via helpers such as `SOC15_REG_OFFSET(OSSSYS, instance, mmREGISTER)`, then read or write the resulting register addresses.

Important offset ranges include:
- `mmIH_VMID_0_LUT` through `mmIH_VMID_15_LUT` at `0x0000`-`0x000f`, and `mmIH_VMID_0_LUT_MM` through `_15_LUT_MM` at `0x0010`-`0x001f`, used for IH PASID lookup programming.
- `mmIH_COOKIE_0` through `mmIH_COOKIE_7` at `0x0020`-`0x0027`, which map the interrupt cookie record registers.
- `mmSEM_REQ_INPUT_0` through `_3` at `0x0040`-`0x0043`, plus part-boundary sentinels such as `mmIH_REGISTER_LAST_PART0` and `mmSEM_REGISTER_LAST_PART0`.
- Ring 0 offsets from `mmIH_RB_CNTL` at `0x0080` through `mmIH_DOORBELL_RPTR` at `0x0087`, including base, base high, read pointer, write pointer, write-pointer writeback address high/low, and doorbell read pointer.
- Ring 1 offsets from `mmIH_RB_CNTL_RING1` at `0x0088` through `mmIH_DOORBELL_RPTR_RING1` at `0x008f`, and ring 2 offsets from `mmIH_RB_CNTL_RING2` at `0x0090` through `mmIH_DOORBELL_RPTR_RING2` at `0x0097`.
- `mmIH_VERSION` at `0x0098`, then IH global control/status/performance/filtering registers from `mmIH_CNTL` at `0x00c0` through `mmIH_REGISTER_LAST_PART2` at `0x00ff`.
- SEM control/status/mailbox/register diagnostics from `mmSEM_CLK_CTRL` at `0x0100` through `mmSEM_REGISTER_LAST_PART2` at `0x017f`.
- IH virtualization/client configuration registers from `mmIH_ACTIVE_FCN_ID` at `0x0180` through `mmIH_REGISTER_LAST_PART1` at `0x019f`.
- SEM virtualization/client response/remap/atomic/EDC/MMHUB registers from `mmSEM_ACTIVE_FCN_ID` at `0x01a0` through `mmSEM_REGISTER_LAST_PART1` at `0x01bf`.

## Control Flow
There is no executable control flow. Including C files resolve symbolic register names to numeric offsets at compile time. Runtime behavior is in the callers that pass these offsets to AMDGPU register access macros or PSP-secured register programming APIs.

The layout has structural flow that mirrors hardware address order. Contiguous ranges let callers compute repeated register addresses by adding a VMID index, as seen in code that writes `SOC15_REG_OFFSET(OSSSYS, 0, mmIH_VMID_0_LUT) + vmid` and the `_MM` equivalent.

## State And Persistence Behavior
The header itself stores no state and performs no persistence. It names hardware registers whose values are persistent hardware state until reset, reprogramming, power transition, or hardware-defined clear behavior.

Important state reached through these offsets includes interrupt ring buffer base addresses and pointers, ring enablement and overflow state, VMID/PASID lookup values, last-interrupt and interrupt-cookie diagnostics, per-VF ring/flood status, client credit and remap tables, PSP/IH client configuration, SEM mailbox state, SEM response addresses, SEM active function/reset state, and MMHUB/UTCL2/MCIF configuration.

## Dependencies And Integration Points
This header has only an include guard and no C includes. It depends on SOC15 AMDGPU register access infrastructure and matching OSSSYS shift/mask headers for field-level manipulation.

Direct include sites in this tree include `amdgpu/gmc_v9_0.c`, `amdgpu/psp_v11_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v9.c`, `amdgpu/psp_v3_1.c`, and `amdgpu/vega10_ih.c`. `vega10_ih.c` uses these offsets to initialize IH ring register addresses for ring 0, ring 1, and ring 2, then toggles and programs those rings. `gmc_v9_0.c` and `amdgpu_amdkfd_gfx_v9.c` use the VMID LUT offsets to write PASID values for KFD/GFX9 memory-management integration. PSP files include the offsets alongside mask headers for secure register programming and IH client configuration.

At a system level, the offsets integrate with the DRM AMDGPU interrupt subsystem, KFD process/PASID management, PSP firmware interaction, GFX9/GMC setup, SOC15 IP base address tables, SR-IOV register programming, SEM client response routing, and low-level diagnostic/performance code.

## Risks
Offsets are hardware ABI. A wrong offset can write a valid value to the wrong register, which is usually worse than a compile error: interrupts may be lost, ring buffers may point to bad memory, write pointers may stop updating, PASID mappings may target the wrong VMID, PSP-secured programming may affect the wrong IH register, SEM mailbox routing may break, or virtualization state may leak across PF/VF boundaries.

The file has repeated, contiguous families that invite off-by-one errors when callers do arithmetic from the first offset. VMID LUT arithmetic must stay within 0-15 for this block, and callers must choose the standard or `_MM` LUT range deliberately. Ring 0, ring 1, and ring 2 are similarly patterned but not always field-identical in the matching mask header, so offset reuse should not imply identical programming semantics.

Because all `*_BASE_IDX` values are `0`, code that assumes another base index for a future IP generation would silently address the wrong SOC15 segment. This header should remain paired with the correct ASIC IP offset table and matching `osssys_4_0*_sh_mask.h` variant.

## Test Signals
Validation signals include compile coverage of all include sites, generated-register diff checks against AMD hardware descriptions, successful boot and GPU reset on OSSSYS 4.0 hardware, IH ring initialization for ring 0-2, interrupt delivery and drain/overflow behavior, write-pointer writeback memory updates, KFD/PASID VMID LUT programming, PSP register programming of IH controls, SR-IOV PF/VF reset and status tests, SEM mailbox/response client traffic, and diagnostic readback for interrupt flood/drop, credit, IOV violation, and MMHUB error registers.

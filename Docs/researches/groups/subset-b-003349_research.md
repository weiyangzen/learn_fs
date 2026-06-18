# subset-b-003349 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_0_1_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_0_1_sh_mask.h

## Purpose
This generated AMDGPU ASIC register header defines shift and mask constants for the OSSSYS 4.0.1 register block. OSSSYS contains interrupt handler (IH) and semaphore/SEM hardware registers used around interrupt-ring setup, VMID/PASID association, SR-IOV active-function state, interrupt filtering, mailbox/response routing, credit accounting, performance counters, clock controls, and diagnostic violation logs.

The header is not executable code. Its value is the hardware bitfield ABI: each `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macro tells AMDGPU register helpers how to compose or decode a 32-bit memory-mapped register value without open-coded bit positions.

## Important APIs, Types, And Constants
The file exports preprocessor constants only. It declares no C functions, structs, enums, storage, or inline helpers. Consumers are expected to pair these field definitions with an OSSSYS offset header and access registers through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, or secure PSP register programming paths.

Important IH groups include:
- `IH_VMID_0_LUT` through `IH_VMID_15_LUT` and `_MM` variants, each exposing a 16-bit `PASID` field for mapping interrupt VMIDs to process address-space IDs.
- `IH_COOKIE_0` through `IH_COOKIE_7`, which describe the interrupt-cookie record layout: client ID, source ID, ring ID, VM ID, timestamp bits, PASID source, and a 128-bit context ID split across four registers.
- `IH_RB_CNTL`, `IH_RB_BASE`, `IH_RB_BASE_HI`, `IH_RB_RPTR`, `IH_RB_WPTR`, `IH_RB_WPTR_ADDR_{HI,LO}`, and `IH_DOORBELL_RPTR`, which describe ring-buffer enablement, sizing, GPU timestamping, write-pointer writeback, overflow handling, memory-controller attributes, read/write pointer offsets, writeback address alignment, and doorbell read-pointer configuration.
- `IH_RB_*_RING1` and `IH_RB_*_RING2`, which mirror the ring-control/base/pointer/doorbell fields for additional IH rings. Ring 1 and ring 2 control macros omit some ring-0-only fields such as `WPTR_WRITEBACK_ENABLE`, `ENABLE_INTR`, and `RPTR_REARM`.
- `IH_VERSION`, `IH_CNTL`, `IH_CNTL2`, and `IH_STATUS`, which expose version fields, write-pointer writeback timing, FIFO high-water settings, self-interrupt write-pointer update controls, idle/full/overflow states, BIF interrupt-line state, switch readiness, and per-ring full/overflow state.
- `IH_PERFMON_CNTL` and result registers for two IH performance counters.
- `IH_DSM_MATCH_*`, `IH_LIMIT_INT_RATE_CNTL`, `IH_INT_FLOOD_*`, `IH_STORM_CLIENT_LIST_CNTL`, `IH_INT_DROP_*`, and match-value/mask registers for interrupt matching, rate limiting, flood/storm/drop tracking, and selective interrupt drop.
- `IH_INT_FLAGS`, `IH_LAST_INT_INFO*`, `IH_CLIENT_CREDIT_ERROR`, `IH_CREDIT_STATUS`, `IH_GPU_IOV_VIOLATION_LOG`, `IH_COOKIE_REC_VIOLATION_LOG`, and `IH_MMHUB_ERROR` for per-client flags, last-interrupt decode, credit return diagnostics, IOV violation logging, cookie-record violation logging, and MMHUB response errors.
- `IH_ACTIVE_FCN_ID`, `IH_VIRT_RESET_REQ`, `IH_CLIENT_CFG`, `IH_CLIENT_CFG_INDEX`, `IH_CLIENT_CFG_DATA`, `IH_CID_REMAP_*`, `IH_CHICKEN`, and `IH_MMHUB_CNTL` for SR-IOV active function selection, virtual reset requests, client table programming, client-ID remapping, protection controls, and MMHUB unit/traffic-level programming.

Important SEM groups include:
- `SEM_REQ_INPUT_0` through `SEM_REQ_INPUT_3`, full-width request input payload fields.
- `SEM_CLK_CTRL`, `SEM_UTC_CREDIT`, `SEM_UTC_CONFIG`, `SEM_UTCL2_TRAN_EN_LUT`, and `SEM_MCIF_CONFIG`, which configure SEM clock timing/overrides, UTCL2 credits, snoop/GCC/MTYPE behavior, per-client UTCL2 translation enablement, and memory-controller request credits/swapping.
- `SEM_PERFMON_CNTL` and result registers for SEM performance counters.
- `SEM_STATUS`, with idle, FIFO full, pending mailbox, outstanding clean, invalidation mismatch, and switch-ready status bits.
- `SEM_MAILBOX_CLIENTCONFIG`, `SEM_MAILBOX`, `SEM_MAILBOX_CONTROL`, and `SEM_MAILBOX_CLIENTCONFIG_EXTRA`, which map CP/SDMA/UVD/VCE/VCE1 clients to mailbox ports and gate hostport access.
- `SEM_CHICKEN_BITS` and `SEM_CHICKEN_BITS2`, which hold pipeline, ECC, atomic, mailbox clear, active-function protection, and MM-client VFID behavior controls.
- `SEM_GPU_IOV_VIOLATION_LOG`, `SEM_ACTIVE_FCN_ID`, `SEM_VIRT_RESET_REQ`, `SEM_CID_REMAP_*`, `SEM_MMHUB_CNTL`, and `SEM_OUTSTANDING_THRESHOLD` for virtualization diagnostics, active function/reset state, ID remapping, MMHUB signaling, and outstanding request thresholds.
- `SEM_RESP_SDMA0`, `SEM_RESP_SDMA1`, `SEM_RESP_UVD`, `SEM_RESP_VCE_0`, `SEM_RESP_ACP`, `SEM_RESP_ISP`, `SEM_RESP_VCE_1`, `SEM_RESP_VP8`, and `SEM_RESP_GC`, which define response address fields for SEM clients.
- `SEM_ATOMIC_OP_LUT` and `SEM_EDC_CONFIG`, which describe atomic signal/wait lookup fields and EDC disable control.

## Control Flow
There is no runtime control flow in this header: no branches, loops, calls, initialization routines, or callbacks. The only flow is compile-time inclusion. Driver code includes a matching offset header and this mask/shift header, then register helper macros expand these constants into read-modify-write operations.

The ordering is still meaningful for maintenance. The file follows the single `osssys_osssysdec` address block, starting with VMID LUTs and interrupt-cookie layouts, then ring-buffer controls, IH status/performance/filtering/diagnostics, SEM controls/status/mailboxes/virtualization, and finally active-function/client-remap/response/atomic fields. This order should track the hardware register database and sibling OSSSYS generated headers.

## State And Persistence Behavior
The header stores no software state. The described registers are live GPU hardware state. Values written by consumers can persist until explicit driver reprogramming, GPU reset, function-level reset, virtualization reset, power-gating transition, or hardware clear/write-one-to-clear semantics, depending on the register.

State-sensitive fields include ring enablement and base addresses, read/write pointers, write-pointer writeback addresses, overflow clear/status bits, VMID-to-PASID LUT entries, active PF/VF function IDs, interrupt drop/flood status, credit-return status, mailbox routing, SEM outstanding/idle state, clock overrides, and IOV violation logs. Because some status fields are diagnostic or clear-on-write style, callers must preserve unrelated bits and follow the hardware programming sequence documented by AMD.

## Dependencies And Integration Points
This file has only an include guard and no C includes. It depends on AMD's generated-register naming convention: mask names must exactly match the register names used by the offset header and the fields expected by `REG_SET_FIELD`/`REG_GET_FIELD`.

The closest direct integration points in this tree use the OSSSYS 4.0 offset and mask family. `vega10_ih.c` programs `IH_RB_CNTL`, ring bases, doorbells, overflow clear, ring enable, `ENABLE_INTR`, `RPTR_REARM`, and memory-controller attributes. `gmc_v9_0.c` and `amdgpu_amdkfd_gfx_v9.c` write the `IH_VMID_0_LUT` and `_MM` LUT ranges for PASID propagation. `psp_v3_1.c` uses `IH_CLIENT_CFG_DATA` fields for PSP/IH client credit-return configuration. `psp_v11_0.c` includes the OSSSYS 4.0 headers as part of PSP programming support. This specific 4.0.1 mask header appears as a generated sibling for a close hardware revision; callers must include it only with matching 4.0.1 register offsets/IP tables.

The macros integrate with the DRM AMDGPU interrupt subsystem, GPU memory-management/PASID paths, KFD process queue support, PSP secure register programming in SR-IOV contexts, MMHUB/UTCL2 interaction, virtualization diagnostics, performance counter/debug tooling, and low-level reset/clock-control code.

## Risks
The primary risk is silent hardware misprogramming. A wrong bit shift or mask can enable the wrong ring, corrupt a ring-buffer size, point writeback to the wrong address, lose interrupts, mishandle write-pointer overflow, associate a VMID with the wrong PASID, break SR-IOV isolation, hide credit errors, or damage SEM mailbox/response routing.

Repeated families are copy-drift sensitive: 16 IH VMID LUTs, 16 MM LUTs, three IH rings, 31 client flag/credit bits, multiple VF status bitmaps, many SEM response registers, and paired value/mask registers all need lane-by-lane consistency. Ring 0 also has fields that rings 1 and 2 do not, so generic ring code must not assume every ring-control register has identical field coverage.

The file uses `0x80000000L` and other high-bit long constants. Consumers should operate on unsigned 32-bit register values to avoid signed-extension surprises in ad hoc code. Because the header is generated hardware ABI, manual edits should be avoided unless regenerated from authoritative register data and compared against sibling versions such as `osssys_4_0_sh_mask.h` and later OSSSYS revisions.

## Test Signals
Useful validation signals include compile coverage for ASIC code that selects OSSSYS 4.0.1 fields, generated-header diff checks against AMD register XML/database output, boot and GPU reset on matching ASICs, IH ring initialization and teardown, interrupt delivery on rings 0-2, write-pointer writeback and overflow-clear tests, MSI/MSI-X rearm behavior, PASID/VMID updates exercised by KFD/SVM workloads, SR-IOV PF/VF reset and active-function tests, PSP secure register programming for IH ring control, SEM mailbox/response traffic, interrupt flood/drop diagnostics, performance counter readback, and fault/IOV violation log decode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_0_1_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_0_offset.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_0_offset.h -->

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

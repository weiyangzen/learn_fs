# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_7_0_0_sh_mask.h

## Purpose

`osssys_7_0_0_sh_mask.h` is the generated shift/mask companion for the OSSSYS 7.0.0 register offset map. It defines the bitfield contract for the same `osssys_osssysdec` address block, letting driver code encode and decode IH, SEM, virtualization, client, and diagnostic registers without hard-coded bit arithmetic at each call site.

The file does not contain functions or data objects. It exports preprocessor constants in the pattern `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. AMDGPU code consumes these constants indirectly through macros such as `REG_SET_FIELD` and directly through masks where needed.

## Important APIs, Types, And Macros

The important macro families are:

- VMID LUT fields: every `IH_VMID_*_LUT` and `IH_VMID_*_LUT_MM` register exposes a 16-bit `PASID` field at shift `0` with mask `0x0000FFFFL`.
- Interrupt cookie fields: `IH_COOKIE_0` encodes client/source/ring/VMID/VMID type; `IH_COOKIE_1` and `IH_COOKIE_2` encode timestamp bits and timestamp source; `IH_COOKIE_3` carries PASID and PASID source; `IH_COOKIE_4` through `IH_COOKIE_7` carry a 128-bit context ID split across four registers.
- Ring buffer fields: `IH_RB_CNTL` covers `RB_ENABLE`, `RB_SIZE`, write-pointer writeback, full-drain/page-clear controls, used threshold, overflow enable/clear, ring0 `ENABLE_INTR`, memory-controller swap/snoop/read-only controls, memory VMID/space, and read-pointer rearm. `IH_RB_RPTR`, `IH_RB_WPTR`, `IH_RB_BASE`, `IH_RB_BASE_HI`, and writeback address fields define pointer and address layout. Ring 1 has matching `IH_RB_*_RING1` definitions, with a reduced control surface that omits ring0-only interrupt enable and writeback fields.
- Doorbell fields: `IH_DOORBELL_RPTR`, `IH_DOORBELL_RETRY_CAM`, and `IH_DOORBELL_RPTR_RING1` define a 26-bit doorbell offset plus enable bit at bit 28.
- Control and power fields: `IH_CNTL`, `IH_CNTL2`, `IH_CLK_CTRL`, `IH_LIMIT_INT_RATE_CNTL`, `IH_RETRY_INT_CAM_CNTL`, `IH_MEM_POWER_CTRL`, and `IH_MEM_POWER_CTRL2` cover write-pointer update timing, clock overrides, interrupt-rate limiting, retry CAM sizing/backpressure, and low-power memory behavior.
- Status/performance fields: `IH_STATUS`, `IH_PERFMON_CNTL`, and two performance result registers expose idle/full/overflow/stall/power-gate status and two programmable performance counters.
- Matching and filtering fields: DSM match registers, interrupt flood controls, `IH_INT_FLAGS`, `IH_INT_DROP_CNTL`, and drop match value/mask registers define diagnostic matching and intentional drop filters for client/source/VF/context identifiers.
- SR-IOV and diagnostics: `IH_VF_RB_STATUS*`, `IH_VF_RB1_STATUS*`, `IH_ACTIVE_FCN_ID`, `IH_VIRT_RESET_REQ`, IOV violation logs, cookie-record violation logs, credit error/status, and `IH_MMHUB_ERROR` expose per-VF and bus/MMHUB fault state.
- Client routing: `IH_CLIENT_CFG`, indexed ring1/client config data registers, `IH_CID_REMAP_*`, and `IH_CHICKEN` define client counts, source match entries, credit-return addresses, remapping from initiator/client IDs, active-function protection, debug/cross triggers, memory-space options, and firewall enable.
- SEM mailbox fields: `SEM_MAILBOX` and `SEM_MAILBOX_CLEAR` expose 16-bit hostport data and clear masks.

## Control Flow And Runtime Use

The file has no executable control flow. It shapes control flow in register programming code by allowing call sites to set fields symbolically. In `amdgpu/ih_v7_0.c`, examples include:

- `REG_SET_FIELD(tmp, IH_RB_CNTL, RB_ENABLE, ...)` and `REG_SET_FIELD(tmp, IH_RB_CNTL, ENABLE_INTR, ...)` when toggling interrupt rings.
- `REG_SET_FIELD(ih_rb_cntl, IH_RB_CNTL, WPTR_OVERFLOW_CLEAR, 1)`, `WPTR_OVERFLOW_ENABLE`, `RB_SIZE`, `WPTR_WRITEBACK_ENABLE`, `MC_SNOOP`, `MC_RO`, `MC_VMID`, and `MC_SPACE` while preparing ring buffer control values.
- `REG_SET_FIELD(..., IH_DOORBELL_RPTR, OFFSET, ...)` and `ENABLE` for doorbell-based read-pointer updates.
- `REG_SET_FIELD(ih_cntl, IH_CNTL2, SELF_IV_FORCE_WPTR_UPDATE_TIMEOUT, ...)` and `SELF_IV_FORCE_WPTR_UPDATE_ENABLE` when forcing write-pointer updates for self interrupts.
- `REG_SET_FIELD(tmp, IH_MSI_STORM_CTRL, DELAY, ...)` when adjusting MSI storm behavior.

In GMC/KFD paths, the PASID shift/mask constants describe the VMID LUT register payloads. Some consumers write PASID values directly because the PASID field occupies low bits, while other paths shift by `IH_VMID_0_LUT__PASID__SHIFT` for clarity.

## State And Persistence Behavior

This header is stateless. The fields describe live and sometimes sticky hardware state:

- Ring buffer enable, base, pointer, overflow, drain, threshold, and doorbell fields define the persistent configuration of the active IH rings until reset or reprogramming.
- `IH_STATUS` and `IH_RB_STATUS` style fields are readback state. Some bits are transient idle/full/stall indicators; others are overflow/flood conditions requiring explicit clear/rearm sequences.
- PASID and context cookie fields are produced or consumed as interrupt metadata and determine how software attributes interrupts to VMIDs, PASIDs, rings, and contexts.
- SR-IOV fields persist the active PF/VF identity, reset requests, per-VF ring status, and violation logs.
- Power/clock control fields can affect whether internal memories are clocked or power-gated; incorrect persistence across suspend/resume could change interrupt latency or break readbacks.

## Dependencies And Integration Points

The field names must match the offset register names and the AMDGPU register helper macros. Integration points include:

- `REG_SET_FIELD` and related AMDGPU bitfield macros, which derive `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` names from the register and field tokens supplied at call sites.
- `osssys_7_0_0_offset.h`, which supplies the corresponding `reg...` MMIO offsets.
- `amdgpu_ih` ring initialization and interrupt dispatch, where these fields control interrupt enablement, ring memory placement, write-pointer writeback, doorbells, overflow handling, and storm mitigation.
- GMC/KFD PASID mapping, where the low 16-bit PASID field in each VMID LUT register is used for TLB invalidation by PASID and for process attribution.
- SR-IOV/PSP paths that may program selected IH registers indirectly while still using the same bitfield encoding.

## Risks

Because generic register helpers synthesize macro names, missing or renamed field macros become compile-time failures. More subtle risks are incorrect shift/mask values that compile but program the wrong bits. High-risk fields include `RB_ENABLE`, `ENABLE_INTR`, `RB_SIZE`, writeback address fields, `MC_SPACE`, `MC_VMID`, `WPTR_OVERFLOW_CLEAR`, and doorbell `OFFSET`/`ENABLE`, because they directly affect interrupt delivery and memory addressing.

The ring0 and ring1 control layouts are similar but not identical. Accidentally using `IH_RB_CNTL` field names against ring1-specific programming can set unsupported bits or miss required ring1 behavior. The existing driver mostly uses `IH_RB_CNTL` helpers for common fields and `IH_RB_CNTL_RING1` where the ring1-only path requires it, so changes should preserve that distinction.

Several fields carry security or isolation meaning, including active-function protection, register firewall enable, PF/VF identity, VF reset request bits, IOV violation logs, client ID remapping, and interrupt drop filters. Incorrect values can hide violations, misattribute interrupts, or break VF isolation.

The 7.1 OSSSYS generation has a very similar mask header, but offsets moved for some client/virtualization registers. Field compatibility should not be assumed to imply address compatibility.

## Test Signals

Useful signals include:

- Compile coverage for `ih_v7_0.c`, `gmc_v12_0.c`, KFD PASID-mapping users, and any SR-IOV paths using the macros.
- Hardware bring-up where IH ring enable succeeds, MSI/MSI-X interrupts arrive, and the ring write pointer advances with and without writeback enabled.
- Overflow tests that trigger `IH_RB_WPTR__RB_OVERFLOW` and clear it through `IH_RB_CNTL__WPTR_OVERFLOW_CLEAR`.
- Doorbell tests where the read pointer is advanced through the configured doorbell offset and the register `ENABLE` bit matches expected mode.
- VMID/PASID mapping tests for both GFX and MM hubs, including TLB invalidation by PASID.
- SR-IOV tests checking active function, VF reset request, VF ring status, IOV violation logs, and PSP indirect programming.
- Suspend/resume and power-management tests that cover clock override and memory power-gating fields without losing interrupt delivery.

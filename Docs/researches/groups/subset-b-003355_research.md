# subset-b-003355 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_7_0_0_offset.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_7_0_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_7_0_0_sh_mask.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_7_0_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_7_1_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_7_1_0_offset.h

## Purpose

`osssys_7_1_0_offset.h` is the generated register offset map for OSSSYS 7.1.0. Like the 7.0.0 offset header, it describes the `osssys_osssysdec` address block with base address `0x4280` and exports `reg...` plus `..._BASE_IDX` macros for use with SOC15 AMDGPU register helpers.

The file preserves most of the OSSSYS 7.0.0 interrupt-handler register map but introduces a version-specific `regIH_VMID_LUT_INDEX` register and moves the SEM/client/virtualization tail window down from the `0x0180` range to the `0x0120` range. It is therefore a hardware-version ABI map, not a general replacement for the 7.0.0 header.

## Important APIs, Types, And Macros

This header exports only preprocessor macros. Important groups include:

- `regIH_VMID_0_LUT` through `regIH_VMID_15_LUT` and `regIH_VMID_0_LUT_MM` through `regIH_VMID_15_LUT_MM`, still contiguous at `0x0000`-`0x001f`.
- `regIH_COOKIE_0` through `regIH_COOKIE_7` at `0x0020`-`0x0027`.
- `regIH_VMID_LUT_INDEX` at `0x0028`, new relative to 7.0.0. This register selects which VMID LUT slice/instance subsequent LUT accesses address on 7.1 hardware.
- Ring 0 and ring 1 IH registers at the same offsets as 7.0.0 for `RB_CNTL`, `RPTR`, `WPTR`, base address, writeback address, doorbell, retry CAM, status, control, rate-limit, memory power, performance, DSM match, VF status, flood/drop, MSI storm, and last interrupt info.
- SEM mailbox registers at `regSEM_MAILBOX` `0x010a` and `regSEM_MAILBOX_CLEAR` `0x010b`, with `regSEM_REGISTER_LAST_PART2` reduced to `0x011f`.
- The virtualization/client tail window beginning at `regIH_VIRT_RESET_REQ` `0x0120`, followed by `regIH_CLIENT_CFG`, indexed ring1/client configuration, CID remap, `regIH_CHICKEN`, interrupt drop match/mask registers, and `regIH_MMHUB_CNTL` at `0x0147`.
- `regIH_REGISTER_LAST_PART1` at `0x019f`, marking the tail of this generated register partition.

All `*_BASE_IDX` macros are `0`.

## Control Flow And Runtime Use

The header contains no executable control flow. Consumers use it to compute register addresses. Direct consumer evidence in this tree includes:

- `amdgpu/gmc_v12_1.c`, which includes `osssys_7_1_0_offset.h` and `osssys_7_1_0_sh_mask.h`. Its VMID/PASID lookup helper computes an index from the hub instance, writes that value to `SOC15_REG_OFFSET(OSSSYS, 0, regIH_VMID_LUT_INDEX)`, then reads `SOC15_REG_OFFSET(OSSSYS, 0, regIH_VMID_0_LUT) + vmid` and masks the low 16 bits.
- `amdgpu/ih_v7_0.c`, which is shared across OSSSYS 7.x interrupt handling. That file currently includes the 7.0.0 offset/mask headers and carries local `regIH_RING1_CLIENT_CFG_INDEX_V7_1`, `regIH_RING1_CLIENT_CFG_DATA_V7_1`, and `regIH_CHICKEN_V7_1` constants matching this 7.1 offset map. It chooses those constants when `amdgpu_ip_version(adev, OSSSYS_HWIP, 0) == IP_VERSION(7, 1, 0)`.

The runtime flow for 7.1 VMID lookup is version-specific: select a LUT index first, then access the same contiguous LUT offsets used by earlier hardware. This is the key behavioral addition represented by the offset header.

## State And Persistence Behavior

The header is stateless. The hardware registers it names hold the same categories of live state as 7.0.0: IH ring configuration and pointers, VMID/PASID mappings, interrupt cookies, storm/drop/flood diagnostics, SR-IOV status and reset requests, SEM mailbox data, client remapping, and MMHUB control.

The new `regIH_VMID_LUT_INDEX` has important state behavior: it is a selector that affects which VMID LUT instance is addressed by later LUT reads or writes. Callers must treat it as mutable global hardware selector state. Code that writes it should restore or intentionally leave it in a known state if later operations could assume a different LUT slice. The observed `gmc_v12_1_get_vmid_pasid_mapping_info()` flow writes the selector immediately before reading the LUT, reducing but not eliminating interleaving risk if other contexts access the same selector without serialization.

## Dependencies And Integration Points

Primary dependencies and integration points are:

- SOC15 register-address helpers, which combine `OSSSYS`, instance `0`, and the generated register offsets.
- `gmc_v12_1.c`, where the new LUT selector is part of VMID/PASID lookup for multi-instance/hub-aware TLB invalidation.
- The 7.1 shift/mask header for field encoding. This work item did not require researching that file, but `gmc_v12_1.c` includes it alongside this offset header.
- Shared IH initialization in `ih_v7_0.c`, which must account for moved 7.1 offsets when programming ring1 client configuration and the `IH_CHICKEN` register.
- The older 7.0.0 offset map, which is mostly compatible for the front part of the register block but differs in the tail window.

## Risks

The largest risk is treating the 7.0.0 and 7.1.0 offset maps as interchangeable. The early IH ring and status windows are stable, but the tail region changed: 7.0.0 has `regIH_ACTIVE_FCN_ID` at `0x0180` and subsequent client/virtualization registers through `0x01a8`; 7.1.0 removes that active-function offset from this header and places `regIH_VIRT_RESET_REQ` at `0x0120`, `regIH_CHICKEN` at `0x0129`, and `regIH_MMHUB_CNTL` at `0x0147`. Using 7.0 addresses on 7.1 hardware can write to the wrong register window.

`regIH_VMID_LUT_INDEX` introduces selector state. Missing selector writes can read the wrong PASID mapping; unsynchronized selector use can produce wrong results if multiple paths access the selector/LUT pair concurrently. Tests should look for locking or hardware access serialization around selector-dependent reads and writes.

Local hard-coded 7.1 constants in `ih_v7_0.c` are a maintenance risk because they duplicate values already present in this header. If the generated header changes, those local constants can drift unless updated together.

## Test Signals

Useful validation signals include:

- Build coverage for `gmc_v12_1.c` with the 7.1 offset and mask headers.
- VMID/PASID lookup tests across multiple `inst` values that verify the index calculation writes the expected selector values and reads the correct PASID from VMIDs 1-15.
- TLB invalidation-by-PASID tests on 7.1 hardware, especially with multiple hub/instance combinations, because stale or wrong LUT selector state would flush the wrong VMID.
- IH bring-up on OSSSYS 7.1.0 hardware verifying the moved `IH_CHICKEN` and ring1 client config offsets are programmed correctly by the version checks in `ih_v7_0.c`.
- Suspend/resume, reset, and SR-IOV tests checking that selector state and moved tail-window registers are restored or reprogrammed reliably.
- Register readback or hardware trace checks comparing `regIH_VMID_LUT_INDEX`, `regIH_RING1_CLIENT_CFG_INDEX`, `regIH_RING1_CLIENT_CFG_DATA`, and `regIH_CHICKEN` addresses against the generated 7.1 spec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_7_1_0_offset.h -->

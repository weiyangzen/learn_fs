# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_2_0_sh_mask.h

## Purpose
`osssys_4_2_0_sh_mask.h` is a generated AMDGPU OSSSYS 4.2.0 register field header. It provides C preprocessor constants for bit shifts and bit masks in the OSS system decode block, mainly interrupt-handler (IH) and semaphore/SEM registers. Driver code combines these constants with AMDGPU helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` to build or decode 32-bit MMIO register values without hard-coded bit arithmetic in the implementation files.

## Important APIs, Types, and Functions
The file has no C functions, structs, or runtime APIs. Its ABI is the macro namespace:

- `IH_VMID_0_LUT` through `IH_VMID_15_LUT` and `_MM` variants expose `PASID` fields used to associate VMIDs with PASIDs for graphics and multimedia/IH routing.
- `IH_COOKIE_0` through `IH_COOKIE_7` describe interrupt cookie fields: client ID, source ID, ring ID, VM ID, timestamp fragments, PASID source, and context ID fragments.
- `IH_RB_CNTL`, `IH_RB_BASE`, `IH_RB_BASE_HI`, `IH_RB_RPTR`, `IH_RB_WPTR`, writeback address, and `IH_DOORBELL_RPTR` macros define the primary IH ring programming fields. `IH_RB_CNTL_RING1`/`RING2` and related base/read/write pointer/doorbell macros repeat the layout for secondary IH rings.
- `IH_RETRY_INT_CAM_CNTL`, `IH_LIMIT_INT_RATE_CNTL`, `IH_INT_FLOOD_CNTL`, ring flood status registers, `IH_INT_DROP_*`, DSM match registers, and storm-client controls define filtering, retry, rate limit, and interrupt-drop instrumentation fields.
- `IH_STATUS`, `IH_VERSION`, `IH_PERFMON_CNTL`, `IH_PERFCOUNTER*_RESULT`, `IH_CLK_CTRL`, `IH_INT_FLAGS`, `IH_LAST_INT_INFO*`, `IH_CLIENT_CREDIT_ERROR`, `IH_GPU_IOV_VIOLATION_LOG`, `IH_COOKIE_REC_VIOLATION_LOG`, `IH_CREDIT_STATUS`, `IH_MMHUB_ERROR`, `IH_MEM_POWER_CTRL`, `IH_ACTIVE_FCN_ID`, `IH_VIRT_RESET_REQ`, `IH_CLIENT_CFG*`, `IH_CID_REMAP_*`, `IH_CHICKEN`, and `IH_MMHUB_CNTL` cover status, performance, clock/power, virtualization, credit, client configuration, and error-reporting fields.
- `SEM_*` macros cover semaphore request inputs, clock/power controls, UTC and UTCL2 translation controls, MCIF credits, SEM performance counters, status, mailbox configuration, GPU IOV violation logging, response address registers for SDMA/UVD/VCE/ACP/ISP/GC clients, CID remap, atomic operation lookup, EDC, chicken bits, and MMHUB tuning.

Every exported register field follows the generated `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` naming convention. Constants use `L`-suffixed integer literals and are intended for 32-bit register values.

## Control Flow and State
There is no executable control flow. Inclusion is gated by `_osssys_4_2_0_SH_MASK_HEADER`, then consumers use the macros at compile time. The practical data flow is:

1. A driver includes the matching offset header and this mask header.
2. The driver obtains a register address from an offset macro, often through `SOC15_REG_OFFSET(OSSSYS, instance, reg-or-mm-name)`.
3. The driver reads or initializes a 32-bit value.
4. `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` uses the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` macros to place field bits.
5. The value is written through AMDGPU MMIO helpers such as `WREG32()`, `WREG32_NO_KIQ()`, or PSP-mediated register programming on SR-IOV paths.

Runtime state lives in hardware registers and driver-owned software structures, not in this header. The header describes persistent hardware state such as IH ring base addresses, read/write pointers, doorbell enablement, write-pointer writeback, interrupt overflow bits, per-VF full/overflow status, active function IDs, client credit state, SEM mailbox state, and power/clock override bits.

## Dependencies
The header depends on the AMD register database contract and on consumers using the exact register names expected by AMDGPU field helpers. It is paired with the corresponding 4.2.0 offset header, and related variants such as `osssys_4_0*_sh_mask.h` and `osssys_4_4_2_sh_mask.h` show the same generated schema for adjacent IP versions. The direct consumer found in this tree is `drivers/gpu/drm/amd/amdgpu/vega20_ih.c`, which includes `oss/osssys_4_2_0_sh_mask.h` and uses fields such as `IH_RB_CNTL.RB_ENABLE`, `RB_GPU_TS_ENABLE`, `WPTR_OVERFLOW_CLEAR`, `ENABLE_INTR`, `MC_SPACE`, `WPTR_WRITEBACK_ENABLE`, `MC_SNOOP`, `MC_RO`, `MC_VMID`, `RPTR_REARM`, and `IH_DOORBELL_RPTR.OFFSET/ENABLE` while initializing and toggling IH rings.

## Integration Points
This file integrates with the SOC15 AMDGPU register-access layer, the VEGA20 interrupt handler implementation, PSP-mediated IH programming for SR-IOV virtual functions, interrupt ring buffer allocation and doorbell setup, VMID/PASID routing, KFD and graphics-memory-management paths that depend on IH VMID lookup semantics, and low-level diagnostics for interrupt flooding, dropped interrupts, credit failures, IOV violations, and MMHUB errors. Because the macro names are part of the driver source ABI, implementation files can be written independently of raw numeric bit positions as long as the ASIC IP version selects the matching header.

## Risks
The main risk is register ABI drift: a wrong mask, shift, IP-version pairing, or copied field name silently programs hardware incorrectly. IH ring-control fields are especially sensitive because mistakes can disable interrupts, lose write-pointer updates, fail to clear overflow, select the wrong memory space/VMID, or break MSI rearm behavior. Virtualization fields are also high risk: wrong active-function, VF reset, VF ring status, or PASID/VMID fields can route interrupts or semaphore responses to the wrong function. SEM and UTCL2/MCIF fields affect translation, snooping, mailbox, and memory-client behavior, so stale constants can produce hangs that look like unrelated GPU faults. Since these are preprocessor constants, ordinary C type checking cannot validate field width, reserved-bit preservation, or whether a particular field is valid for the selected ASIC.

## Test Signals
Useful validation signals are successful AMDGPU builds with `vega20_ih.c`, boot and driver probe on the relevant ASIC, working MSI/MSI-X interrupt delivery, stable IH ring enable/disable, correct read/write pointer writeback, no unexpected IH ring overflow or flood counters, working SR-IOV VF interrupt programming through PSP paths, correct KFD/PASID interrupt attribution, and absence of MMHUB/IOV/credit error logs under graphics, compute, multimedia, and reset stress. Register dumps should show only intended field bits changing when IH rings, doorbells, flood/drop controls, and SEM mailbox features are configured.
